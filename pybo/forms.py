from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 게시물 작성 폼
class QuestionForm(FlaskForm): # Flask-WTF 모듈의 FlaskForm 클래스를 상속받음 > subject,content 속성 포함하고 있음
    subject = StringField('제목', validators=[DataRequired('제목은 필수 입력 항목입니다.')]) # 글자수에 제한이 있음 > StringField. 첫번째 인자는 폼 lable로 사용되며, 두 번째 인자는 검증할 때 사용하는 도구
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다.')]) # 글자수에 제한이 없음 > TextAreaField
    # validators에서 DataRequired는 필수항목인지 확인, Email은 이메일인지 점검, Length는 길이 점검 (복수 사용 가능). 추가 내용은 플라스크 필드 공식문서 참고

# 댓글 작성 폼
class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다.')])

# 계정 생성 폼
class UserCreateForm(FlaskForm): 
    username = StringField('사용자이름', validators=[DataRequired('이름을 작성해주세요.'), Length(min=3, max=25)])
    # equalto 옵션을 통해 비밀번호 확인과 동일한지 검증
    password1 = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 작성해주세요.'), EqualTo('password2', '비밀번호와 비밀번호 확인이 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호를 작성해주세요.')])
    # Email 옵션을 통해 이메일 형식인지 검증
    email = EmailField('이메일', validators=[DataRequired('이메일을 작성해주세요.'), Email()])

# 로그인 폼
class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired('아이디를 입력해주세요.'), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 입력해주세요.')])

# 댓글 폼
class CommentForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용을 작성해주세요.')])