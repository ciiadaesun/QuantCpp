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

////////////////////////////////////
// 여기서부터 Logistic Regression //
////////////////////////////////////

double log_logistic_func_scalar(double XB, long y)
{
	double prob, logprob;
	if ((XB < 35.0) && (XB > -35.0))
	{
		prob = 1.0 / (1.0 + exp(-XB));
		if (y == 0) logprob = log(1.0 - prob);
		else logprob = log(prob);
	}
	else if (XB >= 35.0)
	{
		if (y == 0) logprob = -XB;
		else logprob = 1.0E-16;
	}
	else
	{
		if (y == 0) logprob = 1.0E-16;
		else logprob = XB;
	}
	return logprob;
}

double log_logistic_func(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j;
	double XB;
	double s = 0.0;
	for (i = 0; i < ndata; i++)
	{
		XB = 0.0;
		for (j = 0; j < nbeta; j++) XB += x[i][j] * beta[j];
		s += log_logistic_func_scalar(XB, y[i]);
	}
	return s;
}

double* log_logistic_func_vector(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j;
	double* ResultArray = (double*)malloc(sizeof(double) * ndata);
	double XB;
	for (i = 0; i < ndata; i++)
	{
		XB = 0.0;
		for (j = 0; j < nbeta; j++) XB += x[i][j] * beta[j];
		ResultArray[i] = log_logistic_func_scalar(XB, y[i]);
	}
	return ResultArray;
}

double* ProbFun(double** x, double* beta, long ndata, long nbeta)
{
	long i, j;
	double xb = 0.0;
	double* ResultArray = (double*)malloc(sizeof(double) * ndata);
	for (i = 0; i < ndata; i++)
	{
		xb = 0.0;
		for (j = 0; j < nbeta; j++) xb += x[i][j] * beta[j];
		ResultArray[i] = 1.0 / (1.0 + exp(-xb));
	}
	return ResultArray;
}

double* ErrorFunc(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j;
	double xb;
	double* ResultArray = (double*)malloc(sizeof(double) * ndata);
	for (i = 0; i < ndata; i++)
	{
		xb = 0.0;
		for (j = 0; j < nbeta; j++) xb += x[i][j] * beta[j];
		ResultArray[i] = -log_logistic_func_scalar(xb, y[i]);
	}
	return ResultArray;
}

double ErrorFuncSum(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i;
	double s = 0.0;
	double* Error = ErrorFunc(x, y, beta, ndata, nbeta);
	for (i = 0; i < ndata; i++) s += Error[i];
	free(Error);
	return s;
}

double** Error_Jacov(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j;
	double* Prob = ProbFun(x, beta, ndata, nbeta);
	double** ResultMatrix = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) ResultMatrix[i] = (double*)malloc(sizeof(double) * nbeta);
	
	double p;
	for (i = 0; i < ndata; i++)
	{
		p = Prob[i];
		for (j = 0; j < nbeta; j++)
		{
			ResultMatrix[i][j] = (p - (double)y[i]) * x[i][j];
		}
	}
	free(Prob);
	return ResultMatrix;
}

double** Error_Hessian(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j, k;
	double s = 0.0;
	double FixA, FixB, FixC;
	double* p = ProbFun(x, beta, ndata, nbeta);

	double** ResultMatrix = (double**)malloc(sizeof(double*) * nbeta);
	for (i = 0; i < nbeta; i++) ResultMatrix[i] = (double*)malloc(sizeof(double) * nbeta);

	for (i = 0; i < nbeta; i++)
	{
		for (j = 0; j < nbeta; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = x[k][i];
				FixB = x[k][j];
				FixC = p[k] * (1.0-p[k]);
				s += FixA * FixB * FixC;
			}
			ResultMatrix[i][j] = s;
		}
	}

	free(p);
	return ResultMatrix;
}

double** Error_Inv_Hessian(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j, k;
	double s = 0.0;
	double FixA, FixB, FixC;
	double* p = ProbFun(x, beta, ndata, nbeta);

	double** ResultMatrix = (double**)malloc(sizeof(double*) * nbeta);
	for (i = 0; i < nbeta; i++) ResultMatrix[i] = (double*)malloc(sizeof(double) * nbeta);

	for (i = 0; i < nbeta; i++)
	{
		for (j = 0; j < nbeta; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = x[k][i];
				FixB = x[k][j];
				FixC = p[k] * (1.0 - p[k]);
				s += FixA * FixB * FixC;
			}
			ResultMatrix[i][j] = s;
		}
	}

	double** InvResultMatrix = (double**)malloc(sizeof(double*) * nbeta);
	for (i = 0; i < nbeta; i++) InvResultMatrix[i] = (double*)malloc(sizeof(double) * nbeta);
	long matshape[2] = { nbeta, nbeta };
	matrixinverse(ResultMatrix, matshape, InvResultMatrix);

	free(p);
	for (i = 0; i < nbeta; i++) free(ResultMatrix[i]);
	free(ResultMatrix);

	return InvResultMatrix;
}

