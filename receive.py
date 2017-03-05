# __author__ = chenchen
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import os


def parse_xml(web_data):
    if len(web_data) == 0:
        return None
    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == 'text':
        return TextMsg(xmlData)
    elif msg_type == 'image':
        return ImageMsg(xmlData)
    elif msg_type == 'voice':
        return VoiceMsg(xmlData)


class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text.encode("utf-8")


class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text

class VoiceMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.MediaId = xmlData.find('MediaId').text
        midia_id = xmlData.find('MediaId').text
        access_token = 'JSjUozBnWYQ3eGnR8ESdHZHZT7RRRmxvT5aSP6cwPmCKpSfxXDbfP1BjshehoGK087TMkV1jLgcBlSYqWiRbAzxcraUR-hipk1MCpg3Lf7QHBGpL0FaD0O5VxfkQdogoWYXiAAABDC'
        file_url = '\"https://api.weixin.qq.com/cgi-bin/media/get?access_token=' + access_token + '&media_id=' + midia_id + '\"'
        download_command ='curl -I -G ' + file_url
        tmp = os.popen(download_command).readlines()
        print tmp