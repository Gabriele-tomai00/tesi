# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import w3lib.html
import os
import shutil
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse


class cleanContentPipeline:
    def process_item(self, item, spider):
        soup = BeautifulSoup(item.text, "lxml")
        to_return = {}
        to_return['body'] = item.text
        to_return['cleaned'] = soup.body.get_text(strip=True)
        return to_return

class saveBodyPipeline:
    def __init__(self):
        self.output_dir = "output_bodies"
        os.makedirs(self.output_dir, exist_ok=True)
        self.counter = 1  # Per creare nomi di file unici

    def process_item(self, item, spider):
        if 'body' in item:
            original_path = os.path.join(self.output_dir, f"{self.counter}_original.html")
            with open(original_path, "w", encoding="utf-8") as f:
                f.write(item['body'])

            parsed_url = urlparse(item.url)
            domain = parsed_url.netloc
            cleaned_path = os.path.join(self.output_dir, f"{self.counter}{domain}.html")
            with open(cleaned_path, "w", encoding="utf-8") as f:
                f.write(item['cleaned'])

            self.counter += 1

        return item
    

class getMetadataPipeline:
    def process_item(self, item, spider):
        return item

class html2textPipeline:
    def process_item(self, item, spider):
        h = html2text.HTML2Text()
        h.ignore_links = True          # <--- non stampa gli href
        h.ignore_images = True         # <--- nel dubbio
        h.body_width = 0               # <--- no wrapping forzato, più leggibile
        # item['content'] = h.handle(item['body'])
        del item["body"]
        return item
    

class saveWebpagePipeline:
    def __init__(self):
        self.output_dir = "output_bodies"
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)  # cancella TUTTA la cartella
        os.makedirs(self.output_dir, exist_ok=True)
        self.counter = 1  # Per creare nomi di file unici

    def process_item(self, item, spider):
        original_path = os.path.join(self.output_dir, f"{self.counter}_original.html")
        with open(original_path, "w", encoding="utf-8") as f:
            f.write(item['body'])

        cleaned_path = os.path.join(self.output_dir, f"{self.counter}_cleaned.html")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            f.write(item['content'])

        self.counter += 1
        return item
    

class saveLinksPipeline:
    def __init__(self):
        self.file_path = "units_links.txt"
        with open(self.file_path, "w") as f:
            pass

    def process_item(self, item, spider):
        if 'url' in item:
            with open(self.file_path, "a") as f:
                f.write(item['url'] + "\n")
        return item