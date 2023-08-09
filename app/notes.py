from flask import Blueprint, session
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from app.db import get_db
from auth.decorators import requires_auth

bp = Blueprint("notes", __name__)


@bp.route("/")
def index():
    """Show all the notes, most recent first."""
    db = get_db()
    notes = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM notes p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("notes/index.html", notes=notes)


def get_post(id, check_author=True):
    """Get a notes and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of notes to get
    :param check_author: require the current user to be the author
    :return: the notes with author information
    :raise 404: if a notes with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    notes = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM notes p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if notes is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and notes["author_id"] != g.user["id"]:
        abort(403)

    return notes


@bp.route("/create", methods=("GET", "POST"))
@requires_auth
def create():
    """Create a new notes for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        author_id = "1234"

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO notes (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, author_id),
            )
            db.commit()
            return redirect(url_for("notes.index"))

    return render_template("notes/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@requires_auth
def update(id):
    """Update a notes if the current user is the author."""
    notes = get_post(id)

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
                "UPDATE notes SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("notes.index"))

    return render_template("notes/update.html", notes=notes)


@bp.route("/<int:id>/delete", methods=("POST",))
@requires_auth
def delete(id):
    """Delete a notes.

    Ensures that the notes exists and that the logged in user is the
    author of the notes.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("notes.index"))