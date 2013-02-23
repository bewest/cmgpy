'''
Define some generic base classes that will be inherited by actual
AT commands
'''

class BasicATCommand():
    """
    Send an AT command and grab the response. This approach is
    heavily influenced by bewest's unapy stuff.
    The class name is the command we send
    """
    response = None
    isQuery = False
    followedUp = False
    requiresFollowUp = False
    requiresCRLF = True
    def __init__(self, cmd=None):
        """
        Turn the class name into a string formatted as follows:
        cmd = 'AT+' followed by class name
        If there was a string passed in then use that as execString
        """
        if cmd is None:
            self.execString = 'AT+' + self.__class__.__name__ + '\r \n'
        else:
            self.execString = cmd

    def parseResponse(self, response):
        '''
        For nicely formatted AT commands that we know of, parse 
        them nicely  and put everything in something like a dict 
        so it's easy for the world to get k,v pairs fromm the 
        response
        '''
        # typical to get something like '\r\nOK\r\n'
        response.text = response.raw.strip('\r\n')
        return response

class OptionsATCommand(BasicATCommand):
    '''
    An AT command with options. The command must define a parseOpts
    method. That formats options to a proper AT string
    command.test() tests for acceptable values (appends =?)
    '''
    def __init__(self, **kwargs):
        """
        Turn the class name into a string formatted as follows:
        cmd = 'AT+' followed by class name
        """
        try:
            self.execString = 'AT+' + self.__class__.__name__
        except:
            pass
            #raise('Tried to use OptionsATCommand with out inheritance')

        if kwargs is not None:
            self.parseOpts( **kwargs)
        
    def parseOpts(self, options):
        ''' virtual method - must override '''

    def test(self):
        self.execString += '=?'
        return self.execString

class QueryableATCommand(BasicATCommand):
    '''
    A queryable command. call command.query() to put a ? on the end
    of the execString
    '''
    def query(self):
        self.execString += '?'
        self.isQuery = True
        return self

        


