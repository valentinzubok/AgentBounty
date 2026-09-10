# AgentBounty method map

| Method | Type | Args | Notes |
|--------|------|------|-------|
| `credit` | write | user, amount | onlyOwner |
| `post_bounty` | write | bounty_id, worker, terms, amount | worker ≠ client |
| `fund` | write | bounty_id | client only |
| `submit_work` | write | bounty_id, delivery_url | worker; freezes URL |
| `accept` | write | bounty_id | client; pay worker |
| `dispute` | write | bounty_id, claim | client |
| `adjudicate` | write | bounty_id | LLM on frozen delivery |
| `get_bounty` | view | bounty_id | JSON |
| `get_balance` | view | user | JSON |
| `list_ids` | view | — | JSON array |
| `get_stats` | view | — | by_status counts |
| `get_owner` | view | — | address |
