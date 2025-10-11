from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import os
from dotenv import load_dotenv


load_dotenv()  

# Constants
URL = os.getenv("URL")
OUTPUT_FILE = "app_names.json"  
SCROLL_PAUSE_TIME = 5  
SCRAPING_DURATION = 600 

def load_app_names():
    """Load previously scraped app names from the JSON file."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                data = json.load(f)
                app_names = set(data.get("app_names", []))
                print(f"[DEBUG] Loaded {len(app_names)} existing app names from {OUTPUT_FILE}.")
                return app_names
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode {OUTPUT_FILE}: {e}")
            return set()
    else:
        print("[DEBUG] No existing app names file found. Starting fresh.")
        return set()

def save_app_names(app_names):
    """Save the scraped app names to the JSON file."""
    print(f"[DEBUG] Saving {len(app_names)} app names to {OUTPUT_FILE}...")
    try:
       
        with open(OUTPUT_FILE, "w") as f:
            json.dump({"app_names": list(app_names)}, f, indent=4)
        print("[DEBUG] App names saved successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to save app names: {e}")

def scrape_app_names():
    """Scrape app names from the AppBrain website."""
    print("[DEBUG] Starting the scraping process...")

   
    app_names = load_app_names()

   
    driver = webdriver.Chrome()
    driver.get(URL)

    start_time = time.time()  

    try:
        
        last_height = driver.execute_script("return document.body.scrollHeight")

        while time.time() - start_time < SCRAPING_DURATION:
            print(f"[DEBUG] Scrolling...")

          
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)  

           
            app_elements = driver.find_elements(By.CSS_SELECTOR, "div.browse-app-large-title")
            for element in app_elements:
                app_name = element.text.strip()

                
                if app_name and app_name not in app_names:
                    app_names.add(app_name)
                    print(f"[DEBUG] Added app name: {app_name}")

                    
                    save_app_names(app_names)

           
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("[DEBUG] No new content loaded. Waiting for more content...")
                time.sleep(5) 
            last_height = new_height

    except Exception as e:
        print(f"[ERROR] An error occurred during scraping: {e}")
    finally:
        
        driver.quit()

    print(f"[DEBUG] Scraping completed. {len(app_names)} app names saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    scrape_app_names()