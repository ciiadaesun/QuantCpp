# -*- coding: utf-8 -*-
"""
Created By Daesun Lim
Risk Quant Manager
My FRTB Module v1.0.1 
"""

import numpy as np
import pandas as pd
from numba import jit
import warnings
warnings.filterwarnings('ignore')

GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
GIRR_VegaRiskFactor1 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_VegaRiskFactor2 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_DeltaRfCorr = np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                             [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                             [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                             [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                             [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                             [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                             [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                             [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                             [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                             [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])
CSR_RiskFactorRate = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
CSR_DeltaNonSecuritizedBucketCorr = np.array([[1.000,0.750,0.100,0.200,0.250,0.200,0.150,0.100,0.000,0.450,0.450],
                                        [0.750,1.000,0.050,0.150,0.200,0.150,0.100,0.100,0.000,0.450,0.450 ],
                                        [0.100,0.050,1.000,0.050,0.150,0.200,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.050,1.000,0.200,0.250,0.050,0.050,0.000,0.450,0.450 ],
                                        [0.250,0.200,0.150,0.200,1.000,0.250,0.050,0.150,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.200,0.250,0.250,1.000,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.150,0.100,0.050,0.050,0.050,0.050,1.000,0.050,0.000,0.450,0.450 ],
                                        [0.100,0.100,0.200,0.050,0.150,0.200,0.050,1.000,0.000,0.450,0.450 ],
                                        [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,1.000,0.000,0.000 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,1.000,0.750 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,0.750,1.000 ]])
CSR_DeltaNonSecurCorrDf = pd.DataFrame(CSR_DeltaNonSecuritizedBucketCorr, 
                                       index = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]), 
                                       columns = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]))
CSR_SecuritizedNonCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
CSR_SecuritizedNonCTPDelta_RW = pd.Series([0.009,0.015,0.02,0.02,0.008,0.012,0.012,0.014,
                                           0.01125,0.01875,0.025,0.025,0.01,0.015,0.015,0.0175,
                                           0.01575,0.02625,0.035,0.035,0.014,0.021,0.021,0.0245,0.035 ], 
                                              [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25])
CSR_CTP_RW = pd.Series([0.040,0.040,0.080,0.050,0.040,0.030,0.020,0.060,0.130,0.130,
                            0.160,0.100,0.120,0.120,0.120,0.130 ],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
CSR_SecuritizedCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
EQ_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
FX_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
HighLiquidCurrency = ["USD","EUR","JPY","GBP","AUD",
                      "CAD","CHF","MXN","CNY","NZD",
                      "RUB","HKD","SGD","TRY","KRW",
                      "SEK","ZAR","INR","NOK","BRL"]
COMM_DeltaRiskFactor = pd.Series([0, 0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
COMM_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
EQBucketIndex = [1,2,3,4,5,6,7,8,9,10,11,12,13]
EQSpotRW = [0.5500 ,0.6000 ,0.4500 ,0.5500 ,0.3000 ,0.3500 ,0.4000 ,0.5000 ,0.7000 ,0.5000 ,0.7000 ,0.1500 ,0.2500 ]
EQRepoRW = [0.0055 ,0.0060 ,0.0045 ,0.0055 ,0.0030 ,0.0035 ,0.0040 ,0.0050 ,0.0070 ,0.0050 ,0.0070 ,0.0015 ,0.0025]
EQDeltaRWMappingDF = pd.DataFrame([EQSpotRW,EQRepoRW], columns = EQBucketIndex, index = ["SpotRW","RepoRW"]).T
COMM_Delta_RWMapping = pd.Series([0.3,0.35,0.6,0.8,0.4,0.45,0.2,0.35,0.25,0.35,0.5],index = np.arange(1,12))

GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
GIRR_VegaRiskFactor1 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_VegaRiskFactor2 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_DeltaRfCorr = np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                             [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                             [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                             [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                             [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                             [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                             [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                             [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                             [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                             [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])
CSR_RiskFactorRate = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
CSR_DeltaNonSecuritizedBucketCorr = np.array([[1.000,0.750,0.100,0.200,0.250,0.200,0.150,0.100,0.000,0.450,0.450],
                                        [0.750,1.000,0.050,0.150,0.200,0.150,0.100,0.100,0.000,0.450,0.450 ],
                                        [0.100,0.050,1.000,0.050,0.150,0.200,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.050,1.000,0.200,0.250,0.050,0.050,0.000,0.450,0.450 ],
                                        [0.250,0.200,0.150,0.200,1.000,0.250,0.050,0.150,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.200,0.250,0.250,1.000,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.150,0.100,0.050,0.050,0.050,0.050,1.000,0.050,0.000,0.450,0.450 ],
                                        [0.100,0.100,0.200,0.050,0.150,0.200,0.050,1.000,0.000,0.450,0.450 ],
                                        [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,1.000,0.000,0.000 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,1.000,0.750 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,0.750,1.000 ]])
CSR_DeltaNonSecurCorrDf = pd.DataFrame(CSR_DeltaNonSecuritizedBucketCorr, 
                                       index = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]), 
                                       columns = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]))
CSR_SecuritizedNonCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
CSR_SecuritizedNonCTPDelta_RW = pd.Series([0.009,0.015,0.02,0.02,0.008,0.012,0.012,0.014,
                                           0.01125,0.01875,0.025,0.025,0.01,0.015,0.015,0.0175,
                                           0.01575,0.02625,0.035,0.035,0.014,0.021,0.021,0.0245,0.035 ], 
                                              [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25])
CSR_CTP_RW = pd.Series([0.040,0.040,0.080,0.050,0.040,0.030,0.020,0.060,0.130,0.130,
                            0.160,0.100,0.120,0.120,0.120,0.130 ],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
CSR_SecuritizedCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
EQ_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
FX_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
HighLiquidCurrency = ["USD","EUR","JPY","GBP","AUD",
                      "CAD","CHF","MXN","CNY","NZD",
                      "RUB","HKD","SGD","TRY","KRW",
                      "SEK","ZAR","INR","NOK","BRL"]
COMM_DeltaRiskFactor = pd.Series([0, 0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
COMM_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
EQBucketIndex = [1,2,3,4,5,6,7,8,9,10,11,12,13]
EQSpotRW = [0.5500 ,0.6000 ,0.4500 ,0.5500 ,0.3000 ,0.3500 ,0.4000 ,0.5000 ,0.7000 ,0.5000 ,0.7000 ,0.1500 ,0.2500 ]
EQRepoRW = [0.0055 ,0.0060 ,0.0045 ,0.0055 ,0.0030 ,0.0035 ,0.0040 ,0.0050 ,0.0070 ,0.0050 ,0.0070 ,0.0015 ,0.0025]
EQDeltaRWMappingDF = pd.DataFrame([EQSpotRW,EQRepoRW], columns = EQBucketIndex, index = ["SpotRW","RepoRW"]).T
COMM_Delta_RWMapping = pd.Series([0.3,0.35,0.6,0.8,0.4,0.45,0.2,0.35,0.25,0.35,0.5],index = np.arange(1,12))

def ReadCSV(filedir) :
    try : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python')
    except UnicodeDecodeError : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'cp949')
    
    df = pd.DataFrame()
    for i in chunk_list : 
        df = pd.concat([df,i],axis = 0)
    return df

def PreProcessingKDBData(KDBData) : 
    Data = KDBData.rename(columns = {"부점명":"Depart","포트폴리오":"Portfolio","리스크군":"Risk_Class",
                                     "버킷":"Bucket","리스크요소1":"RiskFactor1","리스크요소2":"RiskFactor2",
                                     "리스크요소3":"RiskFactor3","델타민감도":"Delta_Sensi","베가민감도":"Vega_Sensi",
                                     "상향커버쳐":"CVR_Plus","하향커버쳐":"CVR_Minus","뮤렉스ID":"MurexID",
                                     "민감도유형":"Risk_Type"})
    DataCSR = Data[Data["Risk_Class"].isin(["CSR","신용스프레드","신용스프레드(CSR)"])]
    DataGIRR = Data[Data["Risk_Class"].isin(["GIRR","일반금리","일반금리(GIRR)"])]
    DataFXR = Data[Data["Risk_Class"].isin(["FXR","외환","외환(FXR)","외환리스크","외환리스크(FXR)"])]
    DataEQR = Data[Data["Risk_Class"].isin(["EQR","주식","주식(EQR)","주식리스크","주식리스크(EQR)"])]
    DataCOMR = Data[Data["Risk_Class"].isin(["COMR","일반상품","일반상품리스크","일반상품(COMR)","일반상품리스크(EQR)"])]
    if len(DataCSR) > 0 :
        DataCSR["Bucket"] = DataCSR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataCSR = DataCSR.rename(columns = {"RiskFactor2":"Curve","RiskFactor3":"Tenor","RiskFactor1":"Issuer"})
        DataCSRDelta = DataCSR[DataCSR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataCSRNonDelta = DataCSR.loc[DataCSR.index.difference(DataCSRDelta.index)]
        DataCSRDelta["Delta_Sensi"] = DataCSRDelta["Delta_Sensi"].astype(np.float64) * 10000
        DataCSR = pd.concat([DataCSRDelta, DataCSRNonDelta],axis = 1)
    if len(DataGIRR) > 0 : 
        DataGIRRVega = DataGIRR[DataGIRR["Risk_Type"].isin(["베가","Vega","베가(Vega)"])]
        DataGIRR_NonVega = DataGIRR.loc[DataGIRR.index.difference(DataGIRRVega.index)]
        DataGIRR_NonVega = DataGIRR_NonVega.rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
        DataGIRRVega = DataGIRRVega.rename(columns = {"RiskFactor3":"Curve","RiskFactor1":"Tenor1","RiskFactor2":"Tenor2"})        
        DataGIRR = pd.concat([DataGIRRVega, DataGIRR_NonVega],axis = 0)        
        DataGIRR["Delta_Sensi"] = DataGIRR["Delta_Sensi"].astype(np.float64) * 10000                
    if len(DataEQR) > 0 : 
        DataEQR["Bucket"] = DataEQR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataEQRDelta = DataEQR[DataEQR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataEQRVega = DataEQR[DataEQR["Risk_Type"].isin(["베가","Vega","베가(Vega)"])]
        DataEQRCurvature = DataEQR[DataEQR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        DataEQRDelta = DataEQRDelta.rename(columns = {"RiskFactor2":"StockName","RiskFactor1":"Type","RiskFactor3":"TempRiskFactor"})
        DataEQRCurvature = DataEQRCurvature.rename(columns = {"RiskFactor1":"StockName","RiskFactor2":"Type","RiskFactor3":"TempRiskFactor"})        
        DataEQRVega = DataEQRVega.rename(columns = {"RiskFactor2":"StockName","RiskFactor1":"Tenor","RiskFactor3":"TempRiskFactor"})
        DataEQR = pd.concat([DataEQRDelta,DataEQRCurvature, DataEQRVega],axis=0)
        DataEQR["Delta_Sensi"] = DataEQR["Delta_Sensi"].astype(np.float64) * 100                
    if len(DataFXR) > 0 : 
        DataFXR["Curve"] = DataFXR["RiskFactor1"]
        DataFXR["Tenor"] = DataFXR["RiskFactor1"]
        FXRDelta = DataFXR[DataFXR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        FXRDelta["Bucket"] = FXRDelta["Curve"]
        FXRCurvature = DataFXR[DataFXR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        FXRCurvature["Bucket"] = FXRCurvature["Curve"]
        FXRVega = DataFXR[DataFXR["Risk_Type"].isin(["Vega","베가","베가(Vega)"])]
        FXRVega["Bucket"] = FXRVega["Bucket"].fillna('nan')
        DataFXR = pd.concat([FXRDelta, FXRCurvature, FXRVega],axis = 0)
    if len(DataCOMR) > 0 :        
        DataCOMR["Bucket"] = DataCOMR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataCOMRDelta = DataCOMR[DataCOMR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataCOMRCurvature = DataCOMR[DataCOMR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        DataCOMRVega = DataCOMR[DataCOMR["Risk_Type"].isin(["Vega","베가","베가(Vega)"])]
        DataCOMRDelta = DataCOMRDelta.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
        DataCOMRCurvature = DataCOMRCurvature.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Delivery","RiskFactor3":"TempRiskFactor3"})
        DataCOMRVega = DataCOMRVega.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
        
        DataCOMR = pd.concat([DataCOMRDelta, DataCOMRCurvature, DataCOMRVega],axis = 0)
    return pd.concat([DataCSR,DataGIRR,DataFXR,DataEQR,DataCOMR],axis = 0)

def PreProcessingMyData(RAWData) : 
    CSR = RAWData[RAWData["Risk_Class"].isin(["CSR","csr","신용스프레드","신용스프레드(CSR)"]) ]
    CSR_Delta = CSR[CSR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_Curvature = CSR[CSR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_Vega = CSR[CSR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    Result_CSR = pd.concat([CSR_Delta, CSR_Curvature, CSR_Vega],axis = 0)
    
    CSR_SecuritizedNonCTP = RAWData[RAWData["Risk_Class"].isin(["CSR Securitized Non CTP","유동화(CTP 제외)", "CSR 유동화(CTP 제외)", "신용스프레드 유동화(CTP 제외)"]) ]
    CSR_SecuritizedNonCTPDelta = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    CSR_SecuritizedNonCTPCurvature = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    CSR_SecuritizedNonCTPVega = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    Result_CSR_SecuritizedNonCTP = pd.concat([CSR_SecuritizedNonCTPDelta, CSR_SecuritizedNonCTPCurvature, CSR_SecuritizedNonCTPVega],axis = 0)

    CSR_CTP = RAWData[RAWData["Risk_Class"].isin(["CSR CTP","csr ctp","CSR 유동화(CTP)","신용스프레드 유동화(CTP)"]) ]
    CSR_CTP_Delta = CSR_CTP[CSR_CTP["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_CTP_Curvature = CSR_CTP[CSR_CTP["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_CTP_Vega = CSR_CTP[CSR_CTP["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    Result_CSR_CTP = pd.concat([CSR_CTP_Delta, CSR_CTP_Curvature, CSR_CTP_Vega],axis = 0)

    GIRR = RAWData[RAWData["Risk_Class"] == "GIRR" ]
    GIRR_Delta = GIRR[GIRR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    GIRR_Curvature = GIRR[GIRR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    GIRR_Vega = GIRR[GIRR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor1","RiskFactor3":"Tenor2"})
    Result_GIRR = pd.concat([GIRR_Delta, GIRR_Curvature, GIRR_Vega],axis = 0)

    FXR = RAWData[RAWData["Risk_Class"] == "FXR" ]
    FXR_Delta = FXR[FXR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    FXR_Curvature = FXR[FXR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    FXR_Vega = FXR[FXR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Temp_RiskFactor"})
    Result_FXR = pd.concat([FXR_Delta, FXR_Curvature, FXR_Vega],axis = 0)

    EQR = RAWData[RAWData["Risk_Class"] == "EQR" ]
    EQR_Delta = EQR[EQR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"StockName","RiskFactor3":"Temp_RiskFactor"})
    EQR_Curvature = EQR[EQR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"StockName","RiskFactor3":"Temp_RiskFactor"})
    EQR_Vega = EQR[EQR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"Tenor","RiskFactor3":"StockName"})
    Result_EQR = pd.concat([EQR_Delta, EQR_Curvature, EQR_Vega],axis = 0)

    COMR = RAWData[RAWData["Risk_Class"] == "COMR" ]
    COMR_Delta = COMR[COMR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    COMR_Curvature = COMR[COMR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    COMR_Vega = COMR[COMR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    Result_COMR = pd.concat([COMR_Delta, COMR_Curvature, COMR_Vega],axis = 0)
    return Result_CSR, Result_CSR_SecuritizedNonCTP, Result_CSR_CTP, Result_GIRR, Result_FXR, Result_EQR, Result_COMR

def PivotSensiByRiskFactor(Data, RiskFactorList, CurvatureFlag = 0) : 
    Data = Data.copy()
    for rf in RiskFactorList : 
        Data[rf] = Data[rf].fillna("NaN")
        
    if CurvatureFlag == 0 : 
        Groupped = Data.groupby(RiskFactorList)["WeightedSensi"].sum().reset_index()
        Others = Data.groupby(RiskFactorList).first().reset_index()[Data.columns.difference(list(RiskFactorList) + ["WeightedSensi"])]
        MyData =  pd.concat([Groupped, Others], axis = 1)
        MyData2 = MyData[(MyData["WeightedSensi"]> 0.01) | (MyData["WeightedSensi"]< -0.01) ]
    else : 
        Groupped1 = Data.groupby(RiskFactorList)["CVR_Plus"].sum()
        Groupped2 = Data.groupby(RiskFactorList)["CVR_Minus"].sum()
        Groupped = pd.concat([Groupped1, Groupped2],axis= 1).reset_index()
        Others = Data.groupby(RiskFactorList).first().reset_index()[Data.columns.difference(list(RiskFactorList) + ["CVR_Plus","CVR_Minus"])]
        MyData =  pd.concat([Groupped, Others], axis = 1)
        MyData2 = MyData[(MyData["CVR_Plus"]> 0.01) | (MyData["CVR_Plus"]< -0.01) | (MyData["CVR_Minus"]> 0.01) | (MyData["CVR_Minus"]< -0.01) ]
    return MyData2

def Calc_Kb_DeltaVega(WS, rho, median0up1dn2) : 
    '''
    Calculate Each Bucket RiskCharge 
    of Delta and Vega
    
    WS : Weighted Sensi 1d array
    rho : Sensi Corr 2d array
    
    '''
    n = len(WS)
    WSArray = np.zeros(n)
    rhoArray =np.zeros((n,n))
    for i in range(n) : 
        WSArray[i] = WS[i]
        for j in range(n) : 
            rhoArray[i][j] = rho[i][j]
    
    if median0up1dn2 == 1 : 
        for i in range(n) : 
            for j in range(n) : 
                rhoArray[i][j] = min(1, 1.25 * rhoArray[i][j])
    elif median0up1dn2 == 2 : 
        for i in range(n) : 
            for j in range(n) : 
                rhoArray[i][j] = max(2 * rhoArray[i][j] - 1, 0.75 * rhoArray[i][j])
            
    targetvalue = WSArray.dot(rhoArray).dot(WSArray)
    return np.sqrt(max(0, targetvalue))

@jit('double(double[:],double[:],double[:,:], int64)', nopython = True)
def Calc_AggregatedDeltaVega(Kb, Sb, Corr, median0up1dn2) : 
    '''
    Calculate Bucket Aggregated RiskCharge 
    of Delta and Vega    
    
    Kb : Kb by bucket 1d array
    Sb : Sum(Weighted Sensi) for each Bucket 1d array
    Corr : Interbucket Correlation 2d array
    
    '''
    n = len(Kb)
    riskcharge_sqaure = 0
    riskcharge = 0

    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += Kb[i] * Kb[j]
            else : 
                if median0up1dn2 == 1 : 
                    targetvalue += min(1, 1.25* Corr[i][j]) * Sb[i] * Sb[j]                
                elif median0up1dn2 == 2 : 
                    targetvalue += max(2 *Corr[i][j]-1,0.75 *Corr[i][j])  * Sb[i] * Sb[j]                
                else : 
                    targetvalue += Corr[i][j] * Sb[i] * Sb[j]
                
    riskcharge_sqaure = max(0, targetvalue)
    
    if (riskcharge_sqaure >= 0) : 
        riskcharge = np.sqrt(riskcharge_sqaure)
    else :
        NewSb = np.zeros(n)
        for i in range(n) : 
            NewSb[i] = max(-Kb[i], min(Sb[i], Kb[i]))
        
        targetvalue = 0
        for i in range(n) : 
            for j in range(n) : 
                if i == j : 
                    targetvalue += Kb[i] * Kb[j]
                else : 
                    if median0up1dn2 == 1 :
                        targetvalue += min(1, 1.25* Corr[i][j]) * NewSb[i] * NewSb[j]
                    elif median0up1dn2 == 2 : 
                        targetvalue += max(2 *Corr[i][j]-1,0.75 * Corr[i][j]) * NewSb[i] * NewSb[j]
                    else :     
                        targetvalue += Corr[i][j] * NewSb[i] * NewSb[j]
        
        riskcharge_sqaure = max(0, targetvalue)
        riskcharge = np.sqrt(riskcharge_sqaure)
    return riskcharge

@jit('double(double[:],double[:],double[:], int32)', nopython = True)
def Calc_CVR(Vud, V, DeltaWS, plus0minus1) : 
    '''
    Calculate Each Bucket RiskCharge 
    of Delta and Vega
    
    Vud : Value (h + Up, h + Down) 1d Array
    V : Value(h) 1d Array
    DeltaWS : Delta Weighted Sensi
    plus0minus1 : Flag CVR+ 0, CVR- 1
    
    '''    
    n = len(DeltaWS)
    targetvalue = 0
    if plus0minus1 == 0 : 
        for i in range(n) : 
            targetvalue += -(Vud[i] - V[i] - DeltaWS[i])
    else : 
        for i in range(n) : 
            targetvalue += -(Vud[i] - V[i] + DeltaWS[i])
    return targetvalue

@jit('double(double[:],double[:,:], int32)', nopython = True)
def Calc_Kb_Curvature(CVRPlusMinus, rho, median0up1dn2) : 
    '''
    Calculate Each Kb Curvature
    CVRPlusMinus : 1d array
    rho : 2d array
    '''
    n = len(CVRPlusMinus)
    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += max(0, CVRPlusMinus[i]) * max(0, CVRPlusMinus[j])
            else : 
                if CVRPlusMinus[i] < 0 and CVRPlusMinus[j] < 0 : 
                    phi = 0
                else :
                    phi = 1
                    
                if median0up1dn2 == 1 :
                    targetvalue += min(1, 1.25* rho[i][j]) * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
                elif median0up1dn2 == 2 : 
                    targetvalue += max(2 *rho[i][j]-1,0.75 * rho[i][j]) * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
                else : 
                    targetvalue += rho[i][j] * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
    return np.sqrt(max(0,targetvalue))

@jit('double(double[:],double[:],double[:],double[:],double[:,:], int32)', nopython = True)
def Calc_AggregatedCurvature(KbPlus, KbMinus, SumCVRPlus, SumCVRMinus, Corr, median0up1dn2) : 
    n = len(KbPlus)
    
    Scenario = np.zeros(n)
    Kb = np.zeros(n)
    Sb = np.zeros(n)
    for i in range(n) : 
        if KbPlus[i] >= KbMinus[i] : 
            Scenario[i] = 0
            Kb[i] = KbPlus[i]
            Sb[i] = SumCVRPlus[i]
        else : 
            Scenario[i] = 1
            Kb[i] = KbMinus[i]
            Sb[i] = SumCVRMinus[i]
    
    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += Kb[i] * Kb[j]
            else : 
                if Sb[i] < 0 and Sb[j] < 0 : 
                    phi = 0
                else : 
                    phi = 1
                
                if median0up1dn2 == 1 : 
                    targetvalue += Sb[i] * Sb[j] * min(1, 1.25* Corr[i][j]) * phi
                elif median0up1dn2 == 2 : 
                    targetvalue += Sb[i] * Sb[j] * max(2 *Corr[i][j]-1, 0.75 * Corr[i][j]) * phi
                else : 
                    targetvalue += Sb[i] * Sb[j] * Corr[i][j] * phi
                    
    return np.sqrt(max(0, targetvalue))

def Calc_GIRRDeltaSensiCorr(risktypelist, curvelist, tenorlist, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr) : 
    murexflag = 1
    risktype = np.vectorize(lambda x : 'rate' if 'rate' in x.lower() else ('inf' if 'inf' in x.lower() else 'crs'))(list(risktypelist))
    curve = list(curvelist)
    tenor = list(tenorlist)
    n = len(tenor)
    targetcorr = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetcorr[i][j] = 1.0
            elif (risktype[i] == risktype[j]) and (curve[i] == curve[j]) and (tenor[i] == tenor[j]) : 
                targetcorr[i][j] = 1.0
            else : 
                if (risktype[i].lower() == 'rate' and risktype[j].lower() == 'rate') : 
                    if (curve[i] == curve[j] and str(tenor[i]) != str(tenor[j])) : 
                        # Same Curve different Tenor
                        idx1 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[i]].index[0]
                        idx2 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[j]].index[0]                        
                        c = GIRR_DeltaRfCorr[idx1, idx2]
                        if murexflag == 1 : 
                            c = max(np.exp(-0.03*np.abs((float(tenor[i])-float(tenor[j])))/min(float(tenor[i]),float(tenor[j]))),0.4)
                        targetcorr[i][j] = c
                    elif (curve[i] != curve[j] and str(tenor[i]) == str(tenor[j])) :
                        # Same Tenor Different Curve
                        targetcorr[i][j] = 0.999
                    else : 
                        # Different Curve Different Tenor
                        idx1 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[i]].index[0]
                        idx2 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[j]].index[0]
                        c = GIRR_DeltaRfCorr[idx1, idx2]
                        if murexflag == 1 : 
                            c = max(np.exp(-0.03*np.abs((float(tenor[i])-float(tenor[j])))/min(float(tenor[i]),float(tenor[j]))),0.4)
                        targetcorr[i][j] = c * 0.999                
                elif (risktype[i].lower() == 'rate' and 'inf' in risktype[j].lower()) : 
                    # Rf Rate vs Inflation
                    targetcorr[i][j] = 0.4
                elif (risktype[j].lower() == 'rate' and 'inf' in risktype[i].lower()) : 
                    # Rf Rate vs Inflation
                    targetcorr[i][j] = 0.4
                elif (risktype[i].lower() == 'rate' and risktype[j].lower() == 'crs' )  :
                    # Rf Rate vs CRS
                    targetcorr[i][j] = 0.
                elif (risktype[j].lower() == 'rate' and risktype[i].lower() == 'crs' )  :
                    # Rf Rate vs CRS
                    targetcorr[i][j] = 0.
                elif ('inf' in risktype[i].lower() and 'inf' in risktype[j].lower()) : 
                    # Inflation vs Inflation
                    targetcorr[i][j] = 0.999
                elif ('inf' in risktype[i].lower() and risktype[j].lower() == 'crs') : 
                    # Inflation vs CRS
                    targetcorr[i][j] = 0.
                elif ('inf' in risktype[j].lower() and risktype[i].lower() == 'crs') : 
                    # Inflation vs CRS
                    targetcorr[i][j] = 0.
                else :
                    # CRS vs CRS
                    targetcorr[i][j] = 0.
    return targetcorr

def GIRR_DeltaRiskWeight_Scalar(Tenor, Currency, Type) : 
    
    x = float(Tenor)
    c = str(Currency) in ["KRW","EUR","USD","GBP","AUD","JPY","SEK","CAD"]
    mytype = str(Type)
    
    div = np.sqrt(2) if c == True else 1
    
    if 'inf' in mytype.lower() or "xccy" in mytype.lower() or "crs" in mytype.lower(): 
        return 0.016/div    
    elif float(x) <= 0.25 : 
        return 0.017/div
    elif float(x) <= 0.5 : 
        return 0.017/div
    elif float(x) <= 1 : 
        return 0.016/div
    elif float(x) <= 2 : 
        return 0.013/div
    elif float(x) <= 3 : 
        return 0.012/div
    else : 
        return 0.011/div
GIRR_DeltaRiskWeight = np.vectorize(GIRR_DeltaRiskWeight_Scalar)    
    
def CSR_DeltaRiskWeight(bucket, flagb8 = False) : 
    b = int(bucket)
    MyIndex = np.arange(1,19)
    Value = np.array([0.5, 1, 5, 3, 3, 2, 
                      1.5, 2.5, 2, 4, 12, 
                      7, 8.5, 5.5, 5, 12, 1.5, 5], 
                     dtype = np.float64)/100
    if (b == 8 and flagb8 == True) : 
        w = 0.015
    else : 
        return pd.Series(Value, index = MyIndex).loc[b]
    
def FX_DeltaRiskWeight(FXPair, HighLiquidCurrency) : 
    MyPair = ["",""]
    if '-' in FXPair : 
        MyPair[0] = FXPair.split("-")[0]
        MyPair[1] = FXPair.split("-")[1]
    elif "/" in FXPair : 
        MyPair[0] = FXPair.split("/")[0]
        MyPair[1] = FXPair.split("/")[1]
    else : 
        raise ValueError("CheckFXPair String")
    
    if (MyPair[0] in HighLiquidCurrency) and (MyPair[1] in HighLiquidCurrency) : 
        return 0.10606601717798211
    else :
        return 0.15    
    
def MapEquityRiskWeight(Data,EQRWMappingDF,TypeColName = "Type", BucketColName = "Bucket") : 
    '''
    Calc Risk Weight as EQ (1) RiskFactor type and (2) Bucket
    Data : DataFrame that have columns Type(Price or Repo), Bucket(1, 2, 3, ...)
    excample : 
    
        risktype = ["price","price","price","repo"]
        riskbucket = ["1","1","3","3"]
        df = pd.DataFrame([risktype,riskbucket], index = ["Type","Bucket"]).T        
        MapEquityRiskWeight(df,EQRWMappingDF,TypeColName = "Type", BucketColName = "Bucket")
        -> 0.55, 0.55, 0.45, 0.0045        
        
    '''
    def func(Data, EQRWMappingDF, TypeColName, BucketColName) : 
        if 'price' in str(Data[TypeColName]).lower() or '가격' in str(Data[TypeColName]).lower() : 
            if int(Data[BucketColName]) >= 0 :
                return EQRWMappingDF["SpotRW"].loc[int(Data[BucketColName])]
            else : 
                return 0
        else : 
            if int(Data[BucketColName]) >= 0 :            
                return EQRWMappingDF["RepoRW"].loc[int(Data[BucketColName])]    
            else : 
                return 0
    
    return Data.apply(func, axis = 1, EQRWMappingDF = EQRWMappingDF, TypeColName = TypeColName , BucketColName = BucketColName)

def CSR_sensicorrbucket(bucket, issuerlist, tenorlist, curvelist) : 
    b = bucket
    issuerlist = list(issuerlist)
    tenorlist = list(tenorlist)
    curvelist = list(curvelist)
    n = len(issuerlist)
    targetarray = np.identity(n)
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                issuer1 = issuerlist[i]
                issuer2 = issuerlist[j]
                tenor1 = tenorlist[i]
                tenor2 = tenorlist[j]
                curve1 = curvelist[i]
                curve2 = curvelist[j]
                if (int(b) < 16 ) : 
                    c1 = 1.0 if issuer1 == issuer2 else 0.35
                    c2 = 1.0 if tenor1 == tenor2 else 0.65
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                elif (int(b) > 16) :
                    c1 = 1.0 if issuer1 == issuer2 else 0.8
                    c2 = 1.0 if tenor1 == tenor2 else 0.65
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                else : 
                    c = 1
            targetarray[i][j] = c
    return targetarray
            
def CSR_SecuritizedNonCTPDelta_sensicorr(bucket, tranche, tenorlist, curvelist) : 
    b = bucket
    tranchelist = list(tranche)
    tenorlist = list(tenorlist)
    curvelist = list(curvelist)
    n = len(tranchelist)
    targetarray = np.identity(n)
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                tranche11 = tranchelist[i]
                tranche12 = tranchelist[j]
                tenor1 = tenorlist[i]
                tenor2 = tenorlist[j]
                curve1 = curvelist[i]
                curve2 = curvelist[j]
                if (int(b) < 25 ) : 
                    c1 = 1.0 if tranche1 == tranche2 else 0.4
                    c2 = 1.0 if tenor1 == tenor2 else 0.8
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                else : 
                    c = 1
            targetarray[i][j] = c
    return targetarray    
    
def CSRDeltaBucketRatingCorr(bucketlist) : 
    n = len(bucketlist)
    bucketlist = list(bucketlist)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                b1 = int(bucketlist[i])
                b2 = int(bucketlist[j])
                if b1 < 16 and b2 < 16 : 
                    if (b1 <= 8 and b2 > 8) or (b2 <= 8 and b1 > 8) : 
                        # 버킷 1 ~ 15이고 서로 신용도가 다르면 50%
                        c = 0.5
                    else : 
                        c = 1.0
                else : 
                    c = 1.0
                targetarray[i][j] = c
    return targetarray

def findbucketindex(bucket, bucketindex) : 
    resultindex = -1
    for i, ind in enumerate(bucketindex) : 
        if type(ind) == tuple or type(ind) == list : 
            if int(bucket) in ind : 
                resultindex = i
                break
        else : 
            if int(bucket) == int(ind) : 
                resultindex = i
                break
    return resultindex

def CSRDeltaBucketSectorCorr(bucketlist, CSR_DeltaNonSecurCorrDf) :   
    bucketlist = list(bucketlist)
    n = len(bucketlist)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                b1 = int(bucketlist[i])
                b2 = int(bucketlist[j])
                col = findbucketindex(b1, CSR_DeltaNonSecurCorrDf.columns)
                ind = findbucketindex(b2, CSR_DeltaNonSecurCorrDf.index)
                c = CSR_DeltaNonSecurCorrDf.values[ind][col]
                targetarray[i][j] = c
    return targetarray

def EquityDeltaInBucketSensiCorr(Bucket, TypeList, StockNameList) :
    n = len(StockNameList)
    TypeList = list(TypeList)
    StockNameList = list(StockNameList)
    targetarray = np.identity(n)
    MyType = []
    for t in TypeList : 
        if ('rep' in t) or ('rp' in t) : 
            MyType.append('repo')
        else : 
            MyType.append('spot')
    Bucket = int(Bucket)
    if int(Bucket) < 5 : 
        c = 0.15
    elif int(Bucket) < 9 : 
        c = 0.25
    elif int(Bucket) == 9 : 
        c = 0.075
    elif int(Bucket) == 10 : 
        c = 0.125
    elif int(Bucket) == 11 : 
        c = 1
    elif int(Bucket) > 11 : 
        c = 0.8
    else : 
        c = 0
    
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                if MyType[i] == MyType[j] : 
                    targetarray[i][j] = c
                else :
                    if StockNameList[i] == StockNameList[j] : 
                        targetarray[i][j] = 0.999
                    else : 
                        targetarray[i][j] = c * 0.999
    return targetarray

def EquityDeltaBucketAggregatedCorr(BucketList) : 
    '''
    Calculate Bucket Aggregated Correlation Matrix 
    
    BucketList : BucketList Integer 1 Array    
    '''    
    n = len(BucketList)
    BucketList = list(BucketList)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) :             
            B1 = int(BucketList[i])
            B2 = int(BucketList[j])
            if int(B1) == int(B2) : 
                c = 1
            else : 
                if int(B1) < 10 and int(B2) < 10 :
                    c = 0.15
                elif int(B1) == 11 or int(B2) == 11 : 
                    c = 0.0
                elif int(B1) > 11 and int(B2) > 11 : 
                    c = 0.75
                else : 
                    c = 0.45
            targetarray[i][j] = c
    return targetarray                

def COMM_deltasensicorrbucket(bucket, commoditylist, tenorlist, locationlist) : 
    n = len(commoditylist)
    commoditylist = list(commoditylist)
    tenorlist = list(tenorlist)
    locationlist = list(locationlist)
    targetarray = np.identity(n)
    commcorrseries = pd.Series([0.55,0.95,0.40,0.80,0.6,
                                0.65,0.55,0.45,0.15,0.4,
                                0.15], index = np.arange(1,12))    
    cc = commcorrseries.loc[int(bucket)]
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                if (commoditylist[i] == commoditylist[j]) : 
                    c1 = 1
                else :
                    c1 = cc
                
                if (tenorlist[i] == tenorlist[j]) : 
                    c2 = 1
                else : 
                    c2 = 0.999
                    
                if (locationlist[i] == locationlist[j]) : 
                    c3 = 1
                else : 
                    c3 = 0.999
                c = c1 * c2 * c3
                                    
            targetarray[i][j] = c
    return targetarray

def COMM_DeltaBucketAggregatedCorr(bucketlist) : 
    n = len(bucketlist)
    bucketlist = list(bucketlist)
    targetarray = np.identity(n)
    
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                if (int(bucketlist[i]) < 11 and int(bucketlist[j]) < 11) :
                    targetarray[i][j] = 0.2
                else :
                    targetarray[i][j] = 0
    return targetarray

def COMM_sensicorrbucket(bucket, commoditylist, tenorlist, locationlist) : 
    n = len(commoditylist)
    commoditylist = list(commoditylist)
    tenorlist = list(tenorlist)
    locationlist = list(locationlist)
    targetarray = np.identity(n)
    commcorrseries = pd.Series([0.55,0.95,0.40,0.80,0.6,
                                0.65,0.55,0.45,0.15,0.4,
                                0.15], index = np.arange(1,12))    
    cc = commcorrseries.loc[int(bucket)]
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                if (commoditylist[i] == commoditylist[j]) : 
                    c1 = 1
                else :
                    c1 = cc
                
                if (tenorlist[i] == tenorlist[j]) : 
                    c2 = 1
                else : 
                    c2 = 0.999
                    
                if (locationlist[i] == locationlist[j]) : 
                    c3 = 1
                else : 
                    c3 = 0.999
                c = c1 * c2 * c3
                                    
            targetarray[i][j] = c
    return targetarray

def COMM_BucketAggregatedCorr(bucketlist) : 
    n = len(bucketlist)
    bucketlist = list(bucketlist)
    targetarray = np.identity(n)
    
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                if (int(bucketlist[i]) < 11 and int(bucketlist[j]) < 11) :
                    targetarray[i][j] = 0.2
                else :
                    targetarray[i][j] = 0

optionmaturitycorr = lambda t_i, t_j : np.exp(-0.01*abs(t_i-t_j)/min(t_i, t_j))
def tenorcorr(TenorList) : 
    targetarray = np.identity(len(TenorList)) 
    for i in range(len(TenorList)) : 
        for j in range(len(TenorList)) : 
            if i == j : 
                targetarray[i][j] = 1
            else :
                targetarray[i][j] = optionmaturitycorr(float(TenorList[i]), float(TenorList[j]))
    return targetarray

def GIRR_VegaSensiCorr(OptTenorList, UndTenorList) : 
    n = len(OptTenorList)
    OptTenorList = list(OptTenorList)
    UndTenorList = list(UndTenorList)
    targetarray = np.identity(n)
    
    for i in range(n) : 
        for j in range(n) : 
            if (i == j) :
                targetarray[i][j] = 1
            else : 
                c1 = optionmaturitycorr(float(OptTenorList[i]), float(OptTenorList[j]))
                c2 = optionmaturitycorr(float(UndTenorList[i]), float(UndTenorList[j]))
                c = c1 * c2
                targetarray[i][j] = min(1, c)
    return targetarray

calcsb = lambda df : df["WeightedSensi"].sum()

def Calc_CSRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting    
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Issuer"], CurvatureFlag = 0)
    
    if len(sensidata) < 1 : 
        return 0
    
    corrsensi = CSR_sensicorrbucket(sensidata["BucketCopy"].iloc[0], sensidata["Issuer"], sensidata["Tenor"].astype(np.float64), sensidata["Curve"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return float(KB)

def Calc_CSRDelta_KB_ByBucket(MyData, SensitivityColumnName = "Delta") : 
    MyData["BucketCopy"] = MyData["Bucket"]

    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'm')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'd')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'u')
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)

    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def Calc_CSRDelta(Delta_Data, CSR_DeltaNonSecurCorrDf, SensitivityColumnName = "Delta") :
    MyData = Delta_Data[Delta_Data["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["Curve"] = MyData["Curve"].fillna("NaN")
    MyData["Tenor"] = MyData["Tenor"].fillna("NaN")
    MyData["Issuer"] = MyData["Issuer"].fillna("NaN")
    MyData["RW"] = MyData["Bucket"].apply(CSR_DeltaRiskWeight)
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    
    CSRDelta_ByBuc = Calc_CSRDelta_KB_ByBucket(MyData, SensitivityColumnName)
    
    BucketCorr = CSRDeltaBucketRatingCorr(CSRDelta_ByBuc["Bucket"]) * CSRDeltaBucketSectorCorr(CSRDelta_ByBuc["Bucket"],CSR_DeltaNonSecurCorrDf)
    CSRDelta_M = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_M"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    CSRDelta_D = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_D"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    CSRDelta_U = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_U"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = CSRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,CSRDelta_U, CSRDelta_M, CSRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([CSRDelta_ByBuc, Result],axis = 0)    

def Calc_GIRRDelta_KB(DataByBucket, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, CorrScenario = 'm') :
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Type"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    corrsensi = Calc_GIRRDeltaSensiCorr(sensidata["Type"], sensidata["Curve"], sensidata["Tenor"].astype(np.float64), GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr)
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return float(KB)

def Calc_GIRRDelta_KB_ByBucket(MyData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName = "Delta") : 
    MyData["BucketCopy"] = MyData["Bucket"]
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    
    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'m')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'d')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'u')    
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def GIRRBucketCorr(MyData) : 
    grirbc = 0.5
    c = np.identity(len(MyData)) * (1-grirbc) + grirbc
    return c

def Calc_GIRRDelta(Delta_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName = "Delta") :
    MyData = Delta_Data[Delta_Data["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["RW"] = GIRR_DeltaRiskWeight(MyData["Tenor"].values, MyData["Bucket"].values, MyData["Type"].values)
    GIRRDelta_ByBuc = Calc_GIRRDelta_KB_ByBucket(MyData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName )
    BucketCorr = GIRRBucketCorr(GIRRDelta_ByBuc)

    GIRRDelta_M = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_M"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    GIRRDelta_D = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_D"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    GIRRDelta_U = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_U"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = GIRRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,GIRRDelta_U, GIRRDelta_M, GIRRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])

    return pd.concat([GIRRDelta_ByBuc, Result],axis = 0)   

def Calc_GIRRKb_Curvature(Data_Sensi, CorrScenario, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName = "Delta") : 
    if Data_Sensi["CVR_Plus"].isna().sum() == len(Data_Sensi) and Data_Sensi["CVR_Minus"].isna().sum() == len(Data_Sensi) :    
        V = Data_Sensi["Value"].values.astype(np.float64)
        DeltaWS = Data_Sensi["DeltaWeightedSensi"].values
        Data_Sensi["CVR_Plus"] = Calc_CVR(Data_Sensi["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        Data_Sensi["CVR_Minus"] = Calc_CVR(Data_Sensi["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
        
    if len(Data_Sensi) > 0:
        Kb_plus = max(0,Data_Sensi["CVR_Plus"].sum())
        Kb_minus = max(0,Data_Sensi["CVR_Minus"].sum())
        Kb = max(Kb_plus, Kb_minus)
        Sb_plus = Data_Sensi["CVR_Plus"].sum()
        Sb_minus = Data_Sensi["CVR_Minus"].sum()    
        CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
        Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    else :
        Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, CurvatureScenario = 0,0,0,0,0,0,0
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])

def Calc_GIRRCurvature(CurvatureData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName = "Delta") :
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData["Curve"] = CurvatureData["Curve"].fillna("NaN")
    CurvatureData["Tenor"] = CurvatureData["Tenor"].fillna("NaN")
    CurvatureData["Type"] = CurvatureData["Type"].fillna("NaN")
    if CurvatureData["CVR_Plus"].isna().sum() == len(CurvatureData) and CurvatureData["CVR_Minus"].isna().sum() == len(CurvatureData) :    
        CurvatureData["RW"] = GIRR_DeltaRiskWeight(CurvatureData["Tenor"].values, CurvatureData["Bucket"].values, CurvatureData["Type"].values)
        CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]    
    
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "m", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "u", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "d", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (GIRRBucketCorr(KB_Median))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   

def VegaRiskWeight_Scalar(Risk_Class, Bucket) : 
    rc = str(Risk_Class)
    b = str(Bucket)
    if ((rc in ["EQR","Equity","주식리스크","주식","주식리스크(EQR)"]) and (b in ["1","2","3","4","5","6","7","8","12","13"])) :
        return 0.7778
    else : 
        return 1.0
VegaRiskWeight = np.vectorize(VegaRiskWeight_Scalar)    
             
def Calc_GIRRVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor1","Tenor2"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    sensicorr = GIRR_VegaSensiCorr(sensidata["Tenor1"], sensidata["Tenor2"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), sensicorr, ScenarioFlag)
    return Kb    

def Calc_GIRRVega_KB_ByBucket(VegaData, SensitivityColumnName = "Vega") : 
    if "RW" not in VegaData.columns:
        VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
        VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    KBByBucket_M = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'m')
    KBByBucket_D = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'d')
    KBByBucket_U = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'u')   
    SBByBucket = VegaData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]    
    return Data

def Calc_GIRRVega(VegaData, SensitivityColumnName = "Vega") :    
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    VegaData["Curve"] = VegaData["Curve"].fillna("NaN")
    VegaData["Tenor1"] = VegaData["Tenor1"].fillna("NaN")
    VegaData["Tenor2"] = VegaData["Tenor2"].fillna("NaN")    
    GIRRVega_ByBuc = Calc_GIRRVega_KB_ByBucket(VegaData, SensitivityColumnName)
    BucketCorr = GIRRBucketCorr(GIRRVega_ByBuc)
    GIRRVega_M = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_M"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    GIRRVega_D = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_D"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    GIRRVega_U = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_U"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = GIRRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,GIRRVega_U, GIRRVega_M, GIRRVega_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([GIRRVega_ByBuc, Result],axis = 0) 

def FXRBucketCorr(MyData) : 
    grirbc = 0.6
    c = np.identity(len(MyData)) * (1-grirbc) + grirbc
    return c

def Calc_FXRDelta(FXRDeltaData, HighLiquidCurrency, SensitivityColumnName = "Delta") :    
    FXRDeltaData = FXRDeltaData[FXRDeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]    
    if len(FXRDeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    FXRDeltaData["RW"] = FXRDeltaData["Bucket"].apply(lambda x : FX_DeltaRiskWeight(x, HighLiquidCurrency))
    FXRDeltaData["WeightedSensi"] = FXRDeltaData["RW"] * FXRDeltaData[SensitivityColumnName]
    FXR_SB_ByBucket = FXRDeltaData.groupby("Bucket")["WeightedSensi"].sum()
    FXR_KB_ByBucket = np.abs(FXR_SB_ByBucket)
    BucketCorr = FXRBucketCorr(FXR_KB_ByBucket)
    Data = pd.concat([FXR_KB_ByBucket,FXR_KB_ByBucket,FXR_KB_ByBucket,FXR_SB_ByBucket],axis=1)
    Data.columns = ["KB_U","KB_M","KB_D","SB"]

    KB_M = Calc_AggregatedDeltaVega(Data["KB_U"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 0)
    KB_U = Calc_AggregatedDeltaVega(Data["KB_M"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 1)
    KB_D = Calc_AggregatedDeltaVega(Data["KB_D"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 2)
    Data_ByBucket = Data.reset_index()
    SB = Data_ByBucket["SB"].sum()
    Result = pd.DataFrame([[99999,KB_U, KB_M, KB_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([Data_ByBucket, Result],axis = 0) 

def Calc_FXRKb_Curvature(Data_Sensi, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if Data_Sensi["CVR_Plus"].isna().sum() == len(Data_Sensi) and Data_Sensi["CVR_Minus"].isna().sum() == len(Data_Sensi) :    
        Data_Sensi["DeltaWeightedSensi"] = Data_Sensi["RW"] * Data_Sensi[DeltaSensitivityColumnName]    
        V = Data_Sensi["Value"].values.astype(np.float64)
        DeltaWS = Data_Sensi["DeltaWeightedSensi"].values
        Data_Sensi["CVR_Plus"] = Calc_CVR(Data_Sensi["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        Data_Sensi["CVR_Minus"] = Calc_CVR(Data_Sensi["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb_plus = max(0.,Data_Sensi["CVR_Plus"].sum())
    Kb_minus =max(0.,Data_Sensi["CVR_Minus"].sum())
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = Data_Sensi["CVR_Plus"].sum()
    Sb_minus = Data_Sensi["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])

def Calc_FXRCurvature(FXRCurvatureData, HighLiquidCurrency, DeltaSensitivityColumnName = "Delta") :   
    FXRCurvatureData = FXRCurvatureData[FXRCurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                            
    if len(FXRCurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])        
    FXRCurvatureData["RW"] = FXRCurvatureData["Bucket"].apply(lambda x : FX_DeltaRiskWeight(x, HighLiquidCurrency))
    FXRCurvatureData["DeltaWeightedSensi"] = FXRCurvatureData["RW"] * FXRCurvatureData[DeltaSensitivityColumnName]

    KB_Median = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (FXRBucketCorr(KB_Median))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)       
    
def FXR_VegaSensiCorr(OptTenorList) : 
    n = len(OptTenorList)
    OptTenorList = list(OptTenorList)
    targetarray = np.identity(n) 
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                c = optionmaturitycorr(float(OptTenorList[i]),float(OptTenorList[j]))
                targetarray[i][j] = min(1,c)
    return targetarray
    
def Calc_FXRVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    sensicorr = FXR_VegaSensiCorr(list(sensidata["Tenor"]))
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), sensicorr, ScenarioFlag)
    return Kb    

def Calc_FXRVega_KB_ByBucket(VegaData, SensitivityColumnName = "Vega") : 
    if "RW" not in VegaData.columns : 
        VegaData["RW"] =  VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
        VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    KBByBucket_M = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'m')
    KBByBucket_D = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'d')
    KBByBucket_U = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'u')   
    SBByBucket = VegaData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]    
    return Data

def Calc_FXRVega(VegaData, SensitivityColumnName = "Vega") :    
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]    
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    
    VegaData["Bucket"] = VegaData["Bucket"].fillna("NaN")
    VegaData["Curve"] = VegaData["Curve"].fillna("NaN")
    VegaData["Tenor"] = VegaData["Tenor"].fillna("NaN")
    VegaData["RW"] =  VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    FXRVega_ByBuc = Calc_FXRVega_KB_ByBucket(VegaData, SensitivityColumnName)
    BucketCorr = FXRBucketCorr(FXRVega_ByBuc)
    FXRVega_M = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_M"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    FXRVega_D = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_D"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    FXRVega_U = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_U"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = FXRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,FXRVega_U, FXRVega_M, FXRVega_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([FXRVega_ByBuc, Result],axis = 0)     

def Calc_EQRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    groupped = PivotSensiByRiskFactor(DataByBucket, ["Type","StockName"], CurvatureFlag = 0)
    if len(groupped) == 0 : 
        return 0
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = EquityDeltaInBucketSensiCorr(groupped["BucketCopy"].iloc[0], groupped["Type"], groupped["StockName"])
    KB = Calc_Kb_DeltaVega(groupped["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_EQRDelta(DeltaData, SensitivityColumnName = "Delta") : 
    DeltaData = DeltaData[DeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]        
    if len(DeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    DeltaData = DeltaData.copy()
    DeltaData["BucketCopy"] = DeltaData["Bucket"]
    DeltaData["RW"] = MapEquityRiskWeight(DeltaData, EQDeltaRWMappingDF, TypeColName = "Type",BucketColName = "Bucket")
    DeltaData["WeightedSensi"] = DeltaData["RW"] * DeltaData[SensitivityColumnName]
    
    KB_M = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'m')
    KB_D = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'d')
    KB_U = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'u')
    SB = DeltaData.groupby("Bucket").apply(calcsb)
    
    EQRDelta_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    EQRDelta_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = EquityDeltaBucketAggregatedCorr(EQRDelta_ByBuc["Bucket"])
    EQRDelta_M = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_M"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,0)
    EQRDelta_U = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_U"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,1)
    EQRDelta_D = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_D"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = EQRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,EQRDelta_U, EQRDelta_M, EQRDelta_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([EQRDelta_ByBuc, Result],axis = 0)     
    
def Calc_EQRKb_Curvature(DataByBucket, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if DataByBucket["CVR_Plus"].isna().sum() == len(DataByBucket) and DataByBucket["CVR_Minus"].isna().sum() == len(DataByBucket) :    
        V = DataByBucket["Value"].values.astype(np.float64)
        DeltaWS = DataByBucket["DeltaWeightedSensi"].values
        DataByBucket["CVR_Plus"] = Calc_CVR(DataByBucket["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        DataByBucket["CVR_Minus"] = Calc_CVR(DataByBucket["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
    groupped = PivotSensiByRiskFactor(DataByBucket, ["Type","StockName"], CurvatureFlag = 1)
    CVRP = groupped["CVR_Plus"].values.astype(np.float64)
    CVRM = groupped["CVR_Minus"].values.astype(np.float64)
    TYPE = groupped["Type"]
    NAME = groupped["StockName"]

    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = EquityDeltaInBucketSensiCorr(DataByBucket["BucketCopy"].iloc[0], TYPE, NAME)**2
    Kb_plus = Calc_Kb_Curvature(CVRP, c , ScenarioFlag)
    Kb_minus = Calc_Kb_Curvature(CVRM, c , ScenarioFlag)
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = DataByBucket["CVR_Plus"].sum()
    Sb_minus = DataByBucket["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])    
    
def Calc_EQRCurvature(CurvatureData, EQDeltaRWMappingDF, DeltaSensitivityColumnName = "Delta_Sensi") :  
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                                
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData = CurvatureData.copy()
    CurvatureData["StockName"] = CurvatureData["StockName"].fillna("NaN")
    CurvatureData["Type"] = CurvatureData["Type"].fillna("NaN")
    CurvatureData["BucketCopy"] = CurvatureData["Bucket"]
    
    CurvatureData["RW"] = MapEquityRiskWeight(CurvatureData, EQDeltaRWMappingDF, TypeColName = "Type",BucketColName = "Bucket")
    CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (EquityDeltaBucketAggregatedCorr(DataByBucket["Bucket"]))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   

def Calc_EQRVega_KB(DataByBucket, CorrScenario = 'm') : 
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Tenor","StockName"])
    if len(sensidata) < 1 : 
        return 0
    c = EquityDeltaInBucketSensiCorr(sensidata["BucketCopy"].iloc[0], ["Price"] * len(sensidata) , sensidata["StockName"]) * tenorcorr(sensidata["Tenor"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_EQRVega(VegaData, SensitivityColumnName = "Vega") : 
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]        
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    VegaData = VegaData.copy()
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData[SensitivityColumnName] * VegaData["RW"]
    VegaData["BucketCopy"] = VegaData["Bucket"]
    
    KB_M = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'m')
    KB_D = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'d')
    KB_U = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'u')
    SB = VegaData.groupby("Bucket").apply(calcsb)
    
    EQRVega_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    EQRVega_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = EquityDeltaBucketAggregatedCorr(EQRVega_ByBuc["Bucket"])
    EQRVega_M = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_M"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,0)
    EQRVega_U = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_U"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,1)
    EQRVega_D = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_D"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = EQRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,EQRVega_U, EQRVega_M, EQRVega_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([EQRVega_ByBuc, Result],axis = 0)  

def Calc_COMRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Underlying","Tenor","Delivery"])
    if len(sensidata) == 0 : 
        return 0
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = COMM_deltasensicorrbucket(sensidata["BucketCopy"].iloc[0], sensidata["Underlying"], sensidata["Tenor"], sensidata["Delivery"]) 
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_COMRDelta(DeltaData, DeltaSensitivityColumnName = "Delta") : 
    DeltaData = DeltaData[DeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]        
    
    if len(DeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    DeltaData = DeltaData.copy()
    DeltaData["RW"] = DeltaData["Bucket"].astype(np.int64).map(COMM_Delta_RWMapping)
    DeltaData["WeightedSensi"] = DeltaData["RW"] * DeltaData[DeltaSensitivityColumnName]
    DeltaData["BucketCopy"] = DeltaData["Bucket"]
    
    KB_M = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'m')
    KB_D = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'d')
    KB_U = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'u')
    SB = DeltaData.groupby("Bucket").apply(calcsb)
    
    COMRDelta_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    COMRDelta_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = COMM_DeltaBucketAggregatedCorr(COMRDelta_ByBuc["Bucket"])
    COMRDelta_M = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_M"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,0)
    COMRDelta_U = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_U"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,1)
    COMRDelta_D = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_D"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = COMRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,COMRDelta_U, COMRDelta_M, COMRDelta_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([COMRDelta_ByBuc, Result],axis = 0)     
    
def Calc_COMRKb_Curvature(DataByBucket, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if DataByBucket["CVR_Plus"].isna().sum() == len(DataByBucket) and DataByBucket["CVR_Minus"].isna().sum() == len(DataByBucket) :    
        V = DataByBucket["Value"].values.astype(np.float64)
        DeltaWS = DataByBucket["DeltaWeightedSensi"].values
        DataByBucket["CVR_Plus"] = Calc_CVR(DataByBucket["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        DataByBucket["CVR_Minus"] = Calc_CVR(DataByBucket["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)

    Kb_plus = max(0, DataByBucket["CVR_Plus"].sum())
    Kb_minus = max(0, DataByBucket["CVR_Minus"].sum())
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = DataByBucket["CVR_Plus"].sum()
    Sb_minus = DataByBucket["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])    
    
def Calc_COMRCurvature(CurvatureData, DeltaSensitivityColumnName = "Delta") : 
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                                

    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData = CurvatureData.copy()
    CurvatureData["RW"] = CurvatureData["Bucket"].astype(np.int64).map(COMM_Delta_RWMapping)
    CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]
    CurvatureData["BucketCopy"] = CurvatureData["Bucket"]
    
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()    
    KB_Corr = COMM_DeltaBucketAggregatedCorr(DataByBucket["Bucket"])**2
    
    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   
        
def Calc_COMRVega(VegaData, SensitivityColumnName = "Vega") : 
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]            
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])
    VegaData = VegaData.copy()
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]
    VegaData["BucketCopy"] = VegaData["Bucket"]
    
    KB_M = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'m')
    KB_D = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'d')
    KB_U = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'u')
    SB = VegaData.groupby("Bucket").apply(calcsb)
    
    COMRVega_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    COMRVega_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = COMM_DeltaBucketAggregatedCorr(COMRVega_ByBuc["Bucket"])
    COMRVega_M = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_M"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,0)
    COMRVega_U = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_U"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,1)
    COMRVega_D = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_D"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = COMRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,COMRVega_U, COMRVega_M, COMRVega_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([COMRVega_ByBuc, Result],axis = 0)     
  
def AggregatedFRTB_RiskCharge(CSR_Data, GIRR_Data, FXR_Data, EQR_Data, COMR_Data, CSR_Sec_NonCTP_Data, CSR_CTP_Data, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0) : 
    TempDF = pd.DataFrame([])
    if GroupbyFlag == 0 : 
        CSRDelta_Total = Calc_CSRDelta(CSR_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName)
        
        GIRRDelta_Total = Calc_GIRRDelta(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRCurvature_Total = Calc_GIRRCurvature(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRVega_Total = Calc_GIRRVega(GIRR_Data, VegaSensiName)
        
        FXRDelta_Total = Calc_FXRDelta(FXR_Data, HighLiquidCurrency, DeltaSensiName)
        FXRCurvature_Total = Calc_FXRCurvature(FXR_Data, HighLiquidCurrency, DeltaSensiName)
        FXRVega_Total = Calc_FXRVega(FXR_Data, VegaSensiName)
        
        EQRDelta_Total = Calc_EQRDelta(EQR_Data, DeltaSensiName)
        EQRCurvature_Total = Calc_EQRCurvature(EQR_Data,EQDeltaRWMappingDF, DeltaSensiName)
        EQRVega_Total = Calc_EQRVega(EQR_Data,VegaSensiName)
        
        COMRDelta_Total = Calc_COMRDelta(COMR_Data, DeltaSensiName)
        COMRCurvature_Total = Calc_COMRCurvature(COMR_Data, DeltaSensiName)
        COMRVega_Total = Calc_COMRVega(COMR_Data, DeltaSensiName)  
    elif GroupbyFlag == 1 : 
        CSRDelta_Total = CSR_Data.groupby("Depart").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName)
        
        GIRRDelta_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRCurvature_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRVega_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRVega, VegaSensiName)
        
        FXRDelta_Total = FXR_Data.groupby("Depart").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName)
        FXRCurvature_Total = FXR_Data.groupby("Depart").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName)
        FXRVega_Total = FXR_Data.groupby("Depart").apply(Calc_FXRVega, VegaSensiName)
        
        EQRDelta_Total = EQR_Data.groupby("Depart").apply(Calc_EQRDelta, DeltaSensiName)
        EQRCurvature_Total = EQR_Data.groupby("Depart").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName)
        EQRVega_Total = EQR_Data.groupby("Depart").apply(Calc_EQRVega,VegaSensiName)
        
        COMRDelta_Total = COMR_Data.groupby("Depart").apply(Calc_COMRDelta, DeltaSensiName)
        COMRCurvature_Total = COMR_Data.groupby("Depart").apply(Calc_COMRCurvature, DeltaSensiName)
        COMRVega_Total = COMR_Data.groupby("Depart").apply(Calc_COMRVega, DeltaSensiName)  
    else : 
        CSRDelta_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName)
        
        GIRRDelta_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRCurvature_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName)
        GIRRVega_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRVega, VegaSensiName)
        
        FXRDelta_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName)
        FXRCurvature_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName)
        FXRVega_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRVega, VegaSensiName)
        
        EQRDelta_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRDelta, DeltaSensiName)
        EQRCurvature_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName)
        EQRVega_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRVega,VegaSensiName)
        
        COMRDelta_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRDelta, DeltaSensiName)
        COMRCurvature_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRCurvature, DeltaSensiName)
        COMRVega_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRVega, DeltaSensiName)  
    
    CSRDelta_Total["Risk_Type"] = "CSR_Delta"
    CSRDelta_Total["Risk_Class"] = "CSR"
    GIRRDelta_Total["Risk_Type"] = "GIRR_Delta"
    GIRRDelta_Total["Risk_Class"] = "GIRR"
    GIRRCurvature_Total["Risk_Type"] = "GIRR_Curvature"
    GIRRCurvature_Total["Risk_Class"] = "GIRR"
    GIRRVega_Total["Risk_Type"] = "GIRR_Vega"
    GIRRVega_Total["Risk_Class"] = "GIRR"
    FXRDelta_Total["Risk_Type"] = "FXR_Delta"
    FXRDelta_Total["Risk_Class"] = "FXR"
    FXRCurvature_Total["Risk_Type"] = "FXR_Curvature"
    FXRCurvature_Total["Risk_Class"] = "FXR"
    FXRVega_Total["Risk_Type"] = "FXR_Vega"
    FXRVega_Total["Risk_Class"] = "FXR"
    EQRDelta_Total["Risk_Type"] = "EQR_Delta"
    EQRDelta_Total["Risk_Class"] = "EQR"
    EQRCurvature_Total["Risk_Type"] = "EQR_Curvature"
    EQRCurvature_Total["Risk_Class"] = "EQR"
    EQRVega_Total["Risk_Type"] = "EQR_Vega"
    EQRVega_Total["Risk_Class"] = "EQR"
    COMRDelta_Total["Risk_Type"] = "COMR_Delta"
    COMRDelta_Total["Risk_Class"] = "COMR"
    COMRCurvature_Total["Risk_Type"] = "COMR_Curvature"
    COMRCurvature_Total["Risk_Class"] = "COMR"
    COMRVega_Total["Risk_Type"] = "COMR_Vega"
    COMRVega_Total["Risk_Class"] = "COMR"
    
    AggregatedData = pd.concat([CSRDelta_Total, 
                                GIRRDelta_Total, GIRRCurvature_Total, GIRRVega_Total,
                                FXRDelta_Total, FXRCurvature_Total, FXRVega_Total,
                                EQRDelta_Total, EQRCurvature_Total, EQRVega_Total,
                                COMRDelta_Total, COMRCurvature_Total, COMRVega_Total
                               ], axis = 0)
    if GroupbyFlag == 0 : 
        AggregatedGroupbyData = AggregatedData.groupby(["Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby("Risk_Class")[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClass.loc["SBM"] = TotalClass.sum(0)
        TotalClass = TotalClass.reset_index()
        TotalClass["Risk_Type"] = "*"
        TotalClass["Bucket"] = "*"
        TotalClass = pd.concat([AggregatedData, TotalClass], axis = 0).set_index(["Risk_Class","Risk_Type","Bucket"])
    elif GroupbyFlag == 1 :
        AggregatedGroupbyData = AggregatedData.groupby(["Depart","Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby(["Depart","Risk_Class"])[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClassRiskCharge = TotalClass.groupby("Depart")[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClassRiskCharge["Risk_Class"] = "SBM"
        TotalClassRiskCharge = TotalClassRiskCharge.set_index(["Depart","Risk_Class"])
        TotalClass = pd.concat([TotalClass, TotalClassRiskCharge],axis = 0).sort_index()
    else : 
        AggregatedGroupbyData = AggregatedData.groupby(["Portfolio","Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby(["Portfolio","Risk_Class"])[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClassRiskCharge = TotalClass.groupby("Portfolio")[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClassRiskCharge["Risk_Class"] = "SBM"
        TotalClassRiskCharge = TotalClassRiskCharge.set_index(["Portfolio","Risk_Class"])
        TotalClass = pd.concat([TotalClass, TotalClassRiskCharge],axis = 0).sort_index()
    return TotalClass
    
#if __name__ == __main__ : 
#RAWData = pd.read_csv("FRTB_RAW.csv")
#CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR = PreProcessingMyData(RAWData)
#MyDf = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0)    