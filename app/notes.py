from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint("notes", __name__)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
    if not title:
        error = "Title is required."
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            "INSERT INTO notes (title, body, author_id)" " VALUES (?, ?, ?)",
            (title, body, g.user["id"]),
        )
        db.commit()
        return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_note(id, check_author=True):
    note = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM notes p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if note is None:
        abort(404, f"Note id {id} doesn't exist.")

    if check_author and note["author_id"] != g.user["id"]:
        abort(403)

    return note

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_note(id)
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE notes SET title = ?, body = ?" " WHERE id = ?", (title, body, id)
            )
        db.commit()
        return redirect(url_for("notes.index.html"))
    return render_template("notes/update.html", post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_note(id)
    db = get_db()
    db.execute('DELETE FROM notes WHERE is = ?', (id))
    db.commit()
    return redirect(url_for('notes.index'))