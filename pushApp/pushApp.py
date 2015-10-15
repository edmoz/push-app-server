# -*- coding: utf-8 -*-


import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from contextlib import closing
import requests


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'pushApp.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('PUSHAPP_SETTINGS', silent=True)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def send_push(url):
    r = requests.post(url, headers={"TTL": 60})
    print r.status
    return

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.route('/')
def show_urls():
    cur = g.db.execute('select url, delay from urls order by id desc')
    urls = [dict(url=row[0], delay=row[1]) for row in cur.fetchall()]
    return render_template('show_urls.html', urls=urls)

@app.route('/add', methods=['POST'])
def add_url():
    print 'add_url'
    print request.form['url']
    g.db.execute('insert into urls (url, delay) values (?, ?)',
                 [request.form['url'], request.form['delay']])
    g.db.commit()
    flash('New url was successfully posted')
    send_push(request.form['url'])
    return redirect(url_for('show_urls'))

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    app.run()
    # uncomment to create db
    # init_db()
