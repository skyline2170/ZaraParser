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
import csv
import Picture_class

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
        else:
            return None

    def struct_create(self):
        if not os.path.exists("../data"):
            os.mkdir("../data")
        dir_name = datetime.datetime.now().strftime("%d.%m.%y_%H-%M-%S")
        os.mkdir(f"../data/{dir_name}")
        return dir_name

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

    def run(self, headless=HeadlessStatus.headless_on):
        dir_name = self.struct_create()
        top_bar_hrefs = self.get_top_bar_hrefs()
        driver = self.create_driver(self.driver_path, headless=headless)
        if top_bar_hrefs:
            for category_href in tqdm(top_bar_hrefs):
                self.pars_category_page(category_href, driver)
        else:
            ...
        print("Конец")

    def run_2(self, headless=HeadlessStatus.headless_on, process_check=None, pipe_send=None,
              pipe_recv=None):
        dir_name = self.struct_create()
        top_bar_hrefs = self.get_top_bar_hrefs()
        driver = self.create_driver(self.driver_path, headless=headless)
        if top_bar_hrefs:
            if process_check:
                pipe_send.send(top_bar_hrefs)
                print("data_send")
                print("recv")
                print(pipe_recv.recv())
            else:
                print("запуск run_2 без процессов")
                for category_href in tqdm(top_bar_hrefs):
                    os.mkdir(f"../data/{dir_name}/{category_href[0]}")
                    print(category_href[0])
                    product_list, lost_list = self.pars_category_page(category_href, driver)
                    # print(product_list)
                    print(len(product_list))
                    if product_list:
                        for product in product_list:
                            print(product.name)
                            date = datetime.datetime.now().strftime('%d.%m.%y_%H-%M-%S')
                            if not os.path.exists(f"../data/{dir_name}/{category_href[0]}/img_{product.name}_{date}"):
                                os.mkdir(f"../data/{dir_name}/{category_href[0]}/img_{product.name}_{date}")
                            for i, img in enumerate(product.hrefs_imgs_list):
                                picture = Picture_class.Picture(img)
                                if picture.load_picture():
                                    picture.save_picture(
                                        f"../data/{dir_name}/{category_href[0]}/img_{product.name}_{date}/{i}.jpg")
                                else:
                                    print("картинка не скачана")
                        x = self.f1(product_list)
                        self.create_excel(x, f"../data/{dir_name}/{category_href[0]}/{category_href[0]}")
                        with open(f"../data/{dir_name}/{category_href[0]}/lost_href.txt", "w") as file:
                            file.writelines([i + "\n" for i in lost_list])
                    ##
                    # break
                    ##
                    time.sleep(120)

        else:
            print("Не найдены ссылки в на катеегории")
        print("Конец")

    @staticmethod
    def f1(product_list: list[json_validator.Product]):
        data_list = []
        for product in product_list:
            data_list.append(
                (product.name, product.description, product.price, product.brand, product.color_1,
                 product.color_hexCode,
                 str([j["size"] for j in product.size if j["availability"].lower() == "coming_soon"]),
                 str([j["size"] for j in product.size if j["availability"].lower() == "in_stock"]),
                 str([j["size"] for j in product.size if j["availability"].lower() == "out_of_stock"])
                 ))

            data_list[-1][1].replace("\n", "")
            data_list[-1][1].replace("\n\n", "")
        return data_list[:]

    @staticmethod
    def create_excel(list_data, path):
        with open(f"{path}.csv", "w", encoding="utf-8") as file:
            data_list = [("Name", "Description", "Price", "Brand", "Color", "Color hex cod", "Size comin soon",
                          "Size in stock", "Size out_of_stock")]
            data_list.extend(list_data)
            writer = csv.writer(file)
            writer.writerows(data_list)

    def pars_category_page(self, category_href: list, driver: webdriver.Chrome):
        print("gg")
        driver.get(category_href[1])
        self.page_scroller(driver)
        time.sleep(2)
        product_hrefs = self.find_href_in_category(driver)
        if product_hrefs:
            try_check = 0
            result_product_list = []
            result_lost_list = []
            while True:
                product_list, lost_product_href = self.get_data_products(product_hrefs)
                try_check += 1
                if len(lost_product_href) == 0 or try_check == 3:
                    result_product_list.extend(product_list[:])
                    result_lost_list.extend(lost_product_href[:])
                    break
                else:
                    print(f"Временные потери: {len(lost_product_href)}")
                    result_product_list.extend(product_list[:])
                    product_hrefs = lost_product_href[:]
                    result_lost_list.clear()
                    lost_product_href.clear()
            print("Товары:")
            print(len(result_product_list))
            print("Потеряно:")
            print(len(lost_product_href))
            return result_product_list[:], result_lost_list[:]
        else:
            print("Продукты не найдены на странице")
            return None, None

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

            # hrefs = product_group.find_elements(By.CLASS_NAME, "product-grid-product-info__product-header")
            # hrefs = [i.find_element(By.TAG_NAME, "a").get_attribute("href") for i in hrefs]
            hrefs = [i.get_attribute("href") for i in product_group.find_elements(By.TAG_NAME, "a")]
            print(hrefs)
            return hrefs

        except selenium.common.exceptions.NoSuchElementException:
            loguru.logger.error("Драйвер не нашёл элемент.")
            print(f"Драйвер не нашёл элемент на {driver.current_url}")
            return None

    def get_data_products(self, href_list) -> (list, list) | (None, None):
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
            return None, None

    @staticmethod
    def get_data_product_process(url: str, user_agent: str, find_json, product_list: list, lost_href_list) -> None:
        time.sleep(random.randint(1, 10))
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
    x.run_2(headless=HeadlessStatus.headless_off)
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
