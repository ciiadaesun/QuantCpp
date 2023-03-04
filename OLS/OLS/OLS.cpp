#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <crtdbg.h>

#ifndef max
#define max(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef min
#define min(a,b)            (((a) < (b)) ? (a) : (b))
#endif

// MatrixA와 MatrixB를 곱하여 ResultMatrix에 저장한다.
void Dot2dArray(
	double** MatrixA,				// 매트릭스 A 
	long shape_A[2],				// 매트릭스 A의 Shape = [N, M] 
	double** MatrixB,				// 매트릭스 B
	long shape_B[2],				// 매트릭스 B의 Shape = [M, H]
	double** ResultMatrix			// 매트릭스 결과값 Shape = [N, H]
)
{
	long p, q, i, j, k, maxk;
	double s;
	p = shape_A[0];
	q = shape_B[1];

	maxk = shape_A[1];
	for (i = 0; i < p; i++)
	{
		for (j = 0; j < q; j++)
		{
			s = 0.0;
			for (k = 0; k < maxk; k++)
			{
				s += MatrixA[i][k] * MatrixB[k][j];;
			}
			ResultMatrix[i][j] = s;
		}
	}
}

// X'X 계산
void XprimeDotX(
	double** X,			// 매트릭스 X
	long ShapeX[2],		// 매트릭스 X의 Shape = [N, M] 
	double** XpDotX		// 매트릭스 X'X를 저장할 임시Matrix (Shape = M, M)
)
{
	long i, j, k;
	long ShapeXpX[2] = { ShapeX[1], ShapeX[1] };
	long n = ShapeX[0];
	long idx_row;
	long idx_col;

	double s = 0.0;
	double a, b;
	for (i = 0; i < ShapeXpX[0]; i++)
		for (j = 0; j < ShapeXpX[1]; j++)
		{
			s = 0.0;
			for (k = 0; k < n; k++)
			{
				s += X[k][i] * X[k][j];
			}
			XpDotX[i][j] = s;
		}
}

///////////////////////////////////////////////////////////
// MyMatrix * UnKnown = Known 이고
// Shape(MyMatrix) = (n, n), Shape(Known) = (n, ) 일 때
// UnKnown를 역산한다. Shape(UnKnown) = (n, )
// 이 떄 MyMatrix와 KnownRHS가 바뀌므로 주의
///////////////////////////////////////////////////////////
void gaussian_elimination(double** MyMatrix, double* KnownRHS, double* UnKnown, long n_equations)
{
	double ratio, sum, maxs, tmp;
	long i, j, k, maxi;
	for (k = 0; k < n_equations - 1; k++)
	{
		maxs = fabs(MyMatrix[k][k]);
		maxi = k;
		for (i = k + 1; i < n_equations; i++)
		{
			if (maxs < fabs(MyMatrix[i][k])) maxi = i;
		}
		if (maxi != k)
		{
			for (i = 0; i < n_equations; i++)
			{
				tmp = MyMatrix[k][i];
				MyMatrix[k][i] = MyMatrix[maxi][i];
				MyMatrix[maxi][i] = tmp;
			}
			tmp = KnownRHS[k];
			KnownRHS[k] = KnownRHS[maxi];
			KnownRHS[maxi] = tmp;
		}

		for (i = k + 1; i < n_equations; i++)
		{
			if (MyMatrix[i][k] == 0.) continue;
			ratio = -MyMatrix[i][k] / MyMatrix[k][k];
			for (j = k + 1; j < n_equations; j++)
			{
				if (MyMatrix[k][j] == 0.) continue;
				MyMatrix[i][j] += ratio * MyMatrix[k][j];
			}
			KnownRHS[i] += ratio * KnownRHS[k];
		}
	}

	UnKnown[n_equations - 1] = KnownRHS[n_equations - 1] / MyMatrix[n_equations - 1][n_equations - 1];
	for (i = n_equations - 2; i >= 0; i--)
	{
		sum = 0.;
		for (j = i + 1; j < n_equations; j++) sum += MyMatrix[i][j] * UnKnown[j];
		UnKnown[i] = (KnownRHS[i] - sum) / MyMatrix[i][i];
	}
}

// MyMatrix * UnKnown = Known 이고
// Shape(MyMatrix) = (n, n), Shape(Known) = (n, ) 일 때
// UnKnown를 역산한다. Shape(UnKnown) = (n, )
// 이 떄 MyMatrix와 KnownRHS가 안바뀌게 내부에서 복붙
void gaussian_elimination_autocopy(double** MatrixA, double* Known_RHS, double* UnKnown, long n_equations)
{
	long i, j, k, maxi;

	double** MyMatrix = (double**)malloc(sizeof(double*) * n_equations);
	for (i = 0; i < n_equations; i++) MyMatrix[i] = (double*)malloc(sizeof(double) * n_equations);
	for (i = 0; i < n_equations; i++)
		for (j = 0; j < n_equations; j++)
			MyMatrix[i][j] = MatrixA[i][j];

	double* KnownRHS = (double*)malloc(sizeof(double) * n_equations);
	for (i = 0; i < n_equations; i++) KnownRHS[i] = Known_RHS[i];

	double ratio, sum, maxs, tmp;
	for (k = 0; k < n_equations - 1; k++)
	{
		maxs = fabs(MyMatrix[k][k]);
		maxi = k;
		for (i = k + 1; i < n_equations; i++)
		{
			if (maxs < fabs(MyMatrix[i][k])) maxi = i;
		}
		if (maxi != k)
		{
			for (i = 0; i < n_equations; i++)
			{
				tmp = MyMatrix[k][i];
				MyMatrix[k][i] = MyMatrix[maxi][i];
				MyMatrix[maxi][i] = tmp;
			}
			tmp = KnownRHS[k];
			KnownRHS[k] = KnownRHS[maxi];
			KnownRHS[maxi] = tmp;
		}

		for (i = k + 1; i < n_equations; i++)
		{
			if (MyMatrix[i][k] == 0.) continue;
			ratio = -MyMatrix[i][k] / MyMatrix[k][k];
			for (j = k + 1; j < n_equations; j++)
			{
				if (MyMatrix[k][j] == 0.) continue;
				MyMatrix[i][j] += ratio * MyMatrix[k][j];
			}
			KnownRHS[i] += ratio * KnownRHS[k];
		}
	}

	UnKnown[n_equations - 1] = KnownRHS[n_equations - 1] / MyMatrix[n_equations - 1][n_equations - 1];
	for (i = n_equations - 2; i >= 0; i--)
	{
		sum = 0.;
		for (j = i + 1; j < n_equations; j++) sum += MyMatrix[i][j] * UnKnown[j];
		UnKnown[i] = (KnownRHS[i] - sum) / MyMatrix[i][i];
	}

	for (i = 0; i < n_equations; i++) free(MyMatrix[i]);
	free(MyMatrix);
	free(KnownRHS);
}

