#!/usr/bin/env python
# File encoding: utf-8
'''Simple to use interfacing with C libraries

This module enables using a C library by specifying only the
header name and the library file name.  To see warnings from this
module, configure a log via the logging module (for example, by
calling basicConfig).
'''
from __future__ import absolute_import
from __future__ import with_statement

import ctypes
import ctypes.util
import logging
import os
import operator
import pycparser
# pycparser (https://github.com/eliben/pycparser)
# is not in the standard library
import re
import sys
# Certain functions in this module depend on the pickle or cpp modules,
# and are imported within those functions

# Define some aliases to ease compatibility between python 2 and 3
try:
	import builtins
	basestringTypes = (str, bytes, bytearray)
	long = int
	b = lambda x: x if isinstance(x, bytes) else bytes(x, 'utf8')
except ImportError:
	b = lambda x: str(x)
	basestringTypes = (basestring,)

# Follows symlinks to find the directory of this module
import inspect
_moduleDirectory = os.path.dirname(os.path.realpath(inspect.getsourcefile(b) ) )


def initFromStr(self, p, tipo):
	'''Enable the ctypes base class __init__ methods to initialize
	objects from strings'''
	if isinstance(p, basestringTypes):
		p = tipo(p)
	super(type(self), self).__init__(p)

def initFromNum(self, p, tipo):
	'''Enable the ctypes base class __init__ methods to initialize
	objects from numbers or strings'''
	if isinstance(p, (int, long) ):
		p = tipo(p)
	initFromStr(self, p, b)

ctypes.c_char.__init__ = lambda x,y=0: initFromNum(x,y, chr)

ctypes.c_byte.__init__ = lambda x,y=0: initFromStr(x,y, ord)
ctypes.c_ubyte.__init__ = lambda x,y=0: initFromStr(x,y, ord)
ctypes.c_short.__init__ = lambda x,y=0: initFromStr(x,y, int)
ctypes.c_ushort.__init__ = lambda x,y=0: initFromStr(x,y, int)
ctypes.c_int.__init__ = lambda x,y=0: initFromStr(x,y, int)
ctypes.c_uint.__init__ = lambda x,y=0: initFromStr(x,y, int)
ctypes.c_long.__init__ = lambda x,y=0: initFromStr(x,y, long)
ctypes.c_ulong.__init__ = lambda x,y=0: initFromStr(x,y, long)
ctypes.c_longlong.__init__ = lambda x,y=0: initFromStr(x,y, long)
ctypes.c_ulonglong.__init__ = lambda x,y=0: initFromStr(x,y, long)
ctypes.c_float.__init__ = lambda x,y=0: initFromStr(x,y, float)
ctypes.c_double.__init__ = lambda x,y=0: initFromStr(x,y, float)
ctypes.c_char_p.__init__ = lambda x,y=0: initFromStr(x,y, b)


ctypeMap = {
	'char': ctypes.c_char, 'signed char': ctypes.c_byte, 'unsigned char': ctypes.c_ubyte, 
	'short': ctypes.c_short, 'signed short': ctypes.c_short, 'unsigned short': ctypes.c_ushort, 
	'': ctypes.c_int, 'signed': ctypes.c_int, 'unsigned': ctypes.c_uint,
	'long': ctypes.c_long, 'signed long': ctypes.c_long, 'unsigned long': ctypes.c_ulong,
	'long long': ctypes.c_longlong, 'signed long long': ctypes.c_longlong, 'unsigned long long': ctypes.c_ulonglong,
	'float': ctypes.c_float, 
	'double': ctypes.c_double,
	'void': None,
}


try:
	ctypes.c_longdouble.__init__ = lambda x,y=0: initFromStr(x,y, float)
	ctypes.c_bool.__init__ = lambda x,y=0: initFromStr(x,y, bool)
	ctypeMap.update([('long double', ctypes.c_longdouble)], _Bool = ctypes.c_bool)
except AttributeError:
	# The _Bool and long double types were available beginning with Python 2.6
	pass


# Operators used when calculating a value, as in the size of an array
COperators = {
		'+':  operator.add, '-':  operator.sub,
		'*':  operator.mul, '/':  operator.floordiv, '%':  operator.mod,
		'sizeof': lambda x: ctypes.sizeof(x), '<<': operator.lshift,
		# logical operators were added to enable ternary operation parsing
		'>>': operator.rshift, '==':operator.eq, '!=':operator.ne,
		'>=': operator.ge, '<=': operator.le, '>': operator.gt,
		'<': operator.lt, '~': operator.inv, '^': operator.xor,
}


def calculate(s):
	'''Calculate a numeric value of the given string, which should be an
	equation using only the addition, subtraction, multiplication, division,
	and modulo operators.'''
	if isinstance(s, basestringTypes):
		try:
			from . import cpp
		except ImportError:
			import cpp
		return cpp.calculateValue(s)
	else:
		return s


def pointer(instance):
	'''Return a pointer to the given object.  If the object is
	a type, returns a pointer to the given type.'''
	if isinstance(instance, type):
		return ctypes.POINTER(instance)
	else:
		return ctypes.pointer(instance)


def cast(instance, pointerType):
	'''Cast a pointer to an instance of one type to another type of pointer'''
	return ctypes.cast(instance, pointerType)


