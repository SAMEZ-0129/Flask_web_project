# 템플릿 필터 구현

from datetime import datetime, timedelta

def format_datetime(question_datetime):
    # 현재 날짜
    current_time = datetime.now()
    # 올해의 시작 날짜
    start_of_year = datetime(current_time.year, 1, 1)
    # 어제 날짜
    yesterday = current_time - timedelta(days=1)

    # 질문의 작성일시가 오늘인지 어제인지 확인
    if question_datetime.date() == current_time.date():
        # 오늘 작성된 질문
        return question_datetime.strftime("%H:%M")
    elif question_datetime.year == current_time.year:
        # 올해 작성된 질문
        return question_datetime.strftime("%Y년 %m월 %d일 %H:%M")
    else:
        # 올해 이전에 작성된 질문
        return question_datetime.strftime("%Y년 %m월 %d일")
