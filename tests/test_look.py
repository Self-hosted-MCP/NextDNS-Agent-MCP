# SPDX-License-Identifier: MIT
"""0.4: check_domain, watch_logs, chart, compare_profiles and backups."""
import re

import pytest
from mcp.server.mcpserver import Image
from mcp.server.mcpserver.exceptions import ToolError

from nextdns_agent_mcp import server


def code(text: str) -> str:
    return re.search(r"confirm_code='(\w+)'", text).group(1)


# ---------------------------------------------------------------- check_domain

def test_check_blocked_domain(fake):
    out = server.check_domain("https://www.bad.example/page")
    assert out.startswith("www.bad.example on Home: BLOCKED (Denylist)")
    assert "In the denylist as bad.example." in out and "denylist', action='remove', domains=['bad.example']" in out


def test_check_allowed_domain(fake):
    out = server.check_domain("good.example")
    assert "ALLOWED: answers 93.184.215.14, 2606:2800::1" in out and "To block it" in out


def test_check_allowlisted_and_missing(fake):
    fake.profiles["abc123"]["allowlist"] = [{"id": "good.example", "active": True}]
    out = server.check_domain("good.example")
    assert "ALLOWED (Allowlist)" in out and "In the allowlist as good.example." in out
    fake.profiles["abc123"]["denylist"] = []
    fake.logs = []
    fake.profiles["abc123"]["allowlist"] = []
    fake.missing.add("nothing.example")
    assert "doesn't exist" in server.check_domain("nothing.example")


def test_check_domain_refuses_junk():
    with pytest.raises(ToolError, match="isn't a domain"):
        server.check_domain("not a domain")


# ---------------------------------------------------------------- watch_logs

def test_watch_logs(fake):
    fake.stream_events = [
        {"timestamp": "2026-10-16T19:22:49.107Z", "domain": "github.com", "status": "default", "reasons": []},
        {"timestamp": "2026-10-16T19:22:50.000Z", "domain": "ads.tiktok.com", "status": "blocked",
         "device": {"name": "iPhone"}, "reasons": [{"id": "blocklist:oisd", "name": "OISD"}]}]
    out = server.watch_logs(seconds=5, search="tiktok")
    assert "2 queries for Home in 5 seconds, 1 blocked" in out
    assert "blocked | ads.tiktok.com | iPhone | OISD" in out
    assert [c for c in fake.calls if c[1].endswith("/logs/stream")][0][2]["search"] == "tiktok"


def test_watch_logs_nothing_and_limits(fake):
    assert "Nothing came in" in server.watch_logs(seconds=1)   # clamped to 5
    assert "5 seconds" in server.watch_logs(seconds=1)


# ---------------------------------------------------------------- chart

def test_chart_over_time(fake):
    fake.analytics["status;series"] = {
        "data": [{"status": "default", "queries": [5, 9, 3]}, {"status": "blocked", "queries": [1, 2, 0]}],
        "meta": {"series": {"times": ["2026-10-14T00:00:00Z", "2026-10-15T00:00:00Z", "2026-10-16T00:00:00Z"],
                            "interval": 86400}, "pagination": {"cursor": None}}}
    text, img = server.chart("status", interval="1d")
    assert isinstance(img, Image) and img.data.startswith(b"\x89PNG")
    assert "default 17; blocked 3" in text


def test_chart_bars(fake):
    fake.analytics["domains"] = {"data": [{"domain": f"d{i}.example", "queries": 100 - i} for i in range(12)]}
    text, img = server.chart("domains", over_time=False, status="blocked")
    assert img.data.startswith(b"\x89PNG") and "d0.example 100" in text
    assert fake.calls[-1][2]["status"] == "blocked"


def test_chart_nothing_to_draw():
    assert "nothing to draw" in server.chart("status")


# ---------------------------------------------------------------- compare_profiles

def test_compare(fake):
    kids = fake.profiles["def456"]
    kids["denylist"].append({"id": "game.example", "active": True})
    kids["security"]["cryptojacking"] = True
    kids["settings"]["logs"]["retention"] = 86400
    out = server.compare_profiles("Home", "Kids")
    assert "denylist: only in the second: game.example" in out
    assert "security.cryptojacking: False vs True" in out
    assert "settings.logs.retention: 7776000 vs 86400" in out


def test_compare_same():
    assert "Same settings and lists." in server.compare_profiles("Home", "Home")


# ---------------------------------------------------------------- backups

def test_backup_list_and_restore_needs_confirmation(fake):
    out = server.backup(note="before the trip")
    bid = re.search(r"Backup (\w+)", out).group(1)
    assert bid in server.backups() and "before the trip" in server.backups()
    fake.profiles["abc123"]["denylist"] = []
    fake.profiles["abc123"]["security"]["csam"] = False
    ask = server.restore_backup(bid)
    assert "CONFIRMATION NEEDED" in ask and fake.profiles["abc123"]["denylist"] == []
    out = server.restore_backup(bid, confirm_code=code(ask))
    assert "Restored Home from backup" in out
    assert fake.profiles["abc123"]["denylist"] == [{"id": "bad.example", "active": True}]
    assert fake.profiles["abc123"]["security"]["csam"] is True
    cid = re.search(r"undo\(change_id='(\w+)'\)", out).group(1)
    server.undo(cid)
    assert fake.profiles["abc123"]["denylist"] == []


def test_backup_to_new_profile(fake):
    bid = re.search(r"Backup (\w+)", server.backup()).group(1)
    out = server.restore_backup(bid, new_profile_name="Home again")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    assert fake.profiles[pid]["denylist"] == [{"id": "bad.example", "active": True}]
    assert fake.profiles[pid]["settings"]["logs"]["location"] == "eu"


def test_backup_errors(fake):
    with pytest.raises(ToolError, match="No backup"):
        server.restore_backup("nope00")
    with pytest.raises(ToolError, match="No backup"):
        server.restore_backup("../../etc")
    assert "No backups yet" in server.backups()
    with pytest.raises(ToolError, match="isn't a backup"):
        server.backup_from_file("{}")
    with pytest.raises(ToolError, match="not JSON"):
        server.backup_from_file("hello")


def test_backup_file_round_trip(fake):
    import json
    bid = re.search(r"Backup (\w+)", server.backup()).group(1)
    text = (server.BACKUP_DIR / f"{bid}.json").read_text()
    b = server.backup_from_file(text)
    assert b["id"] != bid and b["profile_name"] == "Home"
    assert json.loads((server.BACKUP_DIR / f"{b['id']}.json").read_text())["sections"]["denylist"]
