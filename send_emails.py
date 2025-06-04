
import os
import json
import smtplib
import time
import random
from datetime import datetime, timedelta
from email.message import EmailMessage
from imaplib import IMAP4_SSL

# Constants
SENT_EMAILS_FILE = "sent.json" 
EMAIL_LIMIT_PER_ACCOUNT = 450   
TEST_EMAIL_INTERVAL = 20        
IMAP_SERVER = "imap.gmail.com"  


with open("credentials.json", "r") as f:
    ACCOUNTS = json.load(f)

def reset_email_count():
    """Reset the email count for each account if 24 hours have passed since the last reset."""
    print("[DEBUG] Checking if email counts need to be reset...")
    current_time = datetime.now()

    for account in ACCOUNTS:
       
        last_reset_str = account.get("last_reset")
        if last_reset_str:
           
            last_reset = datetime.fromisoformat(last_reset_str)
           
            if current_time - last_reset >= timedelta(hours=24):
                print(f"[DEBUG] Resetting email count for {account['email']}.")
                account["sent"] = 0
                account["last_reset"] = current_time.isoformat()
        else:
            
            print(f"[DEBUG] Initializing last_reset for {account['email']}.")
            account["sent"] = 0
            account["last_reset"] = current_time.isoformat()

    
    with open("credentials.json", "w") as f:
        json.dump(ACCOUNTS, f, indent=4)
    print("[DEBUG] Email counts reset successfully.")

def load_emails_from_json(json_file):
    """Load emails from a JSON file that is a list of objects with 'email' keys."""
    print(f"[DEBUG] Loading emails from {json_file}...")
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"[DEBUG] Loaded {len(data)} emails from {json_file}.")
                    return data
                elif isinstance(data, dict) and "emails" in data:
                    print(f"[DEBUG] Loaded {len(data['emails'])} emails from {json_file}.")
                    return data["emails"]
                else:
                    print(f"[ERROR] Unexpected JSON format in {json_file}.")
                    return []
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode JSON file {json_file}: {e}")
            return []
    else:
        print(f"[ERROR] JSON file {json_file} does not exist.")
        return []

def load_sent_emails():
    """Load already sent emails from the sent.json file."""
    print("[DEBUG] Loading sent emails...")
    if os.path.exists(SENT_EMAILS_FILE):
        try:
            with open(SENT_EMAILS_FILE, "r") as f:
                data = json.load(f)
                print(f"[DEBUG] Loaded {len(data.get('emails', []))} sent emails.")
                return set(data.get("emails", []))
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode sent.json: {e}")
            return set()
    else:
        print("[DEBUG] No sent.json file found. Starting fresh.")
        return set()

def save_sent_email(email):
    """Save a sent email to the sent.json file."""
    print(f"[DEBUG] Saving sent email: {email}")
    sent_emails = load_sent_emails()
    sent_emails.add(email.lower())  
    with open(SENT_EMAILS_FILE, "w") as f:
        json.dump({"emails": list(sent_emails)}, f, indent=4)
    print("[DEBUG] Sent email saved successfully.")

def get_available_account(is_test=False):
    """Get an available Gmail account that hasn't reached its daily limit."""
    for account in ACCOUNTS:
        if is_test and account.get("is_test"):
            return account
        if not is_test and account.get("sent", 0) < EMAIL_LIMIT_PER_ACCOUNT and not account.get("is_test"):
            return account
    return None

def update_credentials():
    """Update the sent count in credentials.json."""
    with open("credentials.json", "w") as f:
        json.dump(ACCOUNTS, f, indent=4)

