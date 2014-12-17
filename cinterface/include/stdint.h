#ifndef _STDINT_H_
#define _STDINT_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_INTPTR_BITS || !defined __CPP_SIZE_BITS \
		|| !defined __CPP_PTRDIFF_BITS || !defined __CPP_ATOMIC_BITS \
		|| !defined __CPP_WCHAR_BITS || !defined __CPP_WINT_BITS
	#error Missing macro definitions detected
#endif


/* This is one of many places that assume CHAR_BIT is 8 */
#define __CPP_8BIT char
#define INT8_C(value) value
#define UINT8_C(value) value ## U

#if __CPP_LONGLONG_BITS == 64
#define __CPP_64BIT long long
#define INT64_C(value) value ## LL
#define UINT64_C(value) value ## ULL
#endif

#if __CPP_SHORT_BITS == 16
	#define __CPP_16BIT short
	#define INT16_C(value) value
	#define UINT16_C(value) value ## U
#elif __CPP_SHORT_BITS == 32
	#define __CPP_32BIT short
	#define INT32_C(value) value
	#define UINT32_C(value) value ## U
#endif

#if __CPP_LONG_BITS == 32
	#define __CPP_32BIT long
	#define INT32_C(value) value ## L
	#define UINT32_C(value) value ## UL
#elif __CPP_LONG_BITS == 64
	#define __CPP_64BIT long
	#define INT64_C(value) value ## L
	#define UINT64_C(value) value ## UL
#endif

#if __CPP_INT_BITS == 16
	#define __CPP_16BIT int
	#define INT16_C(value) value
	#define UINT16_C(value) value ## U
#elif __CPP_INT_BITS == 32
	#define __CPP_32BIT int
	#define INT32_C(value) value
	#define UINT32_C(value) value ## U
#elif __CPP_INT_BITS == 64
	#define __CPP_64BIT int
	#define INT64_C(value) value
	#define UINT64_C(value) value ## U
#endif


typedef signed __CPP_8BIT int8_t;
typedef unsigned __CPP_8BIT uint8_t;
typedef signed __CPP_8BIT int_least8_t;
typedef unsigned __CPP_8BIT uint_least8_t;
typedef signed __CPP_8BIT int_fast8_t;
typedef unsigned __CPP_8BIT uint_fast8_t;

#define INT8_MIN (((1 << (8-2)) - 1) *-2 - 2)
#define INT8_MAX (((1 << (8-2)) - 1) * 2 + 1)
#define UINT8_MAX (((1 << (8-2)) - 1) * 4 + 4)
#define INT_LEAST8_MIN INT8_MIN
#define INT_LEAST8_MAX INT8_MAX
#define UINT_LEAST8_MAX UINT8_MAX
#define INT_FAST8_MIN INT8_MIN
#define INT_FAST8_MAX INT8_MAX
#define UINT_FAST8_MAX UINT8_MAX


#ifndef __CPP_16BIT
	#if __CPP_SHORT_BITS >= 16
		typedef short int_least16_t
		typedef unsigned short uint_least16_t;
		#define INT_LEAST16_MIN  (((1 << (__CPP_SHORT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST16_MAX  (((1 << (__CPP_SHORT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST16_MAX (((1U << (__CPP_SHORT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_INT_BITS >= 16
		typedef int int_least16_t
		typedef unsigned int uint_least16_t;
		#define INT_LEAST16_MIN  (((1 << (__CPP_INT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST16_MAX  (((1 << (__CPP_INT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST16_MAX (((1U << (__CPP_INT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONG_BITS >= 16
		typedef long int_least16_t
		typedef unsigned long uint_least16_t;
		#define INT_LEAST16_MIN  (((1L << (__CPP_LONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST16_MAX  (((1L << (__CPP_LONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST16_MAX (((1UL << (__CPP_LONG_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONGLONG_BITS >= 16
		typedef long long int_least16_t
		typedef unsigned long long uint_least16_t;
		#define INT_LEAST16_MIN  (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST16_MAX  (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST16_MAX (((1ULL << (__CPP_LONGLONG_BITS-2)) - 1) * 4 + 4)
	#else
		#error No suitable type for int_least16_t
	#endif
