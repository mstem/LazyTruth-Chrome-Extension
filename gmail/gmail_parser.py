'''

David Woo Hyeok Kang
June 14th, 2012

E-mail Fetch-Parser

'''

from email.parser import Parser
import email
import httplib, urllib, smtplib
import string
import json

#parsing_html, nesting/tree structure
from bs4 import BeautifulSoup, NavigableString #Not really necessary
import re

FROM_PATTERN = [re.compile(r"(?<=>)\s*From:.*?(?=<br>)"),
                re.compile(r"(?<=>)\s*On.*?(?=<br>)"),
                re.compile(r"(?<=>)\s*\d{4}/\d+/\d+.+?(?=<br>)")]

class gmail_parser(object):

    def __init__(self, fetch_body, fetch_header):
        # Note that the attributes data_body, data_header are dictionaries
        self.data_body = fetch_body
        self.data_header = fetch_header

        self.id = fetch_body.keys()

###############
# DATA PARSER #
###############

    def get_header(self, header_data):

        parsed_header = email.message_from_string(header_data)
        return parsed_header

    def get_body_html(self, body_data):
        try:
            parsed_body = email.message_from_string(body_data).get_payload(1)
            return parsed_body
        except TypeError:
            parsed_body = email.message_from_string(body_data).get_payload()
            return parsed_body
        except:
            print "No Body exists"

####################
# Pattern Matching #
####################

    def parse_to(self, html_body):
        # Safety measure to clean off newline character
        html_body = self.cleanse_body(html_body)
        p1=re.compile(r"(?<=>)\s*To:.*?(?=<br>)") # DONE

        l = self.pattern_list(html_body, [p1])

        return html_body, l

    def parse_date(self, html_body):
        html_body = self.cleanse_body(html_body)
        p1 = re.compile("(?<=>)\s*Date:.*?(?=<br>)") # DONE
        p2 = re.compile("(?<=>)\s*Sent:.*?(?=<br>)") # DONE

        l = self.pattern_list(html_body, [p1, p2])

        return html_body, l

    def parse_subject(self, html_body):
        # the list that we return is what controls the output
        html_body = self.cleanse_body(html_body)
        p1=re.compile(r"(?<=>)\s*From:.*?(?=\r\n)") # DONE
        p2=re.compile(r"(?<=>)\s*On.*?(?=<br>)") # DONE
        p3=re.compile(r"(?<=>)\s*\d{4}/\d+/\d+.+?(?=<br>)") # DONE
        p4=re.compile(r"Subject: ([\w\s:]*)")

        #print "From Pattern:\n", p1.findall(html_body)
        #print "On Pattern:\n", p2.findall(html_body)
        #print "Date Pattern : \n", p3.findall(html_body)
        #print "Test Pattern : \n", p4.findall(html_body)


        l = self.pattern_list(html_body, [p1, p2, p3, p4])
        #return html_body, l
        return p4.findall(html_body)
    
    def parse_from(self, html_body):
        # the list that we return is what controls the output
        html_body = self.cleanse_body(html_body)
        p1=re.compile(r"(?<=>)\s*From:.*?(?=\r\n)") # DONE
        p2=re.compile(r"(?<=>)\s*On.*?(?=<br>)") # DONE
        p3=re.compile(r"(?<=>)\s*\d{4}/\d+/\d+.+?(?=<br>)") # DONE
        p4=re.compile(r"From: [\w\s]+?<([\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4})>")

        #print "From Pattern:\n", p1.findall(html_body)
        #print "On Pattern:\n", p2.findall(html_body)
        #print "Date Pattern : \n", p3.findall(html_body)
        #print "Test Pattern : \n", p4.findall(html_body)


        l = self.pattern_list(html_body, [p1, p2, p3, p4])
        #return html_body, l
        return p4.findall(html_body)

    def cleanse_body(self, html_body):
        html_body = str(html_body).replace('=\r', '')
        return html_body.replace('\n', '')

    def pattern_list(self, html_body, list_pattern):
        '''
        list_pattern is a list of pattern objects (i.e. re.compile objects)
        html_body is the body to perform the search

        Method returns a list of the indicies, ordered
        '''
        
        nested_indicies = [[item.span() for item in pattern.finditer(html_body)]
                           for pattern in list_pattern]

        l = []

        for y in nested_indicies:
            for item in y:
                l.append(item)

        l.sort()
        
        return l

