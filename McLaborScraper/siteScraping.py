import McLaborScraper.Scraper as Scraper
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import xlsxwriter
import pickle
import time

def printer():
    print("heloo")


def runScrapingLoop(window,statusLabel,searchEntry,startStopQueueButton,queueLabels,searchIsRunning):
    delay = 15
    for x in range(len(queueLabels)):
        if startStopQueueButton["text"] == "Pause Queue":
            scrape(window,statusLabel,queueLabels[0]["text"],searchIsRunning)
            queueLabels[0].destroy()
            queueLabels.pop(0)
            if len(queueLabels) > 0:
                for mins in range(delay):
                    if startStopQueueButton["text"] == "Pause Queue":
                        statusLabel["text"] = str(delay - mins) + " mins until next search"
                        time.sleep(1)
                    else:
                        statusLabel["text"] == "Queue Paused"
                        searchIsRunning[0] = False
                        return
        else:
            statusLabel["text"] == "Queue Paused"
            searchIsRunning[0] = False
            return
    startStopQueueButton["text"] = "Begin Queue"
    statusLabel["text"] = "Queue Completed"

def scrape(window,statusLabel,query,searchIsRunning):
    # Collect settings and entered query
    searchIsRunning[0] = True
    settingsFile = open("settings.dat","rb")
    settingsDict = pickle.load(settingsFile)
    settingsFile.close()
    if query == '':
        statusLabel["text"] = "Please enter query"
        return

    #setup excel sheet to print results to
    workbookName = '_'.join(query.split())

    workbook = xlsxwriter.Workbook(settingsDict['saveDirectory'] + "/" + workbookName + '.xlsx')

    worksheet = workbook.add_worksheet()

    compNameCol = 0
    locCol = 1
    townCol = 2
    stateCol = 3
    zipCol = 4
    phoneCol = 5
    infoCol = 6
    siteCol = 7
    emailCol = 8
    titleRow = 2

    index = 3
    errorIndex = 2
    noScrapeIndex = 2
    statusIndex = 1
    worksheet.write(0,0, "Google Search: ")
    worksheet.write(0,1, query)
    worksheet.write(1,0, "Number of Google Results Searched: ")
    worksheet.write(1,2, str(settingsDict['numGoogResults']))
    worksheet.write(titleRow,compNameCol, "Company Name")
    worksheet.write(titleRow,locCol, "Mailing Address")
    worksheet.write(titleRow,townCol, "Mailing City")
    worksheet.write(titleRow,stateCol, "Mailing State")
    worksheet.write(titleRow,zipCol, "Mailing Zip Code")
    worksheet.write(titleRow,phoneCol, "Phone Number Combined")
    worksheet.write(titleRow,infoCol, "Email Address (Info)")
    worksheet.write(titleRow,siteCol, "Website Address")
    worksheet.write(titleRow,emailCol, "Contact Emails")
    worksheet.set_column(0,2,20)
    worksheet.set_column(2,4,15)
    worksheet.set_column(5,6,20)
    worksheet.set_column(7,7,30)
    worksheet.set_column(8,15,25)
    # worksheet.write(1,noScrapeCol, "Sites Where Not Allowed")
    # worksheet.write(1,errorCol, "Sites Encountered Unknown Error")

    goodSites = []
    statusLabel["text"] = "Collecting sites..."
    window.update_idletasks()

    #search google for sites and collect only those that are homepages and
    # about pages (avoiding things like angies list)

    for site in search(query, tld='com', lang='en', num=10, start=0, stop=settingsDict['numGoogResults'], pause=2.0):
        cleanValidSite = Scraper.validateSite(site)
        if cleanValidSite is not None:
            goodSites.append(cleanValidSite)
    #eliminate any site repeats
    goodSites = Scraper.makeUnique(goodSites)
    badSites = []
    for site in goodSites:
        #update gui
        siteProgress = str(statusIndex) + "/" + str(len(goodSites))
        statusLabel["text"] = "Collecting information..." + " " + siteProgress
        window.update_idletasks()
        statusIndex = statusIndex + 1
        emails = []

        # Collect homepage content and test for scraping permission.
        # If not available denote on excel sheet the reason
        try:
            homepageSoup = BeautifulSoup(requests.get(site,timeout=3.0).content,"lxml")
        except:
            badSites.append(site)
            continue
        if not Scraper.isAllowedToScrape(site,homepageSoup):
            badSites.append(site)
            continue

        #if site can be scraped write site to appropriate
        # excel cell and collect emails from homepage
        worksheet.write(index,siteCol, site)
        emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(homepageSoup))
        #get contact page and if it is there collect the content.
        contPage = Scraper.getContactPage(site,homepageSoup)
        if contPage != None:
            try:
                contSoup = BeautifulSoup(requests.get(contPage,timeout=3.0).content,"lxml")
            except:
                # if contact page can not be scraped report out emails and collect
                # and report out company name and continue to next site
                if emails != []:
                    Scraper.reportEmails(emails,infoCol,emailCol,worksheet)

                compName = Scraper.scrapeCompName(homepageSoup)
                if compName is not None:
                    worksheet.write(index, compNameCol, compName)
                else:
                    worksheet.write(index, compNameCol, "")

                phoneNums = Scraper.scrapePhoneNumber(homepageSoup)
                if phoneNums:
                    worksheet.write(index,phoneCol,','.join(phoneNums))
                index = index + 1
                continue

            #collect and report company name
            compName = Scraper.scrapeCompName(homepageSoup,contSoup)
            if compName is not None:
                worksheet.write(index, compNameCol, compName)

            # add new emails found on contact page, make all unique and report
            emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(contSoup))
            if emails != []:
                Scraper.reportEmails(emails,index,infoCol,emailCol,worksheet)

            #find and report all phone numbers found on contact page
            phoneNums = Scraper.scrapePhoneNumber(contSoup)
            if phoneNums:
                worksheet.write(index,phoneCol,','.join(phoneNums))
            #find best address prioritizing full address -> PO Box -> just town
            bestAddress = Scraper.scrapeBestAddress(contSoup,True)
            if bestAddress is not None:
                worksheet.write(index,locCol,bestAddress)
                town = Scraper.getTownFromLoc(bestAddress)
                worksheet.write(index,townCol,town)
                zip = Scraper.getZipFromLoc(bestAddress)
                worksheet.write(index,zipCol,zip)
                worksheet.write(index,stateCol,"MA") #scraper only functional for MA 4-3-2020
            else:
                worksheet.write(index,townCol,"")
            index = index + 1

        else:
            # if there is no contact page report out emails,location and company name
            # and continue to next site
            if emails != []:
                Scraper.reportEmails(emails,index,infoCol,emailCol,worksheet)

            #Only look for specific addresses or po boxes on front page in case
            # of site listing available towns for work
            bestAddress = Scraper.scrapeBestAddress(homepageSoup)
            if bestAddress is not None:
                worksheet.write(index,locCol,bestAddress)
                town = Scraper.getTownFromLoc(bestAddress)
                worksheet.write(index,townCol,town)
                zip = Scraper.getZipFromLoc(bestAddress)
                worksheet.write(index,zipCol,zip)
                worksheet.write(index,stateCol,"MA") #scraper only functional for MA 4-3-2020
            else:
                worksheet.write(index,townCol,"")

            phoneNums = Scraper.scrapePhoneNumber(homepageSoup)
            if phoneNums:
                worksheet.write(index,phoneCol,','.join(phoneNums))

            compName = Scraper.scrapeCompName(homepageSoup)
            if compName is not None:
                worksheet.write(index, compNameCol, compName)
            index = index + 1
    index = index + 1
    worksheet.write(index,siteCol,"Inaccessible Sites:")
    index = index + 1
    for badSite in badSites:
        worksheet.write(index,siteCol,badSite)
        index = index + 1
    workbook.close()
    statusLabel["text"] = "Collection Complete"
    window.update_idletasks()
    searchIsRunning[0] = False
