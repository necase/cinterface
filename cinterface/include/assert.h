
#undef assert

#ifndef NDEBUG
void abort(void);
int printf(const char *, ...);

#define assert(x) \
((void) ((x) ? 0 : ((void)printf("Failed assertion '%s' at line %u of file %s.\n", #x, __LINE__, __FILE__), abort() ) ) )
#else
#define assert(x) (0)
#endif