double* Error_Sum_Jacov(double** x, long* y, double* beta, long ndata, long nbeta)
{
	long i, j;
	double* Prob = ProbFun(x, beta, ndata, nbeta);
	double** ResultMatrix = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) ResultMatrix[i] = (double*)malloc(sizeof(double) * nbeta);

	double p;
	for (i = 0; i < ndata; i++)
	{
		p = Prob[i];
		for (j = 0; j < nbeta; j++)
		{
			ResultMatrix[i][j] = (p - (double)y[i]) * x[i][j];
		}
	}

	double* ResultArray = (double*)malloc(sizeof(double) * nbeta);
	double s = 0.0;

	for (j = 0; j < nbeta; j++)
	{
		s = 0.0;
		for (i = 0; i < ndata; i++)
		{
			s += ResultMatrix[i][j];
		}
		ResultArray[j] = s;
	}

	free(Prob);
	for (i = 0; i < ndata; i++) free(ResultMatrix[i]);
	free(ResultMatrix);

	return ResultArray;
}

long JT_Res(double** Jacov, long shape_Jacov[2], double* Res, double* JT_Res_Array)
{
	long i, j, k;
	long p = shape_Jacov[1];
	long n = shape_Jacov[0];
	double s = 0.0;
	for (i = 0; i < p; i++)
	{
		s = 0.0;
		for (j = 0; j < n; j++)
		{
			s += Jacov[j][i] * Res[j];
		}
		JT_Res_Array[i] = s;
	}
	return 1;
}

double** DataReshape(double* data, long* shape)
{
	long i, j, k;
	double** DataReshaped = (double**)malloc(sizeof(double*) * shape[0]);
	for (i = 0; i < shape[0]; i++) DataReshaped[i] = (double*)malloc(sizeof(double) * shape[1]);

	k = 0;
	for (i = 0; i < shape[0]; i++)
	{
		for (j = 0; j < shape[1]; j++)
		{
			DataReshaped[i][j] = data[k];
			k++;
		}
	}
	return DataReshaped;
}

