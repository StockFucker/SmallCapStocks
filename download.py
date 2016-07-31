#!/usr/bin/python2
# coding:utf8

import urllib
import urllib2
import socket

class download:
    def __init__(self, timeout=20):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0'
        self.headers = {'User-Agent': self.user_agent, 'Accept-encoding':'gzip, deflate'}
        self.opener = urllib2.build_opener()
        socket.setdefaulttimeout(timeout)

    def get(self, url):
        print 'Downloading: %s' % url
        request = urllib2.Request(url)
        response = self.opener.open(request)
        html = response.read()
        return html
    
    def post(self, url, data):
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        request = urllib2.Request(url, data, self.headers)
        response = self.opener.open(request)
        print 'Downloading %s' % url
        html = response.read()
        return html

if __name__ == '__main__':
    download().get('http://qt.gtimg.cn/q=sh600307')
