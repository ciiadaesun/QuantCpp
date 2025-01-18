#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#include "CalcDate.h"

#include "SABR.h"
#ifndef UTILITY
#include "Util.h"
#define UTILITY 1
#endif

#ifndef STRUCTURE
#include "Structure.h"
#define STRUCTURE 1
#endif
#include "GetTextDump.h"

#include <crtdbg.h>

double Sumation(long NArray, double* Array)
{
	long i;
	double s = 0.0;
	for (i = 0; i < NArray; i++)
	{
		s += Array[i];
	}
	return s;
}

long isin(long x, long* marray, long narray)
{
	long i;
	long s = 0;
	for (i = 0; i < narray; i++)
	{
		if (x == marray[i])
		{
			s = 1;
			break;
		}
	}
	return s;
}

long isinFindIndex(long x, long* array, long narray, long& Idx)
{
	long i;
	long s = 0;
	Idx = -1;
	for (i = 0; i < narray; i++)
	{
		if (x == array[i])
		{
			s = 1;
			Idx = i;
			break;
		}
	}
	return s;
}

long SaveErrorName(char* Error, char ErrorName[100])
{
	long k;
	long i;
	long Ascii;
	k = 0;
	for (i = 0; i < 100; i++)
	{
		Ascii = (long)ErrorName[i];
		if ((Ascii >= 48 && Ascii <= 57) || (Ascii >= 65 && Ascii <= 90) || (Ascii >= 97 && Ascii <= 122) || (Ascii == 32))
		{
			Error[k] = ErrorName[i];
			k++;
		}
		else
		{
			break;
		}
	}
	return -1;
}

double SimpleBSCall(double S, double X, double r_drift, double T, double d, double r_disc, double Sigma)
{
	double d1 = (log(S / X) + (r_drift + 0.5 * Sigma * Sigma) * T) / (Sigma * sqrt(T));
	double d2 = d1 - Sigma * sqrt(T);
	return S * exp(-d * T) * CDF_N(d1) - X * exp(-r_disc * T) * CDF_N(d2);
}

DLLEXPORT(double) CalcForwardPrice(long PriceDateYYYYMMDD, long EndDateYYYYMMDD, double S, long nrate, double *term_rate, double *rate, long ndiv, double* term_div, double* div)
{
	if (PriceDateYYYYMMDD < 19000001) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateYYYYMMDD);
	if (EndDateYYYYMMDD < 19000001) EndDateYYYYMMDD = ExcelDateToCDate(EndDateYYYYMMDD);
	double T = ((double)DayCountAtoB(PriceDateYYYYMMDD, EndDateYYYYMMDD))/365.0;
	double r = Interpolate_Linear(term_rate, rate, nrate, T);
	double d = Interpolate_Linear(term_div, div, ndiv, T);
	return S * exp((r - d) * T);
}

double SimpleBSCall_With_Forward(double F, double X, double T, double r_disc, double Sigma)
{
	double d1 = (log(F / X) + (0.5 * Sigma * Sigma) * T) / (Sigma * sqrt(T));
	double d2 = d1 - Sigma * sqrt(T);
	return (F* CDF_N(d1) - X * CDF_N(d2))*exp(-r_disc * T);
}

double SimpleBSPut_With_Forward(double F, double X, double T, double r_disc, double Sigma)
{
	double d1 = (log(F / X) + (0.5 * Sigma * Sigma) * T) / (Sigma * sqrt(T));
	double d2 = d1 - Sigma * sqrt(T);
	return (-F * CDF_N(-d1) + X * CDF_N(-d2)) * exp(-r_disc * T);
}

DLLEXPORT(long) CalcImvolFromPrice(long PriceDateYYYYMMDD, long EndDateYYYYMMDD, long PayDateYYYYMMDD, double F, double X, long nrate, double* term_rate, double* rate, double OptPrice, long Call0Put1Flag, double* ResultValue)
{
	if (PriceDateYYYYMMDD < 19000001) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateYYYYMMDD);
	if (EndDateYYYYMMDD < 19000001) EndDateYYYYMMDD = ExcelDateToCDate(EndDateYYYYMMDD);
	if (PayDateYYYYMMDD < 19000001) PayDateYYYYMMDD = ExcelDateToCDate(PayDateYYYYMMDD);
	double T = ((double)DayCountAtoB(PriceDateYYYYMMDD, EndDateYYYYMMDD)) / 365.0;
	double r = Interpolate_Linear(term_rate, rate, nrate, T);

	double TPAY = ((double)DayCountAtoB(PriceDateYYYYMMDD, PayDateYYYYMMDD)) / 365.0;
	double TEND_to_TPAY = ((double)DayCountAtoB(EndDateYYYYMMDD, PayDateYYYYMMDD)) / 365.0;
	double fr = Calc_Forward_Rate(term_rate, rate, nrate, T, TPAY);
	double DF_TEND_to_TPAY = 1.0 / (1.0 + fr * TEND_to_TPAY);

	long i, j, ResultCode = 0;
	double MaxRate = 3.0;
	double MinRate = 0.0001;
	double TargetRate = MaxRate;
	double dblErrorRange = 0.00001;
	double CalcRate = 0.;
	double p;
	for (j = 0; j < 1000; j++)
	{
		if (Call0Put1Flag == 0) p = SimpleBSCall_With_Forward(F, X, T, r, TargetRate);
		else if (Call0Put1Flag == 1) p = SimpleBSPut_With_Forward(F, X, T, r, TargetRate);
		else p = 0.5*(SimpleBSCall_With_Forward(F, X, T, r, TargetRate) + SimpleBSPut_With_Forward(F, X, T, r, TargetRate));
		CalcRate = p - OptPrice;
		if (fabs(CalcRate ) < dblErrorRange) break;
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
	if (j < 1000) return ResultCode;
	else return -1;
}

double SimpleBSPut(double S, double X, double r_drift, double T, double d, double r_disc, double Sigma)
{
	double d1 = (log(S / X) + (r_drift + 0.5 * Sigma * Sigma) * T) / (Sigma * sqrt(T));
	double d2 = d1 - Sigma * sqrt(T);
	return -S * exp(-d * T) * CDF_N(-d1) + X * exp(-r_disc * T) * CDF_N(-d2);
}


double CalcMu(double b, double Sigma)
{
	return (b - 0.5 * Sigma * Sigma) / (Sigma * Sigma);
}

double CalcLambda(double mu, double r, double Sigma)
{
	return sqrt(mu * mu + 2.0 * r / (Sigma * Sigma));
}

double CalcZ(double H, double K, double Sigma, double T, double Lambda)
{
	return log(H / K) / (Sigma * sqrt(T)) + Lambda * Sigma * sqrt(T);
}

double CalcX1(double S, double K, double Sigma, double T, double Mu)
{
	return log(S / K) / (Sigma * sqrt(T)) + (1.0 + Mu) * Sigma * sqrt(T);
}

double CalcX2(double S, double H, double Sigma, double T, double Mu)
{
	return log(S / H) / (Sigma * sqrt(T)) + (1.0 + Mu) * Sigma * sqrt(T);
}

double CalcY1(double S, double H, double K, double Sigma, double T, double Mu)
{
	return log(H * H / (S * K)) / (Sigma * sqrt(T)) + (1.0 + Mu) * Sigma * sqrt(T);
}

double CalcY2(double S, double H, double Sigma, double T, double Mu)
{
	return log(H / S) / (Sigma * sqrt(T)) + (1.0 + Mu) * Sigma * sqrt(T);
}

double CalcA(double phi, double S, double b, double T, double x1, double X, double r, double Sigma)
{
	return phi * S * exp(-(b-r) * T) * CDF_N(phi * x1) - phi * X * exp(-r * T) * CDF_N(phi * x1 - phi * Sigma * sqrt(T));
}

double CalcB(double phi, double S, double b, double T, double x2, double K, double r, double Sigma)
{
	return phi * S * exp(-(b-r) * T) * CDF_N(phi * x2) - phi * K * exp(-r * T) * CDF_N(phi * x2 - phi * Sigma * sqrt(T));
}

double CalcC(double phi, double S, double b, double T, double H, double mu, double n, double y1, double K, double r, double Sigma)
{
	return phi * S * exp(-(b-r) * T) * pow(H / S, 2 * (mu + 1.0)) * CDF_N(n * y1) - phi * K * exp(-r * T) * pow(H / S, 2.0 * mu) * CDF_N(n * y1 - n * Sigma * sqrt(T));
}

double CalcD(double phi, double S, double b, double T, double H, double mu, double n, double y2, double K, double r, double Sigma)
{
	return phi * S * exp(-(b-r) * T) * pow(H / S, 2 * (mu + 1.0)) * CDF_N(n * y2) - phi * K * exp(-r * T) * pow(H / S, 2.0 * mu) * CDF_N(n * y2 - n * Sigma * sqrt(T));
}

double CalcE(double Reb, double r, double T, double n, double x2, double Sigma, double H, double S, double mu, double y2)
{
	return Reb * exp(-r * T) * (CDF_N(n * x2 - n * Sigma * sqrt(T)) - pow(H / S, 2.0 * mu) * CDF_N(n * y2 - n * sqrt(T)));
}

double CalcF(double Reb, double H, double S, double mu, double Lambda, double n, double z, double Sigma, double T)
{
	return Reb * (pow(H / S, mu + Lambda) * CDF_N(n * z) + pow(H / S, mu - Lambda) * CDF_N(n * z - 2.0 * n * Lambda * Sigma * sqrt(T)));
}

double C_out(double n, double x1, double x2, double y1, double y2, double CalcA, double CalcB, double CalcC, double CalcD, double S, double X, double H)
{
	double Co;
	if (n == 1)
	{
		if (X > H) Co = CalcA - CalcC;
		else Co = CalcB - CalcD;
	}
	else
	{
		if (X > H) Co = 0;
		else Co = CalcA - CalcB + CalcC - CalcD;
	}
	return Co;
}

double P_out(double n, double x1, double x2, double y1, double y2, double CalcA, double CalcB, double CalcC, double CalcD, double S, double X, double H)
{
	double Po;
	if (n == 1)
	{
		if (X > H) Po = CalcA -CalcB+ CalcC-CalcD;
		else Po = 0.;
	}
	else
	{
		if (X > H) Po = CalcB- CalcD;
		else Po = CalcA - CalcC;
	}
	return Po;
}


double Call_Down(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig
)
{
	long i, j;
	double b;
	if (DiscreteDivFlag == 1) b = r_ref - rho_fx * fxvol * sig;
	else b = r_ref - rho_fx * fxvol * sig - div;
	double phi, n;
	phi = 1; // Call 1 Put -1
	n = 1;	 // Down 1 Up -1

	double x1, x2, y1, y2, z, mu, lambda;	
	double Sigma = sig;	
	double r = r_disc;
	if (DiscreteDivFlag == 1)
	{
		S = (S -div);
	}

	mu = CalcMu(b, Sigma);
	lambda = CalcLambda(mu, r, Sigma);
	z = CalcZ(H, X, Sigma, T, lambda);
	x1 = CalcX1(S, X, Sigma, T, mu);
	x2 = CalcX2(S, H, Sigma, T, mu);
	y1 = CalcY1(S, H, X, Sigma, T, mu);
	y2 = CalcY2(S, H, Sigma, T, mu);

	double A, B, C, D, E, F;
	E = 0.;
	F = 0.;

	A = CalcA(phi, S, b, T, x1, X, r, Sigma);
	B = CalcB(phi, S, b, T, x2, X, r, Sigma);
	C = CalcC(phi, S, b, T, H, mu, n, y1, X, r, Sigma);
	D = CalcD(phi, S, b, T, H, mu, n, y2, X, r, Sigma);

	double c_di, c, c_do, d1, d2;
	if (X > H) c_do = A - C + F;
	else c_do = B - D + F;

	double resultvalue;
	double bscall;
	if (in0out1flag == 0)
	{
		if (DiscreteDivFlag == 1) bscall = SimpleBSCall(S, X, b, T, 0., r, Sigma);
		else bscall = SimpleBSCall(S, X, b, T, div, r, Sigma);
		c_di = bscall - c_do;
		resultvalue = c_di;
	}
	else
	{
		resultvalue = c_do;
	}	

	return resultvalue;
}

double Call_Up(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig
)
{
	long i, j;
	double b;
	if (DiscreteDivFlag == 1) b = r_ref - rho_fx * fxvol * sig;
	else b = r_ref - rho_fx * fxvol * sig - div;
	double phi, n;
	phi = 1; // Call 1 Put -1
	n = 1;	 // Down 1 Up -1

	double x1, x2, y1, y2, z, mu, lambda;
	double Sigma = sig;
	double r = r_disc;
	if (DiscreteDivFlag == 1)
	{
		S = (S - div);
	}

	mu = CalcMu(b, Sigma);
	lambda = CalcLambda(mu, r, Sigma);
	z = CalcZ(H, X, Sigma, T, lambda);
	x1 = CalcX1(S, X, Sigma, T, mu);
	x2 = CalcX2(S, H, Sigma, T, mu);
	y1 = CalcY1(S, H, X, Sigma, T, mu);
	y2 = CalcY2(S, H, Sigma, T, mu);
	double A, B, C, D, E, F;
	E = 0.;
	F = 0.;

	A = CalcA(phi, S, b, T, x1, X, r, Sigma);
	B = CalcB(phi, S, b, T, x2, X, r, Sigma);
	C = CalcC(phi, S, b, T, H, mu, n, y1, X, r, Sigma);
	D = CalcD(phi, S, b, T, H, mu, n, y2, X, r, Sigma);

	double c_ui, c, c_uo, d1, d2;
	if (X > H) c_uo = F;
	else c_uo = A-B+C-D+F;

	double resultvalue;
	double bscall;
	if (in0out1flag == 0)
	{
		if (DiscreteDivFlag == 1) bscall = SimpleBSCall(S, X, b, T, 0., r, Sigma);
		else bscall = SimpleBSCall(S, X, b, T, div, r, Sigma);
		c_ui = bscall - c_uo;
		resultvalue = c_ui;
	}
	else
	{
		resultvalue = c_uo;
	}
	return resultvalue;
}

double Put_Up(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig
)
{
	long i, j;
	double b;
	if (DiscreteDivFlag == 1) b = r_ref - rho_fx * fxvol * sig;
	else b = r_ref - rho_fx * fxvol * sig - div;
	double phi, n;
	phi = 1; // Call 1 Put -1
	n = 1;	 // Down 1 Up -1

	double x1, x2, y1, y2, z, mu, lambda;
	double Sigma = sig;
	double r = r_disc;
	if (DiscreteDivFlag == 1)
	{
		S = (S - div);
	}

	mu = CalcMu(b, Sigma);
	lambda = CalcLambda(mu, r, Sigma);
	z = CalcZ(H, X, Sigma, T, lambda);
	x1 = CalcX1(S, X, Sigma, T, mu);
	x2 = CalcX2(S, H, Sigma, T, mu);
	y1 = CalcY1(S, H, X, Sigma, T, mu);
	y2 = CalcY2(S, H, Sigma, T, mu);
	double A, B, C, D, E, F;
	E = 0.;
	F = 0.;

	A = CalcA(phi, S, b, T, x1, X, r, Sigma);
	B = CalcB(phi, S, b, T, x2, X, r, Sigma);
	C = CalcC(phi, S, b, T, H, mu, n, y1, X, r, Sigma);
	D = CalcD(phi, S, b, T, H, mu, n, y2, X, r, Sigma);
	double c, p_ui, p_uo, d1, d2, p;

	if (X > H) p_uo = B-D+F;
	else p_uo = A - C+F;

	double resultvalue;
	double bsput;
	if (in0out1flag == 0)
	{
		if (DiscreteDivFlag == 1) bsput = SimpleBSPut(S, X, b, T, 0., r, Sigma);
		else bsput = SimpleBSPut(S, X, b, T, div, r, Sigma);
		p_ui = bsput - p_uo;
		resultvalue = p_ui;
	}
	else
	{
		resultvalue = p_uo;
	}

	return resultvalue;
}


