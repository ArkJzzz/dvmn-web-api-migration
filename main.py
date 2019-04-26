#!usr/bin/python3

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'ArkJzzz (arkjzzz@gmail.com)'


import requests
import os
import sys
import argparse
from urllib.parse import urlparse
from dotenv import load_dotenv



def check_link(input_link, api_address, headers):
    '''
    [+] Функция проверяет, является ли ссылка сокращенной или нет.
    '''
    schemes = ('//', 'http://', 'https://')
    if not (input_link.startswith(schemes)):
        input_link = 'http://{input_link}'.format(input_link=input_link)

    parse_result = urlparse(input_link)

    link_to_check = '{api_address}/{netloc}/{path}'.format(
        api_address=api_address, 
        netloc=parse_result.netloc, 
        path=parse_result.path
    )

    response = requests.get(link_to_check, headers=headers)
    if response.ok:
        checked_link = response.json()['id']
    else:
        checked_link = input_link
    bitlink_flag = response.ok

    check_link_out = {'bitlink_flag': bitlink_flag, 'checked_link': checked_link}
    return check_link_out


def cut_link(api_address, headers, token, original_url):
    ''' 
    [+] Функция принимает на вход токен и ссылку для сокращения, делает запрос к API и возвращает сокращенную ссылку
    [+] сайт принимает и возвращает данные в json
    [+] вывод об ошибке и завершение программы, если введена неправильная ссылка
    '''
    payload = {'long_url': original_url}
    response = requests.get(original_url)
    response.raise_for_status()
    response = requests.post(api_address, headers=headers, json=payload)
    bitlink = response.json()['id']
    return bitlink


def count_clicks(api_address, headers, token, shortlink):
    '''
    [+] Функция, возвращающая количество переходов по ссылке
    [+] проверяет статус ответа
    '''
    summary_clicks_link = '{api_address}/{shortlink}/clicks/summary'.format(
        api_address=api_address, 
        shortlink=shortlink
    )
    response = requests.get(summary_clicks_link, headers=headers)
    response.raise_for_status()
    clicks = response.json()['total_clicks']
    return clicks


def create_parser():
    parser = argparse.ArgumentParser(description='''
        Программа принимает на вход ссылку.
        Если ссылка является не сокращенной, то возвращает сокращенную ссылку.
        Если ссылка является сокращенной, то возвращает количество переходов по ней.
        ''')
    parser.add_argument('link', nargs='+', help='Ссылка')
    
    return parser


def main():
    load_dotenv()

    api_address = 'https://api-ssl.bitly.com/v4/bitlinks'
    token = os.getenv("TOKEN")
    headers = {'Authorization': token}

    parser = create_parser()
    input_links = parser.parse_args(sys.argv)

    for input_link in input_links.link:
        check_link_out = check_link(input_link, api_address, headers)

        if check_link_out['bitlink_flag']:
            try: 
                clicks = count_clicks(api_address, headers, token, check_link_out['checked_link'])
            except requests.exceptions.RequestException as HttpError:
                print('Опаньки.. Что-то c Вашей ссылкой не то...: ', HttpError)  
            else:
                print(clicks)
        else:
            try:
                bitlink = cut_link(api_address, headers, token, check_link_out['checked_link'])
            except requests.exceptions.RequestException as HttpError:
                print('Опаньки.. Что-то c Вашей ссылкой не то...: ', HttpError)  
            else:
                print(bitlink)


if __name__ == "__main__":
    main()


