#!/usr/bin/python2
# coding:utf8

import time
import urllib2
import socket

class download:
    def __init__(self, num_retries=3, timeout=20):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0'
        self.headers = {'User-Agent': self.user_agent, 'Accept-encoding':'gzip, deflate'}
        self.opener = urllib2.build_opener()
        self.num_retries = num_retries
        socket.setdefaulttimeout(timeout)

    def get(self, url):
        html = None
        while self.num_retries>=0 and not html:
            print '%s Downloading: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), url)
            try:
                request = urllib2.Request(url)
                response = self.opener.open(request)
                html = response.read()
            except Exception, e:
                print e
                pass
            self.num_retries = self.num_retries - 1
        return html

    def post(self, url, data):
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        request = urllib2.Request(url, data, self.headers)
        response = self.opener.open(request)
        print 'Downloading %s' % url 
        html = response.read()
        return html