double stdev(double* myarray, long n)
{
	long i;
	double m;
	m = 0.0;
	for (i = 0; i < n; i++) m += myarray[i]/(double)n;

	double var = 0.0;
	for (i = 0; i < n; i++) var += (myarray[i] - m) * (myarray[i] - m) / (double)n;

	return sqrt(var);
}

// EigenValue와 EigenVector 계산한다. 
// A(n, n)에 EigenValue 저장하고
// V(n, n)에 EigenVector 저장한다.
void Calc_Eigenvector(
	long n,					// 매트릭스 Shape
	double** A,				// input/output : input으로 Eigenvector, value 계산할 Matrix를 집어넣으면 EigenValue로 바꿔줌
	double** V,				// output : 임시 n,n Matrix를 넣으면 Eigenvector를 리턴
	long Nrun,				// 반복횟수
	double errorboundary	// 에러 임계치
)
{
	long i, j, k, p, q, r;
	double c, s, t, tau, tmax, alpha, xp, xq, eps = 1.0E-22;
	double sum;
	double tol = errorboundary;
	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++)
			if (i == j) V[i][j] = 1.0; else V[i][j] = 0.0;

	for (k = 0; k < Nrun; k++)
	{
		tmax = -1;
		sum = 0.0;
		for (i = 0 ; i < n; i++)
			for (j = i + 1; j < n; j++)
			{
				t = fabs(A[i][j]);
				sum += (t * t);
				if (t > tmax) { tmax = t; p = i; q = j; }
			}
		sum = sqrt(2.0 * sum);
		if (sum < tol) return;
		alpha = (A[q][q] - A[p][p]) / 2.0 / (A[p][q]);
		t = ((alpha > eps) ? 1.0 / (alpha + sqrt(1.0 + alpha * alpha)) : (alpha < eps) ? 1.0 / (alpha - sqrt(1.0 + alpha * alpha)) : 1.0);
		c = 1.0 / sqrt(1.0 + t * t);
		s = c * t;
		tau = s / (1.0 + c);

		for (r = 0; r < p; r++) A[p][r] = c * A[r][p] - s * A[r][q];
		for (r = p + 1; r < q; r++) if (r != q) A[r][p] = c * A[p][r] - s * A[q][r];
		for (r = 0; r < p; r++) A[q][r] = s * A[r][p] + c * A[r][q];
		for (r = p + 1; r < q; r++) A[q][r] = s * A[p][r] + c * A[r][q];
		for (r = q + 1; r < n; r++) A[r][q] = s * A[p][r] + c * A[q][r];

		A[p][p] = A[p][p] - t * A[p][q];
		A[q][q] = A[q][q] + t * A[p][q];
		A[q][p] = 0.0;

		for (i = 0; i < n; i++)
			for (j = i + 1; j < n; j++)
				A[i][j] = A[j][i];

		for (i = 0; i < n; i++)
		{
			xp = V[i][p];
			xq = V[i][q];
			V[i][p] = c * xp - s * xq;
			V[i][q] = s * xp + c * xq;
		}
	}
}

// Inverse Matrix를 계산한다. 
void matrixinverse(double** MyMatrix, long* MatrixShape, double** InvMatrix)
{
	long i, j,k;
	long n = MatrixShape[0];
	double* Known = (double*)malloc(sizeof(double) * n);
	for (i = 0; i < n; i++) Known[i] = 0.0;

	double* UnKnown = (double*)malloc(sizeof(double) * n);
	double** MatrixCopy = (double**)malloc(sizeof(double*) * n);
	for (i = 0; i < n; i++) MatrixCopy[i] = (double*)malloc(sizeof(double) * n);

	for (i = 0; i < n; i++)
	{
		// Known Setting
		for (j = 0; j < n; j++)
		{
			if (i == j) Known[j] = 1.0;
			else Known[j] = 0.0;
		}

		// Matrix Setting
		for (j = 0 ; j < n; j++) 
			for (k = 0; k < n; k++)
			{
				MatrixCopy[j][k] = MyMatrix[j][k];
			}

		gaussian_elimination(MatrixCopy, Known, UnKnown, n);
		for (j = 0; j < n; j++) InvMatrix[j][i] = UnKnown[j];

		// Known Setting
		for (j = 0; j < n; j++)
		{
			Known[j] = 0.0;
		}
	}
	free(Known);
	free(UnKnown);
	for (i = 0; i < n; i++) free(MatrixCopy[i]);
	free(MatrixCopy);
}

