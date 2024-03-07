from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Account, Transaction
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func
from datetime import datetime, date

transactions = Blueprint("transactions", __name__)

#create a new transaction for user with given user_id
@transactions.route("/create_transaction/<int:user_id>", methods=["GET"])
@login_required
def create_transaction(user_id):
    account = Account.query.filter_by(user_id=user_id).first()
    if not account:
        flash("Problem retrieving account associated with that user", category="error")
        return redirect(url_for("views.home"))

    #current day calculation logic
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    today_withdrawals = Transaction.query.filter(
        Transaction.account_id == account.id,
        Transaction.transaction_type == "withdraw",
        Transaction.created >= start_of_day,
        Transaction.created <= end_of_day,
    ).all()

    today_deposits = Transaction.query.filter(
        Transaction.account_id == account.id,
        Transaction.transaction_type == "deposit",
        Transaction.created >= start_of_day,
        Transaction.created <= end_of_day,
    ).all()

    total_withdrawn = sum(transaction.amount for transaction in today_withdrawals)
    total_deposited = sum(transaction.amount for transaction in today_deposits)

    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash("User details retireaval error", message="error")

    account_details = {
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "account_id": account.id,
        "amount": account.amount,
        "withdrawal_count": len(today_withdrawals),
        "withdrawal_amount": total_withdrawn,
        "deposit_count": len(today_deposits),
        "deposit_amount": total_deposited,
        "date": today,
    }
    if not account_details:
        flash("User has no such records at this time", category="message")
        return redirect(url_for("views.home"))

    return render_template(
        "transactions/create.html", account_details=account_details, user=current_user
    )


# complete user transaction creation
@transactions.route("/create_transaction", methods=["POST"])
@login_required
def complete_transaction():
    user_id = request.form.get("user_id")
    account_id = request.form.get("account_id")
    amount = request.form.get("amount")
    transaction_type = request.form.get("transaction_type")
    created = func.now()

    #validate deposit and withdraw requests
    valid_deposit_request = valid_deposit(account_id, transaction_type, amount)
    valid_withdrawal_request = valid_withdrawal(
            account_id, transaction_type, amount
        )

    #if validation for deposit or withdraw is successful
    if ((transaction_type == "deposit") and (valid_deposit_request == True)) or ((transaction_type == "withdraw") and (valid_withdrawal_request == True)):
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
        if not account:
            flash("Account retrieval error!", category="error")
            return redirect(url_for("views.home"))

        #update account balance
        update_main_account = update_account(account, amount, transaction_type)
        if update_main_account == True:
            try:
                new_transaction = Transaction(
                    account_id=account_id,
                    transaction_type=transaction_type,
                    amount=amount,
                    created=created,
                )
                db.session.add(new_transaction)
                db.session.commit()
                flash("Transaction created successfully", category="success")
                return redirect(url_for("transactions.view_transactions"))
            except Exception as e:
                db.session.rollback()
                flash("Error: ".str(e), category="error")
                return redirect(url_for("views.home"))
        else:
            flash("Updating Main Account Balance failed!", category="error")
            return redirect(url_for("views.home"))
    else:
        return redirect(url_for("views.home"))
    
  
# validate deposit
def valid_deposit(account_id, transaction_type, amount):
    deposit_max_limit_status = day_max_deposit_limit_reached(
        account_id, amount
    )
    deposit_max_frequency_status = day_max_deposit_frequency_reached(
        account_id
    )
    if transaction_type == "deposit":
        if int(amount) > 40000:
            flash("Max deposit is 40K!", category="error")
            return False
        elif deposit_max_limit_status == True:
            flash("Max daily deposit limit is 150K!", category="error")
            return False
        elif deposit_max_frequency_status == True:
            flash("Max deposit frequency limit reached!", category="error")
            return False
        else:
            return True
    else:
        return False


# validate withdrawal
def valid_withdrawal(account_id, transaction_type, amount):
    withdraw_max_limit_status = day_max_withdraw_limit_reached(
        account_id, amount
    )
    withdraw_max_frequency_status = day_max_withdraw_frequency_reached(
        account_id
    )

    if transaction_type == "withdraw":
        if int(amount) > 20000:
            flash("Max withdraw amount is 20K per transaction!", category="error")
            return False
        elif withdraw_max_limit_status == True:
            flash("Max daily withdraw limit is 50K!", category="error")
            return False
        elif withdraw_max_frequency_status == True:
            flash("Max withdraw frequency limit reached!", category="error")
            return False
        else:
            return True

    else:
        return False


# update main user account amount on withdrawal or deposit
def update_account(account, amount, transaction_type):
    try:
        if transaction_type == "deposit":
            account.amount += int(amount)
        elif transaction_type == "withdraw":
            if int(amount) > account.amount:
                flash("Insufficient funds", category="error")
                return False

            account.amount -= int(amount)
        else:
            return False

        account.updated = func.now()

        # db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash("Error: " + str(e), category="error")
        return False

# check if current day deposit amount limit is reached
def day_max_deposit_limit_reached(account_id, amount):
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    deposit_sum = (
        Transaction.query.filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == "deposit",
            Transaction.created >= start_of_day,
            Transaction.created <= end_of_day,
        )
        .with_entities(func.sum(Transaction.amount))
        .scalar()
    )

    if deposit_sum is not None and int(deposit_sum) + int(amount) > 150000:
        return True
    return False

# check if current day deposit frequency limit is reached
def day_max_deposit_frequency_reached(account_id):

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    deposit_count = Transaction.query.filter(
        Transaction.account_id == account_id,
        Transaction.transaction_type == "deposit",
        Transaction.created >= start_of_day,
        Transaction.created <= end_of_day,
    ).count()

    if int(deposit_count) >= 4:
        return True
    return False

# check if current day withdraw frequency limit is reached
def day_max_withdraw_frequency_reached(account_id):

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    withdraw_count = Transaction.query.filter(
        Transaction.account_id == account_id,
        Transaction.transaction_type == "withdraw",
        Transaction.created >= start_of_day,
        Transaction.created <= end_of_day,
    ).count()

    if int(withdraw_count) >= 3:
        return True
    return False

# check if current day withdraw amount limit is reached
def day_max_withdraw_limit_reached(account_id, amount):

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    withdraw_sum = (
        Transaction.query.filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == "withdraw",
            Transaction.created >= start_of_day,
            Transaction.created <= end_of_day,
        )
        .with_entities(func.sum(Transaction.amount))
        .scalar()
    )

    if withdraw_sum is not None and int(withdraw_sum) + int(amount) > 50000:
        return True
    return False

# return all completed transactions for all users
@transactions.route("/view_transactions/", methods=["GET"])
@login_required
def view_transactions():
    transactions_details = db.session.query(
        Transaction,
        Account.id.label('account_id'),
        Account.amount.label('account_amount'),
        User.first_name,
        User.last_name,
        User.email
    ).join(
        Account, Transaction.account_id == Account.id
    ).join(
        User, Account.user_id == User.id
    ).all()

    results = []
    for transaction, account_id, account_amount, first_name, last_name, email in transactions_details:
        result = {
            'transaction_id': transaction.id,
            'account_id': account_id,
            'account_amount': account_amount,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'transaction_type': transaction.transaction_type,
            'transaction_amount': transaction.amount,
            'transaction_created': transaction.created
        }
        results.append(result)
    return render_template("transactions/read.html", transactions=results , user=current_user)
