#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "HW_Calibration.h"

#ifndef UTILITY
#include "Util.h"
#endif

#ifndef DateFunction
#include "CalcDate.h"
#endif 
#include <crtdbg.h>

typedef struct struct_cpn_schd_info {
	long NCpn;
	long* ResetDate;
	long* CpnDate;
	long* CpnPayDate;
	double* FixedRate;
	double* ParticipateRate;
	double* FloorBoundary;
	double* CapBoundary;
	double* RangeCpnRate;
	double PreDeterminedRate;
} CPN_SCHD;

typedef struct option_info {
	long CancelOptionFlag;	// Option 사용여부 0 미사용 1 사용
	long NCancel;			// Option개수
	long CancelType;		// 0 Domestic Leg Call 보유 1 Domestic Leg Call 보유
	long* CancelDate;		// OptionDate
} OPT_SCHD;

typedef struct hw1_info {
	long NTermHW;
	double* HWTerm;
	double* HWVol;
	double kappa;
	double longterm_shortrate;
	long longterm_shortrateflag;
} HW1F_INFO;

typedef struct ratetype {
	long N;
	double* TermArray;
	double* RateArray;
} RATE_INFO;

typedef struct refrate_type {
	long NCPN_Ann;
	double Maturity;
	long RefRateType;
} REF_RATE;


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
	double* dt
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
			B += term * PtT;
		}

		ResultRate = (1. - PtT) / B;
	}
	else
	{
		if (t >= 0.0) PtT = PV_t_T[0] * exp(-ShortRate * B_t_T[0] + QVTerm[0]);
		else PtT = Calc_Discount_Factor(RateTerm, Rate, NRateTerm, T);

		if (dt[0] < 1.0) ResultRate = (1.0 - PtT) / (dt[0] * PtT);
		else ResultRate = -1.0 / dt[0] * log(PtT);
	}

	return ResultRate;
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
long isinfindindexlong(long n, long* myarray, long target)
{
	long i, v = -1;
	for (i = 0; i < n; i++)
	{
		if (myarray[i] == target)
		{
			v = i;
			break;
		}
	}
	return v;
}

void Copy2dMatrix(double** CopyResult, double** MyMatrix, long p, long q)
{
	long i, j;
	for (i = 0; i < p; i++) for (j = 0; j < q; j++) CopyResult[i][j] = MyMatrix[i][j];
}

double _stdcall B_s_to_t(
	double kappa,
	double s,
	double t
)
{
	return (1.0 - exp(-kappa * (t - s))) / kappa;
}

double _stdcall V_t_T(
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
		vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t + T) / 2.);
		double term1 = (1.0 - exp(-kappa * t)) / kappa;
		double term2 = (exp(-kappa * (T - t)) - exp(-kappa * T)) / kappa;
		double term3 = (1.0 - exp(-2.0 * kappa * t)) / (2.0 * kappa);
		double term4 = (exp(-2.0 * kappa * (T - t)) - exp(-2.0 * kappa * T)) / (2.0 * kappa);

		RHS = 0.5 * (vol * vol) / (kappa * kappa) * (-2.0 * (term1 - term2) + (term3 - term4));
	}
	else
	{
		RHS = 0.0;
		long NInteg = 10.0;
		double u = 0.;
		double du = t / ((double)NInteg);
		double Bst, BsT;
		for (i = 0; i < NInteg; i++)
		{
			vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
			Bst = B_s_to_t(kappa, u, t);
			BsT = B_s_to_t(kappa, u, T);
			RHS += 0.5 * vol * vol * (Bst * Bst - BsT * BsT) * du;
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

	if (NHWVol == 1 || kappa > 0.1)
	{
		vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, (t + T) / 2.);
		vol2 = Interpolate_Linear(HWVolTerm2, HWVol2, NHWVol, (t + T) / 2.);
		double term1 = (1.0 - exp(-kappa * t)) / kappa;
		double term2 = (exp(-kappa * (T - t)) - exp(-kappa * T)) / kappa;
		double term1_2F = (1.0 - exp(-kappa2 * t)) / kappa2;
		double term2_2F = (exp(-kappa2 * (T - t)) - exp(-kappa2 * T)) / kappa2;

		double term3 = (1.0 - exp(-(kappa + kappa2) * t)) / (2.0 * (kappa + kappa2));
		double term4 = (exp(-(kappa + kappa2) * (T - t)) - exp(-(kappa + kappa2) * T)) / (kappa + kappa2);

		RHS = 2.0 * rho * 0.5 * (vol * vol2) / (kappa * kappa2) * (-(term1 - term2 + term1_2F - term2_2F) + (term3 - term4));
	}
	else
	{
		RHS = 0.0;
		long NInteg = 10.0;
		double u = 0.;
		double du = t / ((double)NInteg);
		double Bst, BsT, Bst2, BsT2;
		for (i = 0; i < NInteg; i++)
		{
			vol = Interpolate_Linear(HWVolTerm, HWVol, NHWVol, u);
			vol2 = Interpolate_Linear(HWVolTerm2, HWVol2, NHWVol, u);
			Bst = B_s_to_t(kappa, u, t);
			BsT = B_s_to_t(kappa, u, T);
			Bst2 = B_s_to_t(kappa2, u, t);
			BsT2 = B_s_to_t(kappa2, u, T);
			RHS += 2.0 * rho * 0.5 * vol * vol2 * (Bst * Bst2 - BsT * BsT2) * du;
			u = u + du;
		}
	}

	return RHS;
}

double _stdcall HW_Rate_LongTermShortRate(
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
	double* dt
)
{
	long i;
	double PtT;
	double term = 1.0 / ((double)NCPN_Ann);
	double ResultRate;
	double A, B;
	if (ReferenceType == 0) NCfSwap = 1;
	if (ReferenceType == 1)
	{
		if (NCPN_Ann > 0)
		{
			B = 0.0;
			for (i = 0; i < NCfSwap; i++)
			{
				term = dt[i];
				PtT = PV_t_T[i] * exp(-ShortRate * B_t_T[i] + QVTerm[i]);
				B += term * PtT;
			}

			ResultRate = (1. - PtT) / B;
		}
		else
		{
			if (t >= 0.0) PtT = PV_t_T[0] * exp(-ShortRate * B_t_T[0] + QVTerm[0]);
			else PtT = Calc_Discount_Factor(RateTerm, Rate, NRateTerm, T);

			if (dt[0] < 1.0) ResultRate = (1.0 - PtT) / (dt[0] * PtT);
			else ResultRate = -1.0 / dt[0] * log(PtT);
		}

	}
	else
	{
		term = 1.0 / 365.0;
		PtT = PV_t_T[0] * exp(-ShortRate * B_t_T[0] + QVTerm[0]);
		ResultRate = (1.0 - PtT) / (term * PtT);
	}

	return ResultRate;
}

double _stdcall integ_thetaterm(
	double kappa,
	double theta,
	double t1,
	double t2
)
{
	long i;
	long NInteg = 4;
	double ds;
	double s;
	double sumvalue = 0.0;
	ds = (t2 - t1) / (double)NInteg;
	for (i = 0; i < NInteg; i++)
	{
		s = t1 + (double)i * ds;
		sumvalue += theta * exp(kappa * (s - t2)) * ds;
	}
	return sumvalue;
}

double _stdcall MeanRevertingDeterministic(
	long NZero,
	double* ZeroTerm,
	double* ZeroRate,
	double sigma,
	double kappa,
	double t
)
{
	long i;
	double dt = 1.0 / 365.0;
	double P0, P1;
	double ft;
	P0 = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, t);
	P1 = Calc_Discount_Factor(ZeroTerm, ZeroRate, NZero, t + dt);
	ft = -(P1 - P0) / dt;
	return ft + sigma * sigma / (2.0 * kappa * kappa) * (1.0 - exp(-kappa * t)) * (1.0 - exp(-kappa * t));
}

double PayoffLeg(
	long NAFlag,
	double Notional,
	double ParticipateRate,
	double Rate,
	double FixedCPNRate,
	double DeltaT,
	double RangeDn,
	double RangeUp,
	double RangeCpn
)
{
	double cpnrate = 0.0;

	if (ParticipateRate > 0)
	{
		cpnrate = (double)NAFlag * Notional + Notional * (ParticipateRate * Rate + FixedCPNRate) * DeltaT;
		if (Rate <= RangeUp && Rate >= RangeDn) cpnrate += Notional * ParticipateRate * RangeCpn * DeltaT;
	}
	else if (ParticipateRate < 0)
	{
		cpnrate = (double)NAFlag * -Notional + Notional * (ParticipateRate * Rate - FixedCPNRate) * DeltaT;
		if (Rate <= RangeUp && Rate >= RangeDn) cpnrate += Notional * ParticipateRate * RangeCpn * DeltaT;
	}
	else
	{
		cpnrate = (double)NAFlag * Notional + Notional * FixedCPNRate * DeltaT;
		if (Rate <= RangeUp && Rate >= RangeDn) cpnrate += Notional * ParticipateRate * RangeCpn * DeltaT;
	}
	return cpnrate;
}