long OLSEst(
	double** Xvariables,// 독립변수 2차원 Matrix
	long* X_Shape,		// X의 Shape (ndata, nvariables), n = nvariables + 1
	double* Y,			// 종속변수 Array
	double* Result		// 결과값 담을 Array 길이 = (n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 4)
)
{
	long i;
	long j;
	long k;


	long nvariables = X_Shape[1];
	long n = nvariables + 1;
	long ndata = X_Shape[0];
	long nobs = ndata;
	long NResult = (n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 4);

	double** xvar = (double**)malloc(sizeof(double*) * ndata);							// sm.add_constant(x)
	double* xreshaped = (double*)malloc(sizeof(double) * ndata * n);					// sm.add_constant(x).reshape(-1)
	for (i = 0; i < ndata; i++) xvar[i] = xreshaped + n * i;

	long xshape[2] = { ndata, n };

	for (i = 0; i < ndata; i++) xvar[i][0] = 1.0;

	for (i = 0; i < ndata; i++)
	{
		for (j = 0; j < nvariables; j++)
		{
			xvar[i][j + 1] = Xvariables[i][j];
		}
	}

	double** xT = (double**)malloc(sizeof(double*) * n);								// X.T
	double* xTreshaped = (double*)malloc(sizeof(double) * ndata * n);					// X.T.reshape(-1)
	for (i = 0; i < n; i++) xT[i] = xTreshaped + ndata * i;

	for (i = 0; i < n; i++) for (j = 0; j < ndata; j++) xT[i][j] = xvar[j][i];
	long xT_shape[2] = { n, ndata };

	double* beta = (double*)malloc(sizeof(double) * n);									// OLS beta
	double** xTx = (double**)malloc(sizeof(double*) * n);								// x.T.dot(x)
	for (i = 0; i < n; i++) xTx[i] = (double*)malloc(sizeof(double) * n);
	XprimeDotX(xvar, xshape, xTx);

	double* xTy = (double*)malloc(sizeof(double) * n);									// x.T.dot(y)


	double s = 0.0;
	for (i = 0; i < xshape[1]; i++)
	{
		s = 0.0;
		for (j = 0; j < xshape[0]; j++)
		{
			s += xvar[j][i] * Y[j];
		}
		xTy[i] = s;
	}

	gaussian_elimination_autocopy(xTx, xTy, beta, n);									// (X'X)beta = (X'Y) 
	double* estimated = (double*)malloc(sizeof(double) * ndata);						// y_hat
	double* resid = (double*)malloc(sizeof(double) * ndata);							// err
	for (i = 0; i < ndata; i++)
	{
		s = 0.0;
		for (j = 0; j < n; j++)
		{
			s += xvar[i][j] * beta[j];
		}
		estimated[i] = s;
		resid[i] = Y[i] - s;
	}

	double SS_ERROR = 0.0;
	for (i = 0; i < nobs; i++) SS_ERROR += resid[i] * resid[i];
	double Y_Mean = 0.0;
	for (i = 0; i < nobs; i++) Y_Mean += Y[i] / (double)nobs;
	double SS_YfromMean = 0.0;
	for (i = 0; i < nobs; i++) SS_YfromMean += (Y[i] - Y_Mean) * (Y[i] - Y_Mean);

	double sig = sqrt(SS_ERROR / (double)(nobs - nvariables - 1));
	double* std_B = (double*)malloc(sizeof(double) * n);
	double* target = (double*)malloc(sizeof(double) * n);
	double* tempvalue = (double*)malloc(sizeof(double) * n);
	double* t_value = (double*)malloc(sizeof(double) * n);
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++) target[j] = 0.0;
		target[i] = sig * sig;
		gaussian_elimination_autocopy(xTx, target, tempvalue, n);
		std_B[i] = sqrt(tempvalue[i]);
		t_value[i] = beta[i] / std_B[i];
	}
	double rsquared = 1.0 - SS_ERROR / SS_YfromMean;
	double rsquared_adj = 1.0 - (1.0 - rsquared) * ((double)(nobs - 1)) / (double)(nobs - nvariables - 1);
	double resid_mean = 0.0;
	for (i = 0; i < ndata; i++) resid_mean += resid[i] / (double)ndata;

	double resid_std = stdev(resid, ndata);
	double loglikelihood = 0.0;
	for (i = 0; i < ndata; i++)
	{
		loglikelihood += log(exp(-(resid[i] * resid[i]) / (2.0 * resid_std * resid_std)) / sqrt(6.283185307179586 * resid_std * resid_std));
	}

	double Df_model = nvariables;
	double Df_res = (double)(nobs - nvariables - 1);
	double Fstatistic = rsquared / nvariables * 1.0 / ((1.0 - rsquared) / (double)((nobs - nvariables - 1)));
	double AIC = -2.0 * loglikelihood + 2.0 * ((double)nvariables + 1.0);
	double BIC = -2.0 * loglikelihood + ((double)nvariables + 1.0) * log((double)nobs);

	double durbin_watson = 0.0;
	for (i = 1; i < ndata; i++)
	{
		durbin_watson += (resid[i] - resid[i - 1]) * (resid[i] - resid[i - 1]) / SS_ERROR;
	}

	for (i = 0; i < n; i++)
	{
		Result[i] = beta[i];
		Result[i + n] = std_B[i];
		Result[i + 2 * n] = t_value[i];
	}

	Result[n * 3] = rsquared;
	Result[n * 3 + 1] = rsquared_adj;
	Result[n * 3 + 2] = resid_std;
	Result[n * 3 + 3] = loglikelihood;
	Result[n * 3 + 4] = Df_model;
	Result[n * 3 + 5] = Df_res;
	Result[n * 3 + 6] = Fstatistic;
	Result[n * 3 + 7] = AIC;
	Result[n * 3 + 8] = BIC;
	Result[n * 3 + 9] = durbin_watson;
	Result[n * 3 + 10] = sig;

	for (i = 0; i < ndata; i++)
	{
		Result[n * 3 + 11 + i] = estimated[i];
		Result[n * 3 + 11 + i] = resid[i];
	}

	////////////////////////////////////////
	// 여기서부터 Heteroskedasticity 계산 //
	////////////////////////////////////////
	double** inv_xTx = (double**)malloc(sizeof(double*) * n);									// inv(X'X)
	for (i = 0; i < n; i++) inv_xTx[i] = (double*)malloc(sizeof(double) * n);
	long inv_xTx_shape[2] = { n, n };
	matrixinverse(xTx, inv_xTx_shape, inv_xTx);

	double** ii = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) ii[i] = (double*)malloc(sizeof(double) * ndata);

	for (i = 0; i < ndata; i++)
	{
		for (j = 0; j < ndata; j++)
		{
			if (i == j) ii[i][j] = resid[i] * resid[i];
			else ii[i][j] = 0.0;
		}
	}

	double** xT_ii_x = (double**)malloc(sizeof(double*) * n);									// X.T.dot(Omega).dot(X)
	for (i = 0; i < n; i++) xT_ii_x[i] = (double*)malloc(sizeof(double) * n);		

	double FixA, FixB, FixC;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = resid[k] * resid[k];
				s += FixA * FixB * FixC;
			}
			xT_ii_x[i][j] = s;
		}
	}
	double** inv_xTx__xTiix = (double**)malloc(sizeof(double*) * n);							// inv(X.T.dot(X)). dot (X.T.dot(Omega).dot(X))
	for (i = 0; i < n; i++) inv_xTx__xTiix[i] = (double*)malloc(sizeof(double) * n);

	double** inv_xTx__xTiix_inv_xTx = (double**)malloc(sizeof(double*) * n);					// Inv(X.T.dot(X)). dot (X.T.dot(Omega).dot(X)). dot (Inv(X.T.dot(X))
	for (i = 0; i < n; i++) inv_xTx__xTiix_inv_xTx[i] = (double*)malloc(sizeof(double) * n);

	double** inv_xTiix = (double**)malloc(sizeof(double*) * n);									// Inv(X.T. dot (Omega). dot (X))
	for (i = 0; i < n; i++) inv_xTiix[i] = (double*)malloc(sizeof(double) * n);


	////////////////////////////////////
	// Heteroskedasticity consistent  //
	// Covariance Matrix 0 White 1980 //
	////////////////////////////////////

	matrixinverse(xT_ii_x, inv_xTx_shape, inv_xTiix);
	Dot2dArray(inv_xTx, inv_xTx_shape, xT_ii_x, inv_xTx_shape, inv_xTx__xTiix);
	Dot2dArray(inv_xTx__xTiix, inv_xTx_shape, inv_xTx, inv_xTx_shape, inv_xTx__xTiix_inv_xTx);

	k = 0;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			Result[n * 3 + 11 + 2 * ndata + k] = inv_xTx__xTiix_inv_xTx[i][j];
			k++;
		}
	}

	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + n * n + i] = sqrt(inv_xTx__xTiix_inv_xTx[i][i]);
	}

	double** xT_invii_x = (double**)malloc(sizeof(double*) * n);								// x.T. dot  Inv(Omega). dot  x
	for (i = 0; i < n; i++) xT_invii_x[i] = (double*)malloc(sizeof(double) * n);
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = ii[k][k];
				s += FixA * FixB / FixC;
			}
			xT_invii_x[i][j] = s;
		}
	}
	double* xT_invii_y = (double*)malloc(sizeof(double) * n);									// x.T. dot  Inv(Omega). dot (Y)
	for (i = 0; i < n; i++)
	{
		s = 0.0;
		for (j = 0; j < ndata; j++)
		{
			FixA = xvar[j][i];
			FixB = 1.0 / ii[j][j];
			FixC = Y[j];
			s += FixA * FixB * FixC;
		}
		xT_invii_y[i] = s;
	}
	double* beta_GLS = (double*)malloc(sizeof(double) * n);										// xT_inv_ii_x * GLSBeta = xT_invii_y
	gaussian_elimination_autocopy(xT_invii_x, xT_invii_y, beta_GLS, n);
	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + n * (n + 1) + i] = beta_GLS[i];
	}

	///////////////////////////////////////////////
	// Heteroskedasticity consistent			 //
	// Covariance Matrix 1 White, Mackinnon 1985 //
	///////////////////////////////////////////////
	k = 0;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			Result[n * 3 + 11 + 2 * ndata + n * (n + 2) + k] = ((double)nobs) / ((double)(nobs - nvariables - 1)) * inv_xTx__xTiix_inv_xTx[i][j];
			k++;
		}
	}

	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + n * (n + 2) + n * n + i] = sqrt(((double)nobs) / ((double)(nobs - nvariables - 1)) * inv_xTx__xTiix_inv_xTx[i][i]);
	}

	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + n * (n + 2) + n * (n + 1) + i] = beta_GLS[i];
	}

	///////////////////////////////////////////////
	// Heteroskedasticity consistent			 //
	// Covariance Matrix 2 White, Mackinnon 1985 //
	///////////////////////////////////////////////

	double** x_dot_inv_xTx = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) x_dot_inv_xTx[i] = (double*)malloc(sizeof(double) * n);
	long x_dot_inv_xTx_shape[2] = { ndata, n };
	for (i = 0; i < ndata; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < n; k++)
			{
				FixA = xvar[i][k];
				FixB = inv_xTx[k][j];
				s += FixA * FixB;
			}
			x_dot_inv_xTx[i][j] = s;
		}
	}

	double** h = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) h[i] = (double*)malloc(sizeof(double) * ndata);
	
	Dot2dArray(x_dot_inv_xTx, x_dot_inv_xTx_shape, xT, xT_shape, h);
	
	for (i = 0; i < ndata; i++) ii[i][i] = resid[i] * resid[i] / (1.0 - h[i][i]);

	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = ii[k][k];
				s += FixA * FixB * FixC;
			}
			xT_ii_x[i][j] = s;
		}
	}
	matrixinverse(xT_ii_x, inv_xTx_shape, inv_xTiix);
	Dot2dArray(inv_xTx, inv_xTx_shape, xT_ii_x, inv_xTx_shape, inv_xTx__xTiix);
	Dot2dArray(inv_xTx__xTiix, inv_xTx_shape, inv_xTx, inv_xTx_shape, inv_xTx__xTiix_inv_xTx);

	k = 0;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			Result[n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + k] = inv_xTx__xTiix_inv_xTx[i][j];
			k++;
		}
	}

	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * n + i] = sqrt(inv_xTx__xTiix_inv_xTx[i][i]);
	}

	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = ii[k][k];
				s += FixA * FixB / FixC;
			}
			xT_invii_x[i][j] = s;
		}
	}

	for (i = 0; i < n; i++)
	{
		s = 0.0;
		for (j = 0; j < ndata; j++)
		{
			FixA = xvar[j][i];
			FixB = 1.0 / ii[j][j];
			FixC = Y[j];
			s += FixA * FixB * FixC;
		}
		xT_invii_y[i] = s;
	}
	gaussian_elimination_autocopy(xT_invii_x, xT_invii_y, beta_GLS, n);
	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * (n + 1) + i] = beta_GLS[i];
	}

	///////////////////////////////////////////////
	// Heteroskedasticity consistent			 //
	// Covariance Matrix 3 White, Mackinnon 1985 //
	///////////////////////////////////////////////
	for (i = 0; i < ndata; i++) ii[i][i] = resid[i] * resid[i] / ((1.0 - h[i][i]) * (1.0 - h[i][i]));

	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = ii[k][k];
				s += FixA * FixB * FixC;
			}
			xT_ii_x[i][j] = s;
		}
	}

	matrixinverse(xT_ii_x, inv_xTx_shape, inv_xTiix);
	Dot2dArray(inv_xTx, inv_xTx_shape, xT_ii_x, inv_xTx_shape, inv_xTx__xTiix);
	Dot2dArray(inv_xTx__xTiix, inv_xTx_shape, inv_xTx, inv_xTx_shape, inv_xTx__xTiix_inv_xTx);

	k = 0;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			Result[n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + k] = inv_xTx__xTiix_inv_xTx[i][j];
			k++;
		}
	}

	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * n + i] = sqrt(inv_xTx__xTiix_inv_xTx[i][i]);
	}

	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			s = 0.0;
			for (k = 0; k < ndata; k++)
			{
				FixA = xvar[k][i];
				FixB = xvar[k][j];
				FixC = ii[k][k];
				s += FixA * FixB / FixC;
			}
			xT_invii_x[i][j] = s;
		}
	}

	for (i = 0; i < n; i++)
	{
		s = 0.0;
		for (j = 0; j < ndata; j++)
		{
			FixA = xvar[j][i];
			FixB = 1.0 / ii[j][j];
			FixC = Y[j];
			s += FixA * FixB * FixC;
		}
		xT_invii_y[i] = s;
	}

	gaussian_elimination_autocopy(xT_invii_x, xT_invii_y, beta_GLS, n);
	for (i = 0; i < n; i++)
	{
		Result[n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * (n + 1) + i] = beta_GLS[i];
	}
	
	double** EigenValue = (double**)malloc(sizeof(double*) * n);
	for (i = 0; i < n; i++) EigenValue[i] = (double*)malloc(sizeof(double) * n);

	double** EigenVector = (double**)malloc(sizeof(double*) * n);
	for (i = 0; i < n; i++) EigenVector[i] = (double*)malloc(sizeof(double) * n);
	
	for (i = 0; i < n; i++) for (j = 0; j < n; j++)
	{
		EigenValue[i][j] = xTx[i][j];
		EigenVector[i][j] = 0.0;

	}

	Calc_Eigenvector(n, EigenValue, EigenVector, 31, 1.0E-22);
	for (i = 0; i < n; i++) Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + i] = EigenValue[i][i];

	k = 0;
	for (i = 0; i < n; i++)
	{
		for (j = 0; j < n; j++)
		{
			Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n + k] = EigenVector[i][j];
			k += 1;
		}
	}
	
	double mu3, sig3, mu4, sig4, Skew, Kurt, JB;
	mu3 = 0.0;
	sig3 = 0.0;
	for (i = 0; i < ndata; i++)
	{
		mu3 += (resid[i] - resid_mean) * (resid[i] - resid_mean) * (resid[i] - resid_mean) / (double)ndata;
		sig3 += (resid[i] - resid_mean) * (resid[i] - resid_mean) / (double)ndata;
	}
	sig3 = pow(sig3, 1.5);

	mu4 = 0.0;
	sig4 = 0.0;
	for (i = 0; i < ndata; i++)
	{
		mu4 += (resid[i] - resid_mean) * (resid[i] - resid_mean) * (resid[i] - resid_mean) * (resid[i] - resid_mean) / (double)ndata;
		sig4 += (resid[i] - resid_mean) * (resid[i] - resid_mean) / (double)ndata;
	}
	sig4 = pow(sig4, 2.0);
	Skew = mu3 / sig3;
	Kurt = mu4 / sig4;
	JB = (double)nobs / 6.0 * (Skew * Skew + 0.25 * (Kurt - 3.0) * (Kurt - 3.0));
	
	
	Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1)] = Skew;
	Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 1] = Kurt;
	Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 2] = JB;
	Result[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 3] = SS_YfromMean;
	
	free(xreshaped);
	free(xvar);

	free(xTreshaped);
	free(xT);

	free(beta);
	for (i = 0; i < n; i++) free(xTx[i]);
	free(xTx);
	free(xTy);
	free(estimated);
	free(resid);
	free(std_B);
	free(target);
	free(tempvalue);
	free(t_value);
	for (i = 0; i < n; i++) free(inv_xTx[i]);
	free(inv_xTx);
	for (i = 0; i < ndata; i++) free(ii[i]);
	free(ii);
	for (i = 0; i < n; i++) free(xT_ii_x[i]);
	free(xT_ii_x);
	for (i = 0; i < n; i++) free(inv_xTx__xTiix[i]);
	free(inv_xTx__xTiix);
	for (i = 0; i < n; i++) free(inv_xTx__xTiix_inv_xTx[i]);
	free(inv_xTx__xTiix_inv_xTx);
	for (i = 0; i < n; i++) free(inv_xTiix[i]);
	free(inv_xTiix);
	for (i = 0; i < n; i++) free(xT_invii_x[i]);
	free(xT_invii_x);
	free(xT_invii_y);
	free(beta_GLS);
	for (i = 0; i < ndata; i++) free(x_dot_inv_xTx[i]);
	free(x_dot_inv_xTx);
	for (i = 0; i < ndata; i++) free(h[i]);
	free(h);
	for (i = 0; i < n; i++) free(EigenValue[i]);
	free(EigenValue);
	for (i = 0; i < n; i++) free(EigenVector[i]);
	free(EigenVector);
	
	return NResult;
}

