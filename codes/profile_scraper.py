import random
import time
import os
import pandas as pd
import sys  # Added for debugging

# Debug: Print loaded modules before Selenium import
print("\n=== BEFORE SELENIUM IMPORT ===")
print("Loaded modules:", list(sys.modules.keys()))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Debug: Print loaded modules after Selenium import
print("\n=== AFTER SELENIUM IMPORT ===")
print("Loaded modules:", list(sys.modules.keys()))

from webdriver_manager.chrome import ChromeDriverManager

# Debug: Print loaded modules after webdriver_manager import
print("\n=== AFTER WEBDRIVER_MANAGER IMPORT ===")
print("Loaded modules:", list(sys.modules.keys()))

# User agents list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

def get_driver():
    """Initialize Chrome driver with anti-detection settings"""
    print("\n=== INITIALIZING DRIVER ===")
    
    chrome_options = Options()
    
    # Basic headless options
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Anti-detection options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Disable images to speed up loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Initialize WebDriver
    print("Installing ChromeDriver...")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Modify navigator properties to prevent detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("Driver initialized successfully")
    return driver

def random_delay(min_sec=2, max_sec=5):
    """Random delay between actions to mimic human behavior"""
    delay = random.uniform(min_sec, max_sec)
    print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

def scrape_profile(driver, profile_url, researcher_id, researcher_name):
    """Scrape publications from a single profile"""
    print(f"\n=== SCRAPING PROFILE: {researcher_name} ===")
    print(f"Profile URL: {profile_url}")
    
    try:
        print("Navigating to profile page...")
        driver.get(profile_url)
        random_delay(3, 6)  # Initial page load delay
        
        # Click "Show more" until it's gone
        print("Checking for 'Show more' button...")
        click_count = 0
        while True:
            try:
                show_more = driver.find_element(By.ID, 'gsc_bpf_more')
                if not show_more.is_displayed():
                    print("'Show more' button not visible")
                    break
                print(f"Clicking 'Show more' (#{click_count + 1})...")
                show_more.click()
                click_count += 1
                random_delay(2, 4)  # Random delay between clicks
            except NoSuchElementException:
                print("No more 'Show more' button found")
                break
            except Exception as e:
                print(f"Error clicking 'Show more': {str(e)}")
                break

        print(f"Found {click_count} 'Show more' buttons")
        publications = []
        rows = driver.find_elements(By.CLASS_NAME, 'gsc_a_tr')
        print(f"Found {len(rows)} publication rows")

        for i, row_elem in enumerate(rows, 1):
            try:
                title_elem = row_elem.find_element(By.CLASS_NAME, 'gsc_a_at')
                title = title_elem.text
                link = title_elem.get_attribute('href')
            except Exception as e:
                print(f"Error getting title/link for row {i}: {str(e)}")
                title = ""
                link = ""

            try:
                cited_by = row_elem.find_element(By.CLASS_NAME, 'gsc_a_c').text
            except Exception as e:
                print(f"Error getting citations for row {i}: {str(e)}")
                cited_by = ""

            try:
                year = row_elem.find_element(By.CLASS_NAME, 'gsc_a_y').text
            except Exception as e:
                print(f"Error getting year for row {i}: {str(e)}")
                year = ""

            try:
                authors = row_elem.find_element(By.CLASS_NAME, 'gsc_a_at').find_element(By.XPATH, '../../td[2]').text
            except Exception as e:
                print(f"Error getting authors for row {i}: {str(e)}")
                authors = ""

            publications.append({
                'researcher_id': researcher_id,
                'researcher_name': researcher_name,
                'title': title,
                'link': link,
                'cited_by': cited_by,
                'year': year,
                'authors': authors
            })

            if i % 10 == 0:
                print(f"Processed {i} publications")

        print(f"Successfully scraped {len(publications)} publications")
        return publications

    except Exception as e:
        print(f"FATAL ERROR scraping profile {researcher_name}: {str(e)}")
        return None

def main():
    # Debug: Print environment info
    print("\n=== STARTING MAIN ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Initialize WebDriver
    print("\nInitializing WebDriver...")
    driver = get_driver()

    # Paths
    input_csv = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Organizations\Profiles_and_Links.csv"
    output_dir = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Publications"
    
    print("\n=== PATHS ===")
    print(f"Input CSV: {input_csv}")
    print(f"Output directory: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    print("Output directory created/verified")

    try:
        # Load profile links
        print("\nLoading input CSV...")
        df = pd.read_csv(input_csv).head(3)  # just the first 3 profiles
        print(f"Loaded {len(df)} profiles to process")
        print("Column names:", df.columns.tolist())

        for index, row in df.iterrows():
            print("\n" + "="*50)
            print(f"Processing profile {index + 1}/{len(df)}")
            
            researcher_id = row['id']
            researcher_name = row['name'].replace(' ', '_')
            profile_url = row['profile link']  # Note the space in column name
            
            print(f"Researcher ID: {researcher_id}")
            print(f"Researcher Name: {row['name']}")
            print(f"Profile URL: {profile_url}")

            publications = scrape_profile(driver, profile_url, researcher_id, row['name'])
            
            if publications:
                # Save to individual CSV
                filename = f"{researcher_name}_{researcher_id}.csv"
                csv_path = os.path.join(output_dir, filename)
                pd.DataFrame(publications).to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Saved {len(publications)} publications to {csv_path}")
            else:
                print("No publications were scraped for this profile")
            
            # Random delay between profiles
            if index < len(df) - 1:  # Don't delay after last profile
                print("Waiting before next profile...")
                random_delay(5, 10)

    except Exception as e:
        print(f"\n!!! CRITICAL ERROR IN MAIN: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close browser
        print("\nClosing browser...")
        driver.quit()
        print("Finished scraping all profiles.")

if __name__ == "__main__":
    print("=== SCRIPT START ===")
    main()
    print("=== SCRIPT END ===")