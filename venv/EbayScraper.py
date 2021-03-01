from bs4 import BeautifulSoup
import requests
import time
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
import threading
from threading import Thread,Semaphore
import numpy as np
sem = threading.Semaphore()


class EbayScraper:
    def __init__(self, maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales):
        self.maxFeedBack = maxFeedBack
        self.minFeedBack = minFeedBack
        self.maxSales = maxSales
        self.minSales = minSales
        self.minWeekSales = minWeekSales
        self.linkList = []
        self.resultLinks = []
        with open("html.txt",'r',encoding='utf8') as pagesLink:
            self.per_section(pagesLink, lambda line: line.startswith('<!DOCTYPE html>'))  # comment


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
        linklst = []
        i = 0
        # creating list that containd lists of pages -> [[1,2,3],[1,2,3],[1,2,3]]
        self.linkList = [page for page in self.linkList if page is not '\n']
        pagesLinksList = np.array_split(self.linkList, 15)
        # Using multi - threading each thread gets 2 pages
        Threads = []
        for i in range(len(pagesLinksList)):
            name = 'Thread ' + str(i+1) + ':'
            Threads.append(Thread(target=self.threadFunction, args=(pagesLinksList[i], name)))
        startTime = time.time()
        for thread in Threads:
            thread.start()
        for thread in Threads:
            thread.join()
        endTime = time.time()
        print('#####  '+ str(endTime - startTime)+ '  ####')

        # Creating a file that contains all links of hot products
        if len(self.resultLinks) > 0:
            fileName = str(input('שם קובץ של מוצרים חמים:')) + '.txt'
            with open(fileName,'a') as file:
                i = 0
                for link in self.resultLinks:
                    i = i + 1
                    file.write(str(i) + '.) '+ link + '\n')
        else:
            print("לא נמצאו לינקים של מוצרים חמים!")



    def checkFeedBack(self,html):
        linkLst = []
        soup = BeautifulSoup(html, features="html.parser")
        for div in soup.find_all('div', class_= "s-item__image"):
            link = div.find('a').get('href')
            if self.getLinkdata(link):
                linkLst.append(link)
        return linkLst

    # Get feedback score and check him (minFeedBack,maxFeedBack)
    def getLinkdata(self,link):
        r = self.connectionChecker(link)
        soup = BeautifulSoup(r.content, features="html.parser")
        for div in soup.find_all('div', attrs={'class': 'mbg vi-VR-margBtm3'}):
            score = div.find('span', attrs={'class': 'mbg-l'}).text
            score = int(re.sub('[ ()'
                               ']', '', score))
            if (int(self.minFeedBack) <= score <= int(self.maxFeedBack)) and self.CheckBidStatuse(soup):
                return True
        return False



    def checkLastWeekSales(self,link):
        r = self.connectionChecker(link)
        soup = BeautifulSoup(r.content, features="html.parser")
        timeNow = datetime.now().__format__('%b-%d-%y %H:%M:%S')
        timeNow = datetime.strptime(timeNow, '%b-%d-%y %H:%M:%S')
        sumWeekSales = 0
        for td in soup.find_all('td', attrs={'align':'left', 'nowrap':False, 'class': 'contentValueFont'}):
            prodDateSale = td.text
            prodDateSale = re.sub(' PST', '', prodDateSale)
            prodDateSale = datetime.strptime(prodDateSale, '%b-%d-%y %H:%M:%S')
            if (timeNow - prodDateSale).days < 7:
                sumWeekSales = sumWeekSales + 1
                if sumWeekSales >= self.minWeekSales:
                    return True
            else:
                return False
        return False


    def connectionChecker(self,link):
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            return session.get(link)
        except requests.exceptions.ConnectionError:

            return None

    def threadFunction(self,links,name):
        resltLink = []
        for link in links:  # pages links
            resltLink = self.checkFeedBack(link)
            if len(resltLink) > 0:
                sem.acquire()
                for link in resltLink:
                    self.resultLinks.append(link)
                resltLink = []
                sem.release()







    def CheckBidStatuse(self, soup):
        for div in soup.find_all('div', attrs={'class': 'vi-quantity-wrapper'}):
             link = div.find('a', attrs={'class': 'vi-txt-underline'})
             if link is not None:
                 link = link.get('href')
             score = div.find('a')
             if score is not None:
                 score = score.text
                 score = float(re.sub(' sold','', score))
                 if self.maxSales > self.minSales and (self.minSales <= score <= self.maxSales) :
                     return self.checkLastWeekSales(link)
        return False