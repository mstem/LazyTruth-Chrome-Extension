'''
David Woo Hyeok Kang
June 8th, 2012

Edited on June 11th, 2012
Edited on June 12th/13th, 2012

Retrieving the e-mail information 
'''
#Connection
import getpass, imaplib, os

#time parser
import time
import datetime

DEFAULT_ID = "kang.woohyeok"
DEFAULT_PW = 'tangtangball011'

LARGE_DOMAINS = ["gmail", "yahoo"]

class gmail_imap(object):
    def __init__(self, user = DEFAULT_ID, pwd=DEFAULT_PW, mailbox="INBOX"):
        self.mb = mailbox
        self.user = user
        self.pwd = pwd
        self.domain = "imap.gmail.com"

        self.imap = self.get_connected()

        self.mb_list = self.get_mailbox_list()

        self.select_mailbox(self.mb)

    def get_connected(self):        
        m = imaplib.IMAP4_SSL(self.domain)
        m.login(self.user, self.pwd)

        return m

    def get_mailbox_list(self):
        return self.imap.list()[1]

    def select_mailbox(self, mb):
        '''
        Valid Names --> INBOX, [Gmail]/(All Mail, Drafts, Sent Mail, Spam,
        Starred, Trash
        '''
        self.imap.select(mb)
        self.mb = mb

    def search(self, since="month", x_gm_raw='', time_filter=True):
        '''
        valid options for since would be
        "month" -> inbox e-mail since last-month
        "day" -> inbox e-mail since yesterday
        "year" -> inbox e-mail since last year
        "all" -> all inbox e-mail

        x_gm_raw is the advanced gmail query that you can add
        add in a string that you would like to query
        i.e.) "has: attachment in:unread"
              "from:David OR from:Anne" (Note that OR must be capitalized)
        By default, x_gm_raw is nothing
            --> (simply month time filter to avoid massive influx of info)

        else -->
            if time_filter is True: BOTH Time filter + x_gm_raw
            else: x_gm_raw ONLY

        Note that if you do since='all', time_filter=False, all your
        email is returned (expected behaviro)

        NO time_filter + x_gm_raw
        (i) since='all', x_gm_raw
        (ii) x_gm_raw, time_filter=False
        '''
        if time_filter:
            last_check = since_parser(since)
            current_check = since_parser('now')

            x_gm_raw += (' after:' + last_check +' before:' +current_check)

        else:
            x_gm_raw = x_gm_raw
            
        typ, msgs = self.imap.search(None, '(X-GM-RAW "'+x_gm_raw+'")')

        query_ids = msgs[0].split()

        return query_ids

    
####################
# Raw_DATA Fetcher #
####################

    def fetcher(self, q_id_list, criterion):
        dic = {}
        for msg_id in q_id_list:
            typ, data = self.imap.fetch(msg_id, criterion)

            pseudo_data = data[0][1]

            dic[msg_id] = pseudo_data

        return dic
        
    def fetch_body(self, q_id_list):
        return self.fetcher(q_id_list, '(RFC822)')

    def fetch_header(self, q_id_list):
        return self.fetcher(q_id_list, '(RFC822.HEADER)')


####################
# Internal Fetcher #
####################

    def fetch_thread(self, q_id_list):
        return self.fetcher(q_id_list, '(X-GM-THRID)')
            

    def fetch_gmailid(self, q_id_list):
        return self.fetcher(q_id_list, '(X-GM-MSGID)')
        

    
def since_parser(since):
    cur_time = time.time()
    d = {"month":30, "day":1, "year":365, "all":cur_time/(3600*24), "now":0}

    tstamp = cur_time - 3600 * 24 * d[since]

    since_parse = datetime.date.fromtimestamp(tstamp)

    return '%d/%02d/%d' %(since_parse.year,since_parse.month,since_parse.day)





