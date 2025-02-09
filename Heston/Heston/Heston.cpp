#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "CalcDate.h"

#ifndef UTILITY
#include "Util.h"
#endif

#ifndef STRUCTURE
#include "Structure.h"
#endif

#ifndef NULL
#define NULL 0
#endif

#include <assert.h>
#include <vector>
#include <cmath>
#include <complex>
#include <algorithm>

#include <crtdbg.h>

using namespace std;

void round5(double** Matrix, long nrow, long ncol)
{
    for (long i = 0; i < nrow; i++)
        for (long j = 0; j < ncol; j++) Matrix[i][j] = floor(Matrix[i][j] * 100000.0 + 0.5) / 100000.0;
}

double BS_CallPrice(double S, double K, double T, double Sigma, double r, double div)
{
    long i, j;
    double d1, d2, Nd1, Nd2;
    d1 = (log(S / K) + (r - div + 0.5 * Sigma * Sigma) * T) / (Sigma * sqrt(T));
    d2 = d1 - Sigma * sqrt(T);
    Nd1 = CDF_N(d1);
    Nd2 = CDF_N(d2);
    return S * exp(-div * T) * Nd1 - K * exp(-r * T) * Nd2;
}

double trapezoidalMethod(vector<double> x, vector<double> y)
{
    long i;
    long n = x.size();
    double answer = 0.0;
    double add = 0.0;
    double prevadd = 0.0;
    long nsignchange = 0;
    for (i = 1; i < n; i++)
    {
        add = 0.5 * (x[i] - x[i - 1]) * (y[i - 1] + y[i]);
        answer += add;

        if (i >= 500 && fabs(add) > 1.0e-4) break;

        if (prevadd < 0 && add > 0) nsignchange += 1;
        else if (prevadd > 0 && add < 0) nsignchange += 1;

        if (nsignchange == 5) break;

        prevadd = add;

    }
    return answer;
}

double trapezoidalMethod(double* x, double* y, long n)
{
    long i;
    double answer = 0.0;
    double add = 0.0;
    for (i = 1; i < n; i++)
    {
        add = 0.5 * (x[i] - x[i - 1]) * (y[i - 1] + y[i]);
        answer += add;
        if (i >= 500 && add < answer * 0.000001)
            break;
    }
    return answer;
}

//S: Spot price
//K: Strike price
//r: Risk-free interest rate
//div: Dividend yield
//V0: Initial volatility
//tau: Time to maturity (years)
//LR_Vol: Long-run volatility
//kappa: Mean-reversion rate for volatility
//Vol_Of_Vol: Volatility of volatility
//rho: Price-volatility correlation
//gamma: Risk-aversion parameter
//optType: Option type (call or put)
double Heston_integrand(complex<double> K, double X, double V0,
    double tau, double LR_Vol, double kappa, double Vol_Of_Vol,
    double rho, double gamma)
{
    complex<double> thetaadj;
    double sigma = Vol_Of_Vol;

    double omega = kappa * LR_Vol;
    complex<double> t((sigma * sigma) * tau / 2.0, 0.0);
    complex<double> a((2.0 * omega) / (sigma * sigma), 0.0);
    complex<double> im(0.0, 1.0);

    if (gamma == 1.0) thetaadj = complex<double>(kappa, 0.0);
    else thetaadj = complex<double>((1.0 - gamma) * rho * sigma + sqrt(kappa * kappa - gamma * (1.0 - gamma) * sigma * sigma), 0.0);

    complex<double> b = (2.0 / (sigma * sigma)) * (thetaadj);
    complex<double> c = (K * K - im * K) / (sigma * sigma);
    complex<double> d = sqrt(b * b + 4.0 * c);
    complex<double> g = (b + d) / 2.0;
    complex<double> h = (b + d) / (b - d);
    complex<double> f1;
    complex<double> f2;
    complex<double> H;
    complex<double> temp1;
    complex<double> temp2;
    if (real(t * d) >= 500)
    {
        complex<double> td(500.0, imag(t * d));
        f1 = a * (t * g - log((1.0 - h * exp(td)) / (1.0 - h)));
        f2 = g * ((1.0 - exp(td)) / (1.0 - h * exp(td)));
        H = exp(f1 + f2 * V0);
    }
    else if (real(t * d) <= -500)
    {
        complex<double> td(-500.0, imag(t * d));
        f1 = a * (t * g - log((1.0 - h * exp(td)) / (1.0 - h)));
        f2 = g * ((1.0 - exp(td)) / (1.0 - h * exp(td)));
        H = exp(f1 + f2 * V0);
    }
    else
    {
        f1 = a * (t * g - log((1.0 - h * exp(t * d)) / (1.0 - h)));
        f2 = g * ((1.0 - exp(t * d)) / (1.0 - h * exp(t * d)));
        H = exp(f1 + f2 * V0);
    }
    //function to be integrated
    complex<double> integrand = exp(-im * K * X) * (H / (K * K - im * K));
    return real(integrand);
}


double HestonPrice_Test(double S, double K, double r, double div,
    double V0, double tau,
    double LR_Vol, double kappa, double Vol_Of_Vol, double rho,
    double gamma, long optType)
{
    double ki = 0.5;
    double price;
    complex<double> pass_phi;
    double omega = kappa * LR_Vol;
    double ksi = Vol_Of_Vol;
    double theta = kappa;
    int kmax = ceil(max(1000.0, 10.0 / sqrt(V0 * tau)));
    vector<double> int_x(kmax * 5);
    vector<double> int_y(kmax * 5);
    double X = log(S / K) + (r - div) * tau;
    int count = 0;
    //setting up the numerical integration
    for (double phi = 0.000001; phi < kmax; phi += 0.2)
    {
        int_x[count] = phi;
        pass_phi = complex<double>(phi, ki);
        int_y[count] = Heston_integrand(pass_phi, X, V0, tau, LR_Vol, kappa, Vol_Of_Vol, rho, gamma);
        count += 1;
    }
    //computing the price
    double callPrice = S * exp(-div * tau) - (1.0 / (PI)) * K * exp(-r * tau) * trapezoidalMethod(int_x, int_y);
    if (optType == 0)price = callPrice;
    else price = callPrice + K * exp(-r * tau) - S * exp(-div * tau);
    return price;
}

