# SPDX-License-Identifier: Apache-2.0
"""The 0.2 write tools, the change log and undo."""
import re

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from nextdns_agent_mcp import server


def change_id(text: str) -> str:
    return re.search(r"undo\(change_id='(\w+)'\)", text).group(1)


def home(fake):
    return fake.profiles["abc123"]


# ---------------------------------------------------------------- change log and undo

def test_every_change_is_logged_and_can_be_undone(fake):
    out = server.list_entries("denylist", "add", ["ads.example"])
    cid = change_id(out)
    log = server.changes()
    assert cid in log and "list_entries: add ads.example (denylist)" in log and "Home (abc123)" in log
    out = server.undo(cid)
    assert "Put Home back" in out
    assert [e["id"] for e in home(fake)["denylist"]] == ["bad.example"]
    assert "undone by" in server.changes()
    with pytest.raises(ToolError, match="already undone"):
        server.undo(cid)


def test_undo_of_the_undo_redoes(fake):
    cid = change_id(server.privacy(add_blocklists=["oisd"]))
    out = server.undo(cid)
    redo = re.search(r"undo\(change_id='(\w+)'\) redoes", out).group(1)
    assert {"id": "oisd"} not in [{"id": b["id"]} for b in home(fake)["privacy"]["blocklists"]]
    server.undo(redo)
    assert "oisd" in [b["id"] for b in home(fake)["privacy"]["blocklists"]]


def test_nothing_changed_is_not_logged(fake):
    out = server.list_entries("denylist", "add", ["bad.example"])
    assert "undo(" not in out
    assert server.changes() == "No changes recorded yet."


def test_undo_stops_when_changed_since(fake):
    cid = change_id(server.list_entries("denylist", "add", ["a.example"]))
    home(fake)["denylist"].append({"id": "dashboard.example", "active": True})   # someone used the dashboard
    with pytest.raises(ToolError, match="changed again since"):
        server.undo(cid)
    server.undo(cid, force=True)
    assert [e["id"] for e in home(fake)["denylist"]] == ["bad.example"]


def test_undo_needs_change_rights(fake, monkeypatch):
    cid = change_id(server.list_entries("denylist", "add", ["a.example"]))
    monkeypatch.setenv("NEXTDNS_PROFILES", "abc123=read")
    with pytest.raises(ToolError, match="read only"):
        server.undo(cid)


def test_unknown_change():
    with pytest.raises(ToolError, match="No change"):
        server.undo("nope")


def test_rate_limit(fake, monkeypatch):
    monkeypatch.setenv("NEXTDNS_CHANGE_LIMIT", "2")
    server.list_entries("denylist", "add", ["a.example"])
    server.list_entries("denylist", "add", ["b.example"])
    with pytest.raises(ToolError, match="Too many changes"):
        server.list_entries("denylist", "add", ["c.example"])


def test_changes_filter_by_profile(fake, monkeypatch):
    monkeypatch.setenv("NEXTDNS_PROFILES", "abc123=full,def456=full,Secret=hidden")
    server.list_entries("denylist", "add", ["a.example"])
    server.list_entries("allowlist", "add", ["k.example"], profile="Kids")
    out = server.changes(profile="kids")
    assert "k.example" in out and "a.example" not in out


# ---------------------------------------------------------------- security

def test_security_switches_and_tlds(fake):
    out = server.security(turn_on=["cryptojacking", "Threat intelligence feeds"], turn_off=["csam"],
                          block_tlds=[".com"], unblock_tlds=["zip"])
    assert "cryptojacking on" in out and "csam off" in out and "blocked .com" in out and "unblocked .zip" in out
    assert "threatIntelligenceFeeds (already on)" in out
    sec = home(fake)["security"]
    assert sec["cryptojacking"] is True and sec["csam"] is False and sec["tlds"] == [{"id": "com"}]
    server.undo(change_id(out))
    sec = home(fake)["security"]
    assert sec["cryptojacking"] is False and sec["csam"] is True and sec["tlds"] == [{"id": "zip"}]


def test_security_unknown_switch_and_tld(fake):
    with pytest.raises(ToolError, match="Unknown switch: wifi"):
        server.security(turn_on=["wifi"])
    with pytest.raises(ToolError, match="Unknown tlds"):
        server.security(block_tlds=["notatld"])
    assert not [c for c in fake.calls if c[0] != "GET"]


# ---------------------------------------------------------------- parental control