class OLSestimate {
private:


public:
	long ndata;						// 데이터의 개수
	long nvariables;				// 변수의 개수(절편 제외)
	long n;							// 절편 포함 설명변수 개수
	long NResult;					// 위 OLSEst 함수로 계산되는 결과 Array의 길이
	double* ResultArray;			// OLSEst결과
	long nobs;						// 관측치(데이터)개수
	double* beta;					// 베타
	double* std_B;					// 베타 변동성
	double* t_value;				// T값
	double rsquared;				// R^2 결정계수
	double rsquared_adj;			// 조정 결정계수
	double resid_std;				// residual의 std
	double loglikelihood;			// loglikelihood
	long Df_model;					// Df model
	long Df_res;					// Df residual
	double Fstatistic;				// F값
	double AIC;						// AIC
	double BIC;						// BIC
	double durbin_watson;			// durbin watson값
	double sig;						// sqrt(SSE/(n-k))
	double* estimated;				// yhat
	double* resid;					// error
	double** cov_HC0;				// Heteroskedasticity0 Cov Matrix White 1980
	double* HC0_se;					// Heteroskedasticity0 std of GLS Beta
	double* beta_HC0_GLS;			// GLS Beta Using Heteroskedasticity0 Cov
	double** cov_HC1;				// Heteroskedasticity1 1985
	double* HC1_se;					// Heteroskedasticity1 std of GLS Beta
	double* beta_HC1_GLS;			// GLS Beta Using Heteroskedasticity1 Cov
	double** cov_HC2;				// Heteroskedasticity2 1985
	double* HC2_se;					// Heteroskedasticity2 std of GLS Beta
	double* beta_HC2_GLS;			// GLS Beta Using Heteroskedasticity2 Cov
	double** cov_HC3;				// Heteroskedasticity3
	double* HC3_se;					// Heteroskedasticity3 std of GLS Beta
	double* beta_HC3_GLS;			// GLS Beta Using Heteroskedasticity3 Cov
	double* Eigenvalue;				// EigenValue of xTx
	double** Eigenvector;			// EigenVector of xTx
	double Skew;					// Skew
	double Kurt;					// Kurt
	double JB;						// Jarq Bera Test Statistic
	double centered_tss;			// TSS

