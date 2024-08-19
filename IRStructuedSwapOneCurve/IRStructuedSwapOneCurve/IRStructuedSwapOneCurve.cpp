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

	if (NHWVol == 1 || kappa > 0.1)
	{
		vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t);
		//RHS = -vol * vol * (exp(-kappa * T) - exp(-kappa * t)) * (exp(-kappa * T) - exp(-kappa * t)) * (exp(2.0 * kappa * t) - 1.0) / (4.0 * kappa * kappa * kappa);
		//RHS = 0.5 * vol * vol / (kappa * kappa) * (2.0 / kappa * exp(-kappa * (T - t)) - 0.5 / kappa * exp(-2.0 * kappa * (T - t)) - 2.0 / kappa * exp(-kappa * T) + 0.5 / kappa * exp(-2.0 * kappa * T) + 2.0 / kappa * exp(-kappa * t) - 0.5 / kappa * exp(-2.0 * kappa * t) - 1.5 / kappa);
		RHS = 0.5 * (V_t_T(kappa, kappa, t, T, vol, vol) - V_t_T(kappa, kappa, 0, T, vol, vol) + V_t_T(kappa, kappa, 0, t, vol, vol));
	}
	else
	{
		RHS = 0.0;
		long NInteg = 10.0;
		double u = t;
		double du = (T - t) / ((double)NInteg);
		double Bst, BsT;
		for (i = 0; i < NInteg; i++)
		{
			vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
			Bst = B_s_to_t(kappa, u, t);
			BsT = B_s_to_t(kappa, u, T);
			RHS += 0.5 * vol * vol * (Bst * Bst - BsT * BsT) * du;
			u = u + du;
		}

		//double v1, v2, var;
		//v1 = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t);
		//v2 = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, T);
		//var = (T * v2 * v2 - t * v1 * v1) / (T - t);
		//if (var > 0.0) vol = sqrt(var);
		//else vol = 0.5 * v1 + 0.5 * v2;
		//RHS = 0.5 * vol * vol / (kappa * kappa) * (2.0 / kappa * exp(-kappa * (T - t)) - 0.5 / kappa * exp(-2.0 * kappa * (T - t)) - 2.0 / kappa * exp(-kappa * T) + 0.5 / kappa * exp(-2.0 * kappa * T) + 2.0 / kappa * exp(-kappa * t) - 0.5 / kappa * exp(-2.0 * kappa * t) - 1.5 / kappa);
		//RHS = 0.5 * (V_t_T(kappa, kappa, t, T, vol, vol) - V_t_T(kappa, kappa, 0, T, vol, vol) + V_t_T(kappa, kappa, 0, t, vol, vol));
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
	double Bst, BsT, vol, vol2;
	double RHS = 0.0;
	double s, ds;

	long NInteg = 10.0;
	double u = t;
	double du = (T - t) / ((double)NInteg);
	RHS = 0.0;
	if (NHWVol == 1)
	{
		vol = 0.5 * Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t) + 0.5 * Interpolate_Linear(HWVolTerm, HWVol, NHWVol, T);
		vol2 = 0.5 * Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t) + 0.5 * Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, T);
	}
	else
	{
		vol = 0.5 * Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t);
		vol2 = 0.5 * Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t);
	}

	//RHS = -2.0 * rho * 0.5 * vol * vol2 / (kappa * kappa2 * (kappa + kappa2)) * (exp(-kappa * T) - exp(-kappa * t)) * (exp(-kappa2 * T) - exp(-kappa2 * t)) * (exp((kappa + kappa2) * t) - 1.0);
	RHS = 2.0 * rho * 0.5 * (V_t_T(kappa, kappa2, t, T, vol, vol2) - V_t_T(kappa, kappa2, 0, T, vol, vol2) + V_t_T(kappa, kappa2, 0, t, vol, vol2));
	return RHS;
}

double HW_Rate(
	long ReferenceType,
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
		PtT = PV_t_T[0] * exp(-ShortRate * B_t_T[0] + QVTerm[0]);
		if (HW2FFlag > 0) PtT = PtT * exp(-ShortRate2F * B_t_T_2F[0] + QVTerm_2F[0] + CrossTerm_2F[0]);

		if (dt[0] < 1.0) ResultRate = (1.0 - PtT) / (dt[0] * PtT);
		else ResultRate = -1.0 / dt[0] * log(PtT);
	}

	return ResultRate;
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

