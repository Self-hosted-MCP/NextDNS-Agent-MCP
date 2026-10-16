# SPDX-License-Identifier: MIT
"""A small client for the NextDNS API (https://nextdns.github.io/api/).

Every call sends the X-Api-Key header. Replies are JSON with `data` (and sometimes `meta`); problems come back as
`errors`, sometimes with HTTP 200 (an invalid domain, a name already used), so every reply is checked for them.
"""

from __future__ import annotations

import time
from urllib.parse import quote

import httpx

BASE_URL = "https://api.nextdns.io"
RETRIES = 3


class NextDNSError(Exception):
    """A problem the user (or the AI) can act on, already in plain words."""


def explain(errors: list) -> str:
    parts = []
    for e in errors or []:
        if not isinstance(e, dict):
            parts.append(str(e))
            continue
        text = e.get("code") or "error"
        if e.get("detail"):
            text += f": {e['detail']}"
        source = e.get("source") or {}
        where = source.get("parameter") or source.get("pointer")
        if where:
            text += f" (at {where})"
        parts.append(text)
    return "; ".join(parts) or "unknown error"


def part(value: str) -> str:
    """One path segment, safe to put in a URL (domains, list IDs)."""
    return quote(str(value), safe="")


class Client:
    def __init__(self, api_key: str, base_url: str = BASE_URL, transport: httpx.BaseTransport | None = None,
                 timeout: float = 20.0, sleep=time.sleep):
        if not api_key:
            raise NextDNSError("No NextDNS API key. Set NEXTDNS_API_KEY (the key is at the bottom of "
                               "https://my.nextdns.io/account).")
        self.http = httpx.Client(base_url=base_url, transport=transport, timeout=timeout,
                                 headers={"X-Api-Key": api_key, "Accept": "application/json",
                                          "User-Agent": "nextdns-agent-mcp"})
        self.sleep = sleep

    def close(self) -> None:
        self.http.close()

    def request(self, method: str, path: str, params: dict | None = None, body=None) -> dict:
        """The whole JSON reply ({} for an empty one). Waits and tries again when NextDNS is busy."""
        params = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
        for attempt in range(RETRIES + 1):
            try:
                r = self.http.request(method, path, params=params, json=body)
            except httpx.HTTPError as exc:
                if attempt < RETRIES:
                    self.sleep(2 ** attempt)
                    continue
                raise NextDNSError(f"Can't reach NextDNS right now ({type(exc).__name__}). Try again in a moment.")
            if r.status_code in (429, 502, 503, 504) and attempt < RETRIES:
                wait = r.headers.get("Retry-After", "")
                self.sleep(min(float(wait), 30) if wait.replace(".", "", 1).isdigit() else 2 ** attempt)
                continue
            break
        if r.status_code in (401, 403):
            raise NextDNSError("NextDNS refused the API key (or this key may not do that). Check NEXTDNS_API_KEY.")
        if r.status_code == 404:
            raise NextDNSError(f"Not found: {path}")
        reply: dict = {}
        if r.content:
            try:
                reply = r.json()
            except ValueError:
                raise NextDNSError(f"NextDNS sent something unexpected (HTTP {r.status_code}).")
        if isinstance(reply, dict) and reply.get("errors"):
            raise NextDNSError("NextDNS said: " + explain(reply["errors"]))
        if r.status_code >= 400:
            raise NextDNSError(f"NextDNS answered HTTP {r.status_code}.")
        return reply if isinstance(reply, dict) else {"data": reply}

    def get(self, path: str, **params):
        return self.request("GET", path, params).get("data")

    def post(self, path: str, body):
        return self.request("POST", path, body=body).get("data")

    def patch(self, path: str, body):
        return self.request("PATCH", path, body=body).get("data")

    def put(self, path: str, body):
        return self.request("PUT", path, body=body).get("data")

    def delete(self, path: str):
        return self.request("DELETE", path).get("data")

    def page(self, path: str, **params) -> tuple[list, str | None, dict]:
        """One page of a list: (items, next cursor or None, meta)."""
        reply = self.request("GET", path, params)
        meta = reply.get("meta") or {}
        return reply.get("data") or [], (meta.get("pagination") or {}).get("cursor"), meta

    def stream(self, path: str, seconds: float, limit: int = 500, **params) -> list[dict]:
        """Log entries arriving on the live stream (server-sent events) during `seconds`."""
        import json
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        found: list[dict] = []
        end = time.time() + seconds
        try:
            with self.http.stream("GET", path, params=params,
                                  timeout=httpx.Timeout(10.0, read=max(1.0, seconds))) as r:
                if r.status_code in (401, 403):
                    raise NextDNSError("NextDNS refused the API key (or this key may not do that). Check NEXTDNS_API_KEY.")
                if r.status_code >= 400:
                    raise NextDNSError(f"NextDNS answered HTTP {r.status_code} for the live log.")
                for line in r.iter_lines():
                    if line.startswith("data:"):
                        try:
                            found.append(json.loads(line[5:].strip()))
                        except ValueError:
                            pass
                    if time.time() >= end or len(found) >= limit:
                        break
        except httpx.ReadTimeout:
            pass   # the time is up and nothing more came
        except httpx.HTTPError as exc:
            raise NextDNSError(f"The live log stopped ({type(exc).__name__}).")
        return found


DOH_URL = "https://dns.nextdns.io"


def doh(profile_id: str, name: str, qtype: str = "A", transport: httpx.BaseTransport | None = None) -> dict:
    """Asks the profile's own DNS-over-HTTPS server, like a device using it would (JSON answer)."""
    try:
        with httpx.Client(transport=transport, timeout=10.0) as h:
            r = h.get(f"{DOH_URL}/{part(profile_id)}", params={"name": name, "type": qtype},
                      headers={"Accept": "application/dns-json"})
            return r.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise NextDNSError(f"The DNS test query didn't work ({type(exc).__name__}).")
