import sys
import os

if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    
from moteProbe     import moteProbe
from moteConnector.SerialTester import SerialTester
from OpenCli       import OpenCli

LOCAL_ADDRESS     = '127.0.0.1'
TCP_PORT_START    = 8090
MAX_BYTES_TO_SEND = 50

class serialTesterCli(OpenCli):
    
    def __init__(self,moteProbe_handler,moteConnector_handler):
        
        # store params
        self.moteProbe_handler     = moteProbe_handler
        self.moteConnector_handler = moteConnector_handler
    
        # initialize parent class
        OpenCli.__init__(self,"Serial Tester",self._quit_cb)
        
        # add commands
        self.registerCommand('pklen',
                             'pl',
                             'test packet length, in bytes',
                             ['pklen'],
                             self._handle_pklen)
        self.registerCommand('numpk',
                             'num',
                             'number of test packets',
                             ['numpk'],
                             self._handle_numpk)
        self.registerCommand('timeout',
                             'tout',
                             'timeout for answer, in seconds',
                             ['timeout'],
                             self._handle_timeout)
        self.registerCommand('trace',
                             'trace',
                             'activate console trace',
                             ['on/off'],
                             self._handle_trace)
        self.registerCommand('testserial',
                             't',
                             'test serial port',
                             [],
                             self._handle_testserial)
        self.registerCommand('stats',
                             'st',
                             'print stats',
                             [],
                             self._handle_stats)
        
        # by default, turn trace on
        self._handle_pklen([10])
        self._handle_numpk([1])
        self._handle_timeout([1])
        self._handle_trace([1])
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== CLI command handlers
    
    def _handle_pklen(self,params):
        self.moteConnector_handler.setTestPktLength(int(params[0]))
    
    def _handle_numpk(self,params):
        self.moteConnector_handler.setNumTestPkt(int(params[0]))
    
    def _handle_timeout(self,params):
        self.moteConnector_handler.setTimeout(int(params[0]))
    
    def _handle_trace(self,params):
        if params[0] in [1,'on','yes']:
            self.moteConnector_handler.setTrace(self._indicate_trace)
        else:
            self.moteConnector_handler.setTrace(None)
    
    def _handle_testserial(self,params):
        self.moteConnector_handler.test(blocking=False)
    
    def _handle_stats(self,params):
        stats = self.moteConnector_handler.getStats()
        output  = []
        for k in ['numSent','numOk','numCorrupted','numTimeout']:
            output += ['- {0:<15} : {1}'.format(k,stats[k])]
        output  = '\n'.join(output)
        print output
    
    def _indicate_trace(self,debugText):
        print debugText
    
    #===== helpers
    
    def _quit_cb(self):
        self.moteConnector_handler.quit()
        self.moteProbe_handler.quit()

def main():
    
    moteProbe_handler        = None
    moteConnector_handler    = None
    
    # find serial port
    if len(sys.argv)>1:
        serialPort = sys.argv[1]
    else:
        serialPort = moteProbe.utils.findSerialPorts()[0]
    serialPort     = ('COM136', 115200)
    tcpPort        = TCP_PORT_START
    
    # create a moteProbe
    moteProbe_handler = moteProbe.moteProbe(serialPort,tcpPort)
    
    # create a SerialTester to attached to the moteProbe
    moteConnector_handler = SerialTester(
                                LOCAL_ADDRESS,
                                moteProbe_handler.getTcpPort(),
                                serialPort[0]
                            )
    
    # create an open CLI
    cli = serialTesterCli(moteProbe_handler,moteConnector_handler)
    
    # start threads
    #moteConnector_handler.start()
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('serialTesterCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in [
                   'SerialTester',
                   'moteProbeSerialThread',
                   'OpenHdlc',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()