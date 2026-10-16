# SPDX-License-Identifier: MIT
"""The web version: AI app logins, the settings page, and what each connected app may do."""
import asyncio
import re

import pytest
from mcp.server.auth.provider import AuthorizationParams
from mcp.server.mcpserver.exceptions import ToolError
from mcp.shared.auth import OAuthClientInformationFull
from pydantic import AnyUrl
from starlette.testclient import TestClient

from conftest import KEY
from nextdns_agent_mcp import server

PASS = "short1"   # six characters are enough
ORIGIN = {"origin": "http://localhost"}


@pytest.fixture
def web(monkeypatch):
    monkeypatch.setenv("LOGIN_PASSPHRASE", PASS)
    monkeypatch.setenv("PUBLIC_URL", "http://localhost")
    for f in (server.OAUTH_FILE, server.PAGE_FILE, server.SECRETS_FILE, server.STATE_DIR / "sessions.json"):
        f.unlink(missing_ok=True)
    app = server.build_server(True)
    client = TestClient(app.streamable_http_app(), base_url="http://localhost")
    yield client, server.PROVIDER
    monkeypatch.setattr(server, "PROVIDER", None)


def sign_in(client) -> tuple[str, str]:
    r = client.post("/settings/login", data={"passphrase": PASS}, headers=ORIGIN, follow_redirects=False)
    assert r.status_code == 303
    page = client.get("/settings").text
    return re.search(r'name="csrf" value="([^"]+)"', page)[1], page


def save(client, csrf, **form):
    return client.post("/settings/save", data={"csrf": csrf, **form}, headers=ORIGIN)


def connect(provider, cid="c1", name="Claude") -> str:
    """Registers an AI app and starts its login: returns the login page's req."""
    info = OAuthClientInformationFull(client_id=cid, client_name=name, redirect_uris=[AnyUrl("https://claude.ai/cb")])
    asyncio.run(provider.register_client(info))
    params = AuthorizationParams(state="s", scopes=["nextdns"], code_challenge="x" * 43,
                                 redirect_uri=AnyUrl("https://claude.ai/cb"), redirect_uri_provided_explicitly=True)
    url = asyncio.run(provider.authorize(info, params))
    return url.split("req=")[1]


# ---------------------------------------------------------------- settings page

def test_settings_needs_the_passphrase(web):
    client, provider = web
    assert "Open settings" in client.get("/settings").text
    r = client.post("/settings/login", data={"passphrase": "wrong!"}, headers=ORIGIN)
    assert r.status_code == 401 and "Wrong passphrase" in r.text
    assert len(provider.failures) == 1


def test_lockout_after_five_wrong_tries(web):
    client, provider = web
    provider.failures = [__import__("time").time()] * 5
    r = client.post("/settings/login", data={"passphrase": PASS}, headers=ORIGIN)
    assert r.status_code == 403 and "Wait 15 minutes" in r.text


def test_page_shows_profiles_and_is_locked_down(web):
    client, _ = web
    csrf, page = sign_in(client)
    assert "Home" in page and "abc123" in page and "Kids" in page
    assert "comes from the settings file or hosting variables" in page   # the key is an env var in the tests
    r = client.get("/settings")
    assert r.headers["x-frame-options"] == "DENY" and "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert "not made by NextDNS" in page


def test_forms_need_token_and_same_origin(web):
    client, _ = web
    csrf, _ = sign_in(client)
    assert client.post("/settings/save", data={"kind": "safety"}, headers=ORIGIN).status_code == 403
    r = client.post("/settings/save", data={"csrf": csrf, "kind": "safety"}, headers={"origin": "https://evil.example"})
    assert r.status_code == 403


def test_key_saved_encrypted(web, monkeypatch):
    client, _ = web
    monkeypatch.delenv("NEXTDNS_API_KEY")
    csrf, page = sign_in(client)
    assert "Paste your NextDNS API key" in page and "https://my.nextdns.io/account" in page
    assert "https://nextdns.github.io/api/" in page
    r = save(client, csrf, kind="key", api_key="wrong-key")
    assert "refused the API key" in r.text
    r = save(client, csrf, kind="key", api_key=KEY)
    assert "The key works: 3 profile(s)" in r.text and "ending in -key" in r.text
    assert KEY not in server.SECRETS_FILE.read_text()
    assert server.config()["NEXTDNS_API_KEY"] == KEY
    save(client, csrf, kind="key", action="remove")
    assert server.config()["NEXTDNS_API_KEY"] == ""


