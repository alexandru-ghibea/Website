from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, File
from . import db
import json
import os
views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        note = request.form.get("notes")
        file = request.files.get("csv_file")
        email = current_user.email
        if len(note) < 1:
            flash("Note is to short", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            uploaded = File(data=file.filename, user_id=current_user.id)
            db.session.add(new_note)
            db.session.add(uploaded)
            db.session.commit()
            email_folder = f"user_folder/{email}"
            if not os.path.exists(email_folder):
                flash("Something went wrong")
            file.save(f"{email_folder}/{file.filename}")
            flash("Note and File uploaded!", category="success")
    return render_template('index.html', user=current_user)


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


@views.route('data_analytics', methods=["POST", "GET"])
def data_analytics():
    csv_file = File.query.all()
    return render_template("data_analytics.html", user=current_user, csv_file=csv_file)


@views.route('/file/<int:id>', methods=["GET"])
def view_file(id):
    file = File.query.get(id)
    return render_template("data_analytics.html", file=file, user=current_user)
