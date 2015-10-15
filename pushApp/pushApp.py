# -*- coding: utf-8 -*-


import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from contextlib import closing
import requests
import time
import threading

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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def send_push(url):
    print 'send_push'
    r = requests.post(url, headers={"TTL": 60})
    print r.text
    # return r.status_code

def spawn_push_thread(url, delay):
    print 'spawn_push_thread', delay
    t = threading.Timer(delay, send_push, [url])
    t.start()


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
    spawn_push_thread(request.form['url'], float(request.form['delay']))
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
