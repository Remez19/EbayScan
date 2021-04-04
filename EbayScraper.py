from bs4 import BeautifulSoup
import requests
import time
import re
from Link import Link
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
import threading
from threading import Thread, Semaphore
import numpy as np
from Utils import connectToDB, insertToDB, selectFromDB
from dateutil import parser
from currency_converter import CurrencyConverter

sem = threading.Semaphore()


class EbayScraper:
    def __init__(self, maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales, minPrice, maxPrice):
        self.dataBaseCon = connectToDB('LAPTOP-VNSLHC31', 'Ebay')
        self.maxFeedBack = maxFeedBack
        self.minFeedBack = minFeedBack
        self.maxSales = maxSales
        self.minSales = minSales
        self.minWeekSales = minWeekSales
        self.minPrice = minPrice
        self.maxPrice = maxPrice
        self.linkList = []
        self.resultLinks = []
        self.ThreadNum = 10
        self.numPages = 1  # מס' עמודים לחיפוש פר לינק
        self.pagesToSearch = [
            'https://www.ebay.com/sch/i.html?_from=R40&_nkw=led&_sacat=0&LH_TitleDesc=0&LH_BIN=1&_pgn=']
        self.currentDateStr = datetime.now().__format__('%b-%d-%y')
        self.currentDate = datetime.now()
        self.currencyCheck = CurrencyConverter()
        userOperation = int(input("תלחץ 1 לחיפוש לפי דפים. תלחץ 2 לקובץ:"))
        while userOperation != 1 and userOperation != 2:
            self.ThreadNum = int(input("תלחץ 1 לחיפוש לפי דפים. תלחץ 2 לקובץ:"))
        if userOperation == 1:
            self.ThreadNum = int(input("הכנס מס' של חוטים:"))
            self.createPagesLinks()
        if userOperation == 2:
            self.ThreadNum = int(input("הכנס מס' של חוטים:"))
            with open("html.txt", 'r', encoding='utf8') as pagesLink:
                self.per_section(pagesLink, lambda line: line.startswith('<!DOCTYPE html>'))  # comment

    def createPagesLinks(self):
        for link in self.pagesToSearch:
            for i in range(self.numPages):
                l = link + str(i + 1)
                print(l)
                r = self.connectionChecker(l, True)
                if r:
                    self.linkList.append(r.content)

    def per_section(self, file, is_delimiter):
        ret = []
        flagStart = True
        page = ''
        for line in file:
            if is_delimiter(line) and flagStart is False:
                if ret:
                    flagStart = True
                    page = ''
                    for l in ret:
                        page = page + l + "" + '\n'
                    self.linkList.append(page)
                    ret = []
                    ret.append(line.rstrip())
            else:
                flagStart = False
                ret.append(line.rstrip())  # OR  ret.append(line)
        page = ''
        for l in ret:
            page = page + l + "" + '\n'
        self.linkList.append(page)

    def startScraping(self):
        self.checkConditions()

    # Creates a thread for each 4 links we have
    def checkConditions(self):
        # creating list that containd lists of pages -> [[1,2,3],[1,2,3],[1,2,3]]
        self.linkList = [page for page in self.linkList if page is not '\n']
        pagesLinksList = np.array_split(self.linkList, self.ThreadNum)
        # Using multi - threading
        Threads = []
        threadID = 0
        for page in pagesLinksList:
            threadID += 1
            Threads.append(Thread(target=self.threadFunction, args=(page, threadID)))
        startTime = time.time()
        for thread in Threads:
            thread.start()
        for thread in Threads:
            thread.join()
        endTime = time.time()
        runTime = str((endTime - startTime) / 60)
        print('#####  ' + runTime + '  ####')
        print('--------------------')
        insertQuery = 'INSERT INTO EbayData (Link, Sales_Total, Week_Sales, Check_Date, Seller_Name, ' \
                      'Seller_Link, Seller_FeedBacks, Prod_Name, Prod_Price, Prod_Shipping_Price, Run_Time, Prod_Img' \
                      ', Ali_Seller, In_My_Store_Or_Not, My_Salles, Link_In_My_Store)' \
                      'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
        selectQuery = 'SELECT [Link] FROM [Ebay].[dbo].[EbayData]'
        dbLinks = selectFromDB(dataBaseCon=self.dataBaseCon, selectQuery=selectQuery)
        for link in dbLinks:
            link = link[0]
        for link in self.resultLinks:
            if link not in dbLinks:
                link.setRunTime(runTime)
                insertToDB(dataBaseCon=self.dataBaseCon, data=link.getLink(), insertQuery=insertQuery)
            else:
                print('EXISTING')

    def checkFeedBack(self, html):
        linkLst = []
        prodName = str(html)
        prodName = prodName[prodName.find('<title>') + 7:prodName.find(' | ')]
        soup = BeautifulSoup(html, features="html.parser")
        for div in soup.find_all('div', class_="s-item__image"):
            link = div.find('a').get('href')
            link = self.getLinkdata(link, prodName)
            if link is not None:
                linkLst.append(link)
        return linkLst

    # מסורבל - להוציא לפונקציות
    def getLinkdata(self, link, prodName):
        r = self.connectionChecker(link)
        if r:
            soup = BeautifulSoup(r.content, features="html.parser")
            for div in soup.find_all('div', attrs={'class': 'mbg vi-VR-margBtm3'}):
                score = div.find('span', attrs={'class': 'mbg-l'}).text
                score = int(re.sub('[ ()'
                                   ']', '', score))
                if (int(self.minFeedBack) <= score <= int(self.maxFeedBack)):
                    result = self.CheckSalesNumber(soup)
                    if result:
                        sales, weekSales = result
                        if weekSales >= self.minWeekSales:
                            sellerLink = \
                                soup.find('div', attrs={'class': 'si-pd-a', 'style': 'overflow: hidden;'}).find('a')[
                                    'href']
                            sellerName = div.find('span', attrs={'class': 'mbg-nw'}).text
                            prodPrice = soup.find('span', attrs={'class': 'notranslate'}).text
                            currencyCode = prodPrice[:prodPrice.find(' ')]
                            if currencyCode == 'US':
                                currencyCode += 'D'
                            prodPrice = prodPrice.replace(',', '.')
                            prodPrice = float(re.sub('[^0-9.]', '', prodPrice))
                            try:
                                prodPrice = str(
                                    self.currencyCheck.convert(prodPrice, currencyCode, 'ILS'))
                                if self.minPrice <= float(prodPrice) <= self.maxPrice:
                                    prodShipping = soup.find('span', attrs={'class': 'notranslate sh-cst'})
                                    if prodShipping is not None:
                                        prodShipping = prodShipping.text
                                        prodShipping = prodShipping.replace(',', '.')
                                        prodShipping = float(re.sub('[^0-9.]', '', prodShipping))
                                        prodShipping = str(
                                            self.currencyCheck.convert(prodShipping, currencyCode, 'ILS'))
                                    else:
                                        prodShipping = 'FREE'
                                    return Link(link=link, totalSales=sales, weekSales=weekSales,
                                                currentDate=self.currentDateStr,
                                                sellerName=sellerName, sellerLink=sellerLink, feedBack=score,
                                                prodName=prodName,
                                                shippingCost=prodShipping,
                                                prodPrice=prodPrice)
                                else:
                                    return None
                            except Exception as e:
                                prodPrice = soup.find('span', attrs={'class': 'notranslate'}).text
                                prodShipping = soup.find('span', attrs={'class': 'notranslate sh-cst'})
                                if prodShipping is not None:
                                    prodShipping = prodShipping.text
                                    prodShipping = prodShipping.replace(',', '.')
                                else:
                                    prodShipping = 'FREE'
                                return Link(link=link, totalSales=sales, weekSales=weekSales,
                                            currentDate=self.currentDateStr,
                                            sellerName=sellerName, sellerLink=sellerLink, feedBack=score,
                                            prodName=prodName,
                                            shippingCost=prodShipping,
                                            prodPrice=prodPrice)
        return None

    def checkLastWeekSales(self, link):
        r = self.connectionChecker(link)
        if r:
            soup = BeautifulSoup(r.content, features="html.parser")
            sumWeekSales = 0
            try:
                for td in soup.find_all('td', attrs={'align': 'left', 'nowrap': False, 'class': 'contentValueFont'}):
                    prodDateSale = parser.parse(td.text, ignoretz=True)
                    if (self.currentDate - prodDateSale).days < 7:
                        sumWeekSales = sumWeekSales + 1
                    else:
                        break
            except Exception as e:
                print("Date Format Failure" + "td:     " + td.text)
                print(e)
            return sumWeekSales

    def connectionChecker(self, link, head=False):
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
            print(f"Status Code:{r.status_code}")
            return None

    def threadFunction(self, links, threadID):
        resltLink = []
        for link in links:  # pages links
            resltLink = self.checkFeedBack(link)
            if len(resltLink) > 0:
                sem.acquire()
                for link in resltLink:
                    print(link.link)
                    self.resultLinks.append(link)
                resltLink = []
                sem.release()

    def CheckSalesNumber(self, soup):
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
                    return (salses, self.checkLastWeekSales(link))
        return None
