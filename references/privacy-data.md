# Privacy Data Minimization

## Classify on Write

Tag every new field: non-personal, PII, sensitive. Unknown defaults to PII until reviewed. Keep a field inventory so deletion requests find all copies.

## Collect With Purpose

Require stated purpose per PII field. Reject speculative collection. Keep PII out of logs, telemetry, error bodies, analytics events, and model context windows.

## Retain Then Delete

Assign TTL per store including backups, caches, search indexes, queues, and analytics copies. Implement working delete path end-to-end, not flag-only. Verify with export-then-delete drill on dummy account.

## Rights and Sharing

Support export, correct, delete flows for applicable regimes (GDPR, CCPA, LGPD). Gate third-party sharing (analytics, ad, LLM vendor) on consent plus processing agreement. Keep region as configurable policy, not hardcoded assumption.

## Scoring Link

Unmapped PII deducts under Hygiene. Missing TTL or delete path deducts per store. PII in logs/telemetry deducts under Secrets/Exposure. State deduction per dimension in scorecard math.
