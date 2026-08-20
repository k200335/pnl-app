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
OTHER_ACCOUNTS = ["기타영업외수익", "이자수익", "임대료", "이자비용"]
TAX_ACCOUNTS = ["세금과공과", "법인세비용"]
BS_ACCOUNTS = ["단기차입금", "장기차입금", "가수금", "가지급금", "예수금", "퇴직소득세", "임차보증금", "미지급금 정산", "현금"]

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

def display_detail_table(df_raw, account_name, key_suffix):
    base_df = df_raw[df_raw['account'] == account_name].copy()
    
    col1, _ = st.columns([1, 3])
    with col1:
        month_options = ["전체"] + [f"{i}월" for i in range(1, 13)]
        selected_month = st.selectbox(
            f"📅 [{account_name}] 조회 월 선택", 
            month_options, 
            key=f"month_select_{key_suffix}"
        )
    
    if selected_month != "전체":
        display_df = base_df[base_df['month'] == selected_month].copy()
    else:
        display_df = base_df.copy()
        
    display_df = display_df.sort_values(by='day', ascending=False)
    
    dep_sum = display_df['deposit'].fillna(0).sum()
    with_sum = display_df['withdrawal'].fillna(0).sum()
    amt_sum = display_df['amount'].fillna(0).sum()
    
    view_df = display_df[['day', 'maingroup', 'subgroup', 'where', 'abstract01', 'deposit', 'withdrawal', 'amount']].copy()
    
    sum_row = pd.DataFrame([{
        'day': '📌 합계',
        'maingroup': '-',
        'subgroup': '-',
        'where': '-',
        'abstract01': f'{selected_month} 총계 ({len(view_df)}건)',
        'deposit': dep_sum,
        'withdrawal': with_sum,
        'amount': amt_sum
    }])
    
    combined_view = pd.concat([view_df, sum_row], ignore_index=True)
    
    st.info(f"👉 **[{account_name}]** ({selected_month}) 세부 거래내역 - 총 **{len(view_df)}건**")
    
    def style_detail(df):
        def apply_row_style(row):
            is_total = str(row['day']) == '📌 합계'
            css = []
            for _ in row:
                if is_total:
                    css.append("background-color: #E8F0FE; font-weight: bold; font-size: 15px;")
                else:
                    css.append("")
            return css
        return df.style.format({
            'deposit': '{:,.0f}',
            'withdrawal': '{:,.0f}',
            'amount': '{:,.0f}'
        }).apply(apply_row_style, axis=1)

    st.dataframe(style_detail(combined_view), use_container_width=True)

