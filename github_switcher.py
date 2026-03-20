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


config = load_config()
ACCOUNTS = config["accounts"]
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


def switch_to(account):
    subprocess.run(
        [GH, "auth", "switch", "--user", account],
        capture_output=True
    )


def open_claude_terminal(skip_permissions):
    cmd = f"{CLAUDE} --dangerously-skip-permissions" if skip_permissions else CLAUDE
    script = f'tell application "{TERMINAL}" to do script "{cmd}"'
    subprocess.Popen(["osascript", "-e", script])


class GitHubSwitcher(rumps.App):
    def __init__(self):
        self.active = get_active_account()
        self.skip_permissions = False
        super().__init__(f"GH: {self.active}", quit_button=None)
        self.build_menu()

    def build_menu(self):
        self.menu.clear()
        for account in ACCOUNTS:
            is_active = account.lower() == self.active.lower()
            label = f"✓ {account}" if is_active else f"  {account}"

            switch_item = rumps.MenuItem(
                "Active" if is_active else "Switch",
                callback=None if is_active else self.make_switch(account)
            )
            claude_item = rumps.MenuItem(
                "Open Claude Terminal",
                callback=self.make_open_claude(account)
            )

            submenu = rumps.MenuItem(label)
            submenu.add(switch_item)
            submenu.add(claude_item)
            self.menu.add(submenu)

        self.menu.add(rumps.separator)

        skip_item = rumps.MenuItem(
            "Dangerously Skip Permissions",
            callback=self.toggle_skip_permissions
        )
        skip_item.state = self.skip_permissions
        self.menu.add(skip_item)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    def toggle_skip_permissions(self, sender):
        self.skip_permissions = not self.skip_permissions
        sender.state = self.skip_permissions

    def make_switch(self, account):
        def switch(_):
            switch_to(account)
            self.active = get_active_account()
            self.title = f"GH: {self.active}"
            self.build_menu()
        return switch

    def make_open_claude(self, account):
        def open_claude(_):
            switch_to(account)
            self.active = get_active_account()
            self.title = f"GH: {self.active}"
            self.build_menu()
            open_claude_terminal(self.skip_permissions)
        return open_claude


if __name__ == "__main__":
    GitHubSwitcher().run()
