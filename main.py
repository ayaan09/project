from classes import *


@app.route('/',  methods = ['GET', 'POST'])
def main():
    if request.method=='POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if (name and username and email and password) :
            usr = users(name, email, username, password, 0)
            db.session.add(usr)
            db.session.commit()

        return redirect(url_for("home"))
    else:
        return render_template("register.html")

@app.route('/admin-login',  methods = ['GET', 'POST'])
def adminlogin():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        if ( username and password) :
            if username=="admin" and password=="admin":
                session.permanent = True
                session["username"]=username
                return redirect(url_for("admin_panel"))
    else:
        return render_template("admin-login.html")

@app.route('/adminpanel', methods=['GET', 'POST'])
def admin_panel():
    if session["username"]=="admin":
        return f"<h1>Hello Admin</h1>"

@app.route('/transactions', methods=['GET', 'POST'])
def transaction():
    bankacc = session['id']
    if request.method=='GET':
        found_user = transactions.query.filter_by(payee_id=bankacc).all()
        other_user = transactions.query.filter_by(payer_id=bankacc).all()
        name = users.query.filter_by(_id=session['id']).first().name
        names_payee=[]
        names_paid_to=[]
        amount=[]
        time=[]
        for userage in found_user:
            names_paid_to.append(users.query.filter_by(_id=userage.payee_id).first().name)
            names_payee.append(users.query.filter_by(_id=userage.payer_id).first().name)
            amount.append(userage.amount)
            time.append(str(userage.time).split(' ')[0])

        for userage in other_user:
            names_paid_to.append(users.query.filter_by(_id=userage.payee_id).first().name)
            names_payee.append(users.query.filter_by(_id=userage.payer_id).first().name)
            amount.append(userage.amount)
            time.append(str(userage.time).split(' ')[0])
        return render_template('transactions.html',name=name,time=time, user=names_payee, getter=names_paid_to, amt=amount)



@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method=='POST':    
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        found_user = users.query.filter_by(username=username).first()
        if found_user.password==password:
            session["username"]=username
            session['id'] = found_user._id
            return redirect(url_for("home"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/home')
def home():
    if "username" in session:
        user = session["username"]
        found_user = users.query.filter_by(username=user).first()
        balance = found_user.balance
        name = found_user.name
        id = found_user._id 
        return render_template("home.html", id=id ,name=name, balance=balance)
    else:
        return redirect(url_for("login"))

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    name = users.query.filter_by(_id=session['id']).first().name
    username  = session["username"]
    found_user = users.query.filter_by(username=username).first()
    if not found_user:
        return redirect(url_for("login"))
    else:
        if(request.method=='POST'):
            payee = request.form['payee']
            amount = float(request.form['amount'])
            if amount<=found_user.balance:
                flash("payment initiated")
                payee_user = users.query.filter_by(_id=payee).first()
                if not payee_user:
                    flash("Account not found")
                else:
                    payee_user.add_balance(amount)
                    found_user.deduct_balance(amount)
                    trs = transactions(payee_user._id, found_user._id, amount)
                    db.session.add(trs)
                    db.session.commit()
                return render_template("transfer.html", name=name)
            else:
                flash("You do not have enough funds")
                return render_template("transfer.html", name=name)
    return render_template("transfer.html", name=name)


@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))

@app.route('/authorize_payment', methods=["POST", "GET"])
def authpay():
    if request.method == "POST":
        content= request.json
        payer_id = content['payer_id']
        payee_id = content['payee_id']
        pwd = content['pwd']
        add = content['amount']
        type= content['type']
        found_user = users.query.filter_by(_id=payee_id).first()
        another_user = users.query.filter_by(_id=payer_id).first()
        if found_user.password == pwd:
            if type=="deposit":
                if another_user.balance<add:
                    return jsonify({"transaction":"fail"})
                else:
                    found_user.add_balance(add)
                    another_user.deduct_balance(add)
                    db.session.commit()
                    trs = transactions(payee_id, payer_id, add)
                    db.session.add(trs)
                    db.session.commit()
                    return jsonify({"transaction":"ok"})
            elif type=="withdraw":
                if found_user.balance<add:
                    return jsonify({"transaction":"fail"})
                else:
                    another_user.deduct_balance(add)
                    db.session.commit()
                    trs = transactions(payee_id, payer_id, add)
                    db.session.add(trs)
                    return jsonify({"transaction":"ok"})
        else:
            return jsonify({"transaction":"fail"})

@app.route('/loans')
def loans_():
    name = users.query.filter_by(_id=session['id']).first().name
    outstanding='You have no outstanding loans'
    loan = loans.query.filter_by(loanReceipientId=session['id']).first()
    print(loan)
    if(not loan):
        return render_template('loan.html', loan=outstanding, name=name)
    else:
        outstanding=f"You have ${loan.amount} due"
        return render_template('loan.html',loan=outstanding, name=name)


@app.route('/settle-loan', methods=['GET', "POST"])
def settle_loan():
    name = users.query.filter_by(_id=session['id']).first().name
    loan = loans.query.filter_by(loanReceipientId=session['id']).first()
    user = users.query.filter_by(_id=session['id']).first()
    outstanding=0
    if loan.amount>user.balance:
        loan.amount = float(loan.amount)-float(user.balance)
        user.deduct_balance(user.balance)
        db.session.commit()
        if loan:
            outstanding = loan.amount
        return render_template('loan.html',loan=outstanding, name=name)
    else:
        user.deduct_balance(loan.amount)
        loan = loans.query.filter_by(loanReceipientId=session['id']).first()
        db.session.delete(loan)
        db.session.commit()
        if loan:
            outstanding = loan.amount
        return render_template('loan.html',loan=outstanding, name=name)


@app.route('/apply-loan', methods=['GET', "POST"])
def apply_loan():
    name = users.query.filter_by(_id=session['id']).first().name  
    if request.method=='POST':
        amount = float(request.form['amount'])
        salary = float(request.form['salary'])
        education = request.form['education']
        found_user = users.query.filter_by(_id=session['id']).first()
        loan = loans.query.filter_by(loanReceipientId=session['id']).first()
        if not loan: 
            if salary*4>amount and education=="University":
                flash("Loan Has Been Granted!")
                found_user.add_balance(amount)
                trs = transactions(session['id'], 1, amount)
                lns = loans(amount, session['id'])
                db.session.add(trs)
                db.session.add(lns)
                db.session.commit()
            elif (salary*6 >amount and education=="High School"):
                flash("Loan Has Been Granted!")
                found_user.add_balance(amount)
                trs = transactions(session['id'], 1, amount)
                lns = loans(amount, session['id'])
                db.session.add(trs)
                db.session.add(lns)
                db.session.commit()
            else:
                flash('Loan Has Been Rejected')
        else:
            flash('Loan Has Been Rejected')

        return render_template("apply-loan.html", name=name)
    else:
        return render_template("apply-loan.html", name=name)


@app.route('/credit-card')
def cc():
    username  = session["username"]
    found_user = users.query.filter_by(username=username).first()
    balance = found_user.balance
    name = found_user.name
    if found_user.card_no == 1:
        card_no = "The User Has No Credit Card"
        return f"<h1>The User Has No Credit Card</h1>"
    else:
        card_no = found_user._id

        return render_template("creditcard.html", card_no = card_no, name=name,balance= balance)




if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port='8080', debug=True)