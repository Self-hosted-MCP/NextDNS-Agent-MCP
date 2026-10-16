# SPDX-License-Identifier: MIT
"""Logins for the web version: AI apps connect with OAuth and you allow them with your passphrase; the settings page
uses the same passphrase with a cookie.

Single user, no accounts. Tokens are random strings; files keep only their fingerprints (store.token_key).
"""

from __future__ import annotations

import hmac
import json
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    RegistrationError,
    TokenError,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

from .store import check_passphrase, private_write, read_json, token_key

MIN_PASSPHRASE = 6   # short is fine: five wrong tries lock the logins for 15 minutes


def passphrase_ok(passphrase: str, cfg: dict) -> bool:
    """LOGIN_HASH (from set-passphrase) wins; LOGIN_PASSPHRASE is the plain one for hosting dashboards."""
    if cfg.get("LOGIN_HASH"):
        return check_passphrase(passphrase, cfg["LOGIN_HASH"])
    plain = cfg.get("LOGIN_PASSPHRASE", "")
    return bool(plain) and hmac.compare_digest(passphrase.encode(), plain.encode())


def public_url(cfg: dict) -> str:
    """PUBLIC_URL, or the address Render or Railway gives the app, or localhost."""
    if cfg.get("PUBLIC_URL"):
        return cfg["PUBLIC_URL"].rstrip("/")
    if cfg.get("RENDER_EXTERNAL_URL"):
        return cfg["RENDER_EXTERNAL_URL"].rstrip("/")
    if cfg.get("RAILWAY_PUBLIC_DOMAIN"):
        return f"https://{cfg['RAILWAY_PUBLIC_DOMAIN']}"
    return f"http://localhost:{cfg.get('PORT') or 8766}"


SCOPE = "nextdns"


