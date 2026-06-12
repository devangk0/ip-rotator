import threading
import time
import requests
import datetime
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label, Log
from textual.containers import Horizontal, Vertical
from textual import on
from stem import Signal
from stem.control import Controller

# --- Tor configuration (same as tkinter script) ---
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051

def get_ip():
    try:
        s = requests.Session()
        s.proxies = {
            "http":  f"socks5h://127.0.0.1:{TOR_SOCKS_PORT}",
            "https": f"socks5h://127.0.0.1:{TOR_SOCKS_PORT}",
        }
        return s.get("https://checkip.amazonaws.com", timeout=10).text.strip()
    except:
        return None

def new_circuit():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
        return True
    except:
        return False


# --- Textual UI (styled) ---
CSS = """
Screen {
    layout: horizontal;
}
#left {
    width: 1fr;
    height: 100%;
    border: solid $surface;
    padding: 1 2;
}
#left-title {
    text-align: center;
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}
.stat-row {
    height: 3;
    layout: horizontal;
}
.stat-label {
    width: 14;
    color: $text-muted;
    content-align: left middle;
}
.stat-value {
    width: 1fr;
    color: $success;
    text-style: bold;
    content-align: left middle;
}
#countdown {
    color: $success;
    text-style: bold;
    content-align: left middle;
    width: 1fr;
}
#countdown.urgent {
    color: $error;
}
#status-val {
    color: $text-muted;
    text-style: bold;
    content-align: left middle;
    width: 1fr;
}
#status-val.running {
    color: $success;
}
#status-val.stopped {
    color: $error;
}
#btn-area {
    margin-top: 1;
}
#btn-start {
    height: 3;
    background: $success;
    color: $background;
    margin-bottom: 1;
    width: 1fr;
}
#btn-stop {
    height: 3;
    background: $error;
    color: $background;
    margin-bottom: 1;
    width: 1fr;
}
#btn-row {
    height: 3;
    layout: horizontal;
}
#btn-rotate {
    height: 3;
    background: $warning;
    color: $background;
    width: 1fr;
    margin-right: 1;
}
#btn-clear {
    height: 3;
    width: 1fr;
}
#right {
    width: 2fr;
    height: 100%;
    border: solid $surface;
    padding: 1 2;
}
#right-title {
    text-align: center;
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}
#rotation-log {
    height: 1fr;
    border: solid $surface;
    padding: 0 1;
}

"""

