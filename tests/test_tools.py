# SPDX-License-Identifier: Apache-2.0
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from nextdns_agent_mcp import server
from nextdns_agent_mcp.api import Client, NextDNSError


def writes(fake):
    return [c for c in fake.calls if c[0] != "GET"]


# ---------------------------------------------------------------- profiles and modes

def test_profiles_shows_modes_and_hides_hidden():
    out = server.profiles()
    assert "Home  id abc123: read and change  (default)" in out
    assert "Kids  id def456: read only" in out
    assert "Secret" not in out and "zzz999" not in out


def test_hidden_profile_cannot_be_reached():
    with pytest.raises(ToolError, match="No profile"):
        server.profile("zzz999")


def test_profile_by_name_or_id_any_case():
    assert "Kids (id def456)" in server.profile("kids")
    assert "Kids (id def456)" in server.profile("DEF456")


def test_needs_profile_when_several_and_no_default(monkeypatch):
    monkeypatch.delenv("NEXTDNS_DEFAULT_PROFILE")
    with pytest.raises(ToolError, match="Which profile"):
        server.profile()


def test_only_profile_is_used_without_asking(monkeypatch):
    monkeypatch.delenv("NEXTDNS_DEFAULT_PROFILE")
    monkeypatch.setenv("NEXTDNS_PROFILES", "abc123=full,def456=hidden,zzz999=hidden")
    assert "Home (id abc123)" in server.profile()


def test_unlisted_profiles_are_full_by_default(monkeypatch):
    monkeypatch.setenv("NEXTDNS_PROFILES", "")
    assert "Kids  id def456: read and change" in server.profiles()


def test_default_mode_hidden(monkeypatch):
    monkeypatch.setenv("NEXTDNS_DEFAULT_MODE", "hidden")
    monkeypatch.setenv("NEXTDNS_PROFILES", "abc123=full")
    out = server.profiles()
    assert "Home" in out and "Kids" not in out


def test_server_read_only(monkeypatch, fake):
    monkeypatch.setenv("NEXTDNS_READ_ONLY", "on")
    assert "READ-ONLY MODE" in server.profiles()
    with pytest.raises(ToolError, match="Read-only mode"):
        server.list_entries("denylist", "add", ["x.example"])
    assert writes(fake) == []


def test_read_profile_refuses_changes(fake):
    with pytest.raises(ToolError, match="read only for this app"):
        server.list_entries("denylist", "add", ["x.example"], profile="Kids")
    with pytest.raises(ToolError, match="read only"):
        server.privacy(profile="Kids", add_blocklists=["oisd"])
    assert writes(fake) == []


# ---------------------------------------------------------------- profile summary

def test_profile_summary():
    out = server.profile()
    assert "On: threat intelligence feeds [threatIntelligenceFeeds]" in out
    assert "cryptojacking protection [cryptojacking]" in out.split("Off:")[1]
    assert "Blocked TLDs (1): zip" in out
    assert "nextdns-recommended" in out
    assert "Blocked services (1): tiktok" in out
    assert "bad.example" in out
    assert "kept 3 months, stored in eu" in out
    assert "https://dns.nextdns.io/abc123" in out and "abc123.dns.nextdns.io" in out


def test_profile_never_shows_linked_ip_token():
    assert "secret-token" not in server.profile()
    assert "secret-token" not in server.profile(section="setup")


def test_profile_one_section_in_full(fake):
    fake.profiles["abc123"]["denylist"] = [{"id": f"d{i}.example", "active": True} for i in range(40)]
    short = server.profile()
    assert "15 more" in short and "d39.example" not in short
    full = server.profile(section="denylist")
    assert "d39.example" in full and "Denylist (40)" in full


def test_profile_unknown_section():
    with pytest.raises(ToolError, match="Unknown section"):
        server.profile(section="wifi")


# ---------------------------------------------------------------- catalog

def test_catalog_search():
    out = server.catalog("blocklists", search="hagezi")
    assert "hagezi-pro: HaGeZi Pro, 150,000 domains" in out and "oisd" not in out


