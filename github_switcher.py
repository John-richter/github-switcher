#!/usr/bin/env python3
import json
import os
import subprocess
import rumps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
SAMPLE_PATH = os.path.join(SCRIPT_DIR, "config.sample.json")


def load_config():
    path = CONFIG_PATH if os.path.exists(CONFIG_PATH) else SAMPLE_PATH
    with open(path) as f:
        return json.load(f)


def normalize_accounts(raw):
    """Accept either a list of strings or a list of objects."""
    accounts = []
    for entry in raw:
        if isinstance(entry, str):
            accounts.append({"name": entry})
        else:
            accounts.append(entry)
    return accounts


config = load_config()
ACCOUNTS = normalize_accounts(config["accounts"])
GH = config.get("gh_path", "/usr/local/bin/gh")
CLAUDE = config.get("claude_path", "/usr/local/bin/claude")
TERMINAL = config.get("terminal", "Terminal")


def get_active_account():
    result = subprocess.run(
        [GH, "auth", "status"],
        capture_output=True, text=True
    )
    lines = result.stdout.splitlines()
    for i, line in enumerate(lines):
        if "Active account: true" in line:
            for j in range(i - 1, -1, -1):
                if "Logged in to github.com account" in lines[j]:
                    parts = lines[j].split("account")
                    return parts[-1].strip().split()[0]
    return "unknown"


def switch_to(account_name):
    subprocess.run(
        [GH, "auth", "switch", "--user", account_name],
        capture_output=True
    )


def open_claude_terminal(account, skip_permissions):
    claude = account.get("claude_path", CLAUDE)
    config_dir = account.get("claude_config_dir")

    cmd = claude
    if config_dir:
        cmd += f" --config-dir {os.path.expanduser(config_dir)}"
    if skip_permissions:
        cmd += " --dangerously-skip-permissions"

    script = f'tell application "{TERMINAL}" to do script "{cmd}"'
    subprocess.Popen(["osascript", "-e", script])


class GitHubSwitcher(rumps.App):
    def __init__(self):
        self.active = get_active_account()
        self.skip_permissions = {a["name"]: False for a in ACCOUNTS}
        super().__init__(f"GH: {self.active}", quit_button=None)
        self.build_menu()

    def build_menu(self):
        self.menu.clear()
        for account in ACCOUNTS:
            name = account["name"]
            is_active = name.lower() == self.active.lower()
            label = f"✓ {name}" if is_active else f"  {name}"

            switch_item = rumps.MenuItem(
                "Active" if is_active else "Switch",
                callback=None if is_active else self.make_switch(name)
            )
            claude_item = rumps.MenuItem(
                "Open Claude Terminal",
                callback=self.make_open_claude(account)
            )
            skip_item = rumps.MenuItem(
                "Dangerously Skip Permissions",
                callback=self.make_toggle_skip(name)
            )
            skip_item.state = self.skip_permissions[name]

            submenu = rumps.MenuItem(label)
            submenu.add(switch_item)
            submenu.add(rumps.separator)
            submenu.add(claude_item)
            submenu.add(skip_item)
            self.menu.add(submenu)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    def make_toggle_skip(self, name):
        def toggle(sender):
            self.skip_permissions[name] = not self.skip_permissions[name]
            sender.state = self.skip_permissions[name]
        return toggle

    def make_switch(self, name):
        def switch(_):
            switch_to(name)
            self.active = get_active_account()
            self.title = f"GH: {self.active}"
            self.build_menu()
        return switch

    def make_open_claude(self, account):
        def open_claude(_):
            name = account["name"]
            switch_to(name)
            self.active = get_active_account()
            self.title = f"GH: {self.active}"
            self.build_menu()
            open_claude_terminal(account, self.skip_permissions[name])
        return open_claude


if __name__ == "__main__":
    GitHubSwitcher().run()
