from flask import Blueprint, jsonify
from app.extensions import db
from app.models.models import Solicitud

test_bp = Blueprint('test', __name__)

@test_bp.route('/test_solicitud')
def test_solicitud():
    try:
        # Try to query the Solicitud model
        count = db.session.query(Solicitud).count()
        return jsonify({
            'success': True,
            'message': f'Successfully queried Solicitud model. Count: {count}',
            'model_loaded': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error querying Solicitud model: {str(e)}',
            'model_loaded': False
        })
