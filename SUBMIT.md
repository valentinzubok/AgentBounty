# AgentBounty — Intelligent Contracts submission pack

**Type:** Builder → **Intelligent Contracts** (NOT Project)

This repository is **IC-only** (contract + tests + docs). No wallet dApp.

## Steward revision (Sep 11, 2026)

Source updated to address steward blockers. **Redeploy** this file on Studionet, then paste the new address + deploy tx below before portal Resubmit.

| Steward ask | Fix in `contracts/AgentBounty.py` |
|-------------|-----------------------------------|
| (1) Adjudicate on sufficient frozen evidence, not 280-char preview | Freeze + store `delivery_body` (8k) + hash/`byte_len`; `_judge_pay` uses evidence blob |
| (2) `pay_worker` only as literal JSON bool | `_literal_pay_worker` — non-bool → fail-safe `false` |
| (3) Canonicalize addresses | `_require_address` / `_sender` → lowercase `0x` before store/compare |
| (4) Bounded cancel/refund recovery | `cancel_funded` (worker idle) + `timeout_release` (client idle); 7-day windows |

## Studionet (REDEPLOY REQUIRED)

| Item | Value |
|------|--------|
| Address | `TBD — paste after Studio redeploy` |
| Deploy | `TBD` |
| credit | `TBD` |
| post_bounty | `TBD` |
| fund | `TBD` |
| Read | `get_bounty("demo-1")` → `status: funded` |

Previous demo (superseded by this revision):
[`0xAf7e3250…`](https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36)

## Title

```text
AgentBounty — task bounty with frozen delivery + LLM pay_worker consensus
```

## Notes (portal paste after redeploy)

```text
AgentBounty escrows bookkeeping units for a task bounty. Client posts terms + amount, funds escrow, worker submit_work freezes delivery under eq_principle_strict_eq (get_webpage SHA-256 of normalized page). Adjudication uses the bounded frozen delivery_body (up to 8k chars) + content_hash — not the 280-char UI preview alone. Client accept (happy path) or dispute → adjudicate: validators LLM-agree on {"pay_worker": bool} via prompt_comparative. pay_worker is accepted only as a literal JSON boolean; any other type fails safe to false (refund). All addresses are canonicalized to lowercase 0x-hex before storage and comparison. Bounded recovery: cancel_funded refunds the client if the worker misses the submit window after fund; timeout_release pays the worker if the client misses accept/dispute after submit (default 7-day windows via GenVM tx clock).

Lifecycle: credit → post_bounty → fund → submit_work → accept | dispute → adjudicate | cancel_funded | timeout_release.

IC-only repository (no wallet dApp). Console Project is separate: AgentBountyDesk.

Studionet: <ADDRESS>
Deploy: <DEPLOY_TX>
credit / post_bounty / fund: <TXS>
get_bounty(demo-1) → status funded

Source: contracts/AgentBounty.py
GitHub: https://github.com/valentinzubok/AgentBounty
License: MIT
```

## Steward reply (short)

```text
Updated AgentBounty.py + redeployed matching Studionet source:

1) adjudicate now judges frozen delivery_body (≤8k) + content_hash/byte_len/url — not the 280-char preview alone
2) pay_worker accepted only as JSON boolean literal; otherwise fail-safe false
3) all addresses lowercased via _require_address / _sender before store/compare
4) cancel_funded (funded + worker idle past worker_deadline) and timeout_release (submitted + client idle past client_deadline)

GitHub: https://github.com/valentinzubok/AgentBounty/blob/main/contracts/AgentBounty.py
Studionet: <ADDRESS>
Deploy tx: <DEPLOY_TX>
```

## Evidence (after redeploy)

1. https://github.com/valentinzubok/AgentBounty
2. https://github.com/valentinzubok/AgentBounty/blob/main/contracts/AgentBounty.py
3. Studionet address link
4. Deploy tx
5. post_bounty / fund txs

## Contract link (Portal — address only)

```text
https://explorer-studio.genlayer.com/address/<ADDRESS>
```