def test_profile_modes_and_safety_from_the_page(web, monkeypatch):
    client, _ = web
    monkeypatch.delenv("NEXTDNS_PROFILES")
    monkeypatch.delenv("NEXTDNS_DEFAULT_PROFILE")
    csrf, _ = sign_in(client)
    r = save(client, csrf, kind="profiles", mode_abc123="full", mode_def456="read", mode_zzz999="hidden",
             default_profile="abc123")
    assert "Saved the profiles" in r.text
    out = server.profiles()
    assert "Home  id abc123: read and change  (default)" in out and "Kids  id def456: read only" in out
    assert "Secret" not in out
    save(client, csrf, kind="safety", NEXTDNS_READ_ONLY="yes", NEXTDNS_DEFAULT_MODE="full")
    assert "READ-ONLY MODE" in server.profiles()
    with pytest.raises(ToolError, match="turned off"):   # the box wasn't ticked
        server.delete_profile("Home")


def test_settings_file_wins_over_the_page(web):
    client, _ = web
    csrf, page = sign_in(client)
    assert "can only be changed there" in page   # NEXTDNS_PROFILES is an env var in the tests
    save(client, csrf, kind="profiles", mode_abc123="hidden")
    assert "Home" in server.profiles()


def test_undo_from_the_page(web, fake):
    client, _ = web
    server.list_entries("denylist", "add", ["ads.example"])
    csrf, page = sign_in(client)
    cid = server.read_changes()[-1]["id"]
    assert "add ads.example (denylist)" in page
    r = save(client, csrf, kind="undo", change_id=cid)
    assert "Put Home back" in r.text
    assert [e["id"] for e in fake.profiles["abc123"]["denylist"]] == ["bad.example"]


def test_undo_of_a_new_profile_needs_the_box(web, fake):
    client, _ = web
    pid = re.search(r"\(id (\w+)\)", server.create_profile("Temp")).group(1)
    csrf, _ = sign_in(client)
    cid = server.read_changes()[-1]["id"]
    assert "Tick the box" in save(client, csrf, kind="undo", change_id=cid).text and pid in fake.profiles
    assert "Deleted the profile Temp" in save(client, csrf, kind="undo", change_id=cid, sure="yes").text
    assert pid not in fake.profiles


def test_sign_out(web):
    client, _ = web
    csrf, _ = sign_in(client)
    client.post("/settings/logout", data={"csrf": csrf}, headers=ORIGIN)
    assert "Open settings" in client.get("/settings").text


def test_theme_and_icon(web):
    client, _ = web
    r = client.post("/theme", data={"next": "/settings"}, follow_redirects=False)
    assert r.status_code == 303 and "theme=light" in r.headers["set-cookie"]
    assert client.get("/icon.svg").headers["content-type"].startswith("image/svg+xml")
    assert client.get("/health").text == "ok"


# ---------------------------------------------------------------- AI app login

def test_login_page_lists_profiles(web):
    client, provider = web
    req = connect(provider)
    page = client.get(f"/login?req={req}").text
    assert "Connect Claude to" in page and 'value="abc123" checked' in page and "Secret" not in page
    assert 'name="change" value="yes" checked' in page


def test_login_gives_a_code_and_saves_the_grant(web):
    client, provider = web
    req = connect(provider)
    r = client.post("/login", data={"req": req, "passphrase": "nope!!", "profile": ["abc123"]})
    assert r.status_code == 401
    r = client.post("/login", data={"req": req, "passphrase": PASS, "profile": ["abc123", "zzz999"]},
                    follow_redirects=False)
    assert r.status_code == 302 and r.headers["location"].startswith("https://claude.ai/cb?code=")
    # a hidden profile can't be granted, and "change" wasn't ticked
    assert provider.grants["c1"]["profiles"] == ["abc123"] and provider.grants["c1"]["change"] is False


def test_login_needs_a_profile(web):
    client, provider = web
    req = connect(provider)
    r = client.post("/login", data={"req": req, "passphrase": PASS})
    assert r.status_code == 400 and "Tick at least one profile" in r.text


def test_expired_login_link(web):
    client, _ = web
    assert "expired" in client.get("/login?req=nope").text


def test_redirects_only_to_known_apps(web):
    _, provider = web
    from mcp.server.auth.provider import RegistrationError
    bad = OAuthClientInformationFull(client_id="x", redirect_uris=[AnyUrl("https://evil.example/cb")])
    with pytest.raises(RegistrationError):
        asyncio.run(provider.register_client(bad))


def test_tokens_stored_as_fingerprints(web):
    _, provider = web
    tok = provider.issue("c1", ["nextdns"], None)
    text = server.OAUTH_FILE.read_text()
    assert tok.access_token not in text and tok.refresh_token not in text


# ---------------------------------------------------------------- what a connected app may do

