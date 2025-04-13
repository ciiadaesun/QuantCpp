#include <stdio.h>
#include <math.h>

#include "CalcDate.h"
#include "Structure.h"
#include "Util.h"
#include "GetTextDump.h"
#include <crtdbg.h>
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

//Forward Rate 계산
double Calc_Forward_Rate_ForSOFR(
    double* TermArray, // 기간구조의 기간 Array [0.25,  0.5,   1.0, ....]
    double* RateArray, // 기간구조의 Rate Array [0.008, 0.012, 0.014, ...]
    long LengthArray,  // 기간구조 개수
    double T1,         // Forward Start 시점
    double T2,          // Forward End 시점
    double DeltaT
)
{
    double DFT1;
    double DFT2;
    double FRate;
    //Linear Interpolation
    if (T1 < TermArray[LengthArray - 1] && T1> TermArray[0])
    {
        DFT1 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T1) * T1);
        DFT2 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T2) * T2);
        FRate = 1.0 / DeltaT * (DFT1 / DFT2 - 1.0);
    }
    else if (T1 <= TermArray[0])
    {
        DFT1 = exp(-RateArray[0] * T1);
        DFT2 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T2) * T2);
        FRate = 1.0 / DeltaT * (DFT1 / DFT2 - 1.0);
    }
    else
    {
        DFT1 = exp(-RateArray[LengthArray - 1] * T1);
        DFT2 = exp(-RateArray[LengthArray - 1] * T2);
        FRate = 1.0 / DeltaT * (DFT1 / DFT2 - 1.0);
    }

    return FRate;
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

long* Generate_CpnDate_Holiday(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD, long ModifiedFollowing = 1)
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
            if ((MOD7 == 1 || MOD7 == 0) || isin(CpnDate, HolidayYYYYMMDD, NHoliday)) SaturSundayFlag = 1;
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
    long TempYYYYMMDD = PriceDateYYYYMMDD;
    long TempYYYY = 0;
    long TempMM = 0;
    long ncpn = 0;
    long* CpnDate;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62)
    {
        // 2개월 미만의 경우 쿠폰 한번지급으로 고정
        free(HolidayYYYYMMDD);
        return 1;
    }
    else if (SwapMatYYYY - PriceYYYY <= 1)
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
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;
        long StartDateYYYYMMDD = PriceDateYYYYMMDD;
        long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
        long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        long EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;

        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        free(CpnDate);
        free(HolidayYYYYMMDD);
        return ncpn;
    }
}

