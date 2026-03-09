from flask import Blueprint, render_template

bp = Blueprint('progress', __name__)


@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
