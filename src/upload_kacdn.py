#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import mimetypes
import random
from pymongo import MongoClient, ASCENDING
import os, sys
import time
try:
    settings = __import__('settings')
except ImportError:
    print 'Error import module "settings", see settings.py.template'
    sys.exit(1)

#DB_URL = getattr(settings, 'DB_TEST_URL', {})
DB_URL = getattr(settings, 'DB_KA_URL', {})
KACDN_UPLOAD_URL = getattr(settings, 'KACDN_UPLOAD_URL', {})

class UploadToKACDN(object):
    def __init__(self, cdn_count=5):
        super(UploadToKACDN, self).__init__()
        self.cdn_count = cdn_count

    def upload(self, content, content_type='image/jpeg', filename='image.jpg'):
        files = {
            'file': (filename, content, content_type),
        }
        cdn_idx = '%02d'%(random.randrange(self.cdn_count)+1,)
        #url = 'http://localhost:17080/upload.json'
        url = KACDN_UPLOAD_URL
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            return False
        if r.status_code != 200:
            return False
        try:
            url = json.loads(r.text).get('upload_url')
        except ValueError, e:
            return False
        try:
            r = requests.post(url, files=files)
        except requests.exceptions.ConnectionError as e:
            return False
        if r.status_code != 200:
            return False
        try:
            rv = json.loads(r.text)
        except ValueError:
            return False
        return rv.get('url', False)
 
if __name__=='__main__':
    db_name = DB_URL.split('/')[-1]
    db = MongoClient(DB_URL)[db_name]
    #db_translate = db.translate
    db_translate = db.images

    query = {
        'path': { '$exists': True },
        'kacdn_url': { '$exists': False }
    }
    kacdn = UploadToKACDN()
    last_path = None
    last_kacdn_url = None
    errs = 0
    while True:
        imgs = []
        for r in db_translate.find(query, limit=10, sort=[('path', ASCENDING), ]):
            imgs.append(r)

        if len(imgs) == 0:
            break

        for r in imgs:
            print '%s'%r.get('path'),
            sys.stdout.flush()
            if last_path != r.get('path'):
                if not os.path.isfile(r.get('path')):
                    print 'File \"%s\"" not found'%r.get('path')
                    exit(1)
                fn = r.get('path').split('/')[-1]
                ct = mimetypes.guess_type(fn)[0] or 'application/octet-stream'
                kacdn_url = kacdn.upload(open(r.get('path'), 'r'), filename=fn, content_type=ct)
                if not kacdn_url:
                    print 'Can\'t upload file \"%s\"'%r.get('path'),
                    errs += 1
                    if errs > 2:
                        print 'exit'
                        exit(2)
                    else:
                        print 'wait 10 sec to reupload'
                    time.sleep(10)
                    break
                errs = 0
            else:
                kacdn_url = last_kacdn_url
            print ' =>', kacdn_url
            r['kacdn_url'] = kacdn_url
            db_translate.save(r)

            last_path = r.get('path')
            last_kacdn_url = kacdn_url

            if os.path.isfile(r.get('path')):
                os.remove(r.get('path'))
