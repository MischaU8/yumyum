#!/usr/bin/env python3

from flask import Flask, render_template, request
from flask_htmx import HTMX

app = Flask(__name__)
htmx = HTMX(app)


@app.route("/search")
def search():
    q = request.args.get('q')
    videos = []
    if q:
        print("Searching for ", q)
        videos = [{"id": 1, "title": q, "description": q}]
    if htmx:
        return render_template("partials/search_result.html", videos=videos)
    return render_template("search.html", videos=videos)


@app.route("/")
def home():
    return render_template("index.html")