def specifiedArgTypes(string):
	'''Returns a list of types that are asked for by the first specifier given in the string'''
	# This regular expression tests for the various parts of a
	# valid specifier without regarding how they are combined
	# The parts are: flags, width, precision, length, specifier
	# All but the specifier are optional
	m = re.match(
			r'%([-+ #0])?([1-9][0-9]*|\*)?(\.[0-9]*|\.\*)?'
			+ r'(hh|h|ll|l|j|z|t|L)?'
			+ r'(d|i|u|o|x|X|f|F|e|E|g|G|a|A|c|s|p|n)',
			string )
	argTypes = []
	if not m:
		return argTypes
	if m.group(2) == '*':
		argTypes.append(ctypes.c_int)
	if m.group(3) == '.*':
		argTypes.append(ctypes.c_int)
	spec = m.group(5)
	if m.group(4) == None:
		if spec in 'di':
			argTypes.append(ctypes.c_int)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_uint)
		elif spec in 'fFeEgGaA':
			argTypes.append(ctypes.c_double)
		elif spec =='c':
			argTypes.append(ctypes.c_char)
		elif spec =='s':
			argTypes.append(ctypes.c_char_p)
		elif spec =='p':
			argTypes.append(ctypes.c_void_p)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_int))
	elif m.group(4) == 'hh':
		if spec in 'di':
			argTypes.append(ctypes.c_byte)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_ubyte)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_byte))
	elif m.group(4) == 'h':
		if spec in 'di':
			argTypes.append(ctypes.c_short)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_ushort)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_short))
	elif m.group(4) == 'l':
		if spec in 'di':
			argTypes.append(ctypes.c_long)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_ulong)
		elif spec in 'fFeEgGaA':
			argTypes.append(ctypes.c_double)
		elif spec =='c':
			argTypes.append(ctypes.c_wchar)
		elif spec =='s':
			argTypes.append(ctypes.c_wchar_p)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_long))
	elif m.group(4) == 'll':
		if spec in 'di':
			argTypes.append(ctypes.c_longlong)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_ulonglong)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_longlong))
	elif m.group(4) == 'j':
		if spec in 'di':
			argTypes.append(ctypes.c_longlong)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_ulonglong)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_longlong))
	elif m.group(4) == 'z':
		if spec in 'di':
			argTypes.append(ctypes.c_size_t)
		elif spec in 'uoxX':
			argTypes.append(ctypes.c_size_t)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ctypes.c_size_t))
	elif m.group(4) == 't':
		if ctypes.sizeof(ctypes.c_void_p) == 4:
			ptrdiff = ctypes.c_int32
		else:
			ptrdiff = ctypes.c_int64
		if spec in 'di':
			argTypes.append(ptrdiff)
		elif spec in 'uoxX':
			argTypes.append(ptrdiff)
		elif spec =='n':
			argTypes.append(ctypes.POINTER(ptrdiff))
	elif m.group(4) == 'L':
		if spec in 'fFeEgGaA':
			argTypes.append(ctypes.c_longdouble)
	else:
		# This line should never execute unless the regular expression has been incorrectly changed
		raise ValueError ('Invalid length or length not supported: %s' % m.group(4) )
	return argTypes


def transformArgsf(func, *args):
	'''Transform function arguments for printf-like functions
	from python callers into ctypes-compatible arguments
	'''
	fixedArgs = transformArgs(func, *args)
	try:
		n = len(fixedArgs)
		formatstr = fixedArgs[-1].value
		## May wish to change everything to bytes instead of changing this to str
		if hasattr(formatstr, 'find'):
			formatstr = str(formatstr)
		ndx = formatstr.find('%')
		optionalArgs = []
		while ndx != -1:
			for argType in specifiedArgTypes(formatstr[ndx:] ):
				if hasattr(argType, 'contents') or issubclass(argType, ctypes.c_void_p):
					transformedArg = ctypes.cast(args[n], argType)
				else:
					transformedArg = argType(args[n])
				optionalArgs.append(transformedArg)
				n += 1
			try:
				if formatstr[1+ndx] == '%':
					ndx += 1
			except IndexError:
				break
			ndx = formatstr.find('%', 1+ndx)
		fixedArgs.extend(optionalArgs)
		func.argtypes = [type(a) for a in fixedArgs]
	except:
		# Callers must be more careful with variable argument lists because
		# there is no general way to check the argument types
		log.info('Variable argument list not compatible with printf; '
				+ 'Argument types will not be verified by the interface.')
		for arg in args[len(fixedArgs):]:
			# This should largely match the argument handling in transformArgs
			# around line 320.  It would be preferable to refactor this into
			# a separate function to be called both here and in transformArgs.
			if arg == None:
				fixedArgs.append(arg)
			elif isinstance(arg, basestringTypes):
				fixedArgs.append(ctypes.c_char_p(arg))
			elif isinstance(arg, list):
				transformedArg = arg
				extraPointers = 0
				while isinstance(transformedArg, list):
					if len(transformedArg) > 1:
						raise ValueError('Lists representing pointers must not have multiple elements.')
					transformedArg = transformedArg[0]
					extraPointers += 1
				while extraPointers > 0:
					if isinstance(transformedArg, type):
						# Null pointer
						transformedArg = ctypes.POINTER(transformedArg)()
						# Alter the list item so the caller can use the transformed argument
						arg[0] = transformedArg
					elif isinstance(transformedArg, basestringTypes):
						transformedArg = ctypes.c_char_p(transformedArg)
					else:
						transformedArg = ctypes.pointer(transformedArg)
					extraPointers -= 1
				if transformedArg != arg:
					# Alter the list item so the caller can use the transformed argument
					if hasattr(transformedArg, 'contents'):
						arg[0] = transformedArg.contents
					elif isinstance(transformedArg, ctypes.c_char_p):
						arg[0] = transformedArg._objects
				fixedArgs.append(transformedArg)
			elif hasattr(arg, '__module__') and arg.__module__ == 'ctypes':
				fixedArgs.append(arg)
			else:
				raise ValueError('Unknown argument type: ' + str(type(arg))
						+ ' of argument ' + len(fixedArgs) + ': ' + str(arg) )

	return fixedArgs


def transformArgs(func, *args):
	'''Transform function arguments from python objects into
	ctypes-compatible objects
	'''
	argsImage = []
	if hasattr(func, 'requiredArgs'):
		func.argtypes = func.requiredArgs
	for arg, argType in zip(args, func.argtypes):
		# This should mostly match the argument handling in transformArgsf
		# around line 270.
		if argType == type(arg) or arg == None:
			if is_ctypes_null_pointer(arg):
				arg.contents = arg._type_()
			argsImage.append(arg)
		elif isinstance(arg, basestringTypes):
			transformedArg = ctypes.c_char_p(arg)
			if argType != ctypes.c_char_p:
				transformedArg = ctypes.cast(transformedArg, argType)
			argsImage.append(transformedArg)
		elif isinstance(arg, list):
			transformedArg = arg
			extraPointers = 0
			while isinstance(transformedArg, list):
				if len(transformedArg) > 1:
					raise ValueError('Lists representing pointers must not have multiple elements.')
				transformedArg = transformedArg[0]
				extraPointers += 1
			while extraPointers > 0:
				if isinstance(transformedArg, type):
					# Null pointer
					transformedArg = ctypes.POINTER(transformedArg)()
					# Alter the list item so the caller can use the transformed argument
					arg[0] = transformedArg
				elif isinstance(transformedArg, basestringTypes) and argType == ctypes.c_char_p:
					transformedArg = ctypes.c_char_p(transformedArg)
				else:
					nextType = argType
					for nn in range(extraPointers):
						nextType = nextType._type_
					if hasattr(nextType, 'contents'):
						transformedArg = ctypes.POINTER(nextType)(transformedArg)
					else:
						transformedArg = ctypes.pointer(nextType(transformedArg))
				extraPointers -= 1
			if transformedArg != arg:
				# Alter the list item so the caller can use the transformed argument
				if hasattr(transformedArg, 'contents'):
					arg[0] = transformedArg.contents
				elif isinstance(transformedArg, ctypes.c_char_p):
					arg[0] = transformedArg._objects
			argsImage.append(transformedArg)
		else:
			# Try to coax the argument to the right type
			argsImage.append(argType(arg))
	return argsImage


