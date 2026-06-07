#%%
"""
v1.0.2
"""

## python -m pip install selenium 
#import requests
#import pandas as pd
#import re
#
#KODEX_MAP = {
#    "069500": ("2ETF01", "KODEX 200"),
#    "091160": ("2ETF07", "KODEX 반도체"),
#    # 필요한 KODEX ETF 계속 추가
#}
#
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#import pandas as pd
#import re
#import requests
#
#url = "https://www.samsungfund.com/etf/product/list.do"
#
#r = requests.get(
#    url,
#    headers={"User-Agent":"Mozilla/5.0"}
#)
#
#print(r.status_code)
#print(r.text[:3000])
#
#def get_kodex_master():
#
#    driver = webdriver.Chrome()
#
#    driver.get("https://m.samsungfund.com/etf/product/list.do")
#
#    html = driver.page_source
#
#    driver.quit()
#
#    matches = re.findall(
#        r'view\.do\?id=(2ETF\d+).*?>(KODEX.*?)<',
#        html,
#        re.S
#    )
#
#    return pd.DataFrame(
#        matches,
#        columns=["ETF_ID", "ETF명"]
#    )
#    raise ValueError("ETF ID를 찾지 못함")
#
#def _format_date(date):
#    date = str(date).replace("-", "").replace(".", "")
#
#    if len(date) != 8:
#        raise ValueError("date는 YYYYMMDD 또는 YYYY.MM.DD 형식이어야 합니다.")
#
#    return f"{date[:4]}.{date[4:6]}.{date[6:8]}"
#
#
#def _to_num(x):
#    if x is None:
#        return None
#
#    x = str(x).replace(",", "").replace("%", "").strip()
#
#    if x in ["", "-", "None", "nan"]:
#        return None
#
#    return pd.to_numeric(x, errors="coerce")
#
#
#def get_kodex_holdings(etf_code, date):
#    """
#    KODEX ETF 구성종목 PDF 조회
#
#    etf_code : 예) 069500, 091160
#    date     : 예) 20260529 또는 2026.05.29
#    """
#
#    etf_code = str(etf_code).zfill(6)
#
#    if etf_code not in KODEX_MAP:
#        raise ValueError(f"{etf_code}는 KODEX_MAP에 ETF_ID 매핑이 없습니다.")
#
#    etf_id, etf_name = KODEX_MAP[etf_code]
#    date_api = _format_date(date)
#
#    url = f"https://m.samsungfund.com/api/v1/kodex/product-pdf/{etf_id}.do"
#
#    headers = {
#        "User-Agent": "Mozilla/5.0",
#        "Accept": "application/json, text/plain, */*",
#        "Referer": f"https://m.samsungfund.com/etf/product/view.do?id={etf_id}",
#    }
#
#    r = requests.get(
#        url,
#        params={"gijunYMD": date_api},
#        headers=headers,
#        timeout=30,
#    )
#
#    if r.status_code != 200:
#        raise RuntimeError(f"조회 실패: {r.status_code}, {r.url}, {r.text[:300]}")
#
#    data = r.json()["pdf"]
#
#    rows = []
#
#    for x in data["list"]:
#        rows.append({
#            "ETF코드": etf_code,
#            "ETF명": etf_name,
#            "ETF_ID": etf_id,
#            "기준일": data.get("gijunYMD"),
#            "수신시간": data.get("rcvTime"),
#            "종목명": x.get("secNm"),
#            "종목코드": x.get("itmNo"),
#            "비중": _to_num(x.get("ratio")),
#            "수량": _to_num(x.get("applyQ")),
#            "평가금액": _to_num(x.get("evalA")),
#            "현재가": _to_num(x.get("curp")),
#            "등락": _to_num(x.get("risep")),
#        })
#
#    df = pd.DataFrame(rows)
#
#    return df.sort_values(
#        "비중",
#        ascending=False,
#        na_position="last"
#    ).reset_index(drop=True)
#

# 사용 예시
#df = get_kodex_holdings("091160", "20260529")
#print(df.head(20))
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
