#!/usr/bin/env python
# -*- coding: utf-8 -*-

#                                  #
#  RUN SCRIPT FROM ROOT DIRECTORY  #
#                                  #

import glob
import os
import sys
from pymongo import MongoClient
import re
try:
    settings = __import__('settings')
except ImportError:
    print 'Error import module "settings", see settings.py.template'
    sys.exit(1)

DB_URL = getattr(settings, 'DB_KA_URL', {})


if __name__=='__main__':
    db_name = DB_URL.split('/')[-1]
    db = MongoClient(DB_URL)[db_name]
    db_images = db.images

    header_url = 'http://gdrive-cdn.herokuapp.com/537b65a5bc09f0000721dda7/512px-barcode.png'

    files = glob.glob('./before_replace/2*.md')
    files.sort()
    time_match = re.compile('(\d{2}):(\d{2})\s')
    while len(files):
        day_files = [files[0], ]
        files.pop(0)
        date = os.path.basename(day_files[0])[:10]
        print date,
        sys.stdout.flush()
        while len(files) and os.path.basename(files[0]).startswith(date):
            day_files.append(files[0])
            files.pop(0)
        print len(day_files), 'files,',
        sys.stdout.flush()

        records = []
        for fn in day_files:
            with open(fn, 'r') as fi:
                for line in fi:
                    line = line.decode('utf-8').strip()
                    if len(line) and header_url not in line:
                        # not empty and not ![img](http://gdrive-cdn.herokuapp.com/537b65a5bc09f0000721dda7/512px-barcode.png)
                        records.append(line)
        print len(records), 'records,',
        sys.stdout.flush()

        links = []
        for r in records:
            i = 0
            while r.find('[![img](', i) > -1:
                x = r.find('[![img](', i) + 8
                i = r.find(')', x)
                url = r[x:i]
                if url.startswith('https://github.com/derand/kanojo_activity/raw/master/'):
                    #url = url[len('https://github.com/derand/kanojo_activity/raw/master/'):]
                    print r
                    exit(1)
                if url not in links:
                    links.append(url)
                #print url,
            #print
        print len(links), 'unique,',
        sys.stdout.flush()

        query = {
            'url': { '$in': links }
        }
        #print db_images.find(query).count(),
        translate = {}
        for r in db_images.find(query):
            if r.has_key('kacdn_url'):
                #translate['https://github.com/derand/kanojo_activity/raw/master/'+r.get('path')] = r.get('kacdn_url')
                translate[r.get('url')] = r.get('kacdn_url')

        pieces = int(round(float(len(records))/1000)) + 1
        print pieces, 'pieces ',
        sys.stdout.flush()
        file_idx = -1
        hour = 0
        fout = None
        for r in records:
            tmp = time_match.search(r)
            if tmp:
                hour = int(tmp.groups()[0])
            #else:
            #    print 'error', r
            #    exit()
            if hour == 23 and file_idx < 1:
                idx = 0
            else:
                idx = hour/(24/pieces)

            if idx > file_idx:
                print '*',
                sys.stdout.flush()
                file_idx = idx
                if fout:
                    fout.close()
                fn = '%s_%d.md'%(date, file_idx+1)
                fout = open(fn, 'w')
                fout.write('![img](%s)\n\n'%header_url)
 
            i = 0
            while r.find('[![img](', i) > -1:
                x = r.find('[![img](', i) + 8
                i = r.find(')', x)
                url = r[x:i]
                if translate.has_key(url):
                    r = r.replace(url, translate[url])
            fout.write(r.encode('utf-8'))
            fout.write('\n\n')

        if fout:
            fout.close()

        for dfn in day_files:
            os.remove(dfn)

        print
