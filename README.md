# AgentBounty

<p align="center">
  <strong>Task bounty escrow — freeze delivery, then LLM-settle pay_worker under GenLayer consensus.</strong>
</p>

<p align="center">
  <a href="https://docs.genlayer.com/"><img src="https://img.shields.io/badge/GenLayer-Intelligent%20Contract-0ea5a0?style=flat-square" alt="GenLayer" /></a>
  <a href="https://studio.genlayer.com/contracts"><img src="https://img.shields.io/badge/Studio-deployable-111827?style=flat-square" alt="Studio" /></a>
  <a href="https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36"><img src="https://img.shields.io/badge/Studionet-live-14b8a6?style=flat-square" alt="Studionet" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="MIT" /></a>
</p>

| | |
|---|---|
| **Contract** | [`0xAf7e3250b6F6711FA279f665660a751631CF2d36`](https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36) |
| **Source** | [`contracts/AgentBounty.py`](contracts/AgentBounty.py) |
| **Portal type** | **Intelligent Contracts** (this repo is IC-only — no wallet dApp) |
| **Console Project** | separate repo: `AgentBountyDesk` |

---

## Why it exists

Agent task markets need escrow that does not chase a rotting live delivery URL. **AgentBounty** freezes the worker delivery page under SHA-256 consensus, then settles with GenLayer LLMs on `{"pay_worker": bool}` only.

```text
credit → post_bounty → fund → submit_work (freeze) → accept | dispute → adjudicate
```

---

## Features

| Method | Kind | Detail |
|--------|------|--------|
| `credit` | write · owner | Bookkeeping mint for demos |
| `post_bounty` | write | Client posts terms; **worker ≠ client** |
| `fund` | write | Lock client units into escrow |
| `submit_work` | write | Worker freezes `delivery_url` via `get_webpage` + `eq_principle_strict_eq` |
| `accept` | write | Happy path — pay worker |
| `dispute` + `adjudicate` | write | LLM `prompt_comparative` on `pay_worker` |
| `get_bounty` / `list_ids` / `get_stats` / `get_balance` / `get_owner` | view | Steward reads |

---

## Live Studionet smoke

| Step | Result |
|------|--------|
| Deploy | [`0xb7b32543…`](https://explorer-studio.genlayer.com/tx/0xb7b325432986836dc24652ed695c2200e035d2a1bb9d9a110d94dfdb1386ef7e) |
| `credit` | [`0xfeb31f1c…`](https://explorer-studio.genlayer.com/tx/0xfeb31f1c955d1cfd8a6a8ae33768ba2f847e9582c34050b00747c2f9ff83c6d4) |
| `post_bounty(demo-1)` | [`0x84eb8aaf…`](https://explorer-studio.genlayer.com/tx/0x84eb8aafe30288769550e126ab0e5f60f7891f94bc165723d77f8a7cefc583c8) |
| `fund(demo-1)` | [`0xcea52358…`](https://explorer-studio.genlayer.com/tx/0xcea523584a1fdcc0fa78b5d7946e98d715d6044820e0ce284cce14ebb0896fd9) |
| `get_bounty("demo-1")` | `status: funded`, amount `100`, worker `0x2222…` |

Full record: [`DEPLOY.md`](DEPLOY.md) · Portal paste: [`SUBMIT.md`](SUBMIT.md)

---

## Quick start (Studio)

1. Open [studio.genlayer.com/contracts](https://studio.genlayer.com/contracts)
2. Paste [`contracts/AgentBounty.py`](contracts/AgentBounty.py)
3. Constructor = your wallet `0x…`
4. Follow [`docs/STUDIO.md`](docs/STUDIO.md)

Demo listing / delivery fixture:

```text
https://test-server.genlayer.com/static/genvm/hello.html
```

Placeholder worker (≠ client):

```text
0x2222222222222222222222222222222222222222
```

---

## Local tests

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

---

## License

MIT — [`LICENSE`](LICENSE) · © 2026 Valentyn Zubok
