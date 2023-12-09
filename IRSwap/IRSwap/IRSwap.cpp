#include <stdio.h>
#include <math.h>

#include "CalcDate.h"
#include "Structure.h"
#include "Util.h"
#include "GetTextDump.h"
//#include <crtdbg.h>
#ifndef DLLEXPORT(A)
#ifdef WIN32
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#elif _WIN64
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#elif __linux__
#define DLLEXPORT(A) extern "C" A
#elif __hpux
#define DLLEXPORT(A) extern "C" A
#elif __unix__
#define DLLEXPORT(A) extern "C" A
#else
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#endif
#endif 

long sumation(long* array, long narray)
{
    long i;
    long s = 0;
    for (i = 0; i < narray; i++)
    {
        s += array[i];
    }
    return s;
}

double sumation(double* array, long narray)
{
    long i;
    double s = 0;
    for (i = 0; i < narray; i++)
    {
        s += array[i];
    }
    return s;
}

long isin(long x, long* array, long narray)
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

long isinfindindex(long x, long* array, long narray)
{
    long i;
    for (i = 0; i < narray; i++)
    {
        if (x == array[i])
        {
            return i;
        }
    }
    return -1;
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

double Continuous_ForwardRate(curveinfo& Curve, double T0, double T1)
{
    double r0, r1;
    double Result;
    if (T0 != T1)
    {
        r0 = Curve.Interpolated_Rate(T0);
        r1 = Curve.Interpolated_Rate(T1);
        Result = (r1 * T1 - r0 * T0) / (T1 - T0);
    }
    else
    {
        T1 = T0 + 1.0 / 365;
        r0 = Curve.Interpolated_Rate(T0);
        r1 = Curve.Interpolated_Rate(T1);
        Result = (r1 * T1 - r0 * T0) / (T1 - T0);
    }
    return Result;
}

long NPaymentSwap(double T_OptionMaturity, double T_SwapMaturity, double PayFreqOfMonth)
{
    double dT = (T_SwapMaturity - T_OptionMaturity + 0.00001);
    double Num_AnnPayment = 12.0 / PayFreqOfMonth;
    long N;
    N = (long)(dT * Num_AnnPayment + 0.5);
    return N;
}

long MappingPaymentDates(double T_SwapMaturity, double FreqMonth, long* TempDatesArray, long NDates)
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

long US_Holiday_SaturSunday_Check(long HolidayYYYYMMDD)
{
    // US Holiday를 넣으면 토, 일 이면 대체공휴일을 리턴하고 아니면 그대로 리턴
    long HolidayExcelType = CDateToExcelDate(HolidayYYYYMMDD);
    long MOD7 = HolidayExcelType % 7;

    long SaturSundayFlag;

    if (MOD7 == 0) SaturSundayFlag = 1;
    else if (MOD7 == 1) SaturSundayFlag = 2;
    else SaturSundayFlag = 0;

    if (SaturSundayFlag == 0)
    {
        // 토, 일 둘다 아닐 경우
        return HolidayYYYYMMDD;
    }
    else if (SaturSundayFlag == 1)
    {
        // 토요일일 경우 금요일이 대체공휴일
        return ExcelDateToCDate(HolidayExcelType - 1);
    }
    else
    {
        // 일요일일 경우 월요일이 대체공휴일
        return ExcelDateToCDate(HolidayExcelType + 1);
    }
}

long* Generate_CpnDate(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate)
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
    long CpnDateExcel;
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

long* Generate_CpnDate_Holiday(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
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
            if ((MOD7 == 1 || MOD7 == 0) || isin(CpnDate, HolidayYYYYMMDD, NHoliday)) SaturSundayFlag = 1;
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
                    if ((MOD7 != 1 && MOD7 != 0) && !isin(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
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

DLLEXPORT(long) Number_Coupon(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDateExcelType,        // 평가일
    long SwapMatExcelType,          // 스왑 만기
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* HolidayExcelType          // 공휴일
)
{
    long i;
    long PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateExcelType);          // 평가일
    long SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMatExcelType);             // 스왑 만기
    
    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2) ProductType = 1;
    if (ProductType == 0) return 1;

    // 에러처리
    if (PriceDateYYYYMMDD <= 19000101 || PriceDateYYYYMMDD >= 999990101)  return -1;
    if (SwapMat_YYYYMMDD <= 19000101 || SwapMat_YYYYMMDD >= 999990101) return -1;
    if (AnnCpnOneYear > 6) return -1;

    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
    for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayExcelType[i]);
    long HolidayError = 0;
    if (HolidayUseFlag > 0)
    {
        for (i = 0; i < NHoliday; i++)
        {
            if (HolidayYYYYMMDD[i] > 999991231 || HolidayYYYYMMDD[i] < 19000101)
            {
                HolidayError = 1;
                break;
            }
        }
    }
    if (HolidayError == 1)
    {
        free(HolidayYYYYMMDD);
        return -1;
    }

    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;
    
    long n;
    long TempYYYYMMDD= PriceDateYYYYMMDD;
    long TempYYYY=0;
    long TempMM=0;
    long ncpn = 0;
    long* CpnDate;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62)
    {
        // 2개월 미만의 경우 쿠폰 한번지급으로 고정
        free(HolidayYYYYMMDD);
        return 1;
    }
    else if(SwapMatYYYY - PriceYYYY <= 1)
    {
        // 1년 미만 만기의 경우 만기까지 몇개월 남았는지 카운트
        n = 0;
        for (i = 0; i < 24; i++)
        {
            TempYYYYMMDD = EDate_Cpp(PriceDateYYYYMMDD, i + 1);
            TempYYYY = (long)TempYYYYMMDD / 10000;
            TempMM = (long)(TempYYYYMMDD - TempYYYY * 10000) / 100;
            n = i + 1;
            if (TempYYYY == SwapMatYYYY && TempMM == SwapMatMM)
            {
                break;
            }
        }

        if (n < 6)
        {
            // 만기까지 6개월 미만으로 남았으면 쿠폰 1번 지급 끝
            // (1년에 4번을 초과하여 지급하는 경우는 없다고 가정)
            free(HolidayYYYYMMDD);
            return 1;
        }
        else
        {
            if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
            else CpnDate = Generate_CpnDate(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

            free(CpnDate);
            free(HolidayYYYYMMDD);
            return ncpn;
        }
    }
    else
    {
        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        free(CpnDate);
        free(HolidayYYYYMMDD);
        return ncpn;
    }
}

DLLEXPORT(long) ResultCpnMapping(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDateExcelType,        // 평가일
    long StartDateExcelType,        // 시작일
    long SwapMatExcelType,          // 스왑 만기
    long NBDayFromEndDate,          // N영업일 뒤 지급
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* HolidayExcelType,         // 공휴일
    long NumberCoupon,
    long* ResultForwardStart,
    long* ResultForwardEnd,
    long* ResultPayDate
)
{
    long i;
    long j;
    long n;
    long PayDateExcelType, PayDateYYYYMMDD, MOD7;
    long PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateExcelType);          // 평가일
    long StartDateYYYYMMDD = ExcelDateToCDate(StartDateExcelType);          // 평가일
    long SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMatExcelType);             // 스왑 만기
    long ncpn;
    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1,NHoliday));
    for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayExcelType[i]);
    

    if (NumberCoupon < 0) return -1;
    if (NumberCoupon <= 1)
    {
        ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
        ResultForwardEnd[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
        n = 0;
        if (NBDayFromEndDate == 0)
        {
            ResultPayDate[0] = ResultForwardEnd[0];
        }
        else
        {
            for (i = 1; i < 10; i++)
            {
                PayDateYYYYMMDD = DayPlus(SwapMat_YYYYMMDD, i);
                PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                MOD7 = PayDateExcelType % 7;
                if ((MOD7 != 1 && MOD7 != 0 ) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                {
                    // 영업일이면 n+=1
                    n += 1;
                }

                if (n == NBDayFromEndDate)
                {
                    ResultPayDate[0] = PayDateExcelType;
                    break;
                }
            }
        }
    }
    else
    {
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;

        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        for (i = 0; i < min(NumberCoupon,ncpn); i++)
        {
            if (i == 0)
            {
                ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                TempDateExcelType = CDateToExcelDate(CpnDate[0]);
                ResultForwardEnd[0] = TempDateExcelType;
            }
            else
            {
                ResultForwardStart[i] = CDateToExcelDate(CpnDate[i - 1]);
                TempDateExcelType = CDateToExcelDate(CpnDate[i]);
                ResultForwardEnd[i] = TempDateExcelType;
            }

            if (NBDayFromEndDate == 0)
            {
                ResultPayDate[i] = ResultForwardEnd[i];
            }
            else
            {
                n = 0;            
                for (j = 1; j < 10; j++)
                {
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j);
                    PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                    MOD7 = PayDateExcelType % 7;
                    if ((MOD7 != 1 && MOD7 != 0 ) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        ResultPayDate[i] = PayDateExcelType;
                        break;
                    }
                }
            }
        }
        if (CpnDate) free(CpnDate);
    }
    if (HolidayYYYYMMDD) free(HolidayYYYYMMDD);
    return 1;
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

double Calc_Forward_Rate_Daily(
    double* Term,
    double* Rate,
    long LengthArray,
    double T1,
    double denominator,
    long* TimePos
)
{
    long i;
    long startidx = *TimePos + 0;
    double dt = 0.00273972602739726;
    double T2 = T1 + dt;
    double r1, r2;
    double DF1, DF2, FRate;

    if (T1 <= Term[0]) r1 = Rate[0];
    else if (T1 >= Term[LengthArray - 1]) r1 = Rate[LengthArray - 1];
    else
    {
        for (i = max(1, startidx); i < LengthArray; i++)
        {
            if (T1 < Term[i])
            {
                *TimePos = i - 1;
                r1 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T1 - Term[i - 1]) + Rate[i - 1];
                break;
            }
        }
    }

    if (T2 <= Term[0]) r2 = Rate[0];
    else if (T2 >= Term[LengthArray - 1]) r2 = Rate[LengthArray - 1];
    else
    {
        for (i = max(1, startidx); i < LengthArray; i++)
        {
            if (T2 < Term[i])
            {
                r2 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T2 - Term[i - 1]) + Rate[i - 1];
                break;
            }
        }
    }

    DF1 = exp(-r1 * T1);
    DF2 = exp(-r2 * T2);
    FRate = denominator * (DF1 / DF2 - 1.0);
    return FRate;
}

double Calc_Forward_Rate_Daily(
    double* Term,
    double* Rate,
    long LengthArray,
    double T1,
    double denominator,
    long* TimePos,
    long NHoliday
)
{
    long i;
    long startidx = *TimePos + 0;
    double dt = 0.00273972602739726;
    double T2 = T1 + ((double)(NHoliday + 1)) * dt;
    double r1, r2;
    double DeltaT = T2 - T1;
    double DF1, DF2, FRate;

    if (T1 <= Term[0]) r1 = Rate[0];
    else if (T1 >= Term[LengthArray - 1]) r1 = Rate[LengthArray - 1];
    else
    {
        for (i = max(1, startidx); i < LengthArray; i++)
        {
            if (T1 < Term[i])
            {
                *TimePos = i - 1;
                r1 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T1 - Term[i - 1]) + Rate[i - 1];
                break;
            }
        }
    }

    if (T2 <= Term[0]) r2 = Rate[0];
    else if (T2 >= Term[LengthArray - 1]) r2 = Rate[LengthArray - 1];
    else
    {
        for (i = max(1, startidx); i < LengthArray; i++)
        {
            if (T2 < Term[i])
            {
                r2 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T2 - Term[i - 1]) + Rate[i - 1];
                break;
            }
        }
    }

    DF1 = exp(-r1 * T1);
    DF2 = exp(-r2 * T2);
    FRate = denominator/(double)(NHoliday+1) * (DF1 / DF2 - 1.0);
    return FRate;
}

/////////////////////////////
// Forward Swap Rate 계산 ///
/////////////////////////////
double FSR(
    double* Term,            // 기간구조 Term Array
    double* Rate,            // 기간구조 Rate Array
    long NTerm,                // 기간구조 Term 개수
    double T_Option,        // Forward Swap 시작일
    double Tenor,            // 스왑 만기
    double FreqMonth        // Month환산 스왑 Frequency
)
{
    long i;
    double Swap_Rate;

    long ndates = NPaymentSwap(T_Option, T_Option + Tenor, FreqMonth);
    long* dates = (long*)malloc(sizeof(long) * (ndates));
    ndates = MappingPaymentDates(T_Option + Tenor, FreqMonth, dates, ndates);

    double* P0T = (double*)malloc(sizeof(double) * (ndates + 1));
    P0T[0] = Calc_Discount_Factor(Term, Rate, NTerm, T_Option); // 옵션만기시점
    for (i = 1; i < ndates + 1; i++)
    {
        P0T[i] = Calc_Discount_Factor(Term, Rate, NTerm, (double)dates[i - 1] / 365.0);
    }

    double a, b, dt;
    a = P0T[0] - P0T[ndates];
    b = 0.0;
    for (i = 0; i < ndates; i++)
    {
        if (i == 0) dt = (double)dates[0] / 365.0 - T_Option;
        else dt = ((double)(dates[i] - dates[i - 1])) / 365.0;
        b += dt * P0T[i + 1];
    }
    Swap_Rate = a / b;


    if (dates) free(dates);
    if (P0T) free(P0T);
    return Swap_Rate;
}

typedef struct schd_info {
    long PriceDate_C;            // PricingDate CType

    long ReferenceType;            // Reference Rate type
    long FixedFlotype;            // Fix or Flo Flag 0:Fix 1: Flo
    long DayCount;                // DayCountConvention 0:365 1:365
    double NotionalAmount;        // Notional Amount
    long NAFlag;                // Notional 지급여부

    long RefSwapFlag;            // 레퍼런스금리가 스왑금리인지여부
    long NSwapPayAnnual;        // 레퍼런스금리가 스왑금리라면 연 쿠폰지급 수
    double RefSwapMaturity;        // 레퍼런스 금리가 스왑금리라면 만기

    long NCF;                    // 현금흐름개수
    long* ForwardStart_C;        // 금리추정시작일
    long* ForwardEnd_C;            // 금리추정종료일
    long* StartDate_C;            // Fraction 시작일(기산일)
    long* EndDate_C;            // Fraction 종료일(기말일)
    long* PayDate_C;            // 지급일
    long NotionalPayDate_C;        // 액면금액 지급일
    long* Days_ForwardStart;    // 평가일 to 추정시작일
    long* Days_ForwardEnd;        // 평가일 to 추정종료일
    long* Days_StartDate;        // 평가일 to 기산일
    long* Days_EndDate;            // 평가일 to 기말일
    long* Days_PayDate;            // 평가일 to 지급일

    long HolidayFlag_Ref;        // 기초금리 Holiday Calc Flag
    long NHolidays_Ref;            // 기초금리 Holiday 개수
    long* Days_Holidays_Ref;    // 기초금리 평가일 to Holiday

    double* FixedRefRate;        // 과거 확정금리 데이터
    double* Slope;                // 기초금리에 대한 페이오프 기울기
    double* CPN;                // 쿠폰이자율

    long Days_Notional;            // 평가일 to Notional 지급일

    long LockOutRef;            //  LockOut 날짜 N영업일
    long LookBackRef;            //  LookBack 날짜 
    long ObservationShift;        //  Observation Shift 할 지여부

    long* NWeekendDate;            //  주말개수(길이 = NCF)
    long** WeekendList;            //  주말 Array 리스트

    long NRefHistory;            // 오버나이트 히스토리 개수
    long* RefHistoryDate;        // 오버나이트 히스토리 상대날짜
    double* RefHistory;            // 오버나이트 금리 히스토리

} SCHD;

