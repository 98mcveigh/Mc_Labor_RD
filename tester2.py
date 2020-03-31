import re
strs = ['Give us a call!', '', 'Boston Lightning Rod Co., Inc.', '\r\n                            1201 East Street\r\n                        ', '\nDedham, \r\n                             MA\n02027\n', 'Dedham', 'MA', '02027', 'Tel: 800-992-3466', '800-992-3466', '\n\nE-Mail:\npmwjr@blrco.net\n']
for str in strs:
    if re.search('[\{|\}|\<|\>]',str):
        print(re.search('[\{,\},\<,\>]',str))
        print(str + " does not work")
