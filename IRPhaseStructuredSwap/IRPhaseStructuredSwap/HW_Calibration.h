#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "Util.h"
#include "CalcDate.h"
#include <crtdbg.h>


#ifndef DLLEXPORT(A)
#ifdef WIN32
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif _WIN64
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif __linux__
#define DLLEXPORT(A) extern "C" __declspec
#elif __hpux
#define DLLEXPORT(A) extern "C" __declspec
#elif __unix__
#define DLLEXPORT(A) extern "C" __declspec
#else 
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#endif
#endif

#define NTAB                32
#define Notional_Amount     10000.0
#define Param1_Min          0.002         //Kappa최소값
#define Param1_Max          0.1          //Kappa최대값
#define Interval1           0.002         //Kappa간격
#define Param2_Min          0.001         //Vol최소값
#define Param2_Max          0.04          //Vol최대값
#define Interval2           0.0002          //Vol간격

#define Tiny_Value                1.0e-7        // 변동성 최소값
#define Max_Value                1.0            // 변동성 최대값

// 2-factor 모형의 Fixed Payer Swaption 가격 계산
double _stdcall Swaption2F(
    double NA,			// 액면금액
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    double* Vol12,
    long nVol,			// 변동성 구간 개수
    double rho,			// 상관계수
    double StrikeRate,	// 고정금리(지급부분)
    long MaturityDate,	// 옵션 만기일까지 일수
    long* Dates,			// 지급일: 계산일로부터 각 중간지급일까지의 일수
    double* termdates,      // 지급일까지 t 로 환산
    double* termC,
    long nDates,			// 지급 회수(계산일 이후 남은 회수)
    double* PT,
    double P0_at_OptMaturity,
    long nQuad,                 //Gauss Normal Quadrature 개수
    double* x,                  //Gauss Normal Quadrature의 x값
    double* w                   //Gauss Normal Quadrature의 y값 비율
);

long Number_Of_Payment(double T_OptionMaturity, double T_SwapMaturity, double PayFreqOfMonth)
{
    double dT = (T_SwapMaturity - T_OptionMaturity + 0.00001);
    double Num_AnnPayment = 12.0 / PayFreqOfMonth;
    long N;
    N = (long)(dT * Num_AnnPayment + 0.01);
    return N;
}

long PaymentDatesMapping(double T_SwapMaturity, double FreqMonth, long* TempDatesArray, long NDates)
{
    long i;
    long DayDiff = (long)(FreqMonth / 12.0 * 365.0);

    TempDatesArray[NDates - 1] = (long)(365.0 * T_SwapMaturity + 0.5);
    for (i = NDates - 2; i >= 0; i--)
    {
        TempDatesArray[i] = TempDatesArray[i + 1] - DayDiff;
    }
    return NDates;
}

double Interpolate_Linear_Point(double* x, double* fx, long nx, double targetx, long& Point)
{
    long i;
    double result = 0.0;

    if (nx == 1 || targetx == x[0])
        return fx[0];
    else if (targetx == x[nx - 1])
        return fx[nx - 1];


    if (targetx < x[0]) return fx[0];
    else if (targetx > x[nx - 1]) return fx[nx - 1];
    else
    {
        for (i = max(1, Point); i < nx; i++)
        {
            if (targetx < x[i])
            {
                result = (fx[i] - fx[i - 1]) / (x[i] - x[i - 1]) * (targetx - x[i - 1]) + fx[i - 1];
                Point = i - 1;
                break;
            }
        }
        return result;
    }
}

double FSR(
    double* Term,
    double* Rate,
    long NTerm,
    double T_Option,
    double Tenor,
    double FreqMonth
)
{
    long i;
    long Point = 0;
    double r, t;
    double Swap_Rate;

    long ndates = Number_Of_Payment(T_Option, T_Option + Tenor, FreqMonth);
    long* dates = (long*)malloc(sizeof(long) * (ndates));
    ndates = PaymentDatesMapping(T_Option + Tenor, FreqMonth, dates, ndates);

    double* PT = (double*)malloc(sizeof(double) * (ndates + 1));
    t = T_Option;
    r = Interpolate_Linear_Point(Term, Rate, NTerm, t, Point);
    PT[0] = exp(-r * t); // 옵션만기시점
    for (i = 1; i < ndates + 1; i++)
    {
        t = (double)(dates[i - 1] / 365.0);
        r = Interpolate_Linear_Point(Term, Rate, NTerm, t, Point);
        PT[i] = exp(-r * t);
    }

    double a, b, dt;
    a = PT[0] - PT[ndates];
    b = 0.0;
    for (i = 0; i < ndates; i++)
    {
        if (i == 0)
            dt = (double)dates[0] / 365.0 - T_Option;
        else
            dt = ((double)(dates[i] - dates[i - 1])) / 365.0;
        b += dt * PT[i + 1];
    }
    Swap_Rate = a / b;


    if (dates) free(dates);
    if (PT) free(PT);
    return Swap_Rate;
}


// 적분 계산 공통함수
// I(t) = Int_0^t sigma(s)^2 A exp(ks) ds
double Integ(
    double t,
    double A,
    double kappa,
    double* tVol,
    double* Vol,
    long nVol
)
{
    long i;
    long NodeNum = 10;
    long Point = 0;
    double ds = t / (double)NodeNum;
    double s;
    double value = 0.0;
    double sigma;
    if (nVol == 1) return A * Vol[0] * Vol[0] / (kappa) * (exp(kappa * t) - 1.0);
    for (i = 0; i < NodeNum; i++)
    {
        s = (double)(i + 1) * ds;
        sigma = Interpolate_Linear_Point(tVol, Vol, nVol, s, Point);
        value += sigma * sigma * A * exp(kappa * s) * ds;
    }
    return value;
}



// 적분 계산 공통함수
// I(t) = Int_0^t sigma(s)^2 A exp(Bs) ds
/*
double I(
    double t,
    double A,
    double B,
    double* tVol,		// 변동성 구간 종점
    double* Vol,			// 구간 변동성
    long nVol 			// 변동성 구간 개수
)
{
    long i, N = 0;
    double value = 0;

    if (t <= tVol[0]) N = 0;
    else if (t >= tVol[nVol - 1]) N = nVol - 1;
    else {
        for (i = 0; i < nVol - 1; i++) {
            if (t >= tVol[i] && t < tVol[i + 1]) {
                N = i + 1;
                break;
            }
        }
    }

    if (B == 0.0) {
        if (N == 0) value += Vol[0] * Vol[0] * A * t;
        else {
            for (i = 0; i < N; i++) {
                if (i == 0) value += Vol[0] * Vol[0] * A * tVol[0];
                else value += Vol[i] * Vol[i] * A * (tVol[i] - tVol[i - 1]);
            }

            value += Vol[N] * Vol[N] * A * (t - tVol[N - 1]);
        }
    }
    else {
        if (N == 0) value += Vol[0] * Vol[0] * A / B * (exp(B * t) - 1.0);
        else {
            for (i = 0; i < N; i++) {
                if (i == 0) value += Vol[0] * Vol[0] * A / B * (exp(B * tVol[0]) - 1.0);
                else value += Vol[i] * Vol[i] * A / B * (exp(B * tVol[i]) - exp(B * tVol[i - 1]));
            }

            value += Vol[N] * Vol[N] * A / B * (exp(B * t) - exp(B * tVol[N - 1]));
        }
    }

    return value;
}*/

double B(double s, double t, double kappa)
{
    return (1.0 - exp(-kappa * (t - s))) / kappa;
}

// 1-factor 모형의 Fixed Payer Swaption 가격 계산
double HW_Swaption(
    double NA,            // 액면금액
    double kappa,        // 회귀속도 
    double* tVol,        // 변동성 구간 종점
    double* Vol,            // 구간 변동성
    long nVol,            // 변동성 구간 개수
    double* t,            // 할인채 만기
    double* r,            // 할인채 가격
    long nr,                // 할인채 개수
    double StrikeRate,    // 고정금리(지급부분)
    long MaturityDate,    // 옵션 만기일까지 일수
    long* Dates,            // 지급일: 계산일로부터 각 중간지급일까지의 일수
    long nDates            // 지급 회수(계산일 이후 남은 회수)
)
{
    long i;
    double T0, PrevT, T, deltaT;
    double* PT = (double*)malloc(sizeof(double) * (nDates + 1));
    double VT0, G, H;
    double d1, d2;
    double value;

    if (kappa < -0.002) kappa = -0.002;

    for (i = 0; i < nVol; i++) {
        if (Vol[i] < 0.0) Vol[i] = -Vol[i];
        if (Vol[i] < Tiny_Value) Vol[i] = Tiny_Value;
    }

    T0 = (double)MaturityDate / 365.0;
    PT[0] = Calc_Discount_Factor(t, r, nr, T0);

    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        PT[i + 1] = Calc_Discount_Factor(t, r, nr, T);
    }

    VT0 = exp(-2.0 * kappa * T0) * Integ(T0, 1.0, 2.0 * kappa, tVol, Vol, nVol);

    G = PT[nDates];
    PrevT = T0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;
        G += StrikeRate * deltaT * PT[i + 1];
        PrevT = T;
    }
    G /= PT[0];

    H = PT[nDates] * B(T0, (double)Dates[nDates - 1] / 365.0, kappa);
    PrevT = T0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;
        H += StrikeRate * deltaT * PT[i + 1] * B(T0, T, kappa);
        PrevT = T;
    }
    H /= G * PT[0];

    d1 = -log(G) / (H * sqrt(VT0)) + 0.5 * H * sqrt(VT0);
    d2 = -log(G) / (H * sqrt(VT0)) - 0.5 * H * sqrt(VT0);

    value = PT[0] * (CDF_N(d1) - G * CDF_N(d2));

    if (PT) free(PT);

    return NA * value;
}

// 1-factor 모형의 Fixed Payer Swaption 가격 빠른 계산
double HW_Swaption(
    double NA,              // 액면금액
    double kappa,           // 회귀속도 
    double* tVol,           // 변동성 구간 종점
    double* Vol,            // 구간 변동성
    long nVol,              // 변동성 구간 개수
    double* t,              // 할인채 만기
    double* r,              // 할인채 가격
    long nr,                // 할인채 개수
    double StrikeRate,      // 고정금리(지급부분)
    long MaturityDate,      // 옵션 만기일까지 일수
    long* Dates,            // 지급일: 계산일로부터 각 쿠폰지급일까지의 일수
    long nDates,            // 지급 회수(계산일 이후 남은 회수
    double* PT              // P[0] = P(0, TOpt), P[N] = P(0, TSwp), Shape = nDates + 1
)
{
    long i;
    double T0, PrevT, T, deltaT;

    double VT0, G, H;
    double d1, d2;
    double value;

    if (kappa < -0.002) kappa = -0.002;

    for (i = 0; i < nVol; i++) 
    {
        if (Vol[i] < 0.0) Vol[i] = -Vol[i];
        if (Vol[i] < Tiny_Value) Vol[i] = Tiny_Value;
    }

    T0 = (double)MaturityDate / 365.0;
    VT0 = exp(-2.0 * kappa * T0) * Integ(T0, 1.0, 2.0 * kappa, tVol, Vol, nVol);
    G = PT[nDates];
    PrevT = T0;
    for (i = 0; i < nDates; i++) 
    {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;
        G += StrikeRate * deltaT * PT[i + 1];
        PrevT = T;
    }
    G /= PT[0];

    H = PT[nDates] * B(T0, (double)Dates[nDates - 1] / 365.0, kappa);
    PrevT = T0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;
        H += StrikeRate * deltaT * PT[i + 1] * B(T0, T, kappa);
        PrevT = T;
    }
    H /= G * PT[0];

    d1 = -log(G) / (H * sqrt(VT0)) + 0.5 * H * sqrt(VT0);
    d2 = -log(G) / (H * sqrt(VT0)) - 0.5 * H * sqrt(VT0);

    value = PT[0] * (CDF_N(d1) - G * CDF_N(d2));
    return NA * value;
}

// 1-factor 모형의 Cap 가격 계산
double HW_Cap(
    double NA,            // 액면금액
    double kappa,        // 회귀속도 
    double* tVol,        // 변동성 구간 종점
    double* Vol,            // 구간 변동성
    long nVol,            // 변동성 구간 개수
    double* t,            // 할인채 만기
    double* r,            // 할인채 가격
    long nr,                // 할인채 개수
    double StrikeRate,    // 행사금리
    long* Dates,            // 지급일: 계산일로부터 각 지급일까지의 일수
    long nDates            // 지급 회수(계산일 이후 남은 회수)
)
{
    long i;
    double d1, d2, PrevT, T, deltaT;
    double PrevDisc, Disc;
    double BP, u;
    double value;

    if (kappa < -0.002) kappa = -0.002;

    for (i = 0; i < nVol; i++) {
        if (Vol[i] < 0.0) Vol[i] = -Vol[i];
        if (Vol[i] < Tiny_Value) Vol[i] = Tiny_Value;
    }

    PrevT = 0.0;
    value = 0.0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;

        PrevDisc = Calc_Discount_Factor(t, r, nr, PrevT);
        Disc = Calc_Discount_Factor(t, r, nr, T);

        BP = B(PrevT, T, kappa);
        u = BP * BP * exp(-2.0 * kappa * PrevT) * Integ(PrevT, 1.0, 2.0 * kappa, tVol, Vol, nVol);

        if (i == 0) {
            if (PrevDisc > (1.0 + StrikeRate * deltaT) * Disc) value = PrevDisc - (1.0 + StrikeRate * deltaT) * Disc;
        }
        else {
            d1 = -log((1.0 + StrikeRate * deltaT) * Disc / PrevDisc) / sqrt(u) + 0.5 * sqrt(u);
            d2 = d1 - sqrt(u);

            value += PrevDisc * CDF_N(d1) - (1.0 + StrikeRate * deltaT) * Disc * CDF_N(d2);
        }

        PrevT = T;
    }

    return NA * value;
}

// 1-factor 모형의 Cap 가격 계산
double HW_Cap(
    double NA,            // 액면금액
    double kappa,        // 회귀속도 
    double* tVol,        // 변동성 구간 종점
    double* Vol,            // 구간 변동성
    long nVol,            // 변동성 구간 개수
    double* t,            // 할인채 만기
    double* r,            // 할인채 가격
    long nr,                // 할인채 개수
    double StrikeRate,    // 행사금리
    long* Dates,            // 지급일: 계산일로부터 각 지급일까지의 일수
    long nDates,            // 지급 회수(계산일 이후 남은 회수)
    double* PT
)
{
    long i;
    double d1, d2, PrevT, T, deltaT;
    double PrevDisc, Disc;
    double BP, u;
    double value;

    if (kappa < -0.002) kappa = -0.002;

    for (i = 0; i < nVol; i++) {
        if (Vol[i] < 0.0) Vol[i] = -Vol[i];
        if (Vol[i] < Tiny_Value) Vol[i] = Tiny_Value;
    }

    PrevT = 0.0;
    value = 0.0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        deltaT = T - PrevT;

        PrevDisc = PT[i];
        Disc = PT[i + 1];

        BP = B(PrevT, T, kappa);
        u = BP * BP * exp(-2.0 * kappa * PrevT) * Integ(PrevT, 1.0, 2.0 * kappa, tVol, Vol, nVol);

        if (i == 0) {
            if (PrevDisc > (1.0 + StrikeRate * deltaT) * Disc) value = PrevDisc - (1.0 + StrikeRate * deltaT) * Disc;
        }
        else {
            d1 = -log((1.0 + StrikeRate * deltaT) * Disc / PrevDisc) / sqrt(u) + 0.5 * sqrt(u);
            d2 = d1 - sqrt(u);

            value += PrevDisc * CDF_N(d1) - (1.0 + StrikeRate * deltaT) * Disc * CDF_N(d2);
        }

        PrevT = T;
    }

    return NA * value;
}


double BS_Swaption(
    double NA,
    double Vol,
    double StrikePrice,
    double* Term,
    double* Rate,
    long NTerm,
    double T_Option,
    double Tenor,
    double FreqMonth,
    long VolFlag
)
{
    long i;
    long NDates;
    double dT = FreqMonth / 12.0;
    double Annuity;
    double ForwardSwapRate;
    double d1, d2;
    double Ti;

    ForwardSwapRate = FSR(Term, Rate, NTerm, T_Option, Tenor, FreqMonth);

    NDates = Number_Of_Payment(T_Option, T_Option + Tenor, FreqMonth);
    Annuity = 0.0;
    for (i = 0; i < NDates; i++)
    {
        Ti = T_Option + Tenor - (double)i * dT;
        Annuity += dT * Calc_Discount_Factor(Term, Rate, NTerm, Ti);
    }
    double value;

    if (VolFlag == 0)
    {
        d1 = (log(ForwardSwapRate / StrikePrice) + 0.5 * Vol * Vol * T_Option) / (Vol * sqrt(T_Option));
        d2 = d1 - Vol * sqrt(T_Option);

        value = Annuity * (ForwardSwapRate * CDF_N(d1) - StrikePrice * CDF_N(d2));
    }
    else
    {
        d1 = (ForwardSwapRate - StrikePrice) / (Vol * sqrt(T_Option));

        value = Annuity * ((ForwardSwapRate - StrikePrice) * CDF_N(d1) + Vol * sqrt(T_Option) * (exp(-d1 * d1 / 2.0) / 2.506628274631));
    }
    return NA * value;
}

double BS_Cap(
    double NA,            // 액면금액
    double Vol,            // 변동성
    double* t,            // 할인채 만기
    double* r,            // 할인채 가격
    long nr,                // 할인채 개수
    double StrikeRate,    // 행사금리
    double Swaption_Mat,        // 입력: 각 스왑션(캡)의 만기(연환산) 
    double Swap_Mat,            // 입력: 각 스왑션(캡)의 기초자산(스왑) 만기(연환산)
    double Swap_Period,        // 입력: 각 스왑션의 기초자산인 스왑(캡) 지급 주기(월환산)
    long VolFlag
)
{
    long i;
    double d1, d2, PrevT, T, delta;
    double PrevDisc, Disc;
    double F, value;
    long nDates;
    long* Dates;

    nDates = Number_Of_Payment(Swaption_Mat, Swaption_Mat + Swap_Mat, Swap_Period);
    Dates = (long*)malloc(sizeof(long) * (nDates));
    PaymentDatesMapping(Swaption_Mat + Swap_Mat, Swap_Period, Dates, nDates);

    PrevT = 0.0;
    value = 0.0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        delta = T - PrevT;

        PrevDisc = Calc_Discount_Factor(t, r, nr, PrevT);
        Disc = Calc_Discount_Factor(t, r, nr, T);

        F = (PrevDisc / Disc - 1.0) / delta;        // 선도금리

        if (i == 0) {    // 첫번째 지급일 
            if (F > StrikeRate) value = delta * Disc * (F - StrikeRate);
        }
        else {
            if (VolFlag == 0)
            {
                d1 = (log(F / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
                d2 = d1 - Vol * sqrt(PrevT);

                value += delta * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2));
            }
            else
            {
                d1 = (F - StrikeRate) / (Vol * sqrt(PrevT));
                value += delta * Disc * ((F - StrikeRate) * CDF_N(d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.0) / 2.50662874631);
            }
        }

        PrevT = T;
    }
    if (Dates) free(Dates);

    return NA * value;
}

void Calc_Error_Array(
    long nSwapMaturity,
    double* HW_Vol,
    double* tHW_Vol,
    long nHW_Vol,
    double* temp_vol,

    double* t,
    double* r,
    long nr,

    double* Swaption_Mat,
    double* Swap_Mat,
    double* Swap_Period,
    double* Strike_Rate,
    double* Swaption_Price,

    long Number_KappaRange,
    double* KappaRange,
    long Number_VolRange,
    double* VolRange,
    double** ErrorArray
)
{
    long i, j, k;
    long p, q;
    long nodet;
    long nDates;
    long* dates;
    double kappa;
    double Price;
    double* PT;
    long MaturityDate;

    k = 0;
    for (j = 0; j < nSwapMaturity; j++)
    {
        // Swaption의 경우 NodeT계산
        if (Swaption_Mat[k] > 0.0)
        {
            for (nodet = 0; nodet < nHW_Vol - 1; nodet++) {
                if (Swaption_Mat[k] >= tHW_Vol[nodet] && Swaption_Mat[k] < tHW_Vol[nodet + 1]) {
                    break;
                }
            }
        }
        else // Cap의 경우 NodeT계산
        {
            for (nodet = 0; nodet < nHW_Vol - 1; nodet++) {
                if (Swap_Mat[k] >= tHW_Vol[nodet] && Swap_Mat[k] < tHW_Vol[nodet + 1]) {
                    break;
                }
            }
        }

        nDates = Number_Of_Payment(Swaption_Mat[k], Swaption_Mat[k] + Swap_Mat[k], Swap_Period[k]);
        dates = (long*)malloc(nDates * sizeof(long));
        PaymentDatesMapping(Swaption_Mat[k] + Swap_Mat[k], Swap_Period[k], dates, nDates);
        MaturityDate = (long)(Swaption_Mat[k] * 365.0);

        PT = (double*)malloc(sizeof(double) * (nDates + 1));
        PT[0] = Calc_Discount_Factor(t, r, nr, (double)MaturityDate / 365.0);

        for (i = 0; i < nDates; i++) {
            PT[i + 1] = Calc_Discount_Factor(t, r, nr, (double)dates[i] / 365.0);
        }

        for (p = 0; p < nodet; p++) {
            temp_vol[p] = HW_Vol[p];
        }

        for (p = 0; p < Number_KappaRange; p++) {
            for (q = 0; q < Number_VolRange; q++) {
                kappa = KappaRange[p];
                temp_vol[nodet] = VolRange[q];
                if (Swaption_Mat[k] > 0.0) {
                    Price = HW_Swaption(Notional_Amount, kappa, tHW_Vol, temp_vol, nodet + 1, t, r, nr, Strike_Rate[k], MaturityDate, dates, nDates, PT);
                }
                else {
                    Price = HW_Cap(Notional_Amount, kappa, tHW_Vol, temp_vol, nodet + 1, t, r, nr, Strike_Rate[k], dates, nDates);
                }
                ErrorArray[p][q] = ErrorArray[p][q] + fabs(Price - Swaption_Price[k]);
            }
        }


        k += 1;
        free(dates);
        free(PT);
    }
}

