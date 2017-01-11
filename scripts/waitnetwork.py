#!.virtualenv/bin/python
# -*- coding: utf-8 -*-
'''
Simple Python Wait for the Network to be online enough to start a server...
'''

from __future__ import print_function

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Wait for Network...

def test_network(times=10):

    from socket import socket, gaierror, NI_NUMERICSERV, getnameinfo
    from time import sleep

    for i in range(times):
        try:
            print(getnameinfo(socket().getsockname(), NI_NUMERICSERV))

            print("Network Online, continuing")
            break
        except gaierror:
            print("Network not available... Trying again (%s of %s)" % (i, times))
            sleep(1)


if __name__ == '__main__':
    test_network()
