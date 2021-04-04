# link : https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=sunglasses&_sacat=0
from EbayScraper import EbayScraper

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maxFeedBack = 700  # מקסימום פידבקים
    minFeedBack = 10  # מינימום פידבקים
    minSales = 1  # מינימום מכירות
    maxSales = 4000 # מקסימום מכירות
    minWeekSales = 7  # מינימום מחירות לשבוע
    maxPrice = 1000 # מיון מחיר(מקסימום)
    minPrice = 0 #מיון מחיר(מינימום)
    ebayScraper = EbayScraper(maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales, minPrice, maxPrice)
    ebayScraper.startScraping()
    if len(ebayScraper.resultLinks) > 0:
        ebayScraper.resultLinks.sort(key=lambda x: x.weekSales, reverse=False)
        with open('C:/Users/rdone/Desktop/links.txt', 'a') as file:
            for link in ebayScraper.resultLinks:
                file.write(str(link.link) + '###' + str(link.weekSales) + '###' + str(ebayScraper.currentDate))
            print("COMPLETE")
            print("COMPLETE")