double HestonPrice(double S, double K, double r, double div,
    double init_variance, double tau,
    double LR_variance, double kappa, double volofvol, double rho,
    double gamma, long optType,
    long kmax, double* int_x, double* int_y)
{
    double ki = 0.5;
    double price;
    complex<double> pass_phi;
    long n = kmax * 5;
    long nsignchange = 0;
    double X = log(S / K) + (r - div) * tau;
    long count = 0;
    double trapezoidalValue = 0.0;
    double add = 0.0;
    double phi;
    double fabs_trapezoidalValue = 0.0;
    double prev_trapezoidalValue = 0.0;
    double fabs_add = 0.0;
    double prevadd = 0.0;
    double prev_fabs_add = 0.0;
    double dx = 0.2;

    //setting up the numerical integration
    for (phi = 0.00000001; phi < (double)kmax; phi += dx)
    {
        if (count == 2000)
            price = 0.0;
        int_x[count] = phi;
        pass_phi = complex<double>(phi, ki);
        int_y[count] = Heston_integrand(pass_phi, X, init_variance, tau, LR_variance, kappa, volofvol, rho, gamma);
        if (count > 0)
        {
            add = dx * 0.5 * (int_y[count - 1] + int_y[count]);
            fabs_add = fabs(add);
            prev_trapezoidalValue = trapezoidalValue;

            trapezoidalValue += add;

            if (prevadd < 0 && add > 0) nsignchange += 1;
            else if (prevadd > 0 && add < 0) nsignchange += 1;

            if (nsignchange == 5) break;

            fabs_trapezoidalValue = fabs(trapezoidalValue);
            if ((count >= 100 && fabs_add < fabs_trapezoidalValue * 0.000001) || (count >= 400 && fabs_add < fabs_trapezoidalValue * 0.0001)) break;

            prevadd = add;
            prev_fabs_add = fabs_add;
        }
        count += 1;
    }
    //computing the price
    double callPrice = S * exp(-div * tau) - (1.0 / (PI)) * K * exp(-r * tau) * trapezoidalValue;
    
    if (callPrice < 0.0 || callPrice > S) callPrice = BS_CallPrice(S, K, tau, sqrt(init_variance), r, div);

    if (optType == 0) price = callPrice;
    else price = callPrice + K * exp(-r * tau) - S * exp(-div * tau);
    return price;
}

double HestonPrice2(double S, double K, double r, double div,
    double init_variance, double tau,
    double LR_variance, double kappa, double volofvol, double rho)
{
    long i, j;
    double theta = LR_variance;
    double dx = 0.1;

    complex<double> b, eps, g, h, q, F1, F2, H, epsq;
    double X = log(S / K) + (r - div) * tau;
    complex<double> x, im;
    double value = 0.0, CallValue = 0.0, valuechange;
    x = complex<double>(0.0, 0.5);
    im = complex<double>(0.0, 1.0);
    for (i = 0; i < 2000; i++)
    {
        x = complex<double>((double)(i)*dx + 0.5 * dx, 0.5);
        b = 2.0 / (volofvol * volofvol) * (im * x * rho * volofvol + kappa);
        eps = sqrt(b * b + 4.0 * (x * x - im * x) / (volofvol * volofvol));
        g = (b - eps) / 2.0;
        h = (b - eps) / (b + eps);
        q = volofvol * tau * 0.5;
        if (real(eps * q) >= 500) epsq = complex<double>(500.0, imag(eps * q));
        else if (real(eps * q) <= -500) epsq = complex<double>(-500.0, imag(eps * q));
        else epsq = eps * q;
        F1 = 2.0 * kappa * theta / (volofvol * volofvol) * (q * g - log((1.0 - h * exp(-epsq)) / (1.0 - h)));
        F2 = g * (1.0 - exp(-epsq)) / (1.0 - h * exp(-epsq));
        H = exp(F1 + F2 * init_variance);
        valuechange = real(exp(-im * x * X) * H / (x * x - im * x)) * dx;
        value += valuechange;
        if (i > 250 && fabs(valuechange) < 0.000001 * fabs(value)) break;
    }
    double temp = (1.0 / (PI)) * K * exp(-r * tau) * value;
    CallValue = S * exp(-div * tau) - (1.0 / (PI)) * K * exp(-r * tau) * value;
    if (CallValue  < 0.0 || CallValue > S) CallValue = BS_CallPrice(S, K, tau, sqrt(init_variance), r, div);
    return CallValue;
}


double Heston_LocalVol(double S, double K, double r, double div,
    double init_variance, double tau,
    double LR_variance, double kappa, double volofvol, double rho,
    double gamma,
    long kmax, double* int_x, double* int_y, double CallOption)
{
    double dK;
    long optType = 0;
    if (K <= 2.0 && K > 0.0) dK = 0.01;
    else dK = K * 0.01;

    double Cup, Cdn, C;
    Cup = HestonPrice(S, K + dK, r, div, init_variance, tau, LR_variance, kappa, volofvol, rho, gamma, optType, kmax, int_x, int_y);
    Cdn = HestonPrice(S, K - dK, r, div, init_variance, tau, LR_variance, kappa, volofvol, rho, gamma, optType, kmax, int_x, int_y);
    C = HestonPrice(S, K, r, div, init_variance, tau, LR_variance, kappa, volofvol, rho, gamma, optType, kmax, int_x, int_y);
    
    double C_k =  (Cup - Cdn) / (2.0 * dK);
    double C_kk = (Cup + Cdn - 2.0 * C) / (dK * dK);
    
    double T_up = tau + 1.0 / 12.0;
    double T_dn = max(0.001, tau - 1.0 / 12.0);
    double dT = (T_up - T_dn) * 0.5;
    double Cup2, Cdn2;
    Cup2 = HestonPrice(S, K, r, div, init_variance, T_up, LR_variance, kappa, volofvol, rho, gamma, optType, kmax, int_x, int_y);
    Cdn2 = HestonPrice(S, K, r, div, init_variance, T_dn, LR_variance, kappa, volofvol, rho, gamma, optType, kmax, int_x, int_y);
    double C_T = (Cup2 - Cdn2) / (2.0 * dT);

    double LocalVar = (C_T) / (0.5 * K * K * C_kk);
    double LocalVol = 0.0;
    if (LocalVar > 0.0)
        LocalVol = sqrt(LocalVar);
    else
        LocalVol = -999999.99;
    return LocalVol;
}


