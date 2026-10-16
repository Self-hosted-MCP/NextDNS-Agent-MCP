# SPDX-License-Identifier: MIT
"""A fake NextDNS API, so the tests never touch a real account."""
import atexit
import copy
import json
import os
import re
import shutil
import tempfile

import httpx
import pytest

_tmp = tempfile.mkdtemp(prefix="nextdns-mcp-test-")
atexit.register(shutil.rmtree, _tmp, ignore_errors=True)
os.environ["NEXTDNS_CONFIG_DIR"] = _tmp
os.environ.pop("NEXTDNS_ENV_FILE", None)
for _k in list(os.environ):
    if _k.startswith("NEXTDNS_") and _k != "NEXTDNS_CONFIG_DIR":
        os.environ.pop(_k, None)

from nextdns_agent_mcp import server  # noqa: E402

KEY = "test-key"

PROFILE = {
    "name": "Home",
    "setup": {"ipv4": [], "ipv6": ["2a07:a8c0::ab:c123"],
              "linkedIp": {"servers": ["45.90.28.1"], "ip": None, "ddns": None, "updateToken": "secret-token"},
              "dnscrypt": "sdns://xyz"},
    "security": {"threatIntelligenceFeeds": True, "cryptojacking": False, "csam": True, "tlds": [{"id": "zip"}]},
    "privacy": {"blocklists": [{"id": "nextdns-recommended", "name": None, "entries": 100}], "natives": [],
                "disguisedTrackers": True, "allowAffiliate": False},
    "parentalControl": {"safeSearch": False, "youtubeRestrictedMode": False, "blockBypass": False,
                        "services": [{"id": "tiktok", "active": True}], "categories": [],
                        "recreation": {"times": {}, "timezone": None}},
    "settings": {"logs": {"enabled": True, "drop": {"ip": False, "domain": False}, "retention": 7776000,
                          "location": "eu"},
                 "blockPage": {"enabled": False}, "performance": {"ecs": True, "cacheBoost": False,
                                                                  "cnameFlattening": False}, "web3": False},
    "denylist": [{"id": "bad.example", "active": True}],
    "allowlist": [],
    "rewrites": [],
}

CATALOG = {
    "/privacy/blocklists": [{"id": "nextdns-recommended", "name": None, "entries": 100},
                            {"id": "oisd", "name": "OISD", "entries": 200000, "updatedOn": "2026-10-15T00:00:00Z",
                             "description": "A big list."},
                            {"id": "hagezi-pro", "name": "HaGeZi Pro", "entries": 150000}],
    "/privacy/natives": [{"id": "apple"}, {"id": "samsung"}, {"id": "windows"}],
    "/parentalControl/services": [{"id": "tiktok", "website": "https://www.tiktok.com"}],
    "/parentalControl/categories": [{"id": "porn"}, {"id": "gambling"}],
    "/security/tlds": [{"id": "zip", "spamhaus": 1}, {"id": "com", "spamhaus": 0}],
}


def merge(node: dict, body: dict) -> None:
    for k, v in body.items():
        if isinstance(v, dict) and isinstance(node.get(k), dict) and k != "recreation":
            merge(node[k], v)
        else:
            node[k] = v


