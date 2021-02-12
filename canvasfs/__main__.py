#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser
import traceback

import pyfuse3
import trio

from .canvas_fs import CanvasFs
from .utilities import Context

try: import faulthandler
except ImportError: pass
else: faulthandler.enable()

log = logging.getLogger(__name__)

def init_logging(debug=False):
	formatter = logging.Formatter(
		'%(asctime)s.%(msecs)03d %(threadName)s: '
		'[%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
	)
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
	parser = ArgumentParser(allow_abbrev=False)

	parser.add_argument('context_id', type=int, help='the ID of the context to be mounted')
	parser.add_argument('mountpoint', type=str, help='path to mount the FS at')

	parser.add_argument('-c', '--context', choices=['course', 'user', 'group'], default='course', help='canvas context type')
	parser.add_argument('--debug', action='store_true', default=False, help='enable debugging output')
	parser.add_argument('--debug-fuse', action='store_true', default=False, help='enable FUSE debugging output')

	return parser.parse_args()

options = parse_args()
init_logging(options.debug)

context = Context(options.context + 's')

canvas_fs = CanvasFs(options.context_id, context)
fuse_options = set(pyfuse3.default_options)
fuse_options.add('fsname=canvasfs')

if options.debug_fuse:
	fuse_options.add('debug')

pyfuse3.init(canvas_fs, options.mountpoint, fuse_options)

try:
	trio.run(pyfuse3.main)
except KeyboardInterrupt:
	pyfuse3.close()
except:
	traceback.print_exc()
	pyfuse3.close()
	exit(1)
