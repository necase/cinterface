#!/usr/bin/env python
# File encoding: utf-8
# Copyright 2014 Nic Case. Distributed according to the BSD License
'''A C Preprocessor implemented in Python

This module implements a C Preprocessor and includes several functions
useful to preprocessing and using the information from a C source file.
To see warnings from this preprocessor, configure a log via the logging
module (for example, by calling basicConfig).
'''
# Simplify support for Python 2.5
from __future__ import with_statement

'''
Unsupported/unimplemented/untested features:
Digraphs and trigraphs
'?' conditional operator
Multi-character and wide character constants
Distinguishing between preprocessing numbers with embedded macros
Test unicode handling on non-UTF8 locales
Test wide character constants
Use of file and line number hints in the preprocessed output
	gcc has # lineNumber filename   and msvc has #line lineNumber filename
tgmath.h, wchar.h

Development notes:
strand: piece of a string
Token: item that contains information representing a strand including
		previous macro expansions
'''
import codecs
import locale
import logging
import os
import platform
import re
import sys
import time

try:
	import builtins
	long = int
except ImportError:
	next = lambda obj: obj.next()

# Module data: the compiled regular expression objects used in this module

# Matches any preprocessor directive; the first group is the directive name,
# the second group is the first word of the directive's argument
anyDirective = re.compile(r'^[\s\000]*#[\s\000]*'
		+ r'(include|ifdef|ifndef|if|define|undef|error|warning|line|pragma|else|elif|endif)?'
		+ r'[\s\000]+(\S*)') # Any directive

lineComment = re.compile(r'//.*')  # finds // style comments
blockComment = re.compile(r'/\*.*') # finds the beginning of /* ... */ comments
blockCommentEnd = re.compile(r'\*/') # finds the ending of /* ... */ comments
lineContinuation = re.compile(r'\\[\s\000]*$')
definedWithVarDirective = re.compile(r'[\s\000]*defined[\s\000]*\(*\s*(\w+)') # #define

onlyTokenList = re.compile(r'(\w+)|(\(|\))|(\.\.\.)|(\S)|(\s+)')
defineArgs = re.compile(r'(\w+)' + r'(\([^\)]*\))?' + r'\s*(.*)')
tokenList = re.compile(r'defined|\w+\(.*\)'
		+ r'|[\w\'\\]+|\(|\)|!=|==|\|\||&&|##|#|<<|>>|&|\^|\||~|%|>=|>|<=|<|\+|-|\*|/|!')

# blockDelimiter: one of the characters that should be treated as the
# beginning or end of a string that should not be analyzed (thus, is a block)
blockDelimiter = re.compile(r'(\")|(/\*|\*/|//)')

# Matches a valid conditional directive (ifdef, ifndef, if, or endif)
condDirective = re.compile(r'^[\s\000]*#[\s\000]*'
		+ r'(ifdef|ifndef|if|endif)'
		+ r'[\s\000]+')

# Used in isCNumber
integers = re.compile(r'^([+-]?[0-9]+)(([uU]?[lL]?)$|([lL]?[uU]?)$)')
hexnumbers = re.compile(r'^(0[xX][0-9a-fA-F]+)(([uU]?[lL]?)$|([lL]?[uU]?)$)')
charconstant = re.compile(r"'(\w)'")
octalconstant = re.compile(r"^'\\([0-7]+)'")
hexconstant = re.compile(r"^'\\x([0-9a-fA-F]+)'")
escapesequence = re.compile(r"'\\([abfnrtv\\'\"\?])'")
escapedict = {'a':7, 'b':8, 'f':12, 'n':10, 'r':13, 't':9, 'v':11,
		'\\':92, "'":39, '"':34, '?':63}


def flattenList(l):
	'''Return a generator yielding each element from a nested list'''
	for item in l:
		if isinstance(item, list):
			for subitem in flattenList(item):
				yield subitem
		else:
			yield item

# Follows symlinks to find the directory of this module
import inspect
_moduleDirectory = os.path.dirname(os.path.realpath(inspect.getsourcefile(flattenList) ) )


def warnUnicodeError(e):
	'''Produce a warning and continue on encountering a UnicodeError'''
	try:
		c = unicode('\ufffd')
	except NameError:
		c = '\ufffd'
	if isinstance(e, UnicodeEncodeError):
		log.warn('Invalid input: %s' % e.object.encode('utf8', 'replace'))
	else:
		log.warn('Invalid input: %s' % e.object.decode('utf8', 'replace'))
	r = c * len(e.object[e.start:e.end])
	return r, e.end

codecs.register_error('warn', warnUnicodeError)


class Token(object):
	'''An object that contains several properties of a preprocessing token'''
	def __init__(self, value = None, string = '', shouldRescan = 1, macroHistory = None):
		if macroHistory is None:
			macroHistory = set()
		self.value = value
		self.string = string
		self.shouldRescan = shouldRescan
		self.macroHistory = macroHistory
	
	def __repr__(self):
		return ('Token[' + repr(self.value) + ', ' + repr(self.string) + ', '
				+ repr(self.shouldRescan) + ', ' + repr(self.macroHistory) +  ']')


def getStringEnd(iterator):
	'''Returns the index of the end of a double-quote delimited string'''
	stringEnd = -1
	for token in iterator:
		if token.group() == '"':
			if token.string[token.start()-1] == '\\':
				continue
			stringEnd = token.end()
			break
	return stringEnd


def stringify(s):
	'''Returns the stringified representation of its input.
	Escapes backslashes and quotes and encapsulates the result in quotes.
	'''
	return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def blockify(iterator, strStart):
	'''Returns the tokens within a parenthesized or quoted expression as a list
	along with the final value of the parenthesis balance.  Requires an
	iterator that consumes its arguments so the caller can resume where
	this function ended.
	'''
	parenBalance = 1
	l = []
	for token in iterator:
		if token.group() == ')':
			parenBalance -= 1
			# The last element of the list will be the length of the string that corresponds to the list
			l.append(token.end() - strStart)
			break
		elif token.group() == '(':
			pEnd = findMatchingParen(iterator)
			tokens = token.string[token.start():pEnd]
			l.append(tokens)
		elif token.group() == '"':
			stringStart = token.start()
			stringEnd = getStringEnd(iterator)
			l.append(token.string[stringStart:stringEnd])
		else:
			l.append(token.group())
	return l, parenBalance


