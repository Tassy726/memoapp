# アプリ名：メモ帳アプリ
import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

app = create_app()

if __name__ == "__main__":
    # ローカル開発用
    app.run(debug=True)
