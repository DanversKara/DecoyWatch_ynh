# Decoy Watch (YunoHost app) [WORKING BUILD]
# README IS OUT OF DATE - NEW COMING SOON

**Decoy Watch** — Because the best defense is knowing when you've been probed. 🔍🛡️  
“One Decoy at a Time” 🪤

This repository packages **Decoy Watch** as a **YunoHost** application (`decoy_watch`).

Decoy Watch is an open-source honeypot/decoy monitoring setup designed to help detect unauthorized access attempts (e.g., touching backup files or decoy credentials) and send alerts via email.

⚠️ **WARNING**: Decoy files are TRAPS. Never use them for real credentials or data. Accessing them intentionally will trigger security alerts.

[![YunoHost App](https://img.shields.io/badge/YunoHost-11.2+-blue?logo=yunohost)](https://yunohost.org)
[![License](https://img.shields.io/badge/license-BSD--3Clause%20AND%20GPL--2.0%20AND%20MIT-green)](LICENSE)
[![FOSS](https://img.shields.io/badge/100%25%20FOSS-✅-brightgreen)](#license)

## Features

- Monitor one or more directories for suspicious access/activity
- Multiple monitoring backends:
  - `inotify`
  - `aide`
  - `both`
- Decoy file types selectable at install time:
  - `aws`, `database`, `ssh`, or `all`
- Email alerting:
  - via YunoHost local mail
  - or via external SMTP
- Optional network honeypot toggle (may require manual OpenCanary configuration)

## YunoHost integration

- Minimum YunoHost version: `>= 11.2`
- Architectures: `amd64`, `arm64`
- Multi-instance: ✅

### Ports / endpoints

Declared ports (see `manifest.toml`):

- Internal webhook port (default): `18080` (not exposed)
- Optional exposed ports:
  - SSH decoy: `2222`
  - HTTP decoy: `8088`

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🪤 Decoy Generator | Creates fake AWS, DB, SSH credentials marked as monitored |
| 🔍 File Monitoring | Real-time (`inotify`) or compliance-grade (`AIDE`) detection |
| 🌐 Network Honeypots | Optional OpenCanary SSH/HTTP decoys |
| 📧 Email Alerts | Local YunoHost mail or external SMTP |
| 🔀 Auto Port Detection | Finds free ports to avoid conflicts |
| 🔐 YunoHost Native | Secure config storage, firewall rules, backups |

---

## 📋 Requirements

| Requirement | Details |
|-------------|---------|
| YunoHost | ≥ 11.2 |
| Architecture | amd64 or arm64 |
| Disk Space | ~500 MB |
| RAM | 128 MB runtime / 256 MB during install |
| Email | Working mail system (YunoHost local) **or** SMTP credentials for external provider |

---

## 🚀 Installation

### Via YunoHost Web Admin

```bash
yunohost app install https://github.com/DanversKara/DecoyWatch_ynh
   ```

Install through the YunoHost admin interface, or via CLI.

During install you will be prompted for:

- **Domain** for webhook endpoint
- **URL path** (default: `/decoywatch`)
- **Alert email** (required): `user@example.com`
- **Email method**: `local` (use YunoHost's mail system) or `smtp` (configure external server)
- **SMTP settings** *(only if `smtp` selected)*:
  - Server address, port (default: 587)
  - Auth username & password
  - From-address (default: `decoy-watch@$(hostname)`)
- **Directories to monitor**: comma-separated absolute paths (e.g., `/home/user/backups,/var/backups`)
- **Monitoring mode**: `inotify` (real-time), `aide` (compliance-grade), or `both`
- **Decoy types**: `aws`, `database`, `ssh`, or `all`
- **Enable network honeypot**: Yes/No (OpenCanary SSH/HTTP decoys)

> Tip: `watch_dirs` must be absolute paths and comma-separated.

## ⚙️ Post-Install Configuration

Update notification settings via YunoHost CLI:

```bash
# Change alert email
yunohost app setting set decoy_watch notify_email "newalert@example.com"

# Switch to external SMTP
yunohost app setting set decoy_watch email_method smtp
yunohost app setting set decoy_watch smtp_server "smtp.example.com"
yunohost app setting set decoy_watch smtp_port "587"
# ...etc

## 🎣 How Decoys Work

### File Decoys

```
📁 /home/BACKUP_USER/backups/
├── aws_credentials.fake      ← Fake AWS keys
├── database_backup.sql.fake  ← Fake DB dump
├── ssh_key.pem.fake          ← Fake SSH private key
└── .decoy_watch_marker       ← Internal marker
```

## 🔍 Summary of Changes Made
```
| Section | What Was Wrong | What Was Fixed |
|---------|---------------|----------------|
| 📋 Requirements | Listed Telegram/Matrix/Signal as required | Changed to email/SMTP requirements |
| 🚀 Installation | Example showed Telegram tokens/chat IDs | Updated to show email/SMTP parameters |
| ⚙️ Configuration | Referenced non-existent chat config keys | Aligned with actual `notify_email`/`smtp_*` settings |
| General | Minor duplicate features section | Suggested consolidation for clarity |


> 💡 **Pro Tip**: Run `yunohost app showsettings decoy_watch` after install to verify which settings are actually stored—this helps keep docs in sync with reality.

If you *do* intend to support Telegram/Matrix/Signal/ntfy/matrix/Gotify in the future, I recommend updating `scripts/install` to handle those parameters first, or just download this code as a zip file, goto chatgpt/claude, upload and ask it to modify it to work with the code, then re-upload to your GitHub, and do the hash sha256sum 1. upload all files to github after new changes, 2. goto release, draft a New release, v1.0, tag v1.0, then ssh curl -sL "https://github.com/YOUR_GIT_HUB/DecoyWatch_ynh/archive/refs/tags/v1.0.tar.gz" | sha256sum get the hash code then goto manifest.toml update url and sources.main.sha256 = "UPDATE_ME_AFTER_TAGGING" then install app on yunohost repo: "https://github.com/YOUR_GIT_HUB/DecoyWatch_ynh


## ⚙️ Advanced Configuration

```
# Add more watch directories
yunohost app setting set decoy_watch watch_dirs \
  "/home/BACKUP_USER/backups,/var/backups,/srv/important"

# Switch monitoring mode
yunohost app setting set decoy_watch monitoring_mode both

# Disable network honeypot
yunohost app setting set decoy_watch enable_network_honeypot 0
```

## 🧪 Testing Your Setup

### 1. Verify decoy files exist

```
ls -la /home/BACKUP_USER/backups/*.fake
```

### 2. Test notification manually

```
sudo /opt/yunohost/decoy_watch/scripts/notify "🧪 Test Alert" "If you see this, alerts work!" warning
```

## 🔐 Security Best Practices

**✅ Do**:

- Store tokens via YunoHost settings (never in scripts)
- Use strong, believable fake passwords in decoys
- Rotate decoy content periodically
- Monitor logs: `journalctl -u decoy-* -f`

**❌ Don't**:

- Place real credentials in `.fake` files
- Remove warning headers from decoys
- Expose the internal webhook port (`18080`) directly
- Place decoys in paths used by legitimate automated scripts

* * *


## Documentation

- Repository: https://github.com/DanversKara/DecoyWatch_ynh
- License attribution and third-party notices: `doc/LICENSES.md`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

Need help or want to report a bug? See [SUPPORT.md](SUPPORT.md).  
Security issues should be reported privately — see [SECURITY.md](SECURITY.md) (recommended).

## 📜 License & Attribution

| Component           | License      | Source                                                                                   |
|---------------------|--------------|------------------------------------------------------------------------------------------|
| OpenCanary          | BSD-3-Clause | [github.com/thinkst/opencanary](https://github.com/thinkst/opencanary)                   |
| AIDE                | GPL-2.0-only | [github.com/Achiefs/fim](https://github.com/Achiefs/fim)                                 |
| inotify-tools       | GPL-2.0-only | [github.com/inotify-tools/inotify-tools](https://github.com/inotify-tools/inotify-tools) |
| Decoy Watch scripts | MIT          | This repository                                                                          |
| YunoHost helpers    | AGPL-3.0     | [yunohost.org](https://yunohost.org)                                                     |

Full license texts: [doc/LICENSES.md](doc/LICENSES.md)
* * *

## 🆘 Support

- 🐛 **Bugs**: [GitHub Issues](https://github.com/DanversKara/DecoyWatch_ynh/issues)
- 💬 **Discussion**: [YunoHost Forum](https://forum.yunohost.org/c/apps/11) (tag `decoy-watch`)
- 📚 **Docs**: [Admin Guide](https://github.com/DanversKara/DecoyWatch_ynh/blob/main/doc/ADMIN.md)

* * *

> 🎯 **Pro Tip**: Place decoys in common attack paths:  
> `/home/*/backups/`, `/var/www/`, `/etc/`, `/root/`  
> **Never** in paths used by legitimate automated scripts!

**Decoy Watch** — Because the best defense is knowing when you've been probed. 🔍🛡️

*"One Decoy at a Time"* 🪤