def getType(s, iface=None):
	'''Returns a type object representing the type given in the string'''
	typename = []
	numlongs = s.count('long')
	signed = 'signed' if 'signed' in s else 'unsigned' if 'unsigned' in s else ''
	if signed:
		typename.append(signed)
	while numlongs > 0:
		typename.append('long')
		numlongs -= 1
	numPointers = s.count('*')
	typename.extend([item for item in s.replace('*', '').split() if item not in ['signed', 'unsigned', 'long', 'int', '_Complex'] ])
	r = translateType(' '.join(typename), iface)
	while numPointers > 0:
		if r == ctypes.c_char:
			r = ctypes.c_char_p
		else:
			r = ctypes.POINTER(r)
		numPointers -= 1
	return r


def translateType(tipo, iface = None):
	'''Translate types from strings into a ctypes object'''
	if tipo in ctypeMap:
		return ctypeMap[tipo]
	if iface:
		if tipo in iface.struct:
			return iface.struct[tipo]
		elif tipo in iface.union:
			return iface.union[tipo]
		elif tipo in iface:
			if not isinstance(tipo, object):
				raise ValueError('Type %s not supported' % str(tipo))
			return iface[tipo]
		elif tipo in iface.enum:
			return iface.enum[tipo]
	if tipo == 'long double':
		log.warning('long double is aliased to double')
		return ctypeMap['double']
	if tipo == '_Bool':
		log.warning('_Bool is aliased to unsigned char')
		return ctypeMap['unsigned char']
	return ''


class Namespace(dict):
	'''A class that exposes only the attributes explicitly added to it,
	and exposes those same attributes via a dict lookup
	'''
	def __repr__(self):
		# Enable printing useful information
		return '%s(%s)' % (type(self).__name__, dict.__repr__(self) )
	
	def __getattribute__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError("'%s' object has no attribute '%s'"
					% (type(self).__name__, key) )
	
	def __getattr__(self, key):
		# Enable readline module and dir() support
		if key == '__dict__':
			return self
		raise AttributeError("'%s' object has no attribute '%s'"
					% (type(self).__name__, key) )
	
	def __setattr__(self, key, value):
		self[key] = value
	
	def __delattr__(self, key):
		del self[key]


class CInterface(Namespace):
	'''The user-visible class representing the C interface'''
	def __init__(self, libs):
		super(CInterface, self).__init__()
		super(CInterface, self).__setitem__(':exportedVars:', Namespace() )
		self[':libraries:'] = libs
		self.struct = Namespace()
		self.union = Namespace()
		self.enum = Namespace()
	
	
	def __setattr__(self, key, value):
		if key in super(CInterface, self).__getitem__(':exportedVars:'):
			z = ctypes.pointer(self[key] )
			z[0] = value
		else:
			return super(CInterface, self).__setattr__(key, value)
	
	
	def __getitem__(self, key):
		if key in super(CInterface, self).__getitem__(':exportedVars:'):
			varInfo = self[':exportedVars:'][key]
			return varInfo[0].in_dll(varInfo[1], key)
		else:
			return super(CInterface, self).__getitem__(key)
	
	
	def __setitem__(self, key, value):
		if key in super(CInterface, self).__getitem__(':exportedVars:'):
			z = ctypes.pointer(self[key] )
			z[0] = value
		else:
			return super(CInterface, self).__setitem__(key, value)
	
	
class CFunctionPointer(object):
	'''A class to represent a C function'''
	def __init__(self):
		self.function = int
		self.argtypes = []
		self.transformArgs = lambda *x: list(x)
		self.convention = ''
	
	def __call__(self, *args):
		funcArgs = self.transformArgs(*args)
		return self.function(*funcArgs)


def defineFunction(iface, name, rtype, argTypes, convention, typeDescs):
	'''Insert a reference to the specified function into the CInterface object.
	'''
	if convention == '__stdcall':
		prototype = ctypes.WINFUNCTYPE(rtype, *argTypes)
	else:
		prototype = ctypes.CFUNCTYPE(rtype, *argTypes)
	func = CFunctionPointer()
	func.convention = convention
	func.argtypes = argTypes
	for lib in iface[':libraries:']:
		try:
			func.function = prototype((name, lib) )
			setattr(iface, name, func)
			setattr(func, 'typeDescs', typeDescs)
			if len(argTypes) > 0 and issubclass(argTypes[-1], EllipsisType):
				setattr(func, 'transformArgs', lambda *x: transformArgsf(func.function, *x) )
				setattr(func.function, 'requiredArgs', argTypes[:-1] )
			else:
				setattr(func, 'transformArgs', lambda *x: transformArgs(func.function, *x) )
			break
		except AttributeError:
			continue
	else:
		log.info("%s symbol not found" % name)


'''
Serializable representation reference:
	
-CDLL objects:
	{'type':'CDLL', 'lib':item._name}
-CFunctionPointer objects:
	{'type': 'func', 'argTypes': args, 'restype': rv, 'convention': c}
-CFUNCTYPE/WINFUNCTYPE objects (callback functions):
	{'type': 'funcpointer', 'argTypes': args, 'restype': rv, 'convention': c}
-Structure/Union classes:
	{'type':'struct', 'fields':fields, 'name': item.__name__}
	{'type':'union',  'fields':fields, 'name': item.__name__}
		fields == None -> opaque struct
		element[1] in fields == None -> Pointer to same class
-Structure/Union objects:
	{'type':'struct', 'fields':f, 'name': name, 'values':v}
	{'type':'union',  'fields':f, 'name': name, 'values':v}
-Array classes:
	{'type':'array', 'class':t, 'length':item._length_}
-Array objects:
	{'type':'array', 'class':r, 'length':item._length_, 'values':v}
-Pointers as classes:
	{'type': 'pointer', 'name':name, 'class':encodeItem(type(item))}
-Pointers to objects:
	{'type': 'pointer', 'name':name, 'class':encodeItem(type(item)), 'object':obj}
		obj == None -> null pointer
-ctypes standard objects:
	{'type':'ctypes', 'class':item.__class__, 'value': v}
		v == None -> null pointer

All other objects are saved directly
'''


def save(interface, filename):
	'''Export the C interface to a file'''
	try:
		import cPickle as pickle
	except ImportError:
		import pickle
	r = encode(interface)
	o = {'version':0, 'object':r}
	with open(filename, 'wb') as f:
		pickle.dump(o, f, 2)


def encode(interface):
	'''Encodes a CInterface instance by translating unpicklable objects to
	dicts with the necessary information to reconstruct them'''
	t = {}
	for item in interface:
		if isinstance(interface[item], dict):
			v = {}
			for key in interface[item]:
				r = encodeItem(interface[item][key], interface, key)
				v[key] = r
			t[item] = v
		elif isinstance(interface[item], list):
			l = []
			for element in interface[item]:
				r = encodeItem(element, interface)
				l.append(r)
			t[item] = l
		else:
			r = encodeItem(interface[item], interface, item )
			t[item] = r
	return t


