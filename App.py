from Views.MainWin import Ui_MainWindow
from Utils import connectToDB, selectFromDB
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from EbayScraper import EbayScraper
import threading
from threading import Thread, Semaphore


class MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, RunConfig, dataBaseCon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.scanEbay_btn.clicked.connect(self.scanEbayFunc)
        self.runOptions = None
        self.dataBaseCon = dataBaseCon
        self.RunConfig = RunConfig[0]

    def scanEbayFunc(self):
        if not self.runOptions:
            self.runOptions = qtw.QFormLayout()
            self.runOptions.setVerticalSpacing(10)
            self.runOptions.setContentsMargins(300, 10, 0, 0)
            label = qtw.QLabel()
            label.setStyleSheet(" color: white;\n"
                                "font: bold 25px;\n"
                                "text-decoration: underline;")
            label.setText("Run Configuration")
            self.runOptions.addRow(label)

            # Max FeedBack
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Max Feedback:")
            self.maxFeedBackInput = qtw.QLineEdit()
            print(self.RunConfig)
            self.maxFeedBackInput.setText(self.RunConfig[0])
            self.maxFeedBackInput.setMaximumWidth(300)
            self.maxFeedBackInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.maxFeedBackInput)

            # Min FeedBack
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Min Feedback:")
            self.minFeedBackInput = qtw.QLineEdit()
            self.minFeedBackInput.setText(self.RunConfig[1])
            self.minFeedBackInput.setMaximumWidth(300)
            self.minFeedBackInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.minFeedBackInput)

            # Min Sales
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Min Sales:")
            self.minSalesInput = qtw.QLineEdit()
            self.minSalesInput.setText(self.RunConfig[2])
            self.minSalesInput.setMaximumWidth(300)
            self.minSalesInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.minSalesInput)

            # Max Sales
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Max Sales:")
            self.maxSalesInput = qtw.QLineEdit()
            self.maxSalesInput.setText(self.RunConfig[3])
            self.maxSalesInput.setMaximumWidth(300)
            self.maxSalesInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.maxSalesInput)

            # Min Week Sales
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Min Week Sales:")
            self.minWeekSalesInput = qtw.QLineEdit()
            self.minWeekSalesInput.setText(self.RunConfig[4])
            self.minWeekSalesInput.setMaximumWidth(300)
            self.minWeekSalesInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.minWeekSalesInput)

            # Min Price
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Min Price:")
            self.minPriceInput = qtw.QLineEdit()
            self.minPriceInput.setText(self.RunConfig[5])
            self.minPriceInput.setMaximumWidth(300)
            self.minPriceInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.minPriceInput)

            # Max Price
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Max Price:")
            self.maxPriceInput = qtw.QLineEdit()
            self.maxPriceInput.setText(self.RunConfig[6])
            self.maxPriceInput.setMaximumWidth(300)
            self.maxPriceInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.maxPriceInput)

            # number of pages per link
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Number Of Pages:")
            self.numPagesInput = qtw.QLineEdit()
            self.numPagesInput.setText(self.RunConfig[7])
            self.numPagesInput.setMaximumWidth(300)
            self.numPagesInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.numPagesInput)

            # number of threads
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Number Of Threads:")
            self.numThreadInput = qtw.QLineEdit()
            self.numThreadInput.setText(self.RunConfig[8])
            self.numThreadInput.setMaximumWidth(300)
            self.numThreadInput.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runOptions.addRow(label, self.numThreadInput)

            # Link List
            label = qtw.QLabel()
            label.setStyleSheet(" color: rgb(85, 255, 255)")
            label.setText("Links:")
            self.runLinkList = qtw.QTextEdit()
            self.runLinkList.setText(self.RunConfig[9])
            self.runLinkList.setStyleSheet("background-color: rgb(208, 208, 208)")
            self.runLinkList.setMaximumWidth(600)
            self.runOptions.addRow(label, self.runLinkList)

            # Run btn
            button = qtw.QPushButton()
            button.setText("Start")
            button.setStyleSheet("QPushButton{\n"
                                 "    color: white;\n"
                                 "    background-color: rgb(77, 77, 77);\n"
                                 "    border-style: outset;\n"
                                 "    border-width: 2px;\n"
                                 "    border-radius: 10px;\n"
                                 "    text-color: white;\n"
                                 "    border-color: rgb(85, 255, 255);\n"
                                 "    font: bold 30px;\n"
                                 "    padding: 6px;\n"
                                 " }QPushButton:hover {\n"
                                 "      background-color: rgb(148, 148, 148);\n"
                                 " }")
            button.setMaximumWidth(510)
            button.clicked.connect(self.runNarkis)
            self.runOptions.addRow(button)
            self.dataWind.addLayout(self.runOptions)


    def runNarkis(self):
        # Get the input fron the user !
        try:
            maxFeedBack = int(self.maxFeedBackInput.text())
            minFeedBack = int(self.minFeedBackInput.text())
            minSales = int(self.minSalesInput.text())
            maxSales = int(self.maxSalesInput.text())
            minWeekSales = int(self.minWeekSalesInput.text())
            maxPrice = int(self.maxPriceInput.text())
            minPrice = int(self.minPriceInput.text())
            pagesToSearch = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=LED+fountain&_sacat=0&LH_TitleDesc=0&_udlo=15&LH_BIN=1&_ipg=200&_pgn=1'
            numPages = int(self.numPagesInput.text())
            numThreads = int(self.numThreadInput.text())
        except Exception as e:
            msg = qtw.QMessageBox()
            msg.setWindowTitle("Error check info")
            msg.setText("One of the required fields are worng")
            msg.exec_()
            return
        # Remove the run configuration
        for i in range(self.runOptions.count()):
            self.runOptions.removeRow(0)
        self.dataWind.removeItem(self.runOptions)
        # Set progress bar and buttons in horizontal box

        self.runStatus = qtw.QHBoxLayout()
        self.runStatus.setContentsMargins(60, 0, 0, 1700)
        self.runStatus.setSpacing(5)

        stopRunBtn = qtw.QPushButton()
        stopRunBtn.setText("Stop Scan")
        stopRunBtn.setStyleSheet("QPushButton{\n"
                                 "    color: white;\n"
                                 "    background-color: rgb(77, 77, 77);\n"
                                 "    border-style: outset;\n"
                                 "    border-width: 2px;\n"
                                 "    border-radius: 10px;\n"
                                 "    text-color: white;\n"
                                 "    border-color: rgb(85, 255, 255);\n"
                                 "    font: bold 30px;\n"
                                 "    padding: 6px;\n"
                                 " }QPushButton:hover {\n"
                                 "      background-color: rgb(148, 148, 148);\n"
                                 " }")
        stopRunBtn.clicked.connect(self.stopScan)

        seeLinksBtn = qtw.QPushButton()
        seeLinksBtn.setText("See Links")
        seeLinksBtn.setStyleSheet("QPushButton{\n"
                                  "    color: white;\n"
                                  "    background-color: rgb(77, 77, 77);\n"
                                  "    border-style: outset;\n"
                                  "    border-width: 2px;\n"
                                  "    border-radius: 10px;\n"
                                  "    text-color: white;\n"
                                  "    border-color: rgb(85, 255, 255);\n"
                                  "    font: bold 30px;\n"
                                  "    padding: 6px;\n"
                                  " }QPushButton:hover {\n"
                                  "      background-color: rgb(148, 148, 148);\n"
                                  " }")
        seeLinksBtn.clicked.connect(self.stopScan)

        self.progBar = qtw.QProgressBar()
        self.lcdNumber = qtw.QLCDNumber()
        self.lcdNumber.setStyleSheet("QLCDNumber{\n"
                                     "    color: black;\n"
                                     "    border-style: outset;\n"
                                     "    border-width: 4px;\n"
                                     "    border-radius: 10px;\n"
                                     "    border-color: rgb(85, 255, 255);\n"
                                     "    font: bold 15px;\n"
                                     " }")

        self.runStatus.addWidget(self.lcdNumber)
        self.runStatus.addWidget(self.progBar)
        self.runStatus.addWidget(stopRunBtn)
        self.runStatus.addWidget(seeLinksBtn)
        self.dataWind.addLayout(self.runStatus)

        self.scanThread = ScanEbayThread(self.dataBaseCon, maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales, minPrice, maxPrice,
                                         pagesToSearch, numPages, numThreads)

        self.scanThread.finished.connect(self.scanThreadFinish)
        self.scanEbay_btn.setDisabled(True)
        self.scanThread.start()

    def scanThreadFinish(self):
        self.scanEbay_btn.setDisabled(False)
        msg = qtw.QMessageBox()
        msg.setWindowTitle("Scan Complete")
        msg.setText("Finish scaning ebay")
        msg.exec_()

    def stopScan(self):
        # terminate scan thread and delete run status
        for i in range(self.runStatus.count()):
            self.runStatus.itemAt(i).widget().deleteLater()
        self.dataWind.removeItem(self.runStatus)
        self.dataWind.removeItem(self.runOptions)
        self.dataWind.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 700)
        self.scanThread.terminate()