def test_parental_control(fake):
    out = server.parental_control(block_categories=["gambling"], pause=["tiktok"], allow_in_recreation=["tiktok"],
                                  recreation_times={"Monday": "18:00-20:00", "saturday": "9:30-22:00"},
                                  recreation_timezone="Europe/Lisbon", safe_search=True)
    assert "blocked gambling" in out and "tiktok paused" in out and "tiktok allowed in recreation time" in out
    assert "monday 18:00-20:00" in out and "safeSearch on" in out
    pc = home(fake)["parentalControl"]
    assert pc["categories"] == [{"id": "gambling", "active": True}]
    assert pc["services"] == [{"id": "tiktok", "active": False, "recreation": True}]
    assert pc["recreation"] == {"times": {"monday": {"start": "18:00:00", "end": "20:00:00"},
                                          "saturday": {"start": "09:30:00", "end": "22:00:00"}},
                                "timezone": "Europe/Lisbon"}
    server.undo(change_id(out))
    pc = home(fake)["parentalControl"]
    assert pc["categories"] == [] and pc["safeSearch"] is False and pc["recreation"]["times"] == {}
    assert pc["services"] == [{"id": "tiktok", "active": True}]


def test_parental_control_checks(fake):
    with pytest.raises(ToolError, match="time zone"):
        server.parental_control(recreation_times={"monday": "18:00-20:00"})
    with pytest.raises(ToolError, match="isn't a day"):
        server.parental_control(recreation_times={"someday": "18:00-20:00"})
    with pytest.raises(ToolError, match="isn't a time"):
        server.parental_control(recreation_times={"monday": "6pm-8pm"}, recreation_timezone="Europe/Lisbon")
    out = server.parental_control(unblock_services=["instagram"], pause=["porn"])
    assert "instagram (not blocked)" in out and "porn (not in the blocked" in out


# ---------------------------------------------------------------- rewrites

def test_rewrites_add_remove_and_undo(fake):
    out = server.rewrites("add", "NAS.home", "192.168.1.10")
    assert "Added rewrite nas.home -> 192.168.1.10" in out
    assert "already there" in server.rewrites("add", "nas.home", "192.168.1.10")
    out = server.rewrites("remove", "nas.home")
    assert "Removed rewrite nas.home (192.168.1.10)" in out
    assert home(fake)["rewrites"] == []
    server.undo(change_id(out))   # no PUT for rewrites: undo adds it back one by one
    assert [(r["name"], r["content"]) for r in home(fake)["rewrites"]] == [("nas.home", "192.168.1.10")]
    assert "No rewrite" in server.rewrites("remove", "other.home")
    with pytest.raises(ToolError, match="Pass content"):
        server.rewrites("add", "x.home")


# ---------------------------------------------------------------- settings

def test_profile_settings_and_rename(fake):
    out = server.profile_settings(rename="House", log_retention="1 day", log_location="ch", drop_client_ips=True,
                                  cache_boost=True, web3=True)
    s = home(fake)["settings"]
    assert home(fake)["name"] == "House"
    assert s["logs"] == {"enabled": True, "drop": {"ip": True, "domain": False}, "retention": 86400, "location": "ch"}
    assert s["performance"]["cacheBoost"] is True and s["performance"]["ecs"] is True and s["web3"] is True
    assert "Settings of House changed" in out
    server.undo(change_id(out))
    assert home(fake)["name"] == "Home"
    assert home(fake)["settings"]["logs"]["retention"] == 7776000 and home(fake)["settings"]["web3"] is False


@pytest.mark.parametrize("value,seconds", [("1h", 3600), ("7 days", 604800), ("1 week", 604800), ("3M", 7776000),
                                           ("3 months", 7776000), ("2 years", 63072000), ("30d", 2592000)])
def test_retention_values(value, seconds):
    assert server.retention_seconds(value) == seconds


@pytest.mark.parametrize("value", ["5 days", "1m", "forever", "10 minutes"])
def test_retention_refused(value):
    with pytest.raises(ToolError):
        server.retention_seconds(value)


def test_profile_settings_checks():
    with pytest.raises(ToolError, match="Nothing to change"):
        server.profile_settings()
    with pytest.raises(ToolError, match="Log location"):
        server.profile_settings(log_location="mars")


# ---------------------------------------------------------------- create, delete, clear logs

