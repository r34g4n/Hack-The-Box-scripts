#!/usr/bin/python3


import re
import bs4
import requests
import hashlib


class NullEncodingStringError(Exception):
    pass

session = requests.session()

def prompt():
    
    potential_url = "http://docker.hackthebox.eu:32246/"
    print(f"default url is: {potential_url}")

    url = input('Enter a valid HTB url(Type C to use the default url): ')
    if url.upper() == 'C':
        url = potential_url
        print("default url was chosen...")
    if not url.__contains__('://'):
        url = "://" + url
    if not url.__contains__('http'):
        url = "http" + url

    print(f"testing server {url} ....")
    try:
        requests.get(url, timeout=10)
        return url
    except requests.ConnectionError:
        print(f"Connection Error occurred. Please try with a valid url or ip ....")
        return prompt()
    except requests.Timeout:
        print("connection was timed out. Give it another try....")
        return prompt()

url  = prompt()





def get_page(session, url):
    print(f"sending GET request to {url} ....")
    page = session.get(url)
    print(f"GET request to {url} succeeded with status code: {page.status_code} ....")
    return page

def search_htb_flag(text):
    print("searching for potential HTB flags....")
    htb_flag = re.search('HTB{.*}',text)
    return htb_flag

def scrap_encoding_strings(page_content):
    print(f"scrapping for potential key clue...")
    soup = bs4.BeautifulSoup(page_content, 'html.parser')
    return soup.find_all('h3')


def encrypt_to_md5(text, encoding='utf-8'):
    print(f"encoding {text} to md5...")
    result = hashlib.md5(text.encode(encoding)).hexdigest()
    print(f"encoded: {result} ....")
    return result




# print(htb_flag)

def orchestrator(url=url, response=False):
    if response:
        print(f"spinning up a quest instance through the last response received....")
        page_text = response.text
    else:
        page = get_page(session, url)
        page_text = page.text

    htb_flag = search_htb_flag(page_text)

    if not htb_flag:
        print(f"HTB flag was not found...moving to scrapping....")
        encoding_strings = scrap_encoding_strings(page_text)
        if encoding_strings:
            print(f'a clue was found....')
            string = list(encoding_strings)[0].get_text() # ti got lazy from here
            encoded_string = encrypt_to_md5(string)
            data = {'hash': encoded_string}
            print("sending out a POST request....")
            response = session.post(url=url, data=data)
            return orchestrator(url=url, response=response)
        else:
            return NullEncodingStringError("Something Strange happened...")
    else:
        print("SUCCESS: HTB key was found....")
        # print htb flag
        print('*-' * 20)
        print(htb_flag.group())
        print('*-' * 20)
        return htb_flag

flag = orchestrator(url)
