import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import csv
import urllib.request
import pymysql

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 如果需要无界面模式，可以添加这一行
driver = webdriver.Chrome(options=options)
driver.get("http://www.dangdang.com/")
driver.implicitly_wait(30)

keyWord = driver.find_element(By.XPATH, '//*[@id="key_S"]')
keyWord.send_keys("vue")

btn = driver.find_element(By.XPATH, '//*[@id="form_search_new"]/input[10]')
btn.click()

# 创建连接
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root',
                       db='mybook', charset='utf8')
# 创建游标
cursor = conn.cursor()

for i in range(5):
    dataLIst = driver.find_elements(By.CSS_SELECTOR, "#search_nature_rg li")
    for item in dataLIst:
        title = item.find_element(By.CSS_SELECTOR, "a").get_attribute("title")
        price = item.find_element(By.CSS_SELECTOR, ".search_now_price").text
        print(title)

        # cursor.executemany("INSERT INTO `dangdang` (`title`, `price`) VALUES (%s, %s)")
        cursor.executemany("insert into `dangdang`(`title`, `price`) values(%s,%s)", [(title, price)])
        conn.commit()

    # Move to the next page
    driver.find_element(By.CSS_SELECTOR, ".paging .next").click()
    # Wait for a short duration to ensure the new page is loaded
    time.sleep(1)
conn.close()
input("aaaaaaaaaaa")
