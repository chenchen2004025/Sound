# __author__ = chenchen
# -*- coding: utf-8 -*-
import urllib
import time
import json


class Basic:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):
        appId = "wx885bdaac4012f92e"
        appSecret = "d3acc5e8cc31c84856b047775429eefc"

        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (appId, appSecret))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())

        self.__accessToken = urlResp['JSjUozBnWYQ3eGnR8ESdHZHZT7RRRmxvT5aSP6cwPmCKpSfxXDbfP1BjshehoGK087TMkV1jLgcBlSYqWiRbAzxcraUR-hipk1MCpg3Lf7QHBGpL0FaD0O5VxfkQdogoWYXiAAABDC']
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

    def run(self):
        while (True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()