def isCtypesFunc(item):
	if hasattr(item, 'argtypes') and hasattr(item, '__module__') and item.__module__ == 'ctypes':
		return True
	return False


def is_array(item):
	if hasattr(item, '_length_') and hasattr(item, '_type_'):
		return True
	return False


def encodeRef(item, interface, name=None, parents=None):
	pointers = 0
	while is_pointer(item):
		if not isinstance(item, ctypes.c_char_p):
			item = item._type_
		pointers += 1
	if name in interface and isinstance(item, type):
		if is_array(item):
			return None
		t = interface[name]
		while is_pointer(t):
			t = t._type_
			pointers -= 1
		r = {'type':'ref', 'name':name, 'pointers':pointers}
		return r
	else:
		return None


def encodeItem(item, interface=None, name=None, parents=None):
	'''Encodes a single element of the CInterface object to a picklable object'''
	# Possible input classes are: str, CFunctionPointer, any ctypes type, 
	# builtin numeric types
	# Special ctypes types: Structure/Union, CDLL/windll, Arrays, Pointers
	r = item
	if parents == None:
		parents = set()
	if isinstance(item, basestringTypes + (long, int, float) ):
		# This function should return the argument: this is the only early return
		return r
	if isinstance(item, ctypes.CDLL):
		# lib is the file name to pass to LoadLibrary
		r = {'type':'CDLL', 'lib':item._name}
	elif isinstance(item, tuple):
		acc = []
		for element in item:
			v = encodeItem(element, interface, name, parents)
			acc.append(v)
		r = tuple(acc)
	elif isinstance(item, CFunctionPointer) or isCtypesFunc(item):
		# Might not work properly for printf-like functions
		args = []
		if isCtypesFunc(item):
			if isinstance(item, type):
				f = item()
				item.argtypes = f.argtypes
				item.function = f
			else:
				raise ValueError('Unexpected error encountered')  ## This is probably only reachable if there is a bug somewhere else
				item.function = item
			item.typeDescs = [''] * (len(item.argtypes) + 1)
			## Another place where setting the convention may be necessary
			item.convention = '__cdecl'
		for element, desc in list(zip(item.argtypes, item.typeDescs[1:] ) ):
			a = encodeRef(element, interface, desc, parents)
			if not a:
				a = encodeItem(element, interface, name, parents)
			args.append(a)
		rv = encodeRef(item.function.restype, interface, item.typeDescs[0], parents)
		if not rv:
			rv = encodeItem(item.function.restype, interface, name, parents)
		# argTypes and restype are the arguments to defineFunction
		r = {'type': 'func', 'argTypes': args, 'restype': rv, 'convention':item.convention, 'typeDescs':item.typeDescs}
		if isCtypesFunc(item):
			if isinstance(item, type):
				r['type'] = 'funcpointertype'
			else:
				r['type'] = 'funcpointer'
	elif isinstance(item, type) and issubclass(item, (ctypes.Structure, ctypes.Union) ):
		typeDescs = []
		if hasattr(item, '_fields_') and item.__name__ not in parents:
			parents.add(item.__name__)
			fields = []
			for element, typeDesc in list(zip(item._fields_, item.typeDescs) ):
				fieldref = encodeRef(element[1], interface, typeDesc, parents)
				if fieldref:
					if len(element) > 2:
						fields.append((element[0], fieldref, element[2]) )
					else:
						fields.append((element[0], fieldref) )
					continue
				if (not (hasattr(element[1], '_type_') and item == element[1]._type_)) and element[1].__name__ not in parents:
					r = encodeItem(element[1], interface, element[0], parents )
				elif element[1].__name__ in parents:	
					# Pointer to same object type, possible forward-declaration
					r = [] # Recursive declaration
				else:
					r = None
				if len(element) > 2:
					fields.append((element[0], r, element[2] ) )
				else:
					fields.append((element[0], r ) )
			typeDescs = item.typeDescs
			parents.discard(item.__name__)
		elif item.__name__ in parents:
			fields = [] # Recursive declaration
		else:
			fields = None
		t = 'struct'
		if issubclass(item, ctypes.Union):
			t = 'union'
		## Using item.__name__ can change unicode names to str in Python2
		r = {'type':t, 'fields':fields, 'name': item.__name__, 'typeDescs':typeDescs}
	elif isinstance(item, type) and issubclass(item, ctypes.Array):
		t = encodeItem(item._type_, interface, name, parents)
		r = {'type':'array', 'class':t, 'length':item._length_}
	elif isinstance(item, type) and hasattr(item, 'contents'):
		# Pointer to something
		v = encodeItem(item._type_, interface, name, parents)
		r = {'type':'pointer', 'class':v, 'name': name}
	
	return r


def is_ctypes_null_pointer(instance):
	try:
		getattr(instance, 'contents')
	except AttributeError:
		return False
	except ValueError:
		# Null pointers throw a ValueError when accessing the contents
		# attribute, but we use this function to determine whether the
		# instance is a null pointer , so we want to return True
		# for null pointers
		return True
	return False


def is_pointer(instance):
	'''A replacement for the hasattr function for ctypes types that
	returns a True result for ctypes-based null pointers
	'''
	try:
		getattr(instance, 'contents')
		if isinstance(instance, type) and issubclass(instance, ctypes.Structure):
			return False
	except AttributeError:
		## c_char_p objects have no contents attribute, which may cause unexpected behavior
		if isinstance(instance, type) and issubclass(instance, (ctypes.c_char_p, ctypes.c_void_p) ):
			return True
		return False
	except ValueError:
		# Null pointers throw a ValueError when accessing the contents
		# attribute, but we use this function to determine whether the
		# instance is a pointer object/type, so we want to return True
		# for null pointers
		pass
	return True


def load(filename):
	'''Load a C interface from a file'''
	try:
		import cPickle as pickle
	except ImportError:
		import pickle
	with open(filename, 'rb') as f:
		g = pickle.load(f)
	if g['version'] > 0:
		raise ValueError('Unable to load cinterface data with version ' + str(g['version']) + ': You must upgrade the cinterface package.')
	return decode(g['object'])


