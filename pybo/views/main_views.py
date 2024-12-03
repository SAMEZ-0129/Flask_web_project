from flask import Blueprint, url_for
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/hello')
def hello_pybo():
    return "Helloooooo!"

# 시작화면
@bp.route('/')  
def index():
    return redirect(url_for('question._list')) # question_views에 _list의 URL로 리다이렉트
    # redirect는 입력받은 URL로 리다이렉트해주고, url_for는 rout가 설정된 함수명(_list)으로 URL을 역으로 찾아줌
    # > 최종적으로 위 방식은 /question/list/ URL로 이동함