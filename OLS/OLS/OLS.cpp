#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <crtdbg.h>
#include "Util.h"

#ifndef max
#define max(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef min
#define min(a,b)            (((a) < (b)) ? (a) : (b))
#endif


void TempFunc(double** x_before_const, long* y, long nvariables, long num_data, double* beta_0, double alpha_0, long method, double* ResultArray)
{
	long i;
	long nbeta = nvariables + 1;
	LOGIT LOGITClass(x_before_const, y, nvariables, num_data, beta_0, alpha_0, method);
	for (i = 0 ; i < nbeta; i++) ResultArray[i] = LOGITClass.beta[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + nbeta] = LOGITClass.std_beta[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + 2 * nbeta] = LOGITClass.tvalue[i];
	ResultArray[3 * nbeta] = LOGITClass.rsquared;
	ResultArray[3 * nbeta + 1] = LOGITClass.LL;
	ResultArray[3 * nbeta + 2] = LOGITClass.LL_null;
	ResultArray[3 * nbeta + 3] = LOGITClass.AIC;
	ResultArray[3 * nbeta + 4] = LOGITClass.BIC;
	ResultArray[3 * nbeta + 5] = LOGITClass.converge;
	for (i = 0 ; i < nbeta; i++) ResultArray[3 * nbeta + 5 + i] = LOGITClass.p[i];
}

DLLEXPORT(long) MLE_Estimate(
	double* x_reshape, 
	double* y, 
	double* beta_0,
	long ndata, 
	long nvariables,
	double* ResultArray, 
	double alpha_0, 
	long method
	)
{
	//_CrtSetBreakAlloc(3427);
	long i, j;
	long shape[2] = { ndata, nvariables };
	double** x_before_const = DataReshape(x_reshape, shape);
	long nbeta = nvariables + 1;

	long* yvar = (long*)malloc(sizeof(long) * ndata);
	for (i = 0; i < ndata; i++) yvar[i] = (long)(y[i] + 0.0001);

	TempFunc(x_before_const, yvar, nvariables, ndata, beta_0, alpha_0, method,ResultArray);
	for (i = 0; i < ndata; i++) free(x_before_const[i]);
	free(x_before_const);

	free(yvar);
	_CrtDumpMemoryLeaks();
	return 1;
}

void TempFuncOLS(double** x, double* y, long num_data, long nvariables, long NeweyWestLag, double* ResultArray)
{
	long i;
	long nbeta = nvariables + 1;
	long n = nbeta;
	OLS OLSClass(x, y, num_data, nvariables, NeweyWestLag);
	for (i = 0; i < nbeta; i++) ResultArray[i] = OLSClass.beta[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + nbeta] = OLSClass.std_B[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + 2 * nbeta] = OLSClass.t_value[i];
	ResultArray[3 * nbeta] = OLSClass.rsquared;
	ResultArray[3 * nbeta + 1] = OLSClass.rsquared_adj;
	ResultArray[3 * n + 2] = OLSClass.resid_std;
	ResultArray[n * 3 + 3] = OLSClass.loglikelihood;
	ResultArray[n * 3 + 4] = OLSClass.Df_model;
	ResultArray[n * 3 + 5] = OLSClass.Df_res;
	ResultArray[n * 3 + 6] = OLSClass.Fstatistic;
	ResultArray[n * 3 + 7] = OLSClass.AIC;
	ResultArray[n * 3 + 8] = OLSClass.BIC;
	ResultArray[n * 3 + 9] = OLSClass.durbin_watson;
	ResultArray[n * 3 + 10] = OLSClass.sig;
	for (i = 0; i < num_data; i++) ResultArray[n * 3 + 11 + i] = OLSClass.estimated[i];
	for (i = 0; i < num_data; i++) ResultArray[n * 3 + 11 + num_data + i] = OLSClass.resid[i];
	ResultArray[n * 3 + 11 + 2 * num_data] = OLSClass.Skew;
	ResultArray[n * 3 + 11 + 2 * num_data + 1] = OLSClass.Kurt;
	ResultArray[n * 3 + 11 + 2 * num_data + 2] = OLSClass.JB;
	ResultArray[n * 3 + 11 + 2 * num_data + 3] = OLSClass.centered_tss;
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + i] = OLSClass.p[i];
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + nbeta + i] = OLSClass.std_B_NeweyWest[i];
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + 2 * nbeta + i] = OLSClass.p_neweywest[i];
}

DLLEXPORT(long) OLS_Estimate(
	double* x_reshape,
	double* y,
	long ndata,
	long nvariables,
	long NeweyWestLag,
	double* ResultArray)
{
	long i, j;
	long shape[2] = { ndata, nvariables };
	double** x_before_const = DataReshape(x_reshape, shape);
	TempFuncOLS(x_before_const, y, ndata, nvariables, NeweyWestLag, ResultArray);

	for (i = 0; i < ndata; i++) free(x_before_const[i]);
	free(x_before_const);

	//_CrtDumpMemoryLeaks();
	return 1;
}

