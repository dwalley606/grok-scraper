from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import time

def save_chats(chats, file='chats.json'):
    try:
        with open(file, 'r') as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    existing.extend(chats)
    with open(file, 'w') as f:
        json.dump(existing, f, indent=2)

def scrape_grok():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible Chromium
        page = browser.new_page()
        page.goto('https://grok.com/sign-in')  # Start at login

        print("Log in manually in Chromium, get to the chat page, then press Enter here...")
        input()  # Wait for you to log in

        print("Page URL:", page.url)
        print("Page content snippet:", page.content()[:1000])
        messages = page.query_selector_all('.message-bubble p')
        print("Found messages:", [msg.inner_text()[:50] + "..." for msg in messages])

        last_count = 0
        try:
            while True:
                messages = page.query_selector_all('.message-bubble p')
                if len(messages) > last_count:
                    new_chats = [
                        {'text': msg.inner_text(), 'timestamp': datetime.now().isoformat()}
                        for msg in messages[last_count:]
                    ]
                    save_chats(new_chats)
                    print(f"Saved {len(new_chats)} new messages to chats.json")
                    last_count = len(messages)
                time.sleep(2)
        except KeyboardInterrupt:
            print("Stopped by user—closing...")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_grok()