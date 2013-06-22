import imaplib2, time
import gmail_parser
from gmail_parser import gmail_parser
import gmail_connect
from gmail_connect import gmail_imap, since_parser
reload(gmail_connect)
from threading import *
 
# This is the threading object that does all the waiting on 
# the event
class Idler(object):
    def __init__(self, conn):
        self.thread = Thread(target=self.idle)
        self.M = conn
        self.event = Event()
 
    def start(self):
        self.thread.start()
 
    def stop(self):
        # This is a neat trick to make thread end. Took me a 
        # while to figure that one out!
        self.event.set()
 
    def join(self):
        self.thread.join()
 
    def idle(self):
        # Starting an unending loop here
        while True:
            # This is part of the trick to make the loop stop 
            # when the stop() command is given
            if self.event.isSet():
                return
            self.needsync = False
            # A callback method that gets called when a new 
            # email arrives. Very basic, but that's good.
            def callback(args):
                if not self.event.isSet():
                    self.needsync = True
                    self.event.set()
            # Do the actual idle call. This returns immediately, 
            # since it's asynchronous.
            self.M.idle(callback=callback)
            # This waits until the event is set. The event is 
            # set by the callback, when the server 'answers' 
            # the idle call and the callback function gets 
            # called.
            self.event.wait()
            # Because the function sets the needsync variable,
            # this helps escape the loop without doing 
            # anything if the stop() is called. Kinda neat 
            # solution.
            if self.needsync:
                print "got event!"
                self.event.clear()
                self.dosync()
 
    # The method that gets called when a new email arrives. 
    # Replace it with something better.
    def dosync(self):
        a = gmail_imap()
        l = a.search(time_filter = True)
        header = a.fetch_header(l)
        body= a.fetch_body(l)
        print body
        gp = gmail_parser(body, header)
        fromAddress = gp.parse_from(str(header))
        subject = gp.parse_subject(str(header))
        ms = [gp.get_body_html(body[id]) for id in gp.id]
        body = gp.get_body(ms[0])
        jsonData = gp.call_api(body)
        gp.send_email(subject[0],fromAddress[0],jsonData)
 
# Had to do this stuff in a try-finally, since some testing 
# went a little wrong.....
try:
    # Set the following two lines to your creds and server
    M = imaplib2.IMAP4_SSL("imap.gmail.com")
    M.login("ask@lazytruth.com","{PW}")
    # We need to get out of the AUTH state, so we just select 
    # the INBOX.
    M.select("INBOX")
    # Start the Idler thread
    idler = Idler(M)
    idler.start()
    while True:
        time.sleep(1*60)
    # Because this is just an example, exit after 1 minute.
finally:
    # Clean up.
    idler.stop()
    idler.join()
    M.close()
    # This is important!
    M.logout()