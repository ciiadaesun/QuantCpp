#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
Investment Model
v1.0.1
"""
import re
import numpy as np
import pandas as pd
import requests
import os
import time
from bs4 import BeautifulSoup
vers = "1.0.1"
recentupdate = '20251221'

TodayDate = int(f"{pd.Timestamp.now().date():%Y%m%d}")
consdir = os.getcwd() + '\\MarketData\\investment\\FSIS\\연결'
indivdir = os.getcwd() + '\\MarketData\\investment\\FSIS\\별도'
HEADERS = {"User-Agent": "Mozilla/5.0"}
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://m.stock.naver.com/",
}

def to_number(x):
    """'1,234', '-', '(1,234)' 등을 숫자로 변환. 실패하면 None."""
    if x is None:
        return None
    s = str(x).strip()
    if s in ("", "-", "N/A", "NaN"):
        return None

    # 쉼표 제거
    s = s.replace(",", "")

    # (1234) -> -1234 처리 (정규식 없이)
    if s.startswith("(") and s.endswith(")"):
        inner = s[1:-1].strip()
        s = "-" + inner

    # 퍼센트/기타 기호가 섞일 가능성 방어
    s = s.replace("%", "").strip()

    try:
        return float(s)
    except ValueError:
        return None

def get_kospi200_list(page_size=300):
    """
    코스피200 종목코드/종목명 목록(JSON).
    시점에 따라 200이 아니라 202 등으로 내려올 수 있어 page_size를 여유 있게 둠.
    """
    url = f"https://m.stock.naver.com/api/json/sise/enrollItemListJson.nhn?pageSize={page_size}"
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    j = r.json()

    items = j.get("result", {}).get("itemList", [])
    if not items:
        raise RuntimeError("코스피200 종목 리스트가 비어있습니다. 엔드포인트/파라미터를 점검하세요.")

    df = pd.DataFrame(items).rename(columns={"cd": "code", "nm": "name"})
    df["code"] = df["code"].astype(str).str.zfill(6)
    return df[["code", "name"]].drop_duplicates()

def get_exclude_codes_etf_etn(session: requests.Session) -> set:
    """
    네이버 ETF/ETN 목록 API를 통해 제외할 종목코드 set 생성
    - ETF: /api/sise/etfItemList.nhn
    - ETN: /api/sise/etnItemList.nhn
    """
    exclude = set()

    # ETF
    r = session.get("https://finance.naver.com/api/sise/etfItemList.nhn", timeout=20)
    r.raise_for_status()
    data = r.json()
    for x in data.get("result", {}).get("etfItemList", []):
        code = str(x.get("itemcode", "")).strip()
        if code:
            exclude.add(code)

    # ETN
    r = session.get("https://finance.naver.com/api/sise/etnItemList.nhn", timeout=20)
    r.raise_for_status()
    data = r.json()
    for x in data.get("result", {}).get("etnItemList", []):
        code = str(x.get("itemcode", "")).strip()
        if code:
            exclude.add(code)

    return exclude

def get_kospi_top500_ex_etf_fast() -> pd.DataFrame:
    base = "https://finance.naver.com/sise/sise_market_sum.naver"
    out = []
    page = 1

    with requests.Session() as s:
        s.headers.update(HEADERS)

        exclude_codes = get_exclude_codes_etf_etn(s)

        while len(out) < 500:
            r = s.get(base, params={"sosok": 0, "page": page}, timeout=20)
            r.raise_for_status()
            r.encoding = "euc-kr"

            soup = BeautifulSoup(r.text, "html.parser")

            # ✅ 표 안에서 "각 행의 a태그"를 직접 읽어 코드/이름을 동시에 추출
            # 시장총액 표는 보통 class='type_2' 테이블에 존재
            table = soup.select_one("table.type_2")
            if not table:
                raise RuntimeError("시장총액 테이블(table.type_2)을 찾지 못했습니다.")

            for a in table.select('a[href*="item/main.naver?code="]'):
                href = a.get("href", "")
                name = a.get_text(strip=True)
                if not name:
                    continue

                # href 예: /item/main.naver?code=005930
                # code는 6자리 숫자인 경우가 대부분이지만, 안전하게 '=' 뒤를 그대로 추출
                code = href.split("code=")[-1].split("&")[0].strip()
                if not code:
                    continue

                # ✅ ETF/ETN 제외
                if code in exclude_codes:
                    continue

                out.append({"종목코드": code, "종목명": name})
                if len(out) >= 500:
                    break

            page += 1

    # 중복 제거 + 500개 컷
    df = pd.DataFrame(out).drop_duplicates(subset=["종목코드"]).head(500).reset_index(drop=True)
    df.columns = ['code','name']
    return df

def _extract_encparam(html: str) -> str:
    patterns = [
        r"encparam\s*:\s*'([^']+)'",
        r"encparam\s*=\s*'([^']+)'",
        r"encparam\s*=\s*\"([^\"]+)\"",
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    raise RuntimeError("encparam을 찾지 못했습니다. (페이지 구조 변경 가능)")

def _pick_fin_table(dfs, items=("매출액","영업이익","당기순이익")):
    for df in dfs:
        if df.shape[1] < 2:
            continue
        first = df.columns[0]
        col0 = df[first].astype(str)

        hit = sum(col0.str.contains(re.escape(it), na=False).any() for it in items)
        if hit >= 2:
            out = df.copy()
            out[first] = out[first].astype(str).str.strip()
            out = out.set_index(first)
            out.columns = [re.sub(r"\s+", "", str(c)) for c in out.columns]
            return out
    return None

def _extract_float_shares_regex(html: str):
    # "유통주식수 123,456,789주" 패턴
    m = re.search(r"유통주식수\s*[:\-]?\s*([\d,]+)\s*주", html)
    if m:
        return int(m.group(1).replace(",", ""))

    # 혹시 '발행주식수' 같은 표기 케이스
    m = re.search(r"발행주식수\s*[:\-]?\s*([\d,]+)\s*주", html)
    if m:
        return int(m.group(2).replace(",", ""))

    return None

def _get_page_encparam(sess, cmp_cd: str, fin_typ: int | None, verify_ssl=True):
    # fin_typ을 URL에 같이 넣어서 “그 탭 기준”으로 encparam을 얻는다
    base = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={cmp_cd}"
    url = base if fin_typ is None else (base + f"&fin_typ={fin_typ}")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.naver.com/",
    }
    r = sess.get(url, headers=headers, timeout=20, verify=verify_ssl)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = "euc-kr"

    encparam = _extract_encparam(r.text)
    return encparam, url  # url은 ajax Referer로도 사용

def fetch_financial_summary(
    cmp_cd: str,
    freq_typ: str = "Y",
    fin_typ: int | None = None,
    items=("매출액", "영업이익", "당기순이익"),
    verify_ssl: bool = True
):
    """
    - freq_typ: 'Y'(연간) / 'Q'(분기)
    - fin_typ: 3(IFRS 별도), 0(IFRS 연결), 1(GAAP 별도), 2(GAAP 연결)
    - 핵심 수정: fin_typ별로 encparam을 다시 뽑아 AJAX 호출
    """
    cmp_cd = str(cmp_cd).zfill(6)
    sess = requests.Session()

    ajax_url = "https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx"

    fin_typ_candidates = [fin_typ] if fin_typ is not None else [0, 1, 2, 3, 4, 5, 6]
    last_err = None

    for ft in fin_typ_candidates:
        try:
            # ✅ fin_typ별 encparam 재취득
            encparam, referer_url = _get_page_encparam(sess, cmp_cd, ft, verify_ssl=verify_ssl)

            ajax_headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": referer_url,  # ✅ fin_typ이 반영된 페이지로 referer
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "text/html, */*; q=0.01",
            }

            params = {
                "cmp_cd": cmp_cd,
                "fin_typ": str(ft),
                "freq_typ": freq_typ,
                "encparam": encparam,
            }

            rr = sess.get(ajax_url, headers=ajax_headers, params=params, timeout=20, verify=verify_ssl)
            rr.raise_for_status()

            dfs = pd.read_html(rr.text)
            table = _pick_fin_table(dfs, items=items)
            table.columns = [x.split("/")[0][-4:] + x.split("/")[1][:2] for x in table.columns]
            if table is not None:
                return table, {"cmp_cd": cmp_cd, "fin_typ": ft, "freq_typ": freq_typ, "encparam": encparam}

        except Exception as e:
            last_err = e

    raise RuntimeError(f"재무 요약 표를 찾지 못했습니다. 마지막 예외: {last_err}")

def Currenct_Stock_Information(cmp_cd) : 
    url = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={cmp_cd}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.naver.com/",
    }

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = "euc-kr"

    soup = BeautifulSoup(r.text, "html.parser")

    # ✅ "주요재무정보" 표 tbody를 특정 (너 코드처럼 첫 tbody를 쓰되, 더 안전하게 제목 포함 테이블을 고를 수도 있음)
    tbodies = soup.select("tbody")
    tbody = tbodies[0]
    trs = tbody.select("tr")

    rows = []
    max_tds = 0

    for tr in trs:
        th = tr.select_one("th")
        key = th.get_text(strip=True) if th else ""

        tds = tr.select("td")
        vals = [td.get_text(" ", strip=True) for td in tds]  # 값들(여러 칸일 수 있음)
        max_tds = max(max_tds, len(vals))

        rows.append((key, vals))

    # ✅ td 개수에 맞춰 컬럼 생성 (Value1, Value2, ...)
    cols = ["주요재무정보"] + [f"Value{i+1}" for i in range(max_tds)]

    data = []
    for key, vals in rows:
        # td 개수가 부족하면 None으로 패딩
        padded = vals + [None] * (max_tds - len(vals))
        data.append([key] + padded)

    df = pd.DataFrame(data, columns=cols)

    return df.set_index("주요재무정보")

def Update_Financial_Data(RenewFlag = False, fin_type = 3) : 
    KOSPI500LIST = get_kospi_top500_ex_etf_fast()
    MMDD = int(str(TodayDate)[-4:])
    if MMDD < 430: 
        FirstYYYYMM = str((TodayDate//10000 - 1) * 100 + 12)
    elif MMDD < 715 : 
        FirstYYYYMM = str(TodayDate)[:-4] + '03'
    elif MMDD < 1015 :
        FirstYYYYMM = str(TodayDate)[:-4] + '06'
    elif MMDD < 1231 :
        FirstYYYYMM = str(TodayDate)[:-4] + '09'
    else : 
        FirstYYYYMM = str(TodayDate)[:-4] + '12'
    YYYYMM = FirstYYYYMM
    for i in range(24) : 
        if '12' in YYYYMM : 
            os.makedirs(consdir + '\\' + YYYYMM + "결산" , exist_ok=True) 
            os.makedirs(indivdir + '\\' + YYYYMM + "결산" , exist_ok=True) 
            os.makedirs(consdir + '\\' + YYYYMM, exist_ok=True) 
            os.makedirs(indivdir + '\\' + YYYYMM, exist_ok=True) 
        else : 
            os.makedirs(consdir + '\\' + YYYYMM, exist_ok=True) 
            os.makedirs(indivdir + '\\' + YYYYMM, exist_ok=True) 

        TempDate = pd.to_datetime(str(YYYYMM)[:-2] + '-' +str(YYYYMM)[-2:] + '-01')
        TempDate2 = (TempDate + pd.DateOffset(months = -3)).date()
        YYYYMM = str(TempDate2.year) + ('0' + str(TempDate2.month))[-2:]

    ResultFrame1 = pd.DataFrame()
    ResultFrame2 = pd.DataFrame()
    ResultFrame3 = pd.DataFrame()
    ResultFrame4 = pd.DataFrame()
    StockList = list(KOSPI500LIST[KOSPI500LIST.columns[0]])
    NStockList = len(StockList)
    Number1 = int(NStockList/2) #한번에하면 랙걸려서 파이썬 튕김
    for n in range(Number1) :
        cmp_cd = StockList[n] 
        try : 
            df_y_indiv, meta_y_indiv = fetch_financial_summary(cmp_cd, freq_typ="Y", fin_typ = fin_type)
            df_y_indiv.columns = [[cmp_cd] * len(df_y_indiv.columns) , df_y_indiv.columns]

            df_q_indiv, meta_q_indiv = fetch_financial_summary(cmp_cd, freq_typ="Q", fin_typ = fin_type)
            df_q_indiv.columns = [[cmp_cd] * len(df_q_indiv.columns) , df_q_indiv.columns]
            ResultFrame1 = pd.concat([ResultFrame1, df_y_indiv],axis = 1)
            ResultFrame2 = pd.concat([ResultFrame2, df_q_indiv],axis = 1)
            print(str(n) + ": " + cmp_cd + "완료" )
        except RuntimeError : 
            print(str(n) + ": " + cmp_cd + "데이터 없음" )
            pass
    print("절반 concat완료")

    for n in range(Number1, NStockList) :
        cmp_cd = StockList[n] 
        try : 
            df_y_indiv, meta_y_indiv = fetch_financial_summary(cmp_cd, freq_typ="Y", fin_typ = fin_type)
            df_y_indiv.columns = [[cmp_cd] * len(df_y_indiv.columns) , df_y_indiv.columns]

            df_q_indiv, meta_q_indiv = fetch_financial_summary(cmp_cd, freq_typ="Q", fin_typ = fin_type)
            df_q_indiv.columns = [[cmp_cd] * len(df_q_indiv.columns) , df_q_indiv.columns]
            ResultFrame3 = pd.concat([ResultFrame3, df_y_indiv],axis = 1)
            ResultFrame4 = pd.concat([ResultFrame4, df_q_indiv],axis = 1)
            print(str(n) + ": " + cmp_cd + "완료" )
        except RuntimeError : 
            print(str(n) + ": " + cmp_cd + "데이터 없음" )
            pass
    print("전체 concat완료")
    ResultFrame1 = pd.concat([ResultFrame1, ResultFrame3], axis = 1)
    ResultFrame2 = pd.concat([ResultFrame2, ResultFrame4], axis = 1)

    ResultFrame1.columns = pd.MultiIndex.swaplevel(ResultFrame1.columns,0)
    ResultFrame2.columns = pd.MultiIndex.swaplevel(ResultFrame2.columns,0)
    mydir = indivdir if fin_type == 3 else consdir
    for d in sorted(pd.MultiIndex.droplevel(ResultFrame1.columns, 1).unique()) :         
        if int(d) <= int(FirstYYYYMM) and '12' in str(d): 
            if RenewFlag == False : 
                if 'FSISData.xlsx' not in os.listdir(mydir + '\\' + str(d) + '결산') : 
                    ResultFrame1[d].to_excel(mydir + '\\' + str(d) + '결산' + '\\FSISData.xlsx')
            else : 
                ResultFrame1[d].to_excel(mydir + '\\' + str(d) + '결산' + '\\FSISData.xlsx')

    for d in sorted(pd.MultiIndex.droplevel(ResultFrame2.columns, 1).unique()) : 
        if int(d) <= int(FirstYYYYMM) and str(d)[-2:] in ['03','06','09','12']   : 
            if RenewFlag == False : 
                if 'FSISData.xlsx' not in os.listdir(mydir + '\\' + str(d)) : 
                    ResultFrame2[d].to_excel(mydir + '\\' + str(d) + '\\FSISData.xlsx')
            else : 
                ResultFrame2[d].to_excel(mydir + '\\' + str(d) + '\\FSISData.xlsx')
            print(str(d) + "저장완료")

def Calc_mktv() : 
    KOSPI500 = get_kospi_top500_ex_etf_fast()
    KOSPI500LIST = list(KOSPI500['code'])
    f = lambda x : float(str(x).split("억원")[0]) * 100000000 if "억원" in str(x) else (float(str(x).split("백만원")[0]) * 1000000 if "백만원" in str(x) else float(x))
    mktvlist = []
    recentret = []
    for n, cmp_cd in enumerate(KOSPI500LIST) : 
        cur_info = Currenct_Stock_Information(cmp_cd)
        mktv = f(cur_info.loc["시가총액"][0].replace(",",""))
        mktvlist.append(mktv/100000000) #시총도 억단위 맞추자
        recentret.append(cur_info.iloc[-1].iloc[0])
        if (n == 50) : 
            print("10% 완료")
        elif (n == 100) : 
            print("30% 완료")
        elif (n == 200) : 
            print("50% 완료")
        elif (n == 350) : 
            print("70% 완료")
        elif (n == 450) : 
            print("90% 완료")        
    KOSPI500[cur_info.index[-1]] = recentret        
    KOSPI500["시가총액"] = mktvlist    
    return KOSPI500

# 사용 예시
if __name__ == "__main__":
    Update_Financial_Data(RenewFlag = True)
    # 카카오(035720) 연간
    MarketValue = Calc_mktv()
    numberofstock = 50
    FSISprev = pd.read_excel(indivdir + '\\' + str((TodayDate - 10000)//10000 * 100 + 12) + '결산\\FSISData.xlsx',index_col = 0)
    FSISprevprev = pd.read_excel(indivdir + '\\' + str((TodayDate - 20000)//10000 * 100 + 12) + '결산\\FSISData.xlsx',index_col = 0)

    # 0.25 * 최근연도 + 0.125전전분기 + 0.125직전분기 + 0.5최근분기
    MMDD = int(str(TodayDate)[-4:])
    if MMDD < 331: 
        FirstYYYYMM = str((TodayDate//10000 - 1) * 100 + 12)
    elif MMDD < 715 : 
        FirstYYYYMM = str(TodayDate)[:-4] + '03'
    elif MMDD < 1015 :
        FirstYYYYMM = str(TodayDate)[:-4] + '06'
    elif MMDD < 1231 :
        FirstYYYYMM = str(TodayDate)[:-4] + '09'
    else : 
        FirstYYYYMM = str(TodayDate)[:-4] + '12'
    NameList = []
    PERList = []
    DEBTList = []
    PSRList = []
    PBRList = []
    POCFRList = []
    ROEList = []
    ROAList = []
    EBITRATIOList = []   
    for k, cmp_cd in enumerate(list(MarketValue[MarketValue.columns[0]])) : 
        if cmp_cd in FSISprev.columns : 
            FSISPrevIsna = FSISprev[cmp_cd].isna()
            if bool(FSISPrevIsna["매출액"]) == True and bool(FSISPrevIsna["영업이익"]) : 
                FSISData_Y = FSISprevprev
            else : 
                FSISData_Y = FSISprev

            YYYYMM = FirstYYYYMM
            AdjustSales = float(FSISData_Y[cmp_cd]['매출액'] * 0.25)
            AdjustEBIT = float(FSISData_Y[cmp_cd]['영업이익'] * 0.25)
            AdjustNP = float(FSISData_Y[cmp_cd]['당기순이익'] * 0.25)
            AdjustEquity = float(FSISData_Y[cmp_cd]['자본총계'] * 0.25)
            AdjustAsset = float(FSISData_Y[cmp_cd]['자산총계'] * 0.25)
            AdjustOCF = float(FSISData_Y[cmp_cd]['영업활동현금흐름'] * 0.25)
            FSISprev[cmp_cd]
            nanflag = False
            n = 0
            if bool(FSISprev[cmp_cd].isna()['매출액'] == True) : 
                nanflag = True
            else : 
                for i in range(24) : 
                    mydata = pd.read_excel(indivdir + '\\' + YYYYMM + '\\FSISData.xlsx', index_col = 0)
                    if cmp_cd in mydata.columns : 
                        srs = mydata[cmp_cd].fillna(0.0)
                        if bool(srs["매출액"] == 0) or bool(srs["영업이익"] == 0) : 
                            None
                        else : 
                            if n == 0 : 
                                AdjustSales += float(srs['매출액'] *4* 0.5)
                                AdjustEBIT += float(srs['영업이익'] *4* 0.5)
                                AdjustNP += float(srs['당기순이익'] *4* 0.5)
                                AdjustOCF += float(srs['영업활동현금흐름'] *4* 0.5)
                                AdjustAsset += float(srs['자산총계']* 0.5)
                                AdjustEquity += float(srs['자본총계']* 0.5)
                            else : 
                                AdjustSales += float(srs['매출액'] *4* 0.125)
                                AdjustEBIT += float(srs['영업이익'] *4* 0.125)
                                AdjustNP += float(srs['당기순이익'] *4* 0.125)                            
                                AdjustOCF += float(srs['영업활동현금흐름'] *4* 0.125)
                                AdjustAsset += float(srs['자산총계']* 0.125)
                                AdjustEquity += float(srs['자본총계']* 0.125)
                            n += 1 
                        
                        if n >= 3 : 
                            break

                    TempDate = pd.to_datetime(str(YYYYMM)[:-2] + '-' +str(YYYYMM)[-2:] + '-01')
                    TempDate2 = (TempDate + pd.DateOffset(months = -3)).date()
                    YYYYMM = str(TempDate2.year) + ('0' + str(TempDate2.month))[-2:]

            if (n < 2) : 
                AdjustSales = float(FSISData_Y[cmp_cd]['매출액'] * 0.8)
                AdjustEBIT = float(FSISData_Y[cmp_cd]['영업이익'] * 0.8)
                AdjustNP = float(FSISData_Y[cmp_cd]['당기순이익'] * 0.8)
                AdjustEquity = float(FSISData_Y[cmp_cd]['자본총계'])
                AdjustAsset = float(FSISData_Y[cmp_cd]['자산총계'])
                AdjustOCF = float(FSISData_Y[cmp_cd]['영업활동현금흐름'] * 0.8)
            AdjustDebtRatio = (AdjustAsset - AdjustEquity)/AdjustEquity
            np.isnan(AdjustSales)
            DEBT = 9999 if AdjustDebtRatio < 0 else AdjustDebtRatio
            mv = float(MarketValue.set_index(MarketValue.columns[0]).loc[cmp_cd]['시가총액'])
            PER = mv/AdjustNP if AdjustNP > 0 else 9999
            PSR = mv/AdjustSales if AdjustSales > 0 else 9999
            PBR = mv/AdjustEquity if AdjustEquity > 0 else 9999
            POCFR = mv/AdjustOCF if AdjustOCF > 0 else 9999
            ROE = AdjustNP/AdjustEquity if AdjustNP > 0 else -9999 
            ROA = AdjustNP/AdjustAsset if AdjustNP > 0 else -9999
            EBITRATIO = AdjustEBIT/AdjustSales if AdjustEBIT > 0 else -9999
            NameList.append(cmp_cd)
            PERList.append(PER)
            PSRList.append(PSR)
            PBRList.append(PBR)
            POCFRList.append(POCFR)
            ROEList.append(ROE)
            ROAList.append(ROA)
            EBITRATIOList.append(EBITRATIO)
            DEBTList.append(DEBT)
        if (k == 50) : 
            print("10% 완료")
        elif (k == 100) : 
            print("30% 완료")
        elif (k == 200) : 
            print("50% 완료")
        elif (k == 350) : 
            print("70% 완료")
        elif (k == 450) : 
            print("90% 완료")
    Result = pd.DataFrame([PERList, PSRList, PBRList, POCFRList, ROEList, ROAList, EBITRATIOList, DEBTList], index = ["PER", "PSR", "PBR", "POCFR", "ROE", "ROA", "EBITRATIO", "DEBT"], columns = NameList).T.fillna(0.0)
    PERRank = Result["PER"].rank()
    PSRRank = Result["PSR"].rank()
    PBRRank = Result["PBR"].rank()
    POCFRRank = Result["POCFR"].rank()
    ROERank = Result["ROE"].rank(ascending = False)
    ROARank = Result["ROA"].rank(ascending = False)
    EBITRATIORank = Result["EBITRATIO"].rank(ascending = False)
    DEBTRank = Result["DEBT"].rank()
    TotalRank = (PERRank + PSRRank + PBRRank + POCFRRank + ROERank + ROARank + EBITRATIORank).rank().sort_values()
    MyData = TotalRank.reset_index().rename(columns = {0:"total순위"})
    MyData = MyData.sort_values(by = "total순위")
    targetmap1 = MarketValue.set_index(MarketValue.columns[0])[MarketValue.columns[1]]
    targetmap2 = MarketValue.set_index(MarketValue.columns[0])[MarketValue.columns[-2]]
    MyData["종목명"] = MyData['index'].map(targetmap1)
    MyData["PERRank"] = MyData['index'].map(PERRank)
    MyData["PSRRank"] = MyData['index'].map(PSRRank)
    MyData["PBRRank"] = MyData['index'].map(PBRRank)
    MyData["POCFRRank"] = MyData['index'].map(POCFRRank)
    MyData["ROERank"] = MyData['index'].map(ROERank)
    MyData["ROARank"] = MyData['index'].map(ROARank)
    MyData["EBITRATIORank"] = MyData['index'].map(EBITRATIORank)

    MyData["최근수익률(1M/3M/6M/1Y)"] = MyData['index'].map(targetmap2)
    MyData.iloc[:numberofstock].to_excel("주식랭크.xlsx", index = False)
# %%
x = 20
df = get_kospi_top500_ex_etf_fast()
df.iloc[250]
#get_etf_codes()
# %%
