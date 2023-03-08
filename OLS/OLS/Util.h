#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef max
#define max(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef min
#define min(a,b)            (((a) < (b)) ? (a) : (b))
#endif

#define PI		3.141592653589793238462643383279
#define UTILITY 1

#ifndef DLLEXPORT(A)
#ifdef WIN32
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif _WIN64
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif __linux__
#define DLLEXPORT(A) extern "C" __declspec
#elif __hpux
#define DLLEXPORT(A) extern "C" __declspec
#elif __unix__
#define DLLEXPORT(A) extern "C" __declspec
#else 
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#endif
#endif


long GetMinor(double** src, double** dest, long row, long col, long order);
double CalcDeterminant(double** mat, long order, double*** MinorMatrixList);

/////////////////////////////////////////////////
// Numerical Recipy Random Number Generator
// Page 305
/////////////////////////////////////////////////

#define IA 16807
#define IM 2147483647
#define AM (1.0/IM)
#define IQ 127773
#define IR 2836
#define NTAB 32
#define NDIV (1+(IM-1)/NTAB)
#define EPS 1.2e-7
#define RNMX (1.0-EPS)
long idum = -1;
long iy = 0;
long iv[NTAB];
long iset = 0;
double gset = 0.0;

double ran1(long* idum, long& iy, long* iv)
{
	long j;
	long k;

	double temp;

	if (*idum <= 0 || !iy) {
		if (-(*idum) < 1) *idum = 1;
		else *idum = -(*idum);
		for (j = NTAB + 7; j >= 0; j--) {
			k = (*idum) / IQ;
			*idum = IA * (*idum - k * IQ) - IR * k;
			if (*idum < 0) *idum += IM;
			if (j < NTAB) iv[j] = *idum;
		}
		iy = iv[0];
	}
	k = (*idum) / IQ;
	*idum = IA * (*idum - k * IQ) - IR * k;
	if (*idum < 0) *idum += IM;
	j = iy / NDIV;
	iy = iv[j];
	iv[j] = *idum;
	if ((temp = AM * iy) > RNMX) return RNMX;
	else return temp;
}

double randnorm()
{
	double fac, rsq, v1, v2;
	if (idum < 0) iset = 0;
	if (iset == 0) {
		do {
			v1 = 2.0 * ran1(&idum, iy, iv) - 1.0;
			v2 = 2.0 * ran1(&idum, iy, iv) - 1.0;
			rsq = v1 * v1 + v2 * v2;
		} while (rsq >= 1.0 || rsq == 0.0);
		fac = sqrt(-2.0 * log(rsq) / rsq);
		gset = v1 * fac;
		iset = 1;
		return v2 * fac;
	}
	else
	{
		iset = 0;
		return gset;
	}
}

double randn(long seed, long& idum_forsim, long& iset_forsim, double& gset_forsim, long& iy_forsim, long* iv_forsim)
{
	double fac, rsq, v1, v2;

	if (seed == 0) {
		idum_forsim = -1;
		iset_forsim = 0;
		gset_forsim = 0.0;
	}

	if (iset_forsim == 0) {
		do {
			v1 = 2.0 * ran1(&idum_forsim, iy_forsim, iv_forsim) - 1.0;
			v2 = 2.0 * ran1(&idum_forsim, iy_forsim, iv_forsim) - 1.0;
			rsq = v1 * v1 + v2 * v2;
		} while (rsq >= 1.0 || rsq == 0);
		fac = sqrt(-2.0 * log(rsq) / rsq);
		gset_forsim = v1 * fac;
		iset_forsim = 1;
		return v2 * fac;
	}
	else {
		iset_forsim = 0;
		return gset_forsim;
	}
}

// mu = 0, sigma = 1 RandomNumber Generate (시드값 주면 리턴하지않고 시드셋팅)
void randnorm(long seed)
{
	idum = -1;
	iset = 0;
	gset = 0.0;
}

// Make 1d Array
double* make_array(long n)
{
	double* Array = (double*)calloc(n, sizeof(double));
	return Array;
}

// Make 1d Array Random Number
double* make_array_randn(long n)
{
	long i;
	double* Array = (double*)calloc(n, sizeof(double));
	for (i = 0; i < n; i++)
	{
		Array[i] = randnorm();
	}
	return Array;
}

// Make 2d Array
double** make_array(long n, long m)
{
	long i;
	double** Array_2d = (double**)malloc(n * sizeof(double*));
	for (i = 0; i < n; i++)
	{
		Array_2d[i] = (double*)calloc(m, sizeof(double));
	}
	return Array_2d;
}

// Make 2d Array Random Number
double** make_array_randn(long n, long m)
{
	long i, j;
	double** Array_2d = (double**)malloc(n * sizeof(double*));
	for (i = 0; i < n; i++)
	{
		Array_2d[i] = (double*)calloc(m, sizeof(double));
		for (j = 0; j < m; j++)
			Array_2d[i][j] = randnorm();
	}
	return Array_2d;
}


// Print Array
void Print_Array(double* Array, long n)
{
	long i;
	printf("[");
	for (i = 0; i < n - 1; i++)
		printf("%0.5lf,  ", Array[i]);
	printf("%0.5lf]", Array[n - 1]);
}

// Print Array
void Print_Array(double** Array, long n, long m)
{
	long i;
	printf("[");
	for (i = 0; i < n - 1; i++)
	{
		Print_Array(Array[i], m);
		printf("\n");
	}
	Print_Array(Array[n - 1], m);
	printf("]");
}

void rounding(double** Matrix, long nrow, long ncol, long n_decimal)
{
	long i;
	long j;
	double div = 1.0;
	for (i = 0; i < n_decimal; i++) div *= 10.0;

	for (i = 0; i < nrow; i++)
		for (j = 0; j < ncol; j++) Matrix[i][j] = floor(Matrix[i][j] * div + 0.5) / div;
}

//표준정규분포(Standard Normal Distribution) PDF
DLLEXPORT(double) PDF_N(double x)
{
	return exp(-x * x / 2.0) / sqrt(2.0 * PI);
}

//표준정규분포(Standard Normal Distribution) CDF
DLLEXPORT(double) CDF_N(double x)
{
	double y, Exponential, S, S2, value;

	y = fabs(x);
	if (y > 37.0) value = 0.;
	else {
		Exponential = exp(-y * y / 2);
		if (y < 7.07106781186547) {
			S = 3.52624965998911E-02 * y + 0.700383064443688;
			S = S * y + 6.37396220353165;
			S = S * y + 33.912866078383;
			S = S * y + 112.079291497871;
			S = S * y + 221.213596169931;
			S = S * y + 220.206867912376;
			S2 = 8.83883476483184E-02 * y + 1.75566716318264;
			S2 = S2 * y + 16.064177579207;
			S2 = S2 * y + 86.7807322029461;
			S2 = S2 * y + 296.564248779674;
			S2 = S2 * y + 637.333633378831;
			S2 = S2 * y + 793.826512519948;
			S2 = S2 * y + 440.413735824752;
			value = Exponential * S / S2;
		}
		else {
			S = y + 0.65;
			S = y + 4.0 / S;
			S = y + 3.0 / S;
			S = y + 2.0 / S;
			S = y + 1.0 / S;
			value = Exponential / (S * 2.506628274631);
		}
	}

	if (x > 0.0) value = 1.0 - value;

	return value;
}

