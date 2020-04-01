import re

str = "\xA9 - 2020 Mc Labor Sources Inc | hahahah"
realTest = ['Copyright MC Labor Sources Inc. All Rights Reserved.','\n©2014-2017 Massachusetts Electrical Contractors Association, Inc. | Maintained by Kingsbury Web', 'Copyright © 2018 - Riordan Brothers Integration', '© JDO Electric, Somerville, MA', '© 2020 Boston Lightning Rod Co., Inc.', 'Copyright © 2019 | Giroux Electrical Contractors | All Rights Reserved', '© 2017 MacEwan Electric, All Rights Reserved', ' © 2018 Boucher Energy Systems, Inc. All Rights Reserved. Site designed by PENTA Communications, Inc.']
# print(re.search('(\d+)[^.,;\|]+',str,re.I)) #matches 2020 Mc Labor Sources Inc

def getCompNameByCopyright(copyrightString):
    print(copyrightString)
    match = re.search('(\d+)[^a-z]+',copyrightString,re.I)
    # print(match)
    if match is not None:
        newString = copyrightString[match.span()[1]:]
        # print(newString)
        goodSpan = re.search('[^.,;\|]+',newString,re.I).span()
        print(newString[goodSpan[0]:goodSpan[1]])
    else:
        noYearMatch = re.search('(\xA9|copyright)[^a-z]+',copyrightString,re.I)
        if noYearMatch is not None:
            newString = copyrightString[noYearMatch.span()[1]:]
            # print(newString)
            goodSpan = re.search('[^.,;\|]+',newString,re.I).span()
            print(newString[goodSpan[0]:goodSpan[1]])

for test in realTest:
    getCompNameByCopyright(test)
