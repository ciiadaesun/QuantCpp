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


double DayCountFraction(long Day1, long Day2, long Flag)
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
	else
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

long* Generate_CpnDate_IFS(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate)
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

long* Generate_CpnDate_Holiday_IFS(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
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
			if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
			else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

			free(CpnDate);
			free(HolidayYYYYMMDD);
			return ncpn;
		}
	}
	else
	{
		if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
		else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

		free(CpnDate);
		free(HolidayYYYYMMDD);
		return ncpn;
	}
}

DLLEXPORT(long) Number_Coupon_CDate(
	long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
	long PriceDateCDate,			// 평가일
	long SwapMatCDate,				// 스왑 만기
	long AnnCpnOneYear,             // 연 스왑쿠폰지급수
	long HolidayUseFlag,            // 공휴일 입력 사용 Flag
	long NHoliday,                  // 공휴일 개수
	long* HolidayCDate				// 공휴일
)
{
	long i;
	long PriceDateYYYYMMDD = PriceDateCDate;          // 평가일
	long SwapMat_YYYYMMDD = SwapMatCDate;             // 스왑 만기

	if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2) ProductType = 1;
	if (ProductType == 0) return 1;

	// 에러처리
	if (PriceDateYYYYMMDD <= 19000101 || PriceDateYYYYMMDD >= 999990101)  return -1;
	if (SwapMat_YYYYMMDD <= 19000101 || SwapMat_YYYYMMDD >= 999990101) return -1;
	if (AnnCpnOneYear > 6) return -1;

	long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
	for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = HolidayCDate[i];
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
			if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
			else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

			free(CpnDate);
			free(HolidayYYYYMMDD);
			return ncpn;
		}
	}
	else
	{
		if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
		else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

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
	long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
	for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayExcelType[i]);


	if (NumberCoupon < 0) return -1;
	if (NumberCoupon <= 1)
	{
		ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
		ResultForwardEnd[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
		n = 0;
		if (NBDayFromEndDate == 0)
		{
			if (HolidayUseFlag == 0) ResultPayDate[0] = ResultForwardEnd[0];
			else
			{
				ResultPayDate[0] = ResultForwardEnd[0];
				MOD7 = ResultPayDate[0] % 7;
				if (MOD7 == 0) ResultPayDate[0] += 2;
				else if (MOD7 == 1) ResultPayDate[0] += 1;
			}
		}
		else
		{
			for (i = 1; i < 10; i++)
			{
				PayDateYYYYMMDD = DayPlus(SwapMat_YYYYMMDD, i);
				PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
				MOD7 = PayDateExcelType % 7;
				if ((MOD7 != 1 && MOD7 != 0) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
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

		if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
		else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

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

DLLEXPORT(long) ResultCpnMappingCDate(
	long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
	long PriceDateCDate,			// 평가일
	long StartDateCDate,			// 시작일
	long SwapMatCDate,				// 스왑 만기
	long NBDayFromEndDate,          // N영업일 뒤 지급
	long AnnCpnOneYear,             // 연 스왑쿠폰지급수
	long HolidayUseFlag,            // 공휴일 입력 사용 Flag
	long NHoliday,                  // 공휴일 개수
	long* HolidayCDate,				// 공휴일
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
	long PriceDateYYYYMMDD = PriceDateCDate;          // 평가일
	long StartDateYYYYMMDD = StartDateCDate;          // 평가일
	long SwapMat_YYYYMMDD = SwapMatCDate;             // 스왑 만기
	long ncpn;
	long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
	for (i = 0; i < NHoliday; i++) HolidayYYYYMMDD[i] = HolidayCDate[i];


	if (NumberCoupon < 0) return -1;
	if (NumberCoupon <= 1)
	{
		ResultForwardStart[0] = (StartDateYYYYMMDD);
		ResultForwardEnd[0] = (SwapMat_YYYYMMDD);
		n = 0;
		if (NBDayFromEndDate == 0)
		{
			if (HolidayUseFlag == 0) ResultPayDate[0] = ResultForwardEnd[0];
			else
			{
				PayDateExcelType = CDateToExcelDate(ResultForwardEnd[0]);
				MOD7 = PayDateExcelType % 7;
				if (MOD7 == 0) PayDateExcelType += 2;
				else if (MOD7 == 1) PayDateExcelType += 1;
				
				ResultPayDate[0] = ExcelDateToCDate(PayDateExcelType);
			}
		}
		else
		{
			for (i = 1; i < 10; i++)
			{
				PayDateYYYYMMDD = DayPlus(SwapMat_YYYYMMDD, i);
				PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
				MOD7 = PayDateExcelType % 7;
				if ((MOD7 != 1 && MOD7 != 0) && !isin(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
				{
					// 영업일이면 n+=1
					n += 1;
				}

				if (n == NBDayFromEndDate)
				{
					ResultPayDate[0] = ExcelDateToCDate(PayDateExcelType);
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

		if (HolidayUseFlag == 1) CpnDate = Generate_CpnDate_Holiday_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD);
		else CpnDate = Generate_CpnDate_IFS(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD);

		for (i = 0; i < min(NumberCoupon, ncpn); i++)
		{
			if (i == 0)
			{
				ResultForwardStart[0] = (StartDateYYYYMMDD);
				TempDateExcelType = (CpnDate[0]);
				ResultForwardEnd[0] = TempDateExcelType;
			}
			else
			{
				ResultForwardStart[i] = (CpnDate[i - 1]);
				TempDateExcelType = (CpnDate[i]);
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
						ResultPayDate[i] = ExcelDateToCDate(PayDateExcelType);
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

double FixedLeg(
	double NA,
	long NAFlag,
	long PriceDate,
	long DayCountFrac,
	long CpnFrac,

	long NAMat,
	long NCpn,
	long* StartDate,
	long* EndDate,
	long* PayDate,

	double* FixedCpn,
	long NRate,
	double* RateTerm,
	double* Rate,
	double* Result
)
{
	long i;
	double NPV_Fix = 0.;
	double T, deltat, CalcCpn, r;
	double DiscNA ;
	for (i = 0; i < NCpn; i++)
	{
		T = DayCountAtoB(PriceDate, PayDate[i]) / 365.;
		if (T > 0.0)
		{
			deltat = DayCountFraction(StartDate[i], EndDate[i], DayCountFrac);
			if (CpnFrac == 0) CalcCpn = deltat * NA * FixedCpn[i];
			else CalcCpn = NA * (pow(1.0 + FixedCpn[i], deltat) - 1.);
			r = Interpolate_Linear(RateTerm, Rate, NRate, T);
			if (T > 0.)
			{
				Result[i] = CalcCpn;
				Result[i + NCpn] = exp(-r * T);
				Result[i + 2 * NCpn] = CalcCpn * Result[i + NCpn];
				NPV_Fix += Result[i + 2 * NCpn];
			}
		}
	}

	if (NAFlag > 0)
	{
		T = DayCountAtoB(PriceDate, NAMat)/365.;
		r = Interpolate_Linear(RateTerm, Rate, NRate, T);
		DiscNA = NA * exp(-r * T);
		NPV_Fix += DiscNA;
		Result[3 * NCpn] = NA;
		Result[3 * NCpn + 1] = exp(-r * T);
		Result[3 * NCpn + 2] = NA * Result[3 * NCpn + 1];
	}

	return NPV_Fix;
}

double InflationLeg(
	double NA,
	long NAFlag,
	long PriceDate,
	long DayCountFrac,

	long NAMatInfla,
	long RealRateProductFlag,
	long NCpnInfla,
	long* StartDateInfla,
	long* EndDateInfla,

	double* ForwardRateMultipleInfla,
	long* EstStartDate,
	long* EstEndDate,
	long* PayDateInfla,
	long* ConvincedFlag,

	double* EstStartCPI,
	double* EstEndCPI,
	double* ConvincedRate,
	long* RealRateUseFlag,
	double* RealRateMargin,

	long NRate,
	double* RateTerm,
	double* Rate,
	long PriceDateInflation,
	long NInfla,

	double* InflaTerm,
	double* InflaRate,
	double CurrentCPI,
	double* Result
)
{
	long i;
	double NPV_Inflation = 0.;
	double T, deltat, CalcCpn, r, fr, r_cpi, DiscNA;
	double CPI_Start, CPI_End;
	double T_EstStart, T_EstEnd, T_EstRateStart, T_EstRateEnd;

	double InflationReturn = 0.0;
	for (i = 0; i < NCpnInfla; i++)
	{
		T = DayCountAtoB(PriceDate, PayDateInfla[i]) / 365.;
		r = Interpolate_Linear(RateTerm, Rate, NRate, T);

		T_EstStart = DayCountAtoB(PriceDateInflation, EstStartDate[i]) / 365.0;
		T_EstEnd = DayCountAtoB(PriceDateInflation, EstEndDate[i]) / 365.0;

		// 이자율 추정시작
		if (StartDateInfla[i] != 0) T_EstRateStart = DayCountAtoB(PriceDate, StartDateInfla[i]) / 365.0;
		if (EndDateInfla[i] != 0) T_EstRateEnd = DayCountAtoB(PriceDate, EndDateInfla[i]) / 365.0;

		CPI_Start = 0.;
		CPI_End = 0.;

		if (T > 0.0)
		{
			InflationReturn = 0.0;
			if (T_EstStart < 0.0)
			{
				if (T_EstEnd < 0.0)
				{
					if (ConvincedFlag[i] > 0)
					{
						CPI_Start = EstStartCPI[i];
						CPI_End = EstEndCPI[i];
						if (RealRateProductFlag > 0 && RealRateUseFlag[i] > 0) InflationReturn = CPI_End / CPI_Start;
						else InflationReturn = CPI_End / CPI_Start - 1.0;
					}
				}
				else if (EstEndDate[i] == PriceDateInflation)
				{
					if (ConvincedFlag[i] > 0)
					{
						CPI_Start = EstStartCPI[i];
						CPI_End = CurrentCPI;
						if (RealRateProductFlag > 0 && RealRateUseFlag[i] > 0) InflationReturn = CPI_End / CPI_Start;
						else InflationReturn = CPI_End / CPI_Start - 1.0;
					}
				}
				else
				{
					if (ConvincedFlag[i] > 0)
					{
						CPI_Start = EstStartCPI[i];
						r_cpi = Interpolate_Linear(InflaTerm, InflaRate, NInfla, T_EstEnd);
						CPI_End = exp(r_cpi * T_EstEnd) * CurrentCPI;
						if (RealRateProductFlag > 0 && RealRateUseFlag[i] > 0) InflationReturn = CPI_End / CPI_Start;
						else InflationReturn = CPI_End / CPI_Start - 1.0;
					}
				}
			}
			else if (PriceDateInflation == EstStartDate[i])
			{
				CPI_Start = CurrentCPI;
				r_cpi = Interpolate_Linear(InflaTerm, InflaRate, NInfla, T_EstEnd);
				CPI_End = exp(r_cpi * T_EstEnd) * CurrentCPI;
				if (RealRateProductFlag > 0) InflationReturn = CPI_End / CPI_Start;
				else InflationReturn = CPI_End / CPI_Start - 1.0;
			}
			else
			{
				r_cpi = Interpolate_Linear(InflaTerm, InflaRate, NInfla, T_EstStart);
				CPI_Start = exp(r_cpi * T_EstStart) * CurrentCPI;
				r_cpi = Interpolate_Linear(InflaTerm, InflaRate, NInfla, T_EstEnd);
				CPI_End = exp(r_cpi * T_EstEnd) * CurrentCPI;
				if (RealRateProductFlag > 0 && RealRateUseFlag[i] > 0) InflationReturn = CPI_End / CPI_Start;
				else InflationReturn = CPI_End / CPI_Start - 1.0;
			}

			fr = 0.;
			deltat = 0.;
			if (StartDateInfla[i] != 0)
			{
				deltat = DayCountAtoB(StartDateInfla[i], EndDateInfla[i]) / 365.;
				if (T_EstRateStart < 0.0)
				{
					if (ConvincedFlag[i] > 0)
					{
						fr = ConvincedRate[i];
					}
				}
				else if (T_EstRateStart == 0.0)
				{
					fr = Calc_Forward_Rate(RateTerm, Rate, NRate, 0.0, T_EstRateEnd);
				}
				else
				{
					fr = Calc_Forward_Rate(RateTerm, Rate, NRate, T_EstRateStart, T_EstRateEnd);
				}
			}
			if (RealRateProductFlag > 0 && RealRateUseFlag[i] > 0) CalcCpn = InflationReturn * RealRateMargin[i] * NA + fr * deltat * NA * ForwardRateMultipleInfla[i];
			else CalcCpn = InflationReturn * NA + fr * deltat * NA * ForwardRateMultipleInfla[i];

			Result[i] = CalcCpn;
			Result[i + NCpnInfla] = exp(-r * T);
			Result[i + 2 * NCpnInfla] = CalcCpn * Result[i + NCpnInfla];
			Result[i + 3 * NCpnInfla] = CPI_Start;
			Result[i + 4 * NCpnInfla] = CPI_End;
			Result[i + 5 * NCpnInfla] = fr;

			NPV_Inflation += Result[i + 2 * NCpnInfla];
		}
	}

	if (NAFlag > 0)
	{
		T = DayCountAtoB(PriceDate, NAMatInfla) / 365.;
		r = Interpolate_Linear(RateTerm, Rate, NRate, T);
		DiscNA = NA * exp(-r * T);
		NPV_Inflation += DiscNA;
		Result[6 * NCpnInfla] = NA;
		Result[6 * NCpnInfla + 1] = exp(-r * T);
		Result[6 * NCpnInfla + 2] = NA * Result[6 * NCpnInfla + 1];
	}
	return NPV_Inflation;
}

double Pricing_TwoLeg(
	double NA,
	long NAFlag,
	long PriceDate,
	long DayCountFrac,
	long CpnFrac,

	long NAMat,
	long NCpn,
	long* StartDate,
	long* EndDate,
	long* PayDate,

	double* FixedCpn,
	long NAMatInfla,
	long RealRateProductFlag,
	long NCpnInfla,
	long* StartDateInfla,

	long* EndDateInfla,
	double* ForwardRateMultipleInfla,
	long* EstStartDate,
	long* EstEndDate,
	long* PayDateInfla,

	long* ConvincedFlag,
	double* EstStartCPI,
	double* EstEndCPI,
	double* ConvincedRate,
	long* RealRateUseFlag,

	double* RealRateMargin,
	long NRate,
	double* RateTerm,
	double* Rate,
	long PriceDateInflation,

	long NInfla,
	double* InflaTerm,
	double* InflaRate,
	double CurrentCPI,
	double* Result
)
{
	long i;
	double* ResultFix = Result + 3;
	double* ResultInflation = ResultFix + (3 * (NCpn + 1));
	double NPV_Fix, NPV_Inflation, NPV;
	NPV_Fix = FixedLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
		NAMat, NCpn, StartDate, EndDate, PayDate,
		FixedCpn, NRate, RateTerm, Rate, ResultFix);
	NPV_Inflation = InflationLeg(NA, NAFlag, PriceDate, DayCountFrac,
		NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla, EndDateInfla,
		ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla, ConvincedFlag,
		EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag, RealRateMargin,
		NRate, RateTerm, Rate, PriceDateInflation, NInfla,
		InflaTerm, InflaRate, CurrentCPI, ResultInflation);
	NPV = - NPV_Fix + NPV_Inflation;
	Result[0] = NPV;
	Result[1] = -NPV_Fix;
	Result[2] = NPV_Inflation;
	return NPV;
}

DLLEXPORT(long) InflationSwap_Pricing(
	double NA,										// Notional Amount
	long NAFlag,									// Notional Use Flag
	long PriceDate,									// PriceDate
	long DayCountFrac,								// DayCountFrac 0: Act/365, 1: Act/360, 2: Act/Act
	long CpnFrac,									// 0: Simple Interest 1: Compound Interest(1+C)^(A/B)

	long NAMat,										// Notional Maturity FixedLeg
	long NCpn,										// Number Cpn Fix
	long* StartDate,								// DayCountStartDate
	long* EndDate,									// DayCountEndDate
	long* PayDate,									// PayDate

	double* FixedCpn,								// FixedCouponRate
	long NAMatInfla,								// Notional Maturity Inflation Leg
	long RealRateProductFlag,						// RealRate Product Flag 
	long NCpnInfla,									// Number Coupon Inflation
	long* StartDateInfla,							// Inflation Leg DayCount Start if Reference Rate Coupon Plus

	long* EndDateInfla,								// Inflation Leg DayCount End If Reference Rate Coupon Plus
	double* ForwardRateMultipleInfla,				// Reference Rate Multiple (CD, Libor)
	long* EstStartDate,								// CPI Estimate Start Date
	long* EstEndDate,								// CPI Estimate End Date
	long* PayDateInfla,								// PayDate Inflation Leg

	long* ConvincedFlag,							// 1 if Reference CPI Convinced Already
	double* EstStartCPI,							// Predetermind CPI (Start)
	double* EstEndCPI,								// Predetermind CPI (End)
	double* ConvincedRate,							// Predetermind Reference Rate
	long* RealRateUseFlag,							// 1 if RealRate Margin

	double* RealRateMargin,							// RealRate Margin
	long NRate,										// Number of ZeroRate
	double* RateTerm,								// ZeroRate Term Array
	double* Rate,									// ZeroRate Array
	long PriceDateInflation,						// PriceDate of Inflation Curve

	long NInfla,									// Number of Inflation Curve Term
	double* InflaTerm,								// Inflation Curve Term
	double* InflaRate,								// Inflation Curve Zero Rate
	double CurrentCPI,								// Current CPI
	long GreekFlag,									// 1 if Using Greek

	long TextFlag,									// 1 if Using Text Dump
	double* Result,									// Result Output : Length = 3 + 3 * (NCpn + 1) + 6 * (NCpnInfla + 1)
	double* ResultGreek								// Greek Length = 3 + NZero + NInfla
)
{
	long i, j;

	double NPV;
	long ResultCode = 1;
	
	char CalcFunctionName[] = "InflationSwap_Pricing";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag > 0)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "NA", NA);
		DumppingTextData(CalcFunctionName, SaveFileName, "NAFlag", NAFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate", PriceDate); 
		DumppingTextData(CalcFunctionName, SaveFileName, "DayCountFrac", DayCountFrac);
		DumppingTextData(CalcFunctionName, SaveFileName, "CpnFrac", CpnFrac);

		DumppingTextData(CalcFunctionName, SaveFileName, "DayCountFrac", NAMat);
		DumppingTextData(CalcFunctionName, SaveFileName, "CpnFrac", NCpn);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "StartDate", NCpn, StartDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EndDate", NCpn, EndDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDate", NCpn, PayDate);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "FixedCpn", NCpn, FixedCpn);
		DumppingTextData(CalcFunctionName, SaveFileName, "NAMatInfla", NAMatInfla);
		DumppingTextData(CalcFunctionName, SaveFileName, "RealRateProductFlag", RealRateProductFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NCpnInfla", NCpnInfla);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "StartDateInfla", NCpnInfla, StartDateInfla);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EndDateInfla", NCpnInfla, EndDateInfla);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardRateMultipleInfla", NCpnInfla, ForwardRateMultipleInfla);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EstStartDate", NCpnInfla, EstStartDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EstEndDate", NCpnInfla, EstEndDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDateInfla", NCpnInfla, PayDateInfla);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ConvincedFlag", NCpnInfla, ConvincedFlag);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EstStartCPI", NCpnInfla, EstStartCPI);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "EstEndCPI", NCpnInfla, EstEndCPI);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ConvincedRate", NCpnInfla, ConvincedRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RealRateUseFlag", NCpnInfla, RealRateUseFlag);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RealRateMargin", NCpnInfla, RealRateMargin);
		DumppingTextData(CalcFunctionName, SaveFileName, "NRate", NRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateTerm", NRate, RateTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rate", NRate, Rate);
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDateInflation", PriceDateInflation);

		DumppingTextData(CalcFunctionName, SaveFileName, "NInfla", NInfla);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "InflaTerm", NInfla, InflaTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "InflaRate", NInfla, InflaRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "CurrentCPI", CurrentCPI);
		DumppingTextData(CalcFunctionName, SaveFileName, "GreekFlag", GreekFlag);

		DumppingTextData(CalcFunctionName, SaveFileName, "TextFlag", TextFlag);
	}

	if (PriceDate < 19000000) PriceDate = ExcelDateToCDate(PriceDate);
	if (NAMat < 19000000) NAMat = ExcelDateToCDate(NAMat);
	for (i = 0; i < NCpn; i++)
	{
		if (StartDate[i] < 19000000) StartDate[i] = ExcelDateToCDate(StartDate[i]);
		if (EndDate[i] < 19000000) EndDate[i] = ExcelDateToCDate(EndDate[i]);
		if (PayDate[i] < 19000000) PayDate[i] = ExcelDateToCDate(PayDate[i]);
	}

	if (NAMatInfla < 19000000) NAMatInfla = ExcelDateToCDate(NAMatInfla);
	for (i = 0; i < NCpnInfla; i++)
	{
		if (StartDateInfla != 0)
		{
			if (StartDateInfla[i] < 19000000) StartDateInfla[i] = ExcelDateToCDate(StartDateInfla[i]);
		}
		if (EndDateInfla[i] != 0)
		{
			if (EndDateInfla[i] < 19000000) EndDateInfla[i] = ExcelDateToCDate(EndDateInfla[i]);
		}
		if (EstStartDate[i] < 19000000) EstStartDate[i] = ExcelDateToCDate(EstStartDate[i]);
		if (EstEndDate[i] < 19000000) EstEndDate[i] = ExcelDateToCDate(EstEndDate[i]);
		if (PayDateInfla[i] < 19000000) PayDateInfla[i] = ExcelDateToCDate(PayDateInfla[i]);
		if (RealRateProductFlag <= 0)
		{
			RealRateUseFlag[i] = 0;
		}
	}

	if (PriceDateInflation < 19000000) PriceDateInflation = ExcelDateToCDate(PriceDateInflation);

	NPV = Pricing_TwoLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
		NAMat, NCpn, StartDate, EndDate, PayDate,
		FixedCpn, NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla,
		EndDateInfla, ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla,
		ConvincedFlag, EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag,
		RealRateMargin, NRate, RateTerm, Rate, PriceDateInflation,
		NInfla, InflaTerm, InflaRate, CurrentCPI, Result);

	if (GreekFlag == 1)
	{
		double TempNPV, NPV_Fix_Up_ParralelRate, NPV_Infla_Up_ParralelRate, NPV_Infla_Up_ParralelInfla;
		double* ResultTemp = (double*)malloc(sizeof(double) * (3 + 3 * (NCpn + 1) + 6 * (NCpnInfla + 1)));
		double* CurveParralel = (double*)malloc(sizeof(double) * NRate);
		for (i = 0; i < NRate; i++)
		{
			CurveParralel[i] = Rate[i] + 0.0001;
		}
		double* InflaCurveParralel = (double*)malloc(sizeof(double) * NInfla);
		for (i = 0; i < NInfla; i++)
		{
			InflaCurveParralel[i] = InflaRate[i] + 0.0001;
		}

		TempNPV = Pricing_TwoLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
			NAMat, NCpn, StartDate, EndDate, PayDate,
			FixedCpn, NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla,
			EndDateInfla, ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla,
			ConvincedFlag, EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag,
			RealRateMargin, NRate, RateTerm, CurveParralel, PriceDateInflation,
			NInfla, InflaTerm, InflaRate, CurrentCPI, ResultTemp);

		NPV_Fix_Up_ParralelRate = (ResultTemp[1] - Result[1]); 
		NPV_Infla_Up_ParralelRate = (ResultTemp[2] - Result[2]);

		TempNPV = Pricing_TwoLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
			NAMat, NCpn, StartDate, EndDate, PayDate,
			FixedCpn, NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla,
			EndDateInfla, ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla,
			ConvincedFlag, EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag,
			RealRateMargin, NRate, RateTerm, Rate, PriceDateInflation,
			NInfla, InflaTerm, InflaCurveParralel, CurrentCPI, ResultTemp);

		NPV_Infla_Up_ParralelInfla = (ResultTemp[2] - Result[2]);

		ResultGreek[0] = NPV_Fix_Up_ParralelRate;
		ResultGreek[1] = NPV_Infla_Up_ParralelRate;
		ResultGreek[2] = NPV_Infla_Up_ParralelInfla;

		double* CurveKeyRate = (double*)malloc(sizeof(double) * NRate);
		for (i = 0; i < NRate; i++)
		{
			for (j = 0; j < NRate; j++)
			{
				if (i == j)
				{
					CurveKeyRate[j] = Rate[j] + 0.0001;
				}
				else
				{
					CurveKeyRate[j] = Rate[j];
				}
			}

			TempNPV = Pricing_TwoLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
				NAMat, NCpn, StartDate, EndDate, PayDate,
				FixedCpn, NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla,
				EndDateInfla, ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla,
				ConvincedFlag, EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag,
				RealRateMargin, NRate, RateTerm, CurveKeyRate, PriceDateInflation,
				NInfla, InflaTerm, InflaRate, CurrentCPI, ResultTemp);

			ResultGreek[3 + i] = (ResultTemp[0] - Result[0]);
		}

		double* InflaCurveKeyRate = (double*)malloc(sizeof(double) * NInfla);
		for (i = 0; i < NInfla; i++)
		{
			for (j = 0; j < NInfla; j++)
			{
				if (i == j)
				{
					InflaCurveKeyRate[j] = InflaRate[j] + 0.0001;
				}
				else
				{
					InflaCurveKeyRate[j] = InflaRate[j];
				}
			}

			TempNPV = Pricing_TwoLeg(NA, NAFlag, PriceDate, DayCountFrac, CpnFrac,
				NAMat, NCpn, StartDate, EndDate, PayDate,
				FixedCpn, NAMatInfla, RealRateProductFlag, NCpnInfla, StartDateInfla,
				EndDateInfla, ForwardRateMultipleInfla, EstStartDate, EstEndDate, PayDateInfla,
				ConvincedFlag, EstStartCPI, EstEndCPI, ConvincedRate, RealRateUseFlag,
				RealRateMargin, NRate, RateTerm, Rate, PriceDateInflation,
				NInfla, InflaTerm, InflaCurveKeyRate, CurrentCPI, ResultTemp);

			ResultGreek[3 + NRate + i] = (ResultTemp[0] - Result[0]);
		}

		free(ResultTemp);
		free(CurveParralel);
		free(InflaCurveParralel);
		free(CurveKeyRate);
		free(InflaCurveKeyRate);

	}
	return ResultCode;
}

