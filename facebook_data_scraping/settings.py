# -*- coding: utf-8 -*-

# Scrapy settings for facebook_data_scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'facebook_data_scraping'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0 ~> 3ayn (BB-0.8)'


SPIDER_MODULES = ['facebook_data_scraping.spiders']
NEWSPIDER_MODULE = 'facebook_data_scraping.spiders'


#USER_AGENT = 'facebook_data_scraping (+http://www.yourdomain.com)'

# Throttling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_DEBUG = True

URLLENGTH_LIMIT = 13337

SPLASH_URL = 'http://localhost:32775'

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
SPLASH_COOKIES_DEBUG = True
COOKIES_ENABLED = True
