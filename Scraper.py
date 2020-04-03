from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import zips

def getContactPage(site,siteSoup):
    #get ending of website (.com,.org,.net,...)
    siteEnding = site[-5:-1]
    linkTags = siteSoup.findAll('a', href=True)
    for link in linkTags:
        # Search for any link that contains the word "contact"
        matchCheck = re.search('contact',link['href'])
        if matchCheck is not None:
            if siteEnding in matchCheck.string and site != matchCheck.string:
                #return match if it is an absolute link
                return matchCheck.string
            else:
                #attach match to site return if it is a relative linke
                return site + matchCheck.string
        else:
            continue
    return None

def makeUnique(lis):
    wrapCount = dict.fromkeys(lis)
    # make dictionary and every time a key contains another key (i.e. 1train23 contains train)
    # then increase the key value by 1. Dictionaries automatically get rid of repeats
    # Keep only keys with value of 0
    for key in wrapCount:
        wrapCount[key] = 0
    for uniqueCandidate in lis:
        for wrapperCandidate in lis:
            if uniqueCandidate in wrapperCandidate and uniqueCandidate != wrapperCandidate:
                wrapCount[wrapperCandidate] = wrapCount[wrapperCandidate] + 1
    final = []
    for candidate in wrapCount:
        if wrapCount[candidate] is 0:
            final.append(candidate)

    return list(dict.fromkeys(final))

def isAllowedToScrape(site,soup):
    # check title for most common phrases when sites do not allow scraping
    title = soup.find('title')
    if title is not None and ("403" in title.text or "Not Acceptable!" in title.text or "Access Denied" in title.text):
        return False
    else:
        return True

def getStringNoSpaces(str):
    #divide all words by the list below --> should leave only alphanumeric chars
    deliminate = re.split('[\:,\;,\-,\|,\/,\s*]\s*',str)
    cleanWords = []
    #get rid of any blank spaces
    for word in deliminate:
        if word == '':
            continue
        else:
            cleanWords.append(word)
    #return final string with each word/number seperate only by a single space
    return ' '.join(cleanWords)

def getGoodTags(tagList):
    #return only tags that contain the useful text
    goodTags = []
    for tag in tagList:
        if tag.name == "script":
            continue
        elif tag.name == "style":
            continue
        elif tag.name == "img":
            continue
        elif tag.name == "br":
            continue
        elif tag.name == "meta":
            continue
        elif tag.name == "html":
            continue
        elif tag.name == "head":
            continue
        elif tag.name == "body":
            continue
        elif tag.name == "title":
            continue
        else:
            goodTags.append(tag)
    return goodTags

def getPageString(tagList):
    goodContents = []
    tags = getGoodTags(tagList)
    for tag in tags:
        if re.search('[\{|\}|\<|\>]',tag.text):
            # eliminate any text strings that have javascript in them
            continue
        else:
            for word in re.split('[-,\s]\s*',tag.text):
                #add each individual word to goodContents list after splitting
                # by any spaces or dashes
                goodContents.append(word)
    #make goodContents into a string. this still contains unneccesary long blank
    #space so getStringNoSpaces used to produce final string with only single spaces
    semiDoneString = ' '.join(goodContents)
    pageString = getStringNoSpaces(semiDoneString)
    #TODO: this is a little messy could probably do something a little simpler/cleaner
    return pageString

def scrapeEmail(soup):
    # collect email by looking through entire page for letters@letters(.com/.org/.net)
    pageString = getPageString(soup.findAll(True))
    searchMatch = re.findall('[\w\.]+@[\w]+(.com|.net|.org)', pageString)
    return searchMatch

def validateSite(site):
    # find site ending then split based on that ending
    endingMatch = re.search('.com/|.net/|.org/')
    if endingMatch is not None:
        ending = endingMatch.group(0)
    else:
        return None
    splits = site.split(ending)
    # only want results that are the homepage or the about page
    # to avoid sites like Angies list that advertise lists of companies
    if splits[1] == '' or ("about" in splits[1] and len(splits[1].split("/")) < 2):
        #return just the homepage site link
        return (splits[0] + ending)
    else:
        return None

def scrapeAddress(soup):
    #look through entire page for address in form of ## stname sttype town Mass Zip
    addresses = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for stType in zips.streetTypes():
            regex = '(\d+)' + '(\D+)' + re.escape(stType) + '(\D+)' + re.escape(matcher) + '(\d+){5}'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                addresses.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    # get rid of repeats and eliminate any matches that
    # have unwanted data (i.e. phone num before building ##)
    return makeUnique(addresses)

def scrapePOBox(soup):
    #look through entire page for PoBox in form of poBox ## town Mass Zip
    poBoxes = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ']
    poBoxMatchers = [' P.O. box ', ' PO box ',' P.O box ',' PO. box ']
    for matcher in massMatchers:
        for boxMatcher in poBoxMatchers:
            regex = re.escape(boxMatcher) + '(\d+)' + '(\D+)' + re.escape(matcher) + '(\d+){5}'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                poBoxes.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    # get rid of repeats
    return makeUnique(poBoxes)