class FakeNextDNS:
    """Enough of api.nextdns.io for the tools: profiles, their parts, lists, catalogs, analytics and logs."""

    def __init__(self):
        self.profiles = {"abc123": copy.deepcopy(PROFILE),
                         "def456": {**copy.deepcopy(PROFILE), "name": "Kids"},
                         "zzz999": {**copy.deepcopy(PROFILE), "name": "Secret"}}
        self.calls: list[tuple[str, str, dict, object]] = []
        self.fail_next: list[int] = []   # status codes to answer before working normally
        self.analytics: dict[str, dict] = {}
        self.logs: list[dict] = []
        self.next_id = 0
        self.stream_events: list[dict] = []
        self.missing: set[str] = set()   # domains that don't exist

    def dns(self, pid: str, name: str, qtype: str) -> httpx.Response:
        prof = self.profiles[pid]
        blocked = any(name == e["id"] or name.endswith("." + e["id"]) for e in prof["denylist"] if e.get("active", True))
        allowed = any(name == e["id"] or name.endswith("." + e["id"]) for e in prof["allowlist"] if e.get("active", True))
        q = {"Question": [{"name": name + ".", "type": 1 if qtype == "A" else 28}]}
        if name in self.missing:
            return httpx.Response(200, json={"Status": 3, **q})
        if blocked and not allowed:
            self.logs.insert(0, {"timestamp": "2026-10-16T19:22:42.784Z", "domain": name, "status": "blocked",
                                 "reasons": [{"id": "denylist", "name": "Denylist"}]})
            return httpx.Response(200, json={"Status": 0, **q, "Answer": [{"data": "0.0.0.0" if qtype == "A" else "::"}],
                                             "Additional": [{"data": "; EDE: 17 (Filtered): (Blocked by NextDNS: blacklist)"}]})
        self.logs.insert(0, {"timestamp": "2026-10-16T19:22:42.784Z", "domain": name, "status": "allowed" if allowed else "default",
                             "reasons": [{"id": "allowlist", "name": "Allowlist"}] if allowed else []})
        return httpx.Response(200, json={"Status": 0, **q, "Answer": [{"data": "93.184.215.14" if qtype == "A" else "2606:2800::1"}]})

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else None
        params = dict(request.url.params)
        path = request.url.raw_path.decode().split("?")[0]
        self.calls.append((request.method, path, params, body))
        if request.url.host == "dns.nextdns.io":
            return self.dns(path.strip("/"), params.get("name", ""), params.get("type", "A"))
        if request.headers.get("X-Api-Key") != KEY:
            return httpx.Response(403, text="Forbidden")
        if self.fail_next:
            return httpx.Response(self.fail_next.pop(0), json={"errors": [{"code": "busy"}]})
        return self.route(request.method, path, params, body)

    @staticmethod
    def ok(data=None, meta=None):
        if data is None:
            return httpx.Response(204)
        out = {"data": data}
        if meta is not None:
            out["meta"] = meta
        return httpx.Response(200, json=out)

    def route(self, method, path, params, body):
        if path in CATALOG:
            return self.ok(CATALOG[path])
        if path == "/profiles" and method == "POST":
            pid = f"new{len(self.profiles):03d}"
            blank = copy.deepcopy(PROFILE)
            blank.update(name=body["name"], denylist=[], allowlist=[], rewrites=[])
            blank["security"] = {k: False for k in blank["security"] if k != "tlds"} | {"tlds": []}
            blank["privacy"] = {"blocklists": [], "natives": [], "disguisedTrackers": False, "allowAffiliate": False}
            blank["parentalControl"]["services"] = []
            self.profiles[pid] = blank
            return self.ok({"id": pid, "fingerprint": pid, "role": "owner", "name": body["name"]})
        if path == "/profiles":
            return self.ok([{"id": k, "fingerprint": "fp" + k, "role": "owner", "name": v["name"]}
                            for k, v in self.profiles.items()])
        m = re.fullmatch(r"/profiles/(\w+)(/.*)?", path)
        if not m or m.group(1) not in self.profiles:
            return httpx.Response(404, json={"errors": [{"code": "notFound"}]})
        pid, rest = m.group(1), m.group(2) or ""
        prof = self.profiles[pid]
        if rest.startswith("/analytics/"):
            name = rest.split("/")[-1]
            got = self.analytics.get(name, {"data": []})
            return httpx.Response(200, json={"meta": {"pagination": {"cursor": None}}, **got})
        if rest == "/logs/stream":
            body = "".join(f"id: e{i}\ndata: {json.dumps(e)}\n\n" for i, e in enumerate(self.stream_events))
            return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})
        if rest == "/logs" and method == "GET":
            return self.ok(self.logs, {"pagination": {"cursor": None}, "stream": {"id": "s1"}})
        if rest == "/logs/download":
            return self.ok({"url": "https://api.nextdns.io/logs/" + pid + "/abc"})
        if rest == "/logs" and method == "DELETE":
            self.logs = []
            return self.ok()
        if not rest:
            if method == "DELETE":
                del self.profiles[pid]
                return self.ok()
            if method == "PATCH":
                prof.update(body)
                return self.ok()
            return self.ok({"id": pid, "fingerprint": "fp" + pid, **prof})
        parts = [p for p in rest.split("/") if p]
        from urllib.parse import unquote
        parts = [unquote(p) for p in parts]
        # walk to the object or list
        node, parent, key = prof, None, None
        for i, seg in enumerate(parts):
            if isinstance(node, dict) and seg in node:
                parent, key, node = node, seg, node[seg]
            elif isinstance(node, list) and i == len(parts) - 1:
                item = next((x for x in node if x.get("id") == seg), None)
                if item is None:
                    return httpx.Response(404, json={"errors": [{"code": "notFound"}]})
                if method == "DELETE":
                    node.remove(item)
                    return self.ok()
                if method == "PATCH":
                    item.update(body)
                    return self.ok()
                return self.ok(item)
            else:
                return httpx.Response(404, json={"errors": [{"code": "notFound"}]})
        if method == "GET":
            return self.ok(node)
        if method == "PATCH" and isinstance(node, dict):
            merge(node, body)
            return self.ok()
        if method == "POST" and isinstance(node, list) and key == "rewrites":
            self.next_id += 1
            node.append({"id": f"rw{self.next_id}", "name": body["name"], "type": "A", "content": body["content"]})
            return self.ok()
        if method == "PUT" and key == "rewrites":
            return httpx.Response(404, json={"errors": [{"code": "notFound"}]})
        if method == "POST" and isinstance(node, list):
            if not re.fullmatch(r"[a-z0-9.*_-]+", str(body.get("id", ""))):
                return httpx.Response(200, json={"errors": [{"code": "invalid", "source": {"pointer": "/id"}}]})
            if any(x.get("id") == body["id"] for x in node):
                return httpx.Response(200, json={"errors": [{"code": "duplicate"}]})
            node.append(body)
            return self.ok()
        if method == "PUT" and isinstance(node, list):
            parent[key] = body
            return self.ok()
        return httpx.Response(400, json={"errors": [{"code": "badRequest"}]})


@pytest.fixture(autouse=True)
def fake(monkeypatch):
    api = FakeNextDNS()
    monkeypatch.setattr(server, "TRANSPORT", httpx.MockTransport(api))
    monkeypatch.setattr(server, "SLEEP", lambda s: None)
    server._catalog_cache.clear()
    for f in (server.CHANGES_FILE, server.CREATED_FILE):
        f.unlink(missing_ok=True)
    shutil.rmtree(server.BACKUP_DIR, ignore_errors=True)
    monkeypatch.setenv("NEXTDNS_API_KEY", KEY)
    monkeypatch.setenv("NEXTDNS_PROFILES", "abc123=full,def456=read,Secret=hidden")
    server._confirms.clear()
    monkeypatch.setenv("NEXTDNS_DEFAULT_PROFILE", "Home")
    return api