'''
def nesting():
    Nesting needs a bit more work

    top two layer doesn't seem to get nested

    and if class not gmail_quote, not sure how it will work out

    a = gmail_imap()
    html_dic = a.get_body_html()

    ordered_key = html_dic.keys()

    ordered_key.sort()
    print ordered_key

    one_email = html_dic[ordered_key[0]]
    return one_email

def bs_preprocess(html):
    """remove distracting whitespaces and newline characters""" 
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE) 
    html = re.sub(pat, '', html)       # remove leading and trailing whitespaces 
    html = re.sub('\n', ' ', html)     # convert newlines to spaces 
                                         # this preserves newline delimiters 
    html = re.sub('[\s]+<', '<', html) # remove whitespaces before opening tags 
    html = re.sub('>[\s]+', '>', html) # remove whitespaces after closing tags 

    return html

    
    anonymous_email = a.sanitize_string_body(one_email)

    #soup = BeautifulSoup(anonymous_email)

    #return soup

    return anonymous_email


    nests = soup.find_all('div', {'class':'gmail_quote'})
    i = 0
    for nest in nests:
        print "nest level: ", i
        i += 1

        print "The information is:", nest

        print ''
        



############
###UNUSED###
############
def __main__():
    a = gmail_imap()
    l1 = a.search()

    #head_dic = a.fetch_header(l1)
    body_dic = a.fetch_body(l1)

    unordered_list =  body_dic.keys()
    unordered_list.sort()
    print unordered_list

    one_key = unordered_list[-1]


    for key in head_dic.keys():
        parsed_message = a.parse_header(head_dic[key])

        print "From: ", parsed_message["From"]
        print "In-Reply-To", parsed_message["In-Reply-To"]
        #print parsed_message.keys()
        print "Received:", parsed_message["Received"]



    print "key is: ",one_key
    mb = a.parse_body(body_dic[one_key])
    dirty_html = mb.get_payload()[1].get_payload()

    print "dirty html is: ", dirty_html
    cleansed_string = dirty_html.replace('=\r\n', '')
    immac_string = cleansed_string.replace('=\n', '')
    perfect_string = immac_string.replace('3D', '')

    html_mails = re.findall('[a-z]*?@[a-z]*.[a-z]*', perfect_string)

    anon_dic = {}

    print "html_mails: ", html_mails

    for link in html_mails:
        anon_dic[link] = anonymize(link)

    anon_string = perfect_string[:]
    for key in anon_dic.keys():
        anon_string = anon_string.replace(key, anon_dic[key])

    return anon_string

def imap_conn(since="month", user=DEFAULT_ID, pwd=DEFAULT_PW):

    valid options for since would be
    "month" -> inbox e-mail since last-month
    "day" -> inbox e-mail since yesterday
    "year" -> inbox e-mail since last year
    "all" -> all inbox e-mail


    last_check = since_parser(since)
    
    parsed_dic = {}
    
    if user == DEFAULT_ID:
        pass
    else:  
        user = raw_input("Enter your GMail username:")
        pwd = getpass.getpass("Enter your password: ")

    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user,pwd)

    m.select()

    typ, msgnums = m.search(None, '(SINCE "'+last_check+'")')

    id_list = msgnums[0].split()

    for msg_id in id_list:
        typ, data = m.fetch(msg_id, '(X-GM-THRID)')
        print data

        header_data = data[0][1]

        header = Parser().parsestr(header_data)

        parsed_dic[msg_id] = header

    return parsed_dic   


######################
# Tentatively UNUSED #
######################

import pycurl
import StringIO

SCOPE =  "https://mail.google.com/mail/feed/atom"

CLIENT_ID = '399578378355-5r3kfvrk3pugc6181qfnnsmvqf17og39.apps.googleusercontent.com'

CLIENT_SECRET = 'VKso7UPKaxxLqKS1Y2ucpRoi'

dic = {"client_id": CLIENT_ID, "scope": SCOPE}


c = pycurl.Curl()
c.setopt(c.URL, 'https://accounts.google.com/o/oauth2/device/code')

b = StringIO.StringIO()
c.setopt(c.WRITEFUNCTION, b.write)

c.setopt(c.HTTPHEADER, ["Content-Type : application/x-www-form-urlencoded"])

c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, str(dic))
#print str(dic)


c.perform()

h = b.getvalue()
'''