double Put_Down(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig
)
{
	long i, j;
	double b;
	if (DiscreteDivFlag == 1) b = r_ref - rho_fx * fxvol * sig;
	else b = r_ref - rho_fx * fxvol * sig - div;
	double phi, n;
	phi = 1; // Call 1 Put -1
	n = 1;	 // Down 1 Up -1

	double x1, x2, y1, y2, z, mu, lambda;
	double Sigma = sig;
	double r = r_disc;
	if (DiscreteDivFlag == 1)
	{
		S = (S - div);
	}

	mu = CalcMu(b, Sigma);
	lambda = CalcLambda(mu, r, Sigma);
	z = CalcZ(H, X, Sigma, T, lambda);
	x1 = CalcX1(S, X, Sigma, T, mu);
	x2 = CalcX2(S, H, Sigma, T, mu);
	y1 = CalcY1(S, H, X, Sigma, T, mu);
	y2 = CalcY2(S, H, Sigma, T, mu);
	double A, B, C, D, E, F;
	E = 0.;
	F = 0.;

	A = CalcA(phi, S, b, T, x1, X, r, Sigma);
	B = CalcB(phi, S, b, T, x2, X, r, Sigma);
	C = CalcC(phi, S, b, T, H, mu, n, y1, X, r, Sigma);
	D = CalcD(phi, S, b, T, H, mu, n, y2, X, r, Sigma);
	double c, p_di, p_do, d1, d2, p;

	double resultvalue;
	if (X > H) p_do = A-B +C- D + F;
	else p_do = F;

	double bsput;
	if (in0out1flag == 0)
	{
		if (DiscreteDivFlag == 1) bsput = SimpleBSPut(S, X, b, T, 0., r, Sigma);
		else bsput = SimpleBSPut(S, X, b, T, div, r, Sigma);
		p_di = bsput - p_do;
		resultvalue = p_di;
	}
	else
	{
		resultvalue = p_do;
	}

	return resultvalue;
}

