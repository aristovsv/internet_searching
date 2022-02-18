from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd


def scraping_headhunter(search_keyword):
    vacancy_list = []
    params = {
        'text': search_keyword,
        'search_field': 'name',
        'items_on_page': '100',
        'page': ''
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82 Safari/537.36 '
    }
    link = 'https://hh.ru/search/vacancy'
    html = requests.get(link, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')
        pagination = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not pagination:
            last_page = 1
        else:
            last_page = int(pagination.find_all('a', {'class': 'bloko-button'})[-2].getText())

    for page in range(0, last_page):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)
        if html.ok:
            parsed_html = bs(html.text, 'html.parser')
            vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                .find_all('div', {'class': 'vacancy-serp-item'})
            for item in vacancy_items:
                vacancy_list.append(parse_item_headhunter(item))

    return vacancy_list


def parse_item_headhunter(item):
    vacancy_data = {}

    vacancy_title = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText().replace(u'\xa0', u' ')
    vacancy_data['vacancy_title'] = vacancy_title

    company_name = item.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).find('a')
    if company_name:
        company_name = company_name.getText()
    else:
        company_name = None
    vacancy_data['company_name'] = company_name

    city = item.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText().split(', ')[0]
    vacancy_data['city'] = city

    salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        data_sal = salary.getText()
        salary = re.sub(r' ', '', data_sal).replace(' –', '')
        salary = re.split(r'\s|-', salary)
        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
        else:
            salary_min = int(salary[0])
            salary_max = int(salary[1])
        salary_currency = salary[2]
    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['salary_currency'] = salary_currency

    vacancy_link = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
    vacancy_link = re.split(r'\?', vacancy_link)[0]
    vacancy_data['vacancy_link'] = vacancy_link

    vacancy_data['site'] = 'www.hh.ru'

    return vacancy_data


def scraping_superjob(search_keyword):
    vacancy_list = []
    params = {
        'keywords': search_keyword,
        'page': ''
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82 Safari/537.36 '
    }
    link = 'https://russia.superjob.ru/vacancy/search/'
    html = requests.get(link, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')
        pagination = parsed_html.find('a', {'class': 'f-test-button-1'})
        if not pagination:
            last_page = 1
        else:
            pagination = pagination.findParent()
            last_page = int(pagination.find_all('a')[-2].getText())

    for page in range(1, last_page + 1):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)
        if html.ok:
            parsed_html = bs(html.text, 'html.parser')
            vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})
            for item in vacancy_items:
                vacancy_list.append(parse_item_superjob(item))

    return vacancy_list


def parse_item_superjob(item):
    vacancy_data = {}

    vacancy_title = item.find_all('a')
    if vacancy_title:
        vacancy_title = vacancy_title[0].getText()
    else:
        vacancy_title = 'Not found'
    vacancy_data['vacancy_title'] = vacancy_title

    company_name = item.find('span', {'class': 'f-test-text-vacancy-item-company-name'})
    if not company_name:
        company_name = 'Not founded'
    else:
        company_name = company_name.getText()
    vacancy_data['company_name'] = company_name

    company_location = item.find('span', {'class': 'f-test-text-company-item-location'}).getText()
    company_location = re.split(',', re.split('•', company_location)[1])[0]
    vacancy_data['city'] = company_location

    salary = item.find('span', {'class': 'f-test-text-company-item-salary'}).findChildren()
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    elif salary[0].getText() == 'По договорённости':
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        string_line = item.find('span', {'class': 'f-test-text-company-item-salary'}).getText()
        salary = re.split(r'\s|-', string_line)
        if salary[0] == 'до':
            salary_min = None
            salary_currency = re.split('/', salary.pop(-1))[0]
            salary.pop(0)
            salary_max = ''.join(salary)
        elif salary[0] == 'от':
            salary_max = None
            salary_currency = re.split('/', salary.pop(-1))[0]
            salary.pop(0)
            salary_min = ''.join(salary)
        elif '–' in salary:
            salary = re.sub(r' ', '', string_line).replace(' –', '')
            salary = re.split(r'\s|-', salary)
            salary_currency = re.split('/', salary.pop(-1))[0]
            list_salary = re.split(r'—', ''.join(salary))
            salary_min = int(list_salary[0])
            salary_max = int(list_salary[1])
        else:
            salary_currency = re.split('/', salary.pop(-1))[0]
            salary_max = None
            try:
                salary_min = int(re.split(r'—', ''.join(salary))[0])
            except ValueError:
                salary_min = ' '.join(salary) + ' ' + salary_currency
                salary_currency = None
    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['salary_currency'] = salary_currency

    vacancy_link = item.find_all('a')
    if vacancy_link:
        vacancy_link = vacancy_link[0]['href']
        vacancy_data['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'
    else:
        vacancy_data['vacancy_link'] = 'Not found'

    vacancy_data['site'] = 'www.superjob.ru'

    return vacancy_data


def scraping_vacancy(search_keyword):
    vacancy_date = []
    vacancy_date.extend(scraping_headhunter(search_keyword))
    vacancy_date.extend(scraping_superjob(search_keyword))
    out_df = pd.DataFrame(vacancy_date)
    return out_df


search_keyword = input('Input keyword for search vacancy: ')
df = scraping_vacancy(search_keyword)
filename = f'parsed/{search_keyword}.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')
df.to_excel(writer, sheet_name=search_keyword, index=False, encoding='utf-8')

for column in df:
    column_width = max(df[column].astype(str).map(len).max(), len(column))
    if column_width > 70:
        column_width = 70
    col_idx = df.columns.get_loc(column)
    writer.sheets[search_keyword].set_column(col_idx, col_idx, column_width)
writer.save()