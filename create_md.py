#!/usr/bin/env python3

import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from slugify import slugify

DATA_DIR = "_data/"
UNSORTED_DIR = "unsorted/"
DB_PATH = f"{DATA_DIR}/yumyum.db"
JSON_FIELDS = [
    "id",
    "title",
    "description",
    "upload_date",
    "epoch",
    "duration",
]


def fix_date(d):
    # turn yyyymmdd into yyyy-mm-dd
    return "-".join([d[:4], d[4:6], d[6:]])


def get_info(info_file):
    data = {}

    with open(info_file) as f:
        raw_data = json.load(f)

    if raw_data["_type"] != "video":
        return data

    for field in JSON_FIELDS:
        if field in raw_data:
            data[field] = raw_data[field]

    if "title" in data:
        data["title"] = re.sub(r"^Plasticity\s*\|\s*", "", data["title"])

    if "description" in data:
        VERSION_RE = r"Version used in video:\s*([\d.]+)"
        m = re.search(VERSION_RE, data["description"])
        if m:
            data["plasticity_version"] = m.group(1)
            data["description"] = re.sub(VERSION_RE, "", data["description"]).rstrip()
        data["description"] = re.sub(r"\s+", " ", data["description"])

    if "upload_date" in data:
        data["upload_date"] = fix_date(data["upload_date"])

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
    return dicts


def main():
    # create a set of all known markdown IDs
    md_ids = set()
    for md_path in Path(".").glob("**/*_*.md"):
        md_id = "_".join(md_path.stem.split("_")[1:])
        md_ids.add(md_id)

    for info_path in Path(DATA_DIR).glob("*.info.json"):
        print(info_path)
        data = get_info(info_path)

        if len(data) > 0:
            # check if a markdown file doesn't exist yet
            if data["id"] in md_ids:
                print(f"Skipping {info_path}, markdown exists {data['id']}")
                continue

            transcript_name = info_path.name.replace(".info.json", ".en.ttml")
            ttml_path = info_path.with_name(transcript_name)
            if ttml_path.is_file():
                transcript = get_transcript(data["id"], ttml_path)
                # db["transcripts"].insert(transcript, replace=True)
                # print(f"Saved transcript {data['id']}")
            else:
                print(f"Skipping transcript {data['id']}")
                transcript = []

            # create markdown file with metadata and transcript
            output = f"""ID: {data["id"]}
Title: {data["title"]}
Description: {data["description"]}
Duration: {data["duration"]}
Version: {data.get("plasticity_version", "")}
Uploaded: {data["upload_date"]}

"""
            output += "\n".join([t["line"] for t in transcript])
            if transcript:
                output += "\n"
            # print(output)

            # write to unsorted topic dir
            md_path = Path(
                UNSORTED_DIR, slugify(data["title"]) + "_" + data["id"] + ".md"
            )
            with open(md_path, "w") as f:
                f.write(output)
            print(md_path)
        else:
            print(f"Skipping {info_path}, no data found...")


if __name__ == "__main__":
    main()
