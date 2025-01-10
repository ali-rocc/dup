import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load the CSV file
data_path = '/mnt/data/merged_health_1.csv'
data = pd.read_csv(data_path)

# Clean up URLs (remove trailing commas if any)
data['Link'] = data['Link'].str.rstrip(',')

# Check for duplicate business names
duplicates = data[data.duplicated(subset=['Business Name'], keep=False)]

# Process duplicate rows
for index, row in duplicates.iterrows():
    if pd.isna(row['Suburb']):  # Check if suburb is missing
        url = row['Link']
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Attempt to find suburb using the new selector
                suburb_element = soup.select_one('h2[style="float:left"]')
                if suburb_element:
                    suburb_text = suburb_element.text

                    # Extract suburb from the text (assumes specific format)
                    if 'in ' in suburb_text:
                        suburb = suburb_text.split('in ')[-1].strip()
                        data.loc[index, 'Suburb'] = suburb  # Update the DataFrame
                else:
                    print(f"Suburb element not found for URL: {url}")
            else:
                print(f"Failed to fetch URL {url}, status code: {response.status_code}")

        except Exception as e:
            print(f"Failed to process URL {url}: {e}")

# Save the updated DataFrame to a new CSV file
updated_data_path = '/mnt/data/updated_health_data.csv'
data.to_csv(updated_data_path, index=False)

print(f"Updated data saved to {updated_data_path}")
