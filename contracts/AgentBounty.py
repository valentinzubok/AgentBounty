# { "Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0" }

from genlayer import *
import hashlib
import json
import re
import time

# AgentBounty — task bounty with frozen delivery URL + LLM pay/refund consensus.
# Copyright (c) 2026 Valentyn Zubok. MIT License.
#
# Lifecycle:
#   credit → post_bounty → fund → submit_work (freeze delivery body) →
#   accept | dispute → adjudicate ({"pay_worker": literal bool}) |
#   cancel_funded (worker idle) | timeout_release (client idle)
#
# Bookkeeping units only (Studionet). Consensus compares pay_worker boolean only.
# IC-only packaging: no wallet dApp in this repository (submit under Intelligent Contracts).

MAX_ID_LEN = 64
MAX_TERMS_LEN = 1200
MAX_CLAIM_LEN = 600
MAX_AMOUNT = 1_000_000_000
PREVIEW_CHARS = 280
# Adjudication uses this bounded frozen body — not the short UI preview alone.
EVIDENCE_CHARS = 8000
HASH_ALGO = "sha256"
# Bounded recovery windows (tx-pinned Unix seconds via GenVM clock).
WORKER_ACTION_SECS = 7 * 24 * 3600
CLIENT_ACTION_SECS = 7 * 24 * 3600

STATUS_OPEN = "open"
STATUS_FUNDED = "funded"
STATUS_SUBMITTED = "submitted"
STATUS_ACCEPTED = "accepted"
STATUS_DISPUTED = "disputed"
STATUS_PAID = "paid"
STATUS_REFUNDED = "refunded"
STATUS_CANCELLED = "cancelled"

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
HTTPS_URL_RE = re.compile(r"^https://[^\s<>\"']+$", re.IGNORECASE)


def _now_ts() -> int:
    """Deterministic GenVM clock (transaction datetime), not host wall clock."""
    return int(time.time())


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
    """Validate and canonicalize to lowercase 0x-hex (consistent storage/compare)."""
    addr = str(value).strip()
    if not ADDR_RE.match(addr):
        raise Exception(f"{label} must be a 0x address")
    return "0x" + addr[2:].lower()


def _sender() -> str:
    return _require_address("sender", str(gl.message.sender_address))


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
        "body": "",
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
            entry["body"] = normalized[:EVIDENCE_CHARS]
            entry["byte_len"] = len(normalized)
            entry["status"] = "ok"
    except Exception as exc:
        entry["preview"] = str(exc)[:120]
        entry["status"] = "error"
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _literal_pay_worker(raw) -> bool:
    """Accept pay_worker only as a JSON boolean; otherwise fail safely to False."""
    if isinstance(raw, bool):
        return raw
    return False


def _evidence_blob(entry: dict) -> str:
    """Build adjudication evidence from frozen fields (body + hash), not preview alone."""
    body = str(entry.get("delivery_body") or entry.get("delivery_preview") or "")
    return (
        f"url={entry.get('delivery_url', '')}\n"
        f"hash_algo={HASH_ALGO}\n"
        f"content_hash={entry.get('delivery_hash', '')}\n"
        f"byte_len={entry.get('delivery_byte_len', 0)}\n"
        f"frozen_body:\n{body}"
    )


