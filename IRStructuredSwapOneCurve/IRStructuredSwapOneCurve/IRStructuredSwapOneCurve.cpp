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

double rounding_double(double x, long n_decimal)
{
	if (n_decimal == 0)
	{
		return x;
	}
	else
	{
		long i;
		long j;
		double div = 1.0;
		for (i = 0; i < min(15, n_decimal); i++) div *= 10.0;

		double resultvalue = ceil(x * div) / div;
		return resultvalue;
	}
}

DLLEXPORT(long) NCpnDate_Holiday_2Phase(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYearPhase1, long Phase2UseFlag, long AnnCpnOneYearPhase2, long Phase2Date, long ModifiedFollowing)
{
	long i;
	if (AnnCpnOneYearPhase1 < 0) AnnCpnOneYearPhase1 = 0;
	if (AnnCpnOneYearPhase2 < 0) AnnCpnOneYearPhase2 = 0;

	long Holidays[1] = { 19500101 };
	long NHoliday = 1;
	long FirstCpnDate = PriceDateYYYYMMDD;
	long LastForwardEndDate = (long)(SwapMat_YYYYMMDD / 100) * 100 + PriceDateYYYYMMDD - (long)(PriceDateYYYYMMDD / 100) * 100;
	if (Phase2UseFlag == 0 || PriceDateYYYYMMDD >= Phase2Date || Phase2Date < 0 || Phase2Date >= SwapMat_YYYYMMDD)
	{
		long NArray = 0;
		long* CpnDate;
		CpnDate = Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, LastForwardEndDate, AnnCpnOneYearPhase1, NArray, FirstCpnDate, NHoliday, Holidays, ModifiedFollowing);
		return NArray;
	}
	else
	{
		long Phase1Maturity;
		long Phase1MaturityYYYY = (Phase2Date / 10000);
		long Phase1MaturityMMDD = LastForwardEndDate - (LastForwardEndDate / 10000) * 10000;
		Phase1Maturity = Phase1MaturityYYYY * 10000 + Phase1MaturityMMDD;
		long NumCpn=0;
		long N1 = 0, N2 = 0;
		long* CpnDate1 = Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, Phase1Maturity, AnnCpnOneYearPhase1, N1, FirstCpnDate, NHoliday, Holidays, ModifiedFollowing);
		long* CpnDate2 = Malloc_CpnDate_Holiday(Phase2Date, LastForwardEndDate, AnnCpnOneYearPhase2, N2, FirstCpnDate, NHoliday, Holidays, ModifiedFollowing);

		NumCpn = N1 + N2;
		free(CpnDate1);
		free(CpnDate2);
		return NumCpn;
	}
}

long* Malloc_CpnDate_Holiday_2Phase(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYearPhase1, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD, long Phase2UseFlag, long AnnCpnOneYearPhase2, long Phase2Date, long ModifiedFollowing = 1)
{
	long i;
	if (AnnCpnOneYearPhase1 < 0) AnnCpnOneYearPhase1 = 0;
	if (AnnCpnOneYearPhase2 < 0) AnnCpnOneYearPhase2 = 0;

	long LastForwardEndDate = (long)(SwapMat_YYYYMMDD / 100) * 100 + PriceDateYYYYMMDD - (long)(PriceDateYYYYMMDD / 100) * 100;
	if (Phase2UseFlag == 0 || PriceDateYYYYMMDD == Phase2Date || Phase2Date < 0)
	{
		return Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, LastForwardEndDate, AnnCpnOneYearPhase1, lenArray, FirstCpnDate, NHoliday, HolidayYYYYMMDD, ModifiedFollowing);
	}
	else
	{
		long Phase1Maturity;
		long Phase1MaturityYYYY = (Phase2Date / 10000);
		long Phase1MaturityMMDD = LastForwardEndDate - (LastForwardEndDate / 10000) * 10000;
		Phase1Maturity = Phase1MaturityYYYY * 10000 + Phase1MaturityMMDD;
		long NumCpn;
		long N1 = 0, N2 = 0;
		long* CpnDate1 = Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, Phase1Maturity, AnnCpnOneYearPhase1, N1, FirstCpnDate, NHoliday, HolidayYYYYMMDD, ModifiedFollowing);
		long* CpnDate2 = Malloc_CpnDate_Holiday(Phase2Date, LastForwardEndDate, AnnCpnOneYearPhase2, N2, FirstCpnDate, NHoliday, HolidayYYYYMMDD, ModifiedFollowing);

		NumCpn = N1 + N2;
		lenArray = NumCpn;
		long* CpnDateResult = (long*)malloc(sizeof(long) * lenArray);
		for (i = 0; i < N1; i++) CpnDateResult[i] = CpnDate1[i];
		for (i = N1; i < N1 + N2; i++) CpnDateResult[i] = CpnDate2[i - N1];
		free(CpnDate1);
		free(CpnDate2);
		return CpnDateResult;
	}
}

double _stdcall s_2F(
	double sig1,
	double sig2,
	double corr_factor,
	double dt,
	double dx,
	double dy
)
{
	return 0.5 * sig1 * sig2 * corr_factor * dt / (4.0 * dx * dy);
}

double U_i_j(double** U, long i, long j, long N)
{
	if (i < 0 && j < 0)
	{
		return 0.5 * (2.0 * U[0][0] - U[0][1]) + 0.5 * (2.0 * U[0][0] - U[1][0]);
	}
	else if (i < 0 && j == N)
	{
		return 2.0 * U[0][N - 1] - U[1][N - 2];
	}
	else if (i == N && j < 0)
	{
		return 2.0 * U[N - 1][0] - U[N - 2][1];
	}
	else if (i < 0 && j >= 0 && j < N)
	{
		return (2.0 * U[0][j] - U[1][j]);
	}
	else if (i >= 0 && i < N && j < 0)
	{
		return (2.0 * U[i][0] - U[i][1]);
	}
	else if (i == N && j == N)
	{
		return 0.5 * (2.0 * U[N - 1][N - 1] - U[N - 1][N - 2]) + 0.5 * (2.0 * U[N - 1][N - 1] - U[N - 2][N - 1]);
	}
	else if (i == N && j < N)
	{
		return (2.0 * U[N - 1][j] - U[N - 2][j]);
	}
	else if (i < N && j == N)
	{
		return (2.0 * U[i][N - 1] - U[i][N - 2]);
	}
	else return U[i][j];
}

void ResultRHS_2F(
	long NGreed,
	double* x,
	double* y,
	double kappa1,
	double kappa2,
	double sig1,
	double sig2,
	double corr_factor,
	double dx,
	double dy,
	double dt,
	double** Value_2F,
	double** ResultRHS
)
{
	long i, j;
	double u_i_j, u_iu_jd, u_id_ju, u_iu_ju, u_id_jd;
	double s = s_2F(sig1, sig2, corr_factor, dt, dx, dy);

	for (i = 0; i < NGreed; i++)
	{
		for (j = 0; j < NGreed; j++)
		{
			u_iu_ju = U_i_j(Value_2F, i + 1, j + 1, NGreed);
			u_id_jd = U_i_j(Value_2F, i - 1, j - 1, NGreed);
			u_iu_jd = U_i_j(Value_2F, i + 1, j - 1, NGreed);
			u_id_ju = U_i_j(Value_2F, i - 1, j + 1, NGreed);
			ResultRHS[i][j] = s * (u_iu_ju + u_id_jd - u_iu_jd - u_id_ju) + Value_2F[i][j];
		}
	}
}

void Copy2dMatrix(double** CopyResult, double** MyMatrix, long p, long q)
{
	long i, j;
	for (i = 0; i < p; i++) for (j = 0; j < q; j++) CopyResult[i][j] = MyMatrix[i][j];
}

void TransposeMat(
	long N,
	double** Mat
)
{
	long i, j;
	double tempvalue = 0.0;
	for (i = 0; i < N; i++)
	{
		for (j = 0; j < N; j++)
		{
			if (i < j)
			{
				tempvalue = Mat[i][j] + 0.0;
				Mat[i][j] = Mat[j][i];
				Mat[j][i] = tempvalue;
			}
		}
	}
}


