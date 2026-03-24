import os
import threading
from flask import Flask
from config import Config
from templates.admin.protect_data_admin import run_protected
import subprocess
import sys
_started = False
_started_lock = threading.Lock()


def start_background_once():
    global _started
    with _started_lock:
        if _started:
            return
        _started = True
        script_path = os.path.join(os.path.dirname(__file__), 'templates', 'admin', 'protect_data_admin.py')
        subprocess.Popen([sys.executable, script_path], 
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
       
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.scan_routes import scan_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.debug = True

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        start_background_once()

    app.run(debug=True, port=5000)