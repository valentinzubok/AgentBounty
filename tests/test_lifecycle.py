from pathlib import Path

import pytest

from conftest import load_contract

ROOT = Path(__file__).resolve().parents[1]
OWNER = "0x1111111111111111111111111111111111111111"
WORKER = "0x2222222222222222222222222222222222222222"
FIXTURE = "https://test-server.genlayer.com/static/genvm/hello.html"


@pytest.fixture
def mod(monkeypatch):
    m = load_contract(ROOT)
    return m


@pytest.fixture
def c(mod):
    import sys

    gl = sys.modules["genlayer"]
    gl.message.sender_address = OWNER
    return mod.AgentBounty(OWNER)


def test_lifecycle_accept(c, mod):
    import sys

    gl = sys.modules["genlayer"]
    c.credit(OWNER, "1000")
    c.post_bounty("b1", WORKER, "Deliver hello page content", "100")
    c.fund("b1")
    gl.message.sender_address = WORKER
    c.submit_work("b1", FIXTURE)
    gl.message.sender_address = OWNER
    c.accept("b1")
    import json

    b = json.loads(c.get_bounty("b1"))
    assert b["status"] == "accepted"
    assert b["delivery_hash"]


def test_dispute_adjudicate_pay(c, mod):
    import json
    import sys

    gl = sys.modules["genlayer"]
    c.credit(OWNER, "500")
    c.post_bounty("b2", WORKER, "Deliver hello page", "50")
    c.fund("b2")
    gl.message.sender_address = WORKER
    c.submit_work("b2", FIXTURE)
    gl.message.sender_address = OWNER
    c.dispute("b2", "Check delivery matches terms")
    c.adjudicate("b2")
    b = json.loads(c.get_bounty("b2"))
    assert b["status"] == "paid"
    assert b["pay_worker"] is True


def test_worker_cannot_be_client(c):
    c.credit(OWNER, "100")
    with pytest.raises(Exception, match="worker cannot"):
        c.post_bounty("bad", OWNER, "terms here", "10")
