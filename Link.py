



class Link:
    def __init__(self, link, totalSales, weekSales,currentDate, sellerName, sellerLink, feedBack , prodName, shippingCost, prodPrice):
        self.link = link
        self.weekSales = weekSales
        self.totalSales = totalSales
        self.currentDate = currentDate
        self.sellerName = sellerName
        self.feedBack = feedBack
        self.sellerLink = sellerLink
        self.prodName = prodName
        if shippingCost == '':
            self.shippingCost = '0'
        else:
            self.shippingCost = shippingCost
        self.prodPrice = prodPrice
        self.runTime = None

        
    def getLink(self):
        return (self.link, str(self.totalSales), self.weekSales, self.currentDate, self.sellerName, self.sellerLink, self.feedBack, self.prodName, self.prodPrice, self.shippingCost, self.runTime, None, None, None, None, None)

    def setRunTime(self, runTime):
        self.runTime = runTime

    def getLinkDetails(self):
        print('Link: ' + self.link)
        print('Week Sales: ' + str(self.weekSales))
        print('Total Sales: ' + str(self.totalSales))
        print('Date: ' + self.currentDate)
        print('Seller Name: ' + self.sellerName)
        print('Seller Link: ' + self.sellerLink)
        print('FeedBack Number: ' + str(self.feedBack))
        print('Prod Name: ' + self.prodName)
        print('Shpping Cost: ' + str(self.shippingCost))
        print('Product Price: ' + str(self.prodPrice))
        print('Run Time: ' + self.runTime)






