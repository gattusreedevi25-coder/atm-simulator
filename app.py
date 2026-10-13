
import os
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key-change-me")

# Demo account for learning only.
# Data is stored in memory and resets when the app restarts.
accounts = {
    "1234567890": {
        "pin": "1234",
        "balance": 5000.00,
        "transactions": []
    }
}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "account" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account_number = request.form.get("account", "").strip()
        pin = request.form.get("pin", "").strip()

        account = accounts.get(account_number)

        if account and account["pin"] == pin:
            session.clear()
            session["account"] = account_number
            return redirect(url_for("dashboard"))

        flash("Invalid account number or PIN.", "error")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    account_number = session["account"]
    account = accounts.get(account_number)

    if not account:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        balance=account["balance"],
        transactions=list(reversed(account["transactions"])),
        account_number=account_number
    )


@app.route("/transaction", methods=["POST"])
@login_required
def transaction():
    account_number = session["account"]
    account = accounts.get(account_number)

    if not account:
        session.clear()
        return redirect(url_for("login"))

    action = request.form.get("action", "")
    amount_text = request.form.get("amount", "").strip()

    try:
        amount = round(float(amount_text), 2)
    except (ValueError, TypeError):
        flash("Please enter a valid amount.", "error")
        return redirect(url_for("dashboard"))

    if not amount > 0 or amount > 1000000:
        flash("Enter an amount greater than ₹0 and no more than ₹10,00,000.", "error")
        return redirect(url_for("dashboard"))

    if action == "deposit":
        account["balance"] = round(account["balance"] + amount, 2)
        account["transactions"].append(
            {"type": "Deposit", "amount": amount}
        )
        flash(f"₹{amount:.2f} deposited successfully.", "success")

    elif action == "withdraw":
        if amount > account["balance"]:
            flash("Insufficient balance.", "error")
        else:
            account["balance"] = round(account["balance"] - amount, 2)
            account["transactions"].append(
                {"type": "Withdrawal", "amount": amount}
            )
            flash(f"₹{amount:.2f} withdrawn successfully.", "success")
    else:
        flash("Invalid transaction.", "error")

    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
