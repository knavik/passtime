import os
import requests
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# --- API CONFIG ---
BASE_URL = "https://pass-og-id.politiet.no/qmaticwebbooking/rest/schedule"
PROFILE_URL = f"{BASE_URL}/appointmentProfiles/"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "nb-NO,nb;q=0.9,no;q=0.8,nn;q=0.7,en-US;q=0.6,en;q=0.5,fr;q=0.4,es;q=0.3,mr;q=0.2",
    "referer": "https://pass-og-id.politiet.no/timebestilling/index.html",
}

# --- Global config ---
DATE_FORMAT = "%Y-%m-%d"
CHECK_INTERVAL = 60 * 5  # check every 5 minutes
ALERTED_DATES = set()

# --- Load environment variables for notifications via gmail ---
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

EMAIL_ENABLED = all([EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_RECIPIENT])

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(subject, message):
    if not EMAIL_ENABLED:
        print("ℹ️ Email notifications are disabled (missing config).")
        return

    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_RECIPIENT

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_RECIPIENT, msg.as_string())

        print(f"📧 Email sent: {subject}")

    except Exception as e:
        print("❌ Error sending email:", e)


def choose_location_and_service():
    print("📍 Fetching locations and services...")
    response = requests.get(PROFILE_URL, headers=HEADERS)
    response.raise_for_status()
    profiles = response.json()

    # Step 1: Select location
    for i, p in enumerate(profiles, 1):
        print(f"{i}. {p['branchName']}")

    choice = int(input("\nVelg politistasjon (skriv nummer): ")) - 1
    branch = profiles[choice]
    branch_id = branch["branchPublicId"]

    print(f"\n👉 Du valgte: {branch['branchName']}")

    # Step 2: Select service
    services = []
    for group in branch["serviceGroups"]:
        services.extend(group["services"])

    for i, s in enumerate(services, 1):
        print(f"{i}. {s['name']}")

    choice = int(input("\nVelg tjeneste (skriv nummer): ")) - 1
    service = services[choice]
    service_id = service["publicId"]

    print(f"\n👉 Du valgte tjeneste: {service['name']}\n")

    # Build URL for fetching available dates
    url = f"{BASE_URL}/branches/{branch_id}/dates;servicePublicId={service_id};customSlotLength=15"
    return url


# Ask user for date range
def choose_date_range():
    start_str = input("From date (YYYY-MM-DD): ")
    end_str = input("To date (YYYY-MM-DD): ")

    start_date = datetime.strptime(start_str, DATE_FORMAT)
    end_date = datetime.strptime(end_str, DATE_FORMAT)

    print(f"\n📅 Monitoring range {start_date.date()} → {end_date.date()}\n")
    return start_date, end_date



def check_dates(url, start_date, end_date):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        dates = response.json()

        if not dates:
            print("No available dates from server.")
            return

        print(f"✅ Received {len(dates)} dates. First available: {dates[0]['date']}")

        found_new = False
        for entry in dates:
            date_str = entry["date"]
            date_obj = datetime.strptime(date_str, DATE_FORMAT)

            # Check if date is within user-defined range
            if start_date <= date_obj <= end_date:
                if date_str not in ALERTED_DATES:
                    ALERTED_DATES.add(date_str)
                    found_new = True
                    print(f"🚨 New appointment available: {date_str}")

                    send_email(
                        subject="🚨 New passport appointment found",
                        message=f"A new appointment date is available: {date_str}\n\nURL: {url}"
                    )

        if not found_new:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new dates in range.\n")

    except Exception as e:
        print("❌ Error while checking dates:", e)


def main():
    if EMAIL_ENABLED:
        send_email(
            subject="✅ Passport Checker Test Email",
            message="This is a test email to confirm your notification setup is working."
        )
    else:
        print("⚠️ Running without email notifications (no credentials found).")

    url = choose_location_and_service()

    start_date, end_date = choose_date_range()

    while True:
        check_dates(url, start_date, end_date)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()