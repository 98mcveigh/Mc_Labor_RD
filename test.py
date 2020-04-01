import Scraper
from bs4 import BeautifulSoup
from googlesearch import search
from lxml import html
import requests
import re

# query = "electrical contractors quincy ma"
# goodSites = []
# for site in search(query, tld='com', lang='en', num=10, start=0, stop=50, pause=2.0):
#     siteValidity = Scraper.validateSite(site)
#     if siteValidity is not None:
#         print(site)
#         goodSites.append(siteValidity)
#     else:
#         continue
# goodSites = Scraper.makeUnique(goodSites)
# print(goodSites)

sites = ['http://www.johnvespaelectric.com/', 'http://tandgelectrical.com/', 'https://www.mecanews.com/', 'http://www.riordanbrothers.com/', 'http://www.hoelectric.com/', 'https://www.wayneelectriccoinc.com/', 'http://www.jdoelectric.com/', 'https://www.bostonlightningrod.com/', 'https://girouxelectric.com/', 'https://www.electrician-in-boston.net/', 'https://www.lowes.com/', 'https://boucherenergy.com/','http://www.larryselectricalservice.com/', 'http://crockerelectrical.com/', 'http://integratedelectric.com/', 'https://carlosrecinoselectric.com/', 'https://lynnwell.com/', 'https://www.conklinelectric.com/']
# sites = ['http://integratedelectric.com/']
# sites = ['http://www.larryselectricalservice.com/', 'http://crockerelectrical.com/', 'http://integratedelectric.com/', 'https://carlosrecinoselectric.com/', 'https://lynnwell.com/', 'https://www.conklinelectric.com/']
# biglist = []
for site in sites:
    print(site)
    try:
        soup = BeautifulSoup(requests.get(site,timeout=2.0).content,"lxml")
    except:
        continue
    if not Scraper.isAllowedToScrape(site,soup):
        print("Can not scrape")
        continue
    print(Scraper.scrapeCompNameByCopyright(site,soup))
