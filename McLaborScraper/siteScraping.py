import McLaborScraper.Scraper as Scraper
import McLaborScraper.Excel as Excel
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import xlsxwriter
import pickle
import time


def searchDelay(gui):
    delay = 15 #30*60
    if len(gui.queue) > 0:
        for secs in range(delay):
            if gui.startStopQueueButton["text"] == "Pause Queue" and len(gui.queue) > 0:
                gui.statusLabel["text"] = Scraper.getMinutesSeconds(delay - secs) + " until next search"
                time.sleep(1)
            else:
                return False
        return True
    return False

def runScrapingLoop(gui):
    #check that there are queues to search
    shouldRunLoop = True
    while shouldRunLoop:
        #check that the queue has length and is running
        if len(gui.queueLabels) > 0 and gui.startStopQueueButton["text"] == "Pause Queue":
            #collect search object and delete it from queue
            searchObject = gui.queue[0]
            gui.queue.pop(0)
            gui.queueLabels[0].destroy()
            gui.queueLabels.pop(0)
            gui.updateQueue()
            #run search
            scrape(gui,searchObject)
            if searchDelay(gui):
                continue
            else:
                shouldRunLoop = False
                continue
        else:
            shouldRunLoop = False
            continue
    if len(gui.queue) > 0 and gui.queue[0].worksheetSettings != None:
        Excel.reportBadSites(gui.queue[0].worksheetSettings,gui.queue[0].worksheetSettings["worksheet"])
        gui.queue[0].worksheetSettings["workbook"].close()
        text = gui.queue[0].entry
        testText = gui.queue[0].entry
        while testText == text:
            gui.queue.pop(0)
            gui.queueLabels[0].destroy()
            gui.queueLabels.pop(0)
            gui.updateQueue()
            try:
                testText = gui.queue[0].entry
            except:
                break
    gui.startStopQueueButton["text"] = "Begin Queue"
    gui.statusLabel["text"] = "Queue Completed"
    gui.searchIsRunning[0] = False
    return