def splitArgumentList(s):
	'''Return a list of tokens separated by commas at the top level, thus
	parsing a function's argument list
	'''
	s = re.sub('\s+', ' ', s)
	l = []
	pos = 0
	iterator = re.finditer(r'[",\(\)]', s)
	for token in iterator:
		if token.group() == ',':
			tokens = s[pos:token.start()].strip()
			l.append(tokens)
			pos = token.end()
		elif token.group() == '"':
			stringEnd = getStringEnd(iterator)
		elif token.group() == '(':
			pEnd = findMatchingParen(iterator)
	l.append(s[pos:].strip())
	# The last element of the list will be the length of the string
	# that corresponds to the list
	l.append(len(s))
	return l


def findMatchingParen(iterator):
	'''Finds the location of the end parenthesis that matches the open
	parenthesis which was encountered just before calling this function
	'''
	parenBalance = 1
	parenEnd = -1
	for token in iterator:
		if token.group() == '(':
			parenBalance += 1
		elif token.group() == ')':
			parenBalance -= 1
			if parenBalance == 0:
				parenEnd = token.end()
				break
		elif token.group() == '"':
			idx = getStringEnd(iterator)
	return parenEnd


def strandify(s, exp, d):
	'''Split a string into a list of pieces of the string (strands)
	'''
	parenBalance = 0
	if type(exp) != type(lineComment):
		tokenIt  = re.finditer(exp, s)
	else:
		tokenIt = exp.finditer(s)
	t = []
	foundCallable = 0
	for token in tokenIt:
		currentWord = token.group()
		if currentWord == '(' and foundCallable:
			foundCallable = 0
			tStart = token.start()
			tokens, balance = blockify(tokenIt, tStart)
			t.append(tokens)
			if balance != 0:
				parenBalance = 1
		elif currentWord == '"':
			stringStart = token.start()
			stringEnd = getStringEnd(tokenIt)
			t.append(s[stringStart:stringEnd])
		elif currentWord == ')':
			t.append(currentWord)
		elif currentWord in d and d[currentWord] == callable:
			foundCallable = 1
			t.append(currentWord)
		else:
			t.append(currentWord)
	if parenBalance != 0:
		t[-1] = s[ token.start(): ]
	return t, parenBalance


def join(prefix, iterator):
	'''Adds a prefix to each item in an iterator and returns resulting list'''
	return [prefix+item for item in iterator]


def findMacros(t, d):
	'''Returns a set of macros defined in the dictionary d found in
	the input string'''
	s = set()
	w = re.findall(r'\w+', t)
	for word in w:
		if word in d:
			s.add(word)
	return s


def expandFunctionLikeMacro(macroName, token, d):
	'''Expands macro given in the string macroName with arguments given
	in token according to the recipe in d
	'''
	if macroName == '__CPP_STRINGIFY__':
		block = stringify(token.string[1:-1].strip())
		token.macroHistory.add(macroName)
		outtoken_part = expandList(block, d, token.macroHistory)
	elif macroName == '__CPP_MERGE__':
		block = token.string[1:-1]
		outtoken_part = expandList(block, d, token.macroHistory)
	else:
		expansion = d['__CPP_expansion__'][macroName]
		argList = d['__CPP_arguments__'][macroName]
		arguments = splitArgumentList(token.string[1:-1])
		expandedArgs = []
		for arg, argName in zip(arguments[:-1], argList):
			if '${' + argName + '}' in flattenList(expansion):
				expandedArgs.append(expandLine(arg, d))
			else:
				expandedArgs.append('')
		origArgList = join('__', argList)
		origArgList.extend(argList)
		arguments.pop()
		arguments.extend(expandedArgs)
		token.macroHistory.add(macroName)
		if '...' in argList:
			namedArgLen = len(d['__CPP_arguments__'][macroName]) - 1
			newargs = arguments[:namedArgLen]
			newargs.append(','.join(arguments[namedArgLen:len(expandedArgs)]) )
			newargs.extend(expandedArgs[:namedArgLen])
			newargs.append(','.join(expandedArgs[namedArgLen:len(expandedArgs)]) )
			arguments = newargs
		tokensDict = dict(list(zip(origArgList, arguments)))
		outtoken_part = expandList(d['__CPP_expansion__'][macroName], d, token.macroHistory, tokensDict)
		if '...' in argList:
			for idx, tt in enumerate(outtoken_part):
				if tt.string == '__VA_ARGS__':
					outtoken_part[idx:idx+1], _ = tokenize(tokensDict['...'], d)
	return outtoken_part


def retokenize(tokens, d):
	'''Retokenize the string s and re-expand the line
	Convert instances of '(' to lists if they are arguments
	of a function-like macro
	'''
	s = ''.join(h.string for h in tokens)
	unbalancedParens = 0
	outtoken = []
	inparen = 0
	paren = []
	for t in tokens:
		if inparen:
			if ')' in t.value:
				inparen += t.value.count('(') - t.value.count(')')
				if inparen <= 0:
					parenStr = ''.join(h.string for h in paren) + t.value
					parenTokens, unbalancedParens = tokenize(parenStr, d, t.macroHistory)
					outtoken.extend(parenTokens[1:])
					inparen = 0
					paren = []
				else:
					paren.append(t)
			elif '(' in t.value:
				inparen += t.value.count('(') - t.value.count(')')
				paren.append(t)
			else:
				paren.append(t)
		elif '(' in t.value:
			if len(outtoken) > 0 and outtoken[-1].string in d:
				paren.append(outtoken[-1])
				paren.append(t)
				inparen += t.value.count('(') - t.value.count(')')
			else:
				outtoken.append(t)
		else:
			outtoken.append(t)
	outtoken = expandTokens(s, d, outtoken, unbalancedParens)
	return outtoken


