from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('task', __name__)

@bp.route('/tasks/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, title, body, created, user_id, username'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('task/index.html', tasks=tasks)


@bp.route('/add-task', methods=('GET', 'POST'))
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (title, body, user_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('task.index'))

    return render_template('task/add_task.html')


def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT t.id, title, body, created, user_id, username'
        ' FROM task t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and task['user_id'] != g.user['id']:
        abort(403)

    return task


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        print('request was post')
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('task.index'))

    return render_template('task/update.html', task=task)


@bp.route('/<int:id>/delete', methods=('DELETE', 'GET'))
@login_required
def delete(id):
    task = get_task(id)
    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (task['id'],))
    db.commit()
    return redirect(url_for('task.index'))