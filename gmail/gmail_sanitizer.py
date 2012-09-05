'''
David Woo Hyeok Kang
June 21st, 2012

Anonymizer/Counter for Domain

#############
RANDOM THOUGHT

A procedure that traverses through nested list/dictionary and
replaces a mutable value if matching the string desired to a new value

#############
'''
# tree builder
import gmail_tree as gtree
from gmail_tree import gmail_tree
reload(gtree)

# parser
import gmail_parser as gparse
from gmail_parser import gmail_parser
reload(gparse)

# connector
import gmail_connect as gconnect
from gmail_connect import gmail_imap, since_parser
reload(gconnect)

# anonymizer
import hashlib
import re

LARGE_DOMAINS = ['gmail.com', 'yahoo.com']

class gmail_sanitizer(object):

    def __init__(self, parsed_tree, parsed_html):
        self.tree = parsed_tree
        self.body = parsed_html
        self.all_anon_dic = self.anonymizer(self.get_all_emails())

##################
# Sensitive Info #
##################

    def get_all_emails(self):
        pattern = re.compile('[\w.]*@[a-z.]*')
        return pattern.findall(self.body)

    #NOTE: get_all_phones/get_all_zip pretty unreliable as of now

    def get_all_phones(self):
        pattern = re.compile('\d*-?\d+-\d+-\d+')
        return pattern.findall(self.body)

    def get_all_zip(self):
        pattern = re.compile('\d*')
        return pattern.findall(self.body)

##############
# Anonymizer #
##############

    def anonymizer(self, email_list):
        anon_dic = {}
        for email in email_list:
            email = email.replace('3D', '')
            anon_dic[email] = anonymize(email)

        return anon_dic

    def anonymize_email(self, anon_dic):
        new_body = self.body
        for key in anon_dic:
            new_body = new_body.replace(key, anon_dic[key])

        return new_body

    def anonymize_tree(self):
        all_anon_dic = self.all_anon_dic
        all_anon_dic['']=''
        new_tree = []
        
        for dic in self.tree:
            from_email = dic.keys()[0]
            ignore, to_email = dic[from_email]

            new_from= all_anon_dic[from_email]
            new_to = all_anon_dic[to_email]

            new_tree.append({new_from:[ignore, new_to]})

        return new_tree          

###########
# Counter #
###########

    def email_counter(self, tree_list):
        print self.all_anon_dic
        for key in self.all_anon_dic:
            username, domain, type = at_separator(key)

            if domain in LARGE_DOMAINS:
                pass
            pass
        pass
                
        

'''
Counter Needs More Work
'''
        
def anonymize(e_address):
    try:
        username, domain, type = at_separator(e_address)
        print username, domain, type
        return hashlib.sha1(e_address).hexdigest()

    except:
        return e_address

def at_separator(e_address):
    lst = e_address.split('@')
    domain = lst[1].split('.')

    if domain[-1] == 'edu':
        print "edu address, saving?!"
        
    return lst[0], domain[0], domain[-1]


def email_counter(domain):

    if domain in LARGE_DOMAINS:
        pass
    pass

#def __main__():
a = gmail_imap()
l = a.search(x_gm_raw="is:starred", time_filter = False)

header = a.fetch_header(l)
body= a.fetch_body(l)

gp = gmail_parser(body, header)

'''
ms = [gp.get_body_html(body[id]) for id in gp.id]
pls = [gp.parse_from(str(body)) for body in ms]
tbs = [gp.tag_insert(p,l, {"nest":"level"}) for (p,l) in pls]
cls = [tb.replace('3D', '') for tb in tbs]
sls = [gp.nest_slice(cl) for cl in cls]
'''

b1 = gp.get_body_html(body[gp.id[0]])
b1, ignore = gp.parse_from(str(b1))
b2 = gp.get_body_html(body[gp.id[1]])
b2, ignore = gp.parse_from(str(b2))
b3 = gp.get_body_html(body[gp.id[2]])
b3, ignore = gp.parse_from(str(b3))
b4 = gp.get_body_html(body[gp.id[3]])
b4, ignore = gp.parse_from(str(b4))

h1 = gp.get_header(header[gp.id[0]])
h2 = gp.get_header(header[gp.id[1]])
h3 = gp.get_header(header[gp.id[2]])
h4 = gp.get_header(header[gp.id[3]])


ignore, fl1 = gp.extractor(info='From', id_num=0)
ignore, tl1 = gp.extractor(info='To', id_num=0)
ignore, dl1 = gp.extractor(info='Date', id_num=0)
ignore, sl1 = gp.extractor(info='Subject', id_num=0)

ignore, fl2 = gp.extractor(info='From', id_num=1)
ignore, tl2 = gp.extractor(info='To', id_num=1)
ignore, dl2 = gp.extractor(info='Date', id_num=1)
ignore, sl2 = gp.extractor(info='Subject', id_num=1)

ignore, fl3 = gp.extractor(info='From', id_num=2)
ignore, tl3 = gp.extractor(info='To', id_num=2)
ignore, dl3 = gp.extractor(info='Date', id_num=2)
ignore, sl3 = gp.extractor(info='Subject', id_num=2)

ignore, fl4 = gp.extractor(info='From', id_num=3)
ignore, tl4 = gp.extractor(info='To', id_num=3)
ignore, dl4 = gp.extractor(info='Date', id_num=3)
ignore, sl4 = gp.extractor(info='Subject', id_num=3)

gt = gmail_tree(b1, h1)

d = gt.standard_linker(fl1, tl1, dl1)
d = gt.jumbled_linker(d, fl1)
new_d = gt.associate_email(d)

gs = gmail_sanitizer(new_d, b1)
print gs.all_anon_dic