def expandTokens( s, d, tokens, unbalancedParens):
	'''Completely replace the macros in a list of tokens
	'''
	ns = s
	parseArguments = 0
	macroName = ''
	trackingDefect = 0
	replacedToken = 0
	outtoken = []
	for pos, token in enumerate(tokens):
		if token.shouldRescan == 0:
			# no need to examine token further--it will not expand further
			outtoken.append(token)
			continue
		if parseArguments:
			if not isinstance(token.value, list):
				# Allows for spaces between function name and argument list
				if not( token.value.strip(' \t') == '' ):
					if token.value not in d or d[token.value] != callable:
						parseArguments = 0
					else:
						macroName = token.value
				if token.value == os.linesep:
					nl = token.value
					while nl.isspace():
						nl = getNextLine(d)
					if nl.strip()[0] == '(':
						ttokens, tunbalancedParens = tokenize(s.rstrip() + ' ' + nl, d)
						return expandTokens(s.rstrip() + ' ' + nl, d, ttokens, tunbalancedParens)
					else:
						# This is the one place that needs to look ahead, and if there is 
						# nothing to be done, just preprocess the next line and pretend it 
						# was part of this line
						tt = preprocessLine(nl, d)
						outtoken.append( Token(None, tt, None, None) )
						return outtoken
				outtoken.append(token)
				continue
			parseArguments = 0
			if macroName == '':
				# recursive call of a function-like macro
				token.shouldRescan = 0
				outtoken.append(token)
				continue
			outtoken_part = expandFunctionLikeMacro(macroName, token, d)
			replacedToken = 1
			poptok = outtoken.pop()
			while poptok.value != macroName:
				poptok = outtoken.pop()
			outtoken.extend(outtoken_part)
		elif isinstance(token.value, list):
			outtoken.append(token)
		elif token.value in d:
			if token.value in token.macroHistory:
				# Already expanded this macro, so stop expanding it now
				token.shouldRescan = 0
				if d[token.value] == callable:
					parseArguments = 1
					macroName = ''
				outtoken.append(token)
				continue
			ts = s
			while unbalancedParens and d[token.value] == callable:
				# Loop executes when a function-like macro should have arguments on the next line
				# Need to get the next lines until the parentheses are terminated
				nl = getNextLine(d)
				ts = ts.rstrip() + nl
				nll, newBalance = strandify(ts, onlyTokenList, d)
				unbalancedParens = newBalance
				if unbalancedParens == 0:
					tmptokens, unbalancedParens = strandify(ts, onlyTokenList, d)
					tmptokensstr = ''
					while len(tokens) > pos+1:
						tokens.pop()
					for tt in tmptokens[pos+1:]:
						if isinstance(tt, list):
							ttstr = '(' + ''.join(tt[:-1]) + ')'
						else:
							ttstr = tt
						tokens.append( Token(tt, ttstr, 1, token.macroHistory) )
					ns = ns.rstrip() + ts[len(s)-1:]
					s = ts
			if d[token.value] == callable:
				parseArguments = 1
				macroName = token.value
				token.shouldRescan = 1
				outtoken.append( token )
			else:
				replacedToken = 1
				token.macroHistory.add(token.value)
				expandedTokens, uParens = tokenize(d[token.value], d, token.macroHistory)
				outtoken.extend(expandedTokens)
		else:
			# Prevent examining this token again
			token.shouldRescan = 0
			outtoken.append( token )
	if replacedToken:
		outtoken = retokenize(outtoken, d)
	return outtoken


def expandList(tokens, d, macroHistory = None, tokensDict = None):
	'''Expand macros in the list of strands
	'''
	if not isinstance(tokens, list):
		tokens = [tokens]
	outtokens = []
	shouldRescan = 1
	if macroHistory == None:
		macroHistory = set()
	else:
		macroHistory = macroHistory.copy()
	for token in tokens:
		if token[0:2] == '${':
			unexpandedKey = '__' + token[2:-1]
			if ( unexpandedKey in tokensDict
					and tokensDict[token[2:-1]] != tokensDict[unexpandedKey] ):
				mm = findMacros(tokensDict[token[2:-1]], d)
				macroHistory.update( mm )
		if isinstance(token, list):
			joinedArgs = [tokensDict[t[2:-1]] if t[0:2] == '${' and t[-1] == '}' and t[2:-1] in tokensDict else t for t in token]
			tokenstr = '(' + ''.join(joinedArgs) + ')'
			token = joinedArgs
		elif len(token) > 3 and token[0:2] == '${':
			tokenstr = tokensDict[token[2:-1]]
			parenTokens, unbalancedParens = strandify(tokenstr, onlyTokenList, d)
			for t in parenTokens:
				if isinstance(t,list):
					tokenstr = '(' + ''.join(t[:-1]) + ')'
				else:
					tokenstr = t
				parenMacroHistory = macroHistory.copy()
				outtokens.append(Token(t, tokenstr, shouldRescan, parenMacroHistory) )
			continue
		else:
			tokenstr = token
		outtokens.append( Token(token, tokenstr, shouldRescan, macroHistory.copy() ) )
	
	return outtokens


def tokenize(s, d, macroHistory = None):
	'''Translates a string into a list of tokens
	'''
	strands, unbalancedParens = strandify(s, onlyTokenList, d)
	tokens = []
	shouldRescan = 1
	if macroHistory == None:
		macroHistory = set()
	for strand in strands:
		if isinstance(strand, list):
			strandString = '(' + ''.join(strand[:-1]) + ')'
		else:
			strandString = strand
		tokens.append(Token(strand, strandString, shouldRescan, macroHistory.copy() ))
	
	return tokens, unbalancedParens


def expandLine(s, d):
	'''Performs macro expansion on string s according to the definition
	dictionary d
	'''
	tokens, unbalancedParens = tokenize(s, d)
	outtoken = expandTokens(s, d, tokens, unbalancedParens)
	return ''.join(h.string for h in outtoken)


