#ifndef _FENV_H_
#define _FENV_H_

typedef struct fenv_t fenv_t;
typedef struct fexcept_t fexcept_t;

int feclearexcept(int);
int fegetenv(fenv_t *);
int fegetexceptflag(fexcept_t *, int);
int fegetround(void);
int feholdexcept(fenv_t *);
int feraiseexcept(int);
int fesetexceptflag(const fexcept_t *, int);
int fesetenv(const fenv_t *);
int fesetround(int);
int fetestexcept(int);
int feupdateenv(const fenv_t *);

#define FE_ALL_EXCEPT 0

#define FE_TONEAREST 0
#define FE_DOWNWARD 4
#define FE_UPWARD 8
#define FE_TOWARDZERO 12

extern const fenv_t fe_dfl_env;
#define FE_DFL_ENV fe_dfl_env

/* The standard guarantees this header provides access to
* #pragma STDC FENV_ACCESS (on or off)
*/

#endif
