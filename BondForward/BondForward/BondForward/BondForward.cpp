#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "CalcDate.h"
#include "Structure.h"
#include "Util.h"
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

typedef struct bnd_schd_info {
    long PriceDate_C;              // PricingDate CType

    long ReferenceType;            // Reference Rate type
    long FixedFlotype;             // Fix or Flo Flag 0:Fix 1: Flo
    long DayCount;                 // DayCountConvention 0:ACT365 1:ACT360 
    double NotionalAmount;         // Notional Amount
    long NAFlag;                   // Notional 지급여부

    long RefSwapFlag;              // 레퍼런스금리가 스왑금리인지여부
    long NSwapPayAnnual;           // 레퍼런스금리가 스왑금리라면 연 쿠폰지급 수
    double RefSwapMaturity;        // 레퍼런스 금리가 스왑금리라면 만기

    long NumberCpnFor1Y;           // Number of Coupon for 1Y
    long NCF;                      // 현금흐름개수
    long* ForwardStart_C;          // 금리추정시작일
    long* ForwardEnd_C;            // 금리추정종료일
    long* StartDate_C;             // Fraction 시작일(기산일)
    long* EndDate_C;               // Fraction 종료일(기말일)
    long* PayDate_C;               // 지급일
    long NotionalPayDate_C;        // 액면금액 지급일

    long HolidayFlag_Ref;          // 기초금리 Holiday Calc Flag
    long NHolidays_Ref;            // 기초금리 Holiday 개수
    long* Holidays_Ref;            // 기초금리 평가일 to Holiday

    double* FixedRefRate;          // 과거 확정금리 데이터
    double* Slope;                 // 기초금리에 대한 페이오프 기울기
    double* CPN;                   // 쿠폰이자율

    long LockOutRef;               //  LockOut 날짜 N영업일
    long LookBackRef;              //  LookBack 날짜 
    long ObservationShift;         //  Observation Shift 할 지여부

    long NRefHistory;              // 오버나이트 히스토리 개수
    long* RefHistoryDate;          // 오버나이트 히스토리 날짜
    double* RefHistory;            // 오버나이트 금리 히스토리

    long N_NotHoliday;            // Holiday가 아닌 영업일 Array개수
    long* NotHoliday;
    long* DayCount_NotHoliday;

} BNDSCHD;

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
                ResultForwardEndYYYYMMDD[0] = CpnDate[0];
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

