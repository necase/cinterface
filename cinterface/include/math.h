#ifndef _MATH_H_
#define _MATH_H_

/* Assume FLT_EVAL_METHOD from float.h is 0 */
typedef float float_t;
typedef double double_t;


double acos(double);
float acosf(float);
long double acosl(long double);
double asin(double);
float asinf(float);
long double asinl(long double);
double atan(double);
float atanf(float);
long double atanl(long double);
double atan2(double, double);
float atan2f(float, float);
long double atan2l(long double, long double);
double cos(double);
float cosf(float);
long double cosl(long double);
double sin(double);
float sinf(float);
long double sinl(long double);
double tan(double);
float tanf(float);
long double tanl(long double);
double acosh(double);
float acoshf(float);
long double acoshl(long double);
double asinh(double);
float asinhf(float);
long double asinhl(long double);
double atanh(double);
float atanhf(float);
long double atanhl(long double);
double cosh(double);
float coshf(float);
long double coshl(long double);
double sinh(double);
float sinhf(float);
long double sinhl(long double);
double tanh(double);
float tanhf(float);
long double tanhl(long double);
double exp(double);
float expf(float);
long double expl(long double);
double exp2(double);
float exp2f(float);
long double exp2l(long double);
double expm1(double);
float expm1f(float);
long double expm1l(long double);
double frexp(double, int *);
float frexpf(float, int *);
long double frexpl(long double, int *);
int ilogb(double);
int ilogbf(float);
int ilogbl(long double);
double ldexp(double, int);
float ldexpf(float, int);
long double ldexpl(long double, int);
double log(double);
float logf(float);
long double logl(long double);
double log10(double);
float log10f(float);
long double log10l(long double);
double log1p(double);
float log1pf(float);
long double log1pl(long double);
double log2(double);
float log2f(float);
long double log2l(long double);
double logb(double);
float logbf(float);
long double logbl(long double);
double modf(double, double *);
float modff(float, float *);
long double modfl(long double, long double *);
double scalbn(double, int);
float scalbnf(float, int);
long double scalbnl(long double, int);
double scalbln(double, long int);
float scalblnf(float, long int);
long double scalblnl(long double, long int);
double cbrt(double);
float cbrtf(float);
long double cbrtl(long double);
double fabs(double);
float fabsf(float);
long double fabsl(long double);
double hypot(double, double);
float hypotf(float, float);
long double hypotl(long double, long double);
double pow(double, double);
float powf(float, float);
long double powl(long double, long double);
double sqrt(double);
float sqrtf(float);
long double sqrtl(long double);
double erf(double);
float erff(float);
long double erfl(long double);
double erfc(double);
float erfcf(float);
long double erfcl(long double);
double lgamma(double);
float lgammaf(float);
long double lgammal(long double);
double tgamma(double);
float tgammaf(float);
long double tgammal(long double);
double ceil(double);
float ceilf(float);
long double ceill(long double);
double floor(double);
float floorf(float);
long double floorl(long double);
double nearbyint(double);
float nearbyintf(float);
long double nearbyintl(long double);
double rint(double);
float rintf(float);
long double rintl(long double);
long int lrint(double);
long int lrintf(float);
long int lrintl(long double);
long long int llrint(double);
long long int llrintf(float);
long long int llrintl(long double);
double round(double);
float roundf(float);
long double roundl(long double);
long int lround(double);
long int lroundf(float);
long int lroundl(long double);
long long int llround(double);
long long int llroundf(float);
long long int llroundl(long double);
double trunc(double);
float truncf(float);
long double truncl(long double);
double fmod(double, double);
float fmodf(float, float);
long double fmodl(long double, long double);
double remainder(double, double);
float remainderf(float, float);
long double remainderl(long double, long double);
double remquo(double, double, int *);
float remquof(float, float, int *);
long double remquol(long double, long double, int *);
double copysign(double, double);
float copysignf(float, float);
long double copysignl(long double, long double);
double nan(const char *);
float nanf(const char *);
long double nanl(const char *);
double nextafter(double, double);
float nextafterf(float, float);
long double nextafterl(long double, long double);
double nexttoward(double, long double);
float nexttowardf(float, long double);
long double nexttowardl(long double, long double);
double fdim(double, double);
float fdimf(float, float);
long double fdiml(long double, long double);
double fmax(double, double);
float fmaxf(float, float);
long double fmaxl(long double, long double);
double fmin(double, double);
float fminf(float, float);
long double fminl(long double, long double);
double fma(double, double, double);
float fmaf(float, float, float);
long double fmal(long double, long double, long double);



#define isfinite(x) ((x) < 1e5000 && (x) > -1e5000 ? 1 : 0)
#define isinf(x) ((x) == 1e5000 || (x) == -1e5000 ? 1 : 0)
#define isnan(x) ((x) != (x))

/* This isnormal gives wrong answers for denormal numbers
* (for a number < machine epsilon at 1.0)
*/
#define isnormal(x) isfinite(x)

/* This signbit gives wrong answers for NaNs and infinities */
#define signbit(x) ((x) < 0)
#define isgreater(x, y) (!isnan(x) && !isnan(y) && (x > y) )
#define isgreaterequal(x, y) (!isnan(x) && !isnan(y) && (x >= y) )
#define isless(x, y) (!isnan(x) && !isnan(y) && (x < y) )
#define islessequal(x, y) (!isnan(x) && !isnan(y) && (x <= y) )
#define islessgreater(x, y) (!isnan(x) && !isnan(y) && (x < y || x > y) )
#define isunordered(x, y) (isnan(x) || isnan(y) )


#define INFINITY 1e5000f
#define NAN nanf("")
#define HUGE_VAL 1e5000
#define HUGE_VALF 1e5000f
#define HUGE_VALL 1e5000L

#define MATH_ERRNO 1
#define MATH_ERREXCEPT 2
#define math_errhandling 1

/* The standard guarantees access to
* #pragma STDC FP_CONTRACT {on|off}
* when this file is included
*/

#define FP_ILOGB0 (-1)
#define FP_ILOGBNAN (-1)


#define FP_INFINITE 0
#define FP_NAN 1
#define FP_ZERO 2
#define FP_SUBNORMAL 3
#define FP_NORMAL 4

#define fpclassify(x) (!isfinite(x) ? FP_INFINITE : isnan(x) ? FP_NAN : x == 0 ? FP_ZERO : isnormal(x) ? FP_NORMAL : FP_SUBNORMAL)


#endif
