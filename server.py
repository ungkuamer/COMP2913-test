
from flask import Flask, render_template, redirect, url_for, request, jsonify
from supabase import create_client, Client
import stripe
import os

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FileField, IntegerField
from wtforms import SubmitField
from wtforms.validators import InputRequired, Length, Email

from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

from werkzeug.utils import secure_filename

import gpxpy
import gpxpy.gpx

from classes import User
from payment import card_check
from datetime import datetime, timedelta

app = Flask(__name__)

# CSRF
app.secret_key = 'c2a9d08bab60b9f7d727e6cc471c74fd'
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

# Supabase connection
url: str = "https://heukhrfwwtsnixqctfiy.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldWtocmZ3d3Rzbml4cWN0Zml5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDczMTAwNDYsImV4cCI6MjAyMjg4NjA0Nn0.Y2qPXw8whbYg2t2LJHec02kjLeIPwN-K5pfQOR1rBkU"
supabase: Client = create_client(url, key)

# Stripe
stripe.api_key = "pk_test_51OhYOQIcceGFCV5CbQ807r4tf6fLZTgcVZSCTg7OKdzl4VvFDcLiDAQB6lU8NcwhG87NIQaimTDClheq5qEwjiBk00wAur0ikT"

# Forms
class BaseForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = 'c2a9d08bab60b9f7d727e6cc471c74fd'

class RegisterForm(BaseForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    email = EmailField(validators=[InputRequired(), Email("Please enter valid email!")])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)])

    submit = SubmitField("Submit")

class LoginForm(BaseForm):
    email = EmailField(validators=[InputRequired(), Email("Please enter valid email!")])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)])

    submit = SubmitField("Login")

class UploadForm(BaseForm):
    file = FileField()
    submit = SubmitField("Upload")

class PaymentForm(BaseForm):
    name = StringField(validators=[InputRequired(), Length(min=3, max=50)])
    card_number = IntegerField(validators=[InputRequired(), card_check.is_luhn_valid])
    date = StringField(validators=[InputRequired(), Length(min=7, max=7), card_check.check_date])
    cvv = IntegerField(validators=[InputRequired(), Length(min=3, max=4)])
# Routes
@app.route("/")
def home():
    user = supabase.auth.get_user()

    if user != None:
        if user.user.user_metadata['admin'] == True:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    return render_template("index.html")

