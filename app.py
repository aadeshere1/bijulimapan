from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, render_template, url_for
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

import os

app = Flask(__name__)
if os.environ['ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/flaskmovie'

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
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='aadesh@gmail.com', password='password')
    db.session.commit()

@app.route('/')
def index():
    allUser = User.query.all()
    oneUser = User.query.filter_by(username="aadesh").first()
    return render_template('add_user.html', allUser=allUser, oneUser=oneUser)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
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

if __name__ == "__main__":
    app.run()