double Calc_Current_IRS(
    long CalcCRSFlag,
    curveinfo& Float_DiscCurve,
    curveinfo& Float_RefCurve,
    curveinfo& Fix_DiscCurve,
    curveinfo& FX_FloCurve,
    curveinfo& FX_FixCurve,
    SCHD* Float_Schedule,
    SCHD* Fix_Schedule
)
{
    long i;
    double IRSpread;
    double denominator;

    if (Float_Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    double P0;
    double P1;
    double P_Pay;
    double T0;
    double T1;
    double TPay;
    double FloatValue, FixValue;
    double dt_Fix;
    double FX = 1.0;
    double NA = 1.0;

    P0 = 1.0;
    T0 = 0.0;
    FloatValue = 0.0;
    for (i = 0; i < Float_Schedule->NCF; i++)
    {
        T1 = ((double)(Float_Schedule->Days_ForwardEnd[i] - Float_Schedule->Days_ForwardStart[0])) / denominator;
        TPay = ((double)(Float_Schedule->Days_PayDate[i] - Float_Schedule->Days_ForwardStart[0])) / denominator;
        P1 = exp(-Float_RefCurve.Interpolated_Rate(T1) * T1);
        P_Pay = exp(-Float_DiscCurve.Interpolated_Rate(TPay) * TPay);

        if (CalcCRSFlag == 0)
        {
            NA = 1.0;
            FX = 1.0;
        }
        else
        {
            NA = Float_Schedule->NotionalAmount;
            FX = FX_FloCurve.Interpolated_Rate(T1);
        }

        FloatValue += NA * FX * (P0 / P1 - 1.0) * P_Pay;
        P0 = P1;
    }

    if (Fix_Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    FixValue = 0.0;
    for (i = 0; i < Fix_Schedule->NCF; i++)
    {
        dt_Fix = ((double)(Fix_Schedule->Days_EndDate[i] - Fix_Schedule->Days_StartDate[i])) / denominator;
        TPay = ((double)(Fix_Schedule->Days_PayDate[i] - Fix_Schedule->Days_StartDate[0])) / denominator;
        P_Pay = exp(-Fix_DiscCurve.Interpolated_Rate(TPay) * TPay);

        T1 = ((double)(Fix_Schedule->Days_EndDate[i] - Fix_Schedule->Days_StartDate[0])) / denominator;

        if (CalcCRSFlag == 0)
        {
            NA = 1.0;
            FX = 1.0;
        }
        else
        {
            NA = Fix_Schedule->NotionalAmount;
            FX = FX_FixCurve.Interpolated_Rate(T1);
        }

        FixValue += NA * FX * P_Pay * dt_Fix;
    }

    IRSpread = FloatValue / FixValue;
    return IRSpread;
}

double SOFR_ForwardRate_Compound(
    curveinfo& RefCurve,
    long ForwardStartIdx,
    long ForwardEndIdx,
    long LockOutDays,
    long LookBackDays,
    long ObservShift,
    long HolidayFlag,
    long NHoliday,
    long* Holiday,
    long NSaturSunDay,
    long* SaturSunDay,
    long UseHistorySOFR,
    long NRefHistory,
    long* RefHistoryDate,
    double* RefHistory,
    double denominator,
    double& AnnualizedOISRate,
    long SOFRUseFlag
)
{
    long i;
    long j;
    long k;
    long n;

    long NRefCrvTerm = RefCurve.nterm();
    double* RefCrvTerm = RefCurve.Term;
    double* RefCrvRate = RefCurve.Rate;

    long nday = ForwardEndIdx - ForwardStartIdx;

    long HistDayIdx = 0;
    long AverageFlag = 0;
    if (SOFRUseFlag == 3) AverageFlag = 1;

    // 빠른 Holiday찾기용 TimePos Pointer
    long HoliStartIdx = 0;
    long HoliStartIdx2 = 0;
    long SatSunIdx = 0;
    long SatSunIdx2 = 0;

    long isHolidayFlag = 0;
    long isHolidayFlag2 = 0;

    long CountHoliday = 0;
    long CountHoliday2 = 0;

    long TimePos = 0;
    long TimePos2 = 0;

    double dt = 1.0 / 365.0;
    double Prev_PI;
    double ForwardRate;

    double t = 0.0;
    double PI_0;
    double T;
    T = (double)(ForwardEndIdx - ForwardStartIdx) / denominator;

    double CurrentRate;
    CurrentRate = Interpolate_Linear(RefCrvTerm, RefCrvRate, NRefCrvTerm, dt);

    long ObservShiftFlag = 0;
    if (LookBackDays > 0 && ObservShift > 0)     ObservShiftFlag = 1;

    ///////////////////////////
    // Average 키움증권 추가 //
    ///////////////////////////
    long NCumpound = 0;
    double AverageRate = 0.0;

    ///////////////////////////
    // N영업일 전 LockOutDay 계산
    ///////////////////////////
    long LockOutDay = ForwardEndIdx;
    long LockOutFlag = 0;

    if (LockOutDays > 0)
    {
        k = 0;
        for (i = 1; i < 30; i++)
        {
            LockOutDay -= 1;
            // N영업일까지 날짜 뒤로가기
            if (max(isin(LockOutDay, Holiday, NHoliday), isin(LockOutDay, SaturSunDay, NSaturSunDay)) == 0) k += 1;
            if (k == LockOutDays) break;
        }
    }
    double LockOutDayRate = 0.0;


    ///////////////////////////
    // Holiday Rate가 Interpolate일 때 사용할 변수
    ///////////////////////////
    double TargetRate[2] = { 0.0,0.0 };
    double TargetT[2] = { 0.0,0.0 };

    long lookbackday;
    Prev_PI = 1.0;
    PI_0 = 1.0;
    if (UseHistorySOFR == 1 && ObservShiftFlag == 0)
    {
        //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // Forward Start 날짜가 가격 계산일보다 앞에 있을 경우 History Rate 뒤져봐야함 + Observe Shift 적용 안하는 경우 //
        //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        HistDayIdx = 0;
        if (LookBackDays < 1)
        {
            ////////////////////////////
            // LookBack 적용안할 경우 //
            ////////////////////////////
            if (ForwardEndIdx >= 0)
            {
                if (HolidayFlag == 3)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        HistDayIdx = isinfindindex(i, RefHistoryDate, NRefHistory);

                        if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                        else ForwardRate = CurrentRate;

                        Prev_PI *= 1.0 + ForwardRate * 1.0 / denominator;
                        AverageRate += ForwardRate;

                        NCumpound += 1;
                    }
                }
                else if (HolidayFlag == 0)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        if (i == ForwardStartIdx) isHolidayFlag = 0;
                        else isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                        if (isHolidayFlag == 0)
                        {
                            HistDayIdx = isinfindindex(i, RefHistoryDate, NRefHistory);

                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = i + 1; j < 0; j++)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }
                            }
                            Prev_PI *= 1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator;
                            AverageRate += ForwardRate;

                            NCumpound += 1;
                        }

                    }
                }
                else if (HolidayFlag == 1)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        if (i == ForwardStartIdx) isHolidayFlag = 0;
                        else isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                        if (isHolidayFlag == 0)
                        {
                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = i + 1; j < ForwardEndIdx; j++)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }
                            }
                            HistDayIdx = isinfindindex(i + CountHoliday + 1, RefHistoryDate, NRefHistory);

                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            Prev_PI *= 1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator;
                            AverageRate += ForwardRate;

                            NCumpound += 1;
                        }
                    }
                }
                if (HolidayFlag == 2)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        if (i == ForwardStartIdx) isHolidayFlag = 0;
                        else isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                        if (isHolidayFlag == 0)
                        {
                            ///////////////////////////////
                            // 영업일인 경우 당일 이자율 //
                            ///////////////////////////////
                            HistDayIdx = isinfindindex(i, RefHistoryDate, NRefHistory);
                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;
                            CountHoliday = 0;
                        }
                        else if (isHolidayFlag == 1 && NRefHistory > 0)
                        {
                            ///////////////////////////////////////////////////////////
                            // 영업일이 아닌 경우 직전, 직후 영업일 ForwardRate 찾기 //
                            ///////////////////////////////////////////////////////////

                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = j - 1; j < ForwardStartIdx; j--)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }
                            }
                            HistDayIdx = isinfindindex(i - CountHoliday - 1, RefHistoryDate, NRefHistory);
                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            TargetRate[0] = ForwardRate;
                            TargetT[0] = (-(double)(CountHoliday)-1.0);

                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = i + 1; j < ForwardEndIdx; j++)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }

                            }
                            HistDayIdx = isinfindindex(i + CountHoliday + 1, RefHistoryDate, NRefHistory);
                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            TargetRate[1] = ForwardRate;
                            TargetT[1] = ((double)(CountHoliday)+1.0);
                            ForwardRate = Interpolate_Linear(TargetT, TargetRate, 2, 0.0);
                        }
                        else ForwardRate = CurrentRate;

                        Prev_PI *= 1.0 + ForwardRate * 1.0 / denominator;
                        AverageRate += ForwardRate;

                        NCumpound += 1;
                    }
                }
            }
            ////////////////////////////////////////////////////////
            // 과거 반영 다 끝났으면 ForwardStartIdx 0으로 바꾸기 //
            ////////////////////////////////////////////////////////
            ForwardStartIdx = 0;
        }
        else if (LookBackDays > 0)
        {
            //////////////////////////
            // LookBack 적용할 경우 //
            //////////////////////////
            if (ForwardEndIdx >= 0)
            {
                if (HolidayFlag == 3)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        lookbackday = i;

                        k = 0;

                        for (n = 1; n < 120; n++)
                        {
                            ///////////////////////////
                            // N영업일 전 LookBackDay 계산
                            ///////////////////////////
                            lookbackday -= 1;
                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        HistDayIdx = isinfindindex(lookbackday, RefHistoryDate, NRefHistory);
                        if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                        else ForwardRate = CurrentRate;
                        Prev_PI *= 1.0 + ForwardRate * 1.0 / denominator;
                        AverageRate += ForwardRate;

                        NCumpound += 1;
                    }
                }
                else if (HolidayFlag == 0)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        if (i == ForwardStartIdx) isHolidayFlag = 0;
                        else isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                        if (isHolidayFlag == 0)
                        {
                            lookbackday = i;

                            k = 0;

                            for (n = 1; n < 120; n++)
                            {
                                ///////////////////////////
                                // N영업일 전 LookBackDay 계산
                                ///////////////////////////
                                lookbackday -= 1;

                                if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                                if (k == LookBackDays) break;
                            }
                            HistDayIdx = isinfindindex(lookbackday, RefHistoryDate, NRefHistory);
                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = i + 1; j < ForwardEndIdx; j++)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }

                            }
                            Prev_PI *= 1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator;
                            AverageRate += ForwardRate;

                            NCumpound += 1;
                        }
                    }
                }
                else if (HolidayFlag == 1)
                {
                    for (i = ForwardStartIdx; i < 0; i++)
                    {
                        if (i == ForwardStartIdx) isHolidayFlag = 0;
                        else isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                        if (isHolidayFlag == 0)
                        {
                            CountHoliday = 0;
                            HoliStartIdx = 0;
                            SatSunIdx = 0;

                            for (j = i + 1; j < ForwardEndIdx; j++)
                            {
                                isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                                if (isHolidayFlag2 == 0) break;
                                else
                                {
                                    CountHoliday += 1;
                                }
                            }

                            if (CountHoliday == 0)
                            {
                                lookbackday = i;
                            }
                            else
                            {
                                lookbackday = i + CountHoliday + 1;
                            }

                            k = 0;
                            for (n = 1; n < 120; n++)
                            {
                                ///////////////////////////
                                // N영업일 전 LookBackDay 계산
                                ///////////////////////////
                                lookbackday -= 1;
                                if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                                if (k == LookBackDays) break;
                            }
                            HistDayIdx = isinfindindex(lookbackday, RefHistoryDate, NRefHistory);
                            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                            else ForwardRate = CurrentRate;

                            Prev_PI *= 1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator;
                            AverageRate += ForwardRate;

                            NCumpound += 1;
                        }
                    }
                }
            }
            ForwardStartIdx = 0;
        }
    }
    else if (UseHistorySOFR == 1 && ObservShiftFlag == 1)
    {
        ///////////////////////////
        // Forward Start 날짜가 가격 계산일보다 앞에 있을 경우
        // 또한 ObservShift가 있는 경우
        ///////////////////////////
        HistDayIdx = 0;
        if (ForwardEndIdx >= 0)
        {
            for (i = ForwardStartIdx; i < 0; i++)
            {
                lookbackday = i;
                isHolidayFlag = max(isin(i, Holiday, NHoliday), isin(i, SaturSunDay, NSaturSunDay));

                if (isHolidayFlag == 0)
                {
                    //////////////////
                    // Holiday가 아니라면 LookBack영업일 Back
                    //////////////////

                    k = 0;
                    if (LookBackDays > 0)
                    {
                        for (n = 1; n < 120; n++)
                        {
                            lookbackday -= 1;
                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                    }
                    HistDayIdx = isinfindindex(lookbackday, RefHistoryDate, NRefHistory);
                    if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                    else ForwardRate = Interpolate_Linear(RefCrvTerm, RefCrvRate, NRefCrvTerm, dt);

                    ///////////////////////////
                    // Observation Dt 계산
                    ///////////////////////////
                    CountHoliday = 0;
                    HoliStartIdx = 0;
                    SatSunIdx = 0;

                    for (j = lookbackday + 1; j < 0; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx));
                        if (isHolidayFlag2 == 0) break;
                        else CountHoliday += 1;
                    }

                    if (CountHoliday == 0) Prev_PI *= 1.0 + ForwardRate * 1.0 / denominator;
                    else Prev_PI *= 1.0 + ForwardRate * ((double)(1 + CountHoliday) / denominator);
                    AverageRate += ForwardRate;

                    NCumpound += 1;
                }
            }
        }
        ForwardStartIdx = 0;
    }

    PI_0 = Prev_PI;
    HoliStartIdx = 0;
    HoliStartIdx2 = 0;
    TimePos = 0;
    TimePos2 = 0;
    LockOutFlag = 0;
    NCumpound = 0;
    SatSunIdx = 0;
    SatSunIdx2 = 0;

    if (ObservShiftFlag == 0)
    {
        if (HolidayFlag == 0)
        {
            //////////////////
            // HolidayRate Forward Fill
            //////////////////
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                //////////////////////////
                // 첫 날은 영업일로 처리
                //////////////////////////
                if (i == ForwardStartIdx)
                {
                    if (UseHistorySOFR == 0) isHolidayFlag = 0;
                    else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));
                }
                else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    lookbackday = i + 0;

                    ////////////////////
                    // Forward Rate Time 추정 LookBack 반영
                    ////////////////////
                    if (LookBackDays < 1) t = ((double)i) / 365.0;
                    else
                    {
                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;

                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }

                    ////////////////////
                    // 해당일 이후 Holiday개수 체크하여 dt설정
                    ////////////////////
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;
                    for (j = i + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday += 1;
                        }
                    }

                    if (CountHoliday == 0)
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator,  &TimePos);
                    }
                    else
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator , &TimePos, CountHoliday);
                    }

                    LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                    PI_0 *= (1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator);
                    AverageRate += ForwardRate;

                    NCumpound += 1;
                }
            }
        }
        else if (HolidayFlag == 1)
        {
            //////////////////
            // HolidayRate Backward Fill
            //////////////////
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                //////////////////////////
                // 첫 날은 영업일로 처리
                //////////////////////////
                if (i == ForwardStartIdx)
                {
                    if (UseHistorySOFR == 0) isHolidayFlag = 0;
                    else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));
                }
                else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    ////////////////////
                    // 해당일 이후 Holiday개수 체크하여 dt설정
                    ////////////////////
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    for (j = i + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday += 1;
                        }
                    }

                    if (CountHoliday == 0)
                    {
                        lookbackday = i + 0;
                    }
                    else
                    {
                        lookbackday = i + CountHoliday + 1;
                    }

                    ////////////////////
                    // Forward Rate Time 추정 LookBack 반영
                    ////////////////////
                    if (LookBackDays < 1) t = ((double)lookbackday) / 365.0;
                    else
                    {
                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;

                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }

                    CountHoliday2 = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    for (j = lookbackday + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday2 += 1;
                        }
                    }

                    if (CountHoliday2 == 0)
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);
                    }
                    else
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos, CountHoliday2);
                    }

                    LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                    PI_0 *= (1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator);
                    AverageRate += ForwardRate;

                    NCumpound += 1;
                }
            }
        }
        else if (HolidayFlag == 2)
        {
            //////////////////
            // HolidayRate Interpolated Fill
            //////////////////
            TimePos2 = 0;
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                if (i == ForwardStartIdx)
                {
                    if (UseHistorySOFR == 0) isHolidayFlag = 0;
                    else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));
                }
                else isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    lookbackday = i + 0;

                    if (LookBackDays < 1) t = ((double)i) / 365.0;
                    else
                    {
                        ///////////////////////////
                        // N영업일 전 LookBackDay 계산
                        ///////////////////////////

                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;

                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }
                    ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, &TimePos);

                    TargetRate[0] = ForwardRate;
                    TargetT[0] = 0.0;

                    ////////////////////
                    // 해당일 이후 Holiday개수 체크하여 dt설정
                    ////////////////////
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    for (j = i + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));

                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday += 1;
                        }
                    }

                    if (CountHoliday == 0)
                    {
                        LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                        PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                        AverageRate += ForwardRate;
                        NCumpound += 1;
                    }
                    else
                    {
                        ////////////////////
                        // Holiday 이후 이자율추정
                        ////////////////////
                        lookbackday = i + CountHoliday + 1;

                        if (LookBackDays < 1) t = ((double)lookbackday) / 365.0;
                        else
                        {
                            k = 0;
                            for (n = 1; n < 120; n++)
                            {
                                /////////////////////
                                // N영업일 전까지 빼기
                                /////////////////////
                                lookbackday -= 1;

                                if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                                if (k == LookBackDays) break;
                            }
                            t = ((double)lookbackday) / 365.0;
                        }
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos2);

                        LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                        TargetRate[1] = ForwardRate;
                        TargetT[1] = ((double)(CountHoliday + 1));

                        PI_0 *= (1.0 + TargetRate[0] * 1.0 / denominator);
                        AverageRate += TargetRate[0];
                        NCumpound += 1;
                        for (j = 0; j < CountHoliday; j++)
                        {
                            //////////////////////////////////////
                            // Holiday동안 Linterp Rate로 Compound
                            //////////////////////////////////////
                            if (LockOutFlag == 0) ForwardRate = Interpolate_Linear(TargetT, TargetRate, 2, (double)(j + 1));
                            PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                            AverageRate += ForwardRate;
                            NCumpound += 1;
                        }
                    }
                }
            }
        }
        else
        {
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                lookbackday = i + 0;

                ////////////////////
                // Forward Rate Time 추정 LookBack 반영
                ////////////////////
                if (LookBackDays < 1) t = ((double)i) / 365.0;
                else
                {
                    k = 0;
                    for (n = 1; n < 120; n++)
                    {
                        /////////////////////
                        // N영업일 전까지 빼기
                        /////////////////////
                        lookbackday -= 1;
                        if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                        if (k == LookBackDays) break;
                    }
                    t = ((double)lookbackday) / 365.0;
                }
                ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);

                LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                AverageRate += ForwardRate;
                NCumpound += 1;
            }
        }
    }
    else if (ObservShiftFlag == 1)
    {
        if (HolidayFlag == 0)
        {
            //////////////////
            // HolidayRate Forward Fill
            //////////////////
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    lookbackday = i + 0;

                    ////////////////////
                    // Forward Rate Time 추정 LookBack 반영
                    ////////////////////
                    if (LookBackDays < 1) t = ((double)i) / 365.0;
                    else
                    {
                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;

                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }

                    ////////////////////
                    // Observe Shift Dt 추정 LookBack 반영
                    ////////////////////
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;
                    for (j = lookbackday + 1; j < ForwardEndIdx; j++)
                    {

                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else CountHoliday += 1;
                    }

                    if (CountHoliday == 0)
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);
                    }
                    else
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos, CountHoliday);
                    }

                    if (lookbackday < 0)
                    {
                        HistDayIdx = isinfindindex(lookbackday, RefHistoryDate, NRefHistory);
                        if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
                        else ForwardRate = CurrentRate;
                    }

                    LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                    PI_0 *= (1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator);
                    AverageRate += ForwardRate;

                    NCumpound += 1;
                }
            }

        }
        else if (HolidayFlag == 1)
        {
            //////////////////
            // HolidayRate Backward Fill
            //////////////////
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    for (j = i + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday += 1;
                        }
                    }

                    if (CountHoliday == 0)
                    {
                        lookbackday = i + 0;
                    }
                    else
                    {
                        lookbackday = i + CountHoliday + 1;
                    }

                    ////////////////////
                    // Forward Rate Time 추정 LookBack 반영
                    ////////////////////
                    if (LookBackDays < 1) t = ((double)lookbackday) / 365.0;
                    else
                    {
                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;
                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }

                    CountHoliday2 = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    for (j = lookbackday + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else
                        {
                            CountHoliday2 += 1;
                        }
                    }

                    if (CountHoliday2 == 0)
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);
                    }
                    else
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos, CountHoliday2);
                    }
                    LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                    ////////////////////
                    // Observe Shift Dt 추정 LookBack 반영
                    ////////////////////                    
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;

                    if (lookbackday != i)
                    {
                        for (j = lookbackday + 1; j < ForwardEndIdx; j++)
                        {
                            isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                            if (isHolidayFlag2 == 0) break;
                            else CountHoliday += 1;
                        }
                    }

                    PI_0 *= (1.0 + ForwardRate * (1.0 + (double)CountHoliday) / denominator);
                    AverageRate += ForwardRate;

                    NCumpound += 1;
                }
            }

        }
        else if (HolidayFlag == 2)
        {
            //////////////////
            // HolidayRate Interpolated Fill
            //////////////////
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                isHolidayFlag = max(isin(i, Holiday, NHoliday, HoliStartIdx), isin(i, SaturSunDay, NSaturSunDay, SatSunIdx));

                if (isHolidayFlag == 0)
                {
                    lookbackday = i + 0;

                    ////////////////////
                    // Forward Rate Time1 추정 LookBack 반영
                    ////////////////////
                    if (LookBackDays < 1) t = ((double)i) / 365.0;
                    else
                    {
                        k = 0;
                        for (n = 1; n < 120; n++)
                        {
                            /////////////////////
                            // N영업일 전까지 빼기
                            /////////////////////
                            lookbackday -= 1;
                            if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                            if (k == LookBackDays) break;
                        }
                        t = ((double)lookbackday) / 365.0;
                    }

                    ////////////////////
                    // Observ Shift
                    ////////////////////
                    CountHoliday = 0;
                    HoliStartIdx2 = 0;
                    SatSunIdx2 = 0;
                    for (j = lookbackday + 1; j < ForwardEndIdx; j++)
                    {
                        isHolidayFlag2 = max(isin(j, Holiday, NHoliday, HoliStartIdx2), isin(j, SaturSunDay, NSaturSunDay, SatSunIdx2));
                        if (isHolidayFlag2 == 0) break;
                        else CountHoliday += 1;
                    }

                    if (CountHoliday == 0)
                    {
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);

                        LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                        PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                        AverageRate += ForwardRate;

                    }
                    else
                    {
                        TargetT[0] = 0.0;
                        ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);

                        LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                        TargetRate[0] = ForwardRate;
                        PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                        AverageRate += ForwardRate;
                        NCumpound += 1;


                        ////////////////////
                        // Forward Rate Time2 추정 LookBack 반영
                        ////////////////////
                        t = ((double)(lookbackday + CountHoliday + 1)) / denominator;
                        TargetT[1] = (double)(CountHoliday + 1);
                        TargetRate[1] = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);

                        LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                        for (j = 0; j < CountHoliday; j++)
                        {
                            if (LockOutFlag == 0) ForwardRate = Interpolate_Linear(TargetT, TargetRate, 2, ((double)(j + 1)));
                            PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                            AverageRate += ForwardRate;
                            NCumpound += 1;
                        }
                    }
                }
            }
        }
        else
        {
            for (i = ForwardStartIdx; i < ForwardEndIdx; i++)
            {
                lookbackday = i + 0;

                ////////////////////
                // Forward Rate Time 추정 LookBack 반영
                ////////////////////
                if (LookBackDays < 1) t = ((double)i) / 365.0;
                else
                {
                    k = 0;
                    for (n = 1; n < 120; n++)
                    {
                        /////////////////////
                        // N영업일 전까지 빼기
                        /////////////////////
                        lookbackday -= 1;
                        if (max(isin(lookbackday, Holiday, NHoliday), isin(lookbackday, SaturSunDay, NSaturSunDay)) == 0) k += 1;
                        if (k == LookBackDays) break;
                    }
                    t = ((double)lookbackday) / 365.0;
                }
                ForwardRate = Calc_Forward_Rate_Daily(RefCrvTerm, RefCrvRate, NRefCrvTerm, t, denominator, &TimePos);

                LockOutCheck(LockOutFlag, LockOutDay, i, LockOutDayRate, ForwardRate);

                PI_0 *= (1.0 + ForwardRate * 1.0 / denominator);
                AverageRate += ForwardRate;
                NCumpound += 1;
            }
        }
    }

    if (AverageFlag == 1)
    {
        AverageRate = AverageRate / (double)NCumpound;
        PI_0 = pow(1.0 + AverageRate / denominator, (int)nday);
    }

    AnnualizedOISRate = (PI_0 - 1.0) * 1.0 / T;

    return PI_0 - 1.0;
}

