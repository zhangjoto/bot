#!/usr/bin/env python
#
# Author: zhangjoto
# E-Mail: zhangjoto@gmail.com
#
# Create Date: 2016-10-04
#

import atexit
import logging
import json
import time

import requests


class TelegramApi():
    def __init__(self, token, proxies={}):
        self.bot_url = 'https://api.telegram.org/bot{}'.format(token)
        self.logger = logging.getLogger(__name__)
        self.offset = self.get_offset()
        atexit.register(self.save_offset)
        self.proxies = proxies

    def save_offset(self):
        with open('offset.txt', 'w') as fp:
            fp.write(str(self.offset))

    def get_offset(self):
        try:
            with open('offset.txt') as fp:
                return int(fp.read())
        except OSError:
            return 0

    def iter_message(self):
        query_url = '{}/getUpdates'.format(self.bot_url)
        while True:
            try:
                q = requests.post(query_url, data={'offset': self.offset + 1},
                                  proxies=self.proxies)
                # 防止网络原因导致收到的应答报文不完整
                resp = json.loads(q.content.decode())
            except Exception as err:
                self.logger.error(err)
                continue
            if resp['ok']:
                for result in resp['result']:
                    mesg = result['message']
                    # 只处理文本消息，声音图片等消息一概忽略
                    if 'text' in mesg:
                        yield mesg['chat'], mesg['text']
                    # 每条消息更新一次offset，避免出现result未赋值的异常
                    self.offset = result['update_id']
            time.sleep(5)

    def send_message(self, mesg):
        send_url = '{}/sendMessage'.format(self.bot_url)
        try:
            p = requests.post(send_url, data=mesg, proxies=self.proxies)
        except Exception as err:
            self.logger.error(err)
