from flask import Flask,render_template,request,flash,session,redirect,jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_ckeditor import CKEditor
import os
import json
from datetime import datetime

app=Flask(__name__)
Bootstrap(app)
CKEditor(app)
app.config['SECRET_KEY']=os.urandom(20)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///blog.db'
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    firstname=db.Column(db.String(100),nullable=False)
    lastname=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.Text,nullable=False)


class Blogpost(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(1000),nullable=False)
    content=db.Column(db.Text,nullable=False)
    author=db.Column(db.String(100),default="Anonymous")
    authorid=db.Column(db.Integer)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return "Blogpost"+str(self.id)


@app.route("/")
def main():
    blogposts=Blogpost.query.all()
    return render_template('home.html',blogposts=blogposts)

@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        username=request.form['username']
        email=request.form['email']
        password=request.form['pwd']
        if request.form['pwd']==request.form['confirm_pwd']:
           try:
            new_user=User(username=username,firstname=firstname,lastname=lastname,email=email,password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash("successfully registered",'success')
            return redirect("/login")
           except:
               flash("Somthing went worng",'danger') 
               return redirect("/register")  
        flash("check password correctly",'danger')
        return render_template("login.html")
    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method== 'POST':
        userDetails=request.form
        username=userDetails['username']
        user=User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password,userDetails['pwd']):
            #    try:
                 session['login']=True
                 session['username']=user.username
                 session['firstname']=user.firstname
                 session['lastname']=user.lastname
                #  session['uid']=User.id
                 flash("Welcome "+user.username,"success")
                 return redirect("/")
            #    except:
            #     flash("Wrong password","danger")
            #     return render_template('login.html')
            else:
                flash("Wrong password","danger")
                return redirect("/login")
        else:
            flash("No user found create from here","info")
            return render_template("register.html")
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('login')
    return redirect("/login")



@app.route("/createpost",methods=['POST','GET'])
def createpost():
    if request.method=='POST':
        post=request.form
        newpost=Blogpost(title=post['title'],content=post['body'],author=session['username'],authorid=0)
        db.session.add(newpost)
        db.session.commit()
        flash("Post create Successfully","success")
        return redirect("/")
    return render_template("createpost.html")


@app.route("/allposts",methods=['GET'])
def allposts():
    try:
        posts=Blogpost.query.filter_by(author=session['username']).all()
        return render_template("authorallposts.html",posts=posts)
    except:
        return render_template("authorallposts.html",posts=None)


@app.route("/<string:title>",methods=['GET'])
def post(title):
    posts=Blogpost.query.filter_by(title=title).first()
    return render_template("post.html",posts=posts)

@app.route("/author/<string:name>",methods=['GET'])
def authorposts(name):
    posts=Blogpost.query.filter_by(author=name).all()
    return render_template("authornamepost.html",posts=posts)
@app.route("/delete/<int:id>")
def deletepost(id):
    deletepost=Blogpost.query.get_or_404(id)
    try:
        db.session.delete(deletepost)
        db.session.commit()
        flash("Post deleted successfully",'success')
        return redirect("/allposts")
    except:
        flash("Post delete unsuccessfully",'danger')
        return redirect("/allposts")

@app.route("/edit/<int:pid>",methods=['GET','POST'])
def editpost(pid):
    editpost=Blogpost.query.get_or_404(pid)
    if request.method=='POST':
        try:
            blogpost=db.session.query(Blogpost).filter(Blogpost.id==pid).one()
            blogpost.content=request.form['body']
            blogpost.title=request.form['title']
            db.session.commit()
            flash("Post edited successfully",'success')
            return redirect("/allposts")
        except:
            flash("Post edit unsuccessfully",'danger')
            return redirect("/allposts")
    return render_template("editpost.html",editpost=editpost)
if __name__=="__main__":
    app.run(debug=True,port=5001)
