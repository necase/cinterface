#ifndef _LIMITS_H_
#define _LIMITS_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_CHAR_SIGNED
	#error Missing macro definitions detected
#endif

/* These definitions require 2's complement arithmetic */
#define CHAR_BIT 8
#define SCHAR_MIN	(-128)
#define SCHAR_MAX 127
#define UCHAR_MAX 255
#define CHAR_MIN (__CPP_CHAR_SIGNED ? SCHAR_MIN : 0 )
#define CHAR_MAX (__CPP_CHAR_SIGNED ? SCHAR_MAX : UCHAR_MAX )
#define MB_LEN_MAX 6

/* These definitions are convoluted to avoid integer promotion/overflow */
#define SHRT_MIN (((1 << (__CPP_SHORT_BITS-2)) - 1) *-2 - 2)
#define SHRT_MAX (((1 << (__CPP_SHORT_BITS-2)) - 1) * 2 + 1)
#define USHRT_MAX (((1U << (__CPP_SHORT_BITS-2)) - 1) * 4 + 4)
#define INT_MIN (((1 << (__CPP_INT_BITS-2)) - 1) *-2 - 2)
#define INT_MAX (((1 << (__CPP_INT_BITS-2)) - 1) * 2 + 1)
#define UINT_MAX (-1U)
#define LONG_MIN (((1L << (__CPP_LONG_BITS-2)) - 1) *-2 - 2)
#define LONG_MAX (((1L << (__CPP_LONG_BITS-2)) - 1) * 2 + 1)
#define ULONG_MAX (-1UL)
#define LLONG_MIN (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) *-2 - 2)
#define LLONG_MAX (((1LL << (__CPP_LONGLONG_BITS-2)) - 1) * 2 + 1)
#define ULLONG_MAX (-1ULL)

#endif