// Inverse Cummulative Norm
DLLEXPORT(double) INV_CDF_N(double p)
{

	double a1 = -39.69683028665376;
	double a2 = 220.9460984245205;
	double a3 = -275.9285104469687;
	double a4 = 138.3577518672690;
	double a5 = -30.66479806614716;
	double a6 = 2.506628277459239;

	double b1 = -54.47609879822406;
	double b2 = 161.5858368580409;
	double b3 = -155.6989798598866;
	double b4 = 66.80131188771972;
	double b5 = -13.28068155288572;

	double c1 = -0.007784894002430293;
	double c2 = -0.3223964580411365;
	double c3 = -2.400758277161838;
	double c4 = -2.549732539343734;
	double c5 = 4.374664141464968;
	double c6 = 2.938163982698783;

	double d1 = 0.007784695709041462;
	double d2 = 0.3224671290700398;
	double d3 = 2.445134137142996;
	double d4 = 3.754408661907416;

	//Define break-points.

	double p_low = 0.02425;
	double p_high = 1 - p_low;
	double  q, r, e, u;
	double x = 0.0;


	//Rational approximation for lower region.

	if (0 < p && p < p_low) {
		q = sqrt(-2 * log(p));
		x = (((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
	}

	//Rational approximation for central region.

	if (p_low <= p && p <= p_high) {
		q = p - 0.5;
		r = q * q;
		x = (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) * q / (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1);
	}

	//Rational approximation for upper region.

	if (p_high < p && p < 1) {
		q = sqrt(-2 * log(1 - p));
		x = -(((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
	}

	//Pseudo-code algorithm for refinement

	if ((0 < p) && (p < 1)) {
		e = 0.5 * erfc(-x / sqrt(2)) - p;
		u = e * sqrt(2 * PI) * exp(x * x / 2);
		x = x - u / (1 + x * u / 2);
	}

	return x;
}

// Linear Interpolation (X변수, Y변수, X길이, 타겟X)
DLLEXPORT(double) Interpolate_Linear(double* x, double* fx, long nx, double targetx, long extrapolateflag)
{
	long i;
	double result = 0.0;

	if (nx == 1 || targetx == x[0])
		return fx[0];
	else if (targetx == x[nx - 1])
		return fx[nx - 1];


	if (targetx < x[0])
	{
		if (extrapolateflag == 0) return fx[0];
		else return (fx[1] - fx[0]) / (x[1] - x[0]) * (targetx - x[0]) + fx[0];
	}
	else if (targetx > x[nx - 1])
	{
		if (extrapolateflag == 0) return fx[nx - 1];
		else return (fx[nx - 1] - fx[nx - 2]) / (x[nx - 1] - x[nx - 2]) * (targetx - x[nx - 1]) + fx[nx - 1];
	}
	else
	{
		for (i = 1; i < nx; i++)
		{
			if (targetx < x[i])
			{
				result = (fx[i] - fx[i - 1]) / (x[i] - x[i - 1]) * (targetx - x[i - 1]) + fx[i - 1];
				break;
			}
		}
		return result;
	}
}

// Linear Interpolation (X변수, Y변수, X길이, 타겟X)
double Interpolate_Linear(double* x, double* fx, long nx, double targetx)
{
	return Interpolate_Linear(x, fx, nx, targetx, 0);
}

// LogLinear Interpolation (X변수, Y변수, X길이, 타겟X)
DLLEXPORT(double) Interpolate_LogLinear(double* x, double* fx, long nx, double targetx, long extrapolateflag)
{
	long i;
	double result = 0.0;

	if (nx == 1 || targetx == x[0])
		return fx[0];
	else if (targetx == x[nx - 1])
		return fx[nx - 1];


	if (targetx < x[0])
	{
		if (extrapolateflag == 0) return fx[0];
		else return exp((log(fx[1]) - log(fx[0])) / (x[1] - x[0]) * (targetx - x[0]) + log(fx[0]));
	}
	else if (targetx > x[nx - 1])
	{
		if (extrapolateflag == 0) return fx[nx - 1];
		else return exp((log(fx[nx - 1]) - log(fx[nx - 2])) / (x[nx - 1] - x[nx - 2]) * (targetx - x[nx - 1]) + log(fx[nx - 1]));
	}
	else
	{
		for (i = 1; i < nx; i++)
		{
			if (targetx < x[i])
			{
				result = exp((log(fx[i]) - log(fx[i - 1])) / (x[i] - x[i - 1]) * (targetx - x[i - 1]) + log(fx[i - 1]));
				break;
			}
		}
		return result;
	}
}

// LogLinear Interpolation (X변수, Y변수, X길이, 타겟X)
double Interpolate_LogLinear(double* x, double* fx, long nx, double targetx)
{
	return Interpolate_LogLinear(x, fx, nx, targetx, 0);
}

DLLEXPORT(double) Interpolate_ExpLinear(double* x, double* fx, long nx, double targetx, long extrapolateflag)
{
	long i;
	double result = 0.0;

	if (nx == 1 || targetx == x[0])
		return fx[0];
	else if (targetx == x[nx - 1])
		return fx[nx - 1];


	if (targetx < x[0])
	{
		if (extrapolateflag == 0) return fx[0];
		else return log((exp(fx[1]) - exp(fx[0])) / (x[1] - x[0]) * (targetx - x[0]) + exp(fx[0]));
	}
	else if (targetx > x[nx - 1])
	{
		if (extrapolateflag == 0) return fx[nx - 1];
		else return log((exp(fx[nx - 1]) - exp(fx[nx - 2])) / (x[nx - 1] - x[nx - 2]) * (targetx - x[nx - 1]) + exp(fx[nx - 1]));
	}
	else
	{
		for (i = 1; i < nx; i++)
		{
			if (targetx < x[i])
			{
				result = log((exp(fx[i]) - exp(fx[i - 1])) / (x[i] - x[i - 1]) * (targetx - x[i - 1]) + exp(fx[i - 1]));
				break;
			}
		}
		return result;
	}
}

// LogLinear Interpolation (X변수, Y변수, X길이, 타겟X)
double Interpolate_ExpLinear(double* x, double* fx, long nx, double targetx)
{
	return Interpolate_ExpLinear(x, fx, nx, targetx, 0);
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

// Cholesky 분해된 Array를 리턴 (함수내부 동적할당)
double** Cholesky_Decomposition(double** matrix, long n)
{
	long i, j, k;
	double sum;

	double** lower = (double**)malloc(n * sizeof(double*));
	for (i = 0; i < n; i++)
	{
		lower[i] = (double*)calloc(n, sizeof(double));
	}

	// Decomposing a matrix into Lower Triangular
	for (i = 0; i < n; i++) {
		for (j = 0; j <= i; j++) {
			sum = 0.0;

			if (j == i) // summation for diagonals
			{
				for (k = 0; k < j; k++)
					sum += pow(lower[j][k], 2);
				lower[j][j] = sqrt(matrix[j][j] -
					sum);
			}
			else
			{
				// Evaluating L(i, j) using L(j, j)
				for (k = 0; k < j; k++)
					sum += (lower[i][k] * lower[j][k]);
				lower[i][j] = (matrix[i][j] - sum) /
					lower[j][j];
			}
		}
	}
	return lower;
}

// Cholesky 분해된 Array를 리턴 (CorrMatrix.reshape(-1) , EmptyMatrix.reshape(-1), Length)
DLLEXPORT(long) Cholesky_Decomposition(double* matrix_reshaped, double* temp_array, long n)
{
	long i, j, k;
	double sum;

	double** matrix = (double**)malloc(n * sizeof(double*));
	k = 0;
	for (i = 0; i < n; i++)
	{
		matrix[i] = (double*)malloc(sizeof(double) * n);
		for (j = 0; j < n; j++)
		{
			matrix[i][j] = matrix_reshaped[k];
			k++;
		}
	}

	double** lower = (double**)malloc(n * sizeof(double*));
	for (i = 0; i < n; i++)
	{
		lower[i] = (double*)calloc(n, sizeof(double));
	}

	// Decomposing a matrix into Lower Triangular
	for (i = 0; i < n; i++) {
		for (j = 0; j <= i; j++) {
			sum = 0.0;

			if (j == i) // summation for diagonals
			{
				for (k = 0; k < j; k++)
					sum += pow(lower[j][k], 2);
				lower[j][j] = sqrt(matrix[j][j] -
					sum);
			}
			else
			{
				// Evaluating L(i, j) using L(j, j)
				for (k = 0; k < j; k++)
					sum += (lower[i][k] * lower[j][k]);
				lower[i][j] = (matrix[i][j] - sum) /
					lower[j][j];
			}
		}
	}


	k = 0;
	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++)
		{
			temp_array[k] = lower[i][j];
			k++;
		}

	for (i = 0; i < n; i++)
		if (matrix[i]) free(matrix[i]);
	if (matrix) free(matrix);

	for (i = 0; i < n; i++)
		if (lower[i]) free(lower[i]);
	if (lower) free(lower);


	return 1;
}

// Generate Multivariate Random Number
double** random_mvrn(long number_random, long number_variable, double** Corr)
{
	long i, j, n, k;
	double mvrn;

	double** Chol_Array = Cholesky_Decomposition(Corr, number_variable);
	double* RANDN = (double*)malloc(sizeof(double) * number_variable);

	double** MVRN = (double**)malloc(sizeof(double*) * number_random);
	for (i = 0; i < number_random; i++)
		MVRN[i] = (double*)malloc(sizeof(double) * number_variable);

	for (i = 0; i < number_random; i++)
	{
		for (n = 0; n < number_variable; n++)
		{
			RANDN[n] = randnorm();
		}

		for (j = 0; j < number_variable; j++)
		{
			mvrn = 0.0;
			for (k = 0; k <= j; k++)
			{
				mvrn += Chol_Array[j][k] * RANDN[k];
			}
			MVRN[i][j] = mvrn;
		}
	}

	for (i = 0; i < number_variable; i++)
		if (Chol_Array[i]) free(Chol_Array[i]);
	if (Chol_Array) free(Chol_Array);

	if (RANDN) free(RANDN);
	return MVRN;
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
DLLEXPORT(long) Tri_diagonal_Fast(
	double* Alpha,    // Tridiagonal Matrix에서 왼쪽 대각선 행렬
	double* Beta,     // Tridiagonal Matrix에서 중앙 대각선 행렬
	double* Gamma,    // Tridiagonal Matrix에서 오른쪽 대각선 행렬
	double* V_T1,     // V(T1)
	long N,           // 대각선 행렬들의 길이
	double* TempAlpha,// 임시 행렬1 
	double* TempBeta, // 임시 행렬2
	double* TempGamma // 임시 행렬3
)
{
	long i;

	for (i = 0; i <= N - 1; i++)
	{
		TempAlpha[i] = Alpha[i];
		TempBeta[i] = Beta[i];
		TempGamma[i] = Gamma[i];
	}

	TempAlpha[0] = 0.0;
	TempGamma[N - 1] = 0.0;

	if (N <= 1) V_T1[0] /= TempBeta[0];
	else {
		for (i = 1; i <= N - 1; i++) {
			TempAlpha[i] /= TempBeta[i - 1];
			TempBeta[i] -= TempAlpha[i] * TempGamma[i - 1];
			V_T1[i] -= TempAlpha[i] * V_T1[i - 1];
		}
		V_T1[N - 1] /= TempBeta[N - 1];

		for (i = N - 2; i >= 0; i--) V_T1[i] = (V_T1[i] - TempGamma[i] * V_T1[i + 1]) / TempBeta[i];
	}
	return 1;
}

// LocalVol Data와 ,S, T를 넣으면 Interpolated Local Vol을 계산해줌. (느린계산)
double Calc_Volatility(
	// LocalVol Data
	long nt,           // Term 개수        
	long nparity,      // Parity 개수
	double* t,         // Term Array     ex) [0.25,  0.5,   1, ...] 
	double* parity,    // Parity Array   exp)[0.5,   0.7,  1.0, ...]
	double** vol_array,// Vol Array
	// Simulation Data
	double T,          // 시점
	double S           // 현재주가(%)
)
{

	long node_T;
	long node_S;
	double slope_T;
	double slope_S;
	double result_vol;


	if (T <= t[0])
	{
		node_T = 0;
		if (S <= parity[0])                      // T 가 minT 보다 작고, S가 minS 보다 작음
		{
			node_S = 0;
			result_vol = vol_array[node_S][node_T];
		}
		else if (S >= parity[nparity - 1])          // T 가 minT 보다 작고, S가 maxS 보다 큼
		{
			node_S = nparity - 1;
			result_vol = vol_array[node_S][node_T];
		}
		else                                    //  T 가 minT 보다 작고, S가 minS ~ maxS 사이에 있음
		{
			for (node_S = 0; node_S < nparity - 1; node_S++)
				if (S >= parity[node_S] && S < parity[node_S + 1]) break;
			slope_S = (vol_array[node_S + 1][node_T] * vol_array[node_S + 1][node_T] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (parity[node_S + 1] - parity[node_S]);
			// V_s * dS + V(S,t)
			result_vol = sqrt(slope_S * (S - parity[node_S]) + vol_array[node_S][node_T] * vol_array[node_S][node_T]);
		}
	}
	else if (T >= t[nt - 1])
	{
		node_T = nt - 1;
		if (S <= parity[0])                     // T 가 maxT 보다 크고, S가 minS 보다 작음
		{
			node_S = 0;
			result_vol = vol_array[node_S][node_T];
		}
		else if (S >= parity[nparity - 1])        // T 가 maxT 보다 크고, S가 maxS 보다 큼
		{
			node_S = nparity - 1;
			result_vol = vol_array[node_S][node_T];
		}
		else                                   // T 가 maxT 보다 크고 S가 minS ~ maxS 사이에 있음
		{
			for (node_S = 0; node_S < nparity - 1; node_S++)
				if (S >= parity[node_S] && S < parity[node_S + 1]) break;
			slope_S = (vol_array[node_S + 1][node_T] * vol_array[node_S + 1][node_T] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (parity[node_S + 1] - parity[node_S]);
			// V_s * dS + V(S,t)
			result_vol = sqrt(slope_S * (S - parity[node_S]) + vol_array[node_S][node_T] * vol_array[node_S][node_T]);
		}
	}
	else {
		for (node_T = 0; node_T < nt - 1; node_T++)
			if (T >= t[node_T] && T < t[node_T + 1]) break;
		if (S <= parity[0])                   // T가 minT~ maxT 사이에 있고, S가 minS 보다 작음
		{
			node_S = 0;
			slope_T = (vol_array[node_S][node_T + 1] * vol_array[node_S][node_T + 1] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (t[node_T + 1] - t[node_T]);
			// V_t * dt + V(S,t)
			result_vol = sqrt(slope_T * (T - t[node_T]) + vol_array[node_S][node_T] * vol_array[node_S][node_T]);
		}
		else if (S >= parity[nparity - 1])       // T가 minT~ maxT 사이에 있고, S가 maxS 보다 큼
		{
			node_S = nparity - 1;
			slope_T = (vol_array[node_S][node_T + 1] * vol_array[node_S][node_T + 1] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (t[node_T + 1] - t[node_T]);
			// V_t * dt + V(S,t)
			result_vol = sqrt(slope_T * (T - t[node_T]) + vol_array[node_S][node_T] * vol_array[node_S][node_T]);
		}
		else                                  // T가 minT~ maxT 사이에 있고, S가 minS~maxS 사이에 있음
		{
			for (node_S = 0; node_S < nparity - 1; node_S++)
				if (S >= parity[node_S] && S < parity[node_S + 1]) break;
			slope_S = (vol_array[node_S + 1][node_T] * vol_array[node_S + 1][node_T] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (parity[node_S + 1] - parity[node_S]);
			slope_T = (vol_array[node_S][node_T + 1] * vol_array[node_S][node_T + 1] - vol_array[node_S][node_T] * vol_array[node_S][node_T]) / (t[node_T + 1] - t[node_T]);
			// V_t * dt + V_s * dS + V(S,t)
			result_vol = sqrt(slope_S * (S - parity[node_S]) + slope_T * (T - t[node_T]) + vol_array[node_S][node_T] * vol_array[node_S][node_T]);
		}
	}

	return result_vol;
}

// LocalVol Data와 ,S, T를 넣으면 Interpolated Local Vol을 계산해줌. 
// (그때그때 가까운 node 위치를 기억하여 빠른계산)
double Calc_Volatility(long N_Term, long N_Parity, double* Term, double* Parity, double** LocalVolMat, double T, double S, long* Prev_NodeT, long* Prev_NodeS)
{

	long Current_Node_T = 0;
	long Current_Node_S = 0;
	double Slope_T;
	double Slope_S;
	double Result_Vol;

	if (T <= Term[0])
	{
		Current_Node_T = 0;
		Prev_NodeT[0] = 0;
		if (S <= Parity[0])
		{
			Current_Node_S = 0;
			Prev_NodeS[0] = 0;
			Result_Vol = LocalVolMat[Current_Node_S][Current_Node_T];
			return Result_Vol;
		}
		else if (S >= Parity[N_Parity - 1])
		{
			Current_Node_S = N_Parity - 1;
			Prev_NodeS[0] = N_Parity - 1;
			Result_Vol = LocalVolMat[Current_Node_S][Current_Node_T];
			return Result_Vol;
		}
		else
		{
			if (Parity[Prev_NodeS[0]] <= S)
			{
				for (Current_Node_S = Prev_NodeS[0]; Current_Node_S < N_Parity - 1; Current_Node_S++)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			else
			{
				for (Current_Node_S = max(Prev_NodeS[0] - 1, 0); Current_Node_S >= 0; Current_Node_S--)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			Slope_S = (LocalVolMat[Prev_NodeS[0] + 1][Prev_NodeT[0]] - LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]) / (Parity[Prev_NodeS[0] + 1] - Parity[Prev_NodeS[0]]);
			// V_s * dS + V(S,t)
			Result_Vol = (Slope_S * (S - Parity[Prev_NodeS[0]]) + LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]);
			return Result_Vol;
		}
	}
	else if (T >= Term[N_Term - 1])
	{
		Current_Node_T = N_Term - 1;
		Prev_NodeT[0] = N_Term - 1;
		if (S <= Parity[0])
		{
			Current_Node_S = 0;
			Prev_NodeS[0] = 0;
			Result_Vol = LocalVolMat[Current_Node_S][Current_Node_T];
			return Result_Vol;
		}
		else if (S >= Parity[N_Parity - 1])
		{
			Current_Node_S = N_Parity - 1;
			Prev_NodeS[0] = N_Parity - 1;
			Result_Vol = LocalVolMat[Current_Node_S][Current_Node_T];
			return Result_Vol;
		}
		else
		{
			if (Parity[Prev_NodeS[0]] <= S)
			{
				for (Current_Node_S = Prev_NodeS[0]; Current_Node_S < N_Parity - 1; Current_Node_S++)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			else
			{
				for (Current_Node_S = max(Prev_NodeS[0] - 1, 0); Current_Node_S >= 0; Current_Node_S--)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			Slope_S = (LocalVolMat[Prev_NodeS[0] + 1][Prev_NodeT[0]] - LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]) / (Parity[Prev_NodeS[0] + 1] - Parity[Prev_NodeS[0]]);
			// V_s * dS + V(S,t)
			Result_Vol = (Slope_S * (S - Parity[Prev_NodeS[0]]) + LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]);
			return Result_Vol;
		}
	}
	else
	{
		for (Current_Node_T = Prev_NodeT[0]; Current_Node_T < N_Term - 1; Current_Node_T++)
			if (T >= Term[Current_Node_T] && T < Term[Current_Node_T + 1])
			{
				Prev_NodeT[0] = Current_Node_T;
				break;
			}

		if (S <= Parity[0])                   // T가 minT~ maxT 사이에 있고, S가 minS 보다 작음
		{
			Current_Node_S = 0;
			Prev_NodeS[0] = 0;
			Result_Vol = LocalVolMat[Current_Node_S][Prev_NodeT[0]];
			return Result_Vol;
		}
		else if (S >= Parity[N_Parity - 1])
		{
			Current_Node_S = N_Parity - 1;
			Prev_NodeS[0] = N_Parity - 1;
			Result_Vol = LocalVolMat[Current_Node_S][Prev_NodeT[0]];
			return Result_Vol;
		}
		else
		{
			if (Parity[Prev_NodeS[0]] <= S)
			{
				for (Current_Node_S = Prev_NodeS[0]; Current_Node_S < N_Parity - 1; Current_Node_S++)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			else
			{
				for (Current_Node_S = max(Prev_NodeS[0] - 1, 0); Current_Node_S >= 0; Current_Node_S--)
				{
					if (S >= Parity[Current_Node_S] && S < Parity[Current_Node_S + 1])
					{
						Prev_NodeS[0] = Current_Node_S;
						break;
					}
				}
			}
			Slope_S = (LocalVolMat[Prev_NodeS[0] + 1][Prev_NodeT[0]] - LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]) / (Parity[Prev_NodeS[0] + 1] - Parity[Prev_NodeS[0]]);
			Slope_T = (LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0] + 1] - LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]) / (Term[Prev_NodeT[0] + 1] - Term[Prev_NodeT[0]]);
			// V_t * dt + V_s * dS + V(S,t)
			Result_Vol = (Slope_S * (S - Parity[Prev_NodeS[0]]) + Slope_T * (T - Term[Prev_NodeT[0]]) + LocalVolMat[Prev_NodeS[0]][Prev_NodeT[0]]);
			return Result_Vol;
		}
	}
}

//Discount Factor 계산
DLLEXPORT(double) Calc_Discount_Factor(
	double* TermArray,
	double* RateArray,
	long LengthArray,
	double T
)
{
	double DF;
	DF = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T) * T);

	return DF;
}

DLLEXPORT(double) Calc_Zero_Rate(
	double* TermArray,
	double* RateArray,
	long LengthArray,
	double T
)
{
	return Interpolate_ExpLinear(TermArray, RateArray, LengthArray, T);
}

double Calc_Forward_Rate_Fast(
	double* TermArray, // 기간구조의 기간 Array [0.25,  0.5,   1.0, ....]
	double* RateArray, // 기간구조의 Rate Array [0.008, 0.012, 0.014, ...]
	long LengthArray,  // 기간구조 개수
	double T1,         // Forward Start 시점
	double T2,		   // Forward End 시점
	long* TimePos
)
{
	long i;
	long startidx = *TimePos + 0;
	double dt = T2 - T1;
	double r1, r2;
	double DF1, DF2, FRate;

	if (T1 <= TermArray[0])
	{
		r1 = RateArray[0];
	}
	else if (T1 > TermArray[LengthArray - 1])
	{
		r1 = RateArray[LengthArray - 1];
	}
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T1 < TermArray[i])
			{
				*TimePos = i - 1;
				r1 = (RateArray[i] - RateArray[i - 1]) / (TermArray[i] - TermArray[i - 1]) * (T1 - TermArray[i - 1]) + RateArray[i - 1];
				break;
			}
		}
	}

	if (T2 > T1)
	{
		if (T2 <= TermArray[0])
		{
			r2 = RateArray[0];
		}
		else if (T2 > TermArray[LengthArray - 1])
		{
			r2 = RateArray[LengthArray - 1];
		}
		else
		{
			for (i = max(1, startidx); i < LengthArray; i++)
			{
				if (T2 < TermArray[i])
				{
					r2 = (RateArray[i] - RateArray[i - 1]) / (TermArray[i] - TermArray[i - 1]) * (T2 - TermArray[i - 1]) + RateArray[i - 1];
					break;
				}
			}
		}
	}
	else
	{
		r2 = r1;
	}


	if (T2 == T1) return r1;
	else
	{
		DF1 = exp(-r1 * T1);
		DF2 = exp(-r2 * T2);
		FRate = 1.0 / dt * (DF1 / DF2 - 1.0);
		return FRate;
	}
}

double Calc_Forward_Rate_Daily(
	double* Term,
	double* Rate,
	long LengthArray,
	double T1,
	long* TimePos
)
{
	long i;
	long startidx = *TimePos + 0;
	double dt = 0.00273972602739726;
	double T2 = T1 + dt;
	double r1, r2;
	double DF1, DF2, FRate;

	if (T1 <= Term[0]) r1 = Rate[0];
	else if (T1 >= Term[LengthArray - 1]) r1 = Rate[LengthArray - 1];
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T1 < Term[i])
			{
				*TimePos = i - 1;
				r1 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T1 - Term[i - 1]) + Rate[i - 1];
				break;
			}
		}
	}

	if (T2 <= Term[0]) r2 = Rate[0];
	else if (T2 >= Term[LengthArray - 1]) r2 = Rate[LengthArray - 1];
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T2 < Term[i])
			{
				r2 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T2 - Term[i - 1]) + Rate[i - 1];
				break;
			}
		}
	}

	DF1 = exp(-r1 * T1);
	DF2 = exp(-r2 * T2);
	FRate = 1.0 / dt * (DF1 / DF2 - 1.0);
	return FRate;
}

