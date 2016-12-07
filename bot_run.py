#!/usr/bin/env python
#
# Author: zhangjoto
# E-Mail: zhangjoto@gmail.com
#
# Create Date: 2016-10-09
#

import logging
import subprocess

import bot_api


cmds = {}


def load_token():
    with open('token.txt') as fp:
        return fp.read().strip()

def route(cmd):
    def decorate(func):
        cmds[cmd] = func
        return func
    return decorate


@route('ip')
def get_external_ip():
    output = subprocess.check_output(['upnpc', '-s'])
    for line in output.decode().splitlines():
        if line.startswith('ExternalIPAddress'):
            return line.split(' = ')[1]


@route('open')
def open_sshd():
    try:
        output = subprocess.check_output(
                ['sudo', 'systemctl', 'start', 'out_sshd'])
        return 'sshd opened, server ip: {}'.format(get_external_ip())
    except subprocess.CalledProcessError as err:
        return err


@route('close')
def close_sshd():
    try:
        output = subprocess.check_output(
                ['sudo', 'systemctl', 'stop', 'out_sshd'])
        return 'sshd closed.'
    except subprocess.CalledProcessError as err:
        return err


def main():
    proxies = {'http': 'socks5://127.0.0.1:9050',
               'https': 'socks5://127.0.0.1:9050'}
    api = bot_api.TelegramApi(token=load_token(), proxies=proxies)
    for meta, mesg  in api.iter_message():
        if (meta['first_name'] in ('zhangjoto', 'yarlinghe') and
                meta['type'] == 'private'):
            mesg = mesg.lower()
            if mesg in cmds:
                try:
                    ret = cmds[mesg]()
                except Exception as err:
                    ret = str(err)
            else:
                ret = 'Invalid command.'
            api.send_message({'chat_id': meta['id'], 'text': ret})


if __name__ == '__main__':
    main()