def isCNumber(s):
	'''Returns a tuple indicating number signedness and length,
	and the number or the string if not a number.
	The first element of the tuple has these possible values:
		0: not a number
		1: signed int
		2: unsigned int
		3: signed long
		4: unsigned long
		5: signed long long
		6: unsigned long long
	'''
	m = integers.search(s)
	if m:
		if 'U' in m.group(2).upper():
			n, size = cast_unsigned(s)
			return size*2, n
	base = 0
	if not m:
		m = hexnumbers.search(s)
		base = 16
	if not m:
		m = charconstant.search(s)
		if m:
			return 1, ord(m.group(1))
	if not m:
		m = escapesequence.search(s)
		if m:
			return 1, escapedict[m.group(1)]
	if not m:
		m = octalconstant.search(s)
		base = 8
	if not m:
		m = hexconstant.search(s)
		base = 16
	if m:
		return 1, long(m.group(1), base)
	else:
		return 0, s


def cast_unsigned(s):
	'''Convert a string of a numerical constant with the unsigned specifier to
	a positive python number.  Returns that number and the size specifier
	as a tuple of integers.  The second value is 1 for ints, 2 for longs,
	and 3 for long longs
	'''
	import ctypes
	s = s.strip()
	longs = s.upper().count('L')
	s = s.rstrip('uUlL')
	if longs == 0:
		size = 1
		n = ctypes.c_uint(long(s) )
	elif longs == 1:
		size = 2
		n = ctypes.c_ulong(long(s) )
	elif longs == 2:
		size = 3
		n = ctypes.c_ulonglong(long(s) )
	else:
		raise ValueError('Invalid number: %s' % s)
	return n.value, size


def cast_unsigned2(n, intType):
	'''Convert a number to its unsigned representation given a signed number
	and its integer length (a number compatible with the return value of
	cast_unsigned).
	'''
	if intType % 2 == 1:
		return n
	import ctypes
	if intType == 2:
		m = ctypes.c_uint(long(n) )
	elif intType == 4:
		m = ctypes.c_ulong(long(n) )
	elif intType == 6:
		m = ctypes.c_ulonglong(long(n) )
	else:
		raise ValueError('Invalid number: %s' % s)
	return m.value


def defined_op(name, d):	return long(name in d)
def not_op(left, right):	return long(not right)
def bnot_op(left, right):	return ~right
def mul_op(left, right):	return left * right
def div_op(left, right):	return left // right
def mod_op(left, right):	return left % right
def add_op(left, right):	return left + right
def sub_op(left, right):	return left - right
def bshiftr_op(left, right):	return left >> right
def bshiftl_op(left, right):	return left << right
def gt_op(left, right):	return long(left > right)
def ge_op(left, right):	return long(left >= right)
def lt_op(left, right):	return long(left < right)
def le_op(left, right):	return long(left <= right)
def eq_op(left, right):	return long(left == right)
def ne_op(left, right):	return long(left != right)
def band_op(left, right):	return left & right
def bxor_op(left, right):	return left ^ right
def bor_op(left, right):	return left | right
def land_op(left, right):	return long(left and right and 1)
def lor_op(left, right):	return long((left or right) and 1)

def def_op_simple(iterator, r, d, t):
	# Returns an integer rather than a tuple
	ans, token = evaluate(iterator, r, d, 70, 0, t)
	return long(ans in d)

def pnot_op_simple(iterator, r, d, t):
	# Returns an integer rather than a tuple
	ans, token = evaluate(iterator, r, d, 60, 0, t)
	return long(not ans)


def neg_op(iterator, l,r, d,t):
	ans, token = evaluate(iterator, r, d, 60, 0, t)
	return -ans, token

def paren_op(iterator, l,r, d,t):
	ans, token = evaluate(iterator, r, d, 0, 0, t)
	if token == ')':
		try:
			token = next(iterator)
		except StopIteration:
			token = ''
			pass
	else:
		raise SyntaxError('Unexpected token: %s' % token)
	return ans, token


def def_op(iterator, r, d,t):
	ans, token = evaluate(iterator, r, d, 70,0,t)
	return long(ans in d), token

def pnot_op(iterator, r, d, t):
	ans, token = evaluate(iterator, r, d, 60,0,t)
	return long(not ans), token

def pbnot_op(iterator, r, d, t):
	ans, token = evaluate(iterator, r, d, 60,0,t)
	return ~ans, token