class PassphraseOAuth:
    """The AI app registers, you type your passphrase once and tick its profiles, the app gets tokens."""

    ACCESS_TTL = 3600   # short-lived: a leaked key stops working within the hour
    REFRESH_TTL = 90 * 24 * 3600
    MAX_CLIENTS = 50   # registering is open to anyone, so keep the list from growing forever

    def __init__(self, public_url: str, redirect_hosts: list[str], path: Path, check):
        """check(passphrase) -> bool."""
        self.public_url = public_url.rstrip("/")
        self.redirect_hosts = [h.lower() for h in redirect_hosts]
        self.path = path
        self.check = check
        self.lock = threading.Lock()
        self.pending: dict[str, tuple[float, str, AuthorizationParams]] = {}
        self.codes: dict[str, AuthorizationCode] = {}
        self.failures: list[float] = []
        data = read_json(path, {})
        self.clients = {k: OAuthClientInformationFull.model_validate(v) for k, v in data.get("clients", {}).items()}
        self.access = {k: AccessToken.model_validate(v) for k, v in data.get("access", {}).items()}
        self.refresh = {k: RefreshToken.model_validate(v) for k, v in data.get("refresh", {}).items()}
        # app -> {"profiles": [ids ticked on the login page], "change": may it change them}
        self.grants: dict[str, dict] = data.get("grants", {})

    def save(self) -> None:
        now = time.time()
        self.access = {k: v for k, v in self.access.items() if not v.expires_at or v.expires_at > now}
        self.refresh = {k: v for k, v in self.refresh.items() if not v.expires_at or v.expires_at > now}
        private_write(self.path, json.dumps({
            "clients": {k: v.model_dump(mode="json") for k, v in self.clients.items()},
            "access": {k: v.model_dump(mode="json") for k, v in self.access.items()},
            "refresh": {k: v.model_dump(mode="json") for k, v in self.refresh.items()},
            "grants": self.grants,
        }, indent=1))

    def redirect_ok(self, uri) -> bool:
        p = urlparse(str(uri))
        host = (p.hostname or "").lower()
        if host in ("localhost", "127.0.0.1", "::1"):
            return p.scheme in ("http", "https")
        return p.scheme == "https" and any(host == h or host.endswith("." + h) for h in self.redirect_hosts)

    def app_name(self, client_id: str) -> str:
        client = self.clients.get(client_id)
        return (client.client_name if client else None) or "An AI app"

    async def get_client(self, client_id: str):
        return self.clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        bad = [str(u) for u in (client_info.redirect_uris or []) if not self.redirect_ok(u)]
        if bad:
            raise RegistrationError("invalid_redirect_uri", f"Redirect not allowed: {', '.join(bad)}")
        with self.lock:
            # every connection attempt registers first, before the passphrase: forget the ones that never logged in
            cutoff = time.time() - 3600
            for cid in [cid for cid, c in self.clients.items()
                        if (c.client_id_issued_at or 0) < cutoff and cid not in self.grants]:
                del self.clients[cid]
            while len(self.clients) >= self.MAX_CLIENTS:
                oldest = min(self.clients, key=lambda k: self.clients[k].client_id_issued_at or 0)
                del self.clients[oldest]
            self.clients[client_info.client_id] = client_info
            self.save()

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        if not self.redirect_ok(params.redirect_uri):
            raise AuthorizeError("invalid_request", "Redirect not allowed")
        req = secrets.token_urlsafe(24)
        with self.lock:
            self.pending = {k: v for k, v in self.pending.items() if v[0] > time.time()}
            self.pending[req] = (time.time() + 600, client.client_id, params)
        return f"{self.public_url}/login?req={req}"

    def describe(self, req: str) -> tuple[str, str] | None:
        """(app name, where the login goes back to) for a waiting login, shown on the login page."""
        entry = self.pending.get(req)
        if not entry or entry[0] < time.time():
            return None
        return self.app_name(entry[1]), urlparse(str(entry[2].redirect_uri)).hostname or "?"

    def locked_out(self) -> bool:
        cutoff = time.time() - 900
        self.failures = [t for t in self.failures if t > cutoff]
        return len(self.failures) >= 5

    def complete_login(self, req: str, passphrase: str, profiles: list[str], change: bool) -> str | None:
        """The redirect back to the app on success, None on a wrong passphrase. profiles: the IDs ticked."""
        if not profiles:
            raise ValueError("Tick at least one profile.")
        with self.lock:
            if self.locked_out():
                raise PermissionError("Too many wrong tries. Wait 15 minutes.")
            entry = self.pending.get(req)
            if not entry or entry[0] < time.time():
                raise LookupError("This login link expired. Start the connection again in your AI app.")
            if not self.check(passphrase):
                self.failures.append(time.time())
                return None
            del self.pending[req]
            _, client_id, params = entry
            self.grants[client_id] = {"profiles": sorted(set(profiles)), "change": bool(change), "since": time.time()}
            self.save()
            code = secrets.token_urlsafe(32)
            self.codes[code] = AuthorizationCode(
                code=code, scopes=params.scopes or [SCOPE], expires_at=time.time() + 300, client_id=client_id,
                code_challenge=params.code_challenge, redirect_uri=params.redirect_uri,
                redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
                resource=params.resource, subject="owner")
        return construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state)

    def add_profile(self, client_id: str, pid: str) -> None:
        """A profile the app made itself joins its grant."""
        with self.lock:
            grant = self.grants.get(client_id)
            if grant is not None and pid not in grant["profiles"]:
                grant["profiles"].append(pid)
                self.save()

    def drop_profile(self, pid: str) -> None:
        """A deleted profile leaves every app's grant."""
        with self.lock:
            changed = False
            for grant in self.grants.values():
                if pid in grant.get("profiles", []):
                    grant["profiles"].remove(pid)
                    changed = True
            if changed:
                self.save()

    def set_grant(self, client_id: str, profiles: list[str], change: bool) -> None:
        with self.lock:
            if client_id in self.grants:
                self.grants[client_id].update(profiles=sorted(set(profiles)), change=bool(change))
                self.save()

    async def load_authorization_code(self, client, authorization_code: str):
        code = self.codes.get(authorization_code)
        if code and code.client_id == client.client_id and code.expires_at > time.time():
            return code
        return None

    def issue(self, client_id: str, scopes: list[str], resource: str | None) -> OAuthToken:
        now = int(time.time())
        access, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        a_key, r_key = token_key(access), token_key(refresh)
        self.access[a_key] = AccessToken(token=a_key, client_id=client_id, scopes=scopes,
                                         expires_at=now + self.ACCESS_TTL, resource=resource, subject="owner")
        self.refresh[r_key] = RefreshToken(token=r_key, client_id=client_id, scopes=scopes,
                                           expires_at=now + self.REFRESH_TTL, resource=resource, subject="owner")
        self.save()
        return OAuthToken(access_token=access, token_type="Bearer", expires_in=self.ACCESS_TTL,
                          refresh_token=refresh, scope=" ".join(scopes))

    async def exchange_authorization_code(self, client, authorization_code: AuthorizationCode) -> OAuthToken:
        with self.lock:
            if self.codes.pop(authorization_code.code, None) is None:
                raise TokenError("invalid_grant", "Code already used")
            return self.issue(client.client_id, authorization_code.scopes, authorization_code.resource)

    async def load_refresh_token(self, client, refresh_token: str):
        tok = self.refresh.get(token_key(refresh_token))
        if tok and tok.client_id == client.client_id and (not tok.expires_at or tok.expires_at > time.time()):
            return tok.model_copy(update={"token": refresh_token})
        return None

    async def exchange_refresh_token(self, client, refresh_token: RefreshToken, scopes: list[str]) -> OAuthToken:
        with self.lock:
            if self.refresh.pop(token_key(refresh_token.token), None) is None:
                raise TokenError("invalid_grant", "Refresh token already used")
            return self.issue(client.client_id, scopes or refresh_token.scopes, refresh_token.resource)

    async def load_access_token(self, token: str):
        tok = self.access.get(token_key(token))
        if tok and (not tok.expires_at or tok.expires_at > time.time()) and self.for_us(tok.resource) \
                and tok.client_id in self.grants:
            return tok.model_copy(update={"token": token})
        return None

    def for_us(self, resource) -> bool:
        """A key issued for a different server (another 'resource') is never accepted here."""
        if not resource:
            return True
        r = str(resource).rstrip("/").lower()
        return r in (self.public_url.lower(), f"{self.public_url.lower()}/mcp")

    async def revoke_token(self, token) -> None:
        self.disconnect(token.client_id, forget=False)

    def disconnect(self, client_id: str, forget: bool = True) -> None:
        """Log an app out. forget=True also removes it and its profile choice (the settings page's Disconnect)."""
        with self.lock:
            self.access = {k: v for k, v in self.access.items() if v.client_id != client_id}
            self.refresh = {k: v for k, v in self.refresh.items() if v.client_id != client_id}
            if forget:
                self.clients.pop(client_id, None)
                self.grants.pop(client_id, None)
            self.save()


