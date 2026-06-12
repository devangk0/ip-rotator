# 🔄 IP Rotator — Tor-Based TUI Tool

Automatically rotates your IP address through the Tor network on a timer you control. Includes a terminal dashboard and a pre-configured Firefox browser to verify your rotating IP.

---

## 📦 What's Inside the Package

```
ip-rotator/
├── ipRotator.py          ← main script (keep this name exactly)
├── torrc                 ← Tor configuration file
├── tor/                  ← Tor binaries (tor.exe lives here)
├── data/                 ← Tor runtime data (don't touch)
└── FirefoxPortable/      ← Firefox to verify your IP
```

---

## ✅ Requirements

- Windows 10 or 11
- Python 3.8 or newer — download from [python.org](https://python.org) if needed
  - ⚠️ During install, check **"Add Python to PATH"**
- No Tor Browser or VPN needed — everything is included

> 📁 The tool can be placed **anywhere** on any drive — no config files need editing.

---

## 🚀 Getting Started

You will need **two Command Prompt windows** open at the same time.

---

### Step 1 — Start Tor

Open your first Command Prompt and navigate to the `tor` folder inside the package:

```cmd
cd path\to\ip-rotator\tor
```

Then start Tor:

```cmd
tor.exe -f ..\torrc
```

⏳ Wait until you see this line in the output:

```
Bootstrapped 100% (done): Done
```

> 🟢 Tor is now running. **Keep this window open** — closing it stops Tor.

---

### Step 2 — Install Dependencies

Open a **second** Command Prompt and navigate to the main package folder:

```cmd
cd path\to\ip-rotator
```

Install the required Python libraries (one-time only):

```cmd
pip install textual requests stem
```

---

### Step 3 — Run the Tool

In the same second terminal, run:

```cmd
python ipRotator.py
```

> ⚠️ The script name is case-sensitive — use exactly `ipRotator.py`

You'll be prompted:

```
Rotation interval in seconds (min 5):
```

Type a number (e.g. `30`) and press **Enter**. The TUI dashboard will launch.

---

### Step 4 — Start Rotating

In the dashboard, click the **▶ Start** button.

The tool will:
1. Request a new Tor circuit
2. Wait 3 seconds for it to connect
3. Fetch your new IP
4. Count down to the next rotation
5. Repeat automatically

---

### Step 5 — Configure Firefox Proxy (once only)

Before using Firefox to verify your IP, you need to point it at Tor. Do this once — it saves permanently.

1. Open `FirefoxPortable\FirefoxPortable.exe`
2. Click the **☰ menu** (top-right) → **Settings**
3. Scroll to the bottom → **Network Settings** → click **Settings…**
4. Select **Manual proxy configuration**
5. Fill in exactly:
   - **SOCKS Host:** `127.0.0.1` &nbsp;&nbsp;&nbsp; **Port:** `9050`
   - **SOCKS version:** ● SOCKS v5
   - ☑ Check **"Proxy DNS when using SOCKS v5"**
6. Click **OK**

> ✅ You only need to do this once — Firefox Portable saves the setting.

---

### Step 6 — Verify Your IP in Firefox

1. In Firefox, go to: `http://httpbin.org/ip`
2. After each rotation completes, press **Ctrl+Shift+R** to hard-refresh
3. You should see a new IP address each time 🎉

> ⚠️ Use `http://` not `https://` — plain HTTP avoids caching issues.

---

## 🖥️ Dashboard Overview

```
┌─ Live Stats ──────┐  ┌─ Rotation Log ──────────────────────────┐
│ Current IP  x.x.x │  │ [14:02:01]  INIT   93.115.21.4          │
│ Rotations   3     │  │ [14:02:34]  #0001  185.220.101.7        │
│ Uptime      00:01 │  │ [14:03:07]  #0002  176.10.99.200        │
│ Interval    30s   │  │                                          │
│ Next Rotate 12s   │  │                                          │
│ Status      running│  │                                          │
│                   │  │                                          │
│ [▶ Start        ] │  │                                          │
│ [■ Stop         ] │  │                                          │
│ [↺ Rotate Now][⌫] │  │                                          │
└───────────────────┘  └──────────────────────────────────────────┘
```

| Button | What it does |
|---|---|
| ▶ Start | Begins automatic IP rotation |
| ■ Stop | Pauses rotation (keeps Tor running) |
| ↺ Rotate Now | Skips the countdown and rotates immediately |
| ⌫ Clear Log | Wipes the log panel |

> ⏱️ The **Next Rotate** counter turns 🔴 red when ≤ 5 seconds remain.

---

## 🛑 How to Stop Everything

1. Click **■ Stop** in the dashboard (or press `Ctrl+Q` to close the TUI entirely)
2. Switch to Terminal #1 and press `Ctrl+C` to stop Tor
3. Close Firefox Portable normally

---

## 🔧 Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `tor.exe` won't start | Wrong folder | Make sure you `cd` into the `tor\` folder first |
| Stuck at "Bootstrapped X%" | No internet / firewall blocking | Check your internet connection; temporarily disable firewall |
| `python` not recognized | Python not in PATH | Reinstall Python and tick **"Add Python to PATH"** |
| `ModuleNotFoundError` | Libraries not installed | Run `pip install textual requests stem` again |
| TUI shows "Tor not running" | Tor hasn't started yet | Complete Step 1 first and wait for 100% bootstrap |
| Firefox shows your real IP | Proxy not configured | Follow Step 5 to set up the proxy manually |
| IP not changing in Firefox | Old cached page | Use **Ctrl+Shift+R** (hard refresh), not just F5 |
| `ipRotator.py` not found | Wrong filename or folder | Check spelling — capital **R** — and that you're in the right folder |

---

## 💡 Tips

- A rotation interval of **30–60 seconds** is a good balance between speed and reliability
- The **Rotate Now** button is useful if a circuit feels slow — it skips the wait immediately
- You can run the tool for hours unattended — it will keep rotating on its own
- The log panel records every IP with a timestamp, useful for checking history

---

*Built with [Textual](https://textual.textualize.io/) · Powered by [Tor](https://www.torproject.org/)*
