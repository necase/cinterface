The cinterface package implements automatically building
an interface to an external C library from its header files.

You may install this package using one of the methods below.
1.	Run the following command: pip install cinterface
2.	Manually download and uncompress the package.  From the
	directory that is created by the uncompression, run
	python setup.py install
3.	Manually download and uncompress the package.  From the
	directory that is created by the uncompression, copy the
	cinterface directory to a directory in the Python path.

Below are examples of using the package.
To use an external library, using sqlite3 as an example
(although sqlite3 has its own python module):
# This is a loose translation of https://sqlite.org/quickstart.html
# which uses statements from https://sqlite.org/cli.html
import cinterface
headerFile = 'sqlite3.h'
libraryName = ['sqlite3']
statements = ['create table tbl1(one varchar(10), two smallint);',
	"insert into tbl1 values('hello!',10);",
	"insert into tbl1 values('goodbye', 20);",
	'select * from tbl1;'
]

try:
	bytes
except:
	bytes = lambda x,y: x.encode(y)

def callback(NotUsed, argc, argv, azColName):
	for i in range(argc):
		print((azColName[i] + bytes(' = ', 'utf8') + argv[i]).decode('utf8') )
	return 0

lib = cinterface.include(headerFile, libraryName)

callback_type = lib.sqlite3_exec.argtypes[2]
callback_function = callback_type(callback)
zErrMsg = lib.sqlite3_exec.argtypes[4]()
db = [lib.sqlite3] # In a function invocation, the list item will be automatically transformed to a null pointer of the given type
ppdb = [db]
rc = lib.sqlite3_open(':memory:', ppdb)
if rc:
	print("Can't open database: %s" % lib.sqlite3_errmsg(db) )
	lib.sqlite3_close(db)
	raise ValueError

db = ppdb[0]
for statement in statements:
	rc = lib.sqlite3_exec(db, statement, callback_function, 0, zErrMsg)
	if rc != lib.SQLITE_OK:
		print('SQL error: %s' % zErrMsg[0])
		lib.sqlite3_free(zErrMsg)

rc = lib.sqlite3_close(db)


If you repeatedly use the interface for the same library, use the
save and load functions of the cinterface module to reduce the time
it takes to translate the header file into a python object, as 
shown below:
### For the first invocation:
import cinterface
filename = 'curl.dat'
headerFile = 'test/curl_mod.h'
libraryName = ['curl']

libcurl = cinterface.include(headerFile, libraryName)
cinterface.save(libcurl, filename)

### In subsequent invocations:
filename = 'curl.dat'
import cinterface
libcurl = cinterface.load(filename)
# Proceed to use lib the same as if you called cinterface.include


The interfaces for the package are not yet complete and may change
in future versions.  Many of the functions in the modules may
change names and become clearly marked as implementation details.


Advanced Usage:
The cinterface package necessarily needs to use a c preprocessor to 
translate the interface of a library.  You can access the preprocessor
as the module cinterface.cpp.  Examples of its usage are given below.
For more detail of the available options, consult the source.

To preprocess a file from the command line and save the preprocessed
output to a file:
$ python -m cinterface.cpp path/to/header.h outputfile.i

To preprocess a file in python code:
from cinterface import cpp
ppout = cpp.preprocess(filename)

The cpp module accepts parameters to customize the preprocessor by
changing the input encoding, defining macros, undefining macros,
and adding directories to the include search path.  The module will
accept any text file and attempt to preprocess it.