long MLE_Logistic_Estimate(double** x, long* y, double* beta_0, long ndata, long nbeta, double* ResultArray, double alpha_0 = 0.001, long method = 2)
{
	long i, j, k;
	double* theta = (double*)malloc(sizeof(double) * nbeta);							// 할당 1
	double alpha = alpha_0;
	for (i = 0; i < nbeta; i++) theta[i] = beta_0[i];

	double* gradalpha = (double*)malloc(sizeof(double) * nbeta);						// 할당 2
	for (i = 0; i < nbeta; i++) gradalpha[i] = alpha_0;

	double* min_theta = (double*)malloc(sizeof(double) * nbeta);						// 할당 3
	for (i = 0; i < nbeta; i++) min_theta[i] = theta[i];
	double* prev_theta = (double*)malloc(sizeof(double) * nbeta);						// 할당 4
	for (i = 0; i < nbeta; i++) prev_theta[i] = theta[i];

	double min_value = 99999999999.9;
	double firsterr = 99999999999.9;

	long n_notchange = 0;
	double pctchangelimit = 0.2;
	long converge = 0;
	long nloop = 100;
	double value, residsum, deltathetasum;
	double** jacov;
	long shape_jacov[2] = { ndata, nbeta };
	double* resid;

	long shape_jTj[2] = { nbeta, nbeta };
	double** jTj = (double**)malloc(sizeof(double*) * nbeta);							// 할당 5
	for (i = 0; i < nbeta; i++) jTj[i] = (double*)malloc(sizeof(double) * nbeta);		

	double** inv_jTj = (double**)malloc(sizeof(double*) * nbeta);						// 할당 6						
	for (i = 0; i < nbeta; i++) inv_jTj[i] = (double*)malloc(sizeof(double) * nbeta);

	double* JTRes = (double*)malloc(sizeof(double) * nbeta);							// 할당 7
	double* deltatheta = (double*)malloc(sizeof(double) * nbeta);						// 할당 8
	double* tenpercentchange = (double*)malloc(sizeof(double) * nbeta);					// 할당 9
	double* temptheta = (double*)malloc(sizeof(double) * nbeta);						// 할당 10
	double thetachange = 0.0;
	for (i = 0; i < nloop; i++)
	{
		value = -log_logistic_func(x, y, theta, ndata, nbeta);					
		jacov = Error_Jacov(x, y, theta, ndata, nbeta);							// 반복문 내부할당 1
		resid = ErrorFunc(x, y, theta, ndata, nbeta);							// 반복문 내부할당 2

		if (i == 0)
		{
			firsterr = 0.0;
			for (j = 0; j < ndata; j++) firsterr += resid[j];
		}

		if (value < min_value)
		{
			for (j = 0; j < nbeta; j++) min_theta[j] = theta[j];
			min_value = value;
			if (method == 3) alpha = alpha_0;
			else if (method == 4)
			{
				alpha = max(1.0E-10, 0.1 * alpha);
				residsum = 0.0;
				for (j = 0; j < ndata; j++) residsum += resid[j];
				if (fabs(residsum) < fabs(firsterr) * 0.001)
				{
					for (j = 0; j < ndata; j++) free(jacov[j]);
					free(jacov);
					free(resid);

					break;
				}
			}
		}

		if (method == 1)
		{
			// 가우스뉴턴
			JT_Res(jacov, shape_jacov, resid, JTRes);
			XprimeDotX(jacov, shape_jacov, jTj);
			gaussian_elimination_autocopy(jTj, JTRes, deltatheta, nbeta);

			residsum = 0.0;
			for (j = 0; j < ndata; j++) residsum += resid[j];

			for (j = 0; j < nbeta; j++)
			{
				if (fabs(theta[j]) > 1.0E-10) tenpercentchange[j] = fabs(theta[j]) * pctchangelimit;
				else tenpercentchange[j] = 1.0E-10;

				if (fabs(deltatheta[j]) < tenpercentchange[j]) deltatheta[j] = deltatheta[j];
				else
				{
					if (deltatheta[j] >= 0.0) deltatheta[j] = tenpercentchange[j];
					else deltatheta[j] = -tenpercentchange[j];
				}
			}
			for (j = 0; j < nbeta; j++)
			{
				for (k = 0; k < nbeta; k++)
				{
					if (k != j) temptheta[k] = theta[k];
					else temptheta[k] = theta[k] - deltatheta[k];
				}
				
				if (fabs(residsum) < fabs(ErrorFuncSum(x, y, theta, ndata, nbeta))) deltatheta[j] = 0.0;
			}

			deltathetasum = 0.0;
			for (j = 0; j < nbeta; j++) deltathetasum += deltatheta[j];

			if (deltathetasum == 0.0) n_notchange += 1;
			else
			{
				n_notchange = 0;
				pctchangelimit = 0.2;
			}

			if (n_notchange >= 2) pctchangelimit *= 0.8;
		}
		else if (method == 2)
		{
			double** invHess = Error_Inv_Hessian(x, y, theta, ndata, nbeta);
			double* ErrSumJcv = Error_Sum_Jacov(x, y, theta, ndata, nbeta);
			double ab = 0.0;
			for (j = 0; j < nbeta; j++)
			{
				ab = 0.0;
				for (k = 0; k < nbeta; k++) ab += invHess[j][k] * ErrSumJcv[k];
				deltatheta[j] = ab;
			}
			for (j = 0; j < nbeta; j++) free(invHess[j]);
			free(invHess);
			free(ErrSumJcv);
		}
		else if (method == 3)
		{
			for (j = 0; j < nbeta; j++)
			{
				double ab = 0.0;
				for (k = 0; k < ndata; k++) ab += jacov[k][j] * resid[k];
				deltatheta[j] = ab * gradalpha[j] * 2.0;
			}
		}
		else if (method == 4)
		{
			// 가우스뉴턴
			JT_Res(jacov, shape_jacov, resid, JTRes);
			XprimeDotX(jacov, shape_jacov, jTj);
			for (j = 0; j < nbeta; j++) jTj[j][j] = jTj[j][j] + alpha;
			gaussian_elimination_autocopy(jTj, JTRes, deltatheta, nbeta);

			residsum = 0.0;
			for (j = 0; j < ndata; j++) residsum += resid[j];

			for (j = 0; j < nbeta; j++)
			{
				if (fabs(theta[j]) > 1.0E-10) tenpercentchange[j] = fabs(theta[j]) * pctchangelimit;
				else tenpercentchange[j] = 1.0E-10;

				if (fabs(deltatheta[j]) < tenpercentchange[j]) deltatheta[j] = deltatheta[j];
				else
				{
					if (deltatheta[j] >= 0.0) deltatheta[j] = tenpercentchange[j];
					else deltatheta[j] = -tenpercentchange[j];
				}
			}
			for (j = 0; j < nbeta; j++)
			{
				for (k = 0; k < nbeta; k++)
				{
					if (k != j) temptheta[k] = theta[k];
					else temptheta[k] = theta[k] - deltatheta[k];
				}

				if (fabs(residsum) < fabs(ErrorFuncSum(x, y, theta, ndata, nbeta))) deltatheta[j] = 0.0;
			}

			deltathetasum = 0.0;
			for (j = 0; j < nbeta; j++) deltathetasum += deltatheta[j];

			if (deltathetasum == 0.0) n_notchange += 1;
			else
			{
				n_notchange = 0;
				pctchangelimit = 0.2;
			}

			if (n_notchange >= 2) pctchangelimit *= 0.8;
		}
		for (j = 0; j < nbeta; j++) theta[j] = theta[j] - deltatheta[j];

		if (i > 0)
		{
			if ((method == 1) || (method == 3) || (method == 4) && (n_notchange > 10))
			{
				for (j = 0; j < ndata; j++) free(jacov[j]);
				free(jacov);
				free(resid);
				break;
			}
			else if (method == 2)
			{
				thetachange = 0.0;
				for (j = 0; j < nbeta; j++) thetachange += (theta[j] - prev_theta[j]) / prev_theta[j];
				if (fabs(thetachange) < 0.000000001)
				{
					for (j = 0; j < ndata; j++) free(jacov[j]);
					free(jacov);
					free(resid);
					break;
				}
			}
		}

		for (j = 0; j < nbeta; j++) prev_theta[j] = theta[j];

		for (j = 0; j < ndata; j++) free(jacov[j]);
		free(jacov);
		free(resid);
	}
	for (j = 0; j < nbeta; j++) ResultArray[j] = min_theta[j];
	ResultArray[nbeta] = min_value;

	if (i < nloop - 1)
	{
		ResultArray[nbeta + 1] = 1.0;
	}
	free(theta);													// 할당 1
	free(gradalpha);												// 할당 2
	free(min_theta);												// 할당 3
	free(prev_theta);												// 할당 4
	for (i = 0; i < nbeta; i++) free(jTj[i]);						// 할당 5
	free(jTj);
	for (i = 0; i < nbeta; i++) free(inv_jTj[i]);					// 할당 6
	free(inv_jTj);
	free(JTRes);													// 할당 7
	free(deltatheta);												// 할당 8
	free(tenpercentchange);											// 할당 9
	free(temptheta);												// 할당 10
	return 1;
}

