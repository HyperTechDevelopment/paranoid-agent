#!/usr/bin/env python3
"""Port/exposure inventory: OS listeners + Dockerfile/compose config. No external scan."""
import argparse, json, os, re, shutil, subprocess

def os_listeners():
    rows = []
    for cmd in (["ss", "-tln"], ["netstat", "-ano"], ["netstat", "-tlnp"]):
        exe = shutil.which(cmd[0])
        if not exe:
            continue
        try:
            r = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, timeout=10)
        except Exception:
            continue
        if r.returncode != 0 or not r.stdout.strip():
            continue
        for line in r.stdout.splitlines():
            m = re.search(r"(0\.0\.0\.0|127\.0\.0\.1|::|\[::\]|localhost)[:.](\d{1,5})", line)
            if m:
                rows.append({"raw": line.strip()[:160], "host": m.group(1), "port": int(m.group(2)),
                             "via": cmd[0]})
        if rows:
            break
    return rows

def scan_configs(root):
    exposes = []
    for dirpath, _, files in os.walk(root):
        if ".git" in dirpath or "node_modules" in dirpath:
            continue
        for fn in files:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            try:
                if os.path.getsize(p) > 200_000:
                    continue
                if fn == "Dockerfile" or fn == "docker-compose.yml" or fn == "docker-compose.yaml" \
                   or fn in ("fly.toml", "Procfile") or fn.endswith((".toml", ".yml", ".yaml")):
                    with open(p, encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    for m in re.finditer(r"EXPOSE\s+(\d{2,5})", text):
                        exposes.append({"file": rel, "port": int(m.group(1)), "kind": "EXPOSE"})
                    for m in re.finditer(r'["\']?(\d{2,5})["\']?\s*:\s*["\']?(\d{2,5})["\']?', text):
                        if "ports" in text[: max(0, text.find(m.group(0)))] [-500:]:
                            exposes.append({"file": rel, "host_port": int(m.group(1)),
                                            "container_port": int(m.group(2)), "kind": "compose-ports"})
                    if re.search(r"0\.0\.0\.0", text):
                        exposes.append({"file": rel, "kind": "bind-0.0.0.0"})
            except OSError:
                continue
    return exposes[:200]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.path)
    data = {"target": root, "listeners": os_listeners(),
            "configs": scan_configs(root),
            "guidance": "0.0.0.0 + unauthenticated in prod = CRITICAL; 127.0.0.1 local-only = lower"}
    text = json.dumps(data, indent=2)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)

if __name__ == "__main__":
    main()
