# AgentBounty — Studionet deploy record

**Network:** GenLayer Studio / Studionet  
**Contract:** [`0xAf7e3250b6F6711FA279f665660a751631CF2d36`](https://explorer-studio.genlayer.com/address/0xAf7e3250b6F6711FA279f665660a751631CF2d36)  
**Owner / client:** `0x6f6077eC587f2964d30aCE8D803Edc27988046e3`  
**Source:** [`contracts/AgentBounty.py`](contracts/AgentBounty.py)  
**License:** MIT

## Successful transactions

| Step | Method | Result | Explorer |
|------|--------|--------|----------|
| Deploy | Contract Deployment | SUCCESS | [0xb7b32543…](https://explorer-studio.genlayer.com/tx/0xb7b325432986836dc24652ed695c2200e035d2a1bb9d9a110d94dfdb1386ef7e) |
| Bootstrap | `credit(owner, 1000)` | SUCCESS | [0xfeb31f1c…](https://explorer-studio.genlayer.com/tx/0xfeb31f1c955d1cfd8a6a8ae33768ba2f847e9582c34050b00747c2f9ff83c6d4) |
| Bounty | `post_bounty(demo-1, 0x2222…)` | SUCCESS | [0x84eb8aaf…](https://explorer-studio.genlayer.com/tx/0x84eb8aafe30288769550e126ab0e5f60f7891f94bc165723d77f8a7cefc583c8) |
| Escrow | `fund(demo-1)` | SUCCESS | [0xcea52358…](https://explorer-studio.genlayer.com/tx/0xcea523584a1fdcc0fa78b5d7946e98d715d6044820e0ce284cce14ebb0896fd9) |

## Verified read: `get_bounty("demo-1")`

| Field | Value |
|-------|-------|
| status | `funded` |
| amount | `100` |
| client | `0x6f6077eC587f2964d30aCE8D803Edc27988046e3` |
| worker | `0x2222222222222222222222222222222222222222` |
| terms | Deliver hello page |

## Failed txs (expected / documented)

| Method | Error | Note |
|--------|-------|------|
| `post_bounty` (self as worker) | `worker cannot be the client` | Use placeholder `0x2222…` |
| `fund` before successful post | `unknown bounty_id` | Cascaded |

## Pitch views for stewards

```text
get_bounty("demo-1")
list_ids()
get_stats()
get_owner()
```
