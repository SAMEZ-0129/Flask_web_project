from datetime import datetime
from flask import Blueprint, render_template
from flask_socketio import SocketIO, emit
from pybo.views.auth_views import login_required


bp = Blueprint('sheet', __name__, url_prefix='/sheet')
socketio = SocketIO()

@bp.route('/collaborative')
@login_required
def collaborative_sheet():
    current_date = datetime.now()
    return render_template('sheet/collaborative.html', current_date=current_date)

@socketio.on('cell_update')
def handle_cell_update(data):
    emit('cell_updated', data, broadcast=True)

@bp.route('/save', methods=['POST'])
@login_required
def save_sheet():
    try:
        data = request.json
        sheet_data = data.get('sheetData')
        
        # 여기에 데이터베이스 저장 로직 추가
        # 예: Sheet 모델을 만들어서 저장
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})