double BarrierOptionDelta(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	double (*funcs)(long, double, double, double, double, double, double, double, double, long, double, double)
)
{
	double Su = S * 1.01;
	double Sd = S * 0.99;
	double dS = S * 0.01;
	double Pu, Pd;
	Pu = funcs(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	Pd = funcs(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	return (Pu - Pd) / (2.0 * dS);
}

double BarrierOptionDelta(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	long ProductFlag			// 0 Call Down, Call Up, Put Down, Put Up
)
{
	double Su = S * 1.01;
	double Sd = S * 0.99;
	double dS = S * 0.01;
	double Pu, Pd;
	if (ProductFlag == 0)
	{
		Pu = Call_Down(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Down(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 1)
	{
		Pu = Call_Up(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Up(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 2)
	{
		Pu = Put_Down(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Down(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else
	{
		Pu = Put_Up(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Up(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}

	return (Pu - Pd) / (2.0 * dS);
}

double BarrierOptionGamma(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	double (*funcs)(long, double, double, double, double, double, double, double, double, long, double, double)
)
{
	double Su = S * 1.01;
	double Sd = S * 0.99;
	double dS = S * 0.01;
	double Pu, Pd, P;
	Pu = funcs(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	Pd = funcs(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	P = funcs(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	return (Pu + Pd -2.0 * P) / (dS * dS);
}

double BarrierOptionGamma(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	long ProductFlag			// 0 Call Down, Call Up, Put Down, Put Up
)
{
	double Su = S * 1.01;
	double Sd = S * 0.99;
	double dS = S * 0.01;
	double Pu, Pd, P;
	if (ProductFlag == 0)
	{
		Pu = Call_Down(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Down(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		P = Call_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 1)
	{
		Pu = Call_Up(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Up(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		P = Call_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 2)
	{
		Pu = Put_Down(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Down(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		P = Put_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else
	{
		Pu = Put_Up(in0out1flag, Su, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Up(in0out1flag, Sd, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		P = Put_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}

	return (Pu + Pd - 2.0 * P) / (dS * dS);
}

double BarrierOptionVega(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	double (*funcs)(long, double, double, double, double, double, double, double, double, long, double, double)
)
{
	double sigu = sig + 0.01;
	double sigd = max(sig - 0.01,0.00001);
	double dsig = 0.5 * (sigu - sigd);
	double Pu, Pd;
	Pu = funcs(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigu);
	Pd = funcs(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigd);
	return (Pu - Pd) / (2.0 );
}

double BarrierOptionVega(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	long ProductFlag			// 0 Call Down, Call Up, Put Down, Put Up
)
{
	double sigu = sig + 0.01;
	double sigd = max(sig - 0.01, 0.00001);
	double dsig = 0.5 * (sigu - sigd);
	double Pu, Pd;

	if (ProductFlag == 0)
	{
		Pu = Call_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigu);
		Pd = Call_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigd);
	}
	else if (ProductFlag == 1)
	{
		Pu = Call_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigu);
		Pd = Call_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigd);
	}
	else if (ProductFlag == 2)
	{
		Pu = Put_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigu);
		Pd = Put_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigd);
	}
	else
	{
		Pu = Put_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigu);
		Pd = Put_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sigd);
	}
	return (Pu - Pd) / (2.0);
}

double BarrierOptionRho(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	double (*funcs)(long, double, double, double, double, double, double, double, double, long, double, double)
)
{
	double Pu, Pd;
	Pu = funcs(in0out1flag, S, X, H, T, r_disc + 0.01, r_ref+0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	Pd = funcs(in0out1flag, S, X, H, T, r_disc -0.01, r_ref-0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	return (Pu - Pd) / (2.0);
}

double BarrierOptionRho(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	double r_disc,				// 할인이자율
	double r_ref,				// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	long ProductFlag			// 0 Call Down, Call Up, Put Down, Put Up
)
{
	double Pu, Pd;

	if (ProductFlag == 0)
	{
		Pu = Call_Down(in0out1flag, S, X, H, T, r_disc + 0.01, r_ref + 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Down(in0out1flag, S, X, H, T, r_disc - 0.01, r_ref- 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 1)
	{
		Pu = Call_Up(in0out1flag, S, X, H, T, r_disc + 0.01, r_ref + 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Up(in0out1flag, S, X, H, T, r_disc - 0.01, r_ref - 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 2)
	{
		Pu = Put_Down(in0out1flag, S, X, H, T, r_disc + 0.01, r_ref + 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Down(in0out1flag, S, X, H, T, r_disc - 0.01, r_ref - 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else
	{
		Pu = Put_Up(in0out1flag, S, X, H, T, r_disc + 0.01, r_ref + 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Up(in0out1flag, S, X, H, T, r_disc - 0.01, r_ref - 0.01, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	return (Pu - Pd) / (2.0);
}

double BarrierOptionTheta(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	long n_rcv_disc,
	double *rcv_disc_term,		
	double *rcv_disc_rate,		// 할인이자율
	
	long n_rcv_ref,				
	double *rcv_ref_term,	
	double *rcv_ref_rate,		// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	double (*funcs)(long, double, double, double, double, double, double, double, double, long, double, double)
)
{
	double T_u = T + 1.0 / 365.0;
	double T_d = max(T - 1.0 / 365.0,0.00001);
	double dT = 0.5 * (T_u - T_d);
	double Pu, Pd;

	double r_disc_Tu = Interpolate_Linear(rcv_disc_term, rcv_disc_rate, n_rcv_disc, T_u);
	double r_disc_Td = Interpolate_Linear(rcv_disc_term, rcv_disc_rate, n_rcv_disc, T_d);

	double r_ref_Tu = Interpolate_Linear(rcv_ref_term, rcv_ref_rate, n_rcv_ref, T_u);
	double r_ref_Td = Interpolate_Linear(rcv_ref_term, rcv_ref_rate, n_rcv_ref, T_d);

	Pu = funcs(in0out1flag, S, X, H, T_u, r_disc_Tu, r_ref_Tu, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	Pd = funcs(in0out1flag, S, X, H, T_d, r_disc_Td, r_ref_Td, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	return -(Pu - Pd) / (2.0);
}

double BarrierOptionTheta(
	long in0out1flag,			// 0 : Down And In, 1: Down And Out 
	double S,					// 현재주가
	double X,					// 행사가격
	double H,					// 배리어
	double T,					// 만기
	long n_rcv_disc,
	double* rcv_disc_term,
	double* rcv_disc_rate,		// 할인이자율

	long n_rcv_ref,
	double* rcv_ref_term,
	double* rcv_ref_rate,		// 레퍼이자율
	double rho_fx,				// fx, rf 상관계수
	double fxvol,				// fxvol
	long DiscreteDivFlag,		// 이산배당Flag
	double div,					// 배당수익률 또는 이산배당의 현재가치
	double sig,
	long ProductFlag			// 0 Call Down, Call Up, Put Down, Put Up
)
{
	double T_u = T + 1.0 / 365.0;
	double T_d = max(T - 1.0 / 365.0, 0.00001);
	double dT = 0.5 * (T_u - T_d);
	double Pu, Pd;

	double r_disc_Tu = Interpolate_Linear(rcv_disc_term, rcv_disc_rate, n_rcv_disc, T_u);
	double r_disc_Td = Interpolate_Linear(rcv_disc_term, rcv_disc_rate, n_rcv_disc, T_d);

	double r_ref_Tu = Interpolate_Linear(rcv_ref_term, rcv_ref_rate, n_rcv_ref, T_u);
	double r_ref_Td = Interpolate_Linear(rcv_ref_term, rcv_ref_rate, n_rcv_ref, T_d);

	if (ProductFlag == 0)
	{
		Pu = Call_Down(in0out1flag, S, X, H, T_u, r_disc_Tu, r_ref_Tu, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Down(in0out1flag, S, X, H, T_d, r_disc_Td, r_ref_Td, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 1)
	{
		Pu = Call_Up(in0out1flag, S, X, H, T_u, r_disc_Tu, r_ref_Tu, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Call_Up(in0out1flag, S, X, H, T_d, r_disc_Td, r_ref_Td, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else if (ProductFlag == 2)
	{
		Pu = Put_Down(in0out1flag, S, X, H, T_u, r_disc_Tu, r_ref_Tu, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Down(in0out1flag, S, X, H, T_d, r_disc_Td, r_ref_Td, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}
	else
	{
		Pu = Put_Up(in0out1flag, S, X, H, T_u, r_disc_Tu, r_ref_Tu, rho_fx, fxvol, DiscreteDivFlag, div, sig);
		Pd = Put_Up(in0out1flag, S, X, H, T_d, r_disc_Td, r_ref_Td, rho_fx, fxvol, DiscreteDivFlag, div, sig);
	}

	return -(Pu - Pd) / (2.0);
}

long BSBarrierOption(
	long TypeFlag,			// Option Type: 1이면 콜, 2이면 풋
	double S0,				// 기초자산 현재가
	double X,				// 행사가격
	double H,				// 배리어
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	double T_Ref,
	double T_Pay,
	double* ResultPrice,
	long down0up1flag,
	long in0out1flag
)
{
	long i = 0;
	long N;
	double dvd;
	double vol;
	double fxvol;
	double r, r_disc, Rf_Quanto, frate;
	double Price, Delta, Gamma, Vega, Theta, Rho;

	if (T_Ref <= 0.0) T_Ref = 0.00001;

	double T_Mat_to_Pay = 0.0, r_Mat_to_Pay = 0.0, DF_Mat_to_Pay = 1.0;
	if (T_Ref < T_Pay)
	{
		T_Mat_to_Pay = T_Pay - T_Ref;
		r_Mat_to_Pay = Calc_Forward_Rate(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), T_Ref, T_Pay);
		DF_Mat_to_Pay = 1.0 / (1.0 + r_Mat_to_Pay * T_Mat_to_Pay);
	}

	if (DivTypeFlag == 0)
	{
		dvd = DivCurve->Rate[0];
	}
	else if (DivTypeFlag == 1)
	{
		dvd = DivCurve->Interpolated_Rate(T_Ref);
	}
	else if (DivTypeFlag == 2)
	{
		N = 0;
		for (i = 0; i < DivCurve->nterm(); i++)
		{
			if (DivCurve->Term[i] > T_Ref) break;
			N += 1;
		}
		dvd = 1.0 / T_Ref * Sumation(N, DivCurve->Rate) / S0;
	}
	vol = VolMat->Calc_Implied_Volatility(T_Ref, S0 / X);
	fxvol = FXVolCurve->Interpolated_Rate(T_Ref);
	r = RefCurve->Interpolated_Rate(T_Ref);
	r_disc = DiscCurve->Interpolated_Rate(T_Ref);
	Rf_Quanto = r - fxvol * vol * QuantoCorr;
	// 
	long DiscreteDivFlag = 0;
	double discdivsum = 0.0;
	if (DivTypeFlag == 2)
	{
		DiscreteDivFlag = 1;

	}

	if (TypeFlag == 1)
	{
		if (down0up1flag == 0)
		{
			Price = Call_Down(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol);
			Delta = BarrierOptionDelta(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)0);
			Gamma = BarrierOptionGamma(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)0);
			Theta = BarrierOptionTheta(in0out1flag, S0, X, H, T_Ref, DiscCurve->nterm(), DiscCurve->Term, DiscCurve->Rate, RefCurve->nterm(), RefCurve->Term, RefCurve->Rate, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)0);
			Vega = BarrierOptionVega(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)0);
			Rho = BarrierOptionRho(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)0);
		}
		else
		{
			Price = Call_Up(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol);
			Delta = BarrierOptionDelta(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)1);
			Gamma = BarrierOptionGamma(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)1);
			Theta = BarrierOptionTheta(in0out1flag, S0, X, H, T_Ref, DiscCurve->nterm(), DiscCurve->Term, DiscCurve->Rate, RefCurve->nterm(), RefCurve->Term, RefCurve->Rate, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)1);
			Vega = BarrierOptionVega(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)1);
			Rho = BarrierOptionRho(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)1);
		}
	}
	else
	{
		if (down0up1flag == 0)
		{
			Price = Put_Down(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol);
			Delta = BarrierOptionDelta(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)2);
			Gamma = BarrierOptionGamma(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)2);
			Theta = BarrierOptionTheta(in0out1flag, S0, X, H, T_Ref, DiscCurve->nterm(), DiscCurve->Term, DiscCurve->Rate, RefCurve->nterm(), RefCurve->Term, RefCurve->Rate, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)2);
			Vega = BarrierOptionVega(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)2);
			Rho = BarrierOptionRho(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)2);
		}
		else
		{
			Price = Put_Up(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol);
			Delta = BarrierOptionDelta(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)3);
			Gamma = BarrierOptionGamma(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)3);
			Theta = BarrierOptionTheta(in0out1flag, S0, X, H, T_Ref, DiscCurve->nterm(), DiscCurve->Term, DiscCurve->Rate, RefCurve->nterm(), RefCurve->Term, RefCurve->Rate, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)3);
			Vega = BarrierOptionVega(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)3);
			Rho = BarrierOptionRho(in0out1flag, S0, X, H, T_Ref, r_disc, r, QuantoCorr, fxvol, DiscreteDivFlag, dvd, vol, (long)3);
		}
	}
	ResultPrice[0] = Price * DF_Mat_to_Pay;
	ResultPrice[1] = Delta;
	ResultPrice[2] = Gamma;
	ResultPrice[3] = Vega;
	ResultPrice[4] = Theta;
	ResultPrice[5] = Rho;
	return 1;
}

long BSOption(
	long TypeFlag,			// Option Type: 1이면 콜, 2이면 풋
	double S0,				// 기초자산 현재가
	double X,				// 행사가격
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	double T_Ref,
	double T_Pay,
	double* ResultPrice
)
{
	long i;
	long N;
	double dvd;
	double vol;
	double fxvol;
	double r, r_disc, Rf_Quanto, frate;
	double Price, Delta, Gamma, Vega, Theta, Rho;

	if (DivTypeFlag == 0)
	{
		dvd = DivCurve->Rate[0];
	}
	else if (DivTypeFlag == 1)
	{
		dvd = DivCurve->Interpolated_Rate(T_Ref);
	}
	else if (DivTypeFlag == 2)
	{
		N = 0;
		for (i = 0; i < DivCurve->nterm(); i++)
		{
			if (DivCurve->Term[i] > T_Ref) break;
			N += 1;
		}
		dvd = 1.0/T_Ref * Sumation(N, DivCurve->Rate) / S0;
	}
	vol = VolMat->Calc_Implied_Volatility(T_Ref, S0 / X);
	fxvol = FXVolCurve->Interpolated_Rate(T_Ref);
	r = RefCurve->Interpolated_Rate(T_Ref);
	r_disc = DiscCurve->Interpolated_Rate(T_Pay);
	Rf_Quanto = r - fxvol * vol * QuantoCorr;

	double d1 = (log(S0 / X) + (r - dvd + 0.5 * vol * vol) * T_Ref) / (vol * sqrt(T_Ref));
	double d2 = d1 - vol * sqrt(T_Ref);

	if (T_Ref <= 0.0)
	{
		if (TypeFlag == 1)
		{
			Price = max(0, S0 - X) * exp(-r_disc * T_Pay);
			Delta = 1.0;
			Gamma = 0.0;
			Vega = 0.0;
			Theta = 0.0;
			Rho = 0.0;
		}
		else
		{
			Price = max(0, X - S0) * exp(-r_disc * T_Pay);
			Delta = -1.0;
			Gamma = 0.0;
			Vega = 0.0;
			Theta = 0.0;
			Rho = 0.0;
		}
	}
	else
	{
		if (TypeFlag == 1) 
		{ //call
			if (X <= 0.0)
			{
				Price = S0 * exp(-dvd * T_Ref) - X * exp(-Rf_Quanto * T_Ref);
				Delta = exp(-dvd * T_Ref);
				Gamma = 0.0;
				Vega = 0.0;
				Theta = dvd * S0 * exp(-dvd * T_Ref) - r * X * exp(-r * T_Ref);
				Rho = X * T_Ref * exp(-r * T_Ref);
			}
			else
			{
				Price = S0 * exp(-dvd * T_Ref) * CDF_N(d1) - X * exp(-Rf_Quanto * T_Ref) * CDF_N(d2);
				Delta = exp(-dvd * T_Ref) * CDF_N(d1);
				Gamma = exp(-dvd * T_Ref) * PDF_N(d1) / (S0 * vol * sqrt(T_Ref));
				Vega = exp(-dvd * T_Ref) * S0 * sqrt(T_Ref) * PDF_N(d1);
				Theta = -0.5 * S0 * PDF_N(d1) * vol * exp(-dvd * T_Ref) / sqrt(T_Ref) + dvd * S0 * CDF_N(d1) * exp(-dvd * T_Ref) - r * X * exp(-r * T_Ref) * CDF_N(d2);
				Rho = X * T_Ref * exp(-r * T_Ref) * CDF_N(d2);
			}
		}
		else
		{	// put
			if (X <= 0.0)
			{
				Price = 0.0;
				Delta = 0.0;
				Gamma = 0.0;
				Vega = 0.0;
				Theta = 0.0;
				Rho = 0.0;
			}
			else
			{
				Price = -S0 * exp(-dvd * T_Ref) * CDF_N(-d1) + X * exp(-Rf_Quanto * T_Ref) * CDF_N(-d2);
				Delta = exp(-dvd * T_Ref) * (CDF_N(d1) - 1.0);
				Gamma = exp(-dvd * T_Ref) * PDF_N(d1) / (S0 * vol * sqrt(T_Ref));
				Vega = exp(-dvd * T_Ref) * S0 * sqrt(T_Ref) * PDF_N(d1);
				Theta = 0.5 * S0 * PDF_N(d1) * vol * exp(-dvd * T_Ref) / sqrt(T_Ref) - dvd * S0 * CDF_N(-d1) * exp(-dvd * T_Ref) + r * X * exp(-r * T_Ref) * CDF_N(-d2);
				Rho = -X * T_Ref * exp(-r * T_Ref) * CDF_N(-d2);
			}
		}
		if (T_Pay - T_Ref <= 0.0) frate = 0.0;
		else frate = Calc_Forward_Rate(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), T_Ref, T_Pay);
		Price = Price / (1.0 + frate * (T_Pay - T_Ref));
		Delta = Delta / (1.0 + frate * (T_Pay - T_Ref));
		Gamma = Gamma / (1.0 + frate * (T_Pay - T_Ref));
		Vega = Vega / (1.0 + frate * (T_Pay - T_Ref))/100.0;
		Theta = Theta / (1.0 + frate * (T_Pay - T_Ref)) * 1.0/ 365.0;
		Rho = Rho / (1.0 + frate * (T_Pay - T_Ref))/100.0;
	}
	ResultPrice[0] = Price;
	ResultPrice[1] = Delta;
	ResultPrice[2] = Gamma;
	ResultPrice[3] = Vega;
	ResultPrice[4] = Theta;
	ResultPrice[5] = Rho;
	return 1;
}

long BSDigitalOption(
	long TypeFlag,			// Option Type: 1이면 콜, 2이면 풋
	double S0,				// 기초자산 현재가
	double X,				// 행사가격
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	double T_Ref,
	double T_Pay,
	double* ResultPrice
)
{
	long i;
	long N;
	double dvd;
	double vol;
	double fxvol;
	double r, r_disc, Rf_Quanto, frate;
	double Price, Delta, Gamma, Vega, Theta, Rho;
	double fix_amt = 1.0;

	if (DivTypeFlag == 0)
	{
		dvd = DivCurve->Rate[0];
	}
	else if (DivTypeFlag == 1)
	{
		dvd = DivCurve->Interpolated_Rate(T_Ref);
	}
	else if (DivTypeFlag == 2)
	{
		N = 0;
		for (i = 0; i < DivCurve->nterm(); i++)
		{
			if (DivCurve->Term[i] > T_Ref) break;
			N += 1;
		}
		dvd = 1.0 / T_Ref * Sumation(N, DivCurve->Rate) / S0;
	}
	vol = VolMat->Calc_Implied_Volatility(T_Ref, S0 / X);
	fxvol = FXVolCurve->Interpolated_Rate(T_Ref);
	r = RefCurve->Interpolated_Rate(T_Ref);
	r_disc = DiscCurve->Interpolated_Rate(T_Pay);
	Rf_Quanto = r - fxvol * vol * QuantoCorr;

	double d1 = (log(S0 / X) + (r - dvd + 0.5 * vol * vol) * T_Ref) / (vol * sqrt(T_Ref));
	double d2 = d1 - vol * sqrt(T_Ref);
	double theta_d2 = -(r - dvd - 0.5 * vol * vol) / (vol * sqrt(T_Ref)) + 0.5 * d2 / T_Ref;
	if (T_Ref <= 0.0)
	{
		if (TypeFlag == 1)
		{
			if (S0 >= X) Price = fix_amt * exp(-r_disc * T_Pay);
			else Price = 0.0;

			Delta = 0.0;
			Gamma = 0.0;
			Vega = 0.0;
			Theta = 0.0;
			Rho = 0.0;
		}
		else
		{
			if (S0 <= X) Price = fix_amt * exp(-r_disc * T_Pay);
			else Price = 0.0;

			Delta = 0.0;
			Gamma = 0.0;
			Vega = 0.0;
			Theta = 0.0;
			Rho = 0.0;
		}
	}
	else
	{
		if (TypeFlag == 1)
		{ //call
			if (X <= 0.0)
			{
				Price = fix_amt * exp(-r_disc * T_Ref);
				Delta = 0.0;
				Gamma = 0.0;
				Vega = 0.0;
				Theta = dvd * S0 * exp(-dvd * T_Ref) - r * X * exp(-r * T_Ref);
				Rho = X * T_Ref * exp(-r * T_Ref);
			}
			else
			{
				Price = fix_amt * exp(-r_disc * T_Pay) * CDF_N(d2) ;
				Delta = fix_amt * exp(-r_disc * T_Pay) * PDF_N(d2) / (vol * sqrt(T_Ref) * S0);
				Gamma = -fix_amt * exp(-r_disc * T_Pay) * PDF_N(d2) / (vol * vol * (T_Ref)*S0 * S0) * (d2 + (vol * sqrt(T_Ref)));
				Vega = -fix_amt * exp(-r_disc * T_Pay) * PDF_N(d2) * (sqrt(T_Ref) + d2 / vol);
				Theta = fix_amt * exp(-r_disc * T_Pay) * (Rf_Quanto * CDF_N(d2) + PDF_N(d2) * theta_d2);
				Rho = -fix_amt * exp(-r_disc * T_Pay) * (T_Ref * CDF_N(d2) - PDF_N(d2) * sqrt(T_Ref) / vol);
			}
		}
		else
		{	// put
			if (X <= 0.0)
			{
				Price = 0.0;
				Delta = 0.0;
				Gamma = 0.0;
				Vega = 0.0;
				Theta = 0.0;
				Rho = 0.0;
			}
			else
			{
				Price = fix_amt * exp(-r_disc * T_Pay) * CDF_N(-d2);
				Delta = -fix_amt * exp(-r_disc * T_Pay) * PDF_N(d2) / (vol * sqrt(T_Ref) * S0);
				Gamma = fix_amt*exp(-r_disc * T_Pay) * PDF_N(d2) / (vol * vol * (T_Ref)*S0 * S0) * (d2 + (vol * sqrt(T_Ref)));
				Vega = fix_amt* exp(-r_disc * T_Pay)* PDF_N(d2)* (sqrt(T_Ref) + d2 / vol);
				Theta = fix_amt * exp(-r_disc * T_Pay) * (Rf_Quanto * CDF_N(-d2) - PDF_N(d2) * theta_d2);
				Rho = -(fix_amt * (exp(-r_disc * T_Pay) * (PDF_N(d2) * sqrt(T_Ref) / vol - T_Ref * CDF_N(-1.0 * d2))));
			}
		}
		if (T_Pay - T_Ref <= 0.0) frate = 0.0;
		else frate = Calc_Forward_Rate(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), T_Ref, T_Pay);
		Price = Price / (1.0 + frate * (T_Pay - T_Ref));
		Delta = Delta / (1.0 + frate * (T_Pay - T_Ref));
		Gamma = Gamma / (1.0 + frate * (T_Pay - T_Ref));
		Vega = Vega / (1.0 + frate * (T_Pay - T_Ref)) / 100.0;
		Theta = Theta / (1.0 + frate * (T_Pay - T_Ref)) * 1.0 / 365.0;
		Rho = Rho / (1.0 + frate * (T_Pay - T_Ref)) / 100.0;
	}
	ResultPrice[0] = Price;
	ResultPrice[1] = Delta;
	ResultPrice[2] = Gamma;
	ResultPrice[3] = Vega;
	ResultPrice[4] = Theta;
	ResultPrice[5] = Rho;
	return 1;
}

long NextYYYYMM(long YYYY, long MM, long Freq)
{
	if (Freq == 1)
	{
		if (MM == 12) return (YYYY + 1) * 100 + 01;
		else return YYYY * 100 + (MM + 1);
	}
	else if (Freq == 2)
	{
		if (MM == 12) return (YYYY + 1) * 100 + 02;
		else if (MM == 11) return (YYYY + 1) * 100 + 01;
		else return YYYY * 100 + (MM + 2);
	}
	else if (Freq == 3)
	{
		if (MM == 12) return (YYYY + 1) * 100 + 03;
		else if (MM == 11) return (YYYY + 1) * 100 + 02;
		else if (MM == 10) return (YYYY + 1) * 100 + 01;
		else return YYYY * 100 + (MM + 3);
	}
	else if (Freq == 4)
	{
		if (MM == 12) return (YYYY + 1) * 100 + 04;
		else if (MM == 11) return (YYYY + 1) * 100 + 03;
		else if (MM == 10) return (YYYY + 1) * 100 + 02;
		else if (MM == 9) return (YYYY + 1) * 100 + 01;
		else return YYYY * 100 + (MM + 4);
	}
	else if (Freq == 6)
	{
		if (MM == 12) return (YYYY + 1) * 100 + 06;
		else if (MM == 11) return (YYYY + 1) * 100 + 05;
		else if (MM == 10) return (YYYY + 1) * 100 + 04;
		else if (MM == 9) return (YYYY + 1) * 100 + 03;
		else if (MM == 8) return (YYYY + 1) * 100 + 02;
		else if (MM == 7) return (YYYY + 1) * 100 + 01;
		else return YYYY * 100 + (MM + 6);
	}
	else
	{
		return (YYYY + 1) * 100 + MM;
	}
}

long MonthAdjust(long YYYYMMDD)
{
	long Year = YYYYMMDD / 10000;
	long Month = (YYYYMMDD - Year * 10000) / 100;
	long Day = (YYYYMMDD - Year * 10000 - Month * 100);
	long Days[13] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
	long Days_Leap[13] = { 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
	long Leap = LeapCheck(Year);
	long idx = 0;
	if (Month == 1) idx = 0;
	else idx = Month - 1;

	if (Leap == 1)
	{
		return min(YYYYMMDD, Year * 10000 + Month * 100 + Days_Leap[idx]);
	}
	else
	{
		return min(YYYYMMDD, Year * 10000 + Month * 100 + Days[idx]);
	}
}

DLLEXPORT(long) NSchedule_CommOpt(long StartDate, long EndDate, long FreqMonth)
{
	if (StartDate < 19000109) StartDate = ExcelDateToCDate(StartDate);
	if (EndDate < 19000109) EndDate = ExcelDateToCDate(EndDate);
	long i;

	long Year;
	long Month;

	long NMax = ((EndDate / 10000 - StartDate / 10000) + 2) * 12;
	long n;

	long YYYYMM;
	n = 0;
	for (i = 0; i < NMax; i++)
	{
		
		if (i == 0)
		{
			Year = StartDate / 10000;
			Month = (StartDate - Year * 10000) / 100;
		}
		else
		{
			Year = YYYYMM / 100;
			Month = YYYYMM - Year * 100;
		}

		if (Year * 100 + Month <= EndDate / 100)
		{
			n += 1;
		}
		else
		{
			break;
		}
		YYYYMM = NextYYYYMM(Year, Month, FreqMonth);
	}
	return n;
}

long Calc_PrevBD(long YYYYMMDD, long NHoliday, long*Holiday)
{
	long i, MOD07, TargetDay;
	TargetDay = YYYYMMDD;
	long ExlDate, TmpExcelDate, TmpYYYYMMDD, isholidayflag, issatursunday;
	ExlDate = CDateToExcelDate(YYYYMMDD);
	for (i = 0; i < 20; i++)
	{
		TmpExcelDate = ExlDate - i;
		TmpYYYYMMDD = ExcelDateToCDate(TmpExcelDate);
		MOD07 = TmpExcelDate % 7;
		if (MOD07 == 0 || MOD07 == 1) issatursunday = 1;
		else issatursunday = 0;

		if (isin(TmpYYYYMMDD, Holiday, NHoliday)) isholidayflag = 1;
		else isholidayflag = 0;

		if (issatursunday == 0 && isholidayflag == 0)
		{
			TargetDay = TmpYYYYMMDD;
			break;
		}
	}
	return TargetDay;
}

DLLEXPORT(long) MapLastFixingDate(long NForwardEnd, long* ForwardEnd, long HolidayFlag, long NBD_AfterFix, long* ResultFixingDate, long* ResultPayDate)
{
	long i, j;
	for (i = 0; i < NForwardEnd; i++) if (ForwardEnd[i] < 19000101) ForwardEnd[i] = ExcelDateToCDate(ForwardEnd[i]);
	long NHolidayArray; 
	long* HolidayArray; 
	long TempExcelDate, TempYYYYMMDD, MOD07, issatursunday, isholiday, n;
	if (HolidayFlag < 10)
	{
		NHolidayArray = Number_Holiday(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), HolidayFlag);
		HolidayArray = (long*)malloc(sizeof(long) * NHolidayArray);
		Mapping_Holiday_CType(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), HolidayFlag, NHolidayArray, HolidayArray);
	}
	else
	{
		long n1;
		long n2;
		long h1 = HolidayFlag / 10;
		long h2 = HolidayFlag - h1 * 10;
		n1 = Number_Holiday(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), h1);
		n2 = Number_Holiday(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), h2);
		NHolidayArray = n1 + n2;
		HolidayArray = (long*)malloc(sizeof(long) * NHolidayArray);
		Mapping_Holiday_CType(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), h1, n1, HolidayArray);
		Mapping_Holiday_CType(ForwardEnd[0] / 10000, (ForwardEnd[NForwardEnd - 1] / 10000 + 1), h2, n2, HolidayArray + n1);
		
	}

	for (i = 0; i < NForwardEnd; i++)
	{
		ResultFixingDate[i] = Calc_PrevBD(ForwardEnd[i], NHolidayArray, HolidayArray);
		if (NBD_AfterFix == 0)
		{
			ResultPayDate[i] = ResultFixingDate[i];
		}
		else
		{
			n = 0;
			for (j = 0; j < 30; j++)
			{
				if (j == 0) TempExcelDate = CDateToExcelDate(ResultFixingDate[i]) + 1;
				else TempExcelDate = TempExcelDate + 1;

				TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
				MOD07 = TempExcelDate % 7;
				if (MOD07 == 0 || MOD07 == 1) issatursunday = 1;
				else issatursunday = 0;

				if (isin(TempYYYYMMDD, HolidayArray, NHolidayArray)) isholiday = 1;
				else isholiday = 0;

				if (issatursunday == 0 && isholiday == 0) n += 1;
				if (n >= NBD_AfterFix)
				{
					break;
				}
			}
			ResultPayDate[i] = TempYYYYMMDD;
		}
	}
	free(HolidayArray);
	return 1;
}

DLLEXPORT(long) Malloc_Schedule_CommOpt(long StartDate, long EndDate, long DayStart, long DayEnd, long FreqMonth, long* StartDateArray, long* EndDateArray)
{
	if (StartDate < 19000109) StartDate = ExcelDateToCDate(StartDate);
	if (EndDate < 19000109) EndDate = ExcelDateToCDate(EndDate);
	long i;

	long Year;
	long Month;

	long NMax = ((EndDate / 10000 - StartDate / 10000) + 2) * 12;
	long n;

	long YYYYMM;
	n = 0;
	for (i = 0; i < NMax; i++)
	{

		if (i == 0)
		{
			Year = StartDate / 10000;
			Month = (StartDate - Year * 10000) / 100;
		}
		else
		{
			Year = YYYYMM / 100;
			Month = YYYYMM - Year * 100;
		}

		if (Year * 100 + Month <= EndDate / 100)
		{
			StartDateArray[n] = Year * 10000 + Month * 100 + DayStart;
			YYYYMM = NextYYYYMM(Year, Month, FreqMonth);
			if (DayStart < DayEnd && FreqMonth == 1) EndDateArray[n] = MonthAdjust(Year * 10000 + Month * 100 + DayEnd);
			else EndDateArray[n] = MonthAdjust(YYYYMM * 100 + DayEnd);

			n += 1;
		}
		else
		{
			//StartDateArray[n] = Year * 10000 + Month * 100 + DayStart;
			//YYYYMM = NextYYYYMM(Year, Month, FreqMonth);
			//if (DayStart > DayEnd) EndDateArray[n] = MonthAdjust(YYYYMM * 100 + DayEnd);
			//else EndDateArray[n] = MonthAdjust(Year * 10000 + Month * 100 + DayEnd);

			break;
		}
	}
	return 1;
}


double sumation_beta(long start_idx, long end_idx, double* Forward, double* Weight)
{
	long i;
	double m = 0.;
	for (i = start_idx; i <= end_idx; i++)
	{
		m += Forward[i] * Weight[i];
	}
	return m;
}

double Arithmetic_Asian_Opt_m1(long n, double* Weight, double* Forward)
{
	return sumation_beta(0, n - 1, Forward, Weight);
}

double Arithmetic_Asian_Opt_m2(long n, double* Forward, double* Weight, double* T, long nVol, double* TermVol, double* Vol)
{
	long i;
	double m2 = 0.;
	double b_i, b_j, e, sig, tau, value1, value2;

	value1 = 0.;
	for (i = 0 ; i <= n-1; i++)
	{
		tau = T[i];
		sig = Interpolate_Linear(TermVol, Vol, nVol, tau);
		e = exp(sig * sig * tau);

		b_i = Forward[i] * Weight[i];
		value1 += b_i* e* sumation_beta(i, n - 1, Forward, Weight);
	}
	value1 = 2.0 * value1;

	value2 = 0.;
	for (i = 0; i <= n - 1; i++)
	{
		tau = T[i];
		sig = Interpolate_Linear(TermVol, Vol, nVol, tau);
		e = exp(sig * sig * tau);

		b_i = Forward[i] * Weight[i];
		value2 += b_i * b_i * e;
	}
	m2 = value1 - value2;
	return m2;
}

double Arithmetic_Asian_Opt_m3(long n, double* Forward, double* Weight, double* T, long nVol, double* TermVol, double* Vol)
{
	long i, j;
	double m3 = 0.;
	double b_i, b_j, b_k, e_i, e_j, sig_i, tau_i, sig_j, tau_j, V1, V2, V3, V4;
	
	for (i = 0; i <= n - 1; i++)
	{
		tau_i = T[i];
		sig_i = Interpolate_Linear(TermVol, Vol, nVol, tau_i);
		e_i = exp(sig_i * sig_i * tau_i);

		b_i = Forward[i] * Weight[i];
		V1 = b_i * b_i * e_i;
		V2 = 3.0 * b_i * e_i * sumation_beta(i, n - 1, Forward, Weight);
		V3 = 0.0;
		V4 = 0.0;
		for (j = i; j <= n - 1; j++)
		{
			tau_j = T[j];
			sig_j = Interpolate_Linear(TermVol, Vol, nVol, tau_j);
			e_j = exp(sig_j * sig_j * tau_j);
			b_j = Forward[j] * Weight[j];
			V3 += 3.0 * b_j * b_j * e_j;


			V4 += 6.0 * b_j * e_j * sumation_beta(j, n - 1, Forward, Weight);
		}
		m3 += 2.0 * b_i * e_i * e_i * (V1 - V2 - V3 + V4);
	}

	return m3;
}

double Arithmetic_Asian_Option_Delta(long n, double* Forward, double* Weight, double* T, long nVol, double* TermVol, double* Vol, double r, double y1, double y11, double d1)
{
	long i, j, k;
	double delta_i, delta;
	double sumaFe, sumaF, v;
	delta = 0.;
	for (i = 0; i < n; i++)
	{
		sumaFe = 0.0;
		for (k = 0; k <= i - 1; k++)
		{
			v = Interpolate_Linear(TermVol, Vol, nVol, T[k]);
			sumaFe += Weight[k] * Forward[k] * exp(v * v * T[k]);
		}

		v = Interpolate_Linear(TermVol, Vol, nVol, T[i]);
		sumaF = 0.0;
		for (k = i; k <= n - 1; k++)
		{
			sumaF += Weight[k] * Forward[k] * exp(v * v * T[i]);
		}
		delta_i = Weight[i] * exp(-r * T[n-1]) * (CDF_N(d1) + y1 * PDF_N(d1) * y1 * y1 / (sqrt(log(y11 / (y1 * y1))) * y11) * ((sumaFe + sumaF) / y11 - 1.0 / y1));
		delta += delta_i;
	}
	return delta;
}

double Arithmetic_Asian_Option_Vega(long n, double* Forward, double* Weight, double* T, long nVol, double* TermVol, double* Vol, double r, double y1, double y11, double d1)
{
	long i, j;
	double vega_i, vega;
	double sumaF, aF_i, v;
	vega = 0.;
	for (i = 0; i < n; i++)
	{
		sumaF = 0.;
		for (j = i + 1; j <= n - 1; j++)
		{
			sumaF += 2.0 * Weight[j] * Forward[j];
		}
		aF_i = Weight[i] * Forward[i];
		v = Interpolate_Linear(TermVol, Vol, nVol, T[i]);
		vega_i = (sumaF + aF_i)* Weight[i] * Forward[i] * exp(v * v * T[i])* v* T[i] * exp(-r * T[n - 1])* (PDF_N(d1) / ((y11 / y1) * sqrt(log(y11 / (y1 * y1)))));
		vega += vega_i;
	}
	return vega;
}

double Arithmetic_Asian_Opt_Pricing(long n, double* Forward, double* Weight, double* T, long nVol, double* TermVol, double* Vol, double PrevCummulative_Weight,double Strike, double PrevAverage, long Call0Put1, double T_Option, long nRate, double* TermRate, double* Rate, double& delta, double& vega)
{
	double mu1, mu2, mu3;
	double m1, m2, m3;
	double value = 0.0;
	m1 = Arithmetic_Asian_Opt_m1(n, Weight, Forward);
	m2 = Arithmetic_Asian_Opt_m2(n, Forward, Weight, T, nVol, TermVol, Vol);
	m3 = Arithmetic_Asian_Opt_m3(n, Forward, Weight, T, nVol, TermVol, Vol);

	mu1 = m1;
	mu2 = m2 - mu1 * mu1;
	mu3 = m3 - 3.0 * mu1 * mu2 - mu1 * mu1 * mu1;

	double z = pow(0.5 * mu3 + 0.5 * sqrt(mu3 * mu3 + 4.0 * mu2 * mu2 * mu2), 1.0 / 3.0);
	double y1 = mu1;// mu2 / (z - mu2 / z);
	double y11 = mu2 + y1 * y1;
	double E = mu1 - y1;
	double d1, d2;
	double r_disc;
	r_disc = Interpolate_Linear(TermRate, Rate, nRate, T_Option);
	if (Strike - PrevCummulative_Weight * PrevAverage - E <= 0)
	{
		if (Call0Put1 == 0)
		{
			value = exp(-r_disc * T_Option)* (y1 - (Strike - PrevCummulative_Weight * PrevAverage - E));
		}
		else
		{
			value = 0.0;
		}
	}
	else
	{
		d1 = log(sqrt(y11) / (Strike - PrevCummulative_Weight * PrevAverage - E)) / sqrt(log(y11 / (y1 * y1)));
		d2 = d1 - sqrt(log(y11 / (y1 * y1)));
		if (Call0Put1 == 0)
		{
			value = exp(-r_disc * T_Option) * (y1 * CDF_N(d1) - (Strike - PrevCummulative_Weight * PrevAverage - E) * CDF_N(d2));
		}
		else
		{
			value = exp(-r_disc * T_Option) * ((Strike - PrevCummulative_Weight * PrevAverage - E) * CDF_N(-d2) - y1 * CDF_N(-d1));
		}
	}
	delta = Arithmetic_Asian_Option_Delta(n, Forward, Weight, T, nVol, TermVol, Vol, r_disc, y1, y11, d1);
	vega = Arithmetic_Asian_Option_Vega(n, Forward, Weight, T, nVol, TermVol, Vol, r_disc, y1, y11, d1);
	return value;
}

long Arithmetic_Asian_Opt_Pricing_Preprocessing(
	long Long0Short1,
	long Call0Put1,
	long PricingDate,
	long AverageStartDate,
	long AverageEndDate,
	long OptionMaturityDate,
	double S,
	double K,
	double PrevAverage,
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	long HolidayFlag,
	long NAdditionalHoliday,
	long* AdditionalHolidays,
	double* ResultPrice
)
{
	long i, j;
	for (i = 0; i < NAdditionalHoliday; i++) if (AdditionalHolidays[i] < 19000101) AdditionalHolidays[i] = ExcelDateToCDate(AdditionalHolidays[i]);

	if (AverageStartDate == PricingDate) PrevAverage = S;
	long nh; 
	long res;
	long* Holiday; 
	if (HolidayFlag < 10)
	{
		nh = Number_Holiday(AverageStartDate / 10000, AverageEndDate / 10000, HolidayFlag);
		Holiday = (long*)malloc(sizeof(long) * (nh + NAdditionalHoliday) );
		res = Mapping_Holiday_CType(AverageStartDate / 10000, AverageEndDate / 10000, HolidayFlag, nh, Holiday);
		if (NAdditionalHoliday > 0)
		{
			for (i = 0; i < NAdditionalHoliday; i++)
			{
				Holiday[i + nh] = AdditionalHolidays[i];
			}
			nh += NAdditionalHoliday;
		}
	}
	else
	{
		long n1;
		long n2;
		long h1 = HolidayFlag / 10;
		long h2 = HolidayFlag - h1 * 10;
		n1 = Number_Holiday(AverageStartDate / 10000, AverageEndDate / 10000, h1);
		n2 = Number_Holiday(AverageStartDate / 10000, AverageEndDate / 10000, h2);
		nh = n1 + n2;
		Holiday = (long*)malloc(sizeof(long) * (nh + NAdditionalHoliday));
		res = Mapping_Holiday_CType(AverageStartDate / 10000, AverageEndDate / 10000, h1, n1, Holiday);
		res = Mapping_Holiday_CType(AverageStartDate / 10000, AverageEndDate / 10000, h2, n2, Holiday + n1);
		if (NAdditionalHoliday > 0)
		{
			for (i = 0; i < NAdditionalHoliday; i++)
			{
				Holiday[i + n1 + n2] = AdditionalHolidays[i];
			}
			nh += NAdditionalHoliday;
		}

	}

	double w, price;
	double T_Option = ((double)DayCountAtoB(PricingDate, OptionMaturityDate)) / 365.;
	double PrevCummulativeWeight = 0.;

	long NDays = DayCountAtoB(AverageStartDate, AverageEndDate) + 1;
	long StartExcelDate = CDateToExcelDate(AverageStartDate);
	long MOD7, SaturSundayFlag;
	long N_BD_Avg = 0;
	long IsHolidayFlag;
	long YYYYMMDD;
	for (i = 0; i < NDays; i++)
	{
		MOD7 = (StartExcelDate + i) % 7;
		YYYYMMDD = ExcelDateToCDate(StartExcelDate + i);
		IsHolidayFlag = isin(YYYYMMDD, Holiday, nh);
		if ((MOD7 == 1 || MOD7 == 0) || IsHolidayFlag == 1) SaturSundayFlag = 1;
		else SaturSundayFlag = 0;

		if (SaturSundayFlag != 1) N_BD_Avg += 1;
	}
	long* AvgDate = (long*)malloc(sizeof(long) * N_BD_Avg);			// 1
	j = 0;
	for (i = 0; i < NDays; i++)
	{
		MOD7 = (StartExcelDate + i) % 7;
		YYYYMMDD = ExcelDateToCDate(StartExcelDate + i);
		IsHolidayFlag = isin(YYYYMMDD, Holiday, nh);
		if ((MOD7 == 1 || MOD7 == 0) || IsHolidayFlag == 1) SaturSundayFlag = 1;
		else SaturSundayFlag = 0;

		if (SaturSundayFlag != 1)
		{
			AvgDate[j] = YYYYMMDD;
			j += 1;
		}
	}
	
	long NPrev = 0;
	long NForward = 0;
	for (i = 0; i < N_BD_Avg; i++)
	{
		if (AvgDate[i] <= PricingDate) NPrev += 1;
		else NForward += 1;
	}

	long* ForwardDate = (long*)malloc(sizeof(long) * NForward);		// 2
	j = 0;
	for (i = 0; i < N_BD_Avg; i++)
	{
		if (AvgDate[i] > PricingDate)
		{
			ForwardDate[j] = AvgDate[i];
			j += 1;
		}
	}
	w = 1.0 / ((double)NForward);
	PrevCummulativeWeight = ((double)NPrev) / (double)N_BD_Avg;
	
	double r_ref, d, rho, fxv;
	double* Forward = (double*)malloc(sizeof(double) * NForward);	// 3
	double* Weight = (double*)malloc(sizeof(double) * NForward);	// 4
	double* Time = (double*)malloc(sizeof(double) * NForward);		// 5

	long NVol = NForward;
	double* VolTerm = (double*)malloc(sizeof(double) * NForward);	// 6
	double* Vol = (double*)malloc(sizeof(double) * NForward);		// 7
	for (i = 0; i < NForward; i++)
	{
		Time[i] = ((double)DayCountAtoB(PricingDate, ForwardDate[i]))/365.;
		r_ref = RefCurve->Interpolated_Rate(Time[i]);
		d = DivCurve->Interpolated_Rate(Time[i]);
		if (fabs(QuantoCorr) < 0.0001)
		{
			Forward[i] = S * exp((r_ref - d) * Time[i]);
		}
		else
		{
			Forward[i] = S * exp((r_ref - d - QuantoCorr * FXVolCurve->Interpolated_Rate(Time[i]) * VolMat->Calc_Implied_Volatility(Time[i], S / K)) * Time[i]);
		}
		Weight[i] = w;
		VolTerm[i] = Time[i];
		Vol[i] = max(0.000001,VolMat->Calc_Implied_Volatility(Time[i], S / K));
	}
	double delta = 0., vega= 0.;
	price = Arithmetic_Asian_Opt_Pricing(NForward, Forward, Weight, Time, NVol, VolTerm, Vol, PrevCummulativeWeight, K, PrevAverage, Call0Put1, T_Option, DiscCurve->nterm(), DiscCurve->Term, DiscCurve->Rate, delta, vega);
	if (Long0Short1 == 0)
	{
		ResultPrice[0] = price;
		ResultPrice[1] = delta;
		ResultPrice[3] = vega/100.;
	}
	else
	{
		ResultPrice[0] = -price;
		ResultPrice[1] = -delta;
		ResultPrice[3] = -vega/100.;
	}

	free(Holiday);
	free(Forward);
	free(Weight);
	free(Time);
	free(VolTerm);
	free(Vol);
	free(AvgDate);
	free(ForwardDate);
	return 1;
}

long ErrorCalcCommodityAsianOption(
	long LongShort,
	long CallPut,
	long PricingDate,
	double StrikePrice,
	long NRate,

	double* TermRate,
	double* Rate,
	long NForward,
	long* ForwardTime,
	double* Forward,

	long NVol,
	long* VolTime,
	double* Vol,
	long NCF,
	long* ForwardStart,

	long* ForwardEnd,
	long* PayDate,
	double* FixedAverage,
	double* ResultPrice,
	double* ResultOption,

	double* ResultDelta,
	double* ResultVega,
	double* ResultDisc,
	long UnderlyingHoliday,
	char* Error
)
{
	long i, j;
	char ErrorName[100];

	if (LongShort != 0 && LongShort != 1)
	{
		strcpy_s(ErrorName, "Check LongShortFlag");
		return SaveErrorName(Error, ErrorName);
	}

	if (StrikePrice < 0)
	{
		strcpy_s(ErrorName, "Check StrikePrice");
		return SaveErrorName(Error, ErrorName);
	}

	if (CallPut != 0 && CallPut != 1)
	{
		strcpy_s(ErrorName, "Check CallPutFlag");
		return SaveErrorName(Error, ErrorName);
	}

	if (PricingDate >= PayDate[NCF - 1] || PricingDate < 0)
	{
		strcpy_s(ErrorName, "Check PricingDate");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NVol; i++)
	{
		if (Vol[i] < 0.0)
		{
			strcpy_s(ErrorName, "Minus Vol Error");
			return SaveErrorName(Error, ErrorName);
		}
	}

	long errorflag = 0;
	for (i = 0; i < NCF; i++)
	{
		if (i > 0)
		{
			if (ForwardStart[i] < ForwardStart[i - 1])
			{
				errorflag = 1;
				break;
			}
			if (ForwardEnd[i] < ForwardEnd[i - 1])
			{
				errorflag = 1;
				break;
			}
			if (PayDate[i] < PayDate[i - 1])
			{
				errorflag = 1;
				break;
			}
		}
	}
	if (errorflag == 1)
	{
		strcpy_s(ErrorName, "Check Schedule and Sort");
		return SaveErrorName(Error, ErrorName);
	}

	if (UnderlyingHoliday < 0)
	{
		strcpy_s(ErrorName, "Check UnderlyingHolidayFlag");
		return SaveErrorName(Error, ErrorName);
	}
	return 1;
}

DLLEXPORT(long) CalcCommodityAsianOption(
	long LongShort,					// Long 0 Short 1
	long CallPut,					// Call 0 Put 1
	long PricingDate,				// PricingDate(YYYYMMD or ExcelDate
	double StrikePrice,				// Strike Price
	long NRate,						// len(DiscRateArray)

	double* TermRate,				// Term Array
	double* Rate,					// Rate Array
	long NForward,					// len(ForwardTime)
	long* ForwardTime,				// Forward Maturity
	double* Forward,				// Forward

	long NVol,						// len(Vol)
	long* VolTime,					// Vol Maturity
	double* Vol,					// Vol
	long NCF,						// Number of CashFlow
	long* ForwardStart,				// Forward Start(Not Business Day == OKay)

	long* ForwardEnd,				// Forward End(Not Business Day == OKay)
	long* PayDate,					// PaymentDay(Not Business Day == OKay)
	double* FixedAverage,			// Pre Fixed Average Price
	double* ResultPrice,			// Output : len == NCF
	double* ResultOption,			// Output : len == NCF

	double* ResultDelta,			// Output : len == NCF
	double* ResultVega,				// Output : len == NCF
	double* ResultDisc,				// Output : len == NCF
	long UnderlyingHoliday,			// Underlying Holiday Flag (0 : Korean, 1 : USD, 2 : GBP)
	long TextFlag,					// Text Logging
	long GreekFlag,					// Calc Greek(Dummy)
	long NAdditionalHoliday,
	long* AdditionalHolidays,
	char* Error						// Error Message
)
{
	long i, j;
	long ErrorCode = 0;
	ErrorCode = ErrorCalcCommodityAsianOption(LongShort,CallPut,PricingDate,StrikePrice,NRate,
		TermRate,Rate,NForward,ForwardTime,Forward,
		NVol,VolTime,Vol,NCF,ForwardStart,
		ForwardEnd,PayDate,FixedAverage,ResultPrice,ResultOption,
		ResultDelta,ResultVega,ResultDisc,UnderlyingHoliday,Error);
	if (ErrorCode < 0) return ErrorCode;


	char CalcFunctionName[] = "CalcCommodityAsianOption";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "LongShort", LongShort);
		DumppingTextData(CalcFunctionName, SaveFileName, "CallPut", CallPut);
		DumppingTextData(CalcFunctionName, SaveFileName, "PricingDate", PricingDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "StrikePrice", StrikePrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "NRate", NRate);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermRate", NRate, TermRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rate", NRate, Rate);
		DumppingTextData(CalcFunctionName, SaveFileName, "NForward", NForward);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardTime", NForward, ForwardTime);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Forward", NForward, Forward);

		DumppingTextData(CalcFunctionName, SaveFileName, "NVol", NVol);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "VolTime", NVol, VolTime);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Vol", NVol, Vol);
		DumppingTextData(CalcFunctionName, SaveFileName, "NCF", NCF);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardStart", NCF, ForwardStart);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardEnd", NCF, ForwardEnd);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDate", NCF, PayDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "UnderlyingHoliday", UnderlyingHoliday);
	}


	double TempResult[100] = { 0.0 };
	if (PricingDate < 19000101) PricingDate = ExcelDateToCDate(PricingDate);
	for (i = 0; i < NForward; i++) if (ForwardTime[i] < 19000101) ForwardTime[i] = ExcelDateToCDate(ForwardTime[i]);
	for (i = 0; i < NVol; i++) if (VolTime[i] < 19000101) VolTime[i] = ExcelDateToCDate(VolTime[i]);
	for (i = 0; i < NCF; i++)
	{
		if (ForwardStart[i] < 19000101) ForwardStart[i] = ExcelDateToCDate(ForwardStart[i]);
		if (ForwardEnd[i] < 19000101) ForwardEnd[i] = ExcelDateToCDate(ForwardEnd[i]);
		if (PayDate[i] < 19000101) PayDate[i] = ExcelDateToCDate(PayDate[i]);
	}
	for (i = 0; i < NRate; i++) if (TermRate[i] > 30000.0) TermRate[i] = ((double)DayCountAtoB(PricingDate, ExcelDateToCDate((long)(TermRate[i])))) / 365.;
	long NRateDisc = 1;
	double RateTermDisc[1] = { 1.0 };
	double RateDisc[1] = { 0.0 };
	double VolTemp[1] = { Vol[0] };

	long NReferenceCurve = DayCountAtoB(min(PricingDate, ForwardTime[0]), ForwardTime[NForward - 1]);
	double S = Forward[0];
	long StartDateExl;
	if (PricingDate < ForwardTime[0]) StartDateExl = CDateToExcelDate(PricingDate);
	else StartDateExl = CDateToExcelDate(ForwardTime[0]);
	long* ForwardDate = (long*)malloc(sizeof(long) * NReferenceCurve);
	double* ForwardPrice = (double*)malloc(sizeof(double) * NReferenceCurve);
	long TmpDateExl, TmpYYYYMMDD, idx, isinflag;
	for (i = 0; i < NReferenceCurve; i++)
	{
		TmpDateExl = StartDateExl + i;
		TmpYYYYMMDD = ExcelDateToCDate(TmpDateExl);
		isinflag = isinFindIndex(TmpYYYYMMDD, ForwardTime, NForward, idx);
		if (isinflag == 1)
		{
			ForwardDate[i] = ForwardTime[idx];
			ForwardPrice[i] = Forward[idx];
		}
		else
		{
			ForwardDate[i] = TmpYYYYMMDD;
			ForwardPrice[i] = -99999.99;
		}
	}
	long NotFound;
	for (i = 0; i < NReferenceCurve; i++)
	{
		if (ForwardPrice[i] < -99.9)
		{
			for (j = i; j < NReferenceCurve; j++)
			{
				if (ForwardPrice[j] > -99.9)
				{
					ForwardPrice[i] = ForwardPrice[j];
					break;
				}
			}

			if (j == NReferenceCurve) NotFound = 1;
			else NotFound = 0;
		}

		if (NotFound && i > 0) ForwardPrice[i] = ForwardPrice[i - 1];
	}
	long NRefRate = NReferenceCurve;
	double* TermRef = (double*)malloc(sizeof(double) * NRefRate);
	double* RefRate = (double*)malloc(sizeof(double) * NRefRate);
	for (i = 0; i < NRefRate; i++)
	{
		TermRef[i] = ((double)DayCountAtoB(PricingDate, ForwardDate[i])) / 365.0;
		if (fabs(TermRef[i]) < 0.000001) RefRate[i] = 0.;
		else RefRate[i] = log(ForwardPrice[i] / S) / TermRef[i];
	}
	curveinfo DiscCurve(NRateDisc, RateTermDisc, RateDisc);
	curveinfo RefCurve(NRefRate, TermRef, RefRate);
	curveinfo DivCurve(NRateDisc, RateTermDisc, RateDisc);
	curveinfo FXVolCurve(NRateDisc, RateTermDisc, RateDisc);
	volinfo VolMat(1, RateTermDisc, 1, RateTermDisc, VolTemp);
	double T, TPay, Disc, r, s;
	double* TermVol = (double*)malloc(sizeof(double) * NVol);
	for (i = 0; i < NVol; i++)
	{
		TermVol[i] = ((double)DayCountAtoB(PricingDate, VolTime[i]))/365.;
	}
	s = 0.;
	for (i = 0; i < NCF; i++)
	{
		T = ((double)DayCountAtoB(PricingDate, ForwardEnd[i]))/365.;
		TPay = ((double)DayCountAtoB(PricingDate, PayDate[i])) / 365.;
		VolMat.Vol_Matrix[0][0] = Interpolate_Linear(TermVol, Vol, NVol, T);
		if (VolMat.LocalVolMat != NULL) VolMat.LocalVolMat[0][0] = VolMat.Vol_Matrix[0][0];

		r = Interpolate_Linear(TermRate, Rate, NRate, TPay);
		Disc = exp(-r * TPay);
		if (PayDate[i] >PricingDate)
		{
			Arithmetic_Asian_Opt_Pricing_Preprocessing(LongShort,CallPut,PricingDate,ForwardStart[i],ForwardEnd[i],
														PayDate[i],S,StrikePrice,FixedAverage[i],&DiscCurve,	
														&RefCurve,	&DivCurve,	0.0,	&FXVolCurve,&VolMat,		
														0,UnderlyingHoliday, NAdditionalHoliday, AdditionalHolidays, TempResult);
		}

		ResultOption[i] = TempResult[0];
		ResultDelta[i] = TempResult[1];
		ResultVega[i] = TempResult[3];
		ResultDisc[i] = Disc;
		s += (Disc  * TempResult[0]) / ((double)NCF);
	}

	ResultPrice[0] = s;
	free(TermVol);
	free(ForwardDate);
	free(ForwardPrice);
	free(TermRef);
	free(RefRate);
	return 1;
}

double AsianOptionSimul(
	long TypeFlag,			// Option Type: 1이면 콜, 2이면 풋
	double S0,				// 기초자산 현재가
	double X,				// 행사가격
	double MeanPrice,		// 평균가격
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	long VolTypeFlag,
	long Days_CalcToMeanStart,
	long Days_CalcToMaturity,
	double T_CalcToPay,
	double** FixedRandn,
	long S_UpDnFlag
)
{
	long i, j;
	long N;
	long idx;
	long NSimul = 10000;
	long idx_T, idx_S;
	long Days_MeanStartToMaturity = Days_CalcToMaturity - Days_CalcToMeanStart;

	double OptPrice = 0.0;
	double eps;
	double vol, simvol = 0.0;
	double S_Start, StockPrice;
	double dt = 1.0 / 365.0;
	double T_MeanStart_To_Maturity;
	double w_MeanStart_To_CalcDate, T_MeanStart_To_CalcDate;
	double w_Simul_To_Maturity, T_Simul_To_Maturity;
	double T, T2;
	double Drift, Diffusion;
	if (Days_CalcToMeanStart < 0)
	{
		T_MeanStart_To_CalcDate = ((double)(-Days_CalcToMeanStart)) / 365.0;
		T_MeanStart_To_Maturity = ((double)(Days_CalcToMaturity - Days_CalcToMeanStart)) / 365.0;
		w_MeanStart_To_CalcDate = T_MeanStart_To_CalcDate / T_MeanStart_To_Maturity;
		w_Simul_To_Maturity = 1.0 - w_MeanStart_To_CalcDate;
		N = Days_CalcToMaturity;
	}
	else if (Days_CalcToMeanStart == 0)
	{
		T_MeanStart_To_CalcDate = 1.0 / 365.0;
		T_MeanStart_To_Maturity = ((double)(Days_CalcToMaturity - Days_CalcToMeanStart)) / 365.0;
		w_MeanStart_To_CalcDate = T_MeanStart_To_CalcDate / T_MeanStart_To_Maturity;
		w_Simul_To_Maturity = 1.0 - w_MeanStart_To_CalcDate;
		N = Days_CalcToMaturity;
		MeanPrice = S0;
	}
	else
	{
		w_MeanStart_To_CalcDate = 0.0;
		w_Simul_To_Maturity = 1.0;
		N = Days_CalcToMaturity - Days_CalcToMeanStart;
	}

	if (S_UpDnFlag == 0) S_Start = 1.0;
	else if (S_UpDnFlag == 1) S_Start = 1.01;
	else S_Start = 0.99;

	double* DailyForwardRate = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		DailyForwardRate[i] = Calc_Forward_Rate(RefCurve->Term, RefCurve->Rate, RefCurve->nterm(), ((double)(i)) * dt, ((double)(i + 1)) * dt);
	}
	double* DailyDiv = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	if (DivTypeFlag == 0)
	{
		for (i = 0; i < Days_CalcToMaturity; i++)
		{
			DailyDiv[i] = DivCurve->Rate[0];
		}
	}
	else if (DivTypeFlag == 1)
	{
		for (i = 0; i < Days_CalcToMaturity; i++)
		{
			DailyDiv[i] = Calc_Forward_Rate(DivCurve->Term, DivCurve->Rate, DivCurve->nterm(), ((double)(i)) * dt, ((double)(i + 1)) * dt);
		}
	}
	else if (DivTypeFlag == 2)
	{
		for (i = 0; i < Days_CalcToMaturity; i++) DailyDiv[i] = 0.0;

		idx = 0;
		for (j = 0; j < DivCurve->nterm(); j++)
		{
			T2 = DivCurve->Term[j];
			for (i = idx; i < Days_CalcToMaturity; i++)
			{
				T = ((double)(i + 1)) * dt;
				if (T >= T2)
				{
					DailyDiv[i] = DivCurve->Rate[j];
					idx = i;
					break;
				}
			}

		}
	}
	double* DailyFXVol = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		DailyFXVol[i] = Interpolate_Linear(FXVolCurve->Term, FXVolCurve->Rate, FXVolCurve->nterm(), ((double)(i + 1)) * dt);
	}

	if (VolTypeFlag == 2) simvol = VolMat->Calc_Implied_Volatility(((double)Days_CalcToMaturity)/365.0, S0/X);
	double DF = Calc_Discount_Factor(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), T_CalcToPay);
	double AvgStock;
	if (Days_CalcToMaturity <= 0)
	{
		if (TypeFlag == 1)
		{
			return DF * max(MeanPrice - X, 0.0);
		}
		else
		{
			return DF* max(X - MeanPrice, 0.0) ;
		}
	}

	for (i = 0; i < NSimul; i++)
	{
		StockPrice = S_Start;
		idx_T = 0;
		idx_S = 0;
		T = 0.0;
		AvgStock = 0.0;
		for (j = 0; j < Days_CalcToMaturity; j++)
		{
			T = T + dt;
			eps = FixedRandn[i][j];
			if (VolTypeFlag == 2) vol = simvol;
			else vol = VolMat->Calc_Volatility_for_Simulation(T, StockPrice, &idx_T, &idx_S);
			
			if (DivTypeFlag == 2)
			{
				Drift = (DailyForwardRate[j] - 0.5 * vol * vol- QuantoCorr * vol * DailyFXVol[j]) * dt;
				Diffusion = vol * sqrt(dt) * eps;
				StockPrice = (StockPrice - DailyDiv[j]) * exp(Drift + Diffusion);
			}
			else
			{
				Drift = (DailyForwardRate[j] - DailyDiv[j] - 0.5 * vol * vol - QuantoCorr * vol * DailyFXVol[j]) * dt;
				Diffusion = vol * sqrt(dt) * eps;
				StockPrice = (StockPrice ) * exp(Drift + Diffusion);
			}
			
			if (j >= Days_CalcToMeanStart)
			{
				AvgStock += StockPrice/(double)N;
			}
		}
		StockPrice = S0 * StockPrice;
		if (Days_MeanStartToMaturity == 0) AvgStock = StockPrice;
		else
		{
			AvgStock = S0 * AvgStock;
			AvgStock = AvgStock * w_Simul_To_Maturity + w_MeanStart_To_CalcDate * MeanPrice;
		}

		if (TypeFlag == 1) OptPrice += DF * max(AvgStock - X, 0.0) / (double)NSimul;
		else OptPrice += DF * max(X - AvgStock, 0.0) / (double)NSimul;
	}

	free(DailyForwardRate);
	free(DailyDiv);
	free(DailyFXVol);
	return OptPrice;
}

long AsianOptionSimul(
	long TypeFlag,			// Option Type: 1이면 콜, 2이면 풋
	double S0,				// 기초자산 현재가
	double X,				// 행사가격
	double MeanPrice,		// 평균가격
	curveinfo* DiscCurve,	// 할인커브
	curveinfo* RefCurve,	// 레퍼런스커브
	curveinfo* DivCurve,	// 배당커브
	double QuantoCorr,		// Quanto COrrelation
	curveinfo* FXVolCurve,	// FXVol 커브
	volinfo* VolMat,		// Vol 정보
	long DivTypeFlag,		// Div 배당타입
	long VolTypeFlag,
	long Days_CalcToMeanStart,
	long Days_CalcToMaturity,
	double T_CalcToPay,
	long GreekFlag,
	double* ResultPrice
)
{
	long i, j, k;
	long NSimul = 10000;
	double dt = 1.0 / 365.0;
	randnorm(0);
	double** FixedRandn = make_array_randn(NSimul, Days_CalcToMaturity + 10);
	double OptPrice, OptPriceU, OptPriceD, Delta, Gamma, Vega, Theta, Rho;

	if (GreekFlag == 0)
	{
		OptPrice = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
									RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
									DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
									0);
		ResultPrice[0] = OptPrice;
	}
	else
	{
		OptPrice = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			0);
		ResultPrice[0] = OptPrice;
		OptPriceU = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			1);
		OptPriceD = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			-1);
		Delta = (OptPriceU - OptPriceD) / (2.0 * 0.01 * S0);
		Gamma = (OptPriceU + OptPriceD - 2.0 * OptPrice) / (0.01 * 0.01 * S0 * S0);
		ResultPrice[1] = Delta;
		ResultPrice[2] = Gamma;
		double* VolReshaped_Up = (double*)malloc(sizeof(double) * (VolMat->size(0) * VolMat->size(1)));
		double* VolReshaped_Dn = (double*)malloc(sizeof(double) * (VolMat->size(0) * VolMat->size(1)));
		k = 0;
		for (i = 0 ; i < VolMat->size(0); i++)
			for (j = 0; j < VolMat->size(1); j++)
			{
				VolReshaped_Up[k] = VolMat->Vol_Matrix[i][j] + 0.01;
				VolReshaped_Dn[k] = max(0.0, VolMat->Vol_Matrix[i][j] - 0.01);
				k += 1;
			}
		volinfo VolUp(VolMat->size(0), VolMat->Parity, VolMat->size(1), VolMat->Term, VolReshaped_Up);
		volinfo VolDn(VolMat->size(0), VolMat->Parity, VolMat->size(1), VolMat->Term, VolReshaped_Dn);
		if (VolTypeFlag == 0)
		{
			long NTempRate = 1;
			double TempRefRateTerm[1] = { 1.0 };
			double TempRefRate[1] = { 0.0 };
			if (DivTypeFlag == 2)
			{
				curveinfo TempCurve(NTempRate, TempRefRateTerm, TempRefRate);
				VolUp.set_localvol(&TempCurve, &TempCurve, 2.0, 0.01);
				fillna_Interpolate(VolUp.LocalVolMat, VolUp.size(0), VolUp.size(1));
				VolDn.set_localvol(&TempCurve, &TempCurve, 2.0, 0.01);
				fillna_Interpolate(VolDn.LocalVolMat, VolDn.size(0), VolDn.size(1));
			}
			else
			{
				VolUp.set_localvol(RefCurve, DivCurve, 2.0, 0.01);
				fillna_Interpolate(VolUp.LocalVolMat, VolUp.size(0), VolUp.size(1));
				VolDn.set_localvol(RefCurve, DivCurve, 2.0, 0.01);
				fillna_Interpolate(VolDn.LocalVolMat, VolDn.size(0), VolDn.size(1));
			}
		}
		else
		{
			VolUp.LocalVolMat = VolUp.Vol_Matrix;
			VolUp.Parity_Locvol = VolUp.Parity;
			VolUp.Term_Locvol = VolUp.Term;
			VolDn.LocalVolMat = VolDn.Vol_Matrix;
			VolDn.Parity_Locvol = VolDn.Parity;
			VolDn.Term_Locvol = VolDn.Term;
		}
		OptPriceU = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, &VolUp,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			0);
		OptPriceD = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, &VolDn,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			0);
		Vega = (OptPriceU - OptPriceD) / 2.0;
		ResultPrice[3] = Vega;

		if (Days_CalcToMaturity > 0)
		{
			long Days_CalcToMeanStart_Up = Days_CalcToMeanStart + 1;
			long Days_CalcToMaturity_Up = Days_CalcToMaturity + 1;
			long Days_CalcToMeanStart_Dn = Days_CalcToMeanStart - 1;
			long Days_CalcToMaturity_Dn = Days_CalcToMaturity - 1;
			double T_CalcToPay_Up = T_CalcToPay + dt;
			double T_CalcToPay_Dn = T_CalcToPay - dt;
			OptPriceU = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
				RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
				DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart_Up, Days_CalcToMaturity_Up, T_CalcToPay_Up, FixedRandn,
				0);
			OptPriceD = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
				RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
				DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart_Dn, Days_CalcToMaturity_Dn, T_CalcToPay_Dn, FixedRandn,
				0);
			Theta = -(OptPriceU - OptPriceD) / 2.0;
		}
		else
		{
			Theta = 0.0;
		}
		ResultPrice[4] = Theta;

		for (i = 0; i < DiscCurve->nterm(); i++)
		{
			DiscCurve->Rate[i] = DiscCurve->Rate[i] + 0.0001;
		}
		for (i = 0; i < RefCurve->nterm(); i++)
		{
			RefCurve->Rate[i] = RefCurve->Rate[i] + 0.0001;
		}
		OptPriceU = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			0);

		for (i = 0; i < DiscCurve->nterm(); i++)
		{
			DiscCurve->Rate[i] = DiscCurve->Rate[i] - 0.0002;
		}
		for (i = 0; i < RefCurve->nterm(); i++)
		{
			RefCurve->Rate[i] = RefCurve->Rate[i] - 0.0002;
		}
		OptPriceD = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, DiscCurve,
			RefCurve, DivCurve, QuantoCorr, FXVolCurve, VolMat,
			DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, FixedRandn,
			0);

		Rho = (OptPriceU - OptPriceD) / 2.0;
		for (i = 0; i < DiscCurve->nterm(); i++)
		{
			DiscCurve->Rate[i] = DiscCurve->Rate[i] + 0.0001;
		}
		for (i = 0; i < RefCurve->nterm(); i++)
		{
			RefCurve->Rate[i] = RefCurve->Rate[i] + 0.0001;
		}
		ResultPrice[5] = Rho *100.0;

		free(VolReshaped_Up);
		free(VolReshaped_Dn);
	}
	for (i = 0; i < NSimul; i++) free(FixedRandn[i]);
	free(FixedRandn);
	return 1;
}
double an(
	double dt,
	double Rf,
	double Div,
	double QuantoCorr,
	double Vol,
	double FXVol,
	long GreedIdx
)
{
	double value;
	double n = (double)GreedIdx;
	value = 0.5 * dt * ((Rf - QuantoCorr * FXVol * Vol - Div) * n - Vol * Vol * n * n);
	return value;
}

