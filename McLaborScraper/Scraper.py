from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
from McLaborScraper.inc.zips import towns,zips,streetTypes
import json

def getContactPage(site,siteSoup):
    #get ending of website (.com,.org,.net,...)
    siteEnding = site[-5:-1]
    linkTags = siteSoup.findAll('a', href=True)
    for link in linkTags:
        # Search for any link that contains the word "contact"
        matchCheck = re.search('contact',link['href'],re.I)
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
        if wrapCount[candidate] == 0:
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
    deliminate = re.split('[\(,\),\:,\;,\-,\|,\/,\s*]\s*',str)
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
    searchMatch = re.findall('([a-z]+@\w+\.\w{3})', pageString,re.I)
    return searchMatch

def testSiteEnding(splits):
    if ("about" in splits[1] and (len(splits[1].split("/")) < 2 or splits[1].split("/")[1] == '')):
        return True
    elif ("contact" in splits[1] and (len(splits[1].split("/")) < 2 or splits[1].split("/")[1] == '')):
        return True
    else:
        return False

def validateSite(site):
    # find site ending then split based on that ending
    endingMatch = re.search('.com/|.net/|.org/',site,re.I)
    if endingMatch is not None:
        ending = endingMatch.group(0)
    else:
        return None
    splits = site.split(ending)
    # only want results that are the homepage or the about page
    # to avoid sites like Angies list that advertise lists of companies
    if splits[1] == '' or testSiteEnding(splits):
        #return just the homepage site link
        return (splits[0] + ending)
    else:
        return None
def scrapeAddress(soup):
    #look through entire page for address in form of ## stname sttype town Mass Zip
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for stType in streetTypes():
            regex = '(\d+)' + '(\D+)' + re.escape(stType) + '(\D+)' + re.escape(matcher) + '(\d{5})'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                return searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]]
    # get rid of repeats and eliminate any matches that
    # have unwanted data (i.e. phone num before building ##)
    return None

def scrapePOBox(soup):
    #look through entire page for PoBox in form of poBox ## town Mass Zip
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ']
    poBoxMatchers = [' P.O. box ', ' PO box ',' P.O box ',' PO. box ']
    for matcher in massMatchers:
        for boxMatcher in poBoxMatchers:
            regex = re.escape(boxMatcher) + '(\d+)' + '(\D+)' + re.escape(matcher) + '(\d{5})'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                return searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]]
    # get rid of repeats
    return None

def scrapeTown(soup):
    #look through entire page for town in form of town mass Zip
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for town in towns():
            regex = re.escape(town) + re.escape(matcher) + '(\d{5})'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                return searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]]
    # get rid of repeats
    return None

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
        if re.search("copyright|\xA9",tag.text,re.I):
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
        # the compName is found between "copyright"/symbol and the first deliminating
        # character (.,;|)
        firstMatch = re.search('(\xA9|copyright)[^a-z]+',copyrightString,re.I)
        if firstMatch is not None:
            newString = copyrightString[firstMatch.span()[1]:]
            secondMatch = re.search('(\xA9|copyright)[^a-z]+',newString,re.I)
            if secondMatch is not None:
                finalString = newString[secondMatch.span()[1]:]
            else:
                finalString = newString
            nameMatch = re.search('[^.,;\|]+',finalString,re.I)
            if nameMatch is not None:
                compName = finalString[nameMatch.span()[0]:nameMatch.span()[1]]
                if len(compName) > 40:
                    return None
                return compName
    return None

def scrapeCompNameByClearbit(site):
    startPoint = re.search('//',site).span()[1]
    newString = site[startPoint:]
    if newString[0:3] == "www":
        newString = newString[4:]
    endPoint = re.search('\.\w{3}',newString).span()[1]
    coreSite = newString[:endPoint]
    ClearbitSite = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + coreSite
    try:
        soup = BeautifulSoup(requests.get(ClearbitSite,timeout = 3.0).content,"lxml")
    except:
        return None
    results = soup.find('p').text
    if results != "[]":
        compNameStart = re.search('\"name\":\"',results).span()[1]
        compNameString = results[compNameStart:]
        compName = compNameString[:re.search('\"',compNameString).span()[0]]
        return compName.encode('utf-8').decode('unicode-escape')
    return None

def scrapeCompName(site,homepageSoup=None,contSoup=None):
    compNameClearbit = scrapeCompNameByClearbit(site)
    if compNameClearbit:
        # print("From Clearbit: ",compNameClearbit)
        return getStringNoSpaces(compNameClearbit)
    if homepageSoup == None:
        return None
    compNameCopyright = scrapeCompNameCopyright(homepageSoup)
    if compNameCopyright:
        # print("From Copyright: ",compNameCopyright)
        return getStringNoSpaces(compNameCopyright)
    # If searching through copyright strings fail, find company name by
    # finding the longest overlap between the homepage title and
    # the contact page
    if contSoup is not None:
        compName = scrapeCompanyNameTitle(homepageSoup,contSoup)
        if compName is not None:
            # print("From Title/Contact: ",compName)
            return getStringNoSpaces(compName)
    # If title/contact does not work. find longest match between homepage
    # title and homepage content
    compName = scrapeCompanyNameTitle(homepageSoup,homepageSoup)
    if compName is not None:
        # print("From Title/Homepage: ",compName)
        return getStringNoSpaces(compName)
    return None

def getMailAndTownFromLoc(location):
    # Loops through all towns in mass and finds match in the location.
    # find longest so as to match "East Bridgewater" and not just "Bridgewater"
    record = ""
    mailingAddress = ""
    for town in towns():
        potMatch = re.search(town,location,re.I)
        if potMatch and (potMatch.span()[1] - potMatch.span()[0]) > len(record):
            record = location[potMatch.span()[0]:potMatch.span()[1]]
            mailingAddress = getStringNoSpaces(location[:potMatch.span()[0]])
        else:
            continue
    return [mailingAddress,record]

def getZipFromLoc(location):
    # Loops through all zips in mass and finds match in the location.
    for zip in zips():
        if zip in location:
            return zip
    return ""


def scrapeBestAddress(soup,shouldScrapeTown = False):
    bestAddress = scrapeAddress(soup)
    if bestAddress is not None:
        return bestAddress
    bestAddress = scrapePOBox(soup)
    if bestAddress is not None:
        return bestAddress
    if shouldScrapeTown:
        bestAddress = scrapeTown(soup)
        if bestAddress is not None:
            return bestAddress
    return None

def scrapePhoneNumber(soup):
    pageString = getPageString(soup.findAll(True))
    phoneNumMatch = re.search('(\d{3} \d{3} \d{4})',pageString)
    if phoneNumMatch != None:
        phoneNum = phoneNumMatch.string[phoneNumMatch.span()[0]:phoneNumMatch.span()[1]]
        finalNums = "(" + phoneNum[0:3] + ")" + phoneNum[3:7] + "-" + phoneNum[8:12]
        return finalNums
    return None

def getMinutesSeconds(totalSeconds):
    seconds = totalSeconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02d:%02d" % (minutes, seconds)