class ScanEbayThread(qtc.QThread):
    changeProgBarVal = qtc.pyqtSignal(int)
    def __init__(self, dataBaseCon,maxFeedBack, minFeedBack, maxSales, minSales, minWeekSales, minPrice, maxPrice, pagesToSearch,
                 numPages, numThreads):
        qtc.QThread.__init__(self)
        self.maxFeedBack = maxFeedBack
        self.minFeedBack = minFeedBack
        self.maxSales = maxSales
        self.minSales = minSales
        self.minWeekSales = minWeekSales
        self.minPrice = minPrice
        self.maxPrice = maxPrice
        self.pagesToSearch = pagesToSearch
        self.numPages = numPages
        self.numThreads = numThreads
        self.dataBaseCon = dataBaseCon

    def run(self):
        ebayScraper = EbayScraper(dataBaseCon,self.maxFeedBack, self.minFeedBack, self.maxSales, self.minSales, self.minWeekSales,
                                  self.minPrice,
                                  self.maxPrice,
                                  self.pagesToSearch, self.numPages,
                                  self.numThreads)
        ebayScraper.startScraping()



if __name__ == '__main__':
    dataBaseCon = connectToDB('LAPTOP-VNSLHC31', 'Ebay')
    RunConfig = selectFromDB(dataBaseCon, "SELECT * FROM [Ebay].[dbo].[RunConfig]")
    app = qtw.QApplication([])
    widget = MainWindow(RunConfig, dataBaseCon)
    widget.show()

    app.exec_()
