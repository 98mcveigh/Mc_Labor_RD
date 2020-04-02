from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re
import zips

def getContactPage(site,siteSoup):
    siteEnding = site[-5:-1]
    linkTags = siteSoup.findAll('a', href=True)
    for link in linkTags:
        matchCheck = re.search('contact',link['href'])
        if matchCheck is not None:
            if siteEnding in matchCheck.string and site != matchCheck.string:
                return matchCheck.string
            else:
                return site + matchCheck.string
        else:
            continue
    return None

def makeUnique(lis):
    wrapCount = dict.fromkeys(lis)
    for key in wrapCount:
        wrapCount[key] = 0
    for emailCandidate in lis:
        for wrapperCandidate in lis:
            if emailCandidate in wrapperCandidate and emailCandidate != wrapperCandidate:
                wrapCount[wrapperCandidate] = wrapCount[wrapperCandidate] + 1
    final = []
    for candidate in wrapCount:
        if wrapCount[candidate] is 0:
            final.append(candidate)

    return list(dict.fromkeys(final))

def isEmail(emailCand,siteEnding):
    candEnding = emailCand[-4:]
    if "@" in emailCand and emailCand[0] != "@":
        if candEnding == siteEnding:
            return True
        else:
            return False
    else:
        return False

def isAllowedToScrape(site,soup):
    title = soup.find('title')
    if title is not None and ("403" in title.text or "Not Acceptable!" in title.text):
        return False
    else:
        return True

def scrapeEmail(soup):
    pageString = getPageString(soup.findAll(True))
    searchMatch = re.findall(r'[\w\.]+@[\w\.]+', pageString)
    return searchMatch

def validateSite(site):
    splits = site.split(".com/")
    if len(splits) < 2:
        splits = site.split(".net/")
        if len(splits) < 2:
            splits = site.split(".org/")
            if len(splits) < 2:
                return None
            else:
                ending = ".org/"
        else:
            ending = ".net/"
    else:
        ending = ".com/"

    if splits[1] == '' or ("about" in splits[1] and len(splits[1].split("/")) < 2):
        return (splits[0] + ending)
    else:
        return None

def scrapePOBox(soup):
    poBoxes = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ']
    poBoxMatchers = [' P.O. box ', ' PO box ',' P.O box ',' PO. box ']
    for matcher in massMatchers:
        for boxMatcher in poBoxMatchers:
            regex =re.escape(boxMatcher) + '(\d+)' + '(\D+)' + re.escape(matcher) + '(\d+)'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                poBoxes.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    return poBoxes

def scrapeAddress(soup):
    addresses = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for stType in zips.streetTypes():
            regex = '(\d+)' + '(\D+)' + re.escape(stType) + '(\D+)' + re.escape(matcher) + '(\d+)'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                addresses.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    return makeUnique(addresses)

def scrapeTown(soup):
    towns = []
    pageString = getPageString(soup.findAll(True))
    massMatchers = [' MA ',' massachusetts ',' ma. ']
    for matcher in massMatchers:
        for town in zips.towns():
            regex = re.escape(town) + re.escape(matcher) + '(\d+)'
            searchMatch = re.search(regex,pageString,re.I)
            if searchMatch is not None:
                towns.append(searchMatch.string[searchMatch.span()[0]:searchMatch.span()[1]])
    return makeUnique(towns)

def getPageString(tagList):
    # TODO: make sure this still works for all other functions
    goodContents = []
    test = []
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
        elif tag.name == "hmtl":
            continue
        elif tag.name == "head":
            continue
        elif tag.name == "body":
            continue
        elif tag.name == "title":
            continue
        else:
            if re.search('[\{|\}|\<|\>]',tag.text):
                continue
            else:
                for word in re.split('[-,\s]\s*',tag.text):
                    goodContents.append(word)
    semiDoneString = ' '.join(goodContents)
    pageString = getStringNoSpaces(semiDoneString)
    return pageString

def getGoodTags(tagList):
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
        elif tag.name == "hmtl":
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

def getOverLap(str1,str2):
    # TODO: miiiight be able to make this faster with recursion?
    record = []
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

def getStringNoSpaces(str):
    deliminate = re.split('[\:,\;,\-,\|,\/,\s*]\s*',str)
    cleanWords = []
    for word in deliminate:
        if word == '':
            continue
        else:
            cleanWords.append(word)
    return ' '.join(cleanWords)

def scrapeCompanyNameByTitle(titleSoup,referenceSoup):
    title = titleSoup.findAll('title')
    if len(title) > 0:
        titleString = getStringNoSpaces(title[0].text)
    else:
        return None
    refString = getPageString(referenceSoup.findAll(True))
    return getOverLap(titleString,refString)

def scrapeCompNameByCopyrightOrTitle(site,homepageSoup,contSoup=None):
    tags = getGoodTags(homepageSoup.findAll(True))
    eligibleCopyright = []
    for tag in tags:
        if re.search("copyright|all rights reserved|\xA9",tag.text,re.I):
            if re.search("\{|\}",tag.text,re.I):
                continue
            else:
                eligibleCopyright.append(tag.text)
        else:
            continue
    if eligibleCopyright != []:
        strings = makeUnique(eligibleCopyright)
        if strings != []:
            copyrightString = max(strings,key=len)
            match = re.search('(\d+)[^a-z]+',copyrightString,re.I)
            if match is not None:
                newString = copyrightString[match.span()[1]:]
                goodSpan = re.search('[^.,;\|]+',newString,re.I).span()
                return newString[goodSpan[0]:goodSpan[1]]
            else:
                noYearMatch = re.search('(\xA9|copyright)[^a-z]+',copyrightString,re.I)
                if noYearMatch is not None:
                    newString = copyrightString[noYearMatch.span()[1]:]
                    goodSpan = re.search('[^.,;\|]+',newString,re.I).span()
                    return newString[goodSpan[0]:goodSpan[1]]
        if contSoup is not None:
            # print("couldnt go by copyright doing title/contact...")
            compName = scrapeCompanyNameByTitle(homepageSoup,contSoup)
            if compName is not None:
                return compName
            else:
                # print("couldnt go by title/contact doing title/homepage...")
                compName = scrapeCompanyNameByTitle(homepageSoup,homepageSoup)
                if compName is not None:
                    return compName
                else:
                    return None
        else:
            # print("couldnt go by title/contact doing title/homepage...")
            compName = scrapeCompanyNameByTitle(homepageSoup,homepageSoup)
            if compName is not None:
                return compName
            else:
                return None
    else:
        # print("no eligible copyright")
        if contSoup is not None:
            # print("couldnt go by copyright doing title/contact...")
            compName = scrapeCompanyNameByTitle(homepageSoup,contSoup)
            if compName is not None:
                return compName
            else:
                # print("couldnt go by title/contact doing title/homepage...")
                compName = scrapeCompanyNameByTitle(homepageSoup,homepageSoup)
                if compName is not None:
                    return compName
                else:
                    return None
        else:
            # print("couldnt go by title/contact doing title/homepage...")
            compName = scrapeCompanyNameByTitle(homepageSoup,homepageSoup)
            if compName is not None:
                return compName
            else:
                return None

def getTownFromLoc(locArray):
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
