#!/usr/bin/env python3

import sqlite3
from flask import Flask, g, render_template, request
from flask_htmx import HTMX

DB_PATH = "data/yumyum.db"

app = Flask(__name__)
htmx = HTMX(app)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/search")
def search():
    q = request.args.get("q")
    videos = []
    if q:
        print("Searching for ", q)
        # videos = [{"id": 1, "title": q, "description": q}]
        videos = query_db("select * from videos where title like ?", [f"%{q}%"])
    if htmx:
        return render_template("partials/search_result.html", videos=videos)
    return render_template("search.html", videos=videos)


@app.route("/")
def home():
    return render_template("index.html")
