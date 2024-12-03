import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db')) # 데이터베이스 접속 주소
SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLAlchemy의 이벤트를 처리하는 옵션 (지금 만드는 기능에는 불필요하여 비활성화)
SECRET_KEY='dev' # 실제로 키값을 사용할 때는 dev와 같은 임시값은 위험하다. 실 서비스 운영시에는 유추하기 어려운 문자열로 구현하는 것이 안전.
