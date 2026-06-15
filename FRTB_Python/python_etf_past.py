# %%
import re
import time
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def _to_num(x):
    if x is None:
        return None
    x = str(x).replace(",", "").replace("%", "").strip()
    if x in ["", "-", "None", "nan"]:
        return None
    return pd.to_numeric(x, errors="coerce")


def _format_date(date):
    date = str(date).replace("-", "").replace(".", "")
    return f"{date[:4]}.{date[4:6]}.{date[6:8]}"


def get_kodex_product_info(etf_code, headless=False):
    """
    ETF코드 -> KODEX ETF_ID, ETF명 자동 조회
    예: 091160 -> 2ETF07, KODEX 반도체
    """
    etf_code = str(etf_code).zfill(6)

    opt = Options()
    if headless:
        opt.add_argument("--headless=new")
    opt.add_argument("--window-size=1600,1400")

    driver = webdriver.Chrome(options=opt)

    try:
        driver.get("https://www.samsungfund.com/etf/product/list.do")
        time.sleep(2)

        # 검색창 찾기
        search_input = driver.find_element(
            By.CSS_SELECTOR,
            "input[placeholder*='ETF']"
        )

        search_input.clear()
        search_input.send_keys(etf_code)
        time.sleep(2)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

        # ETF코드가 포함된 요소 찾기
        elems = driver.find_elements(By.XPATH, f"//*[contains(text(), '{etf_code}')]")

        if not elems:
            raise ValueError(f"{etf_code} 검색 결과를 찾지 못했습니다.")

        elem = elems[0]

        # 코드가 있는 영역의 부모를 타고 올라가며 클릭 가능한 카드/행 클릭
        driver.execute_script("""
            let e = arguments[0];
            for (let i = 0; i < 8; i++) {
                if (!e) break;
                if (e.tagName === 'A' || e.onclick || e.getAttribute('role') === 'button') {
                    e.click();
                    return;
                }
                e = e.parentElement;
            }
            arguments[0].click();
        """, elem)

        time.sleep(2)

        current_url = driver.current_url

        m = re.search(r"id=(2ETF\d+)", current_url)

        if not m:
            # 혹시 클릭이 안 됐으면 주변 링크에서 찾기
            html = driver.page_source
            m = re.search(r"view\.do\?id=(2ETF\d+)", html)

        if not m:
            raise ValueError(f"ETF_ID를 찾지 못했습니다. 현재 URL: {current_url}")

        etf_id = m.group(1)

        # ETF명 추출
        etf_name = ""

        # 1) title에서 추출
        title = driver.title.strip()
        if "KODEX" in title:
            etf_name = title.split("|")[0].split("-")[0].strip()

        # 2) 화면의 h1/h2에서 추출
        if not etf_name:
            for tag in ["h1", "h2", "h3"]:
                elems = driver.find_elements(By.TAG_NAME, tag)
                for e in elems:
                    txt = e.text.strip()
                    if "KODEX" in txt:
                        etf_name = txt.split("\n")[0].strip()
                        break
                if etf_name:
                    break

        # 3) body 전체 텍스트에서 KODEX 포함 라인 추출
        if not etf_name:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            for line in body_text.split("\n"):
                line = line.strip()
                if line.startswith("KODEX"):
                    etf_name = line
                    break

        return etf_id, etf_name

    finally:
        driver.quit()


def get_kodex_holdings(etf_code, date, headless=True):
    """
    ETF코드 + 기준일 -> KODEX 구성종목 PDF DataFrame
    """
    etf_code = str(etf_code).zfill(6)

    etf_id, etf_name = get_kodex_product_info(etf_code, headless=headless)

    date_api = _format_date(date)

    url = f"https://m.samsungfund.com/api/v1/kodex/product-pdf/{etf_id}.do"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://m.samsungfund.com/etf/product/view.do?id={etf_id}",
    }

    r = requests.get(
        url,
        params={"gijunYMD": date_api},
        headers=headers,
        timeout=30,
    )

    if r.status_code != 200:
        raise RuntimeError(f"조회 실패: {r.status_code}, {r.url}, {r.text[:300]}")

    data = r.json()["pdf"]

    rows = []

    for x in data["list"]:
        rows.append({
            "ETF코드": etf_code,
            "ETF명": etf_name,
            "ETF_ID": etf_id,
            "기준일": data.get("gijunYMD"),
            "수신시간": data.get("rcvTime"),
            "종목명": x.get("secNm"),
            "종목코드": x.get("itmNo"),
            "비중": _to_num(x.get("ratio")),
            "수량": _to_num(x.get("applyQ")),
            "평가금액": _to_num(x.get("evalA")),
            "현재가": _to_num(x.get("curp")),
            "등락": _to_num(x.get("risep")),
        })

    df = pd.DataFrame(rows)

    return df.sort_values(
        "비중",
        ascending=False,
        na_position="last"
    ).reset_index(drop=True)
