# SPDX-License-Identifier: MIT
"""The Claude Desktop extension and hosting files stay in step with the code."""
import asyncio
import json
import zipfile
from pathlib import Path

from nextdns_agent_mcp import server

ROOT = Path(__file__).resolve().parent.parent


def test_manifest_lists_every_tool():
    manifest = json.loads((ROOT / "extension" / "manifest.json").read_text())
    listed = {t["name"] for t in manifest["tools"]}
    real = {t.name for t in asyncio.run(server.mcp.list_tools())}
    assert listed == real


def test_manifest_settings_reach_the_server():
    env = json.loads((ROOT / "extension" / "manifest.json").read_text())["server"]["mcp_config"]["env"]
    assert set(env) <= set(server.SETTINGS)
    assert server.is_on("true") and not server.is_on("false")   # what Claude Desktop passes for a checkbox


def test_build_mcpb(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_mcpb", ROOT / "scripts" / "build_mcpb.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.build(tmp_path)
    names = zipfile.ZipFile(out).namelist()
    assert "manifest.json" in names and "icon.png" in names and "uv.lock" in names
    assert "src/nextdns_agent_mcp/server.py" in names and not any("__pycache__" in n for n in names)
    assert json.loads(zipfile.ZipFile(out).read("manifest.json"))["version"] == mod.version()


def test_hosting_files_agree_on_the_port():
    for name in ("Dockerfile", "render.yaml", "Caddyfile"):
        assert "8766" in (ROOT / name).read_text(), name


def test_docs_list_every_tool():
    real = {t.name for t in asyncio.run(server.mcp.list_tools())}
    text = (ROOT / "docs" / "tools.md").read_text()
    assert all(f"### `{name}`" in text for name in real)


def test_docs_list_every_setting():
    text = (ROOT / "docs" / "settings.md").read_text()
    shown = {s for s in server.SETTINGS if s not in ("NEXTDNS_API_URL", "RENDER_EXTERNAL_URL", "RAILWAY_PUBLIC_DOMAIN")}
    assert all(f"`{s}`" in text or s in ("HOST", "PORT") for s in shown)


def _anchors(text: str) -> set[str]:
    """GitHub's heading anchors: lowercase, punctuation dropped, spaces to dashes."""
    import re
    out = set()
    for line in text.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip().lower()
            out.add(re.sub(r"[^\w\- ]", "", title).replace(" ", "-"))
    return out


def test_docs_links_work():
    import re
    files = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]
    broken = []
    for f in files:
        text = f.read_text()
        for target in re.findall(r"\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"", text):
            link = target[0] or target[1]
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, anchor = link.partition("#")
            dest = (f.parent / path).resolve() if path else f
            if not dest.exists():
                broken.append(f"{f.name}: {link}")
            elif anchor and dest.suffix == ".md" and anchor not in _anchors(dest.read_text()):
                broken.append(f"{f.name}: {link} (no such heading)")
    assert not broken, broken