	// variables informationi
	// X -> independent Variable **Matrix (ndata , num_variables)
	// Y -> dependent Variable *Array (ndata, )
	// num_data -> number of dataset
	// num_variables -> number of independent variables except constant
	OLSestimate(double** X, double* Y, long num_data, long num_variables)
	{
		long i;
		n = num_variables + 1;
		nvariables = num_variables;
		ndata = num_data;
		nobs = ndata;
		ResultArray = (double*)malloc(sizeof(double) * (n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 4));
		long X_Shape[2] = { ndata, nvariables };
		NResult = OLSEst(X, X_Shape, Y, ResultArray);
		beta = ResultArray;
		std_B = ResultArray + n;
		t_value = ResultArray + 2 * n;
		rsquared = ResultArray[3 * n];
		rsquared_adj = ResultArray[3 * n + 1];
		resid_std = ResultArray[3 * n + 2];
		loglikelihood = ResultArray[n * 3 + 3];
		Df_model = (long)ResultArray[n * 3 + 4];
		Df_res = (long)ResultArray[n * 3 + 5];
		Fstatistic = ResultArray[n * 3 + 6];
		AIC = ResultArray[n * 3 + 7];
		BIC = ResultArray[n * 3 + 8];
		durbin_watson = ResultArray[n * 3 + 9];
		sig = ResultArray[n * 3 + 10];
		estimated = ResultArray + n * 3 + 11;
		resid = ResultArray + n * 3 + 11 + ndata;

		cov_HC0 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC0[i] = ResultArray + n * 3 + 11 + 2 * ndata + i * n;
		HC0_se = ResultArray + n * 3 + 11 + 2 * ndata + n * n;
		beta_HC0_GLS = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 1);