double OptimizeHWCap(
    long nCap,
    double* t,
    double* r,
    long nr,
    long CaliFlag,
    double* Cap_Mat,
    double* Cap_Strike,
    double* Cap_Tenor,
    double* Cap_Vol,
    double* Cap_Price,
    long na,
    long* ia,
    double* a,
    double* tHW_Vol,
    double* HW_Vol,
    long nHW_Vol,
    long* Cap_ErrorShape,
    double*** Distance_Array,
    long HW_Kappa_Flag,
    double Fixed_Kappa
)
{
    long i, j, p, q;
    long N, M;
    long N2, M2;

    double* Params1_Array;
    double* Params2_Array;

    double* Params1_Array2;
    double* Params2_Array2;
    double** Distance_Array2;

    double Param1_Min2;
    double Param1_Max2;
    double Param2_Min2;
    double Param2_Max2;

    double minvalue;
    double kappa;
    long break_flag;


    double* Swaption_Mat = (double*)malloc(sizeof(double) * nCap);          // 할당 1
    for (i = 0; i < nCap; i++)
        Swaption_Mat[i] = 0.0;

    for (i = 0; i < nCap; i++)
        tHW_Vol[i] = Cap_Mat[i];

    double* ResultKappa;
    double* temp_vol;
    long nSwapMaturity = 1;

    N = (long)((Param1_Max - Param1_Min) / Interval1) + 1;
    M = (long)((Param2_Max - Param2_Min) / Interval2) + 1;

    Params1_Array = (double*)malloc(sizeof(double) * N);                    // 할당 2
    Params2_Array = (double*)malloc(sizeof(double) * M);                    // 할당 3

    Cap_ErrorShape[0] = nCap;
    Cap_ErrorShape[1] = N;
    Cap_ErrorShape[2] = M;

    for (i = 0; i < nCap; i++) {
        Distance_Array[i] = (double**)malloc(sizeof(double*) * N);          // Result 할당부분
        for (j = 0; j < N; j++)
        {
            Distance_Array[i][j] = (double*)malloc(sizeof(double) * M);
        }
    }

    if (HW_Kappa_Flag != 1) {
        for (i = 0; i < N; i++)
            Params1_Array[i] = Param1_Min + (double)i * Interval1;
    }
    else {
        for (i = 0; i < N; i++)
            Params1_Array[i] = Fixed_Kappa;
    }

    for (i = 0; i < M; i++)
        Params2_Array[i] = Param2_Min + (double)i * Interval2;

    ResultKappa = (double*)calloc(nCap, sizeof(double));                    // 할당 4
    temp_vol = (double*)calloc(nCap, sizeof(double));                       // 할당 5

    for (i = 0; i < nCap; i++)
    {
        for (p = 0; p < N; p++)
            for (q = 0; q < M; q++)
                Distance_Array[i][p][q] = 0.0;

        Calc_Error_Array(nSwapMaturity, HW_Vol, tHW_Vol, nCap, temp_vol,
            t, r, nr, Swaption_Mat + i * nSwapMaturity, Cap_Mat + i * nSwapMaturity,
            Cap_Tenor + i * nSwapMaturity, Cap_Strike + i * nSwapMaturity, Cap_Price + i * nSwapMaturity, N, Params1_Array,
            M, Params2_Array, Distance_Array[i]);

        minvalue = Distance_Array[i][0][0];
        for (p = 1; p < N; p++)
            for (q = 1; q < M; q++)
                minvalue = min(minvalue, Distance_Array[i][p][q]);

        for (p = 0; p < N; p++) {
            break_flag = 0;
            for (q = 0; q < M; q++) {
                if (Distance_Array[i][p][q] == minvalue) {
                    break_flag = 1;
                    break;
                }
            }
            if (break_flag == 1)
                break;
        }

        Param1_Min2 = Params1_Array[max(0, p - 1)];
        Param1_Max2 = Params1_Array[min(N - 1, p + 1)];

        Param2_Min2 = Params2_Array[max(0, q - 1)];
        Param2_Max2 = Params2_Array[min(M - 1, q + 1)];

        N2 = (long)((Param1_Max2 - Param1_Min2) / (Interval1 / 10.0)) + 1;
        M2 = (long)((Param2_Max2 - Param2_Min2) / (Interval2 / 10.0)) + 1;

        Params1_Array2 = (double*)malloc(sizeof(double) * N2);                   // 반복문 내부 할당 1
        Params2_Array2 = (double*)malloc(sizeof(double) * M2);                   // 반복문 내부 할당 2

        Distance_Array2 = (double**)calloc(N2, sizeof(double*));                 // 반복문 내부 할당 3
        for (p = 0; p < N2; p++)
            Distance_Array2[p] = (double*)calloc(M2, sizeof(double));

        if (HW_Kappa_Flag != 1)
        {
            for (p = 0; p < N2; p++) {
                Params1_Array2[p] = Param1_Min2 + (double)p * Interval1 / 10.0;
            }
        }
        else
        {
            for (p = 0; p < N2; p++) {
                Params1_Array2[p] = Fixed_Kappa;
            }
        }

        for (p = 0; p < M2; p++) {
            Params2_Array2[p] = Param2_Min2 + (double)p * Interval2 / 10.0;
        }

        Calc_Error_Array(nSwapMaturity, HW_Vol, tHW_Vol, nCap, temp_vol,
            t, r, nr, Swaption_Mat + i * nSwapMaturity, Cap_Mat + i * nSwapMaturity,
            Cap_Tenor + i * nSwapMaturity, Cap_Strike + i * nSwapMaturity, Cap_Price + i * nSwapMaturity, N2, Params1_Array2,
            M2, Params2_Array2, Distance_Array2);

        minvalue = Distance_Array2[0][0];
        for (p = 1; p < N2; p++)
            for (q = 1; q < M2; q++)
                minvalue = min(minvalue, Distance_Array2[p][q]);

        for (p = 0; p < N2; p++)
        {
            break_flag = 0;
            for (q = 0; q < M2; q++)
            {
                if (Distance_Array2[p][q] == minvalue)
                {
                    break_flag = 1;
                    break;
                }
            }
            if (break_flag == 1)
                break;
        }

        ResultKappa[i] = Params1_Array2[p];
        HW_Vol[i] = Params2_Array2[q];

        free(Params1_Array2);
        free(Params2_Array2);
        for (p = 0; p < N2; p++)
        {
            free(Distance_Array2[p]);
        }
        free(Distance_Array2);

    }


    kappa = 0.0;
    for (i = 0; i < nCap; i++)
    {
        kappa += ResultKappa[i] / (double)nCap;
    }
    a[0] = kappa;

    free(Swaption_Mat);
    free(Params1_Array);
    free(Params2_Array);

    free(ResultKappa);
    free(temp_vol);
    return 1.0;
}

double OptimizeHWSwaption(
    long nSwaption,
    long nCap,
    long* Cap_ErrorShape,
    double*** Cap_ErrorArray,
    double* Cap_Mat,
    double* t,                    //
    double* r,                    // 입력: 무위험 금리 기간 구조
    long nr,                    //
    long CaliFlag,               // 0 Swaption Cap 둘다 1 Cap 2 Swaption
    double* Swaption_Mat,        // 입력: 각 스왑션(캡)의 만기(연환산) 
    double* Swap_Mat,            // 입력: 각 스왑션(캡)의 기초자산(스왑) 만기(연환산)
    double* Strike_Rate,        // 입력: 각 스왑션(캡)의 행사가격
    double* Swap_Period,        // 입력: 각 스왑션의 기초자산인 스왑(캡) 지급 주기(월환산)
    double* Swaption_Vol,        // 입력: 각 스왑션(캡)의 변동성
    double* Swaption_Price,
    long na,
    long* ia,
    double* a,
    double* tHW_Vol,            // 입력: HW 변동성 기간 구조 시점
    double* HW_Vol,            // 입력/결과: HW 변동성
    long nHW_Vol,                // 입력: HW 변동성 기간 구조 개수
    long HW_Kappa_Flag,
    double Fixed_Kappa
)
{
    long i, j, k, k2;
    long p, q;
    long N, M;
    long N2, M2;

    long nMaturity;
    long nOption;

    double* Params1_Array;
    double* Params2_Array;
    double** Distance_Array;

    double* Params1_Array2;
    double* Params2_Array2;
    double** Distance_Array2;

    double Param1_Min2;
    double Param1_Max2;
    double Param2_Min2;
    double Param2_Max2;

    double minvalue;
    double kappa;
    long break_flag;

    double* ResultKappa;
    double* temp_vol;

    if (CaliFlag == 1)
        nMaturity = nSwaption / nHW_Vol;
    else if (CaliFlag == 0)
        nMaturity = nSwaption / (nHW_Vol - nCap);

    nOption = nSwaption / nMaturity;

    N = (long)((Param1_Max - Param1_Min) / Interval1) + 1;
    M = (long)((Param2_Max - Param2_Min) / Interval2) + 1;

    Params1_Array = (double*)malloc(sizeof(double) * N);          // 할당 1
    Params2_Array = (double*)malloc(sizeof(double) * M);          // 할당 2

    Distance_Array = (double**)malloc(sizeof(double*) * N);       // 2차원 할당3
    for (i = 0; i < N; i++)
        Distance_Array[i] = (double*)malloc(sizeof(double) * M);
    if (HW_Kappa_Flag != 1)
    {
        for (i = 0; i < N; i++)
        {
            Params1_Array[i] = Param1_Min + (double)i * Interval1;
        }
    }
    else
    {
        for (i = 0; i < N; i++)
        {
            Params1_Array[i] = Fixed_Kappa;
        }
    }

    for (i = 0; i < M; i++)
        Params2_Array[i] = Param2_Min + (double)i * Interval2;

    ResultKappa = (double*)calloc(nHW_Vol, sizeof(double));     // 할당4
    temp_vol = (double*)calloc(nHW_Vol, sizeof(double));       // 할당5

    k = 0;
    k2 = 0;
    for (i = 0; i < nOption; i++)
    {

        for (p = 0; p < N; p++) {
            for (q = 0; q < M; q++) {
                Distance_Array[p][q] = 0.0;
            }
        }

        if (CaliFlag == 0)
        {
            for (j = 0; j < nCap; j++)
            {
                if (tHW_Vol[i] == Cap_Mat[j])
                {
                    for (p = 0; p < N; p++) {
                        for (q = 0; q < M; q++)
                            Distance_Array[p][q] = Cap_ErrorArray[j][p][q];
                    }
                    break;
                }
            }
        }

        Calc_Error_Array(nMaturity, HW_Vol, tHW_Vol, nOption, temp_vol,
            t, r, nr, Swaption_Mat + i * nMaturity, Swap_Mat + i * nMaturity,
            Swap_Period + i * nMaturity, Strike_Rate + i * nMaturity, Swaption_Price + i * nMaturity, N, Params1_Array,
            M, Params2_Array, Distance_Array);

        minvalue = Distance_Array[0][0];
        for (p = 1; p < N; p++)
            for (q = 1; q < M; q++)
                minvalue = min(minvalue, Distance_Array[p][q]);

        for (p = 0; p < N; p++) {
            break_flag = 0;
            for (q = 0; q < M; q++) {
                if (Distance_Array[p][q] == minvalue) {
                    break_flag = 1;
                    break;
                }
            }
            if (break_flag == 1)
                break;
        }

        Param1_Min2 = Params1_Array[max(0, p - 1)];
        Param1_Max2 = Params1_Array[min(N - 1, p + 1)];

        Param2_Min2 = Params2_Array[max(0, q - 1)];
        Param2_Max2 = Params2_Array[min(M - 1, q + 1)];

        N2 = (long)((Param1_Max2 - Param1_Min2) / (Interval1 / 10.0)) + 1;
        M2 = (long)((Param2_Max2 - Param2_Min2) / (Interval2 / 10.0)) + 1;

        Params1_Array2 = (double*)malloc(sizeof(double) * N2);                   // 반복문 내부 할당 1
        Params2_Array2 = (double*)malloc(sizeof(double) * M2);                   // 반복문 내부 할당 2

        Distance_Array2 = (double**)calloc(N2, sizeof(double*));                 // 반복문 내부 할당 3 (2차원)
        for (p = 0; p < N2; p++)
            Distance_Array2[p] = (double*)calloc(M2, sizeof(double));

        if (HW_Kappa_Flag != 1)
        {
            for (p = 0; p < N2; p++) {
                Params1_Array2[p] = Param1_Min2 + (double)p * Interval1 / 10.0;
            }
        }
        else
        {
            for (p = 0; p < N2; p++) {
                Params1_Array2[p] = Fixed_Kappa;
            }
        }

        for (p = 0; p < M2; p++) {
            Params2_Array2[p] = Param2_Min2 + (double)p * Interval2 / 10.0;
        }

        Calc_Error_Array(nMaturity, HW_Vol, tHW_Vol, nOption, temp_vol,
            t, r, nr, Swaption_Mat + i * nMaturity, Swap_Mat + i * nMaturity,
            Swap_Period + i * nMaturity, Strike_Rate + i * nMaturity, Swaption_Price + i * nMaturity, N2, Params1_Array2,
            M2, Params2_Array2, Distance_Array2);

        minvalue = Distance_Array2[0][0];
        for (p = 1; p < N2; p++)
            for (q = 1; q < M2; q++)
                minvalue = min(minvalue, Distance_Array2[p][q]);

        for (p = 0; p < N2; p++)
        {
            break_flag = 0;
            for (q = 0; q < M2; q++)
            {
                if (Distance_Array2[p][q] == minvalue)
                {
                    break_flag = 1;
                    break;
                }
            }
            if (break_flag == 1)
                break;
        }

        ResultKappa[i] = Params1_Array2[p];
        HW_Vol[i] = Params2_Array2[q];
        free(Params1_Array2);               // 반복문 내부 할당 해제 1
        free(Params2_Array2);               // 반복문 내부 할당 해제 2
        for (p = 0; p < N2; p++)
        {
            free(Distance_Array2[p]);
        }
        free(Distance_Array2);              // 반복문 내부 할당 해제 3 (2차원)

    }

    kappa = 0.0;
    for (i = 0; i < nOption; i++)
    {
        kappa += ResultKappa[i] / (double)nOption;
    }
    a[0] = kappa;

    free(Params1_Array);
    free(Params2_Array);
    for (i = 0; i < N; i++)
        free(Distance_Array[i]);
    free(Distance_Array);


    free(temp_vol);
    free(ResultKappa);

    return 1.0;
}

long Sort_VolData(
    long nHWVol_Swaption,
    double* tHWVol_Swaption,
    double* HWVol_Swaption,
    long nHWVol_Cap,
    double* tHWVol_Cap,
    double* HWVol_Cap,
    double* tHWVol,
    double* HWVol,
    long nHWVol
)
{
    long i;
    long j;
    long k;
    long nSame;

    // 중복되는 Term 개수 Count
    long N_Time_Equal;
    N_Time_Equal = 0;
    for (i = 0; i < nHWVol_Swaption; i++)
        for (j = 0; j < nHWVol_Cap; j++)
        {
            if (tHWVol_Swaption[i] == tHWVol_Cap[j])
            {
                N_Time_Equal += 1;
                break;
            }
        }

    // Term 겹치는 중복 개수 제거
    long NVol = nHWVol_Swaption + nHWVol_Cap - N_Time_Equal;
    double* Term_Vol = (double*)malloc(sizeof(double) * NVol);
    double* Vol = (double*)malloc(sizeof(double) * NVol);

    for (i = 0; i < nHWVol_Swaption; i++)
    {
        Term_Vol[i] = tHWVol_Swaption[i];
        Vol[i] = HWVol_Swaption[i];
    }

    k = nHWVol_Swaption;
    for (i = 0; i < nHWVol_Cap; i++)
    {
        nSame = 0;
        for (j = 0; j < nHWVol_Swaption; j++)
        {
            if (tHWVol_Cap[i] == tHWVol_Swaption[j])
            {
                nSame += 1;
                break;
            }
        }

        if (nSame == 0)
        {
            Term_Vol[k] = tHWVol_Cap[i];
            Vol[k] = HWVol_Cap[i];
            k += 1;
        }
    }

    double temp_idx;
    double temp_value;
    for (i = 0; i < NVol; i++)
    {
        for (j = 0; j < NVol - 1; j++)
        {
            if (Term_Vol[j] > Term_Vol[j + 1])
            {
                temp_idx = Term_Vol[j];
                temp_value = Vol[i];
                Term_Vol[j] = Term_Vol[j + 1];
                Vol[j] = Vol[j + 1];
                Term_Vol[j + 1] = temp_idx;
                Vol[j + 1] = temp_value;
            }
        }
    }

    for (i = 0; i < NVol; i++)
    {
        tHWVol[i] = Term_Vol[i];
        HWVol[i] = Vol[i];
    }

    for (i = NVol; i < nHWVol; i++)
    {
        tHWVol[i] = tHWVol[i - 1] + 1.0e-7;
        HWVol[i] = HWVol[i - 1];
    }

    free(Term_Vol);
    free(Vol);
    return NVol;
}

long Calibration(
    double* t,                    //
    double* r,                    // 입력: 무위험 금리 기간 구조
    long nr,                    //
    long CaliFlag,               // 0 Swaption Cap 둘다 1 Cap 2 Swaption
    double* Swaption_Mat,        // 입력: 각 스왑션(캡)의 만기(연환산) 
    double* Swap_Mat,            // 입력: 각 스왑션(캡)의 기초자산(스왑) 만기(연환산)
    double* Strike_Rate,        // 입력: 각 스왑션(캡)의 행사가격
    double* Swap_Period,        // 입력: 각 스왑션의 기초자산인 스왑(캡) 지급 주기(월환산)
    double* Swaption_Vol,        // 입력: 각 스왑션(캡)의 변동성
    long nSwaption,                // 입력: 스왑션(캡) 개수
    double* Cap_Mat,            // 입력: 각 캡의 만기(연환산)
    double* Cap_Tenor,            // 입력: 각 캡의 지급 주기(월환산)
    double* Cap_Strike,
    double* Cap_Vol,            // 입력: 각 캡의 변동성
    long nCap,                    // 입력: 캡 개수
    double* HW_Kappa,            // 결과: HW 모형 모수 Kappa
    long HW_Kappa_Flag,            // 입력: HW_Kappa 고정 여부(0:고정, 1:변동)
    double Fixed_Kappa,
    double* tHW_Vol,            // 입력: HW 변동성 기간 구조 시점
    double* HW_Vol,            // 입력/결과: HW 변동성
    long nHW_Vol,                // 입력: HW 변동성 기간 구조 개수
    long lognormalvol0normalvol1

)
{
    long i;
    long j;

    long ma;

    double* tVol_g = (double*)malloc(sizeof(double) * (nHW_Vol));

    for (i = 0; i < nHW_Vol; i++) tVol_g[i] = tHW_Vol[i];
    long nVol_g = nHW_Vol;

    // BS 모형으로 스왑션(캡) 가격을 계산
    double* Swaption_Price = (double*)malloc(sizeof(double) * (nSwaption));
    double* Cap_Price = (double*)malloc(sizeof(double) * (nCap));

    for (i = 0; i < nSwaption; i++) {

        if (Swaption_Mat[i] > 0.0) {
            Swaption_Price[i] = BS_Swaption(Notional_Amount, Swaption_Vol[i], Strike_Rate[i], t, r, nr, Swaption_Mat[i], Swap_Mat[i], Swap_Period[i], lognormalvol0normalvol1);

        }
        else {
            Swaption_Price[i] = BS_Cap(Notional_Amount, Swaption_Vol[i], t, r, nr,
                Strike_Rate[i], Swaption_Mat[i], Swap_Mat[i], Swap_Period[i], lognormalvol0normalvol1);
        }

    }


    for (i = 0; i < nCap; i++) {
        Cap_Price[i] = BS_Cap(Notional_Amount, Cap_Vol[i], t, r, nr, Cap_Strike[i], 0.0, Cap_Mat[i], Cap_Tenor[i], lognormalvol0normalvol1);

    }

    ma = nHW_Vol + 1;
    double* a = (double*)malloc(sizeof(double) * (ma));
    long* ia = (long*)malloc(sizeof(long) * (ma));

    ia[0] = HW_Kappa_Flag;
    a[0] = *HW_Kappa;
    for (i = 1; i < ma; i++) {
        ia[i] = 1;
        a[i] = HW_Vol[i - 1];
    }

    double Temp;
    double*** Cap_ErrorArray = (double***)malloc(sizeof(double**) * max(nCap, 1));
    long Cap_ErrorShape[3] = { 0,0,0 };
    long nSwaptionOption = 0;

    if (CaliFlag == 0)
    {
        nSwaptionOption = (nHW_Vol - nCap);
    }


    for (i = 0; i < nCap; i++) {
        tHW_Vol[i + nSwaptionOption] = Cap_Mat[i];
    }

    if (CaliFlag == 0 || CaliFlag == 2)
    {
        Temp = OptimizeHWCap(nCap, t, r, nr, CaliFlag,
            Cap_Mat, Cap_Strike, Cap_Tenor, Cap_Vol, Cap_Price,
            ma, ia, a, tHW_Vol + nSwaptionOption, HW_Vol + nSwaptionOption,
            nCap, Cap_ErrorShape, Cap_ErrorArray, HW_Kappa_Flag, Fixed_Kappa);

        if (CaliFlag == 0)
        {
            Temp = OptimizeHWSwaption(nSwaption, nCap, Cap_ErrorShape, Cap_ErrorArray, Cap_Mat, t, r, nr, CaliFlag,
                Swaption_Mat, Swap_Mat, Strike_Rate, Swap_Period, Swaption_Vol,
                Swaption_Price, ma, ia, a, tHW_Vol, HW_Vol, nHW_Vol, HW_Kappa_Flag, Fixed_Kappa);
        }

        for (i = 0; i < Cap_ErrorShape[0]; i++)
        {
            for (j = 0; j < Cap_ErrorShape[1]; j++)
            {
                if (Cap_ErrorArray[i][j]) free(Cap_ErrorArray[i][j]);
            }
            if (Cap_ErrorArray[i]) free(Cap_ErrorArray[i]);
        }

    }

    if (CaliFlag == 1)
    {
        Temp = OptimizeHWSwaption(nSwaption, nCap, Cap_ErrorShape, Cap_ErrorArray, Cap_Mat, t, r, nr, CaliFlag,
            Swaption_Mat, Swap_Mat, Strike_Rate, Swap_Period, Swaption_Vol,
            Swaption_Price, ma, ia, a, tHW_Vol, HW_Vol, nHW_Vol, HW_Kappa_Flag, Fixed_Kappa);

    }

    if (CaliFlag == 0)
        nHW_Vol = Sort_VolData(nSwaptionOption, tHW_Vol, HW_Vol, nCap, tHW_Vol + nSwaptionOption, HW_Vol + nSwaptionOption, tHW_Vol, HW_Vol, nHW_Vol);

    HW_Kappa[0] = a[0];


    free(tVol_g);
    free(Swaption_Price);
    free(Cap_Price);
    free(a);
    free(ia);
    if (Cap_ErrorArray) free(Cap_ErrorArray);
    return 1;
}

