import os
import urllib.parse
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

# 1. 환경변수 설정
load_dotenv()

# DB 데이터 조회 함수
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

# UI 기본 설정
st.set_page_config(
    page_title="정식 손익계산서", 
    layout="wide", 
    initial_sidebar_state="expanded"
)
st.title("📊 AI 기반 정식 손익계산서 자동화 시스템")

# 연도 선택 셀렉트박스
current_year = datetime.datetime.now().year
year_options = [str(y) for y in range(current_year + 4, 2018, -1)]

st.sidebar.header("조회 조건 설정")
selected_year = st.sidebar.selectbox("조회 연도 선택", year_options, index=year_options.index(str(current_year)))

# 소그룹(subgroup) -> 계정과목 매핑 사전
SUBGROUP_MAP = {
    "가수금": "가수금", "과오납": "가수금", "미확인": "가수금",
    "가지급금": "가지급금", "종합소득세": "가지급금",
    "건강보험": "건강보험", "고용보험": "고용보험",
    "교육비": "교육훈련비", "정부지원금": "국고보조금", "국민연금": "국민연금", "급여": "급여",
    "기타수도광열비": "기타수도광열비", "고철": "기타영업외수익", "기타수입": "기타영업외수익",
    "개인대출": "단기차입금",
    "도서기타인쇄": "도서인쇄비", "명함인쇄": "도서인쇄비", "성적서인쇄": "도서인쇄비",
    "무인경비": "무인경비", "차량할부": "미지급금 정산", "법인세": "법인세비용",
    "차량보험": "보험료", "화재보험": "보험료",
    "경조금": "복리후생비", "명절": "복리후생비", "명절선물비": "복리후생비",
    "복리후생비기타": "복리후생비", "선물비": "복리후생비", "피복비": "복리후생비", "회식비": "복리후생비", "직원보험": "복리후생비",
    "장비구입": "비품", "사무용품": "사무용품비", "산재보험": "산재보험",
    "과태료": "세금과공과", "기타세금": "세금과공과", "등록면허세": "세금과공과",
    "서류발급": "세금과공과", "자동차세": "세금과공과", "재산세": "세금과공과", "주민세": "세금과공과", "취등록세": "세금과공과",
    "기타소모품": "소모품비", "비품": "소모품비", "시험실": "소모품비", "영업팀": "소모품비",
    "가스요금": "수도광열비", "수도요금": "수도광열비", "전기요금": "수도광열비",
    "기타수선": "수선비", "장비수선": "수선비",
    "기타접대": "업무추진비", "사무실접대": "업무추진비", "식대": "업무추진비",
    "현장접대": "업무추진비", "회의비": "업무추진비", "대표": "업무추진비", "양호승": "업무추진비",
    "근로소득세": "예수금", "부가가치세": "예수금", "사업소득세": "예수금",
    "시험비": "용역매출", "안전진단": "용역매출",
    "기타운반비": "운반비", "대출이자": "이자비용", "예금이자": "이자수익", "장비임대": "임대료",
    "복사기": "임차료", "복사기임차료": "임차료", "숙소임대료": "임차료", "여주숙소": "임차료",
    "정수기": "임차료", "창고임대": "임차료", "사무실": "임차료", "충북음성": "임차료",
    "숙소보증금": "임차보증금", "잡급": "잡급",
    "대출원금": "장기차입금", "법인대출": "장기차입금",
    "건설표준시험원": "지급수수료", "기장대행": "지급수수료", "기타지급수수료": "지급수수료",
    "변호사": "지급수수료", "비즈메카": "지급수수료", "삼성탑": "지급수수료",
    "시험의뢰비": "지급수수료", "엘리베이트": "지급수수료", "지게차": "지급수수료",
    "택배착불": "지급수수료", "팀오피스": "지급수수료", "폐기물": "지급수수료",
    "홈페이지": "지급수수료", "덕이동건축관련": "지급수수료", "문자": "지급수수료",
    "본원": "지급수수료", "세금계산서": "지급수수료", "세종안전": "지급수수료",
    "지원": "지급수수료", "팀별": "지급수수료", "하수관거": "지급수수료",
    "기타차량유지비": "차량유지비", "도로통행료": "차량유지비", "주유": "차량유지비",
    "주차비": "차량유지비", "차량수리": "차량유지비", "출장비": "차량유지비",
    "기타통신비": "통신비", "사무실전화": "통신비", "우편요금": "통신비", "인터넷": "통신비", "휴대폰": "통신비",
    "퇴직소득": "퇴직소득세", "퇴직연금": "퇴직연금", "퇴직연금운용관리": "퇴직연금운용관리",
    "예비비": "현금", "카드결재": "미지급금 정산"
}

# 영역별 계정과목 목록 정의
SALES_ACCOUNTS = ["국고보조금", "용역매출"]
COST_ACCOUNTS = [
    "급여", "퇴직급여", "퇴직연금운용관리", "건강보험", "고용보험", "국민연금", "산재보험", "교육훈련비",
    "수도광열비", "기타수도광열비", "임차료", "무인경비", "보험료", "차량유지비",
    "소모품비", "사무용품비", "수선비", "지급수수료", "복리후생비", "통신비", "도서인쇄비",
    "여비교통비", "업무추진비", "운반비", "이자비용", "잡비", "잡급"
]
OTHER_ACCOUNTS = ["기타영업외수익", "이자수익", "임대료", "이자비용"]
TAX_ACCOUNTS = ["세금과공과", "법인세비용"]

