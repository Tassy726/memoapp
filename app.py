import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Memo


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # ---- DB設定（Render では DATABASE_URL を使用、なければ SQLite）----
    database_url = os.getenv("DATABASE_URL")  # 例: postgresql://user:pass@host:5432/dbname
    if database_url:
        # 万一 'postgres://' で来た場合は 'postgresql://' に置換（互換対応）
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memo.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # ---------------------------------------------------------------

    db.init_app(app)

    # 初回起動時にテーブル作成
    with app.app_context():
        db.create_all()

    # 一覧
    @app.route("/")
    def index():
        memos = Memo.query.order_by(Memo.updated_at.desc()).all()
        return render_template("index.html", memos=memos)

    # 作成
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

    # 詳細
    @app.route("/memo/<int:memo_id>")
    def show_memo(memo_id):
        memo = Memo.query.get_or_404(memo_id)
        return render_template("show.html", memo=memo)

    # 編集
    @app.route("/memo/<int:memo_id>/edit", methods=["GET", "POST"])
    def edit_memo(memo_id):
        memo = Memo.query.get_or_404(memo_id)

        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()

            if not title or not body:
                flash("タイトルと本文は必須です。", "error")
                return render_template("edit.html", memo=memo, title=title, body=body)

            memo.title = title
            memo.body = body
            db.session.commit()
            flash("メモを更新しました。", "success")
            return redirect(url_for("show_memo", memo_id=memo.id))

        # GET
        return render_template("edit.html", memo=memo, title=memo.title, body=memo.body)

    # 削除（POST専用）
    @app.route("/memo/<int:memo_id>/delete", methods=["POST"])
    def delete_memo(memo_id):
        memo = Memo.query.get_or_404(memo_id)
        db.session.delete(memo)
        db.session.commit()
        flash("メモを削除しました。", "success")
        return redirect(url_for("index"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