def detect_anomaly_expenses(raw_pivot):
    cost_pivot = raw_pivot.reindex(COST_ACCOUNTS).fillna(0).abs()
    active_months = [m for m in cost_pivot.columns if cost_pivot[m].sum() > 0]
    if len(active_months) < 2:
        return []
    
    latest_month = active_months[-1]
    prev_months = active_months[:-1][-3:]
    
    anomalies = []
    for acc in cost_pivot.index:
        latest_val = cost_pivot.loc[acc, latest_month]
        avg_prev_val = cost_pivot.loc[acc, prev_months].mean()
        
        if avg_prev_val > 0 and latest_val >= avg_prev_val * 2.0 and (latest_val - avg_prev_val) >= 1_000_000:
            rate = ((latest_val - avg_prev_val) / avg_prev_val) * 100
            diff = latest_val - avg_prev_val
            anomalies.append({
                'account': acc,
                'month': latest_month,
                'latest_val': latest_val,
                'avg_val': avg_prev_val,
                'rate': rate,
                'diff': diff
            })
    return anomalies

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

    # ⚠️ [미분류 항목 존재 여부 체크 및 경고]
    unclassified_df = df_raw[df_raw['account'] == "⚠️ 미분류"]
    if not unclassified_df.empty:
        st.error(f"🚨 **[미분류 항목 경고]** 회계 계정과목으로 분류되지 않은 거래가 총 **{len(unclassified_df)}건** 존재합니다! (맨 아래 8번 섹션 확인 필수)")
        st.markdown("---")

    # ⚡ [이상 지출 경고]
    anomalies = detect_anomaly_expenses(raw_pivot)
    if anomalies:
        st.error(f"⚡ **[이달의 주요 이상 지출 경고]** 최근 평균 대비 지출이 급증한 항목이 포착되었습니다!")
        for a in anomalies:
            st.warning(
                f"🚨 **[{a['account']}]** ({a['month']}) 지출: **{a['latest_val']:,.0f}원** "
                f"(직전 평균 대비 **+{a['rate']:.0f}%** 급증 / **+{a['diff']:,.0f}원** 과다 지출)"
            )
        st.markdown("---")

    st.subheader(f"📌 {selected_year}년 정식 손익계산서 (항목 클릭 시 세부내역 표시)")

    # 1. 매출액
    st.markdown("#### 1. 매출액 (수입 계정)")
    sales_df = make_section_df(raw_pivot, SALES_ACCOUNTS, "소계(총매출액)")
    event_sales = st.dataframe(style_table(sales_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="sales_tbl")
    if event_sales and event_sales.get("selection", {}).get("rows"):
        selected_idx = event_sales["selection"]["rows"][0]
        selected_account = sales_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account, "sales")
    st.markdown("---")

    # 2. 매출원가 및 영업비용
    st.markdown("#### 2. 매출원가 및 영업비용 (지출 계정)")
    cost_df = make_section_df(raw_pivot, COST_ACCOUNTS, "소계(총영업비용)")
    event_cost = st.dataframe(style_table(cost_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="cost_tbl")
    if event_cost and event_cost.get("selection", {}).get("rows"):
        selected_idx = event_cost["selection"]["rows"][0]
        selected_account = cost_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account, "cost")
    st.markdown("---")

    # 3. 영업이익 종합
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
    st.markdown("#### 4. 영업외손익 (임대료, 이자 등)")
    other_df = make_section_df(raw_pivot, OTHER_ACCOUNTS, "소계(영업외손익)")
    event_other = st.dataframe(style_table(other_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="other_tbl")
    if event_other and event_other.get("selection", {}).get("rows"):
        selected_idx = event_other["selection"]["rows"][0]
        selected_account = other_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account, "other")
    st.markdown("---")

    # 5. 세금 및 법인세
    st.markdown("#### 5. 세금 및 법인세비용 (비용 항목만)")
    tax_df = make_section_df(raw_pivot, TAX_ACCOUNTS, "소계(세금항목)")
    event_tax = st.dataframe(style_table(tax_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="tax_tbl")
    if event_tax and event_tax.get("selection", {}).get("rows"):
        selected_idx = event_tax["selection"]["rows"][0]
        selected_account = tax_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account, "tax")
    st.markdown("---")

    # 6. 자산 및 부채 정산 항목
    st.markdown("#### 6. 자산·부채 정산 항목 (대출금, 예수금, 가지급금 등)")
    bs_df = make_section_df(raw_pivot, BS_ACCOUNTS, "소계(자산부채정산)")
    event_bs = st.dataframe(style_table(bs_df), use_container_width=True, on_select="rerun", selection_mode="single-row", key="bs_tbl")
    if event_bs and event_bs.get("selection", {}).get("rows"):
        selected_idx = event_bs["selection"]["rows"][0]
        selected_account = bs_df.index[selected_idx]
        if "📌" not in selected_account:
            display_detail_table(df_raw, selected_account, "bs")
    st.markdown("---")

    # 7. 최종 당기순이익
    st.markdown("#### 🎯 7. 최종 당기순이익 (영업이익 + 영업외손익 + 세금)")
    other_sum = raw_pivot.reindex(OTHER_ACCOUNTS).fillna(0).sum()
    tax_sum = raw_pivot.reindex(TAX_ACCOUNTS).fillna(0).sum()
    net_profit = operating_profit + other_sum + tax_sum
    
    net_summary_df = pd.DataFrame([
        operating_profit,
        other_sum,
        tax_sum,
        net_profit
    ], index=["3. 영업이익", "4. 영업외손익 소계", "5. 세금/법인세 소계", "📌 7. 최종 당기순이익"])
    st.dataframe(style_table(net_summary_df), use_container_width=True)
    st.markdown("---")

    # ⚠️ 8. 미분류 항목 출력 섹션 (확인 필수)
    st.markdown("#### ⚠️ 8. 미분류 항목 (확인 필수)")
    if unclassified_df.empty:
        st.success("✅ 미분류된 거래 내역이 존재하지 않습니다. 모든 데이터가 카테고리에 지정되었습니다!")
    else:
        st.warning(f"⚠️ 매핑 테이블에 없는 거래 **{len(unclassified_df)}건**이 존재합니다. 아래 내역을 확인해 주세요.")
        unclass_view = unclassified_df[['day', 'maingroup', 'subgroup', 'where', 'abstract01', 'deposit', 'withdrawal', 'amount']].sort_values(by='day', ascending=False)
        st.dataframe(
            unclass_view.style.format({
                'deposit': '{:,.0f}',
                'withdrawal': '{:,.0f}',
                'amount': '{:,.0f}'
            }),
            use_container_width=True
        )
    st.markdown("---")