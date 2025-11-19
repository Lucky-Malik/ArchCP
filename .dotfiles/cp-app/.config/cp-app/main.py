from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Input, Label, DataTable
from datetime import datetime, timedelta, timezone
import subprocess
import requests
import os
import re

# --- CONFIGURATION & ENV LOADING ---
HOME = os.path.expanduser("~")
CONTEST_ON_SCRIPT = f"{HOME}/.config/cp-tools/scripts/contest-on.sh"
CONTEST_OFF_SCRIPT = f"{HOME}/.config/cp-tools/scripts/contest-off.sh"
ENV_PATH = f"{HOME}/.dotfiles/cp-tools-api/.config/cp-tools/api/.env"

def load_api_key():
    # DEBUG PRINT
    print(f"--- DEBUG: Looking for .env at: {ENV_PATH}")
    """Load the CList API key from the .env file."""
    if not os.path.exists(ENV_PATH):
        return None
    with open(ENV_PATH, 'r') as f:
        for line in f:
            if line.startswith("CLIST_API_KEY="):
                # Remove key name, quotes, and whitespace
                raw_val = line.split("=", 1)[1].strip().strip('"')
                return raw_val
    return None

# --- DATA FETCHING ---
def fetch_contests():
    """Fetch upcoming contests from CList."""
    api_key = load_api_key()
    if not api_key:
        return []

    # Time logic
    now = datetime.now(timezone.utc)
    later = now + timedelta(days=2) # Fetch next 2 days
    
    url = (
        f"https://clist.by/api/v4/contest/?"
        f"{api_key}"
        f"&resource_id__in=1,93" # Codeforces (1) & AtCoder (93)
        f"&start__gt={now.strftime('%Y-%m-%d %H:%M:%S')}"
        f"&start__lt={later.strftime('%Y-%m-%d %H:%M:%S')}"
        f"&order_by=start"
    )
    
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json().get("objects", [])
    except:
        return []

def make_safe_name(event_name):
    """Turn 'Codeforces Round #900 (Div. 3)' into 'Codeforces_Round_900_Div_3'"""
    # Replace non-alphanumeric chars with underscore
    safe = re.sub(r'[^a-zA-Z0-9]', '_', event_name)
    # Remove duplicate underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    return safe.strip('_')

# --- THE TUI APP ---
class CPCli(App):
    """The Competitive Programming Cockpit."""
    
    CSS = """
    Screen { align: center middle; }
    Container { width: 80; height: 80%; border: solid green; padding: 1; background: $surface; }
    #title { text-align: center; text-style: bold; margin-bottom: 1; color: $text; }
    Button { width: 100%; margin-top: 1; }
    DataTable { height: 1fr; margin-top: 1; border: solid $secondary; }
    .label { margin-top: 1; color: $accent; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label("CP MISSION CONTROL", id="title")
            
            # --- Contest Mode Controls ---
            yield Label("Contest Mode:", classes="label")
            with Horizontal():
                yield Button("Mode ON", id="btn_on", variant="error")
                yield Button("Mode OFF", id="btn_off", variant="success")

            # --- The List ---
            yield Label("\nSelect a Contest to Scaffold & Open:", classes="label")
            yield DataTable(id="contest_table", cursor_type="row")
            
            yield Static(id="status_log", content="Fetching contests...")
        yield Footer()

    def on_mount(self) -> None:
        """Run when app starts."""
        table = self.query_one(DataTable)
        table.add_columns("Event", "Site", "Starts In")
        
        contests = fetch_contests()
        
        if not contests:
            self.query_one("#status_log", Static).update("❌ Could not fetch contests (Check API/Internet)")
            return

        now = datetime.now(timezone.utc)
        
        for c in contests:
            # Calculate rough time until start
            start_dt = datetime.fromisoformat(c['start']).replace(tzinfo=timezone.utc)
            diff = start_dt - now
            hours = int(diff.total_seconds() // 3600)
            time_str = f"{hours}h"

            # Add row. We use the contest object as the "Row Key" so we can retrieve it later!
            # We store (Event Name, Site Name, Time String)
            # We Identify the row by the specific Contest ID
            key = c['id'] 
            label = c['event']
            site = c['resource']
            
            # Add the row, and attach the full data object to it
            table.add_row(label, site, time_str, key=key)
            # We store the full data in a separate dictionary mapping if needed, 
            # but here we can just store the list and lookup, or attach metadata.
            # Textual's modern approach lets us map keys.
            # Let's store the specific data we need in a hidden map for simplicity
            if not hasattr(self, "contest_map"):
                self.contest_map = {}
            self.contest_map[key] = c

        self.query_one("#status_log", Static).update("✅ Ready. Click a contest to launch.")
        self.set_focus(table)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        row_key = event.row_key.value
        contest_data = self.contest_map.get(row_key)
        
        if not contest_data:
            return

        # 1. Prepare Data
        raw_name = contest_data['event']
        url = contest_data['href'] # CList gives us the URL
        safe_folder_name = make_safe_name(raw_name)

        # 2. Update Status
        self.query_one("#status_log", Static).update(f"🚀 Launching: {safe_folder_name}")

        # --- NEW: Switch to a Named Workspace ---
    # We use i3-msg to switch to a workspace named after the contest
    # The "10:" prefix is optional, but helps sorting. We can just use the name.
        workspace_name = f"{safe_folder_name}" 
        try:
            subprocess.run(["i3-msg", "workspace", workspace_name])
        except Exception as e:
        # Even if i3 fails, we still want to launch the apps
            pass
        # 3. Execute Commands
        # We need to run scaffold AND firefox.
        # Scaffold needs a terminal. Firefox does not.
        
        # Command A: Open Firefox
        subprocess.Popen(["firefox", url])

        # Command B: Open Terminal + Scaffold
        # Note: We pass the safe name to scaffold
        cmd = f"source ~/.bashrc; scaffold {safe_folder_name}; nvim .; exec bash"
        subprocess.Popen(["alacritty", "-e", "bash", "-c", cmd])
        
        # Exit the TUI
        self.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle mode buttons."""
        button_id = event.button.id
        if button_id == "btn_on":
            self.run_script(CONTEST_ON_SCRIPT)
        elif button_id == "btn_off":
            self.run_script(CONTEST_OFF_SCRIPT)

    def run_script(self, script_path):
        try:
            subprocess.Popen(["alacritty", "-e", "bash", "-c", f"{script_path}; read -p 'Press Enter to close...'"])
        except Exception as e:
            self.query_one("#status_log", Static).update(f"Error: {e}")

if __name__ == "__main__":
    app = CPCli()
    app.run()