DLLEXPORT(long) Number_Coupon_YYYYMMDD(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDateYYYYMMDD,         // 평가일
    long SwapMat_YYYYMMDD,          // 스왑 만기
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* HolidayYYYYMMDD           // 공휴일
)
{
    long i;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2) ProductType = 1;
    if (ProductType == 0) return 1;

    // 에러처리
    if (PriceDateYYYYMMDD <= 19000101 || PriceDateYYYYMMDD >= 999990101)  return -1;
    if (SwapMat_YYYYMMDD <= 19000101 || SwapMat_YYYYMMDD >= 999990101) return -1;
    if (AnnCpnOneYear > 6) return -1;

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
        return -1;
    }

    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

    long n;
    long TempYYYYMMDD = PriceDateYYYYMMDD;
    long TempYYYY = 0;
    long TempMM = 0;
    long ncpn = 0;
    long* CpnDate;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62)
    {
        // 2개월 미만의 경우 쿠폰 한번지급으로 고정
        return 1;
    }
    else if (SwapMatYYYY - PriceYYYY <= 1)
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
            return 1;
        }
        else
        {
            if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
            else CpnDate = Generate_CpnDate(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

            free(CpnDate);
            return ncpn;
        }
    }
    else
    {
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;
        long StartDateYYYYMMDD = PriceDateYYYYMMDD;
        long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
        long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        long EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;

        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        free(CpnDate);
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
    long PayDateExcelType, PayDateYYYYMMDD, EndDateYYYYMMDD, EndDateExcel, MOD7;
    long PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateExcelType);          // 평가일
    long StartDateYYYYMMDD = ExcelDateToCDate(StartDateExcelType);          // 평가일
    long SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMatExcelType);             // 스왑 만기
    long ncpn;
    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
    for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayExcelType[i]);


    if (NumberCoupon < 0) return -1;
    if (NumberCoupon <= 1)
    {
        if (NBDayFromEndDate == 0)
        {
            ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
            ResultForwardEnd[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
            ResultPayDate[0] = ResultForwardEnd[0];
        }
        else
        {
            n = 0;
            ResultForwardStart[0] = StartDateExcelType;
            // PayDate결정
            PayDateYYYYMMDD = SwapMat_YYYYMMDD;
            PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
            MOD7 = PayDateExcelType % 7;
            for (i = 1; i < 7; i++)
            {
                if (isweekend(PayDateExcelType) || isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                {
                    // 휴일이면 n+=1
                    PayDateExcelType += 1;
                    PayDateYYYYMMDD = ExcelDateToCDate(PayDateExcelType);
                }
                else
                {
                    break;
                }
            }

            ResultPayDate[0] = PayDateExcelType;
            EndDateYYYYMMDD = PayDateYYYYMMDD;
            EndDateExcel = PayDateExcelType;
            for (i = 1; i < 10; i++)
            {
                EndDateExcel = EndDateExcel - 1;
                EndDateYYYYMMDD = ExcelDateToCDate(EndDateExcel);
                MOD7 = EndDateExcel % 7;
                if ((MOD7 != 1 && MOD7 != 0) && !isin(EndDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                {
                    // 영업일이면 n+=1
                    n += 1;
                }

                if (n == NBDayFromEndDate)
                {
                    ResultForwardEnd[0] = EndDateExcel;
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
        long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
        long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        //EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;
        long nbdcheck = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, 1, &EndDateYYYYMMDD);
        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        for (i = 0; i < min(NumberCoupon, ncpn); i++)
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
                    if ((MOD7 != 1 && MOD7 != 0) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
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

DLLEXPORT(long) ResultCpnMapping_YYYYMMDD(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDateYYYYMMDD,         // 평가일
    long StartDateYYYYMMDD,         // 시작일
    long SwapMat_YYYYMMDD,          // 스왑 만기
    long NBDayFromEndDate,          // N영업일 뒤 지급
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* HolidayYYYYMMDD,          // 공휴일
    long NumberCoupon,
    long* ResultForwardStartYYYYMMDD,
    long* ResultForwardEndYYYYMMDD,
    long* ResultPayDateYYYYMMDD
)
{
    long i;
    long j;
    long n;
    long PayDateExcelType, PayDateYYYYMMDD, EndDateYYYYMMDD, EndDateExcel, MOD7;
    long ncpn;


    if (NumberCoupon < 0) return -1;
    if (NumberCoupon <= 1)
    {
        if (NBDayFromEndDate == 0)
        {
            ResultForwardStartYYYYMMDD[0] = (StartDateYYYYMMDD);
            ResultForwardEndYYYYMMDD[0] = (SwapMat_YYYYMMDD);
            ResultPayDateYYYYMMDD[0] = ResultForwardEndYYYYMMDD[0];
        }
        else
        {
            n = 0;
            ResultForwardStartYYYYMMDD[0] = StartDateYYYYMMDD;
            // PayDate결정
            PayDateYYYYMMDD = SwapMat_YYYYMMDD;
            PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
            MOD7 = PayDateExcelType % 7;
            for (i = 1; i < 7; i++)
            {
                if (isweekend(PayDateExcelType) || isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                {
                    // 휴일이면 n+=1
                    PayDateExcelType += 1;
                    PayDateYYYYMMDD = ExcelDateToCDate(PayDateExcelType);
                }
                else
                {
                    break;
                }
            }

            ResultPayDateYYYYMMDD[0] = PayDateYYYYMMDD;
            EndDateYYYYMMDD = PayDateYYYYMMDD;
            EndDateExcel = PayDateExcelType;
            for (i = 1; i < 10; i++)
            {
                EndDateExcel = EndDateExcel - 1;
                EndDateYYYYMMDD = ExcelDateToCDate(EndDateExcel);
                MOD7 = EndDateExcel % 7;
                if ((MOD7 != 1 && MOD7 != 0) && !isin(EndDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                {
                    // 영업일이면 n+=1
                    n += 1;
                }

                if (n == NBDayFromEndDate)
                {
                    ResultForwardEndYYYYMMDD[0] = EndDateYYYYMMDD;
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
        long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
        long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        //EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;
        long nbdcheck = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, 1, &EndDateYYYYMMDD);
        if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
        else CpnDate = Generate_CpnDate(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

        for (i = 0; i < min(NumberCoupon, ncpn); i++)
        {
            if (i == 0)
            {
                ResultForwardStartYYYYMMDD[0] = (StartDateYYYYMMDD);
                TempDateExcelType = CDateToExcelDate(CpnDate[0]);
                ResultForwardEndYYYYMMDD[0] = TempYYYYMMDD;
            }
            else
            {
                ResultForwardStartYYYYMMDD[i] = (CpnDate[i - 1]);
                TempDateExcelType = CDateToExcelDate(CpnDate[i]);
                ResultForwardEndYYYYMMDD[i] = CpnDate[i];
            }

            if (NBDayFromEndDate == 0)
            {
                ResultPayDateYYYYMMDD[i] = ResultForwardEndYYYYMMDD[i];
            }
            else
            {
                n = 0;
                for (j = 1; j < 10; j++)
                {
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j);
                    PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                    MOD7 = PayDateExcelType % 7;
                    if ((MOD7 != 1 && MOD7 != 0) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        ResultPayDateYYYYMMDD[i] = PayDateYYYYMMDD;
                        break;
                    }
                }
            }
        }

        if (CpnDate) free(CpnDate);
    }

    return 1;
}

double DayCountFractionAtoB(long Day1, long Day2, long Flag)
{
    long i;
    double tau;
    long imax;
    double Div;

    if (Day1 < 19000101) Day1 = ExcelDateToCDate(Day1);
    if (Day2 < 19000101) Day2 = ExcelDateToCDate(Day2);

    if (Flag == 0) return DayCountAtoB(Day1, Day2) / 365.0;
    else if (Flag == 1) return DayCountAtoB(Day1, Day2) / 360.;
    else if (Flag == 2)
    {
        // Act/Act
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

double GPrimePrime_Over_GPrime(double CpnRate, double YTM, long PriceDate, double SwapMaturity, double FreqMonth)
{
    long i, j;
    double Gp, Gpp;
    double Deltat;
    double T;

    long AnnCpnOneYear = (long)(12.0 / FreqMonth + 0.01);
    long SwapEndDate = EDate_Cpp(PriceDate, (long)(SwapMaturity * 12.0));
    long NCpnDates = 0;
    long FirstCpnDate = PriceDate;
    long* CpnDates = Generate_CpnDate(PriceDate, SwapEndDate, AnnCpnOneYear, NCpnDates, FirstCpnDate);

    Gp = 0.;
    Gpp = 0.;
    for (i = 0; i < NCpnDates; i++)
    {
        T = DayCountFractionAtoB(PriceDate, CpnDates[i], 3);
        if (i == 0) Deltat = DayCountFractionAtoB(PriceDate, CpnDates[i], 3);
        else Deltat = DayCountFractionAtoB(CpnDates[i - 1], CpnDates[i], 3);

        Gp = Gp - CpnRate * Deltat * T * pow(1. + YTM, -T);
        Gpp = Gpp + CpnRate * Deltat * T * T * pow(1. + YTM, -T);

        if (i == NCpnDates - 1)
        {
            Gp = Gp - T * pow(1.0 + YTM, -T);
            Gpp = Gpp + T * T * pow(1.0 + YTM, -T);
        }
    }
    free(CpnDates);
    return (Gpp / 100.) / Gp;
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
    FRate = denominator / (double)(NHoliday + 1) * (DF1 / DF2 - 1.0);
    return FRate;
}

/////////////////////////////
// Forward Swap Rate 계산 ///
/////////////////////////////
double FSR(
    long PricingDate,
    long SwapStartDate,
    long SwapMaturity,
    long NCPN_Ann,
    long DayCountFlag,
    long NHoliday,
    long* Holiday,
    double* Term,            // 기간구조 Term Array
    double* Rate,            // 기간구조 Rate Array
    long NTerm,                // 기간구조 Term 개수
    double* TermDisc,
    double* RateDisc,
    long NTermDisc
)
{
    long i;
    double Swap_Rate;

    long NCpnDate = 0;
    long FirstCpnDate = SwapStartDate;
    long* CpnDate = Generate_CpnDate_Holiday(SwapStartDate, SwapMaturity, NCPN_Ann, NCpnDate, FirstCpnDate, NHoliday, Holiday);
    double t = 0.0;
    t = ((double)DayCountAtoB(PricingDate, SwapStartDate)) / 365.0;
    double* P0T = (double*)malloc(sizeof(double) * (NCpnDate + 1));
    P0T[0] = Calc_Discount_Factor(Term, Rate, NTerm, t);
    for (i = 1; i < NCpnDate + 1; i++)
    {
        t = ((double)DayCountAtoB(PricingDate, CpnDate[i - 1])) / 365.0;
        P0T[i] = Calc_Discount_Factor(Term, Rate, NTerm, t);
    }

    double a, b, dt;
    a = P0T[0] - P0T[NCpnDate];
    b = 0.0;
    for (i = 0; i < NCpnDate; i++)
    {
        t = ((double)DayCountAtoB(PricingDate, CpnDate[i])) / 365.0;

        if (i == 0) dt = DayCountFractionAtoB(SwapStartDate, CpnDate[i], DayCountFlag);
        else dt = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFlag);
        b += dt * Calc_Discount_Factor(TermDisc, RateDisc, NTermDisc, t);
    }
    Swap_Rate = a / b;

    if (CpnDate) free(CpnDate);
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

    long HolidayFlag_Ref;        // 기초금리 Holiday Calc Flag
    long NHolidays_Ref;            // 기초금리 Holiday 개수
    long* Holidays_Ref;    // 기초금리 평가일 to Holiday

    double* FixedRefRate;        // 과거 확정금리 데이터
    double* Slope;                // 기초금리에 대한 페이오프 기울기
    double* CPN;                // 쿠폰이자율

    long LockOutRef;            //  LockOut 날짜 N영업일
    long LookBackRef;            //  LookBack 날짜 
    long ObservationShift;        //  Observation Shift 할 지여부

    long NRefHistory;            // 오버나이트 히스토리 개수
    long* RefHistoryDate;        // 오버나이트 히스토리 날짜
    double* RefHistory;            // 오버나이트 금리 히스토리

    long N_NotHoliday;          // Holiday가 아닌 영업일 Array개수
    long* NotHoliday;
    long* DayCount_NotHoliday;
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
        T1 = ((double)DayCountAtoB(Float_Schedule->ForwardStart_C[0], Float_Schedule->ForwardEnd_C[i])) / 365.0;
        TPay = ((double)DayCountAtoB(Float_Schedule->ForwardStart_C[0], Float_Schedule->PayDate_C[i])) / 365.0;
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
            FX = FX_FloCurve.Interpolated_Rate(TPay);
        }

        FloatValue += NA * FX * (P0 / P1 - 1.0) * P_Pay;
        P0 = P1;
    }

    if (Fix_Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    FixValue = 0.0;
    for (i = 0; i < Fix_Schedule->NCF; i++)
    {
        dt_Fix = DayCountFractionAtoB(Fix_Schedule->StartDate_C[i], Fix_Schedule->EndDate_C[i], Fix_Schedule->DayCount);
        TPay = DayCountFractionAtoB(Fix_Schedule->StartDate_C[0], Fix_Schedule->PayDate_C[i], Fix_Schedule->DayCount);
        P_Pay = exp(-Fix_DiscCurve.Interpolated_Rate(TPay) * TPay);

        if (CalcCRSFlag == 0)
        {
            NA = 1.0;
            FX = 1.0;
        }
        else
        {
            NA = Fix_Schedule->NotionalAmount;
            FX = FX_FixCurve.Interpolated_Rate(TPay);
        }

        FixValue += NA * FX * P_Pay * dt_Fix;
    }

    IRSpread = FloatValue / FixValue;
    return IRSpread;
}

double SOFR_ForwardRate_Compound(
    long PriceDate,
    curveinfo& RefCurve,
    long ForwardStartYYYYMMDD,
    long ForwardEndYYYYMMDD,
    long LockOutDays,
    long LookBackDays,
    long ObservShift,
    long HolidayFlag,
    long N_NotHoliday,
    long* NotHoliday,
    long* DayCountNotHoliday,
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

    long DayYYYYMMDD;

    long NRefCrvTerm = RefCurve.nterm();
    double* RefCrvTerm = RefCurve.Term;
    double* RefCrvRate = RefCurve.Rate;

    long nday = DayCountAtoB(ForwardStartYYYYMMDD, ForwardEndYYYYMMDD);

    long HistDayIdx = 0;
    long AverageFlag = 0;
    if (SOFRUseFlag == 3) AverageFlag = 1;

    long TimePos = 0;
    long TimePos2 = 0;
    double T1Est, T2Est, T3Est, Delta_T1_T2;

    double dt = 1.0 / 365.0;
    double PrevForwardRate;
    double ForwardRate;

    double t = 0.0;
    double PI_0;

    long EstStart = ForwardStartYYYYMMDD;
    long EstEnd = ForwardEndYYYYMMDD;
    if (isin(ForwardStartYYYYMMDD, NotHoliday, N_NotHoliday)) EstStart = ForwardStartYYYYMMDD;
    else
    {
        for (i = 0; i < N_NotHoliday - 1; i++)
        {
            if (NotHoliday[i] < ForwardStartYYYYMMDD && NotHoliday[i + 1] > ForwardStartYYYYMMDD)
            {
                EstStart = NotHoliday[i + 1];
                break;
            }
        }
    }
    if (isin(ForwardEndYYYYMMDD, NotHoliday, N_NotHoliday)) EstEnd = ForwardEndYYYYMMDD;
    else
    {
        for (i = 0; i < N_NotHoliday - 1; i++)
        {
            if (NotHoliday[i] < ForwardEndYYYYMMDD && NotHoliday[i + 1] > ForwardEndYYYYMMDD)
            {
                EstEnd = NotHoliday[i + 1];
                break;
            }
        }
    }

    long EstStartIdx = isinfindindex(EstStart, NotHoliday, N_NotHoliday);
    long EstEndIdx = isinfindindex(EstEnd, NotHoliday, N_NotHoliday);
    double T = ((double)DayCountAtoB(EstStart, EstEnd)) / denominator;
    double CurrentRate = Calc_Forward_Rate(RefCrvTerm, RefCrvRate, NRefCrvTerm, 0., dt);
    PrevForwardRate = CurrentRate;

    long ObservShiftFlag = 0;
    if (LookBackDays > 0 && ObservShift > 0) ObservShiftFlag = 1;

    ///////////////////////////
    // Average 키움증권 추가 //
    ///////////////////////////
    long NCumpound = 0;
    double AverageRate = 0.0;

    ///////////////////////////
    // N영업일 전 LockOutDay 계산
    ///////////////////////////
    long LockOutDay = EstEnd;
    if (LockOutDays > 0) LockOutDay = NotHoliday[max(0, EstEndIdx - LockOutDays)];

    ///////////////////////////
    // Holiday Rate가 Interpolate일 때 사용할 변수
    ///////////////////////////
    double TargetRate[2] = { 0.0,0.0 };
    double TargetT[2] = { 0.0,0.0 };

    PI_0 = 1.0;
    if (LookBackDays < 1) LookBackDays = 0;

    for (i = EstStartIdx; i < EstEndIdx; i++)
    {
        DayYYYYMMDD = NotHoliday[i];
        T1Est = ((double)DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays)])) / 365.0;
        T2Est = ((double)DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays + 1)])) / 365.0;

        if (ObservShiftFlag == 0) Delta_T1_T2 = ((double)DayCountNotHoliday[i]) / denominator;
        else Delta_T1_T2 = ((double)DayCountNotHoliday[max(0, i - LookBackDays)]) / denominator;

        if (T1Est < 0.0)
        {
            HistDayIdx = isinfindindex(NotHoliday[max(0, i - LookBackDays)], RefHistoryDate, NRefHistory);
            if (HistDayIdx >= 0) ForwardRate = RefHistory[HistDayIdx];
            else ForwardRate = CurrentRate;
        }
        else
        {
            if (DayYYYYMMDD < LockOutDay)
            {
                if (HolidayFlag == 0)
                {
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, NRefCrvTerm, T1Est, T2Est, Delta_T1_T2);
                }
                else
                {
                    T3Est = ((double)DayCountAtoB(PriceDate, NotHoliday[max(0, min(N_NotHoliday - 1, i - LookBackDays + 2))])) / 365.0;
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, NRefCrvTerm, T2Est, T3Est, Delta_T1_T2);
                }
            }
            else
            {
                ForwardRate = PrevForwardRate;
            }
        }
        PI_0 *= 1.0 + ForwardRate * Delta_T1_T2;
        AverageRate += ForwardRate;

        PrevForwardRate = ForwardRate;
        NCumpound += 1;
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
    long ObservShift
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
        if (Float_Schedule->PriceDate_C < Float_Schedule->PayDate_C[i])
        {
            Day1 = DayCountAtoB(Float_Schedule->ForwardStart_C[0], Float_Schedule->ForwardEnd_C[i]);// Float_Schedule->Days_ForwardEnd[i] - Float_Schedule->Days_ForwardStart[0];
            TPay = ((double)DayCountAtoB(Float_Schedule->PriceDate_C, Float_Schedule->PayDate_C[i])) / 365.0;
            SOFR_Compound = SOFR_ForwardRate_Compound(Float_Schedule->PriceDate_C, Float_RefCurve, Float_Schedule->ForwardStart_C[i], Float_Schedule->ForwardEnd_C[i], LockOutDays,
                LookBackDays, ObservShift, Float_Schedule->HolidayFlag_Ref, Float_Schedule->N_NotHoliday, Float_Schedule->NotHoliday,
                Float_Schedule->DayCount_NotHoliday, Float_Schedule->NRefHistory, Float_Schedule->RefHistoryDate, Float_Schedule->RefHistory, denominator, Annual_OIS, 1);
            P_Pay = exp(-Float_DiscCurve.Interpolated_Rate(TPay) * TPay);

            if (CalcCRSFlag == 0)
            {
                NA = 1.0;
                FX = 1.0;
            }
            else
            {
                NA = Float_Schedule->NotionalAmount;
                FX = Float_FXCurve.Interpolated_Rate(TPay);
            }

            FloatValue += NA * FX * SOFR_Compound * P_Pay;
        }
    }

    if (Fix_Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    FixValue = 0.0;
    for (i = 0; i < Fix_Schedule->NCF; i++)
    {
        if (Fix_Schedule->PriceDate_C < Fix_Schedule->PayDate_C[i])
        {
            dt_Fix = DayCountFractionAtoB(Fix_Schedule->StartDate_C[i], Fix_Schedule->EndDate_C[i], Fix_Schedule->DayCount);
            TPay = ((double)DayCountAtoB(Fix_Schedule->PriceDate_C, Fix_Schedule->PayDate_C[i])) / 365.0;
            P_Pay = exp(-Fix_DiscCurve.Interpolated_Rate(TPay) * TPay);

            if (CalcCRSFlag == 0)
            {
                NA = 1.0;
                FX = 1.0;
            }
            else
            {
                NA = Fix_Schedule->NotionalAmount;
                FX = Fix_FXCurve.Interpolated_Rate(TPay);
            }
            FixValue += NA * FX * P_Pay * dt_Fix;
        }
    }

    SOFR_Swap_Spread = FloatValue / FixValue;
    return SOFR_Swap_Spread;
}

double Calc_Forward_SOFR_Swap(
    long PriceDate,
    long SwapStartDate,
    long SwapMaturity,
    long NCPN_Ann,
    long DayCountFrac,
    curveinfo& Float_DiscCurve,
    curveinfo& Float_RefCurve,
    curveinfo& Fix_DiscCurve,
    long HolidayCalcFlag,
    long NHoliday,
    long* Holiday,
    long N_NotHoliday,
    long* NotHoliday,
    long* DayCountNotHoliday,
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
    double t;

    long NCpnDate = 0;
    long FirstCpnDate = SwapStartDate;
    long* CpnDate = Generate_CpnDate_Holiday(SwapStartDate, SwapMaturity, NCPN_Ann, NCpnDate, FirstCpnDate, NHoliday, Holiday);

    double* P0T = (double*)malloc(sizeof(double) * (NCpnDate + 1));
    if (PriceDate == SwapStartDate) t = 0.;
    else t = ((double)DayCountAtoB(PriceDate, SwapStartDate)) / 365.0;
    P0T[0] = Calc_Discount_Factor(Fix_DiscCurve.Term, Fix_DiscCurve.Rate, Fix_DiscCurve.nterm(), t); // 옵션만기시점

    for (i = 1; i < NCpnDate + 1; i++)
    {
        t = ((double)DayCountAtoB(PriceDate, CpnDate[i - 1]));
        P0T[i] = Calc_Discount_Factor(Fix_DiscCurve.Term, Fix_DiscCurve.Rate, Fix_DiscCurve.nterm(), t);
    }

    double* P0T_Float = (double*)malloc(sizeof(double) * (NCpnDate + 1));
    if (PriceDate == SwapStartDate) t = 0.;
    else t = ((double)DayCountAtoB(PriceDate, SwapStartDate)) / 365.0;
    P0T_Float[0] = Calc_Discount_Factor(Float_DiscCurve.Term, Float_DiscCurve.Rate, Float_DiscCurve.nterm(), t);

    for (i = 1; i < NCpnDate + 1; i++)
    {
        t = ((double)DayCountAtoB(PriceDate, CpnDate[i - 1]));
        P0T_Float[i] = Calc_Discount_Factor(Float_DiscCurve.Term, Float_DiscCurve.Rate, Float_DiscCurve.nterm(), t);
    }

    double SOFR_Swap_Spread;
    double P_Pay;
    double FloatValue, FixValue;
    double SOFR_Compound;
    double Annual_OIS = 0.0;


    FloatValue = 0.0;
    for (i = 0; i < NCpnDate; i++)
    {
        if (i == 0)
        {
            SOFR_Compound = SOFR_ForwardRate_Compound(PriceDate, Float_RefCurve, SwapStartDate, CpnDate[i], Float_RefLockOut,
                Float_RefLookBack, ObservationShift, HolidayCalcFlag, N_NotHoliday, NotHoliday,
                DayCountNotHoliday, NRefHistory, RefHistoryDate, RefHistory, denominator, Annual_OIS, 1);
        }
        else
        {
            SOFR_Compound = SOFR_ForwardRate_Compound(PriceDate, Float_RefCurve, CpnDate[i - 1], CpnDate[i], Float_RefLockOut,
                Float_RefLookBack, ObservationShift, HolidayCalcFlag, N_NotHoliday, NotHoliday,
                DayCountNotHoliday, NRefHistory, RefHistoryDate, RefHistory, denominator, Annual_OIS, 1);
        }
        P_Pay = P0T_Float[i + 1];
        FloatValue += SOFR_Compound * P_Pay;
    }

    FixValue = 0.0;
    for (i = 0; i < NCpnDate; i++)
    {
        if (i == 0) dt = DayCountFractionAtoB(SwapStartDate, CpnDate[0], DayCountFrac);
        else dt = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFrac);
        FixValue += dt * P0T[i + 1];
    }

    SOFR_Swap_Spread = FloatValue / FixValue;

    free(CpnDate);
    free(P0T_Float);
    free(P0T);
    return SOFR_Swap_Spread;
}

void Floating_PartialValue(
    long PricingDate,
    long CalcCRSFlag,
    curveinfo& DiscCurve,
    curveinfo& RefCurve,
    curveinfo& FXCurve,
    long FixedRateFlag,
    double FixedRate,
    double Slope,
    double FixedAmount,
    double Notional,
    long YYYYMMDDForwardStart,
    long YYYYMMDDForwardEnd,
    long YYYYMMDDStart,
    long YYYYMMDDEnd,
    long YYYYMMDDPay,
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
    double Pay_T = ((double)DayCountAtoB(PricingDate, YYYYMMDDPay)) / 365.0;
    if (CalcCRSFlag == 0) FX = 1.0;
    else FX = FXCurve.Interpolated_Rate(Pay_T);
    double Ref_T0 = ((double)DayCountAtoB(PricingDate, YYYYMMDDForwardStart)) / 365.0;
    double Ref_T1 = ((double)DayCountAtoB(PricingDate, YYYYMMDDForwardEnd)) / 365.0;
    dt_Forward = DayCountFractionAtoB(YYYYMMDDForwardStart, YYYYMMDDForwardEnd, DayCountFlag);
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
    long SwapMaturityYYYYMMDD;
    double denominator;
    double dt;

    if (Schedule->DayCount == 0) denominator = 365.0;
    else denominator = 360.0;

    double FSRVol;
    double GppOvGp;
    double ConvAdjAmt;

    ///////////////
    // SOFR 관련 //
    ///////////////

    long UseHistorySOFR;
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
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C)
                {
                    PrevFlag = 0;
                }

                if (PrevFlag == 0)
                {
                    if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C) FixedRateFlag = 1;
                    else FixedRateFlag = 0;

                    Floating_PartialValue(
                        Schedule->PriceDate_C, CRSFlag, DiscCurve, RefCurve, FXCurve,
                        FixedRateFlag, Schedule->FixedRefRate[i], Schedule->Slope[i], Schedule->CPN[i], Schedule->NotionalAmount,
                        Schedule->ForwardStart_C[i], Schedule->ForwardEnd_C[i], Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->PayDate_C[i],
                        Schedule->DayCount, ResultRefRate + i, ResultCPN + i, ResultDF + i, DiscCFArray + i);
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
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    SwapMaturityYYYYMMDD = EDate_Cpp(Schedule->ForwardStart_C[i], (long)(Schedule->RefSwapMaturity * 12.0 + 0.01));
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;
                    dt = DayCountFractionAtoB(Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount);
                    SwapStartT = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->ForwardStart_C[i])) / 365.0;

                    if (Schedule->ForwardStart_C[i] <= Schedule->PriceDate_C) FixedRateFlag = 1;
                    else FixedRateFlag = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = FXCurve.Interpolated_Rate(Pay_T);

                    FreqMonth = 12.0 / (double)Schedule->NSwapPayAnnual;
                    if (FixedRateFlag == 0)
                    {
                        ResultRefRate[i] = FSR(Schedule->PriceDate_C, Schedule->ForwardStart_C[i], SwapMaturityYYYYMMDD, Schedule->NSwapPayAnnual, Schedule->DayCount, Schedule->NHolidays_Ref, Schedule->Holidays_Ref, RefCurve.Term, RefCurve.Rate, RefCurve.nterm(), DiscCurve.Term, DiscCurve.Rate, DiscCurve.nterm());
                        if (ConvAdjFlag > 0)
                        {
                            FSRVol = Interpolate_Linear(ConvAdjVolTerm, ConvAdjVol, NConvAdjVolTerm, SwapStartT);
                            GppOvGp = GPrimePrime_Over_GPrime(ResultRefRate[i], ResultRefRate[i], Schedule->ForwardStart_C[i], Schedule->RefSwapMaturity, FreqMonth);
                            ConvAdjAmt = GppOvGp * FSRVol * FSRVol * 100. * SwapStartT * 0.5;
                            ResultRefRate[i] = ResultRefRate[i] - ConvAdjAmt;
                        }
                        ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * dt;
                        ResultDF[i] = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                        DiscCFArray[i] = ResultCPN[i] * ResultDF[i];
                    }
                    else
                    {
                        //////////////////////////////////////////////////////////////////////////
                        // 입력해둔 과거 금리가 존재하면 그거 사용하고 아니면 현재 스왑금리사용 //
                        //////////////////////////////////////////////////////////////////////////

                        if (Schedule->FixedRefRate[i] > 0.00001 || Schedule->FixedRefRate[i] < -0.00001) ResultRefRate[i] = Schedule->FixedRefRate[i];
                        else ResultRefRate[i] = FSR(Schedule->PriceDate_C, Schedule->ForwardStart_C[i], SwapMaturityYYYYMMDD, Schedule->NSwapPayAnnual, Schedule->DayCount, Schedule->NHolidays_Ref, Schedule->Holidays_Ref, RefCurve.Term, RefCurve.Rate, RefCurve.nterm(), DiscCurve.Term, DiscCurve.Rate, DiscCurve.nterm());

                        ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * dt;
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
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;
                    dt = DayCountFractionAtoB(Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount);

                    if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C) UseHistorySOFR = 1;
                    else UseHistorySOFR = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = Interpolate_Linear(FXCurve.Term, FXCurve.Rate, FXCurve.nterm(), Pay_T);

                    OIS_Compound = SOFR_ForwardRate_Compound(Schedule->PriceDate_C, RefCurve, Schedule->ForwardStart_C[i], Schedule->ForwardEnd_C[i], Schedule->LockOutRef,
                        Schedule->LookBackRef, Schedule->ObservationShift, Schedule->HolidayFlag_Ref, Schedule->N_NotHoliday, Schedule->NotHoliday,
                        Schedule->DayCount_NotHoliday, Schedule->NRefHistory, Schedule->RefHistoryDate, Schedule->RefHistory, denominator,
                        OIS_Annual, 1);

                    ResultRefRate[i] = OIS_Annual;
                    ResultCPN[i] = FXRate * Schedule->NotionalAmount * (OIS_Compound * Schedule->Slope[i]) + FXRate * Schedule->NotionalAmount * Schedule->CPN[i] * dt;
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
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;
                    dt = DayCountFractionAtoB(Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount);
                    SwapStartT = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->ForwardStart_C[i])) / 365.0;

                    if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C) UseHistorySOFR = 1;
                    else UseHistorySOFR = 0;

                    if (CRSFlag == 0) FXRate = 1.0;
                    else FXRate = Interpolate_Linear(FXCurve.Term, FXCurve.Rate, FXCurve.nterm(), Pay_T);

                    SwapMaturityYYYYMMDD = EDate_Cpp(Schedule->ForwardStart_C[i], (long)(Schedule->RefSwapMaturity * 12.0 + 0.01));
                    FreqMonth = 12.0 / (double)Schedule->NSwapPayAnnual;

                    ResultRefRate[i] = Calc_Forward_SOFR_Swap(Schedule->PriceDate_C, Schedule->ForwardStart_C[i], SwapMaturityYYYYMMDD, Schedule->NSwapPayAnnual, Schedule->DayCount,
                        RefCurve, DiscCurve, DiscCurve, Schedule->HolidayFlag_Ref, Schedule->NHolidays_Ref,
                        Schedule->Holidays_Ref, Schedule->N_NotHoliday, Schedule->NotHoliday, Schedule->DayCount_NotHoliday,
                        Schedule->NRefHistory, Schedule->RefHistoryDate, Schedule->RefHistory, denominator, Schedule->LockOutRef,
                        Schedule->LookBackRef, Schedule->ObservationShift);
                    if (ConvAdjFlag > 0)
                    {
                        FSRVol = Interpolate_Linear(ConvAdjVolTerm, ConvAdjVol, NConvAdjVolTerm, SwapStartT);
                        GppOvGp = GPrimePrime_Over_GPrime(ResultRefRate[i], ResultRefRate[i], Schedule->ForwardStart_C[i], Schedule->RefSwapMaturity, FreqMonth);
                        ConvAdjAmt = GppOvGp * FSRVol * FSRVol * 100. * SwapStartT * 0.5;
                        ResultRefRate[i] = ResultRefRate[i] - ConvAdjAmt;
                    }

                    ResultCPN[i] = FXRate * Schedule->NotionalAmount * (ResultRefRate[i] * Schedule->Slope[i] + Schedule->CPN[i]) * dt;
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
            if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

            if (PrevFlag == 0)
            {
                Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;
                dt = DayCountFractionAtoB(Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount);

                if (CRSFlag == 0) FX = 1.0;
                else  FX = FXCurve.Interpolated_Rate(Pay_T);

                DiscPay = exp(-DiscCurve.Interpolated_Rate(Pay_T) * Pay_T);
                //FixedLeg_PartialValue(
                //    CRSFlag, DiscCurve, FXCurve, Frac_T0, Frac_T1, Pay_T, Schedule->CPN[i], Schedule->NotionalAmount,
                //    ResultRefRate + i, ResultCPN + i, ResultDF + i, DiscCFArray + i);
                ResultRefRate[i] = 0.0;
                ResultCPN[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] * dt;
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
    PayValue = LegValue(CalcCRSFlag, PaySchedule, Pay_DiscCurve, Pay_RefCurve, Pay_FXCurve, ResultRefRate + RcvSchedule->NCF, ResultCPN + RcvSchedule->NCF, ResultDF + RcvSchedule->NCF, Pay_DiscCFArray, PayConvexityAdjFlag, NPayConvexAdjVol, PayConvAdjVolTerm, PayConvAdjVol);

    //////////////////
    // Notional 반영
    //////////////////

    if (RcvSchedule->NAFlag == 1)
    {
        ResultDF[RcvSchedule->NCF + PaySchedule->NCF] = Calc_Discount_Factor(Rcv_DiscCurve.Term, Rcv_DiscCurve.Rate, Rcv_DiscCurve.nterm(), Rcv_T_Mat);// ResultDF[RcvSchedule->NCF - 1];
        ResultRefRate[RcvSchedule->NCF + PaySchedule->NCF] = 0.0;
        ResultCPN[RcvSchedule->NCF + PaySchedule->NCF] = RcvSchedule->NotionalAmount * Rcv_FXMat;
        if (CalcCRSFlag == 0) RcvValue += RcvSchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF];
        else RcvValue += RcvSchedule->NotionalAmount * ResultDF[RcvSchedule->NCF + PaySchedule->NCF] * Rcv_FXMat;
    }

    if (PaySchedule->NAFlag == 1)
    {
        ResultDF[RcvSchedule->NCF + PaySchedule->NCF + 1] = Calc_Discount_Factor(Pay_DiscCurve.Term, Pay_DiscCurve.Rate, Pay_DiscCurve.nterm(), Pay_T_Mat);//ResultDF[RcvSchedule->NCF + PaySchedule->NCF - 1];
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
            else CurrentIRS = Calc_Current_SOFR_Swap(CalcCRSFlag, Pay_DiscCurve, Pay_RefCurve, Rcv_DiscCurve, Pay_FXCurve, Rcv_FXCurve, PaySchedule, RcvSchedule, PaySchedule->LockOutRef, PaySchedule->LookBackRef, PaySchedule->ObservationShift);
        }
        else
        {
            if (RcvSchedule->ReferenceType < 2 && PaySchedule->ReferenceType < 2) CurrentIRS = Calc_Current_IRS(CalcCRSFlag, Rcv_DiscCurve, Rcv_RefCurve, Pay_DiscCurve, Rcv_FXCurve, Pay_FXCurve, RcvSchedule, PaySchedule);
            else CurrentIRS = Calc_Current_SOFR_Swap(CalcCRSFlag, Rcv_DiscCurve, Rcv_RefCurve, Pay_DiscCurve, Rcv_FXCurve, Pay_FXCurve, RcvSchedule, PaySchedule, RcvSchedule->LockOutRef, RcvSchedule->LookBackRef, RcvSchedule->ObservationShift);
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
            T = ((double)DayCountAtoB(PriceDate_C, RcvSchedule->PayDate_C[RcvSchedule->NCF - 1])) / 365.0;
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
            T = ((double)DayCountAtoB(PriceDate_C, RcvSchedule->PayDate_C[RcvSchedule->NCF - 1])) / 365.0;
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

            T = ((double)DayCountAtoB(PriceDate_C, RcvSchedule->PayDate_C[RcvSchedule->NCF - 1])) / 365.0;

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
            T = ((double)DayCountAtoB(PriceDate_C, PaySchedule->PayDate_C[PaySchedule->NCF - 1])) / 365.0;
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
            T = ((double)DayCountAtoB(PriceDate_C, PaySchedule->PayDate_C[PaySchedule->NCF - 1])) / 365.0;
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


            T = ((double)DayCountAtoB(PriceDate_C, PaySchedule->PayDate_C[PaySchedule->NCF - 1])) / 365.0;
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

long ErrorCheckIRS(
    long PriceDate,                // PricingDate ExcelType
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


    long* Rcv_ForwardStart = RcvCashFlowSchedule;
    long* Rcv_ForwardEnd = RcvCashFlowSchedule + NRcvCF;
    long* Rcv_StartDate = RcvCashFlowSchedule + 2 * NRcvCF;
    long* Rcv_EndDate = RcvCashFlowSchedule + 3 * NRcvCF;
    long* Rcv_PayDate = RcvCashFlowSchedule + 4 * NRcvCF;

    long* Pay_ForwardStart = PayCashFlowSchedule;
    long* Pay_ForwardEnd = PayCashFlowSchedule + NPayCF;
    long* Pay_StartDate = PayCashFlowSchedule + 2 * NPayCF;
    long* Pay_EndDate = PayCashFlowSchedule + 3 * NPayCF;
    long* Pay_PayDate = PayCashFlowSchedule + 4 * NPayCF;

    if (PriceDate <= 0 || PriceDate > Rcv_PayDate[NRcvCF - 1] || PriceDate > Pay_PayDate[NPayCF - 1] || PriceDate < Rcv_ForwardStart[0] - 20000 || PriceDate < Pay_ForwardStart[0] - 20000) return -1;

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
    if (Rcv_NotionalPayDate < PriceDate) return -12;
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
        if (Rcv_ForwardStart[i] >= Rcv_ForwardEnd[i] || Rcv_PayDate[i] < Rcv_ForwardEnd[i]) return -20;
    }

    if (Rcv_RefRateType < 0 || Rcv_RefRateType > 5) return -6;
    if (Rcv_RefRateType == 1 || Rcv_RefRateType == 3)
    {
        if (Rcv_SwapYearlyNPayment <= 0 || Rcv_SwapYearlyNPayment > 12) return -7;
    }
    if (Rcv_SwapMaturity < 0.0) return -8;
    if (Rcv_FixFloFlag != 0 && Rcv_FixFloFlag != 1) return -9;

    if (Rcv_NotionalAMT < 0.0) return -11;
    if (Rcv_NotionalPayDate < PriceDate) return -12;
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
        if (Rcv_ForwardStart[i] >= Rcv_ForwardEnd[i] || Rcv_PayDate[i] < Rcv_ForwardEnd[i]) return -20;
    }

    //
    if (Pay_RefRateType < 0 || Pay_RefRateType > 5) return -6;
    if (Pay_RefRateType == 1 || Pay_RefRateType == 3)
    {
        if (Pay_SwapYearlyNPayment <= 0 || Pay_SwapYearlyNPayment > 12) return -7;
    }
    if (Pay_SwapMaturity < 0.0) return -8;
    if (Pay_FixFloFlag != 0 && Pay_FixFloFlag != 1) return -9;
    if (Pay_DayCount != 0 && Pay_DayCount != 1 && Pay_DayCount != 2 && Pay_DayCount != 3) return -10;
    if (Pay_NotionalAMT < 0.0) return -11;
    if (Pay_NotionalPayDate < PriceDate) return -12;
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
        if (Pay_ForwardStart[i] >= Pay_ForwardEnd[i] || Pay_PayDate[i] < Pay_ForwardEnd[i]) return -20;
    }

    return 0;
}

