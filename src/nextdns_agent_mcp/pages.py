# SPDX-License-Identifier: Apache-2.0
"""The web pages: the login page AI apps open, and the settings page.

Plain HTML and CSS, no scripts, nothing loaded from elsewhere (see HEADERS), so the pages work under a strict
Content-Security-Policy. Light and dark follow the device, unless the visitor picked one (a cookie). Every value put
into a page goes through esc() first. The logic behind the pages lives in web.py. The look is the same as
Selfhost-Remote-Mail-MCP's.
"""

from __future__ import annotations

import contextvars
import html
import re
import string

from .i18n import LANG, _

PROJECT = "NextDNS-Agent-MCP"
PROJECT_URL = "https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP"
AUTHOR = "s17sh70x2jfl031ag"

# Never cached, never shown inside another site, never telling other sites where you came from.
HEADERS = {
    "Cache-Control": "no-store",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; "
                               "form-action 'self' https: http://localhost:* http://127.0.0.1:*; frame-ancestors 'none'; base-uri 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}

esc = html.escape

ICON_MARK = ('<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><path d="M16 4 6 8v7c0 6.2 4.3 11 10 13 5.7-2 10-6.8 10-13V8z"/>'
             '<path d="m11.5 16 3.2 3.2 6-6.4"/></svg>')
ICON_SHIELD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z"/>'
               '<path d="M12 8v5"/><path d="M12 16.5v.01"/></svg>')
ICON_ALERT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5"/>'
              '<path d="M12 16.5v.01"/></svg>')
ICON_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.6 2.6L16 9.5"/></svg>')
# The shield mark, as the favicon and the icon AI apps may show next to this server.
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1d4ed8"/>
<g fill="none" stroke="#fff" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round">
<path d="M32 12 18 18v10c0 9 6 16 14 19 8-3 14-10 14-19V18z"/></g><path d="m25.5 31 4.6 4.6 8.4-9" fill="none" stroke="#ffb547" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

_svg = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true">')
THEME_ICONS = {   # what the button shows: the look now
    "": _svg + '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor" stroke="none"/></svg>',
    "light": _svg + '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2'
             'M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg>',
    "dark": _svg + '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>',
}
THEME_LABELS = {"": "Light or dark: like your device. Tap to change.", "light": "Light. Tap to change.",
                "dark": "Dark. Tap to change."}
THEME = contextvars.ContextVar("theme", default="")      # "", "light" or "dark", from the visitor's cookie
HERE_PATH = contextvars.ContextVar("here", default="/")  # the page's own address, to come back to after a tap

MODE_LABELS = {"full": "Read and change", "read": "Read only", "hidden": "Hidden"}

