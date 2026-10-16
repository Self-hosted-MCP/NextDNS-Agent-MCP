# Tools

What the AI can do, in the words it reads (each tool's own description). Every change is saved in the change log and can be undone, except clearing logs. See [safety](safety.md).

## Look

### `profiles`

Show the NextDNS profiles this app may use and what it may do with each. Run this first.

Takes: nothing.

### `profile`

One profile's settings in a clear summary: security, privacy, parental control, denylist, allowlist,
rewrites, settings and setup (the addresses devices use).
profile: ID or name (default: the only or default profile).
section: show just one part in full: security, privacy, parental_control, denylist, allowlist, rewrites,
settings or setup. Without it, long lists are cut short.

Takes: `profile`, `section`.

### `catalog`

What NextDNS offers to choose from, with the IDs the change tools take.
kind: blocklists (privacy blocklists), natives (native tracking protection: apple, samsung, ...), services
(apps parental control can block: tiktok, instagram, ...), categories (porn, gambling, ...) or tlds.
search: words to look for in IDs, names and descriptions. limit: how many to show (default 50).

Takes: `kind`, `search`, `limit`.

### `analytics`

Query counts from a profile's analytics.
report: status (allowed / blocked / default), domains, reasons (why blocked), ips, devices, protocols,
queryTypes, ipVersions, dnssec, encryption or destinations.
from_date / to_date: start (included) and end (not included); ISO, Unix time or relative (-6h, -7d, -1M).
device: a device ID from the devices report, or __UNIDENTIFIED__. status (domains only): blocked, allowed or
default. root=true (domains only): group by root domain. destination (destinations only): countries or gafam.
limit: rows (1-500). series=true: counts over time, split by interval (e.g. 1h, 1d, 3600) and timezone
(e.g. Europe/Lisbon). cursor: from the last answer, for the next page.

Takes: `report`, `profile`, `from_date`, `to_date`, `device`, `status`, `root`, `destination`, `limit`, `series`, `interval`, `timezone`, `cursor`.

### `chart`

Draw a profile's analytics as a picture (PNG). Same reports as analytics: status, domains, reasons, ips,
devices, protocols, queryTypes, ipVersions, dnssec, encryption, destinations.
over_time=true: lines over time (up to 6), split by interval (e.g. 1h, 1d) and timezone (e.g. Europe/Lisbon).
over_time=false: bars of the top rows (limit, up to 20). status (domains only): blocked, allowed or default.

Takes: `report`, `profile`, `over_time`, `from_date`, `to_date`, `device`, `interval`, `timezone`, `status`, `limit`.

### `logs`

Search a profile's query log, newest first.
search: part of a domain (facebook matches facebook.com, fbcdn.net, ...). status: blocked, allowed, default or
error. device: device ID or __UNIDENTIFIED__. from_date / to_date: ISO, Unix time or relative (-1h, -1d).
limit: 10-1000. raw=true: every query, not just the useful ones (A, AAAA, HTTPS, without repeats).
cursor: from the last answer, for the next page. download_link=true: a link to download the whole log instead.

Takes: `profile`, `search`, `status`, `device`, `from_date`, `to_date`, `limit`, `raw`, `oldest_first`, `cursor`, `download_link`.

### `watch_logs`

Watch a profile's queries live for a short time, for example while the user opens an app ("open TikTok
now"), then show what came in and what was blocked.
seconds: how long to watch, 5 to 120 (default 30). search, status (blocked, allowed, default, error), device,
raw: the same filters as logs. Logs must be on for the profile.

Takes: `profile`, `seconds`, `search`, `status`, `device`, `raw`.

### `check_domain`

Is a domain blocked by this profile, and why? Makes a real DNS query through the profile (like a device
would; it shows in the profile's log), then looks at the denylist, allowlist and the log for the reason.
domain: like tiktok.com or a link (cut down to the domain).

Takes: `domain`, `profile`.

### `compare_profiles`

What differs between two profiles: switches, lists, parental control, rewrites and settings.

Takes: `first`, `second`.

### `changes`

What was changed through this app, newest first, with the IDs undo takes.
profile: only this profile (ID or name). limit: how many (default 20).

Takes: `limit`, `profile`.

### `backups`

The saved backups, newest first. profile: only those of this profile (ID or name).

Takes: `profile`.

## Change

### `list_entries`

Change a profile's denylist (always blocked) or allowlist (never blocked). A domain also covers its
subdomains.
list_name: denylist or allowlist. action: add, remove, on (turn an entry back on) or off (keep it, but not
in use). domains: up to 100 at once, like example.com (links are cut down to the domain).

Takes: `list_name`, `action`, `domains`, `profile`.

### `privacy`

Change a profile's privacy settings. IDs come from catalog (kind blocklists or natives).
add_blocklists / remove_blocklists: blocklist IDs, like oisd or hagezi-pro.
add_natives / remove_natives: native tracking protection, like apple, samsung, windows, xiaomi.
disguised_trackers: block third-party trackers disguised as first-party (true / false).
allow_affiliate: let affiliate and tracking links work (true / false). Leave out what shouldn't change.

Takes: `profile`, `add_blocklists`, `remove_blocklists`, `add_natives`, `remove_natives`, `disguised_trackers`, `allow_affiliate`.

### `security`

Change a profile's security protections. profile(section='security') shows them with their keys.
turn_on / turn_off: switch keys like threatIntelligenceFeeds, aiThreatDetection, googleSafeBrowsing,
cryptojacking, dnsRebinding, idnHomographs, typosquatting, dga, nrd (newly registered domains), ddns, parking,
csam, highRiskTlds and more.
block_tlds / unblock_tlds: top-level domains to block entirely, like zip or xyz (IDs from catalog kind=tlds).

Takes: `profile`, `turn_on`, `turn_off`, `block_tlds`, `unblock_tlds`.

### `parental_control`

Change a profile's parental control. IDs come from catalog (kind services or categories).
block_services / unblock_services: apps and sites like tiktok, instagram, fortnite.
block_categories / unblock_categories: porn, gambling, dating, piracy, gaming, social-networks, video-streaming.
pause / resume: keep a blocked service or category in the list but stop (or restart) blocking it.
allow_in_recreation / block_in_recreation: which blocked services or categories are allowed during
recreation time.
recreation_times: the hours when those are allowed, per day, like {"monday": "18:00-20:00", "saturday":
"10:00-22:00"}; "" removes a day. recreation_timezone: like Europe/Lisbon (needed once times are set).
safe_search, youtube_restricted_mode, block_bypass: true or false.

Takes: `profile`, `block_services`, `unblock_services`, `block_categories`, `unblock_categories`, `pause`, `resume`, `allow_in_recreation`, `block_in_recreation`, `recreation_times`, `recreation_timezone`, `safe_search`, `youtube_restricted_mode`, `block_bypass`.

### `rewrites`

Add or remove a DNS rewrite: answer a domain with your own IP address or another domain (for example a
home server name).
action: add or remove. name: the domain, like nas.home or printer.example.com.
content (for add): an IPv4 or IPv6 address, or a domain to point to.

Takes: `action`, `name`, `content`, `profile`.

### `profile_settings`

Change a profile's settings. Leave out what shouldn't change.
rename: a new name for the profile. logs: keep a query log (true / false).
log_retention: how long logs are kept: 1 hour, 6 hours, 1 day, 1 week, 1 month, 3 months, 6 months, 1 year or
2 years. log_location: where logs are stored: us, eu, gb or ch.
drop_client_ips / drop_domains: leave client IPs or domains out of the logs.
block_page: show a block page instead of failing. ecs: EDNS Client Subnet (faster CDNs). cache_boost: keep
answers cached longer. cname_flattening: answer with the final address. web3: resolve Web3 domains (.eth, ...).

Takes: `profile`, `rename`, `logs`, `log_retention`, `log_location`, `drop_client_ips`, `drop_domains`, `block_page`, `ecs`, `cache_boost`, `cname_flattening`, `web3`.

### `create_profile`

Make a new NextDNS profile (for another device, a child, a guest network, ...). This app may change the
profiles it makes.
copy_from: an existing profile (ID or name) to copy every setting and list from.
start (without copy_from): recommended (the usual protections and NextDNS's recommended blocklist) or empty
(everything off).

Takes: `name`, `copy_from`, `start`.

### `backup`

Save a full copy of a profile (settings, lists, parental control, rewrites) on this server, to restore later.
note: a few words to recognise it.

Takes: `profile`, `note`.

### `undo`

Put a profile back the way it was before one change (IDs from changes). Only when the user asked.
If the profile was changed again since (in the NextDNS dashboard or by a later change), undo stops and says
what differs; force=true puts the old state back anyway, which also drops those later changes.
Undoing the creation of a profile deletes it, so it needs a double confirmation like delete_profile:
the first call gives a code, and only after the user says yes, call again with confirm_code.

Takes: `change_id`, `force`, `confirm_code`.

## Asks twice first

### `delete_profile`

DELETES a whole profile and its logs. Devices using it stop being filtered. Only when the user asked.
Needs a double confirmation: the first call deletes nothing and gives a code; ask the user, and only after
they say yes, call again with confirm_code. undo can make a new profile with the same settings and lists, but
with a new ID (devices must be set up again), and the logs are gone for good.

Takes: `profile`, `confirm_code`.

### `clear_logs`

DELETES every entry in a profile's query log, for good (no undo). Only when the user asked.
Needs a double confirmation: the first call deletes nothing and gives a code; ask the user, and only after
they say yes, call again with confirm_code.

Takes: `profile`, `confirm_code`.

### `restore_backup`

Put a backup back.
new_profile_name: make a new profile from the backup (nothing is overwritten).
Otherwise it overwrites a profile (default: the one it was taken from; or profile=...) with the backup: that
needs a double confirmation, so the first call gives a code; ask the user, and only after they say yes, call
again with confirm_code. It can be undone like any change.

Takes: `backup_id`, `profile`, `new_profile_name`, `confirm_code`.
