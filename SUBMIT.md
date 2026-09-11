# AgentBounty — Intelligent Contracts submission pack

**Type:** Builder → **Intelligent Contracts** (NOT Project)

This repository is **IC-only** (contract + tests + docs). No wallet dApp.

## Steward revision (Sep 11, 2026) — LIVE

Matching GitHub source + Studionet redeploy addressing steward blockers.

| Steward ask | Fix |
|-------------|-----|
| (1) Sufficient frozen evidence | `delivery_body` ≤8k + hash; adjudicate uses evidence blob |
| (2) Literal `pay_worker` bool | Non-bool → fail-safe `false` |
| (3) Canonicalize addresses | lowercase `0x` via `_require_address` / `_sender` |
| (4) Bounded recovery | `cancel_funded` + `timeout_release` (7-day windows) |

## Studionet (DONE)

| Item | Value |
|------|--------|
| Address | [`0xEFf281347418bf1f045b59AA7B28f7a781e4e268`](https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268) |
| Deploy | [`0xecda7c65…`](https://explorer-studio.genlayer.com/tx/0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1) |
| credit | [`0xb09ed292…`](https://explorer-studio.genlayer.com/tx/0xb09ed292214d61299fce8d9b9846d5d8648812e40bf34f7b801316eac82e5921) |
| post_bounty | [`0xf53e154b…`](https://explorer-studio.genlayer.com/tx/0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8) |
| fund | [`0x5688f3bc…`](https://explorer-studio.genlayer.com/tx/0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb) |
| Read | `get_bounty("demo-1")` → `status: funded`, amount `1000`, `delivery_body` field present, `worker_deadline` set |

## Title

```text
AgentBounty — task bounty with frozen delivery + LLM pay_worker consensus
```

## Notes

```text
AgentBounty escrows bookkeeping units for a task bounty. Client posts terms + amount, funds escrow, worker submit_work freezes delivery under eq_principle_strict_eq (get_webpage SHA-256 of normalized page). Adjudication uses the bounded frozen delivery_body (up to 8k chars) + content_hash — not the 280-char UI preview alone. Client accept (happy path) or dispute → adjudicate: validators LLM-agree on {"pay_worker": bool} via prompt_comparative. pay_worker is accepted only as a literal JSON boolean; any other type fails safe to false (refund). All addresses are canonicalized to lowercase 0x-hex before storage and comparison. Bounded recovery: cancel_funded refunds the client if the worker misses the submit window after fund; timeout_release pays the worker if the client misses accept/dispute after submit (default 7-day windows via GenVM tx clock).

Lifecycle: credit → post_bounty → fund → submit_work → accept | dispute → adjudicate | cancel_funded | timeout_release.

IC-only repository (no wallet dApp). Console Project is separate: AgentBountyDesk.

Studionet: 0xEFf281347418bf1f045b59AA7B28f7a781e4e268
Deploy: 0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1
credit: 0xb09ed292214d61299fce8d9b9846d5d8648812e40bf34f7b801316eac82e5921
post_bounty: 0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8
fund: 0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb
get_bounty(demo-1) → status funded, amount 1000, worker 0x2222…, worker_deadline set

Source: contracts/AgentBounty.py
GitHub: https://github.com/valentinzubok/AgentBounty
License: MIT
```

## Steward reply (portal)

```text
Updated AgentBounty.py + redeployed matching Studionet source:

1) adjudicate now judges frozen delivery_body (≤8k) + content_hash/byte_len/url — not the 280-char preview alone
2) pay_worker accepted only as JSON boolean literal; otherwise fail-safe false
3) all addresses lowercased via _require_address / _sender before store/compare
4) cancel_funded (funded + worker idle past worker_deadline) and timeout_release (submitted + client idle past client_deadline)

GitHub: https://github.com/valentinzubok/AgentBounty/blob/main/contracts/AgentBounty.py
Studionet: 0xEFf281347418bf1f045b59AA7B28f7a781e4e268
Deploy tx: 0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1
credit: 0xb09ed292214d61299fce8d9b9846d5d8648812e40bf34f7b801316eac82e5921
post_bounty: 0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8
fund: 0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb
get_bounty(demo-1) → status funded (delivery_body + worker_deadline fields present)
```

## Evidence

1. https://github.com/valentinzubok/AgentBounty
2. https://github.com/valentinzubok/AgentBounty/blob/main/contracts/AgentBounty.py
3. https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268
4. https://explorer-studio.genlayer.com/tx/0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1
5. https://explorer-studio.genlayer.com/tx/0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8
6. https://explorer-studio.genlayer.com/tx/0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb

## Contract link (Portal — address only)

```text
https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268
```
