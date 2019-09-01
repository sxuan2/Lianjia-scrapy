# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:41:32 2019

@author: Administrator

add search by subway
"""

# scrawl lianjia py
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


urllist = ["https://bj.lianjia.com/zufang/jianguomenwai/",
           "https://bj.lianjia.com/zufang/jianguomennei/",
           "https://bj.lianjia.com/zufang/chaoyangmenwai1/",
           "https://bj.lianjia.com/zufang/chaoyangmennei1/",
           "https://bj.lianjia.com/zufang/chongwenmen/",
           "https://bj.lianjia.com/zufang/dongdan/",
           "https://bj.lianjia.com/zufang/dongzhimen/",
           "https://bj.lianjia.com/zufang/dongsi1/",
           "https://bj.lianjia.com/zufang/guangqumen/",
           "https://bj.lianjia.com/zufang/gongti/",
           "https://bj.lianjia.com/zufang/tiantan/",
           "https://bj.lianjia.com/zufang/cbd/",
           "https://bj.lianjia.com/zufang/panjiayuan1/",
           "https://bj.lianjia.com/zufang/shuangjing/",
           "https://bj.lianjia.com/ditiezufang/li647s20573/", # line 1 subway
            "https://bj.lianjia.com/ditiezufang/li647s20573/"
           ]

#urllist1 = ["https://bj.lianjia.com/ditiezufang/li651/"] # line 10 subway]
#
#urllistline1 = ["https://bj.lianjia.com/ditiezufang/li647s20573/", # line 1 subway
#             "https://bj.lianjia.com/ditiezufang/li647s20573/" # yonganli & dawanglu
#           ]


def urlmaker(urllist, nbr = 0, pgnbr = 1, entirerent_option = 1, \
             option_1b = 0,option_2b = 1,option_3b = 0):
    url = urllist[nbr]
    
    if entirerent_option == 1:
        url = url + "rt200600000001"
    if option_1b == 1:
        url = url + "l0"
    if option_2b == 1:
        url = url + "l1"
    if option_3b == 1:
        url = url + "l2"
#    if (entirerent_option == 1 | option_1b == 1|option_2b == 1|option_3b == 1):
    url = url + "pg" + str(pgnbr)
    url = url + "/"
    
    return url
    

def get_url_contents(url_to_scrape):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
            }
    
    response = requests.get(url_to_scrape,headers=headers,timeout=5)
    
    return response

        

def get_dataframe(response):    
    soup = BeautifulSoup(response.text, "html.parser")
    df = pd.DataFrame()
    nameList=soup.findAll("p",{"class":"content__list--item--des"})
    priceList = soup.findAll("span",{"class":"content__list--item-price"})
    urlList = soup.findAll("p",{"class":"content__list--item--title twoline"})
    
    for i in range(len(nameList)):
        name = re.sub('/? + | +/', ',', nameList[i].get_text().replace("\n","")).\
        replace(",,",",").replace("/","").split(",")
        
        price = priceList[i].get_text().split(" ")[0]
        
        url = "bj.lianjia.com" + urlList[i].a['href']
        
        d = {"name" : name[0], "area" : name[1], "direction": name[2], \
             "floorplan": name[3], "high/low": name[4], "floor": name[5],\
             "price": price, "url" : url}
        df = df.append(d, ignore_index=True)
        print("get dataframe finished!")

    return df


def get_info(urllist): 
    
    result_df1 = pd.DataFrame()
    for j in range(len(urllist)):
        url_1 = urlmaker(urllist = urllist, nbr = j, pgnbr = 1, entirerent_option = 1, option_1b = 0,option_2b = 1,option_3b = 0)
    #    默认两室整租
        response1 = get_url_contents(url_1)
        soup = BeautifulSoup(response1.text, "html.parser")
        amount = soup.find("span",{"class":"content__title--hl"}).get_text()
        pgnbr_to = int(amount)//30+1
        print("%d pages in total" % (pgnbr_to))
             
        for i in range(pgnbr_to): 
            url_to_scrape = urlmaker(urllist = urllist, nbr = j, pgnbr = i, entirerent_option = 1, option_1b = 0,option_2b = 1,option_3b = 0)
            print("scraping:"+url_to_scrape+"...")
            response = get_url_contents(url_to_scrape)    
            result_df = get_dataframe(response)
            result_df.reset_index(drop = True, inplace = True)
        
        result_df1=pd.concat([result_df,result_df1],axis=0)
        result_df1.reset_index(drop = True, inplace = True)
    
    print("get info finished!!")
    return result_df1

result_df = get_info(urllist)
result_df.reset_index(drop = True, inplace = True)
result_df['price'] = pd.to_numeric(result_df['price'])

for i in range(result_df.shape[0]):
    result_df['area'][i] = result_df['area'][i].split("㎡")[0]
result_df['area'] = pd.to_numeric(result_df['area'])   


result_df = result_df.sort_values(["price", "area"])
result_df.to_csv(r"C:\Users\Administrator\Desktop\租房.csv", encoding='utf-8_sig')

print("success")




