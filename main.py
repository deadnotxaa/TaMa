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
tasks = db.tasks
column = db.column

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
templateLoader = Environment(loader=FileSystemLoader(searchpath='./templates'))
app = Flask(__name__, static_folder='./static', static_url_path='/static')
app.debug = True
CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
user_id = users.find({"user_id_counter": {"$exists": "true"}})[0]["user_id_counter"]
board_id = boards.find({"board_id_counter": {"$exists": "true"}})[0]['board_id_counter']
column_id = column.find({"column_id_counter": {"$exists": "true"}})[0]['column_id_counter']
user_hash = 0
boards_info = []
#for i in boards.find({'board_name': {"$exists": "true"}})[0]:
#    boards_info.append(i)
#boards_info.append(i)


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
    user_boards = []

    if users.count_documents({'user_data.0': user_name}) > 0 or users.count_documents({'user_data.1': user_email}) > 0:
        return register_page("This login or email has been already used")

    global user_hash
    user_hash = secrets.token_hex(nbytes=64)
    while users.count_documents({'user_data.4': user_hash}) > 0:
        secrets.token_hex(nbytes=64)

    resp = make_response(redirect('/login', 302))
    resp.set_cookie('user_hash', str(user_hash), max_age=60 * 60 * 24 * 7)

    users.insert_one({'user_data_id': user_id, 'user_data': [user_name, user_email, user_password, user_id, user_hash, user_boards]})
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
    user_cookie = request.cookies.get('user_hash')
    print("cookie:", user_cookie)

    if user_cookie is None:
        return redirect('/login', 302)

    if request.method == "POST":
        board_redirect = request.form.get('board_redirect')
        print(board_redirect)
        return redirect(url_for("workspace_section", section=board_redirect))
    else:
        a = []
        b = []
        for i in range(boards.count_documents({'board_name': {"$exists": "true"}})):
            a.append((boards.find({'board_name': {"$exists": "true"}})[i]['board_name'], (boards.find({'board_id': {"$exists": "true"}})[i]['board_id'])))

        for i in a:
            x = i[0]
            y = i[1]
            if y in users.find_one({'user_data.4': user_cookie})['user_data'][5]:
                b.append((x, y))

        # print(a)
        # print(boards_info)
        return templateLoader.get_template('workspace.html').render(boards=b)


@app.route('/workspace/<section>', methods=['POST', 'GET'])
def workspace_section(section):
    user_cookie = request.cookies.get('user_hash')
    print("cookie:", user_cookie)

    if user_cookie is None:
        return redirect('/login', 302)

    if int(section) not in users.find_one({'user_data.4': user_cookie})['user_data'][5]:
        return redirect('/login', 302)

    # assert section == request.view_args['section']
    print()
    current_board_name = boards.find_one({'board_id': int(section)})['board_name']
    print(current_board_name)
    return templateLoader.get_template('board_template.html').render(section=section, board_name=current_board_name)


@app.route('/workspace/add_board', methods=['POST', 'GET'])
def add_board():
    global column_id
    global board_id
    board_name = request.form.get('board_name')
    if board_name == "":
        return redirect('/workspace', 302)

    user_cookie = request.cookies.get('user_hash')
    print("cookie:", user_cookie)

    if user_cookie is not None:
        a = users.find_one({'user_data.4': user_cookie})['user_data'][5]
        a.append(board_id + 1)
        users.update_one({'user_data.4': user_cookie}, {"$set": {"user_data.5": a}})

    print('f', board_name)
    board_id += 1
    boards.update_one({"board_id_counter": {"$exists": "true"}}, {"$set": {"board_id_counter": board_id}})
    boards.insert_one({'board_id': board_id, 'board_name': board_name})

    column.insert_one({'column_id': column_id, 'board_id': board_id, 'name': 'to-do'})
    column_id += 1
    column.update_one({"column_id_counter": {"$exists": "true"}}, {"$set": {"column_id_counter": column_id}})

    return redirect('/workspace', 302)


@app.route('/workspace/add_task', methods=["GET", "POST"])
def add_task():
    return 'ok'


@app.route('/workspace/add_column', methods=["POST", "GET"])
def add_column():
    return 'ok'


@app.route('/status', methods=["GET", "POST"])
def status():
    return {'status': 'ok'}


@app.route('/workspace/get_info', methods=["GET", "POST"])
def get_info():
    current_board_id = request.json

    return {'info': 'ok'}


app.run(host="0.0.0.0", port=1000)
