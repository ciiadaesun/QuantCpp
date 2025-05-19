#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "HW_Calibration.h"
#include "GetTextDump.h"

#ifndef UTILITY
#include "Util.h"
#endif

#ifndef DateFunction
#include "CalcDate.h"
#endif 
#include "Structure.h"
#include <crtdbg.h>

//레퍼런스금리정보
typedef struct ReferenceInfo {
    long CurveNum;              // 커브 번호
    long RefRateType;           // 기초금리 타입 0: CD/Libor (Not Accrual) 1: CD/Libor 또는 이자율스왑 2: SOFR
    long RefSwapNCPN_Ann;       // 기초금리 타입이 스왑일 경우 연 이자지급 수
    double RefSwapMaturity;     // 기초금리 타입이 스왑일 경우 스왑 만기

    long DayCountFlag;          // 0: Day1Y = 365, 1: Day1Y = 360 2: Act/ACt 3: 30/360
    double RefRateCondMultiple; // 기준금리 결정조건 Multiple
    long PowerSpreadFlag;       // 파워스프레드 사용여부
    double PowerSpreadMat1;     // 파워스프레드 만기1 
    double PowerSpreadMat2;     // 파워스프레드 만기2
    double RangeUp;             // 쿠폰 상방배리어
    double RangeDn;             // 쿠폰 하방배리어
    double PayoffMultiple;      // 페이오프 결정조건 Multiple

} REFERENCE_INFO;

typedef struct LegInfo {
    long FixFloFlag;                    // 0: 고정금리, 1:변동금리
    long AccrualFlag;                   // Range Accrual 사용여부
    double MaxLossY;                    // 최대손실
    double MaxRetY;                     // 최대이익
    long NReference;                    // 기초금리개수
    REFERENCE_INFO* Reference_Inform;   // 레퍼런스금리정보
    long DiscCurveNum;                  // 할인 커브 번호

    long NCashFlow;                     // 현금흐름지급개수
    long* ForwardStart_C;               // 금리 추정(또는 리셋) 시작일 Ctype
    long* ForwardEnd_C;                 // 금리 추정(또는 리셋) 종료일 Ctype
    long* DaysForwardStart;             // 평가일 to 금리 추정(또는 리셋) 시작일
    long* DaysForwardEnd;               // 평가일 to 금리 추정(또는 리셋) 종료일
    long* FractionStart_C;              // 기산일 Ctype
    long* FractionEnd_C;                // 기말일 Ctype
    long* PayDate_C;                    // 지급일 Ctype
    long* DaysPayDate_C;                // 평가일 to 지급일
    double* CouponRate;                 // 쿠폰Rate
    long* FloatingFlag;                 // Floating 금리 적용 Flag
    double* RangeCoupon;                // Range충족시 쿠폰
    long PayoffStructure;               // 페이오프 조건 0: &조건 1: 합조건
    long CurrentIdx;

    long nUsingCurve;                   // 사용되는커브숫자
    long* HolidayCalcFlag;              // Holiday계산Flag
    long* HolidayCount;                 // Holiday수
    long** HolidayDays;                 // 평가일 to 각 레퍼런스별 Holiday까지 날짜 수

    long* NDayHistory;                  // 과거 레퍼런스 History 개수
    long** RateHistoryDateMatrix;       // 과거 레퍼런스 History Date Matrix
    double** RateHistoryMatrix;         // 과거 레퍼런스 History Rate Matrix

    // 옵션관련 데이터
    long OptionUseFlag;                 // 옵션 사용여부
    long NOption;                       // 옵션 개수
    long CallConditionFlag;             // 행사조건Flag 0:Range1&Range2&Range3 1:Range1||Range2||Range3
    long OptionType;                    // 옵션타입 0:Payer가 Call옵션 1:Receiver가 풋옵션
    long* OptionDate;                   // Option Date
    long OptDateToPayDate;              // 옵션행사일부터 지급일까지 일수
    double* StrikeRate;                 // 옵션행사비율
    double** RangeUp;                   // Ref 123 Range 상한
    double** RangeDn;                   // Ref 123 Range 하한

}LEG_INFO;

typedef struct SimulationInfo {
    long NSimul;                    // 시뮬레이션 개수
    long NDays;                     // 시뮬레이션 날짜 개수
    long NAsset;                    // 기초자산 중복 제외하고 개수
    long DailySimulFlag;            // DailySimul여부
    long* DaysForSimul;             // 시뮬 날짜 Array
    long* YYYYMMDDForSimul;         // 시뮬 날짜 YYYYMMDD Array
    double* dt_Array;               // 시뮬레이션 Day들의 간격
    double* T_Array;                // 시뮬레이션 Day를 T로 변환
    double** FixedRandn;            // 고정된랜덤넘버
    double** FixedRandn2;           // 2Factor 랜덤넘버
    long* NHWVol;                   // HWVol 개수를 NAsset만큼 배열
    double* HWKappa;                // HW Kappa값을 NAsset만큼 배열
    double** HWVolTerm;             // HW Vol Term을 --> NAsset, NHWVol 만큼 배열
    double** HWVol;                 // HW Vol을 --> NAsset, NHWVol 만큼 배열
    long* NRateTerm;                // 기초금리 Term 개수 Array
    double** RateTerm;              // 기초금리 Term Array --> Shape = NAsset, NRateTerm
    double** Rate;                  // 기초금리 Array --> Shape = NAsset, NRateTerm
    long* SimulCurveIdx;            // 시뮬레이션되는 커브 번호
    long HWFactorFlag;
    double* HWKappa2;
    double** HWVol2;
    double* HWQuantoFlag;
    double* HWQuantoRho;
    double* HWQuantoVol;
    double* HW2FRho;
}SIMUL_INFO;

typedef struct HW_Parameter {
    long NAsset;                            // 시뮬레이션 자산 개수
    long NDays;                             // 시뮬레이션 Day 개수

    double** XA;                            // Hull White XA Term = exp(-kappa * (T2-T1)) --> Shape : (NAsset, NDays)
    double** XV;                            // Hull White XV Term = sqrt( integral_(t1)^(t2) exp(-2kappa(t2-t1)) sigma_t^2 dt ) --> Shape : (NAsset, NDays)
    double** XA2F;
    double** XV2F;

    long CurveIdx_DiscRcv;                      // 시뮬레이션 기준 Rcv Discount 커브 index
    long CurveIdx_DiscPay;                      // 시뮬레이션 기준 Pay Discount 커브 index
    long NRcv_Cf;                               // Rcv Leg Cashflow 개수
    long NPay_Cf;                               // Pay Leg Cashflow 개수
    double* Rcv_DF_0_t;                         // Rcv Disc P(0,t)
    double* Rcv_DF_0_T;                         // Rcv Disc P(0,T)
    double* Rcv_DF_t_T;                         // Rcv Disc P(t,T)
    double* B_t_T_RcvDisc;                      // Rcv disc Hull White B(t,T) = (1-exp(-kappa(T-t))/kappa
    double* QVTerm_RcvDisc;                     // Rcv disc Hull White QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds
    double* B_t_T_RcvDisc2F;                    // Rcv disc Hull White 2F B(t,T) = (1-exp(-kappa(T-t))/kappa
    double* QVTerm_RcvDisc2F;                   // Rcv disc Hull White 2F QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds
    double* CrossTerm_RcvDisc2F;                   // Rcv disc Hull White 2F QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds

    double* Pay_DF_0_t;                         // Pay Disc P(0,t)
    double* Pay_DF_0_T;                         // Pay Disc P(0,T)
    double* Pay_DF_t_T;                         // Pay Disc P(t,T)
    double* B_t_T_PayDisc;                      // Pay Disc Hull White B(t,T) = (1-exp(-kappa(T-t))/kappa
    double* QVTerm_PayDisc;                     // Pay Disc Hull White QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds
    double* B_t_T_PayDisc2F;                    // Pay Disc Hull White 2F B(t,T) = (1-exp(-kappa(T-t))/kappa
    double* QVTerm_PayDisc2F;                   // Pay Disc Hull White 2F QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds
    double* CrossTerm_PayDisc2F;                   // Pay Disc Hull White 2F QVTerm(t,T) = integ_0^t sigma^2 * [B(s,t)^2 - B(s,T)^2] ds

    long NRcvCurve;                             // Rcv Leg Reference Curve 개수
    long NPayCurve;                             // Pay Leg Reference Curve 개수

    long** ndates_cpn_rcv;                      // Rcv Reference 금리별 쿠폰개수 -> Shape = NReference, NDays
    double*** RcvRef_DF_t_T;                    // Rcv Ref P(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T;                     // Rcv Ref B(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_QVTerm;                    // Rcv Ref QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T2F;                   // Rcv Ref 2F B(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_QVTerm2F;                  // Rcv Ref 2F QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_CrossTerm2F;               // Rcv Ref 2F QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_dt;                        // Rcv Ref DeltaT(t, T)--> Shape = NReference, NDays, NCpn

    long** ndates_cpn_powerspread_rcv;          // Rcv Reference 반대쪽 파워스프레드 금리별 쿠폰개수 -> Shape = NReference, NDays
    double*** RcvRef_DF_t_T_PowerSpread;        // Rcv Ref 반대쪽 파워스프레드 P(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T_PowerSpread;         // Rcv Ref 반대쪽 파워스프레드 B(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_QVTerm_PowerSpread;        // Rcv Ref 반대쪽 파워스프레드 QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T_PowerSpread2F;       // Rcv Ref 반대쪽 파워스프레드 B(t,T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_QVTerm_PowerSpread2F;      // Rcv Ref 반대쪽 파워스프레드 QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_CrossTerm_PowerSpread2F;   // Rcv Ref 반대쪽 파워스프레드 QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** RcvRef_dt_PowerSpread;            // Rcv Ref 반대쪽 파워스프레드 DeltaT(t, T)--> Shape = NReference, NDays, NCpn

    long** ndates_cpn_pay;                      // Pay Reference 금리별 쿠폰개수 -> Shape = NReference, NDays
    double*** PayRef_DF_t_T;                    // Pay Ref P(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T;                     // Pay Ref B(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_QVTerm;                    // Pay Ref QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T2F;                   // Pay Ref 2F B(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_QVTerm2F;                  // Pay Ref 2F QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_CrossTerm2F;               // Pay Ref 2F QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_dt;                        // Pay Ref DeltaT(t, T)--> Shape = NReference, NDays, NCpn

    long** ndates_cpn_powerspread_pay;          // Pay Reference 반대쪽 파워스프레드 금리별 쿠폰개수
    double*** PayRef_DF_t_T_PowerSpread;        // Pay Ref 반대쪽 파워스프레드 P(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T_PowerSpread;         // Pay Ref 반대쪽 파워스프레드 B(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_QVTerm_PowerSpread;        // Pay Ref 반대쪽 파워스프레드 QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T_PowerSpread2F;       // Pay Ref 반대쪽 파워스프레드 B(t,T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_QVTerm_PowerSpread2F;      // Pay Ref 반대쪽 파워스프레드 QVTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_CrossTerm_PowerSpread2F;   // Pay Ref 반대쪽 파워스프레드 CrossTerm(t, T) --> Shape = NReference, NDays, NCpn
    double*** PayRef_dt_PowerSpread;            // Pay Ref 반대쪽 파워스프레드 DeltaT(t, T)--> Shape = NReference, NDays, NCpn
    double QuantoFlag;
    double QuantoRho;
    double QuantoVol;
    
} HW_INFO;


//A_k = exp(-kappa * (t_(k+1) - t_(k))
double XA(
    double kappa,
    double t0,
    double t1
)
{
    double A_k = exp(-kappa * (t1 - t0));
    return A_k;
}

void Set_XA(
    double kappa,
    long Length_XA_Array,
    double* XA_Array,
    double* dt_Array
)
{
    long i;
    double T, t0, t1;
    T = 0.0;
    for (i = 0; i < Length_XA_Array; i++)
    {
        t0 = T;
        t1 = t0 + dt_Array[i];
        XA_Array[i] = XA(kappa, t0, t1);
        T = t1;
    }
}

// XV = sqrt( int_t0^t1 [ e^(-2kappa*(t1-s)) * sig(s)^2 * ds   ])
double XV(
    double kappa,
    long NHWVol,
    double* HWVolTerm,
    double* HWVol,
    double t0,
    double t1
)
{
    long i;
    double vol = 0.0;
    double B_k, B_k_Square;
    kappa = max(0.00001, kappa);

    if (NHWVol == 1 || t1 - t0 < 0.25)
    {
        vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t0);
        B_k_Square = vol * vol * 0.5 / kappa * (1.0 - exp(-2.0 * kappa * (t1 - t0)));
    }
    else
    {
        long NInteg = 10.0;
        double u = t0;
        double du = (t1 - t0) / ((double)NInteg);
        B_k_Square = 0.0;
        for (i = 0; i < NInteg; i++)
        {
            vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
            B_k_Square += vol * vol * exp(-2.0 * kappa * (t1 - u)) * du;
            u = u + du;
        }
    }

    B_k = sqrt(B_k_Square);
    return B_k;
}

void Set_XV(
    double kappa,
    long NHWVol,
    double* HWVolTerm,
    double* HWVol,
    long Length_XV_Array,
    double* XV_Array,
    double* dt_Array
)
{
    long i;
    double T, t0, t1;
    T = 0.0;
    for (i = 0; i < Length_XV_Array; i++)
    {
        t0 = T;
        t1 = t0 + dt_Array[i];
        XV_Array[i] = XV(kappa, NHWVol, HWVolTerm, HWVol, t0, t1);
        T = t1;
    }
}

double B_s_to_t(
    double kappa,
    double s,
    double t
)
{
    return (1.0 - exp(-kappa * (t - s))) / kappa;
}

double V_t_T(
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

double V_t_T(double k1, double k2, double t, double T,
    double* tVol1, double* Vol1, long nVol1,
    double* tVol2, double* Vol2, long nVol2)
{
    long NInteg = 10;
    double RHS = 0.0;
    double du = (T - t) / (double)NInteg;
    double u, v1, v2, term;
    for (long i = 0; i < NInteg; i++) 
    {
        u = t + du * (i + 0.5);
        v1 = Interpolate_Linear(tVol1, Vol1, nVol1, u);
        v2 = Interpolate_Linear(tVol2, Vol2, nVol2, u);

        term = v1 * v2 *(1.0 - exp(-k1 * (T - u))) / k1 *(1.0 - exp(-k2 * (T - u))) / k2 *du;
        RHS += term;
    }
    return RHS;
}

double HullWhiteQVTerm(
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
    double V_1, V_2, V_3;
    
    if (NHWVol == 1 || kappa > 0.1)
    {
        vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t+T)/2.);
        V_1 = V_t_T(kappa, kappa, t, T, vol, vol);
        V_2 = V_t_T(kappa, kappa, 0, T, vol, vol);
        V_3 = V_t_T(kappa, kappa, 0, t, vol, vol);
        RHS = 0.5 * (V_1 - V_2 + V_3);
    }
    else
    {
        //V_1 = V_t_T(kappa, kappa, t, T, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
        //V_2 = V_t_T(kappa, kappa, 0, T, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
        //V_3 = V_t_T(kappa, kappa, 0, t, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
        //RHS = 0.5 * (V_1 - V_2 + V_3);
        RHS = 0.;
        long NInteg = 10;
        double u = t;
        double du = (T - t) / ((double)NInteg);
        double Bst = 0.;
        for (i = 0; i < NInteg; i++)
        {
            vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
            Bst = B_s_to_t(kappa, u, t);
            RHS += 0.5 * vol * vol * (Bst * Bst) * du;
            u = u + du;
        }
    }
    return RHS;
}

double HullWhite2F_CrossTerm(
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
    double vol, vol2;
    double RHS = 0.0;
    double V_1, V_2, V_3;

    if (NHWVol == 1 || kappa > 0.1)
    {
        vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t + T) / 2.);
        vol2 = Interpolate_Linear(HWVolTerm2, HWVol2, NHWVol, (t + T) / 2.);
        V_1 = V_t_T(kappa, kappa2, t, T, vol, vol2);
        V_2 = V_t_T(kappa, kappa2, 0, T, vol, vol2);
        V_3 = V_t_T(kappa, kappa2, 0, t, vol, vol2);
        RHS = 2.0 * rho * 0.5 * (V_1 - V_2 + V_3);
    }
    else
    {
        V_1 = V_t_T(kappa, kappa2, t, T, HWVolTerm, HWVol, NHWVol, HWVolTerm2, HWVol2, NHWVol);
        V_2 = V_t_T(kappa, kappa2, 0, T, HWVolTerm, HWVol, NHWVol, HWVolTerm2, HWVol2, NHWVol);
        V_3 = V_t_T(kappa, kappa2, 0, t, HWVolTerm, HWVol, NHWVol, HWVolTerm2, HWVol2, NHWVol);
        RHS = 2.0 * rho * 0.5 * (V_1 - V_2 + V_3);
    }
    return RHS;
}


void bubble_sort_long(long* arr, long count, long ascending)
{
    long temp;
    long i, j;
    if (ascending == 1)
    {
        for (i = 0; i < count; i++)
        {
            for (j = 0; j < count - 1; j++)
            {
                if (arr[j] > arr[j + 1])          // 이전 값이 더 크면
                {                                 // 이전 값을 다음 요소로 보내고 다음 요소를 이전 요소 자리로
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    else
    {
        for (i = 0; i < count; i++)
        {
            for (j = 0; j < count - 1; j++)
            {
                if (arr[j] < arr[j + 1])
                {
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
}

long* Make_Unique_Array(long n_array, long* Sorted_Array, long& target_length)
{
    long i;
    long n;
    long unqvalue = Sorted_Array[0];
    n = 1;
    for (i = 1; i < n_array; i++)
    {
        if (Sorted_Array[i] != unqvalue)
        {
            n += 1;
            unqvalue = Sorted_Array[i];
        }
    }

    target_length = n;
    long* ResultArray = (long*)malloc(sizeof(long) * n);
    ResultArray[0] = Sorted_Array[0];
    unqvalue = Sorted_Array[0];
    n = 1;
    for (i = 1; i < n_array; i++)
    {
        if (Sorted_Array[i] != unqvalue)
        {
            ResultArray[n] = Sorted_Array[i];
            unqvalue = Sorted_Array[i];
            n += 1;
        }
    }

    return ResultArray;
}


double DayCountFractionAtoB(long Day1, long Day2, long Flag)
{
    long i;
    double tau;
    long imax;
    double Div;

    if (Day1 < 19000000 && Day2 < 19000000)
    {
        Day1 = ExcelDateToCDate(Day1);
        Day2 = ExcelDateToCDate(Day2);
    }

    if (Flag == 0) return DayCountAtoB(Day1, Day2) / 365.0;
    else if (Flag == 1) return DayCountAtoB(Day1, Day2) / 360.;
    else if (Flag == 2)
    {
        long YearA, YearB;
        long MonthA, MonthB;
        long DayA, DayB;
        long CurrentY;
        long NextY;

        YearA = Day1 / 10000;
        MonthA = (Day1 - YearA * 10000) / 100;
        DayA = (Day1 - YearA * 10000 - MonthA * 100);

        YearB = Day2 / 10000;
        MonthB = (Day2 - YearB * 10000) / 100;
        DayB = (Day2 - YearB * 10000 - MonthB * 100);

        NextY = Day1 + 10000;
        if (Day2 > Day1 && Day2 < NextY)
        {
            Div = DayCountAtoB(Day1, NextY);
            return DayCountAtoB(Day1, Day2) / Div;
        }
        else
        {
            tau = 0.;
            for (i = 0; i <= YearB - YearA; i++)
            {
                CurrentY = Day1 + i * 10000;
                NextY = Day1 + (i + 1) * 10000;
                if (Day2 > CurrentY && Day2 <= NextY)
                {
                    Div = DayCountAtoB(CurrentY, NextY);
                    tau += DayCountAtoB(CurrentY, Day2) / Div;
                    break;
                }
                else
                {
                    tau += 1.0;
                }
            }
            return tau;
        }
    }
    else
    {
        long YearA, YearB;
        long MonthA, MonthB;
        long nMonth;
        YearA = Day1 / 10000;
        MonthA = (Day1 - YearA * 10000) / 100;

        YearB = Day2 / 10000;
        MonthB = (Day2 - YearB * 10000) / 100;

        nMonth = (YearB - YearA) * 12 + (MonthB - MonthA);
        return ((double)30. * (nMonth)) / 360.0;
    }
}

DLLEXPORT(long) isin(long x, long* array, long narray)
{
    long i;
    long s = 0;
    for (i = 0; i < narray; i++)
    {
        if (x == array[i])
        {
            s = 1;
            break;
        }
    }
    return s;
}

long isin(long x, long* array, long narray, long& startidx)
{
    long i;
    long s = 0;
    for (i = startidx; i < narray; i++)
    {
        if (x == array[i])
        {
            s = 1;
            startidx = i;
            break;
        }
    }
    return s;
}


long isinFindIndex(long x, long* array, long narray, long& Idx)
{
    long i;
    long s = 0;
    Idx = -1;
    for (i = 0; i < narray; i++)
    {
        if (x == array[i])
        {
            s = 1;
            Idx = i;
            break;
        }
    }
    return s;
}

long isinFindIndex(long x, long* array, long narray, long& Idx, long* startidx)
{
    long i;
    long ii = *startidx;
    long s = 0;
    Idx = -1;
    for (i = ii; i < narray; i++)
    {
        if (x == array[i])
        {
            *startidx = i;
            s = 1;
            Idx = i;
            break;
        }
    }
    return s;
}

long isbetweenFindIndex(long x, long* array, long narray, long& idx)
{
    long i;
    long s = 0;
    long temp = -1;

    for (i = idx; i < narray - 1; i++)
    {
        if (x >= array[i] && x < array[i + 1])
        {
            s = 1;
            temp = 1;
            idx = temp;
            break;
        }
    }
    return s;
}

long isweekend(long ExlDate)
{
    // 나머지 1이면 일요일, 2이면 월요일, 3이면 화요일, 4이면 수요일, 5이면 목요일, 6이면 금요일, 0이면 토요일
    long MOD7;
    if (ExlDate > 0)
    {
        MOD7 = ExlDate % 7;
        if (MOD7 == 1 || MOD7 == 0) return 1;
    }
    return 0;
}

void LockOutCheck(long& LockOutFlag, long LockOutDay, long Today, double& LockOutDayRate, double& ForwardRate)
{
    if (LockOutFlag == 1) ForwardRate = LockOutDayRate + 0.0;
    else
    {
        if (LockOutDay <= Today)
        {
            LockOutDayRate = ForwardRate + 0.0;
            LockOutFlag = 1;
        }
    }
}

long FindIndex(
    long x,
    long* array,
    long narray
)
{
    long i;
    for (i = 0; i < narray; i++)
    {
        if (x == array[i])
        {
            return i;
        }
    }

    if (i == narray) i = -1;

    return i;
}

long FindIndex(
    long x,
    long* array,
    long narray,
    long* loopstart
)
{
    long i;
    long idxstart = *loopstart;
    for (i = max(0, idxstart); i < narray; i++)
    {
        if (x == array[i])
        {
            *loopstart = i;
            return i;
        }
    }

    if (i == narray) i = -1;

    return i;
}

double sumation_array(long n, double* myarray)
{
    double res = 0;
    for (long i = 0; i < n; i++) res += myarray[i];
    return res;
}

long NGenerated_CpnDate(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& FirstCpnDate)
{
    long i, j;

    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

    long n = ((SwapMat_YYYYMMDD / 10000 - PriceDateYYYYMMDD / 10000) + 2) * AnnCpnOneYear;
    long narray = 0;
    long CpnDate;
    long m = max(1, 12 / AnnCpnOneYear);
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);
        if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7)
        {
            FirstCpnDate = CpnDate;
            break;
        }
        if (CpnDate <= PriceDateYYYYMMDD) break;
        narray++;
    }
    return narray;
}

long* Generate_CpnDate_Without_Holiday(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate)
{
    long i, j;

    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

    long n = ((SwapMat_YYYYMMDD / 10000 - PriceDateYYYYMMDD / 10000) + 2) * AnnCpnOneYear;
    long narray = 0;
    long CpnDate;
    long m = max(1, 12 / AnnCpnOneYear);
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);
        if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7)
        {
            FirstCpnDate = CpnDate;
            break;
        }
        if (CpnDate <= PriceDateYYYYMMDD) break;
        narray++;
    }

    long* ResultCpnDate = (long*)malloc(sizeof(long) * narray);
    long CpnDateExcel, CpnDateTemp;
    long MOD7;
    long SaturSundayFlag;
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);

        if (CpnDate <= PriceDateYYYYMMDD || DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7) break;
        else
        {
            CpnDateExcel = CDateToExcelDate(CpnDate);
            MOD7 = CpnDateExcel % 7;
            if (MOD7 == 1 || MOD7 == 0) SaturSundayFlag = 1;
            else SaturSundayFlag = 0;

            if (SaturSundayFlag == 0)
            {
                ResultCpnDate[narray - 1 - i] = CpnDate;
            }
            else
            {
                // Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
                for (j = 1; j <= 7; j++)
                {
                    CpnDateExcel += 1;
                    MOD7 = CpnDateExcel % 7;
                    CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
                    if (MOD7 != 1 && MOD7 != 0)
                    {
                        CpnDate = ExcelDateToCDate(CpnDateExcel);
                        break;
                    }
                }
                ResultCpnDate[narray - 1 - i] = CpnDate;
            }
        }
    }
    lenArray = narray;
    if (AnnCpnOneYear == 1 && PriceMM != SwapMatMM)
    {
        long TargetDateYYYYMMDD = ResultCpnDate[0];
        long TargetDateYYYY;
        long TargetDateMM;
        for (i = 1; i <= 12; i++)
        {
            TargetDateYYYYMMDD = EDate_Cpp(TargetDateYYYYMMDD, -1);
            TargetDateYYYY = (long)TargetDateYYYYMMDD / 10000;
            TargetDateMM = (long)(TargetDateYYYYMMDD - TargetDateYYYY * 10000) / 100;
            if (TargetDateYYYY == PriceYYYY && TargetDateMM == PriceMM)
            {
                FirstCpnDate = TargetDateYYYYMMDD;
                break;
            }
        }
    }
    return ResultCpnDate;
}

