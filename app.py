from flask import Flask
from database import init_db
from routes import main, learning, api, progress


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    init_db()

    app.register_blueprint(main.bp)
    app.register_blueprint(learning.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(progress.bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
