import json
import time
from tqdm import tqdm

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from mail_ru import LOGIN, PSWD


def find_and_send(by, arg: str, send_text: str):  # Находит элемент и вставляет текст
    element = wait.until(ec.element_to_be_clickable((by, arg)))
    element.send_keys(send_text)
    return element


def authorization():  # Авторизация
    find_and_send(By.XPATH, '//input[@name="username"]', LOGIN).submit()
    find_and_send(By.XPATH, '//input[@name="password"]', PSWD).submit()


# Получаем все ссылки на входящие письма в виде списка url
def get_all_url_incoming_email(element, set_url=None):
    if set_url is None:
        set_url = set()

    wait.until(ec.presence_of_element_located((By.XPATH, element)))  # ожидаем отображение всех входящих
    elements = driver.find_elements(By.XPATH, element)  # находим все входящие письма
    sub_list = [el.get_attribute('href') for el in elements]  # выдергиваем url

    if sub_list[-1] in set_url:  # Если ссылка уже есть в списке - заканчиваем парсинг
        return set_url
    else:
        set_url.update(sub_list)  # наполняем список уникальными ссылками на входящие письма
        elements[-1].send_keys(Keys.NULL)  # скроллинг списка
        time.sleep(0.2)
        return get_all_url_incoming_email(element, set_url)


# выдергиваем нужные данные из собранных ссылок
def get_data_from_email(db):
    data_list = []
    for url in tqdm(db):
        driver.get(url)
        WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.XPATH, "//h2[@class]")))
        dict_data_incoming_emails = {
            'url': url,
            'from': driver.find_element(By.XPATH, "//span[@class='letter-contact']").get_attribute('title'),
            'date': driver.find_element(By.XPATH, "//div[@class='letter__date']").text,
            'title': driver.find_element(By.XPATH, "//h2[@class]").text,
            'body': driver.find_element(By.XPATH, '//div[contains(@class, "body-content")]').text
        }
        data_list.append(dict_data_incoming_emails)
        time.sleep(1)
    return data_list


if __name__ == '__main__':

    URL = 'https://account.mail.ru/'

    options = Options()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')

    s = Service(r'C:\chromedriver\chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=options)
    # driver.maximize_window()  # разворачиваем браузер на весь экран

    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)
        authorization()  # Авторизация

        # собираем в data все url из входящей почты
        data = get_all_url_incoming_email("//a[contains(@class, 'js-letter-list-item')]")

        print(f'Собрано {len(data)} входящих писем.')  # Собрано 481 входящих писем.
        data = get_data_from_email(data)

        # Запись данных в файл
        with open('data_file.json', 'w') as json_file:
            json.dump(data, json_file)

        # Вывод на печать собранных данных
        df = pd.DataFrame(data)
        print(df.to_string(max_rows=10, max_colwidth=40, max_cols=8))

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
