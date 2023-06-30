from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages,
    make_response,
    json,
    session)
from validator import validate
from random import randint
import re


app = Flask(__name__)
app.secret_key = "SuperSecretKey"


# First page
@app.route('/page1')
def hello_world():
    return "Welcome to Flask!"


# Dynamic route
@app.route('/courses/<id>')
def courses(id):
    return render_template('/users/show.html', id=id)


# Search form
@app.get('/users')
def users_get():
    users = json.loads(request.cookies.get('users', json.dumps([])))
    sub_string = request.args.get('sub_string')
    messages = get_flashed_messages(with_categories=True)

    if sub_string:
        filtered_data = list(
            filter(lambda user: re.search(sub_string, user['name'], re.I),
                   users))
        return render_template('/users/index.html',
                               users=filtered_data,
                               searched=sub_string)
    return render_template('/users/index.html',
                           users=users,
                           messages=messages)


# Modifying form post route
@app.post('/users')
def create_new_user():
    user_data = request.form.to_dict()
    errors = validate(user_data)

    if errors:
        return render_template('/users/new_user.html',
                               errors=errors,
                               user=user_data)

    user_id = randint(1, 123)
    user_data['id'] = user_id
    users = json.loads(request.cookies.get('users', json.dumps([])))
    users.append(user_data)
    response = make_response(redirect(url_for('users_get'), code=302))
    response.set_cookie('users', json.dumps(users))
    flash("User was added successfully", "success")
    return response


# Modifying form get route
@app.route('/users/new')
def get_new_user():
    user = {'name': '', 'email': '', 'id': ''}
    errors = {}
    return render_template('/users/new_user.html', user=user, errors=errors)


# Update form route
@app.route('/users/<id>/edit')
def update_user(id):
    users = json.loads(request.cookies.get('users', json.dumps([])))

    for user in users:
        if user['id'] == int(id):
            errors = []
            return render_template('/users/edit.html',
                                   user=user,
                                   errors=errors)
    return "User not found", 404


# Update form post
@app.post('/users/<id>/patch')
def patch_user(id):
    data = request.form.to_dict()
    errors = validate(data)
    users = json.loads(request.cookies.get('users', json.dumps([])))
    if errors:
        for user in users:
            if user['id'] == int(id):
                errors = []
                return render_template('/users/edit.html',
                                       user=user,
                                       errors=errors), 422

    for item in users:
        if item['id'] == int(id):
            item['name'] = data['name']
            item['email'] = data['email']
            response = make_response(redirect(url_for('users_get'), code=302))
            response.set_cookie('users', json.dumps(users))
            flash("User has been updated", "success")
            return response
    return "User not found", 404


# Delete post
@app.route('/users/<id>/delete', methods=['POST'])
def deleting_user(id):
    users = json.loads(request.cookies.get('users', json.dumps([])))
    for item in users:
        if item['id'] == int(id):
            users.remove(item)
            break
    response = make_response(redirect(url_for('users_get'), code=302))
    response.set_cookie('users', json.dumps(users))
    flash("User has been deleted", "success")
    return response


# Session form
@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    current_user = session.get('user')
    return render_template('index.html',
                           messages=messages,
                           current_user=current_user)


# session creating
@app.post('/session/new')
def new_session():
    users = json.loads(request.cookies.get('users', json.dumps([])))
    email = request.form.get('email')

    for user in users:
        if email == user['email']:
            session['user'] = user
            return redirect(url_for('index'), code=302)
    flash("Wrong email", "error")
    return redirect(url_for('index'), code=302)


# session deleting
@app.route('/session/delete', methods=['POST', 'DELETE'])
def delete_session():
    session.pop('user')
    return redirect(url_for('index'), code=302)
