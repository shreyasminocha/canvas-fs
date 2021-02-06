#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
hello.py - Example file system for pyfuse3.

This program presents a static file system containing a single file.

Copyright © 2015 Nikolaus Rath <Nikolaus.org>
Copyright © 2015 Gerion Entrup.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import sys

# If we are running from the pyfuse3 source directory, try
# to load the module from there first.
basedir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
if (os.path.exists(os.path.join(basedir, 'setup.py')) and
	os.path.exists(os.path.join(basedir, 'src', 'pyfuse3.pyx'))):
	sys.path.insert(0, os.path.join(basedir, 'src'))

from argparse import ArgumentParser
import stat
import logging
import errno
import pyfuse3
import trio

from canvas_files import CanvasCourseFiles, Item

try:
	import faulthandler
except ImportError:
	pass
else:
	faulthandler.enable()

log = logging.getLogger(__name__)

class TestFs(pyfuse3.Operations):
	def __init__(self, course_id):
		super(TestFs, self).__init__()
		self.course = CanvasCourseFiles(course_id)

		self.hello_name = b"message"
		self.hello_inode = 2
		self.hello_data = b"hello world\n"

	async def getattr(self, inode, ctx=None):
		entry = pyfuse3.EntryAttributes()
		if inode == pyfuse3.ROOT_INODE:
			entry.st_mode = (stat.S_IFDIR | 0o755)
			entry.st_size = 0
		else:
			item_type, item = self.course.get_item(inode)

			if item_type == Item.FOLDER:
				entry.st_mode = (stat.S_IFDIR | 0o755)
				entry.st_size = 0
			elif item_type == Item.FILE:
				entry.st_mode = (stat.S_IFREG | 0o644)
				entry.st_size = item['size']

		stamp = int(1438467123.985654 * 1e9)
		entry.st_atime_ns = stamp
		entry.st_ctime_ns = stamp
		entry.st_mtime_ns = stamp
		entry.st_gid = os.getgid()
		entry.st_uid = os.getuid()
		entry.st_ino = inode

		return entry

	async def lookup(self, parent_inode, name, ctx=None):
		if parent_inode != pyfuse3.ROOT_INODE or name != self.hello_name:
			raise pyfuse3.FUSEError(errno.ENOENT)

		return self.getattr(self.hello_inode)

	async def opendir(self, inode, ctx):
		if inode != pyfuse3.ROOT_INODE:
			raise pyfuse3.FUSEError(errno.ENOENT)

		return inode

	async def readdir(self, fh, start_id, token):
		if fh == pyfuse3.ROOT_INODE:
			fh = 'root'

		ls = self.course.ls(fh)

		for i in range(start_id, len(ls)):
			item = ls[i]

			if 'name' in item:
				name = item['name']
			else:
				name = item['filename']

			pyfuse3.readdir_reply(token, bytes(name, 'utf-8'), await self.getattr(item['id']), i + 1)

		return

	async def open(self, inode, flags, ctx):
		if inode != self.hello_inode:
			raise pyfuse3.FUSEError(errno.ENOENT)
		if flags & os.O_RDWR or flags & os.O_WRONLY:
			raise pyfuse3.FUSEError(errno.EACCES)

		return pyfuse3.FileInfo(fh=inode)

	async def read(self, fh, off, size):
		assert fh == self.hello_inode
		return self.hello_data[off:off+size]

def init_logging(debug=False):
	formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
								  '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	root_logger = logging.getLogger()
	if debug:
		handler.setLevel(logging.DEBUG)
		root_logger.setLevel(logging.DEBUG)
	else:
		handler.setLevel(logging.INFO)
		root_logger.setLevel(logging.INFO)
	root_logger.addHandler(handler)

def parse_args():
	'''Parse command line'''

	parser = ArgumentParser()

	parser.add_argument('mountpoint', type=str,
						help='Where to mount the file system')
	parser.add_argument('--debug', action='store_true', default=False,
						help='Enable debugging output')
	parser.add_argument('--debug-fuse', action='store_true', default=False,
						help='Enable FUSE debugging output')
	return parser.parse_args()


def main():
	options = parse_args()
	init_logging(options.debug)

	testfs = TestFs(34541)
	fuse_options = set(pyfuse3.default_options)
	fuse_options.add('fsname=hello')
	if options.debug_fuse:
		fuse_options.add('debug')
	pyfuse3.init(testfs, options.mountpoint, fuse_options)
	try:
		trio.run(pyfuse3.main)
	except:
		pyfuse3.close(unmount=False)
		raise

	pyfuse3.close()


if __name__ == '__main__':
	main()
