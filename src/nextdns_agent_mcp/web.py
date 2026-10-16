# SPDX-License-Identifier: Apache-2.0
"""The web version's pages: /login (AI apps connecting), /settings, /health and the icon.

Forms post to /settings/save with a "kind": key, profiles, safety, app or undo. Every post needs the page's CSRF
token and must come from this server's own pages.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import re
import time
from urllib.parse import urlparse

from mcp.server.mcpserver.exceptions import ToolError
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from . import pages
from .api import Client, NextDNSError
from .auth import PassphraseOAuth, Sessions, passphrase_ok

COOKIE = "nextdns_settings"


def same_origin(request: Request) -> bool:
    """A form post must come from this server's own pages (blocks other websites posting into the settings)."""
    origin = request.headers.get("origin")
    if not origin or origin == "null":
        return request.headers.get("sec-fetch-site", "same-origin") in ("same-origin", "none")
    return urlparse(origin).netloc == (request.headers.get("host") or "")


def safe_next(path: str) -> bool:
    return (path.startswith("/") and not path.startswith("//") and len(path) < 2000
            and not any(c in path for c in "\\\r\n\t"))


def add_routes(server, provider: PassphraseOAuth, core) -> Sessions:
    """core: the server module (settings, profiles, the change log)."""
    secure = provider.public_url.startswith("https://")
    cookie = ("__Host-" + COOKIE) if secure else COOKIE

    def mark() -> str:
        env = core.env_settings()
        return hashlib.sha256((env.get("LOGIN_HASH") or env.get("LOGIN_PASSPHRASE") or "").encode()).hexdigest()[:16]

    sessions = Sessions(core.STATE_DIR / "sessions.json", mark)
    if secure:   # browsers then always use HTTPS for these pages
        pages.HEADERS["Strict-Transport-Security"] = "max-age=31536000"

    def look(request: Request) -> None:
        theme = request.cookies.get("theme", "")
        pages.THEME.set(theme if theme in ("light", "dark") else "")
        here = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        pages.HERE_PATH.set(here if safe_next(here) else "/settings")

    def html(body: str, status: int = 200) -> HTMLResponse:
        return HTMLResponse(body, status_code=status, headers=pages.HEADERS)

    def profile_choices() -> tuple[list[tuple[str, str, str]], str]:
        """Profiles the login page offers: every one not hidden. Or why there are none."""
        cfg = core.config()
        try:
            c = Client(cfg.get("NEXTDNS_API_KEY", ""), transport=core.TRANSPORT)
            try:
                shown = [p for p in c.get("/profiles") or [] if core.mode_of(p, cfg) != "hidden"]
            finally:
                c.close()
        except NextDNSError as exc:
            return [], f"{exc} Add your NextDNS API key on the settings page first: {provider.public_url}/settings"
        return [(p["id"], p.get("name") or p["id"], core.mode_of(p, cfg)) for p in shown], ""

    def login_page(req: str, error: str = "", status: int = 200) -> HTMLResponse:
        info = provider.describe(req)
        profiles, problem = profile_choices() if info else ([], "")
        return html(pages.login(info[0] if info else None, info[1] if info else None, req, profiles, error,
                                f"{provider.public_url}/settings", problem), status)

    @server.custom_route("/login", methods=["GET", "POST"])
    async def login(request: Request) -> Response:
        look(request)
        if request.method != "POST":   # GET, and HEAD from link previews
            return await asyncio.to_thread(login_page, request.query_params.get("req", ""))
        form = await request.form()
        req = str(form.get("req", ""))
        known = {pid for pid, _n, _m in (await asyncio.to_thread(profile_choices))[0]}
        chosen = [str(p) for p in form.getlist("profile") if str(p) in known]
        try:
            target = provider.complete_login(req, str(form.get("passphrase", "")), chosen, form.get("change") == "yes")
        except (PermissionError, LookupError, ValueError) as exc:
            return await asyncio.to_thread(login_page, req, str(exc), 400 if isinstance(exc, ValueError) else 403)
        if target is None:
            await asyncio.sleep(1)   # slows down guessing
            return await asyncio.to_thread(login_page, req, "Wrong passphrase.", 401)
        return RedirectResponse(target, status_code=302, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})

    @server.custom_route("/health", methods=["GET"])
    async def health(request: Request) -> Response:
        return Response("ok")

    @server.custom_route("/icon.svg", methods=["GET"])
    async def icon(request: Request) -> Response:
        return Response(pages.ICON_SVG, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    @server.custom_route("/favicon.ico", methods=["GET"])
    async def favicon(request: Request) -> Response:
        return Response(pages.ICON_SVG, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    @server.custom_route("/theme", methods=["POST"])
    async def theme(request: Request) -> Response:
        """Light or dark for this browser: device -> light -> dark -> device. Only a look, kept a year."""
        form = await request.form()
        now = request.cookies.get("theme", "")
        nxt = {"": "light", "light": "dark"}.get(now, "")
        back = str(form.get("next", "/settings"))
        r = RedirectResponse(back if safe_next(back) else "/settings", status_code=303)
        r.set_cookie("theme", nxt, max_age=365 * 24 * 3600 if nxt else 0, httponly=True, secure=secure, samesite="lax")
        return r

    if not core.is_on(core.env_settings().get("SETTINGS_PAGE") or "on"):
        return sessions

    def with_cookie(response: Response, token: str, max_age: int | None) -> Response:
        response.set_cookie(cookie, token, max_age=max_age, httponly=True, secure=secure, samesite="strict",
                            path="/" if secure else "/settings")
        return response

    def session_of(request: Request) -> dict | None:
        return sessions.get(request.cookies.get(cookie, ""))

    @server.custom_route("/settings", methods=["GET"])
    async def settings_home(request: Request) -> Response:
        look(request)
        s = session_of(request)
        if s is None:
            return html(pages.settings_login())
        flash = s.pop("flash", None)
        return html(await asyncio.to_thread(settings_page, s["csrf"], flash))

    @server.custom_route("/settings/login", methods=["POST"])
    async def settings_login(request: Request) -> Response:
        look(request)
        if not same_origin(request):
            return Response("Forbidden", status_code=403)
        form = await request.form()
        with provider.lock:
            locked = provider.locked_out()
        if locked:
            return html(pages.settings_login("Too many wrong tries. Wait 15 minutes."), 403)
        if not passphrase_ok(str(form.get("passphrase", "")), core.env_settings()):
            with provider.lock:
                provider.failures.append(time.time())
            await asyncio.sleep(1)   # slows down guessing
            return html(pages.settings_login("Wrong passphrase."), 401)
        remember = form.get("remember") == "yes"
        token = sessions.new(remember)
        return with_cookie(RedirectResponse("/settings", status_code=303, headers={"Cache-Control": "no-store"}),
                           token, Sessions.REMEMBER if remember else None)

    @server.custom_route("/settings/backup/{backup_id}", methods=["GET"])
    async def backup_download(request: Request) -> Response:
        if session_of(request) is None:
            return RedirectResponse("/settings", status_code=303)
        try:
            b = core.load_backup(request.path_params["backup_id"])
        except ToolError:
            return Response("Not found", status_code=404)
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", f"nextdns-{b.get('profile_name') or b['profile']}-{b['id']}") + ".json"
        return Response(json.dumps(b, indent=1), media_type="application/json",
                        headers={**pages.HEADERS, "Content-Disposition": f'attachment; filename="{name}"'})

    @server.custom_route("/settings/logout", methods=["POST"])
    async def settings_logout(request: Request) -> Response:
        form = await request.form()
        s = session_of(request)
        if s and same_origin(request) and hmac.compare_digest(str(form.get("csrf", "")), s["csrf"]):
            sessions.end(request.cookies.get(cookie, ""))
        return with_cookie(RedirectResponse("/settings", status_code=303), "", 0)

    @server.custom_route("/settings/save", methods=["POST"])
    async def settings_save(request: Request) -> Response:
        s = session_of(request)
        if s is None:
            return RedirectResponse("/settings", status_code=303)
        form = await request.form()
        if not same_origin(request) or not hmac.compare_digest(str(form.get("csrf", "")), s["csrf"]):
            return Response("Forbidden: this form didn't come from the settings page.", status_code=403)
        kind = str(form.get("kind", ""))
        if kind == "backup" and form.get("action") == "upload":
            upload = form.get("file")
            data = await upload.read(2_000_001) if hasattr(upload, "read") else b""
            form = {**dict(form), "file_text": data[:2_000_000].decode("utf-8", "replace") if len(data) <= 2_000_000 else ""}
        try:
            s["flash"] = await asyncio.to_thread(save, kind, form)
        except (ToolError, NextDNSError, ValueError) as exc:
            s["flash"] = ("error", str(exc))
        tab = {"key": "key", "profiles": "profiles", "safety": "safety", "app": "apps", "undo": "changes",
               "backup": "backups", "update": "about"}.get(kind, "")
        return RedirectResponse("/settings" + (f"#{tab}" if tab else ""), status_code=303,
                                headers={"Cache-Control": "no-store"})

    def save(kind: str, form) -> tuple[str, str]:
        locked = core.locked_settings()
        if kind == "key":
            if "NEXTDNS_API_KEY" in locked:
                raise ValueError("The API key is set in the settings file or hosting variables.")
            if form.get("action") == "remove":
                core.save_api_key("")
                return "ok", "Removed the API key."
            key = str(form.get("api_key", "")).strip()
            c = Client(key, transport=core.TRANSPORT)
            try:
                found = c.get("/profiles") or []
            finally:
                c.close()
            core.save_api_key(key)
            return "ok", f"The key works: {len(found)} profile(s) in the account. Saved."
        if kind == "profiles":
            modes = []
            for k in form.keys():
                if k.startswith("mode_"):
                    modes.append(f"{k[5:]}={core.clean_mode(str(form.get(k)))}")
            values = {"NEXTDNS_DEFAULT_PROFILE": str(form.get("default_profile", ""))}
            if "NEXTDNS_PROFILES" not in locked:
                values["NEXTDNS_PROFILES"] = ",".join(modes)
            core.save_page_settings({k: v for k, v in values.items() if k not in locked})
            return "ok", "Saved the profiles."
        if kind == "safety":
            values = {"NEXTDNS_READ_ONLY": "on" if form.get("NEXTDNS_READ_ONLY") == "yes" else "off",
                      "NEXTDNS_ALLOW_DELETE": "on" if form.get("NEXTDNS_ALLOW_DELETE") == "yes" else "off",
                      "NEXTDNS_DEFAULT_MODE": core.clean_mode(str(form.get("NEXTDNS_DEFAULT_MODE", "full")))}
            core.save_page_settings({k: v for k, v in values.items() if k not in locked})
            return "ok", "Saved."
        if kind == "app":
            cid = str(form.get("client_id", ""))
            if cid not in provider.grants:
                raise ValueError("That app isn't connected.")
            if form.get("action") == "disconnect":
                name = provider.app_name(cid)
                provider.disconnect(cid)
                return "ok", f"Disconnected {name}. It has to log in again to use NextDNS."
            provider.set_grant(cid, [str(p) for p in form.getlist("profile")], form.get("change") == "yes")
            return "ok", f"Saved what {provider.app_name(cid)} may do."
        if kind == "undo":
            entry = next((e for e in core.read_changes() if e["id"] == str(form.get("change_id", ""))), None)
            if entry and entry.get("kind") == "create" and form.get("sure") != "yes":
                raise ValueError("Tick the box to confirm deleting that profile.")
            return "ok", core.do_undo(str(form.get("change_id", "")), force=form.get("force") == "yes", owner=True)
        if kind == "update":
            if "UPDATE_CHECK" in locked:
                raise ValueError("The update check is set in the settings file or hosting variables. Change it there.")
            on = form.get("UPDATE_CHECK") == "yes"
            core.save_page_settings({"UPDATE_CHECK": "on" if on else "off"})
            if on:
                core.update_status(force=True)
            return "ok", "Update check on." if on else "Update check off."
        if kind == "backup":
            action = form.get("action")
            if action == "make":
                return "ok", core.backup(str(form.get("profile", "")), "made on the settings page").split(" restore_backup")[0]
            if action == "upload":
                if not form.get("file_text"):
                    raise ValueError("Choose a backup file (2 MB at most).")
                b = core.backup_from_file(str(form["file_text"]))
                return "ok", f"Added backup {b['id']} of {b['profile_name']}."
            bid = str(form.get("backup_id", ""))
            b = core.load_backup(bid)
            if action == "delete":
                (core.BACKUP_DIR / f"{b['id']}.json").unlink(missing_ok=True)
                return "ok", f"Deleted backup {b['id']}."
            if action == "new":
                return "ok", core.restore_backup(bid, new_profile_name=str(form.get("name", "")).strip())
            if action == "restore":
                if form.get("sure") != "yes":
                    raise ValueError("Tick the box to confirm overwriting the profile.")
                ask = core.restore_backup(bid)
                code = re.search(r"confirm_code='(\w+)'", ask)
                return "ok", core.restore_backup(bid, confirm_code=code.group(1)) if code else ask
        raise ValueError("Unknown form.")

    def settings_page(csrf: str, flash) -> str:
        cfg = core.config()
        env = core.env_settings()
        key = cfg.get("NEXTDNS_API_KEY", "")
        key_info = {"set": bool(key), "source": "env" if env.get("NEXTDNS_API_KEY") else "page", "last4": key[-4:]}
        profiles, problem = [], ""
        if key:
            try:
                c = Client(key, transport=core.TRANSPORT)
                try:
                    created = core.created_profiles()
                    profiles = [{"id": p["id"], "name": p.get("name") or p["id"], "mode": core.mode_of(p, cfg),
                                 "created": p["id"] in created} for p in c.get("/profiles") or []]
                finally:
                    c.close()
            except NextDNSError as exc:
                problem = str(exc)
        else:
            problem = "Add the API key first."
        options = {"read_only": core.server_read_only(cfg),
                   "allow_delete": core.is_on(cfg.get("NEXTDNS_ALLOW_DELETE") or "on"),
                   "default_mode": core.clean_mode(cfg.get("NEXTDNS_DEFAULT_MODE")),
                   "NEXTDNS_DEFAULT_PROFILE": cfg.get("NEXTDNS_DEFAULT_PROFILE", "")}
        apps = [{"client_id": cid, "name": provider.app_name(cid), "profiles": g.get("profiles", []),
                 "change": g.get("change", False)} for cid, g in provider.grants.items()]
        changes = core.read_changes()[::-1][:40]
        return pages.settings(csrf, flash, key_info, profiles, problem, options, core.locked_settings(), apps,
                              changes, {"version": core.current_version(), "public_url": provider.public_url,
                                        "update": core.update_status()},
                              core.list_backups())

    return sessions
