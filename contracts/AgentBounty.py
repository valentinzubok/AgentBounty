# { "Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0" }

from genlayer import *
import hashlib
import json
import re

# AgentBounty — task bounty with frozen delivery URL + LLM pay/refund consensus.
# Copyright (c) 2026 Valentyn Zubok. MIT License.
#
# Lifecycle:
#   credit → post_bounty → fund → submit_work (freeze delivery) →
#   accept | dispute → adjudicate ({"pay_worker": bool})
#
# Bookkeeping units only (Studionet). Consensus compares pay_worker boolean only.
# IC-only packaging: no wallet dApp in this repository (submit under Intelligent Contracts).

MAX_ID_LEN = 64
MAX_TERMS_LEN = 1200
MAX_CLAIM_LEN = 600
MAX_AMOUNT = 1_000_000_000
PREVIEW_CHARS = 280
HASH_ALGO = "sha256"

STATUS_OPEN = "open"
STATUS_FUNDED = "funded"
STATUS_SUBMITTED = "submitted"
STATUS_ACCEPTED = "accepted"
STATUS_DISPUTED = "disputed"
STATUS_PAID = "paid"
STATUS_REFUNDED = "refunded"

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
HTTPS_URL_RE = re.compile(r"^https://[^\s<>\"']+$", re.IGNORECASE)


def _normalize_id(bounty_id: str) -> str:
    bid = str(bounty_id).strip()
    if not bid:
        raise Exception("bounty_id is required")
    if len(bid) > MAX_ID_LEN:
        raise Exception("bounty_id exceeds 64 chars")
    for ch in bid:
        ok = ("a" <= ch.lower() <= "z") or ("0" <= ch <= "9") or ch in "-_/"
        if not ok:
            raise Exception("bounty_id: only a-z, 0-9, -, _, /")
    return bid


def _require_address(label: str, value: str) -> str:
    addr = str(value).strip()
    if not ADDR_RE.match(addr):
        raise Exception(f"{label} must be a 0x address")
    return addr


def _parse_amount(amount) -> int:
    try:
        amt = int(str(amount).strip())
    except Exception:
        raise Exception("amount must be a positive integer")
    if amt <= 0:
        raise Exception("amount must be positive")
    if amt > MAX_AMOUNT:
        raise Exception("amount exceeds max")
    return amt


def _sanitize_text(label: str, text: str, max_len: int) -> str:
    cleaned = " ".join(str(text).split())
    if not cleaned:
        raise Exception(f"{label} is required")
    if len(cleaned) > max_len:
        raise Exception(f"{label} exceeds {max_len} chars")
    return cleaned


def _require_https(url: str) -> str:
    u = str(url).strip()
    if not HTTPS_URL_RE.match(u):
        raise Exception("url must be https:// with no whitespace")
    if len(u) > 2048:
        raise Exception("url exceeds 2048 chars")
    return u


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize(text: str) -> str:
    return " ".join(str(text).split())


def _capture_page(url: str) -> str:
    entry = {
        "url": url,
        "content_hash": "",
        "hash_algo": HASH_ALGO,
        "preview": "",
        "byte_len": 0,
        "status": "error",
    }
    try:
        raw = gl.get_webpage(url, mode="text")
        if raw is None or str(raw).strip() == "":
            raw = gl.get_webpage(url, mode="html")
        normalized = _normalize(raw if raw is not None else "")
        if normalized == "":
            entry["status"] = "empty"
        else:
            entry["content_hash"] = _hash_text(normalized)
            entry["preview"] = normalized[:PREVIEW_CHARS]
            entry["byte_len"] = len(normalized)
            entry["status"] = "ok"
    except Exception as exc:
        entry["preview"] = str(exc)[:120]
        entry["status"] = "error"
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _judge_pay(terms: str, claim: str, preview: str) -> str:
    judge = (
        "You are a GenLayer bounty adjudicator.\n"
        "Decide if the worker DELIVERY satisfies the bounty TERMS.\n"
        "Return ONLY JSON: {\"pay_worker\": true|false}\n"
        "true = pay the worker; false = refund the client.\n"
        f"TERMS:\n{terms}\n\n"
        f"CLIENT_CLAIM:\n{claim}\n\n"
        f"FROZEN_DELIVERY_PREVIEW:\n{preview}\n"
    )
    try:
        out = gl.nondet.exec_prompt(judge, response_format="json")
    except Exception:
        out = gl.exec_prompt(judge)
    if isinstance(out, dict):
        return json.dumps(
            {"pay_worker": bool(out.get("pay_worker", False))},
            sort_keys=True,
            separators=(",", ":"),
        )
    try:
        parsed = json.loads(str(out))
        return json.dumps(
            {"pay_worker": bool(parsed.get("pay_worker", False))},
            sort_keys=True,
            separators=(",", ":"),
        )
    except Exception:
        return json.dumps({"pay_worker": False}, sort_keys=True, separators=(",", ":"))