double BondLegValue(
    long FXFlag,
    BNDSCHD* Schedule,
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
    double* ConvAdjVol,
    long ForwardMaturity,
    double& ForwardBondPrice,
    long YTMFlag
)
{
    long i;
    double YTM = DiscCurve.Rate[0];
    long FixedRateFlag;
    long PrevFlag;
    long SwapMaturityYYYYMMDD;
    double denominator;
    double dt;
    double alpha, n;
    
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
                        Schedule->PriceDate_C, FXFlag, DiscCurve, RefCurve, FXCurve,
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

                    if (FXFlag == 0) FXRate = 1.0;
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

                    if (FXFlag == 0) FXRate = 1.0;
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

                    if (FXFlag == 0) FXRate = 1.0;
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
        else if (Schedule->ReferenceType == -1)
        {
            //////////////////////////////////////////
            // 기초자산이 Bond Total Return 일 경우 //
            /////////////////////////////////////////

        }
    }
    else
    {
        //////////////
        // 고정금리 //
        //////////////
        if (YTMFlag == 0)
        {
            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

                if (PrevFlag == 0)
                {
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;
                    dt = DayCountFractionAtoB(Schedule->StartDate_C[i], Schedule->EndDate_C[i], Schedule->DayCount);

                    if (FXFlag == 0) FX = 1.0;
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
        else
        {
            alpha = 0.;
            for (i = 0; i < Schedule->NCF; i++)
            {
                if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C && Schedule->ForwardEnd_C[i] > Schedule->PriceDate_C)
                {
                    alpha = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->ForwardEnd_C[i]))/ ((double)DayCountAtoB(Schedule->ForwardStart_C[i], Schedule->ForwardEnd_C[i]));
                    break;
                }
            }

            if (alpha <= 0.) n = 1.;
            else n = 0.;
            
            for (i = 0; i < Schedule->NCF; i++)
            {
                // 이미 쿠폰 지급한 과거인지 확인
                PrevFlag = 1;
                if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

                if (PrevFlag == 0 && Schedule->EndDate_C[i] > Schedule->PriceDate_C)
                {
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;

                    if (FXFlag == 0) FX = 1.0;
                    else  FX = FXCurve.Interpolated_Rate(Pay_T);

                    DiscPay = 1.0 / pow(1.0 + YTM / ((double)Schedule->NumberCpnFor1Y), n + alpha);
                    ResultRefRate[i] = 0.0;
                    ResultCPN[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] / ((double)Schedule->NumberCpnFor1Y);
                    ResultDF[i] = DiscPay;
                    DiscCFArray[i] = ResultDF[i] * ResultCPN[i];
                    ResultRefRate[i] = Schedule->CPN[i];
                    n += 1.0;
                }
                else if (PrevFlag == 0 && Schedule->EndDate_C[i] <= Schedule->PriceDate_C)
                {
                    Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;

                    if (FXFlag == 0) FX = 1.0;
                    else  FX = FXCurve.Interpolated_Rate(Pay_T);
                    DiscPay = 1.0 / pow(1.0 + YTM / ((double)Schedule->NumberCpnFor1Y), Pay_T);
                    ResultRefRate[i] = 0.0;
                    ResultCPN[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] / ((double)Schedule->NumberCpnFor1Y);
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
    }
    value = sumation(DiscCFArray, Schedule->NCF);
    if (FXFlag == 0) FX = 1.0;
    else  FX = FXCurve.Interpolated_Rate(((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[Schedule->NCF - 1])) / 365.0);
    value += ResultDF[Schedule->NCF - 1] * FX * Schedule->NotionalAmount;

    ForwardBondPrice = 0.;
    for (i = 0; i < Schedule->NCF; i++)
    {
        if (ForwardMaturity < Schedule->EndDate_C[i])
        {
            ForwardBondPrice += DiscCFArray[i];
        }
    }
    ForwardBondPrice += ResultDF[Schedule->NCF - 1] * FX * Schedule->NotionalAmount;

    return value;
}

void CpnSumBeforeForwardMaturity(
    long FXFlag,
    long ForwardMaturity,
    BNDSCHD* Schedule,
    curveinfo& DiscCurve,
    curveinfo& FXCurve,
    long YTMFlag,
    long NTotalCpn,
    double* ResultCpn,
    double* ResultDiscCpn
)
{
    long i;
    long PrevFlag;
    double Pay_T, FX, n = 0.;
    double YTM = DiscCurve.Rate[0];
    double s = 0., cpn = 0., dt;

    double alpha = 0., DiscPay;
    for (i = 0; i < Schedule->NCF; i++)
    {
        if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C && Schedule->ForwardEnd_C[i] > Schedule->PriceDate_C)
        {
            alpha = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->ForwardEnd_C[i])) / ((double)DayCountAtoB(Schedule->ForwardStart_C[i], Schedule->ForwardEnd_C[i]));
            break;
        }
    }

    if (alpha <= 0.) n = 1.;
    else n = 0.;

    alpha = 0.;
    for (i = 0; i < Schedule->NCF; i++)
    {
        if (Schedule->ForwardStart_C[i] < Schedule->PriceDate_C && Schedule->ForwardEnd_C[i] > Schedule->PriceDate_C)
        {
            alpha = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->ForwardEnd_C[i])) / ((double)DayCountAtoB(Schedule->ForwardStart_C[i], Schedule->ForwardEnd_C[i]));
            break;
        }
    }

    if (alpha <= 0.) n = 1.;
    else n = 0.;

    for (i = 0; i < Schedule->NCF; i++)
    {
        // 이미 쿠폰 지급한 과거인지 확인
        PrevFlag = 1;
        if (Schedule->PayDate_C[i] > Schedule->PriceDate_C) PrevFlag = 0;

        if (PrevFlag == 0 && Schedule->EndDate_C[i] > Schedule->PriceDate_C && ForwardMaturity >= Schedule->EndDate_C[i])
        {
            Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;

            if (FXFlag == 0) FX = 1.0;
            else  FX = FXCurve.Interpolated_Rate(Pay_T);

            DiscPay = 1.0 / pow(1.0 + YTM / ((double)Schedule->NumberCpnFor1Y), n + alpha);
            ResultCpn[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] / ((double)Schedule->NumberCpnFor1Y);
            ResultDiscCpn[i] = DiscPay * ResultCpn[i];
            n += 1.0;
        }
        else if (PrevFlag == 0 && Schedule->EndDate_C[i] <= Schedule->PriceDate_C && ForwardMaturity >= Schedule->EndDate_C[i])
        {
            Pay_T = ((double)DayCountAtoB(Schedule->PriceDate_C, Schedule->PayDate_C[i])) / 365.0;

            if (FXFlag == 0) FX = 1.0;
            else  FX = FXCurve.Interpolated_Rate(Pay_T);
            DiscPay = 1.0 / pow(1.0 + YTM / ((double)Schedule->NumberCpnFor1Y), Pay_T);
            ResultCpn[i] = FX * Schedule->NotionalAmount * Schedule->CPN[i] / ((double)Schedule->NumberCpnFor1Y);
            ResultDiscCpn[i] = DiscPay * ResultCpn[i];
        }
        else
        {
            ResultCpn[i] = 0.0;
            ResultDiscCpn[i] = 0.0;
        }
    }
}

