#!/usr/bin/python

import pymodem
at = pymodem.commands.at

icon322 = pymodem.Modem('/dev/ttyHS0', 115200)

result = icon322.AT(at.sanity())

result = icon322.AT(at.cmgf(mode=1))
result = icon322.AT(at.cfun(fun=1))

result = icon322.AT(at.cmgs(da="121", msg="nate.ewest@gmail.com (test) SMS to email from python"))