double HestonPrice_Test(double S, double K, double r, double div, double* Params, double tau, double V0)
{
    double kappa = Params[0];
    double Vol_Of_Vol = Params[1];
    double LR_Vol = Params[2];
    double rho = Params[3];
    double gamma = 0.0;
    long optType = 0;
    return HestonPrice_Test(S, K, r, div, V0, tau, LR_Vol, kappa, Vol_Of_Vol, rho, gamma, optType);
}

double HestonPrice(double S, double K, double r, double div, double* Params, double tau, double V0, long kmax, double* int_x, double* int_y)
{
    double kappa = Params[0];
    double Vol_Of_Vol = Params[1];
    double LR_Var = Params[2];
    double rho = Params[3];
    double gamma = 0.0;
    long optType = 0;
    return HestonPrice(S, K, r, div, V0, tau, LR_Var, kappa, Vol_Of_Vol, rho, gamma, optType, kmax, int_x, int_y);
    //return HestonPrice2(S, K, r, div, V0, tau, LR_Var, kappa, Vol_Of_Vol, rho);
}

void make_Jacov_HESTON(
    long GradientDecentFlag,        // �հŸ��� Gradient Decent�� ����� �� ����
    long NParams,                   // Heston �Ķ���� ����
    double* Params,                 // Heston �Ķ���� Array
    long NResidual,                 // ���� ����
    double** TempJacovMatrix,       // �ӽ� ���ں�� ��Ʈ����
    double* ParamsUp,               // �Ķ���� ���� ���� �̺��� Array
    double* ParamsDn,               // �Ķ���� ���� ���� �̺��� Array
    double* TermVolNew,             // BS Call ����ϱ� ���� ���� ����
    double* ParityVolNew,           // BS Call ����ϱ� ���� ���� Moneyness
    double* r,                      // BS Call ����ϱ� ���� ���� ������
    double* div,                    // BS Call ����ϱ� ���� ���� �����ͷ�
    double* BSCallArray,            // BS Call ����
    long kmax,
    double* int_x,
    double* int_y
)
{
    long i;
    long j;
    long n;

    double param_max[5] = { 5.0, 2.0, 2.0, 0.95, 1.0 };
    double param_min[5] = { -0.3, 0.001, 0.00001 , -0.95, 0.00001 };
    double dparamsarray[5] = { 0.01, 0.001, 0.001, 0.02, 0.001 };                           // dP (kappa, vofv, meanvar, rho, v0)
    //if (GradientDecentFlag == 0) for (i = 0; i < 5; i++) dparamsarray[i] = dparamsarray[i] * 10.0;       // ù �������� 10�� �� dP�� �������

    double dparam_up;
    double Pup = 0.0;
    double Pdn = 0.0;
    double ErrorUp = 0.0;
    double ErrorDn = 0.0;
    double V0;

    for (i = 0; i < NResidual; i++)
    {
        for (j = 0; j < NParams; j++)
        {
            for (n = 0; n < NParams; n++)
            {
                if (n != j)
                {
                    ParamsUp[n] = Params[n];
                    ParamsDn[n] = Params[n];
                }
                else
                {
                    ParamsUp[n] = min(param_max[n], Params[n] + dparamsarray[n]);
                    ParamsDn[n] = max(param_min[n], Params[n] - dparamsarray[n]);
                    dparam_up = 0.5 * (ParamsUp[n] - ParamsDn[n]);
                }
            }

            V0 = ParamsUp[4];
            Pup = HestonPrice(1.0, ParityVolNew[i], r[i], div[i], ParamsUp, TermVolNew[i], V0, kmax, int_x, int_y);
            ErrorUp = BSCallArray[i] - Pup;

            V0 = ParamsDn[4];
            Pdn = HestonPrice(1.0, ParityVolNew[i], r[i], div[i], ParamsDn, TermVolNew[i], V0, kmax, int_x, int_y);
            ErrorDn = BSCallArray[i] - Pdn;
            TempJacovMatrix[i][j] = (ErrorUp - ErrorDn) / (2.0 * dparam_up);
        }
    }
}

void make_Residual_Heston(
    long NParams,
    double* Params,
    long NResidual,
    double* ResidualArray,
    double* TermVolNew,
    double* ParityVolNew,
    double* r,
    double* div,
    double* BSCallArray,
    double& ErrorSquareSum,
    double& PrecentError,
    double* HestonCallNew,
    long kmax,
    double* int_x,
    double* int_y,
    double& rmpse
)
{
    long i;
    double s = 0.0, s2 = 0.0;
    double V0;

    // Extreme ITM ���� RMSPE ���
    double meanprice = 0.0, r2 = 0.0, tss = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        V0 = Params[4];
        HestonCallNew[i] = HestonPrice(1.0, ParityVolNew[i], r[i], div[i], Params, TermVolNew[i], V0, kmax, int_x, int_y);
        meanprice += BSCallArray[i] / (double)NResidual;
    }

    rmpse = 0.0;
    tss = 0.0;
    s = 0.0;
    for (i = 0; i < NResidual; i++)
    {
        ResidualArray[i] = BSCallArray[i] - HestonCallNew[i];
        r2 = ResidualArray[i] * ResidualArray[i];
        s += (r2 * r2) ;
        tss += (BSCallArray[i] - meanprice) * (BSCallArray[i] - meanprice);
    }
    rmpse = s / tss;

    for (i = 0; i < NResidual; i++) s2 += fabs(ResidualArray[i] / HestonCallNew[i]);

    ErrorSquareSum = s;
    PrecentError = s2 / (double)NResidual;
}


