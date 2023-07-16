#!/usr/bin/env python3

import json
from pathlib import Path
import re
from typing import cast
from xml.etree import ElementTree as ET

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
import sqlite_utils

DATA_DIR = "_data/"
DB_PATH = f"{DATA_DIR}/yumyum.db"
JSON_FIELDS = [
    "id",
    "title",
    "description",
    "thumbnail",
    "webpage_url",
    "upload_date",
    "epoch",
    "duration",
    "view_count",
    "like_count",
    "comment_count",
]

def main():
    db = sqlite_utils.Database(DB_PATH)
    ensure_tables(db)

    for md_path in Path(".").glob("**/*_*.md"):
        # print(md_path)
        md_id = '_'.join(md_path.stem.split('_')[1:])
        notes_md = Path(md_path).read_text()
        md = markdown.Markdown(
            extensions=[
                "meta",
                WikiLinkExtension(base_url="/tag/", html_class="is-underlined"),
            ]
        )
        notes_html = md.convert(notes_md)
        md_meta = md.Meta

        if md_meta["id"][0] != md_id:
            print(f"WARN: Mismatch in ID between filename '{md_path}' and metadata {md_id}")
            continue

        print(md_meta)
        data = {
            "id": md_meta["id"][0],
            "title": md_meta["title"][0],
            "description": md_meta["description"][0],
            "markdown": notes_md,
            "html": notes_html,
            "tags": re.split(r",\s+", md_meta["tags"][0]),
            "upload_date": md_meta["uploaded"][0],
            "duration": md_meta["duration"][0],
            "plasticity_version": md_meta["version"][0],
        }
        
        db["videos"].insert(data, replace=True)
        print(f"Saved {data['id']}")


def _ensure_table(db: sqlite_utils.Database, table_name: str, *args, **kwargs):
    if table_name not in db.table_names():
        table = cast(sqlite_utils.db.Table, db.table(table_name))
        table.create(*args, **kwargs)


def ensure_tables(db: sqlite_utils.Database):
    _ensure_table(
        db,
        "videos",
        {
            "id": str,
            "title": str,
            "description": str,
            "markdown": str,
            "html": str,
            "tags": str,
            "upload_date": str,
            "duration": int,
            "plasticity_version": str,
        },
        pk="id",
    )


if __name__ == "__main__":
    main()
