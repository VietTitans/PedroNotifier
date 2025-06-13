from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
from email.mime.text import MIMEText
import re
import time
import json
import smtplib
import os

def load_data():
    # Add URL in the list below. Remember to add comma at the end of each URL
    url_list = [
        "https://search.pedro.org.au/advanced-search/results?abstract_with_title=&therapy=0&problem=0&body_part=VL01391&subdiscipline=0&topic=0&method=0&authors_association=&title=&source=&year_of_publication=&date_record_was_created=&nscore=&perpage=20&find=&find=Start+Search",
        "https://search.pedro.org.au/advanced-search/results?abstract_with_title=&therapy=0&problem=0&body_part=VL01394&subdiscipline=0&topic=0&method=0&authors_association=&title=&source=&year_of_publication=&date_record_was_created=&nscore=&perpage=20&find=&find=Start+Search"
    ]
    subscriber_list = [
        "mattnhudinh@gmail.com",
    ]
    body_part_map = {
        "VL01390": "Head or neck",
        "VL01391": "Upper arm, shoulder or shoulder girdle",
        "VL01392": "Forearm or elbow",
        "VL01393": "Hand or wrist",
        "VL01394": "Chest (cardiothoracic)",
        "VL01395": "Thoracic spine",
        "VL01396": "Lumbar spine, SIJ or pelvis",
        "VL01397": "Perineum or genito‑urinary system",
        "VL01398": "Thigh or hip",
        "VL01399": "Lower leg or knee",
        "VL01400": "Foot or ankle",
        "VL01401": "Whole body or no specific body part"
    }
    return url_list, subscriber_list, body_part_map

def add_subscriber(subscriber_list: list[str], new_email: str) -> None:
    if new_email not in subscriber_list:
        subscriber_list.append(new_email)
        print(f"✅ Added new subscriber: {new_email}")
    else:
        print(f"ℹ️ Subscriber {new_email} already in the list")
    
# def remove_subscriber(email: str, subscriber_list: list[str]):
# def add_tracking_url(url: str, url_list: list[str]):
# def remove_tracking_url(url: str, url_list: list[str]):

def fetch_record_count(url: str):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    count: int | None = None

    try:
        content_div = driver.find_element(By.ID, "search-content")
        text = content_div.text.strip()
        normalized_text = ' '.join(text.split())

        match = re.search(r'Found\s+([\d,]+)\s+records', normalized_text, re.IGNORECASE)
        if match:
            number_str = match.group(1).replace(",", "")
            count = int(number_str)
    except Exception as e:
        print("❌ Error finding the search-content element:", e)
    finally:
        driver.quit()

    return count

def load_previous_counts(filename: str) -> dict[str,int]:
    try: 
        with open(filename, "r") as f:
            return (json.load(f))
    except FileNotFoundError:
        return {}
    
def save_counts(counts: dict[str, int], filename: str) -> None:
    try:
        with open(filename, "w") as f:
            json.dump(counts, f, indent=2)
    except IOError as e:
         print(f"❌ Failed to save counts to '{filename}': {e}")

def get_body_part_label(url: str, body_part_map: dict[str, str]) -> str | None:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    body_part_code = params.get("body_part", [None])[0]
    if body_part_code is None:
        return None
    body_part_label = body_part_map.get(body_part_code)
    return body_part_label

def build_message(body_part:str, search_url:str, old_count:int, new_count:int):
    updated_count = old_count - new_count
    message_body = (
        f"🧠 PEDro update for: {body_part}\n"
        f"📈 Numbers of new records: {updated_count}\n"
        f"🔗 URL:\n{search_url}\n\n"
        f"*************************\n\n"
    )
    return message_body

def send_notification(subscriber_list:list[str], message_list:list[str]):
    sender = os.environ.get("EMAIL_SENDER")
    if sender is None:
        raise ValueError("Missing SENDER_EMAIL environment variable")
    app_password = os.environ.get("secrets.EMAIL_PASSWORD")
    if app_password is None:
        raise ValueError("Missing app_password environment variable")
    message = "".join(message_list)
    for subscriber in subscriber_list:
        msg = MIMEText(message)
        msg["Subject"] = "New PEDro Research Alerts"
        msg["From"] = sender
        msg["To"] = subscriber
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, subscriber, msg.as_string())

def main():
    url_list, subscriber_list, body_part_map = load_data()
    historical_counts = load_previous_counts("records_counts.json")
    latest_counts: dict[str, int] = {}
    message_builder: list[str] = []
    hasUpdates: bool = False

    for search_url in url_list:
        label = get_body_part_label(search_url, body_part_map)
        count = fetch_record_count(search_url)

        if label is None or count is None:
            continue
        
        latest_counts[search_url] = count
        previous_counts = historical_counts.get(search_url)

        if previous_counts is None:
            print(f"🔍 [{label}] Initial record count: {count}")
        elif count != previous_counts:
            print(f"📢 [{label}] Record count changed: {previous_counts} → {count}")
            hasUpdates = True
            message_builder.append(build_message(label, search_url, previous_counts, count))
        else:
            print(f"✅ [{label}] No change in record count ({count})")
            
    save_counts(latest_counts, "records_counts.json")

    if hasUpdates:
        send_notification(subscriber_list, message_builder)

if __name__ == "__main__":
    main()