@pytest.fixture
def as_app(web, monkeypatch):
    _, provider = web
    monkeypatch.setattr(server, "current_app", lambda: "c1")
    provider.clients["c1"] = OAuthClientInformationFull(client_id="c1", client_name="Phone Claude",
                                                         redirect_uris=[AnyUrl("https://claude.ai/cb")])
    return provider


def test_app_sees_only_its_profiles(as_app):
    as_app.grants["c1"] = {"profiles": ["abc123"], "change": True}
    out = server.profiles()
    assert "Home" in out and "Kids" not in out
    with pytest.raises(ToolError, match="No profile"):
        server.profile("Kids")


def test_app_without_change_is_read_only(as_app, fake):
    as_app.grants["c1"] = {"profiles": ["abc123"], "change": False}
    assert "Home  id abc123: read only" in server.profiles()
    with pytest.raises(ToolError, match="read only"):
        server.list_entries("denylist", "add", ["x.example"])


def test_app_name_in_change_log_and_new_profile_joins_grant(as_app, fake):
    as_app.grants["c1"] = {"profiles": ["abc123"], "change": True}
    out = server.create_profile("Phone made")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    assert pid in as_app.grants["c1"]["profiles"]
    assert "Phone Claude" in server.changes()


def test_app_grant_edit_and_disconnect_from_page(web, as_app):
    client, _ = web
    as_app.grants["c1"] = {"profiles": ["abc123"], "change": True}
    csrf, page = sign_in(client)
    assert "Phone Claude" in page
    save(client, csrf, kind="app", client_id="c1", profile=["abc123", "def456"])
    assert as_app.grants["c1"] == {"profiles": ["abc123", "def456"], "change": False}
    save(client, csrf, kind="app", client_id="c1", action="disconnect")
    assert "c1" not in as_app.grants


def test_deleted_profile_leaves_grants(as_app, fake):
    as_app.grants["c1"] = {"profiles": ["abc123"], "change": True}
    out = server.create_profile("Gone soon")
    pid = re.search(r"\(id (\w+)\)", out).group(1)
    assert pid in as_app.grants["c1"]["profiles"]
    cid = re.search(r"undo\(change_id='(\w+)'\)", out).group(1)
    ask = server.undo(cid)
    server.undo(cid, confirm_code=re.search(r"confirm_code='(\w+)'", ask).group(1))
    assert as_app.grants["c1"]["profiles"] == ["abc123"]


def test_login_page_explains_the_key_when_missing(web, monkeypatch):
    client, provider = web
    monkeypatch.delenv("NEXTDNS_API_KEY")
    page = client.get(f"/login?req={connect(provider)}").text
    assert "How to get your API key" in page and "https://my.nextdns.io/account" in page


def test_backups_on_the_page(web, fake):
    client, _ = web
    csrf, _ = sign_in(client)
    r = save(client, csrf, kind="backup", action="make", profile="abc123")
    bid = re.search(r"Backup (\w+) of Home saved", r.text).group(1)
    d = client.get(f"/settings/backup/{bid}")
    assert d.headers["content-disposition"].startswith('attachment; filename="nextdns-Home-')
    assert '"denylist"' in d.text
    fake.profiles["abc123"]["denylist"] = []
    assert "Tick the box" in save(client, csrf, kind="backup", action="restore", backup_id=bid).text
    r = save(client, csrf, kind="backup", action="restore", backup_id=bid, sure="yes")
    assert "Restored Home from backup" in r.text and fake.profiles["abc123"]["denylist"]
    r = client.post("/settings/save", data={"csrf": csrf, "kind": "backup", "action": "upload"},
                    files={"file": ("b.json", d.content, "application/json")}, headers=ORIGIN)
    assert "Added backup" in r.text
    r = save(client, csrf, kind="backup", action="new", backup_id=bid, name="From page")
    assert "Made profile From page" in r.text
    assert "Deleted backup" in save(client, csrf, kind="backup", action="delete", backup_id=bid).text


def test_backup_download_needs_sign_in(web):
    client, _ = web
    r = client.get("/settings/backup/abcdef", follow_redirects=False)
    assert r.status_code == 303


def test_update_switch_on_the_page(web, fake, monkeypatch):
    client, _ = web
    monkeypatch.setattr(server, "current_version", lambda: "0.6.3")
    fake.latest_tag = "v0.7.0"
    csrf, page = sign_in(client)
    assert "Check for new versions once a day" in page and "Version v0.7.0 is out" not in page
    r = save(client, csrf, kind="update", UPDATE_CHECK="yes")
    assert "Update check on" in r.text and "Version v0.7.0 is out" in r.text
    r = save(client, csrf, kind="update")
    assert "Update check off" in r.text and "Version v0.7.0 is out" not in r.text