class IPRotatorApp(App):
    CSS = CSS

    BINDINGS = [
        ("t", "toggle_dark", "Toggle Theme"),
        ("ctrl+q", "app_quit", "Quit"),
    ]

    def __init__(self, interval: int):
        super().__init__()
        self.interval = interval
        self.running = False
        self.count = 0
        self._stop = threading.Event()
        self._force = threading.Event()
        self._thread = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            # Left panel
            with Vertical(id="left"):
                yield Label("Live Stats", id="left-title")

                with Horizontal(classes="stat-row"):
                    yield Label("Current IP", classes="stat-label")
                    yield Label("—", id="ip-val", classes="stat-value")

                with Horizontal(classes="stat-row"):
                    yield Label("Rotations", classes="stat-label")
                    yield Label("0", id="rot-val", classes="stat-value")

                with Horizontal(classes="stat-row"):
                    yield Label("Uptime", classes="stat-label")
                    yield Label("00:00:00", id="up-val", classes="stat-value")

                with Horizontal(classes="stat-row"):
                    yield Label("Interval", classes="stat-label")
                    yield Label(f"{self.interval}s", id="interval-val", classes="stat-value")

                with Horizontal(classes="stat-row"):
                    yield Label("Next Rotate", classes="stat-label")
                    yield Label("—", id="countdown", classes="stat-value")

                with Horizontal(classes="stat-row"):
                    yield Label("Status", classes="stat-label")
                    yield Label("idle", id="status-val", classes="stopped")

                with Vertical(id="btn-area"):
                    yield Button("▶  Start", id="btn-start", variant="success")
                    yield Button("■  Stop", id="btn-stop", variant="error", disabled=True)
                    with Horizontal(id="btn-row"):
                        yield Button("↺  Rotate Now", id="btn-rotate", variant="warning", disabled=True)
                        yield Button("⌫  Clear Log", id="btn-clear")

            # Right panel
            with Vertical(id="right"):
                yield Label("Rotation Log", id="right-title")
                yield Log(id="rotation-log", highlight=True)

        yield Footer()

    # --- Thread‑safe UI updates (for background thread) ---
    def _update_status_threadsafe(self, text: str, is_running: bool, is_error: bool = False):
        def upd():
            lbl = self.query_one("#status-val", Label)
            lbl.update(text)
            lbl.remove_class("running", "stopped")
            if is_error:
                lbl.add_class("stopped")
            elif is_running:
                lbl.add_class("running")
            else:
                lbl.add_class("stopped")
        self.call_from_thread(upd)

    def _update_ip_threadsafe(self, ip: str):
        self.call_from_thread(lambda: self.query_one("#ip-val", Label).update(ip))

    def _update_rotations_threadsafe(self, count: int):
        self.call_from_thread(lambda: self.query_one("#rot-val", Label).update(str(count)))

    def _update_uptime_threadsafe(self, elapsed: int):
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.call_from_thread(lambda: self.query_one("#up-val", Label).update(f"{h:02d}:{m:02d}:{s:02d}"))

    def _update_countdown_threadsafe(self, remaining: int):
        def upd():
            lbl = self.query_one("#countdown", Label)
            lbl.update(f"{remaining}s")
            if remaining <= 5:
                lbl.add_class("urgent")
            else:
                lbl.remove_class("urgent")
        self.call_from_thread(upd)

    def _log_entry_threadsafe(self, ip: str, initial: bool = False):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        tag = "INIT" if initial else f"#{self.count:04d}"
        def upd():
            log = self.query_one("#rotation-log", Log)
            log.write_line(f"[{ts}]  {tag}  {ip}")
        self.call_from_thread(upd)

    def _set_buttons_enabled_threadsafe(self, start_enabled: bool, stop_enabled: bool, rotate_enabled: bool):
        def upd():
            self.query_one("#btn-start", Button).disabled = not start_enabled
            self.query_one("#btn-stop", Button).disabled = not stop_enabled
            self.query_one("#btn-rotate", Button).disabled = not rotate_enabled
        self.call_from_thread(upd)

    def _clear_countdown_display_threadsafe(self):
        self.call_from_thread(lambda: self.query_one("#countdown", Label).update("—"))

    # --- Rotation loop (identical logic to tkinter version, using thread‑safe updates) ---
    def _rotation_loop(self, interval: int):
        start_time = time.time()
        while not self._stop.is_set():
            # Rotate circuit
            if not new_circuit():
                self._log_entry_threadsafe("[error] circuit failed")
                self._stop.wait(5)
                continue
            time.sleep(3)   # wait for new circuit
            ip = get_ip()
            if ip:
                self.count += 1
                self._update_rotations_threadsafe(self.count)
                self._update_ip_threadsafe(ip)
                self._log_entry_threadsafe(ip)
            else:
                self._log_entry_threadsafe("[error] IP fetch failed")
            # Countdown loop with force-check
            for remaining in range(interval, 0, -1):
                if self._stop.is_set():
                    break
                if self._force.is_set():
                    self._force.clear()
                    break
                self._update_countdown_threadsafe(remaining)
                elapsed = int(time.time() - start_time)
                self._update_uptime_threadsafe(elapsed)
                time.sleep(1)
            if self._stop.is_set():
                break
        # Cleanup after stop
        self._clear_countdown_display_threadsafe()
        self._set_buttons_enabled_threadsafe(True, False, False)
        self._update_status_threadsafe("stopped", is_running=False, is_error=True)

    # --- Button handlers (on main thread, directly update UI) ---
    @on(Button.Pressed, "#btn-start")
    async def on_start(self, event: Button.Pressed):
        if self.running:
            return
        self.running = True
        self._stop.clear()
        self._force.clear()
        self.count = 0
        # Direct UI updates (no call_from_thread needed)
        self.query_one("#rot-val", Label).update("0")
        self._update_status_direct("running", is_running=True)
        self._set_buttons_direct(False, True, True)
        self._thread = threading.Thread(target=self._rotation_loop, args=(self.interval,), daemon=True)
        self._thread.start()

    @on(Button.Pressed, "#btn-stop")
    async def on_stop(self, event: Button.Pressed):
        if not self.running:
            return
        self.running = False
        self._stop.set()
        # Do NOT join — would block the event loop
        self._update_status_direct("idle", is_running=False)
        self._set_buttons_direct(True, False, False)

    @on(Button.Pressed, "#btn-rotate")
    async def on_rotate_now(self, event: Button.Pressed):
        if self.running:
            self._force.set()

    @on(Button.Pressed, "#btn-clear")
    async def on_clear(self, event: Button.Pressed):
        self.query_one("#rotation-log", Log).clear()

    # --- Direct UI update methods (for main thread) ---
    def _update_status_direct(self, text: str, is_running: bool, is_error: bool = False):
        lbl = self.query_one("#status-val", Label)
        lbl.update(text)
        lbl.remove_class("running", "stopped")
        if is_error:
            lbl.add_class("stopped")
        elif is_running:
            lbl.add_class("running")
        else:
            lbl.add_class("stopped")

    def _set_buttons_direct(self, start_enabled: bool, stop_enabled: bool, rotate_enabled: bool):
        self.query_one("#btn-start", Button).disabled = not start_enabled
        self.query_one("#btn-stop", Button).disabled = not stop_enabled
        self.query_one("#btn-rotate", Button).disabled = not rotate_enabled

    # --- Async helpers for initial fetch (on main thread) ---
    async def on_mount(self):
        # Direct UI updates (main thread)
        self._update_status_direct("checking tor...", is_running=False)
        tor_ok = await asyncio.to_thread(self._check_tor_sync)
        if tor_ok:
            self._update_status_direct("Tor connected", is_running=False)
            ip = await asyncio.to_thread(get_ip)
            if ip:
                self.query_one("#ip-val", Label).update(ip)
                ts = datetime.datetime.now().strftime("%H:%M:%S")
                self.query_one("#rotation-log", Log).write_line(f"[{ts}]  INIT  {ip}")
            else:
                ts = datetime.datetime.now().strftime("%H:%M:%S")
                self.query_one("#rotation-log", Log).write_line(f"[{ts}]  [error] IP unreachable")
        else:
            self._update_status_direct("Tor not running", is_running=False, is_error=True)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.query_one("#rotation-log", Log).write_line(f"[{ts}]  [error] Tor not running")

    def _check_tor_sync(self):
        try:
            with Controller.from_port(port=TOR_CONTROL_PORT) as c:
                c.authenticate()
            return True
        except:
            return False

    # --- Theme and quit actions ---
    def action_toggle_dark(self):
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

    def action_app_quit(self):
        self.exit()


# --- Entry point ---
if __name__ == "__main__":
    interval = 10
    print("IP Rotator - Tor based")
    while True:
        try:
            raw = input("Rotation interval in seconds (min 5): ")
            interval = int(raw)
            if interval < 5:
                print("Minimum is 5 — setting to 5.")
                interval = 5
            break
        except ValueError:
            print("Please enter a whole number.")
    IPRotatorApp(interval).run()