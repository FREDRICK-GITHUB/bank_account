from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Account
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func

accounts = Blueprint("accounts", __name__)


# return dropdown for users without bank account
@accounts.route("/create_account", methods=["GET"])
@login_required
def get_non_account_user():
    # Query for users not in accounts
    non_account_users = User.query.filter(
        User.id.notin_(Account.query.with_entities(Account.user_id))
    ).all()

    # Extract required information
    non_account_users_info = [{"id": user.id} for user in non_account_users]

    return render_template(
        "accounts/create.html", users_info=non_account_users_info, user=current_user
    )


# create new account for user
@accounts.route("/create_account", methods=["POST"])
@login_required
def create_new_user_account():
    user_id = request.form.get("user_id")
    if not user_id:
        flash("User ID error, please check details", category="error")

    existing_account = Account.query.filter_by(user_id=user_id).first()
    if existing_account:
        flash("User has exisiting bank account!", category="error")

    new_account = Account(
        user_id=user_id,
        amount=0,
        created=func.now(),
        updated=func.now(),
        status="active",
    )
    db.session.add(new_account)
    db.session.commit()

    return redirect(url_for("accounts.get_accounts"))


# return all exisiting user accounts
@accounts.route("/get_accounts", methods=["GET"])
@login_required
def get_accounts():
    # Query all account details
    all_accounts = Account.query.all()

    # Prepare the response data
    account_details = []
    for account in all_accounts:
        account_info = {
            "account_id": account.id,
            "user_id": account.user_id,
            "amount": account.amount,
            "created": account.created,
            "updated": account.updated,
        }
        account_details.append(account_info)

    return render_template(
        "accounts/read.html", account_details=account_details, user=current_user
    )
