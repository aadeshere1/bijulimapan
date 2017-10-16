from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, render_template, url_for
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_mail import Mail
import os
import numpy as np
import cv2


mail = Mail()
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config.update(
        DEBUG=True,
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=os.environ['GMAIL_USERNAME'],
        MAIL_PASSWORD=os.environ['GMAIL_PASSWORD']
        )

mail.init_app(app)

if os.environ['ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/flaskmovie'
    app.config['SECRET_KEY'] = 'super-secret'

app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'MMMMM...SALTY'
app.debug = True
db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


# setup flask security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#create a user to test
#@app.before_first_request
#def create_user():
#    db.create_all()
#    user_datastore.create_user(email='aadesh@gmail.com', password='password')
#    db.session.commit()

@app.route('/')
def index():
    return render_template('add_user.html')

@app.route('/profile/<email>')
@login_required
def profile(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return redirect(url_for('index'))
    else:
        return render_template('profile.html', user=user)

@app.route('/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/upload')
def uploadForm():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    cvTarget = os.path.join(APP_ROOT, 'manipulated/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    if not os.path.isdir(cvTarget):
        os.mkdir(cvTarget)

        
    file = request.files['file']
    print(file.filename)
    destination = "/".join([target, file.filename])
    file.save(destination)
    ref = cv2.imread(destination)
    img = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
    cv2.imwrite(img, cvTarget, 'jpg')
    return render_template('complete.html')

    #for file in request.files.getlist("file"):
    #    print(file)
    #    filename = file.filename
    #    destination = "/".join([target, filename])
    #    print(destination)
    #    file.save(destination)
    #    print("removing" + destination)
    #    os.remove(destination)
    #return render_template('complete.html')

if __name__ == "__main__":
    app.run()