//	tri-diagonal 행렬 방정식을 빠르게 푼다.(임시 Array : TempAlpha, TempBeta, TempGamma를 준비해서 할당을 하는 시간 및 할당 해제하는 시간을 없앤다.)
//  V_T0결과는 V_T1[1], V_T1[2], ... , V_T1[N]에 덮어씌워서 저장된다.
// [[Beta[0], Gamma[0], 0.0,      0.0,       0.0,        ..........      , 0.0]     [V_T0[0]  ]     [V_T1[0]  ]    
//  [Alpha[1],Beta[1],  Gamma[1], 0.0,       0.0,        ..........      , 0.0]     [V_T0[1]  ]     [V_T1[1]  ]
//  [0.0,     Alpha[2], Beta[2],  Gamma[2],  0.0,        ..........      , 0.0]     [V_T0[2]  ]     [V_T1[2]  ]
//  [0.0,     0.0,      Alpha[3], Beta[3],   Gamma[3],   ........        , 0.0]     [V_T0[3]  ]     [V_T1[3]  ]
//  [~~~,     ~~,       ~~~~~,    ~~~,       ~~~~~~,   ........        , ...  ]   x [     ..  ]  =  [   ..    ]
//  [0.0,     0.0,      .....     Alpha[N-3],Beta[N-3],  Gamma[N-3],       0.0]     [V_T0[N-3]]     [V_T1[N-3]]
//  [0.0,     0.0,      .....,    0.0,       Alpha[N-2], Beta[N-2], Gamma[N-2]]     [V_T0[N-2]]     [V_T1[N-2]]
//  [0.0,     0.0,      .....,    0.0,       0.0,        Alpha[N-1], Beta[N-1]]]    [V_T0[N-1]]     [V_T1[N-1]]
long Tri_diagonal_Matrix_Fast(
	double* Alpha,    // Tridiagonal Matrix에서 왼쪽 대각선 행렬
	double* Beta,     // Tridiagonal Matrix에서 중앙 대각선 행렬
	double* Gamma,    // Tridiagonal Matrix에서 오른쪽 대각선 행렬
	double** V_T1,     // V(T1)
	long N,           // 대각선 행렬들의 길이
	double* TempAlpha,// 임시 행렬1 
	double* TempBeta, // 임시 행렬2
	double* TempGamma // 임시 행렬3
)
{
	long i;
	long j;
	for (j = 0; j < N; j++)
	{
		for (i = 0; i <= N - 1; i++)
		{
			TempAlpha[i] = Alpha[i];
			TempBeta[i] = Beta[i];
			TempGamma[i] = Gamma[i];
		}

		TempAlpha[0] = 0.0;
		TempGamma[N - 1] = 0.0;

		if (N <= 1) V_T1[0][j] /= TempBeta[0];
		else {
			for (i = 1; i <= N - 1; i++) {
				TempAlpha[i] /= TempBeta[i - 1];
				TempBeta[i] -= TempAlpha[i] * TempGamma[i - 1];
				V_T1[i][j] -= TempAlpha[i] * V_T1[i - 1][j];
			}
			V_T1[N - 1][j] /= TempBeta[N - 1];

			for (i = N - 2; i >= 0; i--) V_T1[i][j] = (V_T1[i][j] - TempGamma[i] * V_T1[i + 1][j]) / TempBeta[i];
		}
	}

	return 1;
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

		term = v1 * v2 * (1.0 - exp(-k1 * (T - u))) / k1 * (1.0 - exp(-k2 * (T - u))) / k2 * du;
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
		vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t + T) / 2.);
		V_1 = V_t_T(kappa, kappa, t, T, vol, vol);
		V_2 = V_t_T(kappa, kappa, 0, T, vol, vol);
		V_3 = V_t_T(kappa, kappa, 0, t, vol, vol);
		RHS = 0.5 * (V_1 - V_2 + V_3);
	}
	else
	{
		V_1 = V_t_T(kappa, kappa, t, T, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
		V_2 = V_t_T(kappa, kappa, 0, T, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
		V_3 = V_t_T(kappa, kappa, 0, t, HWVolTerm, HWVol, NHWVol, HWVolTerm, HWVol, NHWVol);
		//RHS = 0.5 * (V_1 - V_2 + V_3);
		//RHS = 0.;
		//long NInteg = 10;
		//double u = t;
		//double du = (T - t) / ((double)NInteg);
		//double Bst = 0., BsT = 0.;
		//for (i = 0; i < NInteg; i++)
		//{
		//	vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
		//	Bst = B_s_to_t(kappa, u, t);
		//	BsT = B_s_to_t(kappa, u, T);
		//	RHS += 0.5 * vol * vol * (Bst * Bst - BsT * BsT) * du;
		//	u = u + du;
		//}
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

DLLEXPORT(long) IRStructuredSwapFDM(
	long PriceDate,							// PricingDate As YYYYMMDD
	long EffectiveDate,						// EffeciveDate As YYYYMMDD
	long Maturity,							// Maturity As YYYYMMDD
	long NAFlag,							// Notional Use Flag
	double NA,								// Notional Amount

	long* NAdditionalHolidays,				// RcvLeg, PayLeg Additional NHolidays Custom(len = 2)
	long* AdditionalHolidays,				// RcvLeg, PayLeg Additional Holidays Custom(len = 2)
	long* NationFlag,						// RcvLeg, PayLeg Nation Flag 0 : KRW, 1 : USD, ...
	long* NumCpnAnn,						// Number Coupon of 1y (len = 2)
	double* MaxLossRetRcvPay,				// MaxLossRet of Rcv, Pay Leg (len = 4)

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
	long Phase2UseFlag,						// Phase2UseFlag
	long Phase2Date,						// Phase2Date
	double Phase2RcvLegFixedRate,			// Receive Leg Fixed Coupon Rate
	double Phase2RcvLegRangeCoupon,			// Rcv Leg Range OK FixedCoupon Rate

	long Phase2RcvLegStructuredFlag,		// Rcv Leg Structured Coupon Flag
	double Phase2PayLegFixedRate,			// Pay Leg Fixed Coupon Rate
	double Phase2PayLegRangeCoupon,			// Pay Leg Range OK FixedCoupon Rate
	long Phase2PayLegStructuredFlag,		// Pay Leg Structured Coupon Flag
	long* NumCpnAnnPhase2RcvPay,			// RcvPay Phase2 NumCpnAnn

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
	long NZeroDiscRate,
	double* ZeroDiscTerm,

	double* ZeroDiscRate,
	long HW2FFlag,
	long NHWVol,
	double* HWVolTerm,
	double* HWVol,

	double* kappa,
	double FactorCorrelation,
	long* InterestRateRoundingRcvPay,
	long* ResultCpnDateRcv,
	long* ResultCpnDatePay,
	double* ResultFixingRateCpn,
	long TextFlag
)
{
	if (PriceDate < 19000101) PriceDate = ExcelDateToCDate(PriceDate);
	if (Maturity < 19000101) Maturity = ExcelDateToCDate(Maturity);
	if (EffectiveDate < 19000101) EffectiveDate = ExcelDateToCDate(EffectiveDate);
	if (Phase2Date < 19000101) Phase2Date = ExcelDateToCDate(Phase2Date);
	long i, j, k, n;
	for (i = 0; i < NAdditionalHolidays[0] + NAdditionalHolidays[1]; i++) if (AdditionalHolidays[i] < 19000101) AdditionalHolidays[i] = ExcelDateToCDate(AdditionalHolidays[i]);
	for (i = 0; i < NOption; i++) if (OptionDate[i] < 19000101) OptionDate[i] = ExcelDateToCDate(OptionDate[i]);
	for (i = 0; i < NOption; i++) if (OptionPayDate[i] < 19000101) OptionPayDate[i] = ExcelDateToCDate(OptionPayDate[i]);
	for (i = 0; i < NRcvRateHistory; i++) if (RcvRateHistoryDate[i] < 19000101) RcvRateHistoryDate[i] = ExcelDateToCDate(RcvRateHistoryDate[i]);
	for (i = 0; i < NPayRateHistory; i++) if (PayRateHistoryDate[i] < 19000101) PayRateHistoryDate[i] = ExcelDateToCDate(PayRateHistoryDate[i]);
	char CalcFunctionName[] = "IRStructuredSwapFDM";
	char SaveFileName[100];
	long RoundingRcv = InterestRateRoundingRcvPay[0];
	long RoundingPay = InterestRateRoundingRcvPay[1];
	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag > 0)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate", PriceDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "EffectiveDate", EffectiveDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "Maturity", Maturity);
		DumppingTextData(CalcFunctionName, SaveFileName, "NAFlag", NAFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NA", NA);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "NAdditionalHolidays", 2, NAdditionalHolidays);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "AdditionalHolidays", NAdditionalHolidays[0] + NAdditionalHolidays[1], AdditionalHolidays);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "NationFlag", 2, NationFlag);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "NumCpnAnn", 2, NumCpnAnn);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "MaxLossRetRcvPay", 4, MaxLossRetRcvPay);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "MultipleRatefixPayoffRcvPay", 4, MultipleRatefixPayoffRcvPay);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "DayCountRcvPay", 2, DayCountRcvPay);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PowerSpreadFlagRcvPay", 2, PowerSpreadFlagRcvPay);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RangeMaxMinRcvPay", 4, RangeMaxMinRcvPay);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "InfoRefRateRcvPay", 8, InfoRefRateRcvPay);

		DumppingTextData(CalcFunctionName, SaveFileName, "RcvLegFixedRate", RcvLegFixedRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "RcvLegRangeCoupon", RcvLegRangeCoupon);
		DumppingTextData(CalcFunctionName, SaveFileName, "RcvLegStructuredFlag", RcvLegStructuredFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "PayLegFixedRate", PayLegFixedRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "PayLegRangeCoupon", PayLegRangeCoupon);

		DumppingTextData(CalcFunctionName, SaveFileName, "PayLegStructuredFlag", PayLegStructuredFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2UseFlag", Phase2UseFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2Date", Phase2Date);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2RcvLegFixedRate", Phase2RcvLegFixedRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2RcvLegRangeCoupon", Phase2RcvLegRangeCoupon);

		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2RcvLegStructuredFlag", Phase2RcvLegStructuredFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2PayLegFixedRate", Phase2PayLegFixedRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2PayLegRangeCoupon", Phase2PayLegRangeCoupon);
		DumppingTextData(CalcFunctionName, SaveFileName, "Phase2PayLegStructuredFlag", Phase2PayLegStructuredFlag);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "NumCpnAnnPhase2RcvPay", 2, NumCpnAnnPhase2RcvPay);

		DumppingTextData(CalcFunctionName, SaveFileName, "NOption", NOption);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "OptionDate", NOption, OptionDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "OptionDate", NOption, OptionPayDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "OptionType", OptionType);
		DumppingTextData(CalcFunctionName, SaveFileName, "NRcvRateHistory", NRcvRateHistory);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRateHistoryDate", NRcvRateHistory, RcvRateHistoryDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvRateHistoryDate", NRcvRateHistory, RcvRateHistory);
		DumppingTextData(CalcFunctionName, SaveFileName, "NPayRateHistory", NPayRateHistory);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRateHistoryDate", NPayRateHistory, PayRateHistoryDate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayRateHistoryDate", NPayRateHistory, PayRateHistory);

		DumppingTextData(CalcFunctionName, SaveFileName, "NZeroRate", NZeroRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroTerm", NZeroRate, ZeroTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroRate", NZeroRate, ZeroRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "NZeroDiscRate", NZeroDiscRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroDiscTerm", NZeroDiscRate, ZeroDiscTerm);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ZeroDiscRate", NZeroDiscRate, ZeroDiscRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "HW2FFlag", HW2FFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NHWVol", NHWVol);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWVolTerm", NHWVol, HWVolTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "HWVol", NHWVol * 2, HWVol);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "kappa", 2, kappa);
		DumppingTextData(CalcFunctionName, SaveFileName, "FactorCorrelation", FactorCorrelation);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "InterestRateRoundingRcvPay", 2, InterestRateRoundingRcvPay);


	}
	long idx1, idx2;
	long NGreed = 100;

	long PowerSpreadFlagRcv = PowerSpreadFlagRcvPay[0];
	long PowerSpreadFlagPay = PowerSpreadFlagRcvPay[1];

	double* InfoRefRateRcv = InfoRefRateRcvPay;
	double* InfoRefRatePay = InfoRefRateRcvPay + 4;

	double* MaxLossRetRcv = MaxLossRetRcvPay;
	double* MaxLossRetPay = MaxLossRetRcvPay + 2;

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
	double ResultValue = 0.;

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
		NBD = NBusinessCountFromEndToPay(EffectiveDate, Maturity, TotalHolidays[n], NTotalHoliday[n], 1, &LastForwardEndDate);
		//CpnDate[n] = Malloc_CpnDate_Holiday(EffectiveDate, LastForwardEndDate, NumCpnAnn[n], NCpnDate[n], TempDate, NTotalHoliday[n], TotalHolidays[n], 1);
		CpnDate[n] = Malloc_CpnDate_Holiday_2Phase(EffectiveDate, LastForwardEndDate, NumCpnAnn[n], NCpnDate[n], TempDate, NTotalHoliday[n], TotalHolidays[n], Phase2UseFlag, NumCpnAnnPhase2RcvPay[n], Phase2Date);
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
			if (NBDFromEndToPay == 0) CpnPayDate[n][i] = CpnDate[n][i];
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

	long NTotalSimulNotAdj = NCpnDate[0] * 2 + NCpnDate[1] * 2 + NOption * 2 + 2;
	long* TotalArraySimulNotAdj = (long*)malloc(sizeof(long) * NTotalSimulNotAdj);
	TotalArraySimulNotAdj[0] = EffectiveDate;
	TotalArraySimulNotAdj[1] = PriceDate;
	for (i = 0; i < NCpnDate[0]; i++) TotalArraySimulNotAdj[2 + i] = CpnDate[0][i];
	for (i = 0; i < NCpnDate[0]; i++) TotalArraySimulNotAdj[2 + i + NCpnDate[0]] = CpnPayDate[0][i];
	for (i = 0; i < NCpnDate[1]; i++) TotalArraySimulNotAdj[2 + i + 2 * NCpnDate[0]] = CpnDate[1][i];
	for (i = 0; i < NCpnDate[1]; i++) TotalArraySimulNotAdj[2 + i + 2 * NCpnDate[0] + NCpnDate[1]] = CpnPayDate[1][i];
	for (i = 0; i < NOption; i++) TotalArraySimulNotAdj[2 + i + 2 * NCpnDate[0] + 2 * NCpnDate[1]] = OptionDate[i];
	for (i = 0; i < NOption; i++) TotalArraySimulNotAdj[2 + i + 2 * NCpnDate[0] + 2 * NCpnDate[1] + NOption] = OptionPayDate[i];
	long NTotalSimul = 0;
	long* TotalArrayDateSimul = MallocUnique(TotalArraySimulNotAdj, NTotalSimulNotAdj, NTotalSimul);
	bubble_sort_date(TotalArrayDateSimul, NTotalSimul, 1);
	double* dtime = (double*)malloc(sizeof(double) * NTotalSimul);
	double* Time = (double*)malloc(sizeof(double) * NTotalSimul);
	for (i = 0; i < NTotalSimul; i++)
	{
		Time[i] = ((double)DayCountAtoB(PriceDate, TotalArrayDateSimul[i])) / 365.;
		if (i == 0) dtime[i] = ((double)DayCountAtoB(PriceDate, TotalArrayDateSimul[i])) / 365.;
		else dtime[i] = ((double)DayCountAtoB(TotalArrayDateSimul[i - 1], TotalArrayDateSimul[i])) / 365.;
	}

	double* ResultFixingRateCpnRcv = ResultFixingRateCpn + 1;
	double* ResultFixingRateCpnPay = ResultFixingRateCpn + 1 + NCpnDate[0] * 2;

	//////////////////////////
	// KDB ZeroCallableSwap //
	//////////////////////////
	double DF_to_LastPayDate_Rcv = 1.0;
	double DF_to_LastPayDate_Pay = 1.0;
	double AccZeroCpnRcv, AccZeroCpnPay;
	double AccCpnDFRcv, AccCpnDFPay;
	double t_to_LastPayDate_Rcv = 0.;
	double t_to_LastPayDate_Pay = 0.;

	///////////////
	// FDM Greed //
	///////////////
	double xt_min = -0.1, xt_max = 0.4;
	double dxt = (xt_max - xt_min) / ((double)NGreed);
	double yt_min = -0.1, yt_max = 0.4;
	double dyt = (yt_max - yt_min) / ((double)NGreed);
	double x, y, Rate, x_p, y_p, Rate_p;

	double* xt = (double*)malloc(sizeof(double) * NGreed);
	double* yt = (double*)malloc(sizeof(double) * NGreed);
	for (i = 0; i < NGreed; i++) xt[i] = xt_min + ((double)i) * dxt;
	for (i = 0; i < NGreed; i++) yt[i] = yt_min + ((double)i) * dyt;
	double* RcvLastFixingPayoff_1F = (double*)malloc(sizeof(double) * NGreed);
	double* PayLastFixingPayoff_1F = (double*)malloc(sizeof(double) * NGreed);
	double** RcvLastFixingPayoff_2F = (double**)malloc(sizeof(double*) * NGreed);
	double** PayLastFixingPayoff_2F = (double**)malloc(sizeof(double*) * NGreed);
	for (i = 0; i < NGreed; i++) RcvLastFixingPayoff_2F[i] = (double*)malloc(sizeof(double) * NGreed);
	for (i = 0; i < NGreed; i++) PayLastFixingPayoff_2F[i] = (double*)malloc(sizeof(double) * NGreed);

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
	double t, t1, t2, deltat;

	long Today, EndDate1, EndDate2, ncpn, ncpn1, ncpn2, isinflag = 0;
	double df_t, df_T, df_T_Rcv, df_T_Pay, temp = 0., temp2 = 0.;
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
		if (PowerSpreadFlagRcv == 0)
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
				else Rcv_dt[i][j] = DayCountFractionAtoB(TempDateArray[j - 1], TempDateArray[j], DayCountRcvPay[0]);
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
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, y, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
						Rate_Rcv_2F[i][idx1][idx2] = Rate;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, y, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
					Rate_Rcv_1F[i][idx1] = Rate;
				}
			}

			if (Today == PriceDate)
			{
				temp = 0.;
				for (j = 0; j < ncpn; j++) temp += Rcv_dt[i][j] * Rcv_DF_t_T[i][j];
				temp = (1.0 - Rcv_DF_t_T[i][ncpn - 1]) / temp;

				if (HW2FFlag == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Rcv_1F[i][idx1] = temp;
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Rcv_2F[i][idx1][idx2] = temp;
						}
					}
				}
			}
			else if (Today <= PriceDate)
			{
				isinflag = -1;
				for (j = 0; j < NRcvRateHistory; j++)
				{
					if (RcvRateHistoryDate[j] == Today)
					{
						isinflag = j;
						break;
					}
				}

				if (isinflag >= 0)
				{
					if (HW2FFlag == 0)
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							Rate_Rcv_1F[i][idx1] = RcvRateHistory[isinflag];
						}
					}
					else
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							for (idx2 = 0; idx2 < NGreed; idx2++)
							{
								Rate_Rcv_2F[i][idx1][idx2] = RcvRateHistory[isinflag];;
							}
						}
					}
				}
				else
				{
					if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) Rate_Rcv_1F[i][idx1] = 0.;
					else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) Rate_Rcv_2F[i][idx1][idx2] = 0.;
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
			Rcv_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn1);

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
				else Rcv_dt[i][j] = DayCountFractionAtoB(TempDateArray[j - 1], TempDateArray[j], DayCountRcvPay[0]);
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
				if (j == 0) RcvPowerSpread_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray2[j], DayCountRcvPay[0]);
				else RcvPowerSpread_dt[i][j] = DayCountFractionAtoB(TempDateArray2[j - 1], TempDateArray2[j], DayCountRcvPay[0]);
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
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn1, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, y, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
						Rate_Rcv_2F[i][idx1][idx2] = Rate;
						Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn2, NCPN_ANN_Rcv, RcvPowerSpread_DF_t_T[i], RcvPowerSpread_QVTerm[i], RcvPowerSpread_B_t_T[i], RcvPowerSpread_dt[i], HW2FFlag, y, RcvPowerSpread_QVTerm_2F[i], RcvPowerSpread_B_t_T_2F[i], RcvPowerSpread_Cross_t_T_2F[i]);
						Rate_RcvPowerSpread_2F[i][idx1][idx2] = Rate_p;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn1, NCPN_ANN_Rcv, Rcv_DF_t_T[i], Rcv_QVTerm[i], Rcv_B_t_T[i], Rcv_dt[i], HW2FFlag, y, Rcv_QVTerm_2F[i], Rcv_B_t_T_2F[i], Rcv_Cross_t_T_2F[i]);
					Rate_Rcv_1F[i][idx1] = Rate;
					Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn2, NCPN_ANN_Rcv, RcvPowerSpread_DF_t_T[i], RcvPowerSpread_QVTerm[i], RcvPowerSpread_B_t_T[i], RcvPowerSpread_dt[i], HW2FFlag, y, RcvPowerSpread_QVTerm_2F[i], RcvPowerSpread_B_t_T_2F[i], RcvPowerSpread_Cross_t_T_2F[i]);
					Rate_RcvPowerSpread_1F[i][idx1] = Rate_p;
				}
			}

			if (Today == PriceDate)
			{
				temp = 0.;
				for (j = 0; j < ncpn1; j++) temp += Rcv_dt[i][j] * Rcv_DF_t_T[i][j];
				temp = (1.0 - Rcv_DF_t_T[i][ncpn1 - 1]) / temp;
				temp2 = 0.;
				for (j = 0; j < ncpn2; j++) temp += RcvPowerSpread_dt[i][j] * RcvPowerSpread_DF_t_T[i][j];
				temp2 = (1.0 - RcvPowerSpread_DF_t_T[i][ncpn2 - 1]) / temp2;

				if (HW2FFlag == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Rcv_1F[i][idx1] = temp;
						Rate_RcvPowerSpread_1F[i][idx1] = temp2;
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Rcv_2F[i][idx1][idx2] = temp;
							Rate_RcvPowerSpread_2F[i][idx1][idx2] = temp2;
						}
					}
				}
			}
			else if (Today <= PriceDate)
			{
				isinflag = -1;
				for (j = 0; j < NRcvRateHistory; j++)
				{
					if (RcvRateHistoryDate[j] == Today)
					{
						isinflag = j;
						break;
					}
				}

				if (isinflag >= 0)
				{
					if (HW2FFlag == 0)
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							Rate_Rcv_1F[i][idx1] = RcvRateHistory[isinflag];
						}
					}
					else
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							for (idx2 = 0; idx2 < NGreed; idx2++)
							{
								Rate_Rcv_2F[i][idx1][idx2] = RcvRateHistory[isinflag];;
							}
						}
					}
				}
				else
				{
					if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) Rate_Rcv_1F[i][idx1] = 0.;
					else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) Rate_Rcv_2F[i][idx1][idx2] = 0.;
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
		if (PowerSpreadFlagPay == 0)
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
				else Pay_dt[i][j] = DayCountFractionAtoB(TempDateArray[j - 1], TempDateArray[j], DayCountRcvPay[1]);
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
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, y, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
						Rate_Pay_2F[i][idx1][idx2] = Rate;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, y, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
					Rate_Pay_1F[i][idx1] = Rate;
				}
			}

			if (Today == PriceDate)
			{
				temp = 0.;
				for (j = 0; j < ncpn; j++) temp += Pay_dt[i][j] * Pay_DF_t_T[i][j];
				temp = (1.0 - Pay_DF_t_T[i][ncpn - 1]) / temp;
				if (HW2FFlag == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Pay_1F[i][idx1] = temp;
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Pay_2F[i][idx1][idx2] = temp;
						}
					}
				}
			}
			else if (Today <= PriceDate)
			{
				isinflag = -1;
				for (j = 0; j < NPayRateHistory; j++)
				{
					if (PayRateHistoryDate[j] == Today)
					{
						isinflag = j;
						break;
					}
				}

				if (isinflag >= 0)
				{
					if (HW2FFlag == 0)
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							Rate_Pay_1F[i][idx1] = PayRateHistory[isinflag];
						}
					}
					else
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							for (idx2 = 0; idx2 < NGreed; idx2++)
							{
								Rate_Pay_2F[i][idx1][idx2] = PayRateHistory[isinflag];;
							}
						}
					}
				}
				else
				{
					if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) Rate_Pay_1F[i][idx1] = 0.;
					else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) Rate_Pay_2F[i][idx1][idx2] = 0.;
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
			Pay_Cross_t_T_2F[i] = (double*)malloc(sizeof(double) * ncpn1);

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
				else Pay_dt[i][j] = DayCountFractionAtoB(TempDateArray[j - 1], TempDateArray[j], DayCountRcvPay[1]);
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
				if (j == 0) PayPowerSpread_dt[i][j] = DayCountFractionAtoB(Today, TempDateArray2[j], DayCountRcvPay[1]);
				else PayPowerSpread_dt[i][j] = DayCountFractionAtoB(TempDateArray2[j - 1], TempDateArray2[j], DayCountRcvPay[1]);
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
						Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn1, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, y, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
						Rate_Pay_2F[i][idx1][idx2] = Rate;
						Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn2, NCPN_ANN_Pay, PayPowerSpread_DF_t_T[i], PayPowerSpread_QVTerm[i], PayPowerSpread_B_t_T[i], PayPowerSpread_dt[i], HW2FFlag, y, PayPowerSpread_QVTerm_2F[i], PayPowerSpread_B_t_T_2F[i], PayPowerSpread_Cross_t_T_2F[i]);
						Rate_PayPowerSpread_2F[i][idx1][idx2] = Rate_p;
					}
				}
			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					x = xt[idx1];
					Rate = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn1, NCPN_ANN_Pay, Pay_DF_t_T[i], Pay_QVTerm[i], Pay_B_t_T[i], Pay_dt[i], HW2FFlag, y, Pay_QVTerm_2F[i], Pay_B_t_T_2F[i], Pay_Cross_t_T_2F[i]);
					Rate_Pay_1F[i][idx1] = Rate;
					Rate_p = HW_Rate(1, NZeroRate, ZeroTerm, ZeroRate, x, ncpn2, NCPN_ANN_Pay, PayPowerSpread_DF_t_T[i], PayPowerSpread_QVTerm[i], PayPowerSpread_B_t_T[i], PayPowerSpread_dt[i], HW2FFlag, y, PayPowerSpread_QVTerm_2F[i], PayPowerSpread_B_t_T_2F[i], PayPowerSpread_Cross_t_T_2F[i]);
					Rate_PayPowerSpread_1F[i][idx1] = Rate_p;
				}
			}

			if (Today == PriceDate)
			{
				temp = 0.;
				for (j = 0; j < ncpn1; j++) temp += Pay_dt[i][j] * Pay_DF_t_T[i][j];
				temp = (1.0 - Pay_DF_t_T[i][ncpn1 - 1]) / temp;
				temp2 = 0.;
				for (j = 0; j < ncpn2; j++) temp += PayPowerSpread_dt[i][j] * PayPowerSpread_DF_t_T[i][j];
				temp2 = (1.0 - PayPowerSpread_DF_t_T[i][ncpn2 - 1]) / temp2;

				if (HW2FFlag == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Pay_1F[i][idx1] = temp;
						Rate_PayPowerSpread_1F[i][idx1] = temp2;
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Pay_2F[i][idx1][idx2] = temp;
							Rate_PayPowerSpread_2F[i][idx1][idx2] = temp2;
						}
					}
				}
			}
			else if (Today <= PriceDate)
			{
				isinflag = -1;
				for (j = 0; j < NPayRateHistory; j++)
				{
					if (PayRateHistoryDate[j] == Today)
					{
						isinflag = j;
						break;
					}
				}

				if (isinflag >= 0)
				{
					if (HW2FFlag == 0)
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							Rate_Pay_1F[i][idx1] = PayRateHistory[isinflag];
						}
					}
					else
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							for (idx2 = 0; idx2 < NGreed; idx2++)
							{
								Rate_Pay_2F[i][idx1][idx2] = PayRateHistory[isinflag];;
							}
						}
					}
				}
				else
				{
					if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) Rate_Pay_1F[i][idx1] = 0.;
					else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) Rate_Pay_2F[i][idx1][idx2] = 0.;
				}
			}

			free(TempDateArray);
			free(TempDateArray2);
		}
	}

	double* SlopeOfFixingRate_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* SlopeOfPayoff_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* FixedRate_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	long* Structured_Rcv = (long*)malloc(sizeof(long) * NCpnDateRcv);
	double* RangeCpn_Rcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	double* DeltatRcv = (double*)malloc(sizeof(double) * NCpnDateRcv);
	long* ZeroCouponFlagRcv = (long*)malloc(sizeof(long) * NCpnDateRcv);

	double* SlopeOfFixingRate_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* SlopeOfPayoff_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* FixedRate_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	long* Structured_Pay = (long*)malloc(sizeof(long) * NCpnDatePay);
	double* RangeCpn_Pay = (double*)malloc(sizeof(double) * NCpnDatePay);
	double* DeltatPay = (double*)malloc(sizeof(double) * NCpnDatePay);
	long* ZeroCouponFlagPay = (long*)malloc(sizeof(long) * NCpnDatePay);

	long* CpnDateRcv = CpnDate[0];
	long* CpnDatePay = CpnDate[1];
	long DayCountFracRcv = DayCountRcvPay[0];
	long DayCountFracPay = DayCountRcvPay[1];
	for (i = 0; i < NCpnDateRcv; i++)
	{
		SlopeOfFixingRate_Rcv[i] = MultipleRatefixPayoffRcv[0];
		SlopeOfPayoff_Rcv[i] = MultipleRatefixPayoffRcv[1];
		DeltatRcv[i] = DayCountFractionAtoB(RcvFixingDate[i], CpnDateRcv[i], DayCountFracRcv);
		if (RcvFixingDate[i] >= Phase2Date)
		{
			FixedRate_Rcv[i] = Phase2RcvLegFixedRate;
			Structured_Rcv[i] = Phase2RcvLegStructuredFlag;
			RangeCpn_Rcv[i] = Phase2RcvLegRangeCoupon;
			if (NumCpnAnnPhase2RcvPay[0] == 0 ) ZeroCouponFlagRcv[i] = 1;
			else if (NumCpnAnnPhase2RcvPay[0] == -1) ZeroCouponFlagRcv[i] = 2;
			else if (NumCpnAnnPhase2RcvPay[0] == -2) ZeroCouponFlagRcv[i] = 3;
			else ZeroCouponFlagRcv[i] = 0;
		}
		else
		{
			FixedRate_Rcv[i] = RcvLegFixedRate;
			Structured_Rcv[i] = RcvLegStructuredFlag;
			RangeCpn_Rcv[i] = RcvLegRangeCoupon;
			if (NumCpnAnn[0] == 0 ) ZeroCouponFlagRcv[i] = 1;
			else if (NumCpnAnn[0] == -1) ZeroCouponFlagRcv[i] = 2;
			else if (NumCpnAnn[0] == -2) ZeroCouponFlagRcv[i] = 3;
			else ZeroCouponFlagRcv[i] = 0;
		}
	}
	for (i = 0; i < NCpnDatePay; i++)
	{
		SlopeOfFixingRate_Pay[i] = MultipleRatefixPayoffPay[0];
		SlopeOfPayoff_Pay[i] = MultipleRatefixPayoffPay[1];
		DeltatPay[i] = DayCountFractionAtoB(PayFixingDate[i], CpnDatePay[i], DayCountFracPay);
		if (PayFixingDate[i] >= Phase2Date)
		{
			FixedRate_Pay[i] = Phase2PayLegFixedRate;
			Structured_Pay[i] = Phase2PayLegStructuredFlag;
			RangeCpn_Pay[i] = Phase2PayLegRangeCoupon;
			if (NumCpnAnnPhase2RcvPay[1] == 0) ZeroCouponFlagPay[i] = 1;
			else if (NumCpnAnnPhase2RcvPay[1] == -1) ZeroCouponFlagPay[i] = 2;
			else if (NumCpnAnnPhase2RcvPay[1] == -2) ZeroCouponFlagPay[i] = 3;
			else ZeroCouponFlagPay[i] = 0;
		}
		else
		{
			FixedRate_Pay[i] = PayLegFixedRate;
			Structured_Pay[i] = PayLegStructuredFlag;
			RangeCpn_Pay[i] = PayLegRangeCoupon;
			if (NumCpnAnn[1] == 0) ZeroCouponFlagPay[i] = 1;
			else if (NumCpnAnn[1] == -1) ZeroCouponFlagPay[i] = 2;
			else if (NumCpnAnn[1] == -2) ZeroCouponFlagPay[i] = 3;
			else ZeroCouponFlagPay[i] = 0;
		}
	}

	double* Alpha_1Curve = (double*)malloc(sizeof(double) * NGreed);		// IFDM 1F x_t Alpha or OS x_t 
	double* Beta_1Curve = (double*)malloc(sizeof(double) * NGreed);
	double* Gamma_1Curve = (double*)malloc(sizeof(double) * NGreed);

	double* Alpha_2Curve = (double*)malloc(sizeof(double) * NGreed);		// OS y_t 
	double* Beta_2Curve = (double*)malloc(sizeof(double) * NGreed);
	double* Gamma_2Curve = (double*)malloc(sizeof(double) * NGreed);

	double* FDMValue_1F = (double*)malloc(sizeof(double) * NGreed);
	double** FDMValue_2F = (double**)malloc(sizeof(double*) * NGreed);
	for (i = 0; i < NGreed; i++) FDMValue_2F[i] = (double*)malloc(sizeof(double) * NGreed);
	double** RHSValue_2F = (double**)malloc(sizeof(double*) * NGreed);
	for (i = 0; i < NGreed; i++) RHSValue_2F[i] = (double*)malloc(sizeof(double) * NGreed);

	double* TempAlphaArray = (double*)malloc(sizeof(double) * NGreed);
	double* TempBetaArray = (double*)malloc(sizeof(double) * NGreed);
	double* TempGammaArray = (double*)malloc(sizeof(double) * NGreed);
	double* TempCpnArrayRcv_1F = (double*)malloc(sizeof(double) * NGreed);
	double* TempCpnArrayPay_1F = (double*)malloc(sizeof(double) * NGreed);
	double** TempCpnArrayRcv_2F = (double**)malloc(sizeof(double*) * NGreed);
	double** TempCpnArrayPay_2F = (double**)malloc(sizeof(double*) * NGreed);
	for (i = 0; i < NGreed; i++)
	{
		TempCpnArrayRcv_2F[i] = (double*)malloc(sizeof(double) * NGreed);
		TempCpnArrayPay_2F[i] = (double*)malloc(sizeof(double) * NGreed);
	}

	double vol1 = 0., vol2 = 0., b0, c0, bN, aN, fwdvar, vols, volt;
	double Rate_Rcv, Rate_Pay, Rate_Rcv_p, Rate_Pay_p, RcvCpn, PayCpn, RgCpnRcv, RgCpnPay;
	double Instant_FwdDF, Instant_B_s_t, Instant_QVTerm, Instant_B_s_t_2F, Instant_QVTerm_2F, Instant_Cross_QVTerm_2F, R, PtT;
	long LastFixingDateRcv, LastFixingDatePay, LastFixingIdxRcv = 0, LastFixingIdxPay = 0, idxrcv = 0, idxpay = 0, idxrcvfix = 0, idxpayfix = 0, idxhist = 0;

	long** OptionExerciseFlag_2F = (long**)malloc(sizeof(long*) * NGreed);
	for (i = 0; i < NGreed; i++) OptionExerciseFlag_2F[i] = (long*)malloc(sizeof(long) * NGreed);
	long* OptionExerciseFlag_1F = (long*)malloc(sizeof(long) * NGreed);

	double* ForPrintVariable = (double*)malloc(sizeof(double) * 4);
	double deltat_fixing_to_pay = 0.;
	LastFixingDateRcv = RcvFixingDate[NCpnDateRcv - 1];
	LastFixingDatePay = PayFixingDate[NCpnDatePay - 1];
	for (i = 0; i < NTotalSimul; i++)
	{
		if (TotalArrayDateSimul[i] == LastFixingDateRcv)
		{
			LastFixingIdxRcv = i;
			break;
		}
	}
	for (i = 0; i < NTotalSimul; i++)
	{
		if (TotalArrayDateSimul[i] == LastFixingDatePay)
		{
			LastFixingIdxPay = i;
			break;
		}
	}

	long nextoptidx = max(0, NOption - 1);
	long LastFixingIdx = -1;
	double LastFixingPayaoff = 0., cmpv = 0.;
	n = 0;
	for (i = 0; i < NTotalSimul; i++)
	{
		Today = TotalArrayDateSimul[NTotalSimul - 1 - i];
		t = Time[NTotalSimul - 1 - i];
		if (n == 0)
		{
			if (TextFlag > 0)
			{
				ForPrintVariable[0] = (double)Today;
				ForPrintVariable[1] = t;
				ForPrintVariable[2] = t;
				ForPrintVariable[3] = 1.0;
				DumppingTextDataArray(CalcFunctionName, SaveFileName, "DF_in_FDMTimeGreed", 4, ForPrintVariable);
			}

			if (HW2FFlag > 0)
			{
				if (PowerSpreadFlagRcv == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Rcv = Rate_Rcv_2F[LastFixingIdxRcv][idx1][idx2];
							RgCpnRcv = 0.;
							if (Structured_Rcv[NCpnDateRcv - 1] > 0)
							{
								Rate = SlopeOfFixingRate_Rcv[NCpnDateRcv - 1] * Rate_Rcv;
								if ((Rate < RangeMaxMinRcv[0]) && (Rate > RangeMaxMinRcv[1])) RgCpnRcv = (SlopeOfPayoff_Rcv[NCpnDateRcv - 1] * Rate_Rcv) + RangeCpn_Rcv[NCpnDateRcv - 1];
							}
							
							if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 0)
							{
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * DeltatRcv[NCpnDateRcv - 1])), RoundingRcv);
							}
							else if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 1)
							{
								deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
							}
							else 
							{
								deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
							}
							TempCpnArrayRcv_2F[idx1][idx2] = RcvCpn;
							FDMValue_2F[idx1][idx2] = RcvCpn;
						}
					}
					ResultFixingRateCpnRcv[NCpnDateRcv - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Rcv_2F[LastFixingIdxRcv], 0.0, 0.0);
					ResultFixingRateCpnRcv[2 * NCpnDateRcv - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayRcv_2F, 0.0, 0.0);
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Rcv = Rate_Rcv_2F[LastFixingIdxRcv][idx1][idx2];
							Rate_Rcv_p = Rate_RcvPowerSpread_2F[LastFixingIdxRcv][idx1][idx2];
							RgCpnRcv = 0.;
							if (Structured_Rcv[NCpnDateRcv - 1] > 0)
							{
								Rate = SlopeOfFixingRate_Rcv[NCpnDateRcv - 1] * (Rate_Rcv - Rate_Rcv_p);
								if ((Rate < RangeMaxMinRcv[0]) && (Rate > RangeMaxMinRcv[1])) RgCpnRcv = (SlopeOfPayoff_Rcv[NCpnDateRcv - 1] * (Rate_Rcv - Rate_Rcv_p)) + RangeCpn_Rcv[NCpnDateRcv - 1];
							}

							if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 0)
							{
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * DeltatRcv[NCpnDateRcv - 1])), RoundingRcv);
							}
							else if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 1)
							{
								deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
							}
							else
							{
								deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
								RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
							}
							TempCpnArrayRcv_2F[idx1][idx2] = RcvCpn;
							FDMValue_2F[idx1][idx2] = RcvCpn;
						}
					}
					ResultFixingRateCpnRcv[NCpnDateRcv - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Rcv_2F[LastFixingIdxRcv], 0.0, 0.0) - Calc_Volatility(NGreed, NGreed, xt, yt, Rate_RcvPowerSpread_2F[LastFixingIdxRcv], 0.0, 0.0);
					ResultFixingRateCpnRcv[2 * NCpnDateRcv - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayRcv_2F, 0.0, 0.0);
				}

				if (PowerSpreadFlagPay == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Pay = Rate_Pay_2F[LastFixingIdxPay][idx1][idx2];
							RgCpnPay = 0.;
							if (Structured_Pay[NCpnDatePay - 1] > 0)
							{
								Rate = SlopeOfFixingRate_Pay[NCpnDatePay - 1] * Rate_Pay;
								if ((Rate < RangeMaxMinPay[0]) && (Rate > RangeMaxMinPay[1])) RgCpnPay = (SlopeOfPayoff_Pay[NCpnDatePay - 1] * Rate_Pay) + RangeCpn_Pay[NCpnDatePay - 1];
							}

							if (ZeroCouponFlagPay[NCpnDatePay - 1] == 0)
							{
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * DeltatPay[NCpnDatePay - 1])), RoundingPay);
							}
							else if (ZeroCouponFlagPay[NCpnDatePay - 1] == 1)
							{
								deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay, deltat_fixing_to_pay) - 1.0)), RoundingPay);
							}
							else 
							{
								deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
							}
							TempCpnArrayPay_2F[idx1][idx2] = PayCpn;
							FDMValue_2F[idx1][idx2] -= PayCpn;
						}
					}
					ResultFixingRateCpnPay[NCpnDatePay - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Pay_2F[LastFixingIdxPay], 0.0, 0.0);
					ResultFixingRateCpnPay[2 * NCpnDatePay - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayPay_2F, 0.0, 0.0);
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							Rate_Pay = Rate_Pay_2F[LastFixingIdxPay][idx1][idx2];
							Rate_Pay_p = Rate_PayPowerSpread_2F[LastFixingIdxPay][idx1][idx2];
							RgCpnPay = 0.;
							if (Structured_Pay[NCpnDatePay - 1] > 0)
							{
								Rate = SlopeOfFixingRate_Pay[NCpnDatePay - 1] * (Rate_Pay - Rate_Pay_p);
								if ((Rate < RangeMaxMinPay[0]) && (Rate > RangeMaxMinPay[1])) RgCpnPay = (SlopeOfPayoff_Pay[NCpnDatePay - 1] * (Rate_Pay - Rate_Pay_p)) + RangeCpn_Pay[NCpnDatePay - 1];
							}

							if (ZeroCouponFlagPay[NCpnDatePay - 1] == 0)
							{
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * DeltatPay[NCpnDatePay - 1])), RoundingPay);
							}
							else if (ZeroCouponFlagPay[NCpnDatePay - 1] == 1)
							{
								deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay, deltat_fixing_to_pay) - 1.0)), RoundingPay);
							}
							else
							{
								deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
								PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
							}
							TempCpnArrayPay_2F[idx1][idx2] = PayCpn;
							FDMValue_2F[idx1][idx2] -= PayCpn;
						}
					}
					ResultFixingRateCpnPay[NCpnDatePay - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Pay_2F[LastFixingIdxPay], 0.0, 0.0) - Calc_Volatility(NGreed, NGreed, xt, yt, Rate_PayPowerSpread_2F[LastFixingIdxPay], 0.0, 0.0);
					ResultFixingRateCpnPay[2 * NCpnDatePay - 1] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayPay_2F, 0.0, 0.0);
				}
			}
			else
			{
				if (PowerSpreadFlagRcv == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Rcv = Rate_Rcv_1F[LastFixingIdxRcv][idx1];
						RgCpnRcv = 0.;
						if (Structured_Rcv[NCpnDateRcv - 1] > 0)
						{
							Rate = SlopeOfFixingRate_Rcv[NCpnDateRcv - 1] * Rate_Rcv;
							if ((Rate < RangeMaxMinRcv[0]) && (Rate > RangeMaxMinRcv[1])) RgCpnRcv = (SlopeOfPayoff_Rcv[NCpnDateRcv - 1] * Rate_Rcv) + RangeCpn_Rcv[NCpnDateRcv - 1];
						}

						if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 0)
						{
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * DeltatRcv[NCpnDateRcv - 1])), RoundingRcv);
						}
						else if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 1)
						{
							deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
						}
						else 
						{
							deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
						}
						TempCpnArrayRcv_1F[idx1] = RcvCpn;
						FDMValue_1F[idx1] = RcvCpn;
					}
					ResultFixingRateCpnRcv[NCpnDateRcv - 1] = Interpolate_Linear(xt, Rate_Rcv_1F[LastFixingIdxRcv], NGreed, 0.0);
					ResultFixingRateCpnRcv[2 * NCpnDateRcv - 1] = Interpolate_Linear(xt, TempCpnArrayRcv_1F, NGreed, 0.0);
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Rcv = Rate_Rcv_1F[LastFixingIdxRcv][idx1];
						Rate_Rcv_p = Rate_RcvPowerSpread_1F[LastFixingIdxRcv][idx1];
						RgCpnRcv = 0.;
						if (Structured_Rcv[NCpnDateRcv - 1] > 0)
						{
							Rate = SlopeOfFixingRate_Rcv[NCpnDateRcv - 1] * (Rate_Rcv - Rate_Rcv_p);
							if ((Rate < RangeMaxMinRcv[0]) && (Rate > RangeMaxMinRcv[1])) RgCpnRcv = (SlopeOfPayoff_Rcv[NCpnDateRcv - 1] * (Rate_Rcv - Rate_Rcv_p)) + RangeCpn_Rcv[NCpnDateRcv - 1];
						}

						if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 0)
						{
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * DeltatRcv[NCpnDateRcv - 1])), RoundingRcv);
						}
						else if (ZeroCouponFlagRcv[NCpnDateRcv - 1] == 1)
						{
							deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
						}
						else
						{
							deltat_fixing_to_pay = DeltatRcv[NCpnDateRcv - 1];
							RcvCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[NCpnDateRcv - 1] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
						}

						TempCpnArrayRcv_1F[idx1] = RcvCpn;
						FDMValue_1F[idx1] = RcvCpn;
					}
					ResultFixingRateCpnRcv[NCpnDateRcv - 1] = Interpolate_Linear(xt, Rate_Rcv_1F[LastFixingIdxRcv], NGreed, 0.0) - Interpolate_Linear(xt, Rate_RcvPowerSpread_1F[LastFixingIdxRcv], NGreed, 0.0);
					ResultFixingRateCpnRcv[2 * NCpnDateRcv - 1] = Interpolate_Linear(xt, TempCpnArrayRcv_1F, NGreed, 0.0);
				}

				if (PowerSpreadFlagPay == 0)
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Pay = Rate_Pay_1F[LastFixingIdxPay][idx1];
						RgCpnPay = 0.;
						if (Structured_Pay[NCpnDatePay - 1] > 0)
						{
							Rate = SlopeOfFixingRate_Pay[NCpnDatePay - 1] * Rate_Pay;
							if ((Rate < RangeMaxMinPay[0]) && (Rate > RangeMaxMinPay[1])) RgCpnPay = (SlopeOfPayoff_Pay[NCpnDatePay - 1] * Rate_Pay) + RangeCpn_Pay[NCpnDatePay - 1];
						}

						if (ZeroCouponFlagPay[NCpnDatePay - 1] == 0)
						{
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * DeltatPay[NCpnDatePay - 1])), RoundingPay);
						}
						else if (ZeroCouponFlagPay[NCpnDatePay - 1] == 1)
						{
							deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay, deltat_fixing_to_pay) - 1.0)), RoundingPay);
						}
						else
						{
							deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
						}
						TempCpnArrayPay_1F[idx1] = PayCpn;
						FDMValue_1F[idx1] -= PayCpn;
					}
					ResultFixingRateCpnPay[NCpnDatePay - 1] = Interpolate_Linear(xt, Rate_Pay_1F[LastFixingIdxPay], NGreed, 0.0);
					ResultFixingRateCpnPay[2 * NCpnDatePay - 1] = Interpolate_Linear(xt, TempCpnArrayPay_1F, NGreed, 0.0);
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						Rate_Pay = Rate_Pay_1F[LastFixingIdxPay][idx1];
						Rate_Pay_p = Rate_PayPowerSpread_1F[LastFixingIdxPay][idx1];
						RgCpnPay = 0.;
						if (Structured_Pay[NCpnDatePay - 1] > 0)
						{
							Rate = SlopeOfFixingRate_Pay[NCpnDatePay - 1] * (Rate_Pay - Rate_Pay_p);
							if ((Rate < RangeMaxMinPay[0]) && (Rate > RangeMaxMinPay[1])) RgCpnPay = (SlopeOfPayoff_Pay[NCpnDatePay - 1] * (Rate_Pay - Rate_Pay_p)) + RangeCpn_Pay[NCpnDatePay - 1];
						}

						if (ZeroCouponFlagPay[NCpnDatePay - 1] == 0)
						{
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * DeltatPay[NCpnDatePay - 1])), RoundingPay);
						}
						else if (ZeroCouponFlagPay[NCpnDatePay - 1] == 1)
						{
							deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay, deltat_fixing_to_pay) - 1.0)), RoundingPay);
						}
						else
						{
							deltat_fixing_to_pay = DeltatPay[NCpnDatePay - 1];
							PayCpn = NA * (double)NAFlag + NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[NCpnDatePay - 1] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
						}
						TempCpnArrayPay_1F[idx1] = PayCpn;
						FDMValue_1F[idx1] -= PayCpn;
					}
					ResultFixingRateCpnPay[NCpnDatePay - 1] = Interpolate_Linear(xt, Rate_Pay_1F[LastFixingIdxPay], NGreed, 0.0) - Interpolate_Linear(xt, Rate_PayPowerSpread_1F[LastFixingIdxPay], NGreed, 0.0);
					ResultFixingRateCpnPay[2 * NCpnDatePay - 1] = Interpolate_Linear(xt, TempCpnArrayPay_1F, NGreed, 0.0);
				}
			}
		}
		else
		{
			t2 = Time[NTotalSimul - i];
			t1 = Time[NTotalSimul - 1 - i];
			df_t = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, t1);
			df_T = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, t2);
			vols = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t1);
			volt = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, t2);
			vol1 = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t1 + t2) / 2.0);
			Instant_FwdDF = df_T / df_t;
			if (TextFlag > 0)
			{
				ForPrintVariable[0] = (double)Today;
				ForPrintVariable[1] = t1;
				ForPrintVariable[2] = t2;
				ForPrintVariable[3] = Instant_FwdDF;
				DumppingTextDataArray(CalcFunctionName, SaveFileName, "DF_in_FDMTimeGreed", 4, ForPrintVariable);
			}
			deltat = t2 - t1;
			Instant_B_s_t = B_s_to_t(kappa1, t1, t2);
			Instant_QVTerm = HullWhiteQVTerm(t1, t2, kappa1, 1, HWVolTerm, &vol1);
			if (HW2FFlag > 0)
			{
				vols = Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t1);
				volt = Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, t2);
				vol2 = Interpolate_Linear(HWVolTerm, HWVol2, NHWVol, (t1 + t2) / 2.0);
				Instant_B_s_t_2F = B_s_to_t(kappa2, t1, t2);
				Instant_QVTerm_2F = HullWhiteQVTerm(t1, t2, kappa2, 1, HWVolTerm, &vol2);
				Instant_Cross_QVTerm_2F = HullWhite2F_CrossTerm(t1, t2, kappa1, 1, HWVolTerm, &vol1, kappa2, HWVolTerm, &vol2, FactorCorrelation);

				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					PtT = Instant_FwdDF;
					Alpha_1Curve[idx1] = -deltat * 0.5 * (kappa1 * xt[idx1] / dxt + vol1 * vol1 / (dxt * dxt));
					Beta_1Curve[idx1] = (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0) * 0.5;
					Gamma_1Curve[idx1] = deltat * 0.5 * (kappa1 * xt[idx1] / dxt - vol1 * vol1 / (dxt * dxt));
				}

				for (idx2 = 0; idx2 < NGreed; idx2++)
				{
					PtT = Instant_FwdDF;
					Alpha_2Curve[idx2] = -deltat * 0.5 * (kappa2 * yt[idx2] / dyt + vol2 * vol2 / (dyt * dyt));
					Beta_2Curve[idx2] = (1.0 + deltat * vol2 * vol2 / (dyt * dyt)) + (1.0 / PtT - 1.0) * 0.5;
					Gamma_2Curve[idx2] = deltat * 0.5 * (kappa2 * yt[idx2] / dyt - vol2 * vol2 / (dyt * dyt));
				}

				b0 = Beta_1Curve[0] + 2.0 * Alpha_1Curve[0];
				c0 = Gamma_1Curve[0] - Alpha_1Curve[0];
				bN = Beta_1Curve[NGreed - 1] + 2.0 * Gamma_1Curve[NGreed - 1];
				aN = Alpha_1Curve[NGreed - 1] - Gamma_1Curve[NGreed - 1];
				Beta_1Curve[0] = b0;
				Gamma_1Curve[0] = c0;
				Beta_1Curve[NGreed - 1] = bN;
				Alpha_1Curve[NGreed - 1] = aN;

				ResultRHS_2F(NGreed, xt, yt, kappa1, kappa2, vol1, vol2, FactorCorrelation, dxt, dyt, deltat, FDMValue_2F, RHSValue_2F);
				Tri_diagonal_Matrix_Fast(Alpha_1Curve, Beta_1Curve, Gamma_1Curve, RHSValue_2F, NGreed, TempAlphaArray, TempBetaArray, TempGammaArray);
				TransposeMat(NGreed, RHSValue_2F);
				Copy2dMatrix(FDMValue_2F, RHSValue_2F, NGreed, NGreed);

				b0 = Beta_2Curve[0] + 2.0 * Alpha_2Curve[0];
				c0 = Gamma_2Curve[0] - Alpha_2Curve[0];
				bN = Beta_2Curve[NGreed - 1] + 2.0 * Gamma_2Curve[NGreed - 1];
				aN = Alpha_2Curve[NGreed - 1] - Gamma_2Curve[NGreed - 1];
				Beta_2Curve[0] = b0;
				Gamma_2Curve[0] = c0;
				Beta_2Curve[NGreed - 1] = bN;;
				Alpha_2Curve[NGreed - 1] = aN;
				ResultRHS_2F(NGreed, xt, yt, kappa1, kappa2, vol1, vol2, FactorCorrelation, dxt, dyt, deltat, FDMValue_2F, RHSValue_2F);
				Tri_diagonal_Matrix_Fast(Alpha_2Curve, Beta_2Curve, Gamma_2Curve, RHSValue_2F, NGreed, TempAlphaArray, TempBetaArray, TempGammaArray);
				TransposeMat(NGreed, RHSValue_2F);
				Copy2dMatrix(FDMValue_2F, RHSValue_2F, NGreed, NGreed);

			}
			else
			{
				for (idx1 = 0; idx1 < NGreed; idx1++)
				{
					PtT = Instant_FwdDF;
					Alpha_1Curve[idx1] = -deltat * 0.5 * (kappa1 * xt[idx1] / dxt + vol1 * vol1 / (dxt * dxt));
					Beta_1Curve[idx1] = (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0);
					Gamma_1Curve[idx1] = deltat * 0.5 * (kappa1 * xt[idx1] / dxt - vol1 * vol1 / (dxt * dxt));
				}

				b0 = Beta_1Curve[0] + 2.0 * Alpha_1Curve[0];
				c0 = Gamma_1Curve[0] - Alpha_1Curve[0];
				bN = Beta_1Curve[NGreed - 1] + 2.0 * Gamma_1Curve[NGreed - 1];
				aN = Alpha_1Curve[NGreed - 1] - Gamma_1Curve[NGreed - 1];
				Beta_1Curve[0] = b0;
				Gamma_1Curve[0] = c0;
				Beta_1Curve[NGreed - 1] = bN;;
				Alpha_1Curve[NGreed - 1] = aN;

				Tri_diagonal_Fast(Alpha_1Curve, Beta_1Curve, Gamma_1Curve, FDMValue_1F, NGreed, TempAlphaArray, TempBetaArray, TempGammaArray);
			}

			if (Today <= PriceDate)
			{
				// 만약 오늘이 평가일이라면 FDM 종료
				break;
			}


			if (i != 0 && isin_Longtype(Today, RcvPaymentDate, NCpnDateRcv))
			{
				idxrcv = -1;
				for (idxrcv = 0; idxrcv < NCpnDateRcv; idxrcv++)
				{
					if (RcvPaymentDate[idxrcv] == Today)
					{
						break;
					}
				}

				idxrcvfix = -1;
				for (idxrcvfix = 0; idxrcvfix < NTotalSimul; idxrcvfix++)
				{
					if (TotalArrayDateSimul[idxrcvfix] == RcvFixingDate[idxrcv])
					{
						break;
					}
				}

				if (RcvPaymentDate[idxrcv] > PriceDate)
				{
					if (TotalArrayDateSimul[idxrcvfix] >= PriceDate)
					{
						if (HW2FFlag > 0)
						{
							if (PowerSpreadFlagRcv == 0)
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									for (idx2 = 0; idx2 < NGreed; idx2++)
									{
										Rate_Rcv = Rate_Rcv_2F[idxrcvfix][idx1][idx2];
										RgCpnRcv = 0.;
										if (Structured_Rcv[idxrcv] > 0)
										{
											Rate = SlopeOfFixingRate_Rcv[idxrcv] * Rate_Rcv;
											if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[idxrcv] * Rate_Rcv + RangeCpn_Rcv[idxrcv];
										}

										if (ZeroCouponFlagRcv[idxrcv] == 0)
										{
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * DeltatRcv[idxrcv])), RoundingRcv);
										}
										else if (ZeroCouponFlagRcv[idxrcv] == 1)
										{
											deltat_fixing_to_pay = DeltatRcv[idxrcv];
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[idxrcv] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
										}
										else
										{
											deltat_fixing_to_pay = DeltatRcv[idxrcv];
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
										}
										TempCpnArrayRcv_2F[idx1][idx2] = RcvCpn;
										FDMValue_2F[idx1][idx2] += RcvCpn;
									}
								}
								ResultFixingRateCpnRcv[idxrcv] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Rcv_2F[idxrcvfix], 0.0, 0.0);
								ResultFixingRateCpnRcv[NCpnDateRcv + idxrcv] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayRcv_2F, 0.0, 0.0);
							}
							else
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									for (idx2 = 0; idx2 < NGreed; idx2++)
									{
										Rate_Rcv = Rate_Rcv_2F[idxrcvfix][idx1][idx2];
										Rate_Rcv_p = Rate_RcvPowerSpread_2F[idxrcvfix][idx1][idx2];
										RgCpnRcv = 0.;
										if (Structured_Rcv[idxrcv] > 0)
										{
											Rate = SlopeOfFixingRate_Rcv[idxrcv] * (Rate_Rcv - Rate_Rcv_p);
											if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[idxrcv] * (Rate_Rcv - Rate_Rcv_p) + RangeCpn_Rcv[idxrcv];
										}

										if (ZeroCouponFlagRcv[idxrcv] == 0)
										{
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * DeltatRcv[idxrcv])), RoundingRcv);
										}
										else if (ZeroCouponFlagRcv[idxrcv] == 1)
										{
											deltat_fixing_to_pay = DeltatRcv[idxrcv];
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[idxrcv] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
										}
										else
										{
											deltat_fixing_to_pay = DeltatRcv[idxrcv];
											RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
										}
										TempCpnArrayRcv_2F[idx1][idx2] = RcvCpn;
										FDMValue_2F[idx1][idx2] += RcvCpn;
									}
								}
								ResultFixingRateCpnRcv[idxrcv] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Rcv_2F[idxrcvfix], 0.0, 0.0) - Calc_Volatility(NGreed, NGreed, xt, yt, Rate_RcvPowerSpread_2F[idxrcvfix], 0.0, 0.0);
								ResultFixingRateCpnRcv[NCpnDateRcv + idxrcv] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayRcv_2F, 0.0, 0.0);
							}
						}
						else
						{
							if (PowerSpreadFlagRcv == 0)
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									Rate_Rcv = Rate_Rcv_1F[idxrcvfix][idx1];
									RgCpnRcv = 0.;
									if (Structured_Rcv[idxrcv] > 0)
									{
										Rate = SlopeOfFixingRate_Rcv[idxrcv] * Rate_Rcv;
										if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[idxrcv] * Rate_Rcv + RangeCpn_Rcv[idxrcv];
									}

									if (ZeroCouponFlagRcv[idxrcv] == 0)
									{
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * DeltatRcv[idxrcv])), RoundingRcv);
									}
									else if (ZeroCouponFlagRcv[idxrcv] == 1)
									{
										deltat_fixing_to_pay = DeltatRcv[idxrcv];
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[idxrcv] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)), RoundingRcv);
									}
									else
									{
										deltat_fixing_to_pay = DeltatRcv[idxrcv];
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
									}
									TempCpnArrayRcv_1F[idx1] = RcvCpn;
									FDMValue_1F[idx1] += RcvCpn;
								}
								ResultFixingRateCpnRcv[idxrcv] = Interpolate_Linear(xt, Rate_Rcv_1F[idxrcvfix], NGreed, 0.0);
								ResultFixingRateCpnRcv[NCpnDateRcv + idxrcv] = Interpolate_Linear(xt, TempCpnArrayRcv_1F, NGreed, 0.0);
							}
							else
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									Rate_Rcv = Rate_Rcv_1F[idxrcvfix][idx1];
									Rate_Rcv_p = Rate_RcvPowerSpread_1F[idxrcvfix][idx1];
									RgCpnRcv = 0.;
									if (Structured_Rcv[idxrcv] > 0)
									{
										Rate = SlopeOfFixingRate_Rcv[idxrcv] * (Rate_Rcv - Rate_Rcv_p);
										if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[idxrcv] * (Rate_Rcv - Rate_Rcv_p) + RangeCpn_Rcv[idxrcv];
									}

									if (ZeroCouponFlagRcv[idxrcv] == 0)
									{
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * DeltatRcv[idxrcv])),RoundingRcv);
									}
									else if (ZeroCouponFlagRcv[idxrcv] == 1)
									{
										deltat_fixing_to_pay = DeltatRcv[idxrcv];
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[idxrcv] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)),RoundingRcv);
									}
									else
									{
										deltat_fixing_to_pay = DeltatRcv[idxrcv];
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
									}

									TempCpnArrayRcv_1F[idx1] = RcvCpn;
									FDMValue_1F[idx1] += RcvCpn;
								}
								ResultFixingRateCpnRcv[idxrcv] = Interpolate_Linear(xt, Rate_Rcv_1F[idxrcvfix], NGreed, 0.0);
								ResultFixingRateCpnRcv[NCpnDateRcv + idxrcv] = Interpolate_Linear(xt, TempCpnArrayRcv_1F, NGreed, 0.0);
							}
						}
					}
					else if (isin_Longtype(TotalArrayDateSimul[idxrcvfix], RcvRateHistoryDate, NRcvRateHistory))
					{
						for (idxhist = 0; idxhist < NRcvRateHistory; idxhist++)
						{
							if (TotalArrayDateSimul[idxrcvfix] == RcvRateHistoryDate[idxhist])
							{
								break;
							}
						}
						Rate_Rcv = RcvRateHistory[idxhist];
						RgCpnRcv = 0.;
						if (Structured_Rcv[idxrcv] > 0)
						{
							Rate = SlopeOfFixingRate_Rcv[idxrcv] * Rate_Rcv;
							if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[idxrcv] * Rate_Rcv + RangeCpn_Rcv[idxrcv];
						}

						if (ZeroCouponFlagRcv[idxrcv] == 0)
						{
							RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * DeltatRcv[idxrcv])),RoundingRcv);
						}
						else if (ZeroCouponFlagRcv[idxrcv] == 1)
						{
							deltat_fixing_to_pay = DeltatRcv[idxrcv];
							RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], pow(1.0 + FixedRate_Rcv[idxrcv] + RgCpnRcv, deltat_fixing_to_pay) - 1.0)),RoundingRcv);
						}
						else
						{
							deltat_fixing_to_pay = DeltatRcv[idxrcv];
							RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[idxrcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
						}
						if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) FDMValue_1F[idx1] += RcvCpn;
						else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) FDMValue_2F[idx1][idx2] += RcvCpn;
						ResultFixingRateCpnRcv[idxrcv] = Rate_Rcv;
						ResultFixingRateCpnRcv[NCpnDateRcv + idxrcv] = RcvCpn;
					}
				}
				else
				{

				}
			}

			if (i != 0 && isin_Longtype(Today, PayPaymentDate, NCpnDatePay))
			{
				idxpay = -1;
				for (idxpay = 0; idxpay < NCpnDatePay; idxpay++)
				{
					if (PayPaymentDate[idxpay] == Today)
					{
						break;
					}
				}

				idxpayfix = -1;
				for (idxpayfix = 0; idxpayfix < NTotalSimul; idxpayfix++)
				{
					if (TotalArrayDateSimul[idxpayfix] == PayFixingDate[idxpay])
					{
						break;
					}
				}

				if (PayPaymentDate[idxpay] > PriceDate)
				{
					if (TotalArrayDateSimul[idxpayfix] >= PriceDate)
					{
						if (HW2FFlag > 0)
						{
							if (PowerSpreadFlagPay == 0)
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									for (idx2 = 0; idx2 < NGreed; idx2++)
									{
										Rate_Pay = Rate_Pay_2F[idxpayfix][idx1][idx2];
										RgCpnPay = 0.;
										if (Structured_Pay[idxpay] > 0)
										{
											Rate = SlopeOfFixingRate_Pay[idxpay] * Rate_Pay;
											if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[idxpay] * Rate_Pay + RangeCpn_Pay[idxpay];
										}
										
										if (ZeroCouponFlagPay[idxpay] == 0)
										{
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * DeltatPay[idxpay])), RoundingPay);
										}
										else if (ZeroCouponFlagPay[idxpay] == 1)
										{
											deltat_fixing_to_pay = DeltatPay[idxpay];
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[idxpay] + RgCpnPay, deltat_fixing_to_pay) - 1.0)),RoundingPay);
										}
										else
										{
											deltat_fixing_to_pay = DeltatPay[idxpay];
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
										}
										TempCpnArrayPay_2F[idx1][idx2] = PayCpn;
										FDMValue_2F[idx1][idx2] -= PayCpn;
									}
								}
								ResultFixingRateCpnPay[idxpay] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Pay_2F[idxpayfix], 0.0, 0.0);
								ResultFixingRateCpnPay[NCpnDatePay + idxpay] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayPay_2F, 0.0, 0.0);
							}
							else
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									for (idx2 = 0; idx2 < NGreed; idx2++)
									{
										Rate_Pay = Rate_Pay_2F[idxpayfix][idx1][idx2];
										Rate_Pay_p = Rate_PayPowerSpread_2F[idxpayfix][idx1][idx2];
										RgCpnPay = 0.;
										if (Structured_Pay[idxpay] > 0)
										{
											Rate = SlopeOfFixingRate_Pay[idxpay] * (Rate_Pay - Rate_Pay_p);
											if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[idxpay] * (Rate_Pay - Rate_Pay_p) + RangeCpn_Pay[idxpay];
										}
										
										if (ZeroCouponFlagPay[idxpay] == 0)
										{
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * DeltatPay[idxpay])),RoundingPay);
										}
										else if (ZeroCouponFlagPay[idxpay] == 1)
										{
											deltat_fixing_to_pay = DeltatPay[idxpay];
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[idxpay] + RgCpnPay, deltat_fixing_to_pay) - 1.0)),RoundingPay);
										}
										else
										{
											deltat_fixing_to_pay = DeltatPay[idxpay];
											PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
										}
										TempCpnArrayPay_2F[idx1][idx2] = PayCpn;
										FDMValue_2F[idx1][idx2] -= PayCpn;
									}
								}
								ResultFixingRateCpnPay[idxpay] = Calc_Volatility(NGreed, NGreed, xt, yt, Rate_Pay_2F[idxpayfix], 0.0, 0.0) - Calc_Volatility(NGreed, NGreed, xt, yt, Rate_PayPowerSpread_2F[idxpayfix], 0.0, 0.0);
								ResultFixingRateCpnPay[NCpnDatePay + idxpay] = Calc_Volatility(NGreed, NGreed, xt, yt, TempCpnArrayPay_2F, 0.0, 0.0);
							}
						}
						else
						{
							if (PowerSpreadFlagPay == 0)
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									Rate_Pay = Rate_Pay_1F[idxpayfix][idx1];
									RgCpnPay = 0.;
									if (Structured_Pay[idxpay] > 0)
									{
										Rate = SlopeOfFixingRate_Pay[idxpay] * Rate_Pay;
										if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[idxpay] * Rate_Pay + RangeCpn_Pay[idxpay];
									}

									if (ZeroCouponFlagPay[idxpay] == 0)
									{
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * DeltatPay[idxpay])),RoundingPay);
									}
									else if (ZeroCouponFlagPay[idxpay] == 1)
									{
										deltat_fixing_to_pay = DeltatPay[idxpay];
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[idxpay] + RgCpnPay, deltat_fixing_to_pay) - 1.0)),RoundingPay);
									}
									else
									{
										deltat_fixing_to_pay = DeltatPay[idxpay];
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
									}
									TempCpnArrayPay_1F[idx1] = PayCpn;
									FDMValue_1F[idx1] -= PayCpn;
								}
								ResultFixingRateCpnPay[idxpay] = Interpolate_Linear(xt, Rate_Pay_1F[idxpayfix], NGreed, 0.0);
								ResultFixingRateCpnPay[NCpnDatePay + idxpay] = Interpolate_Linear(xt, TempCpnArrayPay_1F, NGreed, 0.0);
							}
							else
							{
								for (idx1 = 0; idx1 < NGreed; idx1++)
								{
									Rate_Pay = Rate_Pay_1F[idxpayfix][idx1];
									Rate_Pay_p = Rate_PayPowerSpread_1F[idxpayfix][idx1];
									RgCpnPay = 0.;
									if (Structured_Pay[idxpay] > 0)
									{
										Rate = SlopeOfFixingRate_Pay[idxpay] * (Rate_Pay - Rate_Pay_p);
										if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[idxpay] * (Rate_Pay - Rate_Pay_p) + RangeCpn_Pay[idxpay];
									}

									if (ZeroCouponFlagPay[idxpay] == 0)
									{
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * DeltatPay[idxpay])),RoundingPay);
									}
									else if (ZeroCouponFlagPay[idxpay] == 1)
									{
										deltat_fixing_to_pay = DeltatPay[idxpay];
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[idxpay] + RgCpnPay, deltat_fixing_to_pay) - 1.0)),RoundingPay);
									}
									else
									{
										deltat_fixing_to_pay = DeltatPay[idxpay];
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
									}
									TempCpnArrayPay_1F[idx1] = PayCpn;
									FDMValue_1F[idx1] -= PayCpn;
								}
								ResultFixingRateCpnPay[idxpay] = Interpolate_Linear(xt, Rate_Pay_1F[idxpayfix], NGreed, 0.0);
								ResultFixingRateCpnPay[NCpnDatePay + idxpay] = Interpolate_Linear(xt, TempCpnArrayPay_1F, NGreed, 0.0);
							}
						}
					}
					else if (isin_Longtype(TotalArrayDateSimul[idxpayfix], PayRateHistoryDate, NPayRateHistory))// History 참고
					{
						for (idxhist = 0; idxhist < NPayRateHistory; idxhist++)
						{
							if (TotalArrayDateSimul[idxpayfix] == PayRateHistoryDate[idxhist])
							{
								break;
							}
						}
						Rate_Pay = PayRateHistory[idxhist];
						RgCpnPay = 0.;
						if (Structured_Pay[idxpay] > 0)
						{
							Rate = SlopeOfFixingRate_Pay[idxpay] * Rate_Pay;
							if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[idxpay] * Rate_Pay + RangeCpn_Pay[idxpay];
						}

						if (ZeroCouponFlagPay[idxpay] == 0)
						{
							PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * DeltatPay[idxpay])),RoundingPay);
						}
						else if (ZeroCouponFlagPay[idxpay] == 1)
						{
							deltat_fixing_to_pay = DeltatPay[idxpay];
							PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], pow(1.0 + FixedRate_Pay[idxpay] + RgCpnPay, deltat_fixing_to_pay) - 1.0)),RoundingPay);
						}
						else
						{
							deltat_fixing_to_pay = DeltatPay[idxpay];
							PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[idxpay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
						}
						if (HW2FFlag == 0) for (idx1 = 0; idx1 < NGreed; idx1++) FDMValue_1F[idx1] -= PayCpn;
						else for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) FDMValue_2F[idx1][idx2] -= PayCpn;
						ResultFixingRateCpnPay[idxpay] = Rate_Pay;
						ResultFixingRateCpnPay[NCpnDatePay + idxpay] = PayCpn;
					}
				}
				else
				{

				}
			}

			if (i != 0 && NOption > 0 && (Today <= OptionPayDate[nextoptidx] && Today >= OptionDate[nextoptidx]))
			{
				if (Today == OptionPayDate[nextoptidx])
				{
					if (HW2FFlag == 0)
					{
						for (idx1 = 0; idx1 < NGreed; idx1++) OptionExerciseFlag_1F[idx1] = 0;
					}
					else
					{
						for (idx1 = 0; idx1 < NGreed; idx1++) for (idx2 = 0; idx2 < NGreed; idx2++) OptionExerciseFlag_2F[idx1][idx2] = 0;
					}
				}

				t1 = t;
				t2 = ((double)DayCountAtoB(PriceDate, OptionPayDate[nextoptidx])) / 365.;
				df_T = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroRate, t2);
				df_t = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroRate, t1);

				LastFixingIdxRcv = -1;
				for (idx1 = 0; idx1 < NCpnDateRcv; idx1++)
				{
					if (OptionDate[nextoptidx] <= RcvPaymentDate[idx1] && RcvFixingDate[idx1] <= OptionDate[nextoptidx])
					{
						LastFixingIdxRcv = idx1;
						break;
					}
				}

				idxrcv = -1;
				if (LastFixingIdxRcv >= 0)
				{
					for (idx1 = 0; idx1 < NTotalSimul; idx1++)
					{
						if (RcvFixingDate[LastFixingIdxRcv] == TotalArrayDateSimul[idx1])
						{
							idxrcv = idx1;
							break;
						}
					}
				}

				DF_to_LastPayDate_Rcv = df_T;
				AccCpnDFRcv = df_T;
				AccZeroCpnRcv = 0.;
				if (LastFixingIdxRcv >= 0)
				{					
					if (ZeroCouponFlagRcv[LastFixingIdxRcv] > 0)
					{
						// ZeroCouponCallable Swap 관련 보정
						//DF_to_LastPayDate_Rcv = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, DayCountFractionAtoB(PriceDate, RcvPaymentDate[NCpnDateRcv - 1], 0));
						AccCpnDFRcv = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, DayCountFractionAtoB(PriceDate, RcvPaymentDate[NCpnDateRcv - 1], 0));
						if (nextoptidx > 0)
						{
							if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 1)
							{
								deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx-1], 3));
								cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv], deltat_fixing_to_pay);
								AccZeroCpnRcv = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], cmpv - 1.0)), RoundingRcv);
							}
							else if (ZeroCouponFlagRcv[LastFixingIdxRcv] >= 1)
							{
								deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx-1], 3));
								AccZeroCpnRcv = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], FixedRate_Rcv[LastFixingIdxRcv] * deltat_fixing_to_pay)), RoundingRcv);
							}
						}
					}

					if (HW2FFlag > 0)
					{
						if (PowerSpreadFlagRcv == 0)
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								for (idx2 = 0; idx2 < NGreed; idx2++)
								{
									Rate_Rcv = Rate_Rcv_2F[idxrcv][idx1][idx2];
									RgCpnRcv = 0.;
									if (Structured_Rcv[LastFixingIdxRcv] > 0)
									{
										Rate = SlopeOfFixingRate_Rcv[LastFixingIdxRcv] * Rate_Rcv;
										if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[LastFixingIdxRcv] * Rate_Rcv + RangeCpn_Rcv[LastFixingIdxRcv];
									}

									if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 0)
									{
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * DeltatRcv[LastFixingIdxRcv])),RoundingRcv);
									}
									else if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 1)
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], cmpv - 1.0)),RoundingRcv);
									}
									else
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
									}
									RcvLastFixingPayoff_2F[idx1][idx2] = RcvCpn;
								}
							}
						}
						else
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								for (idx2 = 0; idx2 < NGreed; idx2++)
								{
									Rate_Rcv = Rate_Rcv_2F[idxrcv][idx1][idx2];
									Rate_Rcv_p = Rate_RcvPowerSpread_2F[idxrcv][idx1][idx2];
									RgCpnRcv = 0.;
									if (Structured_Rcv[LastFixingIdxRcv] > 0)
									{
										Rate = SlopeOfFixingRate_Rcv[LastFixingIdxRcv] * (Rate_Rcv - Rate_Rcv_p);
										if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[LastFixingIdxRcv] * (Rate_Rcv - Rate_Rcv_p) + RangeCpn_Rcv[LastFixingIdxRcv];
									}
									
									if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 0)
									{
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * DeltatRcv[LastFixingIdxRcv])), RoundingRcv);
									}
									else if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 1)
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3)) ;
										cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], cmpv - 1.0)),RoundingRcv);
									}
									else
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
										RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
									}
									RcvLastFixingPayoff_2F[idx1][idx2] = RcvCpn;
								}
							}
						}
					}
					else
					{
						if (PowerSpreadFlagRcv == 0)
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								Rate_Rcv = Rate_Rcv_1F[idxrcv][idx1];
								RgCpnRcv = 0.;
								if (Structured_Rcv[LastFixingIdxRcv] > 0)
								{
									Rate = SlopeOfFixingRate_Rcv[LastFixingIdxRcv] * Rate_Rcv;
									if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[LastFixingIdxRcv] * Rate_Rcv + RangeCpn_Rcv[LastFixingIdxRcv];
								}
								
								if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 0)
								{
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * DeltatRcv[LastFixingIdxRcv])), RoundingRcv);
								}
								else if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 1)
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3)) ;
									cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], cmpv - 1.0)),RoundingRcv);
								}
								else
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
								}
								RcvLastFixingPayoff_1F[idx1] = RcvCpn;
							}
						}
						else
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								Rate_Rcv = Rate_Rcv_1F[idxrcv][idx1];
								Rate_Rcv_p = Rate_RcvPowerSpread_1F[idxrcv][idx1];
								RgCpnRcv = 0.;
								if (Structured_Rcv[LastFixingIdxRcv] > 0)
								{
									Rate = SlopeOfFixingRate_Rcv[LastFixingIdxRcv] * (Rate_Rcv - Rate_Rcv_p);
									if (Rate < RangeMaxMinRcv[0] && Rate > RangeMaxMinRcv[1]) RgCpnRcv = SlopeOfPayoff_Rcv[LastFixingIdxRcv] * (Rate_Rcv - Rate_Rcv_p) + RangeCpn_Rcv[LastFixingIdxRcv];
								}

								if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 0)
								{
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * DeltatRcv[LastFixingIdxRcv])),RoundingRcv);
								}
								else if (ZeroCouponFlagRcv[LastFixingIdxRcv] == 1)
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3)) ;
									cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], cmpv - 1.0)),RoundingRcv);
								}
								else
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(RcvFixingDate[LastFixingIdxRcv], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv, deltat_fixing_to_pay);
									RcvCpn = NA * rounding_double(min(MaxLossRetRcv[1], max(-MaxLossRetRcv[0], (FixedRate_Rcv[LastFixingIdxRcv] + RgCpnRcv) * deltat_fixing_to_pay)), RoundingRcv);
								}
								RcvLastFixingPayoff_1F[idx1] = RcvCpn;
							}
						}

						if (TextFlag > 0)
						{
							DumppingTextDataArray(CalcFunctionName, SaveFileName, "RcvLastFixingPayoff_1F", NGreed, RcvLastFixingPayoff_1F);
						}
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						RcvLastFixingPayoff_1F[idx1] = 0.0;
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							RcvLastFixingPayoff_2F[idx1][idx2] = 0.0;
						}
					}
				}

				LastFixingIdxPay = -1;
				for (idx1 = 0; idx1 < NCpnDatePay; idx1++)
				{
					if (OptionDate[nextoptidx] <= PayPaymentDate[idx1] && PayFixingDate[idx1] <= OptionDate[nextoptidx])
					{
						LastFixingIdxPay = idx1;
						break;
					}
				}

				idxpay = -1;
				if (LastFixingIdxPay >= 0)
				{
					for (idx1 = 0; idx1 < NTotalSimul; idx1++)
					{
						if (PayFixingDate[LastFixingIdxPay] == TotalArrayDateSimul[idx1])
						{
							idxpay = idx1;
							break;
						}
					}
				}

				DF_to_LastPayDate_Pay = df_T;
				AccCpnDFPay = df_T;
				AccZeroCpnPay = 0.;
				if (LastFixingIdxPay >= 0)
				{
					if (ZeroCouponFlagPay[LastFixingIdxPay] > 0)
					{
						// ZeroCouponCallable Swap 관련 보정
						//DF_to_LastPayDate_Pay = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, DayCountFractionAtoB(PriceDate, PayPaymentDate[NCpnDatePay - 1], 0));
						AccCpnDFPay = Calc_Discount_Factor(ZeroDiscTerm, ZeroDiscRate, NZeroDiscRate, DayCountFractionAtoB(PriceDate, PayPaymentDate[NCpnDatePay - 1], 0));
						if (nextoptidx > 0)
						{
							if (ZeroCouponFlagPay[LastFixingIdxPay] == 1)
							{
								deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx - 1], 3));
								cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay], deltat_fixing_to_pay);
								AccZeroCpnPay = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], cmpv - 1.0)), RoundingPay);
							}
							else if (ZeroCouponFlagPay[LastFixingIdxPay] >= 1)
							{
								deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx - 1], 3));
								AccZeroCpnPay = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], FixedRate_Pay[LastFixingIdxPay] * deltat_fixing_to_pay)), RoundingPay);
							}
						}

					}

					if (HW2FFlag > 0)
					{
						if (PowerSpreadFlagPay == 0)
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								for (idx2 = 0; idx2 < NGreed; idx2++)
								{
									Rate_Pay = Rate_Pay_2F[idxpay][idx1][idx2];
									RgCpnPay = 0.;
									if (Structured_Pay[LastFixingIdxPay] > 0)
									{
										Rate = SlopeOfFixingRate_Pay[LastFixingIdxPay] * Rate_Pay;
										if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[LastFixingIdxPay] * Rate_Pay + RangeCpn_Pay[LastFixingIdxPay];
									}
									
									if (ZeroCouponFlagPay[LastFixingIdxPay] == 0)
									{
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * DeltatPay[LastFixingIdxPay])),RoundingPay);
									}
									else if (ZeroCouponFlagPay[LastFixingIdxPay] == 1)
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], cmpv - 1.0)),RoundingPay);
									}
									else
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
									}
									PayLastFixingPayoff_2F[idx1][idx2] = PayCpn;
								}
							}
						}
						else
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								for (idx2 = 0; idx2 < NGreed; idx2++)
								{
									Rate_Pay = Rate_Pay_2F[idxpay][idx1][idx2];
									Rate_Pay_p = Rate_PayPowerSpread_2F[idxpay][idx1][idx2];
									RgCpnPay = 0.;
									if (Structured_Pay[LastFixingIdxPay] > 0)
									{
										Rate = SlopeOfFixingRate_Pay[LastFixingIdxPay] * (Rate_Pay - Rate_Pay_p);
										if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[LastFixingIdxPay] * (Rate_Pay - Rate_Pay_p) + RangeCpn_Pay[LastFixingIdxPay];
									}
									
									if (ZeroCouponFlagPay[LastFixingIdxPay] == 0)
									{
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * DeltatPay[LastFixingIdxPay])),RoundingPay);
									}
									else if (ZeroCouponFlagPay[LastFixingIdxPay] == 1)
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3)) ;
										cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], cmpv - 1.0)),RoundingPay);
									}
									else
									{
										deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
										cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
										PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
									}
									PayLastFixingPayoff_2F[idx1][idx2] = PayCpn;
								}
							}
						}
					}
					else
					{
						if (PowerSpreadFlagPay == 0)
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								Rate_Pay = Rate_Pay_1F[idxpay][idx1];
								RgCpnPay = 0.;
								if (Structured_Pay[LastFixingIdxPay] > 0)
								{
									Rate = SlopeOfFixingRate_Pay[LastFixingIdxPay] * Rate_Pay;
									if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[LastFixingIdxPay] * Rate_Pay + RangeCpn_Pay[LastFixingIdxPay];
								}
								
								if (ZeroCouponFlagPay[LastFixingIdxPay] == 0)
								{
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * DeltatPay[LastFixingIdxPay])),RoundingPay);
								}
								else if (ZeroCouponFlagPay[LastFixingIdxPay] == 1)
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], cmpv - 1.0)),RoundingPay);
								}
								else
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
								}
								PayLastFixingPayoff_1F[idx1]= PayCpn;
							}
						}
						else
						{
							for (idx1 = 0; idx1 < NGreed; idx1++)
							{
								Rate_Pay = Rate_Pay_1F[idxpay][idx1];
								Rate_Pay_p = Rate_PayPowerSpread_1F[idxpay][idx1];
								RgCpnPay = 0.;
								if (Structured_Pay[LastFixingIdxPay] > 0)
								{
									Rate = SlopeOfFixingRate_Pay[LastFixingIdxPay] * (Rate_Pay - Rate_Pay_p);
									if (Rate < RangeMaxMinPay[0] && Rate > RangeMaxMinPay[1]) RgCpnPay = SlopeOfPayoff_Pay[LastFixingIdxPay] * (Rate_Pay - Rate_Pay_p) + RangeCpn_Pay[LastFixingIdxPay];
								}

								if (ZeroCouponFlagPay[LastFixingIdxPay] == 0)
								{
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * DeltatPay[LastFixingIdxPay])),RoundingPay);
								}
								else if (ZeroCouponFlagPay[LastFixingIdxPay] == 1)
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], cmpv - 1.0)),RoundingPay);
								}
								else
								{
									deltat_fixing_to_pay = (DayCountFractionAtoB(PayFixingDate[LastFixingIdxPay], OptionPayDate[nextoptidx], 3));
									cmpv = pow(1.0 + FixedRate_Pay[LastFixingIdxPay] + RgCpnPay, deltat_fixing_to_pay);
									PayCpn = NA * rounding_double(min(MaxLossRetPay[1], max(-MaxLossRetPay[0], (FixedRate_Pay[LastFixingIdxPay] + RgCpnPay) * deltat_fixing_to_pay)), RoundingPay);
								}
								PayLastFixingPayoff_1F[idx1] = PayCpn;
							}
						}

						if (TextFlag > 0)
						{
							DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayLastFixingPayoff_1F", NGreed, PayLastFixingPayoff_1F);
						}
					}
				}
				else
				{
					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						PayLastFixingPayoff_1F[idx1] = 0.0;
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							PayLastFixingPayoff_2F[idx1][idx2] = 0.0;
						}
					}
				}

				if (HW2FFlag > 0)
				{
					if (Today == OptionPayDate[nextoptidx])
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							for (idx2 = 0; idx2 < NGreed; idx2++)
							{
								if (OptionType == 0)
								{
									if (AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnPay) > FDMValue_2F[idx1][idx2]) OptionExerciseFlag_2F[idx1][idx2] = 1;
									else OptionExerciseFlag_2F[idx1][idx2] = 0;
								}
								else
								{
									if (AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnPay) < FDMValue_2F[idx1][idx2]) OptionExerciseFlag_2F[idx1][idx2] = 1;
									else OptionExerciseFlag_2F[idx1][idx2] = 0;
								}
							}
						}
					}

					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						for (idx2 = 0; idx2 < NGreed; idx2++)
						{
							if (OptionExerciseFlag_2F[idx1][idx2] == 1) FDMValue_2F[idx1][idx2] = AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_2F[idx1][idx2] - AccZeroCpnPay);
						}
					}

					//for (idx1 = 0; idx1 < NGreed; idx1++)
					//{
					//	for (idx2 = 0; idx2 < NGreed; idx2++)
					//	{
					//		if (OptionType == 0) FDMValue_2F[idx1][idx2] = max((DF_to_LastPayDate_Rcv / df_t * RcvLastFixingPayoff_2F[idx1][idx2] - DF_to_LastPayDate_Pay / df_t * PayLastFixingPayoff_2F[idx1][idx2]), FDMValue_2F[idx1][idx2]);
					//		else FDMValue_2F[idx1][idx2] = min((DF_to_LastPayDate_Rcv / df_t * RcvLastFixingPayoff_2F[idx1][idx2] - DF_to_LastPayDate_Pay / df_t * PayLastFixingPayoff_2F[idx1][idx2]), FDMValue_2F[idx1][idx2]);
					//	}
					//}
				}
				else
				{
					if (Today == OptionPayDate[nextoptidx])
					{
						for (idx1 = 0; idx1 < NGreed; idx1++)
						{
							if (OptionType == 0)
							{
								if (AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_1F[idx1] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_1F[idx1] - AccZeroCpnPay) > FDMValue_1F[idx1]) OptionExerciseFlag_1F[idx1] = 1;
								else OptionExerciseFlag_1F[idx1] = 0;
							}
							else
							{
								if (AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_1F[idx1] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_1F[idx1] - AccZeroCpnPay) < FDMValue_1F[idx1]) OptionExerciseFlag_1F[idx1] = 1;
								else OptionExerciseFlag_1F[idx1] = 0;
							}
						}
					}

					for (idx1 = 0; idx1 < NGreed; idx1++)
					{
						if (OptionExerciseFlag_1F[idx1] == 1) FDMValue_1F[idx1] = AccZeroCpnRcv * AccCpnDFRcv / df_t + DF_to_LastPayDate_Rcv / df_t * (RcvLastFixingPayoff_1F[idx1] - AccZeroCpnRcv) - AccZeroCpnPay * AccCpnDFPay / df_t - DF_to_LastPayDate_Pay / df_t * (PayLastFixingPayoff_1F[idx1] - AccZeroCpnPay);
					}

					//for (idx1 = 0; idx1 < NGreed; idx1++)
					//{
					//	if (OptionType == 0) FDMValue_1F[idx1] = max((DF_to_LastPayDate_Rcv / df_t * RcvLastFixingPayoff_1F[idx1] - DF_to_LastPayDate_Pay / df_t * PayLastFixingPayoff_1F[idx1]), FDMValue_1F[idx1]);
					//	else FDMValue_1F[idx1] = min((DF_to_LastPayDate_Rcv / df_t * RcvLastFixingPayoff_1F[idx1] - DF_to_LastPayDate_Pay / df_t * PayLastFixingPayoff_1F[idx1]), FDMValue_1F[idx1]);
					//}
				}

				if (Today == min(OptionDate[nextoptidx], OptionPayDate[nextoptidx]))
				{
					nextoptidx = max(0, nextoptidx - 1);
				}
			}

		}

		n += 1;
	}

	if (HW2FFlag == 0) ResultValue = Interpolate_Linear(xt, FDMValue_1F, NGreed, 0.0);
	else ResultValue = Calc_Volatility(NGreed, NGreed, xt, yt, FDMValue_2F, 0.0, 0.0);
	ResultFixingRateCpn[0] = ResultValue;
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

	free(SlopeOfFixingRate_Rcv);
	free(SlopeOfPayoff_Rcv);
	free(FixedRate_Rcv);
	free(Structured_Rcv);
	free(RangeCpn_Rcv);
	free(DeltatRcv);
	free(ZeroCouponFlagRcv);
	free(SlopeOfFixingRate_Pay);
	free(SlopeOfPayoff_Pay);
	free(FixedRate_Pay);
	free(Structured_Pay);
	free(RangeCpn_Pay);
	free(DeltatPay);
	free(ZeroCouponFlagPay);

	free(Alpha_1Curve);
	free(Beta_1Curve);
	free(Gamma_1Curve);
	free(Alpha_2Curve);
	free(Beta_2Curve);
	free(Gamma_2Curve);
	free(FDMValue_1F);
	for (i = 0; i < NGreed; i++) free(FDMValue_2F[i]);
	free(FDMValue_2F);
	for (i = 0; i < NGreed; i++) free(RHSValue_2F[i]);
	free(RHSValue_2F);

	free(TempAlphaArray);
	free(TempBetaArray);
	free(TempGammaArray);
	for (i = 0; i < NGreed; i++)
	{
		free(TempCpnArrayRcv_2F[i]);
		free(TempCpnArrayPay_2F[i]);
	}
	free(TempCpnArrayRcv_2F);
	free(TempCpnArrayPay_2F);
	free(TempCpnArrayRcv_1F);
	free(TempCpnArrayPay_1F);

	for (i = 0; i < NGreed; i++) free(OptionExerciseFlag_2F[i]);
	free(OptionExerciseFlag_2F);
	free(OptionExerciseFlag_1F);

	free(ForPrintVariable);
	free(RcvLastFixingPayoff_1F);
	free(PayLastFixingPayoff_1F);
	for (i = 0; i < NGreed; i++) free(RcvLastFixingPayoff_2F[i]);
	for (i = 0; i < NGreed; i++) free(PayLastFixingPayoff_2F[i]);
	free(RcvLastFixingPayoff_2F);
	free(PayLastFixingPayoff_2F);

	//_CrtDumpMemoryLeaks();
	return 1;
}

