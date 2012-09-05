'''

David Woo Hyeok Kang

June 15th, 2012
Scraping FactCheck.org

'''

import pycurl
import StringIO
import urllib
import datetime

from bs4 import BeautifulSoup
import re


class factcheck(object):
    
    def __init__(self, last_checkin = 'month'):
        #valid checkin values are 'month', 'day', 'year'
        self.log = last_checkin
        self.domain = 'http://factcheck.org/ask-factcheck/'

    def get_html(self, page_number):        
        c = pycurl.Curl()

        if page_number == 1:    addendum = ''
        else:                   addendum = 'page/'+str(page_number)+'/'
        
        c.setopt(c.URL, self.domain + addendum)
        b= self.set_output(c)
        
        c.perform()

        return b.getvalue()

    def set_output(self, curl_handler):
        b= StringIO.StringIO()
        curl_handler.setopt(curl_handler.WRITEFUNCTION, b.write)

        return b

    def entry_list(self, html):
        soup = BeautifulSoup(html)

        sum_entries = soup.findAll('div', {'class':'entry-summary'})
        title_entries = [entry.fetchPreviousSiblings('div', limit=1)
                         for entry in sum_entries]
        tag_entries = [entry.fetchNextSiblings('div',
                        {'class':'entry-utility'}, limit = 1)
                       for entry in sum_entries]

        return sum_entries, tag_entries, title_entries


    def sum_categorize(self, entry):
        more_link = entry.find('a')['href']

        list_strong = entry.findAll('strong')

        itera_l = []

        p1 = re.compile(r'(?<=>)\s?\w+.*?(?=<)')
        # ?<=... : lookahead assertion (match string only if ... precedes)

        result = p1.findall(str(entry))
        question = result[1]
        answer = ''
        for item_index in range(3,len(result)):
            answer += result[item_index]

        return result[1], answer, more_link

    def tag_categorize(self, entry):
        # remember that entry is tag_entries[i][0]
        tags = entry.findAll('a', {'rel':'tag'})

        tag_list = [tag.string for tag in tags]

        return tag_list

    def title_categorize(self, entry):
        #Note that entry is title_entries[i][0]
        title = entry.find('a').string
        date = entry.find('div', {'class':'entry-utility'}).string

        splice = date.strip().split(',')
        date = (splice[1] +','+ splice[2]).strip()
        title = title.strip()

        return title, date
        

#########################
# DATE helper functions #
#########################        
        
    def parse_date(self, fc_str_date):
        year_dic = {'January':1, 'February':2, 'March':3, 'April':4,
                    'May':5, 'June':6, 'July':7, 'August':8,
                    'September':9, 'October':10, 'November':11, 'December':12}
        month, day, year = fc_str_date.split()
        day = day[0]
        return datetime.date(int(year), year_dic[month], int(day))

    def is_recent(self, date):
        # make sure to pass in parsed_date
        return self.parse_log() > date

    def parse_log(self):
        dic = {'month':30, 'day':1, 'year':365}
        today = datetime.date.today()
        one_period = datetime.timedelta(days=dic[self.log])

        return today - one_period
        
