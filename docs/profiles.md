# Profiles and apps

You decide what the AI may see and change, in two layers: a **mode for each profile**, and, on the web version, **a choice for each AI app**.

## Profile modes

| Mode | The AI may |
|---|---|
| **full** (the default) | read and change the profile, everything the NextDNS API allows |
| **read** | read it (settings, analytics, logs) but change nothing |
| **hidden** | nothing: the profile never shows up, not even its name |

Set them in one of these places:

- **The settings page** (web version), **Profiles** tab: a list of your profiles with a mode each.
- **The settings file** or a hosting variable:

  ```
  NEXTDNS_PROFILES=abc123=full,Kids=read,Work laptop=hidden
  ```

  Use the profile's ID or its name (any capitals). The settings file wins over the page.

Profiles you don't list get `NEXTDNS_DEFAULT_MODE`, which is `full` unless you change it. Set it to `hidden` to only show the profiles you name.

## The default profile

With more than one profile, the AI names the one it means. To let it leave that out, choose a default: on the settings page (**Profiles** tab), or `NEXTDNS_DEFAULT_PROFILE=abc123` in the settings file. With only one profile visible, that one is used.

## Each AI app (web version)

When an AI app connects over the internet, the login page asks:

1. **Which profiles may it use?** Every profile that isn't hidden is listed, all ticked. Untick the ones it shouldn't see.
2. **May it change settings?** Ticked by default. Unticked, the app can only look, even on profiles in full mode.

<p align="center"><img src="images/login-page.png" alt="The login page" width="260"></p>

Change your mind later on the settings page, **Apps** tab: **Change** to tick other profiles, or **Disconnect** to log the app out (it has to log in again).

Apps on the same computer (stdio, the Claude Desktop extension) don't log in, so only the profile modes apply to them.

## Profiles the AI makes

A profile the AI creates (`create_profile`, or a backup restored as a new profile) may always be changed by it, unless you list it in `NEXTDNS_PROFILES`. On the web version it's added to that app's profiles too. The settings page marks these profiles "made by AI".

## Read-only for everything

`NEXTDNS_READ_ONLY=on`, or the switch on the settings page (**Safety** tab), stops every change, for every app and every profile.

## Deletes

Deleting a profile and clearing logs are on by default, and always ask you twice ([safety.md](safety.md#asked-twice)). To turn them off completely: `NEXTDNS_ALLOW_DELETE=off`, or untick the box on the settings page (**Safety** tab).
