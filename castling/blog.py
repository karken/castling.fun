from flask import ( 
        Blueprint, request, url_for, g, redirect, flash, render_template
        )

from werkzeug.exceptions import abort

from castling.auth import login_required
from castling.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
            'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
            ' FROM post as p JOIN user as u ON p.author_id = u.id'
            ' ORDER BY created DESC').fetchall();
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('insert into post (author_id, title, body) values (?, ?, ?)',
                    (g.user['id'], title, body))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
            'select p.id, title, body, created, author_id, username'
            ' from post p join user u on p.author_id = u.id'
            ' where p.id = ?', (id,)).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title required'
        elif not body:
            error = 'Message content required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('update post set title = ?, body = ?'
                    'where author_id=?', (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('delete from post where id=?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