double BondForwardPricing(
    long PriceDate,
    long ForwardMaturityDate,
    BNDSCHD* BondSchd,
    long NBondZeroCurveTerm,
    double* BondZeroCurveTerm,
    double* BondZeroCurveRate,
    long BondYTMFlag,
    long BondMarketPriceFlag,
    double BondMarketPrice,
    long NRiskfreeCurveTerm,
    double* RiskfreeCurveTerm,
    double* RiskfreeCurveRate,
    long FXFlag,
    long NFX,
    double* FXTerm,
    double* FXRate,
    double* ResultRefRate,
    double* ResultDiscCF,
    double* ResultCPN,
    double* ResultDF,
    double* CpnBondBeforeFMaturity,
    double* ResultDiscCpnBeforeFMaturity,
    double& BondPriceOnForwardDate,
    double& ResultBondPrice
)
{
    long i, n;
    long PrevFlag;
    long nconv = 1;
    double convvolt[1] = { 1.0 };
    double convvol[1] = { 0.001 };

    curveinfo Rcv_DiscCurve(NBondZeroCurveTerm, BondZeroCurveTerm, BondZeroCurveRate);
    curveinfo Rcv_RefCurve(NRiskfreeCurveTerm, RiskfreeCurveTerm, RiskfreeCurveRate);
    curveinfo Rcv_FXCurve(NFX, FXTerm, FXRate);
    double BondPrice, ForwardPrice;
    double InterestBeforeForwardMaturity;
    double t = ((double)DayCountAtoB(PriceDate, ForwardMaturityDate)) / 365.;
    double t_act = DayCountFractionAtoB(PriceDate, ForwardMaturityDate, 2);
    double DF_t_IRS = exp(-t* Rcv_RefCurve.Interpolated_Rate(t));
    double DF_t_Bond = exp(-t * Rcv_DiscCurve.Interpolated_Rate(t));
    double fbondv = 0.;
    BondPrice = BondLegValue(FXFlag, BondSchd, Rcv_DiscCurve, Rcv_RefCurve, Rcv_FXCurve, ResultRefRate, ResultCPN, ResultDF, ResultDiscCF, 0, nconv, convvolt, convvol, ForwardMaturityDate, fbondv, BondYTMFlag);
    if (BondYTMFlag == 1)
    {
        n = 0;
        for (i = 0; i < BondSchd->NCF; i++)
        {
            PrevFlag = 1;
            if (BondSchd->PayDate_C[i] > BondSchd->PriceDate_C) PrevFlag = 0;

            if (PrevFlag == 0 && ForwardMaturityDate > BondSchd->ForwardStart_C[i] && ForwardMaturityDate > BondSchd->ForwardEnd_C[i])
            {
                n += 1;
            }
            else if (ForwardMaturityDate > BondSchd->ForwardStart_C[i] && ForwardMaturityDate <= BondSchd->PayDate_C[i])
            {
                n += ((double)DayCountAtoB(BondSchd->ForwardStart_C[i], ForwardMaturityDate)) / ((double)DayCountAtoB(BondSchd->ForwardStart_C[i], BondSchd->ForwardEnd_C[i]));
            }
        }
        DF_t_Bond = 1.0 / pow(1.0 + Rcv_DiscCurve.Rate[0] / (double)BondSchd->NumberCpnFor1Y, n);
    }

    CpnSumBeforeForwardMaturity(FXFlag, ForwardMaturityDate, BondSchd, Rcv_DiscCurve, Rcv_FXCurve, BondYTMFlag, BondSchd->NCF, CpnBondBeforeFMaturity, ResultDiscCpnBeforeFMaturity);
    InterestBeforeForwardMaturity = sumation(ResultDiscCpnBeforeFMaturity, BondSchd->NCF);

    if (BondMarketPriceFlag == 0) ForwardPrice = (BondPrice - InterestBeforeForwardMaturity) / DF_t_IRS;
    else ForwardPrice = (BondMarketPrice - InterestBeforeForwardMaturity) / DF_t_IRS;
    
    BondPriceOnForwardDate = fbondv / DF_t_Bond;
    ResultBondPrice = BondPrice;
    return ForwardPrice;
}

