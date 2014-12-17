#ifndef _STDIO_H_
#define _STDIO_H_

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_SHORT_BITS \
		!defined __CPP_SIZE_BITS
	#error Missing macro definitions detected
#endif


#ifndef __CPP_FILE_DEFINED
#define __CPP_FILE_DEFINED
typedef struct FILE FILE;
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

typedef struct fpos_t fpos_t;

#ifndef __CPP_VA_LIST_DEFINED
#define __CPP_VA_LIST_DEFINED
typedef void * va_list;
#endif


#define stdin stdin;
#define stdout stdout;
#define stderr stderr;

void clearerr(FILE *);
int fclose(FILE *);
int feof(FILE *);
int ferror(FILE *);
int fflush(FILE *);
int fgetc(FILE *);
int fgetpos(FILE *, fpos_t *);
char *fgets(char *restrict s, int count, FILE *restrict stream);
FILE *fopen(const char *, const char *);
int fprintf(FILE *, const char *, ...);
int fputc(int, FILE *);
int fputs(const char *, FILE *);
size_t fread(void *, size_t, size_t, FILE *);
FILE *freopen(const char *, const char *, FILE *);
int fscanf(FILE *, const char *, ...);
int fseek(FILE *, long int, int);
int fsetpos(FILE *, const fpos_t *);
long int ftell(FILE *);
size_t fwrite(const void *, size_t, size_t, FILE *);
int getc(FILE *);
int getchar(void);
char *gets(char *);
void perror(const char *);
int printf(const char *, ...);
int putc(int, FILE *);
int putchar(int);
int puts(const char *);
int remove(const char *);
int rename(const char *, const char *);
void rewind(FILE *);
int scanf(const char *, ...);
void setbuf(FILE *, char *);
int setvbuf(FILE *, char *, int, size_t);
int snprintf(char *, size_t, const char *, ...);
int sprintf(char *, const char *, ...);
int sscanf(const char *, const char *, ...);
FILE *tmpfile(void);
char *tmpnam(char *);
int ungetc(int, FILE *);
int vfprintf(FILE *, const char *, va_list);
int vprintf(const char *, va_list);
int vsnprintf(char *, size_t, const char *, va_list);
int vsprintf(char *, const char *, va_list);
int vfscanf(FILE *restrict stream, const char *restrict format, va_list arg);
int vscanf(const char *restrict, va_list);
int vsscanf(const char *restrict s, const char *restrict format, va_list arg);

#ifdef _POSIX_SOURCE
char *ctermid(char *);
FILE *fdopen(int, const char *);
int fileno(FILE *);
void flockfile(FILE *);
int ftrylockfile(FILE *);
void funlockfile(FILE *);
int getc_unlocked(FILE *);
int getchar_unlocked(void);
int getw(FILE *);
int pclose(FILE *);
FILE *popen(const char *, const char *);
int putc_unlocked(int, FILE *);
int putchar_unlocked(int);
int putw(int, FILE *);
char *tempnam(const char *, const char *);
#endif


#define BUFSIZ 1024
#define EOF (-1)
#define FILENAME_MAX 1024
#define FOPEN_MAX 16
#define L_tmpname 1024

#ifndef NULL
#define NULL ((void *)0)
#endif

#define TMP_MAX 16384
#define _IOFBF 0
#define _IOLBF 1
#define _IONBF 2
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2

#endif
