# ELTA Courier Package Tracker

A Python script that monitors ELTA Courier (Greek postal service) packages and sends Telegram notifications when the status changes.

## Features

- ✅ Real-time tracking using ELTA's internal API
- ✅ Telegram notifications on status updates
- ✅ Runs on headless systems (no browser required)
- ✅ Works on Raspberry Pi
- ✅ Checks every hour (configurable)
- ✅ Persistent state across restarts

## Requirements

- Python 3.6+
- `requests` library
- `urllib3` library
- Telegram account

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/elta-tracker.git
cd elta-tracker

# Install dependencies
pip3 install requests urllib3
```

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Search for `@userinfobot` on Telegram
2. Send any message to it
3. Copy your **Chat ID** (a number like: `123456789`)

### 3. Configure the Script

Edit `elta_tracker.py` and update these lines:

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Paste your bot token
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"    # Paste your chat ID
TRACKING_NUMBER    = "CA123456789SI"         # Your ELTA tracking number
```

## Usage

### Run in Foreground

```bash
python3 elta_tracker.py
```

### Run in Background

Using `nohup`:
```bash
nohup python3 elta_tracker.py > tracker.log 2>&1 &
```

Using `screen`:
```bash
screen -S tracker
python3 elta_tracker.py
# Press Ctrl+A then D to detach
# To reattach: screen -r tracker
```

### Check Status

```bash
# View logs
tail -f tracker.log

# Check if running
ps aux | grep elta_tracker
```

### Stop the Tracker

```bash
pkill -f elta_tracker.py
```

## Configuration Options

You can customize the check interval in the script:

```python
CHECK_INTERVAL = 3600   # 3600 = 1 hour (default)
                        # 1800 = 30 minutes
                        # 600  = 10 minutes
```

## How It Works

1. Calls ELTA's internal `track.php` API (same endpoint their website uses)
2. Compares current status with last known status (stored in `~/.package_tracker_state.json`)
3. Sends Telegram notification when changes are detected
4. Repeats every hour

## Notifications

You'll receive Telegram messages for:
- **Startup** - Confirms tracking started
- **Initial status** - First check result
- **Status updates** - Whenever tracking information changes
- **Shutdown** - When tracker is stopped

## Troubleshooting

### No Telegram messages
- Verify bot token and chat ID are correct
- Make sure you've sent `/start` to your bot first
- Check that the bot token has the correct format

### "Could not fetch data" errors
- Check your internet connection
- The ELTA website might be temporarily down
- Try accessing https://www.elta-courier.gr in a browser

### SSL errors on Raspberry Pi
The script disables SSL verification for ELTA's API. If you want proper SSL:
```bash
sudo apt-get update
sudo apt-get install --reinstall ca-certificates
```

## Example Output

```
📦 ELTA Courier Package Tracker  (Direct ELTA API)
📍 Tracking : CA181603324SI
⏰ Interval : 3600s (1.0 h)
💾 State    : /home/user/.package_tracker_state.json
------------------------------------------------------------

[2026-02-18 15:30:00] Checking package status...
   Latest: Άφιξη σε - ΚΤΕΠ ΝΕΟΥ ΨΥΧΙΚΟΥ
✅ Initial status recorded
  📍 18-02-2026 15:22  Παραλήπτης επιθυμεί παράδοση αργότερα  [ΚΤΕΠ ΝΕΟΥ ΨΥΧΙΚΟΥ]
  📍 17-02-2026 14:36  Άφιξη σε  [ΚΤΕΠ ΝΕΟΥ ΨΥΧΙΚΟΥ]
  📍 26-01-2026 02:03  Αποστολή βρίσκεται σε στάδιο μεταφοράς  [Κ.Δ.Τ. ΑΘΗΝΑΣ-ΔΙΑΛΟΓΗ]
⏳ Next check in 1.0 h...
```

## License

MIT License - feel free to use and modify

## Contributing

Pull requests welcome! For major changes, please open an issue first.

## Disclaimer

This script uses ELTA's internal API endpoint. While it mimics how their own website works, use responsibly and don't abuse the API with excessive requests.