void Levenberg_Marquardt_HESTON(
    long niter,                  // Iteration Number
    long NParams,                // in : Parameter ����
    long NResidual,              // in : Residual ����
    double* NextParams,          // out : ���� �Ķ���͸� ���� �� Array (���� = NParams)
    double* CurrentParams,       // in : ���� �Ķ���� (���� = NParams)
    double* lambda,              // in/out : mu �Ķ������ ������
    double** Jacov,              // in : ���ں�� ��Ʈ����
    double* Residual,            // in : �������
    double& ParamSum,            // in : �Ķ���� �������� ��
    double** JT_J,               // out : J'J Matrix
    double** Inverse_JT_J,       // out : (J'J)^-1
    double** JT_Res,             // out : (J'J) dot R
    double** ResultMatrix,       // out : �Ķ���� ������ ��Ʈ����
    long& GradientFlag,          // out : Gradient Decent�� ��� ����� �� ����
    double* Initial_Params,      // in : �Ķ���Ͱ� Range����� ��� �����Ķ���ͷ� �����ϱ� ���� ���
    double* argmin_params
)
{
    long i, j;
    long GradientContinue = 0;
    double mu = *lambda;

    double ParamMax[5] = { 5.0, 2.0,   2.0,     0.95 , 1.0 };
    double ParamMin[5] = { -0.3, 0.001, 0.00001,-0.95,  0.00001 };

    long n = NResidual;
    long m = NParams;

    long Shape_J[2] = { n,m };              // Shape of Jacov : (n, m)
    long Shape_JT[2] = { m,n };             // Shape of J' : (m, n)
    long Shape_Residual[2] = { n,1 };       // Shape of R : (n, 1)
    long Shape_Inv_JT_J[2] = { m,m };       // Shape of Inv(J'J) : (m, m)
    long Shape_JT_Res[2] = { m,1 };         // Shape of (J'R) : (m, 1)

    //////////////////////////////////
    // 1. Calc J'J : Shape = (m, m) //
    //////////////////////////////////
    XprimeDotX(Jacov, Shape_J, JT_J);
    round5(JT_J, m, m);

    ///////////////////////////////////////////////
    // 2. (J'J + mu * diag(J'J)): Shape = (m, m) //
    ///////////////////////////////////////////////
    for (i = 0; i < m; i++)
    {
        JT_J[i][i] = JT_J[i][i] + mu; //*JT_J[i][i]; // ������
    }

    ///////////////////////////////////
    // 3. Inv(J'J + mu * diag(J'J))  //
    ///////////////////////////////////
    MatrixInversion(JT_J, m, Inverse_JT_J);

    /////////////
    // 4. J'R  //
    /////////////
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    /////////////////////////////////////////////
    // 5. Inv(J'J + mu * diag(J'J)) dot (J'R)  //
    /////////////////////////////////////////////
    Dot2dArray(Inverse_JT_J, Shape_Inv_JT_J, JT_Res, Shape_JT_Res, ResultMatrix);

    for (i = 0; i < NParams; i++) NextParams[i] = CurrentParams[i] - ResultMatrix[i][0];

    for (i = 0; i < NParams; i++)
    {
        if (NextParams[i] > ParamMax[i] || NextParams[i] < ParamMin[i])
        {
            if (niter > 0) NextParams[i] = max(ParamMin[i], min(ParamMax[i], argmin_params[i]));
            else NextParams[i] = max(ParamMin[i], min(ParamMax[i], Initial_Params[i]));
            GradientContinue = 1;
        }
    }

    GradientFlag = GradientContinue;
    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(ResultMatrix[i][0]);
    ParamSum = s;
}

void GradientDecent_HESTON(
    long niter,                  // Iteration Number
    long NParams,                // in : Parameter ����
    long NResidual,              // in : Residual ����
    double* NextParams,          // out : ���� �Ķ���͸� ���� �� Array (���� = NParams)
    double* CurrentParams,       // in : ���� �Ķ���� (���� = NParams)
    double* lambda,              // in/out : mu �Ķ������ ������
    double** Jacov,              // in : ���ں�� ��Ʈ����
    double* Residual,            // in : �������
    double& ParamSum,            // in : �Ķ���� �������� ��
    double** JT_Res,             // out : (J'R)
    double* Initial_Params,      // in : �Ķ���Ͱ� Range����� ��� �����Ķ���ͷ� �����ϱ� ���� ���
    double* argmin_params
)
{
    long i, j;

    double mu = *lambda;

    double ParamMax[5] = { 5.0, 2.0,   2.0,     0.95 , 1.0 };
    double ParamMin[5] = { -0.3, 0.001, 0.00001,-0.95,  0.00001 };
    double maxchange[5] = { 0.2, 0.2, 0.05, 0.1, 0.05 };
    double minchange[5] = { -0.2, -0.2, -0.05, -0.1, -0.05 };

    long n = NResidual;
    long m = NParams;

    long Shape_J[2] = { n,m };              // Shape of Jacov : (n, m)
    long Shape_JT[2] = { m,n };             // Shape of J' : (m, n)
    long Shape_Residual[2] = { n,1 };       // Shape of R : (n, 1)

    /////////////
    // 4. J'R  //
    /////////////
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    for (i = 0; i < NParams; i++) NextParams[i] = CurrentParams[i] - max(minchange[i], min(maxchange[i], JT_Res[i][0] * 2.0 * mu));

    for (i = 0; i < NParams; i++)
    {
        if (NextParams[i] > ParamMax[i] || NextParams[i] < ParamMin[i])
        {
            if (niter > 0) NextParams[i] = max(ParamMin[i], min(ParamMax[i], argmin_params[i]));
            else NextParams[i] = max(ParamMin[i], min(ParamMax[i], Initial_Params[i]));
        }
    }

    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(JT_Res[i][0]);
    ParamSum = s;
}

