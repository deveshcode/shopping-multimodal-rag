import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium with Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the page to scrape
url = 'https://www.nike.com/w/mens-clothing-6ymx6znik1'
driver.get(url)

# Scroll and wait for more content to load
scroll_pause_time = 2
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
