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
from Utils import connectToDB, insertToDB, selectFromDB
from dateutil import parser
from currency_converter import CurrencyConverter

sem = threading.Semaphore()

class EbayScraper:
    def __init__(self, maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales, minPrice, maxPrice, pagesToSearch,
                 numPages, numThreads):
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
        self.ThreadNum = numThreads
        self.numPages = numPages  # מס' עמודים לחיפוש פר לינק
        self.pagesToSearch = pagesToSearch
        self.currentDateStr = datetime.now().__format__('%b-%d-%y')
        self.currentDate = datetime.now()
        self.currencyCheck = CurrencyConverter()
        self.createPagesLinks()

    def createPagesLinks(self):
        for link in self.pagesToSearch:
            for i in range(self.numPages):
                p = link + str(i + 1)
                print(p)
                r = self.connectionChecker(p, True)
                if r:
                    self.linkList.append(r)

    def startScraping(self):
        self.checkConditions()

    # Creates a thread for each 4 links we have
    def checkConditions(self):
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
                      'Seller_Link, Seller_FeedBacks, Prod_Name, Prod_Price, Prod_Shipping_Price, Run_Time, Search_Link, Ali_Price' \
                      ', Ali_Seller, In_My_Store_Or_Not, My_Salles, Link_In_My_Store)' \
                      'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
        for link in self.resultLinks:
            link.setRunTime(runTime)
            insertToDB(dataBaseCon=self.dataBaseCon, data=tuple(link.getLink()), insertQuery=insertQuery)
            link.getLinkDetails()
            print('--------------------')


        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     startTime = time.time()
        #     res = [executor.submit(self.threadFunction, page) for page in pagesLinksList]
        #     for res in concurrent.futures.as_completed(res):
        #         for link in res:
        #             self.resultLinks.append(link)
        #     # self.resultLinks = [item for sublist in self.resultLinks for item in sublist if item]
        #     endTime = time.time()
        #     runTime = str((endTime - startTime) / 60)
        #     print('#####  ' + runTime + '  ####')
        #     print('--------------------')
        #     insertQuery = 'INSERT INTO EbayData (Link, Sales_Total, Week_Sales, Check_Date, Seller_Name, ' \
        #                   'Seller_Link, Seller_FeedBacks, Prod_Name, Prod_Price, Prod_Shipping_Price, Run_Time, Prod_Img' \
        #                   ', Ali_Seller, In_My_Store_Or_Not, My_Salles, Link_In_My_Store)' \
        #                   'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
        #     selectQuery = 'SELECT [Link] FROM [Ebay].[dbo].[EbayData]'
        #     dbLinks = selectFromDB(dataBaseCon=self.dataBaseCon, selectQuery=selectQuery)
        #     for link in dbLinks:
        #         link = link[0]
        #
        #     for link in self.resultLinks:
        #         if not any(link.link in s for s in dbLinks):
        #             link.setRunTime(runTime)
        #             insertToDB(dataBaseCon=self.dataBaseCon, data=link.getLink(), insertQuery=insertQuery)
        #             print('INSERT')
        #         else:
        #             print('EXISTING')

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

    def threadFunction(self, links, threadID):
        resltLink = []
        for link in links:  # pages links
            resltLink = self.checkFeedBack(link.content)
            if len(resltLink) > 0:
                sem.acquire()
                for resLink in resltLink:
                    resLink.setSearchLink(link.url)
                    self.resultLinks.append(resLink)
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
                    return salses, self.checkLastWeekSales(link)
        return None
