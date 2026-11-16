#!/usr/bin/env node
// Installer for the paranoid-agent skill: copies the skill payload into
// agent skills directories. Stdlib only, no network.
import { cpSync, existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const SKILL = "paranoid-agent";
const PAYLOAD = ["SKILL.md", "README.md", "README.en.md", "assets", "examples", "references", "scripts"];

const KNOWN = [
  join(homedir(), ".agents", "skills"),
  join(homedir(), ".claude", "skills"),
  join(homedir(), ".codex", "skills"),
];

function usage() {
  console.log(`paranoid-agent installer
Usage:
  npx paranoid-agent-skill [--dir <path>] [--force]

Options:
  --dir <path>   Install into <path> (uses <path>/${SKILL} when it looks like a skills root,
                 otherwise installs directly into <path>).
  --force        Overwrite an existing install.
  --help         Show this text.

No flag: installs into every standard skills dir that already exists
(~/.agents/skills, ~/.claude/skills, ~/.codex/skills); creates ~/.agents/skills if none exists.`);
}

function parseArgs(argv) {
  const out = { dir: null, force: false, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dir") out.dir = argv[++i];
    else if (a === "--force") out.force = true;
    else if (a === "--help" || a === "-h") out.help = true;
    else throw new Error(`unknown flag: ${a}`);
  }
  if (!out.force && !out.dir && !out.help) out.force = false;
  return out;
}

function targetsFor(dir) {
  const looksLikeRoot = /(skills|Skills)$/.test(dir.replace(/\\/g, "/"));
  return [looksLikeRoot ? join(dir, SKILL) : dir];
}

function installInto(dest, force) {
  if (existsSync(dest) && !force) {
    console.log(`skip (exists, use --force): ${dest}`);
    return false;
  }
  mkdirSync(dest, { recursive: true });
  for (const entry of PAYLOAD) {
    const src = join(ROOT, entry);
    if (!existsSync(src)) continue;
    cpSync(src, join(dest, entry), { recursive: true });
  }
  console.log(`installed: ${dest}`);
  return true;
}

try {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }
  let dests = args.dir ? targetsFor(resolve(args.dir)) : KNOWN.filter(existsSync);
  if (!dests.length) {
    dests = [join(homedir(), ".agents", "skills", SKILL)];
    mkdirSync(dirname(dests[0]), { recursive: true });
  } else if (!args.dir) {
    dests = dests.map((d) => join(d, SKILL));
  }
  let ok = false;
  for (const d of dests) ok = installInto(d, args.force) || ok;
  if (!ok) process.exitCode = 1;
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exitCode = 1;
}
