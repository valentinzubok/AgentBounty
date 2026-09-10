# AgentBounty — Intelligent Contracts submission pack

**Type:** Builder → **Intelligent Contracts** (NOT Project)

## Lesson from rejections

| Mistake | Fix here |
|---------|----------|
| Full Next.js wallet app in same repo as IC | **This repo has NO `web/`** — contract + tests + docs only |
| Explorer address ≠ repo code | Redeploy from THIS file tomorrow; paste NEW address |
| Tx links as "contract links" | Only `/address/0x…` in contract field; txs in notes |

Project UI lives separately in **AgentBountyDesk** (submit under Projects).

## Studio smoke (fill tomorrow)

| Step | Method | Tx / result |
|------|--------|-------------|
| Deploy | ctor = your wallet | `ADDRESS=` |
| credit | `credit(you, "1000")` | |
| post | `post_bounty("demo-1", 0x2222…, "Deliver hello", "100")` | worker ≠ client |
| fund | `fund("demo-1")` | |
| submit | Account2 `submit_work("demo-1", hello.html)` | OR skip if single wallet — use Pitch path below |
| Pitch path (1 wallet) | After post+fund with fake worker, steward reads views | |

Fixture URL:
```text
https://test-server.genlayer.com/static/genvm/hello.html
```

Fake worker (allowed): `0x2222222222222222222222222222222222222222`

### Pitch views (single wallet)
```text
get_bounty("demo-1")
list_ids()
get_stats()
get_owner()
```

For full adjudicate path need Account 2 as worker → submit_work → dispute → adjudicate.

## Title
```text
AgentBounty — task bounty with frozen delivery + LLM pay_worker consensus
```

## Notes
```text
AgentBounty escrows bookkeeping units for a task bounty. Client posts terms + amount, funds escrow, worker submit_work freezes delivery_url under eq_principle_strict_eq (get_webpage SHA-256). Client accept (happy path) or dispute → adjudicate: validators LLM-agree on {"pay_worker": bool} via prompt_comparative — pay worker or refund client.

Lifecycle: credit → post_bounty → fund → submit_work → accept | dispute → adjudicate.

IC-only repository (no wallet dApp). Console Project is separate: AgentBountyDesk.

Studionet: REPLACE_ADDRESS
Deploy: REPLACE_DEPLOY_TX
Source: contracts/AgentBounty.py
GitHub: https://github.com/valentinzubok/AgentBounty
```

## Evidence
1. GitHub repo (IC-only)
2. contracts/AgentBounty.py blob
3. Explorer `/address/0x…` (must match this source)
4. Deploy tx
5. fund or submit_work tx (if available)
6. get_bounty view screenshot optional

## Local verify
```bash
cd AgentBounty && python3 -m pytest -q
```