def decodeItem(name, item, iface, M=None):
	'''Returns a single object to incorporate into the interface'''
	r = None
	if isinstance(item, (list, tuple) ):
		r = []
		for element in item:
			r.append(decodeItem(name, element, iface, M) )
		if isinstance(item, tuple):
			r = tuple(r)
	elif not isinstance(item, dict):
		r = item
	elif item['type'] == 'CDLL':
		for lib in iface[':libraries:']:
			if lib._name == item['lib']:
				r = lib
				break
		else:
			raise ValueError('Unknown library: %s' % item['name'])
	elif item['type'] == 'pointer':
		r = decodeItem(name, item['class'], iface, M)
		r = ctypes.POINTER(r)
		if 'object' in item:
			if item['object'] == None:
				r = r()
			else:
				r = decodeItem(name, item['object'], iface, M)
				if isinstance(r, type):
					r = ctypes.POINTER(r)()
				else:
					r = ctypes.pointer(r)
	elif item['type'] in ['struct', 'union']:
		## Should use name instead of item['name'] to keep the unicode items as unicode, but name is not always updated properly
		typlist = iface.struct
		parentClass = ctypes.Structure
		if item['type'] == 'union':
			typlist = iface.union
			parentClass = ctypes.Union
		if item['name'] in typlist and ( hasattr(typlist[item['name']], '_fields_') or not item['fields']  ):
			r = typlist[item['name']]
		else:
			if item['name'] not in typlist:
				typlist[item['name'] ] = type(item['name'], (parentClass,), {})
			fields = []
			if item['fields']:
				for f in item['fields']:
					if f[1] == None:
						z = ctypes.POINTER(typlist[item['name'] ])
					elif f[1] == []:
						z = typlist[item['name'] ]
					else:
						z = decodeItem(f[0], f[1], iface, M)
					if len(f) == 3:
						fields.append((f[0], z, f[2]) )
					else:
						fields.append((f[0], z) )
				typlist[item['name']]._fields_ = fields
				typlist[item['name']].typeDescs = item['typeDescs']
			r = typlist[item['name']]
		if 'values' in item:
			r = typlist[item['name']]()
			for element, value in list(zip(item['fields'], item['values'] )):
				setattr(r, element[0], decodeItem(element[0], value, iface, M) )
	elif item['type'] in [ 'func' , 'funcpointer', 'funcpointertype']:
		decodedArgs = []
		for argType in item['argTypes']:
			decodedArg = decodeItem(name, argType, iface, M)
			decodedArgs.append(decodedArg)
		decodedRType = decodeItem(name, item['restype'], iface, M)
		if item['type'] == 'func':
			defineFunction(iface, name, decodedRType, decodedArgs, item['convention'], item['typeDescs'])
			r = iface[name]
		else:
			r = ctypes.CFUNCTYPE(decodedRType, *decodedArgs)
			if item['type'] == 'funcpointer':
				r = r()
	elif item['type'] == 'array':
		r = item['length'] * decodeItem(name, item['class'], iface, M)
		if 'values' in item:
			v = []
			for element in item['values']:
				v.append(decodeItem(name, element, iface, M) )
			r = r(*v)
	elif item['type'] == 'ctypes':
		if item['value'] == None:
			r = item['class']
		else:
			r = item['class'](item['value'])
	elif item['type'] == 'ref':
		if hasattr(iface, item['name'] ):
			r = iface[item['name'] ]
			if item['pointers']:
				p = item['pointers']
				while p:
					r = ctypes.POINTER(r)
					p -= 1
		else:
			name = item['name']
			pointers = item['pointers']
			child = M[item['name'] ]
			if isinstance(child, dict) and 'type' in child:
				childType = child['type']
			else:
				childType = False
			if childType in ['struct', 'union'] and pointers > 0:
				parentClass = ctypes.Structure
				if item['type'] == 'union':
					parentClass = ctypes.Union
				v = type(str(child['name'] ), (parentClass,), {} )
			else:
				v = decodeItem(item['name'], M[item['name'] ], iface, M)
			iface[name] = v
			while pointers:
				v = ctypes.POINTER(v)
				pointers -= 1
			r = v
	
	return r


def decode(unit):
	'''Restores the C interface from the saved object'''
	libs = []
	libnames = []
	for item in unit[':libraries:']:
		libnames.append(item['lib'])
	for libname in libnames:
		libPath = ctypes.util.find_library(libname)
		if libPath is None:
			libPath = libname
		lib = ctypes.cdll.LoadLibrary(libPath)
		if lib is None:
			raise IOError('Library %s not found' % libPath)
		libs.append(lib)
	r = CInterface(libs)
	for item in ['struct', 'union', 'enum']:
		tipList = unit[item]
		for element in unit[item]:
			t = decodeItem(element, tipList[element], r, unit)
			r[item][element] = t
	
	for item in unit:
		if item in [':libraries:', 'struct', 'union', 'enum']:
			continue
		if item in [':exportedVars:']:
			v = Namespace()
			for key in unit[item]:
				t = decodeItem(item, unit[item][key], r, unit)
				v[key] = t
			r[item] = v
		elif isinstance(unit[item], list):
			assert False, "This cannot yet happen"
			l = []
			for element in unit[item]:
				t = decodeItem(item, element, r, unit)
				l.append(t)
			r[item] = l
		else:
			t = decodeItem(item, unit[item], r, unit)
			r[item] = t

	return r


class EllipsisType(object):
	'''The type of an ellipsis used in a function declaration'''
	@classmethod
	def from_param(self, obj):
		raise NotImplementedError('The from_param method of EllipsisType objects should never be called')


def getNodeTypeName(node):
	r = ''
	while hasattr(node, 'type'):
		if isinstance(node, pycparser.c_ast.FuncDecl):
			r += '(*function) '
		node = node.type
	if isinstance(node, pycparser.c_ast.Struct):
		r += ':struct:'
	elif isinstance(node, pycparser.c_ast.Union):
		r += ':union:'
	if isinstance(node, pycparser.c_ast.IdentifierType):
		return r + ' '.join(node.names)
	else:
		return r + node.name