# 섹션별 표 생성 도우미 함수
def make_section_df(raw_pivot, acc_list, sum_label):
    section_pivot = raw_pivot.reindex(acc_list).fillna(0)
    sum_row = pd.DataFrame([section_pivot.sum()], index=[f"📌 {sum_label}"])
    df_combined = pd.concat([section_pivot, sum_row])
    return df_combined

# 정교한 행/글자 스타일링 함수 (소계 배경색 및 폰트 차별화)
def style_table(df):
    def apply_cell_style(row):
        is_subtotal = "📌" in str(row.name)  # 소계 행 여부 판단
        styles = []
        
        for val in row:
            css = ""
            # 1. 소계 행 스타일 (연한 회색 배경 + 크고 굵은 글씨)
            if is_subtotal:
                css += "background-color: #F0F2F6; font-weight: bold; font-size: 15px; "
            else:
                css += "font-weight: normal; font-size: 14px; "
            
            # 2. 양수(파랑)/음수(빨강) 색상 지정
            if isinstance(val, (int, float)):
                if val > 0:
                    css += "color: #1E88E5;"
                elif val < 0:
                    css += "color: #E53935;"
            
            styles.append(css)
        return styles

    return df.style.format("{:,.0f}").apply(apply_cell_style, axis=1)

if st.sidebar.button("데이터 불러오기 및 손익계산서 생성"):
    with st.spinner("MS SQL 데이터 수집 및 정밀 분리 중..."):
        df = fetch_account_data(selected_year)
        
        if df.empty:
            st.warning(f"{selected_year}년도 데이터가 없습니다.")
        else:
            df['month'] = df['day'].apply(lambda x: f"{int(str(x)[4:6])}월" if len(str(x)) >= 6 else "1월")
            df['amount'] = df['deposit'].fillna(0) - df['withdrawal'].fillna(0)
            
            # 매핑 처리
            df['subgroup_clean'] = df['subgroup'].astype(str).str.strip()
            df['account'] = df['subgroup_clean'].map(SUBGROUP_MAP).fillna("⚠️ 미분류")
            
            # 피벗 생성 및 1월~12월 순서 고정
            raw_pivot = df.pivot_table(index='account', columns='month', values='amount', aggfunc='sum', fill_value=0)
            months = [f"{i}월" for i in range(1, 13)]
            for m in months:
                if m not in raw_pivot.columns:
                    raw_pivot[m] = 0
            raw_pivot = raw_pivot[months]

            # ---------------------------------------------------------
            # 데이터 및 스타일링 출력
            # ---------------------------------------------------------
            st.subheader(f"📌 {selected_year}년 정식 손익계산서")

            # 1. 매출액
            st.markdown("#### 1. 매출액 (수입 계정)")
            sales_df = make_section_df(raw_pivot, SALES_ACCOUNTS, "소계(총매출액)")
            st.dataframe(style_table(sales_df), width='stretch')
            st.markdown("---")

            # 2. 매출원가
            st.markdown("#### 2. 매출원가 및 영업비용 (지출 계정)")
            cost_df = make_section_df(raw_pivot, COST_ACCOUNTS, "소계(총영업비용)")
            st.dataframe(style_table(cost_df), width='stretch')
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
            st.dataframe(style_table(summary_df), width='stretch')
            st.markdown("---")

            # 4. 영업외손익
            st.markdown("#### 4. 영업외손익 (본업 외)")
            other_df = make_section_df(raw_pivot, OTHER_ACCOUNTS, "소계(영업외손익)")
            st.dataframe(style_table(other_df), width='stretch')
            st.markdown("---")

            # 5. 세금 및 기타
            st.markdown("#### 5. 세금 및 기타 항목")
            tax_df = make_section_df(raw_pivot, TAX_ACCOUNTS, "소계(세금항목)")
            st.dataframe(style_table(tax_df), width='stretch')
            st.markdown("---")

            # 미매핑 소그룹 체크
            unmapped_df = df[df['account'] == "⚠️ 미분류"]
            if not unmapped_df.empty:
                st.subheader("⚠️ 매핑표에 없는 소그룹(subgroup) 내역")
                st.info("아래 소그룹들은 매핑표에 포함되지 않았습니다. 매핑표에 추가하시면 해당 카테고리로 자동 집계됩니다.")
                unmapped_summary = unmapped_df.groupby('subgroup_clean').agg(
                    건수=('day', 'count'),
                    총금액=('amount', 'sum'),
                    주요거래처=('where', lambda x: ', '.join(x.dropna().astype(str).unique()[:3]))
                ).reset_index()
                st.dataframe(unmapped_summary.style.format({'총금액': '{:,.0f}'}), width='stretch')

else:
    st.info("왼쪽 사이드바에서 연도를 선택한 후 [데이터 불러오기] 버튼을 눌러주세요.")