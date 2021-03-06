import xlsxwriter
import McLaborScraper.Scraper as Scraper
import time
from datetime import date

def formatNewWorkbook(workbook,worksheet,query):
    sheet = {"workbook":workbook,"worksheet":worksheet,"badSites":[],"index":3,"statusIndex":1,
    "dateCol":0,"compNameCol":1,"locCol":2,"townCol":3,"stateCol":4,"zipCol":5,"phoneCol":6,"infoCol":7,
    "emailCol":8,"siteCol":9,"notesCol":10,"titleRow":2,"badCompNameCol":1}

    worksheet.write(0,0, "Google Search: ")
    worksheet.write(0,1, query)
    worksheet.write(1,0, "Number of Google Results Searched: ")
    worksheet.write(1,2, "150")
    worksheet.write(sheet["titleRow"],sheet["dateCol"], "Date Collected")
    worksheet.write(sheet["titleRow"],sheet["compNameCol"], "Company Name")
    worksheet.write(sheet["titleRow"],sheet["locCol"], "Mailing Address")
    worksheet.write(sheet["titleRow"],sheet["townCol"], "Mailing City")
    worksheet.write(sheet["titleRow"],sheet["stateCol"], "Mailing State")
    worksheet.write(sheet["titleRow"],sheet["zipCol"], "Mailing Zip Code")
    worksheet.write(sheet["titleRow"],sheet["phoneCol"], "Phone Number Combined")
    worksheet.write(sheet["titleRow"],sheet["infoCol"], "Email #1 (Info)")
    worksheet.write(sheet["titleRow"],sheet["emailCol"], "Email #2 (B2B)")
    worksheet.write(sheet["titleRow"],sheet["siteCol"], "Website Address")
    worksheet.write(sheet["titleRow"],sheet["notesCol"], "Notes")
    worksheet.set_column(0,0,15)
    worksheet.set_column(1,3,20)
    worksheet.set_column(4,5,15)
    worksheet.set_column(6,8,20)
    worksheet.set_column(9,10,30)

    return sheet


def reportEmails(emails,sheet,worksheet):
    #print out emails to worksheet. any email start matching the list gets printed
    # out to info column and rest get printed out horizontally each in new cell
    infoNames = ["info","office","customerservice","customersupport","marketing","sales","service","services","support","careers",
    "estimating","help","relations","supplierinfo","supplier","store","accounting","accounts","media"]
    nonInfoNum = 0
    haveInfo = False
    haveB2B = False
    extraEmails = []
    for i,email in enumerate(emails):
        isInfo = False
        emailName = email.split("@")[0]
        for starter in infoNames:
            if starter == emailName:
                if haveInfo:
                    isInfo = True
                    break
                else:
                    worksheet.write(sheet["index"],sheet["infoCol"],email)
                    isInfo = True
                    haveInfo = True
                    break
        if isInfo:
            continue
        else:
            if haveB2B:
                extraEmails.append(email)
                continue
            else:
                worksheet.write(sheet["index"],sheet["emailCol"],email)
                haveB2B = True
    worksheet.write(sheet["index"],sheet["notesCol"],','.join(extraEmails))
    return

def reportBadSites(sheet,worksheet):
    for badSite in sheet["badSites"]:
        compName = Scraper.scrapeCompName(badSite)
        if compName is not None:
            worksheet.write(sheet["index"], sheet["badCompNameCol"], compName)
        worksheet.write(sheet["index"],sheet["siteCol"],badSite)
        worksheet.write(sheet["index"],sheet["dateCol"],date.today().strftime("%m/%d/%Y"))
        sheet["index"] = sheet["index"] + 1
