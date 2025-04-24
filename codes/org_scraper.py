from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

org_and_id = {
    "Lebanese University": "9671583371665794735",
    "American University of Beirut": "2315923684106503984"
}

# Paths
save_path = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Organizations"
os.makedirs(save_path, exist_ok=True)

print("🚀 Launching headless Chrome browser...")
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

df = pd.DataFrame(columns=["id", "name", "organization", "profile link", "affiliation", "majors"])

for org, org_id in org_and_id.items():
    print(f"\n🔍 Scraping researchers from {org}...")

    base_url = f"https://scholar.google.com/citations?view_op=view_org&org={org_id}&hl=en&oi=io"
    driver.get(base_url)
    time.sleep(4)

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        name_tags = soup.find_all("h3", class_="gs_ai_name")
        affil_tags = soup.find_all("div", class_="gs_ai_aff")
        major_tags = soup.find_all("div", class_="gs_ai_int")

        print(f"👤 Found {len(name_tags)} names")

        for name_tag, affil_tag, major_tag in zip(name_tags, affil_tags, major_tags):
            a_tag = name_tag.find('a')
            if a_tag:
                name = a_tag.text.strip()
                profile_link = "https://scholar.google.com" + a_tag['href']
                affiliation = affil_tag.text.strip() if affil_tag else "Not specified"
                major = major_tag.text.strip() if major_tag else "Not specified"
                researcher_id = a_tag['href'].split('user=')[1]
                df.loc[len(df)] = [researcher_id, name, org, profile_link, affiliation, major]
                print(f"   ✅ Added: {name} - {major}")

        # Handle pagination
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'gs_btnPR')
            if next_button.is_enabled():
                next_button.click()
                print("➡️  Moving to next page...")
                time.sleep(4)
            else:
                break
        except:
            print("🛑 No more pages.")
            break

# Save CSV
csv_path = os.path.join(save_path, "Profiles_and_Links.csv")
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n📁 All data saved to: {csv_path}")

driver.quit()
