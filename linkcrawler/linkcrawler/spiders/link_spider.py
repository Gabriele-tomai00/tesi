from scrapy import Spider
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse, urlunparse
import os
import time
from datetime import datetime
import sys
from w3lib.url import canonicalize_url

def normalize_url(url):
    parsed = urlparse(url)
    normalized = parsed._replace(fragment='')
    canonical_url = canonicalize_url(normalized)
    #if url != canonical_url:
        #print(f"Normalized URL: {url} -> {canonical_url}")
    return canonical_url


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = round(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def print_progress(number_of_links):
    if number_of_links % 1000 == 0:
        print(f"Links found (in progress): {number_of_links}", end='\r')

def clean_urls(file_path="units_links.txt"):
    with open(file_path, "r") as f:
        urls = {line.strip() for line in f if line.strip()}

    urls_sorted = sorted(urls)

    # sovrascrivo lo stesso file
    with open(file_path, "w") as f:
        for url in urls_sorted:
            f.write(url + "\n")

    print(f"Totale URL unici: {len(urls_sorted)}")
    print(f"Ora il file {file_path} è stato ripulito e ordinato.")


class UNITSspider(Spider):
    name = 'UNITSspider'
    allowed_domains = ["portale.units.it"]
    start_urls = ["https://portale.units.it/it"]
    start_time = None
    # Set per URL normalizzati
    visited_urls = set()

    custom_settings = {
        'CONCURRENT_REQUESTS': 100,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'AUTOTHROTTLE_START_DELAY': 0,
        'AUTOTHROTTLE_MAX_DELAY': 20,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 60,
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'CRITICAL',
        'USER_AGENT': 'UNITS Links Crawler (network lab)',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_TIMEOUT' : 20,
        'DEPTH_LIMIT': int(sys.argv[1]) if len(sys.argv) > 1 else 1,
    }

    def __init__(self):
        self.link_extractor = LinkExtractor(
            unique=True,
            allow_domains=["portale.units.it"],
            deny_domains=["arts.units.it", "openstarts.units.it", "moodle.units.it", "moodle2.units.it", 
                          "wmail1.units.it", "cargo.units.it", "cspn.units.it", "www-amm.units.it", 
                          "inside.units.it", "flux.units.it", "centracon.units.it", "smats.units.it",
                          "docenti.units.it", "orari.units.it"],
            deny=[r".*feedback.*", r".*search.*", r"#", r".*eventi-passati.*", 
                  r".*openstarts.*", r".*moodle.units.*", r".*moodle2.units.*", 
                  r".*wmail1.*", r".*cargo.*", r".*wmail3.*", r".*wmail4.*",]
        )
        try:
            os.remove('units_links.txt')
        except OSError:
            pass
        self.start_time = time.time()

    def start_requests(self):
        self.start_time = time.time()
        self.start_datetime = datetime.now()  # salvo data/ora di inizio
        print("\n====== CRAWLING SESSION " + str(self.start_datetime.strftime('%d-%m-%Y %H:%M:%S')) + " ======\n")
        print("Custom settings:")
        for key in sorted(self.custom_settings.keys()):
            print(f"   {key}: {self.custom_settings[key]}")

        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)



    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            normalized_url = normalize_url(link.url)
            if normalized_url not in self.visited_urls:
                self.visited_urls.add(normalized_url)
                #print(f"Actual number of links fonud: {len(self.visited_urls)}")
                with open('units_links.txt','a+') as f:
                    f.write(f"\n{str(normalized_url)}")
                print_progress(len(self.visited_urls))
                yield response.follow(url=link, callback=self.parse)


    def closed(self, reason):
        clean_urls()
        duration = format_time(time.time() - self.start_time)
        stats = self.crawler.stats.get_stats()
        response_counts = stats.get('downloader/response_status_count', {})

        with open('crawling_summary.log', 'a') as f:
            f.write("====== CRAWLING SESSION " + str(self.start_datetime.strftime('%d-%m-%Y %H:%M:%S')) + " ======\n")
            f.write(f"End time:   {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
            f.write(f"Duration:   {duration}\n")
            f.write(f"Links found: {len(self.visited_urls)}\n")
            f.write("Custom settings:\n")
            f.write(f"   CONCURRENT_REQUESTS: {self.custom_settings.get('CONCURRENT_REQUESTS', 'N/A')}\n")
            f.write(f"   ROBOTSTXT_OBEY: {self.custom_settings.get('ROBOTSTXT_OBEY', 'N/A')}\n")
            f.write(f"   DOWNLOAD_TIMEOUT: {self.custom_settings.get('DOWNLOAD_TIMEOUT', 'N/A')}\n")
            f.write(f"   DEPTH_LIMIT: {self.custom_settings.get('DEPTH_LIMIT', 'N/A')}\n")
            f.write("\n")
 
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(UNITSspider)
    process.start()
