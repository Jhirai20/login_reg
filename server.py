from flask import Flask, redirect, render_template, request, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt

app=Flask(__name__)
bcrypt = Bcrypt(app) 
app.secret_key='keepsake'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success',)
def result():
    return render_template("success.html")


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
@app.route ('/process', methods=['POST'])
def process():
    is_valid = True
    if len(request.form['fname']) <1:
        flash("First name cannot be blank!")
    if len(request.form['lname']) <1:
        flash("Last name cannot be blank!")
    if len(request.form['email']) <1:
        flash("Email cannot be blank!")
    if request.form['password']!=request.form['password2']:
        flash("Passwords don't match!")
    if not is_valid:
        return redirect('/')
    else:
        if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
            flash("Invalid email address!")
        else:
            pw_hash = bcrypt.generate_password_hash(request.form['password2'])
            print(pw_hash) 
            mysql=connectToMySQL('login')
            query = "INSERT INTO users(first_name, last_name, email,pw_hash, created_at, updated_at) VALUES (%(fname)s,%(lname)s,%(email)s,%(password_hash)s,NOW(),NOW());"
            data = {
                'fname': request.form['fname'],
                'lname': request.form['lname'],
                'email': request.form['email'],
                "password_hash" : pw_hash
            }
            session['userfname'] = request.form['fname']
            session['userlname'] = request.form['lname']
            result =mysql.query_db(query,data)
            return redirect('/success')
    return redirect('/')

@app.route ('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("login")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"] }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['pw_hash'], request.form['password']):
            session['userid'] = result[0]['id']
            session['userfname'] = result[0]['first_name']
            session['userlname'] = result[0]['last_name']
            print(session['userid'])
            return redirect('/success')
    flash("You could not be logged in")
    return redirect("/")

@app.route('/logout',)
def logout():
    session.clear()
    return redirect("/")
if __name__=="__main__":
    app.run(debug=True)