
import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem

class AmazonptclassificationPipeline(ImagesPipeline):
	
	def process_item(self, item, spider):
		return item