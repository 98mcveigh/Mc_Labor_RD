import xlsxwriter


def formatNewWorkbook(workbook,worksheet,query,settingsDict):
    sheet = {"workbook":workbook,"worksheet":worksheet,"index":3,"statusIndex":1,"compNameCol":0,"locCol":1,"townCol":2,"stateCol":3,"zipCol":4,"phoneCol":5,"infoCol":6,"siteCol":7,"emailCol":8,"titleRow":2,"badCompNameCol":5}

    worksheet.write(0,0, "Google Search: ")
    worksheet.write(0,1, query)
    worksheet.write(1,0, "Number of Google Results Searched: ")
    worksheet.write(1,2, str(settingsDict['numGoogResults']))
    worksheet.write(sheet["titleRow"],sheet["compNameCol"], "Company Name")
    worksheet.write(sheet["titleRow"],sheet["locCol"], "Mailing Address")
    worksheet.write(sheet["titleRow"],sheet["townCol"], "Mailing City")
    worksheet.write(sheet["titleRow"],sheet["stateCol"], "Mailing State")
    worksheet.write(sheet["titleRow"],sheet["zipCol"], "Mailing Zip Code")
    worksheet.write(sheet["titleRow"],sheet["phoneCol"], "Phone Number Combined")
    worksheet.write(sheet["titleRow"],sheet["infoCol"], "Email Address (Info)")
    worksheet.write(sheet["titleRow"],sheet["siteCol"], "Website Address")
    worksheet.write(sheet["titleRow"],sheet["emailCol"], "Contact Emails")
    worksheet.set_column(0,2,20)
    worksheet.set_column(2,4,15)
    worksheet.set_column(5,6,20)
    worksheet.set_column(7,7,30)
    worksheet.set_column(8,15,25)

    return sheet


def reportEmails(emails,sheet,worksheet):
    #print out emails to worksheet. any email start matching the list gets printed
    # out to info column and rest get printed out horizontally each in new cell
    infoNames = ["info","office","marketing","sales","service","estimating","help","relations","supplierinfo","supplier","store","accounting","accounts"]
    nonInfoNum = 0
    haveInfo = False
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
        if isInfo:
            continue
        else:
            col = sheet["emailCol"] + nonInfoNum
            worksheet.write(sheet["index"],col,email)
            nonInfoNum = nonInfoNum + 1
    return
