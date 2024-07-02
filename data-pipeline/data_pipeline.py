import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
# Set up Selenium with Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# Prompt the user to enter the URL
url = input("Please enter the URL of the page to scrape: ")
#url = 'https://www.nike.com/w/mens-clothing-6ymx6znik1'
driver.get(url)

# Scroll and wait for more content to load
scroll_pause_time = 15
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Wait to load the page
    time.sleep(scroll_pause_time)
    
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Get page content after scrolling
page_content = driver.page_source
driver.quit()

# Parse the HTML content
soup = BeautifulSoup(page_content, 'html.parser')

# Extract data
products = []

product_cards = soup.find_all('div', class_='product-card__body')
for card in product_cards:
    title = card.find('div', class_='product-card__title').get_text()
    details = card.find('div', class_='product-card__subtitle').get_text()
    image = card.find('img', class_='product-card__hero-image')['src']
    product_url = card.find('a', class_='product-card__link-overlay')['href']
    full_product_url = f"https://www.nike.com{product_url}"
    products.append({
        'Title': title,
        'Details': details,
        'Image URL': image,
        'Product URL': full_product_url
    })

# Store data in a DataFrame
df = pd.DataFrame(products)
print(df.head())

# Save data to CSV
df.to_csv('nike_mens_clothing.csv', index=False)

# Load the CSV file
df = pd.read_csv('nike_mens_clothing.csv')

# Initialize lists to store additional data
additional_info = []

# Define headers for HTTP requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Function to scrape additional data from product page
def scrape_product_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract desired information (e.g., product description, price)
        description_tag = soup.find('div', class_='description-preview')
        description = description_tag.get_text(strip=True) if description_tag else "N/A"

        price_tag = soup.find('div', class_='product-price')
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        return {
            'Description': description,
            'Price': price
        }
    else:
        return {
            'Description': "N/A",
            'Price': "N/A"
        }

# Loop through each product URL and scrape additional data
for index, row in df.iterrows():
    print(f"Scraping {index + 1}/{len(df)}: {row['Product URL']}")
    product_url = row['Product URL']
    product_url = product_url[20:]
    additional_data = scrape_product_page(product_url)
    additional_info.append(additional_data)
    time.sleep(1)  # Be polite and don't hammer the server

# Convert additional data to DataFrame
additional_df = pd.DataFrame(additional_info)

# Concatenate original DataFrame with additional data
combined_df = pd.concat([df, additional_df], axis=1)

# Save the updated DataFrame to a new CSV file
combined_df.to_csv('nike_mens_clothing_with_additional_data.csv', index=False)

# Display the first few rows of the updated DataFrame
print(combined_df.head())


print(len(combined_df))

