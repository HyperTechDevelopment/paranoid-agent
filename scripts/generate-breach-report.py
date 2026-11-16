#!/usr/bin/env python3
"""Generate hacker-terminal breach-report.html from findings.json + template."""
import argparse, html, json, os, re, sys

TEMPLATE_NAMES = ["breach-report-template.html", "assets/breach-report-template.html"]

def load_template(here):
    for name in [os.path.join(here, "..", "assets", "breach-report-template.html"),
                 os.path.join(here, "breach-report-template.html")]:
        if os.path.exists(name):
            with open(name, encoding="utf-8") as f:
                return f.read()
    sys.exit("template not found: assets/breach-report-template.html")

def guard_no_raw_secrets(findings):
    text = json.dumps(findings)
    bad = []
    if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\s]{100,}", text):
        bad.append("private-key body detected")
    for m in re.finditer(r"sk-live-[A-Za-z0-9]{12,}", text):
        # allow redacted form sk-live-***xxxx only
        if "***" not in text[max(0, m.start()-10): m.end()+10]:
            bad.append("raw stripe-like secret detected")
            break
    if bad:
        sys.exit("refusing to render: " + "; ".join(bad) + " — redact findings first")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--before", type=int, required=True)
    ap.add_argument("--after", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(a.findings, encoding="utf-8") as f:
        findings = json.load(f)
    guard_no_raw_secrets(findings)
    findings["before"] = a.before
    findings["after"] = a.after
    tpl = load_template(here)
    payload = json.dumps(findings, ensure_ascii=False).replace("</", "<\\/")
    rendered = tpl.replace("/*__FINDINGS__*/{}", payload)
    rendered = rendered.replace("__BEFORE__", str(a.before)).replace("__AFTER__", str(a.after))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"wrote {a.out} ({len(rendered)} bytes)")

if __name__ == "__main__":
    main()