long SaveErrorName(char* Error, char ErrorName[100])
{
    long k;
    long i;
    long Ascii;
    k = 0;
    for (i = 0; i < 100; i++)
    {
        Ascii = (long)ErrorName[i];
        if ((Ascii >= 48 && Ascii <= 57) || (Ascii >= 65 && Ascii <= 90) || (Ascii >= 97 && Ascii <= 122) || (Ascii == 32))
        {
            Error[k] = ErrorName[i];
            k++;
        }
        else
        {
            break;
        }
    }
    return -1;
}

long ErrorCheck_HW_Calibration(
    double* t,                    //
    double* r,                    // 입력: 무위험 금리 기간 구조
    long nr,                        //
    long CaliFlag,               // 0 Swaption Cap 둘다 1 Swaption 2 Cap
    double* Cap_Mat,            // 입력: 각 캡의 만기(연환산)
    double Caplet_Freq,            // 입력: 각 캡의 지급 주기(월환산)
    double* Cap_Vol,            // 입력: 각 캡의 변동성
    long nCap,                    // 입력: 캡 개수
    double* Swaption_Mat,        // 입력: 각 스왑션의 만기(연환산) 
    double* Swap_Mat,            // 입력: 각 스왑 만기(연환산)
    double* Swaption_Vol,        // 입력: 각 스왑션(캡)의 변동성
    double SwapPay_Freq,
    long nSwaption,                // 입력: 스왑션(캡) 개수
    long HW_Kappa_Flag,            // 입력: HW_Kappa 고정 여부(0:고정, 1:변동)
    double Fixed_Kappa,
    long nHW_Vol,                // 입력: HW 변동성 기간 구조 개수
    long ErrorCheckFlag,
    char* Error
)
{
    long i;

    char ErrorName[100];

    if (nCap + nSwaption < 0 || nHW_Vol < 1)
    {
        strcpy_s(ErrorName, "Check nCap nSwaption nHWVol");
        return SaveErrorName(Error, ErrorName);
    }

    if (ErrorCheckFlag > 0)
    {
        for (i = 1; i < nr; i++)
        {
            if (t[i] < t[i - 1])
            {
                strcpy_s(ErrorName, "Curve t1 is bigger than t2");
                return SaveErrorName(Error, ErrorName);
            }
        }

        if (CaliFlag < 0 || CaliFlag > 2)
        {
            strcpy_s(ErrorName, "Check CaliFlag");
            return SaveErrorName(Error, ErrorName);
        }

        if (nCap < 0)
        {
            strcpy_s(ErrorName, "nCap is zero");
            return SaveErrorName(Error, ErrorName);
        }

        for (i = 1; i < nCap; i++)
        {
            if (Cap_Mat[i] < Cap_Mat[i - 1]) {
                strcpy_s(ErrorName, "Cap Mat t1 is bigger than t2");
                return SaveErrorName(Error, ErrorName);
            }
            if (Cap_Vol[i] < 0.0)
            {
                strcpy_s(ErrorName, "CapVol must be Positive");
                return SaveErrorName(Error, ErrorName);
            }
        }
        if (Cap_Vol[0] < 0.0)
        {
            strcpy_s(ErrorName, "CapVol must be Positive");
            return SaveErrorName(Error, ErrorName);
        }

        if (Cap_Mat[0] < (double)Caplet_Freq / 12.0)
        {
            strcpy_s(ErrorName, "First Cap term must be bigger than Cap Frequency");
            return SaveErrorName(Error, ErrorName);
        }

        if (nSwaption < 0)
        {
            strcpy_s(ErrorName, "nSwaption must be Positive");
            return SaveErrorName(Error, ErrorName);
        }

        for (i = 1; i < nSwaption; i++)
        {
            if (Swaption_Vol[i] < 0.0)
            {
                strcpy_s(ErrorName, "SwaptionVol must be Positive");
                return SaveErrorName(Error, ErrorName);
            }
        }
        if (Swaption_Vol[0] < 0.0)
        {
            strcpy_s(ErrorName, "SwaptionVol must be Positive");
            return SaveErrorName(Error, ErrorName);
        }

        if (HW_Kappa_Flag < 0 || HW_Kappa_Flag > 2)
        {
            strcpy_s(ErrorName, "Check the Kappa Flag");
            return SaveErrorName(Error, ErrorName);
        }

    }


    return 1;
}

// 1-factor 모형의 Calibration 함수
// ATM 변동성만 사용
DLLEXPORT(long) HW_Calibration_ATM(
    double* t,                    //
    double* r,                    // 입력: 무위험 금리 기간 구조
    long nr,                        //
    long CaliFlag,               // 0 Swaption Cap 둘다 1 Swaption 2 Cap
    double* Cap_Mat,            // 입력: 각 캡의 만기(연환산)
    double Caplet_Freq,            // 입력: 각 캡의 지급 주기(월환산)
    double* Cap_Vol,            // 입력: 각 캡의 변동성
    long nCap,                    // 입력: 캡 개수
    double* Swaption_Mat,        // 입력: 각 스왑션의 만기(연환산) 
    double* Swap_Mat,            // 입력: 각 스왑 만기(연환산)
    double* Swaption_Vol,        // 입력: 각 스왑션(캡)의 변동성
    double SwapPay_Freq,
    long nSwaption,                // 입력: 스왑션(캡) 개수
    double* HW_Kappa,            // 결과: HW 모형 모수 Kappa
    long HW_Kappa_Flag,            // 입력: HW_Kappa 고정 여부(0:고정, 1:변동)
    double Fixed_Kappa,
    double* tHW_Vol,            // 입력: HW 변동성 기간 구조 시점
    double* HW_Vol,                // 입력/결과: HW 변동성
    long nHW_Vol,                // 입력: HW 변동성 기간 구조 개수

    char* Error,
    long lognormalvol0normalvol1
)
{

    long i;
    long Result = 0;
    long ErrorCheckFlag = 1;

    Result = ErrorCheck_HW_Calibration(t, r, nr, CaliFlag, Cap_Mat, Caplet_Freq, Cap_Vol, nCap, Swaption_Mat, Swap_Mat, Swaption_Vol, SwapPay_Freq, nSwaption, HW_Kappa_Flag, Fixed_Kappa, nHW_Vol, ErrorCheckFlag, Error);
    if (CaliFlag == 1) {
        nHW_Vol = nHW_Vol - nCap;
        nCap = 0;
    }

    if (CaliFlag == 2) {
        nHW_Vol = nCap;
        nSwaption = 0;
    }

    double* Cap_Tenor = (double*)malloc(sizeof(double) * nCap);             //할당1
    double* Swap_Period = (double*)malloc(nSwaption * sizeof(double));      //할당2
    for (i = 0; i < nCap; i++)
        Cap_Tenor[i] = Caplet_Freq;

    for (i = 0; i < nSwaption; i++)
        Swap_Period[i] = SwapPay_Freq;

    double* Cap_Strike = (double*)malloc(max(nCap, 1) * sizeof(double));     //할당3
    if (CaliFlag != 1)
    {
        for (i = 0; i < nCap; i++) {
            Cap_Strike[i] = FSR(t, r, nr, 0.0, Cap_Mat[i], Cap_Tenor[i]);
        }
    }

    double* Swap_Rate = (double*)malloc(max(nSwaption, 1) * sizeof(double)); //할당4
    if (CaliFlag != 2)
    {
        for (i = 0; i < nSwaption; i++) {
            Swap_Rate[i] = FSR(t, r, nr, Swaption_Mat[i], Swap_Mat[i], Swap_Period[i]);
        }
    }

    if (Result > 0)
    {
        Result = Calibration(t, r, nr, CaliFlag, Swaption_Mat, Swap_Mat, Swap_Rate, Swap_Period, Swaption_Vol, nSwaption, Cap_Mat, Cap_Tenor, Cap_Strike, Cap_Vol, nCap,
            HW_Kappa, HW_Kappa_Flag, Fixed_Kappa, tHW_Vol, HW_Vol, nHW_Vol, lognormalvol0normalvol1);
    }

    if (Cap_Tenor) free(Cap_Tenor);
    if (Swap_Period) free(Swap_Period);
    if (Cap_Strike) free(Cap_Strike);
    if (Swap_Rate) free(Swap_Rate);


    //_CrtDumpMemoryLeaks();

    return Result;
}


void NextLambda(double ErrorSquareSum, double PrevErrorSquareSum, double* lambda, long& BreakFlag)
{
    double LambdaMax = 1000000;
    double LambdaMin = 0.00001;

    if (ErrorSquareSum < PrevErrorSquareSum) *lambda *= 0.1;
    else *lambda *= 10.0;

    if (*lambda > LambdaMax) *lambda = LambdaMax;
    if (*lambda < LambdaMin) BreakFlag = 1;
}

void NextLambda(double ErrorSquareSum, double PrevErrorSquareSum, double* lambda, long& BreakFlag, long& ngrad)
{
    double LambdaMax = 1000000;
    double LambdaMin = 0.00001;

    if (ErrorSquareSum < PrevErrorSquareSum)
    {
        if (ngrad < 3) ngrad += 1;
        else
        {
            *lambda *= 0.1;
            ngrad = 0;
        }
    }
    else *lambda *= 10.0;

    if (*lambda > LambdaMax) *lambda = LambdaMax;
    if (*lambda < LambdaMin) BreakFlag = 1;
}

void Levenberg_Marquardt(long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_J, double** Inverse_JT_J, double** JT_Res, double** ResultMatrix, long FixedKappaFlag)
{
    long i;
    double mu = *lambda;
    double MIN_kappa = 0.001;
    double MIN_Vol = 0.00001;
    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };
    long Shape_JT[2] = { m,n };
    long Shape_Residual[2] = { n,1 };

    // J' dot J                 Shape = m * m
    XprimeDotX(Jacov, Shape_J, JT_J);
    rounding(JT_J, m, m, 5);

    // J'J + mu * diag(J'J)     Shape = m * m
    for (i = 0; i < m; i++) JT_J[i][i] = JT_J[i][i] + mu;// *JT_J[i][i];

    // inv(J'J + mu * diag(J'J))
    long Shape_Inv_JT_J[2] = { m,m };    
    //MatrixInversion(JT_J, m, Inverse_JT_J);

    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    double* Known = (double*)malloc(sizeof(double) * m);
    double* UnKnown = (double*)malloc(sizeof(double) * m);
    for (i = 0; i < m; i++) Known[i] = JT_Res[i][0];

    gaussian_elimination(JT_J, Known, UnKnown, m);

    //Dot2dArray(Inverse_JT_J, Shape_Inv_JT_J, JT_Res, Shape_JT_Res, ResultMatrix);

    if (FixedKappaFlag == 0)
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i];// -ResultMatrix[i][0];
            if (i == 0)
            {
                if (NextParams[0] < MIN_kappa) NextParams[0] = MIN_kappa;
            }
            else
            {
                if (NextParams[i] < MIN_Vol) NextParams[i] = MIN_Vol;
            }
        }
    }
    else
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i]; //- ResultMatrix[i][0];
            if (NextParams[i] < MIN_Vol) NextParams[i] = MIN_Vol;
        }

    }
    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(UnKnown[i]);
    ParamSum = s;
    free(Known);
    free(UnKnown);
}

void Gradient_Desent(long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_Res)
{
    long i;
    double mu = *lambda;
    double MIN_kappa = 0.001;
    double MIN_Vol = 0.00001;
    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };


    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    for (i = 0; i < NParams; i++)
    {
        NextParams[i] = CurrentParams[i] - 2.0 * mu * JT_Res[i][0];
        if (i == 0)
        {
            if (NextParams[0] < MIN_kappa) NextParams[0] = MIN_kappa;
        }
        else
        {
            if (NextParams[i] < MIN_Vol) NextParams[i] = MIN_Vol;
        }
    }

    double s = 0.0;
    for (i = 0; i < NParams; i++) s += 2.0 * mu * JT_Res[i][0];
    ParamSum = fabs(s);
}

void make_Residual_HWSwaptionCap(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double& absErrorSum,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{
    long i;
    double kappa;
    double* HWVol;
    if (FixedKappaFlag != 1)
    {
        kappa = Params[0];
        HWVol = Params + 1;
    }
    else
    {
        kappa = FixedKappa;
        HWVol = Params;
    }
    double s = 0.0;
    double percent_rsme = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        if (OptMaturityDates[i] > 0) TempHWSwaptionPrice[i] = HW_Swaption(1.0, kappa, HWVolTerm, HWVol, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
        else TempHWSwaptionPrice[i] = HW_Cap(1.0, kappa, HWVolTerm, HWVol, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);
    }
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = (BSSwaptionPrice[i] - TempHWSwaptionPrice[i]);
        percent_rsme += ResidualArray[i] * ResidualArray[i] / (TempHWSwaptionPrice[i] * TempHWSwaptionPrice[i]);
    }
    percent_rsme = sqrt(percent_rsme / (double)NResidual);
    RMPSE = percent_rsme;
    for (i = 0; i < NResidual; i++) s += fabs(ResidualArray[i]);

    absErrorSum = s;
}

void make_Residual_HWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double& absErrorSum,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{
    long i;
    double kappa;
    double* HWVol;
    if (FixedKappaFlag != 1)
    {
        kappa = Params[0];
        HWVol = Params + 1;
    }
    else
    {
        kappa = FixedKappa;
        HWVol = Params;
    }
    double s = 0.0;
    double percent_rsme = 0.0;
    for (i = 0; i < NResidual; i++) TempHWSwaptionPrice[i] = HW_Swaption(1.0, kappa, HWVolTerm, HWVol, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = (BSSwaptionPrice[i] - TempHWSwaptionPrice[i]);
        percent_rsme += ResidualArray[i] * ResidualArray[i] / (TempHWSwaptionPrice[i]* TempHWSwaptionPrice[i]);
    }
    percent_rsme = sqrt(percent_rsme/(double)NResidual);
    RMPSE = percent_rsme;
    for (i = 0; i < NResidual; i++) s += fabs(ResidualArray[i]);
    
    absErrorSum = s;
}

void make_Residual_HWCapHWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    long* SwaptionFlag,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double& absErrorSum,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{
    long i;
    double kappa;
    double* HWVol;
    if (FixedKappaFlag != 1)
    {
        kappa = Params[0];
        HWVol = Params + 1;
    }
    else
    {
        kappa = FixedKappa;
        HWVol = Params;
    }

    double s = 0.0;
    double percent_rsme = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        if (SwaptionFlag[i] == 0) TempHWSwaptionPrice[i] = HW_Cap(1.0, kappa, HWVolTerm, HWVol, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);
        else TempHWSwaptionPrice[i] = HW_Swaption(1.0, kappa, HWVolTerm, HWVol, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
    }
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = (BSSwaptionPrice[i] - TempHWSwaptionPrice[i]);
        percent_rsme += (ResidualArray[i] * ResidualArray[i]) / (TempHWSwaptionPrice[i] * TempHWSwaptionPrice[i]);
    }
    percent_rsme = sqrt(percent_rsme / (double)NResidual);
    RMPSE = percent_rsme;
    
    for (i = 0; i < NResidual; i++) s += fabs(ResidualArray[i]);
    absErrorSum = s;
}

void make_Jacov_HWSwaptionCap(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa
)
{
    long i;
    long j;
    long n;

    double dhwvol_up = 0.0001;
    double dkappa_up = 0.0001;

    double T;
    double HWT;

    double kappa_up;
    double kappa_dn;

    double* HWVol_up;
    double* HWVol_dn;

    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double dParams;
    double temp = 0.0;

    for (i = 0; i < NResidual; i++)
    {
        for (j = 0; j < NParams; j++)
        {
            // 파라미터 초기화
            for (n = 0; n < NParams; n++) {
                ParamsUp[n] = Params[n];
                ParamsDn[n] = Params[n];
            }

            // 파라미터 Up And Dn
            if (FixedKappaFlag != 1)
            {
                if (j == 0)
                {
                    ParamsUp[j] = Params[j] + dkappa_up;
                    ParamsDn[j] = Params[j] - dkappa_up;
                    dParams = dkappa_up;
                }
                else
                {
                    ParamsUp[j] = Params[j] + dhwvol_up;
                    ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                    dParams = dhwvol_up;
                }

                kappa_up = ParamsUp[0];
                kappa_dn = ParamsDn[0];
                HWVol_up = ParamsUp + 1;
                HWVol_dn = ParamsDn + 1;
            }
            else
            {
                ParamsUp[j] = Params[j] + dhwvol_up;
                ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                dParams = dhwvol_up;

                kappa_up = FixedKappa;
                kappa_dn = FixedKappa;
                HWVol_up = ParamsUp;
                HWVol_dn = ParamsDn;
            }

            T = (double)dates[i][nDates[i] - 1] / 365.0;
            HWT = HWVolTerm[j];
            if (HWT > T)
            {
                TempJacovMatrix[i][j] = 0.0;
            }
            else
            {
                if (OptMaturityDates[i] > 0)
                {
                    Pup = HW_Swaption(1.0, kappa_up, HWVolTerm, HWVol_up, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
                    ErrorUp = BSSwaptionPrice[i] - Pup;
                    Pdn = HW_Swaption(1.0, kappa_dn, HWVolTerm, HWVol_dn, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
                    ErrorDn = BSSwaptionPrice[i] - Pdn;
                    TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
                }
                else
                {
                    Pup = HW_Cap(1.0, kappa_up, HWVolTerm, HWVol_up, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);
                    ErrorUp = BSSwaptionPrice[i] - Pup;
                    Pdn = HW_Cap(1.0, kappa_dn, HWVolTerm, HWVol_dn, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);
                    ErrorDn = BSSwaptionPrice[i] - Pdn;
                    TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
                }
            }
        }
    }
}

void make_Jacov_HWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa
)
{
    long i;
    long j;
    long n;

    double dhwvol_up = 0.0001;
    double dkappa_up = 0.0001;

    double T;
    double HWT;

    double kappa_up;
    double kappa_dn;

    double* HWVol_up;
    double* HWVol_dn;

    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double dParams;
    double temp = 0.0;
    long breakflag = 0;

    for (i = 0; i < NResidual; i++)
    {
        for (j = 0; j < NParams; j++)
        {
            breakflag = 0;
            // 파라미터 초기화
            for (n = 0; n < NParams; n++) {
                ParamsUp[n] = Params[n];
                ParamsDn[n] = Params[n];
            }
            T = (double)dates[i][nDates[i] - 1] / 365.0;

            // 파라미터 Up And Dn
            if (FixedKappaFlag != 1)
            {
                if (j == 0)
                {
                    ParamsUp[j] = Params[j] + dkappa_up;
                    ParamsDn[j] = Params[j] - dkappa_up;
                    dParams = dkappa_up;
                }
                else
                {
                    ParamsUp[j] = Params[j] + dhwvol_up;
                    ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                    dParams = dhwvol_up;

                    HWT = HWVolTerm[j];
                    if (HWT > T + 0.5)
                    {
                        breakflag = 1;
                    }
                }

                kappa_up = ParamsUp[0];
                kappa_dn = ParamsDn[0];
                HWVol_up = ParamsUp + 1;
                HWVol_dn = ParamsDn + 1;
            }
            else
            {
                ParamsUp[j] = Params[j] + dhwvol_up;
                ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                dParams = dhwvol_up;

                kappa_up = FixedKappa;
                kappa_dn = FixedKappa;
                HWVol_up = ParamsUp;
                HWVol_dn = ParamsDn;

                HWT = HWVolTerm[j];
                if (HWT > T + 0.5)
                {
                    breakflag = 1;
                }
            }

            if (breakflag == 1)
            {
                TempJacovMatrix[i][j] = 0.0;
            }
            else
            {
                Pup = HW_Swaption(1.0, kappa_up, HWVolTerm, HWVol_up, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
                ErrorUp = BSSwaptionPrice[i] - Pup;
                Pdn = HW_Swaption(1.0, kappa_dn, HWVolTerm, HWVol_dn, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
                ErrorDn = BSSwaptionPrice[i] - Pdn;
                TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
            }
        }
    }
}

void make_Jacov_HWCapHWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    long* SwaptionFlag,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa
)
{
    long i;
    long j;
    long n;

    double dhwvol_up = 0.0001;
    double dkappa_up = 0.0001;

    double kappa_up;
    double kappa_dn;

    double* HWVol_up;
    double* HWVol_dn;

    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double dParams;
    double temp = 0.0;

    for (i = 0; i < NResidual; i++)
    {
        for (j = 0; j < NParams; j++)
        {
            // 파라미터 초기화
            for (n = 0; n < NParams; n++) {
                ParamsUp[n] = Params[n];
                ParamsDn[n] = Params[n];
            }

            // 파라미터 Up And Dn
            if (FixedKappaFlag != 1)
            {
                if (j == 0)
                {
                    ParamsUp[j] = Params[j] + dkappa_up;
                    ParamsDn[j] = Params[j] - dkappa_up;
                    dParams = dkappa_up;
                }
                else
                {
                    ParamsUp[j] = Params[j] + dhwvol_up;
                    ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                    dParams = dhwvol_up;
                }

                kappa_up = ParamsUp[0];
                kappa_dn = ParamsDn[0];
                HWVol_up = ParamsUp + 1;
                HWVol_dn = ParamsDn + 1;
            }
            else
            {
                ParamsUp[j] = Params[j] + dhwvol_up;
                ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                dParams = dhwvol_up;
                kappa_up = FixedKappa;
                kappa_dn = FixedKappa;
                HWVol_up = ParamsUp;
                HWVol_dn = ParamsDn;
            }

            if (SwaptionFlag[i] == 1) Pup = HW_Swaption(1.0, kappa_up, HWVolTerm, HWVol_up, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
            else Pup = HW_Cap(1.0, kappa_up, HWVolTerm, HWVol_up, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);

            ErrorUp = BSSwaptionPrice[i] - Pup;

            if (SwaptionFlag[i] == 1) Pdn = HW_Swaption(1.0, kappa_dn, HWVolTerm, HWVol_dn, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], OptMaturityDates[i], dates[i], nDates[i], PT[i]);
            else Pdn = HW_Cap(1.0, kappa_dn, HWVolTerm, HWVol_dn, NHWVol, ZeroTerm, ZeroRate, NZero, StrikePrice[i], dates[i], nDates[i], PT[i]);

            ErrorDn = BSSwaptionPrice[i] - Pdn;

            TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
        }
    }
}

void Gradient_Desent_HWCapHWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    long* SwaptionFlag,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double FreqMonth,
    double FreqMonthCap,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{

    long i;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;


    double StopCondition = 0.00001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 0.1 };
    double* NextParams = make_array(NParams);
    double** JT_Res = make_array(NParams, 1);
    double* argminparam = make_array(NParams);
    for (n = 0; n < 30; n++)
    {
        make_Jacov_HWCapHWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, SwaptionFlag, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
            nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);

        lambda[0] *= 0.995;
        make_Residual_HWCapHWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, SwaptionFlag, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
            nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

        if (n >= 1)
        {
            if (absErrorSum < minerror || n == 1)
            {
                minerror = absErrorSum;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
            }
        }

        Gradient_Desent(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_Res);
        for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

        if (ParamSum < StopCondition && n > 10)
        {
            break;
        }

        PrevAbsErrorSum = absErrorSum;
    }

    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    free(NextParams);
    free(argminparam);
}

