# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urlparse
import base64
import random
import string
import codecs

from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from urllib2 import unquote
from HTMLParser import HTMLParser

from scrapy_splash import SplashFormRequest
from scrapy_splash import SplashRequest

from facebook_data_scraping.items import FacebookPhoto


class EventCrawlerSpider(scrapy.Spider):
    # ARGS
    target_username = ""
    email = ""
    password = ""

    # VARS
    name = "events_crawler"
    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/zuck']
    top_url = 'https://www.facebook.com'

    def __init__(self, *args, **kwargs):
      super(EventCrawlerSpider, self).__init__(*args, **kwargs)
      self.email = kwargs.get('email')
      self.password = kwargs.get('password')
      self.target_username = kwargs.get('target_username')

    def parse(self, response):
        return [FormRequest("https://m.facebook.com/login.php",
            formdata={
                'email': self.email,
                'pass': self.password
            }, callback=self.parse_post_login)
        ]

    def parse_post_login(self, response):
        script = """
treat = require("treat")
function main(splash)
  local urls = {}
  splash:init_cookies(splash.args.cookies)
  splash:on_request(function(request)
        table.insert(urls, request.url)
  end)
  splash.images_enabled = false
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })

  assert(splash:wait(0.7))

  local entries = splash:history()
  local last_response = entries[#entries].response
  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
    screen = splash:png(),
    histoire = treat.as_array(urls),
  }
end        """
        return SplashRequest("{0}/{1}".format(self.top_url, self.target_username),
                callback=self.parse_entity_id, endpoint='execute',cache_args=['lua_source'],
                args={'lua_source':script})

    def parse_entity_id(self, response):

        def extract_entity_id(s):
            p = re.compile(ur'"entity_id":"(\d*)"')
            search = re.search(p, s)
            return search.group(1)

        self.entity_id = extract_entity_id(response.body)

        ajax_events_url = "{0}/search/{1}/events".format(
            self.top_url, self.entity_id
        )
        script = """
treat = require("treat")
function main(splash)
  local urls = {}
  splash:init_cookies(splash.args.cookies)
  splash:on_request(function(request)
        table.insert(urls, request.url)
  end)
  splash.images_enabled = false
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(0.5))
  splash:stop()
  local js = string.format("window.scrollTo(0,document.body.scrollHeight);")

  for i=1,3 do
    splash:runjs(js)
    assert(splash:wait(0.5))
  end

  splash:set_viewport_full()

  local entries = splash:history()
  local last_response = entries[#entries].response
  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
    screen = splash:png(),
    histoire = treat.as_array(urls),
  }
end        """
        return SplashRequest(ajax_events_url, callback=self.parse_entrypoint,
                                    endpoint='execute',
                                    cache_args=['lua_source'],
                                    args={'lua_source':script})

    def parse_entrypoint(self, response):
        # To bypass the "you're not login" and get directly JSON payloads

        endpoint = [s for s in response.data['histoire'] if "generic.php" in s]
        #for i in range (1,10):
        #    sploit.append(re.sub(r"page_number%22%3A(\d)","page_number%22%3A{0}".format(i),endpoint[0]))

        #for url in sploit:
            #yield SplashRequest(url, self.parse_data, args={'wait': 0.5})
        return scrapy.Request(endpoint[0], self.parse_data)


    def parse_data(self, response):

        def last_events_query(url, next_cursor):
            parsed = urlparse.urlparse(url)
            cursor = json.loads(urlparse.parse_qs(parsed.query)['data'][0])['cursor']
            return cursor == next_cursor


        def NextL00t(url, next_cursor, next_pagenumber):
            return re.sub(r"%22cursor%22%3A%22(.)+%22%2C%22page_number%22%3A(\d)+%2C%22",
                "%22cursor%22%3A%22{0}%22%2C%22page_number%22%3A{1}%2C%22".format
                (next_cursor, next_pagenumber),url)


        next = {}
        if response.body.startswith("for (;;);"):
            jason = json.loads(response.body[9:]) #remove prefix "for (;;);""
        else:
            jason = json.loads(response.body)

        #inspect_response(response, self)
        #paypay = unquote(jason['payload'])
        #h = HTMLParser()
        #soup = BeautifulSoup(h.unescape(paypay), 'html.parser')
        #sup = BeautifulSoup(jason['payload'],'html.parser')
        #html = sup.prettify(sup.original_encoding)

        if response.url.find("cursor") >-1 and last_events_query(response.url, jason['jsmods']['require'][1][3][0]['cursor']):
            yield
        else:
            next['cursor'] = jason['jsmods']['require'][1][3][0]['cursor']
            next['page_number'] = jason['jsmods']['require'][1][3][0]['page_number']
            #json format
            with open("out/"+self.target_username+"/"+next['cursor'][:7]+".json", "wb") as file:
                json.dump(jason,file)

            if isinstance(jason['payload'], basestring):
            #inspect_response(response, self)
            # parsed html
                f = codecs.open("out/"+self.target_username+"/"+next['cursor'][:7]+".html", "w", encoding='utf8')
                sup = BeautifulSoup(jason['payload'],'html.parser').prettify()
                f.write(sup)
                f.close()
            # text
                f = codecs.open("out/"+self.target_username+"/"+next['cursor'][:7]+".txt", "w", encoding='utf8')
                notag = re.sub(r"<.*?>","",sup)
                csv = re.sub('[\r]', ';', notag)
                f.write(csv)
                f.close()


            ajax_photos_url = NextL00t(response.url,next['cursor'], next['page_number'])
            yield scrapy.Request(ajax_photos_url, callback=self.parse_data)