def evaluate(iterator, token='', d = {}, rightPrecedence = 0,
		stopCalculating = 0, intType = 0):
	'''Top-down parser for calculating the value of conditional expressions'''
	if isinstance(iterator, list):
		iterator = iter(iterator)
	operators = {'defined': lambda l,r: def_op_simple(iterator, r, d, 0),
			'*':mul_op, '!': lambda l,r: pnot_op_simple(iterator, r, d, 0),
			'/': div_op, '%':mod_op, '+': add_op, '-':sub_op, '>>':bshiftr_op,
			'<<':bshiftl_op, '>':gt_op, '>=':ge_op, '<':lt_op, '<=':le_op,
			'==':eq_op, '!=':ne_op, '&':band_op, '^':bxor_op, '|':bor_op,
			'&&':land_op, '||':lor_op}
	precedence = {'defined': 70, '!':60, '~':60, '*':50,
			'/':50, '%':50, '+':47, '-':47, '>>':46,
			'<<':46, '>':45, '>=':45, '<':45, '<=':45,
			'==':44, '!=':44, '&':43, '^':42, '|':41,
			'&&':40, '||':20, '':0 }
	prefix = {'defined': lambda l,r,t: def_op(iterator, r, d,t),
			'!': lambda l,r,t: pnot_op(iterator, r, d,t),
			'~': lambda l,r,t: pbnot_op(iterator, r, d,t), 
			'+': lambda l,r,t: evaluate(iterator, r, d, 60, 0, t),
			'-': lambda l,r,t: neg_op(iterator, l,r,d,t),
			'(': lambda l,r,t: paren_op(iterator, l,r,d,t) }
	defaultPrefix = lambda key: lambda l,r,t: (key, '')
	
	updateExpression = 0
	if token == '':
		for item in iterator:
			intType, token = isCNumber(item)
			break
	left = token
	
	for item in iterator:
		t = token
		itype, token = isCNumber(item)
		if t == '&&' and left == 0:
			stopCalculating = 1
		if t == '||' and left != 0:
			left = 1
			stopCalculating = 1
		if updateExpression:
			if t in ['&&', '||'] and precedence.get(t,0) == rightPrecedence:
				p = rightPrecedence - 1
			else:
				p = precedence.get(t,0)
			tmp, token = evaluate(iterator, token, d, p, stopCalculating, itype)
			if not stopCalculating:
				if t not in ['<<', '>>']:
					if intType > itype:
						if intType > 0:
							tmp = cast_unsigned2(tmp, intType)
					elif itype > intType:
						if itype > 0:
							left = cast_unsigned2(left, itype)
				left = operators[t](left, tmp)
		else:
			left, tmp = prefix.get(t, defaultPrefix(t))(t, token, itype)
			if tmp != '':
				token = tmp
			if rightPrecedence < precedence.get(token,0):
				updateExpression = 1
				continue
			else:
				break
		if rightPrecedence >= precedence.get(token,0):
			break
	return left, token


def isIdentifier(s):
	'''Returns 1 if the string is a valid identifier, otherwise returns 0'''
	if not (s[0].isalpha() or s[0] == '_'):
		return 0
	for c in s:
		if not (c.isalnum() or c == '_'):
			return 0
	return 1


def parseIfDirective(s, d):
	'''Evaluates the conditional expression for #if and #elif directives'''
	s = anyDirective.sub(r'\2', s)
	s = re.sub(r'defined\s*\((.*?)\)', r'defined \1', s)
	strands = tokenList.findall(s)
	expansion = []
	keepMacros = 0
	for item in strands:
		if keepMacros:
			expansion.append(item)
			keepMacros = 0
		elif item == 'defined':
			keepMacros = 1
			expansion.append(item)
		else:
			if isIdentifier(item):
				if item in d:
					tt = expandLine(item,d)
				else:
					tt = '0'
				expansion.append(tt)
			else:
				expansion.append(item)
	expandedStrands = tokenList.findall(''.join(expansion))
	ret, t = evaluate(expandedStrands, '', d)
	if ret != 0:
		ret = 1	
	return ret


def calculateValue(s):
	'''Calculates the value of the input string'''
	strands = tokenList.findall(s)
	ret, t = evaluate(strands, '', {})
	return ret


def skipToEndif(d):
	'''Ignores the rest of the conditional expression'''
	while 1:
		s = getNextLine(d)
		mm = condDirective.search(s)
		if mm:
			if mm.group(1) == 'endif':
				return
			else:
				skipToEndif(d)

def translateMacros(macros):
	r = {}
	for item in macros:
		if item.startswith('__CPP_'):
			continue
		'''Completely translating the macros into usable objects would require
		a C interpreter, which is beyond the current scope of this module.
		Many macros will be returned as strings that the user may have to
		further process if desired.  However, this module will attempt to
		translate some macros for the benefit of the user.  The current list
		of macros that are translated beyond strings is:
		- Object-like macros that translate to a variable or function name
		'''
		if macros[item] == callable:
			argnames = macros['__CPP_arguments__'][item]
			el = expandLine(item + '(' + ', '.join(argnames) + ')', macros)
			'''Would be nice to convert function-like macros into a callable object
			and add it to r
			It should be indistinguishable from a function call, because
			APIs do not necessarily distinguish between macros and functions
			If this is desired, remember to consider definitions like:
			#define eprintf(format, ...) fprintf(stderr, format, __VA_ARGS__)
			#define func1(arg1) otherfunc(arg1, sizeof(int), otherfunc(otherargs) )
			'''
			r[item] = el
		else:
			s = expandLine(item, macros)
			if s in r:
				r[item] = r[s]
			else:
				try:
					g = calculateValue(s)
				except:
					g = s
				r[item] = g
	
	return r


def stringifyDefinitions(d):
	'''Turn the definitions back into strings'''
	def stringifyInternalDefs(func, args):
		s = ''
		if func == '__CPP_STRINGIFY__':
			for arg in args:
				s += '#' + arg[4:-1] + ' '
		elif func == '__CPP_MERGE__':
			s += args[0][4:-1] + ' '
			for arg in args[1:]:
				s += '## ' + arg[4:-1]
		else:
			raise ValueError(func + ' is not an allowed value.')
		return s
	
	dlist = []
	idArgs = 0
	for item in d:
		if item[0:5] == '__CPP':
			continue
		if d[item] == callable:
			args = ','.join(d['__CPP_arguments__'][item])
			expansion = ''
			for element in d['__CPP_expansion__'][item]:
				if idArgs:
					expansion += stringifyInternalDefs(idArgs, element)
					idArgs = 0
				elif element[0:2] == '${':
					expansion += element[2:-1]
				elif element[0:5] == '__CPP':
					idArgs = element
					continue
				else:
					expansion += element
			dlist.append('#define ' + item + '(' + args + ') ' + expansion )
		else:
			dlist.append('#define ' + item + ' ' + d[item])
	
	return os.linesep.join(dlist)