double Calc_Current_SOFR_Swap(
    long CalcCRSFlag,
    curveinfo& Float_DiscCurve,
    curveinfo& Float_RefCurve,
    curveinfo& Fix_DiscCurve,
    curveinfo& Float_FXCurve,
    curveinfo& Fix_FXCurve,
    SCHD* Float_Schedule,
    SCHD* Fix_Schedule,
    long LockOutDays,
    long LookBackDays,
    long ObservShift,
    long NSaturSunDay,
    long* SaturSunDay
)
{
    long i;
    long Day0, Day1;
    long UseSOFRHistory = 0;

    double SOFR_Swap_Spread;
    double denominator;

    if (Float_Schedule->DayCount == 0)denominator = 365.0;
    else denominator = 360.0;

    double P_Pay;
    double TPay;
    double FloatValue, FixValue;
    double dt_Fix;
    double SOFR_Compound;
    double Annual_OIS = 0.0;
    double FX = 1.0;
    double NA = 1.0;

    Day0 = 0;
    FloatValue = 0.0;
    for (i = 0; i < Float_Schedule->NCF; i++)
    {
        Day1 = Float_Schedule->Days_ForwardEnd[i] - Float_Schedule->Days_ForwardStart[0];
        TPay = ((double)(Float_Schedule->Days_PayDate[i] - Float_Schedule->Days_StartDate[0])) / denominator;
        SOFR_Compound = SOFR_ForwardRate_Compound(Float_RefCurve, Day0, Day1, LockOutDays, LookBackDays, ObservShift,
            Float_Schedule->HolidayFlag_Ref, Float_Schedule->NHolidays_Ref, Float_Schedule->Days_Holidays_Ref, NSaturSunDay, SaturSunDay, UseSOFRHistory, Float_Schedule->NRefHistory, Float_Schedule->RefHistoryDate, Float_Schedule->RefHistory, denominator, Annual_OIS, 1);
        P_Pay = exp(-Float_DiscCurve.Interpolated_Rate(TPay) * TPay);

        if (CalcCRSFlag == 0)
        {
            NA = 1.0;
            FX = 1.0;
        }
        else
        {
            NA = Float_Schedule->NotionalAmount;
            FX = Float_FXCurve.Interpolated_Rate(((double)(Float_Schedule->Days_ForwardEnd[i] - Float_Schedule->Days_StartDate[0])) / denominator);
        }

        FloatValue += NA * FX * SOFR_Compound * P_Pay;
        Day0 = Day1;
    }

    if (Fix_Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    FixValue = 0.0;
    for (i = 0; i < Fix_Schedule->NCF; i++)
    {
        dt_Fix = ((double)(Fix_Schedule->Days_EndDate[i] - Fix_Schedule->Days_StartDate[i])) / denominator;
        TPay = ((double)(Fix_Schedule->Days_PayDate[i] - Fix_Schedule->Days_StartDate[0])) / denominator;
        P_Pay = exp(-Fix_DiscCurve.Interpolated_Rate(TPay) * TPay);

        if (CalcCRSFlag == 0)
        {
            NA = 1.0;
            FX = 1.0;
        }
        else
        {
            NA = Fix_Schedule->NotionalAmount;
            FX = Fix_FXCurve.Interpolated_Rate(((double)(Fix_Schedule->Days_EndDate[i] - Fix_Schedule->Days_StartDate[0])) / denominator);
        }
        FixValue += NA * FX * P_Pay * dt_Fix;
    }

    SOFR_Swap_Spread = FloatValue / FixValue;
    return SOFR_Swap_Spread;
}

double Calc_Forward_SOFR_Swap(
    curveinfo& Float_DiscCurve,
    curveinfo& Float_RefCurve,
    curveinfo& Fix_DiscCurve,
    double T_Option,
    double Tenor,
    double FreqMonth,
    long HolidayCalcFlag,
    long NHolidays,
    long* Days_Holidays,
    long NSaturSunDay,
    long* SaturSunDay,
    long NRefHistory,
    long* RefHistoryDate,
    double* RefHistory,
    double denominator,
    long Float_RefLockOut,
    long Float_RefLookBack,
    long ObservationShift
)
{
    long i;
    long k;

    long Day0, Day1;
    double dt;

    long ndates = NPaymentSwap(T_Option, T_Option + Tenor, FreqMonth);
    long* dates = (long*)malloc(sizeof(long) * (ndates));
    ndates = MappingPaymentDates(T_Option + Tenor, FreqMonth, dates, ndates);
    double* P0T = (double*)malloc(sizeof(double) * (ndates + 1));
    P0T[0] = Calc_Discount_Factor(Fix_DiscCurve.Term, Fix_DiscCurve.Rate, Fix_DiscCurve.nterm(), T_Option); // 옵션만기시점
    for (i = 1; i < ndates + 1; i++) P0T[i] = Calc_Discount_Factor(Fix_DiscCurve.Term, Fix_DiscCurve.Rate, Fix_DiscCurve.nterm(), ((double)dates[i - 1]) / 365.0);

    double* P0T_Float = (double*)malloc(sizeof(double) * (ndates + 1));
    P0T_Float[0] = Calc_Discount_Factor(Float_DiscCurve.Term, Float_DiscCurve.Rate, Float_DiscCurve.nterm(), T_Option);
    for (i = 1; i < ndates + 1; i++) P0T_Float[i] = Calc_Discount_Factor(Float_DiscCurve.Term, Float_DiscCurve.Rate, Float_DiscCurve.nterm(), ((double)dates[i - 1]) / 365.0);

    double SOFR_Swap_Spread;

    double P_Pay;

    double FloatValue, FixValue;

    double SOFR_Compound;
    double Annual_OIS = 0.0;

    Day0 = (long)(T_Option * 365.0 + 0.001);

    FloatValue = 0.0;
    for (i = 0; i < ndates; i++)
    {
        Day1 = dates[i];
        SOFR_Compound = SOFR_ForwardRate_Compound(Float_RefCurve, Day0, Day1, Float_RefLockOut, Float_RefLookBack, ObservationShift, HolidayCalcFlag, NHolidays, Days_Holidays, NSaturSunDay, SaturSunDay, 0, NRefHistory, RefHistoryDate, RefHistory, denominator, Annual_OIS, 1);
        P_Pay = P0T_Float[i + 1];
        FloatValue += SOFR_Compound * P_Pay;
        Day0 = Day1;
    }

    FixValue = 0.0;
    for (i = 0; i < ndates; i++)
    {
        if (i == 0) dt = (double)dates[0] / 365.0 - T_Option;
        else dt = ((double)(dates[i] - dates[i - 1])) / 365.0;
        FixValue += dt * P0T[i + 1];
    }


    SOFR_Swap_Spread = FloatValue / FixValue;

    free(dates);
    free(P0T_Float);
    free(P0T);
    return SOFR_Swap_Spread;
}

void Floating_PartialValue(
    long CalcCRSFlag,
    curveinfo& DiscCurve,
    curveinfo& RefCurve,
    curveinfo& FXCurve,
    double Ref_T0,
    double Ref_T1,
    double Frac_T0,
    double Frac_T1,
    double Pay_T,
    long FixedRateFlag,
    double FixedRate,
    double Slope,
    double FixedAmount,
    double Notional,
    long YYYYMMDDStart,
    long YYYYMMDDEnd,
    long DayCountFlag,
    // 결과
    double* ResultRefRate,
    double* ResultCF,
    double* ResultDisc,
    double* ResultDiscCF
)
{
    double dt_Forward;
    double dt_CPN;

    double Disc0, Disc1, DiscPay;
    double ForwardRate;
    double CF;
    double FX = 1.0;

    if (CalcCRSFlag == 0) FX = 1.0;
    else FX = FXCurve.Interpolated_Rate(Frac_T1);

    dt_Forward = (Ref_T1 - Ref_T0);
    dt_CPN = DayCountFractionAtoB(YYYYMMDDStart, YYYYMMDDEnd, DayCountFlag);

    if (FixedRateFlag == 0)
    {
        Disc0 = exp(-RefCurve.Interpolated_Rate(Ref_T0) * Ref_T0);
        Disc1 = exp(-RefCurve.Interpolated_Rate(Ref_T1) * Ref_T1);
        if (dt_Forward < 1.0) ForwardRate = 1.0 / dt_Forward * (Disc0 / Disc1 - 1.0);
        else ForwardRate = Continuous_ForwardRate(RefCurve, Ref_T0, Ref_T1);
    }
    else {
        if (FixedRate > 0.00001 || FixedRate < -0.00001)  ForwardRate = FixedRate;
        else
        {
            Disc0 = exp(-RefCurve.Interpolated_Rate(Ref_T0) * Ref_T0);
            Disc1 = exp(-RefCurve.Interpolated_Rate(Ref_T1) * Ref_T1);
            if (dt_Forward < 1.0) ForwardRate = 1.0 / dt_Forward * (Disc0 / Disc1 - 1.0);
            else ForwardRate = Continuous_ForwardRate(RefCurve, Ref_T0, Ref_T1);
        }
    }
    CF = (Slope * ForwardRate + FixedAmount) * dt_CPN;
    DiscPay = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);

    *ResultRefRate = ForwardRate;
    *ResultCF = Notional * CF * FX;
    *ResultDisc = DiscPay;
    *ResultDiscCF = Notional * DiscPay * CF;
}

void FixedLeg_PartialValue(
    long CalcCRSFlag,
    curveinfo& DiscCurve,
    curveinfo& FXCurve,
    double Frac_T0,
    double Frac_T1,
    double Pay_T,
    double FixedAmount,
    double Notional,
    // 결과
    double* ResultRefRate,
    double* ResultCF,
    double* ResultDisc,
    double* ResultDiscCF
)
{
    double dt_CPN;

    double DiscPay;
    double CF;
    double FX = 1.0;

    dt_CPN = (Frac_T1 - Frac_T0);
    CF = (FixedAmount)*dt_CPN;
    DiscPay = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
    if (CalcCRSFlag == 0) FX = 1.0;
    else FX = FXCurve.Interpolated_Rate(Frac_T1);

    *ResultRefRate = 0.0;
    *ResultCF = FX * Notional * CF;
    *ResultDisc = DiscPay;
    *ResultDiscCF = Notional * DiscPay * CF;
}