void Test(
	long NodeNum,
	long NotionalFlag,
	REF_RATE* RefType_Domestic,
	REF_RATE* RefType_Foreign,
	RATE_INFO* ZeroDomestic,
	RATE_INFO* ZeroForeign,
	HW1F_INFO* hw_d,
	HW1F_INFO* hw_f,
	double rho12,
	double rho23,
	RATE_INFO* FXVol_INFO,
	long DailyFDMFlag,
	long LastCpnDatetoToday,
	CPN_SCHD* Domestic_Cpn_Schd,
	CPN_SCHD* Foreign_Cpn_Schd,
	long DualRangeFlag,
	OPT_SCHD* opt_schd,
	double* resultarray
)
{
	long i, j, k, kk, n, idx_px = 0, idx_py = 0;

	double NotionalAmt = 10000.0;
	double t1, t2;
	double Instant_FwdDF, df_t, df_T;
	long NDays;
	if (opt_schd->CancelOptionFlag == 0) opt_schd->NCancel = 0;

	////////////////////////////////////////////////////////////////
	// if DailyFDMFlag != 0
	// FDM Days = {ResetDate(0 제외) + CouponDate + OptionDate}
	///////////////////////////////////////////////////////////////
	long NReset = Domestic_Cpn_Schd->NCpn;
	long N0 = 0;
	long* ResetDateExcept0;
	for (i = 0; i < Domestic_Cpn_Schd->NCpn; i++)
	{
		if (Domestic_Cpn_Schd->ResetDate[i] == 0)
		{
			NReset -= 1;
			N0 += 1;
		}
	}

	ResetDateExcept0 = Domestic_Cpn_Schd->ResetDate + N0;
	long NCombinedDate = Domestic_Cpn_Schd->NCpn + NReset + opt_schd->NCancel;
	long* CombinedDate = (long*)malloc(sizeof(long) * NCombinedDate);
	for (i = 0; i < NReset; i++) CombinedDate[i] = ResetDateExcept0[i];
	for (i = 0; i < Domestic_Cpn_Schd->NCpn; i++) CombinedDate[i + NReset] = Domestic_Cpn_Schd->CpnDate[i];
	for (i = 0; i < opt_schd->NCancel; i++) CombinedDate[i + NReset + Domestic_Cpn_Schd->NCpn] = opt_schd->CancelDate[i];
	bubble_sort_long(CombinedDate, NCombinedDate, 1);

	long NDate;
	long* Date = Make_Unique_Array(NCombinedDate, CombinedDate, NDate);
	double t, term, dt_on = 1.0 / 365.0;
	// 임시변수
	//
	double shortratestart = -0.16;
	double shortrateend = 0.24;
	double* dt_Array;
	double* T_Array;
	long* DaysForFDM;
	if (DailyFDMFlag == 1)
	{
		NDays = Domestic_Cpn_Schd->CpnDate[Domestic_Cpn_Schd->NCpn - 1];
		dt_Array = (double*)malloc(sizeof(double) * NDays);
		T_Array = (double*)malloc(sizeof(double) * NDays);
		DaysForFDM = (long*)malloc(sizeof(double) * NDays);
		for (i = 0; i < NDays; i++)
		{
			dt_Array[i] = dt_on;
			T_Array[i] = dt_on * (double)(i + 1);
			DaysForFDM[i] = (long)(T_Array[i] * 365.0 + 0.00001);
		}
	}
	else
	{
		NDays = NDate;
		dt_Array = (double*)malloc(sizeof(double) * NDays);
		T_Array = (double*)malloc(sizeof(double) * NDays);
		DaysForFDM = (long*)malloc(sizeof(double) * NDays);
		for (i = 0; i < NDays; i++)
		{
			if (i == 0) dt_Array[0] = ((double)(Date[0])) / 365.0;
			else dt_Array[i] = ((double)(Date[i] - Date[i - 1])) / 365.0;
			T_Array[i] = ((double)Date[i]) / 365.0;;
			DaysForFDM[i] = Date[i];
		}
	}

	long ndates_domestic;
	double** domestic_DF_t_T;
	double** domestic_B_t_T;
	double** domestic_QVTerm;
	double** domestic_dt;

	long ndates_foreign;
	double** foreign_DF_t_T;
	double** foreign_B_t_T;
	double** foreign_QVTerm;
	double** foreign_dt;

	double* DF_t_T_overnight;
	double* B_t_T_overnight;
	double* QVTerm_overnight;

	if (RefType_Domestic->NCPN_Ann >= 1 && RefType_Domestic->Maturity >= 1.0)
	{
		ndates_domestic = Number_Of_Payment(0.0, RefType_Domestic->Maturity, 12.0 / (double)RefType_Domestic->NCPN_Ann);
	}
	else if (RefType_Domestic->NCPN_Ann == 1 && RefType_Domestic->Maturity < 1.0)
	{
		ndates_domestic = 1;
		RefType_Domestic->NCPN_Ann = (long)(1.0 / RefType_Domestic->Maturity + 0.0001);
	}
	else if (RefType_Domestic->RefRateType == 2) ndates_domestic = 1;
	else ndates_domestic = 1;

	//////////////////////////////////////////
	// Hull White 관련 Parameter 사전 세팅
	//////////////////////////////////////////

	domestic_DF_t_T = (double**)malloc(sizeof(double*) * NDays);
	domestic_B_t_T = (double**)malloc(sizeof(double*) * NDays);
	domestic_QVTerm = (double**)malloc(sizeof(double*) * NDays);
	domestic_dt = (double**)malloc(sizeof(double*) * NDays);
	DF_t_T_overnight = (double*)malloc(sizeof(double) * NDays);
	B_t_T_overnight = (double*)malloc(sizeof(double) * NDays);
	QVTerm_overnight = (double*)malloc(sizeof(double) * NDays);
	double DF_0_t, T1, DF_0_T;
	if (RefType_Domestic->RefRateType == 1)
	{
		for (j = 0; j < NDays; j++)
		{
			t = ((double)T_Array[j]);
			if (RefType_Domestic->NCPN_Ann > 0) term = 1.0 / ((double)RefType_Domestic->NCPN_Ann);
			else term = RefType_Domestic->Maturity;

			domestic_DF_t_T[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_B_t_T[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_QVTerm[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_dt[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			DF_0_t = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			for (k = 0; k < ndates_domestic; k++)
			{
				T1 = t + term * ((double)k + 1.0);
				domestic_dt[j][k] = term;
				DF_0_T = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, T1);
				domestic_DF_t_T[j][k] = DF_0_T / DF_0_t;
				domestic_QVTerm[j][k] = HullWhiteQVTerm(t, T1, hw_d->kappa, hw_d->NTermHW, hw_d->HWTerm, hw_d->HWVol);
				domestic_B_t_T[j][k] = B_s_to_t(hw_d->kappa, t, T1);
			}
			DF_t_T_overnight[j] = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t + dt_on) / DF_0_t;
			QVTerm_overnight[j] = HullWhiteQVTerm(t, t + dt_on, hw_d->kappa, hw_d->NTermHW, hw_d->HWTerm, hw_d->HWVol);
			B_t_T_overnight[j] = B_s_to_t(hw_d->kappa, t, t + dt_on);
		}
	}
	else if (RefType_Domestic->RefRateType == 2)
	{
		for (j = 0; j < NDays; j++)
		{
			t = ((double)T_Array[j]);
			term = dt_on;

			domestic_DF_t_T[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_B_t_T[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_QVTerm[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			domestic_dt[j] = (double*)malloc(sizeof(double) * ndates_domestic);
			DF_0_t = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			for (k = 0; k < 1; k++)
			{
				T1 = t + term * ((double)k + 1.0);
				domestic_dt[j][k] = term;
				DF_0_T = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, T1);
				domestic_DF_t_T[j][k] = DF_0_T / DF_0_t;
				domestic_QVTerm[j][k] = HullWhiteQVTerm(t, T1, hw_d->kappa, hw_d->NTermHW, hw_d->HWTerm, hw_d->HWVol);
				domestic_B_t_T[j][k] = B_s_to_t(hw_d->kappa, t, T1);
			}
			DF_t_T_overnight[j] = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t + term) / DF_0_t;
			QVTerm_overnight[j] = HullWhiteQVTerm(t, t + term, hw_d->kappa, hw_d->NTermHW, hw_d->HWTerm, hw_d->HWVol);
			B_t_T_overnight[j] = B_s_to_t(hw_d->kappa, t, t + term);
		}
	}

	//
	if (RefType_Foreign->NCPN_Ann >= 1 && RefType_Foreign->Maturity >= 1.0)
	{
		ndates_foreign = Number_Of_Payment(0.0, RefType_Foreign->Maturity, 12.0 / (double)RefType_Foreign->NCPN_Ann);
	}
	else if (RefType_Foreign->NCPN_Ann == 1 && RefType_Foreign->Maturity < 1.0)
	{
		ndates_foreign = 1;
		RefType_Foreign->NCPN_Ann = (long)(1.0 / RefType_Foreign->Maturity + 0.0001);
	}
	else if (RefType_Foreign->RefRateType == 2) ndates_foreign = 1;
	else ndates_foreign = 1;

	foreign_DF_t_T = (double**)malloc(sizeof(double*) * NDays);
	foreign_B_t_T = (double**)malloc(sizeof(double*) * NDays);
	foreign_QVTerm = (double**)malloc(sizeof(double*) * NDays);
	foreign_dt = (double**)malloc(sizeof(double*) * NDays);

	if (RefType_Foreign->RefRateType == 1)
	{
		for (j = 0; j < NDays; j++)
		{
			t = ((double)T_Array[j]);
			if (RefType_Foreign->NCPN_Ann > 0) term = 1.0 / ((double)RefType_Foreign->NCPN_Ann);
			else term = RefType_Foreign->Maturity;

			foreign_DF_t_T[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_B_t_T[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_QVTerm[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_dt[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			DF_0_t = Calc_Discount_Factor(ZeroForeign->TermArray, ZeroForeign->RateArray, ZeroForeign->N, t);
			for (k = 0; k < ndates_foreign; k++)
			{
				T1 = t + term * ((double)k + 1.0);
				foreign_dt[j][k] = term;
				DF_0_T = Calc_Discount_Factor(ZeroForeign->TermArray, ZeroForeign->RateArray, ZeroForeign->N, T1);
				foreign_DF_t_T[j][k] = DF_0_T / DF_0_t;
				foreign_QVTerm[j][k] = HullWhiteQVTerm(t, T1, hw_f->kappa, hw_f->NTermHW, hw_f->HWTerm, hw_f->HWVol);
				foreign_B_t_T[j][k] = B_s_to_t(hw_f->kappa, t, T1);
			}
		}
	}
	else if (RefType_Foreign->RefRateType == 2)
	{
		for (j = 0; j < NDays; j++)
		{
			t = ((double)T_Array[j]);
			term = dt_on;

			foreign_DF_t_T[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_B_t_T[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_QVTerm[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			foreign_dt[j] = (double*)malloc(sizeof(double) * ndates_foreign);
			DF_0_t = Calc_Discount_Factor(ZeroForeign->TermArray, ZeroForeign->RateArray, ZeroForeign->N, t);
			for (k = 0; k < 1; k++)
			{
				T1 = t + term * ((double)k + 1.0);
				foreign_dt[j][k] = term;
				DF_0_T = Calc_Discount_Factor(ZeroForeign->TermArray, ZeroForeign->RateArray, ZeroForeign->N, T1);
				foreign_DF_t_T[j][k] = DF_0_T / DF_0_t;
				foreign_QVTerm[j][k] = HullWhiteQVTerm(t, T1, hw_f->kappa, hw_f->NTermHW, hw_f->HWTerm, hw_f->HWVol);
				foreign_B_t_T[j][k] = B_s_to_t(hw_f->kappa, t, T1);
			}
		}
	}

	// LastPayoff
	double* x_range = (double*)malloc(sizeof(double) * NodeNum);
	double* y_range = (double*)malloc(sizeof(double) * NodeNum);
	double dx = (shortrateend - shortratestart) / ((double)NodeNum);
	double dy = dx;
	for (i = 0; i < NodeNum; i++)
	{
		x_range[i] = shortratestart + (double)i * dx;
		y_range[i] = shortratestart + (double)i * dy;
	}

	for (i = 0; i < NodeNum; i++)
	{
		if (x_range[i] < 0.0001 && x_range[i] > -0.0001)
		{
			idx_px = i;
			break;
		}
	}
	for (i = 0; i < NodeNum; i++)
	{
		if (y_range[i] < 0.0001 && y_range[i] > -0.0001)
		{
			idx_py = i;
			break;
		}
	}

	double* rx_range = (double*)malloc(sizeof(double) * NodeNum);
	double* ry_range = (double*)malloc(sizeof(double) * NodeNum);

	double DF0, DF1, T2;
	double theta_domestic = 0.0;
	if (hw_d->longterm_shortrateflag == 1) theta_domestic = hw_d->kappa * hw_d->longterm_shortrate;
	double theta_foreign = 0.0;
	if (hw_f->longterm_shortrateflag == 1) theta_foreign = hw_f->kappa * hw_f->longterm_shortrate;

	double last_rx, last_ry, xt, T, Rate, OptValue, Price, Price_NotOpt;
	long idxreset = Domestic_Cpn_Schd->NCpn - 1, idxcalc = Domestic_Cpn_Schd->NCpn - 1;
	idxreset = isinfindindexlong(NDays, DaysForFDM, Domestic_Cpn_Schd->ResetDate[Domestic_Cpn_Schd->NCpn - 1]);
	idxcalc = isinfindindexlong(NDays, DaysForFDM, Domestic_Cpn_Schd->CpnDate[Domestic_Cpn_Schd->NCpn - 1]);
	for (i = 0; i < NodeNum; i++)
	{
		xt = x_range[i];
		t = T_Array[idxreset];
		T = t + RefType_Domestic->Maturity;
		if (hw_d->longterm_shortrateflag == 0) Rate = HW_Rate(RefType_Domestic->RefRateType, t, T, ZeroDomestic->N, ZeroDomestic->TermArray,
			ZeroDomestic->RateArray, xt, ndates_domestic, RefType_Domestic->NCPN_Ann, domestic_DF_t_T[idxreset],
			domestic_QVTerm[idxreset], domestic_B_t_T[idxreset], domestic_dt[idxreset]);
		else Rate = HW_Rate_LongTermShortRate(RefType_Domestic->RefRateType, t, T, ZeroDomestic->N, ZeroDomestic->TermArray,
			ZeroDomestic->RateArray, xt, ndates_domestic, RefType_Domestic->NCPN_Ann, domestic_DF_t_T[idxreset],
			domestic_QVTerm[idxreset], domestic_B_t_T[idxreset], domestic_dt[idxreset]);
		rx_range[i] = Rate;
	}

	for (i = 0; i < NodeNum; i++)
	{
		xt = y_range[i];
		t = T_Array[NDays - 1];
		T = t + RefType_Foreign->Maturity;
		if (hw_f->longterm_shortrateflag == 0) Rate = HW_Rate(RefType_Foreign->RefRateType, t, T, ZeroForeign->N, ZeroForeign->TermArray,
			ZeroForeign->RateArray, xt, ndates_foreign, RefType_Foreign->NCPN_Ann, foreign_DF_t_T[idxreset],
			foreign_QVTerm[idxreset], foreign_B_t_T[idxreset], foreign_dt[idxreset]);
		else Rate = HW_Rate_LongTermShortRate(RefType_Foreign->RefRateType, t, T, ZeroForeign->N, ZeroForeign->TermArray,
			ZeroForeign->RateArray, xt, ndates_foreign, RefType_Foreign->NCPN_Ann, foreign_DF_t_T[idxreset],
			foreign_QVTerm[idxreset], foreign_B_t_T[idxreset], foreign_dt[idxreset]);
		ry_range[i] = Rate;
	}

	// 쿠폰날짜마다 오버나이트금리 계산하여 PayDate부터 CpnDate까지 포워드 할인하기위해 사용
	double* r_on_range = (double*)malloc(sizeof(double) * NodeNum);
	for (i = 0; i < NodeNum; i++)
	{
		xt = x_range[i];
		t = T_Array[idxcalc];
		T = t + dt_on;
		if (hw_d->longterm_shortrateflag == 0)
		{
			//if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
			//else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
		}
		else
		{
			//if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
			//else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
		}
	}

	double** FinalDomestic = (double**)malloc(sizeof(double*) * NodeNum);
	double** FinalForeign = (double**)malloc(sizeof(double*) * NodeNum);
	double** FinalIncludingOpt = (double**)malloc(sizeof(double*) * NodeNum);
	double** RHS_Domestic = (double**)malloc(sizeof(double*) * NodeNum);
	double** RHS_Foreign = (double**)malloc(sizeof(double*) * NodeNum);
	double** RHS_IncludingOpt = (double**)malloc(sizeof(double*) * NodeNum);
	double** PriceMatrix = (double**)malloc(sizeof(double*) * NodeNum);
	for (i = 0; i < NodeNum; i++)
	{
		FinalDomestic[i] = (double*)malloc(sizeof(double) * NodeNum);
		FinalForeign[i] = (double*)malloc(sizeof(double) * NodeNum);
		FinalIncludingOpt[i] = (double*)malloc(sizeof(double) * NodeNum);
		RHS_Domestic[i] = (double*)malloc(sizeof(double) * NodeNum);
		RHS_Foreign[i] = (double*)malloc(sizeof(double) * NodeNum);
		RHS_IncludingOpt[i] = (double*)malloc(sizeof(double) * NodeNum);
		PriceMatrix[i] = (double*)malloc(sizeof(double) * NodeNum);
	}
	double frac, domesticcpn, foreigncpn;
	frac = ((double)(Domestic_Cpn_Schd->CpnDate[Domestic_Cpn_Schd->NCpn - 1] - Domestic_Cpn_Schd->CpnDate[Domestic_Cpn_Schd->NCpn - 2])) / 365.0;
	if (Domestic_Cpn_Schd->NCpn == 1) frac = ((double)(Domestic_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0;

	T1 = max(0.0, ((double)(Domestic_Cpn_Schd->CpnPayDate[Domestic_Cpn_Schd->NCpn - 1] - Domestic_Cpn_Schd->CpnDate[Domestic_Cpn_Schd->NCpn - 1])) / 365.0);
	T2 = max(0.0, ((double)(Foreign_Cpn_Schd->CpnPayDate[Foreign_Cpn_Schd->NCpn - 1] - Foreign_Cpn_Schd->CpnDate[Foreign_Cpn_Schd->NCpn - 1])) / 365.0);
	for (i = 0; i < NodeNum; i++)
	{
		DF0 = 1.0 / (1.0 + r_on_range[i] * T1);
		DF1 = 1.0 / (1.0 + r_on_range[i] * T2);
		for (j = 0; j < NodeNum; j++)
		{
			if (DualRangeFlag == 0)
			{
				/////////////////////////////////////////////////////////////
				// DualRangeFlag 0 -> Domestic Rate Receive, Foreign Rate Pay
				/////////////////////////////////////////////////////////////
				domesticcpn = PayoffLeg(NotionalFlag, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[Domestic_Cpn_Schd->NCpn - 1],
					rx_range[i], Domestic_Cpn_Schd->FixedRate[Domestic_Cpn_Schd->NCpn - 1],
					frac, Domestic_Cpn_Schd->FloorBoundary[Domestic_Cpn_Schd->NCpn - 1], Domestic_Cpn_Schd->CapBoundary[Domestic_Cpn_Schd->NCpn - 1],
					Domestic_Cpn_Schd->RangeCpnRate[Domestic_Cpn_Schd->NCpn - 1]);
				foreigncpn = PayoffLeg(NotionalFlag, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[Foreign_Cpn_Schd->NCpn - 1],
					ry_range[j], Foreign_Cpn_Schd->FixedRate[Foreign_Cpn_Schd->NCpn - 1],
					frac, Foreign_Cpn_Schd->FloorBoundary[Foreign_Cpn_Schd->NCpn - 1], Foreign_Cpn_Schd->CapBoundary[Foreign_Cpn_Schd->NCpn - 1],
					Foreign_Cpn_Schd->RangeCpnRate[Foreign_Cpn_Schd->NCpn - 1]);
			}
			else if (DualRangeFlag == 1)
			{
				/////////////////////////////////////////////////////////////
				// DualRangeFlag 1 -> (Domestic Rate - Foreign Rate) Receive, Foreign Rate Pay
				/////////////////////////////////////////////////////////////
				domesticcpn = PayoffLeg(NotionalFlag, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[Domestic_Cpn_Schd->NCpn - 1],
					rx_range[i] - ry_range[j], Domestic_Cpn_Schd->FixedRate[Domestic_Cpn_Schd->NCpn - 1],
					frac, Domestic_Cpn_Schd->FloorBoundary[Domestic_Cpn_Schd->NCpn - 1], Domestic_Cpn_Schd->CapBoundary[Domestic_Cpn_Schd->NCpn - 1],
					Domestic_Cpn_Schd->RangeCpnRate[Domestic_Cpn_Schd->NCpn - 1]);
				foreigncpn = PayoffLeg(NotionalFlag, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[Foreign_Cpn_Schd->NCpn - 1],
					ry_range[j], Foreign_Cpn_Schd->FixedRate[Foreign_Cpn_Schd->NCpn - 1],
					frac, Foreign_Cpn_Schd->FloorBoundary[Foreign_Cpn_Schd->NCpn - 1], Foreign_Cpn_Schd->CapBoundary[Foreign_Cpn_Schd->NCpn - 1],
					Foreign_Cpn_Schd->RangeCpnRate[Foreign_Cpn_Schd->NCpn - 1]);
			}
			else if (DualRangeFlag == 2)
			{
				/////////////////////////////////////////////////////////////
				// DualRangeFlag 2 -> (Domestic Rate - Foreign Rate) Receive, Domestic Rate Pay
				/////////////////////////////////////////////////////////////
				domesticcpn = PayoffLeg(NotionalFlag, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[Domestic_Cpn_Schd->NCpn - 1],
					rx_range[i] - ry_range[j], Domestic_Cpn_Schd->FixedRate[Domestic_Cpn_Schd->NCpn - 1],
					frac, Domestic_Cpn_Schd->FloorBoundary[Domestic_Cpn_Schd->NCpn - 1], Domestic_Cpn_Schd->CapBoundary[Domestic_Cpn_Schd->NCpn - 1],
					Domestic_Cpn_Schd->RangeCpnRate[Domestic_Cpn_Schd->NCpn - 1]);
				foreigncpn = PayoffLeg(NotionalFlag, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[Foreign_Cpn_Schd->NCpn - 1],
					rx_range[i], Foreign_Cpn_Schd->FixedRate[Foreign_Cpn_Schd->NCpn - 1],
					frac, Foreign_Cpn_Schd->FloorBoundary[Foreign_Cpn_Schd->NCpn - 1], Foreign_Cpn_Schd->CapBoundary[Foreign_Cpn_Schd->NCpn - 1],
					Foreign_Cpn_Schd->RangeCpnRate[Foreign_Cpn_Schd->NCpn - 1]);
			}
			else
			{
				/////////////////////////////////////////////////////////////
				// DualRangeFlag 3 -> Domestic Rate Receive, (Foreign Rate - Domestic) Rate Pay
				/////////////////////////////////////////////////////////////
				domesticcpn = PayoffLeg(NotionalFlag, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[Domestic_Cpn_Schd->NCpn - 1],
					rx_range[i], Domestic_Cpn_Schd->FixedRate[Domestic_Cpn_Schd->NCpn - 1],
					frac, Domestic_Cpn_Schd->FloorBoundary[Domestic_Cpn_Schd->NCpn - 1], Domestic_Cpn_Schd->CapBoundary[Domestic_Cpn_Schd->NCpn - 1],
					Domestic_Cpn_Schd->RangeCpnRate[Domestic_Cpn_Schd->NCpn - 1]);
				foreigncpn = PayoffLeg(NotionalFlag, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[Foreign_Cpn_Schd->NCpn - 1],
					ry_range[j] - rx_range[i], Foreign_Cpn_Schd->FixedRate[Foreign_Cpn_Schd->NCpn - 1],
					frac, Foreign_Cpn_Schd->FloorBoundary[Foreign_Cpn_Schd->NCpn - 1], Foreign_Cpn_Schd->CapBoundary[Foreign_Cpn_Schd->NCpn - 1],
					Foreign_Cpn_Schd->RangeCpnRate[Foreign_Cpn_Schd->NCpn - 1]);
			}
			FinalDomestic[i][j] = (domesticcpn)*DF0;
			FinalForeign[i][j] = (-foreigncpn) * DF1;
			FinalIncludingOpt[i][j] = (domesticcpn)*DF0 + (-foreigncpn) * DF1;
		}
	}

	// FDM 시작
	double* Alpha_Domestic = (double*)malloc(sizeof(double) * NodeNum);
	double* Beta_Domestic = (double*)malloc(sizeof(double) * NodeNum);
	double* Gamma_Domestic = (double*)malloc(sizeof(double) * NodeNum);
	double* Lambda_Domestic = (double*)malloc(sizeof(double) * NodeNum);
	double** QVTerm_Domestic = (double**)malloc(sizeof(double*) * NodeNum);
	for (i = 0; i < NodeNum; i++) QVTerm_Domestic[i] = (double*)malloc(sizeof(double) * NodeNum);

	double* Alpha_Foreign = (double*)malloc(sizeof(double) * NodeNum);
	double* Beta_Foreign = (double*)malloc(sizeof(double) * NodeNum);
	double* Gamma_Foreign = (double*)malloc(sizeof(double) * NodeNum);
	double* Lambda_Foreign = (double*)malloc(sizeof(double) * NodeNum);
	double** QVTerm_Foreign = (double**)malloc(sizeof(double*) * NodeNum);
	for (i = 0; i < NodeNum; i++) QVTerm_Foreign[i] = (double*)malloc(sizeof(double) * NodeNum);

	double* Alpha_Temp = (double*)malloc(sizeof(double) * NodeNum);
	double* Beta_Temp = (double*)malloc(sizeof(double) * NodeNum);
	double* Gamma_Temp = (double*)malloc(sizeof(double) * NodeNum);
	double beta0, gamma0, alphaN, betaN, vol1, vol2, fxvol, alpha_t, f1, f2;

	long today, idx, idx2, NextCpnDate, NextOptDate, NextResetDate;
	////////////////////////
	// 차기 쿠폰 인덱스 설정
	////////////////////////
	idx = max(0, Domestic_Cpn_Schd->NCpn - 2);
	NextCpnDate = Domestic_Cpn_Schd->CpnDate[idx];
	if (idx > 0) frac = ((double)(Domestic_Cpn_Schd->CpnDate[idx] - Domestic_Cpn_Schd->CpnDate[idx - 1])) / 365.0;
	else frac = ((double)(Domestic_Cpn_Schd->CpnDate[idx] - LastCpnDatetoToday)) / 365.0;

	NextOptDate = opt_schd->CancelDate[max(0, opt_schd->NCancel - 1)];
	NextResetDate = Domestic_Cpn_Schd->ResetDate[max(0, Domestic_Cpn_Schd->NCpn - 2)];
	idxcalc = isinfindindexlong(NDays, DaysForFDM, NextResetDate);

	////////////////////////////////////////////
	// 차기 쿠폰날짜 to 쿠폰 지급날짜까지 할인율
	////////////////////////////////////////////
	T1 = max(0.0, ((double)(Domestic_Cpn_Schd->CpnPayDate[idx] - Domestic_Cpn_Schd->CpnDate[idx])) / 365.0);
	T2 = max(0.0, ((double)(Foreign_Cpn_Schd->CpnPayDate[idx] - Foreign_Cpn_Schd->CpnDate[idx])) / 365.0);
	for (i = 0; i < NodeNum; i++)
	{
		xt = x_range[i];
		t = T_Array[idxcalc];
		T = t + dt_on;
		if (hw_d->longterm_shortrateflag == 0)
		{
			if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
			else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
		}
		else
		{
			if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
			else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
			r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
		}
	}

	double Instant_B_s_t, Instant_QVTerm, Instant_B_s_t_2F, Instant_QVTerm_2F, Instant_Cross_QVTerm_2F, PtT, deltat;
	k = 0;
	kk = 0;
	today = DaysForFDM[NDays - 1];
	for (n = 1; n < NDays; n++)
	{
		today = DaysForFDM[NDays - 1 - n];
		vol1 = Interpolate_Linear(hw_d->HWTerm, hw_d->HWVol, hw_d->NTermHW, T_Array[NDays - 1 - n]);
		vol2 = Interpolate_Linear(hw_f->HWTerm, hw_f->HWVol, hw_f->NTermHW, T_Array[NDays - 1 - n]);
		t1 = T_Array[NDays - 1 - n];
		t2 = T_Array[NDays - n];
		deltat = t2 - t1;
		df_t = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, T_Array[NDays - 1 - n]);
		df_T = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, T_Array[NDays - n]);
		fxvol = Interpolate_Linear(FXVol_INFO->TermArray, FXVol_INFO->RateArray, FXVol_INFO->N, T_Array[NDays - 1 - n]);

		Instant_FwdDF = df_T / df_t;
		Instant_B_s_t = B_s_to_t(hw_d->kappa, t1, t2);
		Instant_QVTerm = HullWhiteQVTerm(t1, t2, hw_d->kappa, 1, hw_d->HWTerm, &vol1);
		Instant_B_s_t_2F = B_s_to_t(hw_f->kappa, t1, t2);
		Instant_QVTerm_2F = HullWhiteQVTerm(t1, t2, hw_f->kappa, 1, hw_f->HWTerm, &vol2);
		Instant_Cross_QVTerm_2F = HullWhite2F_CrossTerm(t1, t2, hw_d->kappa, 1, hw_d->HWTerm, &vol1, hw_f->kappa, hw_f->HWTerm, &vol2, rho12);

		for (i = 0; i < NodeNum; i++)
		{
			PtT = Instant_FwdDF;
			Alpha_Domestic[i] = -deltat * 0.5 * (hw_d->kappa * x_range[i] / dx + vol1 * vol1 / (dx * dx));
			Beta_Domestic[i] = (1.0 + deltat * vol1 * vol1 / (dx * dx)) + (1.0 / PtT - 1.0) * 0.5;
			Gamma_Domestic[i] = deltat * 0.5 * (hw_d->kappa * x_range[i] / dx - vol1 * vol1 / (dx * dx));
		}

		for (i = 0; i < NodeNum; i++)
		{
			PtT = Instant_FwdDF;
			Alpha_Foreign[i] = -deltat * 0.5 * ((rho23 * vol2 * fxvol + hw_f->kappa * y_range[i]) / dy + vol2 * vol2 / (dy * dy));
			Beta_Foreign[i] = (1.0 + deltat * vol2 * vol2 / (dy * dy)) + (1.0 / PtT - 1.0) * 0.5;
			Gamma_Foreign[i] = deltat * 0.5 * ((rho23 * vol2 * fxvol + hw_f->kappa * y_range[i]) / dy - vol2 * vol2 / (dy * dy));
		}

		// Tridiagonal 맨 앞,뒤값 조정
		beta0 = Beta_Domestic[0] + 2.0 * Alpha_Domestic[0];
		gamma0 = Gamma_Domestic[0] - Alpha_Domestic[0];
		betaN = Beta_Domestic[NodeNum - 1] + 2.0 * Gamma_Domestic[NodeNum - 1];
		alphaN = Alpha_Domestic[NodeNum - 1] - Gamma_Domestic[NodeNum - 1];
		Beta_Domestic[0] = beta0;
		Gamma_Domestic[0] = gamma0;
		Beta_Domestic[NodeNum - 1] = betaN;
		Alpha_Domestic[NodeNum - 1] = alphaN;

		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalDomestic, RHS_Domestic);
		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalForeign, RHS_Foreign);
		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalIncludingOpt, RHS_IncludingOpt);

		// X에 대한 Implicit
		Tri_diagonal_Matrix_Fast(Alpha_Domestic, Beta_Domestic, Gamma_Domestic, RHS_Domestic, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		Tri_diagonal_Matrix_Fast(Alpha_Domestic, Beta_Domestic, Gamma_Domestic, RHS_Foreign, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		Tri_diagonal_Matrix_Fast(Alpha_Domestic, Beta_Domestic, Gamma_Domestic, RHS_IncludingOpt, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		TransposeMat(NodeNum, RHS_Domestic);
		TransposeMat(NodeNum, RHS_Foreign);
		TransposeMat(NodeNum, RHS_IncludingOpt);

		Copy2dMatrix(FinalDomestic, RHS_Domestic, NodeNum, NodeNum);
		Copy2dMatrix(FinalForeign, RHS_Foreign, NodeNum, NodeNum);
		Copy2dMatrix(FinalIncludingOpt, RHS_IncludingOpt, NodeNum, NodeNum);

		// Tridiagonal 맨 앞,뒤값 조정
		beta0 = Beta_Foreign[0] + 2.0 * Alpha_Foreign[0];
		gamma0 = Gamma_Foreign[0] - Alpha_Foreign[0];
		betaN = Beta_Foreign[NodeNum - 1] + 2.0 * Gamma_Foreign[NodeNum - 1];
		alphaN = Alpha_Foreign[NodeNum - 1] - Gamma_Foreign[NodeNum - 1];
		Beta_Foreign[0] = beta0;
		Gamma_Foreign[0] = gamma0;
		Beta_Foreign[NodeNum - 1] = betaN;
		Alpha_Foreign[NodeNum - 1] = alphaN;

		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalDomestic, RHS_Domestic);
		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalForeign, RHS_Foreign);
		ResultRHS_2F(NodeNum, x_range, y_range, hw_d->kappa, hw_f->kappa, vol1, vol2, rho12, dx, dy, deltat, FinalIncludingOpt, RHS_IncludingOpt);

		// Y에 대한 Implicit
		Tri_diagonal_Matrix_Fast(Alpha_Foreign, Beta_Foreign, Gamma_Foreign, RHS_Domestic, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		Tri_diagonal_Matrix_Fast(Alpha_Foreign, Beta_Foreign, Gamma_Foreign, RHS_Foreign, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		Tri_diagonal_Matrix_Fast(Alpha_Foreign, Beta_Foreign, Gamma_Foreign, RHS_IncludingOpt, NodeNum, Alpha_Temp, Beta_Temp, Gamma_Temp);
		TransposeMat(NodeNum, RHS_Domestic);
		TransposeMat(NodeNum, RHS_Foreign);
		TransposeMat(NodeNum, RHS_IncludingOpt);
		Copy2dMatrix(FinalDomestic, RHS_Domestic, NodeNum, NodeNum);
		Copy2dMatrix(FinalForeign, RHS_Foreign, NodeNum, NodeNum);
		Copy2dMatrix(FinalIncludingOpt, RHS_IncludingOpt, NodeNum, NodeNum);

		if (today <= 0)
		{
			break;
		}

		if (today == NextCpnDate)
		{
			///////////////////////////////////
			// 차기 쿠폰날짜에 기초금리 처리 //
			///////////////////////////////////
			if (NextResetDate > 0)
			{
				/////////////////////////////////////////////////////////////////
				// 차기 쿠폰금리산정의 기초금리 리셋일이 0보다 클 경우 금리추정//
				/////////////////////////////////////////////////////////////////
				idxreset = isinfindindexlong(NDays, DaysForFDM, NextResetDate);
				for (i = 0; i < NodeNum; i++)
				{
					xt = x_range[i];
					t = T_Array[idxreset];
					T = t + RefType_Domestic->Maturity;
					if (hw_d->longterm_shortrateflag == 0) Rate = HW_Rate(RefType_Domestic->RefRateType, t, T, ZeroDomestic->N, ZeroDomestic->TermArray,
						ZeroDomestic->RateArray, xt, ndates_domestic, RefType_Domestic->NCPN_Ann, domestic_DF_t_T[idxreset],
						domestic_QVTerm[idxreset], domestic_B_t_T[idxreset], domestic_dt[idxreset]);
					else Rate = HW_Rate_LongTermShortRate(RefType_Domestic->RefRateType, t, T, ZeroDomestic->N, ZeroDomestic->TermArray,
						ZeroDomestic->RateArray, xt, ndates_domestic, RefType_Domestic->NCPN_Ann, domestic_DF_t_T[idxreset],
						domestic_QVTerm[idxreset], domestic_B_t_T[idxreset], domestic_dt[idxreset]);
					rx_range[i] = Rate;
				}

				for (i = 0; i < NodeNum; i++)
				{
					xt = y_range[i];
					t = T_Array[idxreset];
					T = t + RefType_Foreign->Maturity;
					if (hw_f->longterm_shortrateflag == 0) Rate = HW_Rate(RefType_Foreign->RefRateType, t, T, ZeroForeign->N, ZeroForeign->TermArray,
						ZeroForeign->RateArray, xt, ndates_foreign, RefType_Foreign->NCPN_Ann, foreign_DF_t_T[idxreset],
						foreign_QVTerm[idxreset], foreign_B_t_T[idxreset], foreign_dt[idxreset]);
					else Rate = HW_Rate_LongTermShortRate(RefType_Foreign->RefRateType, t, T, ZeroForeign->N, ZeroForeign->TermArray,
						ZeroForeign->RateArray, xt, ndates_foreign, RefType_Foreign->NCPN_Ann, foreign_DF_t_T[idxreset],
						foreign_QVTerm[idxreset], foreign_B_t_T[idxreset], foreign_dt[idxreset]);
					ry_range[i] = Rate;
				}

			}
			else if (NextResetDate == 0)
			{
				/////////////////////////////////////////////////////////////////////////
				// 차기 쿠폰금리산정의 금리 리셋일이 오늘일 경우 현재 커브의 금리 추정 //
				/////////////////////////////////////////////////////////////////////////
				f1 = FSR(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, 0.0, RefType_Domestic->Maturity, 12.0 / ((double)RefType_Domestic->NCPN_Ann));
				f2 = FSR(ZeroForeign->TermArray, ZeroForeign->RateArray, ZeroForeign->N, 0.0, RefType_Foreign->Maturity, 12.0 / ((double)RefType_Foreign->NCPN_Ann));
				for (i = 0; i < NodeNum; i++)
				{
					rx_range[i] = f1;
					ry_range[i] = f2;
				}
			}
			else
			{
				////////////////////////////////////////////////
				// 차기 쿠폰금리산정의 금리 리셋일 지났을 경우//
				////////////////////////////////////////////////
				f1 = Domestic_Cpn_Schd->PreDeterminedRate;
				f2 = Foreign_Cpn_Schd->PreDeterminedRate;
				for (i = 0; i < NodeNum; i++)
				{
					rx_range[i] = f1;
					ry_range[i] = f2;
				}
			}

			///////////////////////////
			// 쿠폰날짜의 Payoff 결정
			///////////////////////////

			for (i = 0; i < NodeNum; i++)
			{
				DF0 = 1.0 / (1.0 + r_on_range[i] * T1);
				DF1 = 1.0 / (1.0 + r_on_range[i] * T2);
				for (j = 0; j < NodeNum; j++)
				{
					if (idx == 0 && LastCpnDatetoToday < 0)
					{
						///////////////////////////////////////////////////
						// 금번쿠폰 금리 결정 이후 Pricing하는 경우
						///////////////////////////////////////////////////
						if (DualRangeFlag == 0)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 0 -> Domestic Rate Receive, Foreign Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], Domestic_Cpn_Schd->PreDeterminedRate, Domestic_Cpn_Schd->FixedRate[idx],
								((double)(Domestic_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], Foreign_Cpn_Schd->PreDeterminedRate, Foreign_Cpn_Schd->FixedRate[idx],
								((double)(Foreign_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else if (DualRangeFlag == 1)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 1 -> (Domestic Rate - Foreign Rate) Receive, Foreign Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], Domestic_Cpn_Schd->PreDeterminedRate - Foreign_Cpn_Schd->PreDeterminedRate, Domestic_Cpn_Schd->FixedRate[idx],
								((double)(Domestic_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], Foreign_Cpn_Schd->PreDeterminedRate, Foreign_Cpn_Schd->FixedRate[idx],
								((double)(Foreign_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else if (DualRangeFlag == 2)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 2 -> (Domestic Rate - Foreign Rate) Receive, Domestic Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], Domestic_Cpn_Schd->PreDeterminedRate - Foreign_Cpn_Schd->PreDeterminedRate, Domestic_Cpn_Schd->FixedRate[idx],
								((double)(Domestic_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], Domestic_Cpn_Schd->PreDeterminedRate, Foreign_Cpn_Schd->FixedRate[idx],
								((double)(Foreign_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 3 -> Domestic Rate Receive, (Foreign Rate - Domestic) Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], Domestic_Cpn_Schd->PreDeterminedRate, Domestic_Cpn_Schd->FixedRate[idx],
								((double)(Domestic_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], Foreign_Cpn_Schd->PreDeterminedRate - Domestic_Cpn_Schd->PreDeterminedRate, Foreign_Cpn_Schd->FixedRate[idx],
								((double)(Foreign_Cpn_Schd->CpnDate[0] - LastCpnDatetoToday)) / 365.0, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
					}
					else
					{
						///////////////////////////////////////
						// 추정된 금리 기반으로 쿠폰 Generate
						///////////////////////////////////////
						if (DualRangeFlag == 0)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 0 -> Domestic Rate Receive, Foreign Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], rx_range[i], Domestic_Cpn_Schd->FixedRate[idx],
								frac, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], ry_range[j], Foreign_Cpn_Schd->FixedRate[idx],
								frac, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else if (DualRangeFlag == 1)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 1 -> (Domestic Rate - Foreign Rate) Receive, Foreign Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], rx_range[i] - ry_range[j], Domestic_Cpn_Schd->FixedRate[idx],
								frac, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], ry_range[j], Foreign_Cpn_Schd->FixedRate[idx],
								frac, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else if (DualRangeFlag == 2)
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 2 -> (Domestic Rate - Foreign Rate) Receive, Domestic Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], rx_range[i] - ry_range[j], Domestic_Cpn_Schd->FixedRate[idx],
								frac, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], rx_range[i], Foreign_Cpn_Schd->FixedRate[idx],
								frac, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
						else
						{
							/////////////////////////////////////////////////////////////
							// DualRangeFlag 3 -> Domestic Rate Receive, (Foreign Rate - Domestic) Rate Pay
							/////////////////////////////////////////////////////////////
							domesticcpn = PayoffLeg(0, NotionalAmt, Domestic_Cpn_Schd->ParticipateRate[idx], rx_range[i], Domestic_Cpn_Schd->FixedRate[idx],
								frac, Domestic_Cpn_Schd->FloorBoundary[idx], Domestic_Cpn_Schd->CapBoundary[idx], Domestic_Cpn_Schd->RangeCpnRate[idx]);
							foreigncpn = PayoffLeg(0, NotionalAmt, Foreign_Cpn_Schd->ParticipateRate[idx], ry_range[j] - rx_range[i], Foreign_Cpn_Schd->FixedRate[idx],
								frac, Foreign_Cpn_Schd->FloorBoundary[idx], Foreign_Cpn_Schd->CapBoundary[idx], Foreign_Cpn_Schd->RangeCpnRate[idx]);
						}
					}
					FinalDomestic[i][j] = FinalDomestic[i][j] + (domesticcpn)*DF0;
					FinalForeign[i][j] = FinalForeign[i][j] + (-foreigncpn) * DF1;
					FinalIncludingOpt[i][j] = FinalIncludingOpt[i][j] + ((domesticcpn)*DF0 + (-foreigncpn) * DF1);
				}
			}

			////////////////////////
			// 차기 쿠폰 인덱스 설정
			////////////////////////
			k += 1;
			idx = max(0, Domestic_Cpn_Schd->NCpn - 2 - k);
			NextCpnDate = Domestic_Cpn_Schd->CpnDate[idx];
			NextResetDate = Domestic_Cpn_Schd->ResetDate[idx];
			idxcalc = isinfindindexlong(NDays, DaysForFDM, NextCpnDate);

			if (idx > 0) frac = ((double)(Domestic_Cpn_Schd->CpnDate[idx] - Domestic_Cpn_Schd->CpnDate[idx - 1])) / 365.0;
			else frac = ((double)(Domestic_Cpn_Schd->CpnDate[idx] - LastCpnDatetoToday)) / 365.0;

			////////////////////////////////////////////
			// 차기 쿠폰날짜 to 쿠폰 지급날짜까지 할인율
			////////////////////////////////////////////
			T1 = max(0.0, ((double)(Domestic_Cpn_Schd->CpnPayDate[idx] - Domestic_Cpn_Schd->CpnDate[idx])) / 365.0);
			T2 = max(0.0, ((double)(Foreign_Cpn_Schd->CpnPayDate[idx] - Foreign_Cpn_Schd->CpnDate[idx])) / 365.0);
			for (i = 0; i < NodeNum; i++)
			{
				xt = x_range[i];
				t = T_Array[idxcalc];
				T = t + dt_on;
				if (hw_d->longterm_shortrateflag == 0)
				{
					if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
					else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
					r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
				}
				else
				{
					if (t >= 0.0) DF0 = DF_t_T_overnight[idxcalc] * exp(-xt * B_t_T_overnight[idxcalc] + QVTerm_overnight[idxcalc]);
					else DF0 = Calc_Discount_Factor(ZeroDomestic->TermArray, ZeroDomestic->RateArray, ZeroDomestic->N, t);
					r_on_range[i] = (1.0 - DF0) / (dt_on * DF0);
				}
			}
		}

		if (opt_schd->CancelOptionFlag == 1)
		{
			/////////////////////////////
			// 스왑 취소 옵션이 존재하는 경우
			/////////////////////////////
			if (today == NextOptDate)
			{
				for (i = 0; i < NodeNum; i++)
				{
					for (j = 0; j < NodeNum; j++)
					{
						if (opt_schd->CancelType == 0) FinalIncludingOpt[i][j] = max(0.0, FinalIncludingOpt[i][j]); // Domestic Leg가 Cancel 옵션 보유
						else FinalIncludingOpt[i][j] = min(0.0, FinalIncludingOpt[i][j]); // Foreign Leg가 Cancel 옵션 보유
					}
				}
				kk = kk + 1;
				idx2 = max(opt_schd->NCancel - 2 - kk, 0);
				NextOptDate = opt_schd->CancelDate[idx2];
			}
		}

	}

	for (i = 0; i < NodeNum; i++) for (j = 0; j < NodeNum; j++) PriceMatrix[i][j] = FinalDomestic[i][j] + FinalForeign[i][j];
	OptValue = FinalIncludingOpt[idx_px][idx_py] - PriceMatrix[idx_px][idx_py];
	Price = FinalIncludingOpt[idx_px][idx_py];
	Price_NotOpt = PriceMatrix[idx_px][idx_py];

	resultarray[0] = FinalDomestic[idx_px][idx_py];
	resultarray[1] = FinalForeign[idx_px][idx_py];
	resultarray[2] = Price;
	resultarray[3] = OptValue;

	free(Date);
	free(CombinedDate);
	for (j = 0; j < NDays; j++)
	{
		free(domestic_DF_t_T[j]);
		free(domestic_B_t_T[j]);
		free(domestic_QVTerm[j]);
		free(domestic_dt[j]);
	}
	free(domestic_DF_t_T);
	free(domestic_B_t_T);
	free(domestic_QVTerm);
	free(domestic_dt);

	for (j = 0; j < NDays; j++)
	{
		free(foreign_DF_t_T[j]);
		free(foreign_B_t_T[j]);
		free(foreign_QVTerm[j]);
		free(foreign_dt[j]);
	}
	free(foreign_DF_t_T);
	free(foreign_B_t_T);
	free(foreign_QVTerm);
	free(foreign_dt);

	free(dt_Array);
	free(T_Array);
	free(DaysForFDM);
	free(x_range);
	free(y_range);
	free(rx_range);
	free(ry_range);
	for (i = 0; i < NodeNum; i++)
	{
		free(FinalDomestic[i]);
		free(FinalForeign[i]);
		free(FinalIncludingOpt[i]);
		free(RHS_Domestic[i]);
		free(RHS_Foreign[i]);
		free(RHS_IncludingOpt[i]);
		free(PriceMatrix[i]);
	}
	free(FinalDomestic);
	free(FinalForeign);
	free(FinalIncludingOpt);
	free(RHS_Domestic);
	free(RHS_Foreign);
	free(RHS_IncludingOpt);
	free(PriceMatrix);
	free(Alpha_Domestic);
	free(Beta_Domestic);
	free(Gamma_Domestic);
	free(Alpha_Foreign);
	free(Beta_Foreign);
	free(Gamma_Foreign);
	free(Alpha_Temp);
	free(Beta_Temp);
	free(Gamma_Temp);
	free(Lambda_Domestic);
	for (i = 0; i < NodeNum; i++) free(QVTerm_Domestic[i]);
	free(QVTerm_Domestic);
	free(Lambda_Foreign);
	for (i = 0; i < NodeNum; i++) free(QVTerm_Foreign[i]);
	free(QVTerm_Foreign);
	free(r_on_range);
	free(DF_t_T_overnight);
	free(B_t_T_overnight);
	free(QVTerm_overnight);

}



DLLEXPORT(long) IRStructuedSwapFDM(
	long PricingDateYYYYMMDD,
	double* kappa,
	long* nhwvol_domestic_foreign,
	double* hwvolterm_domestic_foreign,
	double* hwvol_domestic_foreign,

	long* nzero_domestic_foreign,
	double* zeroterm_domestic_foreign,
	double* zerorate_domestic_foreign,
	double rho12,
	double rho23,

	long nfxvol,
	double* fxvolterm,
	double* fxvol,
	long* ncpn_ann_domestic_foreign,
	double* maturity_domestic_foreign,

	long* reftype_domestic_foreign,
	long ncpn,
	long* ResetDateYYYYMMDD_RAW,
	long* CpnDateYYYYMMDD_RAW,
	long* PayDateDomesticYYYYMMDD_RAW,

	long* PayDateForeignYYYYMMDD_RAW,
	double* participate_rate_domestic_foreign,
	double* floorboundary_domestic_foreign,
	double* capboundary_domestic_foreign,
	double* rangecpnrate_domestic_foreign,

	double* fixedrate_domestic_foreign,
	double* predeterminedrate_domestic_foreign,
	long optflag,
	long nopt,
	long* CancelDateYYYYMMDD_RAW,

	long CancelType,		// 0 Domestic Leg Call 보유 1 Domestic Leg Call 보유
	long NodeNum,
	long DailyFDMFlag,
	long DualRangeFlag,
	long NotionalFlag,

	long GreekFlag,
	double* resultarray1,
	double* resultarray2
)
{
	long i, j, n;

	double kappa1 = kappa[0];
	long nvol1 = nhwvol_domestic_foreign[0];
	double* termvol1 = hwvolterm_domestic_foreign;
	double* volarray1 = hwvol_domestic_foreign;
	double kappa2 = kappa[1];
	long nvol2 = nhwvol_domestic_foreign[1];
	double* termvol2 = hwvolterm_domestic_foreign + nvol1;
	double* volarray2 = hwvol_domestic_foreign + nvol1;

	long NZero_domestic = nzero_domestic_foreign[0];
	double* ZeroTerm_domestic = zeroterm_domestic_foreign;
	double* ZeroRate_domestic = zerorate_domestic_foreign;

	long NZero_foreign = nzero_domestic_foreign[1];
	double* ZeroTerm_foreign = zeroterm_domestic_foreign + NZero_domestic;
	double* ZeroRate_foreign = zerorate_domestic_foreign + NZero_domestic;

	long NFXVol = nfxvol;
	double* FXVolTerm = fxvolterm;
	double* FXVol = fxvol;

	long PricingDate = PricingDateYYYYMMDD;

	long LastCpnDatetoToday = 0;

	long Domestic_NCPN_Ann = ncpn_ann_domestic_foreign[0];
	double Domestic_Maturity = maturity_domestic_foreign[0];
	long Foreign_NCPN_Ann = ncpn_ann_domestic_foreign[1];
	double Foreign_Maturity = maturity_domestic_foreign[1];
	long Domestic_RateType = reftype_domestic_foreign[0];
	long Foreign_RateType = reftype_domestic_foreign[0];

	long LongShortRateUseFlag = 0;
	double LongShortRate = 0.0;

	long NCoupon = ncpn;
	double* PartRateDomestic_RAW = participate_rate_domestic_foreign;
	double* PartRateForeign_RAW = participate_rate_domestic_foreign + ncpn;
	double* FloorBoundaryDomestic_RAW = floorboundary_domestic_foreign;
	double* FloorBoundaryForeign_RAW = floorboundary_domestic_foreign + ncpn;
	double* CapBoundaryDomestic_RAW = capboundary_domestic_foreign;
	double* CapBoundaryForeign_RAW = capboundary_domestic_foreign + ncpn;
	double* RangeCpnRateDomestic_RAW = rangecpnrate_domestic_foreign;
	double* RangeCpnRateForeign_RAW = rangecpnrate_domestic_foreign + ncpn;
	double* FixedRateDomestic_RAW = fixedrate_domestic_foreign;
	double* FixedRateForeign_RAW = fixedrate_domestic_foreign + ncpn;
	double* PreDeterminedRateDomestic_RAW = predeterminedrate_domestic_foreign;
	double* PreDeterminedRateForeign_RAW = predeterminedrate_domestic_foreign + ncpn;

	long CancelOptionFlag = optflag;
	long NCancelOption = nopt;

	long n_alreadygone = 0;
	long n_alreadygone_opt = 0;
	for (i = 0; i < NCoupon; i++)
	{
		if (CpnDateYYYYMMDD_RAW[i] <= PricingDate)
		{
			n_alreadygone += 1;
		}
	}
	for (i = 0; i < NCancelOption; i++) if (CancelDateYYYYMMDD_RAW[i] <= PricingDate) n_alreadygone_opt += 1;
	long NCpn = NCoupon - n_alreadygone;
	long NCancel = NCancelOption - n_alreadygone_opt;
	long* ResetDateYYYYMMDD = ResetDateYYYYMMDD_RAW + n_alreadygone;
	long* CpnDateYYYYMMDD = CpnDateYYYYMMDD_RAW + n_alreadygone;
	long* PayDateDomesticYYYYMMDD = PayDateDomesticYYYYMMDD_RAW + n_alreadygone;
	long* PayDateForeignYYYYMMDD = PayDateForeignYYYYMMDD_RAW + n_alreadygone;
	long* CancelDateYYYYMMDD = CancelDateYYYYMMDD_RAW + n_alreadygone_opt;

	long* ResetDate = (long*)malloc(sizeof(long) * NCpn);
	long* CpnDate = (long*)malloc(sizeof(long) * NCpn);
	long* CpnPayDateDomestic = (long*)malloc(sizeof(long) * NCpn);
	long* CpnPayDateForeign = (long*)malloc(sizeof(long) * NCpn);
	for (i = 0; i < NCpn; i++)
	{
		ResetDate[i] = DayCountAtoB(PricingDate, ResetDateYYYYMMDD[i]);
		CpnDate[i] = DayCountAtoB(PricingDate, CpnDateYYYYMMDD[i]);
		CpnPayDateDomestic[i] = DayCountAtoB(PricingDate, PayDateDomesticYYYYMMDD[i]);
		CpnPayDateForeign[i] = DayCountAtoB(PricingDate, PayDateForeignYYYYMMDD[i]);
	}

	LastCpnDatetoToday = 0;
	if (ResetDate[0] < 0) LastCpnDatetoToday = ResetDate[0];

	long* CancelDate = (long*)malloc(sizeof(long) * NCancel);
	for (i = 0; i < NCancel; i++) CancelDate[i] = DayCountAtoB(PricingDate, CancelDateYYYYMMDD[i]);

	double* PartRateDomestic = PartRateDomestic_RAW + n_alreadygone;
	double* PartRateForeign = PartRateForeign_RAW + n_alreadygone;
	double* FloorBoundaryDomestic = FloorBoundaryDomestic_RAW + n_alreadygone;
	double* FloorBoundaryForeign = FloorBoundaryForeign_RAW + n_alreadygone;
	double* CapBoundaryDomestic = CapBoundaryDomestic_RAW + n_alreadygone;
	double* CapBoundaryForeign = CapBoundaryForeign_RAW + n_alreadygone;
	double* RangeCpnRateDomestic = RangeCpnRateDomestic_RAW + n_alreadygone;
	double* RangeCpnRateForeign = RangeCpnRateForeign_RAW + n_alreadygone;
	double* FixedRateDomestic = FixedRateDomestic_RAW + n_alreadygone;
	double* FixedRateForeign = FixedRateForeign_RAW + n_alreadygone;
	double PreDeterminedRateDomestic = PreDeterminedRateDomestic_RAW[n_alreadygone];
	double PreDeterminedRateForeign = PreDeterminedRateForeign_RAW[n_alreadygone];

	CPN_SCHD* Domestic_Cpn_Schd = new CPN_SCHD;
	Domestic_Cpn_Schd->NCpn = NCpn;
	Domestic_Cpn_Schd->ResetDate = ResetDate;
	Domestic_Cpn_Schd->CpnDate = CpnDate;
	Domestic_Cpn_Schd->CpnPayDate = CpnPayDateDomestic;
	Domestic_Cpn_Schd->FixedRate = FixedRateDomestic;
	Domestic_Cpn_Schd->ParticipateRate = PartRateDomestic;
	Domestic_Cpn_Schd->FloorBoundary = FloorBoundaryDomestic;
	Domestic_Cpn_Schd->CapBoundary = CapBoundaryDomestic;
	Domestic_Cpn_Schd->RangeCpnRate = RangeCpnRateDomestic;
	Domestic_Cpn_Schd->PreDeterminedRate = PreDeterminedRateDomestic;
	CPN_SCHD* Foreign_Cpn_Schd = new CPN_SCHD;
	Foreign_Cpn_Schd->NCpn = NCpn;
	Foreign_Cpn_Schd->ResetDate = ResetDate;
	Foreign_Cpn_Schd->CpnDate = CpnDate;
	Foreign_Cpn_Schd->CpnPayDate = CpnPayDateForeign;
	Foreign_Cpn_Schd->FixedRate = FixedRateForeign;
	Foreign_Cpn_Schd->ParticipateRate = PartRateForeign;
	Foreign_Cpn_Schd->FloorBoundary = FloorBoundaryForeign;
	Foreign_Cpn_Schd->CapBoundary = CapBoundaryForeign;
	Foreign_Cpn_Schd->RangeCpnRate = RangeCpnRateForeign;
	Foreign_Cpn_Schd->PreDeterminedRate = PreDeterminedRateForeign;
	if (Foreign_Cpn_Schd->NCpn != Domestic_Cpn_Schd->NCpn) return 1;
	n = 0;
	for (i = 0; i < Foreign_Cpn_Schd->NCpn; i++)
	{
		// 두 Leg의 쿠폰측정날짜, 리셋날짜가 동일한 경우만 Pricing하자(지급일은 달라도 됨)
		if (Foreign_Cpn_Schd->ResetDate[i] == Domestic_Cpn_Schd->ResetDate[i] && Foreign_Cpn_Schd->CpnDate[i] == Domestic_Cpn_Schd->CpnDate[i])
		{
			n += 1;
		}
	}

	OPT_SCHD* option_schd = new OPT_SCHD;
	option_schd->CancelOptionFlag = CancelOptionFlag;
	option_schd->NCancel = NCancel;
	option_schd->CancelType = CancelType;
	option_schd->CancelDate = CancelDate;

	HW1F_INFO* hw_d = new HW1F_INFO;
	hw_d->NTermHW = nvol1;
	hw_d->HWTerm = termvol1;
	hw_d->HWVol = volarray1;
	hw_d->kappa = kappa1;
	hw_d->longterm_shortrate = 0.0;
	hw_d->longterm_shortrateflag = 0;

	HW1F_INFO* hw_f = new HW1F_INFO;
	hw_f->NTermHW = nvol2;
	hw_f->HWTerm = termvol2;
	hw_f->HWVol = volarray2;
	hw_f->kappa = kappa2;
	hw_f->longterm_shortrate = 0.0;
	hw_f->longterm_shortrateflag = 0;

	RATE_INFO* ZeroDomestic = new RATE_INFO;
	ZeroDomestic->N = NZero_domestic;
	ZeroDomestic->TermArray = ZeroTerm_domestic;
	ZeroDomestic->RateArray = ZeroRate_domestic;

	RATE_INFO* ZeroForeign = new RATE_INFO;
	ZeroForeign->N = NZero_foreign;
	ZeroForeign->TermArray = ZeroTerm_foreign;
	ZeroForeign->RateArray = ZeroRate_foreign;

	RATE_INFO* FXVol_INFO = new RATE_INFO;
	FXVol_INFO->N = NFXVol;
	FXVol_INFO->TermArray = FXVolTerm;
	FXVol_INFO->RateArray = FXVol;

	REF_RATE* RefType_Domestic = new REF_RATE;
	RefType_Domestic->NCPN_Ann = Domestic_NCPN_Ann;
	RefType_Domestic->Maturity = Domestic_Maturity;
	RefType_Domestic->RefRateType = Domestic_RateType;

	REF_RATE* RefType_Foreign = new REF_RATE;
	RefType_Foreign->NCPN_Ann = Foreign_NCPN_Ann;
	RefType_Foreign->Maturity = Foreign_Maturity;
	RefType_Foreign->RefRateType = Foreign_RateType;

	if (n == Foreign_Cpn_Schd->NCpn) // 스케줄 정상인경우 가격계산
	{
		Test(NodeNum, NotionalFlag, RefType_Domestic, RefType_Foreign,
			ZeroDomestic, ZeroForeign, hw_d, hw_f, rho12,
			rho23, FXVol_INFO, DailyFDMFlag,
			LastCpnDatetoToday, Domestic_Cpn_Schd, Foreign_Cpn_Schd, DualRangeFlag, option_schd, resultarray1);

		if (GreekFlag >= 1)
		{
			double* CurveUp = (double*)malloc(sizeof(double) * (NZero_domestic + NZero_foreign));
			double* PV01_Domestic = (double*)malloc(sizeof(double) * NZero_domestic);
			double* PV01_Foreign = (double*)malloc(sizeof(double) * NZero_foreign);

			double PV01_Curve_Domestic;
			double PV01_Curve_Foreign;
			double P = resultarray1[2];
			long n_fdmhalf = NodeNum / 2;
			long dailyfdmflag2 = 0;
			if (GreekFlag > 1)
			{
				for (i = 0; i < NZero_domestic; i++)
				{
					for (j = 0; j < NZero_domestic; j++)
					{
						if (i == j) CurveUp[j] = ZeroRate_domestic[j] + 0.0001;
						else CurveUp[j] = ZeroRate_domestic[j];
					}

					ZeroDomestic->RateArray = CurveUp;

					Test(n_fdmhalf, NotionalFlag, RefType_Domestic, RefType_Foreign,
						ZeroDomestic, ZeroForeign, hw_d, hw_f, rho12,
						rho23, FXVol_INFO, dailyfdmflag2,
						LastCpnDatetoToday, Domestic_Cpn_Schd, Foreign_Cpn_Schd, DualRangeFlag, option_schd, resultarray2);

					PV01_Domestic[i] = (resultarray2[2] - P);

					// 원상복귀
					ZeroDomestic->RateArray = ZeroRate_domestic;
				}

				for (i = 0; i < NZero_foreign; i++)
				{
					for (j = 0; j < NZero_foreign; j++)
					{
						if (i == j) CurveUp[j] = ZeroRate_foreign[j] + 0.0001;
						else CurveUp[j] = ZeroRate_foreign[j];
					}

					ZeroForeign->RateArray = CurveUp;

					Test(n_fdmhalf, NotionalFlag, RefType_Domestic, RefType_Foreign,
						ZeroDomestic, ZeroForeign, hw_d, hw_f, rho12,
						rho23, FXVol_INFO, dailyfdmflag2,
						LastCpnDatetoToday, Domestic_Cpn_Schd, Foreign_Cpn_Schd, DualRangeFlag, option_schd, resultarray2);

					PV01_Foreign[i] = (resultarray2[2] - P);

					// 원상복귀
					ZeroForeign->RateArray = ZeroRate_foreign;
				}
			}

			// 커브 전체
			for (j = 0; j < NZero_domestic; j++) CurveUp[j] = ZeroRate_domestic[j] + 0.0001;

			ZeroDomestic->RateArray = CurveUp;
			Test(n_fdmhalf, NotionalFlag, RefType_Domestic, RefType_Foreign,
				ZeroDomestic, ZeroForeign, hw_d, hw_f, rho12,
				rho23, FXVol_INFO, dailyfdmflag2,
				LastCpnDatetoToday, Domestic_Cpn_Schd, Foreign_Cpn_Schd, DualRangeFlag, option_schd, resultarray2);

			PV01_Curve_Domestic = (resultarray2[2] - P);
			ZeroDomestic->RateArray = ZeroRate_domestic;

			// 커브 전체
			for (j = 0; j < NZero_foreign; j++) CurveUp[j] = ZeroRate_foreign[j] + 0.0001;

			ZeroForeign->RateArray = CurveUp;
			Test(n_fdmhalf, NotionalFlag, RefType_Domestic, RefType_Foreign,
				ZeroDomestic, ZeroForeign, hw_d, hw_f, rho12,
				rho23, FXVol_INFO, dailyfdmflag2,
				LastCpnDatetoToday, Domestic_Cpn_Schd, Foreign_Cpn_Schd, DualRangeFlag, option_schd, resultarray2);

			PV01_Curve_Foreign = (resultarray2[2] - P);
			ZeroForeign->RateArray = ZeroRate_foreign;

			// 저장
			resultarray2[0] = PV01_Curve_Domestic;
			resultarray2[1] = PV01_Curve_Foreign;
			if (GreekFlag > 1)
			{
				for (i = 0; i < NZero_domestic; i++) resultarray2[2 + i] = PV01_Domestic[i];
				for (i = 0; i < NZero_foreign; i++) resultarray2[2 + i + NZero_domestic] = PV01_Foreign[i];
			}

			free(PV01_Domestic);
			free(PV01_Foreign);
			free(CurveUp);
		}
	}

	free(ResetDate);
	free(CpnDate);
	free(CpnPayDateDomestic);
	free(CpnPayDateForeign);
	free(CancelDate);

	delete Domestic_Cpn_Schd;
	delete Foreign_Cpn_Schd;
	delete option_schd;
	delete hw_d;
	delete hw_f;
	delete ZeroDomestic;
	delete ZeroForeign;
	delete FXVol_INFO;
	delete RefType_Domestic;
	delete RefType_Foreign;
	//_CrtDumpMemoryLeaks();

}