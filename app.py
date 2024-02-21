# Importing required libraries
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates') # Creating the Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://CloudSA66a5af45:password1!@konradserver2.database.windows.net,1433/invoicedatabase?driver=ODBC+Driver+18+for+SQL+Server' # Database connection string
app.config['SECRET_KEY'] = '1234' # Secret key for the app

db = SQLAlchemy() # Creating the database object
migrate = Migrate(app, db) # Creating the migration object
login_manager = LoginManager() # Creating the login manager object
login_manager.init_app(app) # Initializing the login manager
login_manager.login_view = 'login' # Setting the login view

class User(db.Model, UserMixin): # Creating the User model
    id = db.Column(db.Integer, primary_key=True) # User ID
    username = db.Column(db.String(120), unique=True, nullable=False) # Username
    password = db.Column(db.String(120), nullable=False) # Password

default_username = 'admin' # Default username
default_password = 'admin123' # Default password

class Invoice(db.Model): # Creating the Invoice model
    id = db.Column(db.Integer, primary_key=True) # Invoice ID
    date = db.Column(db.DateTime, nullable=False) # Invoice date
    customer_name = db.Column(db.String(120), nullable=False) # Customer name
    invoice_number = db.Column(db.String(20), nullable=False, unique=True) # Invoice number
    total = db.Column(db.Float, nullable=False) # Invoice total
    customer_address = db.Column(db.String(255), nullable=False) # Customer address
    description = db.Column(db.Text, nullable=False) # Invoice description

@login_manager.user_loader # Loading the user
def load_user(user_id): # Function to load the user
    return User.query.get(int(user_id)) # Returning the user

# Checking if data already exists before adding
with app.app_context(): # Creating the app context
    db.init_app(app) # Initializing the database
    db.create_all() # Creating the database

    if not User.query.filter_by(username=default_username).first(): # Checking if the default user exists
        hashed_password = generate_password_hash(default_password, method='pbkdf2:sha256') # Hashing the default password
        default_user = User(username=default_username, password=hashed_password) # Creating the default user
        db.session.add(default_user) # Adding the default user
        db.session.commit() # Committing the changes

    if not Invoice.query.first(): # Checking if the default invoices exist
        invoices = [ # Creating the default invoices
            {"date": datetime(2024, 2, 8, 12, 0, 0), "customer_name": "John Doe", "invoice_number": "INV001", "total": 100.0, "customer_address": "40 York Road IPSWICH, IP70 1IQ", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."},
            {"date": datetime(2024, 2, 9, 14, 30, 0), "customer_name": "Jane Smith", "invoice_number": "INV002", "total": 150.0, "customer_address": "93 Stanley Road OUTER HEBRIDES, HS13 6AP", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."},
        ]

        for data in invoices: # Adding the default invoices
            new_invoice = Invoice(**data) # Creating the new invoice
            db.session.add(new_invoice) # Adding the new invoice
        db.session.commit() # Committing the changes

# Routes for authentication and protected routes
@app.route('/auth/login', methods=['GET', 'POST']) # Login route
def login(): # Login function
    if request.method == 'POST': # Checking if the request method is POST
        username = request.form.get('username') # Getting the username from the form
        password = request.form.get('password') # Getting the password from the form
        user = User.query.filter_by(username=username).first() # Getting the user from the database

        if user and check_password_hash(user.password, password): # Checking if the user exists and the password is correct
            login_user(user) # Logging in the user
            return redirect(url_for('index')) # Redirecting to the index page
        else: # If the user does not exist or the password is incorrect
            flash('Invalid username or passowrd', 'error') # Flashing an error message
        
    return render_template('login.html') # Rendering the login page

@app.route('/logout') # Logout route
@login_required # Requiring the user to be logged in
def logout(): # Logout function
    logout_user() # Logging out the user
    return redirect(url_for('login')) # Redirecting to the login page

# Protected routes
@app.route('/') # Index route
@login_required # Requiring the user to be logged in
def index(): # Index function
    invoices = Invoice.query.all() # Getting all the invoices
    return render_template('index.html', invoices=invoices) # Rendering the index page

@app.route('/add', methods=['POST']) # Add invoice route
@login_required # Requiring the user to be logged in
def add_invoice(): # Add invoice function
    if request.method == 'POST': # Checking if the request method is POST
            new_invoice = Invoice( # Creating the new invoice
                date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'), # Converting the date to a datetime object
                customer_name = request.form['customer_name'], # Getting the customer name from the form
                invoice_number = request.form['invoice_number'], # Getting the invoice number from the form
                total = float(request.form['total']), # Getting the total from the form
                customer_address = request.form['customer_address'], # Getting the customer address from the form
                description = request.form['description'] # Getting the description from the form
            )
            db.session.add(new_invoice) # Adding the new invoice
            db.session.commit() # Committing the changes

    return redirect(url_for('index')) # Redirecting to the index page

@app.route('/delete/<int:invoice_id>') # Delete invoice route
@login_required # Requiring the user to be logged in
def delete_invoice(invoice_id): # Delete invoice function
    invoice_to_delete = Invoice.query.get_or_404(invoice_id) # Getting the invoice to delete

    try: # Trying to delete the invoice
        db.session.delete(invoice_to_delete) # Deleting the invoice
        db.session.commit() # Committing the changes
        return jsonify({'success': True, 'message': 'Invoice deleted succesfully'}) # Returning a success message
    except Exception as e: # Catching any exceptions
        return jsonify({'success': False, 'message': str(e)}) # Returning an error message
    
if __name__ == '__main__': # Checking if the app is being run
    app.run(debug=True) # Running the app in debug mode