def defineMacro(s, d):
	'''Define macros:
	Function-like macros:
		#define MACRO(a,b,c)   a + b + # c  -->
		d['MACRO']: callable
		d['__CPP_arguments__']['MACRO']: ['a', 'b', 'c']
		d['__CPP_expansion__']['MACRO']: ['${a}', ' ', '+', ' ', '${b}',
				' ', '+', ' ', '__CPP_STRINGIFY__', ['${__c}'] ]
	Object-like macros:
		#define MACRO definition
		d['MACRO']: 'definition'
	'''
	s = anyDirective.sub(r'\2', s)
	definedParts = defineArgs.findall(s)[0]
	if definedParts[1]:
		# function-like macro
		d[definedParts[0]] = callable
		args = definedParts[1][1:-1].split(',')
		for nn, arg in enumerate(args):
			args[nn] = arg.strip()
		if '__CPP_arguments__' not in d:
			d.update(__CPP_expansion__={}, __CPP_arguments__={})
		d['__CPP_arguments__'][definedParts[0]] = args
		strands = re.findall(r'".*?[^\\]"|""|\w+|##|#|[^"\w#]+', definedParts[2] )
		foundHash = 0
		mergeArgCount = 0
		for idx, item in enumerate(strands):
			if foundHash:
				if not item.isspace() and item != '':
					if item != '##':
						mergeArgCount += 1
						if mergeArgCount >= 2:
							foundHash = 0
							mergeArgCount = 0
					else:
						mergeArgCount = 0
			if item == '##':
				strands[idx] = ''
				pos = idx - 1
				while pos >= 0 and strands[pos].isspace():
					strands[pos] = ''
					pos -= 1
				if strands[pos][0:2] == '${':
					strands[idx] = ['${__' + strands[pos][2:-1] + '}']
				else:
					if not foundHash:
						strands[idx] = [strands[pos] ]
				if not foundHash:
					strands[pos] = '__CPP_MERGE__'
					foundHash = 1 + idx
				pos = idx + 1
				while pos < len(strands) and strands[pos].isspace():
					strands[pos] = ''
					pos += 1
			elif item == '#':
				pos = idx + 1
				while pos < len(strands) and strands[pos].isspace():
					pos += 1
				if pos < len(strands) and strands[pos] in args:
					strands[idx] = '__CPP_STRINGIFY__'
					pos = idx + 1
					while pos < len(strands) and strands[pos].isspace():
						strands[pos] = ''
						pos += 1
					strands[pos] = ['${__' + strands[pos] + '}']
			elif foundHash:
				if item in args:
					strands[foundHash-1].append( '${__' + item + '}')
					strands[idx] = ''
				elif item != '':
					strands[foundHash-1].append( item )
					strands[idx] = ''
			elif item in args:
				strands[idx] = '${' + item + '}'
		d['__CPP_expansion__'][definedParts[0]] = [t for t in strands if t != '']
	else:
		d[definedParts[0]] = definedParts[2]


def preprocessConditional(m, matchedDirective, d):
	'''Preprocess a group of lines starting with #if, #ifdef, or #ifndef'''
	p = ''
	# decide whether to parse the following lines
	condition = 0
	if matchedDirective == 'ifdef':
		s = m.group(2)
		if s in d:
			condition = 1
	elif matchedDirective == 'ifndef':
		s = m.group(2)
		if not s in d:
			condition = 1
	elif matchedDirective == 'if':
		condition = parseIfDirective(m.string, d)
	else:
		raise IOError(m.string)
	
	ns = ''
	takeElse = not condition
	while 1:
			ns = getNextLine(d)
			mm = anyDirective.search(ns)
			if mm:
				mmDirective = mm.group(1)
			else:
				mmDirective = None
			if mmDirective == 'endif':
				break
			if condition:
				if mmDirective in ['else', 'elif']:
					condition = 0
					skipToEndif(d)
					break
				else:
					ns = preprocessLine(ns, d)
					p = p + ns
			elif mmDirective == 'else':
				if takeElse:
					condition = 1
				else:
					skipToEndif(d)
					break
			elif mmDirective == 'elif':
				condition = parseIfDirective(ns, d)
				if condition:
					takeElse = 0
					ns = anyDirective.sub(r'#if \2', ns)
					ns = preprocessLine(ns, d)
					p = p + ns
					break
			elif mmDirective in ['if', 'ifdef', 'ifndef']:
				skipToEndif(d)
				# No break here because there is one more endif to find after this call
	return p


def preprocessLine(s, d):
	'''Preprocess a single line.  The string s representing the line to
	preprocess should include the line break characters.  The dict d
	should contain any defined macros which should be used to substitute
	values into the expression given in s.
	'''
	p = ''
	m = anyDirective.search(s)
	if m:
		matchedDirective = m.group(1)
		if matchedDirective == 'define':
			defineMacro(s,d)
		elif matchedDirective == 'undef':
			s = m.group(2)
			if s in d:
				d.pop(s)
		elif matchedDirective in ['if', 'ifdef', 'ifndef']:
			p = preprocessConditional(m, matchedDirective, d)
		elif matchedDirective == 'warning':
			log.warning(d['__FILE__'] + ':' + d['__LINE__'] + ': ' + anyDirective.sub(r'\2', s) )
		elif matchedDirective == 'error':
			raise SyntaxError(s)
		elif matchedDirective == 'include':
			# Include named file
			name = s[m.start(2):].rstrip()
			path = []
			if not (name[0] in ['"', '<'] and name[-1] in ['"', '>']):
				name = expandLine(name, d).strip()
			if name[0] == '"' and name[-1] == '"':
				currentDir = os.path.dirname(os.path.abspath(d['__CPP_fileobject__'].name ) )
				path.insert(0, currentDir)
			p = preprocess(name[1:-1], d, path, encoding=d['__CPP_encoding__'])
		elif matchedDirective == 'line':
			# Change line number and source file seen by preprocessor
			s = expandLine(s[m.end(1):], d)
			t = re.search(r'([0-9]+)[\s\000]+(.*)', s)
			d['__LINE__'] = str(int(t.group(1)) - 1)
			if t.group(2):
				d['__FILE__'] = t.group(2)
		elif matchedDirective == 'pragma':
			# Ignore pragma directives
			pass
		elif matchedDirective == None:
			# Ignore empty directives
			pass
		else:
			raise IOError(s)
	else:
		p = expandLine(s, d)
	return p


