from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from time import sleep

# Initialize WebDriver
driver = webdriver.Chrome()

# Open Amazon website
driver.get('https://www.amazon.in')

# Search for smartphones under 10000
input_search = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
)
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "(//input[@type='submit'])[1]"))
)
input_search.send_keys("Smartphones under 10000")
sleep(1)
search_button.click()

# Wait for search results to load
product_class = 'a-size-medium a-color-base a-text-normal'

# Initialize empty list to store product names
products = []

# Loop to scrape multiple pages
for i in range(10):
    print('Scraping Page', i+1)
    product_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']"))
    )
    for p in product_elements:
        products.append(p.text)
    
    # Check if the next button is available and click it
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a"))
        )
        next_button.click()
    except:
        print('No more pages to scrape.')
        break
    
    # Wait for the next page to load
    sleep(2)

# Close the WebDriver
driver.quit()

# Create a DataFrame and save to CSV
df = pd.DataFrame(products, columns=['Product Name'])
df.to_csv('smartphones_under_10000.csv', index=False)





# videos = driver.find_elements_by_css_selector('.style-scope.ytd-rich-item-renderer')

# video_list=[]

# for video in videos:
#     title=video.find_element_by_xpath('.//*[@id="video-title"]').text
#     views=video.find_element_by_xpath('.//*[@id="metadata-line"]/span[1]').text
#     when=video.find_element_by_xpath('.//*[@id="metadata-line"]/span[2]').text
#     print(title,views,when)
#     vid_item={
#         'title':title,
#         'views':views,
#         'posted':when
#     }
#     video_list.append(vid_item)

# df=pd.DataFrame(video_list)
# print(df)