double LegValue(
    long CRSFlag,
    SCHD* Schedule,
    curveinfo& DiscCurve,
    curveinfo& RefCurve,
    curveinfo& FXCurve,
    double* ResultRefRate,
    double* ResultCPN,
    double* ResultDF,
    double* DiscCFArray,
    long ConvAdjFlag,
    long NConvAdjVolTerm,
    double* ConvAdjVolTerm,
    double* ConvAdjVol
)
{
    long i;
    long FixedRateFlag;
    long PrevFlag;
    double denominator;

    if (Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    ///////////////
    // SOFR 관련 //
    ///////////////

    long UseHistorySOFR;
    long* NSaturSunDay_List = Schedule->NWeekendDate;
    long** SaturSunDay_List = Schedule->WeekendList;
    long NRefHistory = Schedule->NRefHistory;
    long* RefHistoryDate = Schedule->RefHistoryDate;
    double* RefHistory = Schedule->RefHistory;

    double Ref_T0, Ref_T1, SwapStartT, SwapEndT;
    double Frac_T0, Frac_T1;
    double Pay_T;
    double value = 0.0;
    double FreqMonth;
    double FXRate = 1.0;
    double OIS_Annual = 0.0, OIS_Compound = 0.0;
    double FX;
    double DiscPay;

    if (Schedule->FixedFlotype == 1)
    {
        //////////////
        // 변동금리 //
        //////////////

        if (Schedule->ReferenceType == 0)
        {
            ///////////////////////////////////////////
            // 일반적인 Libor, CD, Zero Rate 형태   ///
            ///////////////////////////////////////////

            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->Days_PayDate[i] > 0)
                {
                    PrevFlag = 0;
                }

                if (PrevFlag == 0)
                {
                    Ref_T0 = ((double)Schedule->Days_ForwardStart[i]) / 365.;
                    Ref_T1 = ((double)Schedule->Days_ForwardEnd[i]) / 365.;
                    Frac_T0 = ((double)Schedule->Days_StartDate[i]) / denominator;
                    Frac_T1 = ((double)Schedule->Days_EndDate[i]) / denominator;
                    Pay_T = ((double)Schedule->Days_PayDate[i]) / 365.0;

                    if (Schedule->Days_ForwardStart[i] < 0) FixedRateFlag = 1;
                    else FixedRateFlag = 0;

                    Floating_PartialValue(
                        CRSFlag, DiscCurve, RefCurve, FXCurve, Ref_T0, Ref_T1, Frac_T0,
                        Frac_T1, Pay_T, FixedRateFlag, Schedule->FixedRefRate[i], Schedule->Slope[i], Schedule->CPN[i], Schedule->NotionalAmount,
                        Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount,
                        ResultRefRate + i, ResultCPN + i, ResultDF + i, DiscCFArray + i);
                }
                else
                {
                    ResultRefRate[i] = Schedule->FixedRefRate[i];
                    ResultCPN[i] = 0.0;
                    ResultDF[i] = 0.0;
                    DiscCFArray[i] = 0.0;
                }
            }
        }
        else if (Schedule->ReferenceType == 1)
        {
            //////////////////////////////////
            // 기초자산이 Swap Rate 형태   ///
            //////////////////////////////////

            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->Days_PayDate[i] > 0) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    SwapStartT = ((double)Schedule->Days_ForwardStart[i]) / denominator;
                    SwapEndT = SwapStartT + Schedule->RefSwapMaturity;
                    Pay_T = ((double)Schedule->Days_PayDate[i]) / 365.0;

                    if (Schedule->Days_ForwardStart[i] <= 0) FixedRateFlag = 1;
                    else FixedRateFlag = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = FXCurve.Interpolated_Rate(SwapEndT);

                    FreqMonth = 12.0 / (double)Schedule->NSwapPayAnnual;
                    if (FixedRateFlag == 0)
                    {
                        ResultRefRate[i] = FSR(RefCurve.Term, RefCurve.Rate, RefCurve.nterm(), SwapStartT, Schedule->RefSwapMaturity, FreqMonth);
                        if (ConvAdjFlag > 0)
                        {

                        }
                        ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * ((double)(Schedule->Days_EndDate[i] - Schedule->Days_StartDate[i])) / denominator;
                        ResultDF[i] = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                        DiscCFArray[i] = ResultCPN[i] * ResultDF[i];
                    }
                    else
                    {
                        //////////////////////////////////////////////////////////////////////////
                        // 입력해둔 과거 금리가 존재하면 그거 사용하고 아니면 현재 스왑금리사용 //
                        //////////////////////////////////////////////////////////////////////////

                        if (Schedule->FixedRefRate[i] > 0.00001 || Schedule->FixedRefRate[i] < -0.00001) ResultRefRate[i] = Schedule->FixedRefRate[i];
                        else ResultRefRate[i] = FSR(RefCurve.Term, RefCurve.Rate, RefCurve.nterm(), SwapStartT, Schedule->RefSwapMaturity, FreqMonth);

                        ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * ((double)(Schedule->Days_EndDate[i] - Schedule->Days_StartDate[i])) / denominator;
                        ResultDF[i] = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                        DiscCFArray[i] = ResultCPN[i] * ResultDF[i];
                    }
                }
                else
                {
                    ResultRefRate[i] = Schedule->FixedRefRate[i];
                    ResultCPN[i] = 0.0;
                    ResultDF[i] = 0.0;
                    DiscCFArray[i] = 0.0;
                }
            }
        }
        else if (Schedule->ReferenceType == 2)
        {
            //////////////////////////////////
            // 기초자산이 SOFR Rate 형태   ///
            //////////////////////////////////

            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->Days_PayDate[i] > 0) PrevFlag = 0;

                if (PrevFlag == 0)
                {

                    Pay_T = ((double)Schedule->Days_PayDate[i]) / 365.0;
                    if (Schedule->Days_ForwardStart[i] < 0) UseHistorySOFR = 1;
                    else UseHistorySOFR = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = Interpolate_Linear(FXCurve.Term, FXCurve.Rate, FXCurve.nterm(), Pay_T);

                    FreqMonth = 12.0 / (double)Schedule->NSwapPayAnnual;
                    OIS_Compound = SOFR_ForwardRate_Compound(RefCurve, Schedule->Days_ForwardStart[i], Schedule->Days_ForwardEnd[i], Schedule->LockOutRef, Schedule->LookBackRef, Schedule->ObservationShift, Schedule->HolidayFlag_Ref, Schedule->NHolidays_Ref, Schedule->Days_Holidays_Ref, NSaturSunDay_List[i], SaturSunDay_List[i], UseHistorySOFR, Schedule->NRefHistory, Schedule->RefHistoryDate, Schedule->RefHistory, denominator, OIS_Annual, 1);
                    ResultRefRate[i] = OIS_Annual;
                    ResultCPN[i] = FXRate * Schedule->NotionalAmount * (OIS_Compound * Schedule->Slope[i] + Schedule->CPN[i]);
                    ResultDF[i] = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                    DiscCFArray[i] = ResultCPN[i] * ResultDF[i];
                }
                else
                {
                    ResultRefRate[i] = Schedule->FixedRefRate[i];
                    ResultCPN[i] = 0.0;
                    ResultDF[i] = 0.0;
                    DiscCFArray[i] = 0.0;
                }
            }
        }
        else if (Schedule->ReferenceType == 3)
        {
            ///////////////////////////////////////
            // 기초자산이 SOFR Swap Rate 형태   ///
            ///////////////////////////////////////

            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->Days_PayDate[i] > 0) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    SwapStartT = ((double)Schedule->Days_ForwardStart[i]) / denominator;
                    SwapEndT = SwapStartT + Schedule->RefSwapMaturity;
                    Pay_T = ((double)Schedule->Days_PayDate[i]) / 365.0;

                    if (Schedule->Days_ForwardStart[i] <= 0) UseHistorySOFR = 1;
                    else UseHistorySOFR = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = FXCurve.Interpolated_Rate(SwapEndT);

                    FreqMonth = 12.0 / (double)Schedule->NSwapPayAnnual;
                    ResultRefRate[i] = Calc_Forward_SOFR_Swap(RefCurve, RefCurve, DiscCurve, SwapStartT, Schedule->RefSwapMaturity, FreqMonth, Schedule->HolidayFlag_Ref, Schedule->NHolidays_Ref, Schedule->Days_Holidays_Ref, NSaturSunDay_List[i], SaturSunDay_List[i], Schedule->NRefHistory, Schedule->RefHistoryDate, Schedule->RefHistory, denominator, Schedule->LockOutRef, Schedule->LookBackRef, Schedule->ObservationShift);
                    if (ConvAdjFlag > 0)
                    {

                    }

                    ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * ((double)(Schedule->Days_EndDate[i] - Schedule->Days_StartDate[i])) / denominator;
                    ResultDF[i] = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                    DiscCFArray[i] = ResultCPN[i] * ResultDF[i];
                }
                else
                {
                    ResultRefRate[i] = Schedule->FixedRefRate[i];
                    ResultCPN[i] = 0.0;
                    ResultDF[i] = 0.0;
                    DiscCFArray[i] = 0.0;
                }
            }
        }
    }
    else
    {
        //////////////
        // 고정금리 //
        //////////////

        for (i = 0; i < Schedule->NCF; i++)
        {
            // 이미 쿠폰 지급한 과거인지 확인
            PrevFlag = 1;
            if (Schedule->Days_PayDate[i] > 0) PrevFlag = 0;

            if (PrevFlag == 0)
            {
                Frac_T0 = ((double)Schedule->Days_StartDate[i]) / denominator;
                Frac_T1 = ((double)Schedule->Days_EndDate[i]) / denominator;
                Pay_T = ((double)Schedule->Days_PayDate[i]) / 365.0;
                
                if (CRSFlag == 0) FX = 1.0;
                else  FX = FXCurve.Interpolated_Rate(((double)Schedule->Days_EndDate[i])/365.0);
                
                DiscPay = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                //FixedLeg_PartialValue(
                //    CRSFlag, DiscCurve, FXCurve, Frac_T0, Frac_T1, Pay_T, Schedule->CPN[i], Schedule->NotionalAmount,
                //    ResultRefRate + i, ResultCPN + i, ResultDF + i, DiscCFArray + i);
                ResultRefRate[i] = 0.0;
                ResultCPN[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] * ((double)(Schedule->Days_EndDate[i] - Schedule->Days_StartDate[i]))/denominator;
                ResultDF[i] = DiscPay;
                DiscCFArray[i] = ResultDF[i] * ResultCPN[i];
                ResultRefRate[i] = Schedule->CPN[i];
            }
            else
            {
                ResultRefRate[i] = 0.0;
                ResultCPN[i] = 0.0;
                ResultDF[i] = 0.0;
                DiscCFArray[i] = 0.0;
            }
        }
    }
    value = sumation(DiscCFArray, Schedule->NCF);
    return value;
}
long SwapPricer(
    long PriceDate_C,
    long CalcCRSFlag,

    SCHD* RcvSchedule,
    long RcvDisc_NTerm,
    double* RcvDisc_Term,
    double* RcvDisc_Rate,
    long RcvRef_NTerm,
    double* RcvRef_Term,
    double* RcvRef_Rate,

    SCHD* PaySchedule,
    long PayDisc_NTerm,
    double* PayDisc_Term,
    double* PayDisc_Rate,
    long PayRef_NTerm,
    double* PayRef_Term,
    double* PayRef_Rate,

    long Rcv_NFX,
    double* Rcv_TermFX,
    double* Rcv_FX,

    long Pay_NFX,
    double* Pay_TermFX,
    double* Pay_FX,

    long GreekFlag,
    double* ResultPrice,
    double* ResultRefRate,
    double* ResultCPN,
    double* ResultDF,

    double* PV01,
    double* KeyRateRcvPV01,
    double* KeyRatePayPV01,
    long NSaturSunDayForSwap,
    long* SaturSunDayForSwap,
    long PricingOnly,

    long RcvConvexityAdjFlag,       // RcvLeg Convexity 보정Flag
    long PayConvexityAdjFlag,       // PayLeg Convexity 보정Flag
    long NRcvConvexAdjVol,          // Rcv Vol개수
    long NPayConvexAdjVol,          // Pay Vol개수
    double* RcvConvAdjVolTerm,      // Rcv Vol Term
    double* RcvConvAdjVol,          // Rcv Vol Term
    double* PayConvAdjVolTerm,      // Rcv Vol Term
    double* PayConvAdjVol           // Pay Vol Term
    )
{
    long i, j;
    long N, M;
    long s;
    long CalcCurrentSwapFlag;

    double RcvValueUp, RcvValueDn, PayValueUp, PayValueDn;

    double Rcv_T_Mat = ((double)DayCountAtoB(PriceDate_C, RcvSchedule->NotionalPayDate_C)) / 365.0;
    double Pay_T_Mat = ((double)DayCountAtoB(PriceDate_C, PaySchedule->NotionalPayDate_C)) / 365.0;

    double Rcv_FXMat;
    if (CalcCRSFlag == 0) Rcv_FXMat = 1.0;
    else Rcv_FXMat = Interpolate_Linear(Rcv_TermFX, Rcv_FX, Rcv_NFX, Rcv_T_Mat);

    double Pay_FXMat;
    if (CalcCRSFlag == 0) Pay_FXMat = 1.0;
    else Pay_FXMat = Interpolate_Linear(Pay_TermFX, Pay_FX, Pay_NFX, Pay_T_Mat);

    if (RcvSchedule->NAFlag != 0) RcvSchedule->NAFlag = 1;
    if (PaySchedule->NAFlag != 0) PaySchedule->NAFlag = 1;

    curveinfo Rcv_DiscCurve(RcvDisc_NTerm, RcvDisc_Term, RcvDisc_Rate);
    curveinfo Rcv_RefCurve(RcvRef_NTerm, RcvRef_Term, RcvRef_Rate);
    curveinfo Rcv_FXCurve(Rcv_NFX, Rcv_TermFX, Rcv_FX);

    curveinfo Pay_DiscCurve(PayDisc_NTerm, PayDisc_Term, PayDisc_Rate);
    curveinfo Pay_RefCurve(PayRef_NTerm, PayRef_Term, PayRef_Rate);
    curveinfo Pay_FXCurve(Pay_NFX, Pay_TermFX, Pay_FX);

    double RcvValue, PayValue, CurrentIRS;
    double* Rcv_DiscCFArray = (double*)malloc(sizeof(double) * RcvSchedule->NCF);
    double* Pay_DiscCFArray = (double*)malloc(sizeof(double) * PaySchedule->NCF);

    ////////////////////
    // 각 Leg Pricing //
    ////////////////////

    RcvValue = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve, Rcv_RefCurve, Rcv_FXCurve, ResultRefRate, ResultCPN, ResultDF, Rcv_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
    PayValue = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve, Pay_FXCurve, ResultRefRate + RcvSchedule->NCF, ResultCPN + RcvSchedule->NCF, ResultDF + RcvSchedule->NCF, Rcv_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);

    //////////////////
    // Notional 반영
    //////////////////

    if (RcvSchedule->NAFlag == 1)
    {
        ResultDF[RcvSchedule->NCF + PaySchedule->NCF] = Calc_Discount_Factor(Rcv_DiscCurve.Term, Rcv_DiscCurve.Rate, Rcv_DiscCurve.nterm(), ((double)(RcvSchedule->Days_Notional)) / 365.0);// ResultDF[RcvSchedule->NCF - 1];
        ResultRefRate[RcvSchedule->NCF + PaySchedule->NCF] = 0.0;
        ResultCPN[RcvSchedule->NCF + PaySchedule->NCF] = RcvSchedule->NotionalAmount * Rcv_FXMat;
        if (CalcCRSFlag == 0) RcvValue += RcvSchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF];
        else RcvValue += RcvSchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF] * Rcv_FXMat;
    }

    if (PaySchedule->NAFlag == 1)
    {
        ResultDF[RcvSchedule->NCF + PaySchedule->NCF + 1] = Calc_Discount_Factor(Pay_DiscCurve.Term, Pay_DiscCurve.Rate, Pay_DiscCurve.nterm(), ((double)(PaySchedule->Days_Notional)) / 365.0);//ResultDF[RcvSchedule->NCF + PaySchedule->NCF - 1];
        ResultRefRate[RcvSchedule->NCF + PaySchedule->NCF + 1] = 0.0;
        ResultCPN[RcvSchedule->NCF + PaySchedule->NCF + 1] = PaySchedule->NotionalAmount * Pay_FXMat;
        if (CalcCRSFlag == 0) PayValue += PaySchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF + 1];
        else PayValue += PaySchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF + 1] * Pay_FXMat;
    }

    CalcCurrentSwapFlag = RcvSchedule->FixedFlotype + PaySchedule->FixedFlotype;
    if (CalcCurrentSwapFlag == 1 && PricingOnly == 1)
    {
        if (RcvSchedule->FixedFlotype == 0)
        {
            if (RcvSchedule->ReferenceType < 2 && PaySchedule->ReferenceType < 2) CurrentIRS = Calc_Current_IRS(CalcCRSFlag, Pay_DiscCurve, Pay_RefCurve, Rcv_DiscCurve, Pay_FXCurve, Rcv_FXCurve, PaySchedule, RcvSchedule);
            else CurrentIRS = Calc_Current_SOFR_Swap(CalcCRSFlag, Pay_DiscCurve, Pay_RefCurve, Rcv_DiscCurve, Pay_FXCurve, Rcv_FXCurve, PaySchedule, RcvSchedule, PaySchedule->LockOutRef, PaySchedule->LookBackRef, PaySchedule->ObservationShift, NSaturSunDayForSwap, SaturSunDayForSwap);
        }
        else
        {
            if (RcvSchedule->ReferenceType < 2 && PaySchedule->ReferenceType < 2) CurrentIRS = Calc_Current_IRS(CalcCRSFlag, Rcv_DiscCurve, Rcv_RefCurve, Pay_DiscCurve, Rcv_FXCurve, Pay_FXCurve, RcvSchedule, PaySchedule);
            else CurrentIRS = Calc_Current_SOFR_Swap(CalcCRSFlag, Rcv_DiscCurve, Rcv_RefCurve, Pay_DiscCurve, Rcv_FXCurve, Pay_FXCurve, RcvSchedule, PaySchedule, RcvSchedule->LockOutRef, RcvSchedule->LookBackRef, RcvSchedule->ObservationShift, NSaturSunDayForSwap, SaturSunDayForSwap);
        }
    }
    else
    {
        CurrentIRS = 0.0;
    }


    if (GreekFlag > 0)
    {
        double T;

        double* Rcv_Temp_RefRate = (double*)malloc(sizeof(double) * RcvSchedule->NCF);
        double* Rcv_Temp_ResultCPN = (double*)malloc(sizeof(double) * RcvSchedule->NCF);
        double* Rcv_Temp_ResultDF = (double*)malloc(sizeof(double) * RcvSchedule->NCF);
        double* Rcv_Temp_DiscCFArray = (double*)malloc(sizeof(double) * RcvSchedule->NCF);

        double* Pay_Temp_RefRate = (double*)malloc(sizeof(double) * PaySchedule->NCF);
        double* Pay_Temp_ResultCPN = (double*)malloc(sizeof(double) * PaySchedule->NCF);
        double* Pay_Temp_ResultDF = (double*)malloc(sizeof(double) * PaySchedule->NCF);
        double* Pay_Temp_DiscCFArray = (double*)malloc(sizeof(double) * PaySchedule->NCF);

        // Receive Leg
        double* RcvDisc_Rate_Up = (double*)malloc(sizeof(double) * RcvDisc_NTerm);
        double* RcvDisc_Rate_Dn = (double*)malloc(sizeof(double) * RcvDisc_NTerm);
        for (i = 0; i < RcvDisc_NTerm; i++)
        {
            RcvDisc_Rate_Up[i] = RcvDisc_Rate[i] + 0.0001;
            RcvDisc_Rate_Dn[i] = RcvDisc_Rate[i] - 0.0001;
        }

        double* RcvRef_Rate_Up = (double*)malloc(sizeof(double) * RcvRef_NTerm);
        double* RcvRef_Rate_Dn = (double*)malloc(sizeof(double) * RcvRef_NTerm);
        for (i = 0; i < RcvRef_NTerm; i++)
        {
            RcvRef_Rate_Up[i] = RcvRef_Rate[i] + 0.0001;
            RcvRef_Rate_Dn[i] = RcvRef_Rate[i] - 0.0001;
        }


        // Pay Leg
        double* PayDisc_Rate_Up = (double*)malloc(sizeof(double) * PayDisc_NTerm);
        double* PayDisc_Rate_Dn = (double*)malloc(sizeof(double) * PayDisc_NTerm);
        for (i = 0; i < PayDisc_NTerm; i++)
        {
            PayDisc_Rate_Up[i] = PayDisc_Rate[i] + 0.0001;
            PayDisc_Rate_Dn[i] = PayDisc_Rate[i] - 0.0001;
        }

        double* PayRef_Rate_Up = (double*)malloc(sizeof(double) * PayRef_NTerm);
        double* PayRef_Rate_Dn = (double*)malloc(sizeof(double) * PayRef_NTerm);
        for (i = 0; i < PayRef_NTerm; i++)
        {
            PayRef_Rate_Up[i] = PayRef_Rate[i] + 0.0001;
            PayRef_Rate_Dn[i] = PayRef_Rate[i] - 0.0001;
        }

        curveinfo Rcv_DiscCurve_Up(RcvDisc_NTerm, RcvDisc_Term, RcvDisc_Rate_Up);
        curveinfo Rcv_DiscCurve_Dn(RcvDisc_NTerm, RcvDisc_Term, RcvDisc_Rate_Up);

        curveinfo Rcv_RefCurve_Up(RcvRef_NTerm, RcvRef_Term, RcvRef_Rate_Up);
        curveinfo Rcv_RefCurve_Dn(RcvRef_NTerm, RcvRef_Term, RcvRef_Rate_Dn);

        curveinfo Pay_DiscCurve_Up(PayDisc_NTerm, PayDisc_Term, PayDisc_Rate_Up);
        curveinfo Pay_DiscCurve_Dn(PayDisc_NTerm, PayDisc_Term, PayDisc_Rate_Dn);

        curveinfo Pay_RefCurve_Up(PayRef_NTerm, PayRef_Term, PayRef_Rate_Up);
        curveinfo Pay_RefCurve_Dn(PayRef_NTerm, PayRef_Term, PayRef_Rate_Dn);

        // RCV Leg

        RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Up, Rcv_RefCurve, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
        RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
        RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Dn, Rcv_RefCurve, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
        RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
        PV01[0] = (RcvValueUp - RcvValueDn) * 0.5;

        RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve, Rcv_RefCurve_Up, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
        RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
        RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve, Rcv_RefCurve_Dn, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
        RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
        PV01[1] = (RcvValueUp - RcvValueDn) * 0.5;

        N = Rcv_DiscCurve.nterm();
        M = Rcv_RefCurve.nterm();

        if (N == M)
        {
            s = 0;
            for (i = 0; i < N; i++)
            {
                if (Rcv_DiscCurve.Term[i] == Rcv_RefCurve.Term[i])
                {
                    s += 1;
                }
            }

            if (s == N)
            {
                RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Up, Rcv_RefCurve_Up, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Dn, Rcv_RefCurve_Dn, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                PV01[2] = (RcvValueUp - RcvValueDn) * 0.5;
            }
        }

        for (i = 0; i < N; i++)
        {
            T = ((double)(RcvSchedule->Days_PayDate[RcvSchedule->NCF - 1])) / 365.0;
            if (RcvDisc_Term[i] <= T)
            {
                for (j = 0; j < N; j++)
                {
                    if (i == j)
                    {
                        Rcv_DiscCurve_Up.Rate[j] = RcvDisc_Rate[j] + 0.0001;
                        Rcv_DiscCurve_Dn.Rate[j] = RcvDisc_Rate[j] - 0.0001;
                    }
                    else
                    {
                        Rcv_DiscCurve_Up.Rate[j] = RcvDisc_Rate[j];
                        Rcv_DiscCurve_Dn.Rate[j] = RcvDisc_Rate[j];
                    }
                }
                RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Up, Rcv_RefCurve, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Dn, Rcv_RefCurve, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                KeyRateRcvPV01[i] = (RcvValueUp - RcvValueDn) * 0.5;
            }
            else
            {
                KeyRateRcvPV01[i] = 0.0;
            }
        }

        for (i = 0; i < M; i++)
        {
            T = ((double)(RcvSchedule->Days_PayDate[RcvSchedule->NCF - 1])) / 365.0;
            if (RcvRef_Term[i] <= T)
            {
                for (j = 0; j < M; j++)
                {
                    if (i == j)
                    {
                        Rcv_RefCurve_Up.Rate[j] = RcvRef_Rate[j] + 0.0001;
                        Rcv_RefCurve_Dn.Rate[j] = RcvRef_Rate[j] - 0.0001;
                    }
                    else
                    {
                        Rcv_RefCurve_Up.Rate[j] = RcvRef_Rate[j];
                        Rcv_RefCurve_Dn.Rate[j] = RcvRef_Rate[j];
                    }
                }
                RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve, Rcv_RefCurve_Up, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve, Rcv_RefCurve_Dn, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                KeyRateRcvPV01[i + N] = (RcvValueUp - RcvValueDn) * 0.5;
            }
            else
            {
                KeyRateRcvPV01[i + N] = 0.0;
            }
        }

        if (N == M)
        {
            s = 0;
            for (i = 0; i < N; i++)
            {
                if (Rcv_DiscCurve.Term[i] == Rcv_RefCurve.Term[i])
                {
                    s += 1;
                }
            }

            T = ((double)(RcvSchedule->Days_PayDate[RcvSchedule->NCF - 1])) / 365.0;

            if (s == N)
            {
                for (i = 0; i < N; i++)
                {
                    if (RcvRef_Term[i] <= T)
                    {
                        for (j = 0; j < N; j++)
                        {
                            if (i == j)
                            {
                                Rcv_DiscCurve_Up.Rate[j] = RcvDisc_Rate[j] + 0.0001;
                                Rcv_DiscCurve_Dn.Rate[j] = RcvDisc_Rate[j] - 0.0001;
                                Rcv_RefCurve_Up.Rate[j] = RcvRef_Rate[j] + 0.0001;
                                Rcv_RefCurve_Dn.Rate[j] = RcvRef_Rate[j] - 0.0001;
                            }
                            else
                            {
                                Rcv_DiscCurve_Up.Rate[j] = RcvDisc_Rate[j];
                                Rcv_DiscCurve_Dn.Rate[j] = RcvDisc_Rate[j];
                                Rcv_RefCurve_Up.Rate[j] = RcvRef_Rate[j];
                                Rcv_RefCurve_Dn.Rate[j] = RcvRef_Rate[j];
                            }
                        }
                        RcvValueUp = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Up, Rcv_RefCurve_Up, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                        RcvValueUp += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                        RcvValueDn = LegValue(CalcCRSFlag, RcvSchedule, Rcv_DiscCurve_Dn, Rcv_RefCurve_Dn, Rcv_FXCurve, Rcv_Temp_RefRate, Rcv_Temp_ResultCPN, Rcv_Temp_ResultDF, Rcv_Temp_DiscCFArray, RcvConvexityAdjFlag, NRcvConvexAdjVol, RcvConvAdjVolTerm, RcvConvAdjVol);
                        RcvValueDn += (RcvSchedule->NotionalAmount * (double)RcvSchedule->NAFlag) * Rcv_Temp_ResultDF[RcvSchedule->NCF - 1] * Rcv_FXMat;
                        KeyRateRcvPV01[i + N + M] = (RcvValueUp - RcvValueDn) * 0.5;
                    }
                    else
                    {
                        KeyRateRcvPV01[i + N + M] = 0.0;
                    }
                }
            }
        }

        // PAY Leg
        PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Up, Pay_RefCurve, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
        PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
        PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Dn, Pay_RefCurve, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
        PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
        PV01[3] = (PayValueUp - PayValueDn) * 0.5;

        PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve_Up, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
        PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
        PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve_Dn, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
        PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
        PV01[4] = (PayValueUp - PayValueDn) * 0.5;

        N = Pay_DiscCurve.nterm();
        M = Pay_RefCurve.nterm();

        if (N == M)
        {
            s = 0;
            for (i = 0; i < N; i++)
            {
                if (Pay_DiscCurve.Term[i] == Pay_RefCurve.Term[i])
                {
                    s += 1;
                }
            }

            if (s == N)
            {
                PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Up, Pay_RefCurve_Up, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Dn, Pay_RefCurve_Dn, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                PV01[5] = (PayValueUp - PayValueDn) * 0.5;
            }
        }

        for (i = 0; i < N; i++)
        {
            T = ((double)(PaySchedule->Days_PayDate[PaySchedule->NCF - 1])) / 365.0;
            if (PayDisc_Term[i] <= T)
            {
                for (j = 0; j < N; j++)
                {
                    if (i == j)
                    {
                        Pay_DiscCurve_Up.Rate[j] = PayDisc_Rate[j] + 0.0001;
                        Pay_DiscCurve_Dn.Rate[j] = PayDisc_Rate[j] - 0.0001;
                    }
                    else
                    {
                        Pay_DiscCurve_Up.Rate[j] = PayDisc_Rate[j];
                        Pay_DiscCurve_Dn.Rate[j] = PayDisc_Rate[j];
                    }
                }
                PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Up, Pay_RefCurve, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Dn, Pay_RefCurve, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                KeyRatePayPV01[i] = (PayValueUp - PayValueDn) * 0.5;
            }
            else
            {
                KeyRatePayPV01[i] = 0.0;
            }

        }

        for (i = 0; i < M; i++)
        {
            T = ((double)(PaySchedule->Days_PayDate[PaySchedule->NCF - 1])) / 365.0;
            if (PayRef_Term[i] <= T)
            {
                for (j = 0; j < M; j++)
                {
                    if (i == j)
                    {
                        Pay_RefCurve_Up.Rate[j] = PayRef_Rate[j] + 0.0001;
                        Pay_RefCurve_Dn.Rate[j] = PayRef_Rate[j] - 0.0001;
                    }
                    else
                    {
                        Pay_RefCurve_Up.Rate[j] = PayRef_Rate[j];
                        Pay_RefCurve_Dn.Rate[j] = PayRef_Rate[j];
                    }
                }
                PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve_Up, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve_Dn, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                KeyRatePayPV01[i + N] = (PayValueUp - PayValueDn) * 0.5;
            }
            else
            {
                KeyRatePayPV01[i + N] = 0.0;
            }
        }

        if (N == M)
        {
            s = 0;
            for (i = 0; i < N; i++)
            {
                if (Pay_DiscCurve.Term[i] == Pay_RefCurve.Term[i])
                {
                    s += 1;
                }
            }


            T = ((double)(PaySchedule->Days_PayDate[PaySchedule->NCF - 1])) / 365.0;
            if (s == N)
            {
                for (i = 0; i < N; i++)
                {
                    if (PayRef_Term[i] <= T)
                    {
                        for (j = 0; j < N; j++)
                        {
                            if (i == j)
                            {
                                Pay_DiscCurve_Up.Rate[j] = PayDisc_Rate[j] + 0.0001;
                                Pay_DiscCurve_Dn.Rate[j] = PayDisc_Rate[j] - 0.0001;
                                Pay_RefCurve_Up.Rate[j] = PayRef_Rate[j] + 0.0001;
                                Pay_RefCurve_Dn.Rate[j] = PayRef_Rate[j] - 0.0001;
                            }
                            else
                            {
                                Pay_DiscCurve_Up.Rate[j] = PayDisc_Rate[j];
                                Pay_DiscCurve_Dn.Rate[j] = PayDisc_Rate[j];
                                Pay_RefCurve_Up.Rate[j] = PayRef_Rate[j];
                                Pay_RefCurve_Dn.Rate[j] = PayRef_Rate[j];
                            }
                        }
                        PayValueUp = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Up, Pay_RefCurve_Up, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                        PayValueUp += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                        PayValueDn = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve_Dn, Pay_RefCurve_Dn, Pay_FXCurve, Pay_Temp_RefRate, Pay_Temp_ResultCPN, Pay_Temp_ResultDF, Pay_Temp_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);
                        PayValueDn += (PaySchedule->NotionalAmount * (double)PaySchedule->NAFlag) * Pay_Temp_ResultDF[PaySchedule->NCF - 1] * Pay_FXMat;
                        KeyRatePayPV01[i + N + M] = (PayValueUp - PayValueDn) * 0.5;
                    }
                    else
                    {
                        KeyRatePayPV01[i + N + M] = 0.0;
                    }
                }
            }
        }

        free(Rcv_Temp_RefRate);
        free(Rcv_Temp_ResultCPN);
        free(Rcv_Temp_ResultDF);
        free(Rcv_Temp_DiscCFArray);

        free(Pay_Temp_RefRate);
        free(Pay_Temp_ResultCPN);
        free(Pay_Temp_ResultDF);
        free(Pay_Temp_DiscCFArray);


        free(RcvDisc_Rate_Up);
        free(RcvDisc_Rate_Dn);

        free(RcvRef_Rate_Up);
        free(RcvRef_Rate_Dn);

        free(PayDisc_Rate_Up);
        free(PayDisc_Rate_Dn);

        free(PayRef_Rate_Up);
        free(PayRef_Rate_Dn);
    }

    ResultPrice[0] = CurrentIRS;
    ResultPrice[1] = RcvValue;
    ResultPrice[2] = PayValue;

    free(Rcv_DiscCFArray);
    free(Pay_DiscCFArray);

    return 1;
}