double Calc_Forward_Rate_Daily(
	double* Term,
	double* Rate,
	long LengthArray,
	double T1,
	long* TimePos,
	long NHoliday
)
{
	long i;
	long startidx = *TimePos + 0;
	double dt = 0.00273972602739726;
	double T2 = T1 + ((double)(NHoliday + 1)) * dt;
	double r1, r2;
	double DeltaT = T2 - T1;
	double DF1, DF2, FRate;

	if (T1 <= Term[0]) r1 = Rate[0];
	else if (T1 >= Term[LengthArray - 1]) r1 = Rate[LengthArray - 1];
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T1 < Term[i])
			{
				*TimePos = i - 1;
				r1 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T1 - Term[i - 1]) + Rate[i - 1];
				break;
			}
		}
	}

	if (T2 <= Term[0]) r2 = Rate[0];
	else if (T2 >= Term[LengthArray - 1]) r2 = Rate[LengthArray - 1];
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T2 < Term[i])
			{
				r2 = (Rate[i] - Rate[i - 1]) / (Term[i] - Term[i - 1]) * (T2 - Term[i - 1]) + Rate[i - 1];
				break;
			}
		}
	}

	DF1 = exp(-r1 * T1);
	DF2 = exp(-r2 * T2);
	FRate = 1.0 / DeltaT * (DF1 / DF2 - 1.0);
	return FRate;
}

