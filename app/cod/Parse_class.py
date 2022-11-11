import datetime
import os.path
import random
import time
import enum
import multiprocessing as mp
import selenium
from selenium import webdriver
import fake_useragent
import requests as req
import loguru
from selenium.webdriver.common.by import By
from tqdm import tqdm

import json_main_page_validator
import json_validator

loguru.logger.add("log_parser_info.log", level="ERROR", encoding="utf-8")
loguru.logger.add("log_parser.log", level="INFO", encoding="utf-8")


class HeadlessStatus(enum.Enum):
    headless_on = 1
    headless_off = 0


class CreateUserAgent:
    def __init__(self):
        self.__user_agent_list = []
        self.__user_agent = fake_useragent.UserAgent()
        self.create_user_agent_list()

    def create_user_agent_list(self):
        self.__user_agent_list.append(self.__user_agent.chrome)
        self.__user_agent_list.append(self.__user_agent.firefox)
        self.__user_agent_list.append(self.__user_agent.ie)

    def get_user_agent(self, type: str):
        if self.__user_agent_list:
            match type:
                case "chrome":
                    return self.__user_agent_list[0]
                case "firefox":
                    return self.__user_agent_list[1]
                case "ie":
                    return self.__user_agent_list[2]
                case _:
                    return None

    def get_random_user_agent(self):
        if self.__user_agent_list:
            return random.choice(self.__user_agent_list)


class Parser:
    def __init(self):
        pass

    @staticmethod
    def create_driver(driver_path: str,
                      headless: HeadlessStatus = HeadlessStatus.headless_off) -> webdriver.Chrome | None:

        '''Cоздаёт драйвер selenium. На вход получает путь до драйвера Chrome и Headless_status.
        При коректных входных данных вовращает обект драйвера, иначе None.'''

        if isinstance(driver_path, str) and isinstance(headless, HeadlessStatus):
            options = webdriver.ChromeOptions()
            user_agent = CreateUserAgent()
            if headless == HeadlessStatus.headless_on:
                options.add_argument("--headless")
            options.add_argument("--disable-blink-features=automationcontrolled")
            options.add_argument(f"user-agent={user_agent.get_user_agent('chrome')}")
            driver = webdriver.Chrome(driver_path, chrome_options=options)
            return driver
        else:
            loguru.logger.error("Не коретные входные данные")
            return None

    @staticmethod
    def driver_close(driver: webdriver.Chrome):
        '''Закрывает драйвер. На вход получает объект драйвера, который надо закрыть.'''
        if driver:
            driver.quit()

    @staticmethod
    def find_json(raw_data: str, start, finish):
        x = raw_data.find(start)
        if x != -1:
            raw_data = raw_data[x + len(start):]
            x = raw_data.find("{")
            if x != -1:
                raw_data = raw_data[x:]
                x = raw_data.find(finish)
                if x != -1:
                    json = raw_data[:x]
                    return json

    @staticmethod
    def page_scroller(driver: webdriver.Chrome):
        col_href_start = 0
        check = 0
        while True:
            driver.execute_script("window.scrollBy(0,100000000);")
            col_href_finish = len(driver.find_elements(By.TAG_NAME, "a"))
            if col_href_start == col_href_finish:
                check += 1
                if check == 4:
                    break
            else:
                check = 0
            col_href_start = col_href_finish
            time.sleep(2)