long* Generate_CpnDate_With_Holiday(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD, long ModifiedFollowing = 1)
{
    long i, j;
    long LastBusiDay;
    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

    long n = ((SwapMat_YYYYMMDD / 10000 - PriceDateYYYYMMDD / 10000) + 2) * AnnCpnOneYear;
    long narray = 0;
    long CpnDate;
    long m = max(1, 12 / AnnCpnOneYear);
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);
        if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7)
        {
            FirstCpnDate = CpnDate;
            break;
        }
        if (CpnDate <= PriceDateYYYYMMDD) break;
        narray++;
    }

    long* ResultCpnDate = (long*)malloc(sizeof(long) * narray);
    long CpnDateExcel, CpnDateTemp;
    long MOD7;
    long SaturSundayFlag;
    long PrevDate;
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);

        if (CpnDate <= PriceDateYYYYMMDD || DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7) break;
        else
        {
            CpnDateExcel = CDateToExcelDate(CpnDate);
            MOD7 = CpnDateExcel % 7;
            if ((MOD7 == 1 || MOD7 == 0) || isin_Longtype(CpnDate, HolidayYYYYMMDD, NHoliday)) SaturSundayFlag = 1;
            else SaturSundayFlag = 0;

            if (SaturSundayFlag == 0)
            {
                ResultCpnDate[narray - 1 - i] = CpnDate;
            }
            else
            {
                if (ModifiedFollowing == 1)
                {
                    // Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
                    for (j = 1; j <= 7; j++)
                    {
                        CpnDateExcel += 1;
                        MOD7 = CpnDateExcel % 7;
                        CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
                        if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
                        {
                            PrevDate = ExcelDateToCDate(CpnDateExcel);
                            break;
                        }
                    }
                    ResultCpnDate[narray - 1 - i] = min(LastBusinessDate((long)(CpnDate / 100), NHoliday, HolidayYYYYMMDD), PrevDate);
                }
                else
                {
                    // Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
                    for (j = 1; j <= 7; j++)
                    {
                        CpnDateExcel += 1;
                        MOD7 = CpnDateExcel % 7;
                        CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
                        if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
                        {
                            CpnDate = ExcelDateToCDate(CpnDateExcel);
                            break;
                        }
                    }
                    ResultCpnDate[narray - 1 - i] = CpnDate;
                }
            }
        }
    }
    lenArray = narray;
    if (AnnCpnOneYear == 1 && PriceMM != SwapMatMM)
    {
        long TargetDateYYYYMMDD = ResultCpnDate[0];
        long TargetDateYYYY;
        long TargetDateMM;
        for (i = 1; i <= 12; i++)
        {
            TargetDateYYYYMMDD = EDate_Cpp(TargetDateYYYYMMDD, -1);
            TargetDateYYYY = (long)TargetDateYYYYMMDD / 10000;
            TargetDateMM = (long)(TargetDateYYYYMMDD - TargetDateYYYY * 10000) / 100;
            if (TargetDateYYYY == PriceYYYY && TargetDateMM == PriceMM)
            {
                FirstCpnDate = TargetDateYYYYMMDD;
                break;
            }
        }
    }
    return ResultCpnDate;
}

double Simulated_ShortRate(
    double XA,
    double XV,
    double ShortRate_Prev,
    double epsilon
)
{
    double xt = ShortRate_Prev;
    double x_next = XA * xt + XV * epsilon;
    return x_next;
}

double HW_Rate(
    long ReferenceType,
    double t,
    double T,
    long NRateTerm,
    double* RateTerm,
    double* Rate,
    double ShortRate,
    long NCfSwap,
    long NCPN_Ann,
    double* PV_t_T,
    double* QVTerm,
    double* B_t_T,
    double* dt,
    long HW2FFlag,
    double ShortRate2F,
    double* QVTerm_2F,
    double* B_t_T_2F,
    double* CrossTerm_2F
)
{
    long i;
    double PtT;
    double term = 1.0 / ((double)NCPN_Ann);
    double ResultRate;
    double A, B;
    if (ReferenceType == 0) NCfSwap = 1;
    if (NCPN_Ann > 0)
    {
        B = 0.0;
        for (i = 0; i < NCfSwap; i++)
        {
            term = dt[i];
            PtT = PV_t_T[i] * exp(-ShortRate * B_t_T[i] + QVTerm[i]);
            if (HW2FFlag > 0) PtT = PtT * exp(-ShortRate2F * B_t_T_2F[i] + QVTerm_2F[i] + CrossTerm_2F[i]);
            B += term * PtT;
        }

        ResultRate = (1. - PtT) / B;
    }
    else
    {
        if (t >= 0.0)
        {
            PtT = PV_t_T[0] * exp(-ShortRate * B_t_T[0] + QVTerm[0]);
            if (HW2FFlag > 0) PtT = PtT * exp(-ShortRate2F * B_t_T_2F[0] + QVTerm_2F[0] + CrossTerm_2F[0]);
        }
        else PtT = Calc_Discount_Factor(RateTerm, Rate, NRateTerm, T);

        if (dt[0] < 1.0) ResultRate = (1.0 - PtT) / (dt[0] * PtT);
        else ResultRate = -1.0 / dt[0] * log(PtT);
    }

    return ResultRate;
}

long Count_Accrual_Fast(
    long NDays,
    double Rate1,
    double Rate2,
    double LowerBound,
    double UpperBound
)
{
    long nAccrual;
    double Ratio = 0.0;
    double a, b;
    double r_min = min(Rate1, Rate2);
    double r_max = max(Rate1, Rate2);
    if (LowerBound <= r_min && UpperBound >= r_min && LowerBound <= r_max && UpperBound >= r_max) nAccrual = NDays; // 둘 다 Range 만족한 경우
    else if ((LowerBound > r_max) || (UpperBound < r_min)) nAccrual = 0;   // 둘 다 Upper 위나 Lower 아래에 있는 경우
    else if ((LowerBound < r_min) && (UpperBound < r_max))
    {
        a = UpperBound - r_min;
        b = r_max - r_min;
        Ratio = a / b;
        nAccrual = (long)(Ratio * (double)NDays);
    }
    else if ((LowerBound > r_min) && (UpperBound > r_max))
    {
        a = UpperBound - r_max;
        b = r_max - r_min;
        Ratio = a / b;
        nAccrual = (long)(Ratio * (double)NDays);
    }
    else
    {
        Ratio = ((UpperBound - LowerBound) / (r_max - r_min));
        nAccrual = (long)(Ratio * (double)NDays);
    }
    return nAccrual;
}

double PayoffStructure(
    long DailySimulFlag,
    LEG_INFO* Leg_Inform,
    double** SimulatedRate,  // Reset Start Rate
    double** SimulatedRate2, // Reset End Rate
    double** DailyRate,
    long CashFlowIdx,
    long Flag_Required_History,
    double* OutputRate,
    long& NumAccrual
)
{
    long i;
    long j;

    long N;
    long CalcFastFlag = 1;
    long AverageFlag;
    if (Leg_Inform->AccrualFlag == -1) AverageFlag = 1;
    else AverageFlag = 0;
    double AvgRate = 0.;

    double s;
    double dt;
    double Rate, Rate1, Rate2;
    double RateArrayTemp[2];
    double RateTermTemp[2];
    long DayBefore;
    long DayBeforeIdx;
    long ExistHistoryFlag = 0;

    double MaxLoss = Leg_Inform->MaxLossY;
    double MaxRet = Leg_Inform->MaxRetY;

    double LowerBound;
    double UpperBound;
    double CondMultiple;
    double PayoffMultiple;
    double Payoff = 0.0;
    double StrCpn = 0.0;
    
    double CPN_Ratio = 1.0;
    long Cond = 1;
    long NDays;
    long StartYYYYMMDD;
    long EndYYYYMMDD;
    long TempYYYYMMDD;

    NumAccrual = 0;
    NDays = Leg_Inform->DaysForwardEnd[CashFlowIdx] - Leg_Inform->DaysForwardStart[CashFlowIdx];
    StartYYYYMMDD = Leg_Inform->ForwardStart_C[CashFlowIdx];
    EndYYYYMMDD = Leg_Inform->ForwardEnd_C[CashFlowIdx];
    
    dt = 0.0;
    for (i = 0; i < Leg_Inform->NReference; i++)
    {
        dt += DayCountFractionAtoB(StartYYYYMMDD, EndYYYYMMDD, Leg_Inform->Reference_Inform[i].DayCountFlag) * 1.0 / (double)Leg_Inform->NReference;
    }

    N = NDays; // 일단 100% Accrual부터 시작

    if (DailySimulFlag == 0 && Leg_Inform->AccrualFlag == 1 && Flag_Required_History == 0)
    {
        //////////////////////////////////////////////////
        // dt간격 시뮬레이션 and 히스토리 필요없을경우  //
        //////////////////////////////////////////////////

        for (i = 0; i < Leg_Inform->NReference; i++)
        {
            if (Leg_Inform->Reference_Inform[i].RefRateType == 1)
            {
                Rate1 = SimulatedRate[i][CashFlowIdx];
                Rate2 = SimulatedRate2[i][CashFlowIdx];
                LowerBound = Leg_Inform->Reference_Inform[i].RangeDn;
                UpperBound = Leg_Inform->Reference_Inform[i].RangeUp;
                N = min(N, Count_Accrual_Fast(NDays, Rate1, Rate2, LowerBound, UpperBound));
            }
        }
        NumAccrual = N;
        CPN_Ratio = ((double)NumAccrual) / ((double)NDays);
    }
    else if (DailySimulFlag == 1 && Leg_Inform->AccrualFlag == 1 && Flag_Required_History == 0)
    {
        for (i = 0; i < Leg_Inform->NReference; i++)
        {
            if (Leg_Inform->Reference_Inform[i].RefRateType == 1)
            {
                N = 0;
                LowerBound = Leg_Inform->Reference_Inform[i].RangeDn;
                UpperBound = Leg_Inform->Reference_Inform[i].RangeUp;
                for (j = Leg_Inform->DaysForwardStart[CashFlowIdx]; j < Leg_Inform->DaysForwardEnd[CashFlowIdx]; j++)
                {
                    Rate = DailyRate[i][j];
                    if (Rate >= LowerBound && Rate <= UpperBound) N += 1;
                }
                NumAccrual = min(NumAccrual, N);
            }
        }
        CPN_Ratio = ((double)NumAccrual) / ((double)NDays);
    }

    if (Leg_Inform->PayoffStructure == 0)
    {
        ////////////////////////////
        // 기초금리 AND 조건일 때 //
        ////////////////////////////
        if (Flag_Required_History == 0)
        {
            if (AverageFlag == 0)
            {
                for (i = 0; i < Leg_Inform->NReference; i++)
                {
                    LowerBound = Leg_Inform->Reference_Inform[i].RangeDn;
                    UpperBound = Leg_Inform->Reference_Inform[i].RangeUp;
                    CondMultiple = Leg_Inform->Reference_Inform[i].RefRateCondMultiple;
                    PayoffMultiple = Leg_Inform->Reference_Inform[i].PayoffMultiple;
                    OutputRate[i] = SimulatedRate[i][CashFlowIdx];
                    if (LowerBound <= CondMultiple * SimulatedRate[i][CashFlowIdx] && UpperBound >= CondMultiple * SimulatedRate[i][CashFlowIdx]) Cond = Cond * 1;
                    else Cond = 0;
                    StrCpn += max(-MaxLoss, PayoffMultiple * SimulatedRate[i][CashFlowIdx]);
                }
                Payoff = StrCpn * (double)Cond * (double)Leg_Inform->FloatingFlag[CashFlowIdx] + Leg_Inform->CouponRate[CashFlowIdx] + (double)Cond * Leg_Inform->RangeCoupon[CashFlowIdx] * CPN_Ratio;
            }
            else
            {
                for (i = 0; i < Leg_Inform->NReference; i++)
                {
                    LowerBound = Leg_Inform->Reference_Inform[i].RangeDn;
                    UpperBound = Leg_Inform->Reference_Inform[i].RangeUp;
                    CondMultiple = Leg_Inform->Reference_Inform[i].RefRateCondMultiple;
                    PayoffMultiple = Leg_Inform->Reference_Inform[i].PayoffMultiple;
                    AvgRate = 0.5 * SimulatedRate[i][CashFlowIdx] + 0.5 * SimulatedRate2[i][CashFlowIdx];
                    OutputRate[i] = AvgRate;
                    if (LowerBound <= CondMultiple * AvgRate && UpperBound >= CondMultiple * AvgRate) Cond = Cond * 1;
                    else Cond = 0;
                    StrCpn += PayoffMultiple * AvgRate;
                }
                Payoff = StrCpn * (double)Cond * (double)Leg_Inform->FloatingFlag[CashFlowIdx] + Leg_Inform->CouponRate[CashFlowIdx] + (double)Cond * Leg_Inform->RangeCoupon[CashFlowIdx] * CPN_Ratio;
            }

        }
        else
        {
            //////////////////////////////
            // Rate History 뒤져야 할 때
            //////////////////////////////
            DayBefore = -1;
            ExistHistoryFlag = 1;

            RateTermTemp[0] = (double)Leg_Inform->DaysForwardStart[CashFlowIdx];
            RateTermTemp[1] = (double)Leg_Inform->DaysForwardEnd[CashFlowIdx];

            Payoff = 0.0;
            Rate2 = 0.0;
            NumAccrual = NDays;     // 100% Accrual부터 시작
            for (i = 0; i < Leg_Inform->NReference; i++)
            {
                RateArrayTemp[0] = SimulatedRate[i][CashFlowIdx];
                RateArrayTemp[1] = SimulatedRate2[i][CashFlowIdx];
                if (RateArrayTemp[0] == 0.0)
                {
                    ExistHistoryFlag = isinFindIndex(Leg_Inform->ForwardStart_C[CashFlowIdx], Leg_Inform->RateHistoryDateMatrix[i], Leg_Inform->NDayHistory[i], DayBeforeIdx);
                    if (ExistHistoryFlag == 1)
                    {
                        RateArrayTemp[0] = Leg_Inform->RateHistoryMatrix[i][DayBeforeIdx];
                    }
                    else
                    {
                        RateArrayTemp[0] = RateArrayTemp[1];
                    }
                    Rate2 = RateArrayTemp[0];
                }

                LowerBound = Leg_Inform->Reference_Inform[i].RangeDn;
                UpperBound = Leg_Inform->Reference_Inform[i].RangeUp;
                CondMultiple = Leg_Inform->Reference_Inform[i].RefRateCondMultiple;
                PayoffMultiple = Leg_Inform->Reference_Inform[i].PayoffMultiple;
                N = NDays;

                if (Leg_Inform->AccrualFlag == 1)
                {
                    /////////////////////////////////
                    // History 뒤지면서 Accrual
                    /////////////////////////////////
                    for (j = 0; j < NDays; j++)
                    {
                        if (j == 0) TempYYYYMMDD = StartYYYYMMDD;
                        else TempYYYYMMDD = DayPlus(TempYYYYMMDD, 1);
                        ExistHistoryFlag = isinFindIndex(TempYYYYMMDD, Leg_Inform->RateHistoryDateMatrix[i], Leg_Inform->NDayHistory[i], DayBeforeIdx);
                        if (ExistHistoryFlag != 0) Rate = Leg_Inform->RateHistoryMatrix[i][DayBeforeIdx];
                        else Rate = SimulatedRate[i][CashFlowIdx];
                        if (Rate >= LowerBound && Rate <= UpperBound) N += 1;
                    }
                }

                NumAccrual = min(NumAccrual, N);
                
                if (AverageFlag == 0)
                {
                    OutputRate[i] = Rate2;
                    StrCpn += PayoffMultiple * Rate2;
                    if (LowerBound <= CondMultiple * Rate2 && UpperBound >= CondMultiple * Rate2) Cond = Cond * 1;
                    else Cond = 0;
                }
                else
                {
                    AvgRate = 0.5 * Rate2 + 0.5 * SimulatedRate2[i][CashFlowIdx];
                    OutputRate[i] = AvgRate;
                    StrCpn += PayoffMultiple * AvgRate;
                    if (LowerBound <= CondMultiple * AvgRate && UpperBound >= CondMultiple * AvgRate) Cond = Cond * 1;
                    else Cond = 0;
                }
            }

            CPN_Ratio = ((double)NumAccrual) / ((double)NDays);
            Payoff = StrCpn * (double)Cond * (double)Leg_Inform->FloatingFlag[CashFlowIdx] + Leg_Inform->CouponRate[CashFlowIdx] + (double)Cond * Leg_Inform->RangeCoupon[CashFlowIdx] * CPN_Ratio;
        }
    }

    return min(MaxRet, max(-MaxLoss, Payoff)) * dt;
}

double SOFR_Compounded_Rate(
    long PriceDate,
    long EstStartDate,
    long EstEndDate,
    double DF_to_EstEndDate,
    long NHistory,
    long* HistoryDate,
    double* HistoryRate,
    long NHoliday,
    long* Holiday,
    double DefaultOverNightRate,
    long DayCountFlag,
    double& CompValue
)
{
    long i, j, TempDate;
    long EstStartDateExl, EstEndDateExl, PriceDateExl;
    long NNextHoliday;
    double DayFrac = DayCountFractionAtoB(EstStartDate, EstEndDate, DayCountFlag);
    EstStartDateExl = CDateToExcelDate(EstStartDate);
    EstEndDateExl = CDateToExcelDate(EstEndDate);
    PriceDateExl = CDateToExcelDate(PriceDate);
    long HistoryDateExl, NextDayExl, CDate, idx;
    double dt = 1.0 / 365.0;
    double Compounded = 1.0;
    double r = 0.;
    for (TempDate = EstStartDateExl; TempDate < PriceDateExl; TempDate++)
    {
        CDate = ExcelDateToCDate(TempDate);
        if (isinFindIndex(CDate, HistoryDate, NHistory, idx) > 0) r = HistoryRate[idx];
        else r = DefaultOverNightRate;

        NNextHoliday = 0;
        if (isweekend(ExcelDateToCDate(TempDate + 1)) == 1 || isin(ExcelDateToCDate(TempDate + 1), Holiday, NHoliday))
        {
            // 내일이 주말이거나 Holiday일 경우
            NNextHoliday = 0;
            for (NextDayExl = TempDate + 1; NextDayExl < TempDate + 10; NextDayExl++)
            {
                if (isweekend(ExcelDateToCDate(NextDayExl)) == 1 || isin(ExcelDateToCDate(NextDayExl), Holiday, NHoliday)) NNextHoliday += 1;
                else break;
            }
        }
        Compounded *= (1.0 + r * dt * (double)(NNextHoliday + 1));
    }
    Compounded *= 1.0 / DF_to_EstEndDate;
    CompValue = Compounded;
    return (Compounded - 1.0) * 1.0 / DayFrac;
}