def test_create_recommended(fake, monkeypatch):
    monkeypatch.setenv("NEXTDNS_DEFAULT_MODE", "read")
    out = server.create_profile("Guest")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    new = fake.profiles[pid]
    assert new["security"]["cryptojacking"] is True and new["security"]["threatIntelligenceFeeds"] is True
    assert [b["id"] for b in new["privacy"]["blocklists"]] == ["nextdns-recommended"]
    assert f"Guest  id {pid}: read and change" in server.profiles()   # made here, so this app may change it
    cid = change_id(server.list_entries("denylist", "add", ["x.example"], profile="Guest"))
    server.undo(cid)
    assert pid in fake.profiles and fake.profiles[pid]["denylist"] == []
    with pytest.raises(ToolError, match="already a profile"):
        server.create_profile("guest")


def test_copy_profile(fake):
    out = server.create_profile("Home copy", copy_from="Home")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    new, old = fake.profiles[pid], home(fake)
    assert new["denylist"] == old["denylist"] and new["security"]["tlds"] == [{"id": "zip"}]
    assert new["parentalControl"]["services"] == [{"id": "tiktok", "active": True}]
    assert new["settings"]["logs"]["location"] == "eu"


def code(text: str) -> str:
    return re.search(r"confirm_code='(\w+)'", text).group(1)


def test_undo_create_needs_double_confirmation(fake):
    out = server.create_profile("Temp", start="empty")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    cid = change_id(out)
    ask = server.undo(cid)
    assert "CONFIRMATION NEEDED" in ask and pid in fake.profiles
    out = server.undo(cid, confirm_code=code(ask))
    assert pid not in fake.profiles and "Deleted the profile Temp" in out


def test_undo_create_after_use_needs_force(fake):
    cid = change_id(server.create_profile("Temp"))
    server.list_entries("denylist", "add", ["x.example"], profile="Temp")
    with pytest.raises(ToolError, match="changed again"):
        server.undo(cid)
    ask = server.undo(cid, force=True)
    assert "CONFIRMATION NEEDED" in ask


def test_delete_needs_double_confirmation(fake):
    ask = server.delete_profile("Home")
    assert "CONFIRMATION NEEDED" in ask and "abc123" in fake.profiles
    out = server.delete_profile("Home", confirm_code="wrong1")
    assert "wrong or expired" in out and "abc123" in fake.profiles
    with pytest.raises(ToolError, match="read only"):
        server.delete_profile("Kids")
    # a code only works for the action it was given for
    other = code(server.clear_logs("Home"))
    assert "CONFIRMATION NEEDED" in server.delete_profile("Home", confirm_code=other)
    assert "abc123" in fake.profiles


def test_delete_and_restore(fake):
    out = server.delete_profile("Home", confirm_code=code(server.delete_profile("Home")))
    assert "abc123" not in fake.profiles
    with pytest.raises(ToolError):   # a code works once
        server.profile("Home")
    out = server.undo(change_id(out))
    pid = re.search(r"new id (\w+)", out).group(1)
    new = fake.profiles[pid]
    assert new["name"] == "Home" and new["denylist"] == [{"id": "bad.example", "active": True}]
    assert new["settings"]["logs"]["location"] == "eu" and new["security"]["tlds"] == [{"id": "zip"}]


def test_deletes_can_be_turned_off(fake, monkeypatch):
    monkeypatch.setenv("NEXTDNS_ALLOW_DELETE", "off")
    with pytest.raises(ToolError, match="turned off"):
        server.delete_profile("Home")
    with pytest.raises(ToolError, match="turned off"):
        server.clear_logs("Home")


def test_clear_logs(fake):
    fake.logs = [{"domain": "a.example"}]
    ask = server.clear_logs("Home")
    assert "no undo" in ask and fake.logs
    assert "can't be undone" in server.clear_logs("Home", confirm_code=code(ask))
    assert fake.logs == []
    cid = server.changes().split("\n")[1].split(" |")[0]
    with pytest.raises(ToolError, match="can't come back"):
        server.undo(cid)


def test_read_only_blocks_new_tools(fake, monkeypatch):
    monkeypatch.setenv("NEXTDNS_READ_ONLY", "on")
    for call in (lambda: server.security(turn_on=["dga"]), lambda: server.rewrites("add", "a.home", "1.2.3.4"),
                 lambda: server.profile_settings(web3=True), lambda: server.parental_control(safe_search=True),
                 lambda: server.create_profile("X"), lambda: server.delete_profile("Home"),
                 lambda: server.clear_logs("Home")):
        with pytest.raises(ToolError, match="Read-only"):
            call()
    assert not [c for c in fake.calls if c[0] != "GET"]


def test_destructive_tools_are_marked():
    import asyncio
    tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}
    for name in ("delete_profile", "clear_logs", "undo"):
        assert tools[name].annotations.destructive_hint is True
    assert tools["changes"].annotations.read_only_hint is True
