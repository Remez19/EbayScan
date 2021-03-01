# link : https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=sunglasses&_sacat=0
from EbayScraper import EbayScraper


def checkX(x):
    x = x + 1
    print(x)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maxFeedBack = 600  # מקסימום פידבקים
    minFeedBack = 10  # מינימום פידבקים
    minSales = 50  # מינימום מכירות
    maxSales = 2000 # מקסימום מכירות
    minWeekSales = 7  # מינימום מחירות לשבוע
    ebayScraper = EbayScraper(maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales)
    ebayScraper.startScraping()
    # for listLink in ebayScraper.resultLinks:
    #     print(listLink)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
