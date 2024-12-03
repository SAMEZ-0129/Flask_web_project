# 회원가입 뷰
from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
import functools

from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User

# auth라는 접두어로 시작하는 URL 호출 시 본 파일의 함수 호출
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=('GET', 'POST'))
# 회원가입을 위한 블루프린트
def signup():
    # forms.py에서 우리가 구현한 회원가입 폼을 불러와서 form 변수에 생성
    form = UserCreateForm() 
    # 전송 방식이 POST이고 작성된 폼을 제출할 경우
    if request.method == 'POST' and form.validate_on_submit():
        # 입력한 username을 조회해서 이미 등록된 계정인지 검증
        user = User.query.filter_by(username=form.username.data).first()
        # 기존 사용자가 아니면
        if not user:
            # 사용자 이름, 비밀번호, 이메일 정보를 mdoels.py에서 만든 User 모델에 적용해서 user 변수에 저장. (비밀번호는 암호화해서 저장)
            # generate_password_hash 방식은 pbkdf2-sha256 알고리즘을 사용
            user = User(username=form.username.data,password = generate_password_hash(form.password1.data), email = form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        # 이미 존재하는 계정이면 얼럿 노출
        else:
            flash("이미 존재하는 계정입니다.")
    return render_template('auth/signup.html', form=form)

# 사용자 로그인
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = '존재하지 않는 사용자입니다.'
        elif not check_password_hash(user.password , form.password.data):
            error = '비밀번호가 올바르지 않습니다.'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            # 로그인 후 보려던 페이지로 이동 or 첫페이지 이동
            _next = request.args.get('next', '') 
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

# 사용자 로그인 상태 검증
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

# 로그인 필요한 경우 로그인 화면으로 이동
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("로그인이 필요합니다!", "warning")
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view

# 사용자 로그아웃
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
