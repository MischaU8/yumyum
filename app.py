#!/usr/bin/env python3

import glob
import json
from pathlib import Path
import sqlite3

from flask import Flask, g, make_response, render_template, request
from flask_htmx import HTMX
import markdown

# https://python-markdown.github.io/extensions/wikilinks/
from markdown.extensions.wikilinks import WikiLinkExtension


DB_PATH = "_data/yumyum.db"

app = Flask(__name__, static_folder='_static', template_folder='_templates')
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
        print(f"Searching for '{q}'")
        videos = query_db("select * from videos where title like ?", [f"%{q}%"])
    if htmx:
        r = make_response(render_template("partials/search_result.html", videos=videos))
        r.headers.set("Cache-Control", "no-store, max-age=0")
        return r

    return render_template("search.html", q=q, videos=videos)


@app.route("/video/<video_id>")
def video(video_id):
    video = query_db("select * from videos where id = ?", [video_id], one=True)

    notes_files = glob.glob(f"**/*_{video_id}.md")
    if len(notes_files) == 1:
        notes_md = Path(notes_files[0]).read_text()

        md = markdown.Markdown(
            extensions=[
                "meta",
                WikiLinkExtension(base_url="/tag/", html_class="is-underlined"),
            ]
        )
        notes_html = md.convert(notes_md)
        md_meta = md.Meta
    else:
        notes_html = None
        md_meta = {}

    return render_template(
        "video.html",
        video=video,
        notes_html=notes_html,
        md_meta=md_meta,
    )


@app.route("/")
def home():
    random_videos = query_db("select * from videos order by random() limit 10")
    num_videos = query_db("select count(*) from videos", one=True)
    return render_template("index.html", videos=random_videos, num_videos=num_videos[0])