long Simulate_HW(
    long PricingOnly,
    long PricingDateC,
    long NAFlag,
    double Notional,
    LEG_INFO* RcvLeg,
    LEG_INFO* PayLeg,
    SIMUL_INFO* Simul,
    HW_INFO* HW_Information,
    double** SimulatedRateRcv,
    double** SimulatedRateRcv2,
    double** SimulatedRatePay,
    double** SimulatedRatePay2,
    double** SimulShortRate,
    double** SimulShortRate2F,
    long* CurveIdx_Rcv,
    long* CurveIdx_Pay,
    double* ResultPrice,                // 
    double* ResultRcv,                  // 
    double* ResultPay                   // 
)
{
    long i;
    long j;
    long k;

    long NoteFlag = 0;
    long nNaN = 0;
    for (i = 0; i < PayLeg->NCashFlow; i++)
    {
        // Payleg 구조화금리, 쿠폰, RangeCoupon 모두 0이면 Bond평가로 간주
        if ((PayLeg->CouponRate[i] == 0.0) && (PayLeg->FloatingFlag[i] == 0) && (PayLeg->RangeCoupon[i] == 0.0)) nNaN += 1;
    }
    if (nNaN == PayLeg->NCashFlow)
    {
        NoteFlag = 1;
    }

    ////////////////////
    // SOFR Compound  //
    ////////////////////

    long CurveIdxRef;
    double t, T, T1, T2, Pt, PT, PtT;
    double r_sofr, compvalue, r0;
    double SOFRComp0_Rcv[5] = { 0.0,0.0,0.0 };
    double SOFR_AnnOISRate0_Rcv[5] = { 0.0,0.0,0.0 };
    double SOFRComp0_Pay[5] = { 0.0,0.0,0.0 };
    double SOFR_AnnOISRate0_Pay[5] = { 0.0,0.0,0.0 };
    double DF_to_EstEnd;
    for (i = 0; i < RcvLeg->NReference; i++)
    {
        if (RcvLeg->Reference_Inform[i].RefRateType == 2)
        {
            for (j = 0; j < RcvLeg->NCashFlow; j++)
            {
                if (PricingDateC > RcvLeg->ForwardStart_C[j] && PricingDateC < RcvLeg->ForwardEnd_C[j])
                {
                    CurveIdxRef = CurveIdx_Rcv[i];
                    T1 = ((double)DayCountAtoB(PricingDateC, RcvLeg->ForwardEnd_C[j])) / 365.0;
                    r0 = Simul->Rate[CurveIdxRef][0];
                    DF_to_EstEnd = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    r_sofr = SOFR_Compounded_Rate(PricingDateC, RcvLeg->ForwardStart_C[j], RcvLeg->ForwardEnd_C[j], DF_to_EstEnd, RcvLeg->NDayHistory[i],
                        RcvLeg->RateHistoryDateMatrix[i], RcvLeg->RateHistoryMatrix[i], RcvLeg->HolidayCount[i], RcvLeg->HolidayDays[i], r0, RcvLeg->Reference_Inform[i].DayCountFlag, compvalue);
                    SOFRComp0_Rcv[i] = compvalue;
                    SOFR_AnnOISRate0_Rcv[i] = r_sofr;
                    SimulatedRateRcv[i][j] = r_sofr;
                    for (k = 0; k < RcvLeg->NDayHistory[i] - 1; k++)
                    {
                        if (RcvLeg->RateHistoryDateMatrix[i][k] <= RcvLeg->ForwardStart_C[j] && RcvLeg->RateHistoryDateMatrix[i][k + 1] > RcvLeg->ForwardStart_C[j])
                        {
                            RcvLeg->RateHistoryDateMatrix[i][k] = r_sofr;
                            break;
                        }
                    }
                    break;
                }
            }
        }
    }

    for (i = 0; i < PayLeg->NReference; i++)
    {
        if (PayLeg->Reference_Inform[i].RefRateType == 2)
        {
            for (j = 0; j < PayLeg->NCashFlow; j++)
            {
                if (PricingDateC > PayLeg->ForwardStart_C[j] && PricingDateC < PayLeg->ForwardEnd_C[j])
                {
                    CurveIdxRef = CurveIdx_Pay[i];
                    T1 = ((double)DayCountAtoB(PricingDateC, PayLeg->ForwardEnd_C[j])) / 365.0;
                    r0 = Simul->Rate[CurveIdxRef][0];
                    DF_to_EstEnd = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    r_sofr = SOFR_Compounded_Rate(PricingDateC, PayLeg->ForwardStart_C[j], PayLeg->ForwardEnd_C[j], DF_to_EstEnd, PayLeg->NDayHistory[i],
                        PayLeg->RateHistoryDateMatrix[i], PayLeg->RateHistoryMatrix[i], PayLeg->HolidayCount[i], PayLeg->HolidayDays[i], r0, PayLeg->Reference_Inform[i].DayCountFlag, compvalue);
                    SOFRComp0_Pay[i] = compvalue;
                    SOFR_AnnOISRate0_Pay[i] = r_sofr;
                    SimulatedRatePay[i][j] = r_sofr;
                    for (k = 0; k < PayLeg->NDayHistory[i] - 1; k++)
                    {
                        if (PayLeg->RateHistoryDateMatrix[i][k] <= PayLeg->ForwardStart_C[j] && PayLeg->RateHistoryDateMatrix[i][k + 1] > PayLeg->ForwardStart_C[j])
                        {
                            PayLeg->RateHistoryDateMatrix[i][k] = r_sofr;
                            break;
                        }
                    }
                    break;
                }
            }
        }
    }
    
    long idx0, idx1, idx2, idx3, idx4;
    long idxrcv, idxrcv2, idxrcv3, idxpay, idxpay2, idxpay3;

    long n;
    long nAccrual = 0;
    long ndates;

    long Curveidx;

    long xt_idx;
    long Day1, Day2, Day2YYYYMMDD;
    long Dayidx;
    long RateHistoryUseFlag = 0;
    double PricePath_Rcv, PricePath_Pay;
    double RcvPrice, PayPrice;
    double kappa;
    double xt = 0.0;
    double xt_2f = 0.0;
    double Rate = 0.0, Rate1 = 0.0, Rate2 = 0.0;

    
    double** RcvDailyRate = (double**)malloc(sizeof(double*) * RcvLeg->NReference);             // 1
    double** PayDailyRate = (double**)malloc(sizeof(double*) * PayLeg->NReference);             // 2
    if (Simul->DailySimulFlag == 1)
    {
        for (i = 0; i < RcvLeg->NReference; i++) RcvDailyRate[i] = (double*)malloc(sizeof(double) * (Simul->DaysForSimul[Simul->NDays - 1] + 1));
        for (i = 0; i < PayLeg->NReference; i++) PayDailyRate[i] = (double*)malloc(sizeof(double) * (Simul->DaysForSimul[Simul->NDays - 1] + 1));
    }

    double* RcvPayoff = (double*)malloc((RcvLeg->NCashFlow + 1) * sizeof(double));             // 3
    double* PayPayoff = (double*)malloc((PayLeg->NCashFlow + 1) * sizeof(double));             // 4
    long* RcvCFFlag = (long*)malloc(RcvLeg->NCashFlow * sizeof(long));             // 5
    long* PayCFFlag = (long*)malloc(PayLeg->NCashFlow * sizeof(long));             // 6

    RcvPrice = 0.0;
    PayPrice = 0.0;
    double SOFRDailyCompound = 0.0;

    double* RcvOutputRate = (double*)malloc(RcvLeg->NReference * sizeof(double));
    double* PayOutputRate = (double*)malloc(PayLeg->NReference * sizeof(double));

    double** Simul_QuantoTerm = (double**)malloc(sizeof(double*) * Simul->NAsset);
    for (i = 0; i < Simul->NAsset; i++) Simul_QuantoTerm[i] = (double*)malloc(sizeof(double) * Simul->NDays);

    double v;
    for (i = 0; i < Simul->NAsset; i++)
    {
        for (j = 0; j < Simul->NDays; j++)
        {
            v = Interpolate_Linear(Simul->HWVolTerm[i], Simul->HWVol[i], Simul->NHWVol[i], Simul->T_Array[i]);
            if (Simul->HWQuantoFlag[i] > 0.99) Simul_QuantoTerm[i][j] = Simul->HWQuantoRho[i] * Simul->HWQuantoVol[i] * v * Simul->dt_Array[j];
            else Simul_QuantoTerm[i][j] = 0.0;

            if (Simul->HWFactorFlag > 0)
            {
                v = Interpolate_Linear(Simul->HWVolTerm[i], Simul->HWVol2[i], Simul->NHWVol[i], Simul->T_Array[i]);
                if (Simul->HWQuantoFlag[i] > 0.99) Simul_QuantoTerm[i][j] += Simul->HWQuantoRho[i] * Simul->HWQuantoVol[i] * v * Simul->dt_Array[j];
            }
        }
    }

    ////////////////
    // LSMC Data  //
    ////////////////

    double* RcvP0T = (double*)malloc(sizeof(double) * RcvLeg->NCashFlow);
    double* PayP0T = (double*)malloc(sizeof(double) * PayLeg->NCashFlow);

    double*** X;
    long ShapeX[2] = { Simul->NSimul, Simul->NAsset + 1 + Simul->NAsset };
    double** Y;
    long** OptRangeFlag;
    long LengthY = Simul->NSimul;
    long idxoption;
    long idxstart;
    double T_Opt;
    double** Y_Hat;
    double* Beta;

    double* Value_By_OptTime;
    double* Estimated_Value_By_OptTime;
    long* OptimalIdx;
    double** InterestRate_Opt;
    double EstOptValue;
    if (RcvLeg->OptionUseFlag == 1)
    {
        Value_By_OptTime = (double*)malloc(sizeof(double) * Simul->NSimul);             // 7
        Estimated_Value_By_OptTime = (double*)malloc(sizeof(double*) * Simul->NSimul);             // 8
        OptimalIdx = (long*)malloc(sizeof(double) * Simul->NSimul);             // 9
        for (i = 0; i < Simul->NSimul; i++) OptimalIdx[i] = 0;

        InterestRate_Opt = (double**)malloc(sizeof(double**) * Simul->NSimul);             // 10
        for (i = 0; i < Simul->NSimul; i++) InterestRate_Opt[i] = (double*)malloc(sizeof(double) * (Simul->NAsset + 1 + Simul->NAsset));
        for (i = 0; i < Simul->NSimul; i++) InterestRate_Opt[i][Simul->NAsset] = 1.0;

        X = (double***)malloc(sizeof(double**) * RcvLeg->NOption);             // 11
        for (i = 0; i < RcvLeg->NOption; i++) X[i] = make_array(Simul->NSimul, Simul->NAsset + 1);

        Y = (double**)malloc(sizeof(double*) * RcvLeg->NOption);             // 12
        for (i = 0; i < RcvLeg->NOption; i++) Y[i] = make_array(Simul->NSimul);

        OptRangeFlag = (long**)malloc(sizeof(long*) * RcvLeg->NOption);             // 13
        for (i = 0; i < RcvLeg->NOption; i++) OptRangeFlag[i] = (long*)malloc(sizeof(long) * Simul->NSimul);

        Y_Hat = (double**)malloc(sizeof(double*) * RcvLeg->NOption);             // 14
        for (i = 0; i < RcvLeg->NOption; i++) Y_Hat[i] = (double*)malloc(sizeof(double) * (Simul->NSimul));

        for (i = 0; i < RcvLeg->NOption; i++)
            for (j = 0; j < Simul->NSimul; j++) X[i][j][Simul->NAsset] = 1.0;
    }
    else
    {
        RcvLeg->NOption = 0;
        X = (double***)malloc(sizeof(double**) * 1);
        Y = (double**)malloc(sizeof(double*) * 1);
        Value_By_OptTime = (double*)malloc(sizeof(double) * 1);
        Estimated_Value_By_OptTime = (double*)malloc(sizeof(double) * 1);
        OptimalIdx = (long*)malloc(sizeof(long) * 1);
        InterestRate_Opt = (double**)malloc(sizeof(double*) * 1);
        OptRangeFlag = (long**)malloc(sizeof(long*) * 1);
        Y_Hat = (double**)malloc(sizeof(double*) * 1);
    }

    long lastresetend = -1;
    double xt_termlsmc[2] = { 0.0,0.0 };
    double xt_lsmc[2] = { 0.0,0.0 };
    double xt_interp;
    double xt_interp2f;
    double* TimeOption = (double*)malloc(sizeof(double) * RcvLeg->NOption);
    for (idxoption = 0; idxoption < RcvLeg->NOption; idxoption++) TimeOption[idxoption] = ((double)DayCountAtoB(PricingDateC, RcvLeg->OptionDate[idxoption])) / 365.;
    double* DF_Opt = (double*)malloc(sizeof(double) * max(RcvLeg->NOption, 1));
    if (RcvLeg->OptionUseFlag == 1)
    {
        for (idxoption = 0; idxoption < RcvLeg->NOption; idxoption++)
        {
            T_Opt = TimeOption[idxoption];
            if (RcvLeg->OptionType == 1) DF_Opt[idxoption] = Calc_Discount_Factor(Simul->RateTerm[HW_Information->CurveIdx_DiscRcv], Simul->Rate[HW_Information->CurveIdx_DiscRcv], Simul->NRateTerm[HW_Information->CurveIdx_DiscRcv], T_Opt);
            else DF_Opt[idxoption] = Calc_Discount_Factor(Simul->RateTerm[HW_Information->CurveIdx_DiscPay], Simul->Rate[HW_Information->CurveIdx_DiscPay], Simul->NRateTerm[HW_Information->CurveIdx_DiscPay], T_Opt);
        }
    }
    double* DF_To_Pay;
    if (RcvLeg->OptionType == 1) DF_To_Pay = (double*)malloc(sizeof(double) * RcvLeg->NCashFlow);
    else DF_To_Pay = (double*)malloc(sizeof(double) * PayLeg->NCashFlow);

    if (RcvLeg->OptionType == 1)
    {
        for (i = 0; i < RcvLeg->NCashFlow; i++)
        {
            t = ((double)DayCountAtoB(PricingDateC, RcvLeg->PayDate_C[i])) / 365.0;
            DF_To_Pay[i] = Calc_Discount_Factor(Simul->RateTerm[HW_Information->CurveIdx_DiscRcv], Simul->Rate[HW_Information->CurveIdx_DiscRcv], Simul->NRateTerm[HW_Information->CurveIdx_DiscRcv], t);
        }        
    }
    else
    {
        for (i = 0; i < PayLeg->NCashFlow; i++)
        {
            t = ((double)DayCountAtoB(PricingDateC, PayLeg->PayDate_C[i])) / 365.0;
            DF_To_Pay[i] = Calc_Discount_Factor(Simul->RateTerm[HW_Information->CurveIdx_DiscPay], Simul->Rate[HW_Information->CurveIdx_DiscPay], Simul->NRateTerm[HW_Information->CurveIdx_DiscPay], t);
        }
    }

    double** RcvPayoffResult = (double**)malloc(sizeof(double*) * Simul->NSimul);
    double** PayPayoffResult = (double**)malloc(sizeof(double*) * Simul->NSimul);
    for (i = 0; i < Simul->NSimul; i++) RcvPayoffResult[i] = (double*)malloc(sizeof(double) * RcvLeg->NCashFlow);
    for (i = 0; i < Simul->NSimul; i++) PayPayoffResult[i] = (double*)malloc(sizeof(double) * PayLeg->NCashFlow);

    double PtTOptPay, LastFixingCouponRcv, LastFixingCouponPay, LastFixingCoupon;
    double NotionalValue[2] = { 0.0, 0.0 };
    long SimDayYYYYMMDD, LastFixingIdxRcv, LastFixingIdxPay;

    for (i = 0; i < Simul->NSimul; i++)
    {
        PricePath_Rcv = 0.0;
        PricePath_Pay = 0.0;

        /////////////////////////////////
        // 1. Short Rate Simulation    // 
        /////////////////////////////////

        for (j = 0; j < Simul->NDays; j++)
        {
            for (n = 0; n < Simul->NAsset; n++)
            {
                if (j == 0)
                {
                    SimulShortRate[n][j] = 0.0;
                    if (Simul->HWFactorFlag > 0) SimulShortRate2F[n][j] = 0.0;
                }
                else
                {
                    SimulShortRate[n][j] = Simulated_ShortRate(HW_Information->XA[n][j], HW_Information->XV[n][j], SimulShortRate[n][j - 1], Simul->FixedRandn[i * Simul->NDays + j][n]);
                    if (Simul->HWFactorFlag > 0) SimulShortRate2F[n][j] = Simulated_ShortRate(HW_Information->XA2F[n][j], HW_Information->XV2F[n][j], SimulShortRate2F[n][j - 1], Simul->FixedRandn2[i * Simul->NDays + j][n]);

                    SimulShortRate[n][j] -= Simul_QuantoTerm[n][j];
                }
            }
        }

        //////////////////////////////////////
        // 2. Xt at Option Exercise Date    // 
        // 옵션 행사시점의 Xt               //
        //////////////////////////////////////

        for (idxoption = 0; idxoption < RcvLeg->NOption; idxoption++)
        {
            T_Opt = TimeOption[idxoption];
            if (T_Opt <= Simul->T_Array[0])
            {
                xt_termlsmc[0] = 0.;
                xt_termlsmc[1] = Simul->T_Array[0];
                for (n = 0; n < Simul->NAsset; n++)
                {
                    xt_lsmc[0] = 0.;
                    xt_lsmc[1] = SimulShortRate[n][0];
                    xt_interp = Interpolate_Linear(xt_termlsmc, xt_lsmc, 2, T_Opt);
                    X[idxoption][i][n] = xt_interp;
                    if (Simul->HWFactorFlag > 0)
                    {
                        xt_lsmc[0] = 0.;
                        xt_lsmc[1] = SimulShortRate2F[n][0];
                        xt_interp = Interpolate_Linear(xt_termlsmc, xt_lsmc, 2, T_Opt);
                        X[idxoption][i][n] = X[idxoption][i][n] + xt_interp;
                    }
                }
            }
            else if (T_Opt >= Simul->T_Array[Simul->NDays - 1])
            {
                for (n = 0; n < Simul->NAsset; n++)
                {
                    X[idxoption][i][n] = SimulShortRate[n][Simul->NDays - 1];
                    if (Simul->HWFactorFlag > 0) X[idxoption][i][n] = X[idxoption][i][n] + SimulShortRate2F[n][Simul->NDays - 1];
                }
            }
            else
            {
                for (j = 0; j < Simul->NDays-1; j++)
                {
                    if (T_Opt < Simul->T_Array[j + 1] && T_Opt >= Simul->T_Array[j])
                    {
                        xt_termlsmc[0] = Simul->T_Array[j];
                        xt_termlsmc[1] = Simul->T_Array[j + 1];
                        for (n = 0; n < Simul->NAsset; n++)
                        {
                            xt_lsmc[0] = SimulShortRate[n][j];
                            xt_lsmc[1] = SimulShortRate[n][j + 1];
                            xt_interp = Interpolate_Linear(xt_termlsmc, xt_lsmc, 2, T_Opt);
                            X[idxoption][i][n] = xt_interp;
                            if (Simul->HWFactorFlag > 0)
                            {
                                xt_lsmc[0] = SimulShortRate2F[n][j];
                                xt_lsmc[1] = SimulShortRate2F[n][j + 1];
                                xt_interp = Interpolate_Linear(xt_termlsmc, xt_lsmc, 2, T_Opt);
                                X[idxoption][i][n] = X[idxoption][i][n] + xt_interp;
                            }
                        }
                        break;
                    }
                }
            }
        }

        //////////////////////////////////////////
        // 3~4 Calculate RcvLeg Reference Rate  //
        // 3. Not DailySimul Case               //
        // 4. DailySimul Case                   //
        //////////////////////////////////////////

        for (n = 0; n < RcvLeg->NReference; n++)
        {
            Curveidx = CurveIdx_Rcv[n];
            lastresetend = -1;
            Rate = 0.0;
            Rate1 = 0.0;
            Rate2 = 0.0;
            idxrcv = 0;
            idxrcv2 = 0;
            idxrcv3 = 0;
            if (Simul->DailySimulFlag == 0)
            {
                /////////////////////////////////////////
                // 3.1 Calculation Reference Rate      //
                // on ResetDate(DaysForwardStart[j])   //
                // 리셋시점의 기초금리 계산            //
                /////////////////////////////////////////

                for (j = 0; j < Simul->NDays; j++)
                {
                    if (isinFindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardStart, RcvLeg->NCashFlow, Dayidx))
                    {
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;
                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        if (RcvLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                        {
                            ////////////////////////////////////////
                            // 3.1.1 PowerSpread 상품이 아닌 경우 // 
                            ////////////////////////////////////////

                            t = ((double)RcvLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T = ((double)RcvLeg->DaysForwardEnd[Dayidx]) / 365.0;
                            Rate = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f, 
                                HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);
                        }
                        else
                        {
                            ///////////////////////////////////
                            // 3.1.2 PowerSpread 상품의 경우 // 
                            ///////////////////////////////////

                            t = ((double)RcvLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T1 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat1;
                            T2 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat2;

                            Rate1 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f, 
                                HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);

                            Rate2 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T_PowerSpread[n][j],
                                HW_Information->RcvRef_QVTerm_PowerSpread[n][j], HW_Information->RcvRef_B_t_T_PowerSpread[n][j], HW_Information->RcvRef_dt_PowerSpread[n][j], Simul->HWFactorFlag, xt_2f, 
                                HW_Information->RcvRef_QVTerm_PowerSpread2F[n][j], HW_Information->RcvRef_B_t_T_PowerSpread2F[n][j], HW_Information->RcvRef_CrossTerm_PowerSpread2F[n][j]);

                            Rate = Rate1 - Rate2;
                        }
                        SimulatedRateRcv[n][Dayidx] = Rate;
                    }

                    if (isinFindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardEnd, RcvLeg->NCashFlow, Dayidx))
                    {
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;
                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        if (RcvLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                        {
                            ////////////////////////////////////////
                            // 3.1.1 PowerSpread 상품이 아닌 경우 // 
                            ////////////////////////////////////////

                            t = ((double)RcvLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T = ((double)RcvLeg->DaysForwardEnd[Dayidx]) / 365.0;
                            Rate = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);
                        }
                        else
                        {
                            ///////////////////////////////////
                            // 3.1.2 PowerSpread 상품의 경우 // 
                            ///////////////////////////////////

                            t = ((double)RcvLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T1 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat1;
                            T2 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat2;

                            Rate1 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);

                            Rate2 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T_PowerSpread[n][j],
                                HW_Information->RcvRef_QVTerm_PowerSpread[n][j], HW_Information->RcvRef_B_t_T_PowerSpread[n][j], HW_Information->RcvRef_dt_PowerSpread[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->RcvRef_QVTerm_PowerSpread2F[n][j], HW_Information->RcvRef_B_t_T_PowerSpread2F[n][j], HW_Information->RcvRef_CrossTerm_PowerSpread2F[n][j]);

                            Rate = Rate1 - Rate2;
                        }
                        SimulatedRateRcv2[n][Dayidx] = Rate;
                    }
                }
            }
            else // if (Simul->DailySimulFlag == 1 )
            {
                for (j = 0; j < Simul->NDays; j++)
                {
                    if (isinFindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardStart, RcvLeg->NCashFlow, Dayidx, &idxrcv))
                    {
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;
                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        t = Simul->T_Array[j];
                        if (RcvLeg->Reference_Inform[n].RefRateType <= 2)
                        {
                            if (RcvLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                            {
                                ////////////////////////////////////////
                                // 4.1.1 PowerSpread 상품이 아닌 경우 // 
                                ////////////////////////////////////////

                                T = ((double)RcvLeg->DaysForwardEnd[Dayidx]) / 365.0;
                                Rate = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                    HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                    HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);
                            }
                            else
                            {
                                ///////////////////////////////////
                                // 4.1.2 PowerSpread 상품의 경우 // 
                                ///////////////////////////////////

                                T1 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat1;
                                T2 = t + RcvLeg->Reference_Inform[n].PowerSpreadMat2;

                                Rate1 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T[n][j],
                                    HW_Information->RcvRef_QVTerm[n][j], HW_Information->RcvRef_B_t_T[n][j], HW_Information->RcvRef_dt[n][j], Simul->HWFactorFlag, xt_2f, 
                                    HW_Information->RcvRef_QVTerm2F[n][j], HW_Information->RcvRef_B_t_T2F[n][j], HW_Information->RcvRef_CrossTerm2F[n][j]);

                                Rate2 = HW_Rate(RcvLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_rcv[n][j], RcvLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->RcvRef_DF_t_T_PowerSpread[n][j],
                                    HW_Information->RcvRef_QVTerm_PowerSpread[n][j], HW_Information->RcvRef_B_t_T_PowerSpread[n][j], HW_Information->RcvRef_dt_PowerSpread[n][j],Simul->HWFactorFlag, xt_2f,
                                    HW_Information->RcvRef_QVTerm_PowerSpread2F[n][j], HW_Information->RcvRef_B_t_T_PowerSpread2F[n][j], HW_Information->RcvRef_CrossTerm_PowerSpread2F[n][j]);

                                Rate = Rate1 - Rate2;
                            }
                            RcvDailyRate[n][j] = Rate;
                            if (isinFindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardStart, RcvLeg->NCashFlow, Dayidx, &idxrcv2)) SimulatedRateRcv[n][Dayidx] = Rate;
                            if (isinFindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardEnd, RcvLeg->NCashFlow, Dayidx, &idxrcv3)) SimulatedRateRcv2[n][Dayidx] = Rate;
                        }
                    }
                }
            }
        }

        //////////////////////////////////
        // Rcv Reference Rate End       //
        // 5. Payoff Calculation Start  //
        //////////////////////////////////

        for (j = 0; j < RcvLeg->NCashFlow; j++) RcvCFFlag[j] = 0;

        idx1 = 0;
        for (j = 0; j < RcvLeg->NCashFlow; j++)
        {
            RateHistoryUseFlag = 0;
            Day1 = RcvLeg->DaysForwardStart[j];
            Day2 = RcvLeg->DaysPayDate_C[j];
            Day2YYYYMMDD = RcvLeg->PayDate_C[j];
            t = ((double)Day1) / 365.0;
            T = ((double)RcvLeg->DaysPayDate_C[j]) / 365.0;
            Pt = HW_Information->Rcv_DF_0_t[j];
            PT = HW_Information->Rcv_DF_0_T[j];

            if (Day1 >= 0)
            {
                ////////////////////////////////
                // Forward Start 아직  안지남 //
                ////////////////////////////////
                RcvCFFlag[j] = 1;
                RateHistoryUseFlag = 0;
            }
            else if (Day2 > 0)
            {
                ////////////////////////////////////
                // Forward Start지나고 Pay 안지남 //
                ////////////////////////////////////
                RcvCFFlag[j] = 1;
                RateHistoryUseFlag = 1;
            }
            else
            {
                RcvCFFlag[j] = 0;
                RateHistoryUseFlag = 0;
            }


            if (RcvCFFlag[j] == 1)
            {
                ////////////////////////
                // Payoff Calculation //
                ////////////////////////

                RcvPayoff[j] = Notional * PayoffStructure(Simul->DailySimulFlag, RcvLeg, SimulatedRateRcv, SimulatedRateRcv2, RcvDailyRate, j, RateHistoryUseFlag, RcvOutputRate, nAccrual);
                xt_idx = FindIndex(Day1, Simul->DaysForSimul, Simul->NDays, &idx1);
                xt = SimulShortRate[HW_Information->CurveIdx_DiscRcv][xt_idx];
                xt_2f = 0.0;

                if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[HW_Information->CurveIdx_DiscRcv][xt_idx];

                if (t > 0.0)
                {
                    PtT = HW_Information->Rcv_DF_t_T[j] * exp(-xt * HW_Information->B_t_T_RcvDisc[j] + HW_Information->QVTerm_RcvDisc[j]);
                    if (Simul->HWFactorFlag > 0) PtT = PtT * exp(-xt_2f * HW_Information->B_t_T_RcvDisc2F[j] + HW_Information->QVTerm_RcvDisc2F[j]);
                }
                else
                {
                    Pt = 1.0;
                    PtT = HW_Information->Rcv_DF_0_T[j];
                }

            }
            else
            {
                RcvPayoff[j] = 0.0;
                for (n = 0; n < RcvLeg->NReference; n++) RcvOutputRate[n] = 0.0;
                nAccrual = 0;
                Pt = 1.0;
                PtT = HW_Information->Rcv_DF_0_T[j];
            }

            RcvPayoffResult[i][j] = RcvPayoff[j];
            RcvP0T[j] = Pt * PtT;
            PricePath_Rcv += RcvP0T[j] * RcvPayoff[j];

            for (n = 0; n < RcvLeg->NReference; n++) ResultRcv[j + n * RcvLeg->NCashFlow] += RcvOutputRate[n] / (double)Simul->NSimul;

            ResultRcv[3 * RcvLeg->NCashFlow + j] += ((double)nAccrual) / (double)Simul->NSimul;
            ResultRcv[4 * RcvLeg->NCashFlow + j] += RcvPayoff[j] / (double)Simul->NSimul;
            ResultRcv[5 * RcvLeg->NCashFlow + j] += RcvP0T[j] / (double)Simul->NSimul;
            if (j == RcvLeg->NCashFlow - 1 && NAFlag == 1) NotionalValue[0] += RcvP0T[j] * Notional / (double)Simul->NSimul;
        }

        if (RcvLeg->OptionUseFlag == 1)
        {
            //////////////////////////////////////////////////////////////////////
            // 6. Discount Payoff From PayoffDate to OptionDate                 //
            // 해당 Payoff를 받을 수 있는 옵션날짜에 다 Payoff 할인하여 담음    //
            //////////////////////////////////////////////////////////////////////

            for (j = 0; j < RcvLeg->NCashFlow; j++)
            {
                for (n = 0; n < RcvLeg->NOption; n++)
                {
                    if (RcvLeg->OptionDate[n] < RcvLeg->PayDate_C[j])
                    {
                        PtTOptPay = RcvP0T[j] / DF_Opt[n];
                        Y[n][i] += PtTOptPay * RcvPayoff[j];
                    }

                    if (j == RcvLeg->NCashFlow - 1 && NAFlag == 1)
                    {
                        RcvP0T[j] / DF_Opt[n];
                        Y[n][i] += PtTOptPay * Notional;
                    }
                }
            }
        }

        RcvPrice += PricePath_Rcv / (double)Simul->NSimul;


        if (RcvLeg->OptionUseFlag == 1)
        {
            for (n = 0; n < RcvLeg->NOption; n++)
            {
                if (RcvLeg->CallConditionFlag == 0)
                {
                    OptRangeFlag[n][i] = 1;
                    for (k = 0; k < RcvLeg->NReference; k++)
                    {
                        //////////////////////////////////
                        // 하나라도 벗어나면 행사 못함  //
                        //////////////////////////////////
                        if (RcvOutputRate[k] > RcvLeg->RangeUp[k][n] || RcvOutputRate[k] < RcvLeg->RangeDn[k][n])
                        {
                            OptRangeFlag[n][i] = 0;
                            break;
                        }
                    }
                }
                else if (RcvLeg->CallConditionFlag == 1)
                {
                    OptRangeFlag[n][i] = 0;
                    for (k = 0; k < RcvLeg->NReference; k++)
                    {
                        /////////////////////////////////////
                        // Range 하나라도 만족하면 행사함  //
                        /////////////////////////////////////
                        if (RcvOutputRate[k] <= RcvLeg->RangeUp[k][n] && RcvOutputRate[k] >= RcvLeg->RangeDn[k][n])
                        {
                            OptRangeFlag[n][i] = 1;
                            break;
                        }
                    }
                }
                else
                {
                    OptRangeFlag[n][i] = 1;
                }
            }
        }

        //////////////////////////////////////////
        // 7~8 Calculate PayLeg Reference Rate  //
        // 7. Not DailySimul Case               //
        // 8. DailySimul Case                   //
        //////////////////////////////////////////

        for (n = 0; n < PayLeg->NReference; n++)
        {
            Curveidx = CurveIdx_Pay[n];
            lastresetend = -1;
            Rate = 0.0;
            Rate1 = 0.0;
            Rate2 = 0.0;
            idxpay = 0;
            idxpay2 = 0;
            idxpay3 = 0;
            if (Simul->DailySimulFlag == 0)
            {
                /////////////////////////////////////////
                // 7.1 Calculation Reference Rate      //
                // on ResetDate(DaysForwardStart[j])   //
                // 리셋시점의 기초금리 계산            //
                /////////////////////////////////////////

                for (j = 0; j < Simul->NDays; j++)
                {
                    SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                    if (isinFindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardStart, PayLeg->NCashFlow, Dayidx))
                    {
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;

                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        if (PayLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                        {
                            ////////////////////////////////////////
                            // 7.1.1 PowerSpread 상품이 아닌 경우 // 
                            ////////////////////////////////////////

                            t = ((double)PayLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T = ((double)PayLeg->DaysForwardEnd[Dayidx]) / 365.0;
                            Rate = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f, 
                                HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);
                        }
                        else
                        {
                            ///////////////////////////////////
                            // 7.1.2 PowerSpread 상품의 경우 // 
                            ///////////////////////////////////

                            t = ((double)PayLeg->DaysForwardStart[Dayidx] / 365.0);
                            T1 = t + PayLeg->Reference_Inform[n].PowerSpreadMat1;
                            T2 = t + PayLeg->Reference_Inform[n].PowerSpreadMat2;

                            Rate1 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);

                            Rate2 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T_PowerSpread[n][j],
                                HW_Information->PayRef_QVTerm_PowerSpread[n][j], HW_Information->PayRef_B_t_T_PowerSpread[n][j], HW_Information->PayRef_dt_PowerSpread[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->PayRef_QVTerm_PowerSpread2F[n][j], HW_Information->PayRef_B_t_T_PowerSpread2F[n][j], HW_Information->PayRef_CrossTerm_PowerSpread2F[n][j]);

                            Rate = Rate1 - Rate2;
                        }
                        SimulatedRatePay[n][Dayidx] = Rate;
                    }

                    if (isinFindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardEnd, PayLeg->NCashFlow, Dayidx))
                    {
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;

                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        if (PayLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                        {
                            ////////////////////////////////////////
                            // 7.1.1 PowerSpread 상품이 아닌 경우 // 
                            ////////////////////////////////////////

                            t = ((double)PayLeg->DaysForwardStart[Dayidx]) / 365.0;
                            T = ((double)PayLeg->DaysForwardEnd[Dayidx]) / 365.0;
                            Rate = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);
                        }
                        else
                        {
                            ///////////////////////////////////
                            // 7.1.2 PowerSpread 상품의 경우 // 
                            ///////////////////////////////////

                            t = ((double)PayLeg->DaysForwardStart[Dayidx] / 365.0);
                            T1 = t + PayLeg->Reference_Inform[n].PowerSpreadMat1;
                            T2 = t + PayLeg->Reference_Inform[n].PowerSpreadMat2;

                            Rate1 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);

                            Rate2 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T_PowerSpread[n][j],
                                HW_Information->PayRef_QVTerm_PowerSpread[n][j], HW_Information->PayRef_B_t_T_PowerSpread[n][j], HW_Information->PayRef_dt_PowerSpread[n][j], Simul->HWFactorFlag, xt_2f,
                                HW_Information->PayRef_QVTerm_PowerSpread2F[n][j], HW_Information->PayRef_B_t_T_PowerSpread2F[n][j], HW_Information->PayRef_CrossTerm_PowerSpread2F[n][j]);

                            Rate = Rate1 - Rate2;
                        }
                        SimulatedRatePay2[n][Dayidx] = Rate;
                    }
                }
            }
            else // if (Simul->DailySimulFlag == 1)
            {
                for (j = 0; j < Simul->NDays; j++)
                {
                    if (isinFindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardStart, PayLeg->NCashFlow, Dayidx, &idxpay))
                    {
                        SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                        xt = SimulShortRate[Curveidx][j];
                        xt_2f = 0.0;
                        
                        if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[Curveidx][j];

                        t = Simul->T_Array[j];
                        if (PayLeg->Reference_Inform[n].RefRateType <= 2)
                        {
                            if (PayLeg->Reference_Inform[n].PowerSpreadFlag == 0)
                            {
                                ////////////////////////////////////////
                                // 8.1.1 PowerSpread 상품이 아닌 경우 // 
                                ////////////////////////////////////////

                                T = ((double)PayLeg->DaysForwardEnd[Dayidx]) / 365.0;
                                Rate = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                    HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                    HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);
                            }
                            else
                            {
                                ///////////////////////////////////
                                // 8.1.2 PowerSpread 상품의 경우 // 
                                ///////////////////////////////////

                                T1 = t + PayLeg->Reference_Inform[n].PowerSpreadMat1;
                                T2 = t + PayLeg->Reference_Inform[n].PowerSpreadMat2;

                                Rate1 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T1, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T[n][j],
                                    HW_Information->PayRef_QVTerm[n][j], HW_Information->PayRef_B_t_T[n][j], HW_Information->PayRef_dt[n][j], Simul->HWFactorFlag, xt_2f,
                                    HW_Information->PayRef_QVTerm2F[n][j], HW_Information->PayRef_B_t_T2F[n][j], HW_Information->PayRef_CrossTerm2F[n][j]);

                                Rate2 = HW_Rate(PayLeg->Reference_Inform[n].RefRateType, t, T2, Simul->NRateTerm[Curveidx], Simul->RateTerm[Curveidx],
                                    Simul->Rate[Curveidx], xt, HW_Information->ndates_cpn_powerspread_pay[n][j], PayLeg->Reference_Inform[n].RefSwapNCPN_Ann, HW_Information->PayRef_DF_t_T_PowerSpread[n][j],
                                    HW_Information->PayRef_QVTerm_PowerSpread[n][j], HW_Information->PayRef_B_t_T_PowerSpread[n][j], HW_Information->PayRef_dt_PowerSpread[n][j], Simul->HWFactorFlag, xt_2f,
                                    HW_Information->PayRef_QVTerm_PowerSpread2F[n][j], HW_Information->PayRef_B_t_T_PowerSpread2F[n][j], HW_Information->PayRef_CrossTerm_PowerSpread2F[n][j]);

                                Rate = Rate1 - Rate2;
                            }
                            Dayidx = 0;
                            PayDailyRate[n][j] = Rate;
                            if (isinFindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardStart, PayLeg->NCashFlow, Dayidx, &idxpay2)) SimulatedRatePay[n][Dayidx] = Rate;
                            if (isinFindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardEnd, PayLeg->NCashFlow, Dayidx, &idxpay3)) SimulatedRatePay2[n][Dayidx] = Rate;
                        }
                    }
                }
            }
        }


        //////////////////////////////////
        // Pay Reference Rate End       //
        // 9. Payoff Calculation Start  //
        //////////////////////////////////

        for (j = 0; j < PayLeg->NCashFlow; j++) PayCFFlag[j] = 0;

        idx2 = 0;
        for (j = 0; j < PayLeg->NCashFlow; j++)
        {
            RateHistoryUseFlag = 0;
            Day1 = PayLeg->DaysForwardStart[j];
            Day2 = PayLeg->DaysPayDate_C[j];
            Day2YYYYMMDD = PayLeg->PayDate_C[j];
            t = ((double)Day1) / 365.0;
            T = ((double)PayLeg->DaysPayDate_C[j]) / 365.0;
            Pt = HW_Information->Pay_DF_0_t[j];
            PT = HW_Information->Pay_DF_0_T[j];

            if (Day1 >= 0)
            {
                ////////////////////////////////
                // Forward Start 아직  안지남 //
                ////////////////////////////////
                PayCFFlag[j] = 1;
                RateHistoryUseFlag = 0;
            }
            else if (Day2 > 0)
            {
                ////////////////////////////////////
                // Forward Start지나고 Pay 안지남 //
                ////////////////////////////////////
                PayCFFlag[j] = 1;
                RateHistoryUseFlag = 1;
            }
            else
            {
                PayCFFlag[j] = 0;
                RateHistoryUseFlag = 0;
            }


            if (PayCFFlag[j] == 1)
            {
                PayPayoff[j] = Notional * PayoffStructure(Simul->DailySimulFlag, PayLeg, SimulatedRatePay, SimulatedRatePay2, PayDailyRate,  j, RateHistoryUseFlag, PayOutputRate, nAccrual);
                xt_idx = FindIndex(Day1, Simul->DaysForSimul, Simul->NDays, &idx2);
                xt = SimulShortRate[HW_Information->CurveIdx_DiscPay][xt_idx];
                xt_2f = 0.0;

                if (Simul->HWFactorFlag > 0) xt_2f = SimulShortRate2F[HW_Information->CurveIdx_DiscPay][xt_idx];

                if (t > 0.0)
                {
                    PtT = HW_Information->Pay_DF_t_T[j] * exp(-xt * HW_Information->B_t_T_PayDisc[j] + HW_Information->QVTerm_PayDisc[j]);
                    if (Simul->HWFactorFlag > 0) PtT = PtT * exp(-xt_2f * HW_Information->B_t_T_PayDisc2F[j] + HW_Information->QVTerm_PayDisc2F[j]);
                }
                else
                {
                    Pt = 1.0;
                    PtT = HW_Information->Pay_DF_0_T[j];
                }

            }
            else
            {
                PayPayoff[j] = 0.0;
                for (n = 0; n < PayLeg->NReference; n++) PayOutputRate[n] = 0.0;
                nAccrual = 0;
                Pt = 1.0;
                PtT = HW_Information->Pay_DF_0_T[j];
            }

            PayPayoffResult[i][j] = PayPayoff[j];
            PayP0T[j] = Pt * PtT;
            PricePath_Pay += PayP0T[j] * PayPayoff[j];

            for (n = 0; n < PayLeg->NReference; n++)
            {
                ResultPay[j + n * PayLeg->NCashFlow] += PayOutputRate[n] / (double)Simul->NSimul;
            }

            ResultPay[3 * PayLeg->NCashFlow + j] += ((double)nAccrual) / (double)Simul->NSimul;
            ResultPay[4 * PayLeg->NCashFlow + j] += PayPayoff[j] / (double)Simul->NSimul;
            ResultPay[5 * PayLeg->NCashFlow + j] += PayP0T[j] / (double)Simul->NSimul;
            if (j == PayLeg->NCashFlow - 1 && NAFlag == 1 && NoteFlag == 0) NotionalValue[1] += PayP0T[j] * Notional / (double)Simul->NSimul;
        }

        if (RcvLeg->OptionUseFlag == 1)
        {
            //////////////////////////////////////////////////////////////////////
            // 10. Discount Payoff From PayoffDate to OptionDate                //
            // 해당 Payoff를 받을 수 있는 옵션날짜에 다 Payoff 할인하여 담음    //
            //////////////////////////////////////////////////////////////////////
            for (j = 0; j < PayLeg->NCashFlow; j++)
            {
                for (n = 0; n < RcvLeg->NOption; n++)
                {
                    if (RcvLeg->OptionDate[n] < PayLeg->PayDate_C[j])
                    {
                        PtTOptPay = PayP0T[j] / DF_Opt[n];
                        Y[n][i] -= PtTOptPay * PayPayoff[j];
                    }

                    if (j == PayLeg->NCashFlow - 1 && NAFlag == 1 && NoteFlag == 0)
                    {
                        PtTOptPay = PayP0T[j] / DF_Opt[n];
                        Y[n][i] -= PtTOptPay * Notional;
                    }
                }
            }
        }

        PayPrice += PricePath_Pay / (double)Simul->NSimul;

        //////////////////////////////////////////////////////////////////////
        // 11. Calculate Optimal Option Date, Optimal OptValue              //
        //////////////////////////////////////////////////////////////////////

        if (RcvLeg->OptionUseFlag == 1)
        {
            if (OptRangeFlag[0][i] > 0)
            {
                if (RcvLeg->OptionType == 1) 
                {
                    //////////////////////////////////////
                    // 11.1 Receiver have Cancel Option //
                    //////////////////////////////////////

                    if (NoteFlag == 0)
                    {
                        if (Y[0][i] < 0.0) Value_By_OptTime[i] = fabs(Y[0][i]);
                        else Value_By_OptTime[i] = 0.0;
                    }
                    else
                    {
                        /////////////////////////////////
                        // If Evauating Bond not Swap  //
                        // Swap이 아니라               //
                        // Bond평가할 경우             //
                        // (PayLeg가 다 0이면 Bond)    //
                        /////////////////////////////////
                        if (NoteFlag == 1 && NAFlag == 1)
                        {
                            if (Y[0][i] < Notional) Value_By_OptTime[i] = fabs(Notional - Y[0][i] );
                            else Value_By_OptTime[i] = 0.0;
                        }
                        else
                        {
                            Value_By_OptTime[i] = 0.0;
                        }
                    }
                }
                else
                {
                    ///////////////////////////////////
                    // 11.2 Payer have Cancel Option //
                    ///////////////////////////////////

                    if (NoteFlag == 0)
                    {
                        if (Y[0][i] > 0.0) Value_By_OptTime[i] = Y[0][i];
                        else Value_By_OptTime[i] = 0.0;
                    }
                    else
                    {
                        if (NoteFlag == 1 && NAFlag == 1)
                        {
                            /////////////////////////////////
                            // If Evauating Bond not Swap  //
                            // Swap이 아니라               //
                            // Bond평가할 경우             //
                            // (PayLeg가 다 0이면 Bond)    //
                            /////////////////////////////////

                            if (Y[0][i] > Notional) Value_By_OptTime[i] = fabs(Y[0][i] - Notional);
                            else Value_By_OptTime[i] = 0.0;
                        }
                    }
                }
            }
            else Value_By_OptTime[i] = 0.0;
            OptimalIdx[i] = 0;

            for (n = 1; n < RcvLeg->NOption; n++)
            {
                if (RcvLeg->OptionType == 1)
                {
                    //////////////////////////////////////
                    // 11.1 Receiver have Cancel Option //
                    //////////////////////////////////////

                    if (NoteFlag == 0)
                    {
                        if (Y[n][i] < 0.0 && -Y[n][i] > Value_By_OptTime[i] && OptRangeFlag[n][i] > 0)
                        {
                            OptimalIdx[i] = n;
                            Value_By_OptTime[i] = -Y[n][i];
                        }
                    }
                    else
                    {
                        if (Y[n][i] < Notional && Notional - Y[n][i] > Value_By_OptTime[i] && OptRangeFlag[n][i] > 0 && NAFlag == 1)
                        {
                            OptimalIdx[i] = n;
                            Value_By_OptTime[i] = Notional - Y[n][i];
                        }
                    }
                }
                else
                {
                    ///////////////////////////////////
                    // 11.2 Payer have Cancel Option //
                    ///////////////////////////////////

                    if (NoteFlag == 0)
                    {
                        if (Y[n][i] > 0.0 && Y[n][i] > Value_By_OptTime[i] && OptRangeFlag[n][i] > 0)
                        {
                            OptimalIdx[i] = n;
                            Value_By_OptTime[i] = Y[n][i];
                        }
                    }
                    else
                    {
                        if (Y[n][i] > Notional && Y[n][i] - Notional > Value_By_OptTime[i] && OptRangeFlag[n][i] > 0 && NAFlag == 1)
                        {
                            OptimalIdx[i] = n;
                            Value_By_OptTime[i] = Y[n][i] - Notional;
                        }
                    }
                }
            }

            for (n = 0; n < Simul->NAsset; n++)
            {
                /////////////////////////////////////////////////////////////////////////
                // InterestRate_Opt[i][n] is ShortRate[n]                              //
                // InterestRate_Opt[i][Simul->NAsset + 1] is 1.0                       //
                // InterestRate_Opt[i][Simul->NAsset + 1 + n] is Square ShortRate[n]   //
                /////////////////////////////////////////////////////////////////////////
                InterestRate_Opt[i][n] = X[OptimalIdx[i]][i][n];
                InterestRate_Opt[i][Simul->NAsset + 1 + n] = X[OptimalIdx[i]][i][n] * X[OptimalIdx[i]][i][n];
            }

        }
    }

    //////////////
    // LSMC OLS //
    //////////////
    double OptionPrice = 0.0;
    double MaxLegValue;
    double ExerciseValue = 0.0;
    
    if (RcvLeg->OptionUseFlag == 1)
    {
        Beta = OLSBeta(Value_By_OptTime, LengthY, InterestRate_Opt, ShapeX);
        for (i = 0; i < Simul->NSimul; i++)
        {
            for (idxoption = 0; idxoption < RcvLeg->NOption; idxoption++)
            {
                LastFixingCoupon = 0.;

                LastFixingCouponRcv = 0.;
                LastFixingIdxRcv = -1;
                for (j = 0; j < RcvLeg->NCashFlow; j++)
                {
                    if (RcvLeg->OptionDate[idxoption] >= RcvLeg->ForwardStart_C[j] && RcvLeg->OptionDate[idxoption] <= RcvLeg->PayDate_C[j])
                    {
                        LastFixingIdxRcv = j;
                        break;
                    }
                }

                if (LastFixingIdxRcv >= 0) LastFixingCouponRcv = RcvPayoffResult[i][LastFixingIdxRcv];

                LastFixingCouponPay = 0.;
                LastFixingIdxPay = -1;
                for (j = 0; j < PayLeg->NCashFlow; j++)
                {
                    if (RcvLeg->OptionDate[idxoption] >= PayLeg->ForwardStart_C[j] && RcvLeg->OptionDate[idxoption] <= PayLeg->PayDate_C[j])
                    {
                        LastFixingIdxPay = j;
                        break;
                    }
                }

                if (LastFixingIdxPay >= 0) LastFixingCouponPay = PayPayoffResult[i][LastFixingIdxPay];

                if (RcvLeg->OptionType == 1) LastFixingCoupon = LastFixingCouponRcv - LastFixingCouponPay;
                else LastFixingCoupon = -LastFixingCouponRcv + LastFixingCouponPay;

                EstOptValue = Beta[Simul->NAsset];
                for (j = 0; j < Simul->NAsset; j++)
                {
                    EstOptValue += Beta[j] * X[idxoption][i][j];
                    EstOptValue += Beta[Simul->NAsset + 1 + j] * (X[idxoption][i][j] * X[idxoption][i][j]);
                }

                EstOptValue = max(EstOptValue, LastFixingCoupon);
                if (RcvLeg->OptionType == 1)
                {
                    if (NoteFlag == 0)
                    {
                        if (Y[idxoption][i] < 0.0 && -Y[idxoption][i] > EstOptValue)
                        {
                            OptionPrice += -(Y[idxoption][i] * DF_Opt[idxoption]) / (double)Simul->NSimul;
                            break;
                        }
                    }
                    else
                    {
                        if (Y[idxoption][i] < Notional && Notional - Y[idxoption][i] > EstOptValue)
                        {
                            OptionPrice += (Notional -Y[idxoption][i]) * DF_Opt[idxoption] / (double)Simul->NSimul;
                            break;
                        }
                    }
                }
                else
                {
                    if (NoteFlag == 0)
                    {
                        if (Y[idxoption][i] > 0.0 && Y[idxoption][i] > EstOptValue)
                        {
                            OptionPrice += (Y[idxoption][i] * DF_Opt[idxoption]) / (double)Simul->NSimul;
                            break;
                        }
                    }
                    else
                    {
                        if (Y[idxoption][i] > Notional && Y[idxoption][i] - Notional > EstOptValue)
                        {
                            OptionPrice += (Y[idxoption][i] - Notional) * DF_Opt[idxoption] / (double)Simul->NSimul;
                            break;
                        }
                    }
                }
            }
        }

        free(Beta);
    }

    if (PricingOnly == 1)
    {
        ResultPrice[0] = RcvPrice + NotionalValue[0];
        ResultPrice[1] = PayPrice + NotionalValue[1];
        if (NAFlag == 1) ResultPrice[2] = RcvPrice + NotionalValue[0] - PayPrice - NotionalValue[1];
        else ResultPrice[2] = RcvPrice - PayPrice;
        if (RcvLeg->OptionUseFlag == 1)
        {
            ResultPrice[3] = OptionPrice;
            if (RcvLeg->OptionType == 1) ResultPrice[2] += OptionPrice;
            else ResultPrice[2] -= OptionPrice;
        }
    }

    if (Simul->DailySimulFlag == 1)
    {
        for (i = 0; i < RcvLeg->NReference; i++) free(RcvDailyRate[i]);
        for (i = 0; i < PayLeg->NReference; i++) free(PayDailyRate[i]);
    }
    free(RcvDailyRate);                                  // 1
    free(PayDailyRate);             // 2
    free(RcvPayoff);             // 3
    free(PayPayoff);             // 4
    free(RcvCFFlag);             // 5
    free(PayCFFlag);             // 6
    free(RcvOutputRate);
    free(PayOutputRate);
    // 제거중
    if (RcvLeg->OptionUseFlag == 1)
    {
        free(Value_By_OptTime);
        free(Estimated_Value_By_OptTime);
        free(OptimalIdx);

        for (i = 0; i < Simul->NSimul; i++) free(InterestRate_Opt[i]);
        free(InterestRate_Opt);

        for (i = 0; i < RcvLeg->NOption; i++)
        {
            for (j = 0; j < Simul->NSimul; j++) free(X[i][j]);
            free(X[i]);
        }
        free(X);

        for (i = 0; i < RcvLeg->NOption; i++) free(Y[i]);
        free(Y);

        for (i = 0; i < RcvLeg->NOption; i++) free(OptRangeFlag[i]);
        free(OptRangeFlag);

        for (i = 0; i < RcvLeg->NOption; i++) free(Y_Hat[i]);
        free(Y_Hat);

    }
    else
    {
        free(X);
        free(Y);
        free(Value_By_OptTime);
        free(Estimated_Value_By_OptTime);
        free(OptimalIdx);
        free(InterestRate_Opt);
        free(OptRangeFlag);
        free(Y_Hat);

    }
    free(DF_Opt);
    for (i = 0; i < Simul->NAsset; i++) free(Simul_QuantoTerm[i]);
    free(Simul_QuantoTerm);
    free(TimeOption);
    free(DF_To_Pay);
    free(RcvP0T);
    free(PayP0T);
    for (i = 0; i < Simul->NSimul; i++) free(RcvPayoffResult[i]);
    free(RcvPayoffResult);
    for (i = 0; i < Simul->NSimul; i++) free(PayPayoffResult[i]);
    free(PayPayoffResult);
    return 1;
}


