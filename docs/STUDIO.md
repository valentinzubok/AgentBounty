# Studio operator guide — AgentBounty

1. Open https://studio.genlayer.com/contracts
2. Paste `contracts/AgentBounty.py`
3. Constructor = your MetaMask address (Studionet)
4. Deploy
5. As owner: `credit(you, "1000")`
6. `post_bounty("demo-1", "0x2222222222222222222222222222222222222222", "Deliver hello page", "100")`  
   — **worker must not equal your address**
7. `fund("demo-1")`
8. Read: `get_bounty("demo-1")` → expect `status: funded`

Optional (Account 2 as worker):
- `submit_work("demo-1", "https://test-server.genlayer.com/static/genvm/hello.html")`
- client `dispute` → anyone `adjudicate`

See [`DEPLOY.md`](../DEPLOY.md) for the live Studionet record.
