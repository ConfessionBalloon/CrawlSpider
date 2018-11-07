# -*- coding: utf-8 -*-
import scrapy
import re
from fang.items import NewHouseItem
from scrapy_redis.spiders import RedisSpider

class SfwSpider(RedisSpider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['http://www.fang.com/SoufunFamily.htm']
    redis_key = 'fang:start_urls'

    def parse(self, response):
        trs = response.xpath('//div[@class="outCont"]//tr')
        province = None
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            province_td = tds[0]
            province_text = province_td.xpath('.//text()').get()
            province_text = re.sub(r"\s","",province_text)
            if province_text:
                province = province_text
            if province == '其它':
                continue
            city_as = tds[1].xpath('./a')
            for city_a in city_as:
                city = city_a.xpath('./text()').get()
                city_url = city_a.xpath('./@href').get()

                city_list = city_url.split(".")
                a = city_list[0]
                if a != 'http://bj':
                    newhouse_url = a + '.newhouse.fang.com/house/s/'
                    esf_url = a + '.esf.fang.com'
                else:
                    newhouse_url = 'http://newhouse.fang.com/house/s/'
                    esf_url = 'http://esf.fang.com'
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse,meta={'info':(province,city)})
                # yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={'info': (province, city)})

    def parse_newhouse(self, response):
        province,city = response.meta['info']
        ul = response.xpath('//div[@class="nl_con clearfix"]/ul/li')
        for li in ul:
            name1 = li.xpath('.//div[@class="nlcd_name"]/a/text()').get()
            if not name1:
                continue
            name = name1.strip()

            rooms_text = li.xpath('.//div[@class="house_type clearfix"]/a/text()').getall()
            rooms = ''.join(list(filter(lambda x:x.endswith('居'),rooms_text)))

            area1 = ''.join(li.xpath('.//div[@class="house_type clearfix"]/text()').getall())
            area = re.sub(r'\s|/|－','',area1)

            district1 = ''.join(li.xpath('.//div[@class="address"]/a//text()').getall())
            district = re.search(r'.*\[(.+)\].*',district1).group(1)

            address = li.xpath('.//div[@class="address"]/a/@title').get().strip()

            sale = li.xpath('.//div[contains(@class,"fangyuan")]/span/text()').get()
            # sale = li.xpath('.//div[@class="fangyuan"]/span/text()').get()

            price1 = ''.join(li.xpath('.//div[@class="nhouse_price"]//text()').getall()).strip()
            price = re.sub(r'广告','',price1)

            origin_url = li.xpath('.//div[@class="nlcd_name"]/a/@href').get()

            item = NewHouseItem(name=name,rooms=rooms,area=area,district=district,address=address,sale=sale,price=price,origin_url=origin_url,province=province,city=city)
            print(item)
            yield item
        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url,callback=self.parse_newhouse,meta={'info':(province,city)})


    def parse_esf(self, response):
        province, city = response.meta['info']
        esf_list = response.xpath('//div[@class="shop_list shop_list_4"]/dl')
        print(esf_list)
        for dl in esf_list:
            name = dl.xpath('.//p[@class="add_shop"]/a/@title').get()
            address = dl.xpath('.//p[@class="add_shop"]/span/text()').get()
            page1 = re.sub(r'\s','',''.join(dl.xpath('.//dd/p[@class="tel_shop"]//text()').getall()))
            # rooms,area,floor,toward,year,guy = page1.split('|')
            page = page1.split('|')
            rooms = page[0]
            area = page[1]
            floor = page[2]
            toward = page[3]
            year = page[4]
            print('='*50)
            print(name,address,rooms,area,floor,toward,year,response.url)
            print('=' * 50)