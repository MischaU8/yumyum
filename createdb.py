#!/usr/bin/env python3

import datetime
import glob
import json
from pprint import pprint as pp
import os.path
import re
from typing import cast
from xml.etree import ElementTree as ET

import sqlite_utils

DATA_DIR = "data/"
DB_PATH = f"{DATA_DIR}/yumyum.db"
JSON_FIELDS = [
    'id', 'title', 'description', 'thumbnail', 'webpage_url', 'upload_date', 'epoch',
    'duration', 'view_count', 'like_count', 'comment_count'
]


def get_info(info_file):
    data = {}

    with open(info_file) as f:
        raw_data = json.load(f)

    if raw_data['_type'] != 'video':
        return data

    for field in JSON_FIELDS:
        if field in raw_data:
            data[field] = raw_data[field]

    if "title" in data:
        data["title"] = re.sub(r"^Plasticity \|\s+", "", data["title"])

    if "description" in data:
        m = re.search(r"Version used in video:\s+([\d.]+)", data["description"])
        if m:
            data["plasticity_version"] = m.group(1)

    return data


def get_transcript(id, ttml_file, single=True):
    et = ET.parse(ttml_file)
    els = et.findall(".//{http://www.w3.org/ns/ttml}div/{http://www.w3.org/ns/ttml}p")
    dicts = [
        {
            "start": el.attrib["begin"],
            "end": el.attrib["end"],
            "lines": [el.text],
        }
        for el in els
    ]
    if single:
        for d in dicts:
            d["line"] = "\n".join(d.pop("lines"))    
    return {
        'id': id,
        'json': json.dumps(dicts)
    }
    

def main():
    db = sqlite_utils.Database(DB_PATH)
    ensure_tables(db)

    for info_file in glob.glob(f"{DATA_DIR}/*.info.json"):
        print(info_file)
        data = get_info(info_file)

        if len(data) > 0:
            # pp(data)
            db["videos"].insert(data, replace=True)
            # print(f"Saved {data['id']}")

            ttml_file = info_file.replace(".info.json", ".en.ttml")
            if os.path.isfile(ttml_file):
                transcript = get_transcript(data['id'], ttml_file)
                db["transcripts"].insert(transcript, replace=True)
                # print(f"Saved transcript {data['id']}")
            else:
                print(f"Skipping transcript {data['id']}")
        else:
            print(f"Skipping {info_file}")


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
            "thumbnail": str,
            "webpage_url": str,
            "upload_date": str,
            "epoch": int,
            "duration": int,
            "view_count": int,
            "like_count": int,
            "comment_count": int,
            "plasticity_version": str,
        },
        pk="id",
    )

    _ensure_table(
        db,
        "transcripts",
        {
            "id": str,
            "json": str,
        },
        pk="id",
    )


if __name__ == "__main__":
    main()