DLLEXPORT(long) CalcIRS(
    long PriceDate,                    // PricingDate 
    long GreekFlag,                    // Greek산출 Flag
    long NAFlag,                       // Notional 교환 Flag (0:NA교환X, 1:NA교환O, 2:NA교환X TextDump, 3: NA교환O TextDump)
    long* CRS_Flag,                    // [0]CRS Pricing Flag [1]FX선도 Term 개수
    double* CRS_Info,                  // [0~FX개수-1] FX Forward Term, [FX개수-1~2*FX개수-1] FX Forward

    long Rcv_RefRateType,              // Rcv 기초금리 0: Libor/CD 1: Swap 2: SOFR 3:SOFR Swap
    long Rcv_SwapYearlyNPayment,       // Rcv_RefRateType가 1, 3일 때 스왑 연 지급회수
    double Rcv_SwapMaturity,           // Rcv_RefRateType가 1, 3일 때 스왑만기
    long Rcv_FixFloFlag,               // Rcv Fix/Flo Flag
    long Rcv_DayCount,                 // Rcv DayCountConvention 0:Act365  1: Act360 2:ActAct 3:30/360

    double Rcv_NotionalAMT,            // Rcv Leg Notional Amount
    long Rcv_NotionalPayDate,          // Rcv Leg Notional Payment Date
    long RcvDisc_NTerm,                // Rcv Leg 할인 금리 Term 개수
    double* RcvDisc_Term,              // Rcv Leg 할인 금리 Term Array
    double* RcvDisc_Rate,              // Rcv Leg 할인 금리 Rate Array 

    long RcvRef_NTerm,                 // Rcv Leg 레퍼런스 금리 Term 개수
    double* RcvRef_Term,               // Rcv Leg 레퍼런스 금리 Term Array
    double* RcvRef_Rate,               // Rcv Leg 레퍼런스 금리 Rate Array
    long NRcvCF,                       // Rcv Leg CashFlow 개수
    long* RcvCashFlowSchedule,         // Rcv Forward Start, End, 기산, 기말, 지급일

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
    long* PayCashFlowSchedule,          // Pay Forward Start, End, 기산, 기말, 지급일
    double* Pay_Slope,                  // Pay Leg 변동금리 기울기 Array
    double* Pay_CPN,                    // Pay Leg 고정쿠폰 Array

    double* Pay_FixedRefRate,           // Pay Leg 과거 확정금리 Array
    double* ResultPrice,                // Output 계산결과 [0] Current Swap Rate [1] Rcv Value [2] Payment Value
    double* ResultRefRate,              // Output 기초금리 Array [길이 = NCpnRcv + NCpnPay]
    double* ResultCPN,                  // Output 추정 쿠폰 Array[길이 = NCpnRcv + NCpnPay]
    double* ResultDF,                   // Output Discount Factor Array [길이 = NCpnRcv + NCpnPay]

    double* PV01,                       // Output PV01[0]RcvDisc [1]RcvRef [2]both [3]PayDisc [4]PayRef [5]both
    double* KeyRateRcvPV01,             // Output Rcv Key Rate PV01 .rehaped(-1)
    double* KeyRatePayPV01,             // Output Pay KeyRate PV01 .reshaped(-1)
    long* SOFRConv,                     // [0~2] Rcv LockOut LookBackFlag [3~5] Pay LockOut LookBackFlag
    long* HolidayCalcFlag,              // Holiday관련 인풋 Flag [0]: Rcv [1]: Pay

    long* NHolidays,                    // Holiday 개수 [0] NRcvRef [1] NPayRef
    long* Holidays,                     // Holiday
    long* NHistory,                     // OverNight History 개수
    long* HistoryDate,                  // OverNight History
    double* HistoryRate,                // OverNight Rate History

    long* RcvPayConvexityAdjFlag,       // [0] RcvLeg Convexity 보정Flag [1] PayLeg Convexity 보정Flag
    long* NRcvPayConvexAdjVol,          // [0] Rcv Vol개수 [1] Pay Vol개수
    double* RcvTermAndVol,              // [~NRcvConvexAdj] RcvVolTerm, [NRcvConvexAdj~2NRcvConvexAdj-1] RcvVol
    double* PayTermAndVol               // [~NPayConvexAdj] RcvVolTerm, [NPayConvexAdj~2NPayConvexAdj-1] PayVol
)
{
    long i;
    if (PriceDate < 19000101) PriceDate = ExcelDateToCDate(PriceDate);
    if (Rcv_NotionalPayDate < 19000101) Rcv_NotionalPayDate = ExcelDateToCDate(Rcv_NotionalPayDate);
    if (Pay_NotionalPayDate < 19000101) Pay_NotionalPayDate = ExcelDateToCDate(Pay_NotionalPayDate);
    for (i = 0; i < 5 * NRcvCF; i++) if (RcvCashFlowSchedule[i] < 19000101) RcvCashFlowSchedule[i] = ExcelDateToCDate(RcvCashFlowSchedule[i]);
    for (i = 0; i < 5 * NPayCF; i++) if (PayCashFlowSchedule[i] < 19000101) PayCashFlowSchedule[i] = ExcelDateToCDate(PayCashFlowSchedule[i]);
    for (i = 0; i < NHolidays[0] + NHolidays[1]; i++) if (Holidays[i] < 19000101) Holidays[i] = ExcelDateToCDate(Holidays[i]);
    for (i = 0; i < NHistory[0] + NHistory[1]; i++) if (HistoryDate[i] < 19000101) HistoryDate[i] = ExcelDateToCDate(HistoryDate[i]);

    long j;
    long k;
    long n;
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

    ResultCode = ErrorCheckIRS(
        PriceDate, GreekFlag, NAFlag, CRS_Flag, CRS_Info,
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
        DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate_Exl", PriceDate);
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
        DumppingTextDataArray(CalcFunctionName, SaveFileName, "HistoryDateExl", NHistory[0] + NHistory[1], HistoryDate);
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

    long* Rcv_ForwardStart = RcvCashFlowSchedule;
    long* Rcv_ForwardEnd = RcvCashFlowSchedule + NRcvCF;
    long* Rcv_StartDate = RcvCashFlowSchedule + 2 * NRcvCF;
    long* Rcv_EndDate = RcvCashFlowSchedule + 3 * NRcvCF;
    long* Rcv_PayDate = RcvCashFlowSchedule + 4 * NRcvCF;

    long* Pay_ForwardStart = PayCashFlowSchedule;
    long* Pay_ForwardEnd = PayCashFlowSchedule + NPayCF;
    long* Pay_StartDate = PayCashFlowSchedule + 2 * NPayCF;
    long* Pay_EndDate = PayCashFlowSchedule + 3 * NPayCF;
    long* Pay_PayDate = PayCashFlowSchedule + 4 * NPayCF;

    //////////////////
    // SOFR History //
    long Rcv_NHistory = NHistory[0];
    long Pay_NHistory = NHistory[1];
    long* Rcv_HistoryDate = HistoryDate;
    long* Pay_HistoryDate = HistoryDate + Rcv_NHistory;
    double* Rcv_HistoryRate = HistoryRate;
    double* Pay_HistoryRate = HistoryRate + Rcv_NHistory;

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

    ////////////////////////////////////////////
    // Holiday 매핑, 너무 과거나 너무 미래인거 빼고
    ////////////////////////////////////////////

    long NHolidays_Array[2] = { 0,0 };
    long MaxDay;
    long MinDay;

    long RcvRef_HolidayCalc = HolidayCalcFlag[0];
    long PayRef_HolidayCalc = HolidayCalcFlag[1];

    long RcvRef_NHolidays = NHolidays[0];
    long PayRef_NHolidays = NHolidays[1];

    long* RcvRef_Holidays = Holidays;
    long* PayRef_Holidays = Holidays + RcvRef_HolidayCalc;

    MaxDay = EDate_Cpp(max(Rcv_PayDate[NPayCF - 1], Pay_PayDate[NPayCF - 1]), 1);
    MinDay = min(min(PriceDate, min(EDate_Cpp(Rcv_ForwardStart[0], -12), Pay_ForwardStart[0])), min(Rcv_StartDate[0], Pay_StartDate[0]));
    // RcvRef
    NHolidays_Array[0] = 0;
    for (i = 0; i < RcvRef_NHolidays; i++)
    {
        if (RcvRef_Holidays[i] <= MaxDay && RcvRef_Holidays[i] > MinDay)
        {
            NHolidays_Array[0] += 1;
        }
    }
    long* RcvRef_Holiday_Optimal = (long*)malloc(sizeof(long) * max(1, NHolidays_Array[0]));            // 1
    k = 0;
    for (i = 0; i < RcvRef_NHolidays; i++)
    {
        if (RcvRef_Holidays[i] <= MaxDay && RcvRef_Holidays[i] > MinDay)
        {
            RcvRef_Holiday_Optimal[k] = RcvRef_Holidays[i];
            k += 1;
        }
    }

    // PayRef
    NHolidays_Array[1] = 0;
    for (i = 0; i < PayRef_NHolidays; i++)
    {
        if (PayRef_Holidays[i] <= MaxDay && PayRef_Holidays[i] > MinDay)
        {
            NHolidays_Array[1] += 1;
        }
    }
    long* PayRef_Holiday_Optimal = (long*)malloc(sizeof(long) * max(1, NHolidays_Array[1]));            // 2
    k = 0;
    for (i = 0; i < PayRef_NHolidays; i++)
    {
        if (PayRef_Holidays[i] <= MaxDay && PayRef_Holidays[i] > MinDay)
        {
            PayRef_Holiday_Optimal[k] = PayRef_Holidays[i];
            k += 1;
        }
    }

    long isHolidayFlag_Rcv, isHolidayFlag_Pay, isWeekendFlag;
    long StartDayExl, EndDayExl, TempDayYYYYMMDD, TempDayExl;
    long NumberNotHoliday_Rcv, NumberNotHoliday_Pay;
    StartDayExl = CDateToExcelDate(MinDay);
    EndDayExl = CDateToExcelDate(MaxDay);
    NumberNotHoliday_Rcv = 0;
    NumberNotHoliday_Pay = 0;
    for (TempDayExl = StartDayExl; TempDayExl <= EndDayExl; TempDayExl++)
    {
        TempDayYYYYMMDD = ExcelDateToCDate(TempDayExl);
        isWeekendFlag = isweekend(TempDayExl);
        isHolidayFlag_Rcv = isin(TempDayYYYYMMDD, RcvRef_Holiday_Optimal, NHolidays_Array[0]);
        isHolidayFlag_Pay = isin(TempDayYYYYMMDD, PayRef_Holiday_Optimal, NHolidays_Array[1]);
        if (isWeekendFlag == 0 && isHolidayFlag_Rcv == 0)
        {
            NumberNotHoliday_Rcv += 1;
        }
        if (isWeekendFlag == 0 && isHolidayFlag_Pay == 0)
        {
            NumberNotHoliday_Pay += 1;
        }
    }

    long* NotHoliday_YYYYMMDD_Rcv = (long*)malloc(sizeof(long) * NumberNotHoliday_Rcv);             // 3
    long* NotHoliday_YYYYMMDD_Pay = (long*)malloc(sizeof(long) * NumberNotHoliday_Pay);             // 4
    k = 0;
    n = 0;
    for (TempDayExl = StartDayExl; TempDayExl <= EndDayExl; TempDayExl++)
    {
        TempDayYYYYMMDD = ExcelDateToCDate(TempDayExl);
        isWeekendFlag = isweekend(TempDayExl);
        isHolidayFlag_Rcv = isin(TempDayYYYYMMDD, RcvRef_Holiday_Optimal, NHolidays_Array[0]);
        isHolidayFlag_Pay = isin(TempDayYYYYMMDD, PayRef_Holiday_Optimal, NHolidays_Array[1]);
        if (isWeekendFlag == 0 && isHolidayFlag_Rcv == 0)
        {
            NotHoliday_YYYYMMDD_Rcv[k] = TempDayYYYYMMDD;
            k += 1;
        }
        if (isWeekendFlag == 0 && isHolidayFlag_Pay == 0)
        {
            NotHoliday_YYYYMMDD_Pay[n] = TempDayYYYYMMDD;
            n += 1;
        }
    }

    long* NotHoliday_DayCount_Rcv = (long*)malloc(sizeof(long) * NumberNotHoliday_Rcv);             // 5
    long* NotHoliday_DayCount_Pay = (long*)malloc(sizeof(long) * NumberNotHoliday_Pay);             // 6
    for (i = 0; i < NumberNotHoliday_Rcv - 1; i++) NotHoliday_DayCount_Rcv[i] = DayCountAtoB(NotHoliday_YYYYMMDD_Rcv[i], NotHoliday_YYYYMMDD_Rcv[i + 1]);
    for (i = 0; i < NumberNotHoliday_Pay - 1; i++) NotHoliday_DayCount_Pay[i] = DayCountAtoB(NotHoliday_YYYYMMDD_Pay[i], NotHoliday_YYYYMMDD_Pay[i + 1]);

    ////////////////////////////////
    // Receive Schedule Mapping  ///
    ////////////////////////////////

    SCHD* Rcv_Schedule = new SCHD;
    Rcv_Schedule->HolidayFlag_Ref = RcvRef_HolidayCalc;
    Rcv_Schedule->NHolidays_Ref = NHolidays_Array[0];
    Rcv_Schedule->Holidays_Ref = RcvRef_Holidays;
    Rcv_Schedule->NCF = NRcvCF;
    Rcv_Schedule->ForwardStart_C = Rcv_ForwardStart;
    Rcv_Schedule->ForwardEnd_C = Rcv_ForwardEnd;
    Rcv_Schedule->StartDate_C = Rcv_StartDate;
    Rcv_Schedule->EndDate_C = Rcv_EndDate;
    Rcv_Schedule->PayDate_C = Rcv_PayDate;
    Rcv_Schedule->NotionalPayDate_C = Rcv_NotionalPayDate;
    Rcv_Schedule->ReferenceType = Rcv_RefRateType;
    Rcv_Schedule->FixedFlotype = Rcv_FixFloFlag;
    Rcv_Schedule->DayCount = Rcv_DayCount;
    Rcv_Schedule->NotionalAmount = Rcv_NotionalAMT;
    Rcv_Schedule->NRefHistory = Rcv_NHistory;
    Rcv_Schedule->RefHistoryDate = Rcv_HistoryDate;
    Rcv_Schedule->RefHistory = Rcv_HistoryRate;

    if (Rcv_RefRateType != 0 && Rcv_RefRateType != 2) Rcv_Schedule->RefSwapFlag = 1;
    Rcv_Schedule->NSwapPayAnnual = Rcv_SwapYearlyNPayment;
    Rcv_Schedule->RefSwapMaturity = Rcv_SwapMaturity;
    Rcv_Schedule->FixedRefRate = Rcv_FixedRefRate;
    Rcv_Schedule->Slope = Rcv_Slope;
    Rcv_Schedule->CPN = Rcv_CPN;
    Rcv_Schedule->NAFlag = NAFlag;
    Rcv_Schedule->PriceDate_C = PriceDate;

    Rcv_Schedule->LockOutRef = SOFRConv[0];
    Rcv_Schedule->LookBackRef = SOFRConv[1];
    Rcv_Schedule->ObservationShift = SOFRConv[2];
    Rcv_Schedule->N_NotHoliday = NumberNotHoliday_Rcv;
    Rcv_Schedule->NotHoliday = NotHoliday_YYYYMMDD_Rcv;
    Rcv_Schedule->DayCount_NotHoliday = NotHoliday_DayCount_Rcv;
    ////////////////////////////
    // Pay Schedule Mapping  ///
    ////////////////////////////

    SCHD* Pay_Schedule = new SCHD;
    Pay_Schedule->HolidayFlag_Ref = RcvRef_HolidayCalc;
    Pay_Schedule->NHolidays_Ref = NHolidays_Array[1];
    Pay_Schedule->Holidays_Ref = PayRef_Holidays;
    Pay_Schedule->NCF = NPayCF;
    Pay_Schedule->ForwardStart_C = Pay_ForwardStart;
    Pay_Schedule->ForwardEnd_C = Pay_ForwardEnd;
    Pay_Schedule->StartDate_C = Pay_StartDate;
    Pay_Schedule->EndDate_C = Pay_EndDate;
    Pay_Schedule->PayDate_C = Pay_PayDate;
    Pay_Schedule->NotionalPayDate_C = Pay_NotionalPayDate;
    Pay_Schedule->ReferenceType = Pay_RefRateType;
    Pay_Schedule->FixedFlotype = Pay_FixFloFlag;
    Pay_Schedule->DayCount = Pay_DayCount;
    Pay_Schedule->NotionalAmount = Pay_NotionalAMT;
    Pay_Schedule->NRefHistory = Pay_NHistory;
    Pay_Schedule->RefHistoryDate = Pay_HistoryDate;
    Pay_Schedule->RefHistory = Pay_HistoryRate;

    if (Pay_RefRateType != 0 && Pay_RefRateType != 2) Pay_Schedule->RefSwapFlag = 1;
    Pay_Schedule->NSwapPayAnnual = Pay_SwapYearlyNPayment;
    Pay_Schedule->RefSwapMaturity = Pay_SwapMaturity;
    Pay_Schedule->FixedRefRate = Pay_FixedRefRate;
    Pay_Schedule->Slope = Pay_Slope;
    Pay_Schedule->CPN = Pay_CPN;
    Pay_Schedule->NAFlag = NAFlag;
    Pay_Schedule->PriceDate_C = PriceDate;

    Pay_Schedule->LockOutRef = SOFRConv[3];
    Pay_Schedule->LookBackRef = SOFRConv[4];
    Pay_Schedule->ObservationShift = SOFRConv[5];
    Pay_Schedule->N_NotHoliday = NumberNotHoliday_Pay;
    Pay_Schedule->NotHoliday = NotHoliday_YYYYMMDD_Pay;
    Pay_Schedule->DayCount_NotHoliday = NotHoliday_DayCount_Pay;

    long PricingOnly = 1;
    if (GreekFlag == 999)
    {
        PricingOnly = 999;
        GreekFlag = 0;
    }

    ResultCode = SwapPricer(PriceDate, CalcCRSFlag, Rcv_Schedule, RcvDisc_NTerm, RcvDisc_Term,
        RcvDisc_Rate, RcvRef_NTerm, RcvRef_Term, RcvRef_Rate,
        Pay_Schedule, PayDisc_NTerm, PayDisc_Term, PayDisc_Rate,
        PayRef_NTerm, PayRef_Term, PayRef_Rate,
        Rcv_NTermFX, Rcv_TermFX, Rcv_FX, Pay_NTermFX, Pay_TermFX, Pay_FX,
        GreekFlag, ResultPrice, ResultRefRate, ResultCPN, ResultDF,
        PV01, KeyRateRcvPV01, KeyRatePayPV01,
        PricingOnly, RcvConvexityAdjFlag, PayConvexityAdjFlag, NRcvConvexAdjVol, NPayConvexAdjVol, RcvConvexAdjTerm,
        RcvConvexAdjVol, PayConvexAdjTerm, PayConvexAdjVol);

    if (RcvRef_Holiday_Optimal) free(RcvRef_Holiday_Optimal);
    if (PayRef_Holiday_Optimal) free(PayRef_Holiday_Optimal);
    if (NotHoliday_YYYYMMDD_Rcv) free(NotHoliday_YYYYMMDD_Rcv);
    if (NotHoliday_YYYYMMDD_Pay) free(NotHoliday_YYYYMMDD_Pay);
    if (NotHoliday_DayCount_Rcv) free(NotHoliday_DayCount_Rcv);
    if (NotHoliday_DayCount_Pay) free(NotHoliday_DayCount_Pay);

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
        ResultCodeTemp = CalcIRS(PriceDate_ExlDate, GreekFlag, NAFlag, CRS_Flag, CRS_Info,
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
        if (DayCountFlag == 1) ResultRate[0] = -365.0 / (double)(1 + NumHoliday) * log(1.0 / (1.0 + TodayONRate * (double)(1 + NumHoliday) / 360.0));
        else ResultRate[0] = -365.0 / (double)(1 + NumHoliday) * log(1.0 / (1.0 + TodayONRate * (double)(1 + NumHoliday) / 365.0));
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
    //_CrtDumpMemoryLeaks();
    return ResultCode;
}

DLLEXPORT(long) Generate_CpnDate_IRSModule_Using_Holiday(long EffectiveDate, long MaturityDate, long AnnCpnOneYear, long NHoliday, long* Holidays, long CpnNumber0Array1Flag, long* NumberOfCpnReturn, long* StartDateArray, long* EndDateArray, long* CpnDateArray)
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

    // 만약 EndDate가 26~31일이고 PayDate가 차월 1일, 2일, 3일, 4일 등
    if (EffectiveDD > 25 && MaturityDD < 5)
    {
        NBusinessCountFromEndToPay(EffectiveDate, RealPayDate, Holidays, NHoliday, 1, &MaturityDate);
        MaturityDate = ((long)(MaturityDate / 100)) * 100 + EffectiveDD;
    }
    else
    {
        MaturityDate = MaturityYYYYMM * 100 + EffectiveDD;
    }

    long TempDate = EffectiveDate;
    long NCpnDate;
    long* CpnDate = Generate_CpnDate_Holiday(EffectiveDate, MaturityDate, AnnCpnOneYear, NCpnDate, TempDate, NHoliday, Holidays);

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

int main2()
{
    long NHolidays = Number_Holiday(2020, 2050, 1);
    long* Holidays = (long*)malloc(sizeof(long) * NHolidays);
    Mapping_Holiday_CType(2020, 2050, 1, NHolidays, Holidays);
    long TempDate = LastBusinessDate(202305, NHolidays, Holidays);

    long Date = DayPlus(20240101, 366);
    long N = Number_of_Coupons(1, 20240627, 20300102, 4, 1, NHolidays, Holidays, 1);
    long* ResultStart = (long*)malloc(sizeof(long) * N);
    long* ResultEnd = (long*)malloc(sizeof(long) * N);
    long* ResultPay = (long*)malloc(sizeof(long) * N);

    MappingCouponDates(1, 20240627, 20240627, 20300102, -1, 4, 1, NHolidays, Holidays, 1, N, ResultStart, ResultEnd, ResultPay);
    double ZeroTermFore[25] = { 0.002739726,	0.035616438,	0.098630137,	0.180821918	,0.257534247	,0.515068493	,0.767123288	,1.016438356	,1.515068493	,2.016438356	,3.01369863	,4.01369863	,5.01369863	,6.019178082	,7.019178082	,8.019178082	,9.016438356	,10.01643836	,12.02465753	,15.01917808	,20.02465753	,25.03013699	,30.03561644	,40.04383562	,50.04383562 };
    double ZeroRateFore[25] = { 0.04663591, 	0.04652330 	,0.04504692 	,0.04461912 	,0.04435352 	,0.04298215 	,0.04186334 	,0.04101891 	,0.03982147 	,0.03902380 	,0.03805355 	,0.03742306 	,0.03703927 	,0.03687159 	,0.03678656 	,0.03677524 	,0.03680684 	,0.03688299 	,0.03711687 	,0.03740166 	,0.03719903 	,0.03610472 	,0.03474796 	,0.03161303 	,0.02838960 };
    double S = 1426.95;
    long PriceDate = 20241210;
    double ToDate = 20250113;
    double T = ((double)DayCountAtoB(PriceDate, ToDate)) / 365.;
    double SwapPoint = -175.0;
    double SwapPointUnit = 100.0;
    double r = Calc_ZeroRate_FromSwapPoint(SwapPoint, S, SwapPointUnit, T, 25, ZeroTermFore, ZeroRateFore);
    free(Holidays);
    free(ResultStart);
    free(ResultEnd);
    free(ResultPay);
    return 1;
}

double Calc_ZeroRate_FromDiscFactor(long PriceDate, long StartDate, long EndDate, double MarketQuote, long DayCountFlag, long NZero, double* ZeroTerm, double* ZeroRate)
{
    if (StartDate < 19000100) StartDate = ExcelDateToCDate(StartDate);
    if (EndDate < 19000100) EndDate = ExcelDateToCDate(EndDate);
    double r;
    if (PriceDate == StartDate)
    {
        r = 365.0 / ((double)DayCountAtoB(StartDate, EndDate)) * log(1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag));
    }
    else
    {
        double t0 = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.;
        double DF_Start_To_EndDate = 1.0 / (1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag));
        double r0 = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, t0);
        double DF_0_To_EndDate = exp(-r0 * t0) * DF_Start_To_EndDate;
        r = -365.0 / ((double)DayCountAtoB(PriceDate, EndDate)) * log(DF_0_To_EndDate);
    }
    return r;
}

