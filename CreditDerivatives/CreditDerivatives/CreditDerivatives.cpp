#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "CalcDate.h"
#include "Util.h"


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

DLLEXPORT(long) Calc_Hazard_Rate_From_CDSCurve(
	long PricingDateYYYYMMDD,		

	long NPremiumCurve,				// Premium Leg Ŀ�� Term ����
	double* PremiumCurveTerm,		// Premium Leg Ŀ�� Term Array
	double* PremiumCurve,			// Premium Leg Ŀ�� Rate Array

	long NProtectionCurve,			// Protection Leg Ŀ�� Term ����
	double* ProtectionCurveTerm,	// Protection Leg Ŀ�� Term
	double* ProtectionCurve,		// Protection Leg Ŀ�� Rate Array

	long NCDSCurve,					// CDS Term ����
	double* CDSCurveTerm,			// CDS Term Array
	double* CDSCurve,				// CDS Spread Array

	double Recovery,				// Recovery Rate
	long HazardRateCalcFlag,		// Hazard Rate Calc ��� 0: Continuous Annual Hazard Rate 1: �ܸ� �Ļ�Ȯ��
	long NCPN_Ann,					// �� �������� ��			

	long NHoliday,
	long* HolidayYYYYMMDD,

	double* ResultHazardTerm,		// OutPut Hazard Term
	double* ResultHazard			// OutPut Hazard Rate
);

double Calc_RiskyZeroBond(
	double Lambda,
	double rf_rate,
	double T,
	double RR,
	long CalcQMethod
)
{
	long i;
	// 10 + 1���� Node�� ������ ���н� ���
	double* P0t = (double*)malloc(sizeof(double) * 11);
	double* Q0t = (double*)malloc(sizeof(double) * 11);
	P0t[0] = 1.0;
	Q0t[0] = 1.0;

	for (i = 0; i < 10; i++)
	{
		P0t[i + 1] = exp(-rf_rate * (double)(i + 1) / 10.0 * T);
		if (CalcQMethod == 0)
		{
			Q0t[i + 1] = exp(-Lambda * (double)(i + 1) / 10.0 * T);
		}
		else
		{
			Q0t[i + 1] = 1.0 - Lambda * (double)(i + 1) * T;
		}
	}

	double zerobondprice = exp(-(Lambda + rf_rate) * T);
	for (i = 1; i < 11; i++)
		zerobondprice += RR * P0t[i] * (Q0t[i - 1] - Q0t[i]); // integral_0_to_T Z(0,t) d(-Q(0,t))

	if (P0t) free(P0t);
	if (Q0t) free(Q0t);

	return zerobondprice;
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


double Calc_RiskyCouponBondCleanPrice(
	long NT_Coupon,
	double* T_Coupon,
	double* T_Coupon_Pay,
	double* CouponRate,
	double* dt,
	long NHazard,
	double* HazardTerm,
	double* HazardRate,
	long NRiskFree,
	double* RiskFreeTerm,
	double* RiskFreeRate,
	double T_Mat,
	double NotionalAmount,
	double Recovery,
	long CalcQMethod
)
{
	long i;
	double Discounted_Coupon = 0.0;
	double Discounted_Notional = 0.0;
	double Clean_Price;
	double lambda;
	double Rf;
	double Rf_Pay;
	double DF = 1.;
	// ���� Date�� ���� PayDate�� ���̳��°��
	double Fwd_Rate;

	if (NT_Coupon > 0)
	{
		for (i = 0; i < NT_Coupon; i++)
		{
			if (T_Coupon[i] > 0.0)
			{
				lambda = Interpolate_Linear(HazardTerm, HazardRate, NHazard, T_Coupon[i]);
				Rf = Interpolate_Linear(RiskFreeTerm, RiskFreeRate, NRiskFree, T_Coupon[i]);
				if (lambda > 0.0) Discounted_Coupon += NotionalAmount * CouponRate[i] * dt[i] * Calc_RiskyZeroBond(lambda, Rf, T_Coupon[i], Recovery, CalcQMethod);
				else
				{
					DF = Calc_Discount_Factor(RiskFreeTerm, RiskFreeRate, NRiskFree, T_Coupon[i]);
					Discounted_Coupon += NotionalAmount * CouponRate[i] * dt[i] * DF;
				}

				if (T_Coupon[i] < T_Coupon_Pay[i])
				{
					Rf_Pay = Interpolate_Linear(RiskFreeTerm, RiskFreeRate, NRiskFree, T_Coupon_Pay[i]);
					Fwd_Rate = (Rf_Pay * T_Coupon_Pay[i] - Rf * T_Coupon[i]) / (T_Coupon_Pay[i] - T_Coupon[i]);
					Discounted_Coupon = Discounted_Coupon * 1.0 / (1.0 + Fwd_Rate * (T_Coupon_Pay[i] - T_Coupon[i]));
				}
			}
		}
	}
	lambda = Interpolate_Linear(HazardTerm, HazardRate, NHazard, T_Mat);
	Rf = Interpolate_Linear(RiskFreeTerm, RiskFreeRate, NRiskFree, T_Mat);
	if (lambda > 0.0) Discounted_Notional = NotionalAmount * Calc_RiskyZeroBond(lambda, Rf, T_Mat, Recovery, CalcQMethod);
	else
	{
		DF = Calc_Discount_Factor(RiskFreeTerm, RiskFreeRate, NRiskFree, T_Mat);
		Discounted_Notional = NotionalAmount * DF;
	}

	Clean_Price = Discounted_Coupon + Discounted_Notional;
	return Clean_Price;
}

long* Generate_CpnDate_Bond(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate)
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
		if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 1)
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

		if (CpnDate <= PriceDateYYYYMMDD || DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 1) break;
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
				// Forward End ��¥�� ����� �Ǵ� �Ͽ����� ��� ��¥ �̷�
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