		cov_HC1 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC1[i] = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * n + i * n;
		HC1_se = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * n;
		beta_HC1_GLS = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * (n + 1);

		cov_HC2 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC2[i] = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + i * n;
		HC2_se = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * n;
		beta_HC2_GLS = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * (n + 1);

		cov_HC3 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC3[i] = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + i * n;
		HC3_se = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * n;
		beta_HC3_GLS = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * (n + 1);

		Eigenvalue = ResultArray + n * 3 + 11 + 2 * ndata + 4 * n * (n + 2);
		Eigenvector = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) ResultArray + n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n + i * n;

		Skew = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1)];
		Kurt = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 1];
		JB = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 2];
		centered_tss = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 3];
	}


	// variables informationi
	// X -> independent Variable *Matrix (ndata , )
	// Y -> dependent Variable *Array (ndata, )
	// num_data -> number of dataset
	OLSestimate(double* X, double* Y, long num_data)
	{
		long i;
		long num_variables = 1;
		double** X_2d = (double**)malloc(sizeof(double*) * ndata);
		for (i = 0; i < ndata; i++) X_2d[i] = (double*)malloc(sizeof(double) * 1);
		n = num_variables + 1;
		nvariables = num_variables;
		ndata = num_data;
		nobs = ndata;
		ResultArray = (double*)malloc(sizeof(double) * (n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 4));
		long X_Shape[2] = { ndata, nvariables };
		NResult = OLSEst(X_2d, X_Shape, Y, ResultArray);
		beta = ResultArray;
		std_B = ResultArray + n;
		t_value = ResultArray + 2 * n;
		rsquared = ResultArray[3 * n];
		rsquared_adj = ResultArray[3 * n + 1];
		resid_std = ResultArray[3 * n + 2];
		loglikelihood = ResultArray[n * 3 + 3];
		Df_model = (long)ResultArray[n * 3 + 4];
		Df_res = (long)ResultArray[n * 3 + 5];
		Fstatistic = ResultArray[n * 3 + 6];
		AIC = ResultArray[n * 3 + 7];
		BIC = ResultArray[n * 3 + 8];
		durbin_watson = ResultArray[n * 3 + 9];
		sig = ResultArray[n * 3 + 10];
		estimated = ResultArray + n * 3 + 11;
		resid = ResultArray + n * 3 + 11 + ndata;

		cov_HC0 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC0[i] = ResultArray + n * 3 + 11 + 2 * ndata + i * n;
		HC0_se = ResultArray + n * 3 + 11 + 2 * ndata + n * n;
		beta_HC0_GLS = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 1);

		cov_HC1 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC1[i] = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * n + i * n;
		HC1_se = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * n;
		beta_HC1_GLS = ResultArray + n * 3 + 11 + 2 * ndata + n * (n + 2) + n * (n + 1);

		cov_HC2 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC2[i] = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + i * n;
		HC2_se = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * n;
		beta_HC2_GLS = ResultArray + n * 3 + 11 + 2 * ndata + 2 * n * (n + 2) + n * (n + 1);

		cov_HC3 = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) cov_HC3[i] = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + i * n;
		HC3_se = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * n;
		beta_HC3_GLS = ResultArray + n * 3 + 11 + 2 * ndata + 3 * n * (n + 2) + n * (n + 1);

		Eigenvalue = ResultArray + n * 3 + 11 + 2 * ndata + 4 * n * (n + 2);
		Eigenvector = (double**)malloc(sizeof(double*) * n);
		for (i = 0; i < n; i++) ResultArray + n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n + i * n;

		Skew = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1)];
		Kurt = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 1];
		JB = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 2];
		centered_tss = ResultArray[n * 3 + 11 + 2 * ndata + 4 * n * (n + 2) + n * (n + 1) + 3];

		for (i = 0; i < ndata; i++) free(X_2d[i]);
		free(X_2d);
	}

	~OLSestimate()
	{
		free(ResultArray);
		free(cov_HC0);
		free(cov_HC1);
		free(cov_HC2);
		free(cov_HC3);
		free(Eigenvector);
	}

	// Python의 sm.OLS(y,x).fit().summary()와 비슷한 포멧
	void summary()
	{
		printf("\nOLS Regression Result\n\n");
		printf("Dep. Variables: \t y\t");
		printf("R Squared:\t %0.5lf\n", rsquared);
		printf("Model: \t\t\t OLS\t Adj_Rsquared:\t %0.5lf \n", rsquared_adj);
		printf("Method: \t Least_Squares\t F_statistic:\t %0.5lf \n", Fstatistic);
		printf("No_Obs: \t\t %d\t AIC:\t %0.5lf \n", nobs, AIC);
		printf("Df_Residuals: \t\t %d\t BIC:\t %0.5lf\n", Df_res, BIC);
		printf("Df_Model: \t\t %d\n\n", Df_model);
		printf("\t\t coef \t\t stderr \t\t tvalue\n");
		double n1, n2, n3;
		for (long i = 0; i < n; i++)
		{
			n1 = beta[i];
			n2 = std_B[i];
			n3 = t_value[i];
			printf("x%d\t\t%0.5lf", i, n1);
			if (n1 < 0.) printf("\t %0.5lf", n2);
			else printf("\t\t %0.5lf", n2);
			printf("\t\t % 0.5lf \n", n3);
		}
		printf("\nDurbin_Watson: \t %0.5lf\t Jarque_Bera:\t %0.5lf\n", durbin_watson, JB);
		printf("Skew: \t\t %0.5lf\t Kurtosis:\t %0.5lf \n", Skew, Kurt);

	}
};

