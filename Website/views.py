from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, File
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        note = request.form.get("notes")
        file = request.files.get("csv_file")
        if len(note) < 1:
            flash("Note is to short", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            uploaded = File(data=file.filename, user_id=current_user.id)
            db.session.add(new_note)
            db.session.add(uploaded)
            db.session.commit()
            flash("Note added!", category="success")
    return render_template('home.html', user=current_user)


@views.route('/delete-note', methods=["POST"])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