void Levenberg_Marquardt_HWSwaptionForKDBMurex(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{

    long i;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long Levenberg = 1;

    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 1.00 };
    double* NextParams = make_array(NParams);
    double** JT_J = make_array(NParams, NParams);
    double** Inverse_JT_J = make_array(NParams, NParams);
    double** JT_Res = make_array(NParams, 1);
    double** ResultMatrix = make_array(NParams, 1);
    double* argminparam = make_array(NParams);
    double* argminhwprice = make_array(NResidual);
    for (n = 0; n < 20; n++)
    {

        make_Jacov_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
            nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);

        make_Residual_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
            nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

        if (n >= 1)
        {
            NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
            if (absErrorSum < minerror || n == 1)
            {
                minerror = absErrorSum;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                for (i = 0; i < NResidual; i++) argminhwprice[i] = TempHWSwaptionPrice[i];
            }
        }

        Levenberg_Marquardt(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, FixedKappaFlag);
        for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

        if (ParamSum < StopCondition && n > 10) break;
        if (BreakFlag == 1) break;
        if (lambda[0] < 1.0e-07) break;

        PrevAbsErrorSum = absErrorSum;
    }

    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];
    for (i = 0; i < NResidual; i++) TempHWSwaptionPrice[i] = argminhwprice[i];

    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    for (i = 0; i < NParams; i++) free(Inverse_JT_J[i]);
    free(JT_J);
    free(Inverse_JT_J);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(ResultMatrix[i]);
    free(ResultMatrix);
    free(argminparam);
    free(argminhwprice);
}

void Levenberg_Marquardt_HWSwaption(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{

    long i;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long Levenberg = 1;

    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 1.00 };
    double* NextParams = make_array(NParams);
    double** JT_J = make_array(NParams, NParams);
    double** Inverse_JT_J = make_array(NParams, NParams);
    double** JT_Res = make_array(NParams, 1);
    double** ResultMatrix = make_array(NParams, 1);
    double* argminparam = make_array( NParams);

    if (Levenberg == 1)
    {
        for (n = 0; n < 20; n++)
        {

            make_Jacov_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);

            make_Residual_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

            if (n >= 1)
            {
                NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
                if (absErrorSum < minerror || n == 1)
                {
                    minerror = absErrorSum;
                    for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                }
            }

            Levenberg_Marquardt(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, FixedKappaFlag);
            for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

            if (ParamSum < StopCondition && n > 10) break;
            if (BreakFlag == 1) break;
            if (lambda[0] < 1.0e-07) break;

            PrevAbsErrorSum = absErrorSum;
        }
    }
    else
    {
        lambda[0] = 0.0;
        for (n = 0; n < 20; n++)
        {
            make_Jacov_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);


            make_Residual_HWSwaption(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

            if (n >= 1)
            {
                NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
                if (absErrorSum < minerror || n == 1)
                {
                    minerror = absErrorSum;
                    for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                }
            }
            Levenberg_Marquardt(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, FixedKappaFlag);
            for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

            if (ParamSum < StopCondition && n > 10) break;
            if (lambda[0] < 1.0e-07) break;
            PrevAbsErrorSum = absErrorSum;
        }
    }

    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];

    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    for (i = 0; i < NParams; i++) free(Inverse_JT_J[i]);
    free(JT_J);
    free(Inverse_JT_J);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(ResultMatrix[i]);
    free(ResultMatrix);
    free(argminparam);
}

void Levenberg_Marquardt_HWSwaptionCap(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double& RMPSE
)
{

    long i;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long Levenberg = 1;

    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 1.00 };
    double* NextParams = make_array(NParams);
    double** JT_J = make_array(NParams, NParams);
    double** Inverse_JT_J = make_array(NParams, NParams);
    double** JT_Res = make_array(NParams, 1);
    double** ResultMatrix = make_array(NParams, 1);
    double* argminparam = make_array(NParams);

    if (Levenberg == 1)
    {
        for (n = 0; n < 20; n++)
        {

            make_Jacov_HWSwaptionCap(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);

            make_Residual_HWSwaptionCap(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

            if (n >= 1)
            {
                NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
                if (absErrorSum < minerror || n == 1)
                {
                    minerror = absErrorSum;
                    for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                }
            }

            Levenberg_Marquardt(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, FixedKappaFlag);
            for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

            if (ParamSum < StopCondition && n > 10) break;
            if (BreakFlag == 1) break;
            if (lambda[0] < 1.0e-07) break;

            PrevAbsErrorSum = absErrorSum;
        }
    }
    else
    {
        lambda[0] = 0.0;
        for (n = 0; n < 20; n++)
        {
            make_Jacov_HWSwaptionCap(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa);


            make_Residual_HWSwaptionCap(NParams, Params, NZero, ZeroTerm, ZeroRate,
                NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
                TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
                nDates, dates, PT, absErrorSum, FixedKappaFlag, FixedKappa, RMPSE);

            if (n >= 1)
            {
                NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
                if (absErrorSum < minerror || n == 1)
                {
                    minerror = absErrorSum;
                    for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                }
            }
            Levenberg_Marquardt(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, FixedKappaFlag);
            for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

            if (ParamSum < StopCondition && n > 10) break;
            if (lambda[0] < 1.0e-07) break;
            PrevAbsErrorSum = absErrorSum;
        }
    }

    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];

    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    for (i = 0; i < NParams; i++) free(Inverse_JT_J[i]);
    free(JT_J);
    free(Inverse_JT_J);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(ResultMatrix[i]);
    free(ResultMatrix);
    free(argminparam);
}

long HW_GradDecent_Calibration_SwaptionCap(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double* Strike,

    long NCap,
    double* TermCapVol,
    double* CapVol,
    double FreqMonth,
    double FreqMonthCap,

    long NHW,
    double* HWTerm,
    double* HWVol,
    double& kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1
)
{
    long i;

    long k;
    long n;
    n = 0;
    for (i = 0; i < NHW; i++)
    {
        if (TermCapVol[NCap - 1] < HWTerm[i] || (NOpt> 0 && TermOpt[NOpt - 1] < HWTerm[i]) ) n += 1;
    }
    NHW = NHW - n;

    long* SwaptionFlag = (long*)malloc(sizeof(long) * (NSwap * NOpt + NCap));
    for (i = 0; i < (NSwap * NOpt); i++) SwaptionFlag[i] = 1;
    for (i = NSwap * NOpt; i < (NSwap * NOpt + NCap); i++) SwaptionFlag[i] = 0;

    double* TermSwapNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    for (i = 0; i < NSwap * NOpt; i++) TermSwapNew[i] = TermSwap[i % NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermSwapNew[i] = TermCapVol[i - NSwap * NOpt];

    double* TermOptNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    for (i = 0; i < NSwap * NOpt; i++) TermOptNew[i] = TermOpt[i / NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermOptNew[i] = 0.0;

    double* BSSwaptionPrice = make_array(NSwap * NOpt + NCap);
    double* HWSwaptionPrice = make_array(NSwap * NOpt + NCap);

    for (k = 0; k < NSwap * NOpt; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth);
        BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth, lognormalvol0normalvol1);
    }
    for (k = NSwap * NOpt; k < NSwap * NOpt + NCap; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonthCap);
        BSSwaptionPrice[k] = BS_Cap(1.0, CapVol[k - NSwap * NOpt], ZeroTerm, ZeroRate, NZero, Strike[k], TermOptNew[k], TermSwapNew[k], FreqMonthCap, lognormalvol0normalvol1);
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * (NSwap * NOpt + NCap));
    for (i = 0; i < (NSwap * NOpt + NCap); i++) OptMaturityDates[i] = (long)(TermOptNew[i] * 365.0);

    long* nDates = (long*)malloc(sizeof(long) * (NSwap * NOpt + NCap));
    for (i = 0; i < (NSwap * NOpt + NCap); i++)
    {
        if (i < NSwap * NOpt) nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonth);
        else nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonthCap);
    }

    long** dates = (long**)malloc(sizeof(long*) * (NSwap * NOpt + NCap));
    for (i = 0; i < (NSwap * NOpt + NCap); i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        if (i < NSwap * NOpt) PaymentDatesMapping(TermOptNew[i] + TermSwapNew[i], FreqMonth, dates[i], nDates[i]);
        else PaymentDatesMapping(TermOptNew[i] + TermSwapNew[i], FreqMonthCap, dates[i], nDates[i]);
    }

    double** PT = (double**)malloc(sizeof(double*) * (NSwap * NOpt + NCap));
    for (i = 0; i < (NSwap * NOpt + NCap); i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, TermOptNew[i]);
        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    long NResidual = NOpt * NSwap + NCap;
    double* ResidualArray = make_array(NResidual);

    long nparams;
    if (FixedKappaFlag != 1) nparams = 1 + NHW;
    else nparams = NHW;

    double* params = make_array(nparams);
    double* paramsup = make_array(nparams);
    double* paramsdn = make_array(nparams);
    double** tempjacov = make_array(NResidual, nparams);
    double RMPSE = 0.0;

    if (FixedKappaFlag != 1)
    {
        params[0] = kappa;
        for (i = 0; i < NHW; i++) params[i + 1] = HWVol[i];
    }
    else
    {
        for (i = 0; i < NHW; i++) params[i] = HWVol[i];
    }

    Gradient_Desent_HWCapHWSwaption(nparams, params, NZero, ZeroTerm, ZeroRate,
        NHW, HWTerm, NResidual, SwaptionFlag, BSSwaptionPrice, Strike,
        HWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
        nDates, dates, PT, FreqMonth, FreqMonthCap, paramsup, paramsdn,
        tempjacov, FixedKappaFlag, FixedKappa, RMPSE);

    if (FixedKappaFlag != 1)
    {
        kappa = params[0];
        for (i = 0; i < NHW; i++) HWVol[i] = params[i+1];
    }
    else
    {
        kappa = FixedKappa;
        for (i = 0; i < NHW; i++) HWVol[i] = params[i];
    }

    free(TermSwapNew);
    free(TermOptNew);
    free(BSSwaptionPrice);
    free(HWSwaptionPrice);
    free(OptMaturityDates);
    free(nDates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(dates[i]);
    free(dates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(PT[i]);
    free(PT);
    free(params);
    free(paramsup);
    free(paramsdn);
    for (i = 0; i < NResidual; i++) free(tempjacov[i]);
    free(tempjacov);
    free(ResidualArray);
    free(SwaptionFlag);

    return (long)(RMPSE * 10000.0);
}

long HW_LevMarq_Calibration_SwaptionCap(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double* Strike,
    double FreqMonth,

    long NCap,
    double* CapTerm,
    double* CapVol,

    long NHW,
    double* HWTerm,
    double* HWVol,
    double& kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1
)
{
    long i;
    long j;

    long k;
    long n;

    double* TermSwapNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    for (i = 0; i < NSwap * NOpt; i++) TermSwapNew[i] = TermSwap[i % NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermSwapNew[i] = CapTerm[i - NSwap * NOpt];

    double* TermOptNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    for (i = 0; i < NSwap * NOpt; i++) TermOptNew[i] = TermOpt[i / NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermOptNew[i] = 0.0;

    double* BSSwaptionPrice = make_array(NSwap * NOpt + NCap);
    double* HWSwaptionPrice = make_array(NSwap * NOpt + NCap);

    n = 0;
    for (k = 0; k < NSwap * NOpt + NCap; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth);
        if (TermOptNew[k] > 0.0) BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth, lognormalvol0normalvol1);
        else
        {
            BSSwaptionPrice[k] = BS_Cap(1.0, CapVol[n], ZeroTerm, ZeroRate, NZero, Strike[k], TermOptNew[k], CapTerm[n], FreqMonth, lognormalvol0normalvol1);
            n++;
        }
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * (NOpt * NSwap + NCap));
    for (i = 0; i < NOpt * NSwap; i++) OptMaturityDates[i] = (long)(TermOptNew[i] * 365.0);
    for (i = NOpt * NSwap; i < NOpt * NSwap + NCap; i++) OptMaturityDates[i] = 0;

    long* nDates = (long*)malloc(sizeof(long) * (NOpt * NSwap + NCap));
    for (i = 0; i < NOpt * NSwap; i++) nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonth);
    for (i = NOpt * NSwap; i < NOpt * NSwap + NCap; i++) nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonth);

    long** dates = (long**)malloc(sizeof(long*) * (NOpt * NSwap + NCap));
    for (i = 0; i < NOpt * NSwap + NCap; i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        PaymentDatesMapping(TermOptNew[i] + TermSwapNew[i], FreqMonth, dates[i], nDates[i]);
    }

    double** PT = (double**)malloc(sizeof(double*) * (NOpt * NSwap+NCap));
    for (i = 0; i < NOpt * NSwap + NCap; i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, TermOptNew[i]);
        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    long NResidual = NOpt * NSwap + NCap;
    double* ResidualArray = make_array(NResidual);

    long nparams;
    if (FixedKappaFlag != 1) nparams = 1 + NHW;
    else nparams = NHW;

    double* params = make_array(nparams);
    double* paramsup = make_array(nparams);
    double* paramsdn = make_array(nparams);
    double** tempjacov = make_array(NResidual, nparams);
    double RMPSE = 0.0;

    if (FixedKappaFlag != 1)
    {
        params[0] = kappa;
        for (i = 0; i < NHW; i++) params[i + 1] = HWVol[i];
    }
    else
    {
        for (i = 0; i < NHW; i++) params[i] = HWVol[i];
    }

    Levenberg_Marquardt_HWSwaptionCap(nparams, params, NZero, ZeroTerm, ZeroRate,
        NHW, HWTerm, NResidual, BSSwaptionPrice, Strike,
        HWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
        nDates, dates, PT, paramsup, paramsdn,
        tempjacov, FixedKappaFlag, FixedKappa, RMPSE);

    if (FixedKappaFlag != 1)
    {
        kappa = params[0];
        for (i = 0; i < NHW; i++) HWVol[i] = params[i + 1];
    }
    else
    {
        kappa = FixedKappa;
        for (i = 0; i < NHW; i++) HWVol[i] = params[i];
    }

    free(TermSwapNew);
    free(TermOptNew);
    free(BSSwaptionPrice);
    free(HWSwaptionPrice);
    free(OptMaturityDates);
    free(nDates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(dates[i]);
    free(dates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(PT[i]);
    free(PT);
    free(params);
    free(paramsup);
    free(paramsdn);
    for (i = 0; i < NResidual; i++) free(tempjacov[i]);
    free(tempjacov);
    free(ResidualArray);

    return (long)(RMPSE * 10000.0);
}

long HW_LevMarq_Calibration_Swaption(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double* Strike,
    double FreqMonth,

    long NHW,
    double* HWTerm,
    double* HWVol,
    double& kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1
)
{
    long i;
    long j;

    long k;
    long n;

    double* TermSwapNew = (double*)malloc(sizeof(double) * NSwap * NOpt);
    for (i = 0; i < NSwap * NOpt; i++) TermSwapNew[i] = TermSwap[i % NSwap];
    double* TermOptNew = (double*)malloc(sizeof(double) * NSwap * NOpt);
    for (i = 0; i < NSwap * NOpt; i++)
        TermOptNew[i] = TermOpt[i / NSwap];

    double* BSSwaptionPrice = make_array(NSwap * NOpt);
    double* HWSwaptionPrice = make_array(NSwap * NOpt);

    for (k = 0; k < NSwap * NOpt; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth);
        BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth, lognormalvol0normalvol1);
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * NOpt * NSwap);
    for (i = 0; i < NOpt * NSwap; i++) OptMaturityDates[i] = (long)(TermOptNew[i] * 365.0);

    long* nDates = (long*)malloc(sizeof(long) * NOpt * NSwap);
    for (i = 0; i < NOpt * NSwap; i++)
        nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonth);

    long** dates = (long**)malloc(sizeof(long*) * NOpt * NSwap);
    for (i = 0; i < NOpt * NSwap; i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        PaymentDatesMapping(TermOptNew[i] + TermSwapNew[i], FreqMonth, dates[i], nDates[i]);
    }

    double** PT = (double**)malloc(sizeof(double*) * NOpt * NSwap);
    for (i = 0; i < NOpt * NSwap; i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, TermOptNew[i]);
        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    long NResidual = NOpt * NSwap;
    double* ResidualArray = make_array(NResidual);

    long nparams;
    if (FixedKappaFlag != 1) nparams = 1 + NHW;
    else nparams = NHW;

    double* params = make_array(nparams);
    double* paramsup = make_array(nparams);
    double* paramsdn = make_array(nparams);
    double** tempjacov = make_array(NResidual, nparams);
    double RMPSE = 0.0;

    if (FixedKappaFlag != 1)
    {
        params[0] = kappa;
        for (i = 0; i < NHW; i++) params[i + 1] = HWVol[i];
    }
    else
    {
        for (i = 0; i < NHW; i++) params[i] = HWVol[i];
    }

    Levenberg_Marquardt_HWSwaption(nparams, params, NZero, ZeroTerm, ZeroRate,
        NHW, HWTerm, NResidual, BSSwaptionPrice, Strike,
        HWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, OptMaturityDates,
        nDates, dates, PT, paramsup, paramsdn,
        tempjacov, FixedKappaFlag, FixedKappa, RMPSE);

    if (FixedKappaFlag != 1)
    {
        kappa = params[0];
        for (i = 0; i < NHW; i++) HWVol[i] = params[i + 1];
    }
    else
    {
        kappa = FixedKappa;
        for (i = 0; i < NHW; i++) HWVol[i] = params[i];
    }

    free(TermSwapNew);
    free(TermOptNew);
    free(BSSwaptionPrice);
    free(HWSwaptionPrice);
    free(OptMaturityDates);
    free(nDates);
    for (i = 0; i < NOpt * NSwap; i++) free(dates[i]);
    free(dates);
    for (i = 0; i < NOpt * NSwap; i++) free(PT[i]);
    free(PT);
    free(params);
    free(paramsup);
    free(paramsdn);
    for (i = 0; i < NResidual; i++) free(tempjacov[i]);
    free(tempjacov);
    free(ResidualArray);

    return (long)(RMPSE*10000.0);
}


void Gradients_HJM_2F(long NLoop, long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_J, double** JT_Res, double* Initial_Params, double RMPSE, double* ArgminParams)
{
    long i;
    double mu = *lambda;
    double min_params, max_params;
    double MIN_kappa = 0.001;
    double MAX_kappa = 0.2;
    double MAX_kappa1 = 0.1;
    double MAX_kappa2 = 1.1;

    double MIN_Vol = 0.0001;
    double MAX_Vol = 0.3;
    double MIN_RHO = -0.95;
    double MAX_RHO = 0.95;

    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };
    long Shape_JT[2] = { m,n };
    long Shape_Residual[2] = { n,1 };

    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);
    double* UnKnown = (double*)malloc(sizeof(double) * m);
    for (i = 0; i < m; i++)  UnKnown[i] = JT_Res[i][0] * 2.0 * mu;

    for (i = 0; i < NParams; i++)
    {
        NextParams[i] = CurrentParams[i] - UnKnown[i];
        if (i == 0 || i == 1)
        {
            if (i == 0) MAX_kappa = MAX_kappa1;
            else MAX_kappa = MAX_kappa2;
            min_params = MIN_kappa;
            max_params = MAX_kappa;
        }
        else if (i == 2 || i == 3)
        {
            min_params = MIN_Vol;
            max_params = MAX_Vol;
        }
        else
        {
            min_params = MIN_RHO;
            max_params = MAX_RHO;
        }


        if (NextParams[i] > max_params || NextParams[i] < min_params)
        {
            if (NLoop == 0) NextParams[i] = max(min_params, min(max_params, Initial_Params[i]));
            else NextParams[i] = max(min_params, min(max_params, ArgminParams[i]));
        }
    }

    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(UnKnown[i]);
    ParamSum = s;
    free(UnKnown);
}

