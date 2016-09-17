# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urlparse
import base64
import random
import string
import codecs
import html2text
import os
import urllib


from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from urllib2 import unquote
from HTMLParser import HTMLParser
from dateparser import parse


from scrapy_splash import SplashFormRequest
from scrapy_splash import SplashRequest





class EventCrawlerSpider(scrapy.Spider):
    # ARGS
    target_username = ""
    email = ""
    password = ""
    geojson = {"type": "FeatureCollection", "features":[]}

    # VARS
    name = "events_crawler"
    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/4']
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

        #Version bridee a finir d'implementer
        #return SplashRequest("{0}/me".format(self.top_url),
        #        callback=self.parse_entity_id, endpoint='execute',cache_args=['lua_source'],
        #        args={'lua_source':script})


    def parse_entity_id(self, response):

        def extract_entity_id(s):
            p = re.compile(ur'"entity_id":"(\d*)"')
            search = re.search(p, s)
            return search.group(1)

        self.entity_id = extract_entity_id(response.body)

        ajax_events_url = "{0}/search/{1}/events".format(
            self.top_url, self.entity_id
        )
        # Splash, could you please open a facebook page and scroll to the end?
        # It will make FB JS code trigger BrowseScrollingPager/pageletComplete event
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
  splash:stop()
  local js = string.format("window.scrollTo(0,document.body.scrollHeight);")

  for i=1,3 do
    splash:runjs(js)
    assert(splash:wait(0.2))
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



    # To bypass the "you're not login" and get directly JSON entrypoint
    def parse_entrypoint(self, response):
        endpoint = [s for s in response.data['histoire'] if "generic.php" in s]
        return scrapy.Request(endpoint[0], self.free_data)




    def free_data(self, response):
        #need rework to catch the last cursor :/
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

        if response.url.find("cursor") >-1 and last_events_query(response.url, jason['jsmods']['require'][1][3][0]['cursor']):
            yield
        else:
            next['cursor'] = jason['jsmods']['require'][1][3][0]['cursor']
            next['page_number'] = jason['jsmods']['require'][1][3][0]['page_number']
            filename = "out/"

            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            if isinstance(jason['payload'], basestring):
            # parsed response html
            #    f = codecs.open(filename+".html", "w", encoding='utf8')
            #    f.write(sup.prettify())
            #    f.close()
            # text file, tx aaronsw
            #    f = codecs.open(filename+".txt", "w", encoding='utf8')
            #    f.write(html2text.html2text(sup.prettify()))
            #    f.close()

            # Start parsing \o/
                sup = BeautifulSoup(jason['payload'],'html.parser')
                img = sup.find_all("img")
                glm = sup.find_all(class_="_glm")
                glo = sup.find_all(class_="_glo")
                gll = sup.find_all(class_="_gll")
                for i in range(0,len(glm)):
                    event={"type": "Feature","geometry": {"type": "Point","coordinates": []},"properties": {"name": ""}}

                    event['properties']['id'] = re.split("events\/(\d+)", str(gll[i]))[1].strip()
                    event['properties']['name'] = re.split("\<|\>", str(gll[i]))[4].strip()
                    event['properties']['pic'] = re.split("\"",img[i].prettify())[7]
                    event['properties']['link'] = 'https://www.facebook.com/events/'+event['properties']['id']
                    event['properties']['attend'] = re.split("\<|\>", str(glm[i]))[8].strip()
                    event['properties']['desc'] = re.split("\<|\>", str(glo[i]))[6].strip()
                    event['properties']['date'] = str(re.split("to",re.split("\<|\>", str(glo[i]))[16]))
                    event['properties']['location'] = str(re.split("\<|\>", str(glo[i]))[24].strip())
                    rightintwo = re.split("-",event['properties']['date'])
                    if (event['properties']['date'] and len(rightintwo) > 1):
                        event['properties']['date'] = str(parse(rightintwo[0]))
                        event['properties']['date-end'] = str(parse(rightintwo[1]))
                    if (event['properties']['location']):
                        geourl= "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false"
                        clean_location = event['properties']['location'].replace(" ","+").replace(",","+")
                        googleResponse = urllib.urlopen(geourl.format(urllib.quote(clean_location)))
                        jiji = json.loads(googleResponse.read())
                        if (str(jiji['status'])=="OK"):
                            event['properties']['googleApi'] = jiji
                            event['geometry']['coordinates'].append(jiji['results'][0]['geometry']['location']['lng'])
                            event['geometry']['coordinates'].append(jiji['results'][0]['geometry']['location']['lat'])
                        else:
                            event['geometry']['coordinates']=[0,0]
                    self.geojson['features'].append(event)
                    f = codecs.open(filename+self.target_username+".geojson", "w", encoding='utf8')
                    f.write(json.dumps(self.geojson, indent=4))
                    f.close()
            L00t = NextL00t(response.url,next['cursor'], next['page_number'])
            yield scrapy.Request(L00t, callback=self.free_data)