CSS = """
:root{--brand:#1d4ed8;--brand-deep:#1e3a9e;--on-brand:#fff;--on-brand-soft:#dbe6ff;--page:#eef2f8;--card:#fff;
--ink:#16142a;--ink-soft:#4d4a66;--line:#cdcae0;--line-soft:#e6e4f1;--field:#fff;--error:#b42318;--error-bg:#fdecea;
--ok:#12703f;--ok-bg:#e5f5ec;--chip:#e3ebff;--chip-ink:#1e3a9e;--warn:#8a4b00;--warn-bg:#fff3d6;
--lime:#ffb547;--lime-ink:#3d2400;--pink:#ff9f43;--pink-ink:#8a4600;
--shadow:0 18px 40px -18px rgba(15,30,80,.35),0 2px 6px rgba(15,30,80,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--brand:#2554d6;--brand-deep:#1d46b8;--page:#0f0e17;--card:#181725;
--ink:#efeef8;--ink-soft:#aba8c4;--line:#37344c;--line-soft:#28263a;--field:#0f0e17;--error:#ff8f80;--error-bg:#3a1c1a;
--ok:#6fd49b;--ok-bg:#143022;--chip:#1b2a4d;--chip-ink:#b8cbff;--warn:#ffc46b;--warn-bg:#3a2a10;
--lime:#ffbf5e;--lime-ink:#3d2400;--pink:#ffb366;--pink-ink:#ffb366;
--shadow:0 18px 40px -18px rgba(0,0,0,.7),0 2px 6px rgba(0,0,0,.4)}}
:root[data-theme=dark]{--brand:#2554d6;--brand-deep:#1d46b8;--page:#0f0e17;--card:#181725;
--ink:#efeef8;--ink-soft:#aba8c4;--line:#37344c;--line-soft:#28263a;--field:#0f0e17;--error:#ff8f80;--error-bg:#3a1c1a;
--ok:#6fd49b;--ok-bg:#143022;--chip:#1b2a4d;--chip-ink:#b8cbff;--warn:#ffc46b;--warn-bg:#3a2a10;
--lime:#ffbf5e;--lime-ink:#3d2400;--pink:#ffb366;--pink-ink:#ffb366;
--shadow:0 18px 40px -18px rgba(0,0,0,.7),0 2px 6px rgba(0,0,0,.4)}
:root[data-theme=light]{color-scheme:light}:root[data-theme=dark]{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:var(--page);color:var(--ink);
font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
display:flex;flex-direction:column;align-items:center;padding:clamp(0px,6vh,72px) 0 32px}
main{width:100%;max-width:440px;background:var(--card);box-shadow:var(--shadow);overflow:clip}
main.wide{max-width:760px}
@media (min-width:480px){main{border-radius:22px}}
@media (max-width:479px){body{padding:0 0 28px;background:var(--card)}main{box-shadow:none}}
.hero{position:relative;background:var(--brand);color:var(--on-brand);padding:28px 28px 32px}
.theme{position:absolute;top:22px;right:22px;margin:0}
.theme button{display:grid;place-items:center;width:40px;height:40px;padding:0;border-radius:999px;box-shadow:none;
background:color-mix(in srgb,var(--on-brand) 14%,transparent);color:var(--on-brand-soft)}
.theme button:hover,.theme button:focus-visible{background:color-mix(in srgb,var(--on-brand) 26%,transparent);color:var(--on-brand)}
.theme svg{width:19px;height:19px}
.mark{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:-.01em;color:var(--on-brand-soft)}
.mark::after{content:"";width:7px;height:7px;border-radius:2px;background:var(--pink);margin-left:-2px}
.mode{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.mode select{width:auto;min-width:150px}
button:disabled,select:disabled{opacity:.55;cursor:not-allowed}
table.log{width:100%;border-collapse:collapse;font-size:.92rem}table.log td{padding:8px 6px;border-top:1.5px solid var(--line-soft);vertical-align:top}
.hl{background:linear-gradient(transparent 62%,var(--lime) 62%,var(--lime) 92%,transparent 92%);color:var(--on-brand);padding:0 .04em}
.hero .hl{background:linear-gradient(transparent 58%,var(--lime) 58%,var(--lime) 90%,transparent 90%);color:var(--on-brand);
text-shadow:1px 0 0 var(--brand-deep),-1px 0 0 var(--brand-deep),0 1px 0 var(--brand-deep),0 -1px 0 var(--brand-deep),
1px 1px 0 var(--brand-deep),-1px 1px 0 var(--brand-deep),1px -1px 0 var(--brand-deep),-1px -1px 0 var(--brand-deep),0 0 4px var(--brand-deep)}
.tabs{position:sticky;top:0;z-index:2;display:flex;gap:4px;overflow-x:auto;padding:10px 20px;background:color-mix(in srgb,var(--card) 92%,transparent);
backdrop-filter:saturate(1.4) blur(10px);-webkit-backdrop-filter:saturate(1.4) blur(10px);border-bottom:1.5px solid var(--line-soft);scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tabs a{flex:none;color:var(--ink-soft);text-decoration:none;font-weight:700;font-size:.9rem;padding:7px 13px;border-radius:999px;transition:background .15s,color .15s}
.tabs a:hover,.tabs a:focus-visible{background:var(--lime);color:var(--lime-ink);outline:none}
.tabs a.on{background:var(--chip);color:var(--chip-ink)}
.back{display:inline-flex;align-items:center;gap:6px;margin-top:26px;padding:8px 16px 8px 10px;border-radius:999px;
background:color-mix(in srgb,var(--on-brand) 16%,transparent);color:var(--on-brand);font-weight:700;font-size:.95rem;
text-decoration:none;transition:background .15s,color .15s}
.back svg{width:18px;height:18px;flex:none}
.back:hover,.back:focus-visible{background:var(--lime);color:var(--lime-ink);outline:none}
.back + h1{margin-top:22px}
section[id],h2[id]{scroll-margin-top:72px}
.mark svg{width:30px;height:30px;flex:none}
.mark path{stroke-dasharray:90;stroke-dashoffset:0;animation:draw .8s cubic-bezier(.16,1,.3,1) both}
@keyframes draw{from{stroke-dashoffset:90}}
@media (prefers-reduced-motion:reduce){.mark path{animation:none}}
h1{margin:44px 0 10px;font-size:clamp(2rem,8vw,2.6rem);line-height:1.05;letter-spacing:-.035em;font-weight:800;text-wrap:balance}
.hero p{margin:0;color:var(--on-brand-soft);font-size:1.02rem;max-width:46ch}
.hero b{color:var(--on-brand);font-weight:650}
.body{padding:28px}
h2{font-size:1.2rem;letter-spacing:-.02em;margin:40px 0 4px;display:flex;align-items:center;gap:9px}
h2::before{content:"";width:6px;height:6px;border-radius:2px;background:var(--pink);flex:none}
h2:first-child{margin-top:0}
.lead{margin:0 0 16px;color:var(--ink-soft)}
label{display:block;font-weight:650;margin:0 0 8px}
input,select,textarea{width:100%;font:inherit;font-size:1.02rem;padding:12px 14px;border-radius:12px;border:1.5px solid var(--line);
background:var(--field);color:var(--ink);transition:border-color .15s}
input:focus,select:focus,textarea:focus{outline:3px solid color-mix(in srgb,var(--brand) 35%,transparent);outline-offset:1px;border-color:var(--brand)}
button{font:inherit;font-weight:700;font-size:1.02rem;padding:13px 18px;border:0;border-radius:12px;background:var(--brand);
color:var(--on-brand);cursor:pointer;box-shadow:0 8px 18px -10px var(--brand);transition:background .15s,transform .1s}
button:hover{background:var(--brand-deep)}
button:active{transform:translateY(1px)}
button:focus-visible,summary:focus-visible{outline:3px solid color-mix(in srgb,var(--brand) 45%,transparent);outline-offset:3px}
button.block{width:100%;margin-top:14px}
button.quiet{background:transparent;color:var(--ink);border:1.5px solid var(--line);box-shadow:none;font-weight:650;padding:9px 14px;font-size:.95rem}
button.quiet:hover{border-color:var(--ink-soft);background:transparent}
button.danger{background:transparent;color:var(--error);border:1.5px solid color-mix(in srgb,var(--error) 45%,transparent);box-shadow:none;padding:9px 14px;font-size:.95rem}
button.danger:hover{background:var(--error-bg)}
a.button{display:inline-flex;align-items:center;gap:6px;text-decoration:none;border-radius:12px}
a.button svg{width:16px;height:16px;flex:none}
.panel{scroll-margin-top:64px}
@media (max-width:540px){.addons .file-row{flex-direction:column;align-items:stretch}.addons .actions.tight{flex-wrap:wrap}}
.state{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.state p{margin:4px 0 0}
a.button.quiet{color:var(--ink);border:1.5px solid var(--line);font-weight:650;padding:9px 14px;font-size:.95rem}
a.button.quiet:hover{border-color:var(--ink-soft)}
textarea{resize:vertical;line-height:1.45}
.badge.todo{background:var(--warn-bg);color:var(--warn)}
.actions.tight{margin-top:0;flex-wrap:nowrap}
form.stack{display:grid;gap:18px;margin-top:6px}
form.stack .grid{margin-top:0;gap:18px}
form.stack button.block{margin-top:6px}
form.stack .hint{margin:6px 0 0}
label.check{display:flex;align-items:center;gap:8px;font-weight:500;margin:8px 0 0}
label.check input{width:auto;margin:0}
.msg{display:flex;gap:10px;align-items:flex-start;margin:0 0 18px;padding:12px 14px;border-radius:12px;font-weight:600}
.msg svg{width:20px;height:20px;flex:none;margin-top:2px}
.msg.error{background:var(--error-bg);color:var(--error)}
.msg.ok{background:var(--ok-bg);color:var(--ok)}
.msg.tip{background:var(--warn-bg);color:var(--warn)}
.msg b{margin-right:4px}
.note{display:flex;gap:10px;margin:22px 0 0;color:var(--ink-soft);font-size:.92rem}
.note svg{width:18px;height:18px;flex:none;margin-top:3px}
.steps{margin:0;padding-left:20px;color:var(--ink-soft)}
.steps li{margin:6px 0}
.steps a,.hint a{color:inherit;text-underline-offset:3px}
fieldset{border:0;margin:0 0 18px;padding:0}
legend{font-weight:650;margin-bottom:8px;padding:0}
.choice{display:flex;align-items:center;gap:12px;padding:12px 14px;border:1.5px solid var(--line);border-radius:12px;margin:0 0 8px;cursor:pointer;font-weight:500}
.choice:has(input:checked){border-color:var(--brand);background:color-mix(in srgb,var(--brand) 7%,transparent)}
.choice input{width:20px;height:20px;margin:0;accent-color:var(--brand);flex:none}
.choice span.addr{flex:1;min-width:0;overflow-wrap:anywhere}
.badge{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.02em;padding:3px 9px;border-radius:999px;background:var(--chip);color:var(--chip-ink);white-space:nowrap}
.badge.read{background:var(--line-soft);color:var(--ink-soft)}
.badge.lime{background:var(--lime);color:var(--lime-ink)}
b .badge,.item-head .badge{margin-left:6px;vertical-align:1px}
.badge.fail{background:var(--error-bg);color:var(--error)}
.list{border:1.5px solid var(--line-soft);border-radius:16px;overflow:hidden}
.item{padding:16px 18px;border-top:1.5px solid var(--line-soft)}
.item:first-child{border-top:0}
.item-head{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}
.item-head b{overflow-wrap:anywhere}
.muted{color:var(--ink-soft);font-size:.9rem}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.actions form{margin:0}
details{margin-top:12px}
summary{cursor:pointer;font-weight:650;color:var(--brand);list-style:none;display:inline-block}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) summary{color:var(--chip-ink)}}
:root[data-theme=dark] summary{color:var(--chip-ink)}
summary::-webkit-details-marker{display:none}
summary::after{content:" +";font-weight:700}
details[open] summary::after{content:" \\2013"}
.grid{display:grid;gap:14px;margin-top:14px}
@media (min-width:560px){.grid.two{grid-template-columns:1fr 1fr}}
.hint{font-weight:400;color:var(--ink-soft);font-size:.88rem;margin:6px 0 0}
.confirm{display:flex;gap:10px;align-items:center;font-weight:500;margin:10px 0}
.confirm input{width:18px;height:18px;margin:0;accent-color:var(--error)}
.remember{margin:14px 0 0}
.remember input{accent-color:var(--brand)}
.empty{padding:22px 18px;color:var(--ink-soft)}
background:color-mix(in srgb,var(--on-brand) 15%,transparent);color:var(--on-brand);text-decoration:none;transition:background .15s,color .15s}
.tools{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:14px}
.tools form{margin:0}
.tools button.quiet,.tool>summary{display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:7px 14px;border-radius:999px;
border:1.5px solid var(--line);background:transparent;color:var(--ink);font-weight:650;font-size:.92rem;line-height:1.2;box-shadow:none}
.tools button.quiet:hover,.tool>summary:hover{border-color:var(--ink-soft);background:color-mix(in srgb,var(--line-soft) 60%,transparent)}
.tools .sep{width:1.5px;height:22px;background:var(--line-soft);margin:0 2px}
details.tool{margin:0}
.tool>summary::after{content:"";width:6px;height:6px;border-right:1.8px solid currentColor;border-bottom:1.8px solid currentColor;
transform:translateY(-2px) rotate(45deg);opacity:.7;transition:transform .15s}
.tool[open]{flex-basis:100%;order:10;margin-top:6px}
.tool[open]>summary{background:var(--chip);color:var(--chip-ink);border-color:transparent}
.tool[open]>summary::after{transform:translateY(1px) rotate(-135deg)}
.tool.remove>summary{color:var(--error);border-color:color-mix(in srgb,var(--error) 40%,transparent)}
.tool.remove>summary:hover{background:var(--error-bg)}
.tool.remove[open]>summary{background:var(--error-bg);color:var(--error)}
.panel-body{margin-top:10px;padding:16px 18px;border-radius:14px;background:color-mix(in srgb,var(--chip) 45%,var(--card));
border:1.5px solid var(--line-soft)}
.panel-body label{margin-top:2px}
.panel-body .actions{margin-top:14px}
.panel-body .grid{margin-top:0}
.panel-body .grid+.grid{margin-top:14px}
.panel-body .warn{margin-top:0}
@media (max-width:540px){.tools .sep{display:none}}
.bar{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-top:34px;padding-top:22px;border-top:1.5px solid var(--line-soft)}
code{font-size:.9em;background:var(--line-soft);padding:1px 5px;border-radius:5px}
.lead a{color:inherit}
transition:border-color .15s,background .15s}
border:1.5px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.warn{display:flex;gap:10px;align-items:flex-start;margin:12px 0 0;padding:10px 12px;border-radius:12px;
background:var(--warn-bg);color:var(--warn);font-size:.92rem;font-weight:600}
.warn svg{width:18px;height:18px;flex:none;margin-top:2px}
.bar a{color:var(--ink-soft);font-weight:650;text-underline-offset:3px}
footer{margin-top:22px;font-size:.85rem;color:var(--ink-soft);text-align:center;padding:0 16px}
footer a{color:inherit;text-underline-offset:3px;text-decoration-color:var(--pink)}
"""

