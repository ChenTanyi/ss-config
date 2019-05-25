#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import base64
import json
import argparse

#------------ input ----------------
cwd = os.path.abspath(os.path.dirname(__file__))
file_name = 'v2.json'

#------------ function -------------
sys.path.append(cwd)
import ss


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url')
    parser.add_argument('-i', '--image')
    parser.add_argument('-a', '--add')
    parser.add_argument('-p', '--port', type = int)
    parser.add_argument('-n', '--id')
    parser.add_argument('-l', '--aid', type = int)

    args = parser.parse_args()
    return args


def gen_v2json(raw):
    '''
    raw json in v2N
    '''
    config = dict()
    if raw.get('add'):
        config['address'] = raw.get('add')
    if raw.get('port'):
        config['port'] = int(raw.get('port'))
    if raw.get('id'):
        config['users'] = [{
            'id': raw.get('id'),
            'level': 1,
            'alterId': int(raw.get('aid', 64))
        }]

    stream_setting = dict()
    net = raw.get('net')
    if net:
        if net == 'h2':
            net = 'http'
        stream_setting['network'] = net
        if raw.get('tls') == 'tls':
            stream_setting['security'] = 'tls'

        settings = net + 'Settings'
        if net == 'kcp' and raw.get('type'):
            stream_setting[settings] = {'header': {'type': raw.get('type')}}

        if net == 'ws':
            stream_setting[settings] = {
                'path': raw.get('path', '/'),
                'headers': {
                    'Host': raw.get('host', '')
                }
            }

        if net == 'http':
            stream_setting[settings] = {
                'host': raw.get('host', '').split(','),
                'path': raw.get('paht', '/')
            }

    return config, stream_setting


def decode_url(url):
    if re.match('vmess://', url) is None:
        logging.error('url {} need to be: vmess://***'.format(url))
        return dict()
    raw = base64.b64decode(url[8:])
    raw = json.loads(raw)

    return raw


def update_config(args):
    with open(file_name, 'r') as f:
        config = json.load(f)
    server_config = config['outbound']['settings']['vnext'][0]
    print(json.dumps(server_config, indent = 2))

    raw = ss.gen_config(args, decode_url)
    if not raw:
        return

    print(json.dumps(raw, indent = 2))

    update_config, stream_setting = gen_v2json(raw)

    server_config.update(update_config)
    config['outbound']['streamSettings'] = stream_setting

    print(json.dumps(server_config, indent = 2))
    print(json.dumps(stream_setting, indent = 2))

    with open(file_name, 'w') as f:
        json.dump(config, f, indent = 2)


def main():
    args = arg_parse()
    update_config(args)


if __name__ == '__main__':
    os.chdir(cwd)
    main()