def scrapeTown(soup):
    #look through entire page for town in form of town mass Zip
    towns = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for town in zips.towns():
            regex = re.escape(town) + re.escape(matcher) + '(\d+){5}'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                towns.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    # get rid of repeats
    return makeUnique(towns)

def getOverLap(str1,str2):
    #Finds the longest overlap between two strings. Finds matching characters
    # then continues forward through both strings and compares to the record.
    record = ""
    for i,let1 in enumerate(str1):
        for j,let2 in enumerate(str2):
            if let1.lower() == let2.lower():
                test1 = let1.lower()
                test2 = let2.lower()
                x = i
                y = j
                word = []
                while test1 == test2:
                    word.append(str1[x])
                    x = x + 1
                    y = y + 1
                    if x > (len(str1) - 1) or y > (len(str2) - 1):
                        break
                    test1 = str1[x].lower()
                    test2 = str2[y].lower()
                if len(word) > len(record):
                    record = word
    return ''.join(record)

def scrapeCompanyNameTitle(titleSoup,referenceSoup):
    # called by scrapeCompName 2nd/3rd option for compName
    # find longest string that is in both homepage title and the reference
    # page contents
    title = titleSoup.findAll('title')
    if len(title) > 0:
        titleString = getStringNoSpaces(title[0].text)
    else:
        return None
    refString = getPageString(referenceSoup.findAll(True))
    return getOverLap(titleString,refString)

def scrapeCompNameCopyright(homepageSoup):
    #primary step to find comp name called by scrapeCompName
    tags = getGoodTags(homepageSoup.findAll(True))
    eligibleCopyright = []
    #pull out any text that contains "copyright" or "all rights reserved"
    for tag in tags:
        if re.search("copyright|all rights reserved|\xA9",tag.text,re.I):
            if re.search("\{|\}",tag.text,re.I):
                # Eliminate any accidental javascript
                continue
            else:
                eligibleCopyright.append(tag.text)
        else:
            continue
    if eligibleCopyright != []:
        # if there are copyright strings, take out any copies and use longest one
        # to pull comp name from
        strings = list(dict.fromkeys(eligibleCopyright))
        copyrightString = max(strings,key=len)
        # copyright usually goes "copyright (symbol) year compName" so searching
        # for the year and any other non alphabetical characters following it (|,- etc.)
        match = re.search('(\d+)[^a-z]+',copyrightString,re.I)
        if match is not None:
            # widdle the string down by chopping off copyright and year part
            # search for all characters up until .,;| -> the characters are returned
            # as the company name
            newString = copyrightString[match.span()[1]:]
            nameMatch = re.search('[^.,;\|]+',newString,re.I)
            if nameMatch is not None:
                return newString[nameMatch.span()[0]:nameMatch.span()[1]]
        else:
            # do same thing as if match hit but instead of looking after the year
            # the compName is found between "copyright"/symbol and the first deliminating
            # character (.,;| etc.)
            noYearMatch = re.search('(\xA9|copyright)[^a-z]+',copyrightString,re.I)
            if noYearMatch is not None:
                newString = copyrightString[noYearMatch.span()[1]:]
                nameMatch = re.search('[^.,;\|]+',newString,re.I)
                if nameMatch is not None:
                    return newString[nameMatch.span()[0]:nameMatch.span()[1]]
    return None

def scrapeCompName(homepageSoup,contSoup=None):
    compNameCopyright = scrapeCompNameCopyright(homepageSoup)
    if compNameCopyright:
        return compNameCopyright
    # If searching through copyright strings fail, find company name by
    # finding the longest overlap between the homepage title and
    # the contact page
    if contSoup is not None:
        compName = scrapeCompanyNameTitle(homepageSoup,contSoup)
        if compName is not None:
            return compName
    # If title/contact does not work. find longest match between homepage
    # title and homepage content
    compName = scrapeCompanyNameTitle(homepageSoup,homepageSoup)
    if compName is not None:
        return compName
    return None

def getTownFromLoc(locArray):
    # Loops through all towns in mass and finds match in the location.
    # find longest so as to match "East Bridgewater" and not just "Bridgewater"
    locTowns = []
    for loc in locArray:
        record = ""
        for town in zips.towns():
            if town.lower() in loc.lower() and len(town) > len(record):
                record = town
            else:
                continue
        locTowns.append(record)
    return locTowns

def getZipFromLoc(locArray):
    # Loops through all zips in mass and finds match in the location.
    locZips = []
    for loc in locArray:
        for zip in zips.zips():
            if zip in loc:
                locZips.append(zip)
    return locZips

def printEmails(emails,index,infoCol,emailCol,workbook):
    infoNames = ["info","office","marketing","sales"]
    nonInfoNum = 0
    for email in emails:
        emailName = email.split("@")[0]
        infoEmail = False
        for starter in infoNames:
            if starter == emailName:
                workbook.write(index,infoCol,email)
                infoEmail = True
        if infoEmail:
            continue
        else:
            col = emailCol + nonInfoNum
            workbook.write(index,col,email)
            nonInfoNum = nonInfoNum + 1

    return 0