PAGE = string.Template("""<!doctype html>
<html lang="$lang"$theme_attr><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<title>$title</title>
<style>$css</style></head>
<body><main class="$width">
<section class="hero">
$theme
<div class="mark">$icon NextDNS Agent</div>
<h1>$headline</h1>
<p>$sub</p>
</section>
$tabs<section class="body">$content</section>
</main>
<footer><a href="$project_url">$project</a> $by $author · $disclaimer</footer>
</body></html>""")


def theme_button() -> str:
    t = THEME.get()
    label = esc(_(THEME_LABELS.get(t, THEME_LABELS[""])))
    return (f'<form class="theme" method="post" action="/theme"><input type="hidden" name="next" '
            f'value="{esc(HERE_PATH.get())}"><button type="submit" title="{label}" aria-label="{label}">'
            f'{THEME_ICONS.get(t, THEME_ICONS[""])}</button></form>')


def page(headline: str, sub: str, content: str, wide: bool = False, tabs: list[tuple[str, str]] | None = None) -> str:
    """headline and sub may hold simple markup, so callers escape what they put in. tabs: (anchor, label)."""
    nav = (f'<nav class="tabs" aria-label="{esc(_("Sections"))}">'
           + "".join(f'<a href="#{a}">{esc(t)}</a>' for a, t in tabs) + "</nav>" if tabs else "")
    title = re.sub(r"<[^>]+>", "", headline)
    return PAGE.substitute(title=f"{title} · NextDNS Agent", headline=headline, sub=sub, content=content, tabs=nav,
                           css=CSS + panel_css([a for a, _t in tabs or []]), icon=ICON_MARK,
                           width="wide" if wide else "", project=PROJECT, project_url=PROJECT_URL, author=AUTHOR,
                           lang=LANG.get(), by=esc(_("by")), theme=theme_button(),
                           theme_attr=f' data-theme="{THEME.get()}"' if THEME.get() else "",
                           disclaimer=esc(_("not made by NextDNS")))