void Levenberg_HJM_2F(long NLoop, long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_J, double** JT_Res, double* Initial_Params, double RMPSE, double* ArgminParams)
{
    long i;
    double mu = *lambda;
    double min_params, max_params;
    double MIN_kappa = 0.001;
    double MAX_kappa = 0.2;
    double MAX_kappa1 = 0.4;
    double MAX_kappa2 = 1.0;

    double MIN_Vol = 0.00001;
    double MAX_Vol = 0.3;
    double MIN_RHO = -0.9;
    double MAX_RHO = 0.9;

    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };
    long Shape_JT[2] = { m,n };
    long Shape_Residual[2] = { n,1 };
    
    // J' dot J                 Shape = m * m
    XprimeDotX(Jacov, Shape_J, JT_J);

    // J'J + mu * diag(J'J)     Shape = m * m
    for (i = 0; i < m; i++) JT_J[i][i] = JT_J[i][i] + mu;// *JT_J[i][i];

    // inv(J'J + mu * diag(J'J))
    long Shape_Inv_JT_J[2] = { m,m };
    //MatrixInversion(JT_J, m, Inverse_JT_J);

    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    double* Known = (double*)malloc(sizeof(double) * m);
    double* UnKnown = (double*)malloc(sizeof(double) * m);
    for (i = 0; i < m; i++) Known[i] = JT_Res[i][0];

    gaussian_elimination(JT_J, Known, UnKnown, m);
    
    for (i = 0; i < NParams; i++)
    {
        NextParams[i] = CurrentParams[i] - UnKnown[i];
        if (i == 0 || i == 1)
        {
            if (i == 0) MAX_kappa = MAX_kappa1;
            else MAX_kappa = MAX_kappa2;
            min_params = MIN_kappa;
            max_params = MAX_kappa;
        }
        else if (i == 2 || i == 3)
        {
            min_params = MIN_Vol;
            max_params = MAX_Vol;
        }
        else
        {
            min_params = MIN_RHO;
            max_params = MAX_RHO;
        }


        if (NextParams[i] > max_params || NextParams[i] < min_params)
        {
            if (NLoop == 0) NextParams[i] = max(min_params, min(max_params, Initial_Params[i]));
            else NextParams[i] = max(min_params, min(max_params, ArgminParams[i]));
        }
    }

    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(UnKnown[i]);
    ParamSum = s;
    free(UnKnown);
    free(Known);
}

/*
void Gradient_Decent_HWSwaption_2F(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    double rho,
    double* HWVol12_Temp,
    double& RMPSE
)
{

    long i, j;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long Levenberg = 1;
    long ngrad = 0;

    double* InitialParams = (double*)malloc(sizeof(double) * (NParams));
    for (i = 0; i < NParams; i++) InitialParams[i] = Params[i];

    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 0.005 };
    double* NextParams = (double*)malloc(sizeof(double) * (NParams));
    double** JT_Res = make_array(NParams, 1);
    double** PrevJacov = make_array(NResidual, NParams);
    double* PrevResidual = make_array(NResidual);
    double* argminparam = (double*)malloc(sizeof(double) * (NParams));
    double* prevparam = (double*)malloc(sizeof(double) * (NParams));
    double minrmpse = 100000.0;
    double prevrmpse = 100000.0;
    const long nQuad = 13;
    double x[13] = { 0.0 , };
    double w[13] = { 0.0, };
    for (n = 0; n < 6; n++)
    {

        make_Jacov_HWSwaption_2F(n, NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_Temp, nQuad, x, w);

        make_Residual_HWSwaption_2F(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, absErrorSum, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_Temp, RMPSE, nQuad, x, w);

        if (n >= 1)
        {
            if (absErrorSum < minerror || n == 1)
            {
                minerror = absErrorSum;
                minrmpse = RMPSE;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                if (RMPSE < 0.1) break;
            }
            if (absErrorSum < PrevAbsErrorSum) lambda[0] *= 0.7;
            else
            {
                for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) TempJacovMatrix[i][j] = PrevJacov[i][j];
                for (i = 0; i < NResidual; i++) ResidualArray[i] = PrevResidual[i];
                for (i = 0; i < NParams; i++) Params[i] = prevparam[i];
                lambda[0] *= 0.7;
            }
        }

        for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) PrevJacov[i][j] = TempJacovMatrix[i][j];
        for (i = 0; i < NResidual; i++) PrevResidual[i] = ResidualArray[i];

        GradientDecent_2F(n, NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_Res, FixedKappaFlag, InitialParams, RMPSE, argminparam);
        for (i = 0; i < NParams; i++)
        {
            prevparam[i] = Params[i];
            Params[i] = NextParams[i];
        }

        if (ParamSum < StopCondition && n > 10) break;
        if (minrmpse <= 0.1) break;
        PrevAbsErrorSum = absErrorSum;
        prevrmpse = RMPSE;
    }

    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];
    RMPSE = minrmpse;

    free(InitialParams);
    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    free(argminparam);
    free(prevparam);
    for (i = 0; i < NResidual; i++) free(PrevJacov[i]);
    free(PrevJacov);
    free(PrevResidual);
}
*/

void make_Residual_HJM_2F(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double& absErrorSum,
    double& RMPSE,
    long nQuad,
    double* x_array,
    double* w_array
)
{
    long i, n;
    double kappa;
    double kappa2;
    double* HWVol;
    double* HWVol2;

    double s = 0.0;
    double p, r2, tss, bs_meanprice;
    RMPSE = 0.0;
    double TempVol12[1] = { 0.001 };
    double TempTerm[1] = { 1.0 };
    double Vol1[1] = { 0.001 };
    double Vol2[1] = { 0.001 };
    Vol1[0] = Params[2];
    Vol2[0] = Params[3];
    TempVol12[0] = sqrt(fabs(Params[2] * Params[3]));

    bs_meanprice = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        TempHWSwaptionPrice[i] = Swaption2F(1.0, Params[0], Params[1], TempTerm, Vol1, Vol2, TempVol12, 1, Params[4], StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);
        bs_meanprice += BSSwaptionPrice[i] / (double)NResidual;
    }

    tss = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = (BSSwaptionPrice[i] - TempHWSwaptionPrice[i]);
        p = 0.5 * BSSwaptionPrice[i] + 0.5 * TempHWSwaptionPrice[i];
        r2 = ResidualArray[i] * ResidualArray[i];
        tss += (BSSwaptionPrice[i] - bs_meanprice) * (BSSwaptionPrice[i] - bs_meanprice);
        s += r2;
    }

    RMPSE = 0.0;
    for (i = 0; i < NResidual; i++) RMPSE += ((ResidualArray[i] / BSSwaptionPrice[i]) * (ResidualArray[i] / BSSwaptionPrice[i]));
    RMPSE = sqrt(RMPSE);

    absErrorSum = s;
}

void make_Jacov_HJMSwaption_2F(
    long NLoop,
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long nQuad,
    double* x_array,
    double* w_array
)
{
    long i;
    long j;
    long n;

    double dhwvol_up = 0.001;
    double dkappa_up = 0.01;
    double drho_up = 0.03;
    double TempTerm[1] = { 1.0 };
    double TempVol12[1] = { 0.001 };
    double rho_up, rho_dn;
    if (NLoop == 0)
    {
        dhwvol_up *= 10.0;
        dkappa_up *= 10.0;
        drho_up *= 10.0;
    }

    double kappa_up;
    double kappa_dn;
    double kappa_up2;
    double kappa_dn2;

    double HWVol_up[1] = { 0.0001 };
    double HWVol_dn[1] = { 0.0001 };
    double HWVol_up2[1] = { 0.0001 };
    double HWVol_dn2[1] = { 0.0001 };

    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double dParams;
    double temp = 0.0;
    long breakflag = 0;

    for (i = 0; i < NResidual; i++)
    {
        for (j = 0; j < NParams; j++)
        {
            breakflag = 0;

            // 파라미터 초기화
            for (n = 0; n < NParams; n++) {
                ParamsUp[n] = Params[n];
                ParamsDn[n] = Params[n];
            }

            // 파라미터 Up And Dn
            if (j == 0 || j == 1)
            {
                // kappa1, kappa2
                ParamsUp[j] = Params[j] + dkappa_up;
                ParamsDn[j] = max(0.00001, Params[j] - dkappa_up);
            }
            else if (j == 2 || j == 3)
            {
                ParamsUp[j] = Params[j] + dhwvol_up;
                ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
            }
            else
            {
                ParamsUp[j] = min(0.99, Params[j] + drho_up);
                ParamsDn[j] = max(-0.99, Params[j] - drho_up);
            }
            dParams = (ParamsUp[j] - ParamsDn[j]);

            kappa_up = ParamsUp[0];
            kappa_dn = ParamsDn[0];
            kappa_up2 = ParamsUp[1];
            kappa_dn2 = ParamsDn[1];

            HWVol_up[0] = ParamsUp[2];
            HWVol_dn[0] = ParamsDn[2];
            HWVol_up2[0] = ParamsUp[3];
            HWVol_dn2[0] = ParamsDn[3];
            rho_up = ParamsUp[4];
            rho_dn = ParamsDn[4];
            TempVol12[0] = sqrt(fabs(HWVol_up[0] * HWVol_up2[0]));
            Pup = Swaption2F(1.0, ParamsUp[0], ParamsUp[1], TempTerm, HWVol_up, HWVol_up2, TempVol12, 1, rho_up, StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);
            ErrorUp = BSSwaptionPrice[i] - Pup;

            TempVol12[0] = sqrt(fabs(HWVol_dn[0] * HWVol_dn2[0]));
            Pdn = Swaption2F(1.0, ParamsDn[0], ParamsDn[1], TempTerm, HWVol_dn, HWVol_dn2, TempVol12, 1, rho_dn, StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);
            ErrorDn = BSSwaptionPrice[i] - Pdn;

            TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
        }
    }
}



void Gradient_Decent_HJM_2FCalib(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    double* lambda,
    double& RMPSE
)
{

    long i, j;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long nstack = 0;

    double* InitialParams = (double*)malloc(sizeof(double) * (NParams));
    for (i = 0; i < NParams; i++) InitialParams[i] = Params[i];

    double FirstError;
    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double* NextParams = (double*)malloc(sizeof(double) * (NParams));
    double** JT_Res = make_array(NParams, 1);
    double** JT_J = make_array(NParams, NParams);
    double** PrevJacov = make_array(NResidual, NParams);
    double* PrevResidual = make_array(NResidual);
    double argminmultiple = lambda[0];
    double firstrmspe = 0.;
    double* argminparam = (double*)malloc(sizeof(double) * (NParams));
    double* prevparam = (double*)malloc(sizeof(double) * (NParams));
    double* argminprice = (double*)malloc(sizeof(double) * (NResidual));
    double* firstprice = (double*)malloc(sizeof(double) * (NResidual));
    double* firstparam = (double*)malloc(sizeof(double) * (NParams));
    double minrmpse = 100000.0;
    double prevrmpse = 100000.0;
    const long nQuad = 13;
    double x[13] = { 0.0 , };
    double w[13] = { 0.0, };
    for (n = 0; n < 15; n++)
    {

        make_Jacov_HJMSwaption_2F(n, NParams, Params, NZero, ZeroTerm, ZeroRate,
            NResidual, BSSwaptionPrice, StrikePrice,
            ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, ParamsUp, ParamsDn, TempJacovMatrix, nQuad, x, w);

        make_Residual_HJM_2F(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, absErrorSum, RMPSE, nQuad, x, w);

        if (n >= 1)
        {
            //NextLambda(absErrorSum, PrevAbsErrorSum, lambda, BreakFlag);
            if (absErrorSum < minerror || n == 1)
            {
                minerror = absErrorSum;
                argminmultiple = lambda[0];
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                for (i = 0; i < NResidual; i++) argminprice[i] = TempHWSwaptionPrice[i];
            }

            if (absErrorSum < PrevAbsErrorSum)
            {
                // 에러가 감소하였으면 멀티플을 줄이자
                lambda[0] *= 0.8;
                nstack = 0;
            }
            else
            {
                // 에러가 증가하였으면 스택+1
                nstack += 1;
                for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) TempJacovMatrix[i][j] = PrevJacov[i][j];
                for (i = 0; i < NResidual; i++) ResidualArray[i] = PrevResidual[i];
                for (i = 0; i < NParams; i++) Params[i] = prevparam[i];                
            }

            if (nstack >= 3)
            {
                // 3스택이 쌓이면 최저오차 파라미터로부터 작은 멀티플로 다시시작
                for (i = 0; i < NParams; i++) Params[i] = argminparam[i];
                lambda[0] = argminmultiple * 0.5;
                make_Jacov_HJMSwaption_2F(n, NParams, Params, NZero, ZeroTerm, ZeroRate,
                    NResidual, BSSwaptionPrice, StrikePrice,
                    ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
                    OptMaturityDates,
                    nDates, dates, termdates, TempC, PT, ParamsUp, ParamsDn, TempJacovMatrix, nQuad, x, w);

                make_Residual_HJM_2F(NParams, Params, NZero, ZeroTerm, ZeroRate,
                    NResidual, BSSwaptionPrice, StrikePrice,
                    TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
                    OptMaturityDates,
                    nDates, dates, termdates, TempC, PT, absErrorSum, RMPSE, nQuad, x, w);
            }
        }
        else
        {
            for (i = 0; i < NParams; i++) firstparam[i] = Params[i];
            for (i = 0; i < NResidual; i++) firstprice[i] = TempHWSwaptionPrice[i];
            FirstError = absErrorSum;
            firstrmspe = RMPSE;
        }

        for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) PrevJacov[i][j] = TempJacovMatrix[i][j];
        for (i = 0; i < NResidual; i++) PrevResidual[i] = ResidualArray[i];

        Gradients_HJM_2F(n, NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, JT_Res, InitialParams, RMPSE, argminparam);
        for (i = 0; i < NParams; i++)
        {
            prevparam[i] = Params[i];
            Params[i] = NextParams[i];
        }

        if (ParamSum < StopCondition && n > 20) break;
        if (minrmpse <= 0.01) break;
        PrevAbsErrorSum = absErrorSum;
        prevrmpse = RMPSE;
    }

    if (FirstError < minerror)
    {
        for (i = 0; i < NParams; i++)
        {
            Params[i] = firstparam[i];
            TempHWSwaptionPrice[i] = firstprice[i];
        }
        RMPSE = firstrmspe;
    }
    else
    {
        for (i = 0; i < NParams; i++)
        {
            Params[i] = argminparam[i];
            TempHWSwaptionPrice[i] = argminprice[i];
        }
        RMPSE = minrmpse;
    }

    free(argminprice);
    free(InitialParams);
    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    free(JT_J);
    free(argminparam);
    free(prevparam);
    for (i = 0; i < NResidual; i++) free(PrevJacov[i]);
    free(PrevJacov);
    free(PrevResidual);
    free(firstprice);
    free(firstparam);
}

long Gradientdecent_HJM2F_Calibration_Swaption_ForKDBMurex(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NSwaption,

    double* T_OptMaturity,
    double* Term_SwapMat,
    double* SwaptionVol,
    double FreqMonthSwaption,

    double* HWVol,
    double* HWVol2,
    double& kappa,
    double& kappa2,
    double& rho12,
    long lognormalvol0normalvol1,
    double* ResultBlackPrice,
    double* ResultHWPrice,
    double* ResultError
)
{
    long i, j, k, n;
    double* BSSwaptionPrice = (double*)malloc(sizeof(double) * NSwaption);                                          // 할당 1                   
    double* HWSwaptionPrice = (double*)malloc(sizeof(double) * NSwaption);                                          // 할당 2
    double* Strike = (double*)malloc(sizeof(double) * NSwaption);                                                   // 할당 3

    for (k = 0; k < NSwaption; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, T_OptMaturity[k], Term_SwapMat[k], FreqMonthSwaption);
        BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, T_OptMaturity[k], Term_SwapMat[k], FreqMonthSwaption, lognormalvol0normalvol1);
        ResultBlackPrice[k] = BSSwaptionPrice[k];
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * NSwaption);                                               // 할당 4
    for (i = 0; i < NSwaption; i++) OptMaturityDates[i] = (long)(T_OptMaturity[i] * 365.0);

    long* nDates = (long*)malloc(sizeof(long) * NSwaption);                                                         // 할당 5
    for (i = 0; i < NSwaption; i++) nDates[i] = Number_Of_Payment(T_OptMaturity[i], T_OptMaturity[i] + Term_SwapMat[i], FreqMonthSwaption);

    long** dates = (long**)malloc(sizeof(long*) * NSwaption);                                                       // 할당 6
    double** termdates = (double**)malloc(sizeof(double*) * NSwaption);                                             // 할당 7
    double** TempC = (double**)malloc(sizeof(double*) * NSwaption);                                                 // 할당 8
    for (i = 0; i < NSwaption; i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        termdates[i] = (double*)malloc(sizeof(double) * nDates[i]);
        TempC[i] = (double*)malloc(sizeof(double) * nDates[i]);
        PaymentDatesMapping(T_OptMaturity[i] + Term_SwapMat[i], FreqMonthSwaption, dates[i], nDates[i]);
        for (j = 0; j < nDates[i]; j++) termdates[i][j] = ((double)dates[i][j]) / 365.0;
    }

    double** PT = (double**)malloc(sizeof(double*) * NSwaption);                                                    // 할당 9
    for (i = 0; i < NSwaption; i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, T_OptMaturity[i]);
        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    double* P0_at_OptMaturityDates = (double*)malloc(sizeof(double) * NSwaption);                                   // 할당 10
    for (i = 0; i < NSwaption; i++) P0_at_OptMaturityDates[i] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, T_OptMaturity[i]);

    long NResidual = NSwaption;
    double* ResidualArray = (double*)malloc(sizeof(double) * (NResidual));                                          // 할당 11

    long nparams;
    nparams = 5; // kappa, kappa2, sig1, sig2, rho

    double* params = (double*)malloc(sizeof(double) * (nparams));                                                   // 할당 12
    double* paramsup = (double*)malloc(sizeof(double) * (nparams));                                                 // 할당 13
    double* paramsdn = (double*)malloc(sizeof(double) * (nparams));                                                 // 할당 14
    double** tempjacov = (double**)malloc(sizeof(double*) * NResidual);                                             // 할당 15
    for (i = 0; i < NResidual; i++) tempjacov[i] = (double*)malloc(sizeof(double) * nparams);                       

    double RMPSE = 0.0;
    params[0] = max(0.0001,min(2.0,kappa));
    params[1] = max(0.0001,min(2.0,kappa2));
    params[2] = min(max(0.001,HWVol[0]),0.04);
    params[3] = min(max(0.001,HWVol2[0]),0.04);
    params[4] = min(0.999, max(-0.999, rho12));
    double lambda[1] = { 0.2 };
    double firstlambda = lambda[0];
    double lambdaup[1] = { 0.5 };
    double lambdadn[1] = { 0.05 };
    Gradient_Decent_HJM_2FCalib(nparams, params, NZero, ZeroTerm, ZeroRate,
        NResidual, BSSwaptionPrice, Strike, HWSwaptionPrice, ResidualArray,
        Term_SwapMat, T_OptMaturity, P0_at_OptMaturityDates, OptMaturityDates, nDates,
        dates, termdates, TempC, PT, paramsup,
        paramsdn, tempjacov, lambda, RMPSE);

    if (firstlambda == lambda[0])
    {
        // 파라미터가 안변했을 경우
        firstlambda = lambdaup[0];
        Gradient_Decent_HJM_2FCalib(nparams, params, NZero, ZeroTerm, ZeroRate,
            NResidual, BSSwaptionPrice, Strike, HWSwaptionPrice, ResidualArray,
            Term_SwapMat, T_OptMaturity, P0_at_OptMaturityDates, OptMaturityDates, nDates,
            dates, termdates, TempC, PT, paramsup,
            paramsdn, tempjacov, lambdaup, RMPSE);
    }

    if (firstlambda == lambdaup[0])
    {
        // 파라미터가 또 안변했을 경우
        Gradient_Decent_HJM_2FCalib(nparams, params, NZero, ZeroTerm, ZeroRate,
            NResidual, BSSwaptionPrice, Strike, HWSwaptionPrice, ResidualArray,
            Term_SwapMat, T_OptMaturity, P0_at_OptMaturityDates, OptMaturityDates, nDates,
            dates, termdates, TempC, PT, paramsup,
            paramsdn, tempjacov, lambdadn, RMPSE);
    }

    if (params[2] == 0.001 || params[3] == 0.001)
    {
        // 그 외에 이상한 값이 나오는 경우 초기화하고 다시계산
        if (params[2] == 0.001) params[2] = 0.015;
        if (params[3] == 0.001) params[3] = 0.015;
        lambda[0] = firstlambda;
        Gradient_Decent_HJM_2FCalib(nparams, params, NZero, ZeroTerm, ZeroRate,
            NResidual, BSSwaptionPrice, Strike, HWSwaptionPrice, ResidualArray,
            Term_SwapMat, T_OptMaturity, P0_at_OptMaturityDates, OptMaturityDates, nDates,
            dates, termdates, TempC, PT, paramsup,
            paramsdn, tempjacov, lambda, RMPSE);
    }


    kappa = params[0];
    kappa2 = params[1];
    HWVol[0] = params[2];
    HWVol2[0] = params[3];
    rho12 = params[4];

    for (i = 0; i < NSwaption; i++)
    {
        ResultBlackPrice[i] = BSSwaptionPrice[i];
        ResultHWPrice[i] = HWSwaptionPrice[i];
        ResultError[i] = BSSwaptionPrice[i] - HWSwaptionPrice[i];
    }

    free(BSSwaptionPrice);  //1
    free(HWSwaptionPrice);  //2
    free(Strike);           //3

    free(OptMaturityDates); //4
    free(nDates);           //5

    for (i = 0; i < NSwaption; i++) free(dates[i]);                           
    free(dates);            //6
    for (i = 0; i < NSwaption; i++) free(termdates[i]);                       
    free(termdates);        //7
    for (i = 0; i < NSwaption; i++) free(TempC[i]);                          
    free(TempC);            //8

    for (i = 0; i < NSwaption; i++) free(PT[i]);
    free(PT);               //9

    free(P0_at_OptMaturityDates);   //10
    free(ResidualArray);            //11
    free(params);                   //12
    free(paramsup);                 //13
    free(paramsdn);                 //14
    for (i = 0; i < NResidual; i++) free(tempjacov[i]);
    free(tempjacov);                //15
    return 1;
}

