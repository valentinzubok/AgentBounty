from pathlib import Path

import json
import pytest

from conftest import load_contract

ROOT = Path(__file__).resolve().parents[1]
OWNER = "0x1111111111111111111111111111111111111111"
WORKER = "0x2222222222222222222222222222222222222222"
FIXTURE = "https://test-server.genlayer.com/static/genvm/hello.html"


@pytest.fixture
def mod(monkeypatch):
    return load_contract(ROOT)


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
    b = json.loads(c.get_bounty("b1"))
    assert b["status"] == "accepted"
    assert b["delivery_hash"]
    assert b["delivery_body"]
    assert len(b["delivery_body"]) >= len(b["delivery_preview"])


def test_dispute_adjudicate_pay(c, mod):
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


def test_addresses_canonicalized_lowercase(c, mod):
    import sys

    gl = sys.modules["genlayer"]
    mixed_owner = "0xAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAa"
    mixed_worker = "0xBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBb"
    gl.message.sender_address = mixed_owner
    contract = mod.AgentBounty(mixed_owner)
    assert contract.get_owner() == mixed_owner.lower()
    contract.credit(mixed_owner, "100")
    contract.post_bounty("canon", mixed_worker, "Deliver hello page", "10")
    b = json.loads(contract.get_bounty("canon"))
    assert b["client"] == mixed_owner.lower()
    assert b["worker"] == mixed_worker.lower()
    bal = json.loads(contract.get_balance(mixed_owner))
    assert bal["user"] == mixed_owner.lower()
    assert bal["available"] == 100


def test_pay_worker_rejects_non_literal_bool(mod):
    assert mod._literal_pay_worker(True) is True
    assert mod._literal_pay_worker(False) is False
    assert mod._literal_pay_worker("true") is False
    assert mod._literal_pay_worker(1) is False
    assert mod._literal_pay_worker(None) is False


def test_adjudicate_uses_frozen_body_not_preview_alone(c, mod, monkeypatch):
    import sys

    gl = sys.modules["genlayer"]
    long_body = ("Hello world delivery evidence " * 40).strip()
    gl.get_webpage = lambda url, mode="text": long_body

    seen = {}

    def capture_judge(terms, claim, evidence):
        seen["evidence"] = evidence
        return json.dumps({"pay_worker": True}, sort_keys=True, separators=(",", ":"))

    monkeypatch.setattr(mod, "_judge_pay", capture_judge)

    c.credit(OWNER, "200")
    c.post_bounty("b3", WORKER, "Deliver hello page", "20")
    c.fund("b3")
    gl.message.sender_address = WORKER
    c.submit_work("b3", FIXTURE)
    gl.message.sender_address = OWNER
    c.dispute("b3", "verify frozen body")
    c.adjudicate("b3")

    b = json.loads(c.get_bounty("b3"))
    assert "frozen_body:" in seen["evidence"]
    assert b["delivery_hash"] in seen["evidence"]
    assert long_body[:500] in seen["evidence"]
    assert len(seen["evidence"]) > 280


def test_cancel_funded_after_worker_deadline(c, mod, monkeypatch):
    import sys

    gl = sys.modules["genlayer"]
    monkeypatch.setattr(mod, "WORKER_ACTION_SECS", 10)
    clock = {"t": 1_700_000_000}
    monkeypatch.setattr(mod, "_now_ts", lambda: clock["t"])

    c.credit(OWNER, "300")
    c.post_bounty("idle-w", WORKER, "Deliver hello page", "30")
    c.fund("idle-w")
    b = json.loads(c.get_bounty("idle-w"))
    assert b["status"] == "funded"
    assert b["worker_deadline"] == clock["t"] + 10

    with pytest.raises(Exception, match="worker action window still open"):
        c.cancel_funded("idle-w")

    clock["t"] = b["worker_deadline"]
    c.cancel_funded("idle-w")
    b2 = json.loads(c.get_bounty("idle-w"))
    assert b2["status"] == "cancelled"
    bal = json.loads(c.get_balance(OWNER))
    assert bal["available"] == 300
    assert bal["escrowed"] == 0


def test_timeout_release_after_client_deadline(c, mod, monkeypatch):
    import sys

    gl = sys.modules["genlayer"]
    monkeypatch.setattr(mod, "CLIENT_ACTION_SECS", 10)
    clock = {"t": 1_700_000_000}
    monkeypatch.setattr(mod, "_now_ts", lambda: clock["t"])

    c.credit(OWNER, "400")
    c.post_bounty("idle-c", WORKER, "Deliver hello page", "40")
    c.fund("idle-c")
    gl.message.sender_address = WORKER
    c.submit_work("idle-c", FIXTURE)
    b = json.loads(c.get_bounty("idle-c"))
    assert b["status"] == "submitted"
    assert b["client_deadline"] == clock["t"] + 10

    with pytest.raises(Exception, match="client action window still open"):
        c.timeout_release("idle-c")

    clock["t"] = b["client_deadline"]
    c.timeout_release("idle-c")
    b2 = json.loads(c.get_bounty("idle-c"))
    assert b2["status"] == "accepted"
    assert b2["pay_worker"] is True
    wbal = json.loads(c.get_balance(WORKER))
    assert wbal["available"] == 40
