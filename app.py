from crypt import methods
import shutil
from flask import Flask, redirect, render_template, request, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import shutil
import time
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///sugoi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']=False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# DBテーブル作成
db.create_all()

@login_manager.user_loader
def getuser(username):
    return User.query.filter_by(username=username).first()
    
@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    if 'flag' not in session:
        session['flag'] = False
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = getuser(username)
        if check_password_hash(user.password, password):
            login_user(user)
            session['flag'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    session['flag'] = False
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    else:
        return render_template('register.html')

@app.route('/history')
def history():
    if session['flag'] == True:
        r_list = []
        query = resultTable.query.all()
        for r in query:
            result = [r.id, r.user, r.correct_label, r.detected_label]
            r_list.append(result)
        return render_template('history.html', results=r_list)
    else:
        return redirect(url_for('login'))

@app.route('/play', methods=['GET', 'POST'])
def play():
    if session['flag'] == True:
        if request.method == 'GET':
            return render_template('play.html')
        else:
            # 画像ファイルの保存
            shutil.rmtree('./upload/images')
            os.mkdir('./upload/images')
            file = request.files['image']
            file.save('./upload/images/'+str(file.filename))
            # 正解ラベルの取得
            label = request.form['hand']
            print(label)
            if file and label:
                time.sleep(1)
                # 検知画像と使用するモデルのパスを取得
                image_path = os.listdir('./upload/images')
                if '.DS_Store' in image_path:
                    image_path.remove('.DS_Store')
                model_path = os.listdir('./upload/models')
                if '.DS_Store' in model_path:
                    model_path.remove('.DS_Store')
                if len(model_path) == 0:
                    return redirect(url_for('upload'))
                image_source = './upload/images/' + image_path[0]
                model_source = './upload/models/' + model_path[0]
                # detect.pyの実行
                shutil.rmtree('./yolov5/runs/detect')
                command = f'python yolov5/detect.py --weights {model_source} --source {image_source} --save-txt --save-conf --exist-ok'
                subprocess.run(command, shell=True)
                dlabel = detect_label()
                img_path = img_source()
                print(img_path)
                if int(label) == int(dlabel):
                    msg = 'せいかい！'
                else:
                    msg = 'ざんねん！'
                r_insert(label, dlabel)

                return render_template('play.html', label=label, dlabel=dlabel, msg=msg)
    else:
        return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if session['flag'] == True:
        if request.method == 'GET':
            return render_template('upload.html')
        else:
            # 学習モデルファイルを取得
            shutil.rmtree('./upload/models')
            os.mkdir('./upload/models')
            file = request.files['model']
            file.save('./upload/models/'+str(file.filename))
            return redirect(url_for('play'))
    else:
        redirect(url_for('login'))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50))

class resultTable(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user = db.Column(db.String)
    correct_label = db.Column(db.Integer)
    detected_label = db.Column(db.Integer)

def detect_label():
    label_path =os.listdir('./yolov5/runs/detect/exp/labels')
    if '.DS_Store' in label_path:
        label_path.remove('.DS_Store')
    label_source = './yolov5/runs/detect/exp/labels/' + label_path[0]
    with open(label_source) as f:
        s = f.read()
    return s[0]

def img_source():
    img_path = os.listdir('./yolov5/runs/detect/exp')
    if '.DS_Store' in img_path:
        img_path.remove('.DS_Store')
    if 'labels' in img_path:
        img_path.remove('labels')
    return './yolov5/runs/detect/exp/' + img_path[0]

def r_insert(c_label, d_label):
    table = resultTable()
    table.user = session['username']
    table.correct_label = int(c_label)
    table.detected_label = int(d_label)
    db.session.add(table)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)