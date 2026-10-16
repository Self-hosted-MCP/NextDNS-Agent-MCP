# Undo and backups

## The change log

Every change made through this server is saved, with how that part of the profile looked before and after: which tool, which profile, which app, when, and a short summary.

- Ask the AI: *"What did you change today?"* (the `changes` tool)
- Or open the settings page, **Changes** tab.

<p align="center"><img src="images/settings-changes.png" alt="The Changes tab" width="420"></p>

The log keeps the last 300 changes. It lives in the data folder (`changes.json`).

## Undo

Ask *"undo that"*, or press **Undo** on the settings page. The profile goes back to exactly how it was before that change: lists, switches, settings, the name.

- **If the profile changed again since** (in the NextDNS dashboard, by another app or a later change), undo stops and says which parts differ. Then you choose: undo anyway (`force`, or the "Even if it changed again since" box), which also drops those later changes, or leave it.
- **An undo is a change too,** so it can be undone (that redoes the first change).
- **Undoing the creation of a profile deletes it,** so it asks twice first (on the settings page: a box to tick).
- **A deleted profile** can be made again with the same settings and lists. NextDNS gives it a new ID, so devices need its new address. Its old logs can't come back.
- **Cleared logs** can't come back.

## Backups

A backup is a full copy of one profile: name, security, privacy, parental control, denylist, allowlist, rewrites and settings. Logs and analytics are not part of it (NextDNS doesn't allow writing them back).

| To | Ask the AI | On the settings page (Backups tab) |
|---|---|---|
| Make one | *"Back up the Kids profile"* (`backup`) | **Back up now** |
| See them | *"Which backups do I have?"* (`backups`) | The list |
| Put one back | *"Restore yesterday's backup of Kids"* (`restore_backup`, asks twice) | **Restore**, tick the box |
| Make a new profile from one | *"Make a new profile from that backup"* | **Make new profile** |
| Keep a copy elsewhere | | **Download** (a JSON file) |
| Bring a copy back | | **Add a backup file** |

Restoring over a profile is a change like any other: it's in the change log and can be undone.

Backups live in the data folder (`backups/`). On a hosting company, that's the `/data` disk: without one, backups are lost at restart, so download the important ones.

## Undo vs backups

Undo is automatic and step by step. A backup is a snapshot you choose to make, for example before a big clean-up, or to copy one profile's setup to another.