long MyFunc(
	long PriceDate,							// PricingDate As YYYYMMDD
	long EffectiveDate,						// EffeciveDate As YYYYMMDD
	long Maturity,							// Maturity As YYYYMMDD
	long NAFlag,							// Notional Use Flag
	double NA,								// Notional Amount

	long* NAdditionalHolidays,				// RcvLeg, PayLeg Additional NHolidays Custom(len = 2)
	long* AdditionalHolidays,				// RcvLeg, PayLeg Additional Holidays Custom(len = 2)
	long* NationFlag,						// RcvLeg, PayLeg Nation Flag 0 : KRW, 1 : USD, ...
	long* NumCpnAnn,						// Number Coupon of 1y (len = 2)
	double* MaxLossRefRcvPay,				// MaxLossRet of Rcv, Pay Leg (len = 4)

	double* MultipleRatefixPayoffRcvPay,	// Slope of Fixing And Payoff of Rcv, PayLeg(len = 4)
	long* DayCountRcvPay,					// DayCountFraction of Rcv, PayLeg (len = 2)
	long* PowerSpreadFlagRcvPay,			// PowerSpreadFlag Rcv, PayLeg (len = 2)
	double* RangeMaxMinRcvPay,				// FixingRate Max and Min (len = 4)
	double* InfoRefRateRcvPay,				// RefRate NCpnAn, T, T1, T2 of Rcv, PayLeg(len = 8)

	double RcvLegFixedRate,					// Receive Leg Fixed Coupon Rate
	double RcvLegRangeCoupon,				// Rcv Leg Range OK FixedCoupon Rate
	long RcvLegStructuredFlag,				// Rcv Leg Structured Coupon Flag
	double PayLegFixedRate,					// Pay Leg Fixed Coupon Rate
	double PayLegRangeCoupon,				// Pay Leg Range OK FixedCoupon Rate

	long PayLegStructuredFlag,				// Pay Leg Structured Coupon Flag
	long Phase2Date,						// Phase2Date
	double Phase2RcvLegFixedRate,			// Receive Leg Fixed Coupon Rate
	double Phase2RcvLegRangeCoupon,			// Rcv Leg Range OK FixedCoupon Rate
	long Phase2RcvLegStructuredFlag,		// Rcv Leg Structured Coupon Flag

	double Phase2PayLegFixedRate,			// Pay Leg Fixed Coupon Rate
	double Phase2PayLegRangeCoupon,			// Pay Leg Range OK FixedCoupon Rate
	long Phase2PayLegStructuredFlag,		// Pay Leg Structured Coupon Flag
	long NOption,							// Number of Option
	long* OptionDate,						// OptionDateArray As YYYYMMDD

	long* OptionPayDate,					// OptionPayDateArray
	long OptionType,						// 0 : Payer have option, 1: Receiver
	long NRcvRateHistory,					// Number of RcvRate History
	long* RcvRateHistoryDate,				// Rcv FixingRate HistoryDate Array
	double* RcvRateHistory,					// Rcv FixingRate History Array

	long NPayRateHistory,					// Number of RcvRate History
	long* PayRateHistoryDate,				// Pay FixingRate HistoryDate Array
	double* PayRateHistory,					// Pay FixingRate History Array
	long NZeroRate,
	double* ZeroTerm,

	double* ZeroRate,
	long HW2FFlag,
	long NHWVol,
	double* HWVolTerm,
	double* HWVol,

	double* kappa,
	double FactorCorrelation,
	long* ResultCpnDateRcv,
	long* ResultCpnDatePay
)
{
	long i, j, k, n;
	long idx1, idx2;
	long NGreed = 200;

	double* InfoRefRateRcv = InfoRefRateRcvPay;
	double* InfoRefRatePay = InfoRefRateRcvPay + 4;

	double* MaxLossRetRcv = MaxLossRefRcvPay;
	double* MaxLossRefPay = MaxLossRefRcvPay + 2;

	double* MultipleRatefixPayoffRcv = MultipleRatefixPayoffRcvPay;
	double* MultipleRatefixPayoffPay = MultipleRatefixPayoffRcvPay + 2;

	double* RangeMaxMinRcv = RangeMaxMinRcvPay;
	double* RangeMaxMinPay = RangeMaxMinRcvPay + 2;

	double NCPN_ANN_Rcv = InfoRefRateRcv[0];
	double Maturity_Rcv = InfoRefRateRcv[1];
	double Maturity1_Rcv = InfoRefRateRcv[2];
	double Maturity2_Rcv = InfoRefRateRcv[3];

	double NCPN_ANN_Pay = InfoRefRatePay[0];
	double Maturity_Pay = InfoRefRatePay[1];
	double Maturity1_Pay = InfoRefRatePay[2];
	double Maturity2_Pay = InfoRefRatePay[3];

	double kappa1 = kappa[0];
	double kappa2;
	if (HW2FFlag > 0) kappa2 = kappa[1];
	else kappa2 = kappa[0];
	double* HWVol2 = HWVol + NHWVol;

	long NTotalHoliday[2] = { 0, 0 };
	long** TotalHolidays = (long**)malloc(sizeof(long*) * 2);			// 할당1
	long nsum = 0;
	long NCpnDate[2] = { 0, 0 };
	long** CpnDate = (long**)malloc(sizeof(long*) * 2);					// 할당2
	long** CpnPayDate = (long**)malloc(sizeof(long*) * 2);				// 할당3

	long TempDate = PriceDate;
	long* TempHoliday;
	long NTempHoliday;
	long LastForwardEndDate = (long)(Maturity / 100) * 100 + EffectiveDate - (long)(EffectiveDate / 100) * 100;
	long TempExcelDate, TempYYYYMMDD;
	long NBD = 0;
	long NBDFromEndToPay = 0;
	long HolidayFlag, SaturSundayFlag;
	for (n = 0; n < 2; n++)
	{
		if (NationFlag[n] < 0)
		{
			NTotalHoliday[n] = NAdditionalHolidays[n];
			TotalHolidays[n] = (long*)malloc(sizeof(long) * max(1, NTotalHoliday[n]));
			TempHoliday = (long*)malloc(sizeof(long) * 1);
		}
		else
		{
			NTempHoliday = 0;
			NTempHoliday = Number_Holiday(EffectiveDate / 10000, Maturity / 10000 + 1, NationFlag[n]);
			TempHoliday = (long*)malloc(sizeof(long) * max(1, NTempHoliday));
			Mapping_Holiday_CType(EffectiveDate / 10000, Maturity / 10000 + 1, NationFlag[n], NTempHoliday, TempHoliday);
			NTotalHoliday[n] = NTempHoliday + NAdditionalHolidays[n];
			TotalHolidays[n] = (long*)malloc(sizeof(long) * max(1, NTotalHoliday[n]));
			for (i = 0; i < NTempHoliday; i++) TotalHolidays[n][i] = TempHoliday[i];
			for (i = 0; i < NAdditionalHolidays[n]; i++) TotalHolidays[n][i + NTempHoliday] = (AdditionalHolidays + nsum)[i];
		}
		CpnDate[n] = Malloc_CpnDate_Holiday(EffectiveDate, LastForwardEndDate, NumCpnAnn[n], NCpnDate[n], TempDate, NTotalHoliday[n], TotalHolidays[n], 1);
		CpnPayDate[n] = (long*)malloc(sizeof(long) * NCpnDate[n]);
		NBD = 0;
		if (CpnDate[n][NCpnDate[n] - 1] >= Maturity) NBD = 0;
		else
		{
			TempExcelDate = CDateToExcelDate(CpnDate[n][NCpnDate[n] - 1]);
			for (i = 0; i < 100; i++)
			{
				TempExcelDate = TempExcelDate + 1;
				TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
				SaturSundayFlag = (TempExcelDate % 7 == 1 || TempExcelDate % 7 == 0);
				HolidayFlag = isin_Longtype(TempYYYYMMDD, TotalHolidays[n], NTotalHoliday[n]);
				if (SaturSundayFlag == 0 && HolidayFlag == 0) NBD += 1;

				if (TempYYYYMMDD >= Maturity)
				{
					break;
				}
			}
		}

		NBDFromEndToPay = NBD;
		for (i = 0; i < NCpnDate[n]; i++)
		{
			if (NBDFromEndToPay == 0) CpnPayDate[n][i] - CpnDate[n][i];
			else
			{
				TempExcelDate = CDateToExcelDate(CpnDate[n][i]);
				TempYYYYMMDD = CpnDate[n][i];
				NBD = 0;
				for (j = 0; j < 100; j++)
				{
					TempExcelDate = TempExcelDate + 1;
					TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
					SaturSundayFlag = (TempExcelDate % 7 == 1 || TempExcelDate % 7 == 0);
					HolidayFlag = isin_Longtype(TempYYYYMMDD, TotalHolidays[n], NTotalHoliday[n]);
					if (SaturSundayFlag == 0 && HolidayFlag == 0) NBD += 1;
					
					if (NBD >= NBDFromEndToPay)
					{
						CpnPayDate[n][i] = TempYYYYMMDD;
						break;
					}
				}
			}
		}
		free(TempHoliday);
		nsum += NAdditionalHolidays[n];
	}

	for (i = 0; i < NCpnDate[0]; i++)
	{
		ResultCpnDateRcv[i + NCpnDate[0]] = CpnDate[0][i];
		if (i == 0) ResultCpnDateRcv[i] = EffectiveDate;
		else ResultCpnDateRcv[i] = CpnDate[0][i - 1];
		ResultCpnDateRcv[i + 2 * NCpnDate[0]] = CpnPayDate[0][i];
	}

	for (i = 0; i < NCpnDate[1]; i++)
	{
		ResultCpnDatePay[i + NCpnDate[1]] = CpnDate[1][i];
		if (i == 0) ResultCpnDatePay[i] = EffectiveDate;
		else ResultCpnDatePay[i] = CpnDate[1][i - 1];
		ResultCpnDatePay[i + 2 * NCpnDate[1]] = CpnPayDate[1][i];
	}
	long NCpnDateRcv = NCpnDate[0];
	long NCpnDatePay = NCpnDate[1];
	long* RcvFixingDate = ResultCpnDateRcv;
	long* RcvPaymentDate = ResultCpnDateRcv + 2 * NCpnDate[0];
	long* PayFixingDate = ResultCpnDatePay;
	long* PayPaymentDate = ResultCpnDatePay + 2 * NCpnDate[1];

	long NTotalSimulNotAdj = NCpnDate[0] * 2 + NCpnDate[1] * 2 + NOption * 2 + 1;
	long* TotalArraySimulNotAdj = (long*)malloc(sizeof(long) * NTotalSimulNotAdj);
	TotalArraySimulNotAdj[0] = PriceDate;
	for (i = 0; i < NCpnDate[0]; i++) TotalArraySimulNotAdj[1 + i] = CpnDate[0][i];
	for (i = 0; i < NCpnDate[0]; i++) TotalArraySimulNotAdj[1 + i + NCpnDate[0]] = CpnPayDate[0][i];
	for (i = 0; i < NCpnDate[1]; i++) TotalArraySimulNotAdj[1 + i + 2 * NCpnDate[0]] = CpnDate[1][i];
	for (i = 0; i < NCpnDate[1]; i++) TotalArraySimulNotAdj[1 + i + 2 * NCpnDate[0] + NCpnDate[1]] = CpnPayDate[1][i];
	for (i = 0; i < NOption; i++) TotalArraySimulNotAdj[1 + i + 2 * NCpnDate[0] + 2 * NCpnDate[1]] = OptionDate[i];
	for (i = 0; i < NOption; i++) TotalArraySimulNotAdj[1 + i + 2 * NCpnDate[0] + 2 * NCpnDate[1] + NOption] = OptionPayDate[i];
	long NTotalSimul = 0;
	long* TotalArrayDateSimul = MallocUnique(TotalArraySimulNotAdj, NTotalSimulNotAdj, NTotalSimul);
	bubble_sort_date(TotalArrayDateSimul, NTotalSimul, 1);
	double* dtime = (double*)malloc(sizeof(double) * NTotalSimul);
	double* Time = (double*)malloc(sizeof(double) * NTotalSimul);
	for (i = 0; i < NTotalSimul; i++)
	{
		Time[i] = ((double)DayCountAtoB(PriceDate, TotalArrayDateSimul[i])) / 365.;
		if (i == 0) dtime[i] = ((double)DayCountAtoB(PriceDate, TotalArrayDateSimul[i])) / 365.;
		else dtime[i] = ((double)DayCountAtoB(TotalArrayDateSimul[i-1], TotalArrayDateSimul[i])) / 365.;
	}


	///////////////
	// FDM Greed //
	///////////////
	double xt_min = -0.1, xt_max = 0.75;
	double dxt = (xt_max - xt_min) / ((double)NGreed);
	double yt_min = -0.1, yt_max = 0.75;
	double dyt = (yt_max - yt_min) / ((double)NGreed);
	double x, y, Rate, x_p, y_p, Rate_p;

	double* xt = (double*)malloc(sizeof(double) * NGreed);
	double* yt = (double*)malloc(sizeof(double) * NGreed);
	for (i = 0; i < NGreed; i++) xt[i] = xt_min + ((double)i) * dxt;
	for (i = 0; i < NGreed; i++) yt[i] = yt_min + ((double)i) * dyt;

	double** Rate_Rcv_1F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rate_RcvPowerSpread_1F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double*** Rate_Rcv_2F = (double***)malloc(sizeof(double**) * NTotalSimul);
	double*** Rate_RcvPowerSpread_2F = (double***)malloc(sizeof(double**) * NTotalSimul);
	for (i = 0; i < NTotalSimul; i++)
	{
		Rate_Rcv_1F[i] = (double*)malloc(sizeof(double) * NGreed);
		Rate_RcvPowerSpread_1F[i] = (double*)malloc(sizeof(double) * NGreed);
		Rate_Rcv_2F[i] = (double**)malloc(sizeof(double*) * NGreed);
		Rate_RcvPowerSpread_2F[i] = (double**)malloc(sizeof(double*) * NGreed);
		for (j = 0; j < NGreed; j++)
		{
			Rate_Rcv_2F[i][j] = (double*)malloc(sizeof(double) * NGreed);
			Rate_RcvPowerSpread_2F[i][j] = (double*)malloc(sizeof(double) * NGreed);
		}
	}

	double** Rate_Pay_1F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rate_PayPowerSpread_1F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double*** Rate_Pay_2F = (double***)malloc(sizeof(double**) * NTotalSimul);
	double*** Rate_PayPowerSpread_2F = (double***)malloc(sizeof(double**) * NTotalSimul);
	for (i = 0; i < NTotalSimul; i++)
	{
		Rate_Pay_1F[i] = (double*)malloc(sizeof(double) * NGreed);
		Rate_PayPowerSpread_1F[i] = (double*)malloc(sizeof(double) * NGreed);
		Rate_Pay_2F[i] = (double**)malloc(sizeof(double*) * NGreed);
		Rate_PayPowerSpread_2F[i] = (double**)malloc(sizeof(double*) * NGreed);
		for (j = 0; j < NGreed; j++)
		{
			Rate_Pay_2F[i][j] = (double*)malloc(sizeof(double) * NGreed);
			Rate_PayPowerSpread_2F[i][j] = (double*)malloc(sizeof(double) * NGreed);
		}
	}

	////////////////////////////////////
	// Hull White Bond Pricing Params //
	////////////////////////////////////
	long* Rcv_ncpn = (long*)malloc(sizeof(long) * NTotalSimul);
	long* RcvPowerSpread_ncpn = (long*)malloc(sizeof(long) * NTotalSimul);
	double** Rcv_DF_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_B_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_QVTerm = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_dt = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_DF_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_B_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_QVTerm = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_dt = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_B_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_QVTerm_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_B_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_QVTerm_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Rcv_Cross_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** RcvPowerSpread_Cross_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);

	long* Pay_ncpn = (long*)malloc(sizeof(long) * NTotalSimul);
	long* PayPowerSpread_ncpn = (long*)malloc(sizeof(long) * NTotalSimul);
	double** Pay_DF_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_B_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_QVTerm = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_dt = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_DF_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_B_t_T = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_QVTerm = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_dt = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_B_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_QVTerm_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_B_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_QVTerm_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** Pay_Cross_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double** PayPowerSpread_Cross_t_T_2F = (double**)malloc(sizeof(double*) * NTotalSimul);
	double t1, t2;
	long Today, EndDate1, EndDate2, ncpn, ncpn1, ncpn2;
	double df_t, df_T;
	long* TempDateArray;
	long* TempDateArray2;

	// Rcv Leg 
	for (i = 0; i < NTotalSimul; i++)
	{
		t1 = Time[i];
		Today = TotalArrayDateSimul[i];
		df_t = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t1);
		TempDate = Today;
		ncpn = 0;
		ncpn1 = 0;
		ncpn2 = 0;
		x = 0.;
		y = 0.;
		if (PowerSpreadFlagRcvPay[0] == 0)
		{
			EndDate1 = EDate_Cpp(Today, (long)(Maturity_Rcv * 12 + 0.00001));
			TempDateArray = Malloc_CpnDate_Holiday(Today, EndDate1, NCPN_ANN_Rcv, ncpn, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);

			Rcv_ncpn[i] = ncpn;
			Rcv_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_dt[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			Rcv_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);

			RcvPowerSpread_ncpn[i] = ncpn;
			RcvPowerSpread_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_dt[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			RcvPowerSpread_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);

			for (j = 0; j < ncpn; j++)
			{
				if (j == 0) Rcv_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray[j], DayCountRcvPay[0]);
				else Rcv_dt[i][j] = DayCountFractionAtoB(TempDateArray[-1], TempDateArray[j], DayCountRcvPay[0]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				Rcv_DF_t_T[i][j] = df_T / df_t;
				Rcv_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				Rcv_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					Rcv_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					Rcv_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					Rcv_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			if (HW2FFlag > 0)
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					for (idx2 = 0; idx2 < NGreed; idx2++)
					{
						y = yt[idx2];
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, x, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
						Rate_Rcv_2F[i][idx1][idx2] = Rate;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, x, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
					Rate_Rcv_1F[i][idx1] = Rate;
				}
			}
			free(TempDateArray);
		}
		else
		{
			EndDate1 = EDate_Cpp(Today, (long)(Maturity1_Rcv * 12 + 0.00001));
			EndDate2 = EDate_Cpp(Today, (long)(Maturity2_Rcv * 12 + 0.00001));
			TempDateArray = Malloc_CpnDate_Holiday(Today, EndDate1, NCPN_ANN_Rcv, ncpn1, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);
			TempDateArray2 = Malloc_CpnDate_Holiday(Today, EndDate2, NCPN_ANN_Rcv, ncpn2, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);

			Rcv_ncpn[i] = ncpn1;
			Rcv_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_dt[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn1);
			Rcv_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);

			RcvPowerSpread_ncpn[i] = ncpn2;
			RcvPowerSpread_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_dt[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn2);
			RcvPowerSpread_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);

			for (j = 0; j < ncpn1; j++)
			{
				if (j == 0) Rcv_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray[j], DayCountRcvPay[0]);
				else Rcv_dt[i][j] = DayCountFractionAtoB(TempDateArray[-1], TempDateArray[j], DayCountRcvPay[0]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				Rcv_DF_t_T[i][j] = df_T / df_t;
				Rcv_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				Rcv_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					Rcv_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					Rcv_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					Rcv_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			for (j = 0; j < ncpn2; j++)
			{
				if (j == 0) Rcv_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray2[j], DayCountRcvPay[0]);
				else Rcv_dt[i][j] = DayCountFractionAtoB(TempDateArray2[-1], TempDateArray2[j], DayCountRcvPay[0]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray2[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				RcvPowerSpread_DF_t_T[i][j] = df_T / df_t;
				RcvPowerSpread_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				RcvPowerSpread_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					RcvPowerSpread_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					RcvPowerSpread_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					RcvPowerSpread_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			if (HW2FFlag > 0)
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					for (idx2 = 0; idx2 < NGreed; idx2++)
					{
						y = yt[idx2];
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, x, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
						Rate_Rcv_2F[i][idx1][idx2] = Rate;
						Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, RcvPowerSpread_DF_t_T[i], RcvPowerSpread_QVTerm[i], RcvPowerSpread_B_t_T[i], RcvPowerSpread_dt[i], HW2FFlag, x, RcvPowerSpread_QVTerm_2F[i], RcvPowerSpread_B_t_T_2F[i], RcvPowerSpread_Cross_t_T_2F[i]);
						Rate_RcvPowerSpread_2F[i][idx1][idx2] = Rate_p;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, x, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
					Rate_Rcv_1F[i][idx1] = Rate;
					Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, RcvPowerSpread_DF_t_T[i], RcvPowerSpread_QVTerm[i], RcvPowerSpread_B_t_T[i], RcvPowerSpread_dt[i], HW2FFlag, x, RcvPowerSpread_QVTerm_2F[i], RcvPowerSpread_B_t_T_2F[i], RcvPowerSpread_Cross_t_T_2F[i]);
					Rate_RcvPowerSpread_1F[i][idx1] = Rate_p;
				}
			}

			free(TempDateArray);
			free(TempDateArray2);
		}
	}

	// Pay Leg 
	for (i = 0; i < NTotalSimul; i++)
	{
		t1 = Time[i];
		Today = TotalArrayDateSimul[i];
		df_t = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t1);
		TempDate = Today;
		ncpn = 0;
		ncpn1 = 0;
		ncpn2 = 0;
		x = 0.;
		y = 0.;
		if (PowerSpreadFlagRcvPay[0] == 0)
		{
			EndDate1 = EDate_Cpp(Today, (long)(Maturity_Pay * 12 + 0.00001));
			TempDateArray = Malloc_CpnDate_Holiday(Today, EndDate1, NCPN_ANN_Pay, ncpn, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);

			Pay_ncpn[i] = ncpn;
			Pay_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_dt[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			Pay_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);

			PayPowerSpread_ncpn[i] = ncpn;
			PayPowerSpread_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_dt[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn);
			PayPowerSpread_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn);

			for (j = 0; j < ncpn; j++)
			{
				if (j == 0) Pay_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray[j], DayCountRcvPay[1]);
				else Pay_dt[i][j] = DayCountFractionAtoB(TempDateArray[-1], TempDateArray[j], DayCountRcvPay[1]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				Pay_DF_t_T[i][j] = df_T / df_t;
				Pay_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				Pay_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					Pay_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					Pay_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					Pay_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			if (HW2FFlag > 0)
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					for (idx2 = 0; idx2 < NGreed; idx2++)
					{
						y = yt[idx2];
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, x, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
						Rate_Pay_2F[i][idx1][idx2] = Rate;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, x, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
					Rate_Pay_1F[i][idx1] = Rate;
				}
			}
			free(TempDateArray);
		}
		else
		{
			EndDate1 = EDate_Cpp(Today, (long)(Maturity1_Pay * 12 + 0.00001));
			EndDate2 = EDate_Cpp(Today, (long)(Maturity2_Pay * 12 + 0.00001));
			TempDateArray = Malloc_CpnDate_Holiday(Today, EndDate1, NCPN_ANN_Pay, ncpn1, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);
			TempDateArray2 = Malloc_CpnDate_Holiday(Today, EndDate2, NCPN_ANN_Pay, ncpn2, TempDate, NTotalHoliday[0], TotalHolidays[0], 1);

			Pay_ncpn[i] = ncpn1;
			Pay_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_dt[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn1);
			Pay_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);

			PayPowerSpread_ncpn[i] = ncpn2;
			PayPowerSpread_DF_t_T[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_B_t_T[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_QVTerm[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_dt[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_B_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_QVTerm_2F[i] = (double*)malloc(sizeof(double) * ncpn2);
			PayPowerSpread_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn2);

			for (j = 0; j < ncpn1; j++)
			{
				if (j == 0) Pay_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray[j], DayCountRcvPay[1]);
				else Pay_dt[i][j] = DayCountFractionAtoB(TempDateArray[-1], TempDateArray[j], DayCountRcvPay[1]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				Pay_DF_t_T[i][j] = df_T / df_t;
				Pay_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				Pay_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					Pay_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					Pay_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					Pay_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			for (j = 0; j < ncpn2; j++)
			{
				if (j == 0) Pay_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray2[j], DayCountRcvPay[1]);
				else Pay_dt[i][j] = DayCountFractionAtoB(TempDateArray2[-1], TempDateArray2[j], DayCountRcvPay[1]);
				t2 = ((double)DayCountAtoB(PriceDate, TempDateArray2[j])) / 365.;
				df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
				PayPowerSpread_DF_t_T[i][j] = df_T / df_t;
				PayPowerSpread_B_t_T[i][j] = B_s_to_t(kappa1, t1, t2);
				PayPowerSpread_QVTerm[i][j] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
				if (HW2FFlag > 0)
				{
					PayPowerSpread_B_t_T_2F[i][j] = B_s_to_t(kappa2, t1, t2);
					PayPowerSpread_QVTerm_2F[i][j] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
					PayPowerSpread_Cross_t_T_2F[i][j] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
				}
			}

			if (HW2FFlag > 0)
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					for (idx2 = 0; idx2 < NGreed; idx2++)
					{
						y = yt[idx2];
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, x, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
						Rate_Pay_2F[i][idx1][idx2] = Rate;
						Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, PayPowerSpread_DF_t_T[i], PayPowerSpread_QVTerm[i], PayPowerSpread_B_t_T[i], PayPowerSpread_dt[i], HW2FFlag, x, PayPowerSpread_QVTerm_2F[i], PayPowerSpread_B_t_T_2F[i], PayPowerSpread_Cross_t_T_2F[i]);
						Rate_PayPowerSpread_2F[i][idx1][idx2] = Rate_p;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, x, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
					Rate_Pay_1F[i][idx1] = Rate;
					Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, PayPowerSpread_DF_t_T[i], PayPowerSpread_QVTerm[i], PayPowerSpread_B_t_T[i], PayPowerSpread_dt[i], HW2FFlag, x, PayPowerSpread_QVTerm_2F[i], PayPowerSpread_B_t_T_2F[i], PayPowerSpread_Cross_t_T_2F[i]);
					Rate_PayPowerSpread_1F[i][idx1] = Rate_p;
				}
			}

			free(TempDateArray);
			free(TempDateArray2);
		}
	}


	//////////////////////
	// Df Fixing to Pay //
	//////////////////////
	double* DF_Fix_to_Payment_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* DF_to_Fixing_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* B_t_T_DiscRcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* B_t_T_DiscRcv_2F = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* QVTerm_DiscRcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* QVTerm_DiscRcv_2F = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* CrossQVTerm_DiscRcv = (double*)malloc(sizeof(double) * NCpnDateRcv);

	double* DF_Fix_to_Payment_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* DF_to_Fixing_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* B_t_T_DiscPay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* B_t_T_DiscPay_2F = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* QVTerm_DiscPay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* QVTerm_DiscPay_2F = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* CrossQVTerm_DiscPay = (double*)malloc(sizeof(double) * NCpnDatePay);

	double* DF_Opt_to_Payment = (double*)malloc(sizeof(double) * NOption);
	double* DF_Opt = (double*)malloc(sizeof(double) * NOption);
	double* B_t_T_DiscOpt = (double*)malloc(sizeof(double) * NOption);
	double* B_t_T_DiscOpt_2F = (double*)malloc(sizeof(double) * NOption);
	double* QVTerm_DiscOpt = (double*)malloc(sizeof(double) * NOption);
	double* QVTerm_DiscOpt_2F = (double*)malloc(sizeof(double) * NOption);
	double* CrossQVTerm_DiscOpt = (double*)malloc(sizeof(double) * NOption);

	for (i = 0; i < NCpnDateRcv; i++)
	{
		t1 = ((double)DayCountAtoB(PriceDate, RcvFixingDate[i]))/365.;
		t2 = ((double)DayCountAtoB(PriceDate, RcvPaymentDate[i])) / 365.;
		df_t = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t1);
		df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
		DF_Fix_to_Payment_Rcv[i] = df_T / df_t;
		DF_to_Fixing_Rcv[i] = df_t;
		B_t_T_DiscRcv[i] = B_s_to_t(kappa1, t1, t2);
		QVTerm_DiscRcv[i] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
		if (HW2FFlag > 0)
		{
			B_t_T_DiscRcv_2F[i] = B_s_to_t(kappa2, t1, t2);
			QVTerm_DiscRcv_2F[i] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
			CrossQVTerm_DiscRcv[i] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
		}
	}

	for (i = 0; i < NCpnDatePay; i++)
	{
		t1 = ((double)DayCountAtoB(PriceDate, PayFixingDate[i])) / 365.;
		t2 = ((double)DayCountAtoB(PriceDate, PayPaymentDate[i])) / 365.;
		df_t = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t1);
		df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
		DF_Fix_to_Payment_Pay[i] = df_T / df_t;
		DF_to_Fixing_Pay[i] = df_t;
		B_t_T_DiscPay[i] = B_s_to_t(kappa1, t1, t2);
		QVTerm_DiscPay[i] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
		if (HW2FFlag > 0)
		{
			B_t_T_DiscPay_2F[i] = B_s_to_t(kappa2, t1, t2);
			QVTerm_DiscPay_2F[i] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
			CrossQVTerm_DiscPay[i] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
		}
	}

	for (i = 0; i < NOption; i++)
	{
		t1 = ((double)DayCountAtoB(PriceDate, OptionDate[i]))/365.;
		t2 = ((double)DayCountAtoB(PriceDate, OptionPayDate[i])) / 365.;
		df_t = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t1);
		df_T = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZeroRate, t2);
		DF_Opt_to_Payment[i] = df_T / df_t;
		DF_Opt[i] = df_t;
		B_t_T_DiscOpt[i] = B_s_to_t(kappa1, t1, t2);
		QVTerm_DiscOpt[i] = HullWhiteQVTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol);
		if (HW2FFlag > 0)
		{
			B_t_T_DiscOpt_2F[i] = B_s_to_t(kappa2, t1, t2);
			QVTerm_DiscOpt_2F[i] = HullWhiteQVTerm(t1, t2, kappa2, NHWVol, HWVolTerm, HWVol2);
			CrossQVTerm_DiscOpt[i] = HullWhite2F_CrossTerm(t1, t2, kappa1, NHWVol, HWVolTerm, HWVol, kappa2, HWVolTerm, HWVol2, FactorCorrelation);
		}
	}

	for (i = 0; i < 2; i++) free(TotalHolidays[i]);
	free(TotalHolidays);
	for (i = 0; i < 2; i++) free(CpnDate[i]);
	free(CpnDate);
	for (i = 0; i < 2; i++) free(CpnPayDate[i]);
	free(CpnPayDate);
	free(TotalArraySimulNotAdj);
	free(TotalArrayDateSimul);
	free(dtime);
	free(Time);
	free(xt);
	free(yt);

	for (i = 0; i < NTotalSimul; i++)
	{
		for (j = 0; j < NGreed; j++)
		{
			free(Rate_Rcv_2F[i][j]);
			free(Rate_RcvPowerSpread_2F[i][j]);
		}
		free(Rate_Rcv_1F[i]);
		free(Rate_RcvPowerSpread_1F[i]);
		free(Rate_Rcv_2F[i]);
		free(Rate_RcvPowerSpread_2F[i]);
	}
	free(Rate_Rcv_2F);
	free(Rate_RcvPowerSpread_2F);
	free(Rate_Rcv_1F);
	free(Rate_RcvPowerSpread_1F);

	for (i = 0; i < NTotalSimul; i++)
	{
		for (j = 0; j < NGreed; j++)
		{
			free(Rate_Pay_2F[i][j]);
			free(Rate_PayPowerSpread_2F[i][j]);
		}
		free(Rate_Pay_1F[i]);
		free(Rate_PayPowerSpread_1F[i]);
		free(Rate_Pay_2F[i]);
		free(Rate_PayPowerSpread_2F[i]);
	}
	free(Rate_Pay_2F);
	free(Rate_PayPowerSpread_2F);
	free(Rate_Pay_1F);
	free(Rate_PayPowerSpread_1F);

	free(Rcv_ncpn);
	free(RcvPowerSpread_ncpn);
	for (i = 0; i < NTotalSimul; i++)
	{
		free(Rcv_DF_t_T[i]);
		free(Rcv_B_t_T[i]);
		free(Rcv_QVTerm[i]);
		free(Rcv_dt[i]);
		free(RcvPowerSpread_DF_t_T[i]);
		free(RcvPowerSpread_B_t_T[i]);
		free(RcvPowerSpread_QVTerm[i]);
		free(RcvPowerSpread_dt[i]);
		free(Rcv_B_t_T_2F[i]);
		free(Rcv_QVTerm_2F[i]);
		free(RcvPowerSpread_B_t_T_2F[i]);
		free(RcvPowerSpread_QVTerm_2F[i]);
		free(Rcv_Cross_t_T_2F[i]);
		free(RcvPowerSpread_Cross_t_T_2F[i]);
	}
	free(Rcv_DF_t_T);
	free(Rcv_B_t_T);
	free(Rcv_QVTerm);
	free(Rcv_dt);
	free(RcvPowerSpread_DF_t_T);
	free(RcvPowerSpread_B_t_T);
	free(RcvPowerSpread_QVTerm);
	free(RcvPowerSpread_dt);
	free(Rcv_B_t_T_2F);
	free(Rcv_QVTerm_2F);
	free(RcvPowerSpread_B_t_T_2F);
	free(RcvPowerSpread_QVTerm_2F);
	free(Rcv_Cross_t_T_2F);
	free(RcvPowerSpread_Cross_t_T_2F);

	free(Pay_ncpn);
	free(PayPowerSpread_ncpn);
	for (i = 0; i < NTotalSimul; i++)
	{
		free(Pay_DF_t_T[i]);
		free(Pay_B_t_T[i]);
		free(Pay_QVTerm[i]);
		free(Pay_dt[i]);
		free(PayPowerSpread_DF_t_T[i]);
		free(PayPowerSpread_B_t_T[i]);
		free(PayPowerSpread_QVTerm[i]);
		free(PayPowerSpread_dt[i]);
		free(Pay_B_t_T_2F[i]);
		free(Pay_QVTerm_2F[i]);
		free(PayPowerSpread_B_t_T_2F[i]);
		free(PayPowerSpread_QVTerm_2F[i]);
		free(Pay_Cross_t_T_2F[i]);
		free(PayPowerSpread_Cross_t_T_2F[i]);
	}
	free(Pay_DF_t_T);
	free(Pay_B_t_T);
	free(Pay_QVTerm);
	free(Pay_dt);
	free(PayPowerSpread_DF_t_T);
	free(PayPowerSpread_B_t_T);
	free(PayPowerSpread_QVTerm);
	free(PayPowerSpread_dt);
	free(Pay_B_t_T_2F);
	free(Pay_QVTerm_2F);
	free(PayPowerSpread_B_t_T_2F);
	free(PayPowerSpread_QVTerm_2F);
	free(Pay_Cross_t_T_2F);
	free(PayPowerSpread_Cross_t_T_2F);

	free(DF_Fix_to_Payment_Rcv);
	free(DF_to_Fixing_Rcv);
	free(B_t_T_DiscRcv);
	free(B_t_T_DiscRcv_2F);
	free(QVTerm_DiscRcv);
	free(QVTerm_DiscRcv_2F);
	free(CrossQVTerm_DiscRcv);

	free(DF_Fix_to_Payment_Pay);
	free(DF_to_Fixing_Pay);
	free(B_t_T_DiscPay);
	free(B_t_T_DiscPay_2F);
	free(QVTerm_DiscPay);
	free(QVTerm_DiscPay_2F);
	free(CrossQVTerm_DiscPay);

	free(DF_Opt_to_Payment);
	free(DF_Opt);
	free(B_t_T_DiscOpt);
	free(B_t_T_DiscOpt_2F);
	free(QVTerm_DiscOpt);
	free(QVTerm_DiscOpt_2F);
	free(CrossQVTerm_DiscOpt);

	return 1;
}

