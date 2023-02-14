from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, send_file
from flask_login import login_required, current_user
from .models import Note, File
from . import db
import json
import os
import io
import csv
import pandas as pd
from IPython.display import display
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
            email_folder = f"Website/static/uploads/{email}"
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
    csv_file = File.query.filter_by(user_id=current_user.id)
    return render_template("data_analytics.html", user=current_user, csv_file=csv_file)


@views.route("/content", methods=["GET", "POST"])
def see_content():
    csv_file = File.query.filter_by(user_id=current_user.id)
    filename = request.args.get('filename')
    file_path = f"Website/static/uploads/{current_user.email}/{filename}"
    if filename == "AccountDetails.csv":
        account_details = pd.read_csv(file_path)
        account_details = account_details.drop(columns=['First Name', 'Last Name', 'Email Address', 'Phone Number', 'Cookie Disclosure', 'Netflix Updates',
                                                        'Now On Netflix', 'Netflix Offers', 'Netflix Surveys',
                                                        'Netflix Kids And Family', 'Sms Account Related',
                                                        'Sms Content Updates And Special Offers', 'Test Participation',
                                                        'Marketing Communications Matched Identifiers', 'Extra Member Account',
                                                        'Extra Member Primary Account Owner'])
        return render_template("content.html", user=current_user, tables=[account_details.to_html(classes="data")], user_id=current_user, csv_file=csv_file, titles=account_details.columns.values)
    if filename == "Profiles.csv":
        profiles = pd.read_csv(file_path).drop(columns=['Email Address', 'Game Handle', 'Primary Lang', 'Has Auto Playback',
                                                        'Max Stream Quality', 'Profile Lock Enabled', 'Profile Transferred',
                                                        'Profile Transfer Time', 'Profile Transferred From Account',
                                                        'Profile Transferred To Account', 'Date Of Birth', 'Gender', 'Opt-Out'])
        return render_template("content.html", user=current_user, tables=[profiles.to_html(classes="data")], user_id=current_user, csv_file=csv_file, titles=profiles.columns.values)

    return "404 File not found", 404