def scrape(gui,searchObj):
    print("Entry: ",searchObj.entry)
    print("Start: ",searchObj.start)
    print("Stop: ",searchObj.stop)
    print("Individual?: ",searchObj.isIndividual)
    print("Number of this Search: ",searchObj.numOfSearch)
    print("Worksheet Settings: ",searchObj.worksheetSettings)
    # Collect settings and entered query
    query = searchObj.entry
    gui.searchIsRunning[0] = True
    gui.currentSearch["text"] = "Searching " + query
    settingsFile = open("settings.dat","rb")
    settingsDict = pickle.load(settingsFile)
    settingsFile.close()

    #setup excel sheet to print results to
    if searchObj.isIndividual:
        workbookName = '_'.join(query.split())

        workbook = xlsxwriter.Workbook(settingsDict['saveDirectory'] + "/" + workbookName + '.xlsx')

        worksheet = workbook.add_worksheet()

        sheet = Excel.formatNewWorkbook(workbook,worksheet,query,settingsDict)
    elif not searchObj.isIndividual and searchObj.numOfSearch == 0:
        workbookName = '_'.join(query.split())

        workbook = xlsxwriter.Workbook(settingsDict['saveDirectory'] + "/" + workbookName + '.xlsx')

        worksheet = workbook.add_worksheet()

        sheet = Excel.formatNewWorkbook(workbook,worksheet,query,settingsDict)
    else:
        sheet = searchObj.worksheetSettings
        workbook = sheet["workbook"]
        worksheet = sheet["worksheet"]
        sheet["statusIndex"] = 1

    goodSites = []
    gui.statusLabel["text"] = "Collecting sites..."
    gui.window.update_idletasks()

    #search google for sites and collect only those that are homepages and
    # about pages (avoiding things like angies list)
    for site in search(query, tld='com', lang='en', num=30, start=searchObj.start, stop=searchObj.stop, pause=4.0):
        cleanValidSite = Scraper.validateSite(site)
        if cleanValidSite is not None:
            goodSites.append(cleanValidSite)
    #eliminate any site repeats
    goodSites = Scraper.makeUnique(goodSites)

    for site in goodSites:
        #update gui
        siteProgress = str(sheet["statusIndex"]) + "/" + str(len(goodSites))
        gui.statusLabel["text"] = "Collecting information..." + " " + siteProgress
        gui.window.update_idletasks()
        sheet["statusIndex"] = sheet["statusIndex"] + 1
        emails = []

        # Collect homepage content and test for scraping permission.
        # If not available denote on excel sheet the reason
        try:
            homepageSoup = BeautifulSoup(requests.get(site,timeout=3.0).content,"lxml")
        except:
            sheet["badSites"].append(site)
            continue
        if not Scraper.isAllowedToScrape(site,homepageSoup):
            sheet["badSites"].append(site)
            continue

        #if site can be scraped write site to appropriate
        # excel cell and collect emails from homepage
        worksheet.write(sheet["index"],sheet["siteCol"], site)
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
                    Excel.reportEmails(emails,sheet,worksheet)

                compName = Scraper.scrapeCompName(site,homepageSoup)
                if compName is not None:
                    worksheet.write(sheet["index"], sheet["compNameCol"], compName)

                phoneNum = Scraper.scrapePhoneNumber(homepageSoup)
                if phoneNum:
                    worksheet.write(sheet["index"],sheet["phoneCol"],phoneNum)
                sheet["index"] = sheet["index"] + 1
                continue

            #collect and report company name
            compName = Scraper.scrapeCompName(site,homepageSoup,contSoup)
            if compName is not None:
                worksheet.write(sheet["index"], sheet["compNameCol"], compName)

            # add new emails found on contact page, make all unique and report
            emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(contSoup))
            if emails != []:
                Excel.reportEmails(emails,sheet,worksheet)

            #find and report all phone numbers found on contact page
            phoneNum = Scraper.scrapePhoneNumber(contSoup)
            if phoneNum:
                worksheet.write(sheet["index"],sheet["phoneCol"],phoneNum)
            #find best address prioritizing full address -> PO Box -> just town
            bestAddress = Scraper.scrapeBestAddress(contSoup,True)
            if bestAddress is not None:
                worksheet.write(sheet["index"],sheet["locCol"],bestAddress)
                town = Scraper.getTownFromLoc(bestAddress)
                worksheet.write(sheet["index"],sheet["townCol"],town)
                zip = Scraper.getZipFromLoc(bestAddress)
                worksheet.write(sheet["index"],sheet["zipCol"],zip)
                worksheet.write(sheet["index"],sheet["stateCol"],"MA") #scraper only functional for MA 4-3-2020
            sheet["index"] = sheet["index"] + 1

        else:
            # if there is no contact page report out emails,location and company name
            # and continue to next site
            if emails != []:
                Excel.reportEmails(emails,sheet,worksheet)

            #Only look for specific addresses or po boxes on front page in case
            # of site listing available towns for work
            bestAddress = Scraper.scrapeBestAddress(homepageSoup)
            if bestAddress is not None:
                worksheet.write(sheet["index"],sheet["locCol"],bestAddress)
                town = Scraper.getTownFromLoc(bestAddress)
                worksheet.write(sheet["index"],sheet["townCol"],town)
                zip = Scraper.getZipFromLoc(bestAddress)
                worksheet.write(sheet["index"],sheet["zipCol"],zip)
                worksheet.write(sheet["index"],sheet["stateCol"],"MA") #scraper only functional for MA 4-3-2020

            phoneNum = Scraper.scrapePhoneNumber(homepageSoup)
            if phoneNum:
                worksheet.write(sheet["index"],sheet["phoneCol"],phoneNum)

            compName = Scraper.scrapeCompName(site,homepageSoup)
            if compName is not None:
                worksheet.write(sheet["index"], sheet["compNameCol"], compName)
            sheet["index"] = sheet["index"] + 1

    if searchObj.isIndividual or len(gui.queue) == 0:
        Excel.reportBadSites(sheet,worksheet)
        workbook.close()
        gui.searchIsRunning[0] = False
    elif not searchObj.isIndividual and gui.queue[0].numOfSearch == 0:
        Excel.reportBadSites(sheet,worksheet)
        workbook.close()
    elif not searchObj.isIndividual and searchObj.numOfSearch == 0:
        for nextSearch in gui.queue:
            if nextSearch.numOfSearch == 0:
                break
            else:
                nextSearch.worksheetSettings = sheet


    gui.currentSearch["text"] = ""
    gui.statusLabel["text"] = "Collection Complete"
    gui.window.update_idletasks()
