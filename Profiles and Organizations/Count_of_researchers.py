import pandas as pd

# Path to your CSV file
csv_path = r"C:\Users\user\Desktop\Auf Simplon\Google Scholar Scraping\Profiles and Organizations\Profiles_and_Links.csv"

# Read the CSV file
df = pd.read_csv(csv_path)

# Filter and count researchers by organization
orgs_to_check = ["Lebanese University", "American University of Beirut"]

print("👥 Researcher counts by organization:\n")

for org in orgs_to_check:
    count = df[df['organization'] == org].shape[0]
    print(f"🔹 {org}: {count} researchers")


#results
# 🔹 Lebanese University: 282 researchers
# 🔹 American University of Beirut: 873 researchers