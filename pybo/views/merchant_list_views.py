from flask import Blueprint, render_template, request, redirect, flash
from datetime import datetime, date
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os, io, base64
import matplotlib.font_manager as fm
import openpyxl

bp = Blueprint('merchant', __name__, url_prefix='/merchant')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
plt.rc('axes', unicode_minus=False)

def create_separated_category_chart(monthly_counts):
    # 한글 폰트 설정
    font_path = "C:/NanumGothic.ttf"  # 폰트 경로
    font_prop = fm.FontProperties(fname=font_path, size=12)
    plt.rc('font', family=font_prop.get_name())

    # 서브플롯 설정
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 독립몰 그래프
    ax1.bar(monthly_counts.index.astype(str), monthly_counts['독립몰'], label='독립몰', color='b', alpha=0.7)
    ax1.set_title('월별 독립몰 건수')
    ax1.set_xlabel('월')
    ax1.set_ylabel('건수')
    ax1.legend()
    ax1.set_xticklabels(monthly_counts.index.astype(str), rotation=45, ha='right')  # x축 레이블 기울이기

    # 그 외 그래프
    ax2.bar(monthly_counts.index.astype(str), monthly_counts['그 외'], label='호스팅사', color='g', alpha=0.7)
    ax2.set_title('월별 호스팅사 건수')
    ax2.set_xlabel('월')
    ax2.set_ylabel('건수')
    ax2.legend()
    ax2.set_xticklabels(monthly_counts.index.astype(str), rotation=45, ha='right')  # x축 레이블 기울이기

    # 그래프를 이미지로 변환
    buf = io.BytesIO()
    plt.tight_layout()  # 레이아웃 조정
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def read_filtered_data(file_path, filter_column, filter_value):
    # 엑셀 파일 열기
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active

    # 헤더 추출
    headers = [cell.value for cell in sheet[1]]

    # 필터가 적용된 데이터 읽기
    filtered_data = []
    for row in sheet.iter_rows(min_row=2):  # 첫 번째 행은 헤더로 가정
        # 필터 조건에 따라 원하는 데이터를 추가
        if row[filter_column].value == filter_value:  # filter_column 인덱스에 해당하는 값 체크
            filtered_data.append([cell.value for cell in row])

    # 결과를 Pandas DataFrame으로 변환
    df = pd.DataFrame(filtered_data, columns=headers)
    return df

@bp.route('/list', methods=['GET', 'POST'])
def merchant_list():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('파일이 없습니다.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('파일을 선택하세요.')
            return redirect(request.url)

        # 데이터 처리
        try:
            # 첫 번째 행을 헤더로 설정
            data = pd.read_excel(file, header=0)
            # 전체 행과 열 수를 출력하도록 설정
            pd.set_option('display.max_rows', None)  # 모든 행 표시
            pd.set_option('display.max_columns', None)  # 모든 열 표시
            # 열 이름 출력 및 확인
            print(data[data['오픈일시'].dt.to_period('M') == '2024-06'])  # 2024년 6월 데이터 확인
            print(data.columns)
            # print(data.info())
            
            # 공백 제거
            data.columns = data.columns.str.strip()
            
            # '오픈일시' 열을 날짜 형식으로 변환
            if '오픈일시' in data.columns:
                data['오픈일시'] = pd.to_datetime(data['오픈일시'], errors='coerce')
                if data['오픈일시'].isnull().all():
                    flash("오픈일시 열의 데이터 형식이 잘못되었습니다.")
                    return redirect(request.url)
            else:
                flash("'오픈일시' 열이 데이터에 없습니다.")
                return redirect(request.url)

            # 월별 집계
            data['월'] = data['오픈일시'].dt.to_period('M')
            independent_counts = data[data['호스팅사'] == '독립몰'].groupby('월').size()
            non_independent_counts = data[data['호스팅사'] != '독립몰'].groupby('월').size()

            # 모든 월을 포함하도록 결합
            monthly_counts = pd.DataFrame({
                '독립몰': independent_counts.reindex(non_independent_counts.index.union(independent_counts.index), fill_value=0),
                '그 외': non_independent_counts.reindex(non_independent_counts.index.union(independent_counts.index), fill_value=0)
            })

            # 인덱스를 정렬
            monthly_counts = monthly_counts.sort_index()


             # 상반기와 하반기 건수 집계
            first_half = monthly_counts.loc[monthly_counts.index <= '2024-06']
            second_half = monthly_counts.loc[monthly_counts.index > '2024-06']

            first_half_total = first_half.sum()
            second_half_total = second_half.sum()

            # 증가/감소 계산
            independent_change = second_half_total['독립몰'] - first_half_total['독립몰']
            non_independent_change = second_half_total['그 외'] - first_half_total['그 외']

            independent_percentage = (independent_change / first_half_total['독립몰'] * 100) if first_half_total['독립몰'] > 0 else float('inf')
            non_independent_percentage = (non_independent_change / first_half_total['그 외'] * 100) if first_half_total['그 외'] > 0 else float('inf')


            # 그래프 생성
            monthly_category_chart = create_separated_category_chart(monthly_counts)



            # 그래프 생성
            monthly_category_chart = create_separated_category_chart(monthly_counts)

            # '독립몰' 카테고리 데이터 수
            independent_count = data[data['호스팅사'] == '독립몰'].shape[0]

            # '독립몰'이 아닌 모든 데이터 수
            non_independent_count = data[data['호스팅사'] != '독립몰'].shape[0]

            # 현재 날짜 기준 월 설정
            current_date = datetime.now()
            current_month = current_date.strftime('%Y년 %m월')  # "2024년 10월" 형식으로

            return render_template('open_merchant/merchant_list.html',
                                   current_month=current_month,
                                   independent_count=independent_count,
                                   non_independent_count=non_independent_count,
                                   monthly_category_chart=monthly_category_chart,
                                   independent_change=independent_change,
                                   non_independent_change=non_independent_change,
                                   independent_percentage=independent_percentage,
                                   non_independent_percentage=non_independent_percentage,
                                   first_half_total=first_half_total,
                                   second_half_total=second_half_total)
        except Exception as e:
            flash(f'데이터 처리 중 오류가 발생했습니다: {e}')
            return redirect(request.url)
    
    return render_template('open_merchant/merchant_list.html', current_month=None,
                                   independent_count=None,
                                   non_independent_count=None,
                                   monthly_category_chart=None,
                                   independent_change=None,
                                   non_independent_change=None,
                                   independent_percentage=None,
                                   non_independent_percentage=None,
                                   first_half_total=None,
                                   second_half_total=None)