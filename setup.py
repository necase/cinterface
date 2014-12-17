#!/usr/bin/env python
# File encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import

# install_requires argument requires setuptools rather than distutils
try:
	from setuptools import setup
	from setuptools.command.install import install
	from setuptools.command.sdist import sdist
	install_data = object
except ImportError:
	from distutils.core import setup
	from distutils.command.install import install
	from distutils.command.sdist import sdist
	from distutils.command.install_data import install_data

import os
import sys


def generateInttypesH():
	import ctypes
	charBits = 8
	shortBits = ctypes.sizeof(ctypes.c_short) * 8
	intBits = ctypes.sizeof(ctypes.c_int) * 8
	longBits = ctypes.sizeof(ctypes.c_long) * 8
	longlongBits = ctypes.sizeof(ctypes.c_longlong) * 8
	l = []
	l.extend(['#ifndef _INTTYPES_H_', os.linesep, '#define _INTTYPES_H_', os.linesep, '#include <stdint.h>', os.linesep] )
	bitLengths = {charBits: 'hh', longlongBits:'ll', shortBits:'h', longBits:'l', intBits:''}
	# length specifiers are hh:char, h: short, l:long, ll:long long,
	#  j:intmax_t, z:size_t, t:ptrdiff_t
	lookup = {
			'MAX': 'j',
			'PTR' : 't',
			}
	for length in bitLengths:
		if 0 < length <= 64 and length % 8 == 0:
			lookup[length] = bitLengths[length]
			lookup['least' + str(length)] = bitLengths[length]
			lookup['fast' + str(length)] = bitLengths[length]
	
	bitLengthsItems = bitLengths.items()
	bitLengthsItems.sort()
	for length in bitLengthsItems:
		if length > 8 and 'least8' not in lookup:
			lookup['least8'] = bitLengths[length]
			lookup['fast8'] = bitLengths[length]
		if length > 16 and 'least16' not in lookup:
			lookup['least16'] = bitLengths[length]
			lookup['fast16'] = bitLengths[length]
		if length > 32 and 'least32' not in lookup:
			lookup['least32'] = bitLengths[length]
			lookup['fast32'] = bitLengths[length]
		if length > 64 and 'least64' not in lookup:
			lookup['least64'] = bitLengths[length]
			lookup['fast64'] = bitLengths[length]

	for N in [8, 16, 32, 64, 'MAX', 'PTR']:
		for x in ['d', 'i', 'o', 'u', 'x']:
			for func in ['PRI', 'SCN']:
				l.extend(['#define ', func, x, str(N), ' ', '"', lookup[N], x, '"', os.linesep] )
				if not isinstance(N, str):
					l.extend(['#define ', func, x, 'LEAST', str(N), ' ', '"', lookup[N], x, '"', os.linesep] )
					l.extend(['#define ', func, x, 'FAST', str(N), ' ', '"', lookup[N], x, '"', os.linesep] )
	
	l.extend([
			# defining wchar, if necessary; copied from wchar.h
			'#ifndef __CPP_WCHAR_DEFINED\n\t#if __CPP_INT_BITS == __CPP_WCHAR_BITS\n\t\ttypedef unsigned int wchar_t;\n\t#elif __CPP_LONG_BITS == __CPP_WCHAR_BITS\n\t\ttypedef unsigned long wchar_t;\n\t#elif __CPP_LONGLONG_BITS == __CPP_WCHAR_BITS\n\t\ttypedef unsigned long long wchar_t;\n\t#elif __CPP_WCHAR_BITS >= 0\n\t\t#error Unsupported size for wchar_t\n\t#endif\n\t#define __CPP_WCHAR_DEFINED\n#endif\n'
			'typedef struct { intmax_t quot; intmax_t rem; } imaxdiv_t;', os.linesep,
			'intmax_t imaxabs(intmax_t);', os.linesep,
			'imaxdiv_t imaxdiv(intmax_t, intmax_t);', os.linesep,
			'intmax_t strtoimax(const char * restrict nptr, char ** restrict endptr, int base);', os.linesep,
			'uintmax_t strtoumax(const char * restrict nptr, char ** restrict endptr, int base);', os.linesep,
			'intmax_t wcstoimax(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);', os.linesep,
			'uintmax_t wcstoumax(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);', os.linesep
			])
	l.extend(['#endif', os.linesep])
	return ''.join(l)