def test_catalog_kinds():
    assert ".zip (Spamhaus" in server.catalog("tlds")
    assert "tiktok (https://www.tiktok.com)" in server.catalog("services")
    with pytest.raises(ToolError, match="Unknown kind"):
        server.catalog("apps")


def test_catalog_is_cached(fake):
    server.catalog("natives")
    server.catalog("natives")
    assert sum(1 for c in fake.calls if c[1] == "/privacy/natives") == 1


# ---------------------------------------------------------------- denylist and allowlist

def test_add_remove_and_toggle(fake):
    out = server.list_entries("denylist", "add", ["https://Ads.Example.com/path?x=1", "bad.example"])
    assert "Added to the denylist of Home: ads.example.com" in out
    assert "bad.example (already there)" in out
    assert {"id": "ads.example.com", "active": True} in fake.profiles["abc123"]["denylist"]
    assert "Turned off in" in server.list_entries("denylist", "off", ["ads.example.com"])
    assert {"id": "ads.example.com", "active": False} in fake.profiles["abc123"]["denylist"]
    assert "already off" in server.list_entries("denylist", "off", ["ads.example.com"])
    assert "Removed from" in server.list_entries("denylist", "remove", ["ads.example.com"])
    assert all(e["id"] != "ads.example.com" for e in fake.profiles["abc123"]["denylist"])


def test_allowlist_and_not_a_domain(fake):
    out = server.list_entries("allowlist", "add", ["good.example", "not a domain!"])
    assert "good.example" in out and "not a domain! (not a domain)" in out
    assert fake.profiles["abc123"]["allowlist"] == [{"id": "good.example", "active": True}]


def test_remove_missing_entry_is_skipped(fake):
    out = server.list_entries("allowlist", "remove", ["nothere.example"])
    assert "not in the allowlist" in out and writes(fake) == []


def test_list_entries_checks_its_arguments():
    with pytest.raises(ToolError, match="denylist or allowlist"):
        server.list_entries("blocklist", "add", ["a.example"])
    with pytest.raises(ToolError, match="action must be"):
        server.list_entries("denylist", "block", ["a.example"])
    with pytest.raises(ToolError, match="At most"):
        server.list_entries("denylist", "add", [f"d{i}.example" for i in range(101)])


def test_errors_inside_a_200_reply_are_reported(fake, monkeypatch):
    route = fake.route

    def refuse(method, path, params, body):
        if method == "POST" and body and body.get("id") == "refused.example":
            import httpx
            return httpx.Response(200, json={"errors": [{"code": "invalid", "source": {"pointer": "/id"}}]})
        return route(method, path, params, body)

    monkeypatch.setattr(fake, "route", refuse)
    out = server.list_entries("denylist", "add", ["ok.example", "refused.example"])
    assert "Added to the denylist of Home: ok.example" in out
    assert "Failed: refused.example (NextDNS said: invalid (at /id))" in out


# ---------------------------------------------------------------- privacy

def test_privacy_add_remove_and_switches(fake):
    out = server.privacy(add_blocklists=["OISD", "nextdns-recommended"], add_natives=["apple"],
                         allow_affiliate=True, disguised_trackers=True)
    assert "added blocklist oisd" in out and "added native apple" in out and "allowAffiliate on" in out
    assert "nextdns-recommended (already on)" in out
    assert "disguisedTrackers" not in out.split("\n")[0]   # already on, so not sent
    priv = fake.profiles["abc123"]["privacy"]
    assert {"id": "oisd"} in priv["blocklists"] and priv["allowAffiliate"] is True
    out = server.privacy(remove_blocklists=["oisd"], remove_natives=["samsung"])
    assert "removed blocklist oisd" in out and "samsung (not on)" in out


def test_privacy_unknown_id_suggests(fake):
    with pytest.raises(ToolError, match="did you mean hagezi-pro"):
        server.privacy(add_blocklists=["hagezi-pr"])
    assert writes(fake) == []


