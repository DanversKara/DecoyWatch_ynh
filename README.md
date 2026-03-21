# Decoy Watch — YunoHost App

**Decoy Watch** is an open-source honeypot monitor for YunoHost. It places fake credential files in your backup directories and alerts you the moment anything touches them — giving you early warning of unauthorized access before real damage is done.

[![YunoHost](https://img.shields.io/badge/YunoHost-≥12.1-blue?logo=yunohost)](https://yunohost.org)
[![Packaging Format](https://img.shields.io/badge/Packaging-v2-orange)](https://doc.yunohost.org/en/dev/packaging/)
[![License](https://img.shields.io/badge/license-BSD--3Clause%20AND%20GPL--2.0%20AND%20MIT-green)](doc/LICENSES.md)

> ⚠️ **Decoy files are traps.** Never store real credentials in `.fake` files. Accessing them intentionally will trigger security alerts.

---

## Features

| Feature | Description |
|---|---|
| 🪤 Decoy file generator | Creates fake AWS keys, database dumps, and SSH private keys |
| 🔍 Real-time file monitoring | `inotify` watches for any access or modification |
| 🛡️ Integrity monitoring | `AIDE` detects file changes at the filesystem level |
| 🌐 Network honeypot | Optional OpenCanary SSH (port 2222) and HTTP (port 8088) decoys |
| 📧 Email alerting | Via YunoHost local mail or external SMTP |
| 🔐 YunoHost native | Firewall rules, backup/restore, permissions, and settings all managed by YunoHost |

---

## Requirements

| | |
|---|---|
| YunoHost | ≥ 12.1.17 |
| Architecture | amd64 |
| Disk | ~500 MB |
| RAM (runtime) | 128 MB |
| RAM (install) | 256 MB |
| Email | Working YunoHost local mail **or** external SMTP credentials |

---

## Installation

### Via YunoHost web admin

Go to **Apps → Install → Custom app** and paste:

```
https://github.com/DanversKara/DecoyWatch_ynh
```

### Via CLI

```bash
yunohost app install https://github.com/DanversKara/DecoyWatch_ynh
```

### Install parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `domain` | ✅ | — | Domain for the webhook endpoint |
| `path` | ✅ | `/decoywatch` | URL path |
| `notify_email` | ✅ | — | Email address to receive alerts |
| `email_method` | ✅ | `local` | `local` (YunoHost mail) or `smtp` (external) |
| `smtp_server` | SMTP only | — | e.g. `smtp.gmail.com` |
| `smtp_port` | SMTP only | `587` | `25`, `465`, or `587` |
| `smtp_user` | SMTP only | — | SMTP username |
| `smtp_password` | SMTP only | — | SMTP password or app password |
| `smtp_from` | optional | `decoy-watch@localhost` | From address for alert emails |
| `watch_dirs` | ✅ | `/home/yunohost.backup/archives` | Comma-separated absolute paths to monitor |
| `monitoring_mode` | ✅ | `inotify` | `inotify`, `aide`, or `both` |
| `decoy_types` | ✅ | `all` | `aws`, `database`, `ssh`, or `all` |
| `enable_network_honeypot` | ✅ | `true` | Deploy OpenCanary SSH/HTTP honeypot |

---

## What gets installed

### Decoy files

Created in each watched directory at install time:

```
📁 /home/yunohost.backup/archives/
├── aws_credentials.fake       ← Fake AWS access key + secret
├── database_backup.sql.fake   ← Fake PostgreSQL dump
├── ssh_key.pem.fake           ← Fake RSA private key
└── .decoy_watch_marker        ← Internal marker file
```

All `.fake` files have permissions `440` (root:root) and contain clearly marked dummy data.

### Services

| Service | Purpose |
|---|---|
| `decoy-file-watch.service` | inotify watcher — triggers alert on any file access |
| `decoy-net-honeypot.service` | OpenCanary SSH/HTTP honeypot (if enabled) |
| `decoy-webhook.service` | Flask receiver for OpenCanary alerts |
| `decoy-aide-check.timer` | Daily AIDE integrity check |

### Ports

| Port | Protocol | Exposed | Purpose |
|---|---|---|---|
| 18080 | TCP | No | Internal webhook (OpenCanary → Flask) |
| 2222 | TCP | Yes | SSH honeypot |
| 8088 | TCP | Yes | HTTP honeypot |

---

## How monitoring works

### inotify mode

A persistent `inotifywait` process watches your directories. Any `access`, `modify`, or `attrib` event on a decoy file triggers an immediate email alert containing the file path and timestamp.

### AIDE mode

AIDE (Advanced Intrusion Detection Environment) builds a cryptographic database of your decoy files at install time. A daily systemd timer runs `aide --check` and emails you if anything has changed.

### Both

Both inotify (real-time) and AIDE (daily integrity check) run simultaneously — inotify catches live access, AIDE catches anything that slipped through.

---

## Post-install configuration

Update settings using the YunoHost `configure` action, or directly via CLI:

```bash
# Change alert email
yunohost app setting set decoy_watch notify_email "newalert@example.com"

# Switch to external SMTP
yunohost app setting set decoy_watch email_method smtp
yunohost app setting set decoy_watch smtp_server "smtp.gmail.com"
yunohost app setting set decoy_watch smtp_port "587"
yunohost app setting set decoy_watch smtp_user "you@gmail.com"
yunohost app setting set decoy_watch smtp_password "your-app-password"

# Add more directories to monitor
yunohost app setting set decoy_watch watch_dirs \
  "/home/yunohost.backup/archives,/var/backups,/srv/sensitive"

# Switch monitoring mode
yunohost app setting set decoy_watch monitoring_mode both

# Disable network honeypot
yunohost app setting set decoy_watch enable_network_honeypot 0
```

After changing settings, restart affected services:

```bash
systemctl restart decoy-file-watch
systemctl restart decoy-net-honeypot
```

---

## Testing your setup

### Verify decoy files exist

```bash
ls -la /home/yunohost.backup/archives/*.fake
```

### Trigger a test alert manually

```bash
sudo bash /opt/yunohost/decoy_watch/scripts/notify \
  "Test Alert" "If you see this, alerting works!" warning
```

### Simulate a decoy access

```bash
cat /home/yunohost.backup/archives/aws_credentials.fake
```

You should receive an email alert within seconds.

### Check service status

```bash
systemctl status decoy-file-watch
systemctl status decoy-net-honeypot
journalctl -u decoy-file-watch -f
journalctl -u decoy-net-honeypot -f
```

### Verify AIDE database

```bash
# Check database exists
ls -lh /var/lib/aide/aide.db.gz

# Run a manual check
aide --check --config /etc/aide/aide.conf
```

---

## Backup and restore

Backup is handled automatically by YunoHost. It preserves:

- `/etc/aide/aide.conf.d/decoy_watch.conf`
- `/etc/opencanaryd/`
- `/opt/yunohost/decoy_watch/conf/`

Decoy files themselves are **not** backed up — they are regenerated from scratch on restore.

---

## Upgrading from GitHub

If you push changes to your fork:

1. Tag a new release on GitHub (e.g. `v1.1`)
2. Get the SHA256 of the tarball:
   ```bash
   curl -sL "https://github.com/YOUR_USER/DecoyWatch_ynh/archive/refs/tags/v1.1.tar.gz" | sha256sum
   ```
3. Update `manifest.toml`:
   ```toml
   sources.main.url = "https://github.com/YOUR_USER/DecoyWatch_ynh/archive/refs/tags/v1.1.tar.gz"
   sources.main.sha256 = "<hash from step 2>"
   ```
4. Install or upgrade:
   ```bash
   yunohost app upgrade decoy_watch -u https://github.com/YOUR_USER/DecoyWatch_ynh
   ```

---

## Security best practices

**Do:**
- Monitor logs regularly: `journalctl -u decoy-* -f`
- Place decoys in paths attackers commonly target: `/home/*/backups/`, `/var/www/`, `/root/`
- Use believable but clearly fake content in decoy files
- Rotate decoy content periodically to stay convincing

**Don't:**
- Put real credentials or data in `.fake` files
- Remove the `DECOY FILE` warning headers from decoys
- Expose port 18080 (the internal webhook) externally
- Place decoys in paths used by legitimate automated scripts (they will trigger false alerts)

---

## Troubleshooting

### No alert emails received

```bash
# Test the notify script directly
sudo bash /opt/yunohost/decoy_watch/scripts/notify "Test" "test" info

# Verify mail is working on your YunoHost
echo "test" | mail -s "test" root@yourdomain.tld

# Check settings are stored correctly
yunohost app showsettings decoy_watch
```

### inotify watcher not running

```bash
systemctl status decoy-file-watch
journalctl -u decoy-file-watch --no-pager -n 50
systemctl restart decoy-file-watch
```

### AIDE database missing

```bash
aide --init --config /etc/aide/aide.conf
cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

### OpenCanary won't start

```bash
journalctl -u decoy-net-honeypot --no-pager -n 50
python3 -m json.tool /etc/opencanaryd/opencanary.conf
```

---

## License and attribution

| Component | License | Source |
|---|---|---|
| OpenCanary | BSD-3-Clause | [thinkst/opencanary](https://github.com/thinkst/opencanary) |
| AIDE | GPL-2.0-only | [aide/aide](https://github.com/aide/aide) |
| inotify-tools | GPL-2.0-only | [inotify-tools/inotify-tools](https://github.com/inotify-tools/inotify-tools) |
| Decoy Watch scripts | MIT | This repository |
| YunoHost helpers | AGPL-3.0 | [yunohost.org](https://yunohost.org) |

Full license texts: [doc/LICENSES.md](doc/LICENSES.md)

---

## Support

- 🐛 **Bugs**: [GitHub Issues](https://github.com/DanversKara/DecoyWatch_ynh/issues)
- 💬 **Discussion**: [YunoHost Forum](https://forum.yunohost.org/c/apps/11) — tag `decoy-watch`

---

*Decoy Watch — because the best defense is knowing when you've been probed.* 🪤