DLLEXPORT(long) Calc_BondForward(
    double Nominal,
    long Fix0Flo1Flag,
    long PriceDate,
    long RefBondEffectiveDate,
    long RefBondMaturityDate,

    long RefBondNumCpnOneYear,
    double RefBondCpnRate,
    long NDayFromBondEndToPay,
    long ForwardMaturityDate,
    long NBondZeroCurveTerm,

    double* BondZeroCurveTerm,
    double* BondZeroCurveRate,
    long BondYTMFlag,
    long BondMarketPriceFlag,
    double BondMarketPrice,

    double ForwardExercisePrice,
    long NRiskfreeCurveTerm,
    double* RiskfreeCurveTerm,
    double* RiskfreeCurveRate,
    long NFX,

    double* FXTerm,
    double* FXRate,
    long DayCountFlag,
    double FixingRateFloatLeg,
    long NHolidays,

    long* Holidays,
    long GreekFlag,
    long TextFlag,
    long NMaxResultSchedule,
    double* ResultPriceArray,           // Len = 6

    double* ResultSchedule,             // Len = NMaxResultSchedule * 4
    double* ResultGreek                 // Len = NBondZeroCurveTerm * 2 + NRiskfreeCurveTerm * 2
)
{
    long i, j;

    if (PriceDate < 19000100) PriceDate = ExcelDateToCDate(PriceDate);
    if (RefBondEffectiveDate < 19000100) RefBondEffectiveDate = ExcelDateToCDate(RefBondEffectiveDate);
    if (RefBondMaturityDate < 19000100) RefBondMaturityDate = ExcelDateToCDate(RefBondMaturityDate);
    if (ForwardMaturityDate < 19000100) ForwardMaturityDate = ExcelDateToCDate(ForwardMaturityDate);
    for (i = 0 ; i < NHolidays; i++) if (Holidays[i] < 19000100) Holidays[i]= ExcelDateToCDate(Holidays[i]);    
    Preprocessing_TermAndRate(PriceDate, NBondZeroCurveTerm, BondZeroCurveTerm, BondZeroCurveRate);
    Preprocessing_TermAndRate(PriceDate, NRiskfreeCurveTerm, RiskfreeCurveTerm, RiskfreeCurveRate);

    long NCPN_BOND = Number_Coupon_YYYYMMDD(1, RefBondEffectiveDate, RefBondMaturityDate, RefBondNumCpnOneYear, 1, NHolidays, Holidays);
    long* BondForwardStartYYYYMMDD = (long*)malloc(sizeof(long) * NCPN_BOND);               // 1
    long* BondForwardEndYYYYMMDD = (long*)malloc(sizeof(long) * NCPN_BOND);                 // 2
    long* BondPayYYYYMMDD = (long*)malloc(sizeof(long) * NCPN_BOND);                        // 3
    double* Slope = (double*)malloc(sizeof(double) * NCPN_BOND);                            // 4
    double* FixedRefRate = (double*)malloc(sizeof(double) * NCPN_BOND);                     // 5
    double* BndCpn = (double*)malloc(sizeof(double) * NCPN_BOND);                           // 6
    ResultCpnMapping_YYYYMMDD(1, RefBondEffectiveDate, RefBondEffectiveDate, RefBondMaturityDate, NDayFromBondEndToPay,
                              RefBondNumCpnOneYear, 1, NHolidays, Holidays, NCPN_BOND,
                              BondForwardStartYYYYMMDD, BondForwardEndYYYYMMDD, BondPayYYYYMMDD);

    for (i = 0; i < NCPN_BOND; i++)
    {
        Slope[i] = (double)(Fix0Flo1Flag > 0);
        BndCpn[i] = RefBondCpnRate;
        if (BondForwardStartYYYYMMDD[i] < PriceDate && PriceDate < BondForwardEndYYYYMMDD[i] )
        {
            FixedRefRate[i] = FixingRateFloatLeg;
        }
    }
    long NCpnBondBeforeFMaturity = NCPN_BOND;
    double* ResultCpnBeforeFMaturity = (double*)malloc(sizeof(double) * NCPN_BOND);         // 7
    double* ResultDiscCpnBeforeFMaturity = (double*)malloc(sizeof(double) * NCPN_BOND);     // 8
    
    double* ResultRefRate = (double*)malloc(sizeof(double) * NCPN_BOND);                    // 9
    double* ResultDiscCF = (double*)malloc(sizeof(double) * NCPN_BOND);                     // 10
    double* ResultCPN = (double*)malloc(sizeof(double) * NCPN_BOND);                        // 11
    double* ResultDF = (double*)malloc(sizeof(double) * NCPN_BOND);                         // 12

    BNDSCHD* BNDSchedule = new BNDSCHD;                                                     // 13
    BNDSchedule->HolidayFlag_Ref = 1;
    BNDSchedule->NHolidays_Ref = NHolidays;
    BNDSchedule->Holidays_Ref = Holidays;
    BNDSchedule->NCF = NCPN_BOND;
    BNDSchedule->ForwardStart_C = BondForwardStartYYYYMMDD;
    BNDSchedule->ForwardEnd_C = BondForwardEndYYYYMMDD;
    BNDSchedule->StartDate_C = BondForwardStartYYYYMMDD;
    BNDSchedule->EndDate_C = BondForwardEndYYYYMMDD;
    BNDSchedule->PayDate_C = BondPayYYYYMMDD;
    BNDSchedule->NotionalPayDate_C = BondPayYYYYMMDD[NCPN_BOND-1];
    BNDSchedule->ReferenceType = 0;
    BNDSchedule->FixedFlotype = Fix0Flo1Flag;
    BNDSchedule->DayCount = DayCountFlag;
    BNDSchedule->NotionalAmount = Nominal;
    BNDSchedule->NRefHistory = 0;
    BNDSchedule->RefHistoryDate = NULL;
    BNDSchedule->RefHistory = NULL;
    BNDSchedule->NumberCpnFor1Y = RefBondNumCpnOneYear;

    if (BNDSchedule->ReferenceType != 0 && BNDSchedule->ReferenceType != 2) BNDSchedule->RefSwapFlag = 1;
    BNDSchedule->NSwapPayAnnual = 4;
    BNDSchedule->RefSwapMaturity = 0.25;
    BNDSchedule->FixedRefRate = FixedRefRate;
    BNDSchedule->Slope = Slope;
    BNDSchedule->CPN = BndCpn;
    BNDSchedule->NAFlag = 1;
    BNDSchedule->PriceDate_C = PriceDate;

    BNDSchedule->LockOutRef = 0;
    BNDSchedule->LookBackRef = 0;
    BNDSchedule->ObservationShift = 0;
    BNDSchedule->N_NotHoliday = 0;
    BNDSchedule->NotHoliday = NULL;
    BNDSchedule->DayCount_NotHoliday = NULL;

    double BondPriceOnForwardDate = 0.;
    double BondPrice = 0.;
    ForwardMaturityDate = ParseBusinessDateIfHoliday(ForwardMaturityDate, Holidays, NHolidays);
    double ForwardPrice = BondForwardPricing(PriceDate, ForwardMaturityDate, BNDSchedule, NBondZeroCurveTerm, BondZeroCurveTerm,
                                            BondZeroCurveRate, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice, NRiskfreeCurveTerm,
                                            RiskfreeCurveTerm, RiskfreeCurveRate, NFX > 0, NFX, FXTerm,
                                            FXRate, ResultRefRate, ResultDiscCF, ResultCPN, ResultDF, ResultCpnBeforeFMaturity,
                                            ResultDiscCpnBeforeFMaturity, BondPriceOnForwardDate, BondPrice);
    double t = ((double)DayCountAtoB(PriceDate, ForwardMaturityDate)) / 365.;
    double value = (ForwardPrice - ForwardExercisePrice) * exp(-Interpolate_Linear(RiskfreeCurveTerm, RiskfreeCurveRate, NRiskfreeCurveTerm, t));
    double value2 = BondPriceOnForwardDate * exp(-Interpolate_Linear(RiskfreeCurveTerm, RiskfreeCurveRate, NRiskfreeCurveTerm, t)) - ForwardExercisePrice * exp(-Interpolate_Linear(BondZeroCurveTerm, BondZeroCurveRate, NBondZeroCurveTerm, t));
    ResultPriceArray[0] = ForwardPrice;
    ResultPriceArray[1] = BondPrice;
    ResultPriceArray[2] = BondPriceOnForwardDate;
    ResultPriceArray[3] = value;
    ResultPriceArray[4] = (double)NCPN_BOND;
    ResultPriceArray[5] = value2;

    for (i = 0; i < min(NMaxResultSchedule, NCPN_BOND); i++)
    {
        ResultSchedule[i] = BondPayYYYYMMDD[i];
        ResultSchedule[i + NCPN_BOND] = ResultRefRate[i];
        ResultSchedule[i + 2 * NCPN_BOND] = ResultCPN[i];
        ResultSchedule[i + 3 * NCPN_BOND] = ResultDF[i];
        ResultSchedule[i + 4 * NCPN_BOND] = ResultDiscCF[i];
    }

    double* RiskfreeCurveRateUp = (double*)malloc(sizeof(double) * NRiskfreeCurveTerm);     // 14
    double* BondZeroCurveRateUp = (double*)malloc(sizeof(double) * NBondZeroCurveTerm);     // 15
    double* RiskfreeCurveRateDn = (double*)malloc(sizeof(double) * NRiskfreeCurveTerm);     // 16
    double* BondZeroCurveRateDn = (double*)malloc(sizeof(double) * NBondZeroCurveTerm);     // 17
    double Pu, Pd;
    if (GreekFlag)
    {
        for (i = 0; i < NBondZeroCurveTerm; i++)
        {
            for (j = 0; j < NBondZeroCurveTerm; j++)
            {
                if (i == j) BondZeroCurveRateUp[j] = BondZeroCurveRate[j] + 0.0001;
                else BondZeroCurveRateUp[j] = BondZeroCurveRate[j];
            }

            for (j = 0; j < NBondZeroCurveTerm; j++)
            {
                if (i == j) BondZeroCurveRateDn[j] = BondZeroCurveRate[j] - 0.0001;
                else BondZeroCurveRateDn[j] = BondZeroCurveRate[j];
            }

            Pu = BondForwardPricing(PriceDate, ForwardMaturityDate, BNDSchedule, NBondZeroCurveTerm, BondZeroCurveTerm,
                BondZeroCurveRateUp, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice, NRiskfreeCurveTerm,
                RiskfreeCurveTerm, RiskfreeCurveRate, NFX > 0, NFX, FXTerm,
                FXRate, ResultRefRate, ResultDiscCF, ResultCPN, ResultDF, ResultCpnBeforeFMaturity,
                ResultDiscCpnBeforeFMaturity, BondPriceOnForwardDate, BondPrice);
            Pd = BondForwardPricing(PriceDate, ForwardMaturityDate, BNDSchedule, NBondZeroCurveTerm, BondZeroCurveTerm,
                BondZeroCurveRateDn, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice, NRiskfreeCurveTerm,
                RiskfreeCurveTerm, RiskfreeCurveRate, NFX > 0, NFX, FXTerm,
                FXRate, ResultRefRate, ResultDiscCF, ResultCPN, ResultDF, ResultCpnBeforeFMaturity,
                ResultDiscCpnBeforeFMaturity, BondPriceOnForwardDate, BondPrice);
            ResultGreek[i] = (Pu - ForwardPrice);
            ResultGreek[i + NBondZeroCurveTerm] = (Pu + Pd - 2.0 * ForwardPrice);
        }


        for (i = 0; i < NRiskfreeCurveTerm; i++)
        {
            for (j = 0; j < NRiskfreeCurveTerm; j++)
            {
                if (i == j) RiskfreeCurveRateUp[j] = RiskfreeCurveRate[j] + 0.0001;
                else RiskfreeCurveRateUp[j] = RiskfreeCurveRate[j];
            }

            for (j = 0; j < NRiskfreeCurveTerm; j++)
            {
                if (i == j) RiskfreeCurveRateDn[j] = RiskfreeCurveRate[j] - 0.0001;
                else RiskfreeCurveRateDn[j] = RiskfreeCurveRate[j];
            }

            Pu = BondForwardPricing(PriceDate, ForwardMaturityDate, BNDSchedule, NBondZeroCurveTerm, BondZeroCurveTerm,
                BondZeroCurveRate, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice, NRiskfreeCurveTerm,
                RiskfreeCurveTerm, RiskfreeCurveRateUp, NFX > 0, NFX, FXTerm,
                FXRate, ResultRefRate, ResultDiscCF, ResultCPN, ResultDF, ResultCpnBeforeFMaturity,
                ResultDiscCpnBeforeFMaturity, BondPriceOnForwardDate, BondPrice);
            Pd = BondForwardPricing(PriceDate, ForwardMaturityDate, BNDSchedule, NBondZeroCurveTerm, BondZeroCurveTerm,
                BondZeroCurveRate, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice, NRiskfreeCurveTerm,
                RiskfreeCurveTerm, RiskfreeCurveRateDn, NFX > 0, NFX, FXTerm,
                FXRate, ResultRefRate, ResultDiscCF, ResultCPN, ResultDF, ResultCpnBeforeFMaturity,
                ResultDiscCpnBeforeFMaturity, BondPriceOnForwardDate, BondPrice);
            ResultGreek[i + 2 * NBondZeroCurveTerm] = (Pu - ForwardPrice);
            ResultGreek[i + NRiskfreeCurveTerm + 2 * NBondZeroCurveTerm] = (Pu + Pd - 2.0 * ForwardPrice);
        }
    }

    if (BondForwardStartYYYYMMDD) free(BondForwardStartYYYYMMDD);               // 1
    if (BondForwardEndYYYYMMDD) free(BondForwardEndYYYYMMDD);                   // 2    
    if (BondPayYYYYMMDD) free(BondPayYYYYMMDD);                                 // 3
    if (FixedRefRate) free(FixedRefRate);                                       // 4
    if (BndCpn) free(BndCpn);                                                   // 5
    if (Slope) free(Slope);                                                     // 6
    if (ResultCpnBeforeFMaturity) free(ResultCpnBeforeFMaturity);               // 7
    if (ResultDiscCpnBeforeFMaturity) free(ResultDiscCpnBeforeFMaturity);       // 8
    if (ResultRefRate) free(ResultRefRate);                                     // 9
    if (ResultDiscCF) free(ResultDiscCF);                                       // 10
    if (ResultCPN) free(ResultCPN);                                             // 11
    if (ResultDF) free(ResultDF);                                               // 12
    delete (BNDSchedule);                                                       // 13
    if (RiskfreeCurveRateUp) free(RiskfreeCurveRateUp);                         // 14
    if (BondZeroCurveRateUp) free(BondZeroCurveRateUp);                         // 15
    if (RiskfreeCurveRateDn) free(RiskfreeCurveRateDn);                         // 16
    if (BondZeroCurveRateDn) free(BondZeroCurveRateDn);                         // 17
    return 1;
}

