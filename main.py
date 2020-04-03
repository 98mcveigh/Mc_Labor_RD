import Scraper
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import xlsxwriter
import pickle

def main(window,statusLabel,searchEntry):
    # Collect settings and entered query
    settingsFile = open("settings.dat","rb")
    settingsDict = pickle.load(settingsFile)
    settingsFile.close()
    query = searchEntry.get()
    if query == '':
        statusLabel["text"] = "Please enter query"
        return

    #setup excel sheet to print results to
    workbookName = '_'.join(query.split())

    workbook = xlsxwriter.Workbook(settingsDict['saveDirectory'] + workbookName + '.xlsx')

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

    noScrapeCol = 12 #???????????
    errorCol = 17    #???????????

    index = 2
    errorIndex = 2
    noScrapeIndex = 2
    statusIndex = 1
    worksheet.write(0,0, "Google Search: ")
    worksheet.write(0,2, query)
    worksheet.write(1,compNameCol, "Company Name")
    worksheet.write(1,locCol, "Mailing Address")
    worksheet.write(1,townCol, "Mailing City")
    worksheet.write(1,stateCol, "Mailing State")
    worksheet.write(1,zipCol, "Mailing Zip Code")
    worksheet.write(1,phoneCol, "Phone Number Combined")
    worksheet.write(1,infoCol, "Email Address (Info)")
    worksheet.write(1,siteCol, "Website Address")
    worksheet.write(1,emailCol, "Contact Emails")

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
            print(site)
            goodSites.append(cleanValidSite)
    print()
    print()
    #eliminate any site repeats
    goodSites = Scraper.makeUnique(goodSites)
    for site in goodSites:
        #update gui
        siteProgress = str(statusIndex) + "/" + str(len(goodSites))
        statusLabel["text"] = "Collecting information..." + " " + siteProgress
        window.update_idletasks()
        statusIndex = statusIndex + 1
        print()
        print()
        emails = []
        print("Finding Information for: " + site)

        # Collect homepage content and test for scraping permission.
        # If not available denote on excel sheet the reason
        try:
            homepageSoup = BeautifulSoup(requests.get(site,timeout=3.0).content,"lxml")
        except:
            worksheet.write(errorIndex,errorCol, site)
            errorIndex = errorIndex + 1
            print(site + " is not accessible")
            continue
        if not Scraper.isAllowedToScrape(site,homepageSoup):
            worksheet.write(noScrapeIndex,noScrapeCol, site)
            noScrapeIndex = noScrapeIndex + 1
            print(site + " does not allow scraping")
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
                    Scraper.reportEmails(emails,infoCol,emailCol,workbook)
                else:
                    worksheet.write(index, emailCol, "None")
                    worksheet.write(index, infoCol, "None")
                worksheet.write(index, locCol, "None")
                compName = Scraper.scrapeCompName(homepageSoup)
                if compName is not None:
                    worksheet.write(index, compNameCol, compName)
                    print("Company: " + compName)
                else:
                    worksheet.write(index, compNameCol, "None")
                    print("Company name could not be found")
                index = index + 1
                print("Emails: ", emails)
                print("Contact Page Could Not Be Accessed")
                continue

            #collect and report company name
            compName = Scraper.scrapeCompName(homepageSoup,contSoup)
            if compName is not None:
                worksheet.write(index, compNameCol, compName)
                print("Company: " + compName)
            else:
                worksheet.write(index, compNameCol, "None")
                print("Company name could not be found")

            # add new emails found on contact page, make all unique and report
            emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(contSoup))
            if emails != []:
                # TODO: new email each horiz cell
                worksheet.write(index, emailCol, ','.join(emails))
            else:
                worksheet.write(index, emailCol, "None")
            print("Emails: ", emails)

            #find best address prioritizing full address -> PO Box -> just town
            bestAddress = Scraper.scrapeAddress(contSoup)
            if bestAddress != []:
                worksheet.write(index,locCol,','.join(bestAddress))
                print("Address: ",bestAddress)
            else:
                bestAddress = Scraper.scrapePOBox(contSoup)
                if bestAddress != []:
                    worksheet.write(index,locCol,','.join(bestAddress))
                    print("P.O. Box: ",bestAddress)
                else:
                    bestAddress = Scraper.scrapeTown(contSoup)
                    if bestAddress != []:
                        worksheet.write(index,locCol,','.join(bestAddress))
                        print("Town: ",bestAddress)
                    else:
                        worksheet.write(index,locCol,"None")
                        print("No Address, P.O. Box or Town could be found.")
            # report out whatever the best address is and continue to next site
            if bestAddress != []:
                town = Scraper.getTownFromLoc(bestAddress)
                worksheet.write(index,townCol,','.join(town))
                zip = Scraper.getZipFromLoc(bestAddress)
                worksheet.write(#####################FILL THIS IN##########################)
            else:
                worksheet.write(index,townCol,"None")
                print("None")
            index = index + 1

        else:
            # if there is no contact page report out emails and company name
            # and continue to next site
            if emails != []:
                # TODO: make each email new cell horiz
                worksheet.write(index, emailCol, ','.join(emails))
            else:
                worksheet.write(index, emailCol, "None")
            worksheet.write(index, locCol, "None")
            compName = Scraper.scrapeCompName(homepageSoup)
            if compName is not None:
                worksheet.write(index, compNameCol, compName)
                print("Company: " + compName)
            else:
                worksheet.write(index, compNameCol, "None")
                print("Company name could not be found")
            print("Emails: ", emails)
            print("Contact Page was not Accessible")
            index = index + 1
    workbook.close()
    statusLabel["text"] = "Collection Complete - Enter New Search"
    window.update_idletasks()
