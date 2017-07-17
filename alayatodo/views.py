from alayatodo import (
    app,
    db
    )
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify,
    abort
    )
from math import ceil
from db import (
    User,
    Todo
    )

PER_PAGE = 5

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user'] = user.id
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = Todo.query.get(id)
    return render_template('todo.html', todo=todo)


@app.route('/todo', defaults={'page':1}, methods=['GET'])
@app.route('/todo/', defaults={'page':1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
@app.route('/todo/page/<int:page>/', methods=['GET'])
def todos(page):
    if not session.get('logged_in'):
        return redirect('/login')

    todos = Todo.query.filter_by(user_id=session['user'])
    
    total_items = todos.count()
    last_page = int(ceil(total_items / float(PER_PAGE)))
    todos = todos.limit(PER_PAGE)
    todos = todos.offset(((page-1)*PER_PAGE))
    
    return render_template('todos.html', todos=todos, page=page, last_page=last_page)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    user = User.query.get(session['user'])
    description = request.form.get('description')
    if len(description) > 0:
        todo = Todo(user=user, description=description, completed=0)
        db.session.add(todo)
        db.session.commit()
    else:
        flash('You must provide a description')

    flash('Todo inserted')    
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()

    flash('Todo deleted')
    return redirect('/todo')

@app.route('/todo/complete/<id>', methods=['POST'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    todo = Todo.query.get(id)
    todo.completed = 1
    db.session.commit();

    flash('Todo completed')
    return redirect('/todo')

@app.route('/todo/uncomplete/<id>', methods=['POST'])
def todo_uncomplete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    todo = Todo.query.get(id)
    todo.completed = 0
    db.session.commit()

    flash('Todo uncompleted')
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_json(id):
    todo = Todo.query.get(id)
    if not todo:
        return abort(404)
    return jsonify(id=todo.id, user_id=todo.user.id, description=todo.description, completed=todo.completed)