int main()
{   
    double Nominal = 100.;
    long Fix0Flo1Flag = 0;
    long PriceDate = 20260518;
    long RefBondEffectiveDate = 20260518;
    long RefBondMaturityDate = RefBondEffectiveDate + 10 * 10000;
    long RefBondNumCpnOneYear = 1;
    double RefBondCpnRate = 0.04;
    long NDayFromBondEndToPay = 0;
    long ForwardMaturityDate = RefBondEffectiveDate + 10 * 10000;
    long NBondZeroCurveTerm = 3;
    double BondZeroCurveTerm[3] = { 1., 2., 3. };
    double BondZeroCurveRate[3] = { 0.04, 0.04, 0.04 };
    long BondYTMFlag = 1;
    long BondMarketPriceFlag = 0;
    double BondMarketPrice = 100.;
    double ForwardExercisePrice = 0.;
    long NRiskfreeCurveTerm = 2;
    double RiskfreeCurveTerm[2] = { 0.5, 1.};
    double RiskfreeCurveRate[2] = { 0.035, 0.035 };
    long NFX = 0;
    long DayCountFlag = 3;
    double FixingRateFloatLeg = 0.035;
    long NHolidays = 1;
    long Holidays[1] = { 19000101 };
    long GreekFlag = 0;
    long TextFlag = 0;
    long NMaxResultSchedule = 100;
    double ResultPriceArray[100];
    double ResultSchedule[100];
    double ResultGreek[100];
    Calc_BondForward(Nominal, Fix0Flo1Flag, PriceDate, RefBondEffectiveDate, RefBondMaturityDate,
        RefBondNumCpnOneYear, RefBondCpnRate, NDayFromBondEndToPay, ForwardMaturityDate, NBondZeroCurveTerm,
        BondZeroCurveTerm, BondZeroCurveRate, BondYTMFlag, BondMarketPriceFlag, BondMarketPrice,
        ForwardExercisePrice, NRiskfreeCurveTerm, RiskfreeCurveTerm, RiskfreeCurveRate, NFX,
        NULL, NULL, DayCountFlag, FixingRateFloatLeg, NHolidays,
        Holidays, GreekFlag, TextFlag, NMaxResultSchedule, ResultPriceArray,
        ResultSchedule, ResultGreek);
    return 0;
}