class InterfaceTranslator(pycparser.c_ast.NodeVisitor):
	'''This class contains the algorithms used to convert the C source into
	Python objects.  It uses the pycparser visit_* functions to convert the
	nodes as they are visited by the pycparser.parse function.
	'''
	def __init__(self, libs):
		'''The external interface is the output member.  All items not related
		to the C source file are named with colons to avoid
		conflicts with the included file.'''
		self.output = CInterface(libs)
	
	
	def visit_FuncDef(self, node):
		'''Function definitions: int main(void){ return 0;}'''
		if 'static' in node.decl.storage:
			return
		if hasattr(self.output, node.decl.name):
			if hasattr(self.output[node.decl.name], 'restype'):
				return
		self.visit(node.decl)
	
	
	def visit_FuncDecl(self, node):
		'''Function declarations: int main(void);'''
		if isinstance(node.type, pycparser.c_ast.TypeDecl):
			fname = node.type.declname
		else:
			fnode = node.type
			while(not isinstance(fnode.type, pycparser.c_ast.TypeDecl ) ):
				fnode = fnode.type
			fname = fnode.type.declname
		rtype = self.getNodeType(node.type)
		typeDescs = []
		typeDescs.append(getNodeTypeName(node.type) )
		argTypes = []
		if node.args:
			for params in (node.args.params):
				if isinstance(params, pycparser.c_ast.EllipsisParam):
					argTypes.append(EllipsisType)
					typeDescs.append('...')
					break
				if hasattr(params, 'type'):
					params = params.type
					if self.getNodeType(params):
						argTypes.append(self.getNodeType(params))
						typeDescs.append(getNodeTypeName(params))
		
		convention = '__cdecl'
		if '__stdcall' in node.funcspec:
			convention = '__stdcall'
		defineFunction(self.output, fname, rtype, argTypes, convention, typeDescs)
	
	
	def visit_Typedef(self, node):
		'''typedef declarations'''
		if isinstance(node.type.type, pycparser.c_ast.IdentifierType):
			self.output[node.name] = self.getNodeType(node.type)
		else:
			newtype = self.getNodeType(node.type)
			if newtype == '':
				self.visit(node.type)
				newtype = self.getNodeType(node.type)
			self.output[node.name] = newtype


	def visit_Struct(self, node):
		'''struct declarations'''
		if node.name not in self.output.struct:
			self.output.struct[node.name] = type(str(node.name), (ctypes.Structure,), {})
		if not node.decls:
			return
		fields = []
		typeDescs = []
		for f in node.decls:
			ftype = self.getNodeType(f)
			if not f.name:
				f.name = newAnonymousName()
			if f.bitsize:
				fields.append( (f.name, ftype, int(f.bitsize.value)) )
			else:
				fields.append( (f.name, ftype) )
			while hasattr(f, 'type'):
				f = f.type
			if isinstance(f, pycparser.c_ast.IdentifierType):
				typeDescs.append(' '.join(f.names) )
			else:
				typeDescs.append(f.name)
		self.output.struct[node.name]._fields_ = fields
		self.output.struct[node.name].typeDescs = typeDescs
	
	
	def visit_Enum(self, node):
		'''enum declarations'''
		tipo = node.name
		## Probably want this as an option exposed to the user to conform
		## to what common compilers do, like -fshort-enum in gcc
		self.output.enum[tipo] = ctypes.c_int
		offset = 0
		for count, e in enumerate(node.values.enumerators):
			if e.value:
				offset = self.calculate(e.value) - count
			setattr(self.output, e.name, count + offset)
	
	
	def visit_Union(self, node):
		'''union declarations'''
		if node.name not in self.output.union:
			self.output.union[node.name] = type(str(node.name), (ctypes.Union,), {})
		fields = []
		typeDescs = []
		for f in node.decls:
			ftype = self.getNodeType(f)
			if f.bitsize:
				fields.append( (f.name, ftype, int(f.bitsize.value)) )
			else:
				fields.append( (f.name, ftype) )
			while hasattr(f, 'type'):
				f = f.type
			if isinstance(f, pycparser.c_ast.IdentifierType):
				typeDescs.append(' '.join(f.names) )
			else:
				typeDescs.append(f.name)
		self.output.union[node.name]._fields_ = fields
		self.output.union[node.name].typeDescs = typeDescs
	
	
	def visit_Decl(self, node):
		'''Generic declarations'''
		if not 'static' in node.storage:
			tnode = node.type
			declareVar = False
			while isinstance(tnode, pycparser.c_ast.PtrDecl):
				if ((isinstance(tnode.type, pycparser.c_ast.TypeDecl) and
						isinstance(tnode.type.type, pycparser.c_ast.IdentifierType) )
						or isinstance(tnode.type, pycparser.c_ast.ArrayDecl) ):
					declareVar = True
					break
				tnode = tnode.type
			if ((isinstance(node.type, pycparser.c_ast.TypeDecl) and
					isinstance(node.type.type, (pycparser.c_ast.IdentifierType, pycparser.c_ast.Struct) ) ) 
					or isinstance(node.type, pycparser.c_ast.ArrayDecl)
					or declareVar):
				tipo = self.getNodeType(node)
				for lib in self.output[':libraries:']:
					try:
						tipo.in_dll(lib, node.name)
						break
					except ValueError:
						continue
				else:
					# If the variable is not found in any library, do not set it
					return

				self.output[':exportedVars:'][node.name] = (tipo, lib)
			else:
				tnode = node.type
				while isinstance(tnode, pycparser.c_ast.PtrDecl):
					tnode = tnode.type
				if isinstance(tnode, pycparser.c_ast.FuncDecl):
					tnode.funcspec = node.funcspec
				self.visit(node.type)
	
	
	def getNodeType(self, node):
		'''Determines the type the node refers to, and returns a type
		suitable for ctypes'''
		suffix = ''
		f = []
		tipo = None
		while 1:
			if isinstance(node, pycparser.c_ast.IdentifierType):
				typename = []
				numlongs = node.names.count('long')
				signed = 'signed' if 'signed' in node.names else 'unsigned' if 'unsigned' in node.names else ''
				if signed:
					typename.append(signed)
				while numlongs > 0:
					typename.append('long')
					numlongs -= 1
				typename.extend([item for item in node.names if item not in ['signed', 'unsigned', 'long', 'int', '_Complex'] ])
				tipo = translateType(' '.join(typename), self.output)
				if '_Complex' in node.names:
					tipo *= 2
				break
			elif isinstance(node, pycparser.c_ast.PtrDecl):
				f.insert(0, ctypes.POINTER)
				node = node.type
			elif isinstance(node, pycparser.c_ast.ArrayDecl):
				tipo = long(self.calculate(node.dim) ) * self.getNodeType(node.type)
				break
			elif isinstance(node, pycparser.c_ast.Decl):
				if 'static' in node.storage:
					# This may not be reachable with valid C
					return None
				node = node.type
			elif isinstance(node, (pycparser.c_ast.Typename, pycparser.c_ast.TypeDecl) ):
				# Don't care about qualifiers like const or volatile
				node = node.type
			elif isinstance(node, (pycparser.c_ast.Struct, pycparser.c_ast.Union, pycparser.c_ast.Enum ) ):
				if not node.name:
					# anonymous structures
					# define a new type, give it a unique name, and return that name
					node.name = newAnonymousName()
					self.visit(node)
				elif hasattr(node, 'decls') and node.decls:
					nodetype = 'struct'
					if isinstance(node, pycparser.c_ast.Union):
						nodetype = 'union'
					if node.name not in self.output[nodetype]:
						self.visit(node)
				tipo = translateType(node.name, self.output)
				break
			elif isinstance(node, pycparser.c_ast.FuncDecl):
				if f:
					# defining a callback function, discard the pointer
					f.pop()
					## This is copied from the FuncDecl visitor
					rtype = self.getNodeType(node.type)
					argTypes = []
					if node.args:
						for params in (node.args.params):
							if isinstance(params, pycparser.c_ast.EllipsisParam):
								argTypes.append(EllipsisType)
								break
							if hasattr(params, 'type'):
								params = params.type
								if self.getNodeType(params):
									argTypes.append(self.getNodeType(params))
					## Is there any way to correctly use WINFUNCTYPE here?
					tipo = ctypes.CFUNCTYPE(rtype, *argTypes)
					break
				else:
					node = node.type
			elif isinstance(node, pycparser.c_ast.ID):
				tipo = self.output[':exportedVars:'][node.name][0]
				break
			elif isinstance(node, pycparser.c_ast.Constant):
				tipo = cast_value(node.type, node.value)
				break
			else:
				# All possible types should be explicitly handled above
				raise ValueError(type(node))
			
		if f:
			if tipo == '':
				if isinstance(node, pycparser.c_ast.Struct):
					self.output.struct[node.name] = type(str(node.name), (ctypes.Structure,), {})
					tipo = self.output.struct[node.name]
				elif isinstance(node, pycparser.c_ast.Union):
					self.output.union[node.name] = type(str(node.name), (ctypes.Union,), {})
					tipo = self.output.union[node.name]
				else:
					self.output[node.name] = None
					tipo = self.output[node.name]
			if tipo == ctypes.c_char:
				r = ctypes.c_char_p
			else:
				r = f[-1](tipo)
			for func in f[-2::-1]:
				r = func(r)
		else:
			r = tipo
		return r


	def calculate(self, node):
		'''Cacluates a numeric value of the node'''
		if not node:
			return 1
		if len(node.children() ) == 2:
			left = self.calculate(node.left)
			right = self.calculate(node.right)
			f = COperators[node.op]
			return f(left, right)
		elif len(node.children() ) == 1:
			if node.op == '-':
				f = operator.neg
			elif node.op == '+':
				f = operator.pos
			else:
				f = COperators[node.op]
			try:
				arg = self.getNodeType(node.expr)
			except KeyError:
				log.warning('Variable not found when calculating node: %s\n' % node )
				arg = ctypes.c_void_p;
			return f(arg)
		elif len(node.children() ) == 3:
			if self.calculate(node.cond):
				return self.calculate(node.iftrue)
			else:
				return self.calculate(node.iffalse)
		elif isinstance(node, pycparser.c_ast.ID):
			return self.output[node.name]
		return cast_value(node.type, node.value)