def getNextLine(d):
	''' Get the next line of the file to preprocess.  Strip out all
	comments and combine continued lines into a single line.
	Returns the next line to preprocess as a a string.
	'''
	f = d['__CPP_fileobject__']
	linesAdvanced = 1
	s = next(f)
	p = ''
	foundLineContinuation = lineContinuation.search(s)
	while foundLineContinuation:
		linesAdvanced += 1
		s = s[:foundLineContinuation.start()] + next(f)
		foundLineContinuation = lineContinuation.search(s)
	foundQuote = 0
	continueParsingLine = 1
	pos = 0
	while continueParsingLine:
		continueParsingLine = 0
		removedChars = 0
		blockDelimiters = blockDelimiter.finditer(s, pos)
		for match in blockDelimiters:
			if foundQuote:
				if match.group(1) == '"' and match.string[match.start()-1] != '\\':
					foundQuote = 0
				continue
			if match.group(1) == '"':
				foundQuote = 1
				continue
			if match.group(2) == '//':
				s = s[:match.start()]
				if len(s) > 0:
					s += os.linesep
				break
			elif match.group(2) == '/*':
				blockCommentStart = match.start() - removedChars
				p = s[:blockCommentStart]
				# Find block comment end markers
				#   If found, remove the comment portion and search for more comments on the current line
				#   If not found, get a new line and search for the end marker on that line
				for mate in blockDelimiters:
					if mate.group(2) == '*/':
						match = mate
						s = p + ' ' + match.string[match.end():]
						removedChars = match.end() - blockCommentStart - 1
						break
				else:
					# Executed when the for loop terminates by exhausting blockDelimiters,
					# so the search should continue on the next line of the file
					nextLine = ''
					commentEndPos = -1
					while commentEndPos == -1:
						linesAdvanced += 1
						nextLine = next(f)
						foundLineContinuation = lineContinuation.search(nextLine)
						while foundLineContinuation:
							linesAdvanced += 1
							nextLine = nextLine[:foundLineContinuation.start()] + next(f)
							foundLineContinuation = lineContinuation.search(nextLine)
						commentEndPos = nextLine.find('*/')
					s = p + nextLine[commentEndPos+2:]
					pos = blockCommentStart
					continueParsingLine = 1
				
	d['__LINE__'] = str(long(d['__LINE__']) + linesAdvanced)
	return s


def findFile(filename, paths):
	'''Search for filename in the list of given paths
	and return the first existing filename
	'''
	for p in paths:
		fullpath = os.path.join(p, filename)
		if os.path.exists(fullpath):
				return fullpath
	raise IOError('File ' + filename + ' not found.')


def preprocess(filename, defines = None, path = '', callback = None, encoding=None):
	'''Preprocess a file.  The file to be processed is passed in as a
	string in the filename argument; if the file is not in the current or
	parent directory, it may be looked for in the standard include
	directories.  A dict of defined macros may be passed in as the defines
	argument; defines['MACRONAME'] = 'VALUE' is the necessary syntax.
	A list of the directories to search may be passed in as the path
	argument.  Directories
	will be searched, after the current and parent directories, in the order
	given.  Pass in a string as the encoding parameter to dictate the input
	encoding, such as 'utf8'.  Returns the unicode string representing the
	preprocessed file.
	'''
	headerPaths = []
	if sys.platform.startswith('win'):
		if path:
			headerPaths = path
		if defines and '__CPP_path__' in defines:
			headerPaths.extend(defines['__CPP_path__'])
		else:
			try:
				headerPaths.extend(os.environ['INCLUDE'].split(';'))
			except KeyError:
				pass
	else:
		if path:
			headerPaths = path
		if defines and '__CPP_path__' in defines:
			headerPaths.extend(defines['__CPP_path__'])
		else:
			for var in ['CPATH', 'C_INCLUDE_PATH']:
				try:
					headerPaths.extend(os.environ[var].split(':'))
				except KeyError:
					pass
			otherHeaderPaths = ['/usr/local/include', '/usr/include']
			target = platform.machine()
			targetSpecificHeaders = '/usr/include/' + target
			if not os.path.exists(targetSpecificHeaders):
				targetSpecificHeaders = None
				incl = os.listdir('/usr/include')
				for item in incl:
					if item.startswith(target) and os.path.isdir('/usr/include/' + item):
						targetSpecificHeaders = '/usr/include/' + item
						break
			if targetSpecificHeaders:
				otherHeaderPaths.append(targetSpecificHeaders)
			headerPaths.extend(otherHeaderPaths)
	
	if not defines or not '__CPP_fileobject__' in defines:
		if defines == None:
			defines = dict(__CPP_expansion__={}, __CPP_arguments__={})
		savedFile = []
		savedFilename = ''
		defines['__CPP_filelist__'] = []
		defines['__CPP_includedlevel__'] = dict()
		defines['__CPP_path__'] = headerPaths[:]
		# Enable relative path names by inserting the current directory to the
		# beginning of headerPaths, but it will not be propagated beyond the
		# initial call because the path is not saved to the defines variable
		headerPaths.insert(0, os.curdir)
	else:
		savedFile = defines['__CPP_fileobject__']
		savedLine = defines['__LINE__']
		savedFilename = defines['__FILE__']
	
	includeFilePath = findFile(filename, headerPaths)
	if includeFilePath in defines['__CPP_filelist__']:
		if includeFilePath in defines['__CPP_includedlevel__']:
			defines['__CPP_includedlevel__'][includeFilePath] += 1
		else:
			defines['__CPP_includedlevel__'][includeFilePath] = 1
		if defines['__CPP_includedlevel__'][includeFilePath] > 20:
			log.error('Recursive include of file ' + includeFilePath + ' detected.')
			raise ValueError('Recursive include of file ' + includeFilePath + ' detected.')
	
	preprocessedList = []
	if callback == None:
		callback = preprocessedList.append
	defines['__CPP_filelist__'].append(includeFilePath)
	if encoding == None:
		encoding = locale.getpreferredencoding()
	defines['__CPP_encoding__'] = encoding
	with codecs.open(includeFilePath, 'r', encoding=encoding, errors='warn') as f:
		defines.update(__CPP_fileobject__ = f, __LINE__ = '0',
			__FILE__ = stringify(filename), __DATE__ = '"' + time.strftime('%b %d %Y') + '"',
			__TIME__ = '"' + time.strftime('%H:%M:%S') + '"', __STDC__ = '1',
			__STDC_HOSTED__ = '1', __STDC_VERSION__ = '199901L'
			)
		datestr = '"' + time.strftime('%b %d %Y') + '"'
		if datestr[5] == '0':
			# Remove the leading 0 from days less than 10 (01-09)
			datestr = datestr[0:5] + ' ' + datestr[6:]
			defines.update(__DATE__ = datestr)
		if not '__CPP_arguments__' in defines:
			defines.update(__CPP_expansion__={}, __CPP_arguments__={})
		if not '__CPP_STRINGIFY__' in defines:
			defines.update(__CPP_STRINGIFY__ = callable, __CPP_MERGE__ = callable, _Pragma = callable)
			defines['__CPP_arguments__'].update(__CPP_STRINGIFY__='__CPP_a__', __CPP_MERGE__ = ['__CPP_a__', '__CPP_b__'], _Pragma = 'x')
			defines['__CPP_expansion__'].update(__CPP_STRINGIFY__='__CPP_a__', __CPP_MERGE__='__CPP_a__', _Pragma = '')
		
		# Platform-specific standard macros are defined below
		if platform.machine() in ['i386', 'i686']:
			defines['__i386__'] = ''
		elif platform.machine() in ['x86_64', 'AMD64']:
			defines['__x86_64__'] = ''
		elif platform.machine() in ['ppc', 'PowerPC', 'Power Macintosh']:
			defines['__ppc__'] = '1'
		elif platform.machine() in ['ia64']:
			defines['__ia64__'] = '1'
		
		if platform.system() == 'Windows':
			defines['_WIN32'] = ''
			if sys.maxsize > 2 ** 32:
				defines['_WIN64'] = ''
		elif platform.system() == 'Darwin':
			defines['__MACH__'] = ''
			defines['__APPLE__'] = ''
			defines['TARGET_OS_MAC'] = '1'
			if '__i386__' in defines:
				defines['TARGET_CPU_X86'] = '1'
			elif '__ppc__' in defines:
				defines['TARGET_CPU_PPC'] = '1'
		else:
			defines['__unix__'] = ''
		
		while 1:
			try:
				l = getNextLine(defines)
			except StopIteration:
				break
			l = preprocessLine(l, defines)
			callback(l)
		if not isinstance(savedFile, list):
			defines['__CPP_fileobject__'] = savedFile
			defines['__LINE__'] = savedLine
			defines['__FILE__'] = savedFilename
	defines['__CPP_filelist__'].remove(includeFilePath)
	if includeFilePath in defines['__CPP_includedlevel__']:
		defines['__CPP_includedlevel__'][includeFilePath] -= 1
	return ''.join(preprocessedList)


