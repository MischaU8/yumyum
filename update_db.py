#!/usr/bin/env python3

from datetime import timezone
import json
from pathlib import Path
import re
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
import git
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
import sqlite_utils

DATA_DIR = "_data/"
DB_PATH = f"{DATA_DIR}/yumyum.db"
STATS_PATH = f"{DATA_DIR}/stats.json"

root = Path(__file__).parent.resolve()


def first_paragraph_text_only(html):
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.find("p").stripped_strings)


def created_changed_times(repo_path, ref="main"):
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref)))
    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times


def wikilinks_url_builder(label, base, end):
    return base + quote_plus(label)


def build_database(repo_path):
    all_times = created_changed_times(repo_path)
    db = sqlite_utils.Database(DB_PATH)
    video_table = db.table("video", pk="id")

    for filepath in root.glob("**/*_*.md"):
        # print(filepath)
        path = str(filepath.relative_to(root))
        path_slug = path.replace("/", "_")
        slug = filepath.stem
        url = "https://github.com/MischaU8/yumyum/blob/main/{}".format(path)
        md_id = "_".join(filepath.stem.split("_")[1:])
        md_full = Path(filepath).read_text()
        md = markdown.Markdown(
            extensions=[
                "meta",
                WikiLinkExtension(
                    base_url="/yumyum/search?q=",
                    build_url=wikilinks_url_builder,
                ),
            ]
        )
        html = md.convert(md_full)
        md_meta = md.Meta
        md_body = md_full.split("\n\n", 1)[1]

        if md_meta["id"][0] != md_id:
            print(f"WARN: Mismatch in ID between '{filepath}' and metadata {md_id}")
            continue

        print(md_meta)
        data = {
            "id": md_meta["id"][0],
            "path": path_slug,
            "slug": slug,
            "topic": path.split("/")[0],
            "title": md_meta["title"][0],
            "url": url,
            "description": md_meta["description"][0],
            "body": md_body,
            "html": html,
            "upload_date": md_meta["uploaded"][0],
            "duration": md_meta["duration"][0],
            "plasticity_version": md_meta["version"][0],
        }
        # Populate summary
        data["summary"] = first_paragraph_text_only(data.get("html") or "")
        if path in all_times:
            data.update(all_times[path])
        with db.conn:
            video_table.upsert(data, alter=True)
        print(f"Saved {data['id']}")

    video_table.enable_fts(
        ["title", "body"], tokenize="porter", create_triggers=True, replace=True
    )

    # update stats
    stats_table = db.table("video_stats", pk="id")
    with open(STATS_PATH, "r") as f:
        video_stats = json.load(f)

    for video_id, data in video_stats.items():
        data["id"] = video_id
        with db.conn:
            stats_table.upsert(data, alter=True)


def sync_manual():
    db = sqlite_utils.Database(DB_PATH)
    manual_table = db.table("manual", pk="id")

    for page in ["tool", "common", "sketch", "solid"]:
        filepath = (
            root
            / "_data"
            / "plasticity-unofficial-document"
            / "pages"
            / (page + ".en.mdx")
        )
        content = Path(filepath).read_text()
        print("Processing manual index ", page)

        for i, line in enumerate(content.split("\n")):
            if i < 3:
                continue
            # print(l)
            if not line.startswith("|"):
                continue
            row = re.split(r"\s*\|\s*", line)
            if len(row) != 5:
                continue
            command, shortcut, description = row[1:4]
            if not command or command.startswith("**"):
                continue
            # print(command, shortcut, description)
            shortcut = shortcut.replace("<kbd>", "").replace("</kbd>", "")

            m = re.match(r"\[(.*)\]\((.*)\)", command)
            if m:
                command_name = m.group(1)
                command_link = m.group(2)
                # command_name = command_name.replace(" 🚧", "")

                # print("=>", command_name, command_link)
                # print(shortcut)
                # print(description)

                data = {
                    "id": command_link,
                    "command": command_name,
                    "url": "https://plasticitydoc.vercel.app/" + command_link,
                    "shortcut": shortcut,
                    "description": description,
                }

                with db.conn:
                    manual_table.upsert(data, alter=True)

            else:
                print(f"Invalid line {i}: {line}")

    manual_table.enable_fts(
        ["command", "description"],
        tokenize="porter",
        create_triggers=True,
        replace=True,
    )


if __name__ == "__main__":
    # build_database(root)
    sync_manual()
