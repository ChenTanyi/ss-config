#!/usr/bin/env bash

dir=$(dirname $0)
cd $dir
docker rm -f v2ray
docker-compose -p v2ray -f v2.yml up