def send_email(to_email, account):
    """Send an email using the specified Gmail account."""
    msg = EmailMessage()
    msg["Subject"] = "Partnership Proposal for Verified Google Play Console Developers"
    msg["From"] = account["email"]
    msg["To"] = to_email

    # Email Body
    email_body = """
Dear Developer,

I hope this message finds you well.

My name is Brianna, and I represent Dev-X Hub, a technology solutions company specializing in mobile app deployment and distribution. We are currently seeking to establish partnerships with verified Google Play Console account holders for the publication of fully compliant applications on the Play Store.

This collaboration offers a low-effort, passive income opportunity for console owners while ensuring adherence to all relevant Google Play policies and standards.

Partnership Overview:
• $30 compensation per published application
• Weekly payouts based on publishing volume
• Earnings potential of up to $350 per week (based on 10 successfully published apps)

All application projects undergo rigorous internal review and comply strictly with Google’s developer guidelines. As a partner, you are not required to develop or maintain any application—your role is limited to publishing pre-vetted apps through your developer account.

To proceed or request additional details, please reply with your WhatsApp or Telegram contact information.

Alternatively, you may reach us directly:
📲 WhatsApp: +1 (505) 642-4862

We appreciate your time and look forward to the opportunity to work together in a secure and compliant manner.

Best regards,
Brianna
Partnership Development Lead
Dev-X Hub 
    """
    msg.set_content(email_body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(account["email"], account["password"])
            smtp.send_message(msg)

        print(f"[DEBUG] Sent to: {to_email} using {account['email']}")
        account["sent"] = account.get("sent", 0) + 1
        save_sent_email(to_email)
        update_credentials()
    except Exception as e:
        print(f"[ERROR] Failed to send from {account['email']} to {to_email}: {e}")

def send_test_email(sender_account, test_email_address):
    """Send a test email from sender_account to test_email_address."""
    print("[DEBUG] Sending test email...")
    msg = EmailMessage()
    msg["Subject"] = "Test Email – Spam Check"
    msg["From"] = sender_account["email"]
    msg["To"] = test_email_address

    email_body = "This is a test email to check if emails are being spammed."
    msg.set_content(email_body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_account["email"], sender_account["password"])
            smtp.send_message(msg)
        print(f"[DEBUG] Test email sent from {sender_account['email']} to {test_email_address}")
    except Exception as e:
        print(f"[ERROR] Failed to send test email: {e}")

def check_spam_status(account):
    """Check if the test email is in the Spam folder."""
    print("[DEBUG] Checking spam status for test email...")
    try:
        with IMAP4_SSL(IMAP_SERVER) as imap:
            imap.login(account["email"], account["password"])

            
            imap.select("INBOX")
            status, messages = imap.search(None, 'ALL')
            if messages[0]:
                print("[DEBUG] Test email found in Inbox. Emails are not being spammed.")
                return False  
            imap.select('"[Gmail]/Spam"')  
            status, messages = imap.search(None, 'ALL')
            if messages[0]:
                print("[ALERT] Test email detected in Spam folder. Terminating process.")
                return True  

            print("[DEBUG] Test email not found in Spam folder. Emails are not being spammed.")
            return False 
    except Exception as e:
        print(f"[ERROR] Failed to check spam status: {e}")
        return False

def get_test_account():
    """Return the account marked as is_test=True."""
    for account in ACCOUNTS:
        if account.get("is_test"):
            return account
    return None

def main():
    """Main function to send emails."""
    
    reset_email_count()

    
    json_file = input("Enter the JSON file to load emails from (e.g., FEWDF.json): ").strip()
    collected_emails = load_emails_from_json(json_file)

    if not collected_emails:
        print("[DEBUG] No emails found in the specified JSON file.")
        return

    
    sent_emails = load_sent_emails()

    
    unique_emails = [
    email_entry["email"] for email_entry in collected_emails
    if email_entry["email"].lower() not in sent_emails
]

    if not unique_emails:
        print("[DEBUG] No new emails to send.")
        return

    print(f"[DEBUG] Found {len(unique_emails)} unique emails to send.")

        # Send emails
    test_account = get_test_account()
    if not test_account:
        print("[ERROR] No test account found in credentials.json (is_test: true).")
        return

    for i, email in enumerate(unique_emails, start=1):
        account = get_available_account()
        if not account:
            print("[DEBUG] All accounts have reached their daily limit.")
            break

        send_email(email, account)

        # Send a test email after every 20 emails
        if i % TEST_EMAIL_INTERVAL == 0:
            send_test_email(account, test_account["email"])
            if check_spam_status(test_account):
                print("[ALERT] Emails are being marked as spam. Please rephrase the email content.")
                break

       
        time.sleep(random.uniform(1, 3)) 

    print("[DEBUG] Finished sending emails.")

if __name__ == "__main__":
    main()