DLLEXPORT(long) ZeroRateGenerator(
    long PriceDate,                     // 
    double SpotPrice,                   // Spot Price if Using SwapPoint
    double SwapPointUnit,               // SwapPointUnit
    long NationFlag,                    // Currency 0: KRW, 1: USD, 2: GBP, -1: Custom(AdditionalHolidays Self Input)
    long NAdditionalHoliday,            // Additional Holidays Number

    long* AdditionalHolidays,           // Additional Holidays Array
    long DayCountFlag,                  // 0 : Act365, 1: Act360 2: ActAct 3:30/360
    long* RefRateType,                  // [0] Domestic [1] Foreign Estimation 0: CD, LIBOR, 1: SOFR, SONIA etc.. Array Length = 2 
    long NZeroTermFore,                 // SOFR Curve Number (Currency Swap)
    double* ZeroTermFore,               // SOFR Curve Term

    double* ZeroRateFore,               // SOFR Curve Rate
    long NZeroTermEstCurve,             // Domestic Estimate Curve Number
    double* ZeroTermEstCurve,           // Domestic Estimate Curve Term
    double* ZeroRateEstCurve,           // Domestic Estimate Curve Rate
    long NGenerator,                    // Number of Generator

    long* ProductType,                  // 0: Deposit, 1: Swap, 2: SwapPoint, 3: CRS, 4: Basis CRS, 5: KOFR etc.., Array Length = NGenerator 
    long* EstimateStart,                // Estimation Start Date, Array Length = NGenerator  
    long* Maturity,                     // Swap PayMaturity Date, Array Length = NGenerator  
    double* MarketQuote,                // Market Quote, Array Length = NGenerator  
    long* NCpnsAnn,                     // Annual Payment Number, Array Length = NGenerator  

    long* CalcNCpn0CalcZeroResult1,     // Array Length = 1, 0: Calculate Number of Swap Coupon of Each Generator, 1: ZeroCurve Generate MODE
    long* NResultCpnArray,              // OutPut : NCoupon of Each Generators, Array Length = NGenerator  
    long* ResultForwardStart,           // Output : ResultForwardStart, Array Length = sum(NResultCpnArray)
    long* ResultForwardEnd,             // Output : ResultForwardEnd, Array Length = sum(NResultCpnArray)
    long* ResultStartDate,              // Output : ResultStartDate, Array Length = sum(NResultCpnArray)

    long* ResultEndDate,                // Output : ResultEndDate, Array Length = sum(NResultCpnArray)
    long* ResultPayDate,                // Output : ResultPayDate, Array Length = sum(NResultCpnArray)
    long* ResultForwardStartUSD,        // Output : ResultForwardStartUSD, Array Length = sum(NResultCpnArray)
    long* ResultForwardEndUSD,          // Output : ResultForwardEndUSD, Array Length = sum(NResultCpnArray)
    long* ResultStartUSD,               // Output : ResultStartUSD, Array Length = sum(NResultCpnArray)

    long* ResultEndUSD,                 // Output : ResultEndUSD, Array Length = sum(NResultCpnArray)
    long* ResultPayUSD,                 // Output : ResultPayUSD, Array Length = sum(NResultCpnArray)
    double* ResultZeroTerm,             // Output : Result ZeroCurve Term, Array Length = NGenerator
    double* ResultZeroRate,             // Output : Result ZeroCurve Rate, Array Length = NGenerator
    double* ResultIRSInfo1,             // Output : Result Reference Rate(Rcv,Pay), Array Legnth = (sum(NResultCpnArray) + NGenerator) x 2

    double* ResultIRSInfo2,             // Output : Result Reference Rate(Rcv,Pay), Array Legnth = (sum(NResultCpnArray) + NGenerator) x 2
    double* ResultIRSInfo3
)
{
    long i;
    long j;
    long n;
    long k;
    long nbd = -1;
    
    long ncpn;
    long StartYYYY, EndYYYY;
    long StartDD, PayDD;
    long LastBDTemp;
    long n1;
    long ntotal;
    long ResultCode = 0;
    if (PriceDate < 19000100) PriceDate = ExcelDateToCDate(PriceDate);
    for (i = 0; i < NGenerator; i++) if (EstimateStart[i] < 19000100) EstimateStart[i] = ExcelDateToCDate(EstimateStart[i]);
    for (i = 0; i < NGenerator; i++) if (Maturity[i] < 19000100) Maturity[i] = ExcelDateToCDate(Maturity[i]);

    for (i = 0; i < NAdditionalHoliday; i++) if (AdditionalHolidays[i] < 19000100) AdditionalHolidays[i] = ExcelDateToCDate(AdditionalHolidays[i]);

    if (PriceDate > EstimateStart[0]) return -1;
    if (ProductType[0] > 2) return -2;
    StartYYYY = PriceDate / 10000;
    EndYYYY = StartYYYY + 50;       // 최대 Holiday 반영년도
    Preprocessing_TermAndRate(PriceDate, NZeroTermFore, ZeroTermFore, ZeroRateFore);
    Preprocessing_TermAndRate(PriceDate, NZeroTermEstCurve, ZeroTermEstCurve, ZeroRateEstCurve);

    double MaxMarketQuote = 0.;
    double MaxBasisPoint = 0.;
    for (i = 0; i < NGenerator; i++)
    {
        if (ProductType[i] == 0 || ProductType[i] == 1 || ProductType[i] == 3 || ProductType[i] == 5)
        {
            MaxMarketQuote = max(MaxMarketQuote, fabs(MarketQuote[i]));
        }
        else if (ProductType[i] == 4)
        {
            MaxBasisPoint = max(MaxBasisPoint, fabs(MarketQuote[i]));
        }
    }
    double MinBasisPoint = MaxBasisPoint;
    for (i = 0; i < NGenerator; i++) if (ProductType[i] == 4) MinBasisPoint = min(MinBasisPoint, fabs(MarketQuote[i]));

    if (MaxMarketQuote > 0.8)
    {
        ///////////////////////////////
        // 이자율이 0.8 이상인 경우  //
        // 단위가 %인걸로 간주하고   //
        // 100으로 나누자            //
        // 4.3 등일 경우 0.043 변환  //
        ///////////////////////////////
        for (i = 0; i < NGenerator; i++) if (ProductType[i] != 2 && ProductType[i] != 4) MarketQuote[i] = MarketQuote[i] / 100.;
    }
    if (MaxBasisPoint - MinBasisPoint > 0.01)
    {
        ///////////////////////////////
        // 베이시스 스왑의 경우      //
        // 위의 조건의 경우          //
        // 단위가 %인걸로 간주하고   //
        // 100으로 나누자            //
        // 4.3 등일 경우 0.043 변환  //
        ///////////////////////////////
        for (i = 0; i < NGenerator; i++) if (ProductType[i] == 4) MarketQuote[i] = MarketQuote[i] / 100.;
    }

    //////////////////////
    // Domestic Holiday //
    //////////////////////

    long NDomesticHolidays;
    long* DomesticHolidays;
    if (NationFlag >= 0 && NationFlag < 5)
    {
        // 0 KRW, 1:USD, 2:GBP, 3:NYSE, 4:NYMEX
        n1 = Number_Holiday(StartYYYY, EndYYYY, NationFlag);
        NDomesticHolidays = NAdditionalHoliday + n1;
        DomesticHolidays = (long*)malloc(sizeof(long) * NDomesticHolidays);
        Mapping_Holiday_CType(StartYYYY, EndYYYY, NationFlag, n1, DomesticHolidays);
        for (i = n1; i < NDomesticHolidays; i++)
        {
            DomesticHolidays[i] = AdditionalHolidays[i - n1];
        }
    }
    else
    {
        NDomesticHolidays = NAdditionalHoliday;
        DomesticHolidays = (long*)malloc(sizeof(long) * NDomesticHolidays);
        for (i = 0; i < NAdditionalHoliday; i++) DomesticHolidays[i] = AdditionalHolidays[i];
    }

    long SpotDate = NextNthBusinessDate(PriceDate, 2, DomesticHolidays, NDomesticHolidays);
    double T_SpotDate = ((double)DayCountAtoB(PriceDate, SpotDate)) / 365.;
    /////////////////
    // USD Holiday //
    /////////////////

    long NHolidayUSD = Number_Holiday(StartYYYY, EndYYYY, 1);
    long* HolidaysUSD = (long*)malloc(sizeof(long) * NHolidayUSD);
    Mapping_Holiday_CType(StartYYYY, EndYYYY, 1, NHolidayUSD, HolidaysUSD);

    ///////////////////
    // Holiday Union //
    ///////////////////

    long NHolidayUnionDomesticUSD = NHolidayUSD + NDomesticHolidays;
    long* HolidayUnionDomesticUSD = (long*)malloc(sizeof(long) * NHolidayUnionDomesticUSD);
    for (i = 0; i < NHolidayUSD; i++) HolidayUnionDomesticUSD[i] = HolidaysUSD[i];
    for (i = NHolidayUSD; i < NHolidayUnionDomesticUSD; i++) HolidayUnionDomesticUSD[i] = DomesticHolidays[i - NHolidayUSD];

    ////////////////////////////////////
    // Variable For CalcIRS Function  //
    ////////////////////////////////////

    double dblErrorRange = 0.000001;
    double ObjValue;
    double MaxRate;
    double MinRate;
    double TargetRate;
    double PrevRate;
    double dblCalcPrice;
    long ResultCodeTemp;
    long GreekFlag = 0;
    long NAFlag = 0;
    long CRS_Flag[4] = { 0,0,0,0 };
    double CRS_Info[4] = { 0.,0.,0.,0., };
    long Rcv_RefRateType = 0;
    long Pay_RefRateType = 0;

    if (RefRateType[0] == 0) Rcv_RefRateType = 0;
    else Rcv_RefRateType = 2;

    if (RefRateType[1] == 0) Pay_RefRateType = 0;
    else Pay_RefRateType = 2;

    long Rcv_SwapYearlyNPayment = 4.;           // 실질적으로 안쓰는 변수(기초금리가 CMS가아니므로)
    double Rcv_SwapMaturity = 0.25;             // 실질적으로 안쓰는 변수(기초금리가 CMS가아니므로)
    long Rcv_FixFloFlag;                        // 제너레이터에 따라 반복문 안에서 결정
    long Rcv_DayCount = DayCountFlag;
    double Rcv_NotionalAMT = 100.;              // BasisSwap일 경우 반복문 안에서 결정
    long Rcv_NotionalPayDate;                   // 반복문 안에서 결정
    long NRcvCF;                                // 반복문 안에서 결정
    long* RcvCashFlowSchedule;                  // 반복문 안에서 결정

    long Pay_SwapYearlyNPayment = 4.;           // 실질적으로 안쓰는 변수(기초금리가 CMS가아니므로)
    double Pay_SwapMaturity = 0.25;             // 실질적으로 안쓰는 변수(기초금리가 CMS가아니므로)
    long Pay_FixFloFlag;                        // 제너레이터에 따라 반복문 안에서 결정
    long Pay_DayCount = DayCountFlag;       // 반복문 안에서 결정
    double Pay_NotionalAMT = 100.;              // BasisSwap일 경우 반복문 안에서 결정
    long Pay_NotionalPayDate;                   // 반복문 안에서 결정
    long NPayCF;                                // 반복문 안에서 결정
    long* PayCashFlowSchedule;                  // 반복문 안에서 결정

    double ResultPrice[10] = { 0., };
    double PV01[100] = { 0., };
    double KeyRateRcvPV01[100] = { 0., };
    double KeyRatePayPV01[100] = { 0., };
    long SOFRConv[6] = { 0 , };
    long HolidayCalcFlag[8] = { 0, };
    long NHolidays[2] = { 0, 0 };               // 반복문 안에서 결정
    long* Holidays;                             // 반복문 안에서 결정
    long RcvPayConvexityAdjFlag[2] = { 0,0 };
    double TempDoubleArray[2] = { 0.,0. };
    long NOverNightHistory[2] = { 1,1 };
    long OverNightHistoryDate[2] = { 20211101 ,20211101 };
    double OverNightHistoryRate[2] = { 1.314,1.314 };

    if (CalcNCpn0CalcZeroResult1[0] <= 0)
    {
        //////////////////////////////
        // 이 함수를 처음 실행하면  //
        // 각 제너레이터            //
        // 스왑쿠폰개수들을 넣어줌  //
        //////////////////////////////
        ntotal = 0;
        for (i = 0; i < NGenerator; i++)
        {
            if (ProductType[i] == 2 || ProductType[i] == 0)
            {
                // Deposit, SwapPoint
                ncpn = 1;
            }
            else if (ProductType[i] == 3 || ProductType[i] == 4)
            {
                // CRS, Basis CRS
                ncpn = Number_of_Coupons(ProductType[i], EstimateStart[i], Maturity[i], NCpnsAnn[i], 1, NHolidayUnionDomesticUSD, HolidayUnionDomesticUSD, 1);
            }
            else
            {
                // Swap
                ncpn = Number_of_Coupons(ProductType[i], EstimateStart[i], Maturity[i], NCpnsAnn[i], 1, NDomesticHolidays, DomesticHolidays, 1);
            }

            NResultCpnArray[i] = ncpn;
            ntotal += ncpn;
        }

        CalcNCpn0CalcZeroResult1[0] = 1;
        ResultCode = ntotal;
    }
    else
    {
        long ncurve = 0;
        long** ResultForwardStart2D = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultForwardEnd2D = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultStart2D = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultEnd2D = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultPay2D = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultSchedule = (long**)malloc(sizeof(long*) * NGenerator);

        double** ResultSlope2D = (double**)malloc(sizeof(double*) * NGenerator);
        double** ResultCPN2D = (double**)malloc(sizeof(double*) * NGenerator);
        double** ResultFixedRefRate2D = (double**)malloc(sizeof(double*) * NGenerator);
        long** ResultPaySchedule2D = (long**)malloc(sizeof(long*) * NGenerator);

        long** ResultForwardStart2DUSD = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultForwardEnd2DUSD = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultStart2DUSD = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultEnd2DUSD = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultPay2DUSD = (long**)malloc(sizeof(long*) * NGenerator);
        long** ResultScheduleUSD = (long**)malloc(sizeof(long*) * NGenerator);

        double** ResultSlope2DUSD = (double**)malloc(sizeof(double*) * NGenerator);
        double** ResultCPN2DUSD = (double**)malloc(sizeof(double*) * NGenerator);
        double** ResultFixedRefRate2DUSD = (double**)malloc(sizeof(double*) * NGenerator);
        long** ResultPaySchedule2DUSD = (long**)malloc(sizeof(long*) * NGenerator);

        double t, rb;
        double dffo, df_to_startdate;

        long DayAtoB;
        long W1Flag;

        for (i = 0; i < NGenerator; i++)
        {
            ResultForwardStart2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultForwardEnd2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultStart2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultEnd2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultPay2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultSlope2D[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultSchedule[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i] * 5);

            ResultCPN2D[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultFixedRefRate2D[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultPaySchedule2D[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);

            ResultForwardStart2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultForwardEnd2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultStart2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultEnd2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultPay2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
            ResultSlope2DUSD[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultScheduleUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i] * 5);

            ResultCPN2DUSD[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultFixedRefRate2DUSD[i] = (double*)malloc(sizeof(double) * NResultCpnArray[i]);
            ResultPaySchedule2DUSD[i] = (long*)malloc(sizeof(long) * NResultCpnArray[i]);
        }

        k = 0;
        for (i = 0; i < NGenerator; i++)
        {
            if (ProductType[i] == 0 || ProductType[i] == 2)
            {
                ResultForwardStart2D[i][0] = EstimateStart[i];
                ResultForwardEnd2D[i][0] = Maturity[i];
                ResultStart2D[i][0] = EstimateStart[i];
                ResultEnd2D[i][0] = Maturity[i];
                ResultPay2D[i][0] = Maturity[i];
                ResultForwardStart2DUSD[i][0] = ResultForwardStart2D[i][0];
                ResultForwardEnd2DUSD[i][0] = ResultForwardEnd2D[i][0];
                ResultStart2DUSD[i][0] = ResultStart2D[i][0];
                ResultEnd2DUSD[i][0] = ResultEnd2D[i][0];
                ResultPay2DUSD[i][0] = ResultPay2D[i][0];

            }
            else if (ProductType[i] == 3 || ProductType[i] == 4)
            {
                dffo = Calc_Discount_Factor(ZeroTermFore, ZeroRateFore, NZeroTermFore, T_SpotDate);
                if (i >= 1) df_to_startdate = Calc_Discount_Factor(ResultZeroTerm, ResultZeroRate, ncurve, T_SpotDate);
                else df_to_startdate = 1.;
                NAFlag = 1;
                StartDD = EstimateStart[i] - ((long)(EstimateStart[i] / 100)) * 100;
                PayDD = Maturity[i] - ((long)(Maturity[i] / 100)) * 100;
                if (StartDD > 27 && PayDD > 27 && StartDD > PayDD) nbd = 0;
                else nbd = NBusinessCountFromEndToPay(EstimateStart[i], Maturity[i], HolidayUnionDomesticUSD, NHolidayUnionDomesticUSD, 1, &ResultEnd2D[i][NResultCpnArray[i] - 1]);
                // CRS or Basis CRS

                MappingCouponDates2(ProductType[i], EstimateStart[i], EstimateStart[i], Maturity[i], nbd,
                    NCpnsAnn[i], 1, NDomesticHolidays, DomesticHolidays, NHolidayUnionDomesticUSD, HolidayUnionDomesticUSD, 1,
                    NResultCpnArray[i], ResultForwardStart2D[i], ResultForwardEnd2D[i], ResultPay2D[i]);

                MappingCouponDates2(ProductType[i], EstimateStart[i], EstimateStart[i], Maturity[i], nbd,
                    NCpnsAnn[i], 1, NHolidayUSD, HolidaysUSD, NHolidayUnionDomesticUSD, HolidayUnionDomesticUSD, 1,
                    NResultCpnArray[i], ResultForwardStart2DUSD[i], ResultForwardEnd2DUSD[i], ResultPay2DUSD[i]);
                for (j = 0; j < NResultCpnArray[i]; j++)
                {
                    ResultStart2D[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2D[i][j] = ResultForwardEnd2D[i][j];
                    ResultStart2DUSD[i][j] = ResultForwardStart2DUSD[i][j];
                    ResultEnd2DUSD[i][j] = ResultForwardEnd2DUSD[i][j];
                }

                if (ProductType[i] == 3)
                {
                    Rcv_FixFloFlag = 0;
                    Pay_FixFloFlag = 1;
                }
                else
                {
                    Rcv_FixFloFlag = 1;
                    Pay_FixFloFlag = 1;
                }

                for (j = 0; j < NResultCpnArray[i]; j++)
                {
                    ResultStart2D[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2D[i][j] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j] = ResultForwardStart2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i]] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 2] = ResultForwardStart2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 3] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 4] = ResultPay2D[i][j];
                    if (ProductType[i] == 3) ResultSlope2D[i][j] = 0.0;
                    else ResultSlope2D[i][j] = 1.0;
                    ResultCPN2D[i][j] = MarketQuote[i];
                    ResultFixedRefRate2D[i][j] = 0.;

                    ResultForwardStart2DUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2DUSD[i][j] = ResultEnd2D[i][j];
                    ResultStart2DUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2DUSD[i][j] = ResultForwardEnd2D[i][j];
                    ResultPay2DUSD[i][j] = ResultPay2D[i][j];

                    ResultScheduleUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i]] = ResultForwardEnd2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 2] = ResultForwardStart2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 3] = ResultForwardEnd2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 4] = ResultPay2D[i][j];

                    ResultSlope2DUSD[i][j] = 1.0;
                    ResultCPN2DUSD[i][j] = 0.;
                    ResultFixedRefRate2DUSD[i][j] = 0.;

                }
                Rcv_NotionalPayDate = ResultEnd2D[i][NResultCpnArray[i] - 1];
                Pay_NotionalPayDate = ResultEnd2DUSD[i][NResultCpnArray[i] - 1];

                NRcvCF = NResultCpnArray[i];
                NPayCF = NRcvCF;

                NHolidays[0] = NDomesticHolidays;
                NHolidays[1] = NHolidayUSD;
            }
            else
            {
                // CRS가 아닌 경우
                Rcv_FixFloFlag = 1;
                Pay_FixFloFlag = 0;
                Pay_NotionalAMT = Rcv_NotionalAMT;
                DayAtoB = DayCountAtoB(EstimateStart[i], Maturity[i]);
                W1Flag = -1;
                // 짧은스왑만기인 경우 케이스별로 스왑 분류
                if (DayAtoB < 7) W1Flag = 0;            // 1일 스왑인걸로 간주
                else if (DayAtoB < 14) W1Flag = 1;      // 1주 스왑인걸로 간주
                else if (DayAtoB < 21) W1Flag = 2;      // 2주 스왑인걸로 간주
                else if (DayAtoB < 35) W1Flag = 3;      // 1달 스왑인걸로 간주
                else W1Flag = -1;

                if (W1Flag == 0 && NResultCpnArray[i] == 1)
                {
                    // 1일 스왑
                    ResultForwardStart2D[i][0] = EstimateStart[i];
                    ResultForwardEnd2D[i][0] = ParseBusinessDateIfHoliday(DayPlus(EstimateStart[i], 1), DomesticHolidays, NDomesticHolidays);
                    ResultPay2D[i][0] = Maturity[i];
                }
                else if (W1Flag == 1 && NResultCpnArray[i] == 1)
                {
                    // 1주 스왑
                    ResultForwardStart2D[i][0] = EstimateStart[i];
                    ResultForwardEnd2D[i][0] = ParseBusinessDateIfHoliday(DayPlus(EstimateStart[i], 7), DomesticHolidays, NDomesticHolidays);
                    ResultPay2D[i][0] = Maturity[i];
                }
                else if (W1Flag == 2 && NResultCpnArray[i] == 1)
                {
                    // 2주 스왑
                    ResultForwardStart2D[i][0] = EstimateStart[i];
                    ResultForwardEnd2D[i][0] = ParseBusinessDateIfHoliday(DayPlus(EstimateStart[i], 14), DomesticHolidays, NDomesticHolidays);
                    ResultPay2D[i][0] = Maturity[i];
                }
                else if (W1Flag == 3 && NResultCpnArray[i] == 1)
                {
                    // 1달 스왑
                    ResultForwardStart2D[i][0] = EstimateStart[i];
                    LastBDTemp = LastBusinessDate(EDate_Cpp(EstimateStart[i], 1) / 100, NDomesticHolidays, DomesticHolidays);
                    ResultForwardEnd2D[i][0] = ParseBusinessDateIfHoliday(min(LastBDTemp, EDate_Cpp(EstimateStart[i], 1)), DomesticHolidays, NDomesticHolidays);
                    ResultPay2D[i][0] = Maturity[i];
                }
                else
                {
                    StartDD = EstimateStart[i] - ((long)(EstimateStart[i] / 100)) * 100;
                    PayDD = Maturity[i] - ((long)(Maturity[i] / 100)) * 100;
                    if (StartDD > 27 && PayDD > 27 && StartDD > PayDD) nbd = 0;
                    else nbd = NBusinessCountFromEndToPay(EstimateStart[i], Maturity[i], HolidayUnionDomesticUSD, NHolidayUnionDomesticUSD, 1, &ResultEnd2D[i][NResultCpnArray[i] - 1]);

                    MappingCouponDates(ProductType[i], EstimateStart[i], EstimateStart[i], Maturity[i], nbd,
                        NCpnsAnn[i], 1, NDomesticHolidays, DomesticHolidays, 1,
                        NResultCpnArray[i], ResultForwardStart2D[i], ResultForwardEnd2D[i], ResultPay2D[i]);
                }
                Rcv_NotionalPayDate = ResultPay2D[i][NResultCpnArray[i] - 1];
                Pay_NotionalPayDate = Rcv_NotionalPayDate;

                NRcvCF = NResultCpnArray[i];
                NPayCF = NRcvCF;

                NHolidays[0] = NDomesticHolidays;
                NHolidays[1] = NDomesticHolidays;

                for (j = 0; j < NResultCpnArray[i]; j++)
                {
                    ResultStart2D[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2D[i][j] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j] = ResultForwardStart2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i]] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 2] = ResultForwardStart2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 3] = ResultForwardEnd2D[i][j];
                    ResultSchedule[i][j + NResultCpnArray[i] * 4] = ResultPay2D[i][j];

                    ResultSlope2D[i][j] = 1.0;
                    ResultCPN2D[i][j] = 0.;
                    ResultFixedRefRate2D[i][j] = 0.;

                    ResultForwardStart2DUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2DUSD[i][j] = ResultEnd2D[i][j];
                    ResultStart2DUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultEnd2DUSD[i][j] = ResultForwardEnd2D[i][j];
                    ResultPay2DUSD[i][j] = ResultPay2D[i][j];

                    ResultScheduleUSD[i][j] = ResultForwardStart2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i]] = ResultForwardEnd2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 2] = ResultForwardStart2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 3] = ResultForwardEnd2D[i][j];
                    ResultScheduleUSD[i][j + NResultCpnArray[i] * 4] = ResultPay2D[i][j];

                    ResultSlope2DUSD[i][j] = 0.0;
                    ResultCPN2DUSD[i][j] = MarketQuote[i];
                    ResultFixedRefRate2DUSD[i][j] = 0.;

                }

                Rcv_NotionalPayDate = ResultPay2D[i][NResultCpnArray[i] - 1];
                Pay_NotionalPayDate = ResultPay2DUSD[i][NResultCpnArray[i] - 1];
            }

            ResultZeroTerm[i] = ((double)DayCountAtoB(PriceDate, Maturity[i])) / 365.;

            if (ProductType[i] == 0)
            {
                /////////////
                // Deposit // 
                /////////////
                ResultZeroRate[i] = Calc_ZeroRate_FromDiscFactor(PriceDate, EstimateStart[i], Maturity[i], MarketQuote[i], DayCountFlag, ncurve, ResultZeroTerm, ResultZeroRate);
                (ResultIRSInfo1 + k)[0] = MarketQuote[i];
                (ResultIRSInfo1 + k)[1] = (ResultIRSInfo1 + k)[0];

                (ResultIRSInfo2 + k)[0] = 100. * MarketQuote[i] * DayCountFractionAtoB(EstimateStart[i], Maturity[i], DayCountFlag);
                (ResultIRSInfo2 + k)[1] = (ResultIRSInfo2 + k)[0];

                (ResultIRSInfo3 + k)[0] = 100. / (100. + (ResultIRSInfo2 + k)[0]);
                (ResultIRSInfo3 + k)[1] = (ResultIRSInfo3 + k)[0];
            }
            else if (ProductType[i] == 2)
            {
                ///////////////
                // SwapPoint // 
                ///////////////
                ResultZeroRate[i] = Calc_ZeroRate_FromSwapPoint(MarketQuote[i], SpotPrice, SwapPointUnit, ResultZeroTerm[i], NZeroTermFore, ZeroTermFore, ZeroRateFore);
                (ResultIRSInfo3 + k)[0] = Calc_DiscountFactor_FromSwapPoint(MarketQuote[i], SpotPrice, SwapPointUnit, ResultZeroTerm[i], NZeroTermFore, ZeroTermFore, ZeroRateFore);
                (ResultIRSInfo1 + k)[0] = (1.0 / (ResultIRSInfo3 + k)[0] - 1.) / DayCountFractionAtoB(EstimateStart[i], Maturity[i], DayCountFlag);
                (ResultIRSInfo2 + k)[0] = 100. * (1.0 / (ResultIRSInfo3 + k)[0] - 1.);

                (ResultIRSInfo1 + k)[1] = (ResultIRSInfo1 + k)[0];
                (ResultIRSInfo2 + k)[1] = (ResultIRSInfo2 + k)[0];
                (ResultIRSInfo3 + k)[1] = (ResultIRSInfo3 + k)[0];
            }
            else if (ProductType[i] == 1)
            {
                ///////////////////
                // Interest Swap // 
                ///////////////////
                Holidays = (long*)malloc(sizeof(long) * (NHolidays[0] + NHolidays[1]));
                for (j = 0; j < NDomesticHolidays; j++)
                {
                    Holidays[j] = DomesticHolidays[j];
                    Holidays[j + NDomesticHolidays] = DomesticHolidays[j];
                }

                Rcv_SwapYearlyNPayment = NCpnsAnn[i];

                dblErrorRange = 0.000001;
                ObjValue = 0.0;
                MaxRate = MarketQuote[i] + 0.2;
                MinRate = MarketQuote[i] - 0.15;
                TargetRate = MaxRate;
                PrevRate = MaxRate;
                Pay_DayCount = Rcv_DayCount;
                Pay_RefRateType = Rcv_RefRateType;
                if (i > 0)
                {
                    for (n = 0; n < 1000; n++)
                    {
                        ResultZeroRate[ncurve] = TargetRate;
                        ResultCodeTemp = CalcIRS(
                            PriceDate, 0, NAFlag, CRS_Flag, CRS_Info,
                            Rcv_RefRateType, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
                            Rcv_NotionalAMT, Rcv_NotionalPayDate, ncurve + 1, ResultZeroTerm, ResultZeroRate,
                            ncurve + 1, ResultZeroTerm, ResultZeroRate, NResultCpnArray[i], ResultSchedule[i],
                            ResultSlope2D[i], ResultCPN2D[i], ResultFixedRefRate2D[i], Pay_RefRateType, Pay_SwapYearlyNPayment,
                            Pay_SwapMaturity, Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate,
                            ncurve + 1, ResultZeroTerm, ResultZeroRate, ncurve + 1, ResultZeroTerm,
                            ResultZeroRate, NResultCpnArray[i], ResultScheduleUSD[i], ResultSlope2DUSD[i], ResultCPN2DUSD[i],
                            ResultFixedRefRate2DUSD[i], ResultPrice, ResultIRSInfo1 + k, ResultIRSInfo2 + k,
                            ResultIRSInfo3 + k, PV01, KeyRateRcvPV01, KeyRatePayPV01, SOFRConv, HolidayCalcFlag,
                            NHolidays, Holidays, NOverNightHistory, OverNightHistoryDate, OverNightHistoryRate,
                            RcvPayConvexityAdjFlag, RcvPayConvexityAdjFlag, TempDoubleArray, TempDoubleArray);

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
                }
                else
                {
                    ResultZeroRate[ncurve] = Calc_ZeroRate_FromDiscFactor(PriceDate, EstimateStart[i], ResultForwardEnd2D[i][0], MarketQuote[i], DayCountFlag, ncurve, ResultZeroTerm, ResultZeroRate);
                    (ResultIRSInfo3 + k)[0] = Calc_Discount_Factor(ResultZeroTerm, ResultZeroRate, ncurve, DayCountFractionAtoB(PriceDate, Maturity[i], 0));
                    (ResultIRSInfo3 + k)[1] = (ResultIRSInfo3 + k)[0];                    
                }
                free(Holidays);
            }
            else if (ProductType[i] == 3)
            {
                Holidays = (long*)malloc(sizeof(long) * (NHolidays[0] + NHolidays[1]));
                for (j = 0; j < NDomesticHolidays; j++) Holidays[j] = DomesticHolidays[j];
                for (j = 0; j < NHolidayUSD; j++) Holidays[j + NDomesticHolidays] = HolidaysUSD[j];

                Rcv_SwapYearlyNPayment = NCpnsAnn[i];
                dblErrorRange = 0.00001;
                ObjValue = 0.0;
                MaxRate = MarketQuote[i] + 0.2;
                MinRate = MarketQuote[i] - 0.15;
                TargetRate = MaxRate;
                PrevRate = MaxRate;
                Pay_DayCount = 1; // USD Act 360
                for (n = 0; n < 1000; n++)
                {
                    ResultZeroRate[ncurve] = TargetRate;
                    ResultCodeTemp = CalcIRS(
                        PriceDate, 0, NAFlag, CRS_Flag, CRS_Info,
                        0, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
                        Rcv_NotionalAMT * dffo / df_to_startdate , Rcv_NotionalPayDate, ncurve + 1, ResultZeroTerm, ResultZeroRate,
                        ncurve + 1, ResultZeroTerm, ResultZeroRate, NResultCpnArray[i], ResultSchedule[i],
                        ResultSlope2D[i], ResultCPN2D[i], ResultFixedRefRate2D[i], Pay_RefRateType, Pay_SwapYearlyNPayment,
                        Pay_SwapMaturity, Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate,
                        NZeroTermFore, ZeroTermFore, ZeroRateFore, NZeroTermFore, ZeroTermFore,
                        ZeroRateFore, NResultCpnArray[i], ResultScheduleUSD[i], ResultSlope2DUSD[i], ResultCPN2DUSD[i],
                        ResultFixedRefRate2DUSD[i], ResultPrice, ResultIRSInfo1 + k, ResultIRSInfo2 + k,
                        ResultIRSInfo3 + k, PV01, KeyRateRcvPV01, KeyRatePayPV01, SOFRConv, HolidayCalcFlag,
                        NHolidays, Holidays, NOverNightHistory, OverNightHistoryDate, OverNightHistoryRate,
                        RcvPayConvexityAdjFlag, RcvPayConvexityAdjFlag, TempDoubleArray, TempDoubleArray);

                    dblCalcPrice = -ResultPrice[1] + ResultPrice[2];

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
                free(Holidays);
            }
            else if (ProductType[i] == 4)
            {
                Holidays = (long*)malloc(sizeof(long) * (NHolidays[0] + NHolidays[1]));
                for (j = 0; j < NDomesticHolidays; j++) Holidays[j] = DomesticHolidays[j];
                for (j = 0; j < NHolidayUSD; j++) Holidays[j + NDomesticHolidays] = HolidaysUSD[j];

                Rcv_SwapYearlyNPayment = NCpnsAnn[i];
                t = ((double)DayCountAtoB(PriceDate, Maturity[i])) / 365.;
                rb = Interpolate_Linear(ZeroTermFore, ZeroRateFore, NZeroTermFore, t);

                dblErrorRange = 0.000001;
                ObjValue = 0.0;
                MaxRate = rb - MarketQuote[i] + 0.10;
                MinRate = rb - MarketQuote[i] - 0.05;
                TargetRate = MaxRate;
                PrevRate = MaxRate;
                Pay_DayCount = 1; // USD Act 360

                for (n = 0; n < 1000; n++)
                {
                    ResultZeroRate[ncurve] = TargetRate;
                    ResultCodeTemp = CalcIRS(
                        PriceDate, 0, NAFlag, CRS_Flag, CRS_Info,
                        Rcv_RefRateType, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
                        Rcv_NotionalAMT * dffo / df_to_startdate, Rcv_NotionalPayDate, ncurve + 1, ResultZeroTerm, ResultZeroRate,
                        NZeroTermEstCurve, ZeroTermEstCurve, ZeroRateEstCurve, NResultCpnArray[i], ResultSchedule[i],
                        ResultSlope2D[i], ResultCPN2D[i], ResultFixedRefRate2D[i], Pay_RefRateType, Pay_SwapYearlyNPayment,
                        Pay_SwapMaturity, Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate,
                        NZeroTermFore, ZeroTermFore, ZeroRateFore, NZeroTermFore, ZeroTermFore,
                        ZeroRateFore, NResultCpnArray[i], ResultScheduleUSD[i], ResultSlope2DUSD[i], ResultCPN2DUSD[i],
                        ResultFixedRefRate2DUSD[i], ResultPrice, ResultIRSInfo1 + k, ResultIRSInfo2 + k,
                        ResultIRSInfo3 + k, PV01, KeyRateRcvPV01, KeyRatePayPV01, SOFRConv, HolidayCalcFlag,
                        NHolidays, Holidays, NOverNightHistory, OverNightHistoryDate, OverNightHistoryRate,
                        RcvPayConvexityAdjFlag, RcvPayConvexityAdjFlag, TempDoubleArray, TempDoubleArray);

                    dblCalcPrice = -ResultPrice[1] + ResultPrice[2];
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
                free(Holidays);
            }
            else if (ProductType[i] == 5)
            {
                // If Disc Curve is different from Estimation Curve
                // For Example KOFR, 
                Holidays = (long*)malloc(sizeof(long) * (NHolidays[0] + NHolidays[1]));
                for (j = 0; j < NDomesticHolidays; j++)
                {
                    Holidays[j] = DomesticHolidays[j];
                    Holidays[j + NDomesticHolidays] = DomesticHolidays[j];
                }

                Rcv_SwapYearlyNPayment = NCpnsAnn[i];
                dblErrorRange = 0.000001;
                ObjValue = 0.0;
                MaxRate = MarketQuote[i] + 0.2;
                MinRate = MarketQuote[i] - 0.15;
                TargetRate = MaxRate;
                PrevRate = MaxRate;
                Pay_DayCount = Rcv_DayCount;
                Pay_RefRateType = Rcv_RefRateType;
                for (n = 0; n < 1000; n++)
                {
                    ResultZeroRate[ncurve] = TargetRate;
                    ResultCodeTemp = CalcIRS(
                        PriceDate, 0, NAFlag, CRS_Flag, CRS_Info,
                        Rcv_RefRateType, Rcv_SwapYearlyNPayment, Rcv_SwapMaturity, Rcv_FixFloFlag, Rcv_DayCount,
                        Rcv_NotionalAMT, Rcv_NotionalPayDate, NZeroTermEstCurve, ZeroTermEstCurve, ZeroRateEstCurve,
                        ncurve + 1, ResultZeroTerm, ResultZeroRate, NResultCpnArray[i], ResultSchedule[i],
                        ResultSlope2D[i], ResultCPN2D[i], ResultFixedRefRate2D[i], Pay_RefRateType, Pay_SwapYearlyNPayment,
                        Pay_SwapMaturity, Pay_FixFloFlag, Pay_DayCount, Pay_NotionalAMT, Pay_NotionalPayDate,
                        NZeroTermEstCurve, ZeroTermEstCurve, ZeroRateEstCurve, ncurve + 1, ResultZeroTerm,
                        ResultZeroRate, NResultCpnArray[i], ResultScheduleUSD[i], ResultSlope2DUSD[i], ResultCPN2DUSD[i],
                        ResultFixedRefRate2DUSD[i], ResultPrice, ResultIRSInfo1 + k, ResultIRSInfo2 + k,
                        ResultIRSInfo3 + k, PV01, KeyRateRcvPV01, KeyRatePayPV01, SOFRConv, HolidayCalcFlag,
                        NHolidays, Holidays, NOverNightHistory, OverNightHistoryDate, OverNightHistoryRate,
                        RcvPayConvexityAdjFlag, RcvPayConvexityAdjFlag, TempDoubleArray, TempDoubleArray);

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
                free(Holidays);

            }
            ncurve += 1;
            k += (NResultCpnArray[i]+1) * 2;
        }

        n = 0;
        for (i = 0; i < NGenerator; i++)
        {
            for (j = 0; j < NResultCpnArray[i]; j++)
            {
                ResultForwardStart[n] = ResultForwardStart2D[i][j];
                ResultForwardEnd[n] = ResultForwardEnd2D[i][j];
                ResultStartDate[n] = ResultStart2D[i][j];
                ResultEndDate[n] = ResultEnd2D[i][j];
                ResultPayDate[n] = ResultPay2D[i][j];
                if (ProductType[i] == 1 || ProductType[i] == 5)
                {
                    ResultForwardStartUSD[n] = ResultForwardStart[n];
                    ResultForwardEndUSD[n] = ResultForwardEnd[n];
                    ResultStartUSD[n] = ResultStartUSD[n];
                    ResultEndUSD[n] = ResultEndDate[n];
                    ResultPayUSD[n] = ResultPayDate[n];
                }
                else
                {
                    ResultForwardStartUSD[n] = ResultForwardStart2DUSD[i][j];
                    ResultForwardEndUSD[n] = ResultForwardEnd2DUSD[i][j];
                    ResultStartUSD[n] = ResultStart2DUSD[i][j];
                    ResultEndUSD[n] = ResultEnd2DUSD[i][j];
                    ResultPayUSD[n] = ResultPay2DUSD[i][j];
                }
                n++;
            }
        }

        for (i = 0; i < NGenerator; i++)
        {
            free(ResultForwardStart2D[i]);
            free(ResultForwardEnd2D[i]);
            free(ResultStart2D[i]);
            free(ResultEnd2D[i]);
            free(ResultPay2D[i]);
            free(ResultSchedule[i]);
            free(ResultSlope2D[i]);
            free(ResultCPN2D[i]);
            free(ResultFixedRefRate2D[i]);
            free(ResultPaySchedule2D[i]);

            free(ResultForwardStart2DUSD[i]);
            free(ResultForwardEnd2DUSD[i]);
            free(ResultStart2DUSD[i]);
            free(ResultEnd2DUSD[i]);
            free(ResultPay2DUSD[i]);
            free(ResultScheduleUSD[i]);
            free(ResultSlope2DUSD[i]);
            free(ResultCPN2DUSD[i]);
            free(ResultFixedRefRate2DUSD[i]);
            free(ResultPaySchedule2DUSD[i]);
        }
        free(ResultForwardStart2D);
        free(ResultForwardEnd2D);
        free(ResultStart2D);
        free(ResultEnd2D);
        free(ResultPay2D);
        free(ResultSlope2D);
        free(ResultSchedule);
        free(ResultCPN2D);
        free(ResultFixedRefRate2D);

        free(ResultForwardStart2DUSD);
        free(ResultForwardEnd2DUSD);
        free(ResultStart2DUSD);
        free(ResultEnd2DUSD);
        free(ResultPay2DUSD);
        free(ResultScheduleUSD);
        free(ResultSlope2DUSD);
        free(ResultCPN2DUSD);
        free(ResultFixedRefRate2DUSD);
        free(ResultPaySchedule2D);
        free(ResultPaySchedule2DUSD);
    }
    free(DomesticHolidays);
    free(HolidaysUSD);
    free(HolidayUnionDomesticUSD);
    //_CrtDumpMemoryLeaks();
    return ResultCode;
}