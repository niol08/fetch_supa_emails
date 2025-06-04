import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BATCH_SIZE = 50
OUTPUT_FILE = "emails.json"

def fetch_batch():
    response = supabase.table("emails").select("*").limit(BATCH_SIZE).execute()
    return response.data

def delete_batch(ids):
    for id in ids:
        supabase.table("emails").delete().eq("id", id).execute()

def save_emails(emails):

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_emails = json.load(f)
    else:
        all_emails = []

    all_emails.extend(emails)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_emails, f, ensure_ascii=False, indent=2)

def main():
    while True:
        batch = fetch_batch()
        if not batch:
            print("No more emails to process.")
            break
        emails = [row for row in batch]
        ids = [row["id"] for row in batch]
        print(f"Fetched {len(emails)} emails.")
        save_emails(emails)
        delete_batch(ids)
        print(f"Deleted {len(ids)} emails from Supabase.")

if __name__ == "__main__":
    main()