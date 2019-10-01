
from flask import Flask, render_template, request, redirect, session, flash
from config import app, db
from models import User, Crop, Field, Harvest, Images, Map
from functools import wraps
import re
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "user_id" in session:
            return redirect ("/")
        user_id = session['user_id']
        user = User.query.filter_by(id = user_id)
        if not user:
            return redirect ("/")
        return f(user.first(), *args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    return render_template ("index.html")

@app.route("/to_register")
def route_to_register(): 
    return render_template ("createNew.html")

@app.route("/register", methods=['POST'])
def register():
    is_valid = True
    if len(request.form["fname"]) < 2:
        is_valid = False
        flash("Please enter a valid first name")
    if len(request.form["lname"]) < 2:
        is_valid = False
        flash("Please enter a valid last name")
    if not EMAIL_REGEX.match(request.form["email"]):    
        is_valid = False
        flash("Invalid email address!")
    if len(request.form["password"]) < 8:
        is_valid = False
        flash("Password should be at least 8 characters")
    if request.form['password'] != request.form['cpassword']:
        is_valid = False
        flash("Passwords need to match")
    if is_valid:
        f_name = request.form['fname']
        l_name = request.form['lname']
        email = request.form['email']
        user_name = User.query.filter(db.and_(User.first_name == f_name, User.last_name == l_name, User.email == email)).all()
        if user_name:
            is_valid = False
            flash("User already registered")

        if is_valid:
            pw_hash = bcrypt.generate_password_hash(request.form['password'])  
            new_user = User(first_name = request.form['fname'],
                            last_name = request.form['lname'],
                            email = request.form['email'], 
                            password = pw_hash)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")
    return redirect("/to_register")
        
@app.route("/signin", methods=['POST'])
def signin():
    is_valid = True
    if len(request.form['email']) < 1:
        is_valid = False
        flash("please enter your email")
    if len(request.form['password']) <8:
        is_valid = False
        flash("please enter your correct password")
    if not is_valid:
        return redirect("/")
    else:
       login = User.query.filter_by(email = request.form['email']).all()
       print(login)
    if login:
        login = login[0]
        hashed_password = login.password
        if bcrypt.check_password_hash(hashed_password, request.form['password']):
            session['user_id'] = login.id
            return redirect("/CropPortal")
        else:
            flash("Password is invalid")
            return redirect("/")
    else:
        flash("Please use a valid email address")
        return redirect("/")
    return redirect("/")

@app.route("/CropPortal")
@login_required
def CropPortal(user):
    print("*"*20)
    print(user)
    
    return render_template ("cropMain.html", name= user.first_name)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/YearMap", methods=["POST"])
@login_required
def YearMap(user):
    image = Images.query.filter_by(year = request.form['year']).all()
    year = Harvest.query.filter_by(year = request.form['year']).all()
    return render_template("year.html", year= year[0], image = image[0])

@app.route("/CropMap", methods=["POST"])
@login_required
def CropMap(user):
    crop = Crop.query.filter_by(crop_name = request.form['crop']).all()
   
    return render_template("crop.html", crop = crop[0])

@app.route("/addtoDB")
@login_required
def addtoDB(user):
    crops = Crop.query.all()
    
    return render_template ("edit.html", crops = crops)


@app.route("/addCrop", methods=["POST","GET"])
@login_required
def addCrop(user):
    is_valid = True
    if len(request.form['newcrop']) < 1:
        is_valid = False
        flash("please enter a crop")
    if not is_valid:
        return redirect("/addtoDB")
    if is_valid:
        new_crop = Crop(crop_name = request.form['newcrop'])
        db.session.add(new_crop)
        db.session.commit()
        return redirect("/addtoDB")

@app.route("/addField", methods=["POST","GET"])
@login_required
def addField(user):
    is_valid = True
    if len(request.form['newfield']) < 1:
        is_valid = False
        flash("Please enter a field!")
    if not is_valid:
        return redirect("/addtoDB")
    if is_valid:
        new_field = Field(field_name = request.form['newfield'])
        db.session.add(new_field)
        db.session.commit()
        return redirect("/addtoDB")

@app.route("/addHarvest", methods=["POST"])
@login_required
def addHarvest(user):
    field = Field.query.filter_by(field_name = request.form["fieldname"]).all()
    
    crop = Crop.query.filter_by(id = request.form["crop"]).all()
    
    is_valid = True
    if len(request.form['newYear']) < 1:
        is_valid = False
        flash("Please enter a Year!")
    if not is_valid:
        return redirect("/addtoDB")
    if len(request.form['newYield']) < 1:
        harvest_wout_yeild = Harvest(year = request.form['newYear'],
                                      crop_id = crop[0].id ,
                                      field_id = field[0].id)
        db.session.add(harvest_wout_yeild)
        db.session.commit()
        return redirect("/addtoDB")

    elif len(request.form['newYield']) >= 1:
        harvest_with_yeild = Harvest(year = request.form['newYear'],
                                  harvest_yield = request.form['newYield'],
                                  crop_id = crop[0].id ,
                                  field_id = field[0].id)
        db.session.add(harvest_with_yeild)
        db.session.commit()
        return redirect("/addtoDB")

@app.route("/field/<name>")
@login_required
def lookatField(user, name):
    field_name = name
    query = db.session.query(Harvest, Field, Crop).join(Field, Harvest.field_id == Field.id).filter(Field.field_name == name).join(Crop, Harvest.crop_id == Crop.id)
    return render_template("field.html", fields = query, field_name= field_name)

if __name__ == "__main__":
    app.run(debug=True)