
import logging
import sys

streamHandler = logging.StreamHandler(sys.stdout)

loggerConfig = { "Window" : logging.DEBUG,
                 "default" : logging.DEBUG }

def getLogger(name):
    logger = logging.getLogger(name)
    logger.addHandler(streamHandler)
    logger.setLevel(loggerConfig[name])
    return logger
