import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Memo


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # SQLite（開発用）
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memo.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # 初回起動時にテーブル作成
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        memos = Memo.query.order_by(Memo.updated_at.desc()).all()
        return render_template("index.html", memos=memos)

    # ----------------------
    # 新規メモ作成
    # ----------------------
    @app.route("/new", methods=["GET", "POST"])
    def new_memo():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()

            if not title or not body:
                flash("タイトルと本文は必須です。", "error")
                return render_template("new.html", title=title, body=body)

            memo = Memo(title=title, body=body)
            db.session.add(memo)
            db.session.commit()
            flash("メモを作成しました。", "success")
            return redirect(url_for("index"))

        return render_template("new.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
