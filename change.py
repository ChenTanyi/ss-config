#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import base64
import qrtools
import urllib.request
import argparse
import logging

#------------ input ----------------
cwd = os.path.abspath(os.path.dirname(__file__))
os.chdir(cwd)
file_name = 'ss.json'

#------------ function -------------


def decodeUrl(url):
    if re.match('ss://', url) is None:
        logging.error('url {} need to be: ss://***'.format(url))
        return dict()
    raw = base64.b64decode(url[5:]).decode().strip().split(':')
    assert (len(raw) == 3)
    keys = ['method', 'password', 'server', 'server_port']
    values = [raw[0]] + raw[1].split('@') + [int(raw[2])]
    return dict(zip(keys, values))


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url')
    parser.add_argument('-i', '--image')
    parser.add_argument('-sp', '--server_port', type = int)
    parser.add_argument('-s', '--server')
    parser.add_argument('-p', '--password')
    parser.add_argument('-m', '--method')

    args = parser.parse_args()
    return args


def config_update(args):
    with open(file_name, 'r') as f:
        config = json.load(f)

    print(json.dumps(config, indent = 2))

    update_config = dict()
    if args.url:
        update_config = decodeUrl(args.url)
    elif args.image:
        url = args.image
        qrImgFile = url.split('/')[-1]

        try:
            u = urllib.request.urlopen(url)
            with open(qrImgFile, 'wb') as qrImg:
                qrImg.write(u.read())
        except:
            if os.path.exists(qrImgFile):
                os.remove(qrImgFile)
            logging.error('Can read the image of {}'.format(url))
            sys.exit(1)

        qr = qrtools.QR()
        qr.decode(qrImgFile)
        update_config = decodeUrl(qr.data)

        os.remove(qrImgFile)
    else:
        kwargs = vars(args)
        update_config = {k: v for k, v in kwargs.items() if v is not None}

    if not update_config:
        return
    config.update(update_config)

    print(json.dumps(config, indent = 2))

    with open(file_name, 'w') as f:
        json.dump(config, f, indent = 2)


def main():
    args = arg_parse()
    config_update(args)


if __name__ == '__main__':
    main()