# QuantCpp

## C, C++ 관련 파일입니다.

## 1. 파생상품 종류별 엔진 (ELS, CDS, 구조화스왑, 커브생성기, LocalVolatility)

## 2. Util.h : 선형대수, 수치해석 헤더파일 (Interpolate, Tridiagonal, Gauss-Hermite Quadrature, Random Number, OLS, NeweyWest, Logit)

## 3. CalcDate.h : Date 관련 헤더파일 (YYYYMMDD, ExcelDate 등 변환 및 연산) + 한국, 미국, 영국 등 Holiday 생성

## 4. GetTextDump.h : 인풋변수 텍스트로그 생성

## 5. 현재 Murex 가격검증 완료

5.1 IRS -> 0.01bp 이내

5.2 구조화스왑 -> FDM : 20bp 이내, MC : 30bp 이내

5.3 커브제너레이터-> 0.01bp 이내

5.4 스왑션, 캡플로어, EQ옵션 -> 10bp 이내

5.5 CDS Hazard Rate Curve Estimation -> 20bp 이내

## 6. FRTB SA 산출모듈 파이썬 개발 완료

평가엔진모음.zip 압축파일 다운로드 가능
-----------------------------------