class ParserZara(Parser):
    def __init__(self,
                 url="https://www.zara.com/tr/tr/kadin-ayakkabilar-l1251.html?v1=2113973",
                 driver_path="../../chromedriver.exe"):

        self.driver_path = driver_path
        self.url = url
        self.user_agent = CreateUserAgent()
        # self.lost_product = []

    def struct_create(self):
        if not os.path.exists("../data"):
            os.mkdir("../data")
        dir_name = datetime.datetime.now().strftime("%d.%m.%y_%H-%M-%S")
        os.mkdir(f"../data/{dir_name}")
        return dir_name

    def run(self):
        dir_name = self.struct_create()
        driver = self.create_driver(self.driver_path)
        top_bar_hrefs = self.get_top_bar_hrefs()
        # print(top_bar_hrefs)
        # exit(10)
        if top_bar_hrefs:
            for category_href in tqdm(top_bar_hrefs):
                os.mkdir(f"../data/{dir_name}/{category_href[0]}")
                driver.get(category_href[1])
                time.sleep(10)
                self.page_scroller(driver)
                time.sleep(2)
                product_hrefs = self.find_href_in_category(driver)
                product_list, lost_product_href = self.get_data_products(product_hrefs)
                # print(product_list)
                # print(lost_product_href)
                print(len(product_list))
                print(len(lost_product_href))

                # product_list, lost_product_href = self.get_data_products(lost_product_href)
                # print(product_list)
                # print(lost_product_href)
                # print(len(product_list))
                # print(len(lost_product_href))
                # break
        else:
            ...

    def get_top_bar_hrefs(self) -> list[str] | None:
        check = 0
        while check != 5:
            try:
                response = req.get(self.url, headers={"user-agent": self.user_agent.get_random_user_agent()},
                                   timeout=10)
                if response:
                    main_json = self.find_json(response.text, "window.zara.viewPayload", ";</script>")
                    top_bar_href_list = json_main_page_validator.top_bar_validator(main_json)
                    if top_bar_href_list:
                        top_bar_href_list = [(i.name,
                                              f"https://www.zara.com/tr/tr/{i.keyword}-l{i.seo_category_id}.html?v1={i.id}")
                                             for i in
                                             top_bar_href_list]
                        return top_bar_href_list[1:]
                else:
                    loguru.logger.info(f"Код запроса {response}. Url: {self.url}")
            except req.exceptions.ReadTimeout:
                loguru.logger.info(f"request timeout {self.url}")
            time.sleep(5)
        return None

    @staticmethod
    def find_href_in_category(driver: webdriver.Chrome) -> list | None:
        try:
            product_group = driver.find_element(By.CLASS_NAME, "product-groups")
            hrefs = product_group.find_elements(By.CLASS_NAME, "product-grid-product-info")
            hrefs = [i.find_element(By.TAG_NAME, "a").get_attribute("href") for i in hrefs]
            # print(hrefs)
            return hrefs

        except selenium.common.exceptions.NoSuchElementException:
            loguru.logger.error("Драйвер не нашёл элемент.")
            print("Драйвер не нашёл элемент.")
            return None

    def get_data_products(self, href_list) -> (list, list):
        if href_list:
            with mp.Manager() as m:
                product_list = m.list()
                lost_list = m.list()
                process_list = [(i, self.user_agent.get_user_agent("ie"), self.find_json, product_list, lost_list) for i
                                in href_list]
                with mp.Pool(mp.cpu_count() * 4) as pool:
                    pool.starmap(self.get_data_product_process, process_list)
                    pool.close()
                    pool.join()

                return list(product_list)[:], list(lost_list)[:]

        else:
            print("Список ссылок пуст")
            loguru.logger.error("href_list пуст")
            return None

    @staticmethod
    def get_data_product_process(url: str, user_agent: str, find_json, product_list: list, lost_href_list) -> None:
        try:
            response = req.get(url, headers={"user-agent": user_agent}, timeout=10)
            if response:
                json = response.text
                json = find_json(json, "window.zara.viewPayload", ";</script>")
                product = json_validator.vallidator(json)
                if product:
                    product_list.append(product)
                else:
                    print("Ошибка json")
                    lost_href_list.append(url)

            else:
                print("Не удачный запрос.")
                lost_href_list.append(url)

        except req.exceptions.ReadTimeout:
            print("timeout")
            loguru.logger.error("timeout")
            lost_href_list.append(url)

        # except:
        #     print("ошибка")


if __name__ == '__main__':
    x = ParserZara()
    x.run()
    # driver = x.create_driver("../../chromedriver.exe")
    # driver.get(
    #     "https://www.zara.com/tr/tr/kadin-ayakkabilar-gece-l1278.html?v1=2175486")
    #
    # time.sleep(3)
    #
    # # l = x.get_data_product_process(
    # #     "https://www.zara.com/tr/tr/parlak-detayli-topuklu-bilekte-bot-p12107010.html?v1=223692757&v2=2175486",
    # #     x.user_agent, ParserZara.find_json, lost_list)
    # # print(l)
    # # print(lost_list)
    #
    # x.page_scroller(driver)
    # href_list = x.find_href_in_category(driver)
    # y, yy = x.get_data_products(href_list[:10])
    # time.sleep(2)
    # driver.quit()
    # print(y)
    # print(yy)
    # x = Parser_Zara()
    # list_href = x.get_top_bar_hrefs()
    # print(list_href)

    pass
