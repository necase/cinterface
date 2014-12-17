#ifndef _TIME_H_
#define _TIME_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_CLOCK_BITS || !defined __CPP_SIZE_BITS \
		|| !defined __CPP_TIME_BITS
	#error Missing macro definitions detected
#endif


#if __CPP_INT_BITS == __CPP_CLOCK_BITS
	typedef unsigned int clock_t;
#elif __CPP_LONG_BITS == __CPP_CLOCK_BITS
	typedef unsigned long clock_t;
#elif __CPP_LONGLONG_BITS == __CPP_CLOCK_BITS
	typedef unsigned long long clock_t;
#elif __CPP_CLOCK_BITS >= 0
	#error Unsupported size for clock_t
#endif

#if __CPP_INT_BITS == __CPP_TIME_BITS
	typedef unsigned int time_t;
#elif __CPP_LONG_BITS == __CPP_TIME_BITS
	typedef unsigned long time_t;
#elif __CPP_LONGLONG_BITS == __CPP_TIME_BITS
	typedef unsigned long long time_t;
#elif __CPP_TIME_BITS >= 0
	#error Unsupported size for time_t
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

struct tm {
	int tm_sec;
	int tm_min;
	int tm_hour;
	int tm_mday;
	int tm_mon;
	int tm_year;
	int tm_wday;
	int tm_yday;
	int tm_isdst;
};

clock_t clock(void);
double difftime(time_t, time_t);
time_t mktime(struct tm *);
time_t time(time_t *);
char *asctime(const struct tm *);
char *ctime(const time_t *);
struct tm *gmtime(const time_t *);
struct tm *localtime(const time_t *);
size_t strftime(char *restrict s, size_t maxsize, const char *restrict format, const struct tm *restrict timeptr);
					 
#define CLOCKS_PER_SEC 1000000

#ifndef NULL
#define NULL ((void *)0)
#endif

#endif