long IRStructuredSwap(
    long PricingDateC,
    long NAFlag,
    double Notional,
    LEG_INFO* RcvLeg,
    LEG_INFO* PayLeg,
    SIMUL_INFO* Simul,
    long GreekFlag,                     // 
    double* ResultPrice,                // 
    double* ResultRcv,                  // 
    double* ResultPay                   // 
)
{
    long i, j, k;
    long idx0, idx1, idx2, idx3;
    long ResultCode = 0;

    double xt = 0.0;
    double Rate = 0.0, Rate1 = 0.0, Rate2 = 0.0;

    //////////////////////////////
    // Short Rate Parameters    //
    // XA -> Drift,             // 
    // XV -> Diffusion          //
    //////////////////////////////

    long Length_XA_Array = Simul->NDays;
    long Length_XV_Array = Simul->NDays;
    double** XA_Array = (double**)malloc(sizeof(double*) * Simul->NAsset);
    double** XV_Array = (double**)malloc(sizeof(double*) * Simul->NAsset);
    double** XA_Array2 = (double**)malloc(sizeof(double*) * Simul->NAsset);
    double** XV_Array2 = (double**)malloc(sizeof(double*) * Simul->NAsset);
    for (i = 0; i < Simul->NAsset; i++)
    {
        XA_Array[i] = (double*)malloc(sizeof(double) * Simul->NDays);
        XV_Array[i] = (double*)malloc(sizeof(double) * Simul->NDays);
        XA_Array2[i] = (double*)malloc(sizeof(double) * Simul->NDays);
        XV_Array2[i] = (double*)malloc(sizeof(double) * Simul->NDays);
        Set_XA(Simul->HWKappa[i], Length_XA_Array, XA_Array[i], Simul->dt_Array);
        Set_XV(Simul->HWKappa[i], Simul->NHWVol[i], Simul->HWVolTerm[i], Simul->HWVol[i], Length_XV_Array, XV_Array[i], Simul->dt_Array);
        if (Simul->HWFactorFlag > 0)
        {
            Set_XA(Simul->HWKappa2[i], Length_XA_Array, XA_Array2[i], Simul->dt_Array);
            Set_XV(Simul->HWKappa2[i], Simul->NHWVol[i], Simul->HWVolTerm[i], Simul->HWVol2[i], Length_XV_Array, XV_Array2[i], Simul->dt_Array);
        }
    }
    
    //////////////////////////
    // Result Short Rate 1F //
    // And Short Rate 2F    //
    //////////////////////////

    double** SimulatedRateRcv = (double**)malloc(sizeof(double*) * RcvLeg->NReference); 
    for (i = 0; i < RcvLeg->NReference; i++) SimulatedRateRcv[i] = (double*)malloc(sizeof(double) * RcvLeg->NCashFlow);
    for (i = 0; i < RcvLeg->NReference; i++) for (j = 0; j < RcvLeg->NCashFlow; j++) SimulatedRateRcv[i][j] = 0.0;

    double** SimulatedRateRcv2 = (double**)malloc(sizeof(double*) * RcvLeg->NReference);
    for (i = 0; i < RcvLeg->NReference; i++) SimulatedRateRcv2[i] = (double*)malloc(sizeof(double) * RcvLeg->NCashFlow);
    for (i = 0; i < RcvLeg->NReference; i++) for (j = 0; j < RcvLeg->NCashFlow; j++) SimulatedRateRcv2[i][j] = 0.0;

    double** SimulatedRatePay = (double**)malloc(sizeof(double*) * PayLeg->NReference); 
    for (i = 0; i < PayLeg->NReference; i++) SimulatedRatePay[i] = (double*)malloc(sizeof(double) * PayLeg->NCashFlow);
    for (i = 0; i < PayLeg->NReference; i++) for (j = 0; j < PayLeg->NCashFlow; j++) SimulatedRatePay[i][j] = 0.0;

    double** SimulatedRatePay2 = (double**)malloc(sizeof(double*) * PayLeg->NReference);
    for (i = 0; i < PayLeg->NReference; i++) SimulatedRatePay2[i] = (double*)malloc(sizeof(double) * PayLeg->NCashFlow);
    for (i = 0; i < PayLeg->NReference; i++) for (j = 0; j < PayLeg->NCashFlow; j++) SimulatedRatePay2[i][j] = 0.0;

    double** SimulShortRate = (double**)malloc(sizeof(double*) * Simul->NAsset); 
    for (i = 0; i < Simul->NAsset; i++) SimulShortRate[i] = (double*)malloc(sizeof(double) * Simul->NDays);

    double** SimulShortRate2 = (double**)malloc(sizeof(double*) * Simul->NAsset); 
    for (i = 0; i < Simul->NAsset; i++) SimulShortRate2[i] = (double*)malloc(sizeof(double) * Simul->NDays);
    
    long* CurveIdx_Rcv = (long*)malloc(sizeof(long) * RcvLeg->NReference);
    long* CurveIdx_Pay = (long*)malloc(sizeof(long) * PayLeg->NReference);
    for (i = 0; i < RcvLeg->NReference; i++) CurveIdx_Rcv[i] = FindIndex(RcvLeg->Reference_Inform[i].CurveNum, Simul->SimulCurveIdx, Simul->NAsset);
    for (i = 0; i < PayLeg->NReference; i++) CurveIdx_Pay[i] = FindIndex(PayLeg->Reference_Inform[i].CurveNum, Simul->SimulCurveIdx, Simul->NAsset);
    long CurveIdx_DiscRcv = FindIndex(RcvLeg->DiscCurveNum, Simul->SimulCurveIdx, Simul->NAsset);
    long CurveIdx_DiscPay = FindIndex(PayLeg->DiscCurveNum, Simul->SimulCurveIdx, Simul->NAsset);
    
    double* Rcv_DF_0_t = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* Rcv_DF_0_T = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* Rcv_DF_t_T = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double t, T;

    for (i = 0; i < RcvLeg->NCashFlow; i++)
    {
        t = ((double)RcvLeg->DaysForwardStart[i]) / 365.0;

        if (t < 0.0) t = 0.0;

        T = ((double)RcvLeg->DaysPayDate_C[i]) / 365.0;

        if (T < 0.0) T = 0.0;

        Rcv_DF_0_t[i] = Calc_Discount_Factor(Simul->RateTerm[CurveIdx_DiscRcv], Simul->Rate[CurveIdx_DiscRcv], Simul->NRateTerm[CurveIdx_DiscRcv], t);
        Rcv_DF_0_T[i] = Calc_Discount_Factor(Simul->RateTerm[CurveIdx_DiscRcv], Simul->Rate[CurveIdx_DiscRcv], Simul->NRateTerm[CurveIdx_DiscRcv], T);
        Rcv_DF_t_T[i] = Rcv_DF_0_T[i] / Rcv_DF_0_t[i];
    }
    double* Pay_DF_0_t = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* Pay_DF_0_T = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* Pay_DF_t_T = (double*)malloc(PayLeg->NCashFlow * sizeof(double));

    for (i = 0; i < PayLeg->NCashFlow; i++)
    {
        t = ((double)PayLeg->DaysForwardStart[i]) / 365.0;
        if (t < 0.0) t = 0.0;

        T = ((double)PayLeg->DaysPayDate_C[i]) / 365.0;
        if (T < 0.0) T = 0.0;

        Pay_DF_0_t[i] = Calc_Discount_Factor(Simul->RateTerm[CurveIdx_DiscPay], Simul->Rate[CurveIdx_DiscPay], Simul->NRateTerm[CurveIdx_DiscPay], t);
        Pay_DF_0_T[i] = Calc_Discount_Factor(Simul->RateTerm[CurveIdx_DiscPay], Simul->Rate[CurveIdx_DiscPay], Simul->NRateTerm[CurveIdx_DiscPay], T);
        Pay_DF_t_T[i] = Pay_DF_0_T[i] / Pay_DF_0_t[i];
    }
    
    ////////////////////////////////////
    // Hull White Bond Pricing Params //
    // Rcv and Pay Disc               //
    ////////////////////////////////////

    double* B_t_T_RcvDisc = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* QVTerm_RcvDisc = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* B_t_T_RcvDisc2 = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* QVTerm_RcvDisc2 = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    double* CrossTerm_RcvDisc2 = (double*)malloc(RcvLeg->NCashFlow * sizeof(double));
    for (i = 0; i < RcvLeg->NCashFlow; i++)
    {
        t = ((double)RcvLeg->DaysForwardStart[i]) / 365.0;
        if (t < 0.0) t = 0.0;

        T = ((double)RcvLeg->DaysPayDate_C[i]) / 365.0;
        if (T < 0.0) T = 0.0;

        B_t_T_RcvDisc[i] = B_s_to_t(Simul->HWKappa[CurveIdx_DiscRcv], t, T);
        QVTerm_RcvDisc[i] = HullWhiteQVTerm(t, T, Simul->HWKappa[CurveIdx_DiscRcv], Simul->NHWVol[CurveIdx_DiscRcv], Simul->HWVolTerm[CurveIdx_DiscRcv], Simul->HWVol[CurveIdx_DiscRcv]);
        if (Simul->HWFactorFlag > 0)
        {
            B_t_T_RcvDisc2[i] = B_s_to_t(Simul->HWKappa2[CurveIdx_DiscRcv], t, T);
            QVTerm_RcvDisc2[i] = HullWhiteQVTerm(t, T, Simul->HWKappa2[CurveIdx_DiscRcv], Simul->NHWVol[CurveIdx_DiscRcv], Simul->HWVolTerm[CurveIdx_DiscRcv], Simul->HWVol2[CurveIdx_DiscRcv]);
            CrossTerm_RcvDisc2[i] = HullWhite2F_CrossTerm(t, T, Simul->HWKappa[CurveIdx_DiscRcv], Simul->NHWVol[CurveIdx_DiscRcv], Simul->HWVolTerm[CurveIdx_DiscRcv], Simul->HWVol[CurveIdx_DiscRcv], Simul->HWKappa2[CurveIdx_DiscRcv], Simul->HWVolTerm[CurveIdx_DiscRcv], Simul->HWVol2[CurveIdx_DiscRcv], Simul->HW2FRho[CurveIdx_DiscRcv]);
        }
    }

    double* B_t_T_PayDisc = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* QVTerm_PayDisc = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* B_t_T_PayDisc2 = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* QVTerm_PayDisc2 = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    double* CrossTerm_PayDisc2 = (double*)malloc(PayLeg->NCashFlow * sizeof(double));
    for (i = 0; i < PayLeg->NCashFlow; i++)
    {
        t = ((double)PayLeg->DaysForwardStart[i]) / 365.0;
        if (t < 0.0) t = 0.0;

        T = ((double)PayLeg->DaysPayDate_C[i]) / 365.0;
        if (T < 0.0) T = 0.0;

        B_t_T_PayDisc[i] = B_s_to_t(Simul->HWKappa[CurveIdx_DiscPay], t, T);
        QVTerm_PayDisc[i] = HullWhiteQVTerm(t, T, Simul->HWKappa[CurveIdx_DiscPay], Simul->NHWVol[CurveIdx_DiscPay], Simul->HWVolTerm[CurveIdx_DiscPay], Simul->HWVol[CurveIdx_DiscPay]);
        if (Simul->HWFactorFlag > 0)
        {
            B_t_T_PayDisc2[i] = B_s_to_t(Simul->HWKappa2[CurveIdx_DiscPay], t, T);
            QVTerm_PayDisc2[i] = HullWhiteQVTerm(t, T, Simul->HWKappa2[CurveIdx_DiscPay], Simul->NHWVol[CurveIdx_DiscPay], Simul->HWVolTerm[CurveIdx_DiscPay], Simul->HWVol2[CurveIdx_DiscPay]);
            CrossTerm_PayDisc2[i] = HullWhite2F_CrossTerm(t, T, Simul->HWKappa[CurveIdx_DiscPay], Simul->NHWVol[CurveIdx_DiscPay], Simul->HWVolTerm[CurveIdx_DiscPay], Simul->HWVol[CurveIdx_DiscPay], Simul->HWKappa2[CurveIdx_DiscPay], Simul->HWVolTerm[CurveIdx_DiscPay], Simul->HWVol2[CurveIdx_DiscPay], Simul->HW2FRho[CurveIdx_DiscPay]);
        }
    }

    long ndates, ndates2 = 1;
    long CurveIdxRef;
    long idxT1, DayT1, YYYYMMDDT1;
    long ncpn;
    double T1, T_PowerSpread;
    double DF_0_t, DF_0_T, term;

    // RcvLeg Simul HW Params

    long** ndates_Rcv = (long**)malloc(sizeof(long*) * RcvLeg->NReference);
    long*** CpnDates_Rcv = (long***)malloc(sizeof(long**) * RcvLeg->NReference);
    double*** RcvRef_DF_t_T = (double***)malloc(sizeof(double**) * RcvLeg->NReference);        // Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_QVTerm = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_B_t_T2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_QVTerm2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_CrossTerm2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_dt = (double***)malloc(sizeof(double**) * RcvLeg->NReference);

    long** ndates_Rcv_PowerSpread = (long**)malloc(sizeof(long*) * RcvLeg->NReference);
    long*** CpnDates_Rcv_PowerSpread = (long***)malloc(sizeof(long**) * RcvLeg->NReference);
    double*** RcvRef_DF_t_T_PowerSpread = (double***)malloc(sizeof(double**) * RcvLeg->NReference);        // Shape = NReference, NDays, NCpn
    double*** RcvRef_B_t_T_PowerSpread = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_QVTerm_PowerSpread = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_B_t_T_PowerSpread2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_QVTerm_PowerSpread2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_CrossTerm_PowerSpread2 = (double***)malloc(sizeof(double**) * RcvLeg->NReference);
    double*** RcvRef_dt_PowerSpread = (double***)malloc(sizeof(double**) * RcvLeg->NReference);

    long idxfrdstart;
    long SimDayYYYYMMDD, SwapMatYYYYMMDD, TempDate;

    for (i = 0; i < RcvLeg->NReference; i++)
    {
        CurveIdxRef = CurveIdx_Rcv[i];
        ndates_Rcv[i] = (long*)malloc(sizeof(long) * Simul->NDays);
        CpnDates_Rcv[i] = (long**)malloc(sizeof(long*) * Simul->NDays);
        RcvRef_DF_t_T[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_B_t_T[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_QVTerm[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_B_t_T2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_QVTerm2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_CrossTerm2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_dt[i] = (double**)malloc(sizeof(double*) * Simul->NDays);

        ndates_Rcv_PowerSpread[i] = (long*)malloc(sizeof(long) * Simul->NDays);
        CpnDates_Rcv_PowerSpread[i] = (long**)malloc(sizeof(long*) * Simul->NDays);
        RcvRef_DF_t_T_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_B_t_T_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_QVTerm_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_B_t_T_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_QVTerm_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_CrossTerm_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        RcvRef_dt_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);

        if (RcvLeg->Reference_Inform[i].PowerSpreadFlag == 0)
        {
            if (RcvLeg->Reference_Inform[i].RefRateType == 0 || RcvLeg->Reference_Inform[i].RefRateType == 2)
            {
                ncpn = 1;
                for (j = 0; j < Simul->NDays; j++)
                {
                    RcvRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    RcvRef_dt[i][j] = (double*)malloc(sizeof(double) * ncpn);
                }

                idxT1 = RcvLeg->CurrentIdx;
                DayT1 = RcvLeg->DaysForwardEnd[RcvLeg->CurrentIdx];
                T1 = ((double)DayT1) / 365.0;

                idx1 = 0;
                idx2 = 0;
                idx3 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    ndates_Rcv[i][j] = 1;

                    t = ((double)Simul->DaysForSimul[j]) / 365.0;
                    ///////////////////////////////////////////////////
                    // t는 시뮬날짜로하고 t가 ForwardStart날짜면
                    // T1는 차기 Forward End날짜
                    // 못찾으면 기존 Forward End날짜
                    ///////////////////////////////////////////////////
                    idxfrdstart = FindIndex(Simul->DaysForSimul[j], RcvLeg->DaysForwardStart, RcvLeg->NCashFlow);
                    if (idxfrdstart >= 0) T1 = ((double)RcvLeg->DaysForwardEnd[idxfrdstart]) / 365.0;

                    DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    RcvRef_dt[i][j][0] = T1 - t;
                    RcvRef_DF_t_T[i][j][0] = DF_0_T / DF_0_t;
                    RcvRef_B_t_T[i][j][0] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    RcvRef_QVTerm[i][j][0] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    if (Simul->HWFactorFlag > 0)
                    {
                        RcvRef_B_t_T2[i][j][0] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        RcvRef_QVTerm2[i][j][0] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        RcvRef_CrossTerm2[i][j][0] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }

            }
            else if (RcvLeg->Reference_Inform[i].RefRateType == 1)
            {
                /////////////////////////////////
                // 기초금리가 스왑금리 등이라면
                /////////////////////////////////
                idx0 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    /////////////////////////////////////////////////////////
                    // 시뮬시점 t로부터 SwapMaturity까지 모든 HW 파라미터 계산
                    /////////////////////////////////////////////////////////
                    t = ((double)(Simul->DaysForSimul[j])) / 365.0;
                    SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                    SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * RcvLeg->Reference_Inform[i].RefSwapMaturity));
                    TempDate = SimDayYYYYMMDD;
                    CpnDates_Rcv[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, RcvLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates, TempDate); //할당
                    ndates_Rcv[i][j] = ndates;

                    RcvRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    RcvRef_dt[i][j] = (double*)malloc(sizeof(double) * ndates);
                    DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                    idx1 = 0;
                    for (k = 0; k < ndates; k++)
                    {
                        T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Rcv[i][j][k]))/365.0;
                        if (k == 0) RcvRef_dt[i][j][k] = T1 - t;
                        else RcvRef_dt[i][j][k] = ((double)(DayCountAtoB(CpnDates_Rcv[i][j][k - 1], CpnDates_Rcv[i][j][k]))) / 365.0;
                        DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                        RcvRef_DF_t_T[i][j][k] = DF_0_T / DF_0_t;
                        RcvRef_QVTerm[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                        RcvRef_B_t_T[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                        if (Simul->HWFactorFlag > 0)
                        {
                            RcvRef_QVTerm2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                            RcvRef_B_t_T2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                            RcvRef_CrossTerm2[i][j][k] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                        }
                    }
                }
            }
        }
        else
        {
            //////////////////////////////////////////////////////////////
            // PowerSpread가 1일 경우 무조건 RefRateType 는 스왑금리 등
            //////////////////////////////////////////////////////////////
            RcvLeg->Reference_Inform[i].RefRateType = 1;
            idx0 = 0;
            for (j = 0; j < Simul->NDays; j++)
            {
                t = ((double)(Simul->DaysForSimul[j])) / 365.0;
                SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * RcvLeg->Reference_Inform[i].PowerSpreadMat1));
                TempDate = SimDayYYYYMMDD;
                CpnDates_Rcv[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, RcvLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates, TempDate); //할당
                ndates_Rcv[i][j] = ndates;

                RcvRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                RcvRef_dt[i][j] = (double*)malloc(sizeof(double) * ndates);
                DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                idx1 = 0;
                for (k = 0; k < ndates; k++)
                {
                    T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Rcv[i][j][k])) / 365.0;
                    if (k == 0) RcvRef_dt[i][j][k] = T1 - t;
                    else RcvRef_dt[i][j][k] = ((double)(DayCountAtoB(CpnDates_Rcv[i][j][k - 1], CpnDates_Rcv[i][j][k]))) / 365.0;
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    RcvRef_DF_t_T[i][j][k] = DF_0_T / DF_0_t;
                    RcvRef_QVTerm[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    RcvRef_B_t_T[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    if (Simul->HWFactorFlag > 0)
                    {
                        RcvRef_QVTerm2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        RcvRef_B_t_T2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        RcvRef_CrossTerm2[i][j][k] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }

                SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * RcvLeg->Reference_Inform[i].PowerSpreadMat2));
                CpnDates_Rcv_PowerSpread[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, RcvLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates2, TempDate); //할당
                ndates_Rcv_PowerSpread[i][j] = ndates2;

                RcvRef_DF_t_T_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_B_t_T_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_QVTerm_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_B_t_T_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_QVTerm_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_CrossTerm_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                RcvRef_dt_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                idx2 = 0;
                for (k = 0; k < ndates2; k++)
                {
                    T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Rcv_PowerSpread[i][j][k])) / 365.0;
                    if (k == 0) RcvRef_dt_PowerSpread[i][j][k] = T1 - t;
                    else RcvRef_dt_PowerSpread[i][j][k] = ((double)(DayCountAtoB(CpnDates_Rcv_PowerSpread[i][j][k - 1], CpnDates_Rcv_PowerSpread[i][j][k]))) / 365.0;
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    RcvRef_DF_t_T_PowerSpread[i][j][k] = DF_0_T / DF_0_t;
                    RcvRef_QVTerm_PowerSpread[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    RcvRef_B_t_T_PowerSpread[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    if (Simul->HWFactorFlag > 0)
                    {
                        RcvRef_QVTerm_PowerSpread2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        RcvRef_B_t_T_PowerSpread2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        RcvRef_CrossTerm_PowerSpread2[i][j][k] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }
            }
        }
    }

    // PayLeg Simul HW Params
    long** ndates_Pay = (long**)malloc(sizeof(long*) * PayLeg->NReference);
    long*** CpnDates_Pay = (long***)malloc(sizeof(long**) * PayLeg->NReference);
    double*** PayRef_DF_t_T = (double***)malloc(sizeof(double**) * PayLeg->NReference);        // Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_QVTerm = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_B_t_T2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_QVTerm2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_CrossTerm2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_dt = (double***)malloc(sizeof(double**) * PayLeg->NReference);

    long** ndates_Pay_PowerSpread = (long**)malloc(sizeof(long*) * PayLeg->NReference);
    long*** CpnDates_Pay_PowerSpread = (long***)malloc(sizeof(long**) * PayLeg->NReference);
    double*** PayRef_DF_t_T_PowerSpread = (double***)malloc(sizeof(double**) * PayLeg->NReference);        // Shape = NReference, NDays, NCpn
    double*** PayRef_B_t_T_PowerSpread = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_QVTerm_PowerSpread = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_B_t_T_PowerSpread2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_QVTerm_PowerSpread2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_CrossTerm_PowerSpread2 = (double***)malloc(sizeof(double**) * PayLeg->NReference);
    double*** PayRef_dt_PowerSpread = (double***)malloc(sizeof(double**) * PayLeg->NReference);

    for (i = 0; i < PayLeg->NReference; i++)
    {
        CurveIdxRef = CurveIdx_Pay[i];
        ndates_Pay[i] = (long*)malloc(sizeof(long) * Simul->NDays);
        CpnDates_Pay[i] = (long**)malloc(sizeof(long*) * Simul->NDays);
        PayRef_DF_t_T[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_B_t_T[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_QVTerm[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_B_t_T2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_QVTerm2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_CrossTerm2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_dt[i] = (double**)malloc(sizeof(double*) * Simul->NDays);

        ndates_Pay_PowerSpread[i] = (long*)malloc(sizeof(long) * Simul->NDays);
        CpnDates_Pay_PowerSpread[i] = (long**)malloc(sizeof(long*) * Simul->NDays);
        PayRef_DF_t_T_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_B_t_T_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_QVTerm_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_B_t_T_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_QVTerm_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_CrossTerm_PowerSpread2[i] = (double**)malloc(sizeof(double*) * Simul->NDays);
        PayRef_dt_PowerSpread[i] = (double**)malloc(sizeof(double*) * Simul->NDays);

        if (PayLeg->Reference_Inform[i].PowerSpreadFlag == 0)
        {
            if (PayLeg->Reference_Inform[i].RefRateType == 0 || PayLeg->Reference_Inform[i].RefRateType == 2)
            {
                ncpn = 1;
                for (j = 0; j < Simul->NDays; j++)
                {
                    PayRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ncpn);
                    PayRef_dt[i][j] = (double*)malloc(sizeof(double) * ncpn);
                }

                idxT1 = PayLeg->CurrentIdx;
                DayT1 = PayLeg->DaysForwardEnd[PayLeg->CurrentIdx];
                T1 = ((double)DayT1) / 365.0;

                idx1 = 0;
                idx2 = 0;
                idx3 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    ndates_Pay[i][j] = 1;

                    t = ((double)Simul->DaysForSimul[j]) / 365.0;
                    ///////////////////////////////////////////////////
                    // t는 시뮬날짜로하고 t가 ForwardStart날짜면
                    // T1는 차기 Forward End날짜
                    // 못찾으면 기존 Forward End날짜
                    ///////////////////////////////////////////////////
                    idxfrdstart = FindIndex(Simul->DaysForSimul[j], PayLeg->DaysForwardStart, PayLeg->NCashFlow);
                    if (idxfrdstart >= 0) T1 = ((double)PayLeg->DaysForwardEnd[idxfrdstart]) / 365.0;

                    DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    PayRef_dt[i][j][0] = T1 - t;
                    PayRef_DF_t_T[i][j][0] = DF_0_T / DF_0_t;
                    PayRef_B_t_T[i][j][0] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    PayRef_QVTerm[i][j][0] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    if (Simul->HWFactorFlag > 0)
                    {
                        PayRef_B_t_T2[i][j][0] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        PayRef_QVTerm2[i][j][0] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        PayRef_CrossTerm2[i][j][0] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef],  Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }

            }
            else if (PayLeg->Reference_Inform[i].RefRateType == 1)
            {
                /////////////////////////////////
                // 기초금리가 스왑금리 등이라면
                /////////////////////////////////
                idx0 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    /////////////////////////////////////////////////////////
                    // 시뮬시점 t로부터 SwapMaturity까지 모든 HW 파라미터 계산
                    /////////////////////////////////////////////////////////
                    t = ((double)(Simul->DaysForSimul[j])) / 365.0;
                    SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                    SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * PayLeg->Reference_Inform[i].RefSwapMaturity));
                    TempDate = SimDayYYYYMMDD;
                    CpnDates_Pay[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, PayLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates, TempDate); //할당
                    ndates_Pay[i][j] = ndates;

                    PayRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                    PayRef_dt[i][j] = (double*)malloc(sizeof(double) * ndates);
                    DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                    idx1 = 0;
                    for (k = 0; k < ndates; k++)
                    {
                        T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Pay[i][j][k])) / 365.0;
                        if (k == 0) PayRef_dt[i][j][k] = T1 - t;
                        else PayRef_dt[i][j][k] = ((double)(DayCountAtoB(CpnDates_Pay[i][j][k - 1], CpnDates_Pay[i][j][k]))) / 365.0;
                        DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                        PayRef_DF_t_T[i][j][k] = DF_0_T / DF_0_t;
                        PayRef_QVTerm[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                        PayRef_B_t_T[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                        if (Simul->HWFactorFlag > 0)
                        {
                            PayRef_QVTerm2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                            PayRef_B_t_T2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                            PayRef_CrossTerm2[i][j][0] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                        }
                    }
                }
            }
        }
        else
        {
            //////////////////////////////////////////////////////////////
            // PowerSpread가 1일 경우 무조건 RefRateType 는 스왑금리 등
            //////////////////////////////////////////////////////////////
            PayLeg->Reference_Inform[i].RefRateType = 1;
            idx0 = 0;
            for (j = 0; j < Simul->NDays; j++)
            {
                t = ((double)(Simul->DaysForSimul[j])) / 365.0;
                SimDayYYYYMMDD = Simul->YYYYMMDDForSimul[j];
                SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * PayLeg->Reference_Inform[i].PowerSpreadMat1));
                TempDate = SimDayYYYYMMDD;
                CpnDates_Pay[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, PayLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates, TempDate); //할당
                ndates_Pay[i][j] = ndates;

                PayRef_DF_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_B_t_T[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_QVTerm[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_B_t_T2[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_QVTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_CrossTerm2[i][j] = (double*)malloc(sizeof(double) * ndates);
                PayRef_dt[i][j] = (double*)malloc(sizeof(double) * ndates);
                DF_0_t = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], t);
                idx1 = 0;
                for (k = 0; k < ndates; k++)
                {
                    T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Pay[i][j][k])) / 365.0;
                    if (k == 0) PayRef_dt[i][j][k] = T1 - t;
                    else PayRef_dt[i][j][k] = ((double)(DayCountAtoB(CpnDates_Pay[i][j][k - 1], CpnDates_Pay[i][j][k]))) / 365.0;
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    PayRef_DF_t_T[i][j][k] = DF_0_T / DF_0_t;
                    PayRef_QVTerm[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    PayRef_B_t_T[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    if (Simul->HWFactorFlag > 0)
                    {
                        PayRef_QVTerm2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        PayRef_B_t_T2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        PayRef_CrossTerm2[i][j][k] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }

                SwapMatYYYYMMDD = EDate_Cpp(SimDayYYYYMMDD, (long)(12. * PayLeg->Reference_Inform[i].PowerSpreadMat2));
                CpnDates_Pay_PowerSpread[i][j] = Generate_CpnDate_Without_Holiday(SimDayYYYYMMDD, SwapMatYYYYMMDD, PayLeg->Reference_Inform[i].RefSwapNCPN_Ann, ndates2, TempDate); //할당
                ndates_Pay_PowerSpread[i][j] = ndates2;

                PayRef_DF_t_T_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_B_t_T_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_QVTerm_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_B_t_T_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_QVTerm_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_CrossTerm_PowerSpread2[i][j] = (double*)malloc(sizeof(double) * ndates2);
                PayRef_dt_PowerSpread[i][j] = (double*)malloc(sizeof(double) * ndates2);
                idx2 = 0;
                for (k = 0; k < ndates2; k++)
                {
                    T1 = ((double)DayCountAtoB(PricingDateC, CpnDates_Pay_PowerSpread[i][j][k])) / 365.0;
                    if (k == 0) PayRef_dt_PowerSpread[i][j][k] = T1 - t;
                    else PayRef_dt_PowerSpread[i][j][k] = ((double)(DayCountAtoB(CpnDates_Pay_PowerSpread[i][j][k - 1], CpnDates_Pay_PowerSpread[i][j][k]))) / 365.0;
                    DF_0_T = Calc_Discount_Factor(Simul->RateTerm[CurveIdxRef], Simul->Rate[CurveIdxRef], Simul->NRateTerm[CurveIdxRef], T1);
                    PayRef_DF_t_T_PowerSpread[i][j][k] = DF_0_T / DF_0_t;
                    PayRef_QVTerm_PowerSpread[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef]);
                    PayRef_B_t_T_PowerSpread[i][j][k] = B_s_to_t(Simul->HWKappa[CurveIdxRef], t, T1);
                    if (Simul->HWFactorFlag > 0)
                    {
                        PayRef_QVTerm_PowerSpread2[i][j][k] = HullWhiteQVTerm(t, T1, Simul->HWKappa2[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef]);
                        PayRef_B_t_T_PowerSpread2[i][j][k] = B_s_to_t(Simul->HWKappa2[CurveIdxRef], t, T1);
                        PayRef_CrossTerm_PowerSpread2[i][j][k] = HullWhite2F_CrossTerm(t, T1, Simul->HWKappa[CurveIdxRef], Simul->NHWVol[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol[CurveIdxRef], Simul->HWKappa2[CurveIdxRef], Simul->HWVolTerm[CurveIdxRef], Simul->HWVol2[CurveIdxRef], Simul->HW2FRho[CurveIdxRef]);
                    }
                }
            }
        }
    }

    HW_INFO* HW_information = new HW_INFO;
    HW_information->NAsset = Simul->NAsset;
    HW_information->NDays = Simul->NDays;

    HW_information->XA = XA_Array;
    HW_information->XV = XV_Array;
    HW_information->XA2F = XA_Array2;
    HW_information->XV2F = XV_Array2;

    HW_information->CurveIdx_DiscRcv = CurveIdx_DiscRcv;
    HW_information->CurveIdx_DiscPay = CurveIdx_DiscPay;
    HW_information->NRcv_Cf = RcvLeg->NCashFlow;
    HW_information->NPay_Cf = PayLeg->NCashFlow;

    HW_information->Rcv_DF_0_t = Rcv_DF_0_t;
    HW_information->Pay_DF_0_t = Pay_DF_0_t;
    HW_information->Rcv_DF_0_T = Rcv_DF_0_T;
    HW_information->Pay_DF_0_T = Pay_DF_0_T;
    HW_information->Rcv_DF_t_T = Rcv_DF_t_T;
    HW_information->Pay_DF_t_T = Pay_DF_t_T;

    HW_information->B_t_T_RcvDisc = B_t_T_RcvDisc;
    HW_information->B_t_T_PayDisc = B_t_T_PayDisc;
    HW_information->QVTerm_RcvDisc = QVTerm_RcvDisc;
    HW_information->QVTerm_PayDisc = QVTerm_PayDisc;
    HW_information->B_t_T_RcvDisc2F = B_t_T_RcvDisc2;
    HW_information->B_t_T_PayDisc2F = B_t_T_PayDisc2;
    HW_information->QVTerm_RcvDisc2F = QVTerm_RcvDisc2;
    HW_information->QVTerm_PayDisc2F = QVTerm_PayDisc2;
    HW_information->CrossTerm_RcvDisc2F = CrossTerm_RcvDisc2;
    HW_information->CrossTerm_PayDisc2F = CrossTerm_PayDisc2;
    HW_information->NRcvCurve = RcvLeg->NReference;
    HW_information->NPayCurve = RcvLeg->NReference;

    HW_information->ndates_cpn_rcv = ndates_Rcv;
    HW_information->RcvRef_DF_t_T = RcvRef_DF_t_T;
    HW_information->RcvRef_B_t_T = RcvRef_B_t_T;
    HW_information->RcvRef_QVTerm = RcvRef_QVTerm;
    HW_information->RcvRef_B_t_T2F = RcvRef_B_t_T2;
    HW_information->RcvRef_QVTerm2F = RcvRef_QVTerm2;
    HW_information->RcvRef_CrossTerm2F = RcvRef_CrossTerm2;
    HW_information->RcvRef_dt = RcvRef_dt;

    HW_information->ndates_cpn_powerspread_rcv = ndates_Rcv_PowerSpread;
    HW_information->RcvRef_DF_t_T_PowerSpread = RcvRef_DF_t_T_PowerSpread;
    HW_information->RcvRef_B_t_T_PowerSpread = RcvRef_B_t_T_PowerSpread;
    HW_information->RcvRef_QVTerm_PowerSpread = RcvRef_QVTerm_PowerSpread;
    HW_information->RcvRef_B_t_T_PowerSpread2F = RcvRef_B_t_T_PowerSpread2;
    HW_information->RcvRef_QVTerm_PowerSpread2F = RcvRef_QVTerm_PowerSpread2;
    HW_information->RcvRef_CrossTerm_PowerSpread2F = RcvRef_CrossTerm_PowerSpread2;
    HW_information->RcvRef_dt_PowerSpread = RcvRef_dt_PowerSpread;

    HW_information->ndates_cpn_pay = ndates_Pay;
    HW_information->PayRef_DF_t_T = PayRef_DF_t_T;
    HW_information->PayRef_B_t_T = PayRef_B_t_T;
    HW_information->PayRef_QVTerm = PayRef_QVTerm;
    HW_information->PayRef_B_t_T2F = PayRef_B_t_T2;
    HW_information->PayRef_QVTerm2F = PayRef_QVTerm2;
    HW_information->PayRef_CrossTerm2F = PayRef_CrossTerm2;
    HW_information->PayRef_dt = PayRef_dt;

    HW_information->ndates_cpn_powerspread_pay = ndates_Pay_PowerSpread;
    HW_information->PayRef_DF_t_T_PowerSpread = PayRef_DF_t_T_PowerSpread;
    HW_information->PayRef_B_t_T_PowerSpread = PayRef_B_t_T_PowerSpread;
    HW_information->PayRef_QVTerm_PowerSpread = PayRef_QVTerm_PowerSpread;
    HW_information->PayRef_B_t_T_PowerSpread2F = PayRef_B_t_T_PowerSpread2;
    HW_information->PayRef_QVTerm_PowerSpread2F = PayRef_QVTerm_PowerSpread2;
    HW_information->PayRef_CrossTerm_PowerSpread2F = PayRef_CrossTerm_PowerSpread2;
    HW_information->PayRef_dt_PowerSpread = PayRef_dt_PowerSpread;

    ResultCode = Simulate_HW(1, PricingDateC, NAFlag, Notional, RcvLeg, PayLeg,
        Simul, HW_information,
        SimulatedRateRcv, SimulatedRateRcv2, SimulatedRatePay, SimulatedRatePay2, SimulShortRate, SimulShortRate2, CurveIdx_Rcv,
        CurveIdx_Pay, ResultPrice, ResultRcv, ResultPay);


    // 할당 해제
    for (i = 0; i < Simul->NAsset; i++)
    {
        free(XA_Array[i]);
        free(XV_Array[i]);
        free(XA_Array2[i]);
        free(XV_Array2[i]);
    }

    free(XA_Array);
    free(XV_Array);
    free(XA_Array2);
    free(XV_Array2);

    for (i = 0; i < RcvLeg->NReference; i++)
    {
        free(SimulatedRateRcv[i]);
    }
    free(SimulatedRateRcv);
    for (i = 0; i < RcvLeg->NReference; i++)
    {
        free(SimulatedRateRcv2[i]);
    }
    free(SimulatedRateRcv2);

    

    for (i = 0; i < PayLeg->NReference; i++)
    {
        free(SimulatedRatePay[i]);
        free(SimulatedRatePay2[i]);
    }
    free(SimulatedRatePay);
    free(SimulatedRatePay2);

    for (i = 0; i < Simul->NAsset; i++)
    {
        free(SimulShortRate[i]);
        free(SimulShortRate2[i]);
    }
    free(SimulShortRate);
    free(SimulShortRate2);
    
    free(CurveIdx_Rcv);
    free(CurveIdx_Pay);
    
    free(Rcv_DF_0_t);
    free(Rcv_DF_0_T);
    free(Rcv_DF_t_T);
    free(Pay_DF_0_t);
    free(Pay_DF_0_T);
    free(Pay_DF_t_T);
    
    free(B_t_T_RcvDisc);
    free(QVTerm_RcvDisc);
    free(B_t_T_RcvDisc2);
    free(QVTerm_RcvDisc2);
    free(CrossTerm_RcvDisc2);

    free(B_t_T_PayDisc);
    free(QVTerm_PayDisc);
    free(B_t_T_PayDisc2);
    free(QVTerm_PayDisc2);
    free(CrossTerm_PayDisc2);
    // 할당 해제 Rcv Simul HW Params
    for (i = 0; i < RcvLeg->NReference; i++)
    {
        if (RcvLeg->Reference_Inform[i].PowerSpreadFlag == 0)
        {
            if (RcvLeg->Reference_Inform[i].RefRateType == 0 || RcvLeg->Reference_Inform[i].RefRateType == 2)
            {
                ncpn = 1;
                for (j = 0; j < Simul->NDays; j++)
                {
                    free(RcvRef_DF_t_T[i][j]);
                    free(RcvRef_B_t_T[i][j]);
                    free(RcvRef_QVTerm[i][j]);
                    free(RcvRef_B_t_T2[i][j]);
                    free(RcvRef_QVTerm2[i][j]);
                    free(RcvRef_CrossTerm2[i][j]);
                    free(RcvRef_dt[i][j]);
                }
            }
            else if (RcvLeg->Reference_Inform[i].RefRateType == 1)
            {
                /////////////////////////////////
                // 기초금리가 스왑금리 등이라면
                /////////////////////////////////
                idx0 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    free(CpnDates_Rcv[i][j]);

                    free(RcvRef_DF_t_T[i][j]);
                    free(RcvRef_B_t_T[i][j]);
                    free(RcvRef_QVTerm[i][j]);
                    free(RcvRef_B_t_T2[i][j]);
                    free(RcvRef_QVTerm2[i][j]);
                    free(RcvRef_CrossTerm2[i][j]);
                    free(RcvRef_dt[i][j]);
                }
            }
        }
        else
        {
            //////////////////////////////////////////////////////////////
            // PowerSpread가 1일 경우 무조건 RefRateType 는 스왑금리 등
            //////////////////////////////////////////////////////////////
            RcvLeg->Reference_Inform[i].RefRateType = 1;
            idx0 = 0;
            for (j = 0; j < Simul->NDays; j++)
            {
                free(CpnDates_Rcv[i][j]); //할당

                free(RcvRef_DF_t_T[i][j]);
                free(RcvRef_B_t_T[i][j]);
                free(RcvRef_QVTerm[i][j]);
                free(RcvRef_B_t_T2[i][j]);
                free(RcvRef_QVTerm2[i][j]);
                free(RcvRef_CrossTerm2[i][j]);
                free(RcvRef_dt[i][j]);
                free(CpnDates_Rcv_PowerSpread[i][j]); //할당

                free(RcvRef_DF_t_T_PowerSpread[i][j]);
                free(RcvRef_B_t_T_PowerSpread[i][j]);
                free(RcvRef_QVTerm_PowerSpread[i][j]);
                free(RcvRef_B_t_T_PowerSpread2[i][j]);
                free(RcvRef_QVTerm_PowerSpread2[i][j]);
                free(RcvRef_CrossTerm_PowerSpread2[i][j]);
                free(RcvRef_dt_PowerSpread[i][j]);
            }
        }
        free(ndates_Rcv[i]);
        free(CpnDates_Rcv[i]);
        free(RcvRef_DF_t_T[i]);
        free(RcvRef_B_t_T[i]);
        free(RcvRef_QVTerm[i]);
        free(RcvRef_B_t_T2[i]);
        free(RcvRef_QVTerm2[i]);
        free(RcvRef_CrossTerm2[i]);
        free(RcvRef_dt[i]);

        free(ndates_Rcv_PowerSpread[i]);
        free(CpnDates_Rcv_PowerSpread[i]);
        free(RcvRef_DF_t_T_PowerSpread[i]);
        free(RcvRef_B_t_T_PowerSpread[i]);
        free(RcvRef_QVTerm_PowerSpread[i]);
        free(RcvRef_B_t_T_PowerSpread2[i]);
        free(RcvRef_QVTerm_PowerSpread2[i]);
        free(RcvRef_CrossTerm_PowerSpread2[i]);
        free(RcvRef_dt_PowerSpread[i]);
    }

    free(ndates_Rcv);
    free(CpnDates_Rcv);
    free(RcvRef_DF_t_T);
    free(RcvRef_B_t_T);
    free(RcvRef_QVTerm);
    free(RcvRef_B_t_T2);
    free(RcvRef_QVTerm2);
    free(RcvRef_CrossTerm2);
    free(RcvRef_dt);

    free(ndates_Rcv_PowerSpread);
    free(CpnDates_Rcv_PowerSpread);
    free(RcvRef_DF_t_T_PowerSpread);
    free(RcvRef_B_t_T_PowerSpread);
    free(RcvRef_QVTerm_PowerSpread);
    free(RcvRef_B_t_T_PowerSpread2);
    free(RcvRef_QVTerm_PowerSpread2);
    free(RcvRef_CrossTerm_PowerSpread2);
    free(RcvRef_dt_PowerSpread);

    // 할당 해제 Pay Simul HW Params
    for (i = 0; i < PayLeg->NReference; i++)
    {
        if (PayLeg->Reference_Inform[i].PowerSpreadFlag == 0)
        {
            if (PayLeg->Reference_Inform[i].RefRateType == 0 || PayLeg->Reference_Inform[i].RefRateType == 2)
            {
                ncpn = 1;
                for (j = 0; j < Simul->NDays; j++)
                {
                    free(PayRef_DF_t_T[i][j]);
                    free(PayRef_B_t_T[i][j]);
                    free(PayRef_QVTerm[i][j]);
                    free(PayRef_B_t_T2[i][j]);
                    free(PayRef_QVTerm2[i][j]);
                    free(PayRef_CrossTerm2[i][j]);
                    free(PayRef_dt[i][j]);
                }
            }
            else if (PayLeg->Reference_Inform[i].RefRateType == 1)
            {
                /////////////////////////////////
                // 기초금리가 스왑금리 등이라면
                /////////////////////////////////
                idx0 = 0;
                for (j = 0; j < Simul->NDays; j++)
                {
                    free(CpnDates_Pay[i][j]);

                    free(PayRef_DF_t_T[i][j]);
                    free(PayRef_B_t_T[i][j]);
                    free(PayRef_QVTerm[i][j]);
                    free(PayRef_B_t_T2[i][j]);
                    free(PayRef_QVTerm2[i][j]);
                    free(PayRef_CrossTerm2[i][j]);
                    free(PayRef_dt[i][j]);

                }
            }
        }
        else
        {
            //////////////////////////////////////////////////////////////
            // PowerSpread가 1일 경우 무조건 RefRateType 는 스왑금리 등
            //////////////////////////////////////////////////////////////
            PayLeg->Reference_Inform[i].RefRateType = 1;
            idx0 = 0;
            for (j = 0; j < Simul->NDays; j++)
            {
                free(CpnDates_Pay[i][j]); //할당

                free(PayRef_DF_t_T[i][j]);
                free(PayRef_B_t_T[i][j]);
                free(PayRef_QVTerm[i][j]);
                free(PayRef_B_t_T2[i][j]);
                free(PayRef_QVTerm2[i][j]);
                free(PayRef_CrossTerm2[i][j]);
                free(PayRef_dt[i][j]);
                free(CpnDates_Pay_PowerSpread[i][j]); //할당

                free(PayRef_DF_t_T_PowerSpread[i][j]);
                free(PayRef_B_t_T_PowerSpread[i][j]);
                free(PayRef_QVTerm_PowerSpread[i][j]);
                free(PayRef_B_t_T_PowerSpread2[i][j]);
                free(PayRef_QVTerm_PowerSpread2[i][j]);
                free(PayRef_CrossTerm_PowerSpread2[i][j]);
                free(PayRef_dt_PowerSpread[i][j]);
            }
        }
        free(ndates_Pay[i]);
        free(CpnDates_Pay[i]);
        free(PayRef_DF_t_T[i]);
        free(PayRef_B_t_T[i]);
        free(PayRef_QVTerm[i]);
        free(PayRef_B_t_T2[i]);
        free(PayRef_QVTerm2[i]);
        free(PayRef_CrossTerm2[i]);
        free(PayRef_dt[i]);

        free(ndates_Pay_PowerSpread[i]);
        free(CpnDates_Pay_PowerSpread[i]);
        free(PayRef_DF_t_T_PowerSpread[i]);
        free(PayRef_B_t_T_PowerSpread[i]);
        free(PayRef_QVTerm_PowerSpread[i]);
        free(PayRef_B_t_T_PowerSpread2[i]);
        free(PayRef_QVTerm_PowerSpread2[i]);
        free(PayRef_CrossTerm_PowerSpread2[i]);
        free(PayRef_dt_PowerSpread[i]);
    }

    free(ndates_Pay);
    free(CpnDates_Pay);
    free(PayRef_DF_t_T);
    free(PayRef_B_t_T);
    free(PayRef_QVTerm);
    free(PayRef_B_t_T2);
    free(PayRef_QVTerm2);
    free(PayRef_CrossTerm2);
    free(PayRef_dt);

    free(ndates_Pay_PowerSpread);
    free(CpnDates_Pay_PowerSpread);
    free(PayRef_DF_t_T_PowerSpread);
    free(PayRef_B_t_T_PowerSpread);
    free(PayRef_QVTerm_PowerSpread);
    free(PayRef_B_t_T_PowerSpread2);
    free(PayRef_QVTerm_PowerSpread2);
    free(PayRef_CrossTerm_PowerSpread2);
    free(PayRef_dt_PowerSpread);
    delete(HW_information);

    return 1;
}