double bn(
	double dt,
	double Rf_Disc,
	double Vol,
	long GreedIdx
)
{
	double value;
	double n = (double)GreedIdx;
	value = 1 + dt * (Rf_Disc + Vol * Vol * n * n);
	return value;
}

double cn(
	double dt,
	double Rf,
	double Div,
	double QuantoCorr,
	double Vol,
	double FXVol,
	long GreedIdx
)
{
	double value;
	double n = (double)GreedIdx;
	value = 0.5 * dt * (-(Rf - QuantoCorr * Vol * FXVol - Div) * n - Vol * Vol * n * n);
	return value;
}

long AmericanOptionFDM(
	long TypeFlag,				// Option Type: 1이면 콜, 2이면 풋
	long AmericanOptionType,	// 0:아메리칸옵션 1:아메리칸디지털옵션
	double S0,					// 기초자산 현재가
	double X,					// 행사가격
	double MeanPrice,			// 평균가격
	curveinfo* DiscCurve,		// 할인커브
	curveinfo* RefCurve,		// 레퍼런스커브
	curveinfo* DivCurve,		// 배당커브
	double QuantoCorr,			// Quanto COrrelation
	curveinfo* FXVolCurve,		// FXVol 커브
	volinfo* VolMat,			// Vol 정보
	long DivTypeFlag,			// Div 배당타입
	long VolTypeFlag,
	long Days_CalcToMeanStart,
	long Days_CalcToMaturity,
	double T_CalcToPay,
	double* ResultPrice
)
{
	long i, j, k,N;
	long idx;
	double d;
	double dt = 1.0 / 365.0, T,T2;
	double dS = 0.01 * S0;
	double T_Ref = ((double)Days_CalcToMaturity) / 365.0;
	long idxT, idxS;
	double S, fxvol, r_ref, r_disc;
	long NGreed = 200;
	double vol, Rf_Quanto, r;
	double value, valueU, valueD;
	double* DailyForwardRate = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	double* DailyDiscRate = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		if (RefCurve->nterm() > 1) DailyForwardRate[i] = Calc_Forward_Rate(RefCurve->Term, RefCurve->Rate, RefCurve->nterm(), ((double)(i)) * dt, ((double)(i + 1)) * dt);
		else DailyForwardRate[i] = RefCurve->Rate[0];

		if (DiscCurve->nterm() > 1) DailyDiscRate[i] = Calc_Forward_Rate(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), ((double)(i)) * dt, ((double)(i + 1)) * dt);
		else DailyDiscRate[i] = DiscCurve->Rate[0];
	}
	double* DailyDiv = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	if (DivTypeFlag == 0)
	{
		for (i = 0; i < Days_CalcToMaturity; i++)
		{
			DailyDiv[i] = DivCurve->Rate[0];
		}
	}
	else if (DivTypeFlag == 1)
	{
		for (i = 0; i < Days_CalcToMaturity; i++)
		{
			DailyDiv[i] = Calc_Forward_Rate(DivCurve->Term, DivCurve->Rate, DivCurve->nterm(), ((double)(i)) * dt, ((double)(i + 1)) * dt);
		}
	}
	else if (DivTypeFlag == 2)
	{
		N = 0;
		for (i = 0; i < DivCurve->nterm(); i++)
		{
			if (DivCurve->Term[i] > T_Ref) break;
			N += 1;
		}
		d = 1.0 / T_Ref * Sumation(N, DivCurve->Rate) / S0;
		for (i = 0 ; i < Days_CalcToMaturity; i++) DailyDiv[i] = d;
	}

	double* DailyFXVol = (double*)malloc(sizeof(double) * Days_CalcToMaturity);
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		DailyFXVol[i] = Interpolate_Linear(FXVolCurve->Term, FXVolCurve->Rate, FXVolCurve->nterm(), ((double)(i + 1)) * dt);
	}

	double a0, b0, c0, aN, bN, cN;
	double** An = make_array(Days_CalcToMaturity, NGreed);
	double** Bn = make_array(Days_CalcToMaturity, NGreed);
	double** Cn = make_array(Days_CalcToMaturity, NGreed);
	double* S_Array = make_array(NGreed);
	double* Temp_An = make_array(NGreed);
	double* Temp_Bn = make_array(NGreed);
	double* Temp_Cn = make_array(NGreed);
	for (i = 0; i < NGreed; i++) S_Array[i] = (double)i * dS;
	T = 0.0;
	idxT = 0;
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		T = (double)(i+1) * dt;
		idxS = 0;
		r_ref = DailyForwardRate[i];
		r_disc = DailyDiscRate[i];
		fxvol = DailyDiscRate[i];
		d = DailyDiv[i];

		for (j = 0; j < NGreed; j++)
		{
			S = (double)j * dS/S0;
			if (VolTypeFlag == 2) vol = VolMat->Calc_Implied_Volatility(((double)Days_CalcToMaturity) / 365.0, S0 / X);
			else vol = VolMat->Calc_Volatility_for_Simulation(T, S, &idxT, &idxS);
			An[i][j] = an(dt, r_ref, d, QuantoCorr, vol, fxvol, j);
			Bn[i][j] = bn(dt, r_disc, vol, j);
			Cn[i][j] = cn(dt, r_ref, d, QuantoCorr, vol, fxvol, j);
		}
	}
	
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		a0 = An[i][0];
		b0 = Bn[i][0];
		c0 = Cn[i][0];
		aN = An[i][NGreed - 1];
		bN = Bn[i][NGreed - 1];
		cN = Cn[i][NGreed - 1];
		Bn[i][0] = 2 * a0 + b0;
		Cn[i][0] = c0 - a0;
		Bn[i][NGreed - 1] = bN + 2 * cN;
		An[i][NGreed - 1] = aN - cN;
	}
	
	double* Payoff = make_array(NGreed);
	if (AmericanOptionType == 0)
	{
		for (i = 0; i < NGreed; i++)
		{
			if (TypeFlag == 1) Payoff[i] = max(S_Array[i]  - X, 0.0);
			else Payoff[i] = max(X - S_Array[i], 0.0);
		}
	}
	else
	{
		for (i = 0; i < NGreed; i++)
		{
			if (TypeFlag == 1)
			{
				Payoff[i] = 1.0 * (double)(S_Array[i] - X >= 0.0);
			}
			else
			{
				Payoff[i] = 1.0 * (double)(X - S_Array[i] >= 0.0);
			}
		}
	}

	for (i = Days_CalcToMaturity - 1; i >= 0; i--)
	{
		Tri_diagonal_Fast(An[i],    // Tridiagonal Matrix에서 왼쪽 대각선 행렬
			Bn[i],     // Tridiagonal Matrix에서 중앙 대각선 행렬
			Cn[i],    // Tridiagonal Matrix에서 오른쪽 대각선 행렬
			Payoff,     // V(T1)
			NGreed,           // 대각선 행렬들의 길이
			Temp_An,// 임시 행렬1 
			Temp_Bn, // 임시 행렬2
			Temp_Cn // 임시 행렬3
		);
		if (i >= Days_CalcToMeanStart)
		{
			if (AmericanOptionType == 0)
			{
				for (j = 0; j < NGreed; j++)
				{
					if (TypeFlag == 1) Payoff[j] = max(Payoff[j], max(S_Array[j] - X, 0.0));
					else Payoff[j] = max(Payoff[j], max(X - S_Array[j], 0.0));
				}
			}
			else
			{
				for (j = 0; j < NGreed; j++)
				{
					if (TypeFlag == 1) Payoff[j] = max(Payoff[j], 1.0 * (double)(S_Array[i] - X >= 0.0));
					else Payoff[j] = max(Payoff[j],1.0 * (double)(X - S_Array[i] >= 0.0));
				}
			}
		}
	}
	double frate;
	if (T_CalcToPay - T_Ref > 0.0) frate = Calc_Forward_Rate(DiscCurve->Term, DiscCurve->Rate, DiscCurve->nterm(), T_Ref, T_CalcToPay);
	else frate = 0.0;
	double DF_t_T = 1.0 / (1.0 + frate * (T_CalcToPay - T_Ref));
	value = Interpolate_Linear(S_Array, Payoff, NGreed, S0) * DF_t_T;
	valueU = Interpolate_Linear(S_Array, Payoff, NGreed, S0 * 1.01) * DF_t_T;
	valueD = Interpolate_Linear(S_Array, Payoff, NGreed, S0 * 0.99) * DF_t_T;

	ResultPrice[0] = value;
	ResultPrice[1] = (valueU - valueD) / (2.0 * 0.01 * S0);
	ResultPrice[2] = (valueU + valueD - 2.0 * value) / (S0 * S0 * 0.01 * 0.01);
	free(DailyForwardRate);
	free(DailyDiscRate);
	free(DailyDiv);
	free(DailyFXVol);
	for (i = 0; i < Days_CalcToMaturity; i++)
	{
		free(An[i]);
		free(Bn[i]);
		free(Cn[i]);
	}
	free(An);
	free(Bn);
	free(Cn);
	free(Temp_An);
	free(Temp_Bn);
	free(Temp_Cn);
	free(S_Array);
	free(Payoff);
	return 1;
}

