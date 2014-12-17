#ifndef _STDLIB_H_
#define _STDLIB_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_SIZE_BITS || !defined __CPP_WCHAR_BITS
	#error Missing macro definitions detected
#endif


/* The order of quot and rem are not specified by the standard */
typedef struct {
	int quot;
	int rem;
} div_t;

typedef struct {
	long quot;
	long rem;
} ldiv_t;

typedef struct {
	long long quot;
	long long rem;
} lldiv_t;


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



void abort(void);
int abs(int);
int atexit(void (*)(void));
int at_quick_exit(void (*)(void));
double atof(const char *);
int atoi(const char *);
long int atol(const char *);
long long int atoll(const char *);
void *bsearch(const void *, const void *, size_t, size_t, int (*)(const void *, const void *));
void *calloc(size_t, size_t);
div_t div(int, int);
void exit(int);
void free(void *);
char *getenv(const char *);
long int labs(long int);
long long int llabs (long long int);
ldiv_t ldiv(long int, long int);
lldiv_t lldiv (long long int, long long int);
void *malloc(size_t);
int mblen(const char *, size_t);
size_t mbstowcs(wchar_t *, const char *, size_t);
int mbtowc(wchar_t *, const char *, size_t);
void qsort(void *, size_t, size_t, int (*)(const void *, const void *));
void quick_exit(int);
int rand(void);
void *realloc(void *, size_t);
void srand(unsigned int);
double strtod(const char *, char **);
float strtof(const char *, char **);
long int strtol(const char *, char **, int);
long double strtold(const char *, char **);
long long int strtoll(const char *, char **, int);
unsigned long int strtoul(const char *, char **, int);
unsigned long long int strtoull(const char *, char **, int);
int system(const char *);
size_t wcstombs(char *, const wchar_t *, size_t);
int wctomb(char *, wchar_t);
void _Exit(int);

#ifdef _POSIX_SOURCE
long a64l(const char *);
double drand48(void);
char *ecvt(double, int, int *, int *);
double erand48(unsigned short int[3]);
char *fcvt (double, int, int *, int *);
char *gcvt(double, int, char *);
int getsubopt(char **, char *const *, char **);
int grantpt(int);
char *initstate(unsigned int, char *, size_t);
long int jrand48(unsigned short int[3]);
char *l64a(long);
void lcong48(unsigned short int[7]);
long int lrand48(void);
char *mktemp(char *);
int mkstemp(char *);
long int mrand48(void);
long int nrand48(unsigned short int [3]);
char *ptsname(int);
int putenv(char *);
int rand_r(unsigned int *);
long random(void);
char *realpath(const char *, char *);
unsigned short int seed48(unsigned short int[3]);
void setkey(const char *);
char *setstate(const char *);
void srand48(long int);
void srandom(unsigned);
int unlockpt(int);
#endif


// Macros are possibly wrong
#define EXIT_FAILURE (-1)
#define EXIT_SUCCESS 0
#define MB_CUR_MAX 6

#ifndef NULL
#define NULL ((void *)0)
#endif

#define RAND_MAX (((1 << (__CPP_INT_BITS-2)) - 1) * 2 + 1)

#endif
