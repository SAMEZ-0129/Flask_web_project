from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flaskext.markdown import Markdown
import config # config.py 파일
from flask_socketio import SocketIO

# app = Flask(__name__) # 이 부분은 플라스크 어플리케이션을 생성하는 부분이다. 
#                         # __name__ 이라는 변수에는 모듈명이 담긴다. 즉, 이 파일이 실행되면 pybo.py라는 모듈이 실행되므로 __name__에는 pybo라는 문자열이 담긴다.

# @app.route('/') # app.route는 지정된 주소에 접속하면 바로 다음 줄에 있는 함수를 실행시키는 '플라스크 데코레이터' 이다.
# def hello_world():
#     return "Hello, world"

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
socketio = SocketIO()

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()

def create_app(): # create_app 함수가 app 객체를 생성하고 반환 (애플리케이션 팩토리)
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM (Object Relation Mapping)
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app,db)
    from . import models # models.py 참조

    # 소켓 초기화
    socketio.init_app(app)

    # Blueprint
    from .views import main_views, question_views, answer_views, auth_views, comment_views, vote_views,sheet_views # question_views 파일에 등록한 블루프린트 적용
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(comment_views.bp)
    app.register_blueprint(vote_views.bp)
    app.register_blueprint(sheet_views.bp)

    # 작성일자 표기 filter
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime # datetime 이름으로 필터를 등록함

    # Markdown
    '''pip install Flask-Markdown으로 설치한 후 실행해보면 오류가 발생함. 기존 Markup이 deprecated 상태이기 때문.
    C>venvs>프로젝트명>Lib>site-packages>flaskext 파일에서 markdown.py 파일을 수정
    from flask import Markup 을 from markupsafe import Markup 으로 수정 후 저장하면 정상 작동.'''
    Markdown(app, extentions=['nl2br','fenced_code'])

    return app