#df = get_kodex_holdings("091160", "20260529", headless=False)
InputDate = input("YYYYMMDD 날짜 입력 : \n ->")
InputString = input("KODEX ETF 번호 입력(ex : 091160, 278530, 122630 ...) - \n ->").replace(" ","")
ETFCodeList = InputString.split(",")
df_list = []
for c in ETFCodeList : 
    df = get_kodex_holdings(c, InputDate, headless=False)
    #df["종목코드"] = df["구성종목명"].apply(get_stock_code)
    df_list.append(df)

with pd.ExcelWriter("KODEX ETF_구성종목.xlsx", engine="openpyxl") as writer:
    for n in range(len(df_list)) : 
        df_list[n].to_excel(writer, sheet_name=df_list[n]["ETF명"].iloc[0], index=False)

print("저장완료")

# %%
import requests
import pandas as pd
from bs4 import BeautifulSoup


def _to_num(x):
    if x is None:
        return None
    x = str(x).replace(",", "").replace("%", "").strip()
    if x in ["", "-", "None", "nan"]:
        return None
    return pd.to_numeric(x, errors="coerce")


def get_tiger_product_info(etf_code):
    etf_code = str(etf_code).zfill(6)

    url = "https://investments.miraeasset.com/tigeretf/ko/reference/list.ajax"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://investments.miraeasset.com/tigeretf/ko/reference/list.do",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "pageIndex": 1,
        "firstIndex": 0,
        "listCnt": 500,
        "searchText": "",
    }

    r = requests.post(url, headers=headers, data=data, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for btn in soup.select("button.pdfStatusPop"):
        ksd_fund = btn.get("data-ksd-fund", "")
        tiger_name = btn.get("data-jong-name", "").strip()

        if etf_code in ksd_fund:
            return ksd_fund, tiger_name

    raise ValueError(f"TIGER ETF 코드 {etf_code}를 찾지 못했습니다.")


def get_tiger_holdings(etf_code, date, list_cnt=1000):
    etf_code = str(etf_code).zfill(6)
    fix_date = str(date).replace("-", "").replace(".", "")

    ksd_fund, tiger_name = get_tiger_product_info(etf_code)

    url = "https://investments.miraeasset.com/tigeretf/ko/product/chart/prdct-item-list.ajax"

    params = {
        "ksdFund": ksd_fund,
        "prfPrd": "Week01",
        "fixDate": fix_date,
        "listCnt": list_cnt,
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://investments.miraeasset.com/tigeretf/ko/product/search/detail/index.do?ksdFund={ksd_fund}",
        "X-Requested-With": "XMLHttpRequest",
    }

    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()

    data = r.json().get("rtnData", [])

    rows = []

    for x in data:
        rows.append({
            "ETF코드": etf_code,
            "ETF명": tiger_name,
            "KSD_FUND": x.get("ksdFund"),
            "기준일": x.get("wkdate"),
            "종목코드": str(x.get("memItemcode", "")).strip().zfill(6)
                if str(x.get("memItemcode", "")).strip().isdigit()
                else str(x.get("memItemcode", "")).strip(),
            "ISIN": x.get("code"),
            "종목명": x.get("memItemname"),
            "수량": _to_num(x.get("stockQty")),
            "평가금액": _to_num(x.get("stockPrc")),
            "비중": _to_num(x.get("stockRate")),
            "1일수익률": _to_num(x.get("rate1d")),
            "1주수익률": _to_num(x.get("rate1w")),
            "1개월수익률": _to_num(x.get("rate1m")),
            "3개월수익률": _to_num(x.get("rate3m")),
            "6개월수익률": _to_num(x.get("rate6m")),
            "1년수익률": _to_num(x.get("rate1y")),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    return df.sort_values("비중", ascending=False, na_position="last").reset_index(drop=True)
# %%
InputString = input("TIGER ETF 번호 입력(ex : 396500, 102110, 232080 ...) - \n ->").replace(" ", "")
InputDate = input("YYYYMMDD 날짜 입력 : \n ->")

ETFCodeList = InputString.split(",")

df_list = []

for c in ETFCodeList:
    df = get_tiger_holdings(c, InputDate)
    df_list.append(df)

with pd.ExcelWriter("TIGER ETF_구성종목.xlsx", engine="openpyxl") as writer:
    for df in df_list:
        sheet_name = df["ETF명"].iloc[0][:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("저장완료")
# %%