def test_privacy_needs_something():
    with pytest.raises(ToolError, match="Nothing to change"):
        server.privacy()


# ---------------------------------------------------------------- analytics and logs

def test_analytics_status_with_shares(fake):
    fake.analytics["status"] = {"data": [{"status": "default", "queries": 300}, {"status": "blocked", "queries": 100}]}
    out = server.analytics("status")
    assert "default: 300 (75%)" in out and "blocked: 100 (25%)" in out
    method, path, params, _ = fake.calls[-1]
    assert path == "/profiles/abc123/analytics/status" and params["from"] == "-7d" and params["limit"] == "10"


def test_analytics_domains_params(fake):
    fake.analytics["domains"] = {"data": [{"domain": "a.example.com", "root": "example.com", "queries": 5}]}
    out = server.analytics("domains", status="blocked", root=True, limit=900)
    assert "a.example.com (root example.com): 5" in out
    params = fake.calls[-1][2]
    assert params["status"] == "blocked" and params["root"] == "true" and params["limit"] == "500"


def test_analytics_series(fake):
    fake.analytics["status;series"] = {
        "data": [{"status": "blocked", "queries": [1, 2, 3]}],
        "meta": {"series": {"times": ["2026-10-16T00:00:00Z", "2026-10-16T01:00:00Z", "2026-10-16T02:00:00Z"],
                            "interval": 3600}, "pagination": {"cursor": None}}}
    out = server.analytics("status", series=True, interval="1h", timezone="Europe/Lisbon")
    assert "Windows of 1 hour" in out and "blocked: total 6; 1 2 3" in out
    method, path, params, _ = fake.calls[-1]
    assert path.endswith("/analytics/status;series") and params["alignment"] == "clock" and params["partials"] == "end"


def test_analytics_unknown_report_and_empty():
    with pytest.raises(ToolError, match="Unknown report"):
        server.analytics("bandwidth")
    assert "no queries" in server.analytics("query_types")


def test_logs(fake):
    fake.logs = [{"timestamp": "2026-10-16T18:47:21.773Z", "domain": "ads.example", "status": "blocked",
                  "device": {"name": "iPhone"}, "reasons": [{"id": "blocklist:oisd", "name": "OISD"}]}]
    out = server.logs(search="ads", status="blocked", limit=5)
    assert "2026-10-16 18:47:21 | blocked | ads.example | iPhone | OISD" in out
    params = fake.calls[-1][2]
    assert params["search"] == "ads" and params["limit"] == "10" and "raw" not in params


def test_logs_empty_and_download(fake):
    assert "No log entries" in server.logs()
    assert "https://api.nextdns.io/logs/abc123/abc" in server.logs(download_link=True)
    assert fake.calls[-1][2]["redirect"] == "0"


# ---------------------------------------------------------------- the API client

def test_wrong_key(monkeypatch):
    monkeypatch.setenv("NEXTDNS_API_KEY", "wrong")
    with pytest.raises(ToolError, match="refused the API key"):
        server.profiles()


def test_no_key(monkeypatch):
    monkeypatch.delenv("NEXTDNS_API_KEY")
    with pytest.raises(ToolError, match="No NextDNS API key"):
        server.profiles()


def test_retries_when_busy(fake):
    fake.fail_next = [429, 503]
    assert "Home" in server.profiles()


def test_gives_up_after_retries(fake):
    fake.fail_next = [503] * 10
    with pytest.raises(ToolError):
        server.profiles()


def test_client_reports_error_details():
    import httpx
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={"errors": [
        {"code": "invalid", "detail": "bad name", "source": {"pointer": "/name"}}]}))
    with pytest.raises(NextDNSError, match="invalid: bad name \\(at /name\\)"):
        Client("k", transport=t).get("/profiles/x")


def test_tools_are_marked_read_or_write():
    import asyncio
    tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}
    for name in ("profiles", "profile", "catalog", "analytics", "logs"):
        assert tools[name].annotations.read_only_hint is True
    for name in ("list_entries", "privacy"):
        assert tools[name].annotations.read_only_hint is False