long HW_LevMarq_Calibration_Swaption_ForKDBMurex(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NSwaption,

    double* T_OptMaturity,
    double* Term_SwapMat,
    double* SwaptionVol,
    double FreqMonthSwaption,
    long NHW_initial,

    long NHW,
    double* HWTerm,
    double* HWVol,
    double& kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1,
    double* ResultBlackPrice,
    double* ResultHWPrice,
    double* ResultError
)
{
    long i, j, k, n;
    double* BSSwaptionPrice = (double*)malloc(sizeof(double) * NSwaption);
    double* HWSwaptionPrice = (double*)malloc(sizeof(double) * NSwaption);
    double* Strike= (double*)malloc(sizeof(double) * NSwaption);

    for (k = 0; k < NSwaption; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, T_OptMaturity[k], Term_SwapMat[k], FreqMonthSwaption);
        BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, T_OptMaturity[k], Term_SwapMat[k], FreqMonthSwaption, lognormalvol0normalvol1);
        ResultBlackPrice[k] = BSSwaptionPrice[k];
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * NSwaption);
    for (i = 0; i < NSwaption; i++) OptMaturityDates[i] = (long)(T_OptMaturity[i] * 365.0);

    long* nDates = (long*)malloc(sizeof(long) * NSwaption);
    for (i = 0; i < NSwaption; i++) nDates[i] = Number_Of_Payment(T_OptMaturity[i], T_OptMaturity[i] + Term_SwapMat[i], FreqMonthSwaption);

    long** dates = (long**)malloc(sizeof(long*) * NSwaption);
    for (i = 0; i < NSwaption; i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        PaymentDatesMapping(T_OptMaturity[i] + Term_SwapMat[i], FreqMonthSwaption, dates[i], nDates[i]);
    }

    double** PT = (double**)malloc(sizeof(double*) * NSwaption);
    for (i = 0; i < NSwaption; i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, T_OptMaturity[i]);
        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    long NResidual = NSwaption;
    double* ResidualArray = (double*)malloc(sizeof(double) * (NResidual));

    long nparams;
    if (FixedKappaFlag != 1) nparams = 1 + NHW;
    else nparams = NHW;

    double* params = (double*)malloc(sizeof(double) * (nparams));
    double* paramsup = (double*)malloc(sizeof(double) * (nparams));
    double* paramsdn = (double*)malloc(sizeof(double) * (nparams));
    double** tempjacov = (double**)malloc(sizeof(double*) * NResidual);
    for (i = 0; i < NResidual; i++) tempjacov[i] = (double*)malloc(sizeof(double) * nparams);

    double RMPSE = 0.0;

    if (FixedKappaFlag != 1)
    {
        params[0] = kappa;
        for (i = 0; i < NHW; i++) params[i + 1] = HWVol[i];
    }
    else
    {
        for (i = 0; i < NHW; i++) params[i] = HWVol[i];
    }

    Levenberg_Marquardt_HWSwaptionForKDBMurex(nparams, params, NZero, ZeroTerm, ZeroRate,
        NHW, HWTerm, NResidual, BSSwaptionPrice, Strike,
        HWSwaptionPrice, ResidualArray, Term_SwapMat, T_OptMaturity, OptMaturityDates,
        nDates, dates, PT, paramsup, paramsdn,
        tempjacov, FixedKappaFlag, FixedKappa, RMPSE);

    for (i = 0; i < NSwaption; i++)
    {
        ResultBlackPrice[i] = BSSwaptionPrice[i];
        ResultHWPrice[i] = HWSwaptionPrice[i];
        ResultError[i] = BSSwaptionPrice[i] - HWSwaptionPrice[i];
    }

    if (FixedKappaFlag != 1)
    {
        kappa = params[0];
        for (i = 0; i < NHW; i++) HWVol[i] = params[i + 1];
    }
    else
    {
        kappa = FixedKappa;
        for (i = 0; i < NHW; i++) HWVol[i] = params[i];
    }

    free(BSSwaptionPrice);
    free(HWSwaptionPrice);
    free(Strike);
    free(OptMaturityDates);
    free(nDates);
    for (i = 0; i < NSwaption; i++) free(dates[i]);
    free(dates);
    for (i = 0; i < NSwaption; i++) free(PT[i]);
    free(PT);
    free(ResidualArray);
    free(params);
    free(paramsup);
    free(paramsdn);
    for (i = 0; i < NResidual; i++) free(tempjacov[i]);
    free(tempjacov);
    return 1;
}

DLLEXPORT(long) HJM2FCalibrationForKDB(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NSwaption,
    double* T_OptMaturity,

    double* Term_SwapMat,
    double* SwaptionVol,
    double FreqMonthSwaption,
    double* HWVol_initial,
    double* HWVol_initial2,

    double* initial_kappa,
    double* initial_kappa2,
    double* rho,
    long lognormalvol0normalvol1,
    double* ResultBlackPrice,

    double* ResultHWPrice,
    double* ResultError
)
{
    long i;
    long ResultCode = 0;
    //_CrtSetBreakAlloc(161);

    long NHW = 1;
    double* HWTerm;
    double* HWVol;
    double kappa = initial_kappa[0];
    HWTerm = T_OptMaturity;

    ResultCode = Gradientdecent_HJM2F_Calibration_Swaption_ForKDBMurex(
        NZero,
        ZeroTerm,
        ZeroRate,
        NSwaption,

        T_OptMaturity,
        Term_SwapMat,
        SwaptionVol,
        FreqMonthSwaption,

        HWVol_initial,
        HWVol_initial2,
        initial_kappa[0],
        initial_kappa2[0],
        rho[0],
        lognormalvol0normalvol1,
        ResultBlackPrice,
        ResultHWPrice,
        ResultError
    );

    return ResultCode;
}


DLLEXPORT(long) HWCapHWSwaptionCalibrationForKDB(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NSwaption,
    double* T_OptMaturity,

    double* Term_SwapMat,
    double* SwaptionVol,
    double FreqMonthSwaption,
    long NHW_initial,
    double* HWTerm_initial,

    double* HWVol_initial,
    double* initial_kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1,

    double* ResultBlackPrice,
    double* ResultHWPrice,
    double* ResultError
    )
{
    long i;
    long ResultCode = 0;
    //_CrtSetBreakAlloc(161);

    long NHW = 1;
    double* HWTerm;
    double* HWVol;
    double kappa = initial_kappa[0];
    HWTerm = T_OptMaturity;
    NHW = min(NSwaption, NHW_initial);
    HWVol = (double*)malloc(sizeof(double) * NHW);
    for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);

    ResultCode = HW_LevMarq_Calibration_Swaption_ForKDBMurex(
        NZero,
        ZeroTerm,
        ZeroRate,
        NSwaption,

        T_OptMaturity,
        Term_SwapMat,
        SwaptionVol,
        FreqMonthSwaption,
        NHW_initial,

        NHW,
        HWTerm,
        HWVol,
        kappa,
        FixedKappaFlag,
        FixedKappa,
        lognormalvol0normalvol1,
        ResultBlackPrice,
        ResultHWPrice,
        ResultError
    );

    for (i = 0; i < NHW; i++)
    {
        HWTerm_initial[i] = HWTerm[i];
        HWVol_initial[i] = HWVol[i];
        *initial_kappa = kappa;
    }
    free(HWVol);
    return ResultCode;
}

DLLEXPORT(long) HWCapHWSwaptionCalibration(
    long CaliFlag,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double FreqMonthSwaption,

    long NCap,
    double* TermCap,
    double* CapVol,
    double FreqMonthCap,

    long NHW_initial,
    double* HWTerm_initial,
    double* HWVol_initial,
    double* initial_kappa,
    long FixedKappaFlag,
    double FixedKappa,
    long lognormalvol0normalvol1
)
{
    long i;
    long ResultCode = 0;
    //_CrtSetBreakAlloc(161);

    long NHW = 4;
    double* HWTerm;
    double* HWVol;

    double* Strike = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    double kappa = initial_kappa[0];
    if (NCap == 0 && NSwap * NOpt > 0 || CaliFlag == 1)
    {
        HWTerm = TermOpt;
        NHW = min(NOpt, NHW_initial);
        HWVol = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);
        ResultCode = HW_LevMarq_Calibration_Swaption(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap, TermSwap, SwaptionVol, Strike, FreqMonthSwaption,
            NHW, HWTerm, HWVol, kappa, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1);
        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            *initial_kappa = kappa;
        }
        free(HWVol);
    }
    else if (NCap > 0 && CaliFlag == 2)
    {
        NOpt = 0;
        NSwap = 0;
        if (NOpt > NCap)
        {
            HWTerm = TermOpt;
            NHW = min(NHW_initial, NOpt);
        }
        else {
            HWTerm = TermCap;
            NHW = min(NHW_initial, NCap);
        }
        HWVol = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);

        ResultCode = HW_GradDecent_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap, TermSwap, SwaptionVol, Strike,
            NCap, TermCap, CapVol, FreqMonthCap, FreqMonthCap,
            NHW, HWTerm, HWVol, kappa, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1);
        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            *initial_kappa = kappa;
        }
        free(HWVol);
    }
    else if ((NCap > 0 && NSwap * NOpt > 0 && CaliFlag == 0))
    {
        if (NOpt > NCap)
        {
            HWTerm = TermOpt;
            NHW = min(NHW_initial, NOpt);
        }
        else {
            HWTerm = TermCap;
            NHW = min(NHW_initial, NCap);
        }
        HWVol = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);
        ResultCode = HW_LevMarq_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap, TermSwap, SwaptionVol, Strike, FreqMonthSwaption, NCap, TermCap, CapVol,
            NHW, HWTerm, HWVol, kappa, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1);
        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            *initial_kappa = kappa;
        }
        free(HWVol);
    }


    free(Strike);
    _CrtDumpMemoryLeaks();
    return ResultCode;
}

void _stdcall SNormExp(double* x, double* w, long N)
{
    long i, j, its, m;
    double p1, p2, p3, pp, z, z1;
    double pim4, tol;
    //	double PI = 4.0*atan(1.0);

    tol = 3.0e-14;
    pim4 = 0.7511255444649425;// 1.0 / pow(PI, 0.25);

    m = (N + 1) / 2;

    for (i = 0; i < m; i++) {
        switch (i) {
        case 0:
            z = sqrt(2.0 * N + 1.0) - 1.85575 * pow(2.0 * N + 1.0, -0.16667);
            break;
        case 1:
            z = z - 1.14 * pow(N, 0.426) / z;
            break;
        case 2:
            z = 1.86 * z - 0.86 * x[0];
            break;
        case 3:
            z = 1.91 * z - 0.91 * x[1];
            break;
        default:
            z = 2.0 * z - x[i - 2];
        }

        for (its = 1; its <= 10; its++) {
            p1 = pim4;
            p2 = 0.0;
            for (j = 1; j <= N; j++) {
                p3 = p2;
                p2 = p1;
                p1 = z * sqrt(2.0 / (double)j) * p2 - sqrt((double)(j - 1) / (double)j) * p3;
            }

            pp = sqrt(2.0 * (double)N) * p2;
            z1 = z;
            z = z1 - p1 / pp;

            if (fabs(z - z1) < tol) break;
        }

        x[i] = z;
        x[N - 1 - i] = -z;
        w[i] = 2.0 / (pp * pp);
        w[N - 1 - i] = w[i];
    }

    for (i = 0; i < N; i++) {
        x[i] *= 1.4142135623730951;// sqrt(2.0);
        w[i] /= 1.7724538509055159;// sqrt(PI);
    }
}

void _stdcall NormExp(double* x, double* w, long N, double m, double sigma)
{
    long i;

    SNormExp(x, w, N);

    for (i = 0; i < N; i++) x[i] = m + sigma * x[i];
}

// Find_Sol 함수에서 사용
double func(
    double y,
    double kappa,
    double* c,
    double T,
    double* t,
    long nDates
)
{
    long i;
    double value;

    value = 1.0;

    for (i = 0; i < nDates; i++) value -= c[i] * exp(-B(T, t[i], kappa) * y);
    

    return value;
}

// Swaption2F 함수에 필요한 해찾기
double Find_Sol(
    double kappa,
    double* c,
    double T,
    double* t,
    long nDates
)
{
    double tol = 1.0e-5;
    double low, high, mid;
    double low_value, high_value, mid_value;

    low = -1.0;
    high = 1.0;
    low_value = func(low, kappa, c, T, t, nDates);
    high_value = func(high, kappa, c, T, t, nDates);
    while (low_value * high_value > 0.0) 
    {
        low *= 2.0;
        high *= 2.0;
        low_value = func(low, kappa, c, T, t, nDates);
        high_value = func(high, kappa, c, T, t, nDates);
    }

    while (high - low > tol) {
        mid = (low + high) / 2.0;
        mid_value = func(mid, kappa, c, T, t, nDates);

        if (mid_value == 0.0) return mid;

        if (mid_value * high_value > 0.0) high = mid;
        else low = mid;
    }

    mid = (low + high) / 2.0;

    return mid;
}

// Swaption2F 함수에 필요한 해찾기
double Find_Sol2(
    double kappa,
    double* c,
    double T,
    double* t,
    long nDates
)
{
    long i;
    double tol = 1.0e-5;
    double MinValue, MaxValue, value_a,value_b, value, temp, Error1, Error2;

    MinValue = -1.0;
    MaxValue = 1.0;
    Error1 = func(MinValue, kappa, c, T, t, nDates);
    Error2 = func(MaxValue, kappa, c, T, t, nDates);
    while (Error1 * Error2 > 0.0)
    {
        MinValue *= 2.0;
        MaxValue *= 2.0;
        Error1 = func(MinValue, kappa, c, T, t, nDates);
        Error2 = func(MaxValue, kappa, c, T, t, nDates);
    }

    if (fabs(Error1) < tol) return MinValue;
    if (fabs(Error2) < tol) return MaxValue;
    
    value_a = MinValue + 0.0;
    value_b = MaxValue + 0.0;
    value = (MinValue + MaxValue) / 2.0;
    
    if (Error2 < 0.0 && Error1 > 0.0)
    {
        temp = value_a;
        value_a = value_b;
        value_b = temp;
    }

    for (i = 0; i < 200; i++)
    {
        Error1 = func(value, kappa, c, T, t, nDates);

        if (fabs(Error1) < tol) break;

        if (Error1 > 0.0) value_b = value;
        else value_a = value;
        value = (value_a + value_b) / 2.0;
    }
    if (i == 200) return 0.0;
    else return value;
}

// 2-factor 모형의 적분 int_t^T x(u)+y(u) du의 분산 계산
double V(
    double t,
    double T,
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    double* Vol12,      // 구간 변동성 12 Cross Quadratic
    long nVol,			// 변동성 구간 개수
    double rho			// 상관계수
)
{
    long i;
    double value;

    double exp_minus_kappa1_T = exp(-kappa1 * T);
    double exp_minus2_kappa1_T = exp(-2.0 * kappa1 * T);
    double exp_minus_kappa2_T = exp(-kappa2 * T);
    double exp_minus2_kappa2_T = exp(-2.0 * kappa2 * T);
    double kappa1kappa1 = kappa1 * kappa1;
    double kappa2kappa2 = kappa2 * kappa2;
    double kappa1kappa2 = kappa1 * kappa2;

    value = Integ(T, 1.0, 0.0, tVol, Vol1, nVol) / (kappa1 * kappa1) - Integ(t, 1.0, 0.0, tVol, Vol1, nVol) / (kappa1kappa1)
        - 2.0 * exp_minus_kappa1_T * Integ(T, 1.0, kappa1, tVol, Vol1, nVol) / (kappa1kappa1)
        + 2.0 * exp_minus_kappa1_T * Integ(t, 1.0, kappa1, tVol, Vol1, nVol) / (kappa1kappa1)
        + exp_minus2_kappa1_T * Integ(T, 1.0, 2.0 * kappa1, tVol, Vol1, nVol) / (kappa1kappa1)
        - exp_minus2_kappa1_T * Integ(t, 1.0, 2.0 * kappa1, tVol, Vol1, nVol) / (kappa1kappa1)
        + Integ(T, 1.0, 0.0, tVol, Vol2, nVol) / (kappa2kappa2)
        - Integ(t, 1.0, 0.0, tVol, Vol2, nVol) / (kappa2kappa2)
        - 2.0 * exp_minus_kappa2_T * Integ(T, 1.0, kappa2, tVol, Vol2, nVol) / (kappa2kappa2)
        + 2.0 * exp_minus_kappa2_T * Integ(t, 1.0, kappa2, tVol, Vol2, nVol) / (kappa2kappa2)
        + exp_minus2_kappa2_T * Integ(T, 1.0, 2.0 * kappa2, tVol, Vol2, nVol) / (kappa2kappa2)
        - exp_minus2_kappa2_T * Integ(t, 1.0, 2.0 * kappa2, tVol, Vol2, nVol) / (kappa2kappa2)
        + 2.0 * rho * Integ(T, 1.0, 0.0, tVol, Vol12, nVol) / (kappa1kappa2)
        - 2.0 * rho * Integ(t, 1.0, 0.0, tVol, Vol12, nVol) / (kappa1kappa2)
        - 2.0 * rho * exp_minus_kappa1_T * Integ(T, 1.0, kappa1, tVol, Vol12, nVol) / (kappa1kappa2)
        + 2.0 * rho * exp_minus_kappa1_T * Integ(t, 1.0, kappa1, tVol, Vol12, nVol) / (kappa1kappa2)
        - 2.0 * rho * exp_minus_kappa2_T * Integ(T, 1.0, kappa2, tVol, Vol12, nVol) / (kappa1kappa2)
        + 2.0 * rho * exp_minus_kappa2_T * Integ(t, 1.0, kappa2, tVol, Vol12, nVol) / (kappa1kappa2)
        + 2.0 * rho * exp(-(kappa1 + kappa2) * T) * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol12, nVol) / (kappa1kappa2)
        - 2.0 * rho * exp(-(kappa1 + kappa2) * T) * Integ(t, 1.0, kappa1 + kappa2, tVol, Vol12, nVol) / (kappa1kappa2);

    return value;
}

double V(
    double kappa,
    double kappa2,
    double t,
    double T,
    double vol,
    double vol2
)
{
    return vol * vol2 / (kappa * kappa2) * (T - t + (exp(-kappa * (T - t)) - 1.0) / kappa + (exp(-kappa2 * (T - t)) - 1.0) / kappa2 - (exp(-(kappa + kappa2) * (T - t)) - 1.0) / (kappa + kappa2));
}

double QV(
    double t,
    double T,
    double kappa,
    long NHWVol,
    double* HWVolTerm,
    double* HWVol
)
{
    long i;
    double vol;
    double RHS = 0.0;

    if (NHWVol == 1 || kappa > 0.1)
    {
        vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t);
        RHS = 0.5 * (V(kappa, kappa, t, T, vol, vol) - V(kappa, kappa, 0, T, vol, vol) + V(kappa, kappa, 0, t, vol, vol));
    }
    else
    {
        RHS = 0.0;
        long NInteg = 10;
        double u = t;
        double du = (T - t) / ((double)NInteg);
        double Bst, BsT;
        for (i = 0; i < NInteg; i++)
        {
            vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
            Bst = B(u, t, kappa);
            BsT = B(u, T, kappa);
            RHS += 0.5 * vol * vol * (Bst * Bst - BsT * BsT) * du;
            u = u + du;
        }
    }
    return RHS;
}

double CQV(
    double t,
    double T,
    double kappa,
    long NHWVol,
    double* HWVolTerm,
    double* HWVol,
    double kappa2,
    double* HWVolTerm2,
    double* HWVol2,
    double rho
)
{
    long i;
    double Bst, BsT, vol, vol2;
    double RHS = 0.0;
    double s, ds;

    long NInteg = 10.0;
    double u = t;
    double du = (T - t) / ((double)NInteg);
    RHS = 0.0;
    if (NHWVol > 1)
    {
        vol = 0.5 * Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t) + 0.5 * Interpolate_Linear(HWVolTerm, HWVol, NHWVol, T);
        vol2 = 0.5 * Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t) + 0.5 * Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, T);
    }
    else
    {
        vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t);
        vol2 = Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t);
    }

    RHS = 2.0 * rho * 0.5 * (V(kappa, kappa2, t, T, vol, vol2) - V(kappa, kappa2, 0, T, vol, vol2) + V(kappa, kappa2, 0, t, vol, vol2));
    return RHS;
}

// Swaption2F 함수에서 사용
double A(
    double t,
    double T,
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    double* Vol12,      // 구간 변동성 12 Cross Quadratic
    long nVol,			// 변동성 구간 개수
    double rho,			// 상관계수
    double DF_t,
    double DF_T
)
{
    //double V1 = V(t, T, kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho);
    //double V2 = V(0.0, T, kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho);
    //double V3 = V(0.0, t, kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho);
    //return exp(0.5 * (V1 - V2 + V3)) * DF_T / DF_t;
    return exp(QV(t, T, kappa1, nVol, tVol, Vol1) + QV(t, T, kappa2, nVol, tVol, Vol2) + CQV(t, T, kappa1, nVol, tVol, Vol1, kappa2, tVol, Vol2, rho)) * DF_T/DF_t;
}

// Cap2F 함수에서 사용
double SIGMA(
    double T,
    double S,
    double kappa1,		// 회귀속도1
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    long nVol, 			// 변동성 구간 개수
    double rho,			// 상관계수
    double* Vol12ArrayTemp
)
{
    long i;

    double A = (1.0 - exp(-kappa1 * (S - T))) / kappa1;
    double B = (1.0 - exp(-kappa2 * (S - T))) / kappa2;

    double I1 = A * A * exp(-2.0 * kappa1 * T) * Integ(T, 1.0, 2.0 * kappa1, tVol, Vol1, nVol);
    double I2 = B * B * exp(-2.0 * kappa2 * T) * Integ(T, 1.0, 2.0 * kappa2, tVol, Vol2, nVol);
    double I3 = 2.0 * rho * A * B * exp(-(kappa1 + kappa2) * T) * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol12ArrayTemp, nVol);

    return sqrt(fabs(I1 + I2 + I3));
}

// 2-factor 모형의 Cap 가격 계산
double _stdcall Cap2F(
    double NA,			// 액면금액
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    double* Vol12,      // 구간 변동성12 = sqrt(Vol1 * Vol2)
    long nVol,			// 변동성 구간 개수
    double rho,			// 상관계수
    double StrikeRate,	// 행사금리
    long* Dates,			// 지급일: 계산일로부터 각 지급일까지의 일수
    long nDates,			// 지급 회수(계산일 이후 남은 회수)
    double* P0_t           // 스왑지급일에 P0
)
{
    long i;
    double PrevT, T, delta, A, B, PrevDisc, Disc;
    double value;

    kappa1 = max(kappa1, Tiny_Value);
    kappa2 = max(kappa2, Tiny_Value);

    for (i = 0; i < nVol; i++) {
        if (Vol1[i] < 0.0) Vol1[i] = -Vol1[i];
        if (Vol1[i] < Tiny_Value) Vol1[i] = Tiny_Value;
        if (Vol2[i] < 0.0) Vol2[i] = -Vol2[i];
        if (Vol2[i] < Tiny_Value) Vol2[i] = Tiny_Value;
        Vol12[i] = sqrt(fabs(Vol1[i] * Vol2[i]));
    }

    rho = max(min(rho, 0.9999), -0.9999);

    PrevT = 0.0;
    value = 0.0;
    PrevDisc = 1.0;
    for (i = 0; i < nDates; i++) {
        T = (double)Dates[i] / 365.0;
        delta = T - PrevT;
        Disc = P0_t[i]; 

        if ((i == 0) && (PrevDisc > (1.0 + StrikeRate * delta) * Disc))
        {
            value += PrevDisc - (1.0 + StrikeRate * delta) * Disc;
        }
        else 
        {
            B = SIGMA(PrevT, T, kappa1, kappa2, tVol, Vol1, Vol2, nVol, rho, Vol12);
            A = log(PrevDisc / ((1.0 + StrikeRate * delta) * Disc)) / B;
            value += PrevDisc * CDF_N(A + 0.5 * B) - (1.0 + StrikeRate * delta) * Disc * CDF_N(A - 0.5 * B);
        }

        PrevT = T;
        PrevDisc = Disc;
    }

    return NA * value;
}

