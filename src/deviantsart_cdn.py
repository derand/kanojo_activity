#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
import os
import json
import urllib2



class UploadToDeviantsart(object):
	def __init__(self):
		super(UploadToDeviantsart, self).__init__()

	def upload(self, file_path_or_url):
		if os.path.isfile(file_path_or_url):
			return False
			#curl.setopt(pycurl.HTTPPOST, [('fileupload', (pycurl.FORM_FILE, file_path_or_url)), ('format', 'xml'), ('key', self.key)])
		elif 'http' == file_path_or_url[:4]:
			boundary = "----------------------------25bebba7cefe"
			disposition = 'Content-Disposition: form-data; name="%s"'
			form_dict = {
				'file': urllib2.urlopen(file_path_or_url).read(),
				#'s': 'Upload'
			}
			try:
				conn = urllib2.urlopen(file_path_or_url)
			except urllib2.HTTPError:
				return False
			lines = []
			lines.append('--' + boundary)
			lines.append('Content-Disposition: form-data; name="file"; filename="test"')
			lines.append('Content-Type: %s' % conn.info().getheader('Content-Type'))
			lines.append('')
			lines.append(conn.read())
			#for k, v in form_dict.iteritems():
			#	lines.append('--' + boundary)
			#	lines.append(disposition % k)
			#	lines.append('')
			#	lines.append(v)
			lines.append("--" + boundary + "--")
			lines.append('')
			multipart = "\r\n".join(lines)

			req = urllib2.Request('http://deviantsart.com')
			req.add_header("Content-Type", "multipart/form-data; boundary=%s"%boundary)
			try:
				conn = urllib2.urlopen(req, multipart)
			except urllib2.HTTPError:
				return False
			r = conn.read()
			try:
				rv = json.load(r)
			except:
				return False
			return rv.get('url', False)
		return False

if __name__=='__main__':
	sti = UploadToDeviantsart()
	output = sti.upload(argv[1])
	print output