################
# NESTING/TAGS #
################        

    def tag_insert(self, html_body, list_index, tag_name_dic):
        '''
        tag_name_dic
        example {"nest": "level"}
        this will append the level attribute to increase
        only a pair of tag_name:tag_attr supported as of now
        
        '''

        tag_name = tag_name_dic.keys()[0]
        tag_attr = tag_name_dic[tag_name]
        
        tag_indicies = []
        insert_offset = 0
        nest_index = 0

        new_body = html_body[:]

        for i in range(len(list_index)):
            # append <tag_name tag_attr=nest_index>

            start, end= list_index[i]

            tag_index = start + insert_offset

            insert_tag = "<"+tag_name+" "+tag_attr+"=" + str(nest_index) + ">"

            new_body = new_body[:tag_index] + insert_tag + new_body[tag_index:]

            nest_index +=1
            insert_offset += len(insert_tag)

            list_index[i] = (tag_index, end + insert_offset)

            #append </tag_name>
            try:
                next_s, next_e = list_index[i+1]
                
                end_tag = "</"+tag_name+">"
                tag_index = next_s + insert_offset

                new_body = new_body[:tag_index] + end_tag + new_body[tag_index:]

                insert_offset += len(end_tag)

            except:
                # happens at the last iteration, where index error occurs
                pass

            
        return new_body    
        

    def nest_tag(self, html_body, list_index):
        return self.tag_insert(html_body, list_index, {'nest':'level'})

    def nest_slice(self, tagged_body):
        soup = BeautifulSoup(tagged_body)

        return soup.find_all('nest')

#############
# EXTRACTOR #
#############

    def extractor(self, info='Subject', id_num=0):
        '''
        Info: 'from', 'date', 'to', 'subject'
        Info is the information that needs to be extracted
        By default 'subject' is the basic extractor

        id_num refers to the index number of gp.id
        i.e.) gp.id = [12, 13, 14]

        extractor(id_num=0) indicates 12 whereas id_num=1 indicates 13
        '''
        try:
            id = gp.id[id_num]
        except: # None selected
            print "Nothing in the query"            
        
        html = gp.get_body_html(gp.data_body[id])
        
        if info == 'To':
            body_html, lst_index = gp.parse_to(html)
        elif info == 'From':
            body_html, lst_index = gp.parse_from(html)
        elif info == 'Date':
            body_html, lst_index = gp.parse_date(html)
        elif info == 'Subject':
            body_html, lst_index = ('', [])
        else:
            print "Unextractable Field"

        l = []

        # We want first information to be the header information
        l.append((gp.get_header(gp.data_header[id]))[info])
            
        for item in lst_index:
            x,y = item
            l.append(body_html[x:y])

        return l, lst_index

    def cost_function(self, nest_body, player_dic):
        # we want to give more penalty for having images
        # having the least count is a potential? (Not very decisive but maybe)
        #         
        nest_str = str(nest_body)
        length_score = len(nest_str) / 100

        return length_score

    def viral_det(self, list_nest):
        nest_text, score = argmaxWithVal(list_nest, self.cost_function)
        return nest_text
        
    def remove_tags(self, html):
        soup = BeautifulSoup(str(html))
        return soup.text

    def get_body(self, content):
        cleanedBody = str(content)
        cleanedBody = self.cleanse_body(cleanedBody)
        cleanedBody = re.sub(' +',' ',self.remove_tags(cleanedBody))
        reCompiled = re.compile(r"[\w\s]*<*.*@[\w.]*>(.*)", re.DOTALL) # DONE
        if reCompiled.match(cleanedBody):
            cleanedBody = reCompiled.findall(cleanedBody)[0]
        cleanedBody = cleanedBody.replace('=20',' ')
        cleanedBody = cleanedBody.replace('=A0',' ')
        cleanedBody = ' '.join(cleanedBody.split())
        cleanedBody = cleanedBody.replace('= ',' ')
        return cleanedBody

    def call_api(self, body):
        headers = { "Content-type": "application/json"}
        conn = httplib.HTTPSConnection("lazytruth.media.mit.edu")
        params = urllib.urlencode({'text': body})
        conn.request("POST", "/data/api/0.1/match/",params , headers)
        response = conn.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        conn.close()
        return jsonData

    def send_email(self, subject, fromAddress, jsonData):
        SUBJECT = "Re: " + subject
        TO = fromAddress
        FROM = "ask@lazytruth.com"
        AMAZONUSER = "{USER}"
        PORT = 465
        PW = "{PW}"
        print jsonData.keys()
        if 'fact_text' in jsonData.keys():
            #text = urllib.unquote(jsonData['fact_text'])
            text = jsonData['fact_text'].encode('utf-8')
        else:
            text = 'We do not currently have any information about this email.'

        if 'detail_url' in jsonData.keys():
            link = " <a href='%s' target=\"_blank\">Read more</a>" % (jsonData['detail_url'])
            text += link.encode('utf-8')
        if 'fact_image_url' in jsonData.keys():
            image = "<br/><br/><img src='https://lazytruth.media.mit.edu/%s' />" % (jsonData['fact_image_url'])
            text += image.encode('utf-8')

        BODY = string.join((
                "From: %s" % FROM,
                "To: %s" % TO,
                "MIME-Version: 1.0",
                "Content-type: text/html",
                "Subject: %s" % SUBJECT ,
                "",
                text
                ), "\r\n")
        server = smtplib.SMTP_SSL("email-smtp.us-east-1.amazonaws.com", PORT)
        server.login(AMAZONUSER, PW)
        server.sendmail(FROM, [TO], BODY)
        server.quit()
        