DLLEXPORT(long) InflationCurveGenerate(
	long PriceDate,						// 평가일
	long PriceDateInflation,			// 인플레이션 평가일
	long DayCountFrac,					// 0: Act/365 1:Act/360 2:Act/Act
	long CpnFrac,						// 0 : 단리 1: 복리
	long NInflationZC,					// 제로쿠폰개수

	long* InflationZC_StartDate,		// 제로쿠폰 StartDate
	long* InflationZC_ToMaturity_Month,	// 제로쿠폰 만기까지의 Month수
	double* InflationZC_Quote_Rate,		// 호가 이자율
	long NYOYSwap,						// YOY 스왑 개수
	long* YOYSwap_StartDate,			// YOY 스왑 StartDate

	long* YOYSwap_ToMaturity_Year,		// YOY 스왑 만기까지 년수
	double* InflationYOY_Quote_Rate,	// YOY 스왑 Rate
	long AnnCpnOneYear,					// 연 이자지급수
	long NInflationHistory,				// 과거 인플레이션 히스토리 개수
	long* InflationHistoryDate,			// 과거 인플레이션 히스토리 날짜

	double* InflationHistory,			// 과거 인플레이션
	long NationHolidayFlag,				// 0: 한국 1: 미국 2: 영국
	long Pay_NBDateAfterEndDate,		// NBDay후 지급
	double CurrentCPI,					// 현재 CPI(PriceDateInflation)
	long InflationLaggingMonth,			// Inflation Lagging Month

	long NZeroRate,
	double* ZeroTerm,
	double* ZeroRate,

	double* ResultCurveCPI,				// Length = NZC + NYOY
	double* ResultCurveRate,			// Length = NZC + NYOY
	double* ResultCurveTerm				// Length = NZC + NYOY
)
{
	long i, j, idx, k;

	long NationFlag = NationHolidayFlag;

	if (PriceDate < 19000000) PriceDate = ExcelDateToCDate(PriceDate);
	if (PriceDateInflation < 19000000) PriceDateInflation = ExcelDateToCDate(PriceDateInflation);
	
	for (i = 0; i < NInflationZC; i++)
	{
		if (InflationZC_StartDate[i] < 19000000) InflationZC_StartDate[i] = ExcelDateToCDate(InflationZC_StartDate[i]);
	}
	
	for (i = 0; i < NYOYSwap; i++)
	{
		if (YOYSwap_StartDate[i] < 19000000) YOYSwap_StartDate[i] = ExcelDateToCDate(YOYSwap_StartDate[i]);
	}
	
	for (i = 0; i < NInflationHistory; i++)
	{
		if (InflationHistoryDate[i] < 19000000) InflationHistoryDate[i] = ExcelDateToCDate(InflationHistoryDate[i]);
	}

	long PriceDateInfla = PriceDateInflation;
	double deltat, CPI_T, CPI_0, TEND, r_zc_infla;
	double dblErrorRange = 0.0000001;
	double ObjValue = 0.0;
	double MaxRate;
	double MinRate;
	double TargetRate;
	double tau, t;
	double* ZeroRateTermTemp;
	double* ZeroRateTemp;
	if (NZeroRate == 0)
	{
		NZeroRate = 1;
		double ZeroRateTermTemp2[1] = { 1.0 };
		double ZeroRateTemp2[1] = { 0.01 };
		ZeroRateTermTemp = ZeroRateTermTemp2;
		ZeroRateTemp = ZeroRateTemp2;
	}
	else
	{
		ZeroRateTermTemp = ZeroTerm; 
		ZeroRateTemp = ZeroRate;
	}

	long* InflationZC_Maturity = (long*)malloc(sizeof(long) * NInflationZC);						// 할당 1 InflationZC_Maturity
	for (i = 0; i < NInflationZC; i++) InflationZC_Maturity[i] = EDate_Cpp(InflationZC_StartDate[i], InflationZC_ToMaturity_Month[i]);

	long* YOYSwap_Maturity = (long*)malloc(sizeof(long) * max(1, NYOYSwap));								// 할당 2 YOYSwap_Maturity
	for (i = 0; i < NYOYSwap; i++) YOYSwap_Maturity[i] = YOYSwap_StartDate[i] + YOYSwap_ToMaturity_Year[i] * 10000;

	double* TempResultArray;  

	long Number_Cpn_Swap = 0;
	long HolidayUseFlag = 0;
	if (NationFlag > 0 && NationFlag < 3) HolidayUseFlag = 1;
	if (InflationLaggingMonth > 0) InflationLaggingMonth = -InflationLaggingMonth;

	long HolidayEndDate = PriceDate + 51 * 10000;
	long StartYYYYHoliday = PriceDate / 10000;
	long EndYYYYHoliday = HolidayEndDate / 10000;
	long NHoliday = Number_Holiday(StartYYYYHoliday, EndYYYYHoliday, NationFlag);
	long* Holiday = (long*)malloc(sizeof(long) * NHoliday);											// 할당 3 Holiday

	Mapping_Holiday_CType(StartYYYYHoliday, EndYYYYHoliday, NationFlag, NHoliday, Holiday);

	long** ResultForwardStartDateZC_Fix = (long**)malloc(sizeof(long*) * NInflationZC);				// 할당 4 ResultForwardStartDateZC_Fix
	long** ResultForwardEndDateZC_Fix = (long**)malloc(sizeof(long*) * NInflationZC);				// 할당 5 ResultForwardEndDateZC_Fix
	long** ResultPayDateZC_Fix = (long**)malloc(sizeof(long*) * NInflationZC);						// 할당 6 ResultPayDateZC_Fix
	long** ResultForwardStartDateZC_Flo = (long**)malloc(sizeof(long*) * NInflationZC);				// 할당 7 ResultForwardStartDateZC_Flo
	long** ResultForwardEndDateZC_Flo = (long**)malloc(sizeof(long*) * NInflationZC);				// 할당 8 ResultForwardEndDateZC_Flo
	long** ResultPayDateZC_Flo = (long**)malloc(sizeof(long*) * NInflationZC);						// 할당 9 ResultPayDateZC_Flo
	long** ConvincedFlag = (long**)malloc(sizeof(long*) * NInflationZC);							// 할당 10 ConvincedFlag
	long** TempStartDate = ResultForwardStartDateZC_Fix;										
	long** TempEndDate = ResultForwardEndDateZC_Fix;
	double** ForwardRateMultiple = (double**)malloc(sizeof(double*) * NInflationZC);				// 할당 11 ForwardRateMultiple
	double** EstStartCPI = (double**)malloc(sizeof(double*) * NInflationZC);						// 할당 12 EstStartCPI
	double** EstEndCPI = (double**)malloc(sizeof(double*) * NInflationZC);							// 할당 13 EstEndCPI
	double** TempDoubleTwo = EstStartCPI;
	long EstStart, EstEnd;

	k = 0;
	for (i = 0; i < NInflationZC; i++)
	{
		Number_Cpn_Swap = 1; 
		ResultForwardStartDateZC_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultForwardEndDateZC_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultPayDateZC_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultForwardStartDateZC_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultForwardEndDateZC_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultPayDateZC_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ForwardRateMultiple[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		ConvincedFlag[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		EstStartCPI[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		EstEndCPI[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);

		ResultCpnMappingCDate(0, PriceDate, InflationZC_StartDate[i], InflationZC_Maturity[i],
								Pay_NBDateAfterEndDate, 1, HolidayUseFlag, NHoliday, Holiday, 
								1, ResultForwardStartDateZC_Fix[i], ResultForwardEndDateZC_Fix[i], ResultPayDateZC_Fix[i]);
		
		for (j = 0; j < Number_Cpn_Swap; j++)
		{
			ResultForwardStartDateZC_Flo[i][j] = (EDate_Cpp(ResultForwardStartDateZC_Fix[i][j], InflationLaggingMonth) / 100) * 100 + 01;
			ResultForwardEndDateZC_Flo[i][j] = (EDate_Cpp(ResultForwardEndDateZC_Fix[i][j], InflationLaggingMonth) / 100) * 100 + 01;
			ResultPayDateZC_Flo[i][j] = ResultPayDateZC_Fix[i][j];

			if (ResultForwardStartDateZC_Flo[i][j] < PriceDateInfla)
			{
				ConvincedFlag[i][j] = 1;
				idx = isinfindindex(ResultForwardStartDateZC_Flo[i][j], InflationHistoryDate, NInflationHistory);
				
				if (idx >= 0) EstStartCPI[i][j] = InflationHistory[idx];
				else EstStartCPI[i][j] = 0.;

				if (ResultForwardEndDateZC_Flo[i][j] < PriceDateInfla)
				{
					idx = isinfindindex(ResultForwardEndDateZC_Flo[i][j], InflationHistoryDate, NInflationHistory);
					if (idx >= 0) EstEndCPI[i][j] = InflationHistory[idx];
					else EstEndCPI[i][j] = 0.;
				}
				else if (ResultForwardEndDateZC_Flo[i][j] == PriceDateInfla)
				{
					EstEndCPI[i][j] = CurrentCPI;
				}
				else
				{
					EstEndCPI[i][j] = 0.;
				}
			}
			else if (ResultForwardStartDateZC_Flo[i][j] == PriceDateInfla)
			{
				EstStartCPI[i][j] = CurrentCPI;
				EstEndCPI[i][j] = 0.;
			}
			else
			{
				ConvincedFlag[i][j] = 0;
				EstStartCPI[i][j] = 0.;
				EstEndCPI[i][j] = 0.;
			}

			deltat = DayCountFraction(ResultForwardStartDateZC_Fix[i][0], ResultForwardEndDateZC_Fix[i][0], DayCountFrac);

			if (EstStartCPI[i][0] > 0.) CPI_0 = EstStartCPI[i][0];
			else EstStartCPI[i][0] = CurrentCPI;

			if (CpnFrac == 1) CPI_T = CPI_0 * pow(1.0 + InflationZC_Quote_Rate[i], deltat);
			else CPI_T = CPI_0 * (1.0 + InflationZC_Quote_Rate[i] * deltat);

			TEND = DayCountAtoB(PriceDateInflation, ResultForwardEndDateZC_Flo[i][0]) / 365.0;
			r_zc_infla = 1.0 / TEND * log(CPI_T / CurrentCPI);

			ResultCurveCPI[i] = CPI_T;
			ResultCurveRate[i] = r_zc_infla;
			ResultCurveTerm[i] = TEND;
		}	
		k += 1;
	}
	
	long* NumberofCpn_Swap = (long*)malloc(sizeof(long) * max(1, NYOYSwap));								// 할당 14 NumberofCpn_Swap
	long** ResultForwardStartDateYOY_Fix = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));				// 할당 15 ResultForwardStartDateYOY_Fix
	long** ResultForwardEndDateYOY_Fix = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));					// 할당 16 ResultForwardEndDateYOY_Fix
	long** ResultPayDateYOY_Fix = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));							// 할당 17 ResultPayDateYOY_Fix
	long** ResultForwardStartDateYOY_Flo = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));				// 할당 18 ResultForwardStartDateYOY_Flo
	long** ResultForwardEndDateYOY_Flo = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));					// 할당 19 ResultForwardEndDateYOY_Flo
	long** ResultPayDateYOY_Flo = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));							// 할당 20 ResultPayDateYOY_Flo
	long** ConvincedFlagYOY = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));								// 할당 21 ConvincedFlagYOY
	long** TempStartDateYOY = ResultForwardStartDateYOY_Fix;					
	long** TempEndDateYOY = ResultForwardEndDateYOY_Fix;
	long** RealRateUseFlag = (long**)malloc(sizeof(long*) * max(1, NYOYSwap));								// 할당 22 RealRateUseFlag
	double** FixedCpnRateYOY = (double**)malloc(sizeof(double*) * max(1, NYOYSwap));						// 할당 23 FixedCpnRateYOY
	double** ForwardRateMultipleYOY = (double**)malloc(sizeof(double*) * max(1, NYOYSwap));					// 할당 24 ForwardRateMultipleYOY
	double** EstStartCPIYOY = (double**)malloc(sizeof(double*) * max(1, NYOYSwap));							// 할당 25 EstStartCPIYOY
	double** EstEndCPIYOY = (double**)malloc(sizeof(double*) * max(1, NYOYSwap));							// 할당 26 EstStartCPIYOY
	double** TempDoubleTwoYOY = (double**)malloc(sizeof(double*) * max(1, NYOYSwap));						// 할당 27 TempDoubleTwoYOY
	for (i = 0; i < NYOYSwap; i++)
	{
		Number_Cpn_Swap = Number_Coupon_CDate(1, PriceDate, YOYSwap_Maturity[i], AnnCpnOneYear, HolidayUseFlag, NHoliday, Holiday);
		NumberofCpn_Swap[i] = Number_Cpn_Swap;

		RealRateUseFlag[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);

		ResultForwardStartDateYOY_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultForwardEndDateYOY_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultPayDateYOY_Fix[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);

		ResultForwardStartDateYOY_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultForwardEndDateYOY_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		ResultPayDateYOY_Flo[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		
		FixedCpnRateYOY[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		ForwardRateMultipleYOY[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		ConvincedFlagYOY[i] = (long*)malloc(sizeof(long) * Number_Cpn_Swap);
		EstStartCPIYOY[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		EstEndCPIYOY[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);
		TempDoubleTwoYOY[i] = (double*)malloc(sizeof(double) * Number_Cpn_Swap);

		ResultCpnMappingCDate(1, PriceDate, YOYSwap_StartDate[i], YOYSwap_Maturity[i],
			Pay_NBDateAfterEndDate, AnnCpnOneYear, HolidayUseFlag, NHoliday, Holiday,
			Number_Cpn_Swap, ResultForwardStartDateYOY_Fix[i], ResultForwardEndDateYOY_Fix[i], ResultPayDateYOY_Fix[i]);
		for (j = 0; j < Number_Cpn_Swap; j++)
		{
			FixedCpnRateYOY[i][j] = InflationYOY_Quote_Rate[i];
			ForwardRateMultipleYOY[i][j] = 0.;
			RealRateUseFlag[i][j] = 0;
			TempDoubleTwoYOY[i][j] = 0.;

			ResultForwardStartDateYOY_Flo[i][j] = (EDate_Cpp(ResultForwardStartDateYOY_Fix[i][j], InflationLaggingMonth) / 100) * 100 + 01;
			ResultForwardEndDateYOY_Flo[i][j] = (EDate_Cpp(ResultForwardEndDateYOY_Fix[i][j], InflationLaggingMonth) / 100) * 100 + 01;
			ResultPayDateYOY_Flo[i][j] = ResultPayDateYOY_Fix[i][j];

			if (ResultForwardStartDateYOY_Flo[i][j] < PriceDateInfla)
			{
				ConvincedFlagYOY[i][j] = 1;
				idx = isinfindindex(ResultForwardStartDateYOY_Flo[i][j], InflationHistoryDate, NInflationHistory);

				if (idx >= 0) EstStartCPIYOY[i][j] = InflationHistory[idx];
				else EstStartCPIYOY[i][j] = 0.;

				if (ResultForwardEndDateYOY_Flo[i][j] < PriceDateInfla)
				{
					idx = isinfindindex(ResultForwardEndDateYOY_Flo[i][j], InflationHistoryDate, NInflationHistory);
					if (idx >= 0) EstEndCPIYOY[i][j] = InflationHistory[idx];
					else EstEndCPIYOY[i][j] = 0.;
				}
				else if (ResultForwardEndDateYOY_Flo[i][j] == PriceDateInfla)
				{
					EstEndCPIYOY[i][j] = CurrentCPI;
				}
				else
				{
					EstEndCPIYOY[i][j] = 0.;
				}
			}
			else if (ResultForwardStartDateYOY_Flo[i][j] == PriceDateInfla)
			{
				ConvincedFlagYOY[i][j] = 0;
				EstStartCPIYOY[i][j] = CurrentCPI;
				EstEndCPIYOY[i][j] = 0.;
			}
			else
			{
				ConvincedFlagYOY[i][j] = 0;
				EstStartCPIYOY[i][j] = 0.;
				EstEndCPIYOY[i][j] = 0.;
			}
		}
	}
	double PrevRate ,CalcRate;
	double* Rate;
	double* Term;
	long NAMat;
	long NResultArrayTemp;
	for (i = 0; i < NYOYSwap; i++)
	{
		if (YOYSwap_Maturity[i] > PriceDate)
		{
			NAMat = ResultPayDateYOY_Fix[i][max(0, NumberofCpn_Swap[i] - 1)];
			tau = (double)(DayCountAtoB(PriceDate, ResultForwardEndDateYOY_Flo[i][max(0,NumberofCpn_Swap[i] - 1)]));
			t = tau / 365.0;

			MaxRate = InflationYOY_Quote_Rate[i] + 0.25;
			MinRate = InflationYOY_Quote_Rate[i] - 0.15;
			TargetRate = MaxRate;

			NResultArrayTemp = (3 + 3 * (NumberofCpn_Swap[i] + 1) + 6 * (NumberofCpn_Swap[i] + 1));

			Rate = (double*)malloc(sizeof(double) * (k + 1));						// 반복문내 할당 1
			Term = (double*)malloc(sizeof(double) * (k + 1));						// 반복문내 할당 2
			TempResultArray = (double*)malloc(sizeof(double) * NResultArrayTemp);	// 반복문내 할당 3
			PrevRate = MaxRate;

			for (j = 0; j < k; j++)
			{
				Rate[j] = ResultCurveRate[j];
				Term[j] = ResultCurveTerm[j];
			}
			Term[k] = t;

			for (j = 0; j < 1000; j++)
			{
				Rate[k] = TargetRate;

				CalcRate = Pricing_TwoLeg(100.0, 0, PriceDate, DayCountFrac, CpnFrac,
										NAMat, NumberofCpn_Swap[i], ResultForwardStartDateYOY_Fix[i], ResultForwardEndDateYOY_Fix[i], ResultPayDateYOY_Fix[i],
										FixedCpnRateYOY[i], NAMat, 0, NumberofCpn_Swap[i], ResultForwardStartDateYOY_Flo[i],
										ResultForwardEndDateYOY_Flo[i], ForwardRateMultipleYOY[i], ResultForwardStartDateYOY_Flo[i], ResultForwardEndDateYOY_Flo[i], ResultPayDateYOY_Flo[i],
										ConvincedFlagYOY[i], EstStartCPIYOY[i], EstEndCPIYOY[i], TempDoubleTwoYOY[i], RealRateUseFlag[i],
										TempDoubleTwoYOY[i], NZeroRate, ZeroRateTermTemp, ZeroRateTemp, PriceDateInfla, k + 1, Term, Rate, CurrentCPI, TempResultArray);
				
				if (fabs(CalcRate) < dblErrorRange) break;
				if (CalcRate > 0.)
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

			free(TempResultArray);
			free(Rate);
			free(Term);

			ResultCurveRate[k] = TargetRate;
			ResultCurveTerm[k] = (double)(DayCountAtoB(PriceDateInflation, ResultForwardEndDateYOY_Flo[i][max(0, NumberofCpn_Swap[i] - 1)])) / 365.0;
			ResultCurveCPI[k] = CurrentCPI*exp(TargetRate * ResultCurveTerm[k]);

			k++;
		}
	}


	free(InflationZC_Maturity);							// 할당 1
	free(YOYSwap_Maturity);								// 할당 2

	free(Holiday);										// 할당 3
	for (i = 0; i < NInflationZC; i++)
	{
		free(ResultForwardStartDateZC_Fix[i]);
		free(ResultForwardEndDateZC_Fix[i]);
		free(ResultPayDateZC_Fix[i]);
	}
	free(ResultForwardStartDateZC_Fix);					// 할당 4
	free(ResultForwardEndDateZC_Fix);					// 할당 5
	free(ResultPayDateZC_Fix);							// 할당 6

	for (i = 0; i < NInflationZC; i++)
	{
		free(ResultForwardStartDateZC_Flo[i]);
		free(ResultForwardEndDateZC_Flo[i]);
		free(ResultPayDateZC_Flo[i]);
		free(ForwardRateMultiple[i]);
		free(ConvincedFlag[i]);
		free(EstStartCPI[i]);
		free(EstEndCPI[i]);
	}
	free(ResultForwardStartDateZC_Flo);					// 할당 7
	free(ResultForwardEndDateZC_Flo);					// 할당 8
	free(ResultPayDateZC_Flo);							// 할당 9
	free(ConvincedFlag);								// 할당 10
	free(ForwardRateMultiple);							// 할당 11
	free(EstStartCPI);									// 할당 12
	free(EstEndCPI);									// 할당 13

	free(NumberofCpn_Swap);								// 할당 14
	for (i = 0; i < NYOYSwap; i++)
	{
		free(ResultForwardStartDateYOY_Fix[i]);
		free(ResultForwardEndDateYOY_Fix[i]);
		free(ResultPayDateYOY_Fix[i]);
		free(ResultForwardStartDateYOY_Flo[i]);
		free(ResultForwardEndDateYOY_Flo[i]);
		free(ResultPayDateYOY_Flo[i]);
		free(ConvincedFlagYOY[i]);

		free(RealRateUseFlag[i]);
		free(FixedCpnRateYOY[i]);
		free(ForwardRateMultipleYOY[i]);
		free(EstStartCPIYOY[i]);
		free(EstEndCPIYOY[i]);
		free(TempDoubleTwoYOY[i]);
	}
	free(ResultForwardStartDateYOY_Fix);				// 할당 15
	free(ResultForwardEndDateYOY_Fix);					// 할당 16
	free(ResultPayDateYOY_Fix);							// 할당 17
	free(ResultForwardStartDateYOY_Flo);				// 할당 18
	free(ResultForwardEndDateYOY_Flo);					// 할당 19
	free(ResultPayDateYOY_Flo);							// 할당 20
	free(ConvincedFlagYOY);								// 할당 21

	free(RealRateUseFlag);								// 할당 22
	free(FixedCpnRateYOY);								// 할당 23
	free(ForwardRateMultipleYOY);						// 할당 24
	free(EstStartCPIYOY);								// 할당 25
	free(EstEndCPIYOY);									// 할당 26
	free(TempDoubleTwoYOY);								// 할당 27

	//_CrtDumpMemoryLeaks();
	return 1;
}


/*
int main()
{

	long DayCountFrac = 2;
	long CpnFrac = 1;

	long NInflationHistory = 2;
	long InflationHistoryDate[2] = { 20230101, 20230501 };
	double InflationHistory[2] = { 365.12, 373.0 };

	long InflationLaggingMonth = -2;
	long PriceDate = 20230710;
	long PriceDateInfla = 20230710;
	double CurrentCPI = 375.51;

	long NationFlag = 2;
	long Pay_NBDateAfterEndDate = 2;

	long NInflationZC = 2;
	long InflationZC_StartDate[2] = { 20230715, 20230715 };
	long InflationZC_ToMaturity_Month[2] = { 6, 12 };
	double InflationZC_Quote_Rate[2] = { 0.034, 0.044 };

	long NYOYSwap = 4;
	long YOYSwap_StartDate[4] = { 20230715, 20230715, 20230715 , 20230715 };
	long YOYSwap_ToMaturity_Year[4] = { 2, 3, 4 , 5 };
	double InflationYOY_Quote_Rate[4] = { 0.045, 0.042, 0.039, 0.038 };
	long AnnCpnOneYear = 1;

	double ResultCurveCPI[6] = { 0. , };
	double ResultCurveRate[6] = { 0. , };
	double ResultCurveTerm[6] = { 0., };


	long ResultCode;
	
	ResultCode = InflationCurveGenerate(PriceDate, PriceDateInfla, DayCountFrac, CpnFrac, NInflationZC,
		InflationZC_StartDate, InflationZC_ToMaturity_Month, InflationZC_Quote_Rate, NYOYSwap, YOYSwap_StartDate,
		YOYSwap_ToMaturity_Year, InflationYOY_Quote_Rate, AnnCpnOneYear, NInflationHistory, InflationHistoryDate,
		InflationHistory, NationFlag, Pay_NBDateAfterEndDate, CurrentCPI, InflationLaggingMonth,
		ResultCurveCPI, ResultCurveRate, ResultCurveTerm);
}*/