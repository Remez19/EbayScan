# link : https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=sunglasses&_sacat=0
from EbayScraper import EbayScraper
import easygui

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maxFeedBack = 700  # מקסימום פידבקים
    minFeedBack = 10  # מינימום פידבקים
    minSales = 60  # מינימום מכירות
    maxSales = 4000 # מקסימום מכירות
    minWeekSales = 7  # מינימום מחירות לשבוע
    ebayScraper = EbayScraper(maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales)
    ebayScraper.startScraping()
    if len(ebayScraper.resultLinks) > 0:
        savePath = easygui.filesavebox(filetypes='\\*.txt')
        with open(savePath, 'a') as file:
            i = 0
            for link in ebayScraper.resultLinks:
                i = i + 1
                file.write(str(i) + '.) ' + str(link) + '\n')
    else:
        print("לא נמצאו לינקים של מוצרים חמים!")