#else
	typedef __CPP_16BIT int16_t;
	typedef unsigned __CPP_16BIT uint16_t;
	typedef __CPP_16BIT int_least16_t;
	typedef unsigned __CPP_16BIT uint_least16_t;
	#define INT16_MIN (((1 << (16-2)) - 1) *-2 - 2)
	#define INT16_MAX (((1 << (16-2)) - 1) * 2 + 1)
	#define UINT16_MAX (((1U << (16-2)) - 1) * 4 + 4)
#endif

typedef int_least16_t int_fast16_t;
typedef uint_least16_t uint_fast16_t;
#define INT_FAST16_MIN INT_LEAST16_MIN
#define INT_FAST16_MAX INT_LEAST16_MAX
#define UINT_FAST16_MAX UINT_LEAST16_MAX


#ifndef __CPP_32BIT
	#if __CPP_SHORT_BITS >= 32
		typedef short int_least32_t
		typedef unsigned short uint_least32_t;
		#define INT_LEAST32_MIN (((1 << (__CPP_SHORT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST32_MAX (((1 << (__CPP_SHORT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST32_MAX (((1U << (__CPP_SHORT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_INT_BITS >= 32
		typedef int int_least32_t
		typedef unsigned int uint_least32_t;
		#define INT_LEAST32_MIN (((1 << (__CPP_INT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST32_MAX (((1 << (__CPP_INT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST32_MAX (((1U << (__CPP_INT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONG_BITS >= 32
		typedef long int_least32_t
		typedef unsigned long uint_least32_t;
		#define INT_LEAST32_MIN (((1L << (__CPP_LONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST32_MAX (((1L << (__CPP_LONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST32_MAX (((1UL << (__CPP_LONG_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONGLONG_BITS >= 32
		typedef long long int_least32_t
		typedef unsigned long long uint_least32_t;
		#define INT_LEAST32_MIN (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST32_MAX (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST32_MAX (((1ULL << (__CPP_LONGLONG_BITS-2)) - 1) * 4 + 4)
	#else
		#error No suitable type for int_least32_t
	#endif
#else
	typedef __CPP_32BIT int32_t;
	typedef unsigned __CPP_32BIT uint32_t;
	typedef __CPP_32BIT int_least32_t;
	typedef unsigned __CPP_32BIT uint_least32_t;
	#define INT32_MIN (((1L << (32-2)) - 1) *-2 - 2)
	#define INT32_MAX (((1L << (32-2)) - 1) * 2 + 1)
	#define UINT32_MAX (((1UL << (32-2)) - 1) * 4 + 4)
#endif


typedef int_least32_t int_fast32_t;
typedef uint_least32_t uint_fast32_t;
#define INT_FAST32_MIN INT_LEAST32_MIN
#define INT_FAST32_MAX INT_LEAST32_MAX
#define UINT_FAST32_MAX UINT_LEAST32_MAX



#ifndef __CPP_64BIT
	#if __CPP_SHORT_BITS >= 64
		typedef short int_least64_t
		typedef unsigned short uint_least64_t;
		#define INT_LEAST64_MIN (((1 << (__CPP_SHORT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST64_MAX (((1 << (__CPP_SHORT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST64_MAX (((1U << (__CPP_SHORT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_INT_BITS >= 64
		typedef int int_least64_t
		typedef unsigned int uint_least64_t;
		#define INT_LEAST64_MIN (((1 << (__CPP_INT_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST64_MAX (((1 << (__CPP_INT_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST64_MAX (((1U << (__CPP_INT_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONG_BITS >= 64
		typedef long int_least64_t
		typedef unsigned long uint_least64_t;
		#define INT_LEAST64_MIN (((1L << (__CPP_LONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST64_MAX (((1L << (__CPP_LONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST64_MAX (((1UL << (__CPP_LONG_BITS-2)) - 1) * 4 + 4)
	#elif __CPP_LONGLONG_BITS >= 64
		typedef long long int_least64_t
		typedef unsigned long long uint_least64_t;
		#define INT_LEAST64_MIN (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) *-2 - 2)
		#define INT_LEAST64_MAX (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) * 2 + 1)
		#define UINT_LEAST64_MAX (((1ULL << (__CPP_LONGLONG_BITS-2)) - 1) * 4 + 4)
	#else
		#error No suitable type for int_least64_t
	#endif