### User
@app.route("/user/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        
        email = form.email.data
        password = form.password.data

        user = supabase.auth.sign_up({ "email": email,
                                       "password": password, 
                                       "options": {
                                           "data": {
                                               "username": username,
                                               "isSubscribed": False,
                                               "admin": False
                                           }
                                       }
                                    })

        return redirect(url_for('home'))
    
    return render_template("user/register.html", form=form)

@app.route("/user/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        data = supabase.auth.sign_in_with_password({"email":form.email.data, "password":form.password.data})
        user = supabase.auth.get_user()

        data, count = supabase.table('user').select('*').eq('id', user.user.id).execute()
        

        if len(data[1]) == 0 and user.user.user_metadata['admin'] == False:
            data, count = supabase.table('user').insert({"email": user.user.email,
                                                         "username":user.user.user_metadata["username"], 
                                                         "isSubscribed":user.user.user_metadata["isSubscribed"]}).execute()

        if user.user.user_metadata['admin'] == True:
            return redirect(url_for('admin_dashboard'))
        
        return redirect(url_for('dashboard'))
    
    return render_template("user/login.html", form=form)

@app.route("/user/dashboard")
def dashboard():
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for('login'))
    
    if user.user.user_metadata['admin'] == True:
        return redirect(url_for('admin_dashboard'))

    curr_user = {
        "id":user.user.id,
        "username":user.user.user_metadata["username"],
        "email":user.user.email,
        "isAuthenticated":user.user.aud,
        "isSubscribed":user.user.user_metadata["isSubscribed"]
    }

    data, count = supabase.table('uploadedfiles').select('*').eq('userid', user.user.id).execute()
    files = []
    for items in data[1]:
        files.append([items['id'], items['filename']])

    return render_template("user/dashboard.html", user=curr_user, files=files)

@app.route("/logout")
def logout():
    res = supabase.auth.sign_out()
    return redirect(url_for('login'))

'''
This section handle routes regarding admin operations.

"/admin/register" : register user with admin priviledge 
                    (route not public - only for testing)
"/admin/dashboard" : 

'''
### Admin
##### add secret key after register - temp link only for testing
@app.route("/admin/register", methods=['POST', 'GET'])
def admin_register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        
        email = form.email.data
        password = form.password.data

        user = supabase.auth.sign_up({ "email": email,
                                       "password": password, 
                                       "options": {
                                           "data": {
                                               "username": username,
                                               "isSubscribed": True,
                                               "admin": True
                                           }
                                       }
                                    })           
        return redirect(url_for('admin_dashboard'))
    
    return render_template("admin/register.html", form=form)

@app.route("/admin/dashboard")
def admin_dashboard():
    user = supabase.auth.get_user()

    if (user == None or user.user.user_metadata["admin"] == False):
        return redirect(url_for('login'))

    curr_user = {
        "id":user.user.id,
        "username":user.user.user_metadata["username"],
        "email":user.user.email,
        "isAuthenticated":user.user.aud,
        "isSubscribed":user.user.user_metadata["isSubscribed"]
    }

    data, count = supabase.table('user').select('*').execute()

    user_list = []
    for c_user in data[1]:
        user_list.append(User(c_user['id'], c_user['username'], c_user['email'], c_user['isSubscribed']))

    return render_template("admin/dashboard.html", user=curr_user, data=user_list)

@app.route("/admin/user_profile/<id>")
def admin_user_profile(id):
    user = supabase.auth.get_user()

    if (user == None or user.user.user_metadata["admin"] == False):
        return redirect(url_for('login'))
    
    data, count = supabase.table('user').select('*').eq('id', id).execute()

    curr_user = data[1][0]

    data, count = supabase.table('uploadedfiles').select('*').eq('userid', curr_user['id']).execute()
    files = []
    for items in data[1]:
        files.append([items['id'], items['filename']])
    
    return render_template("admin/user_profile.html", user=curr_user, files=files)

'''
IN PROGRESS [stripe implementation]

This section handle routes regarding pricing and payments.

'''

@app.route("/pricing")
def pricing():
    return render_template("payment/pricing.html")

@app.route("/checkout/<int:id>", methods=["POST", "GET"])
def checkout(id):
    form = PaymentForm()
    user = supabase.auth.get_user()
    
    if user == None:
        return redirect(url_for('login'))

    if id == 1:
        price = 0.99
        package = 'Weekly'
        end = datetime.now() + timedelta(weeks=1)
    elif id == 2:
        price = 2.99
        package = 'Monthly'
        end = datetime.now() + timedelta(weeks=4)
    else:
        price = 29.99
        package = 'Yearly'
        end = datetime.now() + timedelta(weeks=52)

    return render_template("payment/checkout.html", price=price, package=package, end=end.date(), form=form)

@app.route("/api/payment", methods=["GET"])
def payment():
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for('login'))
    
    return redirect(url_for('dashboard')) 
    
@app.route("/test/payment")
def test_payment():
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for("login"))
    
    return render_template("payment/teststripe.html")

@app.route("/config")
def get_key():
    stripe_config = {"publicKey": "pk_test_51OhYOQIcceGFCV5CbQ807r4tf6fLZTgcVZSCTg7OKdzl4VvFDcLiDAQB6lU8NcwhG87NIQaimTDClheq5qEwjiBk00wAur0ikT"}
    return jsonify(stripe_config)

