import McLaborScraper.Scraper as Scraper
import re
import requests
from bs4 import BeautifulSoup

test = "https://gastonelectrical.com/"

soup = BeautifulSoup(requests.get(test).content,"lxml")
contPage = Scraper.getContactPage(test,soup)
contSoup = BeautifulSoup(requests.get(contPage).content,"lxml")
print(Scraper.scrapePhoneNumber(contSoup))
