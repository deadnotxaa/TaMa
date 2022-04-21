import jinja2
from flask import Flask, request, make_response, render_template, url_for
from jinja2 import Template, FileSystemLoader, Environment
from werkzeug.utils import redirect
from pymongo import MongoClient
import secrets
from flask_cors import CORS

client = MongoClient("localhost", 27017)
db = client.database
users = db.users
boards = db.boards

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
templateLoader = Environment(loader=FileSystemLoader(searchpath='./templates'))
app = Flask(__name__, static_folder='./static', static_url_path='/static')
CORS(app)
user_id = users.find({"user_id_counter": {"$exists": "true"}})[0]["user_id_counter"]
board_id = boards.find({"board_id_counter": {"$exists": "true"}})[0]['board_id_counter']
user_hash = 0


@app.route('/', methods=["GET"])
def main_page():
    template = templateLoader.get_template('main.html')
    return template.render()


@app.route('/register', methods=["GET", "POST"])
def register_page(error=""):
    user_cookie = request.cookies.get('user_hash')
    if user_cookie is not None:
        if users.find_one({'user_data.4': user_cookie})['user_data'][4] == user_cookie:
            print('ok')
            return redirect('/workspace', 302)
    return templateLoader.get_template('register.html').render(error=error)


@app.route('/registration', methods=["POST", "GET"])
def registration():
    global user_id
    user_name = request.form.get('username')
    user_password = request.form.get('password')
    user_email = request.form.get('email')

    if users.count_documents({'user_data.0': user_name}) > 0 or users.count_documents({'user_data.1': user_email}) > 0:
        return register_page("This login or email has been already used")

    global user_hash
    user_hash = secrets.token_hex(nbytes=64)
    while users.count_documents({'user_data.4': user_hash}) > 0:
        secrets.token_hex(nbytes=64)

    resp = make_response(redirect('/login', 302))
    resp.set_cookie('user_hash', str(user_hash), max_age=60 * 60 * 24 * 7)

    users.insert_one({'user_data_id': user_id, 'user_data': [user_name, user_email, user_password, user_id, user_hash]})
    user_id += 1
    users.update_one({"user_id_counter": {"$exists": "true"}}, {"$set": {"user_id_counter": user_id}})

    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    user_cookie = request.cookies.get('user_hash')
    print("cookie:", user_cookie)

    if user_cookie is not None:
        if users.find_one({'user_data.4': user_cookie})['user_data'][4] == user_cookie:
            print('ok')
            return redirect('/workspace', 302)
    return templateLoader.get_template('login.html').render()


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    user_name_login = request.form.get('username_login')
    user_login_password = request.form.get('password_login')

    if users.count_documents({'user_data.0': user_name_login}) > 0:
        if users.find_one({'user_data.0': user_name_login})['user_data'][2] == user_login_password:
            resp = make_response(redirect('/workspace', 302))
            resp.set_cookie('user_hash', str(users.find_one({'user_data.0': user_name_login})['user_data'][4]), max_age=60 * 60 * 24 * 7)
            return resp
    return redirect('/login', 302)


@app.route('/set_cookie', methods=['POST', 'GET'])
def set_cookie():
    global user_hash
    resp = make_response(redirect('/login', 302))
    resp.set_cookie('user_hash', str(user_hash), max_age=60*60*24*7)
    return resp


@app.route('/workspace', methods=['POST', 'GET'])
def workspace():
    if request.method == "POST":
        board_redirect = request.form.get('board_redirect')
        print(board_redirect)
        return redirect(url_for("workspace_section", section=board_redirect))
    else:
        a = []
        for i in range(boards.count_documents({'board_name': {"$exists": "true"}})):
            a.append(boards.find({'board_name': {"$exists": "true"}})[i]['board_name'])
        print(a)
        return templateLoader.get_template('workspace.html').render(boards=a)


@app.route('/workspace/<section>', methods=['POST', 'GET'])
def workspace_section(section):
    assert section == request.view_args['section']
    return templateLoader.get_template('board_template.html').render(section=section)


@app.route('/workspace/add_board', methods=['POST', 'GET'])
def add_board():
    global board_id
    board_name = request.form.get('board_name')
    print('f', board_name)
    board_id += 1
    boards.update_one({"board_id_counter": {"$exists": "true"}}, {"$set": {"board_id_counter": board_id}})
    boards.insert_one({'board_id': board_id, 'board_name': board_name})
    return redirect('/workspace', 302)


@app.route('/status', methods=["GET"])
def status():
    return {'status': 'ok'}


app.run(host="0.0.0.0", port=1000)