// 할인율 계산 
double P0(
    double t,
    double* tDF,			// 할인채 만기
    double* DF,			// 할인채 가격
    long nDF				// 할인채 개수
)
{
    long i;
    double value = 0.0;
    double* R = (double*)malloc(sizeof(double)*(nDF));	//(double *)malloc(nDF*sizeof(double));

    for (i = 0; i < nDF; i++) R[i] = -log(DF[i]) / tDF[i];

    if (t <= tDF[0]) value = exp(-R[0] * t);
    else if (t >= tDF[nDF - 1]) value = exp(-R[nDF - 1] * t);
    else {
        for (i = 0; i < nDF - 1; i++) {
            if (t >= tDF[i] && t < tDF[i + 1]) {
                value = exp(-(R[i] + (R[i + 1] - R[i]) * (t - tDF[i]) / (tDF[i + 1] - tDF[i])) * t);
                break;
            }
        }
    }

    if (R) free(R);

    return value;
}

// 2-factor 모형의 적분 int_t^T x(u)+y(u) du의 분산 계산
double V(
    double t,
    double T,
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    long nVol,			// 변동성 구간 개수
    double rho			// 상관계수
)
{
    long i;
    double value;
    double* Vol = (double*)malloc(nVol * sizeof(double));

    for (i = 0; i < nVol; i++) Vol[i] = sqrt(fabs(Vol1[i] * Vol2[i]));

    value = Integ(T, 1.0, 0.0, tVol, Vol1, nVol) / (kappa1 * kappa1)
        - Integ(t, 1.0, 0.0, tVol, Vol1, nVol) / (kappa1 * kappa1)
        - 2.0 * exp(-kappa1 * T) * Integ(T, 1.0, kappa1, tVol, Vol1, nVol) / (kappa1 * kappa1)
        + 2.0 * exp(-kappa1 * T) * Integ(t, 1.0, kappa1, tVol, Vol1, nVol) / (kappa1 * kappa1)
        + exp(-2.0 * kappa1 * T) * Integ(T, 1.0, 2.0 * kappa1, tVol, Vol1, nVol) / (kappa1 * kappa1)
        - exp(-2.0 * kappa1 * T) * Integ(t, 1.0, 2.0 * kappa1, tVol, Vol1, nVol) / (kappa1 * kappa1)
        + Integ(T, 1.0, 0.0, tVol, Vol2, nVol) / (kappa2 * kappa2)
        - Integ(t, 1.0, 0.0, tVol, Vol2, nVol) / (kappa2 * kappa2)
        - 2.0 * exp(-kappa2 * T) * Integ(T, 1.0, kappa2, tVol, Vol2, nVol) / (kappa2 * kappa2)
        + 2.0 * exp(-kappa2 * T) * Integ(t, 1.0, kappa2, tVol, Vol2, nVol) / (kappa2 * kappa2)
        + exp(-2.0 * kappa2 * T) * Integ(T, 1.0, 2.0 * kappa2, tVol, Vol2, nVol) / (kappa2 * kappa2)
        - exp(-2.0 * kappa2 * T) * Integ(t, 1.0, 2.0 * kappa2, tVol, Vol2, nVol) / (kappa2 * kappa2)
        + 2.0 * rho * Integ(T, 1.0, 0.0, tVol, Vol, nVol) / (kappa1 * kappa2)
        - 2.0 * rho * Integ(t, 1.0, 0.0, tVol, Vol, nVol) / (kappa1 * kappa2)
        - 2.0 * rho * exp(-kappa1 * T) * Integ(T, 1.0, kappa1, tVol, Vol, nVol) / (kappa1 * kappa2)
        + 2.0 * rho * exp(-kappa1 * T) * Integ(t, 1.0, kappa1, tVol, Vol, nVol) / (kappa1 * kappa2)
        - 2.0 * rho * exp(-kappa2 * T) * Integ(T, 1.0, kappa2, tVol, Vol, nVol) / (kappa1 * kappa2)
        + 2.0 * rho * exp(-kappa2 * T) * Integ(t, 1.0, kappa2, tVol, Vol, nVol) / (kappa1 * kappa2)
        + 2.0 * rho * exp(-(kappa1 + kappa2) * T) * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol, nVol) / (kappa1 * kappa2)
        - 2.0 * rho * exp(-(kappa1 + kappa2) * T) * Integ(t, 1.0, kappa1 + kappa2, tVol, Vol, nVol) / (kappa1 * kappa2);

    if (Vol) free(Vol);

    return value;
}

// Swaption2F 함수에서 사용
double A(
    double t,
    double T,
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    long nVol,			// 변동성 구간 개수
    double rho,			// 상관계수
    double* tDF,			// 할인채 만기
    double* DF,			// 할인채 가격
    long nDF				// 할인채 개수
)
{
    double V1 = V(t, T, kappa1, kappa2, tVol, Vol1, Vol2, nVol, rho);
    double V2 = V(0, T, kappa1, kappa2, tVol, Vol1, Vol2, nVol, rho);
    double V3 = V(0, t, kappa1, kappa2, tVol, Vol1, Vol2, nVol, rho);

    return exp(0.5 * (V1 - V2 + V3)) * P0(T, tDF, DF, nDF) / P0(t, tDF, DF, nDF);
}

double mu_x(double kappa1, double kappa2, long nHW1, double *HWTerm1, double* HWVol1, long nHW2, double* HWTerm2, double* HWVol2, double rho, double T, double t1, double t2)
{
    long i;
    long NodeNum = 10;
    long Point = 0;
    long Point2 = 0;
    double du = (t2-t1) / (double)NodeNum;
    double u = t1;
    double value = 0.0;
    double sigma;
    double v1, v2;
    for (i = 0; i < NodeNum; i++)
    {
        v1 = Interpolate_Linear_Point(HWTerm1, HWVol1, nHW1, u, Point);
        v2 = Interpolate_Linear_Point(HWTerm2, HWVol2, nHW2, u, Point2);
        value += exp(-kappa1 * (t2 - u)) * (v1 * v1 * B(u, T, kappa1) - rho * v1 * v2 * B(u, T, kappa2)) * du;
        u += du;
    }
    return value;
}

// 2-factor 모형의 Fixed Payer Swaption 가격 계산
double _stdcall Swaption2F(
    double NA,			// 액면금액
    double kappa1,		// 회귀속도1 
    double kappa2,		// 회귀속도2 
    double* tVol,		// 변동성 구간 종점
    double* Vol1,		// 구간 변동성1
    double* Vol2,		// 구간 변동성2
    double* Vol12,
    long nVol,			// 변동성 구간 개수
    double rho,			// 상관계수
    double StrikeRate,	// 고정금리(지급부분)
    long MaturityDate,	// 옵션 만기일까지 일수
    long* Dates,			// 지급일: 계산일로부터 각 중간지급일까지의 일수
    double* TimeCpn,      // 지급일까지 t 로 환산
    double* termC,          
    long nDates,			// 지급 회수(계산일 이후 남은 회수)
    double* PT,
    double P0_at_OptMaturity,
    long nQuad,                 //Gauss Normal Quadrature 개수
    double* x,                  //Gauss Normal Quadrature의 x값
    double* w                   //Gauss Normal Quadrature의 y값 비율
)
{
    long i, j;
    double sum, value = 0.0;
    double T;
    double h1, h2, kappa_i, y;
    double m_x, sigma_x, m_y, sigma_y, rho_xy;

    if (kappa1 < Tiny_Value) kappa1 = Tiny_Value;
    if (kappa2 < Tiny_Value) kappa2 = Tiny_Value;

    T = (double)MaturityDate / 365.0;
    double exp_minus_kappa1_T = exp(-kappa1 * T);
    double exp_minus2_kappa1_T = exp(-2.0 * kappa1 * T);
    double exp_minus_kappa2_T = exp(-kappa2 * T);
    double exp_minus2_kappa2_T = exp(-2.0 * kappa2 * T);

    //m_x = -exp(-kappa1 * T) / kappa1 * Integ(T, 1.0, kappa1, tVol, Vol1, nVol)
    //    + exp(-2.0 * kappa1 * T) / kappa1 * Integ(T, 1.0, 2.0 * kappa1, tVol, Vol1, nVol)
    //    - rho * exp(-kappa1 * T) / kappa2 * Integ(T, 1.0, kappa1, tVol, Vol12, nVol)
    //    + rho * exp(-(kappa1 + kappa2) * T) / kappa2 * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol12, nVol);
    //m_y = -exp(-kappa2 * T) / kappa2 * Integ(T, 1.0, kappa2, tVol, Vol2, nVol)
    //    + exp(-2.0 * kappa2 * T) / kappa2 * Integ(T, 1.0, 2.0 * kappa2, tVol, Vol2, nVol)
    //    - rho * exp(-kappa2 * T) / kappa1 * Integ(T, 1.0, kappa2, tVol, Vol12, nVol)
    //    + rho * exp(-(kappa1 + kappa2) * T) / kappa1 * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol12, nVol);    
    m_x = -mu_x(kappa1, kappa2, nVol, tVol, Vol1, nVol, tVol, Vol2, rho, T, 0, T);
    m_y = -mu_x(kappa2, kappa1, nVol, tVol, Vol2, nVol, tVol, Vol1, rho, T, 0, T);
    double v1, v2;
    v1 = Interpolate_Linear(tVol, Vol1, nVol, T);
    v2 = Interpolate_Linear(tVol, Vol2, nVol, T);
    sigma_x = sqrt(v1 * v1 * (1.0 - exp(-2.0 * kappa1 * T)) / (2.0 * kappa1));
    sigma_y = sqrt(v2 * v2 * (1.0 - exp(-2.0 * kappa2 * T)) / (2.0 * kappa2));
    //rho_xy = rho * v1 * v2 * (1.0 - exp(-(kappa1 + kappa2) * T)) / (kappa1 + kappa2);
    rho_xy = rho * exp(-(kappa1 + kappa2) * T) * Integ(T, 1.0, kappa1 + kappa2, tVol, Vol12, 1) / (sigma_x * sigma_y);

    if (sigma_x < 0.0) sigma_x = -sigma_x;
    if (sigma_x < Tiny_Value) sigma_x = Tiny_Value;
    if (sigma_y < 0.0) sigma_y = -sigma_y;
    if (sigma_y < Tiny_Value) sigma_y = Tiny_Value;

    rho_xy = max(-0.9999,min(0.9999,rho_xy));

    gauss_hermite_normal(x, w, m_x, sigma_x, nQuad);
    for (i = 0; i < nQuad; i++) {
        for (j = 0; j < nDates; j++) 
        {
            if (j == 0) 
            {
                termC[j] = StrikeRate * (TimeCpn[j] - T) * A(T, TimeCpn[j], kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho, P0_at_OptMaturity, PT[j]) * exp(-B(T, TimeCpn[j], kappa1) * x[i]);
            }
            else if (j == nDates - 1) 
            {
                termC[j] = (1.0 + StrikeRate * (TimeCpn[j] - TimeCpn[j - 1])) * A(T, TimeCpn[j], kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho, P0_at_OptMaturity, PT[j]) * exp(-B(T, TimeCpn[j], kappa1) * x[i]);
            }
            else 
            {
                termC[j] = StrikeRate * (TimeCpn[j] - TimeCpn[j - 1]) * A(T, TimeCpn[j], kappa1, kappa2, tVol, Vol1, Vol2, Vol12, nVol, rho, P0_at_OptMaturity, PT[j]) * exp(-B(T, TimeCpn[j], kappa1) * x[i]);
            }
        }

        y = Find_Sol2(kappa2, termC, T, TimeCpn, nDates);

        h1 = ((y - m_y) / sigma_y - rho_xy * (x[i] - m_x) / sigma_x) / sqrt(1.0 - rho_xy * rho_xy);

        sum = CDF_N(-h1);
        for (j = 0; j < nDates; j++) 
        {
            h2 = h1 + B(T, TimeCpn[j], kappa2) * sigma_y * sqrt(1.0 - rho_xy * rho_xy);
            kappa_i = -B(T, TimeCpn[j], kappa2) * (m_y - 0.5 * (1.0 - rho_xy * rho_xy) * sigma_y * sigma_y * B(T, TimeCpn[j], kappa2) + rho_xy * sigma_y * (x[i] - m_x) / sigma_x);
            sum -= termC[j] * exp(kappa_i) * CDF_N(-h2);
        }

        value += w[i] * sum;
    }

    return NA * value * P0_at_OptMaturity;
}




// 2-factor 모형의 Calibration 함수
// ATM 변동성만 사용
DLLEXPORT(long) HWCapHWSwaption_2FCalibration(
    long CaliFlag,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double FreqMonthSwaption,

    long NCap,
    double* TermCap,
    double* CapVol,
    double FreqMonthCap,

    long NHW_initial,
    double* HWTerm_initial,
    double* HWVol_initial,
    double* HWVol2_initial,
    double* initial_kappa,
    double* initial_kappa2,
    long FixedKappaFlag,
    double FixedKappa,
    double  FixedKappa2,
    long lognormalvol0normalvol1
)
{
    long i;
    long ResultCode = 0;
    //_CrtSetBreakAlloc(161);

    long NHW = 4;
    double* HWTerm;
    double* HWVol;

    double* Strike = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    double kappa = initial_kappa[0];
    if (NCap == 0 && NSwap * NOpt > 0 || CaliFlag == 1 )
    {
        HWTerm = TermOpt;
        NHW = min(NOpt, NHW_initial);
        HWVol = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);
        ResultCode = HW_LevMarq_Calibration_Swaption(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap, TermSwap, SwaptionVol, Strike, FreqMonthSwaption,
            NHW, HWTerm, HWVol, kappa, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1);
        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            *initial_kappa = kappa;
        }
        free(HWVol);
    }
    else if (NCap > 0)
    {
        if (CaliFlag == 2) NOpt = 0;
        if (NOpt > NCap)
        {
            HWTerm = TermOpt;
            NHW = min(NHW_initial, NOpt);
        }
        else {
            HWTerm = TermCap;
            NHW = min(NHW_initial, NCap);
        }
        HWVol = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++) HWVol[i] = max(0.001, HWVol_initial[i]);

        ResultCode = HW_GradDecent_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap, TermSwap, SwaptionVol, Strike,
            NCap, TermCap, CapVol, FreqMonthSwaption, FreqMonthCap,
            NHW, HWTerm, HWVol, kappa, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1);
        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            *initial_kappa = kappa;
        }
        free(HWVol);
    }
    else
    {
        return -1;
    }

    free(Strike);
    _CrtDumpMemoryLeaks();
}

void make_Jacov_HWSwaption_2F(
    long NLoop,
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    double rho,
    double* HWVol12_TempArray,
    long nQuad,
    double* x_array,
    double* w_array
)
{
    long i;
    long j;
    long n;

    double dhwvol_up = 0.0002;
    double dkappa_up = 0.0002;
    if (NLoop == 0)
    {
        dhwvol_up *= 10.0;
        dkappa_up *= 10.0;
    }
    double T;
    double HWT;
    double kappa_up;
    double kappa_dn;
    double kappa_up2;
    double kappa_dn2;

    double* HWVol_up;
    double* HWVol_dn;
    double* HWVol_up2;
    double* HWVol_dn2;

    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double dParams;
    double temp = 0.0;
    long breakflag = 0;

    for (i = 0; i < NResidual; i++)
    {
        T = (double)dates[i][nDates[i]- 1]/365.0;
        HWT = 0.0;
        for (j = 0; j < NParams; j++)
        {
            breakflag = 0;

            // 파라미터 초기화
            for (n = 0; n < NParams; n++) {
                ParamsUp[n] = Params[n];
                ParamsDn[n] = Params[n];
            }

            // 파라미터 Up And Dn
            if (FixedKappaFlag != 1)
            {
                if (j == 0 || j == 1)
                {
                    ParamsUp[j] = Params[j] + dkappa_up;
                    ParamsDn[j] = max(0.00001, Params[j] - dkappa_up);
                    dParams = (ParamsUp[j] - ParamsDn[j]) * 0.5;
                }
                else
                {
                    ParamsUp[j] = Params[j] + dhwvol_up;
                    ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                    dParams = (ParamsUp[j] - ParamsDn[j]) * 0.5;
                }

                kappa_up = ParamsUp[0];
                kappa_dn = ParamsDn[0];
                kappa_up2 = ParamsUp[1];
                kappa_dn2 = ParamsDn[1];

                HWVol_up = ParamsUp + 2;
                HWVol_dn = ParamsDn + 2;
                HWVol_up2 = ParamsUp + 2 + NHWVol;
                HWVol_dn2 = ParamsDn + 2 + NHWVol;
                if (j >= 2) HWT = HWVolTerm[max(0, (j - 2)%NHWVol - 2)];
            }
            else
            {
                ParamsUp[j] = Params[j] + dhwvol_up;
                ParamsDn[j] = max(0.0001, Params[j] - dhwvol_up);
                dParams = (ParamsUp[j] - ParamsDn[j]) * 0.5;

                kappa_up = FixedKappa;
                kappa_dn = FixedKappa;
                kappa_up2 = FixedKappa2;
                kappa_dn2 = FixedKappa2;

                HWVol_up = ParamsUp;
                HWVol_dn = ParamsDn;
                HWVol_up2 = ParamsUp + NHWVol;
                HWVol_dn2 = ParamsDn + NHWVol;
                HWT = HWVolTerm[max(j%NHWVol - 2, 0)];
            }            

            if (HWT  > T )
            {
                TempJacovMatrix[i][j] = 0.0;
            }
            else
            {
                if (OptMaturityDates[i] > 0)
                {
                    for (n = 0; n < NHWVol; n++) HWVol12_TempArray[n] = sqrt(fabs(HWVol_up[n] * HWVol_up2[n]));
                    Pup = Swaption2F(1.0, kappa_up, kappa_up2, HWVolTerm, HWVol_up, HWVol_up2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);

                    for (n = 0; n < NHWVol; n++) HWVol12_TempArray[n] = sqrt(fabs(HWVol_dn[n] * HWVol_dn2[n]));
                    Pdn = Swaption2F(1.0, kappa_dn, kappa_dn2, HWVolTerm, HWVol_dn, HWVol_dn2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);

                    //TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dParams);
                    TempJacovMatrix[i][j] = (Pdn - Pup) / (2.0 * dParams);
                }
                else
                {
                    for (n = 0; n < NHWVol; n++) HWVol12_TempArray[n] = sqrt(fabs(HWVol_up[n] * HWVol_up2[n]));
                    Pup = Cap2F(1.0, kappa_up, kappa_up2, HWVolTerm, HWVol_up, HWVol_up2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], dates[i], nDates[i], PT[i]);

                    for (n = 0; n < NHWVol; n++) HWVol12_TempArray[n] = sqrt(fabs(HWVol_dn[n] * HWVol_dn2[n]));
                    Pdn = Cap2F(1.0, kappa_dn, kappa_dn2, HWVolTerm, HWVol_dn, HWVol_dn2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], dates[i], nDates[i], PT[i]);

                    TempJacovMatrix[i][j] = (Pdn - Pup) / (2.0 * dParams);

                }
            }
        }
    }
}

void make_Residual_HWSwaption_2F(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double& absErrorSum,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    double rho,
    double* HWVol12_TempArray,
    double& RMPSE,
    long nQuad,
    double* x_array,
    double* w_array
)
{
    long i, n;
    double kappa;
    double kappa2;
    double* HWVol;
    double* HWVol2;
    if (FixedKappaFlag != 1)
    {
        kappa = Params[0];
        kappa2 = Params[1];
        HWVol = Params + 2;
        HWVol2 = Params + 2 + NHWVol;
    }
    else
    {
        kappa = FixedKappa;
        kappa2 = FixedKappa2;
        HWVol = Params;
        HWVol2 = Params + NHWVol;
    }
    double s = 0.0;
    double p, r2, tss, bs_meanprice;
    RMPSE = 0.0;
    for (n = 0; n < NHWVol; n++) HWVol12_TempArray[n] = sqrt(fabs(HWVol[n] * HWVol2[n]));

    bs_meanprice = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        if (OptMaturityDates[i] > 0) TempHWSwaptionPrice[i] = Swaption2F(1.0, kappa, kappa2, HWVolTerm, HWVol, HWVol2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], OptMaturityDates[i], dates[i], termdates[i], TempC[i], nDates[i], PT[i], P0_at_OptMaturity[i], nQuad, x_array, w_array);
        else TempHWSwaptionPrice[i] = Cap2F(1.0, kappa, kappa2, HWVolTerm, HWVol, HWVol2, HWVol12_TempArray, NHWVol, rho, StrikePrice[i], dates[i], nDates[i], PT[i]);
        bs_meanprice += BSSwaptionPrice[i]/(double)NResidual;
    }

    tss = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = (BSSwaptionPrice[i] - TempHWSwaptionPrice[i]);
        p = 0.5 * BSSwaptionPrice[i] + 0.5 * TempHWSwaptionPrice[i];
        r2 = ResidualArray[i] * ResidualArray[i];
        tss += (BSSwaptionPrice[i] - bs_meanprice)* (BSSwaptionPrice[i] - bs_meanprice);
        s += r2;
    }
    RMPSE = s/tss;    
    absErrorSum = s;
}

