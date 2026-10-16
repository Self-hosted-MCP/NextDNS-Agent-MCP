# SPDX-License-Identifier: Apache-2.0
"""Small files on disk: written whole and owner-only, locked while changed, secrets encrypted."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import tempfile
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:   # Windows
    fcntl = None


def private_write(path: Path, text: str) -> None:
    """Writes the whole file at once, owner-only."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


@contextmanager
def editing(path: Path):
    """Hold this while reading, changing and writing back a shared file, so two copies of the server (say Claude
    Desktop and the web version) never undo each other's change."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(path.parent / (path.name + ".lock"), "w") as lock:
        if fcntl:
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl:
                fcntl.flock(lock, fcntl.LOCK_UN)


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def secret_box(secret: str, key_file: Path):
    """Encrypts what's saved from the settings page (the API key). The key is NEXTDNS_SECRET_KEY if set (hosting:
    then a copy of the data folder alone is useless), otherwise a random key kept next to the data."""
    from cryptography.fernet import Fernet
    if secret:
        return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()))
    if not key_file.exists():
        private_write(key_file, Fernet.generate_key().decode())
    return Fernet(key_file.read_text().strip().encode())


def hash_passphrase(passphrase: str, salt: bytes | None = None, rounds: int = 600_000) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, rounds)
    return f"pbkdf2:{rounds}:{salt.hex()}:{digest.hex()}"


def check_passphrase(passphrase: str, stored: str) -> bool:
    import hmac
    try:
        _, rounds, salt, _digest = stored.replace("$", ":").split(":")
        return hmac.compare_digest(hash_passphrase(passphrase, bytes.fromhex(salt), int(rounds)), stored.replace("$", ":"))
    except Exception:
        return False


def token_key(token: str) -> str:
    """Files keep only this fingerprint of each login token, so a copy of a file can't be used to log in."""
    return hashlib.sha256(token.encode()).hexdigest()