double Calc_Forward_FXVol_Daily(
	double* TermArray, // 기간구조의 기간 Array [0.25,  0.5,   1.0, ....]
	double* FXVolArray, // 기간구조의 Rate Array [0.008, 0.012, 0.014, ...]
	long LengthArray,  // 기간구조 개수
	double T1,         // Forward Start 시점
	long* TimePos
)
{
	long i;
	long startidx = *TimePos + 0;
	double dt = 0.00273972602739726;
	double T2 = T1 + dt;
	double V1, V2;
	double DF1, DF2, FVar, FVol;

	if (T1 <= TermArray[0])
	{
		V1 = FXVolArray[0];
	}
	else if (T1 > TermArray[LengthArray - 1])
	{
		V1 = FXVolArray[LengthArray - 1];
	}
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T1 < TermArray[i])
			{
				*TimePos = i - 1;
				V1 = (FXVolArray[i] - FXVolArray[i - 1]) / (TermArray[i] - TermArray[i - 1]) * (T1 - TermArray[i - 1]) + FXVolArray[i - 1];
				break;
			}
		}
	}

	if (T2 <= TermArray[0])
	{
		V2 = FXVolArray[0];
	}
	else if (T2 > TermArray[LengthArray - 1])
	{
		V2 = FXVolArray[LengthArray - 1];
	}
	else
	{
		for (i = max(1, startidx); i < LengthArray; i++)
		{
			if (T2 < TermArray[i])
			{
				V2 = (FXVolArray[i] - FXVolArray[i - 1]) / (TermArray[i] - TermArray[i - 1]) * (T2 - TermArray[i - 1]) + FXVolArray[i - 1];
				break;
			}
		}
	}

	FVar = (T2 * V2 * V2 - T1 * V1 * V1) / dt;
	if (FVar > 0.0) FVol = sqrt(FVar);
	else FVol = V1;

	return FVol;
}

