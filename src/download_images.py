#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Andrey Derevyagin'
__copyright__ = 'Copyright © 2015'

import glob
import json
import urllib2, socket, httplib
import hashlib
import os, sys
import time
from pymongo import MongoClient
try:
    settings = __import__('settings')
except ImportError:
    print 'Error import module "settings", see settings.py.template'
    sys.exit(1)

DB_URL = getattr(settings, 'DB_TEST_URL', {})
DIR_SIZE_LIMIT =  250*1024*1024

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_path(dir_idx):
    while True:
        if dir_idx:
            img_dir = 'imgs%02d/'%dir_idx
        else:
            img_dir = 'imgs'
        if os.path.exists(img_dir):
            sz = get_size(img_dir)
            print sz, img_dir
            if sz > DIR_SIZE_LIMIT:
                dir_idx += 1
                continue
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        break
    return (img_dir, dir_idx)


if __name__=='__main__':
    #https://raw.githubusercontent.com/derand/DatePickerKeyboard/master/screenshot.png
    #https://github.com/derand/kanojo_activity/raw/master/imgs/screenshot.png

    #translate = {}
    #json.dump(translate, file('translate.json', 'w'))
    #translate = json.load(file('translate.json'))
    #print translate

    db_name = DB_URL.split('/')[-1]
    db = MongoClient(DB_URL)[db_name]
    db_translate = db.translate

    '''
    print len(translate)
    i = 0
    for key, value in translate.iteritems():
        el = {
            'url': key,
            'path': value
        }
        db_translate.insert(el)
        print '\r%d'%i,
        sys.stdout.flush()
        i += 1

    exit()
    '''

    dir_idx = 17
    (img_dir, dir_idx) = get_path(dir_idx)
    print img_dir
    files = glob.glob('./old/2*.md')
    files.sort()
    for fn in files:
        fo = open(fn[6:], 'w')
        if fn < './old/2014_05_20.md:':
            fo.write('![img](http://gdrive-cdn.herokuapp.com/537b65a5bc09f0000721dda7/512px-barcode.png)\n\n')
            #print '*',

        with open(fn, 'r') as fi:
            for line in fi:
                i = 0
                line = line.decode('utf-8')
                while line.find('[![img](', i) > -1:
                    x = line.find('[![img](', i) + 8
                    i = line.find(')', x)
                    url = line[x:i]
                    print url,
                    sys.stdout.flush()
                    db_rec = db_translate.find_one({ 'url': url })
                    #if not translate.has_key(url):
                    if not db_rec:
                        data = None
                        try:
                            response = urllib2.urlopen(url, timeout=30)
                            data = response.read()
                        except urllib2.HTTPError, e:
                            print e.code,
                        except urllib2.URLError, e:
                            print e.args,
                        except socket.error, e:
                            print 'socker error',
                        except httplib.BadStatusLine, e:
                            print 'BadStatusLine: \"%s\"'%e.line,
                        if data:
                            tmp_fn = url.split('/')[-1]
                            ext = tmp_fn[tmp_fn.rfind('.'):]
                            if len(ext.strip()) < 2:
                                ext = '.png'
                            md5 = hashlib.md5(data).hexdigest()
                            if len(md5) < 5:
                                print 'Error getting md5 of received data.', len(data)
                                #exit()
                            tmp_fn = None
                            j = 4
                            while j < len(md5):
                                tmp_fn = img_dir + md5[:j] + ext
                                if os.path.isfile(tmp_fn):
                                    if hashlib.md5(open(tmp_fn, 'rb').read()).hexdigest() == md5:
                                        break
                                    else:
                                        j += 1
                                else:
                                    with open(tmp_fn, 'wb') as f:
                                        f.write(data)
                                    break
                            data = tmp_fn
                        db_rec = {
                            'url': url,
                        }
                        if data:
                            db_rec['path'] = data
                        db_translate.insert(db_rec)
                        #translate[url] = data
                        #json.dump(translate, file('translate.json', 'w'))
                        #time.sleep(0.3)
                    #if translate[url]:
                    if db_rec:
                        #print ' => ', translate[url]
                        #line = line.replace(url, 'https://github.com/derand/kanojo_activity/raw/master/'+translate[url])
                        if db_rec.get('path'):
                            print ' => ', db_rec.get('path'),
                            line = line.replace(url, 'https://github.com/derand/kanojo_activity/raw/master/'+db_rec.get('path'))
                        else:
                            print 'No data',
                    print
                fo.write(line.encode('utf-8'))
        fo.close()
        os.remove(fn)

        (img_dir, dir_idx) = get_path(dir_idx)
        print img_dir

