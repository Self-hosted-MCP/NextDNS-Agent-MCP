# Safety

The AI may do everything the NextDNS API allows, on the profiles you let it use. These rules keep that safe.

## Who may use which profile

- **Profile modes:** each profile is **full** (read and change, the default), **read** (read only) or **hidden** (the AI never sees it). Set them on the settings page or with `NEXTDNS_PROFILES` (for example `abc123=full,def456=hidden`). Profiles you don't list get `NEXTDNS_DEFAULT_MODE`.
- **Per app (web version):** when an AI app connects, the login page asks which profiles it may use and whether it may change them. You can change that, or disconnect the app, on the settings page. A profile the app creates itself is added to its list.
- **Read-only mode:** `NEXTDNS_READ_ONLY=on` (or the switch on the settings page) blocks every change, for every app.

## Asked twice

Deleting a profile, clearing a profile's logs, overwriting a profile from a backup, and undoing the creation of a profile (which deletes it) need a **double confirmation**:

1. The first call does nothing. It explains what would happen and gives a one-time code.
2. The AI has to tell you and ask. Only after you say yes may it call again with that code.

Each code works once, for that one action, for 5 minutes. A wrong or old code does nothing. On the settings page, ticking the confirm box is the second step.

`NEXTDNS_ALLOW_DELETE=off` turns deleting profiles and clearing logs off completely.

## Undo

Every change is saved in the change log (the `changes` tool and the Changes tab), with how that part of the profile looked before and after. `undo` (or the Undo button) puts it back.

- If the profile was changed again since (in the NextDNS dashboard, or by a later change), undo stops and says what differs. `force` does it anyway, which also drops those later changes.
- A deleted profile can be made again with the same settings and lists, but NextDNS gives it a new ID, so devices need the new address. Its logs can't come back.
- Cleared logs can't come back.
- The log keeps the last 300 changes.

## Limits

- At most 30 changes a minute (`NEXTDNS_CHANGE_LIMIT`), a brake for a runaway AI.
- At most 100 domains per list change.

## Your data

- The API key goes only to NextDNS. When you paste it on the settings page it is stored encrypted (Fernet), with `NEXTDNS_SECRET_KEY` if set, otherwise a random key kept next to the data.
- Login tokens and settings-page sessions are stored only as fingerprints (SHA-256), so a copy of the files can't be used to log in. AI app keys last 1 hour and renew for up to 90 days.
- The login and settings pages share one passphrase (6 characters or more). Five wrong tries lock them for 15 minutes.
- The pages load nothing from other sites and can't be shown inside another site. Every settings form checks it came from the settings page itself.
- `check_domain` makes a real DNS query through the profile, so it shows in that profile's log.