long* Generate_CpnDate_Holiday_CpnBond(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
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

DLLEXPORT(long) Generate_CpnDate_BondModule_Using_Holiday(long EffectiveDate, long MaturityDate, long AnnCpnOneYear, long NHoliday, long* Holidays, long CpnNumber0Array1Flag, long* NumberOfCpnReturn, long* CpnDateArray)
{
	long i;
	long j;
	long n;

	long ResultCode = 1;
	for (i = 0; i < NHoliday; i++) if (Holidays[i] < 19000101) Holidays[i] = ExcelDateToCDate(Holidays[i]);
	
	if (EffectiveDate < 19000101) EffectiveDate = ExcelDateToCDate(EffectiveDate);
	if (MaturityDate < 19000101) MaturityDate = ExcelDateToCDate(MaturityDate);
	
	long RealPayDate = MaturityDate;
	long EffectiveYYYYMM = EffectiveDate / 100;
	long EffectiveDD = EffectiveDate - EffectiveYYYYMM * 100;

	long MaturityYYYYMM = MaturityDate / 100;
	MaturityDate = MaturityYYYYMM * 100 + EffectiveDD;

	long TempDate = EffectiveDate;
	long NCpnDate;
	long* CpnDate = Generate_CpnDate_Holiday_CpnBond(EffectiveDate, MaturityDate, AnnCpnOneYear, NCpnDate, TempDate, NHoliday, Holidays);

	long MaturityExcel, Mod7;
	MaturityExcel = CDateToExcelDate(MaturityDate);
	Mod7 = MaturityExcel % 7;
	// �������� ���
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
		// End Date ���� Pay Date ���� Business Day Count
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

long RiskyCouponBond_With_Schedule(
	long EffectiveDate,
	long CPNInputFlag,
	double Recovery,
	long CalcQMethod,
	// CPNInputFlag�� 1�� ���� ������
	long NCoupon,
	long* CouponDate,
	long* CouponPayDate,
	double* CouponRate,
	long PrincipalDate,
	double Principal,

	long NHazard,
	double* HazardTerm,
	double* HazardRate,

	long NRiskFree,
	double* RiskFreeTerm,
	double* RiskFreeRate,

	long PricingDate,
	long DayCountFracFlag,
	long TextFlag,
	long GreekFlag,
	double* ResultPrice,
	double* KeyRate_PV01_Convex,
	double* KeyRate_HazardDelta_Gamma
)
{
	long i, j, k;
	long NT;
	long DateDiff;
	long DateDiffPay;
	double* T;
	double* T_Pay;
	double* C;
	double DeltaT;
	double* dt;
	long NumberOfEffectiveCoupon;
	Recovery = min(1.0, Recovery);
	double T_Mat = ((double)DayCountAtoB(PricingDate, PrincipalDate)) / 365.0;
	if (T_Mat < 0)
	{
		T_Mat = 0.0;
		Principal = 0.0;
	}
	double CleanPrice;

	NT = 0;
	for (i = 0; i < NCoupon; i++)
	{
		DateDiff = DayCountAtoB(EffectiveDate, CouponDate[i]);
		if (DateDiff > 0)
		{
			NT += 1;
		}
	}

	T = (double*)malloc(sizeof(double) * NT);
	T_Pay = (double*)malloc(sizeof(double) * NT);
	C = (double*)malloc(sizeof(double) * NT);
	dt = (double*)malloc(sizeof(double) * NT);
	k = 0;
	for (i = 0; i < NCoupon; i++)
	{
		DateDiff = DayCountAtoB(PricingDate, CouponDate[i]);
		DateDiffPay = DayCountAtoB(PricingDate, CouponPayDate[i]);
		if (DateDiff > 0)
		{
			T[k] = ((double)DateDiff) / 365.0;
			T_Pay[k] = ((double)DateDiffPay) / 365.0;
			C[k] = CouponRate[i];
			k += 1;
		}

	}

	NumberOfEffectiveCoupon = k;

	k = 0;
	for (i = 0; i < NCoupon; i++)
	{
		DateDiff = DayCountAtoB(PricingDate, CouponDate[i]);
		if (i == 0){
			DeltaT = DayCountFractionAtoB(EffectiveDate, CouponDate[i], DayCountFracFlag);
		}
		else{
			DeltaT = DayCountFractionAtoB(CouponDate[i - 1], CouponDate[i], DayCountFracFlag);
		}

		if (DateDiff > 0)
		{
			dt[k] = DeltaT;
			k += 1;
		}

	}
	CleanPrice = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
		NHazard, HazardTerm, HazardRate,
		NRiskFree, RiskFreeTerm, RiskFreeRate,
		T_Mat, Principal, Recovery, CalcQMethod);

	ResultPrice[0] = CleanPrice;

	long Accrued_Flag = 0;
	double Accrued_dt;
	double Accrued_CPN_Rate;
	for (i = 0; i < NCoupon - 1; i++)
		if (PricingDate > CouponDate[i - 1] && PricingDate < CouponDate[i])
		{
			Accrued_Flag = 1;
			Accrued_dt = DayCountFractionAtoB(CouponDate[i - 1], PricingDate, DayCountFracFlag);
			Accrued_CPN_Rate = CouponRate[i - 1];
			break;
		}
	if (Accrued_Flag == 1)
	{
		ResultPrice[1] = Principal * Accrued_dt * Accrued_CPN_Rate;
		ResultPrice[2] = ResultPrice[0] + ResultPrice[1];
	}
	else
	{
		ResultPrice[1] = 0.0;
		ResultPrice[2] = CleanPrice;
	}


	double P_Ru;
	double P_Rd;
	double* CurveRUp;
	double* CurveRDn;
	double* CreditCurveLambdaUp;
	double* CreditCurveLambdaDn;
	double PV01;
	double Convexity;
	double HazardDelta;
	double HazardGamma;
	double RecoveryDelta;
	if (GreekFlag >= 1)
	{
		CurveRUp = (double*)malloc(sizeof(double) * NRiskFree);
		CurveRDn = (double*)malloc(sizeof(double) * NRiskFree);
		for (i = 0; i < NRiskFree; i++)
		{
			CurveRUp[i] = RiskFreeRate[i] + 0.0001;
			CurveRDn[i] = RiskFreeRate[i] - 0.0001;
		}

		P_Ru = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, CurveRUp,
			T_Mat, Principal, Recovery, CalcQMethod);

		P_Rd = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, CurveRDn,
			T_Mat, Principal, Recovery, CalcQMethod);

		PV01 = (P_Rd - P_Ru) / (2.0);
		Convexity = (P_Rd + P_Ru - 2.0 * CleanPrice);
		ResultPrice[3] = PV01;
		ResultPrice[4] = Convexity;

		CreditCurveLambdaUp = (double*)malloc(sizeof(double) * NHazard);
		CreditCurveLambdaDn = (double*)malloc(sizeof(double) * NHazard);

		for (i = 0; i < NHazard; i++)
		{
			CreditCurveLambdaUp[i] = HazardRate[i] + 0.0001;
			CreditCurveLambdaDn[i] = HazardRate[i] - 0.0001;
		}

		P_Ru = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, CreditCurveLambdaUp,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, Principal, Recovery, CalcQMethod);

		P_Rd = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, CreditCurveLambdaDn,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, Principal, Recovery, CalcQMethod);

		HazardDelta = (P_Rd - P_Ru) / (2.0);
		HazardGamma = (P_Rd + P_Ru - 2.0 * CleanPrice);

		ResultPrice[5] = HazardDelta;
		ResultPrice[6] = HazardGamma;

		P_Ru = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, Principal, min(Recovery + 0.01, 1.0), CalcQMethod);
		P_Rd = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, Principal, Recovery - 0.01, CalcQMethod);


		RecoveryDelta = (P_Ru - P_Rd) / (2.0);
		ResultPrice[7] = RecoveryDelta;

		if (GreekFlag >= 2)
		{
			for (i = 0; i < NRiskFree; i++)
			{
				if (T_Mat + 4.0 > RiskFreeTerm[i])
				{
					for (j = 0; j < NRiskFree; j++)
					{
						if (i == j)
						{
							CurveRUp[j] = RiskFreeRate[j] + 0.0001;
							CurveRDn[j] = RiskFreeRate[j] - 0.0001;
						}
						else
						{
							CurveRUp[j] = RiskFreeRate[j];
							CurveRDn[j] = RiskFreeRate[j];
						}
					}

					P_Ru = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
						NHazard, HazardTerm, HazardRate,
						NRiskFree, RiskFreeTerm, CurveRUp,
						T_Mat, Principal, Recovery, CalcQMethod);

					P_Rd = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
						NHazard, HazardTerm, HazardRate,
						NRiskFree, RiskFreeTerm, CurveRDn,
						T_Mat, Principal, Recovery, CalcQMethod);

					PV01 = (P_Rd - P_Ru) / (2.0);
					Convexity = (P_Rd + P_Ru - 2.0 * CleanPrice);
					KeyRate_PV01_Convex[i] = PV01;
					KeyRate_PV01_Convex[i + NRiskFree] = Convexity;
				}
				else
				{
					KeyRate_PV01_Convex[i] = 0.;
					KeyRate_PV01_Convex[i + NRiskFree] = 0.;
				}
			}

			for (i = 0; i < NHazard; i++)
			{
				if (T_Mat + 4.0 > HazardTerm[i])
				{
					for (j = 0; j < NHazard; j++)
					{
						if (i == j)
						{
							CreditCurveLambdaUp[j] = HazardRate[j] + 0.0001;
							CreditCurveLambdaDn[j] = HazardRate[j] - 0.0001;
						}
						else
						{
							CreditCurveLambdaUp[j] = HazardRate[j];
							CreditCurveLambdaDn[j] = HazardRate[j];
						}
					}

					P_Ru = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
						NHazard, HazardTerm, CreditCurveLambdaUp,
						NRiskFree, RiskFreeTerm, RiskFreeRate,
						T_Mat, Principal, Recovery, CalcQMethod);

					P_Rd = Calc_RiskyCouponBondCleanPrice(NumberOfEffectiveCoupon, T, T_Pay, C, dt,
						NHazard, HazardTerm, CreditCurveLambdaDn,
						NRiskFree, RiskFreeTerm, RiskFreeRate,
						T_Mat, Principal, Recovery, CalcQMethod);

					HazardDelta = (P_Rd - P_Ru) / (2.0);
					HazardGamma = (P_Rd + P_Ru - 2.0 * CleanPrice);
					KeyRate_HazardDelta_Gamma[i] = HazardDelta;
					KeyRate_HazardDelta_Gamma[i + NHazard] = HazardGamma;
				}
				else
				{
					KeyRate_HazardDelta_Gamma[i] = 0.;
					KeyRate_HazardDelta_Gamma[i + NHazard] = 0.;

				}
			}
		}

		if (CurveRUp) free(CurveRUp);
		if (CurveRDn) free(CurveRDn);
		if (CreditCurveLambdaUp) free(CreditCurveLambdaUp);
		if (CreditCurveLambdaDn) free(CreditCurveLambdaDn);
	}

	if (T) free(T);
	if (T_Pay) free(T_Pay);
	if (C) free(C);
	if (dt) free(dt);

	return 1;
}