void Gauss_Newton_HESTON(
    long NParams,                // in : Parameter ����
    long NResidual,              // in : Residual ����
    double* NextParams,          // out : ���� �Ķ���͸� ���� �� Array (���� = NParams)
    double* CurrentParams,       // in : ���� �Ķ���� (���� = NParams)
    double* lambda,              // in/out : mu �Ķ������ ������
    double** Jacov,              // in : ���ں�� ��Ʈ����
    double* Residual,            // in : �������
    double& ParamSum,            // in : �Ķ���� �������� ��
    double** JT_J,               // out : J'J Matrix
    double** Inverse_JT_J,       // out : (J'J)^-1
    double** JT_Res,             // out : (J'J) dot R
    double** ResultMatrix,       // out : �Ķ���� ������ ��Ʈ����
    long& GradientFlag,          // out : Gradient Decent�� ��� ����� �� ����
    double* Initial_Params       // in : �Ķ���Ͱ� Range����� ��� �����Ķ���ͷ� �����ϱ� ���� ���
)
{
    long i, j;
    long GradientContinue = 0;
    long debugflag = 0;
    double mu = *lambda;

    double ParamMax[5] = { 5.0, 2.0, 2.0, 0.95 , 1.0 };
    double ParamMin[5] = { -0.3, 0.001, 0.00001,-0.95,  0.00001 };

    long n = NResidual, m = NParams;
    long Shape_J[2] = { n,m };              // Shape of Jacov : (n, m)
    long Shape_JT[2] = { m,n };             // Shape of J' : (m, n)
    long Shape_Residual[2] = { n,1 };       // Shape of R : (n, 1)
    long Shape_Inv_JT_J[2] = { m,m };       // Shape of Inv(J'J) : (m, m)
    long Shape_JT_Res[2] = { m,1 };         // Shape of (J'R) : (m, 1)

    //////////////////////////////////
    // 1. Calc J'J : Shape = (m, m) //
    //////////////////////////////////
    XprimeDotX(Jacov, Shape_J, JT_J);
    round5(JT_J, m, m);

    //////////////////
    // 2. inv(J'J) ///
    //////////////////
    MatrixInversion(JT_J, m, Inverse_JT_J);

    /////////////
    // 3. J'R  //
    /////////////
    XprimeY(Jacov, Shape_J, Residual, n, JT_Res);

    /////////////////////////////
    // 4. Inv(J'J ) dot (J'R)  //
    /////////////////////////////
    Dot2dArray(Inverse_JT_J, Shape_Inv_JT_J, JT_Res, Shape_JT_Res, ResultMatrix);

    for (i = 0; i < NParams; i++) NextParams[i] = CurrentParams[i] - ResultMatrix[i][0];

    for (i = 0; i < NParams; i++)
    {
        if (NextParams[i] > ParamMax[i] || NextParams[i] < ParamMin[i])
        {
            NextParams[i] = max(ParamMin[i], min(ParamMax[i], Initial_Params[i]));
            GradientContinue = 1;
        }
    }

    GradientFlag = GradientContinue;
    double s = 0.0;
    for (i = 0; i < NParams; i++) s += fabs(ResultMatrix[i][0]);
    ParamSum = s;
}

void HestonNextLambda(double ErrorSquareSum, double PrevErrorSquareSum, double* lambda, long& BreakFlag, long GradientFlag)
{
    double LambdaMax = 1000000;
    double LambdaMin = 0.000001;
    if (GradientFlag == 0)
    {
        if (ErrorSquareSum < PrevErrorSquareSum)
        {
            // ������ �����ϸ� ���콺���Ͽ� ������
            *lambda *= 0.1;
        }
        else if (ErrorSquareSum < PrevErrorSquareSum * 1.05)
        {

        }
        else *lambda = min(1.0, *lambda * 10.0);
        if (*lambda > LambdaMax) *lambda = LambdaMax;
        if (*lambda < LambdaMin) BreakFlag = 1;
    }
    else
    {
        *lambda = 0.01;
    }
}

double CalcImvol(
    double S,
    double K,
    double T,
    double r,
    double div,
    double kappa,
    double volofvol,
    double LR_variance,
    double rho,
    double kmax,
    double* int_x,
    double* int_y,
    double CallPrice
)
{
    long i;
    double init_variance;
    double Maxvol = 1.0;
    double Minvol = 0.01;
    double Targetvol = Maxvol;
    double dblErrorRange = CallPrice * 0.000001;
    double dblPriceGap;
    double BS_C = 0.0;

    for (i = 0; i < 100; i++)
    {
        init_variance = Targetvol * Targetvol;
        BS_C = HestonPrice(S, K, r, div, init_variance, T, LR_variance, kappa, volofvol, rho, 0.0, 0, kmax, int_x, int_y);

        dblPriceGap = BS_C - CallPrice;
        if (fabs(dblPriceGap) < dblErrorRange)
            break;
        if (dblPriceGap > 0.0)
        {
            Maxvol = Targetvol;
            Targetvol = (Maxvol + Minvol) / 2.0;
        }
        else
        {
            Minvol = Targetvol;
            Targetvol = (Minvol + Maxvol) / 2.0;
        }
    }
    return Targetvol;
}