def panel_css(names: list[str]) -> str:
    """Shows one tab's section at a time: the one in the address (#apps), else the first."""
    if not names:
        return ""
    rules = ["@supports selector(:has(a)){.panel{display:none}.panel:target,.panel:has(:target){display:block}",
             ".panels:not(:has(:target))>.panel:first-child{display:block}",
             f'main:not(:has(.panels :target)) .tabs a[href="#{names[0]}"]']
    rules[-1] += ",".join([""] + [f'main:has(#{n}:target,#{n} :target) .tabs a[href="#{n}"]' for n in names])
    rules[-1] += "{background:var(--chip);color:var(--chip-ink)}}"
    return "".join(rules)


def message(kind: str, text: str) -> str:
    """kind: 'error' or 'ok'. text is escaped here."""
    icon = ICON_ALERT if kind == "error" else ICON_CHECK
    role = ' role="alert"' if kind == "error" else ' role="status"'
    return f'<p class="msg {kind}"{role}>{icon}<span>{esc(text)}</span></p>'


def badge(mode: str) -> str:
    cls = {"full": "", "read": "read", "hidden": "read"}.get(mode, "")
    return f'<span class="badge {cls}">{esc(_(MODE_LABELS.get(mode, mode)))}</span>'


def csrf_field(token: str) -> str:
    return f'<input type="hidden" name="csrf" value="{esc(token)}">'


