# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy import Request, FormRequest
from zhihuSpider.items import ZhihuItem


class ZhihuSpider(CrawlSpider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = [
        'https://www.zhihu.com'
    ]
    rules = (
        Rule(LinkExtractor(allow= ('/question/\d+#.*?',)), callback='parse_page', follow=True),
        Rule(LinkExtractor(allow=('/question/\d+', )), callback='parse_page', follow=True)
    )

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.zhihu.com/"
    }

    # 重写了爬虫类的方法,实现了自定义请求,运行成功后会调用callback回调函数
    def start_requests(self):
        return [Request("https://www.zhihu.com/login", meta = {'cookiejar' : 1}, callback = self.post_login)]

    def post_login(self, response):
        print('准备登录....')
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        print(xsrf)

        return [FormRequest.from_response(response,  # "http://www.zhihu.com/login",
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.headers,  # 注意此处的headers
                                          formdata={
                                              '_xsrf': xsrf,
                                              'email': '18747161745',
                                              'password': 'QWERTY0202'
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_page(self, response):
        problem = Selector(response)
        item = ZhihuItem()
        item['url'] = response.url
        item['name'] = problem.xpath('//span[@class="name"]/text()').extract()
        print("item['name']")
        item['title'] = problem.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()').extract()
        item['description'] = problem.xpath('//div[@class="zm-editable-content"]/text()').extract()
        item['answer'] = problem.xpath('//div[@class=" zm-editable-content clearfix"]/text()').extract()
        return item