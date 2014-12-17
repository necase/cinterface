#ifndef _SIGNAL_H_
#define _SIGNAL_H_

/* Implementation detail: sig_atomic_t is signed */

#if !defined __CPP_INT_BITS || !defined __CPP_LONG_BITS \
		|| !defined __CPP_LONGLONG_BITS || !defined __CPP_CHAR_BITS \
		|| !defined __CPP_SHORT_BITS || !defined __CPP_ATOMIC_BITS
	#error Missing macro definitions detected
#endif

#if __CPP_ATOMIC_BITS == __CPP_CHAR_BITS
typedef signed char sig_atomic_t;
#elif __CPP_ATOMIC_BITS == __CPP_INT_BITS
typedef int sig_atomic_t;
#elif __CPP_ATOMIC_BITS == __CPP_LONG_BITS
typedef long sig_atomic_t;
#elif __CPP_ATOMIC_BITS == __CPP_SHORT_BITS
typedef short sig_atomic_t;
#elif __CPP_ATOMIC_BITS == __CPP_LONGLONG_BITS
typedef long long sig_atomic_t;
#else
#error Invalid size for sig_atomic_t
#endif

void (*signal(int, void (*)(int)))(int);
int raise(int);

#define SIGABRT 0
#define SIGFPE 1
#define SIGILL 2
#define SIGINT 3
#define SIGSEGV 4
#define SIGTERM 5
#define SIG_DFL (void (*)(int))0
#define SIG_IGN (void (*)(int))0
#define SIG_ERR (void (*)(int))0

#endif