class AgentBounty(gl.Contract):
    owner: str
    balances_json: str
    bounties_json: str
    order_json: str
    events_json: str

    def __init__(self, owner: str):
        self.owner = _require_address("owner", owner)
        self.balances_json = "{}"
        self.bounties_json = "{}"
        self.order_json = "[]"
        self.events_json = "[]"

    def _load(self, field: str):
        raw = getattr(self, field)
        return json.loads(raw) if raw else ({} if field != "order_json" and field != "events_json" else [])

    def _save(self, field: str, data) -> None:
        setattr(self, field, json.dumps(data, separators=(",", ":")))

    def _only_owner(self):
        if str(gl.message.sender_address) != self.owner:
            raise Exception("only owner")

    def _balance_of(self, balances, user: str) -> dict:
        key = str(user)
        if key not in balances:
            balances[key] = {"available": 0, "escrowed": 0}
        return balances[key]

    def _append_event(self, name: str, payload: dict) -> None:
        events = self._load("events_json")
        events.append({"event": name, **payload})
        if len(events) > 200:
            events = events[-200:]
        self._save("events_json", events)

    @gl.public.write
    def credit(self, user: str, amount: str) -> None:
        self._only_owner()
        addr = _require_address("user", user)
        amt = _parse_amount(amount)
        balances = self._load("balances_json")
        row = self._balance_of(balances, addr)
        row["available"] = int(row.get("available", 0)) + amt
        balances[addr] = row
        self._save("balances_json", balances)
        self._append_event("Credited", {"user": addr, "amount": amt})

    @gl.public.write
    def post_bounty(self, bounty_id: str, worker: str, terms: str, amount: str) -> None:
        client = str(gl.message.sender_address)
        bid = _normalize_id(bounty_id)
        worker_addr = _require_address("worker", worker)
        if worker_addr == client:
            raise Exception("worker cannot be the client")
        terms_txt = _sanitize_text("terms", terms, MAX_TERMS_LEN)
        amt = _parse_amount(amount)

        bounties = self._load("bounties_json")
        if bid in bounties:
            raise Exception("bounty_id already exists")

        bounties[bid] = {
            "bounty_id": bid,
            "client": client,
            "worker": worker_addr,
            "terms": terms_txt,
            "amount": amt,
            "status": STATUS_OPEN,
            "delivery_url": "",
            "delivery_hash": "",
            "delivery_preview": "",
            "claim": "",
            "pay_worker": False,
        }
        self._save("bounties_json", bounties)
        order = self._load("order_json")
        order.append(bid)
        self._save("order_json", order)
        self._append_event(
            "BountyPosted",
            {"id": bid, "client": client, "worker": worker_addr, "amount": amt},
        )

    @gl.public.write
    def fund(self, bounty_id: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_OPEN:
            raise Exception("bounty is not open")
        client = str(gl.message.sender_address)
        if client != entry["client"]:
            raise Exception("only client may fund")

        amt = int(entry["amount"])
        balances = self._load("balances_json")
        row = self._balance_of(balances, client)
        if int(row.get("available", 0)) < amt:
            raise Exception("insufficient balance")
        row["available"] = int(row["available"]) - amt
        row["escrowed"] = int(row.get("escrowed", 0)) + amt
        balances[client] = row
        self._save("balances_json", balances)

        entry["status"] = STATUS_FUNDED
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event("BountyFunded", {"id": bid, "amount": amt})

    @gl.public.write
    def submit_work(self, bounty_id: str, delivery_url: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_FUNDED:
            raise Exception("bounty is not funded")
        worker = str(gl.message.sender_address)
        if worker != entry["worker"]:
            raise Exception("only worker may submit")

        url = _require_https(delivery_url)

        def fetch_fn() -> str:
            return _capture_page(url)

        snap_json = gl.eq_principle_strict_eq(fetch_fn)
        snap = json.loads(snap_json)
        if snap.get("status") != "ok":
            raise Exception("delivery_url fetch failed or empty")

        entry["delivery_url"] = url
        entry["delivery_hash"] = snap.get("content_hash", "")
        entry["delivery_preview"] = snap.get("preview", "")
        entry["status"] = STATUS_SUBMITTED
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "WorkSubmitted",
            {"id": bid, "url": url, "hash": entry["delivery_hash"]},
        )

    @gl.public.write
    def accept(self, bounty_id: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_SUBMITTED:
            raise Exception("bounty is not submitted")
        if str(gl.message.sender_address) != entry["client"]:
            raise Exception("only client may accept")

        amt = int(entry["amount"])
        balances = self._load("balances_json")
        client_row = self._balance_of(balances, entry["client"])
        client_row["escrowed"] = max(0, int(client_row.get("escrowed", 0)) - amt)
        balances[entry["client"]] = client_row
        worker_row = self._balance_of(balances, entry["worker"])
        worker_row["available"] = int(worker_row.get("available", 0)) + amt
        balances[entry["worker"]] = worker_row
        self._save("balances_json", balances)

        entry["status"] = STATUS_ACCEPTED
        entry["pay_worker"] = True
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event("BountyAccepted", {"id": bid, "amount": amt})

    @gl.public.write
    def dispute(self, bounty_id: str, claim: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_SUBMITTED:
            raise Exception("bounty is not submitted")
        if str(gl.message.sender_address) != entry["client"]:
            raise Exception("only client may dispute")
        entry["claim"] = _sanitize_text("claim", claim, MAX_CLAIM_LEN)
        entry["status"] = STATUS_DISPUTED
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event("BountyDisputed", {"id": bid, "claim": entry["claim"]})

    @gl.public.write
    def adjudicate(self, bounty_id: str) -> None:
        """LLM judges frozen delivery vs terms. Consensus on pay_worker bool only."""
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_DISPUTED:
            raise Exception("bounty is not disputed")
        if not entry.get("delivery_preview"):
            raise Exception("missing frozen delivery")

        terms = entry.get("terms", "")
        claim = entry.get("claim", "")
        preview = entry.get("delivery_preview", "")

        def leader_fn() -> str:
            return _judge_pay(terms, claim, preview)

        try:
            verdict_json = gl.eq_principle.prompt_comparative(
                leader_fn,
                principle="boolean field pay_worker must be identical across validators",
            )
        except Exception:
            verdict_json = gl.eq_principle_strict_eq(leader_fn)

        verdict = json.loads(verdict_json) if isinstance(verdict_json, str) else verdict_json
        if not isinstance(verdict, dict):
            verdict = {"pay_worker": False}
        pay = bool(verdict.get("pay_worker", False))

        amt = int(entry["amount"])
        balances = self._load("balances_json")
        client_row = self._balance_of(balances, entry["client"])
        client_row["escrowed"] = max(0, int(client_row.get("escrowed", 0)) - amt)
        balances[entry["client"]] = client_row

        if pay:
            worker_row = self._balance_of(balances, entry["worker"])
            worker_row["available"] = int(worker_row.get("available", 0)) + amt
            balances[entry["worker"]] = worker_row
            entry["status"] = STATUS_PAID
        else:
            client_row["available"] = int(client_row.get("available", 0)) + amt
            balances[entry["client"]] = client_row
            entry["status"] = STATUS_REFUNDED

        self._save("balances_json", balances)
        entry["pay_worker"] = pay
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "BountyAdjudicated",
            {"id": bid, "pay_worker": pay, "status": entry["status"], "amount": amt},
        )

    @gl.public.view
    def get_bounty(self, bounty_id: str) -> str:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            return json.dumps({"error": "unknown bounty_id"})
        return json.dumps(bounties[bid])

    @gl.public.view
    def get_balance(self, user: str) -> str:
        addr = _require_address("user", user)
        balances = self._load("balances_json")
        row = balances.get(addr, {"available": 0, "escrowed": 0})
        return json.dumps({"user": addr, **row})

    @gl.public.view
    def list_ids(self) -> str:
        return json.dumps(self._load("order_json"))

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner

    @gl.public.view
    def get_stats(self) -> str:
        bounties = self._load("bounties_json")
        counts = {}
        for b in bounties.values():
            st = b.get("status", "?")
            counts[st] = counts.get(st, 0) + 1
        return json.dumps({"total": len(bounties), "by_status": counts})