long RiskyCouponBond(
	long EffectiveDate,
	long CPNInputFlag,
	double Recovery,
	long CalcQMethod,
	// CPNInputFlag�� 0�� ���� �߰�������
	double CPNRate_0,
	long NCPN_Ann_0,
	double NotionalAmount_0,
	long MaturityDate,
	long NHazard,
	double* HazardTerm,
	double* HazardRate,

	long NRiskFree,
	double* RiskFreeTerm,
	double* RiskFreeRate,

	long PricingDate,
	long NHoliday,
	long* HolidayYYYYMMDD,
	long DayCountFracFlag,
	long TextFlag,
	long GreekFlag,
	double* ResultPrice,
	double* KeyRate_PV01_Convex,
	double* KeyRate_HazardDelta_Gamma
)
{
	long i, j;
	long NT = 0;

	double* T;
	double* C;

	double* dt;
	long PrevCpnDate = PricingDate;
	long* CpnDate = Generate_CpnDate_Holiday_CpnBond(EffectiveDate, MaturityDate, NCPN_Ann_0, NT, PrevCpnDate, NHoliday, HolidayYYYYMMDD);
	
	double Accrued_dt=0.0;

	if (isin(PricingDate, CpnDate, NT) == 0)
	{
		long idx;
		Accrued_dt = 0.;
		for (i = 0; i < NT-1; i++)
		{
			if (PricingDate > CpnDate[i] && PricingDate < CpnDate[i + 1])
			{
				Accrued_dt = ((double)DayCountAtoB(CpnDate[i], PricingDate)) / 365.0;
			}
		}
	}
	else
	{
		Accrued_dt = 0.;
	}

	double CleanPrice;

	//NT = (long)(T_Mat_0 * NCPN_Ann_0);
	T = (double*)malloc(sizeof(double) * NT);
	C = (double*)malloc(sizeof(double) * NT);
	dt = (double*)malloc(sizeof(double) * NT);
	double T_Mat = -99999.0;
	for (i = 0; i < NT; i++)
	{
		if (i == 0)
		{
			dt[i] = DayCountFractionAtoB(EffectiveDate, CpnDate[0], DayCountFracFlag);
		}
		else
		{
			dt[i] = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFracFlag);
		}
		T[i] = ((double)DayCountAtoB(PricingDate, CpnDate[i]))/365.0;
		C[i] = CPNRate_0;
		if (i == NT - 1)
		{
			T_Mat = T[i];
		}
	}

	double* T_Pay = T;

	CleanPrice = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
		NHazard, HazardTerm, HazardRate,
		NRiskFree, RiskFreeTerm, RiskFreeRate,
		T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

	ResultPrice[0] = CleanPrice;
	ResultPrice[1] = Accrued_dt * CPNRate_0 * NotionalAmount_0;
	ResultPrice[2] = CleanPrice + ResultPrice[1];

	double P_Ru;
	double P_Rd;
	double* CurveRUp;
	double* CurveRDn;
	double* CreditCurveLambdaUp;
	double* CreditCurveLambdaDn;
	double PV01;
	double Convexity;
	double HazardDelta;
	double HazardGamma;
	double RecoveryDelta;
	if (GreekFlag >= 1)
	{
		CurveRUp = (double*)malloc(sizeof(double) * NRiskFree);
		CurveRDn = (double*)malloc(sizeof(double) * NRiskFree);
		for (i = 0; i < NRiskFree; i++)
		{
			CurveRUp[i] = RiskFreeRate[i] + 0.0001;
			CurveRDn[i] = RiskFreeRate[i] - 0.0001;
		}

		P_Ru = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, CurveRUp,
			T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

		P_Rd = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, CurveRDn,
			T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

		PV01 = (P_Rd - P_Ru) / (2.0);
		Convexity = (P_Rd + P_Ru - 2.0 * CleanPrice);
		ResultPrice[3] = PV01;
		ResultPrice[4] = Convexity;

		CreditCurveLambdaUp = (double*)malloc(sizeof(double) * NHazard);
		CreditCurveLambdaDn = (double*)malloc(sizeof(double) * NHazard);

		for (i = 0; i < NHazard; i++)
		{
			CreditCurveLambdaUp[i] = HazardRate[i] + 0.0001;
			CreditCurveLambdaDn[i] = HazardRate[i] - 0.0001;
		}

		P_Ru = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, CreditCurveLambdaUp,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

		P_Rd = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, CreditCurveLambdaDn,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

		HazardDelta = (P_Rd - P_Ru) / (2.0);
		HazardGamma = (P_Rd + P_Ru - 2.0 * CleanPrice);

		ResultPrice[5] = HazardDelta;
		ResultPrice[6] = HazardGamma;

		P_Ru = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, NotionalAmount_0, min(Recovery + 0.01, 1.0), CalcQMethod);
		P_Rd = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
			NHazard, HazardTerm, HazardRate,
			NRiskFree, RiskFreeTerm, RiskFreeRate,
			T_Mat, NotionalAmount_0, Recovery - 0.01, CalcQMethod);


		RecoveryDelta = (P_Ru - P_Rd) / (2.0);
		ResultPrice[7] = RecoveryDelta;

		if (GreekFlag >= 2)
		{
			for (i = 0; i < NRiskFree; i++)
			{
				if (T_Mat + 4.0 > RiskFreeTerm[i])
				{
					for (j = 0; j < NRiskFree; j++)
					{
						if (i == j)
						{
							CurveRUp[j] = RiskFreeRate[j] + 0.0001;
							CurveRDn[j] = RiskFreeRate[j] - 0.0001;
						}
						else
						{
							CurveRUp[j] = RiskFreeRate[j];
							CurveRDn[j] = RiskFreeRate[j];
						}
					}

					P_Ru = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
						NHazard, HazardTerm, HazardRate,
						NRiskFree, RiskFreeTerm, CurveRUp,
						T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

					P_Rd = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
						NHazard, HazardTerm, HazardRate,
						NRiskFree, RiskFreeTerm, CurveRDn,
						T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

					PV01 = (P_Rd - P_Ru) / (2.0);
					Convexity = (P_Rd + P_Ru - 2.0 * CleanPrice);
					KeyRate_PV01_Convex[i] = PV01;
					KeyRate_PV01_Convex[i + NRiskFree] = Convexity;
				}
				else
				{
					KeyRate_PV01_Convex[i] = 0.;
					KeyRate_PV01_Convex[i + NRiskFree] = 0.;
				}
			}

			for (i = 0; i < NHazard; i++)
			{
				if (T_Mat + 4.0 > HazardTerm[i])
				{
					for (j = 0; j < NHazard; j++)
					{
						if (i == j)
						{
							CreditCurveLambdaUp[j] = HazardRate[j] + 0.0001;
							CreditCurveLambdaDn[j] = HazardRate[j] - 0.0001;
						}
						else
						{
							CreditCurveLambdaUp[j] = HazardRate[j];
							CreditCurveLambdaDn[j] = HazardRate[j];
						}
					}

					P_Ru = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
						NHazard, HazardTerm, CreditCurveLambdaUp,
						NRiskFree, RiskFreeTerm, RiskFreeRate,
						T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

					P_Rd = Calc_RiskyCouponBondCleanPrice(NT, T, T_Pay, C, dt,
						NHazard, HazardTerm, CreditCurveLambdaDn,
						NRiskFree, RiskFreeTerm, RiskFreeRate,
						T_Mat, NotionalAmount_0, Recovery, CalcQMethod);

					HazardDelta = (P_Rd - P_Ru) / (2.0);
					HazardGamma = (P_Rd + P_Ru - 2.0 * CleanPrice);
					KeyRate_HazardDelta_Gamma[i] = HazardDelta;
					KeyRate_HazardDelta_Gamma[i + NHazard] = HazardGamma;
				}
				else
				{
					KeyRate_HazardDelta_Gamma[i] = 0.0;
					KeyRate_HazardDelta_Gamma[i + NHazard] = 0.0;
				}
			}
		}

		if (CurveRUp) free(CurveRUp);
		if (CurveRDn) free(CurveRDn);
		if (CreditCurveLambdaUp) free(CreditCurveLambdaUp);
		if (CreditCurveLambdaDn) free(CreditCurveLambdaDn);
	}

	if (T) free(T);
	if (C) free(C);
	if (dt) free(dt);
	if (CpnDate) free(CpnDate);
	return 1;
}

long Inputcheck_RiskyCouponBond(
	long EffectiveDate,
	long CPNInputFlag,
	double Recovery,
	long CalcQMethod,
	// CPNInputFlag�� 0�� ���� �߰�������
	double CPNRate_0,
	long NCPN_Ann_0,
	double NotionalAmount_0,
	long MaturityDate,
	// CPNInputFlag�� 1�� ���� ������
	long NCoupon,
	long* CouponDate,
	long* CouponPayDate,
	double* CouponRate,
	long PrincipalDate,
	double Principal,

	long NHazard,
	double* HazardTerm,
	double* HazardRate,

	long NRiskFree,
	double* RiskFreeTerm,
	double* RiskFreeRate,

	long PricingDate,
	long DayCountFracFlag,
	long TextFlag,
	long GreekFlag)
{
	long i;

	long EFFECTIVE_DATE_ERROR = -101;
	long CPN_INPUT_FLAG_ERROR = -103;
	long RECOVERY_ERROR = -105;
	long CALC_Q_METHOD_ERROR = -107;
	long CPN_RATE_ERROR = -109;
	long NCPN_ANN_ERROR = -111;
	long NOTIONAL_ERROR = -113;
	long MATURITY_ERROR = -115;
	long DAYCOUNTFRACERROR = -116;
	long NCOUPON_ERROR = -117;
	long COUPONDATE_ERROR = -119;
	long COUPONRATE_ERROR = -121;
	long NOTIONAL_DATE_ERROR = -123;
	long NHAZARD_ERROR = -125;
	long HAZARD_TERM_ERROR = -127;
	long HAZARD_RATE_ERROR = -129;
	long NRISKFREE_ERROR = -131;
	long RISKFREETERM_ERROR = -133;
	long RISKFREERATE_ERROR = -135;
	long PRICINGDATE_ERROR = -137;
	long TEXTFLAGERROR = -139;
	long GREEKFLAGERROR = -141;

	if (EffectiveDate < 19000101 || EffectiveDate > 99991231) return EFFECTIVE_DATE_ERROR;

	if (CPNInputFlag < 0 || CPNInputFlag >= 2) return CPN_INPUT_FLAG_ERROR;

	if (Recovery < 0.0 || Recovery >= 1.0) return RECOVERY_ERROR;

	if (CalcQMethod < 0 || CalcQMethod >= 3) return CALC_Q_METHOD_ERROR;
	if (DayCountFracFlag < 0 || DayCountFracFlag  > 3) return DAYCOUNTFRACERROR;
	if (CPNInputFlag == 0)
	{
		if (NCPN_Ann_0 < 1) return NCPN_ANN_ERROR;

		if (NotionalAmount_0 < 0.0) return NOTIONAL_ERROR;

		if (MaturityDate < 19000000) return MATURITY_ERROR;

	}
	else
	{
		if (NCoupon < 0) return NCOUPON_ERROR;

		for (i = 1; i < NCoupon; i++)
		{
			if (CouponDate[i] < CouponDate[i - 1]) return COUPONDATE_ERROR;
			if (CouponPayDate[i] < CouponPayDate[i - 1]) return COUPONDATE_ERROR;
		}

		if (PrincipalDate < 19000101 || PrincipalDate > 99991231) return NOTIONAL_DATE_ERROR;

		if (Principal < 0) return NOTIONAL_ERROR;

		//Paydate�������� ���� ����
		if (PricingDate > CouponDate[NCoupon - 1]) return PRICINGDATE_ERROR;
	}

	// Hazard ���� ����
	if (NHazard < 1) return NHAZARD_ERROR;

	if (HazardTerm[0] < 0.0) return HAZARD_TERM_ERROR;

	for (i = 1; i < NHazard; i++)
	{
		if (HazardTerm[i] < HazardTerm[i - 1] || HazardTerm[i] < 0.0) return HAZARD_TERM_ERROR;

		//�� ������ �����ؾ��� e^(-lambda1 x T1) < e^(-lambda2 x T2)
		if (HazardRate[i] < HazardRate[i - 1] * HazardTerm[i - 1] / HazardTerm[i]) return HAZARD_RATE_ERROR;
	}

	if (NRiskFree < 1) return NRISKFREE_ERROR;

	return 0;
}

