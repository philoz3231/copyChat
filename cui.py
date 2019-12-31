from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from requests import get
import time
import datetime

url = "https://entertain.naver.com/tvBrand/8246663"

def open_browser(goalDate, f):
    driver = webdriver.Chrome("/Users/junho/Desktop/copyChat/chromedriver")
    driver.get(url)
    timeout = 5
    
    i = 2
    while(1):
        # start page
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_comment'))
            WebDriverWait(driver, timeout).until(element_present)

            page = BeautifulSoup(driver.page_source, "html.parser")
            text = page.find_all("li", class_="u_cbox_comment")
            for hit in text:
                title = hit.find("div", class_="u_cbox_text_wrap")
                datetime = hit.find("span", class_="u_cbox_date").attrs['data-value']
                datetime = datetime[:-5]
                if(goalDate > get_datetime(datetime)):
                    return
                title = title.text
                print(title + '\n' + datetime+ '\n')
                f.write(title + '\n' + datetime+ '\n')
                
            # find 5 pages
            j = i + 4
            while i < j:
                queryString = "//a[@class='u_cbox_page']/span[@class='u_cbox_num_page' and text()='{}']".format(i)
                driver.find_element_by_xpath(queryString).click()
                try:
                    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_comment'))
                    WebDriverWait(driver, timeout).until(element_present)

                    page = BeautifulSoup(driver.page_source, "html.parser")
                    text = page.find_all("li", class_="u_cbox_comment")
                    for hit in text:
                        title = hit.find("div", class_="u_cbox_text_wrap")
                        datetime = hit.find("span", class_="u_cbox_date").attrs['data-value']
                        datetime = datetime[:-5]
                        if(goalDate > get_datetime(datetime)):
                            return
                        title = title.text
                        print(title + '\n' + datetime+ '\n')
                        f.write(title + '\n' + datetime+ '\n')
                    i += 1
                except TimeoutException:
                    print("페이지 로딩에 실패했어요. 인터넷 연결을 확인해주세요")
            # click next button
            queryString = "//a[@class='u_cbox_next']/span[@class='u_cbox_cnt_page' and text()='{}']".format("다음")
            driver.find_element_by_xpath(queryString).click()
            i += 1
        except TimeoutException:
           print("페이지 로딩에 실패했어요. 인터넷 연결을 확인해주세요")
    
    driver.quit()

    return text

def get_datetime(datetimeString):
    month = datetimeString[5:7]
    day = datetimeString[8:10]
    hour = datetimeString[11:13]
    minute = datetimeString[14:16]
    cur_time = datetime.datetime(2019, int(month), int(day), int(hour), int(minute))
    return cur_time

def read_date():
    month = input("Enter month: ")
    day = input("Enter day: ")
    hour = input("Enter hour: ")
    minute = input("Enter minute: ")
    goalDate = datetime.datetime(2019, int(month), int(day), int(hour), int(minute))
    return goalDate

goalDate = read_date()
file = open('chat_res.txt', 'w')
open_browser(goalDate, file)
file.close()