def post_button(csrf: str, fields: dict[str, str], label: str, cls: str = "quiet", extra: str = "") -> str:
    hidden = "".join(f'<input type="hidden" name="{esc(k)}" value="{esc(v)}">' for k, v in fields.items())
    return (f'<form method="post" action="/settings/save">{csrf_field(csrf)}{hidden}{extra}'
            f'<button class="{cls}" type="submit">{esc(label)}</button></form>')


# ---------------------------------------------------------------- login page (AI apps connecting)

def login(app: str | None, host: str | None, req: str, profiles: list[tuple[str, str, str]], error: str = "",
          settings_url: str = "", problem: str = "") -> str:
    """profiles: (id, name, mode) for every profile the AI may see. problem: why none can be shown."""
    if app is None:
        steps = ('<ol class="steps">' + "".join(f"<li>{esc(s)}</li>" for s in (
            _("Go back to your AI app."), _("Start connecting the NextDNS server again."),
            _("A fresh login page opens. It stays valid for 10 minutes."))) + "</ol>")
        return page(esc(_("This login link has expired")), esc(error or _("Login links last 10 minutes.")), steps)
    a = esc(app)
    if profiles:
        boxes = "".join(
            f'<label class="choice"><input type="checkbox" name="profile" value="{esc(pid)}" checked>'
            f'<span class="addr"><b>{esc(name)}</b> <span class="muted">{esc(pid)}</span></span>{badge(mode)}</label>'
            for pid, name, mode in profiles)
        choose = (f'<fieldset><legend>{_("Which profiles may {app} use?", app=a)}</legend>{boxes}</fieldset>'
                  f'<fieldset><legend>{esc(_("Changes"))}</legend><label class="choice"><input type="checkbox" '
                  f'name="change" value="yes" checked><span class="addr">{_("Allow {app} to change settings", app=a)}'
                  f'</span></label><p class="hint">'
                  + esc(_("Not ticked: it can only look. Deleting a profile or clearing logs always asks you twice "
                          "first, and every change can be undone on the settings page."))
                  + "</p></fieldset>")
    else:
        choose = message("error", problem or _("No profiles to show.")) + key_steps()
    local = (host or "").lower() in ("localhost", "127.0.0.1", "::1")
    warn = message("error", _("{app} returns to an app on a computer (localhost). Only continue if that's your own "
                              "computer and you just started this connection there.", app=app)) if local else ""
    content = (f'{message("error", error) if error else ""}{warn}<form method="post" action="/login">'
               f'<input type="hidden" name="req" value="{esc(req)}">{choose}'
               f'<label for="passphrase">{esc(_("Passphrase"))}</label>'
               '<input id="passphrase" type="password" name="passphrase" autocomplete="current-password" autofocus required>'
               f'<button class="block" type="submit"{"" if profiles else " disabled"}>{esc(_("Allow access"))}</button></form>'
               f'<p class="note">{ICON_SHIELD}<span>'
               + esc(_("Only continue if you started this connection yourself, just now. Otherwise close this page: "
                       "nothing happens without your passphrase.")) + "</span></p>"
               + (f'<p class="note">{ICON_CHECK}<span>'
                  + _("Afterwards, manage everything at <b>{url}</b>, with the same passphrase.", url=esc(settings_url))
                  + "</span></p>" if settings_url else ""))
    return page(_('Connect {app} to <span class="hl">NextDNS</span>', app=a),
                _("After you allow it, you go back to <b>{host}</b>.", host=esc(host or "?")), content)


# ---------------------------------------------------------------- settings page