DLLEXPORT(long) Calc_RiskyCouponBond(
	long EffectiveDate,
	long CPNInputFlag,
	double Recovery,
	long CalcQMethod,
	// CPNInputFlag�� 0�� ���� �߰�������
	double CPNRate_0,
	long NCPN_Ann_0,
	double NotionalAmount_0,
	long MaturityDate,
	// CPNInputFlag�� 1�� ���� ������
	long NCoupon,
	long* CouponDate,
	long* CouponPayDate,
	double* CouponRate,
	long PrincipalDate,
	double Principal,

	long InputType,
	long NHazardCDS,
	double* HazardCDSTerm,
	double* HazardCDSRate,

	long NRiskFree,
	double* RiskFreeTerm,
	double* RiskFreeRate,

	long PricingDate,
	long NHoliday,
	long* HolidayYYYYMMDD,

	long DayCountFracFlag,
	long TextFlag,
	long GreekFlag,
	double* ResultPrice,
	double* KeyRate_PV01_Convex,
	double* KeyRate_HazardDelta_Gamma
)
{
	long i;

	// CDS Curve ������� ��ü Calibration�� ����� ����
	double* TempHazardRate = (double*)malloc(sizeof(double) * NHazardCDS);
	double* TempHazardTerm = (double*)malloc(sizeof(double) * NHazardCDS);
	long ResultCode = 0;

	ResultCode = Inputcheck_RiskyCouponBond(EffectiveDate, CPNInputFlag, Recovery, CalcQMethod,
		CPNRate_0, NCPN_Ann_0, NotionalAmount_0, MaturityDate,
		NCoupon, CouponDate, CouponPayDate, CouponRate, PrincipalDate,
		Principal, NHazardCDS, HazardCDSTerm, HazardCDSRate,
		NRiskFree, RiskFreeTerm, RiskFreeRate,
		PricingDate, DayCountFracFlag, TextFlag, GreekFlag);

	if (ResultCode < 0)
		return ResultCode;

	long PricingDate_YYYYMMDD;
	if (PricingDate < 19000101) PricingDate_YYYYMMDD = ExcelDateToCDate(PricingDate);
	else PricingDate_YYYYMMDD = PricingDate;

	for (i = 0; i < NHoliday; i++) if (HolidayYYYYMMDD[i] < 19000101) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayYYYYMMDD[i]);

	if (CPNInputFlag == 1)
	{
		if (InputType == 0)
		{
			ResultCode = RiskyCouponBond_With_Schedule(EffectiveDate, CPNInputFlag, Recovery, CalcQMethod, NCoupon,
				CouponDate, CouponPayDate, CouponRate, PrincipalDate, Principal, NHazardCDS,
				HazardCDSTerm, HazardCDSRate, NRiskFree, RiskFreeTerm, RiskFreeRate,
				PricingDate, DayCountFracFlag, TextFlag, GreekFlag, ResultPrice, KeyRate_PV01_Convex, KeyRate_HazardDelta_Gamma);
		}
		else
		{
			ResultCode = Calc_Hazard_Rate_From_CDSCurve(PricingDate_YYYYMMDD, NRiskFree, RiskFreeTerm, RiskFreeRate,
				NRiskFree, RiskFreeTerm, RiskFreeRate,
				NHazardCDS, HazardCDSTerm, HazardCDSRate,
				Recovery, 0, 2, NHoliday, HolidayYYYYMMDD, TempHazardTerm, TempHazardRate);

			ResultCode = RiskyCouponBond_With_Schedule(EffectiveDate, CPNInputFlag, Recovery, CalcQMethod, NCoupon,
				CouponDate, CouponPayDate, CouponRate, PrincipalDate, Principal, NHazardCDS,
				TempHazardTerm, TempHazardRate, NRiskFree, RiskFreeTerm, RiskFreeRate,
				PricingDate, DayCountFracFlag, TextFlag, GreekFlag, ResultPrice, KeyRate_PV01_Convex, KeyRate_HazardDelta_Gamma);
		}
	}
	else
	{
		if (InputType == 0)
		{
			ResultCode = RiskyCouponBond(EffectiveDate, CPNInputFlag, Recovery, CalcQMethod, CPNRate_0, NCPN_Ann_0, NotionalAmount_0, MaturityDate, NHazardCDS, HazardCDSTerm, HazardCDSRate, NRiskFree, RiskFreeTerm, RiskFreeRate, PricingDate, NHoliday, HolidayYYYYMMDD, DayCountFracFlag, TextFlag, GreekFlag, ResultPrice, KeyRate_PV01_Convex, KeyRate_HazardDelta_Gamma);
		}
		else
		{
			ResultCode = Calc_Hazard_Rate_From_CDSCurve(PricingDate_YYYYMMDD, NRiskFree, RiskFreeTerm, RiskFreeRate,
				NRiskFree, RiskFreeTerm, RiskFreeRate,
				NHazardCDS, HazardCDSTerm, HazardCDSRate,
				Recovery, 0, 2, NHoliday, HolidayYYYYMMDD, TempHazardTerm, TempHazardRate);

			ResultCode = RiskyCouponBond(EffectiveDate, CPNInputFlag, Recovery, CalcQMethod, CPNRate_0, NCPN_Ann_0, NotionalAmount_0, MaturityDate, NHazardCDS, HazardCDSTerm, TempHazardRate, NRiskFree, RiskFreeTerm, RiskFreeRate, PricingDate, NHoliday, HolidayYYYYMMDD, DayCountFracFlag, TextFlag, GreekFlag, ResultPrice, KeyRate_PV01_Convex, KeyRate_HazardDelta_Gamma);
		}
	}


	if (TempHazardRate) free(TempHazardRate);
	if (TempHazardTerm) free(TempHazardTerm);
	return 1;
}




double Calibrate_HazardRate_CreditSpread(
	double riskless_rate,
	double risky_rate,
	double T,
	double RR
)
{

	double ObjValue = exp(-risky_rate * T);

	double value_a = 1.0;
	double value_b = 0.0;
	double value;
	double dblErrorRange = 0.0001;
	double dblCalcPrice = Calc_RiskyZeroBond(value_a, riskless_rate, T, RR, 0);
	if (dblCalcPrice <= 0)  return 0.0;

	double dblPriceGab = ObjValue - dblCalcPrice;
	if (fabs(dblPriceGab) < dblErrorRange)
		return value_a;

	while (dblPriceGab < 0)
	{
		value_b = value_a;
		value_a *= 2.0;

		dblCalcPrice = Calc_RiskyZeroBond(value_a, riskless_rate, T, RR, 0);
		dblPriceGab = ObjValue - dblCalcPrice;

		if (fabs(dblPriceGab) < dblErrorRange)
			return value_a;
	}

	value = (value_a + value_b) / 2.0;
	for (int i = 0; i < 1000; i++)
	{
		dblCalcPrice = Calc_RiskyZeroBond(value, riskless_rate, T, RR, 0);
		dblPriceGab = ObjValue - dblCalcPrice;

		// ���밪 < ���� Ytm ����
		if (fabs(dblPriceGab) < dblErrorRange)
			break;

		// Ytm < ���� Ytm ���� || Ytm == 0
		if (value < dblErrorRange || value == 0.0)
			return 0.0;

		if (dblPriceGab > 0.0)
			value_a = value;
		else
			value_b = value;

		value = (value_a + value_b) / 2.0;
	}
	return value;
}

double Calibrate_HazardRate_CreditSpread2(
	double riskless_rate,
	double risky_rate,
	double T,
	double RR
)
{
	double Lambda = (risky_rate - riskless_rate) / (1 - RR);
	return Lambda;
}

long Calibrate_HazardRateStructure_CreditSpread(
	long NRefZero,
	double* RefZeroTerm,
	double* ZeroRiskFree,
	double* ZeroRiskyBond,
	double Recovery,
	double* ResultHazardStructure,
	long DefaultRateCalcMethod
)
{
	long i;
	for (i = 0; i < NRefZero; i++)
	{
		if (DefaultRateCalcMethod == 0)
		{
			ResultHazardStructure[i] = Calibrate_HazardRate_CreditSpread(ZeroRiskFree[i], ZeroRiskyBond[i], RefZeroTerm[i], Recovery);
		}
		else
		{
			ResultHazardStructure[i] = Calibrate_HazardRate_CreditSpread2(ZeroRiskFree[i], ZeroRiskyBond[i], RefZeroTerm[i], Recovery);
		}
	}
	return 1;
}

