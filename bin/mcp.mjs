#!/usr/bin/env node
// paranoid-agent MCP server (stdio). Thin wrappers over the skill's
// deterministic scripts: sweep, inventory, and report rendering run
// outside agent context; judgment stays with the agent.
// Read-only, except render_breach_report with an explicit write_to path.
// No network egress. Secrets never leave redacted.
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const SCRIPTS = join(ROOT, "scripts");
const VERSION = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8")).version;
const TIMEOUT_MS = 90000;
const MAX_OUT = 1024 * 1024;

let python = null;
function resolvePython() {
  if (python) return python;
  for (const bin of ["python3", "python"]) {
    const r = spawnSync(bin, ["--version"], { encoding: "utf8", timeout: 10000 });
    if (r.status === 0) {
      python = bin;
      return bin;
    }
  }
  throw new Error("no python found (tried python3, python)");
}

function runScript(name, args) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(resolvePython(), [join(SCRIPTS, name), ...args], {
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    const kill = setTimeout(() => child.kill("SIGKILL"), TIMEOUT_MS);
    child.stdout.on("data", (c) => {
      out += c.toString("utf8");
      if (out.length > MAX_OUT) child.kill("SIGKILL");
    });
    child.stderr.on("data", (c) => {
      err += c.toString("utf8").slice(0, 4000);
    });
    child.on("error", (e) => {
      clearTimeout(kill);
      reject(new Error(`spawn failed: ${e.message}`));
    });
    child.on("close", (code, signal) => {
      clearTimeout(kill);
      if (signal === "SIGKILL") {
        reject(new Error(`script timed out or output exceeded limit: ${name}`));
        return;
      }
      if (code !== 0) {
        reject(new Error(`${name} exited ${code}: ${err || out.slice(0, 500)}`));
        return;
      }
      try {
        resolvePromise(JSON.parse(out));
      } catch {
        reject(new Error(`${name} returned non-JSON output: ${out.slice(0, 300)}`));
      }
    });
  });
}

// Second gate: refuse raw secrets even if a script regresses.
function assertRedacted(payload) {
  const text = JSON.stringify(payload);
  const keyBody = /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\s]{64,}/.test(
    text.replace("***REDACTED***", "")
  );
  const liveKey = /sk-live-[A-Za-z0-9]{12,}/.test(text.replace(/\*\*\*/g, ""));
  if (keyBody || liveKey) {
    throw new Error("refusing output: raw secret detected, redaction failed");
  }
}

function textResult(obj) {
  return { content: [{ type: "text", text: JSON.stringify(obj, null, 2) }] };
}

const server = new McpServer(
  { name: "paranoid-agent", version: VERSION },
  {
    instructions:
      "Paranoid security sweep primitives. Tools run local deterministic scans and return redacted JSON. They judge nothing: the agent traces data flow, scores, and writes the kill-list. prod/server targets are read-only; active probes are out of scope for these tools.",
  }
);

server.tool(
  "secret_sweep",
  "Hunt leaked secrets in a worktree plus its last 10 git commits. Returns redacted matches only (prefix/suffix), never raw values.",
  {
    path: z.string().default(".").describe("Worktree path to scan"),
    include_history: z.boolean().default(true).describe("Also scan the last 10 commits"),
  },
  async ({ path, include_history }) => {
    const target = isAbsolute(path) ? path : resolve(process.cwd(), path);
    const args = ["--path", target];
    if (!include_history) args.push("--no-history");
    const payload = await runScript("secret-sweep.py", args);
    assertRedacted(payload);
    return textResult(payload);
  }
);

server.tool(
  "port_inventory",
  "Inventory local listeners (ss/netstat) plus Dockerfile/compose port config. Local read-only, never an external scan.",
  {
    path: z.string().default(".").describe("Project path whose config files to inspect"),
  },
  async ({ path }) => {
    const target = isAbsolute(path) ? path : resolve(process.cwd(), path);
    const payload = await runScript("port-exposure.py", ["--path", target]);
    return textResult(payload);
  }
);

server.tool(
  "render_breach_report",
  "Render the hacker-terminal breach-report HTML from a findings object. Writes to a temp file unless write_to is given; returns path plus byte count instead of full HTML.",
  {
    findings: z
      .record(z.string(), z.unknown())
      .describe("Findings object per references/report-spec.md (attacks, ports, leaks, kills, scores)"),
    before: z.number().int().min(0).max(100).describe("Measured before score"),
    after: z.number().int().min(0).max(100).describe("Projected after score"),
    write_to: z
      .string()
      .optional()
      .describe("Explicit output path for breach-report.html. Omit for a temp file."),
  },
  async ({ findings, before, after, write_to }) => {
    const dir = mkdtempSync(join(tmpdir(), "paranoid-agent-"));
    const findingsPath = join(dir, "findings.json");
    writeFileSync(findingsPath, JSON.stringify(findings));
    const outPath = write_to
      ? resolve(write_to)
      : join(dir, "breach-report.html");
    const r = spawnSync(
      resolvePython(),
      [
        join(SCRIPTS, "generate-breach-report.py"),
        "--findings",
        findingsPath,
        "--before",
        String(before),
        "--after",
        String(after),
        "--out",
        outPath,
      ],
      { encoding: "utf8", timeout: TIMEOUT_MS }
    );
    if (r.status !== 0) {
      throw new Error(`render failed: ${(r.stderr || r.stdout || "").slice(0, 500)}`);
    }
    return textResult({
      path: outPath,
      bytes: statSync(outPath).size,
      before,
      after,
      attacks: Array.isArray(findings.attacks) ? findings.attacks.length : 0,
      ports: Array.isArray(findings.ports) ? findings.ports.length : 0,
      leaks: Array.isArray(findings.leaks) ? findings.leaks.length : 0,
      kills: Array.isArray(findings.kills) ? findings.kills.length : 0,
    });
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
