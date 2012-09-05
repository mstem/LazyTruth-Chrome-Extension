'''
Author: David Woo Hyeok Kang
Created on June 6th, 2012
e-mail: david@lazytruth.com

This python-bitly implementation is intended only for those with
registered bitly id/pw.To implement bitly API for non-registered
users the code would have to be tweaked to meet that end.

Note that not all the API methods are implemented (subjective selection)
To add a method, look at the documentation on bitly developers page.

First, define a new method, add the parameters to the params inside the method
you created, then the url_method.

Then set the json_response(or whatever you wish to call the response you get
from the http get) to self.encode_send_request and see what data you need.

Created for the purpose of LazyTruth, a Gmail contextual gadget.
LazyTruth is a product of the MIT Media Lab's Center for Civic Media.
'''

import json
import pycurl
import StringIO
import urllib


class bitly(object):

    def __init__(self, login, pw):
        self.login = login
        self.pw = pw

        self.access_token = self.get_access_token(self.login, self.pw)
        self.params = {'access_token': self.access_token}

        self.domain = "https://api-ssl.bitly.com/v3/"

############################################
#  METHODS WITHOUT link/ or user/ in front #
############################################

    def shorten(self, long_url):
        '''
        a simple version for shortening.

        returns the shortened bitly_link
        
        cf) /v3/user/link_save which is another method for saving links
        '''
        
        # Note params is intended to be a shallow copy
        params = self.params.copy()
        params["longUrl"] = long_url        

        url_method = self.domain + "shorten?"
        
        json_response = self.encode_send_request(url_method, params)
        print json_response
        
        return json_response["data"]["url"]

    def expand(self, short_url):
        '''
        returns the long_url of the shortened bitly_link that you input
        i.e) (from bitly website example)
        
        http://bit.ly/1RmnUT would return

        http://www.google.com

        Note: no hash option
        '''
        
        params = self.params.copy()
        params["shortUrl"] = short_url

        url_method = self.domain + "expand?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]["expand"][0]["long_url"]

    def title_info(self, short_url="", hash=""):
        '''
        short_url takes precedence over hash.
        i.e.) if user puts
        bitly.title_info("http://bit.ly/ABCDEFG", "ZYXVUT")

        returns the title info of "http://bit.ly/ABCDEFG"
        Note: If the website has no title or is a broken website,
        then you will likely get nothing
        '''
        
        if not short_url and not hash:
            raise ValueError("At least supply one hash or short_url!")
        
        params = self.params.copy()

        url_method = self.domain + "info?"
        
        if short_url:
            params["shortUrl"] = short_url

            json_response = self.encode_send_request(url_method, params)
            print params
            print json_response

        else:
            params["hash"] = hash

            json_response = self.encode_send_request(url_method, params)
            print params
            print json_response

        return json_response["data"]["info"][0]["title"]
    
################################
#  METHODS WITH link/ in front #
################################

    def lookup(self, long_url):
        '''
        method searches for matching bitly link based on a long_url

        If no matching bitly_link exists, returns
        {"url": <url_you_entered>, "error": "NOT_FOUND"}

        If found, returns
        {"url": ..., "aggregate_link": <bitly_link>}
        '''
        params = self.params.copy()
        params["url"] = long_url

        url_method = self.domain + "link/lookup?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]["link_lookup"][0]

    def link_stat(self, method, short_url, unit="day", units="-1", timezone="-5",
               rollup="false", unit_reference_ts=""):
        '''
        Combined /v3/link/clicks, link/countries, link/referrers,
        link/referring_domains, link/shares all have similar structure

        Valid_methods : clicks, countries, referrers, referring_domains,
        shares (/link will be automatically added) all in STRING format

        METHOD : ALL METHODS RETURN "data" of JSON_RESPONSE
        
        default rollup is false -> meaning that different time epoch, depending
        on the selected unit, will be displayed individually        
        '''
        VALID_METHODS = ["clicks", "countries", "referrers", "referring_domains",
                         "shares"]

        params = self.params.copy()
        params["link"] = short_url
        params["unit"] = unit
        params["units"] = units
        params["timezone"] = timezone
        params["rollup"] = rollup

        ################################################
        ## Note that unit_reference_ts is deliberately #
        ## ommited, uncomment to use                   #
        ################################################        
        #params["unit_reference_ts"]=unit_reference_ts

        if method in VALID_METHODS:
            url_method = self.domain + "link/" + method + "?"
        else:
            raise ValueError("Please Enter a Valid Method!!")

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]
        

