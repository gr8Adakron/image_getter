import scrapy
from bs4 import BeautifulSoup
import re
import pandas as pd
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
from scrapy import Request, Selector, Spider
import shutil
import os
import time
import pandas as pd
import re
from ast import literal_eval

class AmazonPTClassify(scrapy.Spider):
    name = "AmazonPTClassify"
    start_urls = []

    def __init__(self):

        self.series_name = ""
        self.author_name = ""
        self.pt_list     = pd.read_csv("PT_list_for_aravind_sir_kroger.csv")
        self.url_list    = pd.read_csv("PT_list_for_aravind_sir_kroger_url_wise.csv")
        self.final_csv   = []
        self.number_of_prod     = 0
        self.fixed_width = "._SL1500_.jpg"
        self.base_url    = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="

    def __del__(self):
        self.print_database()
        print(str(self.name)+': deleted')

    def print_database(self):
        print(" >> Printing Mapping...")
        mapping = pd.DataFrame(self.final_csv)
        mapping.to_csv("image_mapping.csv",index=False)


    def start_requests(self):
        for index,pt_row in self.pt_list.iterrows():
            pt     = pt_row["PT"]
            pt     = str(re.sub("\s+",r" ",pt))
            pt_url = pt.replace(" ","+")
            url    = self.base_url+str(pt_url)  
            self.number_of_prod     = 0
            yield scrapy.Request(url=url, callback=self.parse, meta={'PT': pt})
        for index,url_row in self.url_list.iterrows():
            url    = url_row["url"]
            pt     = url_row["pt"]
            yield scrapy.Request(url=url, callback=self.parse_by_url, meta={'PT': pt})

    def parse_by_url(self, response):
        product_type       = response.meta['PT']
        PT_page            = BeautifulSoup(response.body, "lxml") # a-row s-result-list-parent-container
        parent_container   = PT_page.find('div',{"class":"a-row s-result-list-parent-container"}) # a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal
        all_product_list   = parent_container.find_all('li',{'class':"s-result-item s-result-card-for-container s-carded-grid celwidget "})
       
        #print(pt_detailed_page)
        for single_product in all_product_list:
            single_product_detail_page_div = single_product.find('div',{"class":"a-row a-spacing-none a-spacing-top-mini"})
            single_product_detail_page_url = single_product_detail_page_div.find('a',{"class":"a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal"},href=True)["href"]
            yield scrapy.Request(url=single_product_detail_page_url, callback=self.amazon_detail_pt_page, meta={'url': single_product_detail_page_url, 'PT':product_type }) 
        
        next_target_page      = PT_page.find('a',{"class":"pagnNext"},href=True)
        try   : next_page     = str(next_target_page["href"])
        except: next_page     = None 
        if next_page is not None:
            next_page         = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_by_url, meta={'PT': product_type})

    def parse(self, response):
        product_type   = response.meta['PT']
        PT_page        = BeautifulSoup(response.body, "lxml") 
        pt_image_div   = PT_page.find_all('div',{"class":"a-fixed-left-grid-col a-col-left"})
        for single_div in pt_image_div:
            singel_pt_detail_url                = single_div.find('a',href=True)["href"] 
            yield scrapy.Request(url=singel_pt_detail_url, callback=self.amazon_detail_pt_page, meta={'url': singel_pt_detail_url, 'PT':product_type }) 

        next_target_page      = PT_page.find('a',{"class":"pagnNext"},href=True)
        try   : next_page     = str(next_target_page["href"])
        except: next_page     = None 
        if next_page is not None:
            next_page         = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, meta={'PT': product_type})

    def amazon_detail_pt_page(self,response):
        url                     = response.meta['url']
        product_name            = str(url.split("/")[-3])
        product_type            = response.meta['PT']
        source_code             = BeautifulSoup(response.body, "lxml") # imgTagWrapper
        try:
            script_source       = str(re.findall(r"colorImages.*",str(source_code))[0])
            hiresolution_images = re.findall(r"hiRes\"\:\"(.*?)\"",script_source)
            for single_image in hiresolution_images:
                try:
                    single_image_detail      =  {
                            "image_urls"   :  [single_image],
                            "image_names"  :  [product_type],
                            "product_name" :  product_name,
                            }
                    self.final_csv.append(single_image_detail)
                    yield single_image_detail   
                except:
                    continue
        except:
            return


class EbayPTClassify(scrapy.Spider):
    name = "EbayPTClassify"
    start_urls = []

    def __init__(self):

        self.series_name  = ""
        self.author_name  = ""
        self.url_list     = pd.read_csv("PT_list_for additional_data.csv")
        self.base_part    = "http://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313.TR0.TRC0.H0.X"
        self.middle_part  = ".TRS0&_nkw="
        self.last_part    = "&_sacat=0"

    def start_requests(self):
        for index,pt_row in self.url_list.iterrows():
            pt     = pt_row["PT"]
            pt     = str(re.sub("\s+",r" ",pt))
            pt_url = pt.replace(" ","+")
            url    = self.base_part+str(pt_url)+str(self.middle_part)+str(pt_url)+str(self.last_part)
            #print(url)
            yield scrapy.Request(url=url, callback=self.parse, meta={'PT': pt})

    def parse(self, response):
        product_type   = response.meta['PT']
        PT_page        = BeautifulSoup(response.body, "lxml") 
        pt_image_div   = PT_page.find_all('div',{"class":"lvpic pic img left"})
        for single_div in pt_image_div:
            pt_image                = single_div.find('img',src=True)
            try:
                pt_image_url            = pt_image['src']
                yield {
                        "image_urls"   :  [pt_image_url],
                        "image_names"  :  [product_type],
                }
            except:
                continue
                
        try   : next_page             = response.xpath('//*[@id="Pagination"]//td[@class="pagn-next"]/a/@href').extract_first()
        except: next_page             = None 

        if next_page is not None:
            print(next_page)
            next_page         = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, meta={'PT': product_type})


  # all_image_dict        = literal_eval(re.findall(r"data-a-dynamic-image='(.*?]})\'\s",str(single_pt_image[0]))[0])
        # print(all_image_dict)
        # for single_image in all_thumbnail:
        #     print(single_image)
            # try:
            #     single_image_detail =  {
            #             "image_urls"   :  [single_image],
            #             "image_names"  :  [category],
            #             }
            #     self.final_csv.append(single_image_detail)
            #     yield single_image_detail   
            # except:
            #     continue




#----------------> Working <-----------------------------

# thumbnail_image       = source_code.find('ul',{"class":"a-unordered-list a-nostyle a-button-list a-vertical a-spacing-top-micro"})
#         all_thumbnail         = thumbnail_image.find_all('img',src=True)
#         for single_image in all_thumbnail:
#             try:
#                 image_url                = re.findall(r"^(.*?)._.{3,7}\.[a-z]{1,4}",single_image['src'])[0]
#                 final_product_image_url  = image_url+self.fixed_width
#                 single_image_detail      =  {
#                         "image_urls"   :  [final_product_image_url],
#                         "image_names"  :  [product_type],
#                         "product_name" :  product_name,
#                         }
#                 self.final_csv.append(single_image_detail)
#                 yield single_image_detail   
#             except:
#                 continue