DLLEXPORT(long) Pricing_IRPhaseStructuredSwap(
    long PriceDate,                     // 1 가격계산일 long Type
    long NAFlag,                        // 2 Notional Amount 사용 여부 0: No ExChange Notional Amount 1: ExChange Notioanl Amount
    double Notional,                    // 3 Notional Amount
    long* PayoffStructure,              // 4 [0]: RcvLeg 페이오프조건 [1]: PayLeg 페이오프조건 {페이오프조건 0:Range(R1)&Range(R2)&Range(R3) 1:Range(R1+R2+R3)}
    long* HolidayFlagCount,             // 5 [0~2]: R1,R2,R3 Rcv HolidayFlag, [3~5]: R1, R2, R3 Pay HolidayFlag, [6~8]: R1, R2, R3 Rcv HolidayCount, [9~11]: R1, R2, R3 Pay HolidayCount
    long* Holidays,                     // 6 [0~sum(HolidayFlagCount[6~11])]: Holidays Rcv R1R2R3, Pay R1R2R3

    // Receive Leg Information
    long* RcvFlag,                      // 7 길이 4 [0]: NReference, [1]: Fix/Flo Flag, [2]: Accrual Flag, [3]: DailySimulFlag
    double* RcvMaxLossReturn,           // 8 길이 2 [0]: Max Loss [1] Max Return
    long* RcvRefCurveNumber,            // 9 길이 4 Reference Curve 번호 Array [Len = NReference]
    long* RcvRefRateType,               // 10 길이 3 기초금리 타입 0: CD/Libor (AccrualX) 1: CD/Libor, 이자율Swap 2: SOFR
    double* RcvSwapInfo,                // 11 길이 6 [짝수] 기초금리 타입이 1일 경우 연 이자 지급횟수 [홀수] 만기
    long* RcvDayCountFlag,              // 12 길이 4 DayCount 0: 365 ,  1: 360
    double* RcvRefCondMultiple,         // 13 길이 3 금리결정조건 Multiple
    long* RcvRefPowerSpreadFlag,        // 14 길이 3 파워스프레드 사용여부
    double* RcvRefPowerSpreadMat,       // 15 길이 6 [짝수] 파워스프레드 만기1 [홀수] 파워스프레드 만기2
    double* RcvRefRange,                // 16 길이 6 [짝수] Range 상한 [홀수] Range 하한
    double* RcvPayoffMultiple,          // 17 길이 3 페이오프 조건 Multiple
    long NRcvCashFlow,                  // 18 Receive Leg CashFlow 개수
    long* RcvCashFlowSchedule,          // 19 [0~NCF-1]: ResetStart, [NCF~2*NCF-1]: ResetEnd, [2*NCF~3*NCF-1]: 기산일, [3*NCF~4*NCF-1]: 기말일, [4*NCF~5*NCF-1]: 지급일
    double* RcvCouponFixRate,           // 20 [0~NCF-1]: 고정 쿠폰, [NCF~2*NCF-1]: 확정과거금리 [2*NCF~3*NCF-1]: Range충족쿠폰Rate

    // Receive Leg Information
    long* PayFlag,                      // 21 길이 4 [0]: NReference, [1]: Fix/Flo Flag, [2]: Accrual Flag
    double* PayMaxLossReturn,           // 22 길이 2 [0]: Max Loss [1] Max Return
    long* PayRefCurveNumber,            // 23 길이 4 Reference Curve 번호 Array [Len = NReference]
    long* PayRefRateType,               // 24 길이 3 기초금리 타입 0: CD/Libor (AccrualX) 1: CD/Libor, 이자율Swap 2: SOFR
    double* PaySwapInfo,                // 25 길이 6 [짝수] 기초금리 타입이 1일 경우 연 이자 지급횟수 [홀수] 만기
    long* PayDayCountFlag,              // 26 길이 4 DayCount 0: 365 ,  1: 360
    double* PayRefCondMultiple,         // 27 길이 3 금리결정조건 Multiple
    long* PayRefPowerSpreadFlag,        // 28 길이 3 파워스프레드 사용여부
    double* PayRefPowerSpreadMat,       // 29 길이 6 [짝수] 파워스프레드 만기1 [홀수] 파워스프레드 만기2
    double* PayRefRange,                // 30 길이 6 [짝수] Range 상한 [홀수] Range 하한
    double* PayPayoffMultiple,          // 31 길이 3 페이오프 조건 Multiple
    long NPayCashFlow,                  // 32 Receive Leg CashFlow 개수
    long* PayCashFlowSchedule,          // 33 [0~NCF-1]: ResetStart, [NCF~2*NCF-1]: ResetEnd, [2*NCF~3*NCF-1]: 기산일, [3*NCF~4*NCF-1]: 기말일, [4*NCF~5*NCF-1]: 지급일
    double* PayCouponFixRate,           // 34 [0~NCF-1]: 고정 쿠폰, [NCF~2*NCF-1]: 확정과거금리 [2*NCF~3*NCF-1]: Range충족쿠폰Rate

    // 커브 및 HW정보
    long* NHWVolCount,                  // 35 [0~3] Hull White Vol 개수
    double* HWVolTermArray,             // 36 [0~sum(NHWVolCount)-1] Hull White Vol Term Array
    double* HWVolArray,                 // 37 [0~sum(NHWVolCount)-1] Hull White Vol Array
    double* HWKappaArray,               // 38 [0~3] Hull White Kappa. [4~7] Ull White 2F kappa, [8~11] HW2F rho
    long* NZeroRate,                    // 39 [0~3] ZeroRate 개수
    double* ZeroTerm,                   // 40 [0~sum(NZeroRate)-1] Zero Rate Term
    double* ZeroRate,                   // 41 [0~sum(NZeroRate)-1] Zero Rate

    // 상관계수 및 히스토리 
    double* Corr,                       // 42 Correlation Matrix.rehaped(-1)
    long* NDayHistRcv,                  // 43 [0~3] Rcv Rate History 개수
    long* RateHistDateRcv,              // 44 [0~sum(NDayHistRcv)-1] RateHistory의 Date
    double* RateHistRcv,                // 45 [0~sum(NDayHistRcv)-1] RateHistory의 Rate
    long* NDayHistPay,                  // 46 [0~3] Pay Rate History 개수
    long* RateHistDatePay,              // 47 [0~sum(NDayHistPay)-1] RateHistory의 Date
    double* RateHistPay,                // 48 [0~sum(NDayHistPay)-1] RateHistory의 Rate

    // 시뮬레이션
    long NSimul,                        // 49 시뮬레이션횟수
    long* GreekTextFlag,                // 50 [0]Greek산출여부 [1]TextDumpping여부

    // 옵션관련
    long NOption,                       // 51 옵션개수 길이 
    long* OptionDateAndFlag,            // 52 [0~NOption-1]옵션행사일 [NOption]행사조건 [Noption + 1] 옵션타입(발행자, 투자자 콜) [Noption + 2] 옵션행사일->지급일까지 일수
    double* OptionKAndRange,            // 53 [0~NOption-1]옵션행사가격% [NOption~7NOption-1] Ref1~3 Range상한 및 하한 

    double* ResultPrice,                // 54 산출된 가격 [0] Rcv [1] Pay [2] Price [3] OptionPrice [4~
    double* ResultRcv,                  // 55 [0~NCF-1]금리1, [NCF~2NCF-1]금리2, [2NCF~3NCF-1]금리3, [3NCF~4NCF-1] E(Accrual수), [4NCF~5NCF-1] E(CPN), [5NCF~6NCF-1] E(DF)
    double* ResultPay,                  // 56 [0~NCF-1]금리1, [NCF~2NCF-1]금리2, [2NCF~3NCF-1]금리3, [3NCF~4NCF-1] E(Accrual수), [4NCF~5NCF-1] E(CPN), [5NCF~6NCF-1] E(DF)
    long HWFactorFlag,                  // 57 0: 1Factor 1: 2Factor
    double* HWVolArray2,                // 58 HW 2F Vol Array
    double* HWQuantoInfo,               // 59 HW Quanto Information
    char* Error                         // 60 에러메시지
)
{
    long i;
    //_CrtSetBreakAlloc(156167);
    long ResultCode = 0;
    long ErrorCode = 0;
    long j;
    long k;
    long n;
    long n_null = 0.0;
    double* HWKappaArray2 = HWKappaArray + 4;
    double* HWrho2F = HWKappaArray + 8;
    double* HWQuantoFlag = HWQuantoInfo;
    double* HWQuantoRho = HWQuantoInfo + 4;
    double* HWQuantoFXVol = HWQuantoInfo + 8;
    long GreekFlag = GreekTextFlag[0];
    long TextFlag = GreekTextFlag[1];
    double* ResultPV01 = ResultPrice + 4;
    double* ResultKeyPV01 = ResultPV01 + 8;

    char CalcFunctionName[] = "Pricing_IRStructuredSwap_Excel";
    char SaveFileName[100];
    get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
    if (TextFlag == 1)
    {
        DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate", PriceDate);
        DumppingTextData(CalcFunctionName, SaveFileName, "NAFlag", NAFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "Notional", Notional);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayoffStructure", 2, PayoffStructure);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HolidayFlagCount", 12, HolidayFlagCount);
        n = 0;
        for (i = 6; i < 12; i++) n += HolidayFlagCount[i];
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Holidays_Excel", n, Holidays);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HolidayFlagCount", 12, HolidayFlagCount);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvFlag", 4, RcvFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvMaxLossReturn", 2, RcvMaxLossReturn);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefCurveNumber", 4, RcvRefCurveNumber);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefRateType", 3, RcvRefRateType);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvSwapInfo", 6, RcvSwapInfo);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvDayCountFlag", 4, RcvDayCountFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefCondMultiple", 3, RcvRefCondMultiple);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefPowerSpreadFlag", 3, RcvRefPowerSpreadFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefPowerSpreadMat", 6, RcvRefPowerSpreadMat);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRefRange", 6, RcvRefRange);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvPayoffMultiple", 3, RcvPayoffMultiple);
        DumppingTextData(CalcFunctionName, SaveFileName, "NRcvCashFlow", NRcvCashFlow);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvCashFlowScheduleExcelDate", NRcvCashFlow * 5, RcvCashFlowSchedule);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvCouponFixRate", NRcvCashFlow * 3, RcvCouponFixRate);

        //
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayFlag", 4, PayFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayMaxLossReturn", 2, PayMaxLossReturn);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefCurveNumber", 4, PayRefCurveNumber);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefRateType", 3, PayRefRateType);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PaySwapInfo", 6, PaySwapInfo);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDayCountFlag", 4, PayDayCountFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefCondMultiple", 3, PayRefCondMultiple);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefPowerSpreadFlag", 3, PayRefPowerSpreadFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefPowerSpreadMat", 6, PayRefPowerSpreadMat);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRefRange", 6, PayRefRange);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayPayoffMultiple", 3, PayPayoffMultiple);
        DumppingTextData(CalcFunctionName, SaveFileName, "NPayCashFlow", NPayCashFlow);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayCashFlowScheduleExcelDate", NPayCashFlow * 5, PayCashFlowSchedule);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayCouponFixRate", NPayCashFlow * 3, PayCouponFixRate);

        //
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NHWVolCount", 4, NHWVolCount);
        n = 0;
        for (i = 0; i < 4; i++) if (NHWVolCount[i] > 0) n += NHWVolCount[i];
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWVolTermArray", n, HWVolTermArray);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWVolArray", n, HWVolArray);

        if (HWFactorFlag == 0) DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWKappaArray", 4, HWKappaArray);
        else DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWKappaArray", 12, HWKappaArray);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NZeroRate", 4, NZeroRate);

        n = 0;
        for (i = 0; i < 4; i++) if (NZeroRate[i] > 0) n += NZeroRate[i];

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroTerm", n, ZeroTerm);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroRate", n, ZeroRate);
        DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Corr", 4, 4, Corr);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NDayHistRcv", 3, NDayHistRcv);

        n = 0;
        for (i = 0; i < 3; i++) if (NDayHistRcv[i] > 0) n += NDayHistRcv[i];
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateHistDateRcv", n, RateHistDateRcv);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateHistRcv", n, RateHistRcv);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NDayHistPay", 3, NDayHistPay);
        n = 0;
        for (i = 0; i < 3; i++) if (NDayHistPay[i] > 0) n += NDayHistPay[i];
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateHistDatePay", n, RateHistDatePay);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateHistPay", n, RateHistPay);

        DumppingTextData(CalcFunctionName, SaveFileName, "NSimul", NSimul);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "GreekTextFlag", 2, GreekTextFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "NOption", NOption);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "OptionDateAndFlag", NOption + 3, OptionDateAndFlag);
        DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "OptionKAndRange", NOption, 7, OptionKAndRange);
        DumppingTextData(CalcFunctionName, SaveFileName, "HWFactorFlag", HWFactorFlag);


        n = 0;
    }

    if (PriceDate < 19000101) PriceDate = ExcelDateToCDate(PriceDate);
    for (i = 0; i < NRcvCashFlow * 5; i++) if (RcvCashFlowSchedule[i] < 19000101) RcvCashFlowSchedule[i] = ExcelDateToCDate(RcvCashFlowSchedule[i]);
    for (i = 0; i < NPayCashFlow * 5; i++) if (PayCashFlowSchedule[i] < 19000101) PayCashFlowSchedule[i] = ExcelDateToCDate(PayCashFlowSchedule[i]);
    
    for (i = 0; i < NDayHistRcv[0] + NDayHistRcv[1] + NDayHistRcv[2]; i++) if (RateHistDateRcv[i] < 19000101) RateHistDateRcv[i] = ExcelDateToCDate(RateHistDateRcv[i]);
    for (i = 0; i < NDayHistPay[0] + NDayHistPay[1] + NDayHistPay[2]; i++) if (RateHistDatePay[i] < 19000101) RateHistDatePay[i] = ExcelDateToCDate(RateHistDatePay[i]);

    long* FloatingFlagRcv = (long*)malloc(sizeof(long) * NRcvCashFlow);
    long* FloatingFlagPay = (long*)malloc(sizeof(long) * NPayCashFlow);
    for (i = 0; i < NRcvCashFlow; i++) FloatingFlagRcv[i] = ((long)(RcvCouponFixRate[NRcvCashFlow + i] + 0.05));
    for (i = 0; i < NPayCashFlow; i++) FloatingFlagPay[i] = ((long)(PayCouponFixRate[NPayCashFlow + i] + 0.05));


    long N_Curve_Max = 4;       // 커브 최대 개수
    long N_Ref_Max = 3;         // 레퍼런스 최대 개수

    //////////////////////////////////////////////////////////////////////////
    // HWVolMatrix, ZeroRateMatrix 매핑 Shape = (N_Curve_Max, 각 Term 개수) //
    //////////////////////////////////////////////////////////////////////////

    double** HWVolTermMatrix = (double**)malloc(sizeof(double*) * N_Curve_Max);
    double** HWVolMatrix = (double**)malloc(sizeof(double*) * N_Curve_Max);
    double** HWVolMatrix2 = (double**)malloc(sizeof(double*) * N_Curve_Max);
    n = 0;
    for (i = 0; i < N_Curve_Max; i++)
    {
        HWVolTermMatrix[i] = HWVolTermArray + n;
        HWVolMatrix[i] = HWVolArray + n;
        HWVolMatrix2[i] = HWVolArray2 + n;
        n = n + NHWVolCount[i];
    }

    double** ZeroRateTermMatrix = (double**)malloc(sizeof(double*) * N_Curve_Max);
    double** ZeroRateMatrix = (double**)malloc(sizeof(double*) * N_Curve_Max);
    n = 0;
    for (i = 0; i < N_Curve_Max; i++)
    {
        ZeroRateTermMatrix[i] = ZeroTerm + n;
        ZeroRateMatrix[i] = ZeroRate + n;
        n = n + NZeroRate[i];
    }

    long DailySimulFlag = RcvFlag[3];

    long PriceDateYYYYMMDD;
    if (PriceDate < 19000101) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    long RcvPayoffStructure = PayoffStructure[0];
    long PayPayoffStructure = PayoffStructure[1];

    ///////////////
    // Holiday Mapping 시작
    ///////////////
    long* RcvHolidayCalcFlag = HolidayFlagCount;
    long* PayHolidayCalcFlag = HolidayFlagCount + N_Ref_Max;
    long* RcvHolidayCount = HolidayFlagCount + 2 * N_Ref_Max;
    long* PayHolidayCount = HolidayFlagCount + 3 * N_Ref_Max;
    long* RcvHolidays = Holidays;
    n = 0;
    for (i = 0; i < N_Ref_Max; i++)
    {
        n = n + RcvHolidayCount[i];
    }
    long* PayHolidays = Holidays + n;
    for (i = 0; i < n; i++) if (RcvHolidays[i] < 19000101) RcvHolidays[i] = ExcelDateToCDate(RcvHolidays[i]);

    n = 0;
    for (i = 0; i < N_Ref_Max; i++)
    {
        n = n + PayHolidayCount[i];
    }
    for (i = 0; i < n; i++) if (PayHolidays[i] < 19000101) PayHolidays[i] = ExcelDateToCDate(PayHolidays[i]);

    long MinDate, MaxDate;
    MinDate = RcvCashFlowSchedule[0] - 10000;
    MaxDate = RcvCashFlowSchedule[NRcvCashFlow * 2 - 1] + 20000;
    long* RcvHolidayCountAdj = (long*)malloc(sizeof(long) * N_Ref_Max);
    long* PayHolidayCountAdj = (long*)malloc(sizeof(long) * N_Ref_Max);
    long** RcvHolidayAdj = (long**)malloc(sizeof(long*) * RcvFlag[0]);
    long** PayHolidayAdj = (long**)malloc(sizeof(long*) * PayFlag[0]);

    k = 0;
    for (i = 0; i < RcvFlag[0]; i++)
    {
        n = 0;
        for (j = 0; j < RcvHolidayCount[i]; j++)
        {
            if (RcvHolidays[k] >= MinDate && RcvHolidays[k] <= MaxDate)
            {
                n += 1;
            }
            k += 1;
        }
        RcvHolidayCountAdj[i] = n;
        RcvHolidayAdj[i] = (long*)malloc(sizeof(long) * n);
    }

    k = 0;
    for (i = 0; i < RcvFlag[0]; i++)
    {
        n = 0;
        for (j = 0; j < RcvHolidayCount[i]; j++)
        {
            if (RcvHolidays[k] >= MinDate && RcvHolidays[k] <= MaxDate)
            {
                RcvHolidayAdj[i][n] = RcvHolidays[k];
                n += 1;
            }
            k += 1;
        }
    }

    k = 0;
    for (i = 0; i < PayFlag[0]; i++)
    {
        n = 0;
        for (j = 0; j < PayHolidayCount[i]; j++)
        {
            if (PayHolidays[k] >= MinDate && PayHolidays[k] <= MaxDate)
            {
                n += 1;
            }
            k += 1;
        }
        PayHolidayCountAdj[i] = n;
        PayHolidayAdj[i] = (long*)malloc(sizeof(long) * n);
    }

    k = 0;
    for (i = 0; i < PayFlag[0]; i++)
    {
        n = 0;
        for (j = 0; j < PayHolidayCount[i]; j++)
        {
            if (PayHolidays[k] >= MinDate && PayHolidays[k] <= MaxDate)
            {
                PayHolidayAdj[i][n] = PayHolidays[k];
                n += 1;
            }
            k += 1;
        }
    }


    //////////////////////////////
    // 옵션 관련 Date
    //////////////////////////////
    long NOptionOrg = NOption;
    long NPrevOpt = 0;
    long* OptionDate;
    for (i = 0; i < NOption; i++) if (OptionDateAndFlag[i] < 19000101) OptionDateAndFlag[i] = ExcelDateToCDate(OptionDateAndFlag[i]);

    for (i = 0; i < NOption; i++)
    {
        if (OptionDateAndFlag[i] <= PriceDate) NPrevOpt += 1;
    }

    OptionDate = (long*)malloc(sizeof(long) * max(1, NOptionOrg - NPrevOpt));
    double* OptionStrikeRate = (double*)malloc(sizeof(double) * max(1, NOptionOrg - NPrevOpt));
    double** RangeUp;
    double** RangeDn;

    RangeUp = (double**)malloc(sizeof(double*) * max(1, RcvFlag[0]));
    RangeDn = (double**)malloc(sizeof(double*) * max(1, RcvFlag[0]));
    for (i = 0; i < RcvFlag[0]; i++)
    {
        RangeUp[i] = (double*)malloc(sizeof(double) * max(1, NOptionOrg - NPrevOpt));
        RangeDn[i] = (double*)malloc(sizeof(double) * max(1, NOptionOrg - NPrevOpt));
    }

    k = 0;
    for (i = 0; i < NOption; i++)
    {
        if (OptionDateAndFlag[i] > PriceDate)
        {
            OptionDate[k] = OptionDateAndFlag[i];
            OptionStrikeRate[k] = OptionKAndRange[i];
            for (j = 0; j < RcvFlag[0]; j++)
            {
                RangeUp[j][k] = OptionKAndRange[i + (1 + 2 * j) * NOption];
                RangeDn[j][k] = OptionKAndRange[i + (2 + 2 * j) * NOption];
            }
            k += 1;
        }
    }

    long OptionUseFlag;
    if (NOption > 0) OptionUseFlag = 1;
    else OptionUseFlag = 0;
    long CallConditionFlag = OptionDateAndFlag[NOptionOrg];
    long OptionType = OptionDateAndFlag[NOptionOrg + 1];
    long OptDatetoPayDate = OptionDateAndFlag[NOptionOrg + 2];
    //////////////////////////////
    // 시뮬레이션에 사용되는 커브 번호 Mapping 시작
    //////////////////////////////

    long nCurveUsing = 0;
    long nUsingCurveRcv = RcvFlag[0];
    long nUsingCurvePay = PayFlag[0];

    long nTotalCurve = nUsingCurveRcv + nUsingCurvePay + 2;
    long* RcvPayCurveNumber = (long*)malloc(sizeof(long) * nTotalCurve);
    for (i = 0; i < nUsingCurveRcv; i++)
    {
        RcvPayCurveNumber[i] = RcvRefCurveNumber[i];
    }
    for (i = 0; i < nUsingCurvePay; i++)
    {
        RcvPayCurveNumber[i + nUsingCurveRcv] = PayRefCurveNumber[i];
    }
    RcvPayCurveNumber[nUsingCurveRcv + nUsingCurvePay] = RcvRefCurveNumber[3];
    RcvPayCurveNumber[nUsingCurveRcv + nUsingCurvePay + 1] = PayRefCurveNumber[3];
    bubble_sort_long(RcvPayCurveNumber, nTotalCurve, 1);

    long nSimulateCurve = 0;
    long* SimulateCurveIdx = Make_Unique_Array(nTotalCurve, RcvPayCurveNumber, nSimulateCurve);

    //////////////////////////////
    // 각 Leg의 정보 Mapping
    //////////////////////////////

    // RcvPay 공통
    LEG_INFO* RcvLeg = new LEG_INFO;
    LEG_INFO* PayLeg = new LEG_INFO;
    RcvLeg->NReference = nUsingCurveRcv;
    PayLeg->NReference = nUsingCurvePay;
    RcvLeg->FixFloFlag = RcvFlag[1];
    PayLeg->FixFloFlag = PayFlag[1];
    RcvLeg->AccrualFlag = RcvFlag[2];
    PayLeg->AccrualFlag = PayFlag[2];
    RcvLeg->MaxLossY = RcvMaxLossReturn[0];
    PayLeg->MaxLossY = PayMaxLossReturn[0];
    RcvLeg->MaxRetY = RcvMaxLossReturn[1];
    PayLeg->MaxRetY = PayMaxLossReturn[1];
    RcvLeg->DiscCurveNum = RcvRefCurveNumber[3];
    PayLeg->DiscCurveNum = PayRefCurveNumber[3];
    RcvLeg->Reference_Inform = new REFERENCE_INFO[nUsingCurveRcv];
    PayLeg->Reference_Inform = new REFERENCE_INFO[nUsingCurvePay];
    RcvLeg->PayoffStructure = RcvPayoffStructure;
    PayLeg->PayoffStructure = PayPayoffStructure;

    // Rcv
    for (i = 0; i < nUsingCurveRcv; i++)
    {
        RcvLeg->Reference_Inform[i].CurveNum = RcvRefCurveNumber[i];
        RcvLeg->Reference_Inform[i].RefRateType = RcvRefRateType[i];
        RcvLeg->Reference_Inform[i].RefSwapNCPN_Ann = (long)RcvSwapInfo[2 * i];
        RcvLeg->Reference_Inform[i].RefSwapMaturity = RcvSwapInfo[2 * i + 1];
        RcvLeg->Reference_Inform[i].DayCountFlag = RcvDayCountFlag[i];
        RcvLeg->Reference_Inform[i].RefRateCondMultiple = RcvRefCondMultiple[i];
        RcvLeg->Reference_Inform[i].PowerSpreadFlag = RcvRefPowerSpreadFlag[i];
        RcvLeg->Reference_Inform[i].PowerSpreadMat1 = RcvRefPowerSpreadMat[2 * i];
        RcvLeg->Reference_Inform[i].PowerSpreadMat2 = RcvRefPowerSpreadMat[2 * i + 1];
        RcvLeg->Reference_Inform[i].RangeUp = RcvRefRange[2 * i];
        RcvLeg->Reference_Inform[i].RangeDn = RcvRefRange[2 * i + 1];
        RcvLeg->Reference_Inform[i].PayoffMultiple = RcvPayoffMultiple[i];
    }

    RcvLeg->NCashFlow = NRcvCashFlow;
    RcvLeg->FloatingFlag = FloatingFlagRcv;
    RcvLeg->ForwardStart_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->ForwardEnd_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->DaysForwardStart = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->DaysForwardEnd = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->FractionStart_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->FractionEnd_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->PayDate_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->DaysPayDate_C = (long*)malloc(sizeof(long) * NRcvCashFlow);
    RcvLeg->CouponRate = (double*)malloc(sizeof(double) * NRcvCashFlow);
    RcvLeg->RangeCoupon = (double*)malloc(sizeof(double) * NRcvCashFlow);

    RcvLeg->OptionUseFlag = OptionUseFlag;
    RcvLeg->NOption = NOptionOrg - NPrevOpt;
    RcvLeg->OptionDate = OptionDate;
    RcvLeg->CallConditionFlag = CallConditionFlag;
    RcvLeg->OptionType = OptionType;
    RcvLeg->OptDateToPayDate = OptDatetoPayDate;
    RcvLeg->StrikeRate = OptionStrikeRate;
    RcvLeg->RangeUp = RangeUp;
    RcvLeg->RangeDn = RangeDn;

    for (i = 0; i < NRcvCashFlow; i++)
    {
        RcvLeg->ForwardStart_C[i] = RcvCashFlowSchedule[i];
        RcvLeg->ForwardEnd_C[i] = RcvCashFlowSchedule[i + NRcvCashFlow];
        RcvLeg->DaysForwardStart[i] = DayCountAtoB(PriceDate, RcvLeg->ForwardStart_C[i]);
        RcvLeg->DaysForwardEnd[i] = DayCountAtoB(PriceDate, RcvLeg->ForwardEnd_C[i]);
        if (RcvLeg->DaysForwardStart[i] == RcvLeg->DaysForwardEnd[i]) RcvLeg->DaysForwardEnd[i] = DayPlus(RcvLeg->DaysForwardEnd[i], 1);
        RcvLeg->FractionStart_C[i] = RcvCashFlowSchedule[i + 2 * NRcvCashFlow];
        RcvLeg->FractionEnd_C[i] = RcvCashFlowSchedule[i + 3 * NRcvCashFlow];
        RcvLeg->PayDate_C[i] = RcvCashFlowSchedule[i + 4 * NRcvCashFlow];
        RcvLeg->DaysPayDate_C[i] = DayCountAtoB(PriceDate, RcvLeg->PayDate_C[i]);

        RcvLeg->CouponRate[i] = RcvCouponFixRate[i];
        RcvLeg->RangeCoupon[i] = RcvCouponFixRate[i + 2 * NRcvCashFlow];
    }

    long IdxCurrentRcvLeg = 0;
    for (i = 0; i < NRcvCashFlow; i++)
    {
        if (PriceDate < RcvLeg->PayDate_C[i] && PriceDate >= RcvLeg->ForwardStart_C[i])
        {
            IdxCurrentRcvLeg = i;
        }
    }
    RcvLeg->CurrentIdx = IdxCurrentRcvLeg;

    // Pay
    for (i = 0; i < nUsingCurvePay; i++)
    {
        PayLeg->Reference_Inform[i].CurveNum = PayRefCurveNumber[i];
        PayLeg->Reference_Inform[i].RefRateType = PayRefRateType[i];
        PayLeg->Reference_Inform[i].RefSwapNCPN_Ann = (long)PaySwapInfo[2 * i];
        PayLeg->Reference_Inform[i].RefSwapMaturity = PaySwapInfo[2 * i + 1];
        PayLeg->Reference_Inform[i].DayCountFlag = PayDayCountFlag[i];
        PayLeg->Reference_Inform[i].RefRateCondMultiple = PayRefCondMultiple[i];
        PayLeg->Reference_Inform[i].PowerSpreadFlag = PayRefPowerSpreadFlag[i];
        PayLeg->Reference_Inform[i].PowerSpreadMat1 = PayRefPowerSpreadMat[2 * i];
        PayLeg->Reference_Inform[i].PowerSpreadMat2 = PayRefPowerSpreadMat[2 * i + 1];
        PayLeg->Reference_Inform[i].RangeUp = PayRefRange[2 * i];
        PayLeg->Reference_Inform[i].RangeDn = PayRefRange[2 * i + 1];
        PayLeg->Reference_Inform[i].PayoffMultiple = PayPayoffMultiple[i];
    }

    PayLeg->NCashFlow = NPayCashFlow;
    PayLeg->FloatingFlag = FloatingFlagPay;
    PayLeg->ForwardStart_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->ForwardEnd_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->DaysForwardStart = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->DaysForwardEnd = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->FractionStart_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->FractionEnd_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->PayDate_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->DaysPayDate_C = (long*)malloc(sizeof(long) * NPayCashFlow);
    PayLeg->CouponRate = (double*)malloc(sizeof(double) * NPayCashFlow);
    PayLeg->RangeCoupon = (double*)malloc(sizeof(double) * NPayCashFlow);
    for (i = 0; i < NPayCashFlow; i++)
    {
        PayLeg->ForwardStart_C[i] = PayCashFlowSchedule[i];
        PayLeg->ForwardEnd_C[i] = PayCashFlowSchedule[i + NPayCashFlow];
        PayLeg->DaysForwardStart[i] = DayCountAtoB(PriceDate, PayLeg->ForwardStart_C[i]);
        PayLeg->DaysForwardEnd[i] = DayCountAtoB(PriceDate, PayLeg->ForwardEnd_C[i]);
        if (PayLeg->DaysForwardStart[i] == PayLeg->DaysForwardEnd[i]) PayLeg->DaysForwardEnd[i] = DayPlus(PayLeg->DaysForwardEnd[i], 1);
        PayLeg->FractionStart_C[i] = PayCashFlowSchedule[i + 2 * NPayCashFlow];
        PayLeg->FractionEnd_C[i] = PayCashFlowSchedule[i + 3 * NPayCashFlow];
        PayLeg->PayDate_C[i] = PayCashFlowSchedule[i + 4 * NPayCashFlow];
        PayLeg->DaysPayDate_C[i] = DayCountAtoB(PriceDate, PayLeg->PayDate_C[i]);
        PayLeg->CouponRate[i] = PayCouponFixRate[i];
        PayLeg->RangeCoupon[i] = PayCouponFixRate[i + 2 * NPayCashFlow];
    }

    long IdxCurrentPayLeg = 0;
    for (i = 0; i < NPayCashFlow; i++)
    {
        if (PriceDate < PayLeg->PayDate_C[i] && PriceDate >= PayLeg->ForwardStart_C[i])
        {
            IdxCurrentPayLeg = i;

        }
    }
    PayLeg->CurrentIdx = IdxCurrentPayLeg;
    RcvLeg->nUsingCurve = nUsingCurveRcv;
    PayLeg->nUsingCurve = nUsingCurvePay;
    RcvLeg->HolidayCalcFlag = RcvHolidayCalcFlag;
    PayLeg->HolidayCalcFlag = PayHolidayCalcFlag;
    RcvLeg->HolidayCount = RcvHolidayCountAdj;
    PayLeg->HolidayCount = PayHolidayCountAdj;
    RcvLeg->HolidayDays = RcvHolidayAdj;
    PayLeg->HolidayDays = PayHolidayAdj;

    PayLeg->OptionUseFlag = 0;
    PayLeg->NOption = 0;

    double* CorrMatReshaped = (double*)malloc(sizeof(double) * (nSimulateCurve * nSimulateCurve));
    k = 0;
    n = 0;
    for (i = 0; i < N_Curve_Max; i++)
    {
        for (j = 0; j < N_Curve_Max; j++)
        {
            if (isin(i + 1, SimulateCurveIdx, N_Curve_Max) && isin(j + 1, SimulateCurveIdx, N_Curve_Max))
            {
                CorrMatReshaped[n] = Corr[k];
                n = n + 1;
            }
            k += 1;
        }
    }

    double** CorrMatAdj = (double**)malloc(sizeof(double*) * nSimulateCurve);
    for (i = 0; i < nSimulateCurve; i++) CorrMatAdj[i] = CorrMatReshaped + i * nSimulateCurve;

    ////////////////////////////////////////////////////////////
    // 시뮬레이션에 필요한 날짜 Node 결정 : 두 Leg의 ForwardStartDate, ForwardEndDate를 Unique Sort하자.
    ////////////////////////////////////////////////////////////

    long NDays = 0;
    long* AllDays = (long*)malloc(sizeof(long) * (RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption));
    long* AllDaysYYYYMMDD = (long*)malloc(sizeof(long) * (RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption));
    for (i = 0; i < RcvLeg->NCashFlow; i++)
    {
        if (PriceDate <= RcvLeg->ForwardStart_C[i])
        {
            AllDays[2 * i] = DayCountAtoB(PriceDate, RcvLeg->ForwardStart_C[i]);
            AllDaysYYYYMMDD[2 * i] = RcvLeg->ForwardStart_C[i];
        }
        else
        {
            AllDays[2 * i] = 0;
            AllDaysYYYYMMDD[2 * i] = PriceDate;
        }

        if (PriceDate <= RcvLeg->ForwardEnd_C[i])
        {
            AllDays[2 * i + 1] = DayCountAtoB(PriceDate, RcvLeg->ForwardEnd_C[i]);
            AllDaysYYYYMMDD[2 * i + 1] = RcvLeg->ForwardEnd_C[i];
        }
        else
        {
            AllDays[2 * i+1] = 0;
            AllDaysYYYYMMDD[2 * i + 1] = PriceDate;
        }
    }

    for (i = 0; i < PayLeg->NCashFlow; i++)
    {
        if (PriceDate <= PayLeg->ForwardStart_C[i])
        {
            AllDays[RcvLeg->NCashFlow * 2 + 2 * i] = DayCountAtoB(PriceDate, PayLeg->ForwardStart_C[i]);
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + 2 * i] = PayLeg->ForwardStart_C[i];
        }
        else
        {
            AllDays[RcvLeg->NCashFlow * 2 + 2 * i] = 0;
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + 2 * i] = PriceDate;
        }

        if (PriceDate <= PayLeg->ForwardEnd_C[i])
        {
            AllDays[RcvLeg->NCashFlow * 2 + 2 * i + 1] = DayCountAtoB(PriceDate, PayLeg->ForwardEnd_C[i]);
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + 2 * i + 1] = PayLeg->ForwardEnd_C[i];
        }
        else
        {
            AllDays[RcvLeg->NCashFlow * 2 + 2*i + 1] = 0;
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + 2 * i + 1] = PriceDate;
        }
    }

    for (i = 0; i < RcvLeg->NOption; i++)
    {
        if (PriceDate <= RcvLeg->OptionDate[i])
        {
            AllDays[RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + i] = DayCountAtoB(PriceDate, RcvLeg->OptionDate[i]);
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + i] = RcvLeg->OptionDate[i];
        }
        else
        {
            AllDays[RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + i] = 0;
            AllDaysYYYYMMDD[RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + i] = PriceDate;
        }
    }

    bubble_sort_long(AllDays, (RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption), 1);
    bubble_sort_long(AllDaysYYYYMMDD, (RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption), 1);
    long* DaysForSimul;
    long* YYYYMMDDForSimul;

    DaysForSimul = Make_Unique_Array((RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption), AllDays, NDays);
    YYYYMMDDForSimul = Make_Unique_Array((RcvLeg->NCashFlow * 2 + PayLeg->NCashFlow * 2 + RcvLeg->NOption), AllDaysYYYYMMDD, NDays);

    long MaxDaysSimul = 1000;
    long ExcelStartDate, ExcelEndDate , ExcelDate, weekendflag, holiflag, CDate;
    
    if (DailySimulFlag != 0)
    {
        ExcelStartDate = CDateToExcelDate(PriceDate);
        ExcelEndDate = CDateToExcelDate(YYYYMMDDForSimul[NDays - 1]);

        long NDays2 = NDays;
        long* YYYYMMDDForSimul2 = (long*)malloc(sizeof(long) * NDays);
        for (i = 0; i < NDays; i++) YYYYMMDDForSimul2[i] = YYYYMMDDForSimul[i];

        // 할당 해제
        free(DaysForSimul); 
        free(YYYYMMDDForSimul);

        n = 0;
        for (ExcelDate = ExcelStartDate; ExcelDate < ExcelEndDate; ExcelDate++)
        {
            weekendflag = isweekend(ExcelDate);
            CDate = ExcelDateToCDate(ExcelDate);
            if (weekendflag != 1 || isin(CDate, YYYYMMDDForSimul2, NDays2))
            {
                n += 1;
            }
        }
        MaxDaysSimul = n;        
        DaysForSimul = (long*)malloc(sizeof(long) * MaxDaysSimul);
        YYYYMMDDForSimul = (long*)malloc(sizeof(long) * MaxDaysSimul);
        n = 0;
        for (ExcelDate = ExcelStartDate; ExcelDate < ExcelEndDate; ExcelDate++)
        {
            weekendflag = isweekend(ExcelDate);
            CDate = ExcelDateToCDate(ExcelDate);
            if (weekendflag != 1 || isin(CDate, YYYYMMDDForSimul2, NDays2))
            {
                DaysForSimul[n] = ExcelDate - ExcelStartDate;
                YYYYMMDDForSimul[n] = CDate;
                n += 1;
            }
        }
        free(YYYYMMDDForSimul2);
    }
    else
    {
        MaxDaysSimul = NDays;
    }

    //////////////////////////////////
    // Random Number Generate
    //////////////////////////////////

    long seed = 0;
    randnorm(seed);
    double** FixedRandn = random_mvrn(NSimul * MaxDaysSimul, nSimulateCurve, CorrMatAdj);
    double** FixedRandn2;
    double* HW2FRho_adj;
    long* HW2FactorUseFlag = (long*)malloc(sizeof(long) * nSimulateCurve);;
    if (HWFactorFlag > 0)
    {
        HW2FRho_adj = (double*)malloc(sizeof(double) * nSimulateCurve);
        FixedRandn2 = (double**)malloc(sizeof(double*) * NSimul * MaxDaysSimul);
        for (i = 0; i < NSimul * MaxDaysSimul; i++) FixedRandn2[i] = (double*)malloc(sizeof(double) * nSimulateCurve);
        long idum_sim = -1;
        long iy_sim = 0;
        long iv_sim[NTAB];
        long iset_sim = 0;
        double gset_sim = 0.0;
        double tempcorrmat[4] = { 0.0,0.0,0.0,0.0 };
        double tempresultcorrmat[4] = { 0.0,0.0,0.0,0.0 };
        k = 0;
        for (i = 0; i < N_Curve_Max; i++)
        {
            if (isin(i + 1, SimulateCurveIdx, nSimulateCurve))
            {
                tempcorrmat[0] = 1.0;
                tempcorrmat[1] = HWrho2F[i];
                tempcorrmat[2] = HWrho2F[i];
                tempcorrmat[3] = 1.0;
                Cholesky_Decomposition(tempcorrmat, tempresultcorrmat, 2);
                HW2FRho_adj[k] = tempresultcorrmat[3];

                n_null = 0;
                for (n = 0; n < NHWVolCount[i]; n++)
                {
                    // Vol2 값이 모두 0이면 1Factor Model로 시뮬레이션
                    if (HWVolMatrix2[i][n] < 0.00001 && HWVolMatrix2[i][n] > -0.00001) n_null += 1;                    
                }

                if (n_null == NHWVolCount[i])
                {
                    HW2FactorUseFlag[k] = 0;
                    HWrho2F[k] = 0.01;
                    HWKappaArray2[k] = 0.01;
                }
                else HW2FactorUseFlag[k] = 1;

                k = k + 1;
            }
        }

        for (i = 0; i < NSimul * MaxDaysSimul; i++)
        {
            for (j = 0; j < nSimulateCurve; j++)
            {
                if (HW2FactorUseFlag[j] == 1)
                {
                    FixedRandn2[i][j] = HWrho2F[j] * FixedRandn[i][j] + HW2FRho_adj[j] * randn(1, idum_sim, iset_sim, gset_sim, iy_sim, iv_sim);
                }
                else
                {
                    FixedRandn2[i][j] = 0.;
                }
            }
        }
    }
    else
    {
        FixedRandn2 = FixedRandn;
        HW2FRho_adj = HWKappaArray;
    }

    /////////////////
    // Rate History
    /////////////////

    long** RateHistoryDateMatrixRcv = (long**)malloc(sizeof(long*) * nUsingCurveRcv);
    double** RateHistoryMatrixRcv = (double**)malloc(sizeof(double*) * nUsingCurveRcv);
    k = 0;
    n = 0;
    for (i = 0; i < nUsingCurveRcv; i++)
    {
        RateHistoryDateMatrixRcv[i] = (long*)malloc(sizeof(long) * max(1,NDayHistRcv[i]));
        RateHistoryMatrixRcv[i] = (double*)malloc(sizeof(double) * max(1, NDayHistRcv[i]));
        for (j = 0; j < NDayHistRcv[i]; j++)
        {
            RateHistoryDateMatrixRcv[i][j] = RateHistDateRcv[k];
            RateHistoryMatrixRcv[i][j] = RateHistRcv[k];
            k += 1;
        }
        n = n + NDayHistRcv[i];
    }

    long** RateHistoryDateMatrixPay = (long**)malloc(sizeof(long*) * nUsingCurvePay);
    double** RateHistoryMatrixPay = (double**)malloc(sizeof(double*) * nUsingCurvePay);
    k = 0;
    n = 0;
    for (i = 0; i < nUsingCurvePay; i++)
    {
        RateHistoryDateMatrixPay[i] = (long*)malloc(sizeof(long) * max(1, NDayHistPay[i]));
        RateHistoryMatrixPay[i] = (double*)malloc(sizeof(double) * max(1, NDayHistPay[i]));
        for (j = 0; j < NDayHistPay[i]; j++)
        {
            RateHistoryDateMatrixPay[i][j] = RateHistDatePay[k];
            RateHistoryMatrixPay[i][j] = RateHistPay[k];
            k += 1;
        }
        n = n + NDayHistPay[i];
    }

    RcvLeg->NDayHistory = NDayHistRcv;
    PayLeg->NDayHistory = NDayHistPay;
    RcvLeg->RateHistoryDateMatrix = RateHistoryDateMatrixRcv;
    PayLeg->RateHistoryDateMatrix = RateHistoryDateMatrixPay;
    RcvLeg->RateHistoryMatrix = RateHistoryMatrixRcv;
    PayLeg->RateHistoryMatrix = RateHistoryMatrixPay;

    //////////////////////
    // 시뮬레이션 정보  //
    //////////////////////

    SIMUL_INFO* Simul = new SIMUL_INFO;
    Simul->NSimul = NSimul;
    Simul->DailySimulFlag = DailySimulFlag;
    Simul->NDays = MaxDaysSimul;
    Simul->NAsset = nSimulateCurve;
    Simul->DaysForSimul = DaysForSimul;
    Simul->YYYYMMDDForSimul = YYYYMMDDForSimul;
    Simul->dt_Array = (double*)malloc(sizeof(double) * Simul->NDays);
    Simul->T_Array = (double*)malloc(sizeof(double) * Simul->NDays);
    for (i = 0; i < Simul->NDays; i++)
    {
        if (i == 0) Simul->dt_Array[0] = ((double)DaysForSimul[0]) / 365.0;
        else Simul->dt_Array[i] = ((double)(DaysForSimul[i] - DaysForSimul[i - 1])) / 365.0;

        Simul->T_Array[i] = ((double)DaysForSimul[i]) / 365.0;
    }

    Simul->FixedRandn = FixedRandn;
    Simul->FixedRandn2 = FixedRandn2;
    
    Simul->NHWVol = (long*)malloc(sizeof(long) * Simul->NAsset);
    Simul->HWKappa = (double*)malloc(sizeof(double) * Simul->NAsset);
    Simul->HWKappa2 = (double*)malloc(sizeof(double) * Simul->NAsset);

    Simul->HWVolTerm = (double**)malloc(sizeof(double*) * Simul->NAsset);
    Simul->HWVol = (double**)malloc(sizeof(double*) * Simul->NAsset);
    Simul->HWVol2 = (double**)malloc(sizeof(double*) * Simul->NAsset);
    
    Simul->NRateTerm = (long*)malloc(sizeof(long) * Simul->NAsset);
    Simul->RateTerm = (double**)malloc(sizeof(double*) * Simul->NAsset);
    Simul->Rate = (double**)malloc(sizeof(double*) * Simul->NAsset);
    Simul->HWQuantoFlag = (double*)malloc(sizeof(double) * Simul->NAsset);
    Simul->HWQuantoRho = (double*)malloc(sizeof(double) * Simul->NAsset);
    Simul->HWQuantoVol = (double*)malloc(sizeof(double) * Simul->NAsset);
    Simul->HW2FRho = (double*)malloc(sizeof(double) * Simul->NAsset);
    Simul->SimulCurveIdx = SimulateCurveIdx;
    Simul->HWFactorFlag = HWFactorFlag;
    
    k = 0;
    for (i = 0; i < N_Curve_Max; i++)
    {
        if (isin(i + 1, SimulateCurveIdx, nSimulateCurve))
        {
            Simul->NHWVol[k] = NHWVolCount[i];
            Simul->HWVolTerm[k] = HWVolTermMatrix[i];
            Simul->HWVol[k] = HWVolMatrix[i];
            Simul->HWVol2[k] = HWVolMatrix2[i];
            Simul->HWKappa[k] = HWKappaArray[i];
            Simul->HWKappa2[k] = HWKappaArray2[i];
            Simul->NRateTerm[k] = NZeroRate[i];
            Simul->RateTerm[k] = ZeroRateTermMatrix[i];
            Simul->Rate[k] = ZeroRateMatrix[i];
            Simul->HWQuantoFlag[k] = HWQuantoFlag[i];
            Simul->HWQuantoRho[k] = HWQuantoRho[i];
            Simul->HWQuantoVol[k] = HWQuantoFXVol[i];
            Simul->HW2FRho[k] = HWrho2F[i];
            k = k + 1;
        }
    }

    ResultCode = IRStructuredSwap(PriceDate, NAFlag, Notional, RcvLeg, PayLeg, Simul, GreekFlag, ResultPrice, ResultRcv, ResultPay);

    if (GreekFlag == 1)
    {
        long idxtemp = 0;
        long idxtermup = 0;
        long kk = 0;
        long h = 0;
        long NTotalZeroRate = 0;
        long PointerZero[5] = { 0,0,0,0,0 };
        long idxstart, idxend;
        long UselessTermFlag = 0;
        double RcvValue, PayValue;
        double PV01Rcv, PV01Pay;
        double TempResultPrice[5] = { 0.0, 0.0,0.0,0.0 };
        double* TempResultRcv = (double*)malloc(sizeof(double) * (NRcvCashFlow * 7));
        double* TempResultPay = (double*)malloc(sizeof(double) * (NPayCashFlow * 7));
        double* KeyPV01Rcv;
        double* KeyPV01Pay;
        RcvValue = ResultPrice[0];
        PayValue = ResultPrice[1];
        for (i = 0; i < N_Curve_Max; i++)
        {
            NTotalZeroRate += NZeroRate[i];
            PointerZero[i + 1] = NTotalZeroRate;
        }

        double* ZeroRateParallelUp = (double*)malloc(sizeof(double) * NTotalZeroRate);
        double* ZeroRateKeyUp = (double*)malloc(sizeof(double) * NTotalZeroRate);
        double** ZeroRateMatrixParralelUp = (double**)malloc(sizeof(double*) * N_Curve_Max);
        n = 0;
        for (i = 0; i < N_Curve_Max; i++)
        {
            ZeroRateMatrixParralelUp[i] = ZeroRateParallelUp + n;
            n = n + NZeroRate[i];
        }

        SIMUL_INFO* Simul_ForGreek = new SIMUL_INFO;
        Simul_ForGreek->YYYYMMDDForSimul = YYYYMMDDForSimul;
        Simul_ForGreek->NSimul = Simul->NSimul;
        Simul_ForGreek->DailySimulFlag = Simul->DailySimulFlag;
        Simul_ForGreek->NDays = Simul->NDays;
        Simul_ForGreek->NAsset = Simul->NAsset;
        Simul_ForGreek->DaysForSimul = Simul->DaysForSimul;

        Simul_ForGreek->dt_Array = Simul->dt_Array;
        Simul_ForGreek->T_Array = Simul->T_Array;
        Simul_ForGreek->FixedRandn = FixedRandn;
        Simul_ForGreek->FixedRandn2 = FixedRandn2;
        Simul_ForGreek->NHWVol = Simul->NHWVol;
        Simul_ForGreek->HWKappa = Simul->HWKappa;
        Simul_ForGreek->HWKappa2 = Simul->HWKappa2;

        Simul_ForGreek->HWVolTerm = Simul->HWVolTerm;
        Simul_ForGreek->HWVol = Simul->HWVol;
        Simul_ForGreek->HWVol2 = Simul->HWVol2;

        Simul_ForGreek->NRateTerm = Simul->NRateTerm;
        Simul_ForGreek->RateTerm = Simul->RateTerm;
        Simul_ForGreek->Rate = (double**)malloc(sizeof(double*) * Simul->NAsset);
        Simul_ForGreek->HWQuantoFlag = Simul->HWQuantoFlag;
        Simul_ForGreek->HWQuantoRho = Simul->HWQuantoRho;
        Simul_ForGreek->HWQuantoVol = Simul->HWQuantoVol;
        Simul_ForGreek->SimulCurveIdx = SimulateCurveIdx;
        Simul_ForGreek->HWFactorFlag = Simul->HWFactorFlag;

        k = 0;
        for (i = 1; i < N_Curve_Max + 1; i++)
        {
            if (isin(i, Simul->SimulCurveIdx, Simul->NAsset))
            {
                idxstart = PointerZero[i - 1];
                idxend = PointerZero[i];

                for (j = 0; j < NTotalZeroRate; j++)
                {
                    if (j >= idxstart && j < idxend) ZeroRateParallelUp[j] = ZeroRate[j] + 0.0001;
                    else ZeroRateParallelUp[j] = ZeroRate[j];
                }


                kk = 0;
                for (idxtemp = 0; idxtemp < N_Curve_Max; idxtemp++)
                {
                    if (isin(idxtemp + 1, SimulateCurveIdx, nSimulateCurve))
                    {
                        Simul_ForGreek->Rate[kk] = ZeroRateMatrixParralelUp[idxtemp];
                        kk = kk + 1;
                    }
                }

                ResultCode = IRStructuredSwap(PriceDate, NAFlag, Notional, RcvLeg, PayLeg, Simul_ForGreek, GreekFlag, TempResultPrice, TempResultRcv, TempResultPay);

                PV01Rcv = TempResultPrice[0] - RcvValue;
                PV01Pay = TempResultPrice[1] - PayValue;
                ResultPV01[i - 1] = PV01Rcv;
                ResultPV01[i - 1 + 4] = PV01Pay;
                k = k + 1;
            }
        }

        k = 0;
        for (i = 1; i < N_Curve_Max + 1; i++)
        {
            KeyPV01Rcv = ResultKeyPV01 + PointerZero[i - 1];
            KeyPV01Pay = ResultKeyPV01 + NTotalZeroRate + PointerZero[i - 1];
            if (isin(i, Simul->SimulCurveIdx, Simul->NAsset))
            {
                idxstart = PointerZero[i - 1];
                idxend = PointerZero[i];
                for (idxtermup = idxstart; idxtermup < idxend; idxtermup++)
                {
                    for (j = 0; j < NTotalZeroRate; j++)
                    {
                        if (j == idxtermup) ZeroRateParallelUp[j] = ZeroRate[j] + 0.0001;
                        else ZeroRateParallelUp[j] = ZeroRate[j];
                    }

                    kk = 0;
                    for (idxtemp = 0; idxtemp < N_Curve_Max; idxtemp++)
                    {
                        if (isin(idxtemp + 1, SimulateCurveIdx, nSimulateCurve))
                        {
                            Simul_ForGreek->Rate[kk] = ZeroRateMatrixParralelUp[idxtemp];
                            kk = kk + 1;
                        }
                    }

                    UselessTermFlag = 0;
                    if (NZeroRate[i] > 2)
                    {
                        ////////////////////////////////////////////////////
                        // 스왑 만기보다 너무 Term이 길면 노트 가격 영향 없다
                        ////////////////////////////////////////////////////
                        if (ZeroTerm[idxtermup - 1] > Simul_ForGreek->T_Array[Simul_ForGreek->NDays - 1]) UselessTermFlag = 1;
                    }

                    if (UselessTermFlag == 1)
                    {
                        KeyPV01Rcv[idxtermup - idxstart] = 0.0;
                        KeyPV01Pay[idxtermup - idxstart] = 0.0;
                    }
                    else
                    {
                        ResultCode = IRStructuredSwap(PriceDate, NAFlag, Notional, RcvLeg, PayLeg, Simul_ForGreek, GreekFlag, TempResultPrice, TempResultRcv, TempResultPay);

                        PV01Rcv = TempResultPrice[0] - RcvValue;
                        PV01Pay = TempResultPrice[1] - PayValue;
                        KeyPV01Rcv[idxtermup - idxstart] = PV01Rcv;
                        KeyPV01Pay[idxtermup - idxstart] = PV01Pay;
                    }
                    k = k + 1;
                }
            }
        }

        free(TempResultRcv);
        free(TempResultPay);
        free(ZeroRateParallelUp);
        free(ZeroRateKeyUp);
        free(ZeroRateMatrixParralelUp);
        free(Simul_ForGreek->Rate);
        delete(Simul_ForGreek);
    }


    //////////////////
    // 할당 해제
    //////////////////
    free(FloatingFlagRcv);
    free(FloatingFlagPay);

    free(HWVolTermMatrix);
    free(HWVolMatrix);
    free(HWVolMatrix2);
    free(ZeroRateTermMatrix);
    free(ZeroRateMatrix);
    
    for (i = 0; i < RcvFlag[0]; i++) free(RcvHolidayAdj[i]);
    for (i = 0; i < PayFlag[0]; i++) free(PayHolidayAdj[i]);
    free(RcvHolidayAdj);
    free(PayHolidayAdj);
    free(RcvHolidayCountAdj);
    free(PayHolidayCountAdj);

    free(OptionDate);
    free(OptionStrikeRate);
    for (i = 0; i < RcvFlag[0]; i++) free(RangeUp[i]);
    for (i = 0; i < RcvFlag[0]; i++) free(RangeDn[i]);
    free(RangeUp);
    free(RangeDn);

    free(RcvPayCurveNumber);
    free(SimulateCurveIdx);

    // RcvLeg 할당해제
    free(RcvLeg->ForwardStart_C);
    free(RcvLeg->ForwardEnd_C);
    free(RcvLeg->DaysForwardStart);
    free(RcvLeg->DaysForwardEnd);
    free(RcvLeg->FractionStart_C);
    free(RcvLeg->FractionEnd_C);
    free(RcvLeg->PayDate_C);
    free(RcvLeg->DaysPayDate_C);
    free(RcvLeg->CouponRate);
    free(RcvLeg->RangeCoupon);

    delete(RcvLeg->Reference_Inform);
    delete(RcvLeg);

    // PayLeg 할당해제
    free(PayLeg->ForwardStart_C);
    free(PayLeg->ForwardEnd_C);
    free(PayLeg->DaysForwardStart);
    free(PayLeg->DaysForwardEnd);
    free(PayLeg->FractionStart_C);
    free(PayLeg->FractionEnd_C);
    free(PayLeg->PayDate_C);
    free(PayLeg->DaysPayDate_C);
    free(PayLeg->CouponRate);
    free(PayLeg->RangeCoupon);

    delete(PayLeg->Reference_Inform);
    delete(PayLeg);

    free(CorrMatReshaped);
    free(CorrMatAdj);
    free(AllDays);
    free(AllDaysYYYYMMDD);
    free(DaysForSimul);
    free(YYYYMMDDForSimul);

    free(HW2FactorUseFlag);
    if (HWFactorFlag > 0)
    {
        free(HW2FRho_adj);
        for (i = 0; i < NSimul * MaxDaysSimul; i++) free(FixedRandn2[i]);
        free(FixedRandn2);       
    }
    for (i = 0; i < NSimul * MaxDaysSimul; i++) free(FixedRandn[i]);
    free(FixedRandn);

    for (i = 0; i < nUsingCurveRcv; i++)
    {
        free(RateHistoryDateMatrixRcv[i]);
        free(RateHistoryMatrixRcv[i]);
    }
    free(RateHistoryDateMatrixRcv);
    free(RateHistoryMatrixRcv);

    for (i = 0; i < nUsingCurvePay; i++)
    {
        free(RateHistoryDateMatrixPay[i]);
        free(RateHistoryMatrixPay[i]);
    }
    free(RateHistoryDateMatrixPay);
    free(RateHistoryMatrixPay);

    free(Simul->dt_Array);
    free(Simul->T_Array);
    free(Simul->NHWVol);
    free(Simul->HWKappa);
    free(Simul->HWKappa2);
    

    free(Simul->HWVolTerm);
    free(Simul->HWVol);
    free(Simul->HWVol2);
    
    free(Simul->NRateTerm);
    free(Simul->RateTerm);
    free(Simul->Rate);
    free(Simul->HWQuantoFlag);
    free(Simul->HWQuantoRho);
    free(Simul->HWQuantoVol);
    free(Simul->HW2FRho);
    delete(Simul);
    //_CrtDumpMemoryLeaks();
    return 1;
}