################################
#  METHODS WITH user/ in front #
################################

    def user_info(self, login=""):
        '''
        Retrieves bitly account information

        Caveat: If you use your token to access the information of
        another person's account, you'll get:
        "display_name", "profile_url", "full_name", "member_since", "login",
        "profile_image", "share_accounts"        

        Returns a dictionary

        Deliberately dropped the full_name parameters
        If you would like to add, please add it to the parameters
        '''
        params = self.params.copy()
        params["login"] = login

        url_method = self.domain + "user/info?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]

    def link_save(self, long_url, title= "", note= "", private= "false",
                  user_ts = ""):
        '''
        deliberately ommitted the user_ts section-> unsure of what its
        functionality was (bitly already keeps a timestamp on every bitly
        link created) --> use /v3/info

        returns the shortened_link and whether the link was shortened

        If previously saved the status txt of response is "LINK_ALREADY_EXISTS"
        and with status_code of 304 (which means NOT_MODIFIED)
        
        If not the status_txt is "OK", the link is generated

        privacy setting is default public (false)    
        '''
        
        params = self.params.copy()
        params["longUrl"] = long_url
        params["title"] = title
        params["note"] = note
        params["private"] = private

        url_method = self.domain + "user/link_save?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]["link_save"]["link"],json_response["status_txt"]

    def link_history(self, link="", limit="", offset="", created_before="",
                     created_after="", modified_after="", archived="",
                     private="", user=""):
        '''
        Few things to note: specify user only when accessing someone else's
        link history

        if link is specified, overrides all other options

        Returns a tuple (The number of links, list of dictionary, each key of
        the dictionary for each link)--> the shortened links can be accessed
        through "link" key of each item (dictioanry) of the list
        '''
        
        params = self.params.copy()
        params["link"] = link
        params["limit"] = limit
        params["offset"] = offset
        params["created_before"] = created_before
        params["created_after"] = created_after
        params["modified_after"] = modified_after
        params["archived"] = archived
        params["private"] = private
        params["user"] = user

        url_method = self.domain + "user/link_history?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]["result_count"], json_response["data"]["link_history"]

    def network_history(self, offset="", limit="", expand_user="false"):
        '''
        publicly saved_links from Twitter and Facebook connections)

        default expand_user is false

        returns a list of dictionaries, each entry of the list corresponding
        to a link
        '''
        params = self.params.copy()
        params["offset"]=offset
        params["limit"]=limit
        params["expand_user"] = expand_user

        url_method = self.domain + "user/network_history?"

        json_response = self.encode_send_request(url_method, params)

        return json_response["data"]["entries"]

##############################################
# Default HTTP Protocol Methods using pycurl #
##############################################

    def encode_send_request(self, url_method, params):
        
        encode_param = urllib.urlencode(params)
        full_url = url_method + encode_param        
        
        c = pycurl.Curl()
        c.setopt(c.URL, full_url)
        b = self.set_output(c)

        c.perform()

        raw_response =b.getvalue()

        return json.loads(raw_response)        
        

    def get_access_token(self, login, pw):
        '''
        This process takes the login, password of user's bitly_id
        and returns the access_token of the user for accessing
        the bitly_api

        This is meant to be used for scripting purposes only.
        Otherwise, use OAuth2 protocol (specified on the bitly API documentation)
        '''
        
        # string for USERPWD of curl_setopt
        str_to_add = str(login) + ":" + str(pw)

        #curl initiation    
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://api-ssl.bitly.com/oauth/access_token')

        #setting the output function
        b = self.set_output(c)

        c.setopt(c.HTTPHEADER, ["Accept: application/json"])
        c.setopt(c.HTTPHEADER, ["Content-Type : application/x-www-form-urlencoded"])

        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, '{:}')
        c.setopt(c.SSL_VERIFYPEER, False)

        c.setopt(c.USERPWD, str_to_add)

        c.perform()

        return b.getvalue()

    def set_output(self, curl_handler):
        b= StringIO.StringIO()
        curl_handler.setopt(curl_handler.WRITEFUNCTION, b.write)

        return b
