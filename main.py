import jinja2
from flask import Flask, request, make_response, render_template, url_for, jsonify
from jinja2 import Template, FileSystemLoader, Environment
from werkzeug.utils import redirect
from pymongo import MongoClient
import secrets
from flask_cors import CORS
from bson.json_util import dumps, loads

# just for a joke
if False:
    pass
else:
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
task_id = tasks.find({"task_id_counter": {"$exists": "true"}})[0]['task_id_counter']
user_hash = 0
boards_info = []


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

    # just for a joke 2
    if False:
        pass
    else:
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

        return templateLoader.get_template('workspace.html').render(boards=b)


@app.route('/workspace/<section>', methods=['POST', 'GET'])
def workspace_section(section):
    user_cookie = request.cookies.get('user_hash')
    print("cookie:", user_cookie)

    if user_cookie is None:
        return redirect('/login', 302)

    if int(section) not in users.find_one({'user_data.4': user_cookie})['user_data'][5]:
        return redirect('/login', 302)

    current_board_name = boards.find_one({'board_id': int(section)})['board_name']
    print(current_board_name)

    current_user_name = users.find_one({'user_data.4': user_cookie})['user_data'][0]

    return templateLoader.get_template('board_template.html').render(section=section, board_name=current_board_name, user=current_user_name)


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


@app.route('/status', methods=["GET", "POST"])
def status():
    return {'status': 'ok'}


@app.route('/workspace/get_info', methods=["GET", "POST"])
def get_info():
    current_board_id = request.json
    current_board_id_num = current_board_id['id']
    print(current_board_id_num)
    a = {}
    print(column.count_documents({'board_id': int(current_board_id_num)}))
    for i in range(column.count_documents({'board_id': int(current_board_id_num)})):
        print(a)
        x = column.find({'board_id': int(current_board_id_num)})[i]['column_id']
        y = column.find({'board_id': int(current_board_id_num)})[i]['name']
        a.update({str(i): {'column_id':   x, 'column_name': y}})
        print({str(i): {'column_id':   x, 'column_name': y}})

    return a


@app.route('/add_column', methods=["GET", "POST"])
def add_column():
    global column_id
    add_column_data = request.json
    print('1', add_column_data)

    add_name = add_column_data['name']
    add_id = int(add_column_data['id'])
    print(add_id)

    column_id += 1
    column.insert_one({'column_id': column_id, 'board_id': add_id, 'name': add_name})
    column.update_one({"column_id_counter": {"$exists": "true"}}, {"$set": {"column_id_counter": column_id}})

    return {'column_id': column_id}


@app.route('/add_task', methods=['POST', 'GET'])
def add_task():
    global task_id
    task_id += 1

    add_task_data = request.json
    print('task1', add_task_data)

    add_name = add_task_data['name']
    add_task_column = add_task_data['column']

    tasks.insert_one({'task_name': add_name, 'task_column': add_task_column, 'task_id': task_id})
    tasks.update_one({"task_id_counter": {"$exists": "true"}}, {"$set": {"task_id_counter": task_id}})
    return {'id': task_id}


@app.route('/get_tasks', methods=['POST', 'GET'])
def get_tasks():
    get_column_tasks = request.json
    a = {}
    current_task_id = tasks.find({"task_id_counter": {"$exists": "true"}})[0]['task_id_counter']
    print(type(get_column_tasks), get_column_tasks)

    cnt = 0
    print('get req')
    print(get_column_tasks)
    for i in get_column_tasks:
        print(i, tasks.count_documents({'task_column': str(i)}))
        for j in range(tasks.count_documents({'task_column': str(i)})):
            print(a)
            x = tasks.find({'task_column': str(i)})[j]['task_id']
            y = tasks.find({'task_column': str(i)})[j]['task_name']
            z = tasks.find({'task_column': str(i)})[j]['task_column']
            a.update({str(cnt): {'task_id': x, 'task_name': y, 'column_id': int(z)}})
            print(1, {str(cnt): {'task_id': x, 'task_name': y, 'column_id': z}})
            cnt += 1
    return a


@app.route('/change_column', methods=['POST', 'GET'])
def change_column():
    get_change_info = request.json
    print(get_change_info)

    new_column_id = get_change_info['to']
    changing_task_id = get_change_info['task_id']

    tasks.update_one({"task_id": int(changing_task_id)}, {"$set": {"task_column": str(new_column_id)}})
    print('change_column', new_column_id, changing_task_id)

    return {'status': 'ok'}


@app.route('/user_exit', methods=['POST', 'GET'])
def user_exit():
    user_cookie = request.cookies.get('user_hash')
    resp = make_response(redirect('/', 302))
    resp.set_cookie('user_hash', '', expires=0)
    return resp


@app.route('/delete_column', methods=['POST', 'GET'])
def delete_column():
    get_column_id = request.json
    get_column_id = get_column_id['id']

    for i in range(tasks.count_documents({'task_column': get_column_id})):
        x = tasks.find({'column_id': get_column_id})
        tasks.remove(x)
        print(x)
    return {'status': 'ok'}


@app.route('/delete_task', methods=['POST', 'GET'])
def delete_task():
    get_task_id = request.json
    get_task_id = get_task_id['id']
    tasks.remove({'task_id': get_task_id})
    return {'status': 'ok'}


app.run(host="0.0.0.0", port=1000)
