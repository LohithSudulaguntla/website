from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management

DATA_FILE = "data.xlsx"

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=['Name', 'Email', 'Phone', 'University', 'Branch', 'Password'])
    df.to_excel(DATA_FILE, index=False)

# Route for login page
@app.route('/')
def home():
    return render_template('login.html')

# Route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        university = request.form['university']
        branch = request.form['branch']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        # Load existing data
        df = pd.read_excel(DATA_FILE)

        # Check if the email already exists
        if email in df["Email"].values:
            flash("Email already registered!", "error")
            return redirect(url_for('register'))

        # Store new user
        new_data = pd.DataFrame([[name, email, phone, university, branch, password]],
                                columns=['Name', 'Email', 'Phone', 'University', 'Branch', 'Password'])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)

        flash("Registration Successful! Please log in.", "success")
        return redirect(url_for('home'))

    return render_template('register.html')

# Route for login functionality
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    df = pd.read_excel(DATA_FILE).astype(str)

    # Check if user exists
    user = df[(df['Email'] == email) & (df['Password'] == password)]

    if not user.empty:
        session['user'] = {
            "name": user.iloc[0]['Name'],
            "university": user.iloc[0]['University'],
            "branch": user.iloc[0]['Branch']
        }
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid Email or Password", "error")
        return redirect(url_for('home'))

# Route for dashboard (after login)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('home.html', user=session['user'])

# Route for logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