void Levenberg_Marquardt_HESTON(
    long NParams,               // Heston �Ķ���� ���� = 5
    double* Params,             // �Ķ���� Array = [kappa, volofvol, MeanVaR, rho, V0
    long NResidual,             // Residual ���� = VolSurface�� Parity���� * Term����
    double* ResidualArray,      // ���� Array
    double** TempJacovMatrix,   // Jacovian Matrix�� ���� �Ҵ��س��� Matrix
    double* ParamsUp,           // �Ķ���� ���� ���� �̺��� Array
    double* ParamsDn,           // �Ķ���� ���� ���� �̺��� Array
    double* r,                  // BS Call ����ϱ� ���� ���� ������
    double* div,                // BS Call ����ϱ� ���� ���� �����ͷ�
    double* TermVolNew,         // BS Call ����ϱ� ���� ���� ����
    double* ParityVolNew,       // BS Call ����ϱ� ���� ���� Moneyness
    double* BSCallArray,        // BS Call ����
    double* HestonCallNew,      // Output : Heston Call
    double& RMPSE
)
{
    long i;
    long n;
    long BreakFlag = 0;
    long Levenberg = 1;

    double ErrorSquareSum = 100000.0;
    double PrecentError = 1.0;
    double PrevErrorSquareSum = 0.0;
    double ParamSum = 0.0;
    double lambda[1] = { 1.00 };
    double lambdafirst[1] = { 0.01 };
    double* NextParams = make_array(NParams);
    double** JT_J = make_array(NParams, NParams);
    double** Inverse_JT_J = make_array(NParams, NParams);
    double** JT_Res = make_array(NParams, 1);
    double** ResultMatrix = make_array(NParams, 1);
    double* Initial_Params = (double*)malloc(sizeof(double) * NParams);
    double minerror = 10000.0;
    for (i = 0; i < NParams; i++) Initial_Params[i] = Params[i];
    double FirstErrorSquare = 1.0;
    double* argminparam = (double*)malloc(sizeof(double) * NParams);
    double* argminhestoncall = (double*)malloc(sizeof(double) * NResidual);
    double minrmpse = 1.0;
    /////////////////////////////////
    // Heston Price�� ����� Array //
    /////////////////////////////////
    const long kmax = 1000;
    double integ_x[kmax * 5] = { 0.0, };
    double integ_y[kmax * 5] = { 0.0, };

    long GradientFlag = 1;
    long GaussNewtonFlag = 0;

    for (n = 0; n < 30; n++)
    {
        //////////////////////////
        // Jacovian Matrix ���� //
        //////////////////////////
        make_Jacov_HESTON(n, NParams, Params, NResidual, TempJacovMatrix, ParamsUp, ParamsDn, TermVolNew, ParityVolNew, r, div, BSCallArray, kmax, integ_x, integ_y);

        //////////////////////////
        // Residual Matrix ���� //
        //////////////////////////
        make_Residual_Heston(NParams, Params, NResidual, ResidualArray, TermVolNew, ParityVolNew, r, div, BSCallArray, ErrorSquareSum, PrecentError, HestonCallNew, kmax, integ_x, integ_y, RMPSE);

        if (n == 0) FirstErrorSquare = ErrorSquareSum + 0.0;

        if (n >= 1)
        {
            HestonNextLambda(ErrorSquareSum, PrevErrorSquareSum, lambda, BreakFlag, GradientFlag);
            if (ErrorSquareSum < minerror)
            {
                minerror = ErrorSquareSum;
                minrmpse = RMPSE;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                for (i = 0; i < NResidual; i++) argminhestoncall[i] = HestonCallNew[i];
            }
        }
        if (BreakFlag == 1 && GradientFlag == 0 && lambda[0] < 1.0e-06) break;
        
        if (n == 0)
        {
            GradientDecent_HESTON(n, NParams, NResidual, NextParams, Params, lambdafirst, TempJacovMatrix, ResidualArray, ParamSum, JT_Res, Initial_Params, argminparam);
        }
        else if (lambda[0] >= 1.0e-06 || GradientFlag == 1)
        {
            Levenberg_Marquardt_HESTON(n, NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, GradientFlag, Initial_Params, argminparam);
        }
        else
        {
            ////////////////////////////////////////////
            // lambda�� �������� Gauss Newton�� ��� ///
            ////////////////////////////////////////////
            Gauss_Newton_HESTON(NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_J, Inverse_JT_J, JT_Res, ResultMatrix, GradientFlag, Initial_Params);
        }

        for (i = 0; i < NParams; i++) Params[i] = NextParams[i];

        if (n >= 10 && GradientFlag == 0 && lambda[0] < 1.0e-06) break;
        if (ErrorSquareSum / FirstErrorSquare < 0.001) break;
        if (n >= 7 && minrmpse < 0.05) break;
        PrevErrorSquareSum = ErrorSquareSum;
    }
    RMPSE = minrmpse;
    for (i = 0; i < NResidual; i++) HestonCallNew[i] = argminhestoncall[i];
    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];

    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    for (i = 0; i < NParams; i++) free(Inverse_JT_J[i]);
    free(JT_J);
    free(Inverse_JT_J);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(ResultMatrix[i]);
    free(ResultMatrix);
    free(Initial_Params);
    free(argminparam);
    free(argminhestoncall);
}