long ErrorCheckIRSwap_Excel(
    long PriceDate_Exl,                // PricingDate ExcelType
    long GreekFlag,                    // Greek산출 Flag
    long NAFlag,                    // Notional Amount 사용 Flag
    long* CRS_Flag,                    // [0]CRS Pricing Flag [1]FX선도 Term 개수
    double* CRS_Info,                // [0~FX개수-1] FX Forward Term, [FX개수-1~2*FX개수-1] FX Forward

    long Rcv_RefRateType,            // Rcv 기초금리 0: Libor/CD 1: Swap 2: SOFR 3:SOFR Swap
    long Rcv_SwapYearlyNPayment,    // Rcv_RefRateType가 1, 3일 때 스왑 연 지급회수
    double Rcv_SwapMaturity,        // Rcv_RefRateType가 1, 3일 때 스왑만기
    long Rcv_FixFloFlag,            // Rcv Fix/Flo Flag
    long Rcv_DayCount,                // Rcv DayCountConvention 0:Act365  1: Act360

    double Rcv_NotionalAMT,            // Rcv Leg Notional Amount
    long Rcv_NotionalPayDate,        // Rcv Leg Notional Payment Date
    long RcvDisc_NTerm,                // Rcv Leg 할인 금리 Term 개수
    double* RcvDisc_Term,            // Rcv Leg 할인 금리 Term Array
    double* RcvDisc_Rate,            // Rcv Leg 할인 금리 Rate Array 

    long RcvRef_NTerm,                // Rcv Leg 레퍼런스 금리 Term 개수
    double* RcvRef_Term,            // Rcv Leg 레퍼런스 금리 Term Array
    double* RcvRef_Rate,            // Rcv Leg 레퍼런스 금리 Rate Array
    long NRcvCF,                    // Rcv Leg CashFlow 개수
    long* RcvCashFlowSchedule,        // Rcv Forward Start, End, 기산, 기말, 지급일
    double* Rcv_Slope,                // Rcv Leg 변동금리 기울기 Array

    double* Rcv_CPN,                // Rcv Leg 고정쿠폰 Array
    double* Rcv_FixedRefRate,        // Rcv Leg 과거 확정금리 Array
    long Pay_RefRateType,            // Pay 기초금리 0: Libor/CD 1: Swap 2: SOFR 3:SOFR Swap
    long Pay_SwapYearlyNPayment,    // Pay_RefRateType가 1, 3일 때 스왑 연 지급회수
    double Pay_SwapMaturity,        // Pay_RefRateType가 1, 3일 때 스왑만기

    long Pay_FixFloFlag,            // Pay Fix/Flo Flag
    long Pay_DayCount,                // Pay DayCountConvention 0:Act365  1: Act360
    double Pay_NotionalAMT,            // Pay Leg Notional Amount
    long Pay_NotionalPayDate,        // Pay Leg Notional Payment Date
    long PayDisc_NTerm,                // Pay Leg 할인 금리 Term 개수

    double* PayDisc_Term,            // Pay Leg 할인 금리 Term Array
    double* PayDisc_Rate,            // Pay Leg 할인 금리 Rate Array 
    long PayRef_NTerm,                // Pay Leg 레퍼런스 금리 Term 개수
    double* PayRef_Term,            // Pay Leg 레퍼런스 금리 Term Array
    double* PayRef_Rate,            // Pay Leg 할인 금리 Rate Array 

    long NPayCF,                    // Pay Leg CashFlow 개수
    long* PayCashFlowSchedule,        // Pay Forward Start, End, 기산, 기말, 지급일
    double* Pay_Slope,                // Pay Leg 변동금리 기울기 Array
    double* Pay_CPN,                // Pay Leg 고정쿠폰 Array
    double* Pay_FixedRefRate,        // Pay Leg 과거 확정금리 Array

    long* HolidayCalcFlag,            // Holiday관련 인풋 Flag [0]: Rcv [1]: Pay
    long* NHolidays,                // Holiday 개수 [0] NRcvRef [1] NPayRef
    long* Holidays                    // Holiday Exceltype
)
{
    long i;


    long* Rcv_ForwardStartExl = RcvCashFlowSchedule;
    long* Rcv_ForwardEndExl = RcvCashFlowSchedule + NRcvCF;
    long* Rcv_StartDateExl = RcvCashFlowSchedule + 2 * NRcvCF;
    long* Rcv_EndDateExl = RcvCashFlowSchedule + 3 * NRcvCF;
    long* Rcv_PayDateExl = RcvCashFlowSchedule + 4 * NRcvCF;

    long* Pay_ForwardStartExl = PayCashFlowSchedule;
    long* Pay_ForwardEndExl = PayCashFlowSchedule + NPayCF;
    long* Pay_StartDateExl = PayCashFlowSchedule + 2 * NPayCF;
    long* Pay_EndDateExl = PayCashFlowSchedule + 3 * NPayCF;
    long* Pay_PayDateExl = PayCashFlowSchedule + 4 * NPayCF;

    if (PriceDate_Exl <= 0 || PriceDate_Exl > Rcv_PayDateExl[NRcvCF - 1] || PriceDate_Exl > Pay_PayDateExl[NPayCF - 1] || PriceDate_Exl < Rcv_ForwardStartExl[0] - 1000 || PriceDate_Exl < Pay_ForwardStartExl[0] - 1000) return -1;

    if (GreekFlag != 0 && GreekFlag != 1 && GreekFlag != 999) return -2;

    if (NAFlag != 0 && NAFlag != 1) return -3;

    long CRSPricingFlag = CRS_Flag[0];
    long CRS_NFX_Term = CRS_Flag[1];
    double* CRS_FX_Term = CRS_Info;
    double* CRS_FX_Rate = CRS_Info + CRS_NFX_Term;

    if (CRSPricingFlag != 0 && CRSPricingFlag != 1) return -4;

    if (CRS_FX_Rate[0] < 0.0) return -5;

    for (i = 0; i < CRS_NFX_Term; i++)
    {
        if (i > 0)
        {
            if (CRS_FX_Term[i] < CRS_FX_Term[i - 1]) return -5;
            if (CRS_FX_Rate[i] < 0.0) return -5;
        }
    }

    if (Rcv_RefRateType < 0 || Rcv_RefRateType > 5) return -6;
    if (Rcv_SwapYearlyNPayment <= 0 || Rcv_SwapYearlyNPayment > 12) return -7;
    if (Rcv_SwapMaturity < 0.0) return -8;
    if (Rcv_FixFloFlag != 0 && Rcv_FixFloFlag != 1) return -9;
    if (Rcv_DayCount != 0 && Rcv_DayCount != 1 && Rcv_DayCount != 2 && Rcv_DayCount != 3) return -10;
    if (Rcv_NotionalAMT < 0.0) return -11;
    if (Rcv_NotionalPayDate < PriceDate_Exl) return -12;
    if (RcvDisc_NTerm < 1) return -13;

    for (i = 0; i < RcvDisc_NTerm; i++)
    {
        if (i > 0)
        {
            if (RcvDisc_Term[i] < RcvDisc_Term[i - 1]) return -14;
        }
    }

    if (RcvRef_NTerm < 1) return -16;
    for (i = 0; i < RcvRef_NTerm; i++)
    {
        if (i > 0)
        {
            if (RcvRef_Term[i] < RcvRef_Term[i - 1]) return -17;
        }
    }

    for (i = 0; i < NRcvCF; i++)
    {
        if (Rcv_ForwardStartExl[i] >= Rcv_ForwardEndExl[i] || Rcv_PayDateExl[i] < Rcv_ForwardEndExl[i]) return -20;
    }

    if (Rcv_RefRateType < 0 || Rcv_RefRateType > 5) return -6;
    if (Rcv_RefRateType == 1 || Rcv_RefRateType == 3)
    {
        if (Rcv_SwapYearlyNPayment <= 0 || Rcv_SwapYearlyNPayment > 12) return -7;
    }
    if (Rcv_SwapMaturity < 0.0) return -8;
    if (Rcv_FixFloFlag != 0 && Rcv_FixFloFlag != 1) return -9;
    if (Rcv_DayCount != 0 && Rcv_DayCount != 1) return -10;
    if (Rcv_NotionalAMT < 0.0) return -11;
    if (Rcv_NotionalPayDate < PriceDate_Exl) return -12;
    if (RcvDisc_NTerm < 1) return -13;

    for (i = 0; i < RcvDisc_NTerm; i++)
    {
        if (i > 0)
        {
            if (RcvDisc_Term[i] < RcvDisc_Term[i - 1]) return -14;
        }
    }

    if (RcvRef_NTerm < 1) return -16;
    for (i = 0; i < RcvRef_NTerm; i++)
    {
        if (i > 0)
        {
            if (RcvRef_Term[i] < RcvRef_Term[i - 1]) return -17;
        }
    }

    for (i = 0; i < NRcvCF; i++)
    {
        if (Rcv_ForwardStartExl[i] >= Rcv_ForwardEndExl[i] || Rcv_PayDateExl[i] < Rcv_ForwardEndExl[i]) return -20;
    }

    //
    if (Pay_RefRateType < 0 || Pay_RefRateType > 5) return -6;
    if (Pay_RefRateType == 1 || Pay_RefRateType == 3)
    {
        if (Pay_SwapYearlyNPayment <= 0 || Pay_SwapYearlyNPayment > 12) return -7;
    }
    if (Pay_SwapMaturity < 0.0) return -8;
    if (Pay_FixFloFlag != 0 && Pay_FixFloFlag != 1) return -9;
    if (Pay_DayCount != 0 && Pay_DayCount != 1&& Pay_DayCount != 2 && Pay_DayCount != 3) return -10;
    if (Pay_NotionalAMT < 0.0) return -11;
    if (Pay_NotionalPayDate < PriceDate_Exl) return -12;
    if (PayDisc_NTerm < 1) return -13;

    for (i = 0; i < PayDisc_NTerm; i++)
    {
        if (i > 0)
        {
            if (PayDisc_Term[i] < PayDisc_Term[i - 1]) return -14;
        }
    }

    if (PayRef_NTerm < 1) return -16;
    for (i = 0; i < PayRef_NTerm; i++)
    {
        if (i > 0)
        {
            if (PayRef_Term[i] < PayRef_Term[i - 1]) return -17;
        }
    }

    for (i = 0; i < NPayCF; i++)
    {
        if (Pay_ForwardStartExl[i] >= Pay_ForwardEndExl[i] || Pay_PayDateExl[i] < Pay_ForwardEndExl[i]) return -20;
    }

    return 0;
}

