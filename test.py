import Scraper
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re

# query = "electrical contractors dedham ma"
# goodSites = []
# for site in search(query, tld='com', lang='en', num=10, start=0, stop=100, pause=2.0):
#     siteValidity = Scraper.validateSite(site)
#     if siteValidity is not None:
#         print(site)
#         goodSites.append(siteValidity)
#     else:
#         continue
# goodSites = Scraper.makeUnique(goodSites)
# print(goodSites)

# def scrapeName(site,soup):
#     title = soup.findAll('title')
#     # print(len(title))
#     if len(title) == 1:
#         titleString = Scraper.getStringNoSpaces(title[0].text)
#         print(titleString)
#     else:
#         print("this was longer than one or 0")
#         return "potatoe"
#     tags = Scraper.getGoodTags(soup.findAll(True))
#     eligible = []
#     for tag in tags:
#         if re.search("copyright|all rights reserved|\xA9",tag.text,re.I):
#             if re.search("\{|\}",tag.text,re.I):
#                 continue
#             else:
#                 eligible.append(tag.text)
#     copyrightString = Scraper.makeUnique(eligible)
#     if len(copyrightString) > 0:
#         finalCopyrightString = Scraper.getStringNoSpaces(copyrightString[0])
#         print(finalCopyrightString)
#         print(tester.getOverLap(titleString,finalCopyrightString))


sites = ['http://www.johnvespaelectric.com/', 'http://tandgelectrical.com/', 'https://www.mecanews.com/', 'http://www.riordanbrothers.com/', 'http://www.hoelectric.com/', 'https://www.wayneelectriccoinc.com/', 'http://www.jdoelectric.com/', 'https://www.bostonlightningrod.com/', 'https://girouxelectric.com/', 'https://www.electrician-in-boston.net/', 'https://www.lowes.com/', 'https://boucherenergy.com/']
# sites = ['https://www.bostonlightningrod.com/']
for site in sites:
    try:
        soup = BeautifulSoup(requests.get(site,timeout=2.0).content,"lxml")
    except:
        continue
    contSite = Scraper.getContactPage(site,soup)
    try:
        contSoup = BeautifulSoup(requests.get(contSite,timeout=2.0).content,"lxml")
    except:
        continue
    print(site)
    print(Scraper.scrapeCompanyName(soup))
    print(Scraper.getCompNameTitleContact(soup,contSoup))
