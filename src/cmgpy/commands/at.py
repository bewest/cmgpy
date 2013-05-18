'''
Define some AT commands and how to interpret their responses
'''

import re
from generic_commands import *


# sanity check, so we can do modem.AT.sanity to send `AT` to modem
# Should get back OK
class sanity(BasicATCommand):
    ''' sanity check: send AT '''
    def __init__(self):
        self.execString='AT'
    
class cmgf(OptionsATCommand, QueryableATCommand):
    ''' 
    Message Format
    AT+CMGF[=<mode>] 
    AT+CMGF?
    AT+CMGF=?
    Parameter:
    <mode>
    0 - PDU mode, as defined in GSM 3.40 and GSM 3.41 (factory default)
    1 - text mode
    '''
    def parseOpts(self, mode):
        self.execString = self.execString + '=%s'%mode
        
class cfun(OptionsATCommand, QueryableATCommand):
    '''
    Set Phone Functionality
    AT+CFUN[=<fun>[,<rst>]]
    AT+CFUN?
    AT+CFUN=?
    Parameters:
    <fun> (functionality)
        0 - minimum (sleep)
        1 - mobile full functionality without powersave
        2 - disable tx
        4 - disable tx and rx
        5 - mobile full functionality with powersave
        7 - cyclic sleep
        9 - 0, with different wakeups
    <rst> (reset)
        0 - do not reset before setting <fun>
        1 - reset before setting <fun>
    '''
    def parseOpts(self, fun=None, rst=None):
        if fun is None: # this should mean doing test or query
            pass
        elif rst is None: # rst is optional
            self.execString = self.execString + '=%s'%(fun)
        else: 
            self.execString = self.execString + '=%s,%s'%(fun,rst)

    def parseTestResponse(self, response):
        '''
        response to a test looks like this:
        \r\n+CFUN: (0,1,4),(0-1)\r\n\r\nOK\r\n
        '''
        pass

        
    def parseQueryResponse(self, response):
        '''
        response to a query looks like
        \r\n+CFUN: 1\r\n\r\nOK\r\n
        '''
        respList = response.raw.split('\r\n')
        response.cfun = respList[1].split(' ')[1]
        return response


class csca(OptionsATCommand, QueryableATCommand):
    '''
    Service Center Address
    AT+SCSA[=<number>[,<type]]
    AT+SCSA?
    AT+SCSA=?
    Parameters:
    <number> (service center)
    <type> 
        129 - national numbering scheme
        145 - international numbering scheme (contains the character "+")
    '''
    def parseOpts(self, sca=None, ntype=None):
        if sca is None:
            pass
        elif ntype is None:
            self.execString = self.execString + '=%s'%sca
        else:
            self.execString = self.execString + '=%s,'%sca
        return self

    def parse(self, response):
        print response
        
    def parseQueryResponse(self, response):
        '''
        response to a query looks like
        \r\n+CSCA: "+XXXXXXXX",145\r\n\r\nOK\r\n
        '''
        respList = response.raw.split('\r\n')
        foo = respList[1].split(' ')[1]
        response.num = foo.split(',')[0]
        response.ntype = foo.split(',')[1]
        return response

class cmgs(OptionsATCommand, QueryableATCommand):
    '''
    Message Sending and Writing
    AT+CMGS=<da>[,<toda>]
    da - destination address
    toda - type of destination address
    '''
    def parseOpts(self, da=None, toda=None, msg=None):
        self.requiresFollowUp = True
        self.followedUp = False
        self.requiresCRLF = False
        if da is None: # error
            raise("cgms is missing destination address (DA)")
        elif toda is None: #toda is optional
            self.execString = self.execString + "=\"%s\""%da
        else: # toda is there
            self.execString = self.execString + "=\"%s\",%s"%(da,toda)
        if msg is not None:
            self.msg = msg
        return self
        
    def followUp(self, response):
        '''
        The modem should respond with >
        Then send the message followed by ctrl+z (0x1a)
        '''
        self.followedUp = True
        self.requiresCRLF = True
        # First check if we got '>'
        if response.text.__contains__('>'):
            self.execString = self.msg + '\x1a'
        else:
            raise("Did not receive >")
        return self
    def parseFollowUpResponse(self, response):
        '''
        Parse the response to a followup command. Looks like this:
        +CMGS: 24
        
        OK
        Send back a member called cmgs with value of #.
        '''
        respList = response.text.split('\r\n')
        # ['', '+CMGS: 24', '', 'OK', '']
        cmgsPart = respList[1].split(' ')
        # set self.response.CMGS = 24
        setattr(response, cmgsPart[0][1:-1], cmgsPart[1])
        return response
        
