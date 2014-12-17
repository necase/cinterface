#ifndef _WCTYPE_H_
#define _WCTYPE_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_WCTRANS_BITS || !defined __CPP_WCTYPE_BITS \
		!defined __CPP_WINT_BITS
	#error Missing macro definitions detected
#endif


#ifndef WEOF
	#if __CPP_INT_BITS == __CPP_WINT_BITS
		typedef unsigned int wint_t;
		#define WEOF (-1U)
	#elif __CPP_LONG_BITS == __CPP_WINT_BITS
		typedef unsigned long wint_t;
		#define WEOF (-1UL)
	#elif __CPP_LONGLONG_BITS == __CPP_WINT_BITS
		typedef unsigned long long wint_t;
		#define WEOF (-1ULL)
	#else
		#error Unsupported size for wint_t
	#endif
#endif

#if __CPP_INT_BITS == __CPP_WCTRANS_BITS
	typedef unsigned int wctrans_t;
#elif __CPP_LONG_BITS == __CPP_WCTRANS_BITS
	typedef unsigned long wctrans_t;
#elif __CPP_LONGLONG_BITS == __CPP_WCTRANS_BITS
	typedef unsigned long long wctrans_t;
#else
	#error Unsupported size for wctrans_t
#endif


#if __CPP_INT_BITS == __CPP_WCTYPE_BITS
	typedef unsigned int wctype_t;
#elif __CPP_LONG_BITS == __CPP_WCTYPE_BITS
	typedef unsigned long wctype_t;
#elif __CPP_LONGLONG_BITS == __CPP_WCTYPE_BITS
	typedef unsigned long long wctype_t;
#else
	#error Unsupported size for wctype_t
#endif


int iswalnum(wint_t);
int iswalpha(wint_t);
int iswblank(wint_t);
int iswcntrl(wint_t);
int iswctype(wint_t, wctype_t);
int iswdigit(wint_t);
int iswgraph(wint_t);
int iswlower(wint_t);
int iswprint(wint_t);
int iswpunct(wint_t);
int iswspace(wint_t);
int iswupper(wint_t);
int iswxdigit(wint_t);
wint_t towctrans(wint_t, wctrans_t);
wint_t towlower(wint_t);
wint_t towupper(wint_t);

wctrans_t wctrans (const char*);
wctype_t wctype (const char*);

#endif
