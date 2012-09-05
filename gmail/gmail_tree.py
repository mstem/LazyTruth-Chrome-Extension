'''

David Woo Hyeok Kang
June 14th, 2012
Edited On June 21st, 2012

E-mail Chronology Parser & Anonymizer

'''
import re

# parser
import gmail_parser as gparse
from gmail_parser import gmail_parser
reload(gparse)

# connector
import gmail_connect as gconnect
from gmail_connect import gmail_imap, since_parser
reload(gconnect)

DATE_PATTERN = [re.compile(r'\b\d{4}/\d+/\d+\b'),
              re.compile(r'\b\w* \d{1,2}?, \d{4}.*M\b'),
              re.compile(r'\b\d{1:2}/\d{1:2}/d{4}.*M\b')]


class gmail_tree(object):

    def __init__(self, parsed_html, parsed_header):
        self.html = parsed_html
        self.header = parsed_header

    def new_data(self, parsed_html, parsed_header):
        self.html = parsed_html
        self.header = parsed_header


###############################
# Tree-Structure for HTML Text#
###############################

    #INDEX BASED DICTIONARY

    def standard_linker(self, from_list, to_list, date_list):
        '''
        Idea:
        - link To and Date first (adjacency of about 150 accounts
        for all possible permutations of From-To)
        - and also exploit the fact that all three lists are ordered
        - known that To always come after Date/Sent/From

        Then return a dictionary linking {<From: (To, Date)>}
        '''
        d = {}
        
        date_end_list = [y for (x,y) in date_list]
        from_end_list = [y for (x,y) in from_list]
        for to_tup in to_list:
            to_start, ignore = to_tup

            date_end_index, near_dt = gparse.argmaxWithVal(date_end_list,
                            lambda x: self.is_adjacent(x, to_start))

            from_end_index, near_ft = gparse.argmaxWithVal(from_end_list,
                            lambda x: self.is_adjacent(x, to_start))

            if near_dt and near_ft:
                print "Both Exist"            

            dt_index = date_end_list.index(date_end_index)
            ft_index = from_end_list.index(from_end_index)      

            d[from_list[ft_index]] =[date_list[dt_index], to_tup]

        return d        

    def jumbled_linker(self, standard_d, from_list):
        '''
        Those with On Date, Someone wrote: format
        or Date Someone, Email Address format
        '''
        key_list = standard_d.keys()

        for item in from_list:
            if item not in key_list:
                s,e = item
                #print self.html[s:e]
                date_p1 = re.compile(r'\b\d{4}/\d+/\d+\b') #Done
                date_p2 = re.compile(r'\b\w* \d{1,2}?, \d{4}.*M\b') #Done
                date_p3 = re.compile(r'\b\d+/\d+/\d{4}.*M\b')
                a=date_p1.search(self.html[s:e])
                b=date_p2.search(self.html[s:e])
                c=date_p3.search(self.html[s:e])

                if a:
                    date_s, date_e = a.span()
                    #print a.group()
                elif b:
                    date_s, date_e = b.span()
                    #print b.group()
                else:
                    date_s, date_e = c.span()
                    #print c.group()
                
                standard_d[item] = [(s+date_s, s+date_e), (0,0)]

        return standard_d     

    def is_adjacent(self, end_index, start_index):
        '''
        Standard Formatting Only (On Date, Someone wrote: format doesn't work)
        ----------------------------
        1. From-Sent-To: indexes should be relatively close
        2. Date-From-To: indexes should be relatively close
        3. From-Date-Subj-To : assuming about 150 max characters for subject
        '''        
        return (abs(end_index - start_index) < 150)
    

    # STRING BASED ARRAY
    def associate_email(self, index_dictionary):
        '''
        Out of the index, building a readable string array

        array-> each element(which corresponds to one email) is a dictionary:
        its key is the Sender E-mail
        its values, for the corresponding key, are Date String, To Receiver E-mail

        If there was no Value specified for the Sender
        1. the previous nesting level's Receiver will automatically become
        the sender for current nesting
        2. If the previous nesting had no Receiver, then key for Sender will be
        junk
        3. Note that if the Top Most Level has No From, then an error
        will be generated(IndexError)

        No Value for the Receiver
        1. Then it will simply be ''
        '''
        html_body = self.html
        l=[]

        key_list = index_dictionary.keys()
        key_list.sort()
        # point of indexing first: ability to sort reverse-chronologically

        for key_p in range(len(key_list)):
            fs, fe = key_list[key_p]
            string_from = html_body[fs:fe]

            dt, tt = index_dictionary[key_list[key_p]]
            ds, de = dt
            ts, te = tt
            string_date = html_body[ds:de]
            string_to = html_body[ts:te]

            f_email = self.email_exists(string_from)

            if f_email:
                f_email = f_email.group()
            else:
                next_date, next_to = index_dictionary[key_list[key_p-1]]
                ts, te = next_to
                string_from = html_body[ts:te]

                f_email = self.email_exists(string_from)

                if f_email:
                    f_email = f_email.group()
                else:
                    print "Cannot retrieve f_email"
                    f_email = 'Junk'

            t_email = self.email_exists(string_to)
            if t_email:
                t_email = t_email.group()
            else:
                t_email = ''

            l.append({f_email:[string_date, t_email]})

        # Chronologically ordered (Oldest --> Newest)
        l.reverse()
        header_from = self.email_exists(self.header['From']).group()
        header_to = self.email_exists(self.header['To']).group()
        header_date = self.header['Date']
        l.append({header_from:[header_date, header_to]})

        return l

    def email_exists(self, string):
        pattern = re.compile('[\w.]*@[a-z.]+')
        return pattern.search(string)
    
###############
# Tree Parser #
###############

    def player(self, array_tree):
        '''
        Method that tries to sort out which e-mail addresses recur
        in the from/to addresses and count number of times
        '''
        d={}
        for email in array_tree:
            sender = email.keys()[0]
            date, receiver = email[sender]

            if sender not in d.keys():
                d[sender] = 1
            else:
                d[sender] += 1
            if receiver not in d.keys():
                d[receiver] = 1
            else:
                d[receiver] += 1

        return d

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

gt = gmail_tree(b4, h4)

d = gt.standard_linker(fl4, tl4, dl4)
d = gt.jumbled_linker(d, fl4)
new_d = gt.associate_email(d)

'''

# IMPORTANT CAVEAT: dictionary isn't ordered
d = gs.standard_linker(fl1, tl1, dl1)
keys = d.keys()
keys.sort()
for key in keys:
    fs, fe = key
    print "From Column\n", gs.html[fs: fe]

    dt, tt = d[key]
    ds, de = dt
    ts, te = tt

    print "To Column\n", gs.html[ts: te]
    print "Date Column\n", gs.html[ds: de]

gs.new_body(b1)
d = gs.standard_linker(fl1, tl1, dl1)
d = gs.jumbled_linker(d, fl1)
keys = d.keys()
keys.sort()

h2 = gp.get_header(gp.data_body[gp.id[0]])
print "From Column\n", h2["From"]
print "Date Column\n", h2["Date"]
print "To Column\n", h2["To"], '\n\n'

for key in keys:
    fs, fe = key
    print "From Column\n", gs.html[fs: fe]

    dt, tt = d[key]
    ds, de = dt
    ts, te = tt

    print "To Column\n", gs.html[ts: te]
    print "Date Column\n", gs.html[ds: de], "\n\n"

'''  
