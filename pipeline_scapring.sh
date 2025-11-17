#!/bin/bash
    cd units_scraper
    scrapy crawl scraper -s DEPTH_LIMIT=1 -O ../items.jsonl
    cd ../links_study
    python3 main.py
    cd ..
    python3 pages_cleaner.py --input items.jsonl --output filtered_items.jsonl --verbose