void GradientDecent_HESTON(
    long NParams,               // Heston �Ķ���� ���� = 5
    double* Params,             // �Ķ���� Array = [kappa, volofvol, MeanVaR, rho, V0
    long NResidual,             // Residual ���� = VolSurface�� Parity���� * Term����
    double* ResidualArray,      // ���� Array
    double** TempJacovMatrix,   // Jacovian Matrix�� ���� �Ҵ��س��� Matrix
    double* ParamsUp,           // �Ķ���� ���� ���� �̺��� Array
    double* ParamsDn,           // �Ķ���� ���� ���� �̺��� Array
    double* r,                  // BS Call ����ϱ� ���� ���� ������
    double* div,                // BS Call ����ϱ� ���� ���� �����ͷ�
    double* TermVolNew,         // BS Call ����ϱ� ���� ���� ����
    double* ParityVolNew,       // BS Call ����ϱ� ���� ���� Moneyness
    double* BSCallArray,        // BS Call ����
    double* HestonCallNew,      // Output : Heston Call
    double& RMPSE
)
{
    long i,j;
    long n;
    long BreakFlag = 0;
    long Levenberg = 1;

    double ErrorSquareSum = 100000.0;
    double PrecentError = 1.0;
    double PrevErrorSquareSum = 0.0;
    double ParamSum = 0.0;
    double lambda[1] = { 0.1    };
    double* NextParams = make_array(NParams);
    double** JT_J = make_array(NParams, NParams);
    double** Inverse_JT_J = make_array(NParams, NParams);
    double** JT_Res = make_array(NParams, 1);
    double** ResultMatrix = make_array(NParams, 1);
    double* Initial_Params = (double*)malloc(sizeof(double) * NParams);
    double minerror = 10000.0;
    for (i = 0; i < NParams; i++) Initial_Params[i] = Params[i];
    double FirstErrorSquare = 1.0;
    double* argminparam = (double*)malloc(sizeof(double) * NParams);
    double* argminhestoncall = (double*)malloc(sizeof(double) * NResidual);
    double minrmpse = 1.0;

    double** PrevJacov = make_array(NResidual, NParams);
    double* PrevResidual = make_array(NResidual);
    double* prevparam = (double*)malloc(sizeof(double) * (NParams));

    /////////////////////////////////
    // Heston Price�� ����� Array //
    /////////////////////////////////
    const long kmax = 1000;
    double integ_x[kmax * 5] = { 0.0, };
    double integ_y[kmax * 5] = { 0.0, };

    for (n = 0; n < 30; n++)
    {
        //////////////////////////
        // Jacovian Matrix ���� //
        //////////////////////////
        make_Jacov_HESTON(n, NParams, Params, NResidual, TempJacovMatrix, ParamsUp, ParamsDn, TermVolNew, ParityVolNew, r, div, BSCallArray, kmax, integ_x, integ_y);

        //////////////////////////
        // Residual Matrix ���� //
        //////////////////////////
        make_Residual_Heston(NParams, Params, NResidual, ResidualArray, TermVolNew, ParityVolNew, r, div, BSCallArray, ErrorSquareSum, PrecentError, HestonCallNew, kmax, integ_x, integ_y, RMPSE);

        if (n == 0) FirstErrorSquare = ErrorSquareSum + 0.0;

        if (n >= 1)
        {
            if (ErrorSquareSum < minerror || n == 1)
            {
                minerror = ErrorSquareSum;
                minrmpse = RMPSE;
                for (i = 0; i < NParams; i++) argminparam[i] = Params[i];
                for (i = 0; i < NResidual; i++) argminhestoncall[i] = HestonCallNew[i];
                if (RMPSE < 0.01) break;
            }
            if (ErrorSquareSum < PrevErrorSquareSum) lambda[0] *= 0.8;
            else
            {
                for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) TempJacovMatrix[i][j] = PrevJacov[i][j];
                for (i = 0; i < NResidual; i++) ResidualArray[i] = PrevResidual[i];
                for (i = 0; i < NParams; i++) Params[i] = prevparam[i];
                lambda[0] *= 0.8;
            }

        }

        for (i = 0; i < NResidual; i++) for (j = 0; j < NParams; j++) PrevJacov[i][j] = TempJacovMatrix[i][j];
        for (i = 0; i < NResidual; i++) PrevResidual[i] = ResidualArray[i];

        GradientDecent_HESTON(n, NParams, NResidual, NextParams, Params, lambda, TempJacovMatrix, ResidualArray, ParamSum, JT_Res, Initial_Params, argminparam);
        for (i = 0; i < NParams; i++)
        {
            prevparam[i] = Params[i];
            Params[i] = NextParams[i];
        }

        if (n >= 10 && lambda[0] < 1.0e-06) break;
        if (ErrorSquareSum / FirstErrorSquare < 0.001) break;
        if (n >= 5 && minrmpse < 0.01) break;
        PrevErrorSquareSum = ErrorSquareSum;
    }
    RMPSE = minrmpse;
    for (i = 0; i < NResidual; i++) HestonCallNew[i] = argminhestoncall[i];
    for (i = 0; i < NParams; i++) Params[i] = argminparam[i];

    free(NextParams);
    for (i = 0; i < NParams; i++) free(JT_J[i]);
    for (i = 0; i < NParams; i++) free(Inverse_JT_J[i]);
    free(JT_J);
    free(Inverse_JT_J);
    for (i = 0; i < NParams; i++) free(JT_Res[i]);
    free(JT_Res);
    for (i = 0; i < NParams; i++) free(ResultMatrix[i]);
    free(ResultMatrix);
    free(Initial_Params);
    free(argminparam);
    free(argminhestoncall);

    free(prevparam);
    for (i = 0; i < NResidual; i++) free(PrevJacov[i]);
    free(PrevJacov);
    free(PrevResidual);
}