DLLEXPORT(long) Generate_CpnDate_IRStructuredSwapModule_Using_Holiday(long EffectiveDate, long MaturityDate, long AnnCpnOneYear, long NHoliday, long* Holidays, long CpnNumber0Array1Flag, long* NumberOfCpnReturn, long* StartDateArray, long* EndDateArray, long* CpnDateArray)
{
    long i;
    long j;
    long n;

    long ResultCode = 1;
    for (i = 0; i < NHoliday; i++) if (Holidays[i] < 19000101) Holidays[i] = ExcelDateToCDate(Holidays[i]);

    if (EffectiveDate < 19000101) EffectiveDate = ExcelDateToCDate(EffectiveDate);
    if (MaturityDate < 19000101) MaturityDate = ExcelDateToCDate(MaturityDate);

    long RealPayDate = MaturityDate + 0;
    long EffectiveYYYYMM = EffectiveDate / 100;
    long EffectiveDD = EffectiveDate - EffectiveYYYYMM * 100;

    long MaturityYYYYMM = MaturityDate / 100;
    long MaturityDD = MaturityDate - MaturityYYYYMM * 100;
    // 만약 EndDate가 26~31일이고 PayDate가 1일, 2일, 3일, 4일 등
    if (EffectiveDD > 25 && MaturityDD < 5)
    {
        NBusinessCountFromEndToPay(EffectiveDate, RealPayDate, Holidays, NHoliday, 1, &MaturityDate);
        MaturityDate = ((long)(MaturityDate/100))*100 + EffectiveDD;
    }
    else
    {
        MaturityDate = MaturityYYYYMM * 100 + EffectiveDD;
    }

    long TempDate = EffectiveDate;
    long NCpnDate;
    long* CpnDate = Generate_CpnDate_With_Holiday(EffectiveDate, MaturityDate, AnnCpnOneYear, NCpnDate, TempDate, NHoliday, Holidays);

    long MaturityExcel, Mod7;
    MaturityExcel = CDateToExcelDate(MaturityDate);
    Mod7 = MaturityExcel % 7;
    // 실질만기 계산
    if ((Mod7 == 0 || Mod7 == 1) || (isin(MaturityDate, Holidays, NHoliday)))
    {
        for (i = 1; i < 7; i++)
        {
            MaturityExcel += 1;
            MaturityDate = ExcelDateToCDate(MaturityExcel);
            Mod7 = MaturityExcel % 7;
            if ((Mod7 != 0 && Mod7 != 1) && (isin(MaturityDate, Holidays, NHoliday) == 0))
            {
                break;
            }
        }
    }

    long EndToPay = 0;
    long Date, ExlDate;
    if (MaturityDate < RealPayDate)
    {
        // End Date 부터 Pay Date 까지 Business Day Count
        for (i = 1; i < 10; i++)
        {
            Date = DayPlus(MaturityDate, i);
            ExlDate = CDateToExcelDate(Date);
            Mod7 = ExlDate % 7;
            if ((Mod7 != 0 && Mod7 != 1) && (isin(Date, Holidays, NHoliday) == 0))
            {
                EndToPay += 1;
            }

            if (Date >= RealPayDate) break;
        }
    }

    if (CpnNumber0Array1Flag == 0)
    {
        NumberOfCpnReturn[0] = NCpnDate;
    }
    else
    {
        for (i = 0; i < NCpnDate; i++)
        {
            if (i == 0) StartDateArray[i] = EffectiveDate;
            else StartDateArray[i] = CpnDate[i - 1];
            EndDateArray[i] = CpnDate[i];

            if (EndToPay <= 0)
            {
                CpnDateArray[i] = CpnDate[i];
            }
            else
            {
                ExlDate = CDateToExcelDate(CpnDate[i]);
                Mod7 = ExlDate % 7;
                n = 0;
                for (j = 1; j < 10; j++)
                {
                    Date = DayPlus(CpnDate[i], j);
                    ExlDate = CDateToExcelDate(Date);
                    Mod7 = ExlDate % 7;
                    if ((Mod7 != 0 && Mod7 != 1) && (isin(Date, Holidays, NHoliday) == 0))
                    {
                        n += 1;
                    }
                    if (n >= EndToPay) break;
                }
                CpnDateArray[i] = Date;

            }
        }
    }
    free(CpnDate);
    return ResultCode;
}