#ifndef _SETJMP_H_
#define _SETJMP_H_

#define setjmp(e)  0

typedef int jmp_buf[48];

void longjmp(jmp_buf, int);

#endif