def _judge_pay(terms: str, claim: str, evidence: str) -> str:
    judge = (
        "You are a GenLayer bounty adjudicator.\n"
        "Decide if the worker DELIVERY satisfies the bounty TERMS using ONLY the "
        "FROZEN delivery evidence below (full bounded body + content hash). "
        "Do not rely on live pages.\n"
        "Return ONLY JSON with exactly one field that is a JSON boolean literal:\n"
        '{"pay_worker": true} or {"pay_worker": false}\n'
        "Do not return strings, numbers, or other keys. "
        "true = pay the worker; false = refund the client.\n"
        f"TERMS:\n{terms}\n\n"
        f"CLIENT_CLAIM:\n{claim}\n\n"
        f"FROZEN_DELIVERY_EVIDENCE:\n{evidence}\n"
    )
    try:
        out = gl.nondet.exec_prompt(judge, response_format="json")
    except Exception:
        try:
            out = gl.exec_prompt(judge)
        except Exception:
            return json.dumps({"pay_worker": False}, sort_keys=True, separators=(",", ":"))

    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            return json.dumps({"pay_worker": False}, sort_keys=True, separators=(",", ":"))
    if not isinstance(out, dict):
        return json.dumps({"pay_worker": False}, sort_keys=True, separators=(",", ":"))

    pay = _literal_pay_worker(out.get("pay_worker"))
    return json.dumps({"pay_worker": pay}, sort_keys=True, separators=(",", ":"))


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
        if _sender() != self.owner:
            raise Exception("only owner")

    def _balance_of(self, balances, user: str) -> dict:
        key = _require_address("user", user)
        if key not in balances:
            balances[key] = {"available": 0, "escrowed": 0}
        return balances[key]

    def _append_event(self, name: str, payload: dict) -> None:
        events = self._load("events_json")
        events.append({"event": name, **payload})
        if len(events) > 200:
            events = events[-200:]
        self._save("events_json", events)

    def _release_escrow(self, balances, entry: dict, pay_worker: bool) -> None:
        amt = int(entry["amount"])
        client = entry["client"]
        worker = entry["worker"]
        client_row = self._balance_of(balances, client)
        client_row["escrowed"] = max(0, int(client_row.get("escrowed", 0)) - amt)
        if pay_worker:
            worker_row = self._balance_of(balances, worker)
            worker_row["available"] = int(worker_row.get("available", 0)) + amt
            balances[worker] = worker_row
        else:
            client_row["available"] = int(client_row.get("available", 0)) + amt
        balances[client] = client_row

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
        client = _sender()
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
            "delivery_body": "",
            "delivery_byte_len": 0,
            "claim": "",
            "pay_worker": False,
            "funded_at": 0,
            "submitted_at": 0,
            "worker_deadline": 0,
            "client_deadline": 0,
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
        client = _sender()
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

        now = _now_ts()
        entry["status"] = STATUS_FUNDED
        entry["funded_at"] = now
        entry["worker_deadline"] = now + WORKER_ACTION_SECS
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "BountyFunded",
            {"id": bid, "amount": amt, "worker_deadline": entry["worker_deadline"]},
        )

    @gl.public.write
    def submit_work(self, bounty_id: str, delivery_url: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_FUNDED:
            raise Exception("bounty is not funded")
        worker = _sender()
        if worker != entry["worker"]:
            raise Exception("only worker may submit")

        url = _require_https(delivery_url)

        def fetch_fn() -> str:
            return _capture_page(url)

        snap_json = gl.eq_principle_strict_eq(fetch_fn)
        snap = json.loads(snap_json)
        if snap.get("status") != "ok":
            raise Exception("delivery_url fetch failed or empty")

        now = _now_ts()
        entry["delivery_url"] = url
        entry["delivery_hash"] = snap.get("content_hash", "")
        entry["delivery_preview"] = snap.get("preview", "")
        entry["delivery_body"] = snap.get("body", "")
        entry["delivery_byte_len"] = int(snap.get("byte_len", 0) or 0)
        entry["status"] = STATUS_SUBMITTED
        entry["submitted_at"] = now
        entry["client_deadline"] = now + CLIENT_ACTION_SECS
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "WorkSubmitted",
            {
                "id": bid,
                "url": url,
                "hash": entry["delivery_hash"],
                "byte_len": entry["delivery_byte_len"],
                "client_deadline": entry["client_deadline"],
            },
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
        if _sender() != entry["client"]:
            raise Exception("only client may accept")

        balances = self._load("balances_json")
        self._release_escrow(balances, entry, pay_worker=True)
        self._save("balances_json", balances)

        entry["status"] = STATUS_ACCEPTED
        entry["pay_worker"] = True
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event("BountyAccepted", {"id": bid, "amount": int(entry["amount"])})

    @gl.public.write
    def dispute(self, bounty_id: str, claim: str) -> None:
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_SUBMITTED:
            raise Exception("bounty is not submitted")
        if _sender() != entry["client"]:
            raise Exception("only client may dispute")
        entry["claim"] = _sanitize_text("claim", claim, MAX_CLAIM_LEN)
        entry["status"] = STATUS_DISPUTED
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event("BountyDisputed", {"id": bid, "claim": entry["claim"]})

    @gl.public.write
    def cancel_funded(self, bounty_id: str) -> None:
        """Client refund when worker misses the bounded submit window after fund."""
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_FUNDED:
            raise Exception("bounty is not funded")
        if _sender() != entry["client"]:
            raise Exception("only client may cancel funded bounty")
        deadline = int(entry.get("worker_deadline", 0) or 0)
        if _now_ts() < deadline:
            raise Exception("worker action window still open")

        balances = self._load("balances_json")
        self._release_escrow(balances, entry, pay_worker=False)
        self._save("balances_json", balances)

        entry["status"] = STATUS_CANCELLED
        entry["pay_worker"] = False
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "BountyCancelled",
            {"id": bid, "reason": "worker_idle", "amount": int(entry["amount"])},
        )

    @gl.public.write
    def timeout_release(self, bounty_id: str) -> None:
        """Worker payout when client misses the bounded accept/dispute window after submit."""
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_SUBMITTED:
            raise Exception("bounty is not submitted")
        if _sender() != entry["worker"]:
            raise Exception("only worker may timeout_release")
        deadline = int(entry.get("client_deadline", 0) or 0)
        if _now_ts() < deadline:
            raise Exception("client action window still open")

        balances = self._load("balances_json")
        self._release_escrow(balances, entry, pay_worker=True)
        self._save("balances_json", balances)

        entry["status"] = STATUS_ACCEPTED
        entry["pay_worker"] = True
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "BountyTimeoutRelease",
            {"id": bid, "reason": "client_idle", "amount": int(entry["amount"])},
        )

    @gl.public.write
    def adjudicate(self, bounty_id: str) -> None:
        """LLM judges frozen delivery body+hash vs terms. Consensus on pay_worker bool only."""
        bid = _normalize_id(bounty_id)
        bounties = self._load("bounties_json")
        if bid not in bounties:
            raise Exception("unknown bounty_id")
        entry = bounties[bid]
        if entry.get("status") != STATUS_DISPUTED:
            raise Exception("bounty is not disputed")
        if not entry.get("delivery_hash") or not (
            entry.get("delivery_body") or entry.get("delivery_preview")
        ):
            raise Exception("missing frozen delivery evidence")

        terms = entry.get("terms", "")
        claim = entry.get("claim", "")
        evidence = _evidence_blob(entry)

        def leader_fn() -> str:
            return _judge_pay(terms, claim, evidence)

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
        pay = _literal_pay_worker(verdict.get("pay_worker"))

        balances = self._load("balances_json")
        self._release_escrow(balances, entry, pay_worker=pay)
        self._save("balances_json", balances)

        if pay:
            entry["status"] = STATUS_PAID
        else:
            entry["status"] = STATUS_REFUNDED

        entry["pay_worker"] = pay
        bounties[bid] = entry
        self._save("bounties_json", bounties)
        self._append_event(
            "BountyAdjudicated",
            {"id": bid, "pay_worker": pay, "status": entry["status"], "amount": int(entry["amount"])},
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