//Forward Rate 계산
DLLEXPORT(double) Calc_Forward_Rate(
	double* TermArray, // 기간구조의 기간 Array [0.25,  0.5,   1.0, ....]
	double* RateArray, // 기간구조의 Rate Array [0.008, 0.012, 0.014, ...]
	long LengthArray,  // 기간구조 개수
	double T1,         // Forward Start 시점
	double T2          // Forward End 시점
)
{
	double DFT1;
	double DFT2;
	double FRate;
	//Linear Interpolation
	if (T1 < TermArray[LengthArray - 1] && T1> TermArray[0])
	{
		DFT1 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T1) * T1);
		DFT2 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T2) * T2);
		FRate = 1.0 / (T2 - T1) * (DFT1 / DFT2 - 1.0);
	}
	else if (T1 <= TermArray[0])
	{
		DFT1 = exp(-RateArray[0] * T1);
		DFT2 = exp(-Interpolate_Linear(TermArray, RateArray, LengthArray, T2) * T2);
		FRate = 1.0 / (T2 - T1) * (DFT1 / DFT2 - 1.0);
	}
	else
	{
		DFT1 = exp(-RateArray[LengthArray - 1] * T1);
		DFT2 = exp(-RateArray[LengthArray - 1] * T2);
		FRate = 1.0 / (T2 - T1) * (DFT1 / DFT2 - 1.0);
	}

	return FRate;
}

