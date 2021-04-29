# link : https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=sunglasses&_sacat=0
from EbayScraper import EbayScraper
import threading
from threading import Thread, Semaphore
from bs4 import BeautifulSoup
import requests
import time
import re
from Link import Link
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
import numpy as np
import concurrent.futures
import signal
from Utils import insertToDB, selectFromDB
from dateutil import parser
from currency_converter import CurrencyConverter


def CheckSalesNumber(soup):
    for div in soup.find_all('div', attrs={'class': 'vi-quantity-wrapper'}):
        link = div.find('a', attrs={'class': 'vi-txt-underline'})
        if link is not None:
            link = link.get('href')
        salses = div.find('a')
        if salses is not None:
            salses = salses.text
            salses = re.sub('[^0-9,]', '', salses)
            salses = int(re.sub(',', '', salses))
            if self.maxSales > self.minSales and (self.minSales <= salses <= self.maxSales):
                return salses, self.checkLastWeekSales(link)
    return None

def connectionChecker(link, head=False):
    r = None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if head:
            r = session.get(link, headers=headers, timeout=5)
            if r.status_code > 400:
                raise ValueError
        else:
            r = session.get(link)
            if r.status_code > 400:
                raise ValueError
        return r
    except Exception as e:
        print("Connection Failure")
        if r:
            print(f"Status Code:{r.status_code}")
        return None


def checkLastWeekSales(currentDate, link):
    r = connectionChecker(link)
    if r:
        soup = BeautifulSoup(r.content, features="html.parser")
        sumWeekSales = 0
        try:
            for td in soup.find_all('td', attrs={'align': 'left', 'nowrap': False, 'class': 'contentValueFont'}):
                prodDateSale = parser.parse(td.text, ignoretz=True)
                if (currentDate - prodDateSale).days < 7:
                    sumWeekSales = sumWeekSales + 1
                else:
                    break
        except Exception as e:
            print("Date Format Failure" + "td:     " + td.text)
            print(e)
        return sumWeekSales



# Press the green button in the gutter to run the script.
# https://offer.ebay.com/ws/eBayISAPI.dll?ViewBidsLogin&item=124403499626&rt=nc&_trksid=p2047675.l2564
if __name__ == '__main__':
    link = 'https://offer.ebay.com/ws/eBayISAPI.dll?ViewBidsLogin&item=313196393602&rt=nc&_trksid=p2047675.l2564'
    currentDate = datetime.now()
    print(checkLastWeekSales(currentDate, link))