////////////////////////////////////
// 여기서부터 Logistic Regression //
////////////////////////////////////

double ProbFun(double* x, double* beta, long nbeta)
{
	long i;
	double xb = 0.0;
	for (i = 0; i < nbeta; i++) xb += x[i] * beta[i];
	xb = max(-300.0, min(300.0, xb));
	return 1.0 / (1.0 + exp(-xb));
} 

double log_logisticfunc(double* X, double* Beta, long nBeta, double y)
{
	long i;
	double XB = 0.0;
	double prob;
	double logprob;
	for (i = 0; i < nBeta; i++) XB += X[i] * Beta[i];

	if ((XB < 300.0) && (XB > -300.0))
	{
		prob = 1.0 / (1.0 + exp(-XB));
		if (y == 0) logprob = log(max(1.0E-300, 1 - prob));
		else logprob = log(max(1.0E-300, prob));
	}
	else if (XB >= 100.0)
	{
		logprob = 1.0E-22;
	}
	else
	{
		logprob = -XB;
	}
	return logprob;
}

double log_logisticfunc_scalar(double XB, long nBeta, double y)
{
	long i;
	double prob;
	double logprob;

	if ((XB < 300.0) && (XB > -300.0))
	{
		prob = 1.0 / (1.0 + exp(-XB));
		if (y == 0) logprob = log(max(1.0E-300, 1 - prob));
		else logprob = log(max(1.0E-300, prob));
	}
	else if (XB >= 100.0)
	{
		logprob = 1.0E-22;
	}
	else
	{
		logprob = -XB;
	}
	return logprob;
}

