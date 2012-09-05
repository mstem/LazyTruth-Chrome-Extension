'''
David Woo Hyeok Kang
Made on June 19th, 2012

Bitly-Database Scripts
As of 06/19/2012, Factcheck Ask Factcheck section is taken care of

Few Notes --> models.py needs some edit
Fact Table should include Date(?Maybe), Tag Column, and Question/Answer Column
'''
import factcheck
reload(factcheck)
from bitly_connect import bitly
from bitly_db import TopCounter
from bitly_news import *
#from django.db.models import Q
#from apps.data.models import Fact, FactMetric, Source


#######################################
# For inserting facts into Fact Table #
#######################################

a = TopCounter('clicks')
b = factcheck.factcheck()

MAX_NUM = 2

def fact_generation():
    l = []
    for i in range(1, MAX_NUM):
        html = b.get_html(i)
        suml, tagl, titl = b.entry_list(html)

        for index in range(len(suml)):
            dic = {}
            q, a, detail_url = b.sum_categorize(suml[index])
            tags = b.tag_categorize(tagl[index][0])
            title, date = b.title_categorize(titl[index][0])
            
            dic['text'] = "Q: "+str(q) +"A: "+ str(a)
            if detail_url[:4] != "http":
                detail_url = "http://www.factcheck.org"+ detail_url
            dic['detail_url'] = detail_url
            dic['source'] = 'factcheck.org'
            dic['image'] = ''
            dic['title'] = title
            dic['date'] = date

            l.append(dic)

    return l
        

def parsed_fact_info_insertion(fact_data):
    '''
    Few Assumptions Made:
        raw fact_data: is in array/list format
        d = [{'fact1': {'title': ..., 'source': ..., 'detail_url': ... }},
            {'fact2': {'title': ..., }}
            ...
            ]
    '''
    iteration_level = 0
    for fact in fact_data:
        long_url = fact['detail_url']

        # somehow, django query dislikes unicode searching
        the_source = str(fact["source"])
        
        source_id = Source.objects.get(url=the_source)

        
        bitly_url = a.api.shorten(long_url)
        ##print bitly_url

        fact = Fact(title = fact['title'],
                    source = source_id,
                    detail_url = fact['detail_url'],
                    text = fact['text'],
                    image = fact['image'],
                    short_url = bitly_url)

        fact.save()

        print "done"
        print "iteration level:", iteration_level
        iteration_level += 1
        
def parsed_source_info_insertion(source_list):

    for source in source_list:
        print source['url']
        query= Source.objects.filter(url = str(source["url"]))

        print "length of query: ", len(query)

        if len(query) >= 1:
            print "one already exists"
            pass
        else:        
            s = Source(url = source["url"],
                       name = source["name"],
                       icon = source["icon"])
            s.save()

def fact_metrics_insertion(tot_links):
    link_list = tot_links
    for link in link_list:
        link = link[:-1]
        fact_obj = Fact.objects.get(short_url=str(link))

        fact_slug = fact_obj.title

        tot_clicks, top_country, country_per, top_ref, top_ref_per = get_link_numbers(link)

        fact_metric = FactMetric(fact=fact_obj,
                                 metric_name=fact_slug,
                                 metric_value = tot_clicks,
                                 metric_top_country = top_country,
                                 metric_top_country_p = country_per,
                                 metric_top_referrer = top_ref,
                                 metric_top_referrer_p = top_ref_per)
        fact_metric.save()

def get_link_numbers(link):
    tot_num_clicks = a.link_counts(link)
    top_cat_l = []
    top_val_l = []
    
    a.mod_cat('countries')
    top_country, num_clicks = a.link_category_top(link)


    for method in ["countries", 'referrers']:
        a.mod_cat(method)
        val_cat, val_count = a.link_category_top(link)

        top_cat_l.append(val_cat)
        top_val_l.append(val_count)

    percent_l = list_count_percent(top_val_l, tot_num_clicks)

    return tot_num_clicks, top_cat_l[0], percent_l[0],\
        top_cat_l[1], percent_l[1]

def list_count_percent(lst, total):
    new_lst = []
    for ele in lst:
        new_lst.append(float(ele)/total*100)
    return new_lst


'''
Deprecated Main --> Actual Facts are in Place
'''

def __main__():
    raw_data_wo_source, bitly_link_list, source_list = get_bitlynews()
    parsed_source_info_insertion(source_list)
    parsed_fact_info_insertion(raw_data_wo_source)

    fact_metrics_insertion(bitly_link_list)
    