class LOGIT {
private:

public:
	double* beta;
	long ndata;
	long nbeta;
	double LL;
	double LL_null;
	double* std_beta;
	double rsquared;
	double* tvalue;
	double AIC;
	double BIC;
	double** x;
	double ResultArray[10];
	long converge;

	LOGIT(double** x_before_const, long* y, long nvariables, long num_data, double* beta_0, double alpha_0 = 0.001, long method = 2)
	{
		long i, j;

		nbeta = nvariables + 1;
		ndata = num_data;

		x = (double**)malloc(sizeof(double*) * num_data);
		for (i = 0; i < num_data; i++) x[i] = (double*)malloc(sizeof(double) * nbeta);

		for (i = 0; i < num_data; i++)
		{
			for (j = 0; j < nbeta; j++)
			{
				if (j == 0) x[i][j] = 1.0;
				else x[i][j] = x_before_const[i][j - 1];
			}
		}
		MLE_Logistic_Estimate(x, y, beta_0, num_data, nbeta, ResultArray, alpha_0, method);
		beta = (double*)malloc(sizeof(double) * nbeta);
		std_beta = (double*)malloc(sizeof(double) * nbeta);
		tvalue = (double*)malloc(sizeof(double) * nbeta);

		for (i = 0; i < nbeta; i++) beta[i] = ResultArray[i];
		LL = ResultArray[nbeta];
		converge = (long)(ResultArray[nbeta + 1] + 0.0001);

		double** ErrInvHess = Error_Inv_Hessian(x, y, beta, ndata, nbeta);
		for (i = 0; i < nbeta; i++) std_beta[i] = sqrt(ErrInvHess[i][i]);
		for (i = 0; i < nbeta; i++) tvalue[i] = beta[i] / std_beta[i];

		double ResultArray2[10];
		MLE_Logistic_Estimate(x, y, beta_0, num_data, 1, ResultArray2, 0.001, method);
		LL_null = ResultArray2[1];
		rsquared = 1.0 - LL / LL_null;
		AIC = -2.0 * LL + (double)(2 * nbeta);
		BIC = -2.0 * LL + ((double)nbeta) * log((double)ndata);

		for (i = 0; i < nbeta; i++) free(ErrInvHess[i]);
		free(ErrInvHess);
	}

