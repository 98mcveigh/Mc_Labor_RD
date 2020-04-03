import xlsxwriter
import Scraper
import re
import requests
from bs4 import BeautifulSoup
emails = ["don@me.com","jack@me.com","mark@me.com"]
num ="617 293 5214"
sites = ["http://beshereelectric.com/","http://www.mouradcorp.com/","https://girouxelectric.com/"]
emailCol = 4
infoCol = 2
index = 3
tester = None

# cleanString = Scraper.getStringNoSpaces(test)
# print(re.findall('(\d{3} \d{3} \d{4})',cleanString))
# print("(" + num[0:3] + ")" + num[3:7] + "-" + num[8:12])
