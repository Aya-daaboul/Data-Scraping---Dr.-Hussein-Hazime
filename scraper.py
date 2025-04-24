from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import random

# Configuration
INPUT_CSV = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Organizations\Profiles_and_Links.csv"
OUTPUT_DIR = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Publications"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set up Chrome options
def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Disable for debugging
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Disable images to speed up loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def random_delay(min_sec=1, max_sec=3):
    """Random delay between actions"""
    time.sleep(random.uniform(min_sec, max_sec))

def scrape_profile(driver, profile_url, researcher_id, researcher_name):
    """Scrape publications from a single profile"""
    print(f"\nScraping publications for {researcher_name}...")
    
    try:
        driver.get(profile_url)
        random_delay(3, 5)  # Initial page load
        
        # Click "Show More" until all publications are loaded
        while True:
            try:
                show_more = driver.find_element(By.ID, "gsc_bpf_more")
                if show_more.is_enabled():
                    show_more.click()
                    random_delay(1, 2)  # Short delay between clicks
                else:
                    break
            except NoSuchElementException:
                break
            except Exception as e:
                print(f"Error clicking 'Show more': {str(e)}")
                break

        # Scrape all publications
        publications = []
        pub_elements = driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
        
        for pub in pub_elements:
            try:
                title_elem = pub.find_element(By.CLASS_NAME, "gsc_a_at")
                title = title_elem.text
                link = title_elem.get_attribute('href')
                authors = pub.find_element(By.CLASS_NAME, "gs_gray").text
                journal = pub.find_elements(By.CLASS_NAME, "gs_gray")[1].text
                year = pub.find_element(By.CLASS_NAME, "gsc_a_y").text if pub.find_elements(By.CLASS_NAME, "gsc_a_y") else ""
                citations = pub.find_element(By.CLASS_NAME, "gsc_a_c").text if pub.find_elements(By.CLASS_NAME, "gsc_a_c") else "0"
                
                publications.append({
                    'researcher_id': researcher_id,
                    'researcher_name': researcher_name,
                    'title': title,
                    'link': link,
                    'cited_by': citations,
                    'year': year,
                    'authors': authors,
                    'journal': journal
                })
            except Exception as e:
                print(f"Error processing publication: {str(e)}")
                continue
        
        return publications

    except Exception as e:
        print(f"Error scraping profile {researcher_name}: {str(e)}")
        return None

def main():
    # Initialize WebDriver
    print("Launching Chrome browser...")
    driver = get_driver()

    try:
        # Load profile links
        df = pd.read_csv(INPUT_CSV).head(3)  # Just first 3 for testing
        
        for index, row in df.iterrows():
            researcher_id = row['id']
            researcher_name = row['name'].replace(' ', '_')
            profile_url = row['profile link']
            
            publications = scrape_profile(driver, profile_url, researcher_id, row['name'])
            
            if publications:
                # Save to individual CSV
                filename = f"{researcher_name}_{researcher_id}.csv"
                csv_path = os.path.join(OUTPUT_DIR, filename)
                pd.DataFrame(publications).to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Saved {len(publications)} publications to {csv_path}")
            
            # Random delay between profiles
            if index < len(df) - 1:
                random_delay(3, 6)

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        driver.quit()
        print("Finished scraping all profiles.")

if __name__ == "__main__":
    main()