class cmgl(OptionsATCommand, QueryableATCommand):
    '''
    Message listing (SMS)
    AT+CMGL=<stat>
    stat is a string specifying the types of messgae to return
    '''
    def parseOpts(self, stat='REC UNREAD', debug=False):
        '''
        By default return the unread incoming messages
        But can accept any of the following strings
        "REC UNREAD", "REC READ", "STO UNSENT", "STO SENT", "ALL"
        '''
        self.execString += '="%s"' % stat
        self.debug = debug
        
    def parseResponse(self, response): 
        '''
        we might get a lot of stuff. It will either be an error
        or a list of messages of some category
        For example:
        +CMGL: 12,"REC READ","1410000001",,"13/02/05,19:58:09-24"
        FRM:Earle West 
        SUBJ:test
        MSG:test
        +CMGL: 13,"REC READ","1410000002",,"13/02/05,20:06:57-24"
         1 of 2
        FRM:Earle West 
        SUBJ:POLLING YOU
        MSG:7328584026@txt.att.net
        curl --request POST 'http://transactionalweb.com/mconnect.php'
        (Con't)
        +CMGL: 14,"REC READ","1410000002",,"13/02/05,20:06:58-24"
         2 of 2
        --data
        'postedcontent=<key>12345656667</key><hot stuff>blah blah blah</hotstuff>'(End)
        +CMGL: 15,"REC READ","1410080001",,"13/02/07,08:51:48-24"
        Your MSG could not be DELIVERED because InvalidPduContent
        
        OK

        '''
        debugString = response.raw.replace('\r','\\r').replace('\n','\\n')
        unprocessedMessagesList = re.split('\r\n\+|\r\nOK',response.raw)
        sms = re.compile('CMGL: (?P<cmgl>[0-9]*),'+ #cmgl number
                        '"(?P<stat>[A-Z ]*)",'+ #status
                        '"(?P<da>\+?[0-9]*)",,'+ #address (dst or src)
                        '"?(?P<date>[0-9,/:\-]*)"?'+#date sent, optional
                        '\r\n(?P<message>.*)', # the rest is the message
                        re.DOTALL) # flags
        response.messageList = list()
        for message in unprocessedMessagesList:
            matches = sms.match(message)
            if matches is not None:
                response.messageList.append(matches.groupdict())
        response.text = 'OK'
        
        #############################################################
        # this exists for debugging purposes so that I don't waste  #
        # SMS debugging something downstream that depends on this   #
        #                                                           #
        #                                                           #
        # if self.debug:
        # 	response.messageList.append({'cmgl':18,                     #
        # 	                        'stat':'REC UNREAD',                #
        # 	                        'da':'1410000005',                  #
        # 	                        'message':'FRM:Nathan West\nSUBJ:conf\nMSG:STR http://commlablaptop.ceat.okstate.edu/index.html\n'})
        #                                                           #
        #                                                           #
        #############################################################
        

        return response

class cmgd(OptionsATCommand):
    '''
    Delete SMS
    AT+CMGD=<index>[,<flag>]
    <index> is the index of a single SMS
    <flag> can ignore the index and target a kind of message
        0 - use <index>
        1 - ignore <index>, delete REC READ
        2 - ignore <index>, delete REC READ, STR SENT
        3 - ignore <index>, delete REC READ, STR SENT, STR UNSENT
        4 - ignore <index>, delete everything
    '''
    def parseOpts(self, index, flag=0):
        self.execString += '=%s,%s' % (index, flag)


class cmgr(OptionsATCommand, QueryableATCommand):
    '''
    Message Reader
    AT+CMGR=<index>
    return the message specified by <index>
    '''
    def parseOpts(self, index):
        '''
        By default return the unread incoming messages
        But can accept any of the following strings
        "REC UNREAD", "REC READ", "STO UNSENT", "STO SENT", "ALL"
        '''
        self.execString += '=%s' % index

    def parseResponse(self, response):
        '''
        A typical response looks like this:
        +CMGR: "REC READ","1410000002",,"13/02/05,20:06:58-24"
        --data
        'postedcontent=<key>12345656667</key><hot stuff>blah blah blah</hotstuff>'(End)
        this work was already implemented in cmgl, so I'll just copy that
        '''
        debugString = response.raw.replace('\r','\\r').replace('\n','\\n')
        sms = re.compile('\r\n\+CMGR: '+ #cmgr 
                        '"(?P<stat>[A-Z ]*)",'+ #status
                        '"(?P<da>\+?[0-9]*)",'+ #address (dst or src)
                        '"?(?P<date>[0-9,/:\-]*)"?'+#date sent, optional
                        '\r\n(?P<message>.*)', # the rest is the message
                        re.DOTALL) # flags
        matches = sms.match(response.raw)
        response.message = matches.groupdict()
        return response


#EOF