	~LOGIT()
	{
		long i;
		for (i = 0; i < ndata; i++) free(x[i]);
		free(x);
		free(beta);
		free(std_beta);
		free(tvalue);
	}
};

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

}

DLLEXPORT(long) MLE_Estimate(
	double* x_reshape, 
	double* y, 
	double* beta_0,
	long ndata, 
	long nvariables,
	double* ResultArray, 
	double alpha_0, 
	long method)
{
	//_CrtSetBreakAlloc(3427);
	long i, j;
	long shape[2] = { ndata, nvariables };
	double** x_before_const = DataReshape(x_reshape, shape);
	long nbeta = nvariables + 1;

	long* yvar = (long*)malloc(sizeof(long) * ndata);
	for (i = 0; i < ndata; i++) yvar[i] = (long)(y[i] + 0.0001);

	TempFunc(x_before_const, yvar, nvariables, ndata, beta_0, alpha_0, method, ResultArray);
	for (i = 0; i < ndata; i++) free(x_before_const[i]);
	free(x_before_const);

	free(yvar);
	_CrtDumpMemoryLeaks();
	return 1;
}


/*
long main2()
{
	long i;

	long X_Shape[2] = { 15, 2 };
	double** X = (double**)malloc(sizeof(double*) * (X_Shape[0]));
	for (i = 0; i < X_Shape[0]; i++) X[i] = (double*)malloc(sizeof(double) *  X_Shape[1]);
	X[0][0] = 0.0040;
	X[0][1] = -0.0431;

	X[1][0] = 0.0414;
	X[1][1] = 0.0520;
	
	X[2][0] = -0.0057;
	X[2][1] = -0.0373;

	X[3][0] = -0.0141;
	X[3][1] = -0.0162;

	X[4][0] = 0.0072;
	X[4][1] = 0.0135;

	X[5][0] = -0.0095;
	X[5][1] = 0.0438;

	X[6][0] = -0.0026;
	X[6][1] = -0.0209;
	X[7][0] = 0.0043;
	X[7][1] = 0.0750 ;
	X[8][0] = -0.0036;
	X[8][1] = 0.0077;

	X[9][0] = 0.0135;
	X[9][1] = -0.0599;
	X[10][0] = -0.0021;
	X[10][1] = -0.0515;

	X[11][0] = 0.0479;
	X[11][1] = -0.0047;

	X[12][0] = -0.0121;
	X[12][1] = -0.0296; 

	X[13][0] = -0.0107;
	X[13][1] = 0.0250;

	X[14][0] = -0.0128;
	X[14][1] = 0.1221;

	double* Y = (double*)malloc(sizeof(double) * (X_Shape[0]));
	Y[0] = 0.0361;
	Y[1] = 0.0273;
	Y[2] = 0.0280;
	Y[3] = 0.0363;
	Y[4] = 0.0213;
	Y[5] = 0.0318;
	Y[6] = -0.0003; 
	Y[7] = 0.0401;  
	Y[8] = -0.0050; 
	Y[9] = 0.0410;
	Y[10] = 0.0174;
	Y[11] = 0.0326;
	Y[12] = 0.0069;
	Y[13] = 0.0079; 
	Y[14] = 0.0134;
	
	long nvariables = 2;
	long ndata = 15;
	long n = nvariables + 1;

	OLSestimate OLSClass(X, Y, ndata, nvariables);
	OLSClass.summary();
	
	for (i = 0; i < X_Shape[0]; i++) free(X[i]);
	free(X);
	free(Y);

	return 1;
}

long main()
{
	main2();
	_CrtDumpMemoryLeaks();
}
*/