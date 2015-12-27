#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, ASCENDING
import sys
try:
    settings = __import__('settings')
except ImportError:
    print 'Error import module "settings", see settings.py.template'
    sys.exit(1)

#DB_URL = getattr(settings, 'DB_TEST_URL', {})
DB_SRC_URL = getattr(settings, 'DB_TEST_URL', {})
DB_DEST_URL = getattr(settings, 'DB_KA_URL', {})

if __name__=='__main__':
    db_name = DB_SRC_URL.split('/')[-1]
    db = MongoClient(DB_SRC_URL)[db_name]
    db_src_translate = db.translate

    db_name = DB_DEST_URL.split('/')[-1]
    db = MongoClient(DB_DEST_URL)[db_name]
    db_dest = db.images

    for idx in range(7,18):
        path_exists = []
        last_path = None
        query = {
            "path": { "$regex": "imgs%02d/"%idx }
        }
        print query
        i = 0
        for r in db_dest.find(query):
            if r.has_key('path') and r.get('path') != last_path:
                path_exists.append(r.get('path'))
                last_path = r.get('path')
                i += 1
                print '\rpath loaded: ', i,
                sys.stdout.flush()

        print '\rpath loaded: ', i
        #query = {
        #    'path': { '$exists': True },
        #    #'kacdn_url': { '$exists': False }
        #}
        query['path']['$exists'] = True
        if len(path_exists):
            query['path']['$nin'] = path_exists
        imgs = []
        last_path = None
        i = 0
        for r in db_src_translate.find(query, sort=[('path', ASCENDING), ]):
            if r.has_key('path') and r.get('path') != last_path:
                r.pop('_id', None)
                imgs.append(r)
                last_path = r.get('path')
                i += 1
                print '\rloaded: ', i,
                sys.stdout.flush()

        print
        i = 0
        for r in imgs:
            db_dest.save(r)
            i += 1
            print '\rsaved: ', i,
            sys.stdout.flush()
        print