def cast_value(tipo, value):
	'''Converts a string representation of a numeric type to the corresponding
	Python type'''
	if tipo == 'int':
		return int(value, 0)
	elif tipo == 'float':
		return float(value)
	else:
		raise ValueError('Invalid type: %s' % tipo)


anonNameCounter = 0
def newAnonymousName():
	global anonNameCounter
	anonNameCounter += 1
	prefix = '__include_anon'
	suffix = '__'
	return prefix + str(anonNameCounter) + suffix


import pycparser.c_lexer
cachedCLexerInit = pycparser.c_lexer.CLexer.__init__

def CInterfaceLexerInit(self, *args, **kwargs):
	cachedCLexerInit(self, *args, **kwargs)
	new_keywords = ('__STDCALL', '__CDECL')
	self.keywords += new_keywords
	for w in new_keywords:
		self.keyword_map[w.lower()] = w
	self.tokens += new_keywords


class CInterfaceParser(pycparser.CParser):
	def __init__(self, lex_optimize=True,
			lextab='pycparser.lextab',
			yacc_optimize=True,
			yacctab='yacctab',
			yacc_debug=False):
		'''Initialize the parser'''
		# Write the yacctab file in the module directory
		# rather than the current directory
		cachedDir = os.path.abspath(os.curdir)
		os.chdir(os.path.abspath(os.path.dirname(__file__) ) )
		if not os.path.exists('yacctab.py'):
			yacc_optimize = False
		# Extend the lexer by temporarily monkey-patching the
		# __init__ method of the CLexer class
		pycparser.c_lexer.CLexer.__init__ = CInterfaceLexerInit
		super(type(self), self).__init__(lex_optimize, lextab, yacc_optimize, yacctab, yacc_debug)
		pycparser.c_lexer.CLexer.__init__ = cachedCLexerInit
		os.chdir(cachedDir)
	
	
	def p_function_specifier(self, p):
		''' function_specifier  : INLINE
				| __STDCALL
				| __CDECL
		'''
		p[0] = p[1]


def interpret(filename, libs=None, includePath='',
		macroDefinitions=None, encoding=None):
	'''Pass in the name of the header or C source file to include,
	a list of the loaded libraries to search for the symbols to run,
	and a list of path names to use searching for included files.
	This function returns an object containing all the valid symbols defined
	in the include files that can be found in the libraries.
	'''
	try:
		from . import cpp
	except ImportError:
		import cpp
	import ctypes
	
	if macroDefinitions == None:
		macroDefinitions = {}
	if isinstance(includePath, basestringTypes):
		includePath = [includePath]
	
	# initialize the variables needed to use the cinterface headers
	shortBits = str(ctypes.sizeof(ctypes.c_short) * 8)
	intBits = str(ctypes.sizeof(ctypes.c_int) * 8)
	longBits = str(ctypes.sizeof(ctypes.c_long) * 8)
	longlongBits = str(ctypes.sizeof(ctypes.c_longlong) * 8)
	macroDefinitions.update(
			__CPP_CHAR_SIGNED = '1',
			__CPP_CHAR_BITS = '8',
			__CPP_SHORT_BITS = shortBits,
			__CPP_INT_BITS = intBits,
			__CPP_LONG_BITS = longBits,
			__CPP_LONGLONG_BITS = longlongBits,
			__CPP_SIZE_BITS = str(ctypes.sizeof(ctypes.c_size_t)  * 8),
			__CPP_PTRDIFF_BITS = str(ctypes.sizeof(ctypes.c_void_p) * 8),
			__CPP_INTPTR_BITS = str(ctypes.sizeof(ctypes.c_void_p) * 8),
			__CPP_WCHAR_BITS = str(ctypes.sizeof(ctypes.c_wchar) * 8),
			# The types below are not guaranteed to be the right size
			__CPP_ATOMIC_BITS = str(ctypes.sizeof(ctypes.c_int) * 8),
			__CPP_CLOCK_BITS = str(ctypes.sizeof(ctypes.c_int) * 8),
			__CPP_TIME_BITS = str(ctypes.sizeof(ctypes.c_long) * 8),
			__CPP_WCTRANS_BITS = str(ctypes.sizeof(ctypes.c_wchar) * 8),
			__CPP_WCTYPE_BITS = str(ctypes.sizeof(ctypes.c_wchar) * 8),
			__CPP_WINT_BITS = str(ctypes.sizeof(ctypes.c_wchar) * 8),
			)
	if '^' not in includePath:
		includePath.append(os.path.join(_moduleDirectory, 'include') )
	else:
		includePath.remove('^')
	# Each entry in customMacros is equivalent to using a #define directive
	# where the entry is the part of the line after the directive
	# The C preprocessor does not understand asm macros, so give them
	# empty definitions
	customMacros = ['__asm__(x) ', '__asm(x) ']
	for item in customMacros:
		cpp.defineMacro(item, macroDefinitions)
	ppsource = cpp.preprocess(filename, macroDefinitions, includePath, encoding=encoding)
	for value in ['struct', 'union', 'enum']:
		if value in macroDefinitions:
			log.warning('File defines invalid macro: %s' % value)
			del macroDefinitions[value]
	parser = CInterfaceParser()
	ast = parser.parse(ppsource, filename)

	vf = InterfaceTranslator(libs)
	vf.visit(ast)
	
	translatedMacros = cpp.translateMacros(macroDefinitions)
	for item in translatedMacros:
		if item not in vf.output:
			vf.output[item] = translatedMacros[item]
	
	return vf.output



