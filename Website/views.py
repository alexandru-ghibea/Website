from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, File
from . import db
import json
import os
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
            email_folder = os.path.join("Website", "static", "uploads", email)
            if not os.path.exists(email_folder):
                flash("Something went wrong")
            file_path = os.path.join(email_folder, file.filename)
            file.save(file_path)
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
        caption = f"<caption>{filename}</caption>"
        return render_template("content.html", user=current_user, tables=[caption + account_details.to_html(classes="table table-bordered text-center", index=False)], user_id=current_user, csv_file=csv_file, titles=account_details.columns.values)
    if filename == "Profiles.csv":
        profiles = pd.read_csv(file_path).drop(columns=['Email Address', 'Game Handle', 'Primary Lang', 'Has Auto Playback',
                                                        'Max Stream Quality', 'Profile Lock Enabled', 'Profile Transferred',
                                                        'Profile Transfer Time', 'Profile Transferred From Account',
                                                        'Profile Transferred To Account', 'Date Of Birth', 'Gender', 'Opt-Out'])
        caption = f"<caption>{filename}</caption>"
        return render_template("content.html", user=current_user, tables=[caption + profiles.to_html(classes="table table-bordered text-center", index=False)], user_id=current_user, csv_file=csv_file, titles=profiles.columns.values)
    if filename == "BillingHistory.csv":
        billing = pd.read_csv(file_path).drop(columns=['Mop Creation Date', 'Mop Pmt Processor Desc',
                                                       'Pmt Txn Type', "Description", "Pmt Status", "Mop Last 4", "Tax Amt", "Gross Sale Amt"]).dropna()
        total_amount = billing.groupby(["Payment Type", "Currency"])[
            "Item Price Amt"].sum().reset_index()  # convert to data frame so we can make it to html format
        # Add a new row for the total amount of each currency
        total_amount_sum = total_amount.groupby(
            "Currency")["Item Price Amt"].sum()
        total_row = pd.DataFrame(
            {"Payment Type": "Total Payments", "Currency": total_amount_sum.index, "Item Price Amt": total_amount_sum.values})
        total_amount = total_amount.append(total_row)
        total_amount = total_amount.rename(
            columns={"Item Price Amt": "Total Amount"})
        caption = f"<caption>{filename}</caption>"

        # Create a DataFrame with the start and end dates
        first_payment = billing["Transaction Date"].min()
        last_payment = billing["Transaction Date"].max()
        payments = pd.DataFrame({"Payment Type": [
                                "First Payment", "Last Payment"], "Transaction Date": [first_payment, last_payment]})

        return render_template("content.html", user=current_user, tables=[caption + total_amount.to_html(classes="table table-bordered text-center", index=False) + payments.to_html(classes="table table-bordered text-center", index=False)], user_id=current_user, csv_file=csv_file, titles=["", ""])
        # return render_template("content.html", user=current_user, tables=[caption + total_amount.to_html(classes="table table-bordered text-center", index=False)], user_id=current_user, csv_file=csv_file, titles=billing.columns.values)

    return "Not Implemented", 404