void Levenberg_Marquardt_2F(long NLoop, long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_J, double** Inverse_JT_J, double** JT_Res, double** ResultMatrix, long FixedKappaFlag, double* Initial_Params, double RMPSE, double* ArgminParams)
{
    long i;
    double mu = *lambda;
    double MIN_kappa = 0.001;
    double MAX_kappa = 0.2;

    double MIN_Vol = 0.00001;
    double MAX_Vol = 0.3;
    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };
    long Shape_JT[2] = { m,n };
    long Shape_Residual[2] = { n,1 };

    // J' dot J                 Shape = m * m
    XprimeDotX(Jacov, Shape_J, JT_J);
    rounding(JT_J, m, m, 8);

    // J'J + mu * diag(J'J)     Shape = m * m
    for (i = 0; i < m; i++) JT_J[i][i] = JT_J[i][i] + mu;// *JT_J[i][i];

    // inv(J'J + mu * diag(J'J))
    long Shape_Inv_JT_J[2] = { m,m };

    //MatrixInversion(JT_J, m, Inverse_JT_J);

    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);
    double* Known = (double*)malloc(sizeof(double) * m);
    double* UnKnown = (double*)malloc(sizeof(double) * m);
    for (i = 0; i < m; i++) Known[i] = JT_Res[i][0];

    gaussian_elimination(JT_J, Known, UnKnown, m);

    //Dot2dArray(Inverse_JT_J, Shape_Inv_JT_J, JT_Res, Shape_JT_Res, ResultMatrix);

    if (FixedKappaFlag == 0)
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i];//- ResultMatrix[i][0];
            if (i == 0 || i == 1)
            {
                if (NextParams[i] > MAX_kappa || NextParams[i] < MIN_kappa)
                {
                    if (NLoop == 0) NextParams[i] = max(MIN_kappa, min(MAX_kappa, Initial_Params[i]));
                    else NextParams[i] = max(MIN_kappa, min(MAX_kappa, ArgminParams[i]));
                }
            }
            else
            {
                if (NextParams[i] > MAX_Vol || NextParams[i] < MIN_Vol)
                {
                    if (NLoop == 0) NextParams[i] = max(MIN_Vol, min(MAX_Vol, Initial_Params[i]));
                    else NextParams[i] = max(MIN_Vol, min(MAX_Vol, ArgminParams[i]));
                }
            }
        }
    }
    else
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i];// ResultMatrix[i][0];

            if (NextParams[i] > MAX_Vol || NextParams[i] < MIN_Vol)
            {
                if (NLoop == 0) NextParams[i] = max(MIN_Vol, min(MAX_Vol, Initial_Params[i]));
                else NextParams[i] = max(MIN_Vol, min(MAX_Vol, ArgminParams[i]));
            }
        }

    }
    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(UnKnown[i]);
    ParamSum = s;
    free(Known);
    free(UnKnown);
}

void GradientDecent_2F(long NLoop, long NParams, long NResidual, double* NextParams, double* CurrentParams, double* lambda, double** Jacov, double* Residual, double& ParamSum, double** JT_Res, long FixedKappaFlag, double* Initial_Params, double RMPSE, double* ArgminParams)
{
    long i;
    double mu = *lambda;
    double MIN_kappa = 0.001;
    double MAX_kappa = 0.2;

    double MIN_Vol = 0.00001;
    double MAX_Vol = 0.3;
    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };
    long Shape_JT[2] = { m,n };
    long Shape_Residual[2] = { n,1 };

    // J' dot Res               Shape = m * n dot n * 1 = m * 1
    long Shape_JT_Res[2] = { m,1 };
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);
    double* UnKnown = (double*)malloc(sizeof(double) * m);
    for (i = 0; i < m; i++)  UnKnown[i] = JT_Res[i][0] * 2.0 * mu;

    if (FixedKappaFlag == 0)
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i];//- ResultMatrix[i][0];
            if (i == 0 || i == 1)
            {
                if (NextParams[i] > MAX_kappa || NextParams[i] < MIN_kappa)
                {
                    if (NLoop == 0) NextParams[i] = max(MIN_kappa, min(MAX_kappa, Initial_Params[i]));
                    else NextParams[i] = max(MIN_kappa, min(MAX_kappa, ArgminParams[i]));
                }
            }
            else
            {
                if (NextParams[i] > MAX_Vol || NextParams[i] < MIN_Vol)
                {
                    if (NLoop == 0) NextParams[i] = max(MIN_Vol, min(MAX_Vol, Initial_Params[i]));
                    else NextParams[i] = max(MIN_Vol, min(MAX_Vol, ArgminParams[i]));
                }
            }
        }
    }
    else
    {
        for (i = 0; i < NParams; i++)
        {
            NextParams[i] = CurrentParams[i] - UnKnown[i];// ResultMatrix[i][0];

            if (NextParams[i] > MAX_Vol || NextParams[i] < MIN_Vol)
            {
                if (NLoop == 0) NextParams[i] = max(MIN_Vol, min(MAX_Vol, Initial_Params[i]));
                else NextParams[i] = max(MIN_Vol, min(MAX_Vol, ArgminParams[i]));
            }
        }

    }
    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(UnKnown[i]);
    ParamSum = s;
    free(UnKnown);
}

void Gradient_Decent_HWSwaption_2F(
    long NParams,
    double* Params,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NHWVol,
    double* HWVolTerm,
    long NResidual,
    double* BSSwaptionPrice,
    double* StrikePrice,
    double* TempHWSwaptionPrice,
    double* ResidualArray,
    double* TermSwapNew,
    double* TermOptNew,
    double* P0_at_OptMaturity,
    long* OptMaturityDates,
    long* nDates,
    long** dates,
    double** termdates,
    double** TempC,
    double** PT,
    double* ParamsUp,
    double* ParamsDn,
    double** TempJacovMatrix,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    double rho,
    double* HWVol12_Temp,
    double& RMPSE
)
{

    long i, j;
    long n;
    long Shape0 = NResidual;
    long Shape1 = NParams;
    long BreakFlag = 0;
    long Levenberg = 1;
    long ngrad = 0;

    double* InitialParams = (double*)malloc(sizeof(double) * (NParams));
    for (i = 0; i < NParams; i++) InitialParams[i] = Params[i];

    double StopCondition = 0.0001;
    double minerror = 1000000.0;
    double absErrorSum = 100000.0;
    double PrevAbsErrorSum = 0.0;
    double ParamSum = 10000.0;
    double lambda[1] = { 0.005 };
    double* NextParams = (double*)malloc(sizeof(double) * (NParams));
    double** JT_Res = make_array(NParams, 1);
    double** PrevJacov = make_array(NResidual, NParams);
    double* PrevResidual = make_array(NResidual);
    double* argminparam = (double*)malloc(sizeof(double) * (NParams));
    double* prevparam = (double*)malloc(sizeof(double) * (NParams));
    double minrmpse = 100000.0;
    double prevrmpse = 100000.0;
    const long nQuad = 13;
    double x[13] = { 0.0 , };
    double w[13] = { 0.0, };
    for (n = 0; n < 6; n++)
    {

        make_Jacov_HWSwaption_2F(n, NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, ParamsUp, ParamsDn, TempJacovMatrix, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_Temp, nQuad, x, w);

        make_Residual_HWSwaption_2F(NParams, Params, NZero, ZeroTerm, ZeroRate,
            NHWVol, HWVolTerm, NResidual, BSSwaptionPrice, StrikePrice,
            TempHWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturity,
            OptMaturityDates,
            nDates, dates, termdates, TempC, PT, absErrorSum, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_Temp, RMPSE, nQuad, x, w);

        if (n >= 1)
        {
            if (absErrorSum < minerror || n == 1)
            {
                minerror = absErrorSum;
                minrmpse = RMPSE;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                if (RMPSE < 0.1) break;
            }
            if (absErrorSum < PrevAbsErrorSum) lambda[0] *= 0.7;
            else
            {                
                for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) TempJacovMatrix[i][j] = PrevJacov[i][j];
                for (i = 0; i < NResidual; i++) ResidualArray[i] = PrevResidual[i] ;
                for (i = 0; i < NParams; i++) Params[i] = prevparam[i];
                lambda[0] *= 0.7;
            }
        }

        for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) PrevJacov[i][j] = TempJacovMatrix[i][j];
        for (i = 0; i < NResidual; i++) PrevResidual[i] = ResidualArray[i];

        GradientDecent_2F(n, NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_Res, FixedKappaFlag, InitialParams, RMPSE, argminparam);
        for (i = 0; i < NParams; i++)
        {
            prevparam[i] = Params[i];
            Params[i] = NextParams[i];
        }

        if (ParamSum < StopCondition && n > 10) break;
        if (minrmpse <= 0.1 ) break;
        PrevAbsErrorSum = absErrorSum;
        prevrmpse = RMPSE;
    }

    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];
    RMPSE = minrmpse;

    free(InitialParams);
    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    free(argminparam);
    free(prevparam);
    for (i = 0; i < NResidual; i++) free(PrevJacov[i]);
    free(PrevJacov);
    free(PrevResidual);
}

long HW2F_LevMarq_Calibration_SwaptionCap(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double* Strike,
    double FreqMonth,

    long NCap,
    double* TermCap,
    double* CapVol,

    long NHW,
    double* HWTerm,
    double* HWVol,
    double* HWVol2,
    double& kappa,
    double& kappa2,
    double rho,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    long lognormalvol0normalvol1
)
{
    long i;
    long j;

    long k;
    long n;

    double* TermSwapNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap) );                                             // 할당 1
    for (i = 0; i < NSwap * NOpt; i++) TermSwapNew[i] = TermSwap[i % NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermSwapNew[i] = TermCap[i - NSwap * NOpt];

    double* TermOptNew = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap) );                                              // 할당 2
    for (i = 0; i < NSwap * NOpt; i++) TermOptNew[i] = TermOpt[i / NSwap];
    for (i = NSwap * NOpt; i < NSwap * NOpt + NCap; i++) TermOptNew[i] = 0.0;

    double* BSSwaptionPrice = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));                                          // 할당 3
    double* HWSwaptionPrice = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));                                          // 할당 4
    double fm;
    n = 0;
    for (k = 0; k < NSwap * NOpt + NCap; k++)
    {
        Strike[k] = FSR(ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth);
        if (TermOptNew[k] > 0.0) BSSwaptionPrice[k] = BS_Swaption(1.0, SwaptionVol[k], Strike[k], ZeroTerm, ZeroRate, NZero, TermOptNew[k], TermSwapNew[k], FreqMonth, lognormalvol0normalvol1);
        else
        {
            BSSwaptionPrice[k] = BS_Cap(1.0, CapVol[n], ZeroTerm, ZeroRate, NZero, Strike[k], TermOptNew[k], TermCap[n], FreqMonth, lognormalvol0normalvol1);
            n++;
        }
    }

    long* OptMaturityDates = (long*)malloc(sizeof(long) * (NOpt * NSwap + NCap));                                               // 할당 5
    for (i = 0; i < NOpt * NSwap; i++) OptMaturityDates[i] = (long)(TermOptNew[i] * 365.0);
    for (i = NOpt * NSwap; i < NOpt * NSwap + NCap; i++) OptMaturityDates[i] = 0;

    double* P0_at_OptMaturityDates = (double*)malloc(sizeof(double) * (NOpt * NSwap + NCap));                                   // 할당 6
    for (i = 0; i < NOpt * NSwap; i++) P0_at_OptMaturityDates[i] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, TermOptNew[i]);
    for (i = NOpt * NSwap; i < NOpt * NSwap + NCap; i++) P0_at_OptMaturityDates[i] = 1.0;

    double* HWVol12_TempArray = (double*)malloc(sizeof(double) * NHW);                                                          // 할당 7

    double RMPSE = 1.0;

    long* nDates = (long*)malloc(sizeof(long) * (NOpt * NSwap + NCap));                                                         // 할당 8
    for (i = 0; i < NOpt * NSwap + NCap; i++) nDates[i] = Number_Of_Payment(TermOptNew[i], TermOptNew[i] + TermSwapNew[i], FreqMonth);

    long** dates = (long**)malloc(sizeof(long*) * (NOpt * NSwap + NCap));                                                       // 할당 9
    double** termdates = (double**)malloc(sizeof(double*) * (NOpt * NSwap + NCap));                                             // 할당 10
    double** TempC = (double**)malloc(sizeof(double*) * (NOpt * NSwap + NCap));                                                 // 할당 11
    for (i = 0; i < NOpt * NSwap + NCap; i++)
    {
        dates[i] = (long*)malloc(sizeof(long) * nDates[i]);
        termdates[i] = (double*)malloc(sizeof(double) * nDates[i]);
        TempC[i] = (double*)malloc(sizeof(double) * nDates[i]);
        PaymentDatesMapping(TermOptNew[i] + TermSwapNew[i], FreqMonth, dates[i], nDates[i]);
        for (j = 0; j < nDates[i]; j++) termdates[i][j] = ((double)dates[i][j]) / 365.0;
    }

    double** PT = (double**)malloc(sizeof(double*) * (NOpt * NSwap+NCap) );                                                     // 할당 12
    for (i = 0; i < NOpt * NSwap + NCap; i++)
    {
        PT[i] = (double*)malloc(sizeof(double) * (nDates[i] + 1));
        if (TermOptNew[i] > 0.0) PT[i][0] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, TermOptNew[i]);
        else PT[i][0] = 1.0;

        for (n = 0; n < nDates[i]; n++)  PT[i][n + 1] = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, (double)dates[i][n] / 365.0);
    }

    long NResidual = NOpt * NSwap + NCap;
    double* ResidualArray = (double*)malloc(sizeof(double) * (NResidual));                                                      // 할당 13

    long nparams;
    if (FixedKappaFlag != 1) nparams = 2*(1 + NHW);
    else nparams = NHW*2;

    double* params = (double*)malloc(sizeof(double) * (nparams));                                                               // 할당 14
    double* paramsup = (double*)malloc(sizeof(double)*(nparams));                                                               // 할당 15
    double* paramsdn = (double*)malloc(sizeof(double)*(nparams));                                                               // 할당 16
    double** tempjacov = make_array(NResidual, nparams);                                                                        // 할당 17

    if (FixedKappaFlag != 1)
    {
        params[0] = kappa;
        params[1] = kappa2;
        for (i = 0; i < NHW; i++) params[i + 2] = HWVol[i];
        for (i = 0; i < NHW; i++) params[i + 2 + NHW] = HWVol2[i];
    }
    else
    {
        for (i = 0; i < NHW; i++) params[i] = HWVol[i];
        for (i = 0; i < NHW; i++) params[i + NHW] = HWVol2[i];
    }
    double* HWTerm2F = (double*)malloc(sizeof(double) * NHW * 2);                                                               // 할당 18
    for (i = 0; i < NHW; i++) HWTerm2F[i] = HWTerm[i];
    for (i = NHW; i < 2 * NHW; i++) HWTerm2F[i] = HWTerm[i - NHW];

    //Levenberg_Marquardt_HWSwaption_2F(nparams, params, NZero, ZeroTerm, ZeroRate,
    //    NHW, HWTerm2F, NResidual, BSSwaptionPrice, Strike,
    //    HWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturityDates,
    //    OptMaturityDates,
    //    nDates, dates, termdates, TempC, PT, paramsup, paramsdn,
    //    tempjacov, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_TempArray, RMPSE);
    Gradient_Decent_HWSwaption_2F(nparams, params, NZero, ZeroTerm, ZeroRate,
        NHW, HWTerm2F, NResidual, BSSwaptionPrice, Strike,
        HWSwaptionPrice, ResidualArray, TermSwapNew, TermOptNew, P0_at_OptMaturityDates,
        OptMaturityDates,
        nDates, dates, termdates, TempC, PT, paramsup, paramsdn,
        tempjacov, FixedKappaFlag, FixedKappa, FixedKappa2, rho, HWVol12_TempArray, RMPSE);
    if (FixedKappaFlag != 1)
    {
        kappa = params[0];
        kappa2 = params[1];
        for (i = 0; i < NHW; i++) HWVol[i] = params[i + 2];
        for (i = 0; i < NHW; i++) HWVol2[i] = params[i + 2 + NHW];
    }
    else
    {
        kappa = FixedKappa;
        kappa2 = FixedKappa2;
        for (i = 0; i < NHW; i++) HWVol[i] = params[i];
        for (i = 0; i < NHW; i++) HWVol2[i] = params[i + NHW];
    }

    free(TermSwapNew);                                                                  // 할당1 해제
    free(TermOptNew);                                                                   // 할당2 해제
    free(BSSwaptionPrice);                                                              // 할당3 해제
    free(HWSwaptionPrice);                                                              // 할당4 해제
    free(OptMaturityDates);                                                             // 할당5 해제
    free(P0_at_OptMaturityDates);                                                       // 할당6 해제
    free(HWVol12_TempArray);                                                            // 할당7 해제
    free(nDates);                                                                       // 할당8 해제

    for (i = 0; i < NOpt * NSwap + NCap; i++) free(dates[i]);                           // 할당9 해제
    free(dates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(termdates[i]);                       // 할당10 해제
    free(termdates);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(TempC[i]);                           // 할당11 해제
    free(TempC);
    for (i = 0; i < NOpt * NSwap + NCap; i++) free(PT[i]);                              // 할당12 해제
    free(PT);                                                                           

    free(ResidualArray);                                                                // 할당13 해제
    free(params);                                                                       // 할당14 해제
    free(paramsup);                                                                     // 할당15 해제
    free(paramsdn);                                                                     // 할당16 해제

    for (i = 0; i < NResidual; i++) free(tempjacov[i]);                                 // 할당17 해제
    free(tempjacov);

    free(HWTerm2F);                                                                     // 할당18 해제

    return (long)(RMPSE * 10000.0);
}

DLLEXPORT(long) HWCapHWSwaptionCalibration2F(
    long CaliFlag,
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,

    long NOpt,
    double* TermOpt,
    long NSwap,
    double* TermSwap,
    double* SwaptionVol,
    double FreqMonthSwaption,

    long NCap,
    double* TermCap,
    double* CapVol,
    double FreqMonthCap,

    long NHW_initial,
    double* HWTerm_initial,
    double* HWVol_initial,
    double* HWVol_initial2,
    double* initial_kappa,
    double* initial_kappa2,
    long FixedKappaFlag,
    double FixedKappa,
    double FixedKappa2,
    double rho,
    long lognormalvol0normalvol1
)
{
    long i;
    long ResultCode = 0;
    //_CrtSetBreakAlloc(647);

    long NHW = 4;
    double* HWTerm;
    double* HWVol;
    double* HWVol2;

    double* Strike = (double*)malloc(sizeof(double) * (NSwap * NOpt + NCap));
    double kappa = initial_kappa[0];
    double kappa2 = initial_kappa2[0];

    if ( CaliFlag == 1 && NOpt * NSwap > 0)
    {
        HWTerm = TermOpt;
        NCap = 0;
        NHW = min(NOpt, NHW_initial);
        HWVol = (double*)malloc(sizeof(double) * NHW);
        HWVol2 = (double*)malloc(sizeof(double) * NHW);

        for (i = 0; i < NHW; i++)
        {
            HWVol[i] = max(0.005, HWVol_initial[i]);
            HWVol2[i] = max(0.002, HWVol_initial2[i]);
        }

        ResultCode = HW2F_LevMarq_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap,
            TermSwap, SwaptionVol, Strike,
            FreqMonthSwaption,
            NCap, TermCap, CapVol,
            NHW, HWTerm, HWVol, HWVol2,
            kappa, kappa2, rho,
            FixedKappaFlag,
            FixedKappa, FixedKappa2, lognormalvol0normalvol1);

        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            HWVol_initial2[i] = HWVol2[i];
            *initial_kappa = kappa;
            *initial_kappa2 = kappa2;
        }

        free(HWVol);
        free(HWVol2);
    }
    else if (NCap > 0 && CaliFlag == 2)
    {
        NOpt = 0;
        NSwap = 0;
        HWTerm = TermOpt;
        NHW = min(NHW_initial, NCap);
        HWVol = (double*)malloc(sizeof(double) * NHW);
        HWVol2 = (double*)malloc(sizeof(double) * NHW);

        for (i = 0; i < NHW; i++)
        {
            HWVol[i] = max(0.005, HWVol_initial[i]);
            HWVol2[i] = max(0.002, HWVol_initial2[i]);
        }

        ResultCode = HW2F_LevMarq_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap,
            TermSwap, SwaptionVol, Strike,
            FreqMonthCap,
            NCap, TermCap, CapVol,
            NHW, HWTerm, HWVol, HWVol2,
            kappa, kappa2, rho,
            FixedKappaFlag,
            FixedKappa, FixedKappa2, lognormalvol0normalvol1);

        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            HWVol_initial2[i] = HWVol2[i];
            *initial_kappa = kappa;
            *initial_kappa2 = kappa2;
        }

        free(HWVol);
        free(HWVol2);
    }
    else if ((NCap > 0 && NSwap * NOpt > 0 && CaliFlag == 0))
    {
        if (NOpt > NCap)
        {
            HWTerm = TermOpt;
            NHW = min(NHW_initial, NOpt);
        }
        else {
            HWTerm = TermCap;
            NHW = min(NHW_initial, NCap);
        }
        HWVol = (double*)malloc(sizeof(double) * NHW);
        HWVol2 = (double*)malloc(sizeof(double) * NHW);
        for (i = 0; i < NHW; i++)
        {
            HWVol[i] = max(0.005, HWVol_initial[i]);
            HWVol2[i] = max(0.002, HWVol_initial2[i]);
        }

        ResultCode = HW2F_LevMarq_Calibration_SwaptionCap(NZero, ZeroTerm, ZeroRate,
            NOpt, TermOpt, NSwap,
            TermSwap, SwaptionVol, Strike,
            FreqMonthSwaption,
            NCap, TermCap, CapVol,
            NHW, HWTerm, HWVol, HWVol2,
            kappa, kappa2, rho,
            FixedKappaFlag,
            FixedKappa, FixedKappa2, lognormalvol0normalvol1);

        for (i = 0; i < NHW; i++)
        {
            HWTerm_initial[i] = HWTerm[i];
            HWVol_initial[i] = HWVol[i];
            HWVol_initial2[i] = HWVol2[i];
            *initial_kappa = kappa;
            *initial_kappa2 = kappa2;
        }

        free(HWVol);
        free(HWVol2);
    }


    free(Strike);
    _CrtDumpMemoryLeaks();
    return ResultCode;
}