double Calc_CDS_From_Hazard(
	long NPremiumCurve,
	double* PremiumCurveTerm,
	double* PremiumCurve,

	long NProtectionCurve,
	double* ProtectionCurveTerm,
	double* ProtectionCurve,

	long DataFlag,
	long NHazardRate,
	double* HazardRateTerm,
	double* HazardRate,
	long CalcQMethod,

	double Recovery,
	long ScheduleInputFlag,
	long NCPN_Ann,
	double Maturity,
	long NSchedule,
	long* ResetDateYYYYMMDD,
	long* PayDateYYYYMMDD,
	long PricingDateYYYYMMDD,

	double* Premium_Leg,
	double* Protection_Leg,
	double* Premium_Schedule,
	double NotionalAmount,
	long NHoliday,
	long* HolidayYYYYMMDD
)
{
	long i;
	long k;
	long MaturityDateYYYYMMDD;
	long NCpnDate = 0;
	long FirstCpnDate = PricingDateYYYYMMDD + 0;
	if (ScheduleInputFlag == 0)
	{
		if (Maturity < 1000) MaturityDateYYYYMMDD = EDate_Cpp(PricingDateYYYYMMDD, (long)(Maturity * 12.0 + 0.1));
		else if (Maturity < 19000101) MaturityDateYYYYMMDD = ExcelDateToCDate((long)(Maturity + 0.1));
		else MaturityDateYYYYMMDD = (long)(Maturity + 0.1);
	}
	else
	{
		MaturityDateYYYYMMDD = PayDateYYYYMMDD[NSchedule - 1];
	}

	long* CpnDate = Generate_CpnDate_Holiday_CpnBond(PricingDateYYYYMMDD, MaturityDateYYYYMMDD, NCPN_Ann, NCpnDate, FirstCpnDate, NHoliday, HolidayYYYYMMDD);
	long N_PremiumNode = NCpnDate + 1;
	double *dt_Premium; //= 1.0 / ((double)NCPN_Ann);
	double dt_Protection = 1.0 / 12.0;
	double t;

	double Result_Spread;
	double Premium_Value_At_T;
	// ��������Ƚ��  + 1 ��ŭ �Ҵ�
	double* Z_Premium;
	double* Q_Premium;
	if (ScheduleInputFlag == 0)
	{
		Z_Premium = (double*)malloc(sizeof(double) * (NCpnDate+1));
		dt_Premium = (double*)malloc(sizeof(double) * (NCpnDate));
		for (i = 0; i < NCpnDate; i++)
		{
			if (i == 0) dt_Premium[i] = ((double)DayCountAtoB(FirstCpnDate, CpnDate[0]))/365.0;
			else dt_Premium[i] = ((double)DayCountAtoB(CpnDate[i-1], CpnDate[i]))/365.0;
		}

		if (PricingDateYYYYMMDD == FirstCpnDate) t = 0.0;
		else t = ((double)DayCountAtoB(PricingDateYYYYMMDD, FirstCpnDate)) / 365.0;

		if (t <= 0.0001) Z_Premium[0] = 1.0;
		else Z_Premium[0] = Calc_Discount_Factor(PremiumCurveTerm, PremiumCurve, NPremiumCurve, t);

		for (i = 0; i < NCpnDate; i++)
		{
			t += dt_Premium[i];
			Z_Premium[i+1] = Calc_Discount_Factor(PremiumCurveTerm, PremiumCurve, NPremiumCurve, t);
		}

		Q_Premium = (double*)malloc(sizeof(double) * (NCpnDate + 1));
		Q_Premium[0] = 1.0;

		if (PricingDateYYYYMMDD == FirstCpnDate) t = 0.0;
		else t = ((double)DayCountAtoB(PricingDateYYYYMMDD, FirstCpnDate)) / 365.0;

		for (i = 0; i < NCpnDate; i++)
		{
			t += dt_Premium[i];
			if (CalcQMethod == 0)
			{
				Q_Premium[i+1] = exp(-Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t);
			}
			else
			{
				Q_Premium[i+1] = 1.0 - Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t;
			}
		}
	}
	else
	{
		Maturity = ((double)DayCountAtoB(PricingDateYYYYMMDD, PayDateYYYYMMDD[NSchedule - 1])) / 365.0;
		N_PremiumNode = 1;
		for (i = 0; i < NSchedule; i++)
		{
			if (PricingDateYYYYMMDD < PayDateYYYYMMDD[i])
			{
				N_PremiumNode += 1;
			}
		}
		Z_Premium = (double*)malloc(sizeof(double) * N_PremiumNode);
		dt_Premium = (double*)malloc(sizeof(double) * N_PremiumNode -1);
		Q_Premium = (double*)malloc(sizeof(double) * N_PremiumNode);

		Z_Premium[0] = 1.0;
		Q_Premium[0] = 1.0;
		k = 1;
		for (i = 0; i < NSchedule; i++)
		{
			if (PricingDateYYYYMMDD < PayDateYYYYMMDD[i])
			{
				dt_Premium[k - 1] = ((double)DayCountAtoB(ResetDateYYYYMMDD[i], PayDateYYYYMMDD[i])) / 365.0; 
				t = ((double)DayCountAtoB(PricingDateYYYYMMDD, PayDateYYYYMMDD[i])) / 365.0; 
				Z_Premium[k] = Calc_Discount_Factor(PremiumCurveTerm, PremiumCurve, NPremiumCurve, t);

				if (CalcQMethod == 0) {
					Q_Premium[k] = exp(-Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t);
				}
				else{
					Q_Premium[k] = 1.0 - Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t;
				}
				k+=1;

			}
		}

	}
	// 12 * ����(��) �� + 1��ŭ �Ҵ� 
	long N_ProtectionNode = (long)(12.0 * Maturity + 0.5) + 1;
	double* Z_Protection = (double*)malloc(sizeof(double) * N_ProtectionNode);
	Z_Protection[0] = 1.0;
	t = dt_Protection;
	for (i = 1; i < N_ProtectionNode; i++)
	{
		Z_Protection[i] = Calc_Discount_Factor(ProtectionCurveTerm, ProtectionCurve, NProtectionCurve, t);
		t += dt_Protection;
	}

	double* Q_Protection = (double*)malloc(sizeof(double) * N_ProtectionNode);
	Q_Protection[0] = 1.0;
	t = dt_Protection;
	for (i = 1; i < N_ProtectionNode; i++)
	{
		if (CalcQMethod == 0)
		{
			Q_Protection[i] = exp(-Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t);
		}
		else
		{
			Q_Protection[i] = 1.0 - Calc_Zero_Rate(HazardRateTerm, HazardRate, NHazardRate, t) * t;
		}
		t += dt_Protection;
	}

	double Premium_Value, Protection_Value;

	Protection_Value = 0.0;
	for (i = 1; i < N_ProtectionNode; i++)
		Protection_Value += 0.5 * (1.0 - Recovery) * (Z_Protection[i - 1] + Z_Protection[i]) * max(0.0, (Q_Protection[i - 1] - Q_Protection[i]));

	Premium_Value = 0.0;
	for (i = 1; i < N_PremiumNode; i++)
	{
		Premium_Value_At_T = 0.5 * dt_Premium[i-1] * Z_Premium[i] * (Q_Premium[i - 1] + Q_Premium[i]);
		Premium_Value += Premium_Value_At_T;
		Premium_Schedule[i - 1] = Premium_Value_At_T;
	}

	Result_Spread = Protection_Value / Premium_Value;
	*Protection_Leg = Protection_Value * NotionalAmount;
	*Premium_Leg = Premium_Value * Result_Spread * NotionalAmount;

	for (i = 0; i < N_PremiumNode - 1; i++)
	{
		Premium_Schedule[i] *= Result_Spread * NotionalAmount;
	}

	if (Z_Premium) free(Z_Premium);
	if (Z_Protection) free(Z_Protection);
	if (Q_Premium) free(Q_Premium);
	if (Q_Protection) free(Q_Protection);
	if (dt_Premium) free(dt_Premium);
	if (CpnDate) free(CpnDate);
	return Result_Spread;
}


double Calc_CDS_From_CreditSpread(
	long NPremiumCurve,
	double* PremiumCurveTerm,
	double* PremiumCurve,

	long NProtectionCurve,
	double* ProtectionCurveTerm,
	double* ProtectionCurve,

	long DataFlag,
	long NRefZero,
	double* RefZeroTerm,
	double* ZeroRiskFree,
	double* ZeroRiskyBond,
	long DefaultRateCalcMethod,

	double Recovery,
	long ScheduleInputFlag,
	long NCPN_Ann,
	double Maturity,
	long NSchedule,
	long* ResetDateYYYYMMDD,
	long* PayDateYYYYMMDD,
	long PricingDateYYYYMMDD,

	double* Premium_Leg,
	double* Protection_Leg,
	double* ResultHazardRate,
	double* Premium_Schedule,
	long GreekFlag,
	double* ResultGreeks,
	double OLD_CDS_Spread,
	double NotionalAmount,
	long NHoliday,
	long* HolidayYYYYMMDD
)
{
	long i;
	long temp;
	double ResultSpread;
	double Temp_Protection_Leg = 0.0;
	double Temp_Premium_Leg = 0.0;
	double P_Ru, P_Rd;

	double* HazardRate = (double*)malloc(sizeof(double) * NRefZero);
	double* PremiumCurveRup = (double*)malloc(sizeof(double) * NPremiumCurve);
	double* PremiumCurveRdn = (double*)malloc(sizeof(double) * NPremiumCurve);
	double* ProtectionCurveRup = (double*)malloc(sizeof(double) * NProtectionCurve);
	double* ProtectionCurveRdn = (double*)malloc(sizeof(double) * NProtectionCurve);
	double* HazardUp = (double*)malloc(sizeof(double) * NRefZero);
	double* HazardDn = (double*)malloc(sizeof(double) * NRefZero);
	double* Temp_Premium_Schedule = (double*)malloc(sizeof(double) * (long)(NCPN_Ann * Maturity + 2.0));

	temp = Calibrate_HazardRateStructure_CreditSpread(NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, Recovery, HazardRate, DefaultRateCalcMethod);

	long NHazardRate = NRefZero;
	double* HazardRateTerm = RefZeroTerm;

	ResultSpread = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
		NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
		DataFlag, NHazardRate, HazardRateTerm, HazardRate, 0,
		Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, Premium_Leg, Protection_Leg, Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);


	for (i = 0; i < NRefZero; i++)
	{
		ResultHazardRate[i] = 1.0 - exp(-HazardRate[i] * HazardRateTerm[i]);
	}

	double Protection_Value_U;
	double RPV01_U;
	double Premium_Value_U;
	double Value_ProtectionBuyer_U;
	double Protection_Value_D;
	double RPV01_D;
	double Premium_Value_D;
	double Value_ProtectionBuyer_D;
	if (GreekFlag >= 1)
	{
		for (i = 0; i < NPremiumCurve; i++)
		{
			PremiumCurveRup[i] = PremiumCurve[i] + 0.0001;
			PremiumCurveRdn[i] = PremiumCurve[i] - 0.0001;
		}

		for (i = 0; i < NProtectionCurve; i++)
		{
			ProtectionCurveRup[i] = ProtectionCurve[i] + 0.0001;
			ProtectionCurveRdn[i] = ProtectionCurve[i] - 0.0001;
		}

		P_Ru = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRup,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRup,
			DataFlag, NHazardRate, HazardRateTerm, HazardRate, 0,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

		Protection_Value_U = Temp_Protection_Leg;
		RPV01_U = Temp_Premium_Leg / P_Ru;
		Premium_Value_U = OLD_CDS_Spread * RPV01_U;
		Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

		P_Rd = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRdn,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRdn,
			DataFlag, NHazardRate, HazardRateTerm, HazardRate, 0,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

		Protection_Value_D = Temp_Protection_Leg;
		RPV01_D = Temp_Premium_Leg / P_Rd;
		Premium_Value_D = OLD_CDS_Spread * RPV01_D;
		Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

		ResultGreeks[0] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
		ResultGreeks[1] = (Premium_Value_U - Premium_Value_D) / 2.0;
		ResultGreeks[2] = (Protection_Value_U - Protection_Value_D) / 2.0;

		for (i = 0; i < NRefZero; i++)
		{
			HazardUp[i] = HazardRate[i] + 0.0001;
			HazardDn[i] = HazardRate[i] - 0.0001;
		}

		P_Ru = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NHazardRate, HazardRateTerm, HazardUp, 0,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

		Protection_Value_U = Temp_Protection_Leg;
		RPV01_U = Temp_Premium_Leg / P_Ru;
		Premium_Value_U = OLD_CDS_Spread * RPV01_U;
		Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

		P_Rd = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NHazardRate, HazardRateTerm, HazardDn, 0,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

		Protection_Value_D = Temp_Protection_Leg;
		RPV01_D = Temp_Premium_Leg / P_Rd;
		Premium_Value_D = OLD_CDS_Spread * RPV01_D;
		Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

		ResultGreeks[3] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
		ResultGreeks[4] = (Premium_Value_U - Premium_Value_D) / 2.0;
		ResultGreeks[5] = (Protection_Value_U - Protection_Value_D) / 2.0;

	}
	if (HazardRate) free(HazardRate);
	if (PremiumCurveRup) free(PremiumCurveRup);
	if (PremiumCurveRdn) free(PremiumCurveRdn);
	if (ProtectionCurveRup) free(ProtectionCurveRup);
	if (ProtectionCurveRdn) free(ProtectionCurveRdn);
	if (HazardUp) free(HazardUp);
	if (HazardDn) free(HazardDn);
	if (Temp_Premium_Schedule) free(Temp_Premium_Schedule);

	return ResultSpread;
}

