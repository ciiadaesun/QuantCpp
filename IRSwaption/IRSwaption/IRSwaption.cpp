#include <math.h>
#include <stdio.h>
#include <string.h>
#include "GetTextDump.h"

#ifndef UTILITY
#include "Util.h"
#endif

#ifndef DateFunction
#include "CalcDate.h"
#endif 
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

double DayCountFrc(long Day1, long Day2, long Flag)
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
		long DayA, DayB;
		long CurrentY;
		long NextY;

		YearA = Day1 / 10000;
		MonthA = (Day1 - YearA * 10000) / 100;
		DayA = (Day1 - YearA * 10000 - MonthA * 100);

		YearB = Day2 / 10000;
		MonthB = (Day2 - YearB * 10000) / 100;
		DayB = (Day2 - YearB * 10000 - MonthB * 100);
		return ((double)((YearB - YearA) * 12 + (MonthB - MonthA))) * 30.0 / 360.0;
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

long* Generate_CpnDate_Holiday_IRSwaption(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
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

double ForwardSwapRate(
	long PriceDate,
	long StartDate,
	long NCpn,
	long* SwapDate,
	long Fix_NTerm,
	double* Fix_Term,
	double* Fix_Rate,
	long Est_NTerm,
	double* Est_Term,
	double* Est_Rate,
	long DayCountFracFlag
)
{
	long i;
	double t0 ,dt, t_pay, t1, t2;
	double a, b, f, p;
	a = 0.0;

	for (i = 0; i < NCpn; i++)
	{
		if (i == 0)
		{
			t1 = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.0;
			t2 = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		}
		else
		{
			t1 = ((double)DayCountAtoB(PriceDate, SwapDate[i-1])) / 365.0;
			t2 = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		}

		if (i == 0)
		{
			dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		}
		else
		{
			dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		}

		f = Calc_Forward_Rate(Est_Term, Est_Rate, Est_NTerm, t1, t2);
		t_pay = t2;
		p = Calc_Discount_Factor(Fix_Term, Fix_Rate, Fix_NTerm, t_pay);
		a += f * dt * p;
	}

	b = 0.0;
	for (i = 0; i < NCpn; i++)
	{
		if (i == 0)
		{
			dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		}
		else
		{
			dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		}
		t_pay = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		p = Calc_Discount_Factor(Fix_Term, Fix_Rate, Fix_NTerm, t_pay);
		b += dt * p;
	}
	return a / b;
}

double BS_Swaption(
	long PriceDate,
	long StartDate,
	long NCpn,
	long* SwapDate,
	double NA,
	double Vol,
	double StrikePrice,
	double* Term,
	double* Rate,
	long NTerm,
	long DayCountFracFlag,
	long VolFlag,
	long PricingOrValueFlag,
	double &ResultForwardSwapRate
)
{
	long i;
	double FSR;

	double T_Option = ((double)DayCountAtoB(PriceDate, StartDate))/365.0;
	double dt, t_pay, value, d1, d2, value_atm , d1_atm, d2_atm;
	double annuity = 0.0;
	FSR = ForwardSwapRate(PriceDate, StartDate, NCpn, SwapDate, NTerm, Term, Rate, NTerm, Term, Rate, DayCountFracFlag);
	ResultForwardSwapRate = FSR;

	for (i = 0; i < NCpn; i++)
	{
		if (i == 0)
		{
			dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		}
		else
		{
			dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		}
		t_pay = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		annuity += dt * Calc_Discount_Factor(Term, Rate, NTerm, t_pay);
	}

	value = 0.0;
	value_atm = 0.0;
	if (VolFlag == 0)
	{
		d1 = (log(FSR / StrikePrice) + 0.5 * Vol * Vol * T_Option) / (Vol * sqrt(T_Option));
		d2 = d1 - Vol * sqrt(T_Option);

		d1_atm = 0.5 * Vol * sqrt(T_Option);
		d2_atm = -0.5 * Vol * sqrt(T_Option);

		value = annuity * (FSR * CDF_N(d1) - StrikePrice * CDF_N(d2));
		value_atm = annuity * (FSR * CDF_N(d1_atm) - FSR * CDF_N(d2_atm));
	}
	else
	{
		d1 = (FSR - StrikePrice) / (Vol * sqrt(T_Option));

		value = annuity * ((FSR - StrikePrice) * CDF_N(d1) + Vol * sqrt(T_Option) * (exp(-d1 * d1 / 2.0) / 2.506628274631));
		value_atm = annuity * (Vol * sqrt(T_Option)  / 2.506628274631);
	}
	if (PricingOrValueFlag == 0) return NA * value;
	else return NA * (value - value_atm);
}

DLLEXPORT(long) Pricing_BS_Swaption(
	long PriceDate,				// 평가일
	long StartDate,				// 옵션시작일
	long SwapMaturityDate,		// 스왑 만기 YYYYMMDD
	long AnnCpnOneYear,			// 연 이자지급수
	long PricingOrValueFlag,	// 0: Pricing , 1: Valuation
	double NA,					// 명목원금
	double Vol,					// 변동성
	double StrikePrice,			// 행사금리
	long NTerm,					// 금리 Term 개수
	double* Term,				// 금리 Term Array
	double* Rate,				// 금리 Rate Array
	long DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
	long VolFlag,				// 0: Black Vol 1: Normal Vol
	long HolidayAutoFlag,		// Holiday 자동계산
	long HolidayNationFlag,		// Holiday 자동계산 1일 때, 0: KRW, 1:USD, 2:GBP
	long NHoliday,				// Holiday 수동계산일 때 Holiday개수
	long* HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
	long TextFlag,				// LoggingFlag
	long GreekFlag,				// Greek 계산여부
	double *ResultValue			// Output : 길이 = 2 + NTerm
)
{	
	long i, j;
	double swv;
	long ResultCode = 0;

	long NHolidayInput = 0;
	long* HolidayInput;
	if (HolidayAutoFlag == 0)
	{
		NHolidayInput = NHoliday;
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		for (i = 0; i < NHoliday; i++) HolidayInput[i] = HolidayYYYYMMDD[i];
	}
	else
	{
		NHolidayInput = Number_Holiday(PriceDate / 10000,				// 시작연도
									SwapMaturityDate / 10000,           // 종료연도
									HolidayNationFlag					// 0: KRW한국, 1: USD미국, 2: GBP영국
		);
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		ResultCode = Mapping_Holiday_CType(
			PriceDate / 10000,				// 시작연도
			SwapMaturityDate / 10000,       // 종료연도
			HolidayNationFlag,				// 국가Flag 0한국 1미국 2영국
			NHolidayInput,					// 배열 개수 Number_Holiday에서 확인
			HolidayInput					// Holiday 들어가는 배열
		);
		for (i = 0; i < min(NHoliday, NHolidayInput); i++) HolidayYYYYMMDD[i] = HolidayInput[i];
	}

	char CalcFunctionName[] = "Pricing_BS_Swaption";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag > 0)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate", PriceDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "StartDate", StartDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "SwapMaturityDate", SwapMaturityDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "AnnCpnOneYear", AnnCpnOneYear);
		DumppingTextData(CalcFunctionName, SaveFileName, "PricingOrValueFlag", PricingOrValueFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NA", NA);

		DumppingTextData(CalcFunctionName, SaveFileName, "Vol", Vol);
		DumppingTextData(CalcFunctionName, SaveFileName, "StrikePrice", StrikePrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "NTerm", NTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Term", NTerm, Term);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Term", NTerm, Rate);

		DumppingTextData(CalcFunctionName, SaveFileName, "DayCountFracFlag", DayCountFracFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "VolFlag", VolFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "HolidayAutoFlag", HolidayAutoFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "HolidayNationFlag", HolidayNationFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NHolidayInput", NHolidayInput);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "HolidayInput", NHolidayInput, HolidayInput);
	}

	long Year = StartDate / 10000;
	long Year2 = SwapMaturityDate / 10000;

	long Month = (StartDate - Year * 10000) / 100;
	long Day = (StartDate - Year * 10000 - Month * 100);
	
	long TargetMat = Year2 * 10000 + Month * 100 + Day;

	long nCpnDates = 0;
	long TempDate = StartDate;
	long* CpnDates = Generate_CpnDate_Holiday_IRSwaption(StartDate, TargetMat, AnnCpnOneYear, nCpnDates, StartDate, NHoliday, HolidayYYYYMMDD);

	double* ResultFSR = ResultValue + 2;

	swv = BS_Swaption(PriceDate, StartDate, nCpnDates, CpnDates, NA, Vol, StrikePrice, Term, Rate, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag , *ResultFSR);
	
	double* Value = ResultValue;
	double* PV01_Curve = ResultValue + 1;
	
	double* KeyRatePV01_Curve = ResultValue + 3;
	Value[0] = swv;
	if (GreekFlag > 0)
	{
		double TempFSR = 0.0;
		double* RateForGreek = (double*)malloc(sizeof(double) * NTerm);
		for (i = 0; i < NTerm; i++) RateForGreek[i] = Rate[i] + 0.0001;
		PV01_Curve[0] = BS_Swaption(PriceDate, StartDate, nCpnDates, CpnDates, NA, Vol, StrikePrice, Term, RateForGreek, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, TempFSR) - swv;

		for (i = 0; i < NTerm; i++)
		{
			for (j = 0; j < NTerm; j++)
			{
				if (i == j) RateForGreek[j] = Rate[j] + 0.0001;
				else RateForGreek[j] = Rate[j];
			}
			KeyRatePV01_Curve[i] = BS_Swaption(PriceDate, StartDate, nCpnDates, CpnDates, NA, Vol, StrikePrice, Term, RateForGreek, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, TempFSR) - swv;
		}

		free(RateForGreek);
	}
	free(HolidayInput);
	free(CpnDates);
	return 1;
}
