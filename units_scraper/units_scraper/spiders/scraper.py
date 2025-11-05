from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import time
from datetime import datetime
from units_scraper.utils import *
from pydispatch import dispatcher
from scrapy import signals
import os
import shutil
from bs4 import BeautifulSoup
class ScraperSpider(CrawlSpider):
    name = "scraper"
    allowed_domains = ["units.it"]
    start_urls = ["https://portale.units.it/it"]
    counter = 1

    # WHITELIST DI URL/REGEX PERMESSI (puoi aggiungere pattern)
    # ALLOW_URLS = [
    #     # r"^https://portale\.units\.it/it$",
    #     r"^https://portale\.units\.it/it/eventi/osservazioni-sulla-tortura-dialoghi-sul-contrasto-e-sullaccertamento-di-un-reato-universale$",
    #     # es: r".*didattica.*", r".*studenti.*"
    # ]
    config = parse_deny_config()
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=r"/it/",
                deny_domains=config.get("deny_domains", []),
                deny=config.get("deny_regex", [])
            ),
            callback="parse_item",
            follow=True
        ),
    )



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        remove_output_directory("scraper_md_output")
        dispatcher.connect(self.spider_closed, signals.engine_stopped)

    def parse_item(self, response):
        print_log(response, self.counter)

        metadata = get_metadata(response)
        cleaned_response = filter_response(response)
        md_content = parse_html_content_html2text(cleaned_response)
        self.counter += 1
        if is_informative_markdown(md_content):
            save_webpage_to_file(cleaned_response.text, md_content, response.url, self.counter, "scraper_md_output")
            item = {
                "title": metadata["title"],
                "url": response.url,
                "description": metadata["description"],
                "timestamp": metadata["date"],
                "content": md_content
            }
            yield item



    def spider_closed(self):
        print_scraping_summary(self.crawler.stats.get_stats())