int main()
{
	long i, j, n;
	long PriceDate = 20240727;
	long EffectiveDate = 20240727;
	long Maturity = 20340731;
	long NAFlag = 0;
	double NA = 400000000.0;
	long NAdditionalHolidays[2] = { 1, 2 };
	long AddtionalHolidays[3] = { 20240101, 20240101, 20241225 };
	long NationFlag[2] = { -1, -1 };
	long NumCpnAnn[2] = { 4, 4 };
	double MaxLossRefRcvPay[4] = { 0.99, 0.99, 0.99, 0.99 };
	double MultipleRatefixPayoffRcvPay[4] = { 1.0, 1.0, 0.0, 0.0 };
	long DayCountRcvPay[2] = { 0, 1 };
	long PowerSpreadFlagRcvPay[2] = { 0, 0 };
	double RangeMaxMinRcvPay[4] = { 100.0, -1.0, 100.0, -1.0 };
	double InfoRefRateRcvPay[8] = { 4.0, 10.0, 10.0, 5.0, 4.0, 0.25, 30.0, 10.0 };

	double RcvLegFixedRate = 0.00;
	double RcvLegRangeCoupon = 0.00;
	long RcvLegStructuredFlag = 1;
	double PayLegFixedRate = 0.03;
	double PayLegRangeCoupon = 0.03;
	long PayLegStructuredFlag = 0;

	long Phase2Date = 20290727;
	double Phase2RcvLegFixedRate = 0.00;
	double Phase2RcvLegRangeCoupon = 0.00;
	long Phase2RcvLegStructuredFlag = 1;
	double Phase2PayLegFixedRate = 0.03;
	double Phase2PayLegRangeCoupon = 0.03;
	long Phase2PayLegStructuredFlag = 0;

	long NOption = 2;
	long OptionDate[2] = { 20250727, 20260727 };
	long OptionPayDate[2] = { 20250729, 20260729 };
	long OptionType = 1;

	long NRcvRateHistory = 2;
	long RcvRateHistoryDate[2] = { 20220819, 20220820 };
	double RcvRateHistory[2] = { 0.03914, 0.0392 };

	long NPayRateHistory = 1;
	long PayRateHistoryDate[1] = { 20220819 };
	double PayRateHistory[1] = { 0.0304 };

	long NZeroRate = 4;
	double ZeroTerm[4] = { 0.5, 1.0, 1.5, 2.0 };
	double ZeroRate[4] = { 0.0379, 0.0387, 0.0392, 0.0412 };

	long HW2FFlag = 0;
	long NHWVol = 5;
	double HWVolTerm[5] = { 0.5, 1.0, 1.5, 2.0, 3.0 };
	double HWVol[10] = { 0.0096, 0.0111, 0.0112, 0.0112,0.0114,0.0052,0.0046,0.0066,0.0062,0.0061 };
	double kappa[2] = { 0.07, 0.011 };
	double FactorCorrelation = 0.132;
	long NCpn[2] = { 0.0 };

	NCpn[0] = Number_of_Coupons(1, CDateToExcelDate(EffectiveDate), CDateToExcelDate(Maturity), NumCpnAnn[0], 0, 0,0,0);

	NCpn[1] = Number_of_Coupons(1, CDateToExcelDate(EffectiveDate), CDateToExcelDate(Maturity), NumCpnAnn[0], 0, 0,0,0);
	long* ResultCpnDateRcv = (long*)malloc(sizeof(long) * NCpn[0] * 5);
	long* ResultCpnDatePay = (long*)malloc(sizeof(long) * NCpn[1] * 5);

	MyFunc(PriceDate, EffectiveDate, Maturity, NAFlag, NA,
		NAdditionalHolidays, NAdditionalHolidays, NationFlag, NumCpnAnn, MaxLossRefRcvPay,
		MultipleRatefixPayoffRcvPay, DayCountRcvPay, PowerSpreadFlagRcvPay, RangeMaxMinRcvPay, InfoRefRateRcvPay,
		RcvLegFixedRate, RcvLegRangeCoupon, RcvLegStructuredFlag,PayLegFixedRate,PayLegRangeCoupon,
		PayLegStructuredFlag,Phase2Date,Phase2RcvLegFixedRate,Phase2RcvLegRangeCoupon,Phase2RcvLegStructuredFlag,
		Phase2PayLegFixedRate,Phase2PayLegRangeCoupon,Phase2PayLegStructuredFlag,NOption, OptionDate, 
		OptionPayDate, OptionType, NRcvRateHistory,RcvRateHistoryDate, RcvRateHistory, 
		NPayRateHistory, PayRateHistoryDate, PayRateHistory, NZeroRate, ZeroTerm, 
		ZeroRate, HW2FFlag, NHWVol,HWVolTerm, HWVol, 
		kappa, FactorCorrelation, ResultCpnDateRcv, ResultCpnDatePay
		);
	free(ResultCpnDateRcv);
	free(ResultCpnDatePay);
	_CrtDumpMemoryLeaks();
}