// matrix inversioon
// the result is put in Y
// Too slow to use
// Delete Function
// 너무느리다 그냥 가우스 소거법으로 역행렬 구하는게 더 빠름
//void MatrixInversion(double** A, long order, double** Y)
//{
//	long i, j, k, n;
//	// MinorMatrixList 추가 2022.08.30 임대선 미리 만들어두고 반복사용하기
//	double*** MinorMatrixList = (double***)malloc(sizeof(double**) * order);
//	for (i = 0; i < order; i++)
//	{
//		n = max(1, i);
//		MinorMatrixList[i] = (double**)malloc(sizeof(double*) * n);
//		for (j = 0; j < n; j++)
//		{
//			MinorMatrixList[i][j] = (double*)malloc(sizeof(double) * n);
//		}
//	}
//	// get the determinant of a
//	double det = 1.0 / CalcDeterminant(A, order, MinorMatrixList);
//
//	// memory allocation
//	double* temp = new double[(order - 1) * (order - 1)];
//	double** minor = new double* [order - 1];
//	for (i = 0; i < order - 1; i++)
//		minor[i] = temp + (i * (order - 1));
//
//	for (j = 0; j < order; j++)
//	{
//		for (i = 0; i < order; i++)
//		{
//			// get the co-factor (matrix) of A(j,i)
//			GetMinor(A, minor, j, i, order);
//			Y[i][j] = det * CalcDeterminant(minor, order - 1, MinorMatrixList);
//			if ((i + j) % 2 == 1)
//				Y[i][j] = -Y[i][j];
//		}
//	}
//
//	// release memory
//	delete[] temp;
//	delete[] minor;
//
//	for (i = 0; i < order; i++)
//	{
//		n = max(1, i);
//		for (j = 0; j < n; j++)
//		{
//			free(MinorMatrixList[i][j]);
//		}
//		free(MinorMatrixList[i]);
//	}
//	free(MinorMatrixList);
//}

// Inverse Matrix를 계산한다. (가우스소거법 사용으로 대체)
void MatrixInversion(double** MyMatrix, long n, double** InvMatrix)
{
	long i, j, k;
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
		for (j = 0; j < n; j++)
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


// calculate the cofactor of element (row,col)
long GetMinor(double** src, double** dest, long row, long col, long order)
{
	// indicate which col and row is being copied to dest
	long colCount = 0, rowCount = 0;

	for (long i = 0; i < order; i++)
	{
		if (i != row)
		{
			colCount = 0;
			for (long j = 0; j < order; j++)
			{
				// when j is not the element
				if (j != col)
				{
					dest[rowCount][colCount] = src[i][j];
					colCount++;
				}
			}
			rowCount++;
		}
	}

	return 1;
}

// Calculate the determinant recursively.
double CalcDeterminant(double** mat, long order, double*** MinorMatrixList)
{

	if (order == 1) return mat[0][0];
	else if (order == 2) return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0];
	else if (order == 3) return mat[0][0] * mat[1][1] * mat[2][2] + mat[0][1] * mat[1][2] * mat[2][0] + mat[0][2] * mat[1][0] * mat[2][1] - (mat[0][2] * mat[1][1] * mat[2][0] + mat[0][1] * mat[1][0] * mat[2][2] + mat[0][0] * mat[1][2] * mat[2][1]);
	else if (order == 4)
	{
		double p1, p2, p3, p4, detA;
		p1 = mat[0][0] * (mat[1][1] * mat[2][2] * mat[3][3] + mat[1][2] * mat[2][3] * mat[3][1] + mat[1][3] * mat[2][1] * mat[3][2] -
			mat[1][3] * mat[2][2] * mat[3][1] - mat[1][2] * mat[2][1] * mat[3][3] - mat[1][1] * mat[2][3] * mat[3][2]);

		p2 = -mat[1][0] * (mat[0][1] * mat[2][2] * mat[3][3] + mat[0][2] * mat[2][3] * mat[3][1] + mat[0][3] * mat[2][1] * mat[3][2] -
			mat[0][3] * mat[2][2] * mat[3][1] - mat[0][2] * mat[2][1] * mat[3][3] - mat[0][1] * mat[2][3] * mat[3][2]);

		p3 = mat[2][0] * (mat[0][1] * mat[1][2] * mat[3][3] + mat[0][2] * mat[1][3] * mat[3][1] + mat[0][3] * mat[1][1] * mat[3][2] -
			mat[0][3] * mat[1][2] * mat[3][1] - mat[0][2] * mat[1][1] * mat[3][3] - mat[0][1] * mat[1][3] * mat[3][2]);

		p4 = -mat[3][0] * (mat[0][1] * mat[1][2] * mat[2][3] + mat[0][2] * mat[1][3] * mat[2][1] + mat[0][3] * mat[1][1] * mat[2][2] -
			mat[0][3] * mat[1][2] * mat[2][1] - mat[0][2] * mat[1][1] * mat[2][3] - mat[0][1] * mat[1][3] * mat[2][2]);
		detA = p1 + p2 + p3 + p4;
		return detA;
	}
	double det = 0;

	double** minor;
	minor = MinorMatrixList[max(0, order - 1)];
	//minor = new double* [order - 1];
	//for (long i = 0; i < order - 1; i++)
	//	minor[i] = new double[order - 1];

	for (long i = 0; i < order; i++)
	{
		// get minor of element (0,i)
		GetMinor(mat, minor, 0, i, order);
		// the recusion is here!
		det += (i % 2 == 1 ? -1.0 : 1.0) * mat[0][i] * CalcDeterminant(minor, order - 1, MinorMatrixList);

	}

	// release memory
	//for (long i = 0; i < order - 1; i++)
	//	delete[] minor[i];
	//delete[] minor;

	return det;
}

