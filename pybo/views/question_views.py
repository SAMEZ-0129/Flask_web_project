from flask import Blueprint, render_template, request, url_for, g, flash
from pybo.models import Question, Answer,User                # 구현한 모델 DB 중 Question 호출
from .. forms import QuestionForm, AnswerForm
from datetime import datetime
from werkzeug.utils import redirect
from pybo import db
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')
# html파일에서 함수를 불러올 때 사용하는 블루프린트 클래스 이름이 question임
# question.detail, question._list, question.create와 같이 사용되는 것

# 질문 상세 페이지 불러오기 블루프린트
@bp.route('/detail/<int:question_id>/') # Question 모델 중 id값에 해당하는 질문을 불러오는 매핑 규칙 (ex. /detail/2 로 요청하면 question_id 매개변수에 2가 전달)
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id) # 요청할 Question 쿼리를 question 변수에 선언
    return render_template('question/question_detail.html', question=question, form=form) # render_template 함수로 질문 상세 html파일에 지정한 question 전달
    # question_detail.html 파일에 보고싶은 Question에 해당하는 DB가 전달되는 것 (question_detail.html 파일에서 계속)

# 질문 목록 조회를 위한 블루프린트
# @bp.route('/list/')     
# def _list(): # 참고: _list로 변수명 선언한 이유는 list는 파이썬 기본 예약어기 때문
#     page = request.args.get('page', type=int, default=1) # GET 방식으로 요청한 ULR에서 page 값을 가져옴
#     question_list = Question.query.order_by(Question.create_date.desc())
#     question_list = question_list.paginate(page=page, per_page=10) # page값이 없으면 1, 있으면 해당 페이지로 조회하고 페이지당 질문 10개 노출
#     return render_template('question/question_list.html', question_list = question_list)
@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    # 페이징
    question_list = question_list.paginate(page=page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

# 질문 생성을 위한 블루프린트
@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm() # form 객체 생성
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject = form.subject.data, content = form.content.data, create_date = datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)

# 질문 수정을 위한 블루프린트
@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

# 질문 삭제를 위한 블루프린트
@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))