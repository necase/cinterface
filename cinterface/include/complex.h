#ifndef _COMPLEX_H_
#define _COMPLEX_H_

#define complex _Complex

#define _Complex_I csqrtf(-1)
#define I _Complex_I

#define __CPP_DECLARE_GROUP(func) \
float func##f (float complex);  double func (double complex);  long double func##l (long double complex);

#define __CPP_DECLARE_COMPLEX_GROUP(func) \
float complex func##f (float complex);  double complex func (double complex);  long double complex func##l (long double complex);

__CPP_DECLARE_GROUP(creal)
__CPP_DECLARE_GROUP(cimag)
__CPP_DECLARE_GROUP(cabs)
__CPP_DECLARE_GROUP(carg)
__CPP_DECLARE_COMPLEX_GROUP(conj)
__CPP_DECLARE_GROUP(cproj)
__CPP_DECLARE_COMPLEX_GROUP(cexp)
__CPP_DECLARE_COMPLEX_GROUP(clog)
__CPP_DECLARE_COMPLEX_GROUP(cpow)
__CPP_DECLARE_COMPLEX_GROUP(csqrt)
__CPP_DECLARE_COMPLEX_GROUP(csin)
__CPP_DECLARE_COMPLEX_GROUP(ccos)
__CPP_DECLARE_COMPLEX_GROUP(ctan)
__CPP_DECLARE_COMPLEX_GROUP(casin)
__CPP_DECLARE_COMPLEX_GROUP(cacos)
__CPP_DECLARE_COMPLEX_GROUP(catan)
__CPP_DECLARE_COMPLEX_GROUP(csinh)
__CPP_DECLARE_COMPLEX_GROUP(ccosh)
__CPP_DECLARE_COMPLEX_GROUP(ctanh)
__CPP_DECLARE_COMPLEX_GROUP(casinh)
__CPP_DECLARE_COMPLEX_GROUP(cacosh)
__CPP_DECLARE_COMPLEX_GROUP(catanh)

#endif