long AmericanOptionFDM(
	long TypeFlag,				// Option Type: 1이면 콜, 2이면 풋
	long AmericanOptionType,	// 0:아메리칸옵션 1:아메리칸디지털옵션
	double S0,					// 기초자산 현재가
	double X,					// 행사가격
	double MeanPrice,			// 평균가격
	curveinfo* DiscCurve,		// 할인커브
	curveinfo* RefCurve,		// 레퍼런스커브
	curveinfo* DivCurve,		// 배당커브
	double QuantoCorr,			// Quanto COrrelation
	curveinfo* FXVolCurve,		// FXVol 커브
	volinfo* VolMat,			// Vol 정보
	long DivTypeFlag,			// Div 배당타입
	long VolTypeFlag,
	long Days_CalcToMeanStart,
	long Days_CalcToMaturity,
	double T_CalcToPay,
	long GreekFlag,
	double* ResultPrice
)
{
	long i, j,k;
	long ResultCode;
	double valueU, valueD;
	double Vega, Theta, Rho;
	double TempResultPrice[10] = { 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 };
	ResultCode = AmericanOptionFDM(
		TypeFlag, AmericanOptionType, S0, X, MeanPrice,
		DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
		VolMat, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
		T_CalcToPay, ResultPrice);

	if (GreekFlag > 0)
	{
		double* VolReshaped_Up = (double*)malloc(sizeof(double) * (VolMat->size(0) * VolMat->size(1)));
		double* VolReshaped_Dn = (double*)malloc(sizeof(double) * (VolMat->size(0) * VolMat->size(1)));
		k = 0;
		for (i = 0; i < VolMat->size(0); i++)
			for (j = 0; j < VolMat->size(1); j++)
			{
				VolReshaped_Up[k] = VolMat->Vol_Matrix[i][j] + 0.01;
				VolReshaped_Dn[k] = max(0.001, VolMat->Vol_Matrix[i][j] - 0.01);
				k = k + 1;
			}

		volinfo VolUp(VolMat->size(0), VolMat->Parity, VolMat->size(1), VolMat->Term, VolReshaped_Up);
		volinfo VolDn(VolMat->size(0), VolMat->Parity, VolMat->size(1), VolMat->Term, VolReshaped_Dn);
		if (VolTypeFlag == 0)
		{
			long NTempRate = 1;
			double TempRefRateTerm[1] = { 1.0 };
			double TempRefRate[1] = { 0.0 };
			if (DivTypeFlag == 2)
			{
				curveinfo TempCurve(NTempRate, TempRefRateTerm, TempRefRate);
				VolUp.set_localvol(&TempCurve, &TempCurve, 2.0, 0.01);
				fillna_Interpolate(VolUp.LocalVolMat, VolUp.size(0), VolUp.size(1));
				VolDn.set_localvol(&TempCurve, &TempCurve, 2.0, 0.01);
				fillna_Interpolate(VolDn.LocalVolMat, VolDn.size(0), VolDn.size(1));
			}
			else
			{
				VolUp.set_localvol(RefCurve, DivCurve, 2.0, 0.01);
				fillna_Interpolate(VolUp.LocalVolMat, VolUp.size(0), VolUp.size(1));
				VolDn.set_localvol(RefCurve, DivCurve, 2.0, 0.01);
				fillna_Interpolate(VolDn.LocalVolMat, VolDn.size(0), VolDn.size(1));
			}
		}
		else
		{
			VolUp.LocalVolMat = VolUp.Vol_Matrix;
			VolUp.Parity_Locvol = VolUp.Parity;
			VolUp.Term_Locvol = VolUp.Term;
			VolDn.LocalVolMat = VolDn.Vol_Matrix;
			VolDn.Parity_Locvol = VolDn.Parity;
			VolDn.Term_Locvol = VolDn.Term;
		}

		ResultCode = AmericanOptionFDM(
			TypeFlag, AmericanOptionType, S0, X, MeanPrice,
			DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
			&VolUp, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
			T_CalcToPay, TempResultPrice);
		valueU = TempResultPrice[0];
		ResultCode = AmericanOptionFDM(
			TypeFlag, AmericanOptionType, S0, X, MeanPrice,
			DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
			&VolDn, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
			T_CalcToPay, TempResultPrice);
		valueD = TempResultPrice[0];
		Vega = (valueU - valueD) / 2.0;
		ResultPrice[3] = Vega;
		if (Days_CalcToMaturity > 0)
		{
			long Days_CalcToMeanStart_Up = Days_CalcToMeanStart + 1;
			long Days_CalcToMaturity_Up = Days_CalcToMaturity + 1;
			long Days_CalcToMeanStart_Dn = Days_CalcToMeanStart - 1;
			long Days_CalcToMaturity_Dn = Days_CalcToMaturity - 1;
			double T_CalcToPay_Up = T_CalcToPay + 1.0 / 365.0;
			double T_CalcToPay_Dn = T_CalcToPay - 1.0 / 365.0;
			ResultCode = AmericanOptionFDM(
				TypeFlag, AmericanOptionType, S0, X, MeanPrice,
				DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
				VolMat, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart_Up, Days_CalcToMaturity_Up,
				T_CalcToPay_Up, TempResultPrice);
			valueU = TempResultPrice[0];
			ResultCode = AmericanOptionFDM(
				TypeFlag, AmericanOptionType, S0, X, MeanPrice,
				DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
				VolMat, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart_Dn, Days_CalcToMaturity_Dn,
				T_CalcToPay_Dn, TempResultPrice);
			valueD = TempResultPrice[0];
			Theta = (-(valueU - valueD)) / 2.0;
			for (i = 0; i < DiscCurve->nterm(); i++)
			{
				DiscCurve->Rate[i] = DiscCurve->Rate[i] + 0.0001;
			}
			for (i = 0; i < RefCurve->nterm(); i++)
			{
				RefCurve->Rate[i] = RefCurve->Rate[i] + 0.0001;
			}

			ResultCode = AmericanOptionFDM(
				TypeFlag, AmericanOptionType, S0, X, MeanPrice,
				DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
				VolMat, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
				T_CalcToPay, TempResultPrice);
			valueU = TempResultPrice[0];

			for (i = 0; i < DiscCurve->nterm(); i++)
			{
				DiscCurve->Rate[i] = DiscCurve->Rate[i] - 0.0002;
			}
			for (i = 0; i < RefCurve->nterm(); i++)
			{
				RefCurve->Rate[i] = RefCurve->Rate[i] - 0.0002;
			}
			ResultCode = AmericanOptionFDM(
				TypeFlag, AmericanOptionType, S0, X, MeanPrice,
				DiscCurve, RefCurve, DivCurve, QuantoCorr, FXVolCurve,
				VolMat, DivTypeFlag, VolTypeFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
				T_CalcToPay, TempResultPrice);
			valueD = TempResultPrice[0];
			Rho = (valueU - valueD) / 2.0 *100.0;
			for (i = 0; i < DiscCurve->nterm(); i++)
			{
				DiscCurve->Rate[i] = DiscCurve->Rate[i] + 0.0001;
			}
			for (i = 0; i < RefCurve->nterm(); i++)
			{
				RefCurve->Rate[i] = RefCurve->Rate[i] + 0.0001;
			}
		}
		else
		{
			Theta = 0.0;
		}
		ResultPrice[4] = Theta;
		ResultPrice[5] = Rho;
		free(VolReshaped_Up);
		free(VolReshaped_Dn);
	}
	return ResultCode;
}

