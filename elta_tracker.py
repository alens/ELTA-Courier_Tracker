#!/usr/bin/env python3
"""
ELTA Courier Package Tracker with Telegram Notifications
Directly calls the internal ELTA API - real-time data!
Works on headless Raspberry Pi without browser/display.
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============= CONFIGURATION =============
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Get your chat ID from @userinfobot on Telegram
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"

# Your ELTA tracking number (format: 2 letters + 9 digits + 2 letters)
TRACKING_NUMBER    = "CA123456789SI"

# Check interval in seconds (3600 = 1 hour)
CHECK_INTERVAL     = 3600

# File to store last known status
STATE_FILE         = Path.home() / ".package_tracker_state.json"
# =========================================

ELTA_API_URL = "https://www.elta-courier.gr/track.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "el-GR,el;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.elta-courier.gr",
    "Referer": "https://www.elta-courier.gr/search?br=" + TRACKING_NUMBER,
}


def send_telegram(message):
    """Send notification via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10,
            verify=False,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


def fetch_tracking_data():
    """Call ELTA's internal track.php API directly."""
    try:
        r = requests.post(
            ELTA_API_URL,
            headers=HEADERS,
            data={"number": TRACKING_NUMBER},
            timeout=15,
            verify=False,
        )
        r.raise_for_status()
        # Fix UTF-8 BOM that ELTA includes in response
        text = r.content.decode("utf-8-sig")
        return json.loads(text)
    except Exception as e:
        print(f"❌ ELTA API error: {e}")
        return None


def format_events(data):
    """Extract status and events from ELTA API response."""
    events = []
    latest_status = "Unknown"

    try:
        result = data["result"][TRACKING_NUMBER]["result"]
        if result:
            latest_status = result[0]["status"] + " - " + result[0]["place"]
            for ev in result:
                line = f"  📍 {ev['date']} {ev['time']}  {ev['status']}  [{ev['place']}]"
                events.append(line)
    except (KeyError, IndexError, TypeError) as e:
        print(f"⚠️  Could not parse events: {e}")
        print(f"   Raw data: {json.dumps(data)[:300]}")

    return latest_status, events


def content_hash(data):
    """Generate hash of data to detect changes."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def load_state():
    """Load last known state from file."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state):
    """Save current state to file."""
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def main():
    """Main tracking loop."""
    print("📦 ELTA Courier Package Tracker  (Direct ELTA API)")
    print(f"📍 Tracking : {TRACKING_NUMBER}")
    print(f"⏰ Interval : {CHECK_INTERVAL}s ({CHECK_INTERVAL/3600:.1f} h)")
    print(f"💾 State    : {STATE_FILE}")
    print("-" * 60)

    # Verify configuration
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("❌ ERROR: Please configure your Telegram credentials!")
        print("\nTo set up:")
        print("1. Message @BotFather on Telegram to create a bot and get your token")
        print("2. Message @userinfobot to get your Chat ID")
        print("3. Edit this script and add your credentials at the top")
        return

    if TRACKING_NUMBER == "CA123456789SI":
        print("⚠️  WARNING: Using example tracking number. Please update TRACKING_NUMBER.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    send_telegram(
        f"🚀 <b>Package Tracker Started</b>\n\n"
        f"📦 Tracking: <code>{TRACKING_NUMBER}</code>\n"
        f"⏰ Checking every {CHECK_INTERVAL/3600:.1f} hour(s)\n"
        f"🔗 <a href='https://www.elta-courier.gr/search?br={TRACKING_NUMBER}'>View on ELTA</a>"
    )

    last = load_state()

    while True:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{ts}] Checking package status...")

        data = fetch_tracking_data()

        if data is None:
            print("⚠️  Could not fetch data — will retry next cycle")
            time.sleep(CHECK_INTERVAL)
            continue

        h = content_hash(data)
        latest_status, events = format_events(data)
        events_text = "\n".join(events) if events else "  (no events)"

        print(f"   Latest: {latest_status}")

        if not last:
            print("✅ Initial status recorded")
            print(events_text)
            send_telegram(
                f"📦 <b>Initial Package Status</b>\n\n"
                f"Tracking: <code>{TRACKING_NUMBER}</code>\n"
                f"Status: <b>{latest_status}</b>\n\n"
                f"{events_text}\n\n"
                f"🔗 <a href='https://www.elta-courier.gr/search?br={TRACKING_NUMBER}'>View on ELTA</a>"
            )
        elif h != last.get("hash"):
            print("🔔 STATUS CHANGED!")
            print(events_text)
            send_telegram(
                f"🔔 <b>Package Status Updated!</b>\n\n"
                f"📦 Tracking: <code>{TRACKING_NUMBER}</code>\n"
                f"⏰ {ts}\n"
                f"Status: <b>{latest_status}</b>\n\n"
                f"{events_text}\n\n"
                f"🔗 <a href='https://www.elta-courier.gr/search?br={TRACKING_NUMBER}'>View on ELTA</a>"
            )
        else:
            print("✓ No changes detected")

        save_state({"hash": h, "last_check": ts, "status": latest_status})
        last = {"hash": h}

        print(f"⏳ Next check in {CHECK_INTERVAL/3600:.1f} h...")
        try:
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            break

    print("\n👋 Tracker stopped")
    send_telegram(f"🛑 <b>Tracker stopped</b>\nTracking for {TRACKING_NUMBER} ended.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
