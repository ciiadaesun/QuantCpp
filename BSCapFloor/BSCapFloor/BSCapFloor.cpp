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

long* Generate_CpnDate_Holiday_CapFloor(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
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
				// Forward End ��¥�� ����� �Ǵ� �Ͽ����� ��� ��¥ �̷�
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
	long NCpnDate,
	long* SwapDate,
	long Disc_NTerm,
	double* Disc_Term,
	double* Disc_Rate,
	long Est_NTerm,
	double* Est_Term,
	double* Est_Rate,
	long DayCountFracFlag,
	double FirstFixingRate
)
{
	long i;
	long n;
	double F;
	double Swap_Rate;

	double t = 0.0;
	t = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.0;
	double* P0T = (double*)malloc(sizeof(double) * (NCpnDate + 1));
	P0T[0] = Calc_Discount_Factor(Est_Term, Est_Rate, Est_NTerm, t);
	for (i = 1; i < NCpnDate + 1; i++)
	{
		t = ((double)DayCountAtoB(PriceDate, SwapDate[i - 1])) / 365.0;
		P0T[i] = Calc_Discount_Factor(Est_Term, Est_Rate, Est_NTerm, t);
	}

	double a, b, dt;
	a = 0.;
	for (i = 1; i < NCpnDate + 1; i++)
	{
		t = ((double)DayCountAtoB(PriceDate, SwapDate[i-1])) / 365.0;

		if (i == 1) dt = DayCountFrc(StartDate, SwapDate[i-1], DayCountFracFlag);
		else dt = DayCountFrc(SwapDate[i - 2], SwapDate[i - 1], DayCountFracFlag);

		if (i == 1 && (FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001))
		{
			F = FirstFixingRate;
		}
		else
		{
			F = (P0T[i - 1] / P0T[i] - 1.0) / dt;
		}

		a += dt * F * Calc_Discount_Factor(Disc_Term, Disc_Rate, Disc_NTerm, t);
	}

	b = 0.0;
	for (i = 0; i < NCpnDate; i++)
	{
		t = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;

		if (i == 0) dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		else dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		b += dt * Calc_Discount_Factor(Disc_Term, Disc_Rate, Disc_NTerm, t);
	}
	Swap_Rate = a / b;

	if (P0T) free(P0T);
	return Swap_Rate;
}

