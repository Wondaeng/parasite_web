from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()           #SQLAlchemy를 사용해 데이터베이스 저장

class User(db.Model): 
    __tablename__ = 'user_table'   #테이블 이름 : user_table
    id = db.Column(db.Integer, primary_key = True)   #id를 프라이머리키로 설정
    password = db.Column(db.String(64))     #패스워드를 받아올 문자열길이 
    userid = db.Column(db.String(32))       #이하 위와 동일
    email = db.Column(db.String(32))

class Task(db.Model): 
    __tablename__ = 'task_table'   #테이블 이름 : task_table
    id = db.Column(db.Integer, primary_key = True)   #id를 프라이머리키로 설정
    task_name = db.Column(db.String(64))
    user_name = db.Column(db.String(32))
    visual_path = db.Column(db.String(64))
    date = db.Column(db.String(32))
    sensitivity = db.Column(db.String(32))
    process_stage = db.Column(db.String(32), unique=False)
