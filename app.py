import os
import urllib.parse
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

load_dotenv()

@st.cache_data(ttl=600)
def fetch_account_data(year):
    conn_params = urllib.parse.quote_plus(
        f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
        f"SERVER={os.getenv('DB_HOST')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_params}")
    
    query = f"""
    SELECT day, maingroup, subgroup, [where], abstract01, deposit, withdrawal
    FROM dbo.AccountBook
    WHERE day LIKE '{year}%'
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

st.set_page_config(page_title="정식 손익계산서", layout="wide", initial_sidebar_state="expanded")
st.title("📊 AI 기반 정식 손익계산서 자동화 시스템")

current_year = datetime.datetime.now().year
year_options = [str(y) for y in range(current_year + 4, 2018, -1)]

st.sidebar.header("조회 조건 설정")
selected_year = st.sidebar.selectbox("조회 연도 선택", year_options, index=year_options.index(str(current_year)))

# Subgroup 매핑 사전
SUBGROUP_MAP = {
    "가수금": "가수금", "과오납": "가수금", "미확인": "가수금", "가지급금": "가지급금",
    "급여": "급여", "잡급": "잡급", "퇴직연금": "퇴직연금", "퇴직연금운용관리": "퇴직연금운용관리",
    "건강보험": "건강보험", "고용보험": "고용보험", "국민연금": "국민연금", "산재보험": "산재보험", "교육비": "교육훈련비",
    "시험비": "용역매출", "안전진단": "용역매출", "정부지원금": "국고보조금", "고철": "기타영업외수익", "기타수입": "기타영업외수익", "예금이자": "이자수익",
    "기타수도광열비": "기타수도광열비", "가스요금": "수도광열비", "수도요금": "수도광열비", "전기요금": "수도광열비",
    "복사기": "임차료", "복사기임차료": "임차료", "숙소임대료": "임차료", "여주숙소": "임차료", "정수기": "임차료", "창고임대": "임차료", "사무실": "임차료", "충북음성": "임차료",
    "차량보험": "보험료", "화재보험": "보험료", "직원보험": "보험료",
    "차량할부": "미지급금 정산", "기타차량유지비": "차량유지비", "도로통행료": "차량유지비", "주유": "차량유지비", "주차비": "차량유지비", "차량수리": "차량유지비", "출장비": "차량유지비",
    "기타소모품": "소모품비", "비품": "소모품비", "시험실": "소모품비", "영업팀": "소모품비", "사무용품": "사무용품비",
    "기타수선": "수선비", "장비수선": "수선비",
    "도서기타인쇄": "도서인쇄비", "명함인쇄": "도서인쇄비", "성적서인쇄": "도서인쇄비",
    "기타운반비": "운반비", "지게차": "운반비", "택배착불": "운반비",
    "기타접대": "업무추진비", "사무실접대": "업무추진비", "식대": "업무추진비", "현장접대": "업무추진비", "회의비": "업무추진비", "대표": "업무추진비", "양호승": "업무추진비", "선물비": "업무추진비",
    "경조금": "복리후생비", "명절": "복리후생비", "명절선물비": "복리후생비", "복리후생비기타": "복리후생비", "피복비": "복리후생비", "회식비": "복리후생비",
    "기타통신비": "통신비", "문자": "통신비", "사무실전화": "통신비", "우편요금": "통신비", "인터넷": "통신비", "휴대폰": "통신비", "비즈메카": "통신비",
    "무인경비": "무인경비",
    "과태료": "세금과공과", "기타세금": "세금과공과", "등록면허세": "세금과공과", "서류발급": "세금과공과", "자동차세": "세금과공과", "재산세": "세금과공과", "주민세": "세금과공과", "취등록세": "세금과공과", "종합소득세": "세금과공과",
    "법인세": "법인세비용", "근로소득세": "예수금", "부가가치세": "예수금", "사업소득세": "예수금", "퇴직소득": "퇴직소득세",
    "개인대출": "단기차입금", "대출원금": "장기차입금", "법인대출": "장기차입금", "대출이자": "이자비용",
    "건설표준시험원": "지급수수료", "기장대행": "지급수수료", "기타지급수수료": "지급수수료", "변호사": "지급수수료", "삼성탑": "지급수수료", "시험의뢰비": "지급수수료", "엘리베이트": "지급수수료", "팀오피스": "지급수수료", "폐기물": "지급수수료", "홈페이지": "지급수수료", "덕이동건축관련": "지급수수료", "본원": "지급수수료", "세금계산서": "지급수수료", "세종안전": "지급수수료", "지원": "지급수수료", "팀별": "지급수수료", "하수관거": "지급수수료",
    "장비구입": "비품", "숙소보증금": "임차보증금", "예비비": "현금", "카드결재": "미지급금 정산", "장비임대": "임대료"
}

MAINGROUP_MAP = {
    "입금": "용역매출", "수도광열비": "수도광열비", "통신비": "통신비", "차량유지비": "차량유지비",
    "복리후생비": "복리후생비", "보험료": "보험료", "운반비": "운반비", "이자비용": "이자비용",
    "소모품": "소모품비", "지급수수료": "지급수수료", "지급임차료": "임차료", "인건비": "급여",
    "접대비": "업무추진비", "외주비": "지급수수료", "도서인쇄비": "도서인쇄비", "세금과공과금": "세금과공과",
    "수선비": "수선비", "장비구입": "비품", "출금": "현금"
}

SALES_ACCOUNTS = ["국고보조금", "용역매출"]
COST_ACCOUNTS = [
    "급여", "잡급", "퇴직연금", "퇴직연금운용관리", "건강보험", "고용보험", "국민연금", "산재보험", "교육훈련비",
    "수도광열비", "기타수도광열비", "임차료", "무인경비", "보험료", "차량유지비",
    "소모품비", "사무용품비", "수선비", "지급수수료", "복리후생비", "통신비", "도서인쇄비",
    "업무추진비", "운반비", "비품"
]
OTHER_ACCOUNTS = ["기타영업외수익", "이자수익", "임대료", "이자비용", "단기차입금", "장기차입금", "임차보증금", "가수금", "가지급금", "미지급금 정산", "현금"]
TAX_ACCOUNTS = ["세금과공과", "법인세비용", "예수금", "퇴직소득세"]

def classify_account(row):
    sub = str(row['subgroup']).strip() if pd.notnull(row['subgroup']) else ""
    main = str(row['maingroup']).strip() if pd.notnull(row['maingroup']) else ""
    
    if sub in SUBGROUP_MAP:
        return SUBGROUP_MAP[sub]
    if main in MAINGROUP_MAP:
        return MAINGROUP_MAP[main]
    return "⚠️ 미분류"

def make_section_df(raw_pivot, acc_list, sum_label):
    section_pivot = raw_pivot.reindex(acc_list).fillna(0)
    sum_row = pd.DataFrame([section_pivot.sum()], index=[f"📌 {sum_label}"])
    df_combined = pd.concat([section_pivot, sum_row])
    return df_combined

def style_table(df):
    def apply_cell_style(row):
        is_subtotal = "📌" in str(row.name)
        styles = []
        for val in row:
            css = ""
            if is_subtotal:
                css += "background-color: #F0F2F6; font-weight: bold; font-size: 15px; "
            else:
                css += "font-weight: normal; font-size: 14px; "
            if isinstance(val, (int, float)):
                if val > 0:
                    css += "color: #1E88E5;"
                elif val < 0:
                    css += "color: #E53935;"
            styles.append(css)
        return styles
    return df.style.format("{:,.0f}").apply(apply_cell_style, axis=1)

# 클릭한 항목의 세부 내역을 표시하는 함수
def display_detail_table(df_raw, account_name):
    filtered_df = df_raw[df_raw['account'] == account_name][
        ['day', 'maingroup', 'subgroup', 'where', 'abstract01', 'deposit', 'withdrawal', 'amount']
    ].sort_values(by='day', ascending=False)
    
    st.info(f"👉 **[{account_name}]** 항목 클릭됨 - 총 **{len(filtered_df)}건**의 세부 거래내역")
    st.dataframe(
        filtered_df.style.format({
            'deposit': '{:,.0f}',
            'withdrawal': '{:,.0f}',
            'amount': '{:,.0f}'
        }),
        use_container_width=True
    )

if st.sidebar.button("데이터 불러오기 및 손익계산서 생성"):
    with st.spinner("MS SQL 데이터 수집 및 정밀 분리 중..."):
        df = fetch_account_data(selected_year)
        
        if df.empty:
            st.warning(f"{selected_year}년도 데이터가 없습니다.")
        else:
            df['month'] = df['day'].apply(lambda x: f"{int(str(x)[4:6])}월" if len(str(x)) >= 6 else "1월")
            df['amount'] = df['deposit'].fillna(0) - df['withdrawal'].fillna(0)
            df['account'] = df.apply(classify_account, axis=1)
            
            st.session_state['df_raw'] = df
            
            raw_pivot = df.pivot_table(index='account', columns='month', values='amount', aggfunc='sum', fill_value=0)
            months = [f"{i}월" for i in range(1, 13)]
            for m in months:
                if m not in raw_pivot.columns:
                    raw_pivot[m] = 0
            raw_pivot = raw_pivot[months]
            st.session_state['raw_pivot'] = raw_pivot

if 'raw_pivot' in st.session_state and 'df_raw' in st.session_state:
    raw_pivot = st.session_state['raw_pivot']
    df_raw = st.session_state['df_raw']

    st.subheader(f"📌 {selected_year}년 정식 손익계산서 (항목 클릭 시 세부내역 표시)")

    # 1. 매출액
    st.markdown("#### 1. 매출액 (수입 계정)")
    sales_df = make_section_df(raw_pivot, SALES_ACCOUNTS, "소계(총매출액)")
    event_sales = st.dataframe(style_table(sales_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="sales_tbl")
    if event_sales and event_sales.get("selection", {}).get("rows"):
        selected_idx = event_sales["selection"]["rows"][0]
        selected_account = sales_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account)
    st.markdown("---")

    # 2. 매출원가 및 영업비용
    st.markdown("#### 2. 매출원가 및 영업비용 (지출 계정)")
    cost_df = make_section_df(raw_pivot, COST_ACCOUNTS, "소계(총영업비용)")
    event_cost = st.dataframe(style_table(cost_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="cost_tbl")
    if event_cost and event_cost.get("selection", {}).get("rows"):
        selected_idx = event_cost["selection"]["rows"][0]
        selected_account = cost_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account)
    st.markdown("---")

    # 3. 영업이익 종합 요약
    st.markdown("#### 🏆 3. 영업이익 종합 (총매출액 - 총영업비용)")
    sales_sum = raw_pivot.reindex(SALES_ACCOUNTS).fillna(0).sum()
    cost_sum = raw_pivot.reindex(COST_ACCOUNTS).fillna(0).sum()
    operating_profit = sales_sum + cost_sum
    
    summary_df = pd.DataFrame([
        sales_sum,
        cost_sum,
        operating_profit
    ], index=["1. 총매출액(수입)", "2. 총영업비용(지출)", "📌 3. 영업이익 (매출-비용)"])
    st.dataframe(style_table(summary_df), use_container_width=True)
    st.markdown("---")

    # 4. 영업외손익
    st.markdown("#### 4. 영업외손익 및 기타")
    other_df = make_section_df(raw_pivot, OTHER_ACCOUNTS, "소계(영업외손익)")
    event_other = st.dataframe(style_table(other_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="other_tbl")
    if event_other and event_other.get("selection", {}).get("rows"):
        selected_idx = event_other["selection"]["rows"][0]
        selected_account = other_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account)
    st.markdown("---")

    # 5. 세금 항목
    st.markdown("#### 5. 세금 및 예수금 항목")
    tax_df = make_section_df(raw_pivot, TAX_ACCOUNTS, "소계(세금항목)")
    event_tax = st.dataframe(style_table(tax_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="tax_tbl")
    if event_tax and event_tax.get("selection", {}).get("rows"):
        selected_idx = event_tax["selection"]["rows"][0]
        selected_account = tax_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account)
    st.markdown("---")