long Inputcheck_Calc_CDS_Spread(
	long NPremiumCurve,
	double* PremiumCurveTerm,
	double* PremiumCurve,

	long NProtectionCurve,
	double* ProtectionCurveTerm,
	double* ProtectionCurve,

	long DataFlag,
	long NHazardRate,
	double* HazardRateTerm,
	double* HazardRate,
	long CalcQMethod,

	long NRefZero,
	double* RefZeroTerm,
	double* ZeroRiskFree,
	double* ZeroRiskyBond,
	long DefaultRateCalcMethod,

	double Recovery,
	long NCPN_Ann,
	double Maturity,
	double PrevCDSSpread,
	long CDSPosition,
	long TextFlag,
	long GreekFlag)
{
	long i;
	long NPremiumCurve_Error = -1, PremiumCurveTerm_Error = -2, PremiumCurve_Error = -3;
	long NProtectionCurve_Error = -4, ProtectionCurveTerm_Error = -5, ProtectionCurve_Error = -6;
	long DataFlag_Error = -7, NHazardRate_Error = -8, HazardRateTerm_Error = -9, HazardRate_Error = -10, CalcQMethod_Error = -11;
	long NRefZero_Error = -12, RefZeroTerm_Error = -13, ZeroRiskFree_Error = -14, ZeroRiskyBond_Error = -15, DefaultRateCalcMethod_Error = -16;
	long Recovery_Error = -17, NCPN_Ann_Error = -18, Maturity_Error = -19;

	if (NPremiumCurve < 1) return NPremiumCurve_Error;
	if (PremiumCurveTerm[0] < 0.0) return PremiumCurveTerm_Error;
	for (i = 1; i < NPremiumCurve; i++)
	{
		if (PremiumCurveTerm[i] < PremiumCurveTerm[i - 1]) return PremiumCurveTerm_Error;
	}

	if (NProtectionCurve < 1) return NProtectionCurve_Error;
	if (ProtectionCurveTerm[0] < 0.0) return ProtectionCurveTerm_Error;
	for (i = 1; i < NProtectionCurve; i++)
	{
		if (ProtectionCurveTerm[i] < ProtectionCurveTerm[i - 1]) return ProtectionCurveTerm_Error;
	}

	if (DataFlag == 0)
	{
		if (NHazardRate < 1) return NHazardRate_Error;

		if (HazardRateTerm[0] < 0.0) return HazardRateTerm_Error;

		for (i = 0; i < NHazardRate; i++)
		{
			if (HazardRateTerm[i] < HazardRateTerm[i - 1]) return HazardRateTerm_Error;
		}

	}
	else
	{
		if (NRefZero < 1) return (NRefZero_Error);

		if (RefZeroTerm[0] < 0.0) return RefZeroTerm_Error;

		for (i = 0; i < NRefZero; i++)
		{
			if (RefZeroTerm[i] < RefZeroTerm[i - 1]) return RefZeroTerm_Error;
			if (ZeroRiskFree[i] > ZeroRiskyBond[i]) return RefZeroTerm_Error;
		}
	}
	if (Recovery < 0.0 || Recovery > 1.0) return Recovery_Error;
	if (PrevCDSSpread < 0.0) return -20;

	return 0;
}

DLLEXPORT(long) Calc_CDS_Spread(
	long NPremiumCurve,				// Premium Leg Ŀ�� Term ����
	double* PremiumCurveTerm,		// Premium Leg Ŀ�� Term Array
	double* PremiumCurve,			// Premium Leg Ŀ�� Rate Array

	long NProtectionCurve,			// Protection Leg Ŀ�� Term ����
	double* ProtectionCurveTerm,	// Protection Leg Ŀ�� Term
	double* ProtectionCurve,		// Protection Leg Ŀ�� Rate Array

	long DataFlag,					// Credit ��ǲ ���� 0: Hazard Rate, 1: ����,������ݸ�
	long NHazardRate,				// Hazard Rate Term ����
	double* HazardRateTerm,			// Hazard Rate Term Array
	double* HazardRate,				// Hazard Rate Array
	long CalcQMethod,				// 0:������ = e^(-lambda * t) ���, 1:������ = 1 - lambda * t ���

	long NRefZero,					// CalcQMethod == 1�� �� ���αݸ�����
	double* RefZeroTerm,			// ZeroRate Term Array
	double* ZeroRiskFree,			// RiskFree ZeroRate Array
	double* ZeroRiskyBond,			// Risky ZeroRate Array
	long DefaultRateCalcMethod,		// HazardRate ������ 0:RiskyBond Pricer 1: ���ܻ���

	double Recovery,				// ȸ����
	long ScheduleInputFlag,			// �������Է¹�� 0: �����Է�, 1: �����Է�
	long NCPN_Ann,					// ScheduleInputFlag0: �� �������� ��
	double Maturity,				// ScheduleInputFlag0: ����
	long NSchedule,					// ScheduleInputFlag1: �����ٰ���
	long* ResetDateYYYYMMDD,		// ScheduleInputFlag1: ������ Array
	long* PayDateYYYYMMDD,			// ScheduleInputFlag1: ������ Array
	long PricingDateYYYYMMDD,		// ScheduleInputFlag1: ���ݰ���� 

	long NHoliday,
	long* HolidayYYYYMMDD,

	long TextFlag,					// �ؽ�ƮDumpFlag (�̿ϼ�)
	long GreekFlag,					// Greek����Flag
	double* Result_Value,			// ��� 0: Result_Spread 1:Premium_Leg 2:Protection Leg
	double* ResultHazardRate,		// ����� Hazard Rate Array
	double* Premium_Schedule,		// �����̾������� Array
	double NotionalAmount			// �׸鰡��
)
{
	double Premium_Leg = 0.0;
	double Protection_Leg = 0.0;
	// CDS Spread ����ϴ� �Լ��� GreekFlag 0���� ����
	GreekFlag = 0;
	double ResultGreeks[10] = { 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 };

	long i;

	long ResultCode = Inputcheck_Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve, NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
		DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
		NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, DefaultRateCalcMethod,
		Recovery, NCPN_Ann, Maturity, 0.01, 1,
		TextFlag, GreekFlag);

	for (i = 0; i < NSchedule; i++)
	{
		if (ResetDateYYYYMMDD[i] < 19000101) ResetDateYYYYMMDD[i] = ExcelDateToCDate(ResetDateYYYYMMDD[i]);
		if (PayDateYYYYMMDD[i] < 19000101) PayDateYYYYMMDD[i] = ExcelDateToCDate(PayDateYYYYMMDD[i]);
		if (PricingDateYYYYMMDD < 19000101) PricingDateYYYYMMDD = ExcelDateToCDate(PricingDateYYYYMMDD);
	}

	for (i = 0; i < NHoliday; i++) if (HolidayYYYYMMDD[i] < 19000101) HolidayYYYYMMDD[i] = ExcelDateToCDate(HolidayYYYYMMDD[i]);

	if (ResultCode < 0) return ResultCode;

	double Result_Spread;

	if (DataFlag == 0)
	{
		Result_Spread = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Premium_Leg, &Protection_Leg, Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);
		if (CalcQMethod == 0)
		{
			for (i = 0; i < NHazardRate; i++)
			{
				ResultHazardRate[i] = 1.0 - exp(-HazardRate[i] * HazardRateTerm[i]);
			}
		}
		else
		{
			for (i = 0; i < NHazardRate; i++)
			{
				ResultHazardRate[i] = HazardRate[i] * HazardRateTerm[i];
			}
		}
	}
	else
	{
		Result_Spread = Calc_CDS_From_CreditSpread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, DefaultRateCalcMethod,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Premium_Leg, &Protection_Leg, ResultHazardRate, Premium_Schedule, GreekFlag, ResultGreeks, 0.0, NotionalAmount, NHoliday, HolidayYYYYMMDD);
	}

	Result_Value[0] = Result_Spread;
	Result_Value[1] = Premium_Leg;
	Result_Value[2] = Protection_Leg;
	Result_Value[3] = 0.0;
	Result_Value[4] = 0.0;
	Result_Value[5] = 0.0;

	return 1;
}