double log_logistic_sum_func(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i, j;
	double XB = 0.0;
	double logprob = 0.0;
	for (i = 0; i < nbeta; i++)
	{
		XB = 0.0;
		for (j = 0; j < nbeta; j++)
		{
			XB += x[i][j] * beta[j];
		}
		logprob += log_logisticfunc_scalar(XB, nbeta, y[i]);
	}
	return logprob;
}

double* ErrorFunc(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i;
	double* P = (double*)malloc(sizeof(double) * ndata);
	double* err = (double*)malloc(sizeof(double) * ndata);
	for (i = 0; i < ndata; i++) P[i] = ProbFun(x[i], beta, nbeta);
	
	for (i = 0; i < ndata; i++) err[i] = -(y[i] * log(max(1.0E-300, P[i])) + (1.0 - y[i]) * log(max(1.0E-300, 1.0 - P[i])));

	free(P);
	return err;
}

double** Error_Jacov(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i, j;
	double p;
	double** ErrJcv = (double**)malloc(sizeof(double*) * ndata);
	for (i = 0; i < ndata; i++) ErrJcv[i] = (double*)malloc(sizeof(double) * nbeta);

	for (i = 0; i < ndata; i++)
	{
		p = ProbFun(x[i], beta, nbeta);
		for (j = 0; j < nbeta; j++)
		{
			ErrJcv[i][j] = (p - y[i]) * x[i][j];
		}
	}
	return ErrJcv;
}

double** Err_Hessian(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i, j, k;
	double** xT_ii_x = (double**)malloc(sizeof(double*) * nbeta);									// X.T.dot(Omega).dot(X)
	for (i = 0; i < nbeta; i++) xT_ii_x[i] = (double*)malloc(sizeof(double) * nbeta);
	double* p = (double*)malloc(sizeof(double) * ndata);
	for (i = 0; i < ndata; i++) p[i] = ProbFun(x[i], beta, nbeta);

	double FixA, FixB, FixC,  s;
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
			xT_ii_x[i][j] = s;
		}
	}
	free(p);
	return xT_ii_x;
}

double** Inv_Err_Hessian(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i, j, k;
	double** xT_ii_x = (double**)malloc(sizeof(double*) * nbeta);									// X.T.dot(Omega).dot(X)
	for (i = 0; i < nbeta; i++) xT_ii_x[i] = (double*)malloc(sizeof(double) * nbeta);

	double** inv_xT_ii_x = (double**)malloc(sizeof(double*) * nbeta);
	for (i = 0; i < nbeta; i++) inv_xT_ii_x[i] = (double*)malloc(sizeof(double) * nbeta);
	long shape[2] = { nbeta, nbeta };
	double* p = (double*)malloc(sizeof(double) * ndata);
	for (i = 0; i < ndata; i++) p[i] = ProbFun(x[i], beta, nbeta);

	double FixA, FixB, FixC, s;
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
			xT_ii_x[i][j] = s;
		}
	}
	matrixinverse(xT_ii_x, shape, inv_xT_ii_x);
	free(p);
	for (i = 0; i < nbeta; i++) free(xT_ii_x[i]);
	free(xT_ii_x);
	return inv_xT_ii_x;
}

double* Error_Sum_Jacov(double** x, double* y, long ndata, double* beta, long nbeta)
{
	long i, j;
	double p;
	double* ErrJcv = (double*)malloc(sizeof(double*) * nbeta);
	for (i = 0; i < nbeta; i++) ErrJcv[i] = 0.0;

	for (i = 0; i < ndata; i++)
	{
		p = ProbFun(x[i], beta, nbeta);
		for (j = 0; j < nbeta; j++)
		{
			ErrJcv[j] += (p - y[i]) * x[i][j];
		}
	}
	return ErrJcv;
}

double* MLE_Logistic_Estimate(double** x, double* y, long ndata, long nbeta, double* beta_0, double alpha_0, long method)
{
	double* theta = beta_0;
	double alpha = alpha_0;

	double* min_theta = (double*)malloc(sizeof(double) * nbeta);



	free(min_theta);
}

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