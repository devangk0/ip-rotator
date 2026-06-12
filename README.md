# IP Rotator
### Tor-based automatic IP rotation tool for Windows

Continuously cycles your public IP address through the Tor network on a timer you control. Clean GUI dashboard — no VPN, no subscriptions, no system-wide changes.

---

## What's Inside

```
D:\ipRotator\
├── rotator.py        ← main script
├── torrc             ← Tor configuration
├── tor\              ← Tor binaries (tor.exe lives here)
└── data\             ← Tor runtime data (auto-created)
```

---

## Requirements

- **Windows 10 or 11**
- **Python 3.8+** — [python.org](https://python.org) — check **"Add Python to PATH"** during install
- **Firefox Portable** — [portableapps.com/apps/internet/firefox_portable](https://portableapps.com/apps/internet/firefox_portable)

> Firefox Portable is a self-contained browser that doesn't affect your main browser or system settings. All proxy config stays inside it.

---

## One-Time Setup

### 1 — Install Python dependencies

```cmd
pip install stem requests pysocks
```

### 2 — Configure Firefox Portable (one time only)

1. Launch Firefox Portable
2. Click **☰** → **Settings** → scroll to bottom → **Network Settings** → **Settings…**
3. Select **Manual proxy configuration**
4. Fill in:
   - SOCKS Host: `127.0.0.1` — Port: `9050`
   - Select **SOCKS v5**
   - Check **"Proxy DNS when using SOCKS v5"**
5. Click **OK**

Done. Firefox Portable will always route through Tor when Tor is running.

---

## Running the Tool

You need **two terminals open** every time.

### Terminal 1 — Start Tor

```cmd
D:
cd D:\ipRotator\tor
tor.exe -f D:\ipRotator\torrc
```

Wait until you see:
```
Bootstrapped 100% (done): Done
```

Keep this window open. Closing it stops Tor.

### Terminal 2 — Start the rotator

```cmd
D:
cd D:\ipRotator
python rotator.py
```

The GUI opens. Set your interval and click **START ROTATING**.

---

## Verifying It Works

1. Open Firefox Portable
2. Go to `http://httpbin.org/ip`
3. After each rotation, press `Ctrl + Shift + R` — you'll see a new IP every time

---

## Dashboard

```
┌─────────────────────────────────────────────────┐
│               IP ROTATOR                        │
│          tor-based circuit rotation             │
│                                                 │
│  ● tor connected                                │
│                                                 │
│            current ip                          │
│        185.220.101.29                           │
│                                                 │
│  rotations: 6   interval: 10s   status: running │
│                                                 │
│  rotate every [10] seconds  (min 10)            │
│                                                 │
│  [         STOP          ]                      │
│                                                 │
│  ip history                                     │
│  20:40:12  185.220.101.6                        │
│  20:40:23  193.189.100.204                      │
│  20:40:27  80.94.92.92                          │
│  20:40:38  193.189.100.205                      │
└─────────────────────────────────────────────────┘
```

---

## Stopping Everything

1. Click **STOP** in the rotator GUI (or close it)
2. Press `Ctrl+C` in Terminal 1 to stop Tor
3. Close Firefox Portable

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `tor.exe` not recognized | Switch drive first: type `D:` then `cd D:\ipRotator\tor` |
| Stuck below 100% bootstrap | Check internet; temporarily disable firewall |
| GUI says "tor not running" | Complete Terminal 1 step first and wait for 100% |
| Browser shows real IP | Make sure Firefox Portable proxy settings are saved correctly |
| IP not changing in browser | Hard refresh: `Ctrl+Shift+R`, not just F5 |
| `ModuleNotFoundError` | Run `pip install stem requests pysocks` again |
| Python not recognized | Reinstall Python and check **"Add Python to PATH"** |

---

## Tips

- **10–30 seconds** is the sweet spot — faster rotations don't always give Tor enough time to build a stable circuit
- Each IP in the log is a real Tor exit node from a different country
- The tool runs unattended — set it and forget it
- Firefox Portable is completely separate from your main browser — no conflicts, no traces

---

*Powered by [Tor](https://www.torproject.org/) · Built with Python + tkinter*
