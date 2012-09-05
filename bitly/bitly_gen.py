import bitly_api as bitly
from apps.data.models import fact as Fact


'''
Date: 05/31/12  | LazyTruth Project  | Bit.ly Link Automatic Production
'''
MY_API_KEY = 'R_097be7781d78d2663f8e9af9137796ed'

#The common connection that is used for all internet connection
#to the bitly server
api = bitly.Connection('dkang9322', MY_API_KEY)

def parsed_fact_info_insertion(fact_data):
    '''
    Few Assumptions Made:
        raw fact_data: is in array/list format
        d = [{'fact1': {'title': ..., 'source': ..., 'detail_url': ... }},
            {'fact2': {'title': ..., }}
            ...
            ]
    Please refer to documentation of bitly_python module for detailed
    information about the api
    '''
    #api = bitly.Connection('dkang9322', MY_API_KEY)
    
    for fact in fact_data:
        long_url = fact['detail_url']
        bitly_url = api.shorten(long_url)['url']

        fact = Fact(title = fact['title'],
                    source = fact['source'],
                    detail_url = fact['detail_url'],
                    text = fact['text'],
                    image = fact['image'],
                    short_url = bitly_url)
        fact.save()

def __main__():
    fact_raw_data = open('fact_list.txt')
    

    
        
        