#else
	typedef __CPP_64BIT int64_t;
	typedef unsigned __CPP_64BIT uint64_t;
	typedef __CPP_64BIT int_least64_t;
	typedef unsigned __CPP_64BIT uint_least64_t;
	#define INT64_MIN (((1LL << (64-2)) - 1) *-2 - 2)
	#define INT64_MAX (((1LL << (64-2)) - 1) * 2 + 1)
	#define UINT64_MAX (((1ULL << (64-2)) - 1) * 4 + 4)
#endif


typedef int_least64_t int_fast64_t;
typedef uint_least64_t uint_fast64_t;
#define INT_FAST64_MIN INT_LEAST64_MIN
#define INT_FAST64_MAX INT_LEAST64_MAX
#define UINT_FAST64_MAX UINT_LEAST64_MAX



typedef long long intmax_t;
typedef unsigned long long uintmax_t;
#define INTMAX_MIN (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) *-2 - 2)
#define INTMAX_MAX (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) * 2 + 1)
#define UINTMAX_MAX (-1ULL)

#define INTMAX_C(value) value ## LL
#define UINTMAX_C(value) value ## ULL


#if __CPP_INTPTR_BITS == __CPP_INT_BITS
typedef int intptr_t;
typedef unsigned int uintptr_t;
#elif __CPP_INTPTR_BITS == __CPP_LONG_BITS
typedef long intptr_t;
typedef unsigned long uintptr_t;
#elif __CPP_INTPTR_BITS == __CPP_SHORT_BITS
typedef short intptr_t;
typedef unsigned short uintptr_t;
#elif __CPP_INTPTR_BITS == __CPP_LONGLONG_BITS
typedef long long intptr_t;
typedef unsigned long long uintptr_t;
#else
#error No suitable type for intptr_t
#endif

#define INTPTR_MIN (((1LL << (__CPP_INTPTR_BITS-2)) - 1) *-2 - 2)
#define INTPTR_MAX (((1LL << (__CPP_INTPTR_BITS-2)) - 1) * 2 + 1)
#define UINTPTR_MAX (-1ULL)

/* size_t is unsigned */
#define SIZE_MAX (((1ULL << (__CPP_SIZE_BITS-2)) - 1) * 4 + 4)

/* ptrdiff_t is signed */
#define PTRDIFF_MIN (((1LL << (__CPP_PTRDIFF_BITS-2)) - 1) *-2 - 2)
#define PTRDIFF_MAX (((1LL << (__CPP_PTRDIFF_BITS-2)) - 1) * 2 + 1)

/* sig_atomic_t is signed */
#define SIG_ATOMIC_MIN (((1LL << (__CPP_ATOMIC_BITS-2)) - 1) *-2 - 2)
#define SIG_ATOMIC_MAX (((1LL << (__CPP_ATOMIC_BITS-2)) - 1) * 2 + 1)

#ifndef WCHAR_MIN
/* wchar_t is unsigned */
#define WCHAR_MAX (((1ULL << (__CPP_WCHAR_BITS-2)) - 1) * 4 + 4)
#define WCHAR_MIN 0
#endif

/* wint_t is unsigned */
#define WINT_MAX (((1ULL << (__CPP_WINT_BITS-2)) - 1) * 4 + 4)
#define WINT_MIN 0

#endif