DLLEXPORT(long) IRSwap_Excel(
    long PriceDate_Exl,                // PricingDate ExcelType
    long GreekFlag,                    // Greek산출 Flag
    long NAFlag,                       // Notional 교환 Flag (0:NA교환X, 1:NA교환O, 2:NA교환X TextDump, 3: NA교환O TextDump)
    long* CRS_Flag,                    // [0]CRS Pricing Flag [1]FX선도 Term 개수
    double* CRS_Info,                  // [0~FX개수-1] FX Forward Term, [FX개수-1~2*FX개수-1] FX Forward

    long Rcv_RefRateType,              // Rcv 기초금리 0: Libor/CD 1: Swap 2: SOFR 3:SOFR Swap
    long Rcv_SwapYearlyNPayment,       // Rcv_RefRateType가 1, 3일 때 스왑 연 지급회수
    double Rcv_SwapMaturity,           // Rcv_RefRateType가 1, 3일 때 스왑만기
    long Rcv_FixFloFlag,               // Rcv Fix/Flo Flag
    long Rcv_DayCount,                 // Rcv DayCountConvention 0:Act365  1: Act360

    double Rcv_NotionalAMT,            // Rcv Leg Notional Amount
    long Rcv_NotionalPayDate,          // Rcv Leg Notional Payment Date
    long RcvDisc_NTerm,                // Rcv Leg 할인 금리 Term 개수
    double* RcvDisc_Term,              // Rcv Leg 할인 금리 Term Array
    double* RcvDisc_Rate,              // Rcv Leg 할인 금리 Rate Array 

    long RcvRef_NTerm,                 // Rcv Leg 레퍼런스 금리 Term 개수
    double* RcvRef_Term,               // Rcv Leg 레퍼런스 금리 Term Array
    double* RcvRef_Rate,               // Rcv Leg 레퍼런스 금리 Rate Array
    long NRcvCF,                       // Rcv Leg CashFlow 개수
    long* RcvCashFlowSchedule,         // Rcv Forward Start, End, 기산, 기말, 지급일 ExlDate

    double* Rcv_Slope,                 // Rcv Leg 변동금리 기울기 Array
    double* Rcv_CPN,                   // Rcv Leg 고정쿠폰 Array
    double* Rcv_FixedRefRate,          // Rcv Leg 과거 확정금리 Array
    long Pay_RefRateType,              // Pay 기초금리 0: Libor/CD 1: Swap 2: SOFR 3:SOFR Swap
    long Pay_SwapYearlyNPayment,       // Pay_RefRateType가 1, 3일 때 스왑 연 지급회수

    double Pay_SwapMaturity,            // Pay_RefRateType가 1, 3일 때 스왑만기
    long Pay_FixFloFlag,                // Pay Fix/Flo Flag
    long Pay_DayCount,                  // Pay DayCountConvention 0:Act365  1: Act360
    double Pay_NotionalAMT,             // Pay Leg Notional Amount
    long Pay_NotionalPayDate,           // Pay Leg Notional Payment Date

    long PayDisc_NTerm,                 // Pay Leg 할인 금리 Term 개수
    double* PayDisc_Term,               // Pay Leg 할인 금리 Term Array
    double* PayDisc_Rate,               // Pay Leg 할인 금리 Rate Array 
    long PayRef_NTerm,                  // Pay Leg 레퍼런스 금리 Term 개수
    double* PayRef_Term,                // Pay Leg 레퍼런스 금리 Term Array

    double* PayRef_Rate,                // Pay Leg 할인 금리 Rate Array 
    long NPayCF,                        // Pay Leg CashFlow 개수
    long* PayCashFlowSchedule,          // Pay Forward Start, End, 기산, 기말, 지급일 ExlDate
    double* Pay_Slope,                  // Pay Leg 변동금리 기울기 Array
    double* Pay_CPN,                    // Pay Leg 고정쿠폰 Array

    double* Pay_FixedRefRate,           // Pay Leg 과거 확정금리 Array
    double* ResultPrice,                // Output 계산결과 [0] Current Swap Rate [1] Rcv Value [2] Payment Value
    double* ResultRefRate,              // Output 기초금리 Array
    double* ResultCPN,                  // Output 추정 쿠폰 Array
    double* ResultDF,                   // Output Discount Factor Array

    double* PV01,                       // Output PV01[0]RcvDisc [1]RcvRef [2]both [3]PayDisc [4]PayRef [5]both
    double* KeyRateRcvPV01,             // Output Rcv Key Rate PV01 .rehaped(-1)
    double* KeyRatePayPV01,             // Output Pay KeyRate PV01 .reshaped(-1)
    long* SOFRConv,                     // [0~2] Rcv LockOut LookBackFlag [3~5] Pay LockOut LookBackFlag
    long* HolidayCalcFlag,              // Holiday관련 인풋 Flag [0]: Rcv [1]: Pay

    long* NHolidays,                    // Holiday 개수 [0] NRcvRef [1] NPayRef
    long* Holidays,                     // Holiday Exceltype
    long* NHistory,                     // OverNight History 개수
    long* HistoryDateExl,               // OverNight History ExlDate
    double* HistoryRate,                // OverNight Rate History

    long* RcvPayConvexityAdjFlag,       // [0] RcvLeg Convexity 보정Flag [1] PayLeg Convexity 보정Flag
    long* NRcvPayConvexAdjVol,          // [0] Rcv Vol개수 [1] Pay Vol개수
    double* RcvTermAndVol,              // [~NRcvConvexAdj] RcvVolTerm, [NRcvConvexAdj~2NRcvConvexAdj-1] RcvVol
    double* PayTermAndVol               // [~NPayConvexAdj] RcvVolTerm, [NPayConvexAdj~2NPayConvexAdj-1] PayVol
)
{
    long i;
    long j;
    long k;
    long ResultCode = 0;
    long TextDumpFlag = 0;

    if (NAFlag == 2)
    {
        NAFlag = 0;
        TextDumpFlag = 1;
    }
    else if (NAFlag == 3)
    {
        NAFlag = 1;
        TextDumpFlag = 1;
    }

    ResultCode = ErrorCheckIRSwap_Excel(
        PriceDate_Exl, GreekFlag, NAFlag, CRS_Flag, CRS_Info,
        Rcv_RefRateType, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
        Rcv_NotionalAMT, Rcv_NotionalPayDate, RcvDisc_NTerm, RcvDisc_Term, RcvDisc_Rate,
        RcvRef_NTerm, RcvRef_Term, RcvRef_Rate, NRcvCF, RcvCashFlowSchedule, Rcv_Slope,
        Rcv_CPN, Rcv_FixedRefRate, Pay_RefRateType, Pay_SwapYearlyNPayment, Pay_SwapMaturity,
        Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate, PayDisc_NTerm,
        PayDisc_Term, PayDisc_Rate, PayRef_NTerm, PayRef_Term, PayRef_Rate,
        NPayCF, PayCashFlowSchedule, Pay_Slope, Pay_CPN, Pay_FixedRefRate, HolidayCalcFlag,
        NHolidays, Holidays);

    char CalcFunctionName[] = "IRSwap_Excel";
    char SaveFileName[100];

    get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
    if (TextDumpFlag == 1)
    {
        DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate_Exl", PriceDate_Exl);
        DumppingTextData(CalcFunctionName, SaveFileName, "GreekFlag", GreekFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "NAFlag", NAFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "CRS_Flag", 2, CRS_Flag);
        DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "CRS_Info", 3, CRS_Flag[1], CRS_Info);

        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_RefRateType", Rcv_RefRateType);
        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_SwapYearlyNPayment", Rcv_SwapYearlyNPayment);
        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_SwapMaturity", Rcv_SwapMaturity);
        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_FixFloFlag", Rcv_FixFloFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_DayCount", Rcv_DayCount);

        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_NotionalAMT", Rcv_NotionalAMT);
        DumppingTextData(CalcFunctionName, SaveFileName, "Rcv_NotionalPayDate", Rcv_NotionalPayDate);
        DumppingTextData(CalcFunctionName, SaveFileName, "RcvDisc_NTerm", RcvDisc_NTerm);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvDisc_Term", RcvDisc_NTerm, RcvDisc_Term);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvDisc_Rate", RcvDisc_NTerm, RcvDisc_Rate);

        DumppingTextData(CalcFunctionName, SaveFileName, "RcvRef_NTerm", RcvRef_NTerm);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRef_Term", RcvDisc_NTerm, RcvRef_Term);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRef_Rate", RcvDisc_NTerm, RcvRef_Rate);
        DumppingTextData(CalcFunctionName, SaveFileName, "NRcvCF", NRcvCF);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvCashFlowSchedule", NRcvCF, RcvCashFlowSchedule);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rcv_Slope", NRcvCF, Rcv_Slope);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rcv_CPN", NRcvCF, Rcv_CPN);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rcv_FixedRefRate", NRcvCF, Rcv_FixedRefRate);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_RefRateType", Pay_RefRateType);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_SwapYearlyNPayment", Pay_SwapYearlyNPayment);

        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_SwapMaturity", Pay_SwapMaturity);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_FixFloFlag", Pay_FixFloFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_DayCount", Pay_DayCount);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_NotionalAMT", Pay_NotionalAMT);
        DumppingTextData(CalcFunctionName, SaveFileName, "Pay_NotionalPayDate", Pay_NotionalPayDate);

        DumppingTextData(CalcFunctionName, SaveFileName, "PayDisc_NTerm", PayDisc_NTerm);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDisc_Term", PayDisc_NTerm, PayDisc_Term);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDisc_Rate", PayDisc_NTerm, PayDisc_Rate);
        DumppingTextData(CalcFunctionName, SaveFileName, "PayRef_NTerm", PayRef_NTerm);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRef_Term", PayDisc_NTerm, PayRef_Term);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRef_Rate", PayDisc_NTerm, PayRef_Rate);
        DumppingTextData(CalcFunctionName, SaveFileName, "NPayCF", NPayCF);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayCashFlowSchedule", NPayCF, PayCashFlowSchedule);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Pay_Slope", NPayCF, Pay_Slope);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Pay_CPN", NPayCF, Pay_CPN);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Pay_FixedRefRate", NPayCF, Pay_FixedRefRate);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "SOFRConv", 6, SOFRConv);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NHolidays", 2, NHolidays);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "Holidays", NHolidays[0] + NHolidays[1], Holidays);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NHistory", 2, NHistory);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HistoryDateExl", NHistory[0] + NHistory[1], HistoryDateExl);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HistoryRate", NHistory[0] + NHistory[1], HistoryRate);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvPayConvexityAdjFlag", 2, RcvPayConvexityAdjFlag);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NRcvPayConvexAdjVol", 2, NRcvPayConvexAdjVol);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvTermAndVol", NRcvPayConvexAdjVol[0] * 2, RcvTermAndVol);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayTermAndVol", NRcvPayConvexAdjVol[1] * 2, PayTermAndVol);

    }

    if (ResultCode < 0) return ResultCode;
    long RcvConvexityAdjFlag = RcvPayConvexityAdjFlag[0];
    long PayConvexityAdjFlag = RcvPayConvexityAdjFlag[1];
    long NRcvConvexAdjVol = NRcvPayConvexAdjVol[0];
    long NPayConvexAdjVol = NRcvPayConvexAdjVol[1];
    double* RcvConvexAdjTerm = RcvTermAndVol;
    double* RcvConvexAdjVol = RcvTermAndVol + NRcvConvexAdjVol;
    double* PayConvexAdjTerm = PayTermAndVol;
    double* PayConvexAdjVol = PayTermAndVol + NPayConvexAdjVol;

    long* Rcv_ForwardStartExl = RcvCashFlowSchedule;
    long* Rcv_ForwardEndExl = RcvCashFlowSchedule + NRcvCF;
    long* Rcv_StartDateExl = RcvCashFlowSchedule + 2 * NRcvCF;
    long* Rcv_EndDateExl = RcvCashFlowSchedule + 3 * NRcvCF;
    long* Rcv_PayDateExl = RcvCashFlowSchedule + 4 * NRcvCF;

    long* Pay_ForwardStartExl = PayCashFlowSchedule;
    long* Pay_ForwardEndExl = PayCashFlowSchedule + NPayCF;
    long* Pay_StartDateExl = PayCashFlowSchedule + 2 * NPayCF;
    long* Pay_EndDateExl = PayCashFlowSchedule + 3 * NPayCF;
    long* Pay_PayDateExl = PayCashFlowSchedule + 4 * NPayCF;

    //////////////////
    // SOFR History //
    long Rcv_NHistory = NHistory[0];
    long Pay_NHistory = NHistory[1];
    long* Rcv_HistoryDateExl = HistoryDateExl;
    long* Pay_HistoryDateExl = HistoryDateExl + Rcv_NHistory;
    double* Rcv_HistoryRate = HistoryRate;
    double* Pay_HistoryRate = HistoryRate + Rcv_NHistory;

    long* Rcv_HistoryRelDate = (long*)malloc(sizeof(long) * Rcv_NHistory);                              // 1
    long* Pay_HistoryRelDate = (long*)malloc(sizeof(long) * Pay_NHistory);                              // 2
    for (i = 0; i < Rcv_NHistory; i++) Rcv_HistoryRelDate[i] = Rcv_HistoryDateExl[i] - PriceDate_Exl;
    for (i = 0; i < Pay_NHistory; i++) Pay_HistoryRelDate[i] = Pay_HistoryDateExl[i] - PriceDate_Exl;

    long WeekCheckStart;
    long WeekCheckEnd;

    long NWeekend;

    long* NRcv_Weekend = (long*)malloc(sizeof(long) * NRcvCF);                                          // 3
    long** Rcv_Weekend = (long**)malloc(sizeof(long*) * NRcvCF);                                        // 4

    for (i = 0; i < NRcvCF; i++)
    {
        WeekCheckStart = Rcv_ForwardStartExl[i] - 100;
        if (Rcv_RefRateType == 0 || Rcv_RefRateType == 2) WeekCheckEnd = Rcv_ForwardEndExl[i];
        else WeekCheckEnd = Rcv_ForwardStartExl[i] + (long)(365.0 * Rcv_SwapMaturity);

        NWeekend = 0;
        for (j = WeekCheckStart; j < WeekCheckEnd; j++)
        {
            if (isweekend(j) == 1)
            {
                NWeekend += 1;
            }
        }
        NRcv_Weekend[i] = NWeekend;
        Rcv_Weekend[i] = (long*)malloc(sizeof(long) * max(1, NWeekend));
        k = 0;
        for (j = WeekCheckStart; j < WeekCheckEnd; j++)
        {
            if (isweekend(j) == 1)
            {
                Rcv_Weekend[i][k] = j - PriceDate_Exl;
                k += 1;
            }
        }
    }

    long* NPay_Weekend = (long*)malloc(sizeof(long) * NPayCF);                                          // 5
    long** Pay_Weekend = (long**)malloc(sizeof(long*) * NPayCF);                                        // 6

    for (i = 0; i < NPayCF; i++)
    {
        WeekCheckStart = Pay_ForwardStartExl[i] - 100;
        if (Pay_RefRateType == 0 || Pay_RefRateType == 2) WeekCheckEnd = Pay_ForwardEndExl[i];
        else WeekCheckEnd = Pay_ForwardStartExl[i] + (long)(365.0 * Rcv_SwapMaturity);

        NWeekend = 0;
        for (j = WeekCheckStart; j < WeekCheckEnd; j++)
        {
            if (isweekend(j) == 1)
            {
                NWeekend += 1;
            }
        }
        NPay_Weekend[i] = NWeekend;
        Pay_Weekend[i] = (long*)malloc(sizeof(long) * max(1, NWeekend));
        k = 0;
        for (j = WeekCheckStart; j < WeekCheckEnd; j++)
        {
            if (isweekend(j) == 1)
            {
                Pay_Weekend[i][k] = j - PriceDate_Exl;
                k += 1;
            }
        }
    }
    long NWeekendForSwap = 0;
    WeekCheckStart = min(Rcv_ForwardStartExl[0], Pay_ForwardStartExl[0]) - 100;
    WeekCheckEnd = max(Rcv_ForwardEndExl[NRcvCF], Pay_ForwardEndExl[NPayCF]);
    for (j = WeekCheckStart; j < WeekCheckEnd; j++)
    {
        if (isweekend(j) == 1)
        {
            NWeekendForSwap += 1;
        }
    }
    long* WeekendForSwap = (long*)malloc(sizeof(long) * max(1, NWeekendForSwap));                       // 7
    k = 0;
    for (j = WeekCheckStart; j < WeekCheckEnd; j++)
    {
        if (isweekend(j) == 1)
        {
            WeekendForSwap[k] = j - PriceDate_Exl;
            k += 1;
        }
    }
    //////////////////////
    // CRS 평가할 지 여부
    //////////////////////
    long CalcCRSFlag = CRS_Flag[0];
    long Rcv_NTermFX = CRS_Flag[1];
    long Pay_NTermFX = CRS_Flag[1];

    double* Rcv_TermFX = CRS_Info;
    double* Pay_TermFX = CRS_Info;
    double* Rcv_FX = CRS_Info + CRS_Flag[1];
    double* Pay_FX = CRS_Info + 2 * CRS_Flag[1];

    long NHolidays_Array[2] = { 0,0 };
    long MaxDay;
    long MinDay;

    ////////////////////////////////////////////
    // Excel Date Type -> C Date Type
    ////////////////////////////////////////////

    long PriceDate_C = ExcelDateToCDate(PriceDate_Exl);

    long* Rcv_ForwardStart_C = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Rcv_ForwardEnd_C = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Rcv_StartDate_C = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Rcv_EndDate_C = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Rcv_PayDate_C = (long*)malloc(sizeof(long) * (NRcvCF));
    for (i = 0; i < NRcvCF; i++)
    {
        Rcv_ForwardStart_C[i] = ExcelDateToCDate(Rcv_ForwardStartExl[i]);
        Rcv_ForwardEnd_C[i] = ExcelDateToCDate(Rcv_ForwardEndExl[i]);
        Rcv_StartDate_C[i] = ExcelDateToCDate(Rcv_StartDateExl[i]);
        Rcv_EndDate_C[i] = ExcelDateToCDate(Rcv_EndDateExl[i]);
        Rcv_PayDate_C[i] = ExcelDateToCDate(Rcv_PayDateExl[i]);
    }


    long* Pay_ForwardStart_C = (long*)malloc(sizeof(long) * (NPayCF));
    long* Pay_ForwardEnd_C = (long*)malloc(sizeof(long) * (NPayCF));
    long* Pay_StartDate_C = (long*)malloc(sizeof(long) * (NPayCF));
    long* Pay_EndDate_C = (long*)malloc(sizeof(long) * (NPayCF));
    long* Pay_PayDate_C = (long*)malloc(sizeof(long) * (NPayCF));
    for (i = 0; i < NPayCF; i++)
    {
        Pay_ForwardStart_C[i] = ExcelDateToCDate(Pay_ForwardStartExl[i]);
        Pay_ForwardEnd_C[i] = ExcelDateToCDate(Pay_ForwardEndExl[i]);
        Pay_StartDate_C[i] = ExcelDateToCDate(Pay_StartDateExl[i]);
        Pay_EndDate_C[i] = ExcelDateToCDate(Pay_EndDateExl[i]);
        Pay_PayDate_C[i] = ExcelDateToCDate(Pay_PayDateExl[i]);
    }

    long* Days_Rcv_ForwardStart = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Days_Rcv_ForwardEnd = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Days_Rcv_StartDate = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Days_Rcv_EndDate = (long*)malloc(sizeof(long) * (NRcvCF));
    long* Days_Rcv_PayDate = (long*)malloc(sizeof(long) * (NRcvCF));
    for (i = 0; i < NRcvCF; i++)
    {
        Days_Rcv_ForwardStart[i] = DayCountAtoB(PriceDate_C, Rcv_ForwardStart_C[i]);
        Days_Rcv_ForwardEnd[i] = DayCountAtoB(PriceDate_C, Rcv_ForwardEnd_C[i]);
        Days_Rcv_StartDate[i] = DayCountAtoB(PriceDate_C, Rcv_StartDate_C[i]);
        Days_Rcv_EndDate[i] = DayCountAtoB(PriceDate_C, Rcv_EndDate_C[i]);
        Days_Rcv_PayDate[i] = DayCountAtoB(PriceDate_C, Rcv_PayDate_C[i]);
    }

    long* Days_Pay_ForwardStart = (long*)malloc(sizeof(long) * (NPayCF));
    long* Days_Pay_ForwardEnd = (long*)malloc(sizeof(long) * (NPayCF));
    long* Days_Pay_StartDate = (long*)malloc(sizeof(long) * (NPayCF));
    long* Days_Pay_EndDate = (long*)malloc(sizeof(long) * (NPayCF));
    long* Days_Pay_PayDate = (long*)malloc(sizeof(long) * (NPayCF));
    for (i = 0; i < NPayCF; i++)
    {
        Days_Pay_ForwardStart[i] = DayCountAtoB(PriceDate_C, Pay_ForwardStart_C[i]);
        Days_Pay_ForwardEnd[i] = DayCountAtoB(PriceDate_C, Pay_ForwardEnd_C[i]);
        Days_Pay_StartDate[i] = DayCountAtoB(PriceDate_C, Pay_StartDate_C[i]);
        Days_Pay_EndDate[i] = DayCountAtoB(PriceDate_C, Pay_EndDate_C[i]);
        Days_Pay_PayDate[i] = DayCountAtoB(PriceDate_C, Pay_PayDate_C[i]);
    }

    long RcvRef_HolidayCalc = HolidayCalcFlag[0];
    long PayRef_HolidayCalc = HolidayCalcFlag[1];

    long RcvRef_NHolidays = NHolidays[0];
    long PayRef_NHolidays = NHolidays[1];

    long* RcvRef_Holidays_Exl = Holidays;
    long* PayRef_Holidays_Exl = Holidays + RcvRef_HolidayCalc;

    ////////////////////////////////////////////
    // Holiday 매핑, 너무 과거나 너무 미래인거 빼고
    ////////////////////////////////////////////

    MaxDay = max(Rcv_PayDateExl[NPayCF - 1], Pay_PayDateExl[NPayCF - 1]);
    MinDay = min(min(PriceDate_Exl, min(Rcv_ForwardStartExl[0], Pay_ForwardStartExl[0])), min(Rcv_StartDateExl[0], Pay_StartDateExl[0]));
    // RcvRef
    NHolidays_Array[0] = 0;
    for (i = 0; i < RcvRef_NHolidays; i++) {
        if (RcvRef_Holidays_Exl[i] <= MaxDay && RcvRef_Holidays_Exl[i] > MinDay - 100) { NHolidays_Array[0] += 1; }
    }
    long* RcvRef_Days_Holiday = (long*)malloc(sizeof(long) * max(1, NHolidays_Array[0]));
    NHolidays_Array[0] = 0;
    for (i = 0; i < RcvRef_NHolidays; i++) {
        if (RcvRef_Holidays_Exl[i] <= MaxDay && RcvRef_Holidays_Exl[i] > MinDay - 100) {
            RcvRef_Days_Holiday[NHolidays_Array[0]] = DayCountAtoB(PriceDate_C, ExcelDateToCDate(RcvRef_Holidays_Exl[i]));
            NHolidays_Array[0] += 1;
        }
    }
    // PayRef
    NHolidays_Array[1] = 0;
    for (i = 0; i < PayRef_NHolidays; i++) {
        if (PayRef_Holidays_Exl[i] <= MaxDay && PayRef_Holidays_Exl[i] > MinDay - 100) { NHolidays_Array[1] += 1; }
    }
    long* PayRef_Days_Holiday = (long*)malloc(sizeof(long) * max(1, NHolidays_Array[1]));
    NHolidays_Array[1] = 0;
    for (i = 0; i < PayRef_NHolidays; i++) {
        if (PayRef_Holidays_Exl[i] <= MaxDay && PayRef_Holidays_Exl[i] > MinDay - 100) {
            PayRef_Days_Holiday[NHolidays_Array[1]] = DayCountAtoB(PriceDate_C, ExcelDateToCDate(PayRef_Holidays_Exl[i]));
            NHolidays_Array[1] += 1;
        }
    }

    ////////////////////////////////
    // Receive Schedule Mapping  ///
    ////////////////////////////////

    SCHD* Rcv_Schedule = new SCHD;
    Rcv_Schedule->HolidayFlag_Ref = RcvRef_HolidayCalc;
    Rcv_Schedule->NHolidays_Ref = NHolidays_Array[0];
    Rcv_Schedule->Days_Holidays_Ref = RcvRef_Days_Holiday;
    Rcv_Schedule->NCF = NRcvCF;
    Rcv_Schedule->ForwardStart_C = Rcv_ForwardStart_C;
    Rcv_Schedule->ForwardEnd_C = Rcv_ForwardEnd_C;
    Rcv_Schedule->StartDate_C = Rcv_StartDate_C;
    Rcv_Schedule->EndDate_C = Rcv_EndDate_C;
    Rcv_Schedule->PayDate_C = Rcv_PayDate_C;
    Rcv_Schedule->Days_ForwardStart = Days_Rcv_ForwardStart;
    Rcv_Schedule->Days_ForwardEnd = Days_Rcv_ForwardEnd;
    Rcv_Schedule->Days_StartDate = Days_Rcv_StartDate;
    Rcv_Schedule->Days_EndDate = Days_Rcv_EndDate;
    Rcv_Schedule->Days_PayDate = Days_Rcv_PayDate;
    Rcv_Schedule->NotionalPayDate_C = ExcelDateToCDate(Rcv_NotionalPayDate);
    Rcv_Schedule->Days_Notional = DayCountAtoB(PriceDate_C, Rcv_Schedule->NotionalPayDate_C);
    Rcv_Schedule->ReferenceType = Rcv_RefRateType;
    Rcv_Schedule->FixedFlotype = Rcv_FixFloFlag;
    Rcv_Schedule->DayCount = Rcv_DayCount;
    Rcv_Schedule->NotionalAmount = Rcv_NotionalAMT;
    Rcv_Schedule->NWeekendDate = NRcv_Weekend;
    Rcv_Schedule->WeekendList = Rcv_Weekend;
    Rcv_Schedule->NRefHistory = Rcv_NHistory;
    Rcv_Schedule->RefHistoryDate = Rcv_HistoryRelDate;
    Rcv_Schedule->RefHistory = Rcv_HistoryRate;

    if (Rcv_RefRateType != 0 && Rcv_RefRateType != 2) Rcv_Schedule->RefSwapFlag = 1;
    Rcv_Schedule->NSwapPayAnnual = Rcv_SwapYearlyNPayment;
    Rcv_Schedule->RefSwapMaturity = Rcv_SwapMaturity;
    Rcv_Schedule->FixedRefRate = Rcv_FixedRefRate;
    Rcv_Schedule->Slope = Rcv_Slope;
    Rcv_Schedule->CPN = Rcv_CPN;
    Rcv_Schedule->NAFlag = NAFlag;
    Rcv_Schedule->PriceDate_C = PriceDate_C;

    Rcv_Schedule->LockOutRef = SOFRConv[0];
    Rcv_Schedule->LookBackRef = SOFRConv[1];
    Rcv_Schedule->ObservationShift = SOFRConv[2];

    ////////////////////////////
    // Pay Schedule Mapping  ///
    ////////////////////////////

    SCHD* Pay_Schedule = new SCHD;
    Pay_Schedule->HolidayFlag_Ref = RcvRef_HolidayCalc;
    Pay_Schedule->NHolidays_Ref = NHolidays_Array[1];
    Pay_Schedule->Days_Holidays_Ref = PayRef_Days_Holiday;
    Pay_Schedule->NCF = NPayCF;
    Pay_Schedule->ForwardStart_C = Pay_ForwardStart_C;
    Pay_Schedule->ForwardEnd_C = Pay_ForwardEnd_C;
    Pay_Schedule->StartDate_C = Pay_StartDate_C;
    Pay_Schedule->EndDate_C = Pay_EndDate_C;
    Pay_Schedule->PayDate_C = Pay_PayDate_C;
    Pay_Schedule->Days_ForwardStart = Days_Pay_ForwardStart;
    Pay_Schedule->Days_ForwardEnd = Days_Pay_ForwardEnd;
    Pay_Schedule->Days_StartDate = Days_Pay_StartDate;
    Pay_Schedule->Days_EndDate = Days_Pay_EndDate;
    Pay_Schedule->Days_PayDate = Days_Pay_PayDate;
    Pay_Schedule->NotionalPayDate_C = ExcelDateToCDate(Pay_NotionalPayDate);
    Pay_Schedule->Days_Notional = DayCountAtoB(PriceDate_C, Pay_Schedule->NotionalPayDate_C);
    Pay_Schedule->ReferenceType = Pay_RefRateType;
    Pay_Schedule->FixedFlotype = Pay_FixFloFlag;
    Pay_Schedule->DayCount = Pay_DayCount;
    Pay_Schedule->NotionalAmount = Pay_NotionalAMT;
    Pay_Schedule->NWeekendDate = NPay_Weekend;
    Pay_Schedule->WeekendList = Pay_Weekend;
    Pay_Schedule->NRefHistory = Pay_NHistory;
    Pay_Schedule->RefHistoryDate = Pay_HistoryRelDate;
    Pay_Schedule->RefHistory = Pay_HistoryRate;

    if (Pay_RefRateType != 0 && Pay_RefRateType != 2) Pay_Schedule->RefSwapFlag = 1;
    Pay_Schedule->NSwapPayAnnual = Pay_SwapYearlyNPayment;
    Pay_Schedule->RefSwapMaturity = Pay_SwapMaturity;
    Pay_Schedule->FixedRefRate = Pay_FixedRefRate;
    Pay_Schedule->Slope = Pay_Slope;
    Pay_Schedule->CPN = Pay_CPN;
    Pay_Schedule->NAFlag = NAFlag;
    Pay_Schedule->PriceDate_C = PriceDate_C;

    Pay_Schedule->LockOutRef = SOFRConv[3];
    Pay_Schedule->LookBackRef = SOFRConv[4];
    Pay_Schedule->ObservationShift = SOFRConv[5];

    long PricingOnly = 1;
    if (GreekFlag == 999)
    {
        PricingOnly = 999;
        GreekFlag = 0;
    }
    ResultCode = SwapPricer(PriceDate_C, CalcCRSFlag, Rcv_Schedule, RcvDisc_NTerm, RcvDisc_Term,
        RcvDisc_Rate, RcvRef_NTerm, RcvRef_Term, RcvRef_Rate,
        Pay_Schedule, PayDisc_NTerm, PayDisc_Term, PayDisc_Rate,
        PayRef_NTerm, PayRef_Term, PayRef_Rate,
        Rcv_NTermFX, Rcv_TermFX, Rcv_FX, Pay_NTermFX, Pay_TermFX, Pay_FX,
        GreekFlag, ResultPrice, ResultRefRate, ResultCPN, ResultDF,
        PV01, KeyRateRcvPV01, KeyRatePayPV01, NWeekendForSwap, WeekendForSwap, 
        PricingOnly, RcvConvexityAdjFlag, PayConvexityAdjFlag, NRcvConvexAdjVol, NPayConvexAdjVol, RcvConvexAdjTerm,
        RcvConvexAdjVol, PayConvexAdjTerm, PayConvexAdjVol );

    free(Rcv_HistoryRelDate);
    free(Pay_HistoryRelDate);

    free(NRcv_Weekend);
    for (i = 0; i < NRcvCF; i++) free(Rcv_Weekend[i]);
    free(Rcv_Weekend);

    free(NPay_Weekend);
    for (i = 0; i < NPayCF; i++) free(Pay_Weekend[i]);
    free(Pay_Weekend);

    free(WeekendForSwap);

    free(Rcv_ForwardStart_C);
    free(Rcv_ForwardEnd_C);
    free(Rcv_StartDate_C);
    free(Rcv_EndDate_C);
    free(Rcv_PayDate_C);

    free(Pay_ForwardStart_C);
    free(Pay_ForwardEnd_C);
    free(Pay_StartDate_C);
    free(Pay_EndDate_C);
    free(Pay_PayDate_C);
    free(RcvRef_Days_Holiday);
    free(PayRef_Days_Holiday);
    free(Days_Pay_StartDate);
    free(Days_Rcv_StartDate);
    free(Days_Pay_PayDate);
    free(Days_Rcv_PayDate);
    free(Days_Pay_EndDate);
    free(Days_Rcv_EndDate);
    free(Days_Pay_ForwardEnd);
    free(Days_Rcv_ForwardEnd);
    free(Days_Pay_ForwardStart);
    free(Days_Rcv_ForwardStart);
    delete (Rcv_Schedule);
    delete (Pay_Schedule);
    //_CrtDumpMemoryLeaks();
    return ResultCode;
}

