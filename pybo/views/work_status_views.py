from flask import Blueprint, render_template, request, redirect, flash
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

bp = Blueprint('work_status', __name__, url_prefix='/work_status')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_work_analysis_chart(monthly_work_counts):
    plt.figure(figsize=(10, 5))

    # BAU와 서비스광장 처리 건수를 함께 표시
    bar_width = 0.35
    index = range(len(monthly_work_counts))

    # BAU 데이터 바 그래프
    plt.bar(index, monthly_work_counts['BAU'], bar_width, label='BAU', color='skyblue')

    # 서비스광장 처리 데이터 바 그래프 (BAU 오른쪽에 배치)
    plt.bar([i + bar_width for i in index], monthly_work_counts['서비스광장 처리'], bar_width, label='서비스광장 처리', color='lightgreen')

    # 그래프 제목 및 레이블 설정
    plt.title('월별 BAU 및 서비스광장 처리 건수')
    plt.xlabel('연/월')
    plt.ylabel('건수')
    plt.xticks([i + bar_width / 2 for i in index], monthly_work_counts['연/월'].dt.strftime('%Y-%m'), rotation=45)
    
    plt.legend()
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


@bp.route('/list', methods=['GET', 'POST'])
def work_status_list():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('파일이 없습니다.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('파일을 선택하세요.')
            return redirect(request.url)

        try:
            # 엑셀 파일을 메모리에서 읽기
            data = pd.read_excel(file, header=0)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            # '연/월' 열을 날짜 형식으로 변환
            if '연/월' in data.columns:
                data['연/월'] = pd.to_datetime(data['연/월'], format='%Y-%m', errors='coerce')
                if data['연/월'].isnull().all():  # 전체가 NaN인 경우
                    flash("연/월 열의 데이터 형식이 잘못되었습니다.")
                    return redirect(request.url)
            else:
                flash("'연/월' 열이 데이터에 없습니다.")
                return redirect(request.url)

            # BAU 및 서비스광장 처리 건수 집계
            if 'BAU(네이버요청건+가맹점요청건)' in data.columns:
                data['BAU'] = data['BAU(네이버요청건+가맹점요청건)'].fillna(0)
                if data['BAU'].isnull().any():  # NaN이 하나라도 있는 경우
                    flash("BAU 열에 NaN 값이 포함되어 있습니다.")
                    return redirect(request.url)
            else:
                flash("'BAU(네이버요청건+가맹점요청건)' 열이 데이터에 없습니다.")
                return redirect(request.url)

            if '서비스광장 처리' in data.columns:
                data['서비스광장 처리'] = data['서비스광장 처리'].fillna(0)
            else:
                flash("'서비스광장 처리' 열이 데이터에 없습니다.")
                return redirect(request.url)

            # '연/월' 기준으로 BAU와 서비스광장 처리 건수 집계
            monthly_work_summary = data.groupby(data['연/월'].dt.to_period('M')).agg({
                'BAU': 'sum',
                '서비스광장 처리': 'sum'
            }).reset_index()

            monthly_work_summary['연/월'] = monthly_work_summary['연/월'].dt.to_timestamp()  # Period를 Timestamp로 변환

            # 그래프 생성
            work_analysis_chart = create_work_analysis_chart(monthly_work_summary)

            return render_template('open_merchant/work_status_list.html',
                                   work_analysis_chart=work_analysis_chart,
                                   monthly_work_summary=monthly_work_summary)
        except Exception as e:
            flash(f'데이터 처리 중 오류가 발생했습니다: {e}')
            return redirect(request.url)

    return render_template('open_merchant/work_status_list.html', work_analysis_chart=None)