/*int main()
{
	long i, j, n;
	long PriceDate = 20240727;
	long EffectiveDate = 20240727;
	long Maturity = 20340731;
	long NAFlag = 0;
	double NA = 10000.0;
	long NAdditionalHolidays[2] = { 1, 2 };
	long AddtionalHolidays[3] = { 20240101, 20240101, 20241225 };
	long NationFlag[2] = { 0, 0 };
	long NumCpnAnn[2] = { 4, 4 };
	long NumCpnAnnPhase2[2] = { 4,4 };
	double MaxLossRetRcvPay[4] = { 0.0, 0.99, 0.00, 0.99 };
	double MultipleRatefixPayoffRcvPay[4] = { 1.0, 1.0, 0.0, 0.0 };
	long DayCountRcvPay[2] = { 0, 0 };
	long PowerSpreadFlagRcvPay[2] = { 0, 0 };
	double RangeMaxMinRcvPay[4] = { 100.0, -1.0, 100.0, -1.0 };
	double InfoRefRateRcvPay[8] = { 4.0, 0.25, 10.0, 5.0, 4.0, 0.25, 30.0, 10.0 };

	double RcvLegFixedRate = 0.00;
	double RcvLegRangeCoupon = 0.00;
	long RcvLegStructuredFlag = 1;
	double PayLegFixedRate = 0.04;
	double PayLegRangeCoupon = 0.0;
	long PayLegStructuredFlag = 0;

	long Phase2UseFlag = 1;
	long Phase2Date = 20290727;
	double Phase2RcvLegFixedRate = 0.00;
	double Phase2RcvLegRangeCoupon = 0.00;
	long Phase2RcvLegStructuredFlag = 1;
	double Phase2PayLegFixedRate = 0.04;
	double Phase2PayLegRangeCoupon = 0.0;
	long Phase2PayLegStructuredFlag = 0;

	long NOption = 0;
	long OptionDate[2] = { 20250727, 20260727 };
	long OptionPayDate[2] = { 20250729, 20260729 };
	long OptionType = 1;

	long NRcvRateHistory = 2;
	long RcvRateHistoryDate[2] = { 20220819, 20220820 };
	double RcvRateHistory[2] = { 0.03914, 0.0392 };

	long NPayRateHistory = 1;
	long PayRateHistoryDate[1] = { 20220819 };
	double PayRateHistory[1] = { 0.0304 };

	long NZeroEstRate = 4;
	double ZeroEstTerm[4] = { 0.5, 1.0, 1.5, 2.0 };
	double ZeroEstRate[4] = { 0.0379, 0.0387, 0.0392, 0.0412 };
	long NZeroDiscRate = 4;
	double ZeroDiscTerm[4] = { 0.5, 1.0, 1.5, 2.0 };
	double ZeroDiscRate[4] = { 0.0379, 0.0387, 0.0392, 0.0412 };

	long HW2FFlag = 0;
	long NHWVol = 5;
	double HWVolTerm[5] = { 0.5, 1.0, 1.5, 2.0, 3.0 };
	double HWVol[10] = { 0.0096, 0.0111, 0.0112, 0.0112,0.0114,0.0052,0.0046,0.0066,0.0062,0.0061 };
	double kappa[2] = { 0.07, 0.011 };
	double FactorCorrelation = 0.132;
	long NCpn[2] = { 0.0 };

	long tempn1, tempn2;
	tempn1 = Number_of_Coupons(1, CDateToExcelDate(EffectiveDate), CDateToExcelDate(Maturity), NumCpnAnn[0], 0, 0, 0, 0);
	NCpn[0] = NCpnDate_Holiday_2Phase(EffectiveDate, Maturity, NumCpnAnn[0], 1, NumCpnAnnPhase2[0], Phase2Date);

	tempn2 = Number_of_Coupons(1, CDateToExcelDate(EffectiveDate), CDateToExcelDate(Maturity), NumCpnAnn[1], 0, 0, 0, 0);
	NCpn[1] = NCpnDate_Holiday_2Phase(EffectiveDate, Maturity, NumCpnAnn[1], 1, NumCpnAnnPhase2[1], Phase2Date);

	long* ResultCpnDateRcv = (long*)malloc(sizeof(long) * NCpn[0] * 5);
	long* ResultCpnDatePay = (long*)malloc(sizeof(long) * NCpn[1] * 5);
	double* ResultFixingRateCpn = (double*)malloc(sizeof(double) * (NCpn[0] * 2 + NCpn[1] * 2 + 1));

	IRStructuredSwapFDM(PriceDate, EffectiveDate, Maturity, NAFlag, NA,
		NAdditionalHolidays, NAdditionalHolidays, NationFlag, NumCpnAnn, MaxLossRetRcvPay,
		MultipleRatefixPayoffRcvPay, DayCountRcvPay, PowerSpreadFlagRcvPay, RangeMaxMinRcvPay, InfoRefRateRcvPay,
		RcvLegFixedRate, RcvLegRangeCoupon, RcvLegStructuredFlag, PayLegFixedRate, PayLegRangeCoupon,
		PayLegStructuredFlag, Phase2UseFlag, Phase2Date, Phase2RcvLegFixedRate, Phase2RcvLegRangeCoupon,
		Phase2RcvLegStructuredFlag, Phase2PayLegFixedRate, Phase2PayLegRangeCoupon, Phase2PayLegStructuredFlag, NumCpnAnnPhase2,
		NOption, OptionDate, OptionPayDate, OptionType, NRcvRateHistory,
		RcvRateHistoryDate, RcvRateHistory, NPayRateHistory, PayRateHistoryDate, PayRateHistory,
		NZeroEstRate, ZeroEstTerm, ZeroEstRate, NZeroDiscRate, ZeroDiscTerm, ZeroDiscRate,
		HW2FFlag, NHWVol, HWVolTerm, HWVol, kappa,
		FactorCorrelation, ResultCpnDateRcv, ResultCpnDatePay, ResultFixingRateCpn
	);
	free(ResultCpnDateRcv);
	free(ResultCpnDatePay);
	free(ResultFixingRateCpn);
	_CrtDumpMemoryLeaks();
}*/