def LoadLibrary(name, path=[]):
	import glob
	if isinstance(path, basestringTypes):
		path = [path]
	if os.name in ['nt', 'ce']:
		fname = [name, name + '.dll']
	elif os.name == 'posix' and sys.platform == 'darwin':
		fname = ['lib' + name + '.dylib', name + '.dylib', name+'.framework/'+name]
	elif os.name == 'posix':
		fname = [name + '.so', name + '.so.[0-9]*', name + '.so.[0-9]*.[0-9]*'
				'lib' + name + '.so', 'lib' + name + '.so.[0-9]*',
				'lib' + name + '.so.[0-9]*.[0-9]*']
	libname = ''
	g = []
	for d in path:
		for n in fname:
			g = glob.glob(os.path.join(d, n) )
			if g:
				libname = g[-1]
				break
		if g: break
	
	if libname:
		return ctypes.cdll.LoadLibrary(libname)
	else:
		for libname in fname:
			try:
				return ctypes.cdll.LoadLibrary(libname)
			except:
				pass
		return None



def include(filename, libraries=None, includePath='', linkPath='',
		macroDefinitions=None, encoding=None):
	'''Pass in the name of the header or C source file to include,
	a list of the names of the library files to search for the symbols to
	run, and a list of path names to use searching for included files.
	This function returns an object with attributes covering all the valid
	symbols defined in the include files that can be found in
	the library files.  A directory containing minimal C99 header files will
	be appended to the includePath; if this is undesired behavior, use a path
	component with the single character '^' as one of the paths in includePath,
	and that directory will not be included.
	'''
	if not isinstance(libraries, list):
		if libraries == None:
			libraries = []
		else:
			libraries = [libraries]
	libs = []
	libraries.append('c')
	for libname in libraries:
		lib = None
		if linkPath:
			lib = LoadLibrary(libname, linkPath)
		if lib is None:
			## find_library requires a compiler on linux
			libPath = ctypes.util.find_library(libname)
			if libPath is None:
				libPath = libname
			lib = ctypes.cdll.LoadLibrary(libPath)
			if lib is None:
				raise IOError('Library %s not found' % libPath)
		libs.append(lib)
	if not includePath:
		includePath = [os.curdir]
	return interpret(filename, libs, includePath, macroDefinitions, encoding)


def close(self):
	'''Closes all open libraries and removes attributes from
	the CInterface object
	'''
	class ns(object): pass
	if os.name == 'nt':
		UnloadLibrary = ctypes.windll.kernel32.FreeLibrary
		libdl = ns()
		libdl._handle = None
	else:
		libPath = ctypes.util.find_library('libdl')
		libdl = ctypes.cdll.LoadLibrary(libPath)
		UnloadLibrary = libdl.dlclose
	for lib in self[':libraries:']:
		UnloadLibrary(lib._handle)
	self[':libraries:'] = []
	if libdl._handle is not None:
		libdl.dlclose(libdl._handle)
	items = dict.keys(self)
	self[':exportedVars:'] = {}
	for item in list(items)[:]:
		if item not in [':exportedVars:', ':libraries:']:
			delattr(self, item)
	# Force garbage collection now
	import gc
	gc.collect()


log = logging.getLogger(__name__)
class _NullLogHandler(logging.Handler):
	'''A logging handler that performs no action.  It suppresses a warning
	about not configuring logging if the module is imported by another that
	has not configured logging.
	'''
	# For Python 2.7+, use logging.NullHandler
	def emit(self, x):
		pass
log.addHandler(_NullLogHandler() )


def run_cli(argv=None):
	def cli_define(option, opt_str, value, parser, defs):
		if opt_str in ['--define', '-D']:
			z = value.split('=')
			cpp.defineMacro('#define ' + z[0] + ' ' + '='.join(z[1:]) + os.linesep, defs)
		elif opt_str in ['--undef', '-U']:
			if value in defs:
				del defs[value]
		else:
			# This statement would only run after incorrectly changing the option parser
			raise ValueError('Unknown definition option: %s' % opt_str)
	
	
	try:
		from . import cpp
	except ImportError:
		import cpp
	import optparse
	
	if argv == None:
		argv = sys.argv[1:]
	logging.basicConfig()
	clidefs = {}
	# Read options from argument list
	clparser = optparse.OptionParser()
	clparser.add_option('-I', '--include', dest='includePath', action='append',
			help='Append include file search path')
	clparser.add_option('-D', '--define', action='callback', type='str', callback=cli_define,
			help='Define macro', metavar='MACRO[=VALUE]', callback_args=(clidefs,) )
	clparser.add_option('-U', '--undef', action='callback', type='str',
			help='Undefine macro', callback=cli_define, callback_args=(clidefs,) )
	clparser.add_option('-e', dest='encoding',
			help='Set input file encoding', metavar='CODE')
	clparser.add_option('-o', dest='filename',
			help='Set output file name', metavar='FILE')
	clparser.add_option('-L', dest='linkPath', action='append',
			help='Append library file search path')
	clparser.add_option('-l', dest='libFile', action='append',
			help='Add libraries to link with')
	(options, args) = clparser.parse_args(argv)
	
	h = include(args[0], libraries=options.libFile, includePath=options.includePath, linkPath=options.linkPath,
			macroDefinitions=clidefs, encoding=options.encoding)
	if options.filename:
		fname = options.filename
	else:
		ndx = args[0].rfind('.')
		if ndx == -1:
			bfname = os.path.split(args[0])[1]
			fname = bfname + '.dat'
		else:
			bfname = os.path.split(args[0][:ndx])[1]
			fname = bfname + '.dat'
	save(h, fname)
	return 0



if __name__ == '__main__':
	sys.exit(run_cli() )
