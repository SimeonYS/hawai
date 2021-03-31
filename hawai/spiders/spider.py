import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import HawaiItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class HawaiSpider(scrapy.Spider):
	name = 'hawai'
	year = 2020
	start_urls = ['https://www.asbhawaii.com/news/stories/2021']

	def parse(self, response):
		post_links = response.xpath('//a[@class="readmore"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.asbhawaii.com/news/stories/{self.year}'
		if self.year > 2011:
			self.year -= 1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//span[@class="datetime"]/text()').get()
			date = re.findall(r'\w+\s\d+\,\s\d+', date)
		except TypeError:
			date = ""
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="col-sm-8 col-sm-offset-2 col-xs-12"]//text()[not (ancestor::h1 or ancestor::span)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=HawaiItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
