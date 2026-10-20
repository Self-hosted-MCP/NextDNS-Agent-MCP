# SPDX-License-Identifier: Apache-2.0
"""The update check (off by default) and the update command."""
import pytest

from nextdns_agent_mcp import server


def test_off_by_default_and_asks_nothing(fake):
    assert server.update_status() is None
    assert "Update available" not in server.profiles()
    assert fake.github_calls == 0


def test_tells_about_a_newer_release(fake, monkeypatch):
    monkeypatch.setenv("UPDATE_CHECK", "on")
    monkeypatch.setattr(server, "current_version", lambda: "0.6.3")
    fake.latest_tag = "v0.7.0"
    status = server.update_status()
    assert status["newer"] and status["latest"] == "v0.7.0"
    assert "Update available: v0.7.0 (this server runs 0.6.3)" in server.profiles()


def test_asks_once_a_day(fake, monkeypatch):
    monkeypatch.setenv("UPDATE_CHECK", "on")
    monkeypatch.setattr(server, "current_version", lambda: "0.6.3")
    fake.latest_tag = "v0.6.3"
    server.update_status()
    server.update_status()
    assert fake.github_calls == 1
    assert server.update_status()["newer"] is False
    server.update_status(force=True)
    assert fake.github_calls == 2


def test_a_failed_check_is_no_news(fake, monkeypatch):
    monkeypatch.setenv("UPDATE_CHECK", "on")
    fake.latest_tag = None   # GitHub is down
    assert server.update_status()["newer"] is False
    assert "Home" in server.profiles()


@pytest.mark.parametrize("v,t", [("v0.10.2", (0, 10, 2)), ("0.6.3", (0, 6, 3)), ("v1.0", (-1,)), ("", (-1,))])
def test_version_numbers(v, t):
    assert server.version_tuple(v) == t
    assert server.version_tuple("v0.10.0") > server.version_tuple("v0.9.9")


def test_update_command(fake, monkeypatch, capsys):
    import subprocess
    import shutil
    monkeypatch.setattr(server, "current_version", lambda: "0.6.3")
    fake.latest_tag = "v0.6.3"
    server.run_update()
    assert "Up to date (0.6.3)" in capsys.readouterr().out
    fake.latest_tag = "v0.7.0"
    ran = []
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/uv")
    monkeypatch.setattr(subprocess, "run", lambda cmd: ran.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    server.run_update()
    assert ran == [["/usr/bin/uv", "tool", "install", "--force",
                    "git+https://github.com/Self-hosted-MCP/NextDNS-Agent-MCP@v0.7.0"]]
    assert "Updated to v0.7.0" in capsys.readouterr().out