def settings_login(error: str = "") -> str:
    content = (f'{message("error", error) if error else ""}<form method="post" action="/settings/login">'
               f'<label for="passphrase">{esc(_("Passphrase"))}</label>'
               '<input id="passphrase" type="password" name="passphrase" autocomplete="current-password" autofocus required>'
               '<label class="confirm remember"><input type="checkbox" name="remember" value="yes" checked>'
               f'{esc(_("Remember this device for 90 days"))}</label>'
               f'<button class="block" type="submit">{esc(_("Open settings"))}</button></form>'
               f'<p class="note">{ICON_SHIELD}<span>'
               + esc(_("Same passphrase as when you connect an AI app. Five wrong tries lock it for 15 minutes."))
               + "</span></p>")
    return page(esc(_("Settings")), esc(_("Your NextDNS key, profiles and the AI apps that may use them.")), content)


ACCOUNT_URL = "https://my.nextdns.io/account"
API_DOCS_URL = "https://nextdns.github.io/api/"


def key_steps(open_: bool = True) -> str:
    """How to find the NextDNS API key, with links to the account page and the official docs."""
    steps = "".join(f"<li>{s}</li>" for s in (
        _('Sign in to NextDNS and open your account page: <a href="{url}" target="_blank" rel="noopener">my.nextdns.io/account</a>.',
          url=ACCOUNT_URL),
        esc(_("Scroll to the bottom, to the API section.")),
        esc(_("Click to show the API key, then copy it.")),
        esc(_("Paste it here and press Test and save.")),
    ))
    return (f'<details{" open" if open_ else ""}><summary>{esc(_("How to get your API key"))}</summary>'
            f'<ol class="steps">{steps}</ol><p class="hint">'
            + _('The key lets this server read and change your NextDNS settings, like the dashboard does. More in the '
                '<a href="{url}" target="_blank" rel="noopener">official NextDNS API docs</a>.', url=API_DOCS_URL)
            + "</p></details>")


def _select(name: str, options: list[tuple[str, str]], selected: str, disabled: bool = False) -> str:
    opts = "".join(f'<option value="{esc(v)}"{" selected" if v == selected else ""}>{esc(t)}</option>' for v, t in options)
    return f'<select name="{esc(name)}"{" disabled" if disabled else ""}>{opts}</select>'


def _locked(on: bool) -> str:
    return (f'<p class="hint">{esc(_("Set in the settings file or hosting variables, so it can only be changed there."))}</p>'
            if on else "")


def backups_html(csrf: str, backups: list[dict], profiles: list[dict]) -> str:
    make = (f'<form method="post" action="/settings/save" class="mode">{csrf_field(csrf)}'
            '<input type="hidden" name="kind" value="backup"><input type="hidden" name="action" value="make">'
            + _select("profile", [(p["id"], p["name"]) for p in profiles], profiles[0]["id"] if profiles else "")
            + f'<button type="submit">{esc(_("Back up now"))}</button></form>') if profiles else ""
    upload = (f'<details><summary>{esc(_("Add a backup file"))}</summary>'
              f'<form method="post" action="/settings/save" enctype="multipart/form-data" class="stack">{csrf_field(csrf)}'
              '<input type="hidden" name="kind" value="backup"><input type="hidden" name="action" value="upload">'
              '<input type="file" name="file" accept=".json,application/json" required>'
              f'<button type="submit">{esc(_("Add"))}</button></form></details>')
    if backups:
        rows = ""
        for b in backups:
            restore = (
                f'<details><summary>{esc(_("Restore"))}</summary>'
                + post_button(csrf, {"kind": "backup", "action": "restore", "backup_id": b["id"]},
                              _("Overwrite {name} with this backup", name=b.get("profile_name") or "?"), "quiet",
                              f'<label class="confirm"><input type="checkbox" name="sure" value="yes" required>'
                              f'{esc(_("Yes, overwrite it (can be undone in Changes)"))}</label>')
                + f'<form method="post" action="/settings/save" class="stack" style="margin-top:12px">{csrf_field(csrf)}'
                  '<input type="hidden" name="kind" value="backup"><input type="hidden" name="action" value="new">'
                  f'<input type="hidden" name="backup_id" value="{esc(b["id"])}">'
                  f'<div><label>{esc(_("Or make a new profile from it"))}</label>'
                  f'<input name="name" placeholder="{esc(_("New profile name"))}" required></div>'
                  f'<button class="quiet" type="submit">{esc(_("Make new profile"))}</button></form></details>')
            rows += (f'<div class="item"><div class="item-head"><b>{esc(b.get("profile_name") or "?")}</b>'
                     f'<span class="muted">{esc(b.get("time") or "")} · {esc(b["id"])}</span></div>'
                     + (f'<p style="margin:6px 0 0">{esc(b["note"])}</p>' if b.get("note") else "")
                     + f'<div class="actions"><a class="button quiet" href="/settings/backup/{esc(b["id"])}">'
                       f'{esc(_("Download"))}</a>'
                     + post_button(csrf, {"kind": "backup", "action": "delete", "backup_id": b["id"]}, _("Delete"), "danger")
                     + f"</div>{restore}</div>")
        listing = f'<div class="list" style="margin-top:18px">{rows}</div>'
    else:
        listing = f'<p class="empty">{esc(_("No backups yet."))}</p>'
    return (f'<p class="lead">{esc(_("A full copy of a profile: settings, lists, parental control and rewrites."))}</p>'
            + make + upload + listing)