log = logging.getLogger(__name__)
class _NullLogHandler(logging.Handler):
	'''A logging handler that performs no action.
	'''
	# Using this class as a log handler suppresses a warning about not
	# configuring logging if the module is imported by another that has
	# not configured logging.  For Python 2.7+, use logging.NullHandler
	def emit(self, x):
		pass
log.addHandler(_NullLogHandler() )



def run_cli(argv=None):
	'''Run the command-line interface of the program
	'''
	def cli_define(option, opt_str, value, parser, defs):
		if opt_str in ['--define', '-D']:
			z = value.split('=')
			defineMacro('#define ' + z[0] + ' ' + '='.join(z[1:]) + os.linesep, defs)
		elif opt_str in ['--undef', '-U']:
			if value in defs:
				del defs[value]
		else:
			raise ValueError('Unknown definition option: %s' % opt_str)
	
	import optparse
	logging.basicConfig()
	if os.name == 'posix':
		import signal
		# Ignore possible broken pipes; suppresses warning when redirecting
		# output to a program that reads less than the whole output stream
		signal.signal(signal.SIGPIPE, signal.SIG_DFL)
	if argv == None:
		argv = sys.argv[1:]
	clidefs = {}
	
	parser = optparse.OptionParser()
	parser.add_option('-I', '--include', dest='path', action='append',
				help='Append search path')
	parser.add_option('-D', '--define', action='callback', type='str', callback=cli_define,
				help='Define macro', metavar='MACRO[=VALUE]', callback_args=(clidefs,) )
	parser.add_option('-U', '--undef', action='callback', type='str',
				help='Undefine macro', callback=cli_define, callback_args=(clidefs,) )
	parser.add_option('-e', dest='encoding',
			help='Set input file encoding', metavar='CODE')
	(options, args) = parser.parse_args(argv)
	if options.path:
		options.path.insert(0, os.getcwd() )
		path = options.path
	else:
		path = [os.getcwd() ]
	
	s = preprocess(args[0], defines=clidefs, path=path, encoding=options.encoding)
	if len(args) > 1:
		with codecs.open(args[1], 'w', encoding=options.encoding) as f:
			f.write(s)
	else:
		try:
			print(s)
		except UnicodeEncodeError:
			sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
			print(s)
	return 0


if __name__ == '__main__':
	sys.exit(run_cli() )

#	Copyright (c) 2014, Nic Case
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without
#	modification, are permitted provided that the following conditions are met:
#
#	1.	Redistributions of source code must retain the above copyright
#		notice, this list of conditions and the following disclaimer.
#
#	2.	Redistributions in binary form must reproduce the above copyright
#		notice, this list of conditions and the following disclaimer in the
#		documentation and/or other materials provided with the distribution.
#
#	3.	Neither the name of the copyright holder nor the names of any
#		contributors may be used to endorse or promote products derived
#		from this software without specific prior written permission.
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#	DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#	FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#	DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#	SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#	CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#	OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
