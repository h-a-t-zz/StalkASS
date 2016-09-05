# -*- coding: utf-8 -*-

# Scrapy settings for facebook_data_scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'facebook_data_scraping'

#USER_AGENT = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0 ~> 3ayn (BB-0.8)'


SPIDER_MODULES = ['facebook_data_scraping.spiders']
NEWSPIDER_MODULE = 'facebook_data_scraping.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'facebook_data_scraping (+http://www.yourdomain.com)'

ITEM_PIPELINES = {'facebook_data_scraping.pipelines.FacebookImagesPipeline':10}
IMAGES_STORE = "./downloaded-photos"

# Throttling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_DEBUG = True

URLLENGTH_LIMIT = 13337

SPLASH_URL = 'http://163.172.176.190:32922'

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
