#!/usr/bin/env python
# File encoding: utf-8
'''Simple to use interfacing with C libraries

This package enables using a C library by specifying only the
header name and the library file name.  To see warnings from this
module, configure a log via the logging module (for example, by
calling basicConfig).
'''
from __future__ import absolute_import


def check_reload(packageName):
	import sys, imp
	# Enable reloading for each submodule imported from.
	# The module will exist as packageName.moduleName if a
	# reload call is being processed.
	submodules = [key for key in sys.modules.keys() if key.startswith(packageName + '.') ]
	for module in submodules:
		try:
			imp.reload(sys.modules[module])
		except AttributeError:
			reload(sys.modules[module])

check_reload('cinterface')

# Delete unneccessary names from the namespace
del absolute_import, check_reload

__all__ = ['include', 'close', 'save', 'load', 'CFunctionPointer', 'calculate', 'pointer', 'getType', 'LoadLibrary', 'cast']

from .transform import include, close, save, load, CFunctionPointer, calculate, pointer, getType, LoadLibrary, cast