def settings(csrf: str, flash: tuple[str, str] | None, key: dict, profiles: list[dict], problem: str,
             options: dict, locked: set[str], apps: list[dict], changes: list[dict], about: dict,
             backups: list[dict] | None = None) -> str:
    """key: {set, source, last4}. profiles: {id, name, mode, created}. options: current settings. apps: {client_id,
    name, profiles, change, since}. changes: change log rows, newest first. about: {version, public_url}."""
    top = message(*flash) if flash else ""
    # the key
    if key["source"] == "env":
        key_html = (f'<p class="lead">{esc(_("The API key ending in {last4} comes from the settings file or hosting variables.", last4=key["last4"]))}</p>')
    else:
        key_html = (
            (f'<p class="lead">{esc(_("Saved, ending in {last4}. It is stored encrypted and only sent to NextDNS.", last4=key["last4"]))}</p>'
             if key["set"] else f'<p class="lead">{esc(_("Paste your NextDNS API key."))}</p>')
            + key_steps(open_=not key["set"])
            + f'<form method="post" action="/settings/save" class="stack">{csrf_field(csrf)}'
              '<input type="hidden" name="kind" value="key">'
              f'<div><label for="apikey">{esc(_("API key"))}</label>'
              '<input id="apikey" name="api_key" type="password" autocomplete="off" required></div>'
              f'<button class="block" type="submit">{esc(_("Test and save"))}</button></form>'
            + (post_button(csrf, {"kind": "key", "action": "remove"}, _("Remove the key"), "danger") if key["set"] else ""))
    # profiles
    modes_locked = "NEXTDNS_PROFILES" in locked
    if profiles:
        rows = "".join(
            f'<div class="item"><div class="item-head"><b>{esc(p["name"])}</b><span class="muted">{esc(p["id"])}</span>'
            + (f'<span class="badge lime">{esc(_("made by AI"))}</span>' if p.get("created") else "") + "</div>"
            f'<div class="mode" style="margin-top:10px">'
            + _select(f"mode_{p['id']}", [(m, _(t)) for m, t in MODE_LABELS.items()], p["mode"], modes_locked)
            + "</div></div>" for p in profiles)
        default = options.get("NEXTDNS_DEFAULT_PROFILE", "")
        prof_html = (f'<form method="post" action="/settings/save">{csrf_field(csrf)}<input type="hidden" name="kind" value="profiles">'
                     f'<div class="list">{rows}</div>{_locked(modes_locked)}'
                     f'<label style="margin-top:18px" for="defp">{esc(_("Default profile (used when the AI names none)"))}</label>'
                     + _select("default_profile", [("", _("None"))] + [(p["id"], p["name"]) for p in profiles], default,
                               "NEXTDNS_DEFAULT_PROFILE" in locked).replace("<select ", '<select id="defp" ', 1)
                     + f'<button class="block" type="submit"{" disabled" if modes_locked else ""}>{esc(_("Save"))}</button></form>')
    else:
        prof_html = message("error", problem or _("No profiles yet."))
    # safety
    def check(name: str, label: str, on: bool) -> str:
        dis = " disabled" if name in locked else ""
        return (f'<label class="choice"><input type="checkbox" name="{name}" value="yes"{" checked" if on else ""}{dis}>'
                f'<span class="addr">{esc(label)}</span></label>')
    safety_html = (f'<form method="post" action="/settings/save">{csrf_field(csrf)}<input type="hidden" name="kind" value="safety">'
                   + check("NEXTDNS_READ_ONLY", _("Read-only mode: nothing can be changed, by any app"),
                           options.get("read_only", False))
                   + check("NEXTDNS_ALLOW_DELETE", _("Allow deleting profiles and clearing logs (always asked twice first)"),
                           options.get("allow_delete", True))
                   + f'<label for="dm" style="margin-top:12px">{esc(_("New profiles the AI finds"))}</label>'
                   + _select("NEXTDNS_DEFAULT_MODE", [(m, _(t)) for m, t in MODE_LABELS.items()],
                             options.get("default_mode", "full"), "NEXTDNS_DEFAULT_MODE" in locked).replace("<select ", '<select id="dm" ', 1)
                   + f'<button class="block" type="submit">{esc(_("Save"))}</button></form>')
    # apps
    names = {p["id"]: p["name"] for p in profiles}
    if apps:
        app_rows = ""
        for a in apps:
            boxes = "".join(
                f'<label class="choice"><input type="checkbox" name="profile" value="{esc(p["id"])}"'
                f'{" checked" if p["id"] in a["profiles"] else ""}><span class="addr">{esc(p["name"])}</span></label>'
                for p in profiles)
            app_rows += (
                f'<div class="item"><div class="item-head"><b>{esc(a["name"])}</b>'
                + badge("full" if a["change"] else "read") + "</div>"
                f'<p class="muted">{esc(_("Profiles"))}: {esc(", ".join(names.get(i, i) for i in a["profiles"]) or _("none"))}</p>'
                f'<details><summary>{esc(_("Change"))}</summary>'
                f'<form method="post" action="/settings/save">{csrf_field(csrf)}<input type="hidden" name="kind" value="app">'
                f'<input type="hidden" name="client_id" value="{esc(a["client_id"])}">{boxes}'
                f'<label class="choice"><input type="checkbox" name="change" value="yes"{" checked" if a["change"] else ""}>'
                f'<span class="addr">{esc(_("May change settings"))}</span></label>'
                f'<button type="submit">{esc(_("Save"))}</button></form></details>'
                f'<div class="actions">'
                + post_button(csrf, {"kind": "app", "action": "disconnect", "client_id": a["client_id"]}, _("Disconnect"), "danger")
                + "</div></div>")
        apps_html = f'<div class="list">{app_rows}</div>'
    else:
        apps_html = (f'<p class="empty">{esc(_("No AI app connected yet. Add this server to your AI app:"))} '
                     f'<code>{esc(about["public_url"])}/mcp</code></p>')
    # changes
    if changes:
        rows = ""
        for e in changes:
            state = ""
            if e.get("undone_by"):
                state = f'<span class="badge read">{esc(_("undone"))}</span>'
            elif e.get("kind") == "clear_logs":
                state = f'<span class="badge read">{esc(_("no undo"))}</span>'
            else:
                extra = ""
                if e.get("kind") == "create":
                    extra = (f'<label class="confirm"><input type="checkbox" name="sure" value="yes" required>'
                             f'{esc(_("Yes, delete this profile"))}</label>')
                extra += (f'<label class="check"><input type="checkbox" name="force" value="yes">'
                          f'{esc(_("Even if it changed again since"))}</label>')
                state = (f'<details><summary>{esc(_("Undo"))}</summary>'
                         + post_button(csrf, {"kind": "undo", "change_id": e["id"]}, _("Undo this change"), "quiet", extra)
                         + "</details>")
            rows += (f'<div class="item"><div class="item-head"><b>{esc(e.get("tool", ""))}</b>'
                     f'<span class="muted">{esc(e.get("profile_name") or "")} · {esc(e.get("time") or "")} · '
                     f'{esc(e.get("app") or "")}</span></div><p style="margin:6px 0 0">{esc(e.get("summary") or "")}</p>{state}</div>')
        changes_html = f'<div class="list">{rows}</div>'
    else:
        changes_html = f'<p class="empty">{esc(_("Nothing changed yet."))}</p>'
    upd = about.get("update")
    if upd and upd.get("newer"):
        news = (f'<p class="msg tip">{ICON_ALERT}<span>'
                + _('Version {v} is out. <a href="{url}" target="_blank" rel="noopener">What\'s new and how to update</a>.',
                    v=esc(upd["latest"]), url=esc(upd["url"])) + "</span></p>")
    elif upd:
        news = f'<p class="hint">{esc(_("Up to date. Checked once a day with GitHub."))}</p>'
    else:
        news = ""
    check_box = (f'<form method="post" action="/settings/save">{csrf_field(csrf)}<input type="hidden" name="kind" value="update">'
                 f'<label class="choice"><input type="checkbox" name="UPDATE_CHECK" value="yes"'
                 f'{" checked" if upd is not None else ""}{" disabled" if "UPDATE_CHECK" in locked else ""}>'
                 f'<span class="addr">{esc(_("Check for new versions once a day (asks GitHub, sends nothing about you)"))}</span></label>'
                 f'{_locked("UPDATE_CHECK" in locked)}<button class="quiet" type="submit">{esc(_("Save"))}</button></form>')
    about_html = news + check_box + (f'<p class="lead" style="margin-top:18px">{esc(_("Version {v}.", v=about["version"]))} '
                  f'{esc(_("Connect an AI app with this address:"))} <code>{esc(about["public_url"])}/mcp</code></p>'
                  f'<form method="post" action="/settings/logout">{csrf_field(csrf)}'
                  f'<button class="quiet" type="submit">{esc(_("Sign out"))}</button></form>')
    sections = [("key", _("API key"), key_html), ("profiles", _("Profiles"), prof_html),
                ("apps", _("Apps"), apps_html), ("changes", _("Changes"), changes_html),
                ("backups", _("Backups"), backups_html(csrf, backups or [], profiles)),
                ("safety", _("Safety"), safety_html), ("about", _("About"), about_html)]
    body = top + '<div class="panels">' + "".join(
        f'<section class="panel" id="{a}"><h2>{esc(t)}</h2>{h}</section>' for a, t, h in sections) + "</div>"
    return page(esc(_("Settings")), esc(_("Your NextDNS key, profiles and the AI apps that may use them.")), body,
                wide=True, tabs=[(a, t) for a, t, _h in sections])
