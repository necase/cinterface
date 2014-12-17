#ifndef _STDARG_H_
#define _STDARG_H_

#define va_start(x,y)
#define va_arg(x,y) *(y *)(x)
#define va_end(x)
#define va_copy(x,y) memcpy(x,y,1)

#ifndef __CPP_VA_LIST_DEFINED
#define __CPP_VA_LIST_DEFINED
typedef void * va_list;
#endif

#endif
