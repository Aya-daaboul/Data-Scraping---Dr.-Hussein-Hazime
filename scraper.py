from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Chrome options for local execution (visible browser)
chrome_options = Options()
# chrome_options.add_argument('--headless')  # COMMENTED OUT to see the browser
chrome_options.add_argument("--start-maximized")  # Start browser maximized
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Automatic chromedriver installation and setup
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL to scrape
url = "https://scholar.google.com/citations?hl=en&user=ltu1CEYAAAAJ"

try:
    # Navigate to the page
    print("Loading page...")
    driver.get(url)
    time.sleep(5)  # Wait for page to load
    
    # Scrape basic profile information
    print("Extracting profile data...")
    name = driver.find_element(By.ID, "gsc_prf_in").text
    affiliation = driver.find_element(By.CLASS_NAME, "gsc_prf_ila").text if driver.find_elements(By.CLASS_NAME, "gsc_prf_ila") else ""
    total_citations = driver.find_element(By.ID, "gsc_rsb_st").find_elements(By.TAG_NAME, "td")[1].text
    h_index = driver.find_element(By.ID, "gsc_rsb_st").find_elements(By.TAG_NAME, "td")[3].text
    i10_index = driver.find_element(By.ID, "gsc_rsb_st").find_elements(By.TAG_NAME, "td")[5].text
    
    # Click the "Show More" button to load all publications
    print("Loading all publications...")
    while True:
        try:
            show_more = driver.find_element(By.ID, "gsc_bpf_more")
            if show_more.is_enabled():
                show_more.click()
                time.sleep(2)  # Reduced wait time
            else:
                break
        except Exception as e:
            print(f"Done loading publications: {str(e)}")
            break
    
    # Scrape all publications
    print("Extracting publications data...")
    publications = []
    pub_elements = driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
    
    for pub in pub_elements:
        try:
            title = pub.find_element(By.CLASS_NAME, "gsc_a_at").text
            authors = pub.find_element(By.CLASS_NAME, "gs_gray").text
            journal = pub.find_elements(By.CLASS_NAME, "gs_gray")[1].text
            year = pub.find_element(By.CLASS_NAME, "gsc_a_y").text if pub.find_elements(By.CLASS_NAME, "gsc_a_y") else ""
            citations = pub.find_element(By.CLASS_NAME, "gsc_a_c").text if pub.find_elements(By.CLASS_NAME, "gsc_a_c") else "0"
            
            publications.append({
                "Title": title,
                "Authors": authors,
                "Journal/Conference": journal,
                "Year": year,
                "Citations": citations
            })
        except Exception as e:
            print(f"Error processing publication: {str(e)}")
            continue
    
    # Create DataFrames
    profile_df = pd.DataFrame({
        "Name": [name],
        "Affiliation": [affiliation],
        "Total Citations": [total_citations],
        "h-index": [h_index],
        "i10-index": [i10_index]
    })
    
    publications_df = pd.DataFrame(publications)
    
    # Display results
    print("\nProfile Information:")
    print(profile_df)
    
    print("\nPublications (first 5):")
    print(publications_df.head())
    
    # Save results
    profile_df.to_csv('scholar_profile.csv', index=False)
    publications_df.to_csv('scholar_publications.csv', index=False)
    print("\nResults saved to scholar_profile.csv and scholar_publications.csv")
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    input("Press Enter to close the browser...")  # Keeps browser open for inspection
    driver.quit()