import xlsxwriter
import Scraper
import re
import requests
from bs4 import BeautifulSoup
emails = ["don@me.com","jack@me.com","mark@me.com"]
test ="https://www.needco.com/"
sites = ["http://beshereelectric.com/","http://www.mouradcorp.com/","https://girouxelectric.com/"]
emailCol = 4
infoCol = 2
index = 3
tester = None

soup = BeautifulSoup(requests.get(test).content,"lxml")

print(Scraper.scrapeCompName(soup))
