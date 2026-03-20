# github-switcher

A macOS menu bar app for switching between multiple GitHub accounts. Switches the active `gh` CLI account and optionally launches a Claude terminal session for the selected account.

## Features

- See your active GitHub account at a glance in the menu bar
- Switch between accounts with one click
- Launch a Claude terminal session as any account
- Toggle `--dangerously-skip-permissions` for Claude launches

## Requirements

- macOS
- [gh](https://cli.github.com/) — GitHub CLI, authenticated with two or more accounts
- Python 3
- [rumps](https://github.com/jaredks/rumps) — Python library for macOS menu bar apps
- [claude](https://claude.ai/code) — Claude Code CLI *(optional, for terminal launch)*

## Installation

**1. Install dependencies**

```bash
brew install gh
pip3 install rumps
```

**2. Authenticate your GitHub accounts**

```bash
gh auth login                        # first account
gh auth login                        # second account (run again, follow prompts)
gh auth status                       # verify both are listed
```

**3. Clone and configure**

```bash
git clone https://github.com/John-richter/github-switcher
cd github-switcher
cp config.sample.json config.json
```

Edit `config.json` with your account names and binary paths:

```json
{
  "accounts": ["your-account", "your-other-account"],
  "gh_path": "/usr/local/bin/gh",
  "claude_path": "/usr/local/bin/claude",
  "terminal": "Terminal"
}
```

To find your binary paths:

```bash
which gh
which claude
```

**4. Run**

```bash
python3 github_switcher.py
```

## Auto-start on Login

Create a LaunchAgent to start the app automatically at login:

```bash
cat > ~/Library/LaunchAgents/com.yourname.github-switcher.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourname.github-switcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/path/to/github-switcher/github_switcher.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/yourname/Library/Logs/github-switcher.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourname/Library/Logs/github-switcher.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.yourname.github-switcher.plist
```

Replace `com.yourname`, `/path/to/github-switcher`, and `/Users/yourname` with your actual values.

## Configuration

| Key | Description | Default |
|-----|-------------|---------|
| `accounts` | List of `gh` usernames to show in the menu | *(required)* |
| `gh_path` | Full path to the `gh` binary | `/usr/local/bin/gh` |
| `claude_path` | Full path to the `claude` binary | `/usr/local/bin/claude` |
| `terminal` | Terminal app name for Claude sessions | `Terminal` |

`terminal` accepts any app name that supports AppleScript's `do script` — `Terminal`, `iTerm2`, etc.

`config.json` is gitignored. Copy `config.sample.json` to get started.

## Usage

Click the menu bar item (`GH: account-name`) to open the menu:

- **Switch** — sets the account as active for all `gh` CLI operations
- **Open Claude Terminal** — switches to the account and opens a new terminal window running `claude`
- **Dangerously Skip Permissions** — toggle on to launch Claude with `--dangerously-skip-permissions`
