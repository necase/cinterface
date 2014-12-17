#ifndef _STRING_H_
#define _STRING_H_


#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		|| !defined __CPP_SIZE_BITS
	#error Missing macro definitions detected
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

#ifndef NULL
#define NULL ((void *)0)
#endif

void *memchr(const void *, int, size_t);
int memcmp(const void *, const void *, size_t);
void *memcpy(void *restrict s1, const void *restrict s2, size_t n);
void *memmove(void *, const void *, size_t);
void *memset(void *, int, size_t);

char *strcat(char *restrict s1, const char *restrict s2);
char *strchr(const char *, int);
int strcmp(const char *, const char *);
int strcoll(const char *, const char *);
char *strcpy(char *restrict s1, const char *restrict s2);
size_t strcspn(const char *, const char *);
char *strerror(int);
size_t strlen(const char *);
char *strncat(char *restrict s1, const char *restrict s2, size_t n);
int strncmp(const char *, const char *, size_t);
char *strncpy(char *restrict s1, const char *restrict s2, size_t n);
char *strpbrk(const char *, const char *);
char *strrchr(const char *, int);
size_t strspn(const char *, const char *);
char *strstr(const char *, const char *);
char *strtok(char *restrict s1, const char *restrict s2);
size_t strxfrm(char *restrict s1, const char *restrict s2, size_t n);

#ifdef _POSIX_SOURCE
#include <locale.h>

void *memccpy(void *restrict s1, const void *restrict s2, int, size_t n);
char *stpcpy(char *restrict s1, const char *restrict s2);
char *stpncpy(char *restrict s1, const char *restrict s2, size_t n);
int strcoll_l(const char *, const char *, locale_t);

char *strdup(const char *);

char *strerror_l(int, locale_t);
int strerror_r(int, char *, size_t);

char *strndup(const char *, size_t);
size_t strnlen(const char *, size_t);

char *strsignal(int);

char *strtok_r(char *restrict s1, const char *restrict s2, char **restrict, end);

size_t strxfrm_l(char *restrict s1, const char *restrict s2, size_t n, locale_t l);
#endif

#endif
