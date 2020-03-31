import Scraper
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import xlsxwriter



def main(window,statusLabel,searchEntry):

    query = searchEntry.get()
    if query == '':
        statusLabel["text"] = "Please enter query"
        return

    workbookName = '_'.join(query.split())

    workbook = xlsxwriter.Workbook('C:/Users/98mcv/Desktop/Email_Collection/' + workbookName + '.xlsx')

    worksheet = workbook.add_worksheet()

    siteCol = 0
    compNameCol = 2
    emailCol = 4
    locCol = 6
    noScrapeCol = 10
    errorCol = 15
    worksheet.write(0,0, "Google Search: ")
    worksheet.write(0,2, query)
    worksheet.write(1,siteCol, "Website")
    worksheet.write(1,compNameCol, "Company Name")
    worksheet.write(1,emailCol, "Email(s)")
    worksheet.write(1,locCol, "Location")

    worksheet.write(1,noScrapeCol, "Sites Where Not Allowed")
    worksheet.write(1,errorCol, "Sites Encountered Unknown Error")

    goodSites = []
    statusLabel["text"] = "Collecting sites..."
    window.update_idletasks()
    for site in search(query, tld='com', lang='en', num=10, start=0, stop=50, pause=2.0):
        cleanValidSite = Scraper.validateSite(site)
        if cleanValidSite is not None:
            print(site)
            goodSites.append(cleanValidSite)
        else:
            continue
    print()
    print()
    index = 2
    errorIndex = 2
    noScrapeIndex = 2
    statusIndex = 1
    goodSites = Scraper.makeUnique(goodSites)
    for site in goodSites:
        siteProgress = str(statusIndex) + "/" + str(len(goodSites))
        statusLabel["text"] = "Collecting information..." + " " + siteProgress
        window.update_idletasks()
        statusIndex = statusIndex + 1
        print()
        print()
        emails = []
        print("Finding Information for: " + site)
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
        worksheet.write(index,siteCol, site)
        emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(homepageSoup))
        contPage = Scraper.getContactPage(site,homepageSoup)
        if contPage != None:
            try:
                contSoup = BeautifulSoup(requests.get(contPage,timeout=3.0).content,"lxml")
            except:
                # TODO: need to write in something for comp name here too
                #maybe if contact page not accessible thats another col? idk
                if emails != []:
                    # TODO: Change so emails are placed in cells next to each other horiz
                    worksheet.write(index, emailCol, ','.join(emails))
                else:
                    worksheet.write(index, emailCol, "None")
                worksheet.write(index, locCol, "None")
                worksheet.write(index,compNameCol,"None") #<--may not be best solution?
                index = index + 1
                print("Emails: ", emails)
                print("Contact Page Could Not Be Accessed")
                continue
            compName = Scraper.scrapeCompanyName(homepageSoup,contSoup)
            if compName is not None:
                worksheet.write(index, compNameCol, compName)
                print("Company: " + compName)
            else:
                worksheet.write(index, compNameCol, "None")
                print("Company name could not be found")
            emails = Scraper.makeUnique(emails + Scraper.scrapeEmail(contSoup))
            if emails != []:
                # TODO: new email each horiz cell
                worksheet.write(index, emailCol, ','.join(emails))
            else:
                worksheet.write(index, emailCol, "None")
            print("Emails: ", emails)
            add = Scraper.scrapeAddress(contSoup)
            if add != []:
                worksheet.write(index,locCol,','.join(add))
                print("Address: ",add)
            else:
                poBox = Scraper.scrapePOBox(contSoup)
                if poBox != []:
                    worksheet.write(index,locCol,','.join(poBox))
                    print("P.O. Box: ",poBox)
                else:
                    town = Scraper.scrapeTown(contSoup)
                    if town != []:
                        worksheet.write(index,locCol,','.join(town))
                        print("Town: ",town)
                    else:
                        worksheet.write(index,locCol,"None")
                        print("No Address, P.O. Box or Town could be found.")
            index = index + 1
        else:
            if emails != []:
                # TODO: make each email new cell horiz
                worksheet.write(index, emailCol, ','.join(emails))
            else:
                worksheet.write(index, emailCol, "None")
            worksheet.write(index, locCol, "None")
            compName = Scraper.scrapeCompanyName(homepageSoup,homepageSoup)
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