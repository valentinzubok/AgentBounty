# AgentBounty

<p align="center">
  <strong>Task bounty escrow — freeze delivery, then LLM-settle pay_worker under GenLayer consensus.</strong>
</p>

<p align="center">
  <a href="https://docs.genlayer.com/"><img src="https://img.shields.io/badge/GenLayer-Intelligent%20Contract-0ea5a0?style=flat-square" alt="GenLayer" /></a>
  <a href="https://studio.genlayer.com/contracts"><img src="https://img.shields.io/badge/Studio-deployable-111827?style=flat-square" alt="Studio" /></a>
  <a href="https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268"><img src="https://img.shields.io/badge/Studionet-live-14b8a6?style=flat-square" alt="Studionet" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="MIT" /></a>
</p>

| | |
|---|---|
| **Contract** | [`0xEFf281347418bf1f045b59AA7B28f7a781e4e268`](https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268) |
| **Source** | [`contracts/AgentBounty.py`](contracts/AgentBounty.py) |
| **Portal type** | **Intelligent Contracts** (this repo is IC-only — no wallet dApp) |
| **Console Project** | separate repo: `AgentBountyDesk` |

---

## Why it exists

Agent task markets need escrow that does not chase a rotting live delivery URL. **AgentBounty** freezes the worker delivery page under SHA-256 consensus, then settles with GenLayer LLMs on `{"pay_worker": bool}` only.

```text
credit → post_bounty → fund → submit_work (freeze body) →
  accept | dispute → adjudicate |
  cancel_funded (worker idle) | timeout_release (client idle)
```

---

## Features

| Method | Kind | Detail |
|--------|------|--------|
| `credit` | write · owner | Bookkeeping mint for demos |
| `post_bounty` | write | Client posts terms; **worker ≠ client**; addresses lowercased |
| `fund` | write | Lock escrow; starts bounded worker submit window |
| `submit_work` | write | Freeze delivery **body** (8k) + hash under `eq_principle_strict_eq` |
| `accept` | write | Happy path — pay worker |
| `dispute` + `adjudicate` | write | LLM on frozen body+hash; `pay_worker` must be JSON bool |
| `cancel_funded` | write | Client refund if worker misses submit window |
| `timeout_release` | write | Worker payout if client misses accept/dispute window |
| `get_bounty` / `list_ids` / `get_stats` / `get_balance` / `get_owner` | view | Steward reads |

---

## Live Studionet smoke

| Step | Result |
|------|--------|
| Deploy | [`0xecda7c65…`](https://explorer-studio.genlayer.com/tx/0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1) |
| `credit` | [`0xb09ed292…`](https://explorer-studio.genlayer.com/tx/0xb09ed292214d61299fce8d9b9846d5d8648812e40bf34f7b801316eac82e5921) |
| `post_bounty(demo-1)` | [`0xf53e154b…`](https://explorer-studio.genlayer.com/tx/0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8) |
| `fund(demo-1)` | [`0x5688f3bc…`](https://explorer-studio.genlayer.com/tx/0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb) |
| `get_bounty("demo-1")` | `status: funded`, amount `1000`, worker `0x2222…`, `worker_deadline` set |

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
