'''
David Woo Hyeok Kang
Made on June 6th, 2012
Edited on June 7th, 2012

Bitly-Database Encoding Classes

9/5/2012
Add your username/password at __init__ function
'''
import incf.countryutils
from incf.countryutils import transformations
import datetime
from bitly_connect import bitly
#from apps.data.models import Fact, FactMetric

####################################
# main FactMetric TopCounter Class #
####################################
'''
bitlyAPI counting and data retrieval example

>>> a = TopCounter(<username>, <password>, <category>)
>>> a.mod_cat(<desired_category_change>)
>>> a.link_category_get(<link>) #gets the relevant JSON RESPONSE
>>> a.link_category_top(<link>  #gets the TOP country/referrer/date_of_click
                                #in the form of tule :
                                # i.e.) (<TOP_count/ref/date>, TOP_CLICKS)
>>> a.sum_of_all_items(<link>)
 currently only useful for category "clicks"--> gets aggregate clicks of link
 others --> simply sorts the json response into a nice dictionary format
 
'''

# Note that shares isn't very useful because of its dependency
# on bitly API

class TopCounter(object):

    def __init__(self, category_string, user='USERNAME', pw='PW'):
        self.cat = ""
        self.user = user
        self.pw = pw
        self.api = bitly(self.user, self.pw)
        self.tot_links = self.user_link_get(self.api)
        self.valid= ["countries", "clicks", "referrers", "referring_domains",
                     'shares']
            
        if self.cat_check(category_string): self.cat = category_string
        else: print "Invalid, please use mod_cat to modify your category"

    def mod_cat(self, category_string):
        if self.cat_check(category_string):
            self.cat = category_string

    def cat_check(self, category_string):
        if category_string not in self.valid:
            return False
        else:
            return True

    def link_category_get(self, link):
        # general data for getting all the data, separated by date
        # month and by category
        
        if self.cat == "clicks":
            # date separated clicks
            # i.e.) [{6/1/12: 3 clicks}, {6/2/12 -> 7 clicks}, etc ]
            
            json_list = self.api.link_stat('clicks', short_url=link)["link_clicks"]

            return json_list
        
        else:
            # Not date separated (all rolled up)
            #[{cat:'some_cat", clicks:'6'}, {cat:"some_cat2", clicks:'7'}, etc]
            json_list = self.api.link_stat(self.cat, short_url = link,rollup = 'true')[self.cat]

            return json_list
        

    def link_category_top(self, link):
        '''
        each category has its own helper score function associated
        The helper functions are written below the class/method definitions
        '''

        json_list = self.link_category_get(link)
        
        if self.cat == "clicks":
            max_timestamp, num_top_click = argmaxWithVal(json_list, click_score)

            date = time_conversion(int(max_timestamp['dt']))

            return date, num_top_click

        else:
            if self.cat == "countries":
                
                category, num_top_click =\
                        argmaxWithVal(json_list, country_click_score)
                category = country_expand(category["country"])
                
            elif self.cat == "referrers" or\
                 self.cat == "referring_domains":
                
                category, num_top_click =\
                        argmaxWithVal(json_list, ref_click_score)
                
                try:    category = category['referrer']
                except: category = category['domain']
                
            else:
                category, num_top_click =\
                        argmaxWithVal(json_list, share_click_score)

                category = share_expand(category['share_type'])

            return category, num_top_click

    def link_counts(self, link):
        '''
        Method allows for any category to calculate total link_count
        '''        
        if not (self.cat == 'clicks'):
            old_cat = self.cat
            self.cat = 'clicks'

        json_list = self.link_category_get(link)
        
        tot_sum = 0
        for index in range(len(json_list)):
            tot_sum +=json_list[index]['clicks']

        
        try: self.cat = old_cat
        except: self.cat = self.cat

        return tot_sum

    def pretty_format(self, link):
        '''
        Please refrain from using method when self.cat is 'clicks'
        '''
        new_dic = {}
        json_list = self.link_category_get(link)

        for index in range(len(json_list)):
            key = json_list[index].values()[0]
            try : key = country_expand(key)
            except: key = key
            
            new_dic[key] = json_list[index].values()[-1]

        return new_dic


    def user_link_get(self, user_bitly):
        num_total_links, json = user_bitly.link_history()
        # this json returns a tuple (num_tot_bitly, bitly_data)

        link_list = []
        for link in json:
            link_list.append(link["link"])

        return link_list
                               

'''
Overall Category Top isn't implemented yet.
Would be something like

Top Clicks for aggregate num of clicks
Top Country for all the bitly links
Top Referrer for all the bitly links
Top Referring Domain for all the bitly links
Top Shares for all the bitly links
'''

####################
# HELPER FUNCTIONS #
####################

def argmaxWithVal(l, f):
    # Takes a list of items, and a procedure
    # Returns the element of l that has the highest score
    if l == []:
        raise ValueError("Bitly API tells me that there is no matching query!\
                         Please Double-check http or make sure there is data\
                         to fetch!!")
    highest_index = 0
    highest_score = 0

    for i in range(len(l)):
                
        if f(l[i]) >= highest_score:
            highest_index = i
            highest_score = f(l[i])
            
    return (l[highest_index], highest_score)

def click_score(dictionary):
    return dictionary["clicks"]

def country_click_score(dictionary):
    if dictionary["country"] == "None":
        return -1
    else:
        return dictionary["clicks"]

def ref_click_score(dictionary):
    return dictionary["clicks"]

def share_click_score(dictionary):
    return dictionary['shares']

'''
Not Used for the purpose

def add_by_category(lst):

    for index in range(len(lst)):
        
        
    new_list = []
    l_keys = dictionary.keys()

    for 
    new_list.append({
'''                                        
    

########################
#Conversion Procedures #
########################

def time_conversion(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def country_expand(short_country):
    code_num = transformations.cca2_to_ccn(short_country)
    return transformations.ccn_to_cn(int(code_num))

def share_expand(short_share):
    if short_share == 'tw':
        return 'twitter'
    elif short_share == 'fb':
        return 'facebook'
    elif short_share == 'em':
        return 'email'

