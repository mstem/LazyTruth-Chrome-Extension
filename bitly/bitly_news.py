# bitlynews scarping
# HTML DOM

import pycurl
import json
import StringIO
from bs4 import BeautifulSoup

MAX_NUM = 30

def get_bitlynews():
    html_output = get_html()
    soup = BeautifulSoup(html_output)

    html_titles = soup.find_all(name='td', attrs={"class":"title"}, align=False,
                                limit = MAX_NUM)

    res_list = []
    bitly_list = []
    source_list = []

    for index in range(len(html_titles)):
        a = html_titles[index].contents[0]

        
        real_title = a.string
        detail_url = a['href']
        domain_url = html_titles[index].contents[-1].string

        res_list.append({"title":real_title, 'detail_url':detail_url,
                         "text":'', "image":'', 'source':domain_url})
        source_list.append({"url":domain_url, 'name' : "",'icon':''})

    bitly_link = soup.find_all(name='td', attrs={"class":"subtext"}, limit = MAX_NUM)

    for index in range(len(bitly_link)):
        short_url = bitly_link[index].contents[-1]['href']

        res_list[index]["short_url"] = short_url
        bitly_list.append(short_url)

##    print "resulting fact list: ", res_list, "length of result: ", len(res_list)
##    print "resulting bitly_list: ", bitly_list, "length of bitly_result: ", len(bitly_list)
##
##    print "resulting source list: ", source_list, "length of source_list: ", len(source_list)
  

    return res_list, bitly_list, source_list

def get_html():
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://bitlynews.com')


    b = StringIO.StringIO()

    c.setopt(c.WRITEFUNCTION, b.write)

    c.perform()
    
    return b.getvalue()