#date matcher

#print pls[0]
#tbs = [gp.tag_insert(p,l, {"nest":"level"}) for (p,l) in pls]
#print "BLAH"
#print tbs[0]
#cls = [tb.replace('3D', '') for tb in tbs]
#print "BLAH"
#print cls[0]
#sls = [gp.nest_slice(cl) for cl in cls]
#print "BLAH"
#print sls[0]


#hash password
#change text to FACT variable
#change TO to original senders variables
#define SUBJECTLINE earlier in Justin's script


####################
# HELPER FUNCTIONS #
####################

def argmaxWithVal(l, f):
    # Takes a list of items, and a procedure
    # Returns the element of l that has the highest score
    highest_index = 0
    highest_score = 0

    for i in range(len(l)):
                
        if f(l[i]) >= highest_score:
            highest_index = i
            highest_score = f(l[i])
            
    return (l[highest_index], highest_score)



'''


h1= gp.get_header(header[a])
h2= gp.get_header(header[b])
h3= gp.get_header(header[c])
h4= gp.get_header(header[d])
print h1['From'], h1['To'], h1['Date']
print h2['From'], h2['To'], h2['Date']
print h3['From'], h3['To'], h3['Date']
print h4['From'], h4['To'], h4['Date']
'''



'''
Deprecated

m1 = gp.get_body_html(body[a])
m2 = gp.get_body_html(body[b])
m3 = gp.get_body_html(body[c])
m4 = gp.get_body_html(body[d])
h1= gp.get_header(body[a])
h2= gp.get_header(body[b])
h3=  gp.get_header(body[c])
print h1['From']
print h2['From']
print h3['From']

p1, l1 = gp.parse_from(str(m1))
p2, l2 = gp.parse_from(str(m2))
p3, l3 = gp.parse_from(str(m3))
p4, l4 = gp.parse_from(str(m4))

tb1 = gp.tag_insert(p1, l1, {"nest":"level"})
tb2 = gp.tag_insert(p2, l2, {"nest":"level"})
tb3 = gp.tag_insert(p3, l3, {"nest":"level"})
tb4 = gp.tag_insert(p4, l4, {"nest":"level", "hey":"yo"})

a= tb1.replace('3D', '')
b= tb2.replace('3D', '')
c= tb3.replace('3D', '')
d= tb4.replace('3D', '')

sl1 = gp.nest_slice(a)
sl2 = gp.nest_slice(b)
sl3 = gp.nest_slice(c)
sl4 = gp.nest_slice(d)
'''


#message = gp.get_body_html(body[a])

#print type(message)
#print len(message)

#print gp.parse_nest(message.as_string())[-1]

'''

body = re.sub(r'=\r\n', '', body[gp.id[0]])
body = re.sub(r'\r\n', '', body)


pattern1 = re.compile(r'<div class=[\w]*"[\w]*_quote">')
pattern2 = re.compile(r'From:')



for item in pattern1.finditer(body):
    start, end = item.span()
    print body[start:end]

for item in pattern2.finditer(body):
    start, end = item.span()
    print body[start:end]
    
#print pattern1.finditer(body[gp.id[0]])
#print pattern2.finditer(body[gp.id[0]])
'''