@app.route("/create-checkout-session")
def create_checkout_session():
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for("/login"))
    
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = "sk_test_51OhYOQIcceGFCV5CRc3mkHKKfsU7fb7sdwYEgV5AzQj20d0Prlv46al5m0ut00CjwLWOM1aGftSbf8r58xefVCN300gKuNNJI7"

    data, count = supabase.table('stripecustomers').select('stripeid').eq('userid', user.user.id).execute()

    if len(data[1]) == 0:
        customer_id = None
    else:
        customer_id = data[1][0]['stripeid']

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            success_url=domain_url+ "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url,
            customer_email=user.user.email,
            client_reference_id=user.user.id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": "price_1OiJ7IIcceGFCV5CgsjvtPiB",
                    "quantity": 1
                }
            ]
        )
        return jsonify({"sessionId":checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route("/success")
def success():
    stripe.api_key = "sk_test_51OhYOQIcceGFCV5CRc3mkHKKfsU7fb7sdwYEgV5AzQj20d0Prlv46al5m0ut00CjwLWOM1aGftSbf8r58xefVCN300gKuNNJI7"
    user = supabase.auth.get_user()
    stripe_res = stripe.Customer.list(email=user.user.email)
    data, count = supabase.table('stripecustomers').select('stripeid').eq('userid', user.user.id).execute()

    if len(data[1]) == 0:
        stripe_res = stripe.Customer.list(email=user.user.email)
        to_add = stripe_res['data'][0]['id']
        supabase.table('stripecustomers').insert({'stripeid':to_add}).execute()

    return redirect(url_for("dashboard"))

'''
This section handle routes regarding file uploads.

"/upload" : displayes the page with an upload form and point to an
            api for file upload to database

"/api/upload" : POST api endpoint that receives the data for process
                - uploads the file to supabase storage
                - parse gpx file and convert coordinates to an
                array of int ([latitude, longitude])
                - insert to database linking the uploaded file, the user 
                and the coordinates array    
'''

@app.route("/upload")
def upload():
    if supabase.auth.get_user() == None:
        return redirect(url_for('login'))
    
    form = BaseForm()
    return render_template("upload.html", form=form)

@app.route("/delete/<id>")
def delete(id):
    if supabase.auth.get_user() == None:
        return redirect(url_for('login'))
    
    data, count = supabase.table('uploadedfiles').select('filename', 'userid').eq('id', id).execute()
    filename = data[1][0]['filename']
    userid = data[1][0]['userid']

    supabase.table('uploadedfiles').delete().eq('id', id).execute()
    supabase.storage.from_('gpxfiles').remove(f"{userid}/{filename}")

    return redirect(url_for('dashboard'))

@app.route("/api/upload", methods=["POST"])
def fileupload():
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        return 'No file part'
     
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    newname = secure_filename(file.filename)
    file.save(newname)

    gpx_file = open(newname)
    gpx = gpxpy.parse(gpx_file)

    points = []
    
    '''
    GPX files store and group coordinates/points in different ways,
    either in tracks, waypoints or routes.

    The conditional statement checks for the different
    way of grouping the coordinates.

    '''
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append([point.latitude, point.longitude])

    if len(points) == 0:
        for point in gpx.waypoints:
            points.append([point.latitude, point.longitude])
            
    
    if len(points) == 0:
        for route in gpx.routes:
            for point in route.points:
                points.append([point.latitude, point.longitude])

    with open(newname, "rb") as f:
        supabase.storage.from_('gpxfiles').upload(f"/{user.user.id}/{newname}", f, {"content-type": "application/gpx+xml"})

    data, count = supabase.table('uploadedfiles').insert({"filename":newname, "pointsdata":points}).execute()

    
    if os.path.exists(newname):
        os.remove(newname)

    return redirect(url_for('dashboard'))

'''
This section handle routes regarding map viewing.

"/view/<id>" : generates a new page and takes file id as
               parameter, displays coordinates on map

'''

@app.route("/view/<id>", methods=["GET", "POST"])
def view(id):
    user = supabase.auth.get_user()

    if user == None:
        return redirect(url_for('login'))

    data, count = supabase.table('uploadedfiles').select("pointsdata").eq('id', id).execute()
    
    final_arr = []
    for item in data[1]:
        final_arr = item['pointsdata']

    return render_template('view.html', points=final_arr)

if __name__ ==  "__main__":
    app.run(debug=True)