def generateErrnoH():
	import errno
	l = []
	l.extend(['#ifndef _ERRNO_H_', os.linesep, '#define _ERRNO_H_', os.linesep])
	l.extend(['int errno;', os.linesep])
	errorKeys = errno.errorcode.keys()
	for num in errorKeys:
		l.extend(['#define ', errno.errorcode[num], ' ', str(num), os.linesep ] )
	
	l.extend(['#endif', os.linesep])
	return ''.join(l)



# Use 'python setup.py regenerate' to regenerate the inttypes.h and errno.h files
if sys.argv[1:2] == ['regenerate']:
	def localGenerateFiles():
		class self(object): pass
		self.install_dir = os.curdir
		s = generateInttypesH()
		# Hard code the include path name here to clarify destination
		with open(os.path.join(self.install_dir, 'cinterface', 'include', 'inttypes.h' ), 'w') as f:
			f.write(s)
		
		t = generateErrnoH()
		with open(os.path.join(self.install_dir, 'cinterface', 'include', 'errno.h' ), 'w') as f:
			f.write(t)
			
	localGenerateFiles()
	sys.exit(0)


class custom_install_data(install_data):
	def run(self):
		cmd = self.get_finalized_command('install')
		self.install_dir = getattr(cmd, 'install_lib')
		return install_data.run(self)

class custom_sdist(sdist):
	def make_distribution(self):
		# This prevents installing the SOURCES file from the egg-info directory into the sdist
		try:
			if 'egg-info' in self.filelist.files[-1]:
				self.filelist.files.pop()
		except:
			print('WARNING: egg-info directory may exist in output')
		sdist.make_distribution(self)


class custom_install(install):
	def run(self):
		install.run(self)
		install_dir = self.install_lib
		initial_dir = os.getcwd()
		initial_path = sys.path
		# Remove the source directory from the path
		sys.path[0] = ''
		os.chdir(install_dir)
		import cinterface
		import cinterface.transform
		cinterface.CInterfaceParser = cinterface.transform.CInterfaceParser
		# Instantiate class once to write the yacc table,
		# and once to compile the file. Do it at install time
		# to enure the program has permission to write the files.
		parser = cinterface.CInterfaceParser()
		parser = cinterface.CInterfaceParser()
		os.chdir(initial_dir)
		sys.path = initial_path
		s = generateInttypesH()
		# Hard code the include path name here to clarify destination
		with open(os.path.join(self.install_lib, 'cinterface', 'include', 'inttypes.h' ), 'w') as f:
			f.write(s)
		
		t = generateErrnoH()
		with open(os.path.join(self.install_lib, 'cinterface', 'include', 'errno.h' ), 'w') as f:
			f.write(t)


import inspect
assert(os.path.abspath(os.getcwd() ) == os.path.dirname(os.path.abspath(inspect.getsourcefile(custom_install) ) ) ), 'The current directory must be the package root directory'

import shutil
shutil.rmtree('cinterface.egg-info', ignore_errors=True)
for filename in [['yacctab.py'], ['yacctab.pyc'], ['include', 'inttypes.h'], ['include', 'errno.h'] ]:
	try:
		os.remove(os.path.join('cinterface', *filename) )
	except OSError:
		pass

# test with python setup.py install --prefix=$HOME/usr/local/python_test
# clean up with python setup.py clean --all
# then uninstall with rm -r $HOME/usr/local/python_test
setup(
	name = 'cinterface',
	version = '0.0.1',
	description = 'Simple to use interfacing with C libraries',
	url = 'https://github.com/necase/cinterface',
	author = 'Nic Case',
	license = 'BSD',
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Libraries :: Python Modules',
		],
	keywords = 'ctypes python c interface',
	install_requires = ['pycparser'],
	packages = ['cinterface'],
	cmdclass = {'install': custom_install, 'sdist': custom_sdist, 'install_data': custom_install_data},
	long_description = '''This package enables using a C library by specifying only the
header name and the library file name.''',
	package_data = {'cinterface':[os.path.join('include', '*.h')]},
)
