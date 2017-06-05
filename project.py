import os
import re
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, Response
from werkzeug.utils import secure_filename
from flask_mail import Message, Mail
from random import randint
from shelljob import proc
import paramiko

app = Flask(__name__)
app.config.from_object(__name__)

product = [
    {
        'id':1,
        'name': 'book'
    },
    {
        'id':2,
        'name': 'backpack'
    }]

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'qqdewasteven@gmail.com',
    MAIL_PASSWORD = 'qqdewa9999'
))

mail = Mail(app)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return "Hello World!"
    else:
        data = request.files['files']
        if data:
            app.config['UPLOAD_FOLDER'] = '/home/qqdewa/'
            data.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(data.filename)))
            return secure_filename(data.filename) + '\n'

def checkSSHConnection(ipAddr, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ipAddr,username=username,password=password)
        ssh.close()
    except:
        return 0
    return 1

@app.route('/editor', methods=['GET','POST'])
def editor():
    ipAddr = None
    username = None
    password = None
    if request.method == 'GET':
        return render_template('editor.html')
    else:
        codelines = request.form['codemirror']
        filepath = os.getcwd()
        f = open(filepath+'/fabfile.py', 'w')
        f.write(codelines)
        f.close()
        clines = re.findall(r'env.hosts\s*\=\s*\[\'\d+\.\d+\.\d+\.\d+\'\]',codelines)
        if clines:
            ipAddr = re.search(r'\d+\.\d+\.\d+\.\d+', clines[0])
            ipAddr = ipAddr.group()

        clines = re.findall(r'env.user\s*\=\s*\'\w+\'', codelines)
        if clines:
            username = re.search(r'\'\w+\'', clines[0])
            username = username.group().strip("'")

        clines = re.findall(r'env.password\s*\=\s*\'.+\'', codelines)
        if clines:
            password = re.search(r'\'.+\'', clines[0])
            password = password.group().strip("'")

        if checkSSHConnection(ipAddr, username, password):
            return redirect(url_for('stream'))
        return "Configuration Error"

@app.route('/stream', methods=['GET','POST'])
def stream():
    g = proc.Group()
    p = g.run(["bash", "-c", "cd", "/home/qqdewa/sideproject/"])
    #p = g.run(["bash", "-c", "python fabfile.py"])
    p = g.run(["bash", "-c", "fab -t 5 setup_api"])

    def read_process():
        while g.is_pending():
            lines = g.readlines()
            for proc, line in lines:
                if line:
                    yield line
    return Response(read_process(), mimetype="text/plain")

@app.route('/skulpt', methods=['GET', 'POST'])
def skulpt():
    if request.method == 'GET':
        return render_template('skulpt.html')
    else:
        codelines = request.form['codeeditor']
        filepath = os.getcwd()
        f = open(filepath+'/fabfile.py', 'w')
        f.write(codelines)
        f.close()
        return codelines

@app.route('/product/api/v1.0/list', methods=['GET'])
def product_list():
    return jsonify({'product':product})

@app.route('/sendemail', methods=['GET','POST'])
def sendemail():
    msg = Message("Hello", sender="qqdewasteven@gmail.com", recipients=["qqdewadani@gmail.com"])
    msg.body = "mantap!\n Code: "
    msg.html = "<b>HTML</b> body <br> code: " + ''.join([chr(randint(97,122)) for i in range(10)])
    with app.open_resource("/home/qqdewa/Downloads/images.jpeg") as fp:
        msg.attach("images.jpeg", "images/jpeg", fp.read())
    mail.send(msg)
    return 'Success!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