long FindZeroRate(
    long PriceDate_ExlDate,
    long DayCountFlag,
    long RefRateType,
    long NOverNightHistory,
    long* OverNightHistory_ExlDate,
    double* OverNightHistoryRate,
    long LockOutDays,
    long LookBackDays,
    long ObservShiftFlag,

    long HolidayFlag,
    long NHoliday,
    long* Holiday_ExlDate,

    long NCashFlow,
    long* ForwardStart_ExlDate,
    long* ForwardEnd_ExlDate,
    long* Start_ExlDate,
    long* End_ExlDate,

    long* Pay_ExlDate,
    double SwapRate,
    long NCurve,
    double* ResultTerm,
    double* ResultRate
)
{
    long i, j, k, n;

    long GreekFlag = 999;
    long NAFlag = 1;
    long CRS_Flag[2] = { 0, 0 };
    double CRS_Info[2] = { 0.0, 0.0 };
    long NotionalPayDate;
    /////////////
    // Rcv Leg를 변동금리로 박아두기
    /////////////
    long Rcv_RefRateType;
    if (RefRateType == 0) Rcv_RefRateType = 0;
    else Rcv_RefRateType = 2;

    long Rcv_SwapYearlyNPayment = 1;
    double Rcv_SwapMaturity = 1.0;
    long Rcv_FixFloFlag = 1;
    long Rcv_DayCount = DayCountFlag;
    long Pay_RefRateType;
    if (RefRateType == 0) Pay_RefRateType = 0;
    else Pay_RefRateType = 2;

    long Pay_SwapYearlyNPayment = 1;
    double Pay_SwapMaturity = 1.0;
    long Pay_FixFloFlag = 0;
    long Pay_DayCount = DayCountFlag;

    double Rcv_NotionalAMT = 10000.0;
    double Pay_NotionalAMT = 10000.0;
    long Rcv_NotionalPayDate = Pay_ExlDate[NCashFlow - 1];
    long Pay_NotionalPayDate = Pay_ExlDate[NCashFlow - 1];

    long* CashFlowSchedule = (long*)malloc(sizeof(long) * NCashFlow * 5);
    for (i = 0; i < NCashFlow; i++)
    {
        CashFlowSchedule[i] = ForwardStart_ExlDate[i];
        CashFlowSchedule[i + NCashFlow] = ForwardEnd_ExlDate[i];
        CashFlowSchedule[i + 2 * NCashFlow] = Start_ExlDate[i];
        CashFlowSchedule[i + 3 * NCashFlow] = End_ExlDate[i];
        CashFlowSchedule[i + 4 * NCashFlow] = Pay_ExlDate[i];
    }
    double* Rcv_Slope = (double*)malloc(sizeof(double) * NCashFlow);
    for (i = 0; i < NCashFlow; i++) Rcv_Slope[i] = 1.0;
    double* Rcv_CPN = (double*)malloc(sizeof(double) * NCashFlow);
    for (i = 0; i < NCashFlow; i++) Rcv_CPN[i] = 0.0;

    double* Pay_Slope = (double*)malloc(sizeof(double) * NCashFlow);
    for (i = 0; i < NCashFlow; i++) Pay_Slope[i] = 0.0;
    double* Pay_CPN = (double*)malloc(sizeof(double) * NCashFlow);
    for (i = 0; i < NCashFlow; i++) Pay_CPN[i] = min(0.5, SwapRate);

    double dblErrorRange = 0.000001;
    double ObjValue = 0.0;
    double MaxRate = SwapRate + 0.2;
    double MinRate = SwapRate - 0.15;
    double TargetRate = MaxRate;

    double* Rate = (double*)malloc(sizeof(double) * NCurve);
    double PrevRate = MaxRate;
    for (i = 0; i < NCurve - 1; i++)
    {
        Rate[i] = ResultRate[i];
    }

    long ResultCodeTemp = 0;
    double ResultPrice[10] = { 0.0, };
    double* ResultRefRate = (double*)malloc(sizeof(double) * (NCashFlow + NCashFlow + 2));
    double* ResultCPN = (double*)malloc(sizeof(double) * (NCashFlow + NCashFlow + 2));
    double* ResultDF = (double*)malloc(sizeof(double) * (NCashFlow + NCashFlow + 2));
    double* PV01 = (double*)malloc(sizeof(double) * 6);
    double* KeyRateRcvPV01 = (double*)malloc(sizeof(double) * (2 * (NCurve + NCurve) + NCurve));
    double* KeyRatePayPV01 = (double*)malloc(sizeof(double) * (2 * (NCurve + NCurve) + NCurve));

    long SOFRConv[6] = { LockOutDays, LookBackDays, ObservShiftFlag, LockOutDays, LookBackDays, ObservShiftFlag };
    long HolidayCalcFlag[2] = { HolidayFlag, HolidayFlag };
    long NHolidayAdj[2] = { NHoliday, NHoliday };
    long* Holiday = (long*)malloc(sizeof(long) * (2 * NHoliday));
    for (i = 0; i < NHoliday; i++)
    {
        Holiday[i] = Holiday_ExlDate[i];
        Holiday[i + NHoliday] = Holiday_ExlDate[i];
    }
    long NHistory[2] = { NOverNightHistory, NOverNightHistory };
    long* HistoryDateExl = (long*)malloc(sizeof(long) * (NOverNightHistory + NOverNightHistory));
    double* HistoryRate = (double*)malloc(sizeof(double) * (NOverNightHistory + NOverNightHistory));
    double dblCalcPrice;

    for (i = 0; i < NOverNightHistory; i++)
    {
        HistoryDateExl[i] = OverNightHistory_ExlDate[i];
        HistoryDateExl[i + NOverNightHistory] = OverNightHistory_ExlDate[i];
        HistoryRate[i] = OverNightHistoryRate[i];
        HistoryRate[i + NOverNightHistory] = OverNightHistoryRate[i];
    }

    long ContinuePoint = 1;
    long TempNumber2[2] = { 0, 0 };
    long TempFlag2[2] = { 0, 0 };
    double TempFloat[2] = { 0.0, 0.0 };

    for (i = 0; i < 1000; i++)
    {
        Rate[NCurve - 1] = TargetRate;
        ResultCodeTemp = IRSwap_Excel(PriceDate_ExlDate, GreekFlag, NAFlag, CRS_Flag, CRS_Info,
            Rcv_RefRateType, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
            Rcv_NotionalAMT, Rcv_NotionalPayDate, NCurve, ResultTerm, Rate,
            NCurve, ResultTerm, Rate, NCashFlow, CashFlowSchedule,
            Rcv_Slope, Rcv_CPN, Rcv_CPN, Pay_RefRateType, Pay_SwapYearlyNPayment,
            Pay_SwapMaturity, Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate,
            NCurve, ResultTerm, Rate, NCurve, ResultTerm,
            Rate, NCashFlow, CashFlowSchedule, Pay_Slope, Pay_CPN,
            Pay_CPN, ResultPrice, ResultRefRate, ResultCPN, ResultDF,
            PV01, KeyRateRcvPV01, KeyRatePayPV01, SOFRConv, HolidayCalcFlag,
            NHolidayAdj, Holiday, NHistory, HistoryDateExl, HistoryRate,
            TempFlag2, TempNumber2, TempFloat, TempFloat);

        dblCalcPrice = ResultPrice[1] - ResultPrice[2];
        if (fabs(dblCalcPrice) < dblErrorRange) break;
        if (dblCalcPrice > 0)
        {
            MaxRate = TargetRate;
            TargetRate = (MaxRate + MinRate) / 2.0;
        }
        else
        {
            MinRate = TargetRate;
            TargetRate = (MinRate + MaxRate) / 2.0;
        }
    }
    ResultRate[NCurve - 1] = Rate[NCurve - 1];

    free(CashFlowSchedule);
    free(Rcv_Slope);
    free(Rcv_CPN);
    free(Pay_Slope);
    free(Pay_CPN);
    free(Rate);
    free(ResultRefRate);
    free(ResultCPN);
    free(ResultDF);
    free(PV01);
    free(KeyRateRcvPV01);
    free(KeyRatePayPV01);
    free(Holiday);
    free(HistoryDateExl);
    free(HistoryRate);

    return 1;
}

