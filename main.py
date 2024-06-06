import os
from flask import Flask, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import uuid
from pymongo import MongoClient
from datetime import datetime
import json
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='templates')

# MongoDB Atlas client
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['twitter_trends']
collection = db['trends']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script')
def run_script():
    # Unique ID for this run
    unique_id = str(uuid.uuid4())

    # Selenium setup
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')
    PROXY = f"http://proxy.scraperapi.com?api_key={SCRAPERAPI_KEY}&url="

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--proxy-server=%s' % PROXY)

    driver = webdriver.Chrome(options=options)
    trends = {}
    ip_address = None

    try:
        driver.get('https://x.com/i/flow/login')
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'))
        ).send_keys(os.getenv('TWITTER_USERNAME'))
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]'))
        ).click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'))
        ).send_keys(os.getenv('TWITTER_PASSWORD'))
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button'))
        ).click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Home") or contains(@aria-label, "home")]'))
        )
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//body/div[@id='react-root']/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[4]/div[1]/section[1]/div[1]/div[1]"))
        )

        for i in range(4, 8):
            trend_xpath = f"//body/div[@id='react-root']/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[4]/div[1]/section[1]/div[1]/div[1]/div[{i}]/div[1]/div[1]/div[1]/div[2]/span[1]"
            trend = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, trend_xpath))
            )
            trends[f'trend_{i-3}'] = trend.text

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get('https://httpbin.org/ip')
            ip_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'pre'))
            )
            ip_address = json.loads(ip_element.text)["origin"]
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    data = {
        'unique_id': unique_id,
        'trend_1': trends.get('trend_1', None),
        'trend_2': trends.get('trend_2', None),
        'trend_3': trends.get('trend_3', None),
        'trend_4': trends.get('trend_4', None),
        'date_time': datetime.now().isoformat(),
        'ip_address': ip_address
    }

    result = collection.insert_one(data)
    data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
