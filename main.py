#!/usr/bin/env python
import os
import sys
from twisted.internet import reactor
import django
from django.conf import settings

from TwistedApp import server

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GlobalSettings.settings")
    django.setup(set_prefix=False)
    
    reactor.listenTCP(settings.SERVICE_PORT, server.LoggerFactory())
    reactor.run()
