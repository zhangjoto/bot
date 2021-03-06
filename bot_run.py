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


@route('stat')
def get_stat():
    output1 = subprocess.check_output(['uptime'])
    output2 = subprocess.check_output(['free', '-m'])
    # 暂时只取uptime和free的输出，输出格式还需要针对小屏优化
    return (output1 + output2).decode()


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
    # 执行指令前指定语言环境，避免输出格式受环境影响，并确保任意终端上正常输出
    import os
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    for meta, mesg in api.iter_message():
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
