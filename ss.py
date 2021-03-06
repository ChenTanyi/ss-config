#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
import os
import re
import json
import zbar
import base64
import requests
import argparse
import logging

import numpy as np
from PIL import Image, ImageGrab

#------------ input ----------------
cwd = os.path.abspath(os.path.dirname(__file__))
file_name = 'ss.json'
image_file = 'a.png'

#------------ function -------------


def is_url(url):
    return re.match(r'https?://', url) is not None


def decode_url(url):
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


def get_qr(url):
    r = requests.get(url)
    r.raise_for_status()

    if not r.ok:
        logging.error('Can read the image of {}'.format(url))
        sys.exit(1)

    return r.content


def scan_qr(image):  # image or bytes data
    if isinstance(image, str):
        if is_url(image):
            image = get_qr(image)
        elif os.path.exists(image):
            with open(image, 'rb') as f:
                image = f.read()
        image = Image.open(io.BytesIO(image))

    if not isinstance(image, Image.Image):
        logging.error('Image type error, get {}'.format(type(image)))
        sys.exit(1)

    image = image.convert('L')
    image = np.array(image)

    scanner = zbar.Scanner()
    qr = scanner.scan(image)[0]

    return qr.data.decode()


def gen_config(args, decode_url):
    if args.url:
        update_config = decode_url(args.url)
    elif args.image:
        url = scan_qr(args.image)
        update_config = decode_url(url)
    else:
        im = ImageGrab.grabclipboard()
        if im:
            url = scan_qr(im)
            update_config = decode_url(url)
        else:
            update_config = {
                k: v for k, v in vars(args).items() if v is not None
            }

    return update_config


def config_update(args):
    with open(file_name, 'r') as f:
        config = json.load(f)

    print(json.dumps(config, indent = 2))

    update_config = gen_config(args, decode_url)
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
    os.chdir(cwd)
    main()