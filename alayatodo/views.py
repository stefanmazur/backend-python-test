from alayatodo import app
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

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
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
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', defaults={'page':1}, methods=['GET'])
@app.route('/todo/', defaults={'page':1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
@app.route('/todo/page/<int:page>/', methods=['GET'])
def todos(page):
    if not session.get('logged_in'):
        return redirect('/login')

    cur = g.db.execute("SELECT COUNT(*) FROM todos WHERE user_id=%i" % session['user']['id'])
    total_items = cur.fetchone()["COUNT(*)"]
    last_page = int(ceil(total_items / float(PER_PAGE)))
    
    cur = g.db.execute("SELECT * FROM todos WHERE user_id = ? LIMIT ? OFFSET ?", (session['user']['id'], PER_PAGE, ((page-1)*PER_PAGE)))
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos, page=page, last_page=last_page)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    description = request.form.get('description')
    if len(description) > 0:
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], request.form.get('description', ''))
        )
        g.db.commit()
    else:
        flash('You must provide a description')

    flash('Todo inserted')    
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()

    flash('Todo deleted')
    return redirect('/todo')

@app.route('/todo/complete/<id>', methods=['POST'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET completed = 1 WHERE id ='%s'" % id)
    g.db.commit()

    flash('Todo completed')
    return redirect('/todo')

@app.route('/todo/uncomplete/<id>', methods=['POST'])
def todo_uncomplete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET completed = 0 WHERE id ='%s'" % id)
    g.db.commit()

    flash('Todo uncompleted')
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    if not todo:
        return abort(404)
    return jsonify(id=todo['id'], user_id=todo['user_id'], description=todo['description'], completed=todo['completed'])
