import re
str1 = "mc Labor Sources is copyright"
str2 = "Mc Labor Sources"
print(len(str2))
def getOverLap(str1,str2):
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