DLLEXPORT(long) Calc_OLD_CDS_Value(
	long NPremiumCurve,				// Premium Leg Ŀ�� Term ����
	double* PremiumCurveTerm,		// Premium Leg Ŀ�� Term Array
	double* PremiumCurve,			// Premium Leg Ŀ�� Rate Array

	long NProtectionCurve,			// Protection Leg Ŀ�� Term ����
	double* ProtectionCurveTerm,	// Protection Leg Ŀ�� Term
	double* ProtectionCurve,		// Protection Leg Ŀ�� Rate Array

	long DataFlag,					// Credit ��ǲ ���� 0: Hazard Rate,1: ����,������ݸ�
	long NHazardRate,				// Hazard Rate Term ����
	double* HazardRateTerm,			// Hazard Rate Term Array
	double* HazardRate,				// Hazard Rate Array
	long CalcQMethod,				// 0:������ e^(-H * t) ���, 1:������ 1 - H * t ���

	long NRefZero,					// CalcQMethod == 1�� �� ���αݸ�����
	double* RefZeroTerm,			// ZeroRate Term Array
	double* ZeroRiskFree,			// RiskFree ZeroRate Array
	double* ZeroRiskyBond,			// Risky ZeroRate Array
	long DefaultRateCalcMethod,		// HazardRate ������ 0:RiskyBond Pricer 1: ���ܻ���

	double Recovery,				// ȸ����
	long ScheduleInputFlag,			// �������Է¹�� 0: �����Է�, 1: �����Է�
	long NCPN_Ann,					// ScheduleInputFlag0: �� �������� ��
	double Maturity,				// ScheduleInputFlag0: ����
	long NSchedule,					// ScheduleInputFlag1: �����ٰ���
	long* ResetDateYYYYMMDD,		// ScheduleInputFlag1: ������ Array
	long* PayDateYYYYMMDD,			// ScheduleInputFlag1: ������ Array
	long PricingDateYYYYMMDD,		// ScheduleInputFlag1: ���ݰ���� 

	long NHoliday,
	long *HolidayYYYYMMDD,

	double OLD_CDS_Spread,			// ���� ��� CDS Spread
	long Protection_Position,		// ������1: �� -1: ��
	long TextFlag,					// TextFlag (�̿ϼ�)
	long GreekFlag,					// Greek����Flag
	double* Result_Value,			// ��� [0]: Result_Spread [1]:Premium_Leg [2]:Protection Leg
	double* ResultHazardRate,		// ����� Hazard Rate Array
	double* ResultGreeks,			// [0~2]IR PV01 Net, Pre, Pro [3~5]�ε��� PV01 Net, Pre, Pro 
	double* Premium_Schedule,		// �����̾������� Array
	double NotionalAmount			// �׸鰡��
)
{

	double Premium_Leg = 0.0;
	double Protection_Leg = 0.0;
	// Greeks�� �ӽú���
	double Temp_Premium_Leg;
	double Temp_Protection_Leg;

	double* Temp_Premium_Schedule;
	double* PremiumCurveRup;
	double* PremiumCurveRdn;
	double* ProtectionCurveRup;
	double* ProtectionCurveRdn;
	double* HazardUp;
	double* HazardDn;
	//
	double RPV01;
	double Protection_Value;
	double Premium_Value;
	double Value_ProtectionBuyer;
	long N_PremiumNode = (long)((double)NCPN_Ann * Maturity + 0.5) + 1;

	double P_Rup;
	double P_Rdn;

	long i, j;


	long ResultCode = Inputcheck_Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve, NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
		DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
		NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, DefaultRateCalcMethod,
		Recovery, NCPN_Ann, Maturity, OLD_CDS_Spread, Protection_Position,
		TextFlag, GreekFlag);
	
	for (i = 0; i < NSchedule; i++)
	{
		if (ResetDateYYYYMMDD[i] < 19000101) ResetDateYYYYMMDD[i] = ExcelDateToCDate(ResetDateYYYYMMDD[i]);
		if (PayDateYYYYMMDD[i] < 19000101) PayDateYYYYMMDD[i] = ExcelDateToCDate(PayDateYYYYMMDD[i]);
		if (PricingDateYYYYMMDD < 19000101) PricingDateYYYYMMDD = ExcelDateToCDate(PricingDateYYYYMMDD);
	}

	if (ResultCode < 0) return ResultCode;

	double Result_Spread;
	double Protection_Value_U;
	double Protection_Value_D;
	// Greeks�� �ӽú���
	double Premium_Value_U;
	double Premium_Value_D;
	double Value_ProtectionBuyer_U;
	double Value_ProtectionBuyer_D;
	double RPV01_U;
	double RPV01_D;
	
	//////////////////////////////////////////////////////////////////////
	// DataFlag0 : Hazard Rate �ԷµǾ�����, DataFlag1: ZeroRate Risky - Rf �ԷµǾ�����
	//////////////////////////////////////////////////////////////////////

	if (DataFlag == 0)
	{
		///////////////////////////////////
		// Value ����� ���� ������� Premium_Leg, Protection_Leg, CDS Spread ���
		///////////////////////////////////

		Result_Spread = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Premium_Leg, &Protection_Leg, Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);
		if (CalcQMethod == 0)
		{
			for (i = 0; i < NHazardRate; i++)
			{
				ResultHazardRate[i] = 1.0 - exp(-HazardRate[i] * HazardRateTerm[i]);
			}
		}
		else
		{
			for (i = 0; i < NHazardRate; i++)
			{
				ResultHazardRate[i] = HazardRate[i] * HazardRateTerm[i];
			}
		}


		if (GreekFlag >= 1)
		{
			//////////////////////////////////////////////////////////////////////
			// OLD CDS �� �׸��� ��� -> Value = ProtectionValue - ����������/���������� * ��PremiumValue
			//////////////////////////////////////////////////////////////////////

			Temp_Premium_Schedule = (double*)malloc(sizeof(double) * (long)(NCPN_Ann * Maturity + 2.0));
			PremiumCurveRup = (double*)malloc(sizeof(double) * NPremiumCurve);
			PremiumCurveRdn = (double*)malloc(sizeof(double) * NPremiumCurve);
			ProtectionCurveRup = (double*)malloc(sizeof(double) * NProtectionCurve);
			ProtectionCurveRdn = (double*)malloc(sizeof(double) * NProtectionCurve);
			HazardUp = (double*)malloc(sizeof(double) * NHazardRate);
			HazardDn = (double*)malloc(sizeof(double) * NHazardRate);

			for (i = 0; i < NPremiumCurve; i++)
			{
				PremiumCurveRup[i] = PremiumCurve[i] + 0.0001;
				PremiumCurveRdn[i] = PremiumCurve[i] - 0.0001;
			}

			for (i = 0; i < NProtectionCurve; i++)
			{
				ProtectionCurveRup[i] = ProtectionCurve[i] + 0.0001;
				ProtectionCurveRdn[i] = ProtectionCurve[i] - 0.0001;
			}

			for (i = 0; i < NHazardRate; i++)
			{
				HazardUp[i] = HazardRate[i] + 0.0001;
				HazardDn[i] = HazardRate[i] - 0.0001;
			}

			P_Rup = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRup,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRup,
				DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

			Protection_Value_U = Temp_Protection_Leg;
			RPV01_U = Temp_Premium_Leg / P_Rup;
			Premium_Value_U = OLD_CDS_Spread * RPV01_U;
			Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

			P_Rdn = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRdn,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRdn,
				DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

			Protection_Value_D = Temp_Protection_Leg;
			RPV01_D = Temp_Premium_Leg / P_Rdn;
			Premium_Value_D = OLD_CDS_Spread * RPV01_D;
			Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

			ResultGreeks[0] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
			ResultGreeks[1] = (Premium_Value_U - Premium_Value_D) / 2.0;
			ResultGreeks[2] = (Protection_Value_U - Protection_Value_D) / 2.0;

			P_Rup = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				DataFlag, NHazardRate, HazardRateTerm, HazardUp, CalcQMethod,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

			Protection_Value_U = Temp_Protection_Leg;
			RPV01_U = Temp_Premium_Leg / P_Rup;
			Premium_Value_U = OLD_CDS_Spread * RPV01_U;
			Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

			P_Rdn = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				DataFlag, NHazardRate, HazardRateTerm, HazardDn, CalcQMethod,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

			Protection_Value_D = Temp_Protection_Leg;
			RPV01_D = Temp_Premium_Leg / P_Rdn;
			Premium_Value_D = OLD_CDS_Spread * RPV01_D;
			Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

			ResultGreeks[3] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
			ResultGreeks[4] = (Premium_Value_U - Premium_Value_D) / 2.0;
			ResultGreeks[5] = (Protection_Value_U - Protection_Value_D) / 2.0;

			if (GreekFlag > 1 && (NPremiumCurve == NProtectionCurve))
			{
				for (i = 0; i < NPremiumCurve; i++)
				{
					for (j = 0; j < NPremiumCurve; j++)
					{
						if (i == j)
						{
							PremiumCurveRup[j] = PremiumCurve[j] + 0.0001;
							PremiumCurveRdn[j] = PremiumCurve[j] - 0.0001;
							ProtectionCurveRup[j] = ProtectionCurve[j] + 0.0001;
							ProtectionCurveRdn[j] = ProtectionCurve[j] - 0.0001;
						}
						else
						{
							PremiumCurveRup[j] = PremiumCurve[j]; 
							PremiumCurveRdn[j] = PremiumCurve[j];
							ProtectionCurveRup[j] = ProtectionCurve[j];
							ProtectionCurveRdn[j] = ProtectionCurve[j];
						}
					}

					P_Rup = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRup,
						NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRup,
						DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
						Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

					Protection_Value_U = Temp_Protection_Leg;
					RPV01_U = Temp_Premium_Leg / P_Rup;
					Premium_Value_U = OLD_CDS_Spread * RPV01_U;
					Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

					P_Rdn = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurveRdn,
						NProtectionCurve, ProtectionCurveTerm, ProtectionCurveRdn,
						DataFlag, NHazardRate, HazardRateTerm, HazardRate, CalcQMethod,
						Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

					Protection_Value_D = Temp_Protection_Leg;
					RPV01_D = Temp_Premium_Leg / P_Rdn;
					Premium_Value_D = OLD_CDS_Spread * RPV01_D;
					Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

					ResultGreeks[6+3*i] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
					ResultGreeks[7+3*i] = (Premium_Value_U - Premium_Value_D) / 2.0;
					ResultGreeks[8+3*i] = (Protection_Value_U - Protection_Value_D) / 2.0;
				}

				for (i = 0; i < NHazardRate; i++)
				{
					for (j = 0; j < NHazardRate; j++)
					{
						if (i == j)
						{
							HazardUp[j] = HazardRate[j] + 0.0001;
							HazardDn[j] = HazardRate[j] - 0.0001;
						}
						else
						{
							HazardUp[j] = HazardRate[j];
							HazardDn[j] = HazardRate[j];
						}
					}

					P_Rup = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
						NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
						DataFlag, NHazardRate, HazardRateTerm, HazardUp, CalcQMethod,
						Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

					Protection_Value_U = Temp_Protection_Leg;
					RPV01_U = Temp_Premium_Leg / P_Rup;
					Premium_Value_U = OLD_CDS_Spread * RPV01_U;
					Value_ProtectionBuyer_U = Protection_Value_U - Premium_Value_U;

					P_Rdn = Calc_CDS_From_Hazard(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
						NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
						DataFlag, NHazardRate, HazardRateTerm, HazardDn, CalcQMethod,
						Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Temp_Premium_Leg, &Temp_Protection_Leg, Temp_Premium_Schedule, NotionalAmount, NHoliday, HolidayYYYYMMDD);

					Protection_Value_D = Temp_Protection_Leg;
					RPV01_D = Temp_Premium_Leg / P_Rdn;
					Premium_Value_D = OLD_CDS_Spread * RPV01_D;
					Value_ProtectionBuyer_D = Protection_Value_D - Premium_Value_D;

					ResultGreeks[6 + 3 * NPremiumCurve + i] = (Value_ProtectionBuyer_U - Value_ProtectionBuyer_D) / 2.0;
					ResultGreeks[7 + 3 * NPremiumCurve + i] = (Premium_Value_U - Premium_Value_D) / 2.0;
					ResultGreeks[8 + 3 * NPremiumCurve + i] = (Protection_Value_U - Protection_Value_D) / 2.0;
				}
			}

			if (Temp_Premium_Schedule) free(Temp_Premium_Schedule);
			if (PremiumCurveRup) free(PremiumCurveRup);
			if (PremiumCurveRdn) free(PremiumCurveRdn);
			if (ProtectionCurveRup) free(ProtectionCurveRup);
			if (ProtectionCurveRdn) free(ProtectionCurveRdn);

		}
	}
	else
	{
		Result_Spread = Calc_CDS_From_CreditSpread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
			NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
			DataFlag, NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, DefaultRateCalcMethod,
			Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateYYYYMMDD, PayDateYYYYMMDD, PricingDateYYYYMMDD, &Premium_Leg, &Protection_Leg, ResultHazardRate, Premium_Schedule, GreekFlag, ResultGreeks, OLD_CDS_Spread, NotionalAmount, NHoliday, HolidayYYYYMMDD);
	}

	Result_Value[0] = Result_Spread;
	Result_Value[1] = Premium_Leg;
	Result_Value[2] = Protection_Leg;

	Protection_Value = Protection_Leg;
	RPV01 = Premium_Leg / Result_Spread;
	Premium_Value = OLD_CDS_Spread * RPV01;
	for (i = 0; i < N_PremiumNode - 1; i++)
	{
		Premium_Schedule[i] = OLD_CDS_Spread / Result_Spread * Premium_Schedule[i];
	}
	Result_Value[3] = Premium_Value;
	Result_Value[4] = Protection_Value;
	Value_ProtectionBuyer = Protection_Value - Premium_Value;
	if (Protection_Position == 1) Result_Value[5] = Value_ProtectionBuyer;
	else Result_Value[5] = -Value_ProtectionBuyer;


	return 1;
}

