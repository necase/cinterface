#ifndef _WCHAR_H_
#define _WCHAR_H_
/*
*	Implementation-defined choices: wint_t is unsigned, wchar_t is unsigned,
*	mbstate_t is an unsigned integer type, */
// Required macros listed here:
#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_WINT_BITS \
		|| !defined __CPP_WCHAR_BITS || !defined __CPP_SIZE_BITS
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


typedef struct mbstate_t mbstate_t;

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

struct tm;

#ifndef __CPP_FILE_DEFINED
#define __CPP_FILE_DEFINED
typedef struct FILE FILE;
#endif

#ifndef __CPP_VA_LIST_DEFINED
#define __CPP_VA_LIST_DEFINED
typedef void * va_list;
#endif


int fwprintf(FILE * restrict stream, const wchar_t * restrict format, ...);
int fwscanf(FILE * restrict stream, const wchar_t * restrict format, ...);
int swprintf(wchar_t * restrict s, size_t n, const wchar_t * restrict format, ...);
int swscanf(const wchar_t * restrict s, const wchar_t * restrict format, ...);
int vfwprintf(FILE * restrict stream, const wchar_t * restrict format, va_list arg);
int vfwscanf(FILE * restrict stream, const wchar_t * restrict format, va_list arg);
int vswprintf(wchar_t * restrict s, size_t n, const wchar_t * restrict format, va_list arg);
int vswscanf(const wchar_t * restrict s, const wchar_t * restrict format, va_list arg);
int vwprintf(const wchar_t * restrict format, va_list arg);
int vwscanf(const wchar_t * restrict format, va_list arg);
int wprintf(const wchar_t * restrict format, ...);
int wscanf(const wchar_t * restrict format, ...);
wint_t fgetwc(FILE *);
wchar_t *fgetws(wchar_t * restrict s, int n, FILE * restrict stream);
wint_t fputwc(wchar_t, FILE *);
int fputws(const wchar_t * restrict s, FILE * restrict stream);
int fwide(FILE *, int);
wint_t getwc(FILE *);
wint_t getwchar(void);
wint_t putwc(wchar_t, FILE *);
wint_t putwchar(wchar_t);
wint_t ungetwc(wint_t, FILE *);
double wcstod(const wchar_t * restrict nptr, wchar_t ** restrict endptr);
float wcstof(const wchar_t * restrict nptr, wchar_t ** restrict endptr);
long double wcstold(const wchar_t * restrict nptr, wchar_t ** restrict endptr);
long int wcstol(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);
long long int wcstoll(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);
unsigned long int wcstoul(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);
unsigned long long int wcstoull(const wchar_t * restrict nptr, wchar_t ** restrict endptr, int base);
wchar_t *wcscpy(wchar_t * restrict s1, const wchar_t * restrict s2);
wchar_t *wcsncpy(wchar_t * restrict s1, const wchar_t * restrict s2, size_t n);
wchar_t *wmemcpy(wchar_t * restrict s1, const wchar_t * restrict s2, size_t n);
wchar_t *wmemmove(wchar_t *, const wchar_t *, size_t);
wchar_t *wcscat(wchar_t * restrict s1, const wchar_t * restrict s2);
wchar_t *wcsncat(wchar_t * restrict s1, const wchar_t * restrict s2, size_t n);
int wcscmp(const wchar_t *, const wchar_t *);
int wcscoll(const wchar_t *, const wchar_t *);
int wcsncmp(const wchar_t *, const wchar_t *, size_t);
size_t wcsxfrm(wchar_t * restrict s1, const wchar_t * restrict s2, size_t n);
int wmemcmp(const wchar_t *, const wchar_t *, size_t);
wchar_t *wcschr(const wchar_t *, wchar_t);
size_t wcscspn(const wchar_t *, const wchar_t *);
wchar_t *wcspbrk(const wchar_t *, const wchar_t *);
wchar_t *wcsrchr(const wchar_t *, wchar_t);
size_t wcsspn(const wchar_t *, const wchar_t *);
wchar_t *wcsstr(const wchar_t *, const wchar_t *);
wchar_t *wcstok(wchar_t * restrict s1, const wchar_t * restrict s2, wchar_t ** restrict ptr);
wchar_t *wmemchr(const wchar_t *, wchar_t, size_t);
size_t wcslen(const wchar_t *);
wchar_t *wmemset(wchar_t *, wchar_t, size_t);
size_t wcsftime(wchar_t * restrict s, size_t maxsize, const wchar_t * restrict format, const struct tm * restrict timeptr);
wint_t btowc(int);
int wctob(wint_t);
int mbsinit(const mbstate_t *);
size_t mbrlen(const char * restrict s, size_t n, mbstate_t * restrict ps);
size_t mbrtowc(wchar_t * restrict pwc, const char * restrict s, size_t n, mbstate_t * restrict ps);
size_t wcrtomb(char * restrict s, wchar_t wc, mbstate_t * restrict ps);
size_t mbsrtowcs(wchar_t * restrict dst, const char ** restrict src, size_t len, mbstate_t * restrict ps);
size_t wcsrtombs(char * restrict dst, const wchar_t ** restrict src, size_t len, mbstate_t * restrict ps);


#ifndef NULL
#define NULL ((void *)0)
#endif

#ifndef WCHAR_MIN
	#define WCHAR_MIN 0
	#define WCHAR_MAX (((1ULL << (__CPP_WCHAR_BITS-2)) - 1) * 4 + 4)
#endif


#endif
