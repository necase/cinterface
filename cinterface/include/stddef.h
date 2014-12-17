#ifndef _STDDEF_H_
#define _STDDEF_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_PTRDIFF_BITS \
		|| !defined __CPP_SIZE_BITS || !defined __CPP_WCHAR_BITS
	#error Missing macro definitions detected
#endif


#ifndef NULL
#define NULL ((void *)0)
#endif

#define offsetof(type, field) ((size_t)(&((type *)0)->field))

#if __CPP_INT_BITS == __CPP_PTRDIFF_BITS
	typedef int ptrdiff_t;
#elif __CPP_LONG_BITS == __CPP_PTRDIFF_BITS
	typedef long ptrdiff_t;
#elif __CPP_LONGLONG_BITS == __CPP_PTRDIFF_BITS
	typedef long long ptrdiff_t;
#else
	#error Unsupported size for ptrdiff_t
#endif

#ifndef __CPP_SIZE_DEFINED
	#if __CPP_INT_BITS == __CPP_SIZE_BITS
		typedef unsigned int size_t;
	#elif __CPP_LONG_BITS == __CPP_SIZE_BITS
		typedef unsigned long size_t;
	#elif __CPP_LONGLONG_BITS == __CPP_SIZE_BITS
		typedef unsigned long long size_t;
	#else
		#error Unsupported size for size_t
	#endif
	#define __CPP_SIZE_DEFINED
#endif

#ifndef __CPP_WCHAR_DEFINED
	#if __CPP_INT_BITS == __CPP_WCHAR_BITS
		typedef unsigned int wchar_t;
	#elif __CPP_LONG_BITS == __CPP_WCHAR_BITS
		typedef unsigned long wchar_t;
	#elif __CPP_LONGLONG_BITS == __CPP_WCHAR_BITS
		typedef unsigned long long wchar_t;
	#elif __CPP_WCHAR_BITS >= 0
		#error Unsupported size for wchar_t
	#endif
	#define __CPP_WCHAR_DEFINED
#endif


#endif

