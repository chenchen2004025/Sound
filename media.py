# __author__ = chenchen
# -*- coding: utf-8 -*-
from basic import Basic
import urllib2
import json
import poster.encode
from poster.streaminghttp import register_openers

class Media(object):
    def __init__(self):
        register_openers()
    #上传图片
    def uplaod(self, accessToken, filePath, mediaType):
        accessToken = Basic().get_access_token()
        openFile = open(filePath, "rb")
        param = {'media': openFile}
        postData, postHeaders = poster.encode.multipart_encode(param)

        postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
        request = urllib2.Request(postUrl, postData, postHeaders)
        urlResp = urllib2.urlopen(request)
        print urlResp.read()

    def get(self, mediaId, mediaType):
        accessToken = Basic().get_access_token()
        postUrl = "\nhttps://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (accessToken, mediaId)
        urlResp = urllib2.urlopen(postUrl)
        print postUrl
        headers = urlResp.info().__dict__['headers']
        if ('Content-Type: application/json\r\n' in headers) or ('Content-Type: text/plain\r\n' in headers):
            jsonDict = json.loads(urlResp.read())
            print jsonDict
        else:
            buffer = urlResp.read()  # 素材的二进制
            if mediaType == 'image':
                mediaFile = file("test_media.jpg", "wb")
            else:
                mediaFile = file("test_media.jpg", "wb")
            mediaFile.write(buffer)
            print "get successful"