long PricingOption(
	long LongShort,
	long CallPut,
	long OptionType,
	long CalcDate,
	long MeanStartDate,

	long MaturityDate,
	long PayDate,
	long NRateDisc,
	double* RateTermDisc,
	double* RateDisc,

	long NRateRef,
	double* RateTermRef,
	double* RateRef,
	double StockPrice,
	double StrikePrice,

	double MeanPrice,
	long DivType,
	long NDiv,
	double* DivTerm,
	double* DivRate,

	double QuantoCorr,
	long NFXVol,
	double* FXVolTerm,
	double* FXVol,
	long ImvolLocalVolFlag,

	long NParity,
	double* Parity,
	long NTermVol,
	double* TermVol,
	double* VolReshaped,

	long GreekFlag,
	long HolidayFlag,
	double* ResultPrice
)
{
	long ResultCode = 0;
	long i, j,k;
	long TypeFlag;
	double S0 = StockPrice;
	double X = StrikePrice;

	curveinfo DiscCurve(NRateDisc, RateTermDisc, RateDisc);
	curveinfo RefCurve(NRateRef, RateTermRef, RateRef);
	curveinfo DivCurve(NDiv, DivTerm, DivRate);
	curveinfo FXVolCurve(NFXVol, FXVolTerm, FXVol);
	volinfo VolMat(NParity, Parity, NTermVol, TermVol, VolReshaped);
	if (ImvolLocalVolFlag == 0)
	{
		long NTempRate = 1;
		double TempRefRateTerm[1] = { 1.0 };
		double TempRefRate[1] = { 0.0 };
		if (DivType == 2)
		{
			curveinfo TempCurve(NTempRate, TempRefRateTerm, TempRefRate);
			VolMat.set_localvol(&TempCurve, &TempCurve, 2.0, 0.01);
		}
		else
		{
			VolMat.set_localvol(&RefCurve, &DivCurve, 2.0, 0.01);
		}
		fillna_Interpolate(VolMat.LocalVolMat, VolMat.size(0), VolMat.size(1));
	}
	else
	{
		VolMat.LocalVolMat = VolMat.Vol_Matrix;
		VolMat.Term_Locvol = VolMat.Term;
		VolMat.Parity_Locvol = VolMat.Parity;
	}

	long Days_CalcToMeanStart = DayCountAtoB(CalcDate, MeanStartDate);
	long Days_CalcToMaturity = DayCountAtoB(CalcDate, MaturityDate);
	long Days_CalcToPay = DayCountAtoB(CalcDate, PayDate);

	double T_CalcToMeanStart = ((double)Days_CalcToMeanStart) / 365.0;
	double T_CalcToMaturity = ((double)Days_CalcToMaturity) / 365.0;
	double T_CalcToPay = ((double)Days_CalcToPay) / 365.0;

	if (CallPut == 0) TypeFlag = 1;
	else TypeFlag = 2;
	long down0up1flag;
	long in0out1flag;
	if (OptionType == 0)
	{
		ResultCode = BSOption(TypeFlag,S0,X,&DiscCurve,	&RefCurve,
			&DivCurve,	QuantoCorr,	&FXVolCurve,&VolMat,	DivType,	
			T_CalcToMaturity,T_CalcToPay,ResultPrice);
	}
	else if (OptionType == 1)
	{
		ResultCode = BSDigitalOption(TypeFlag, S0, X, &DiscCurve, &RefCurve,
			&DivCurve, QuantoCorr, &FXVolCurve, &VolMat, DivType,
			T_CalcToMaturity, T_CalcToPay, ResultPrice);
	}
	else if (OptionType == 2)
	{
		ResultCode = AsianOptionSimul(TypeFlag, S0, X, MeanPrice, &DiscCurve,
			&RefCurve, &DivCurve, QuantoCorr, &FXVolCurve, &VolMat,
			DivType, ImvolLocalVolFlag, Days_CalcToMeanStart, Days_CalcToMaturity, T_CalcToPay, GreekFlag, ResultPrice);
	}
	else if (OptionType == 3 || OptionType == 4)
	{
		long AmericanOptionType = 0;
		if (OptionType == 3) AmericanOptionType = 0;
		else AmericanOptionType = 1;

		ResultCode = AmericanOptionFDM(TypeFlag, AmericanOptionType, S0, X, MeanPrice,
			&DiscCurve, &RefCurve, &DivCurve, QuantoCorr, &FXVolCurve,
			&VolMat, DivType, ImvolLocalVolFlag, Days_CalcToMeanStart, Days_CalcToMaturity,
			T_CalcToPay, GreekFlag, ResultPrice);
	}
	else if (OptionType == 5)
	{
		// down and in
		down0up1flag = 0;
		in0out1flag = 0;
		ResultCode = BSBarrierOption(TypeFlag, S0, X, MeanPrice , &DiscCurve, &RefCurve,
			&DivCurve, QuantoCorr, &FXVolCurve, &VolMat, DivType,
			T_CalcToMaturity, T_CalcToPay, ResultPrice, down0up1flag, in0out1flag);
	}
	else if (OptionType == 6)
	{
		// down and out
		down0up1flag = 0;
		in0out1flag = 1;
		ResultCode = BSBarrierOption(TypeFlag, S0, X, MeanPrice, &DiscCurve, &RefCurve,
			&DivCurve, QuantoCorr, &FXVolCurve, &VolMat, DivType,
			T_CalcToMaturity, T_CalcToPay, ResultPrice, down0up1flag, in0out1flag);
	}
	else if (OptionType == 7)
	{
		// up and in
		down0up1flag = 1;
		in0out1flag = 0;
		ResultCode = BSBarrierOption(TypeFlag, S0, X, MeanPrice, &DiscCurve, &RefCurve,
			&DivCurve, QuantoCorr, &FXVolCurve, &VolMat, DivType,
			T_CalcToMaturity, T_CalcToPay, ResultPrice, down0up1flag, in0out1flag);
	}
	else if (OptionType == 8)
	{
		// up and out
		down0up1flag = 1;
		in0out1flag = 1;
		ResultCode = BSBarrierOption(TypeFlag, S0, X, MeanPrice, &DiscCurve, &RefCurve,
			&DivCurve, QuantoCorr, &FXVolCurve, &VolMat, DivType,
			T_CalcToMaturity, T_CalcToPay, ResultPrice, down0up1flag, in0out1flag);
	}
	else if (OptionType == 9)
	{
		Arithmetic_Asian_Opt_Pricing_Preprocessing(
			LongShort,
			CallPut,
			CalcDate,
			MeanStartDate,
			MaturityDate,
			PayDate,
			S0,
			X,
			MeanPrice,
			&DiscCurve,	// 할인커브
			&RefCurve,	// 레퍼런스커브
			&DivCurve,	// 배당커브
			QuantoCorr,		// Quanto COrrelation
			&FXVolCurve,	// FXVol 커브
			&VolMat,		// Vol 정보
			DivType,		// Div 배당타입
			HolidayFlag,
			0,
			NULL,
			ResultPrice
		);
	}


	k = 0;
	for (i = 0 ; i < NParity; i++)
		for (j = 0; j < NTermVol; j++)
		{
			VolReshaped[k] = VolMat.LocalVolMat[i][j];
			k += 1;
		}
	if (LongShort != 0)
	{
		for (i = 0; i < 6; i++) ResultPrice[i] *= -1.0;
	}
	return 1;
}

