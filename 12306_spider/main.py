# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class QiangPiao_Spider(object):
    def __init__(self):
        self.login_url = "https://kyfw.12306.cn/otn/login/init"
        self.init_url = "https://kyfw.12306.cn/otn/index/initMy12306"
        self.order_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        self.buy_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        self.driver = webdriver.Chrome(executable_path=r"E:\python_spider\chromedriver_win32\chromedriver.exe")


    def login(self):
        self.driver.get(self.login_url)
        WebDriverWait(driver=self.driver, timeout=1000).until(
            EC.url_to_be(self.init_url)
        )
        print("登陆成功")

    def get_ticket(self):
        self.driver.get(self.order_url)
        WebDriverWait(self.driver, timeout=1000).until(
            EC.text_to_be_present_in_element_value((By.ID,"fromStationText"), self.from_place)
        )

        WebDriverWait(self.driver, timeout=1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_place)
        )

        WebDriverWait(self.driver, timeout=1000).until(
            EC.text_to_be_present_in_element_value((By.NAME, "leftTicketDTO.train_date"), self.train_date)
        )

        WebDriverWait(self.driver, timeout=1000).until(
            EC.element_to_be_clickable((By.ID, "query_ticket"))
        )
        searchBtn = self.driver.find_elements_by_id("query_ticket")[0]
        searchBtn.click()

        WebDriverWait(self.driver, timeout=1000).until(
            EC.presence_of_element_located((By.XPATH, './/tbody[@id="queryLeftTable"]/tr'))
        )

        trs = self.driver.find_elements(By.XPATH, './/tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        for tr in trs:
            train_number = tr.find_element_by_class_name("number").text
            if train_number in self.train_nums:
                second_ticket = tr.find_element_by_xpath('//td[4]').text
                if second_ticket == "有" or second_ticket.isdigit:
                    order_btn = tr.find_element_by_class_name("btn72")
                    order_btn.click()
                    break

        WebDriverWait(self.driver, timeout=1000).until(
            EC.url_to_be(self.buy_url)
        )
        # self.driver.

    def detail_input(self):
        self.from_place = input("请输入出发地：")
        self.to_place = input("请输入目的地：")
        self.train_date = input("请输入乘车日期：")
        self.train_person = input("请输入乘客姓名（多个人可用英文逗号隔开）：").strip(",")
        self.train_nums = input("请输入欲乘坐车次（多个车次可用英文逗号隔开）：").strip(",")

    def run(self):
        self.detail_input()
        self.login()
        self.get_ticket()


if __name__ == '__main__':
    spider = QiangPiao_Spider()
    spider.run()
