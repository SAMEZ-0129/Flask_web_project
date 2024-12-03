from pybo import db

# 추천 기능 모델 (N:N 관계의 테이블 객체)
question_voter = db.Table(
    'question_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)
answer_voter = db.Table(
    'answer_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)

## 질문 DB 모델
class Question(db.Model): # db.Model을 상속받음
    id = db.Column(db.Integer, primary_key=True)        # 질문 고유번호
    subject = db.Column(db.String(200), nullable=False) # 제목
    content = db.Column(db.Text(), nullable=False)      # 내용
    create_date = db.Column(db.DateTime(), nullable=False)# 작성일시
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) # User 모델과 Question 모델 연결
    user = db.relationship('User', backref=db.backref('question_set')) # Question 모델에서 User 모델 참조
    modify_date = db.Column(db.DateTime(), nullable=True) # 수정이 발생하면 발생시각 저장
    voter = db.relationship('User', secondary=question_voter, backref=db.backref('question_voter_set'))
    # 각 속성은 db.Column 클래스로 생성

# 답변 DB 모델 
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 질문 모델과 답변을 연결하기 위함. 이처럼 어떠한 속성을 가진 기존 모델과 연결하기 위해 ForeignKey를 사용함
    # question.id가 연결할 모델이고 ondelete='CASCADE'는 삭제 연동(질문이 삭제되면 연결된 답변도 DB에서 삭제됨> 실제로 삭제되는 것은 아니고 question.id 값만 빈값으로 업데이트됨)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id',ondelete='CASCADE')) 
    question = db.relationship('Question',backref=db.backref('answer_set', cascade='all,delete-orphan')) # 답변 모델에서 질문을 참조하기 위해 활용
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('answer_set'))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=answer_voter, backref=db.backref('answer_voter_set'))

# 회원가입을 위한 회원 정보
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # unique는 같은 값을 저장할 수 없게 해줌.
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# 코멘트 모델
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comment_set'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=True)
    question = db.relationship('Question', backref=db.backref('comment_set'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), nullable=True)
    answer = db.relationship('Answer', backref=db.backref('comment_set'))
    

class Sheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('sheets'))