void bubble_sort(double* arr, long count, long ascending)
{
	double temp;
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

void bubble_sort(double* arr, long count)
{
	bubble_sort(arr, count, 1);
}

void bubble_sort(double* arr, long* Index, long count, long ascending)
{
	double temp;
	long temp_idx;
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
					temp_idx = Index[j];
					arr[j] = arr[j + 1];
					Index[j] = Index[j + 1];
					arr[j + 1] = temp;
					Index[j + 1] = temp_idx;
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
					temp_idx = Index[j];
					arr[j] = arr[j + 1];
					Index[j] = Index[j + 1];
					arr[j + 1] = temp;
					Index[j + 1] = temp_idx;
				}
			}
		}
	}
}

void bubble_sort(double* arr, long* Index, long count)
{
	bubble_sort(arr, Index, count, 1);
}

void bubble_sort_index(long* index_arr, double* value_arr, long count, long ascending)
{
	long temp;
	double temp_value;
	long i, j;

	if (ascending == 1)
	{
		for (i = 0; i < count; i++)
		{
			for (j = 0; j < count - 1; j++)
			{
				if (index_arr[j] > index_arr[j + 1])
				{
					temp = index_arr[j];
					temp_value = value_arr[i];
					index_arr[j] = index_arr[j + 1];
					value_arr[j] = value_arr[j + 1];
					index_arr[j + 1] = temp;
					value_arr[j + 1] = temp_value;
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
				if (index_arr[j] < index_arr[j + 1])
				{
					temp = index_arr[j];
					temp_value = value_arr[i];
					index_arr[j] = index_arr[j + 1];
					value_arr[j] = value_arr[j + 1];
					index_arr[j + 1] = temp;
					value_arr[j + 1] = temp_value;
				}
			}
		}
	}
}

void bubble_sort_index(long* index_arr, double* value_arr, long count)
{
	bubble_sort_index(index_arr, value_arr, count, 1);
}

long* RankArray(double* list, long list_length, long ascending)
{
	long i, j, max_rank = -1;
	long* rank = (long*)malloc(list_length * sizeof(long));
	for (i = 0; i < list_length; i++) rank[i] = 1;

	for (i = 0; i < list_length; i++)
	{
		for (j = i + 1; j < list_length; j++)
		{
			if (list[i] > list[j]) rank[j]++;
			else if (list[i] < list[j]) rank[i]++;
		}
		max_rank = max(max_rank, rank[i]);
	}

	if (ascending != 0)
		for (i = 0; i < list_length; i++)
			rank[i] = max_rank - rank[i] + 1;
	return rank;
}

// MatrixA와 MatrixB를 곱한 Matrix를 리턴한다.(나중에 메모리 수동 해제해야함)
double** Dot2dArray(double** A, long shape_A[2], double** B, long shape_B[2])
{
	long p, q, i, j, k, maxk;
	double s;
	p = shape_A[0];
	q = shape_B[1];
	double** ResultArray = (double**)malloc(sizeof(double*) * p);
	for (i = 0; i < p; i++)
		ResultArray[i] = (double*)calloc(q, sizeof(double));

	if (shape_A[1] != shape_B[0])
	{
		return ResultArray;
	}
	else
	{
		maxk = shape_A[1];
		for (i = 0; i < p; i++)
		{
			for (j = 0; j < q; j++)
			{
				s = 0.0;
				for (k = 0; k < maxk; k++)
				{
					s += A[i][k] * B[k][j];;
				}
				ResultArray[i][j] = s;
			}
		}
		return ResultArray;
	}
}

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

double** XprimeDotX(double** X, long ShapeX[2])
{
	long i, j, k;
	long ShapeXpX[2] = { ShapeX[1], ShapeX[1] };
	long n = ShapeX[0];
	long idx_row;
	long idx_col;

	double s = 0.0;
	double a, b;

	double** XpDotX = make_array(ShapeXpX[0], ShapeXpX[1]);
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
	return XpDotX;
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

long XprimeY(double** X, long shape_X[2], double* Y, long LengthY, double** XprimeYMatrix)
{
	long i, j, k;
	long p = shape_X[1];
	long n = shape_X[0];
	double s = 0.0;
	for (i = 0; i < p; i++)
	{
		s = 0.0;
		for (j = 0; j < n; j++)
		{
			s += X[j][i] * Y[j];
		}
		XprimeYMatrix[i][0] = s;
	}
	return 1;
}

double* OLSBeta(double* Y, long LengthY, double** X, long ShapeX[2])
{
	long i;
	long n = ShapeX[1];

	double* Unknown = (double*)malloc(sizeof(double) * ShapeX[1]);		// 리턴용 할당
	double* Known = (double*)malloc(sizeof(double) * ShapeX[1]);		// 할당1
	double** XpX = XprimeDotX(X, ShapeX);								// 할당2

	long Shape_XpdotY[2] = { ShapeX[1], 1 };
	double** XpdotY = make_array(ShapeX[1], 1);							// 할당3

	i = XprimeY(X, ShapeX, Y, LengthY, XpdotY);
	for (i = 0; i < n; i++) Known[i] = XpdotY[i][0];

	gaussian_elimination(XpX, Known, Unknown, n);

	free(Known);														// 할당1 해제
	for (i = 0; i < ShapeX[1]; i++) free(XpX[i]);						// 할당2 해제
	free(XpX);
	for (i = 0; i < ShapeX[1]; i++) free(XpdotY[i]);					// 할당3 해제
	free(XpdotY);
	return Unknown;
}


void Calc_C(long nRate, double* Term, double* Rate, double* CArray)
{
	long i, n;
	double h1, h0;
	long Length = nRate - 2;

	CArray[0] = 0.0;
	CArray[nRate - 1] = 0.0;

	double* RHS = CArray + 1;
	double* Alpha = (double*)malloc(sizeof(double) * (nRate - 2));
	double* Beta = (double*)malloc(sizeof(double) * (nRate - 2));
	double* Gamma = (double*)malloc(sizeof(double) * (nRate - 2));

	n = 0;
	for (i = 1; i < nRate - 1; i++)
	{
		h1 = Term[i + 1] - Term[i];
		h0 = Term[i] - Term[i - 1];
		if (n == 0)
		{
			Alpha[n] = 0.0;
			Beta[n] = 2.0 * (h0 + h1);
			Gamma[n] = h1;
		}
		else if (n == nRate - 2)
		{
			Gamma[n] = 0.0;
			Beta[n] = 2.0 * (h0 + h1);
			Gamma[n] = h1;
		}
		else {
			Alpha[n] = h0;
			Beta[n] = 2.0 * (h0 + h1);
			Gamma[n] = h1;
		}
		RHS[i - 1] = 3.0 * ((Rate[i + 1] - Rate[i]) / h1 - (Rate[i] - Rate[i - 1]) / h0);
		n++;
	}

	for (i = 1; i <= Length - 1; i++) {
		Alpha[i] /= Beta[i - 1];
		Beta[i] -= Alpha[i] * Gamma[i - 1];
		RHS[i] -= Alpha[i] * RHS[i - 1];
	}
	RHS[Length - 1] /= Beta[Length - 1];

	for (i = Length - 2; i >= 0; i--) RHS[i] = (RHS[i] - Gamma[i] * RHS[i + 1]) / Beta[i];

	free(Alpha);
	free(Beta);
	free(Gamma);
}

double CubicSpline(long nRate, double* Term, double* Rate, double TargetTerm)
{
	long i;
	double a, b, d, y, hi, xp;

	if (nRate < 4) return Interpolate_Linear(Term, Rate, nRate, TargetTerm);

	double* CArray = (double*)malloc(sizeof(double) * nRate);
	Calc_C(nRate, Term, Rate, CArray);

	if (Term[0] >= TargetTerm)
	{
		hi = Term[1] - Term[0];
		xp = TargetTerm - Term[0];
		a = Rate[0];
		b = (Rate[1] - Rate[0]) / hi - hi * (2.0 * CArray[0] + CArray[1]) / 3.0;
		d = (CArray[1] - CArray[0]) / (3.0 * hi);
		y = a + b * xp + CArray[0] * xp * xp + d * xp * xp * xp;
	}
	else if (Term[nRate - 1] <= TargetTerm)
	{
		hi = Term[nRate - 1] - Term[nRate - 2];
		xp = TargetTerm - Term[nRate - 2];
		a = Rate[nRate - 2];
		b = (Rate[nRate - 1] - Rate[nRate - 2]) / hi - hi * (2.0 * CArray[nRate - 2] + CArray[nRate - 1]) / 3.0;
		d = (CArray[nRate - 1] - CArray[nRate - 2]) / (3.0 * hi);
		y = a + b * xp + CArray[nRate - 2] * xp * xp + d * xp * xp * xp;
	}
	else
	{
		for (i = 1; i < nRate; i++)
		{
			if (Term[i] > TargetTerm) {
				hi = Term[i] - Term[i - 1];
				xp = TargetTerm - Term[i - 1];
				a = Rate[i - 1];
				b = (Rate[i] - Rate[i - 1]) / hi - hi * (2.0 * CArray[i - 1] + CArray[i]) / 3.0;
				d = (CArray[i] - CArray[i - 1]) / (3.0 * hi);
				y = a + b * xp + CArray[i - 1] * xp * xp + d * xp * xp * xp;
				break;
			}
		}
	}

	free(CArray);
	return y;
}

long Calibration_CubicSpline_Params(
	long nRate,
	double* Term,
	double* Rate,
	double* C_Array	// Out: 2차 계수 Param
)
{
	long ResultCode = 1;

	if (nRate < 4)
	{
		ResultCode = -1;
		return ResultCode;
	}

	Calc_C(nRate, Term, Rate, C_Array);
	return ResultCode;
}

double CubicInterpolation(long nRate, double* Term, double* Rate, double* C_Array, double TargetTerm)
{
	long i;
	double a, b, d, y, hi, xp;

	if (nRate < 4) return Interpolate_Linear(Term, Rate, nRate, TargetTerm);

	if (Term[0] >= TargetTerm)
	{
		// Extrapolation
		//hi = Term[1] - Term[0];
		//xp = TargetTerm - Term[0];
		//a = Rate[0];
		//b = (Rate[1] - Rate[0])/ hi - hi * (2.0 * C_Array[0] + C_Array[1]) / 3.0;
		//d = (C_Array[1] - C_Array[0]) / (3.0 * hi);
		//y = a + b * xp + C_Array[0] * xp * xp + d * xp * xp * xp;
		y = Rate[0];
	}
	else if (Term[nRate - 1] <= TargetTerm)
	{
		// Extrapolation
		//hi = Term[nRate - 1] - Term[nRate - 2];
		//xp = TargetTerm - Term[nRate - 2];
		//a = Rate[nRate - 2];
		//b = (Rate[nRate - 1] - Rate[nRate - 2]) / hi - hi * (2.0 * C_Array[nRate - 2] + C_Array[nRate - 1]) / 3.0;
		//d = (C_Array[nRate - 1] - C_Array[nRate - 2]) / (3.0 * hi);
		//y = a + b * xp + C_Array[nRate - 2] * xp * xp + d * xp * xp * xp;
		y = Rate[nRate - 1];
	}
	else
	{
		for (i = 1; i < nRate; i++)
		{
			if (Term[i] > TargetTerm) {
				hi = Term[i] - Term[i - 1];
				xp = TargetTerm - Term[i - 1];
				a = Rate[i - 1];
				b = (Rate[i] - Rate[i - 1]) / hi - hi * (2.0 * C_Array[i - 1] + C_Array[i]) / 3.0;
				d = (C_Array[i] - C_Array[i - 1]) / (3.0 * hi);
				y = a + b * xp + C_Array[i - 1] * xp * xp + d * xp * xp * xp;
				break;
			}
		}
	}
	return y;
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
	for (i = 0; i < n; i++) m += myarray[i] / (double)n;

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
		for (i = 0; i < n; i++)
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
	long i, j, k;
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
		for (j = 0; j < n; j++)
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

class OLS {
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
	OLS(double** X, double* Y, long num_data, long num_variables)
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
	OLS(double* X, double* Y, long num_data)
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

	~OLS()
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