DLLEXPORT(long) OISCurveGeneratorExcel(
    long PriceDateExl,                  // Pricing 시작일
    long DayCountFlag,                  // 0: Act/365 1:Act/360
    long RefRateType,                   // 기초금리타입 0 LIBOR CD 1: SOFR
    double TodayONRate,                 // 오늘 오버나이트금리
    long NOverNightHistory,             // 오버나이트금리 히스토리개수

    long* OverNightHistoryExlDate,      // 오버나이트금리 히스토리 엑셀날짜
    double* OverNightHistoryRate,       // 오버나이트금리 히스토리 이자율
    long LockOutDays,                   // LockOutDay
    long LookBackDays,                  // LookBackDay
    long ObservShiftFlag,

    long HolidayFlag,                   // Holiday에 오버나이트금리 처리 0: FFill, 1 BackFill 2: Interp
    long NHoliday,                      // Holiday날짜 넣을 개수
    long* HolidayExl,                   // Holiday날짜 엑셀타입
    long NOIS,                          // OIS 스왑개수
    long* StartIdxSchedule,             // OIS 관련 Array의 Start 포인터

    long* NArraySchedule,               // 스왑별 스케줄 개수 Array
    long* ForwardStartExlDate,          // 추정시작 길이 = sum(NArraySchedule)
    long* ForwardEndExlDate,            // 추정종료
    long* StartExlDate,                 // DayCount시작
    long* EndExlDate,                   // DayCOunt종료

    long* PayExlDate,                   // 지급일
    double* SwapRate,                   // 스왑레이트
    double* ResultTerm,
    double* ResultRate,
    long TextDumpFlag
)
{
    long i, j, n;
    char CalcFunctionName[] = "OISCurveGeneratorExcel";
    char SaveFileName[100];

    get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
    if (TextDumpFlag == 1)
    {
        DumppingTextData(CalcFunctionName, SaveFileName, "PriceDateExl", PriceDateExl);
        DumppingTextData(CalcFunctionName, SaveFileName, "DayCountFlag", DayCountFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "RefRateType", RefRateType);
        DumppingTextData(CalcFunctionName, SaveFileName, "TodayONRate", TodayONRate);
        DumppingTextData(CalcFunctionName, SaveFileName, "NOverNightHistory", NOverNightHistory);

        DumppingTextDataArray(CalcFunctionName, SaveFileName, "OverNightHistoryExlDate", NOverNightHistory, OverNightHistoryExlDate);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "OverNightHistoryRate", NOverNightHistory, OverNightHistoryRate);
        DumppingTextData(CalcFunctionName, SaveFileName, "LockOutDays", LockOutDays);
        DumppingTextData(CalcFunctionName, SaveFileName, "LookBackDays", LookBackDays);
        DumppingTextData(CalcFunctionName, SaveFileName, "ObservShiftFlag", ObservShiftFlag);

        DumppingTextData(CalcFunctionName, SaveFileName, "HolidayFlag", HolidayFlag);
        DumppingTextData(CalcFunctionName, SaveFileName, "NHoliday", NHoliday);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HolidayExl", NHoliday, HolidayExl);
        DumppingTextData(CalcFunctionName, SaveFileName, "NOIS", NOIS);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "StartIdxSchedule", NOIS, StartIdxSchedule);
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "NArraySchedule", NOIS, NArraySchedule);
        n = 0;
        for (i = 0; i < NOIS; i++)
        {
            DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardStartExlDate", NArraySchedule[i], ForwardStartExlDate + n);
            DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardEndExlDate", NArraySchedule[i], ForwardEndExlDate + n);
            DumppingTextDataArray(CalcFunctionName, SaveFileName, "StartExlDate", NArraySchedule[i], StartExlDate + n);
            DumppingTextDataArray(CalcFunctionName, SaveFileName, "EndExlDate", NArraySchedule[i], EndExlDate + n);
            DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayExlDate", NArraySchedule[i], PayExlDate + n);
            DumppingTextData(CalcFunctionName, SaveFileName, "SwapRate", SwapRate[i]);
            n += NArraySchedule[i];
        }
    }
    long ResultCode = 0;
    double dt = 1.0 / 365.0;

    double T;
    long** ForwardStartDate = (long**)malloc(sizeof(long*) * NOIS);
    long** ForwardEndDate = (long**)malloc(sizeof(long*) * NOIS);
    long** StartDate = (long**)malloc(sizeof(long*) * NOIS);
    long** EndDate = (long**)malloc(sizeof(long*) * NOIS);
    long** PayDate = (long**)malloc(sizeof(long*) * NOIS);

    long* TempDateArray;
    long Tomorrow = PriceDateExl + 1;
    long startidx = 0;
    long Tomorrowisweekend = max(isweekend(Tomorrow), isin(Tomorrow, HolidayExl, NHoliday, startidx));
    long NumHoliday;
    if (Tomorrowisweekend == 0)
    {
        ResultTerm[0] = dt;
        if (DayCountFlag == 1) ResultRate[0] = -365.0 * log(1.0 / (1.0 + TodayONRate * 1.0 / 360.0));
        else ResultRate[0] = -365.0 * log(1.0 / (1.0 + TodayONRate * 1.0 / 365.0));
    }
    else
    {
        long NextDay = PriceDateExl;
        NumHoliday = 0;
        startidx = 0;
        for (i = 0; i < 7; i++)
        {
            NextDay += 1;
            Tomorrowisweekend = max(isweekend(NextDay), isin(NextDay, HolidayExl, NHoliday, startidx));
            if (Tomorrowisweekend == 1)
            {
                NumHoliday += 1;
            }
            else
            {
                break;
            }
        }
        ResultTerm[0] = dt * (double)(1 + NumHoliday);
        if (DayCountFlag == 1) ResultRate[0] = -365.0/ (double)(1 + NumHoliday) * log(1.0 / (1.0 + TodayONRate * (double)(1 + NumHoliday) / 360.0));
        else ResultRate[0] = -365.0/ (double)(1 + NumHoliday) * log(1.0 / (1.0 + TodayONRate * (double)(1 + NumHoliday) / 365.0));
    }

    for (i = 0; i < NOIS; i++)
    {
        ForwardStartDate[i] = (long*)malloc(sizeof(long) * NArraySchedule[i]);
        ForwardEndDate[i] = (long*)malloc(sizeof(long) * NArraySchedule[i]);
        StartDate[i] = (long*)malloc(sizeof(long) * NArraySchedule[i]);
        EndDate[i] = (long*)malloc(sizeof(long) * NArraySchedule[i]);
        PayDate[i] = (long*)malloc(sizeof(long) * NArraySchedule[i]);

        TempDateArray = ForwardStartExlDate + StartIdxSchedule[i];
        for (j = 0; j < NArraySchedule[i]; j++) ForwardStartDate[i][j] = (TempDateArray[j]);
        TempDateArray = ForwardEndExlDate + StartIdxSchedule[i];
        for (j = 0; j < NArraySchedule[i]; j++) ForwardEndDate[i][j] = (TempDateArray[j]);
        TempDateArray = StartExlDate + StartIdxSchedule[i];
        for (j = 0; j < NArraySchedule[i]; j++) StartDate[i][j] = (TempDateArray[j]);
        TempDateArray = EndExlDate + StartIdxSchedule[i];
        for (j = 0; j < NArraySchedule[i]; j++) EndDate[i][j] = (TempDateArray[j]);
        TempDateArray = PayExlDate + StartIdxSchedule[i];
        for (j = 0; j < NArraySchedule[i]; j++) PayDate[i][j] = (TempDateArray[j]);

        T = (PayDate[i][NArraySchedule[i] - 1] - PriceDateExl) / 365.0;
        ResultTerm[i + 1] = T;
    }

    long CaliFlag = 0;
    long NCurve = 1;
    for (i = 0; i < NOIS; i++)
    {
        NCurve += 1;
        CaliFlag = FindZeroRate(PriceDateExl, DayCountFlag, RefRateType, NOverNightHistory, OverNightHistoryExlDate,
            OverNightHistoryRate, LockOutDays, LookBackDays, ObservShiftFlag, HolidayFlag,
            NHoliday, HolidayExl, NArraySchedule[i], ForwardStartDate[i], ForwardEndDate[i],
            StartDate[i], EndDate[i], EndDate[i], SwapRate[i], NCurve, ResultTerm, ResultRate);
    }


    for (i = 0; i < NOIS; i++)
    {
        free(ForwardStartDate[i]);
        free(ForwardEndDate[i]);
        free(StartDate[i]);
        free(EndDate[i]);
        free(PayDate[i]);
    }
    free(ForwardStartDate);
    free(ForwardEndDate);
    free(StartDate);
    free(EndDate);
    free(PayDate);
    return ResultCode;
}