double _stdcall BS_Cap(
	double NA,			// �׸�ݾ�
	long VolFlag,		// 0 : Black Vol 1 : Normal Vol
	double Vol,			// ������
	double* DF,			// OptionDate ~ Cap������� ���ΰ�� = NCaplet + 1
	double StrikeRate,	// ���ݸ�
	long* Dates,		// �� �����ϱ����� �ϼ�
	long nDates,		// ���� ȸ��
	long FirstStartDay,
	double FirstFixingRate,
	long AverageFlag,
	double* deltat,
	long AllStrikeATMFlag,
	double swaprate
)
{
	long i;
	double d1, d2, PrevT, T, delta;
	double PrevDisc, Disc;
	double F, value;

	PrevT = ((double)FirstStartDay)/365.;
	value = 0.0;
	if (AverageFlag == 0)
	{
		if (VolFlag == 0)
		{
			for (i = 0; i < nDates; i++) {
				T = ((double)Dates[i]) / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				F = (PrevDisc / Disc - 1.0) / delta;			// �����ݸ�
				if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001)&& i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

				if (i == 0)
				{
					if (PrevT <= 0.)
					{
						if (F > StrikeRate)
						{
							value = deltat[i] * Disc * (F - StrikeRate);
						}
					}
					else
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (log(F / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2));
					}
				}
				else {
					if (F > 0.)
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (log(F / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2));
					}
					else value += 1.e-13;
				}

				PrevT = T;
			}
		}
		else if (VolFlag == 1)
		{
			for (i = 0; i < nDates; i++) {
				T = (double)Dates[i] / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				F = (PrevDisc / Disc - 1.0) / delta;		// �����ݸ�
				if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) && i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

				if (i == 0)
				{	// ù��° ������ 
					if (PrevT <= 0.)
					{
						if (F > StrikeRate)
						{
							value = deltat[i] * Disc * (F - StrikeRate);
						}
					}
					else
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (F - StrikeRate) / (Vol * sqrt(PrevT));
						value += deltat[i] * Disc * ((F - StrikeRate) * CDF_N(d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
					}
				}
				else {
					if (AllStrikeATMFlag == 1) StrikeRate = F;
					else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
					d1 = (F - StrikeRate) / (Vol * sqrt(PrevT));
					value += deltat[i] * Disc * ((F - StrikeRate) * CDF_N(d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
				}
				PrevT = T;
			}
		}
	}
	else
	{
		double F_Avg = 0.;
		for (i = 0; i < nDates; i++)
		{
			T = ((double)Dates[i]) / 365.0;
			delta = T - PrevT;

			PrevDisc = DF[i];
			Disc = DF[i + 1];

			F = (PrevDisc / Disc - 1.0) / delta;			// �����ݸ�
			if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) && i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

			F_Avg += F / ((double)nDates);
			PrevT = T;
		}
		
		if (VolFlag == 0)
		{
			PrevT = ((double)FirstStartDay) / 365.;
			for (i = 0; i < nDates; i++)
			{
				T = ((double)Dates[i]) / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				if (i == 0)
				{
					if (PrevT <= 0.) if (F_Avg > StrikeRate) value = deltat[i] * Disc * (F_Avg - StrikeRate);
					else
					{
						d1 = (log(F_Avg / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2));
					}
				}
				else {
					if (F_Avg > 0.)
					{
						d1 = (log(F_Avg / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2));
					}
					else value += 1.e-13;
				}

				PrevT = T;
			}
		}
		else
		{
			PrevT = ((double)FirstStartDay) / 365.;
			for (i = 0; i < nDates; i++) {
				T = (double)Dates[i] / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				if (i == 0)
				{	// ù��° ������ 
					if (PrevT <= 0.) if (F_Avg > StrikeRate) value = deltat[i] * Disc * (F_Avg - StrikeRate);
					else
					{
						d1 = (F_Avg - StrikeRate) / (Vol * sqrt(PrevT));
						value += deltat[i] * Disc * ((F_Avg - StrikeRate) * CDF_N(d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
					}
				}
				else {

					d1 = (F_Avg - StrikeRate) / (Vol * sqrt(PrevT));
					value += deltat[i] * Disc * ((F_Avg - StrikeRate) * CDF_N(d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
				}
				PrevT = T;
			}
		}
	}

	return NA * value;
}

double _stdcall BS_Floor(
	double NA,			// �׸�ݾ�
	long VolFlag,		// 0 : Black Vol 1 : Normal Vol
	double Vol,			// ������
	double* DF,			// OptionDate ~ Cap������� ���ΰ�� = NCaplet + 1
	double StrikeRate,	// ���ݸ�
	long* Dates,		// �� �����ϱ����� �ϼ�
	long nDates,		// ���� ȸ��
	long FirstStartDay,
	double FirstFixingRate,
	long AverageFlag,
	double* deltat,
	long AllStrikeATMFlag,
	double swaprate
)
{
	long i;
	double d1, d2, PrevT, T, delta;
	double PrevDisc, Disc;
	double F, value;

	PrevT = ((double)FirstStartDay) / 365.;
	value = 0.0;
	if (AverageFlag == 0)
	{
		if (VolFlag == 0)
		{
			for (i = 0; i < nDates; i++) {
				T = ((double)Dates[i]) / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				F = (PrevDisc / Disc - 1.0) / delta;			// �����ݸ�
				if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) && i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

				if (i == 0)
				{
					if (PrevT <= 0.)
					{
						if (F < StrikeRate)
						{
							value = deltat[i] * Disc * (-F + StrikeRate);
						}
					}
					else
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (log(F / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2));
					}
				}
				else {
					if (F > 0.)
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (log(F / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2));
					}
					else value += 1.e-13;
				}

				PrevT = T;
			}
		}
		else if (VolFlag == 1)
		{
			for (i = 0; i < nDates; i++) {
				T = (double)Dates[i] / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				F = (PrevDisc / Disc - 1.0) / delta;		// �����ݸ�
				if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) && i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

				if (i == 0)
				{	// ù��° ������ 
					if (PrevT <= 0.)
					{
						if (F < StrikeRate)
						{
							value = deltat[i] * Disc * (-F + StrikeRate);
						}
					}
					else
					{
						if (AllStrikeATMFlag == 1) StrikeRate = F;
						else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
						d1 = (F - StrikeRate) / (Vol * sqrt(PrevT));
						value += deltat[i] * Disc * ((-F + StrikeRate) * CDF_N(-d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
					}
				}
				else {
					if (AllStrikeATMFlag == 1) StrikeRate = F;
					else if (AllStrikeATMFlag == 2) StrikeRate = swaprate;
					d1 = (F - StrikeRate) / (Vol * sqrt(PrevT));
					value += deltat[i] * Disc * ((-F + StrikeRate) * CDF_N(-d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
				}
				PrevT = T;
			}
		}
	}
	else
	{
		double F_Avg = 0.;
		for (i = 0; i < nDates; i++)
		{
			T = ((double)Dates[i]) / 365.0;
			delta = T - PrevT;

			PrevDisc = DF[i];
			Disc = DF[i + 1];

			F = (PrevDisc / Disc - 1.0) / delta;			// �����ݸ�
			if ((FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) && i == 0) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

			F_Avg += F / ((double)nDates);
			PrevT = T;
		}

		if (VolFlag == 0)
		{
			PrevT = ((double)FirstStartDay) / 365.;
			for (i = 0; i < nDates; i++) 
			{
				T = ((double)Dates[i]) / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				if (i == 0)
				{
					if (PrevT <= 0.) if (F_Avg < StrikeRate) value = deltat[i] * Disc * (-F_Avg + StrikeRate);
					else
					{
						d1 = (log(F_Avg / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2));
					}
				}
				else {
					if (F_Avg > 0.)
					{
						d1 = (log(F_Avg / StrikeRate) + 0.5 * Vol * Vol * PrevT) / (Vol * sqrt(PrevT));
						d2 = d1 - Vol * sqrt(PrevT);
						value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2));
					}
					else value += 1.e-13;
				}
				PrevT = T;
			}		
		}
		else
		{
			PrevT = ((double)FirstStartDay) / 365.;
			for (i = 0; i < nDates; i++) {
				T = (double)Dates[i] / 365.0;
				delta = T - PrevT;

				PrevDisc = DF[i];
				Disc = DF[i + 1];

				if (i == 0)
				{	// ù��° ������ 
					if (PrevT <= 0.) if (F_Avg < StrikeRate) value = deltat[i] * Disc * (-F_Avg + StrikeRate);
					else
					{
						d1 = (F_Avg - StrikeRate) / (Vol * sqrt(PrevT));
						value += deltat[i] * Disc * ((-F_Avg + StrikeRate) * CDF_N(-d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
					}
				}
				else {

					d1 = (F_Avg - StrikeRate) / (Vol * sqrt(PrevT));
					value += deltat[i] * Disc * ((-F_Avg + StrikeRate) * CDF_N(-d1) + Vol * sqrt(PrevT) * exp(-d1 * d1 / 2.) / 2.506628274631);
				}
				PrevT = T;
			}
		}

	}

	return NA * value;
}

DLLEXPORT(long) Pricing_CapFloor(
	long CapFloorFlag,			// Cap = 0 Floor = 1
	long PriceDate,				// ����
	long StartDate,				// �ɼǽ�����
	long SwapMaturityDate,		// ���� ���� YYYYMMDD
	long AnnCpnOneYear,			// �� �������޼�
	double NA,					// ������
	double Vol,					// ������
	double StrikePrice,			// ���ݸ�
	long UseStrikeAsAverage,	// ���ݸ��� Forward�ݸ��� ������� Flag
	long NTerm,					// �ݸ� Term ����
	double* Term,				// �ݸ� Term Array
	double* Rate,				// �ݸ� Rate Array
	long DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
	long VolFlag,				// 0: Black Vol 1: Normal Vol
	long HolidayAutoFlag,		// Holiday �ڵ����
	long HolidayNationFlag,		// Holiday �ڵ���� 1�� ��, 0: KRW, 1:USD, 2:GBP
	long NHoliday,				// Holiday ��������� �� Holiday����
	long* HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
	double FirstFixingRate,		//
	long AverageFlag,			// Forward�ݸ��� Average�� �����ڻ�
	long AllStrikeATMFlag,		// ��� ���ݸ��� ATM���� Flag
	long TextFlag,				// LoggingFlag
	long GreekFlag,				// Greek ��꿩��
	double* ResultValue			// Output : ���� = 4 + NTerm
)
{
	long i, j, n;
	double swv;
	long ResultCode = 0;

	if (PriceDate < 19000000) PriceDate = ExcelDateToCDate(PriceDate);
	if (StartDate < 19000000) StartDate = ExcelDateToCDate(StartDate);
	if (SwapMaturityDate < 19000000) SwapMaturityDate = ExcelDateToCDate(SwapMaturityDate);


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
		NHolidayInput = Number_Holiday(PriceDate / 10000,				// ���ۿ���
			SwapMaturityDate / 10000,           // ���Ῥ��
			HolidayNationFlag					// 0: KRW�ѱ�, 1: USD�̱�, 2: GBP����
		);
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		ResultCode = Mapping_Holiday_CType(
			PriceDate / 10000,				// ���ۿ���
			SwapMaturityDate / 10000,       // ���Ῥ��
			HolidayNationFlag,				// ����Flag 0�ѱ� 1�̱� 2����
			NHolidayInput,					// �迭 ���� Number_Holiday���� Ȯ��
			HolidayInput					// Holiday ���� �迭
		);
		for (i = 0; i < min(NHoliday, NHolidayInput); i++) HolidayYYYYMMDD[i] = HolidayInput[i];
	}
	long TempDate;
	long TempExcelDate;
	long MOD7;
	long SaturSundayFlag;
	long isholiflag;
	StartDate = ParseBusinessDateIfHoliday(StartDate, HolidayInput, NHolidayInput);

	// StartDate�� ���缭 EndDate�� ����
	long EndYYYYMM = SwapMaturityDate / 100;
	long EndDD = StartDate - ((long)(StartDate / 100)) * 100;
	SwapMaturityDate = EndYYYYMM * 100 + EndDD;
	
	TempDate = StartDate;
	long NCpnDate;
	long* CpnDate = Generate_CpnDate_Holiday_CapFloor(StartDate, SwapMaturityDate, AnnCpnOneYear, NCpnDate, TempDate, NHolidayInput, HolidayInput);
	long* DaysCpnDate = (long*)malloc(sizeof(long) * NCpnDate);
	for (i = 0; i < NCpnDate ; i++) DaysCpnDate[i] = DayCountAtoB(PriceDate, CpnDate[i]);
	long FirstStartDay = DayCountAtoB(PriceDate, StartDate);

	double* DF = (double*)malloc(sizeof(double) * (NCpnDate + 1));
	double* deltat = (double*)malloc(sizeof(double) * (NCpnDate));
	for (i = 0; i < NCpnDate; i++)
	{
		if (i == 0) deltat[i] = DayCountFrc(StartDate, CpnDate[i], DayCountFracFlag);
		else deltat[i] = DayCountFrc(CpnDate[i - 1], CpnDate[i], DayCountFracFlag);
	}
	double t = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.0;
	double r = Interpolate_Linear(Term, Rate, NTerm, t);
	DF[0] = exp(-r * t);
	for (i = 0; i < NCpnDate; i++)
	{
		t = ((double)DayCountAtoB(PriceDate, CpnDate[i])) / 365.0;
		r = Interpolate_Linear(Term, Rate, NTerm, t);
		DF[i + 1] = exp(-r * t);
	}

	if (UseStrikeAsAverage > 0)
	{
		double F_Avg = 0.,F;
		double T, delta, Disc, PrevDisc;
		double PrevT = ((double)FirstStartDay) / 365.;
		for (i = 0; i < NCpnDate; i++)
		{
			T = ((double)DaysCpnDate[i]) / 365.0;
			delta = T - PrevT;

			PrevDisc = DF[i];
			Disc = DF[i + 1];

			F = (PrevDisc / Disc - 1.0) / delta;			// �����ݸ�
			if (FirstFixingRate > 0.000001 || FirstFixingRate < -0.000001) F = FirstFixingRate;	    // �̹� ���� �����������ϰ��

			F_Avg += F / ((double)NCpnDate);
			PrevT = T;
		}
		StrikePrice = F_Avg;
	}

	double swprate = ForwardSwapRate(PriceDate, StartDate, NCpnDate, CpnDate, NTerm,Term, Rate, NTerm, Term, Rate, DayCountFracFlag, FirstFixingRate);

	if (CapFloorFlag == 0)
	{
		swv = BS_Cap(NA, VolFlag, Vol, DF, StrikePrice,	// ���ݸ�
			DaysCpnDate, NCpnDate, FirstStartDay, FirstFixingRate,AverageFlag, deltat, AllStrikeATMFlag , swprate);
	}
	else
	{
		swv = BS_Floor(NA, VolFlag, Vol, DF, StrikePrice,	// ���ݸ�
			DaysCpnDate, NCpnDate, FirstStartDay, FirstFixingRate,AverageFlag, deltat, AllStrikeATMFlag, swprate);
	}

	ResultValue[0] = swv;
	ResultValue[1] = swprate;
	free(HolidayInput);
	free(CpnDate);
	free(DF);
	free(DaysCpnDate);
	free(deltat);
	return ResultCode;
}

DLLEXPORT(long) Pricing_CapFloor_to_Volatility(
	long CapFloorFlag,			// Cap = 0 Floor = 1
	long PriceDate,				// ����
	long StartDate,				// �ɼǽ�����
	long SwapMaturityDate,		// ���� ���� YYYYMMDD
	long AnnCpnOneYear,			// �� �������޼�
	double NA,					// ������
	double Price,				// ����
	double StrikePrice,			// ���ݸ�
	long UseStrikeAsAverage,	// ���ݸ��� Forward�ݸ��� ������� Flag
	long NTerm,					// �ݸ� Term ����
	double* Term,				// �ݸ� Term Array
	double* Rate,				// �ݸ� Rate Array
	long DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
	long VolFlag,				// 0: Black Vol 1: Normal Vol
	long HolidayAutoFlag,		// Holiday �ڵ����
	long HolidayNationFlag,		// Holiday �ڵ���� 1�� ��, 0: KRW, 1:USD, 2:GBP
	long NHoliday,				// Holiday ��������� �� Holiday����
	long* HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
	double FirstFixingRate,		//
	long AverageFlag,			// 
	long AllStrikeATMFlag,		// ��� ���ݸ��� ATM���� Flag
	long TextFlag,				// LoggingFlag
	long GreekFlag,				// Greek ��꿩��
	double* ResultValue			// Output : ���� = 4 + NTerm
)
{
	long i, j, ResultCode= 0;
	double MaxRate = 2.5;
	double MinRate = 0.0001;
	double TargetRate = MaxRate;
	double* ResultArray = (double*)malloc(sizeof(double) * 100);
	if (PriceDate < 19000000) PriceDate = ExcelDateToCDate(PriceDate);
	if (StartDate < 19000000) StartDate = ExcelDateToCDate(StartDate);
	if (SwapMaturityDate < 19000000) SwapMaturityDate = ExcelDateToCDate(SwapMaturityDate);


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
		NHolidayInput = Number_Holiday(PriceDate / 10000,				// ���ۿ���
			SwapMaturityDate / 10000,           // ���Ῥ��
			HolidayNationFlag					// 0: KRW�ѱ�, 1: USD�̱�, 2: GBP����
		);
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		ResultCode = Mapping_Holiday_CType(
			PriceDate / 10000,				// ���ۿ���
			SwapMaturityDate / 10000,       // ���Ῥ��
			HolidayNationFlag,				// ����Flag 0�ѱ� 1�̱� 2����
			NHolidayInput,					// �迭 ���� Number_Holiday���� Ȯ��
			HolidayInput					// Holiday ���� �迭
		);
		for (i = 0; i < min(NHoliday, NHolidayInput); i++) HolidayYYYYMMDD[i] = HolidayInput[i];
	}

	long nCpnDates = 0;
	long TempDate = StartDate;
	long TempStartDate = StartDate;
	long NCpnDate;
	long* CpnDate = Generate_CpnDate_Holiday_CapFloor(StartDate, SwapMaturityDate, AnnCpnOneYear, NCpnDate, TempDate, NHolidayInput, HolidayInput);
	long* DaysCpnDate = (long*)malloc(sizeof(long) * NCpnDate);
	for (i = 0; i < NCpnDate; i++) DaysCpnDate[i] = DayCountAtoB(PriceDate, CpnDate[i]);
	long FirstStartDay = DayCountAtoB(PriceDate, StartDate);
	double CalcRate = 0.;
	double dblErrorRange = 0.0000001;

	for (j = 0; j < 1000; j++)
	{
		Pricing_CapFloor(
			CapFloorFlag,			// Cap = 0 Floor = 1
			PriceDate,				// ����
			StartDate,				// �ɼǽ�����
			SwapMaturityDate,		// ���� ���� YYYYMMDD
			AnnCpnOneYear,			// �� �������޼�
			NA,					// ������
			TargetRate,					// ������
			StrikePrice,			// ���ݸ�
			UseStrikeAsAverage,	// ���ݸ��� Forward�ݸ��� ������� Flag
			NTerm,					// �ݸ� Term ����
			Term,				// �ݸ� Term Array
			Rate,				// �ݸ� Rate Array
			DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
			VolFlag,				// 0: Black Vol 1: Normal Vol
			HolidayAutoFlag,		// Holiday �ڵ����
			HolidayNationFlag,		// Holiday �ڵ���� 1�� ��, 0: KRW, 1:USD, 2:GBP
			NHoliday,				// Holiday ��������� �� Holiday����
			HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
			FirstFixingRate,		//
			AverageFlag,			// Forward�ݸ��� Average�� �����ڻ�
			AllStrikeATMFlag,
			0,				// LoggingFlag
			0,				// Greek ��꿩��
			ResultArray			// Output : ���� = 4 + NTerm
		);
		CalcRate = ResultArray[0] - Price;
		if (fabs(CalcRate / NA) < dblErrorRange) break;
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
	ResultValue[0] = TargetRate;
	ResultValue[1] = ResultArray[1];
	free(HolidayInput);
	free(CpnDate);
	free(DaysCpnDate);
	free(ResultArray);
	return 1;
}