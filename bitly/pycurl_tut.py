#PyCurl example
#June 5th, 2012
# David Kang

import pycurl
import cStringIO
import urllib

#buf = cStringIO.StringIO()


c = pycurl.Curl()
c.setopt(c.URL, 'https://api-ssl.bitly.com/oauth/access_token')
#c.setopt(c.VERBOSE, True)

#c.setopt(c.WRITEFUNCTION, buf.write)
c.setopt(c.HTTPHEADER, ["Accept: application/json"])
c.setopt(c.HTTPHEADER, ["Content-Type : application/x-www-form-urlencoded"])

c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, '{:}')
c.setopt(c.SSL_VERIFYPEER, False)
c.setopt(c.USERPWD, "dkang9322:123dkangA")

c.perform()

