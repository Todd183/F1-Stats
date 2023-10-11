from flask import Blueprint, render_template,request,flash,  redirect,url_for
from flask_login import login_required, current_user
from .models import Transaction
from . import db
from flask_login import login_required, current_user
from datetime import datetime

transaction = Blueprint('transaction', __name__)

@transaction.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        type = request.form.get('type')
        date = datetime.strptime(request.form.get('date'),"%Y-%m-%d").date()

        new_transaction = Transaction(description=description, amount=amount, category=category, type=type, date = date, user_id = current_user.id)

        db.session.add(new_transaction)
        db.session.commit()

        flash('Transaction added successfully', 'success')
        return redirect(url_for('transaction.add_transaction'))

    return render_template('add_transaction.html',user = current_user)