class Sessions:
    """Settings page sign-ins: a random cookie, kept as a fingerprint. Remembered ones survive a restart."""

    SHORT = 12 * 3600
    REMEMBER = 90 * 24 * 3600

    def __init__(self, path: Path, mark):
        """mark() changes when the passphrase changes, which signs everyone out."""
        self.path = path
        self.mark = mark
        self.lock = threading.Lock()
        self.items: dict[str, dict] = {k: v for k, v in read_json(path, {}).items() if v.get("expires", 0) > time.time()}

    def _save(self) -> None:
        private_write(self.path, json.dumps({k: v for k, v in self.items.items() if v.get("remember")}))

    def new(self, remember: bool) -> str:
        with self.lock:
            now = time.time()
            self.items = {k: v for k, v in self.items.items() if v["expires"] > now}
            token = secrets.token_urlsafe(32)
            self.items[token_key(token)] = {"expires": now + (self.REMEMBER if remember else self.SHORT),
                                            "csrf": secrets.token_urlsafe(24), "pp": self.mark(), "remember": remember}
            self._save()
            return token

    def get(self, token: str) -> dict | None:
        if not token:
            return None
        s = self.items.get(token_key(token))
        if s and s["expires"] > time.time() and hmac.compare_digest(s["pp"], self.mark()):
            return s
        return None

    def end(self, token: str) -> None:
        with self.lock:
            if self.items.pop(token_key(token), None) is not None:
                self._save()
