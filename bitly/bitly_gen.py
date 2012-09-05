import bitly_api as bitly
from apps.data.models import fact as Fact


'''
Date: 05/31/12  | LazyTruth Project  | Bit.ly Link Automatic Production

09/05/12
For MY_API_KEY : get it from bitly
For Your_Id : input your id
'''
YOUR_ID = 'Your ID'
MY_API_KEY = 'YOUR API'

#The common connection that is used for all internet connection
#to the bitly server
api = bitly.Connection(YOUR_ID, MY_API_KEY)

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
    

    
        
        
