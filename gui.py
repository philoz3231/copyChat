import cmd, sys
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, 
QGridLayout, QLabel, QLineEdit, QTextEdit, QDesktopWidget,QDateTimeEdit)
from PyQt5.QtCore import QDateTime, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from requests import get
import time
import datetime

class Crawler(QThread):

    print_signal = pyqtSignal(str)

    def __init__(self,url, goalDate):
        QThread.__init__(self)
        self.url = url
        self.goalDate = goalDate

    def run(self):
        self.print_signal.emit("작업을 시작합니다")
        file = open('복사결과.txt', 'w', encoding='utf8')

        self.print_signal.emit("인터넷 연결 중")    
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(self.url)

        timeout = 5
        i = 2
        while(1):
            # start page
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_ico_page'))
                WebDriverWait(driver, timeout).until(element_present)

                page = BeautifulSoup((driver.page_source).encode('utf-8'), "html.parser")
                text = page.find_all("li", class_="u_cbox_comment")
                for hit in text:
                    title = hit.find("div", class_="u_cbox_text_wrap")
                    datetime = hit.find("span", class_="u_cbox_date").attrs['data-value']
                    datetime = datetime[:-5]
                    if(self.goalDate > self.get_datetime(datetime)):
                        return
                    title = title.text
                    self.print_signal.emit(title + '\n' + datetime+ '\n')
                    file.write(title + '\n' + datetime+ '\n')
                    
                # find 5 pages
                j = i + 4
                while i < j:
                    queryString = "//a[@class='u_cbox_page']/span[@class='u_cbox_num_page' and text()='{}']".format(i)
                    driver.find_element_by_xpath(queryString).click()
                    try:
                        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_ico_page'))
                        WebDriverWait(driver, timeout).until(element_present)

                        page = BeautifulSoup((driver.page_source).encode('utf-8'), "html.parser")
                        text = page.find_all("li", class_="u_cbox_comment")
                        for hit in text:
                            title = hit.find("div", class_="u_cbox_text_wrap")
                            datetime = hit.find("span", class_="u_cbox_date").attrs['data-value']
                            datetime = datetime[:-5]
                            if(self.goalDate > self.get_datetime(datetime)):
                                return
                            title = title.text
                            self.print_signal.emit(title + '\n' + datetime+ '\n')
                            file.write(title + '\n' + datetime+ '\n')
                        i += 1
                    except TimeoutException:
                        self.print_signal.emit("페이지 로딩에 실패했어요. 인터넷 연결을 확인해주세요")
                # click next button
                queryString = "//a[@class='u_cbox_next']/span[@class='u_cbox_ico_page']" 
                driver.find_element_by_xpath(queryString).click()
                try:
                    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_ico_page'))
                    WebDriverWait(driver, timeout).until(element_present)
                except TimeoutException:
                    self.print_signal.emit("페이지 로딩에 실패했어요. 인터넷 연결을 확인해주세요")

                i += 1
            except TimeoutException:
                self.print_signal.emit("페이지 로딩에 실패했어요. 인터넷 연결을 확인해주세요")
        
        driver.quit()
        
        file.close()
        
        return text

    def get_datetime(self, datetimeString):
        month = datetimeString[5:7]
        day = datetimeString[8:10]
        hour = datetimeString[11:13]
        minute = datetimeString[14:16]
        cur_time = datetime.datetime(2019, int(month), int(day), int(hour), int(minute))
        return cur_time

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setWindowTitle('CopyChatForTY')
        grid = QGridLayout()
        self.setLayout(grid)


        self.statusTextEdit = QTextEdit()
        grid.addWidget(self.statusTextEdit,0,0,-1,1)
        grid.addWidget(QLabel('드라마 URL'),0,1)
        self.urlLineEdit = QLineEdit()
        self.urlLineEdit.setText('https://entertain.naver.com/tvBrand/8246663')
        grid.addWidget(self.urlLineEdit,0,2)
        grid.addWidget(QLabel('검색할 시간'),1,1)

        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.setDateTimeRange(QDateTime(1900,1,1,00,00,00), QDateTime(2100,1,1,00,00,00))
        self.dateTimeEdit.setDisplayFormat('yyyy.MM.dd hh:mm:ss')
        grid.addWidget(self.dateTimeEdit,1,2)

        self.startButton = QPushButton('시작')
        self.startButton.clicked.connect(self.start_click)
        self.cancelButton = QPushButton('취소')
        self.cancelButton.clicked.connect(self.cancel_click)
        grid.addWidget(self.startButton,2,2)
        grid.addWidget(self.cancelButton,2,1)

        self.resize(900,500)
        self.center()
        self.show()

    def center(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
    
    def start_click(self):
        self.statusTextEdit.clear()

        url = self.urlLineEdit.text()
        time = self.dateTimeEdit.dateTime()
        time = time.toPyDateTime()
        self.crawler = Crawler(url, time)
        self.crawler.print_signal.connect(self.ui_print)
        self.crawler.finished.connect(self.finish_print)
        self.startButton.setEnabled(False)

        self.crawler.start()

    def cancel_click(self):
        self.crawler.terminate()
        self.statusTextEdit.clear()

    
    def ui_print(self, msg):
        self.statusTextEdit.append(msg)

    def finish_print(self):
        self.statusTextEdit.append("결과가 '복사결과.txt' 파일에 저장되었습니다")
        self.statusTextEdit.append("작업이 완료되었습니다")
        self.startButton.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    ex = MyApp()
    sys.exit(app.exec_())
