
import serial
import commands
import time




class Modem():
    """
    This implements a modem that we will be communicating with.
    In general we provide a generic AT interface from python, 
    but we want to do a few specific tasks such as handling SMS
    cleanly and at a higher level.
    """
    def __init__(self, port=0, baud=115200):
        """ set up the modem with location and baud """
        self.port=port
        self.baud=baud
        # we could basically add all of serial.Serial's commands in here
        self.connection = serial.Serial(port, baud, timeout=2)
        self.connection.open()

    def settings(self):
        """ print the settings of the modem """
        print("modem location %s" % self.port)
        print("baud rate %s" % self.baud)

    def send(self, commandString):
        self.lastCommand = commandString
        self.connection.write(commandString)
        self.connection.flush()

    def receive(self):
        resp = ''
        self.response = self.connection.readlines()
        for line in self.response:
            resp += line
        # for line in self.connection.readline():
        #     resp += line
        #     time.sleep(.25)
        return resp

    def AT(self, command):
    	""" 
    	send an AT command to the modem and fetch the response.
    	the command is either an object with the name of the AT 
    	command or it is a string with a complete command and 
    	options. 

    	If it is an object:
    	return an object response:
    	    text - the text response from the modem
    	    rval - -1 (fail/error), 1 (success/OK)
    	    response - if there's a useful data structure to response 
    	            that we are aware of
    	Otherwise, it is a string and (theoretically) unknown to me
    	return an object response:
    	    text - the text response from the modem
    	    rval - 0 (fail/error), 1 (success/OK)
    	"""
        self.ATResponse = Response()
        if isinstance(command, str):
            self.ATResponse = self.handleATString(command)
        else:
            self.ATResponse = self.handleATObject(command)
        return self.ATResponse

    def handleATObject(self, ATCommand):
        '''
        Take in an object ATCommand that is named after a real AT
        command (for instance D for AT+D) called execString. This 
        object should have a string containing the actual command 
        (without the AT+) along with members specifying the 
        parameters, if any
        '''
        self.ATResponse = self.handleATString(ATCommand.execString, requiresCRLF=ATCommand.requiresCRLF)
        self.ATResponse = ATCommand.parseResponse(self.ATResponse)

        if ATCommand.isQuery == True and self.ATResponse.rval == True:
            self.ATResponse = ATCommand.parseQueryResponse(self.ATResponse)

        if ATCommand.requiresFollowUp == True and self.ATResponse.rval == True:
            #ollow up should respond with ATCommand obj with new execString
            ATCommand = ATCommand.followUp(self.ATResponse)
            self.ATResponse = self.handleATString(ATCommand.execString, 
                                    requiresCRLF=ATCommand.requiresCRLF)
            self.ATResponse = ATCommand.parseFollowUpResponse(self.ATResponse)

        return self.ATResponse

    def handleATString(self, ATString, requiresCRLF=True):
        ''' Receive a string, AT ready. Return response '''
        self.send(addCRLF(ATString, requiresCRLF))
        self.ATResponse.raw = self.receive()
        if self.ATResponse.raw.__contains__('ERROR'):
            # error
            self.ATResponse.rval = -1
        else:
            # success
            self.ATResponse.rval = 1
        # slightly redundant debug, but can't hurt
        return self.ATResponse

class Response:
    pass

def addCRLF(ATString, requiresLF):
    if requiresLF:
        return ATString + '\r'
    else: 
        return ATString + '\r \n'

