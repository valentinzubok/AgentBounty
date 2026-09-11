# AgentBounty — Studionet deploy record

**Network:** GenLayer Studio / Studionet  
**Contract:** [`0xEFf281347418bf1f045b59AA7B28f7a781e4e268`](https://explorer-studio.genlayer.com/address/0xEFf281347418bf1f045b59AA7B28f7a781e4e268)  
**Owner / client:** `0x6f6077eC587f2964d30aCE8D803Edc27988046e3`  
**Source:** [`contracts/AgentBounty.py`](contracts/AgentBounty.py)  
**License:** MIT  
**Note:** Redeploy Sep 11, 2026 for steward revision (frozen body, literal bool, address canonicalize, cancel/timeout).

## Successful transactions

| Step | Method | Result | Explorer |
|------|--------|--------|----------|
| Deploy | Contract Deployment | SUCCESS | [0xecda7c65…](https://explorer-studio.genlayer.com/tx/0xecda7c658cefa376ba337bceb2a19bdff6c8eab4a50d92d746b6a79372ba5ea1) |
| Bootstrap | `credit(owner, 1000)` | SUCCESS | [0xb09ed292…](https://explorer-studio.genlayer.com/tx/0xb09ed292214d61299fce8d9b9846d5d8648812e40bf34f7b801316eac82e5921) |
| Bounty | `post_bounty(demo-1, 0x2222…, 1000)` | SUCCESS | [0xf53e154b…](https://explorer-studio.genlayer.com/tx/0xf53e154bd8c0037a752f63ab8642aaa77f795f4103e82bfb494cee01ada3c4d8) |
| Escrow | `fund(demo-1)` | SUCCESS | [0x5688f3bc…](https://explorer-studio.genlayer.com/tx/0x5688f3bc810f41b811d5474c41a8bfc6f6ae907d9d6a40d5095cf3150897d5bb) |

## Verified read: `get_bounty("demo-1")`

| Field | Value |
|-------|-------|
| status | `funded` |
| amount | `1000` |
| client | `0x6f6077ec587f2964d30ace8d803edc27988046e3` (canonicalized) |
| worker | `0x2222222222222222222222222222222222222222` |
| terms | Deliver hello page |
| delivery_body | present (empty until submit_work) |
| worker_deadline | set |

## Pitch views for stewards

```text
get_bounty("demo-1")
list_ids()
get_stats()
get_owner()
```
