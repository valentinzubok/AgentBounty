# AgentBounty — Intelligent Contracts submission pack

**Type:** Builder → **Intelligent Contracts** (NOT Project)

This repository is **IC-only** (contract + tests + docs). No wallet dApp.

## Studionet (DONE)

| Item | Value |
|------|--------|
| Address | [`0xAf7e3250b6F6711FA279f665660a751631CF2d36`](https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36) |
| Deploy | [`0xb7b32543…`](https://explorer-studio.genlayer.com/tx/0xb7b325432986836dc24652ed695c2200e035d2a1bb9d9a110d94dfdb1386ef7e) |
| credit | [`0xfeb31f1c…`](https://explorer-studio.genlayer.com/tx/0xfeb31f1c955d1cfd8a6a8ae33768ba2f847e9582c34050b00747c2f9ff83c6d4) |
| post_bounty | [`0x84eb8aaf…`](https://explorer-studio.genlayer.com/tx/0x84eb8aafe30288769550e126ab0e5f60f7891f94bc165723d77f8a7cefc583c8) |
| fund | [`0xcea52358…`](https://explorer-studio.genlayer.com/tx/0xcea523584a1fdcc0fa78b5d7946e98d715d6044820e0ce284cce14ebb0896fd9) |
| Read | `get_bounty("demo-1")` → `status: funded` |

## Title

```text
AgentBounty — task bounty with frozen delivery + LLM pay_worker consensus
```

## Notes

```text
AgentBounty escrows bookkeeping units for a task bounty. Client posts terms + amount, funds escrow, worker submit_work freezes delivery_url under eq_principle_strict_eq (get_webpage SHA-256). Client accept (happy path) or dispute → adjudicate: validators LLM-agree on {"pay_worker": bool} via prompt_comparative — pay worker or refund client.

Lifecycle: credit → post_bounty → fund → submit_work → accept | dispute → adjudicate.

IC-only repository (no wallet dApp). Console Project is separate: AgentBountyDesk.

Studionet: 0xAf7e3250b6F6711FA279f665660a751631CF2d36
Deploy: 0xb7b325432986836dc24652ed695c2200e035d2a1bb9d9a110d94dfdb1386ef7e
credit: 0xfeb31f1c955d1cfd8a6a8ae33768ba2f847e9582c34050b00747c2f9ff83c6d4
post_bounty: 0x84eb8aafe30288769550e126ab0e5f60f7891f94bc165723d77f8a7cefc583c8
fund: 0xcea523584a1fdcc0fa78b5d7946e98d715d6044820e0ce284cce14ebb0896fd9
get_bounty(demo-1) → status funded, amount 100, worker 0x2222…

Source: contracts/AgentBounty.py
GitHub: https://github.com/valentinzubok/AgentBounty
License: MIT
```

## Evidence

1. https://github.com/valentinzubok/AgentBounty
2. https://github.com/valentinzubok/AgentBounty/blob/main/contracts/AgentBounty.py
3. https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36
4. https://explorer-studio.genlayer.com/tx/0xb7b325432986836dc24652ed695c2200e035d2a1bb9d9a110d94dfdb1386ef7e
5. https://explorer-studio.genlayer.com/tx/0x84eb8aafe30288769550e126ab0e5f60f7891f94bc165723d77f8a7cefc583c8
6. https://explorer-studio.genlayer.com/tx/0xcea523584a1fdcc0fa78b5d7946e98d715d6044820e0ce284cce14ebb0896fd9

## Contract link (Portal — address only)

```text
https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36
```
