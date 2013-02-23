#!/usr/bin/python

import pymodem
import logging
at = pymodem.commands.at

logging.basicConfig(level='DEBUG')
icon322 = pymodem.Modem('/dev/ttyHS0', 115200)

# # test 1
# result1 = icon322.AT('AT')
# assert result1.rval == 1, 'TEST 1 FAILED'
# 
# # test 2
# result2 = icon322.AT(at.sanity())
# assert result2.rval == 1, 'TEST 2 FAILED'
# 
# # test 3
# result3 = icon322.AT(at.cmgf(mode=1))
# assert result3.rval == 1, 'TEST 3 FAILED' 
# 
# # test 4
# result = icon322.AT(at.cfun(fun=1))
# assert result.rval == 1, 'TEST 4 FAILED'
# 
# # test 5
# result = icon322.AT(at.csca().query())
# # if cfun=4, csca? errors.
# assert result.rval == 1, 'TEST 5 FAILED'

# comment out to avoid wasting messages
#result = icon322.AT(at.cmgs(da="+19082165058", msg="Test from pymodem"))

result = icon322.AT(at.cmgl(stat="REC UNREAD"))
messages = result.messageList
for message in messages:
    print " There is a new message!!!!!!!"
    print message

result = icon322.AT(at.cmgl(stat="REC UNREAD") )
print result.text

result = icon322.AT(at.cmgr(index=4))
print result.message
