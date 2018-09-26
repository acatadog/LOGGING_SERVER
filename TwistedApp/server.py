#!/usr/bin/env python
import os, sys, logging, pickle, struct

from twisted.internet.protocol import Protocol, Factory

logger = logging.getLogger('default')
loggerRemote = logging.getLogger('remote')

class LoggerProtocol(Protocol):
    LONG_INT_LENGTH = 4
    
    def __init__(self):
        """
        """
        self._buffer = b""

    def connectionMade(self):
        """
        """
        self.factory.connections += 1
        logger.info( f'Got connection from {self.transport.client}, count = {self.factory.connections}' )

    def connectionLost(self, reason):
        """
        """
        self.factory.connections -= 1
        logger.info( f'{self.transport.client} disconnected, count = {self.factory.connections}' )

    def dataReceived(self, data):
        """
        """
        logRecord = None 
        
        # get an alias to the LONG_INT_LENGTH
        long_int_length = self.LONG_INT_LENGTH
        
        # paste the recieved data onto what we have
        self._buffer += data

        # keep processing the buffer till we need more data
        done = False
        while not done:
            # do we have enough data to pull off the leading big 
            # endian long integer?
            if len(self._buffer) >= long_int_length:
                length = struct.unpack(">L", self._buffer[:long_int_length])[0]
                
                # do we have the complete logging message?
                if len(self._buffer) >= long_int_length + length:
                    # get the pickled log message
                    logPickle = self._buffer[long_int_length : long_int_length + length]
                    oneLog = pickle.loads(logPickle)
                    oneLog["host"] = self.transport.client[0]
                    oneLog["port"] = self.transport.client[1]
                    logRecord = logging.makeLogRecord(oneLog)
                    
                    # do we have a logrecord?, then handle it
                    if logRecord:
                        loggerRemote.handle(logRecord)

                    # update the class buffer with what we have left
                    self._buffer = self._buffer[long_int_length + length:]
                    
                # otherwise, we don't have a complete message
                else:
                    done = True
            # otherwise, don't have enough data for length value
            else:
                done = True

class LoggerFactory(Factory):
    protocol = LoggerProtocol
    
    def __init__(self):
        """
        """
        self.connections = 0


