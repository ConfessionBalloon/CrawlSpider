# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from boss_demo.items import BossDemoItem

class BossSpider(CrawlSpider):
    name = 'boss'
    allowed_domains = ['zhipin.com']
    start_urls = ['https://www.zhipin.com/c101280600/?query=python&page=1']

    rules = (
        Rule(LinkExtractor(allow=r'.+\?query=python&page=\d'), follow=True),
        Rule(LinkExtractor(allow=r'.+job_detail/\w+~.html'), callback='parse_job', follow=False),
    )

    def parse_job(self, response):
        title = response.xpath('//div[@class="name"]/h1/text()').get().strip()
        salary = response.xpath('//div[@class="name"]/span/text()').get().strip()
        info = response.xpath('//div[@class="job-primary detail-box"]/div[@class="info-primary"]/p//text()').getall()
        city = info[0].split("：")[1]
        work_years = info[1].split("：")[1]
        education = info[2].split("：")[1]
        company = response.xpath('//div[@class="info-company"]/h3/a/text()').get()
        content = response.xpath('//div[@class="detail-content"]/div[@class="job-sec"]/div[@class="text"]//text()').getall()
        content = "".join(content).strip()
        item = BossDemoItem(title=title, salary=salary, city=city, work_years=work_years, education=education, company=company, content=content)
        yield item