void HestonCalibration(
    long NTermVol,          // Vol Term ����
    double* TermVol,        // Vol Term �Ⱓ Array
    long NParityVol,        // Vol Parity ����
    double* ParityVol,      // Vol Parity Array,
    double* Vol,            // Vol Surface.Reshape(0)
    double* Params,         // Input/Output: Heston Parameter �ʱⰪ �� ����� [kappa, volofvol, mean variance, rho, initial variance]
    long NTerm,             // Interest Rate �Ⱓ���� ����
    double* TermRate,       // Interest Rate �Ⱓ���� ���� Array
    double* Rate,           // Interest Rate �Ⱓ���� Rate Array,
    long NDiv,              // Dividend �Ⱓ���� ����
    double* DivTerm,        // Dividend �Ⱓ���� ���� Array,
    double* DivRate,        // Dividend �Ⱓ���� �����ͷ� Array 
    double* ResultImVol,    // Output: Calibration ����� ���� Array
    double* HestonPrice,
    double& rmspe
)
{
    long i;
    long j;

    const long nparams = 5;
    long NResidual = NTermVol * NParityVol;

    double* TermVolNew = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    for (i = 0; i < NTermVol * NParityVol; i++) TermVolNew[i] = TermVol[i % NTermVol];
    double* ParityVolNew = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    for (i = 0; i < NTermVol * NParityVol; i++) ParityVolNew[i] = ParityVol[i / NTermVol];
    double* VolNew = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    for (i = 0; i < NTermVol * NParityVol; i++) VolNew[i] = Vol[i];

    double* BSCallArray = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    double* r = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    double* div = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    for (i = 0; i < NTermVol * NParityVol; i++) r[i] = Interpolate_Linear(TermRate, Rate, NTerm, TermVolNew[i]);
    for (i = 0; i < NTermVol * NParityVol; i++) div[i] = Interpolate_Linear(DivTerm, DivRate, NDiv, TermVolNew[i]);

    for (i = 0; i < NTermVol * NParityVol; i++) BSCallArray[i] = BS_CallPrice(1.0, ParityVolNew[i], TermVolNew[i], Vol[i], r[i], div[i]);
    double* HestonCallNew = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    for (i = 0; i < NTermVol * NParityVol; i++) HestonCallNew[i] = Vol[i];

    double* ResidualArray = (double*)malloc(sizeof(double) * NResidual);
    double** TempJacov = (double**)malloc(sizeof(double*) * NResidual);
    for (i = 0; i < NResidual; i++) TempJacov[i] = (double*)malloc(sizeof(double) * nparams);

    double TargetParams[nparams] = { 0.0, };
    double ParamsUp[nparams] = { 0.0, };
    double ParamsDn[nparams] = { 0.0, };
    for (i = 0; i < nparams; i++)
    {
        TargetParams[i] = Params[i];
        ParamsUp[i] = Params[i];
        ParamsDn[i] = Params[i];
    }
    double* ResultHestonCall = (double*)malloc(sizeof(double) * NTermVol * NParityVol);
    rmspe = 1.0;
    Levenberg_Marquardt_HESTON(nparams, Params, NResidual, ResidualArray, TempJacov, ParamsUp, ParamsDn, r, div, TermVolNew, ParityVolNew, BSCallArray, HestonCallNew, rmspe);
    //GradientDecent_HESTON(nparams, Params, NResidual, ResidualArray, TempJacov, ParamsUp, ParamsDn, r, div, TermVolNew, ParityVolNew, BSCallArray, HestonCallNew, rmspe);

    for (i = 0; i < NTermVol * NParityVol; i++)
    {
        ResultHestonCall[i] = HestonCallNew[i];
        HestonPrice[i] = HestonCallNew[i];
    }

    const long kmax = 1000;
    double integ_x[kmax * 5] = { 0.0, };
    double integ_y[kmax * 5] = { 0.0, };
    //for (i = 0; i < NTermVol * NParityVol; i++)
    //{
    //    VolNew[i] = Heston_LocalVol(1.0, ParityVolNew[i], r[i], div[i], Params[4],
    //        TermVolNew[i], Params[2], Params[0], Params[1], Params[3], 0.0, kmax, integ_x, integ_y, HestonCallNew[i]);
    //}

    free(ResultHestonCall);
    free(TermVolNew);
    free(ParityVolNew);
    free(ResidualArray);
    for (i = 0; i < NResidual; i++) free(TempJacov[i]);
    free(TempJacov);
    free(HestonCallNew);
    free(VolNew);
    free(r);
    free(div);
    free(BSCallArray);
}
/*
int main()
{
    long i, j, k;
    long ResultCode = 0;

    const long NParity = 9;
    const long NTermVol = 10;
    double ParityVol[NParity] = { 0.50,0.60,0.70,0.80,0.90,1.00,1.10,1.20,1.30 };
    double TermVol[NTermVol] = { 0.33 ,    0.67     ,1.00     ,1.33 ,    1.67 ,    2.00     ,2.33,     2.67,     3.00 ,    3.33 };
    double VolReshaped[NParity * NTermVol] = { 39.95 , 35.43 , 34.10 , 31.21 , 29.20 , 27.84 , 27.86 , 26.85 , 24.77 , 24.33 ,
                                                35.87 , 30.50 , 29.51 , 26.93 , 25.14 , 23.85 , 23.06 , 22.37 , 21.53 , 22.25 ,
                                                29.75 , 25.55 , 25.75 , 23.00 , 21.76 , 20.73 , 20.20 , 19.83 , 19.36 , 19.22 ,
                                                23.13 , 20.80 , 20.82 , 19.79 , 19.07 , 18.40 , 18.20 , 18.07 , 17.83 , 17.83 ,
                                                18.58 , 17.76 , 17.08 , 16.97 , 16.89 , 16.62 , 16.71 , 16.80 , 16.74 , 16.89 ,
                                                13.40 , 14.10 , 14.57 , 14.75 , 15.11 , 15.18 , 15.54 , 15.82 , 15.92 , 16.16 ,
                                                10.33 , 11.41 , 12.81 , 13.35 , 13.89 , 14.17 , 14.68 , 15.11 , 15.39 , 15.67 ,
                                                10.98 , 10.83 , 12.14 , 12.61 , 13.13 , 13.70 , 14.29 , 14.80 , 15.21 , 15.51 ,
                                                11.48 , 11.39 , 11.79 , 12.48 , 13.10 , 13.55 , 14.18 , 14.78 , 15.26 , 15.60 };
    for (i = 0; i < NParity * NTermVol; i++) if (VolReshaped[i] > 2.0) VolReshaped[i] /= 100.0;
    double HestonPrice[NParity * NTermVol] ={ 0.0, };
    double ResultImvol[NParity * NTermVol] = { 0.0, };
    const long NTerm = 3;
    double TermRate[NTerm] = { 1.0, 2.0, 3.0 };
    double Rate[NTerm] = { 0.01, 0.02, 0.03 };

    const long NDiv = 3;
    double DivTerm[NDiv] = { 1.0, 2.0, 3.0 };
    double DivRate[NDiv] = { 0.02, 0.02, 0.02 };


    double kappa, volofvol, meanvar, rho, V0;
    kappa = 0.5;        // 0    .3
    volofvol = 0.22;   // 0.265
    meanvar = 0.02;     // 0.05
    rho = 0.0;        // -0.01
    V0 = 0.02;          //0.02
    double rmspe = 1.0;
    double params[5] = { kappa, volofvol, meanvar, rho  , V0 };
    HestonCalibration(NTermVol, TermVol, NParity, ParityVol, VolReshaped, params, NTerm, TermRate, Rate, NDiv, DivTerm, DivRate, ResultImvol, HestonPrice, rmspe);


    _CrtDumpMemoryLeaks();
}
*/

DLLEXPORT(long) HestonCalibrate(
    long NZero,
    double* ZeroTerm,
    double* ZeroRate,
    long NDiv,
    double* DivTerm,
    double* DivRate,

    long NParity,
    double* ParityVol,
    long NTermVol,
    double* TermVol,
    double* VolReshaped,

    double kappa_init,
    double volofvol_init,
    double meanvar_init,
    double rho_init,
    double Variance0_init,

    double* Params,
    double* HestonCallPrice,
    double* HestonBSImvol,
    double* ResultLocalVol
    )
{
    long i;
    for (i = 0; i < NParity * NTermVol; i++) if (VolReshaped[i] > 2.0) VolReshaped[i] /= 100.0;
    double rmspe = 1.0;
    double params_array[5] = { kappa_init, volofvol_init, meanvar_init, rho_init  , Variance0_init };

    HestonCalibration(NTermVol, TermVol, NParity, ParityVol, VolReshaped, params_array, NTermVol, ZeroTerm, ZeroRate, NDiv, DivTerm, DivRate, HestonBSImvol, HestonCallPrice, rmspe);
    for (i = 0; i < 5; i++) Params[i] = params_array[i];
    Params[5] = rmspe;

    return 1;
}