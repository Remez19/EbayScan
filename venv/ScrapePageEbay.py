from bs4 import BeautifulSoup
import requests
import re
# pageLink + str(pageNumber)



class EbayScraper():

def checkFeedBack(webLink,maxFeedBack, minFeedBack, hotItemList):
    r = requests.get(webLink)
    content = r.text
    # print("Ran")
    soup = BeautifulSoup(content, features="html.parser")
    # Level 1
    feedBackNumList = []
    divList = []
    linkList = []
    for div in soup.find_all('div', attrs={'class': 's-item__wrapper clearfix'}):
        #print(div)
        a = div.find('a', attrs={'class': 's-item__link'})
        link = div.find('a').get('href')
        linkList.append(link)
    goodLinks = []
    for link in linkList:
        if getLinkdata(link,maxFeedBack,minFeedBack) is not None:
            goodLinks.append(link)
    for link in goodLinks:
        print(link)



def getLinkdata(link,maxFeedBack,minFeedBack):
    r = requests.get(link)
    content = r.text
    soup = BeautifulSoup(content, features="html.parser")

    for div in soup.find_all('div',attrs={'class': 'mbg vi-VR-margBtm3'}):
        score = div.find('span',attrs={'class': 'mbg-l'}).text
        score = [int(s) for s in re.findall(r'\b\d+\b', score)]
        score = score[0]
        if score > maxFeedBack:
            return None
        elif 10 <= score <= 600:
            return score
    return None