long ErrorCheck_OPTIONPRICING_Excel(
	long LongShort,
	long CallPut,
	long OptionType,
	long CalcDateExl,
	long MeanStartDateExl,

	long MaturityDateExl,
	long PayDateExl,
	long NRateDisc,
	double* RateTermDisc,
	double* RateDisc,

	long NRateRef,
	double* RateTermRef,
	double* RateRef,
	double StockPrice,
	double StrikePrice,

	double MeanPrice,
	long DivType,
	long NDiv,
	double* DivTerm,
	double* DivRate,

	double QuantoCorr,
	long NFXVol,
	double* FXVolTerm,
	double* FXVol,
	long ImvolLocalVolFlag,

	long NParity,
	double* Parity,
	long NTermVol,
	double* TermVol,
	double* VolReshaped,

	long GreekFlag,
	double* ResultPrice,
	char* Error
)
{
	long i, j;
	char ErrorName[100];

	if (LongShort != 0 && LongShort != 1)
	{
		strcpy_s(ErrorName, "Check LongShortFlag");
		return SaveErrorName(Error, ErrorName);
	}

	if (CallPut != 0 && CallPut != 1)
	{
		strcpy_s(ErrorName, "Check CallPutFlag");
		return SaveErrorName(Error, ErrorName);
	}

	if (OptionType < 0 || OptionType > 9)
	{
		strcpy_s(ErrorName, "Check OptionType");
		return SaveErrorName(Error, ErrorName);
	}

	if (CalcDateExl < 0)
	{
		strcpy_s(ErrorName, "PricingDate is too early");
		return SaveErrorName(Error, ErrorName);
	}


	if (CalcDateExl > PayDateExl)
	{
		strcpy_s(ErrorName, "PricingDate is too late");
		return SaveErrorName(Error, ErrorName);
	}

	if (MaturityDateExl > PayDateExl)
	{
		strcpy_s(ErrorName, "MaturityDate is too late");
		return SaveErrorName(Error, ErrorName);
	}

	if (MeanStartDateExl > MaturityDateExl)
	{
		strcpy_s(ErrorName, "MeanStartDate is too late");
		return SaveErrorName(Error, ErrorName);
	}

	if (NRateDisc < 1)
	{
		strcpy_s(ErrorName, "Check Number Disc Rate");
		return SaveErrorName(Error, ErrorName);
	}
	for (i = 0; i < NRateDisc; i++)
	{
		if (i > 0)
		{
			if (RateTermDisc[i] < RateTermDisc[i - 1])
			{
				strcpy_s(ErrorName, "Sort Disc Rate Term");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}

	if (NRateRef < 1)
	{
		strcpy_s(ErrorName, "Check Number Ref Rate");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NRateRef; i++)
	{
		if (i > 0)
		{
			if (RateTermRef[i] < RateTermRef[i - 1])
			{
				strcpy_s(ErrorName, "Sort Ref Rate Term");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}

	if (NDiv < 1)
	{
		strcpy_s(ErrorName, "Check Number Div Rate");
		return SaveErrorName(Error, ErrorName);
	}
	for (i = 0; i < NDiv; i++)
	{
		if (i > 0)
		{
			if (DivTerm[i] < DivTerm[i - 1])
			{
				strcpy_s(ErrorName, "Sort Div Term");
				return SaveErrorName(Error, ErrorName);
			}
		}	
	}

	if (DivType < 0 || DivType > 2)
	{
		strcpy_s(ErrorName, "Check Dividend Type");
		return SaveErrorName(Error, ErrorName);
	}

	if (NFXVol < 1)
	{
		strcpy_s(ErrorName, "Check Number FXVol Rate");
		return SaveErrorName(Error, ErrorName);
	}
	for (i = 0; i < NFXVol; i++)
	{
		if (i > 0)
		{
			if (FXVolTerm[i] < FXVolTerm[i - 1])
			{
				strcpy_s(ErrorName, "Sort FXVol Term");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}

	if (ImvolLocalVolFlag < 0 || ImvolLocalVolFlag > 4)
	{
		strcpy_s(ErrorName, "Check Vol Type");
		return SaveErrorName(Error, ErrorName);
	}

	if (NParity < 1)
	{
		strcpy_s(ErrorName, "Check Vol Parity Number");
		return SaveErrorName(Error, ErrorName);
	}

	if (NTermVol < 1)
	{
		strcpy_s(ErrorName, "Check Vol Term Number");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NParity; i++)
	{
		if (i > 0)
		{
			if (Parity[i] < Parity[i - 1])
			{
				strcpy_s(ErrorName, "Sort Parity");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}
	for (i = 0; i < NTermVol; i++)
	{
		if (i > 0)
		{
			if (TermVol[i] < TermVol[i - 1])
			{
				strcpy_s(ErrorName, "Sort Vol Term");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}

	long k = 0;
	for (i = 0 ; i < NParity; i++)
		for (j = 0; j < NTermVol; j++)
		{
			if (VolReshaped[k] < 0.0)
			{
				strcpy_s(ErrorName, "Vol Must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			k += 1;
		}
	return 1;
}

DLLEXPORT(long) OPTIONPRICING_Excel(
	long LongShort,				// 매수0 매도1
	long CallPut,				// 콜0 풋1
	long OptionType,			// 0 바닐라 1디지털 2아시안 3아메리칸 4아메리칸디지털 5Down&In 6Down&Out 7Up&In 8Up&Out
	long CalcDateExl,			// 계산일 엑셀날짜
	long MeanStartDateExl,		// 평균시작일

	long MaturityDateExl,		// 만기일
	long PayDateExl,			// 지급일
	long NRateDisc,				// 할인커브개수
	double* RateTermDisc,		// 할인커브Term
	double* RateDisc,			// 할인커브Rate

	long NRateRef,				// 레퍼커브개수
	double* RateTermRef,		// 레퍼커브Term
	double* RateRef,			// 레퍼커브Rate
	double StockPrice,			// 주식가격
	double StrikePrice,			// 행사가격

	double MeanPrice,			// 아시안옵션의 경우 현재까지 평균가격 또는 배리어옵션의 경우 배리어레벨
	long DivType,				// 배당타입
	long NDiv,					// 배당개수
	double* DivTerm,			// 배당Term Act/365로 입력
	double* DivRate,			// 배당Rate, 이산배당의 경우 배당액

	double QuantoCorr,			// 콴토상관계수
	long NFXVol,				// FX Vol 개수
	double* FXVolTerm,			// FX Vol Term
	double* FXVol,				// FX Vol
	long ImvolLocalVolFlag,		// 0: Imvol입력->Local vol계산, 1:LocalVol, 2:SImple Vol, 3:SABR Beta 1.0, 4:SABR Beta 0.5

	long NParity,				// Parity 개수
	double* Parity,				// Parity(Moneyness)
	long NTermVol,				// 입력 Vol 만기 개수
	double* TermVol,			// 입력 Vol Term
	double* VolReshaped,		// 입력 Vol Reshaped

	long GreekFlag,				// Greek산출
	double* ResultPrice,		// 0 가격, 1 델타, 2감마, 3베가, 4세타, 5로
	double* SABR_Params,		// 길이 : (입력 Vol 만기 개수) x 3 
	char* Error,				
	double* RMSPE,				// 길이 1 RMSPE

	long TextFlag,
	long HolidayFlag
)
{
	long i, j;
	long ResultCode;
	long ErrorCode;

	ErrorCode = ErrorCheck_OPTIONPRICING_Excel(
		LongShort, CallPut, OptionType, CalcDateExl, MeanStartDateExl,
		MaturityDateExl, PayDateExl, NRateDisc, RateTermDisc, RateDisc,
		NRateRef, RateTermRef, RateRef, StockPrice, StrikePrice,
		MeanPrice, DivType, NDiv, DivTerm, DivRate,
		QuantoCorr, NFXVol, FXVolTerm, FXVol, ImvolLocalVolFlag,
		NParity, Parity, NTermVol, TermVol, VolReshaped,
		GreekFlag, ResultPrice, Error);
	if (ErrorCode < 0) return ErrorCode;
	double SABRBeta = 1.0;

	char CalcFunctionName[] = "OPTIONPRICING_Excel";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "Long0Short1", LongShort);
		DumppingTextData(CalcFunctionName, SaveFileName, "Call0Put1", CallPut);
		DumppingTextData(CalcFunctionName, SaveFileName, "OptionType", OptionType);
		DumppingTextData(CalcFunctionName, SaveFileName, "CalcDateExl", CalcDateExl);
		DumppingTextData(CalcFunctionName, SaveFileName, "MeanStartDateExl", MeanStartDateExl);
		DumppingTextData(CalcFunctionName, SaveFileName, "MaturityDateExl", MaturityDateExl);
		DumppingTextData(CalcFunctionName, SaveFileName, "PayDateExl", PayDateExl);

		DumppingTextData(CalcFunctionName, SaveFileName, "NRateDisc", NRateDisc);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateTermDisc", NRateDisc, RateTermDisc);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateDisc", NRateDisc, RateDisc);
		DumppingTextData(CalcFunctionName, SaveFileName, "NRateRef", NRateRef);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateTermRef", NRateRef, RateTermRef);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateRef", NRateRef, RateRef);

		DumppingTextData(CalcFunctionName, SaveFileName, "StockPrice", StockPrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "StrikePrice", StrikePrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "MeanPrice", MeanPrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "DivType", DivType);
		DumppingTextData(CalcFunctionName, SaveFileName, "NDiv", NDiv);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivTerm", NDiv, DivTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivRate", NDiv, DivRate);
		DumppingTextData(CalcFunctionName, SaveFileName, "QuantoCorr", QuantoCorr);
		DumppingTextData(CalcFunctionName, SaveFileName, "NFXVol", NFXVol);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "FXVolTerm", NFXVol, FXVolTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "FXVol", NFXVol, FXVol);
		DumppingTextData(CalcFunctionName, SaveFileName, "ImvolLocalVolFlag", ImvolLocalVolFlag);

		DumppingTextData(CalcFunctionName, SaveFileName, "NParity", NParity);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Parity", NParity, Parity);
		DumppingTextData(CalcFunctionName, SaveFileName, "NTermVol", NTermVol);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermVol", NTermVol, TermVol);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Vol", NParity, NTermVol, VolReshaped);

		DumppingTextData(CalcFunctionName, SaveFileName, "GreekFlag", GreekFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "HolidayFlag", HolidayFlag);
	}


	if (ImvolLocalVolFlag == 3 || ImvolLocalVolFlag == 4)
	{
		if (DivType == 2)
		{
			NDiv = 0;
		}
		long CalcLocalVolFlag = 0; // 로컬볼은 나중에계산
		if (ImvolLocalVolFlag == 3) SABRBeta = 1.0;
		else SABRBeta = 0.5;

		double* Futures = (double*)malloc(sizeof(double) * NTermVol);
		double* TempVol = (double*)malloc(sizeof(double) * NTermVol * NParity);
		if (NParity >= 4 && NTermVol >= 4)
		{
			ImvolLocalVolFlag = 0;
			//////////////////////
			// SABR Calibration //
			//////////////////////
			ResultCode = SABR_Vol(NRateDisc, RateTermDisc, RateDisc, NDiv, DivTerm,
				DivRate, NTermVol,TermVol, NParity, Parity,
				VolReshaped, CalcLocalVolFlag, SABRBeta, VolReshaped, TempVol,
				SABR_Params, Futures, RMSPE);
		}
		free(Futures);
		free(TempVol);
	}

	long CalcDate, MeanStartDate, MaturityDate, PayDate;
	if (CalcDateExl < 19000101) CalcDate = ExcelDateToCDate(CalcDateExl);
	else CalcDate = CalcDateExl;
	if (MeanStartDateExl < 19000101) MeanStartDate = ExcelDateToCDate(MeanStartDateExl);
	else MeanStartDate = MeanStartDateExl;
	if (MaturityDateExl < 19000101) MaturityDate = ExcelDateToCDate(MaturityDateExl);
	else MaturityDate = MaturityDateExl;
	if (PayDateExl < 19000101) PayDate = ExcelDateToCDate(PayDateExl);
	else PayDate = PayDateExl;

	ResultCode = PricingOption(LongShort, CallPut, OptionType, CalcDate, MeanStartDate,
		MaturityDate, PayDate, NRateDisc, RateTermDisc, RateDisc,
		NRateRef, RateTermRef, RateRef, StockPrice, StrikePrice,
		MeanPrice, DivType, NDiv, DivTerm, DivRate,
		QuantoCorr, NFXVol, FXVolTerm, FXVol, ImvolLocalVolFlag,
		NParity, Parity, NTermVol, TermVol, VolReshaped,
		GreekFlag, HolidayFlag, ResultPrice);

	return 1;
}