long Inputcheck_Hazard_Rate_From_CDSCurve(
	long NPremiumCurve,
	double* PremiumCurveTerm,
	double* PremiumCurve,

	long NProtectionCurve,
	double* ProtectionCurveTerm,
	double* ProtectionCurve,

	long NCDSCurve,
	double* CDSCurveTerm,
	double* CDSCurve,

	double Recovery,
	long HazardRateCalcFlag,
	long NCPN_Ann)
{
	long i;
	long NPremiumCurve_Error = -1, PremiumCurveTerm_Error = -2, PremiumCurve_Error = -3;
	long NProtectionCurve_Error = -4, ProtectionCurveTerm_Error = -5, ProtectionCurve_Error = -6;
	long NCDSCurve_Error = -7, CDSCurveTerm_Error = -8, CDSCurve_Error = -9;
	long Recovery_Error = -10, HazardRateCalcFlag_Error = -11, NCPN_Ann_Error = -12, TextFlag_Error = -13, GreekFlag_Error = -14;

	if (NPremiumCurve < 1) return NPremiumCurve_Error;
	if (PremiumCurveTerm[0] < 0.0) return PremiumCurveTerm_Error;
	for (i = 1; i < NPremiumCurve; i++)
	{
		if (PremiumCurveTerm[i] < PremiumCurveTerm[i - 1]) return PremiumCurveTerm_Error;
	}

	if (NProtectionCurve < 1) return NProtectionCurve_Error;
	if (ProtectionCurveTerm[0] < 0.0) return ProtectionCurveTerm_Error;
	for (i = 1; i < NProtectionCurve; i++)
	{
		if (ProtectionCurveTerm[i] < ProtectionCurveTerm[i - 1]) return ProtectionCurveTerm_Error;
	}

	if (NCDSCurve < 1) return NCDSCurve_Error;
	if (CDSCurveTerm[0] < 0.0) return ProtectionCurveTerm_Error;
	for (i = 1; i < NCDSCurve; i++)
	{
		if (CDSCurveTerm[i] < CDSCurveTerm[i - 1]) return CDSCurveTerm_Error;
	}

	if (Recovery < 0.0 || Recovery > 1.0) return Recovery_Error;

	return 1;
}

DLLEXPORT(long) Calc_Hazard_Rate_From_CDSCurve(
	long PricingDateYYYYMMDD,	

	long NPremiumCurve,				// Premium Leg Ŀ�� Term ����
	double* PremiumCurveTerm,		// Premium Leg Ŀ�� Term Array
	double* PremiumCurve,			// Premium Leg Ŀ�� Rate Array

	long NProtectionCurve,			// Protection Leg Ŀ�� Term ����
	double* ProtectionCurveTerm,	// Protection Leg Ŀ�� Term
	double* ProtectionCurve,		// Protection Leg Ŀ�� Rate Array

	long NCDSCurve,					// CDS Term ����
	double* CDSCurveTerm,			// CDS Term Array
	double* CDSCurve,				// CDS Spread Array

	double Recovery,				// Recovery Rate
	long HazardRateCalcFlag,		// Hazard Rate Calc ��� 0: Continuous Annual Hazard Rate 1: �ܸ� �Ļ�Ȯ��
	long NCPN_Ann,					// �� �������� ��			

	long NHoliday,					// Holiday����
	long* HolidayYYYYMMDD,			// Holiday Array (YYYYMMDD Type)

	double* ResultHazardTerm,		// OutPut Hazard Term
	double* ResultHazard			// OutPut Hazard Rate
)
{
	long i, j;

	////////////////
	// ����üũ
	////////////////

	long ResultCode = Inputcheck_Hazard_Rate_From_CDSCurve(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
		NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
		NCDSCurve, CDSCurveTerm, CDSCurve,
		Recovery, HazardRateCalcFlag, NCPN_Ann);

	if (ResultCode < 0) return ResultCode;

	double ObjValue;
	double value_a;
	double value_b;
	double value;
	double dblErrorRange = 0.000001;

	long NHazardRate;
	double* HazardRate = (double*)malloc(sizeof(double) * NCDSCurve);
	double* HazardRateTerm = CDSCurveTerm;
	double* ResultHazardRate = (double*)malloc(sizeof(double) * NCDSCurve);

	double Price1, Price2, Error1, Error2, Price, Error;
	double Maturity;
	double* Premium_Schedule = (double*)malloc(sizeof(double) * ((long)(NCPN_Ann * CDSCurveTerm[NCDSCurve - 1] + 0.5) + 2));
	long TempNumber = 0;
	long EndFlag = 0;

	////////////////
	// ���� ������
	////////////////

	long NRefZero = 1;
	double RefZeroTerm[1] = { 0.0 };
	double ZeroRiskFree[1] = { 0.0 };
	double ZeroRiskyBond[1] = { 0.0 };

	double TempResultPrice[10] = { 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 };
	double MinimumValue = 0.0;
	long ScheduleInputFlag = 0;
	long NSchedule = 0;
	long* ResetDateExcelDate = &NSchedule;
	long* PayDateExcelDate = &NSchedule;
	long MaturityDateYYYYMMDD;
	////////////////

	for (i = 0; i < NCDSCurve; i++)
		ResultHazardTerm[i] = CDSCurveTerm[i];

	for (i = 0; i < NCDSCurve; i++)
	{
		value_a = 0.00001;
		value_b = 0.99;

		if (i > 0) MinimumValue = 0.;// = value * Maturity / CDSCurveTerm[i]; // e^(-lambda2 * T2) < e^(-lambda1 * T1) ����Ȯ���� �������ؾ���
		
		EndFlag = 0;
		NHazardRate = i + 1;
		Maturity = CDSCurveTerm[i];
		if (Maturity < 1000) MaturityDateYYYYMMDD = EDate_Cpp(PricingDateYYYYMMDD, (long)(Maturity * 12.0 + 0.1));
		else if (Maturity < 19000101) MaturityDateYYYYMMDD = ExcelDateToCDate((long)(Maturity + 0.1));
		else MaturityDateYYYYMMDD = (long)(Maturity + 0.1);
		ResultHazardTerm[i] = ((double)DayCountAtoB(PricingDateYYYYMMDD, MaturityDateYYYYMMDD)) / 365.0;
		ObjValue = CDSCurve[i];
		HazardRate[i] = value_a;
		if (HazardRateCalcFlag == 0)
		{
			TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				0, NHazardRate, HazardRateTerm, HazardRate, 0,
				NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
		}
		else
		{
			TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				0, NHazardRate, HazardRateTerm, HazardRate, 1,
				NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
		}

		Price1 = TempResultPrice[0];
		Error1 = ObjValue - Price1;
		if (fabs(Error1) < dblErrorRange)
		{
			ResultHazard[i] = value_a;
			EndFlag = 1;
		}

		HazardRate[i] = value_b;
		if (HazardRateCalcFlag == 0)
		{
			TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				0, NHazardRate, HazardRateTerm, HazardRate, 0,
				NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
		}
		else
		{
			TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
				NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
				0, NHazardRate, HazardRateTerm, HazardRate, 1,
				NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
				Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
		}
		Price2 = TempResultPrice[0];
		Error2 = ObjValue - Price2;
		if (fabs(Error2) < dblErrorRange)
		{
			ResultHazard[i] = value_b;
			EndFlag = 1;
		}

		value = (value_a + value_b) / 2.0;
		for (j = 0; j < 2000; j++)
		{
			HazardRate[i] = value;
			if (HazardRateCalcFlag == 0)
			{
				TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
					NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
					0, NHazardRate, HazardRateTerm, HazardRate, 0,
					NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
					Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
			}
			else
			{
				TempNumber = Calc_CDS_Spread(NPremiumCurve, PremiumCurveTerm, PremiumCurve,
					NProtectionCurve, ProtectionCurveTerm, ProtectionCurve,
					0, NHazardRate, HazardRateTerm, HazardRate, 1,
					NRefZero, RefZeroTerm, ZeroRiskFree, ZeroRiskyBond, 0,
					Recovery, ScheduleInputFlag, NCPN_Ann, Maturity, NSchedule, ResetDateExcelDate, PayDateExcelDate, PricingDateYYYYMMDD, NHoliday, HolidayYYYYMMDD, 0, 0, TempResultPrice, ResultHazardRate, Premium_Schedule, 1.0);
			}

			Price = TempResultPrice[0];
			Error = ObjValue - Price;
			if (fabs(Error) < dblErrorRange)
			{
				ResultHazard[i] = value;
				break;
			}
			else
			{
				if (Error > 0)
				{
					value_a = max(value, MinimumValue);
					value = (value_a + value_b) / 2.0;
				}
				else
				{
					value_b = value;
					value = (value_a + value_b) / 2.0;
				}
			}
			if (TempNumber < 0 && i > 0)
			{
				ResultHazard[i] = ResultHazard[i - 1];
				break;
			}
		}
		if (j == 2000 && i > 0)
		{
			ResultHazard[i] = ResultHazard[i - 1];
		}
	}

	if (HazardRate) free(HazardRate);
	if (ResultHazardRate) free(ResultHazardRate);
	if (Premium_Schedule) free(Premium_Schedule);

	return 1;
}