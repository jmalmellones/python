from subprocess import call
from time import sleep

#     The ping utility exits with one of the following values:
#     0                  At least one response was heard from the specified host.
#     2                  The transmission was successful but no responses were received.
#     any other value    An error occurred.  These values are defined in <sysexits.h>.

def isIphonePresent(iphone_ip):
    result = call(["ping","-c 1", "-W 150", "-q", iphone_ip])
    return result == 0