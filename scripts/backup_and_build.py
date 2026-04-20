#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import posixpath
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CURRENT_DIR = REPO_ROOT / "CURRENT"
VERSIONS_DIR = REPO_ROOT / "VERSIONS"
SITE_DIR = REPO_ROOT / "SITE"
PUBLIC_DIR = SITE_DIR / "PUBLIC_READ"
ASSISTANT_DIR = SITE_DIR / "ASSISTANT_READ"
PRESERVE_SITE = {"CNAME", ".nojekyll"}
META_KEYS = {
    "Статус",
    "Версия",
    "Дата первого принятия",
    "Текущая редакция",
    "История поправок",
    "Уровень доступа",
    "Историческая принадлежность",
    "Связанные закрытые документы",
    "Коды связанных закрытых документов",
}
PUBLIC_ALLOWED = {"PUBLIC"}
ASSISTANT_ALLOWED = {"PUBLIC", "SERVICE"}


def run_git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def changed_current_files() -> list[Path]:
    parent_check = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if parent_check.returncode != 0:
        return []
    output = run_git("diff", "--name-only", "HEAD^", "HEAD", "--", "CURRENT")
    files: list[Path] = []
    for line in output.splitlines():
        line = line.strip()
        if not line.endswith(".txt"):
            continue
        full = REPO_ROOT / line
        if full.exists():
            files.append(full)
    return files


def backup_previous_versions(files: list[Path]) -> None:
    if not files:
        return
    prev_sha = run_git("rev-parse", "--short", "HEAD^")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for current_file in files:
        rel = current_file.relative_to(CURRENT_DIR)
        git_path = current_file.relative_to(REPO_ROOT).as_posix()
        show = subprocess.run(
            ["git", "show", f"HEAD^:{git_path}"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if show.returncode != 0:
            continue
        old_content = show.stdout
        target_dir = VERSIONS_DIR / rel.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        target_name = f"{rel.stem}__backup_from_{prev_sha}__{stamp}.txt"
        target_path = target_dir / target_name
        if not target_path.exists():
            target_path.write_text(old_content, encoding="utf-8")


def relative_url(from_file: Path, to_file: Path) -> str:
    return posixpath.relpath(to_file.as_posix(), from_file.parent.as_posix())


def github_urls(repo: str, current_rel: Path) -> tuple[str, str]:
    git_path = current_rel.as_posix()
    if not repo:
        return "#", "#"
    edit_url = f"https://github.com/{repo}/edit/main/{git_path}"
    history_url = f"https://github.com/{repo}/commits/main/{git_path}"
    return edit_url, history_url


def parse_meta(text: str) -> tuple[str, dict[str, str], str]:
    lines = text.splitlines()
    title = lines[1].strip() if len(lines) > 1 and lines[0].strip() == "BVK CANON" else (lines[0].strip() if lines else "Untitled")
    meta: dict[str, str] = {}
    body_start = 0
    for idx, line in enumerate(lines):
        if ":" in line and idx < 20:
            k, v = line.split(":", 1)
            key = k.strip()
            if key in META_KEYS or key == "Назначение":
                meta[key] = v.strip()
                body_start = idx + 1
                continue
        if idx > 8 and line.strip():
            body_start = idx
            break
    body = "\n".join(lines[body_start:]).strip()
    return title, meta, body


def clean_site_dir() -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for item in list(SITE_DIR.iterdir()):
        if item.name in PRESERVE_SITE:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    ASSISTANT_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")


def all_current_txt() -> list[Path]:
    return sorted(CURRENT_DIR.rglob("*.txt"))


def access_level(meta: dict[str, str]) -> str:
    return meta.get("Уровень доступа", "PUBLIC").strip().upper() or "PUBLIC"


def visible_in_public(meta: dict[str, str]) -> bool:
    return access_level(meta) in PUBLIC_ALLOWED


def visible_in_assistant(meta: dict[str, str]) -> bool:
    return access_level(meta) in ASSISTANT_ALLOWED


def render_document(current_file: Path, out_root: Path, repo: str, audience: str) -> tuple[str, str]:
    rel_current = current_file.relative_to(REPO_ROOT)
    rel_under_current = current_file.relative_to(CURRENT_DIR)
    txt_target = out_root / "txt" / rel_under_current
    html_target = out_root / "html" / rel_under_current.with_suffix(".html")
    txt_target.parent.mkdir(parents=True, exist_ok=True)
    html_target.parent.mkdir(parents=True, exist_ok=True)

    text = current_file.read_text(encoding="utf-8")
    txt_target.write_text(text, encoding="utf-8")

    title, meta, _body = parse_meta(text)
    edit_url, history_url = github_urls(repo, rel_current)
    txt_url = relative_url(html_target, txt_target)
    index_url = relative_url(html_target, out_root / "index.html")
    recovery_url = relative_url(html_target, out_root / "RECOVERY_SCAN.html")

    hidden_public_keys = {"Закрытые ссылки для рабочего слоя"}
    meta_rows = []
    for key, value in meta.items():
        if not value:
            continue
        if audience == "public" and key in hidden_public_keys:
            continue
        meta_rows.append(f"<tr><th>{html.escape(key)}</th><td>{html.escape(value)}</td></tr>")
    meta_rows_html = "\n    ".join(meta_rows)

    page = f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <title>{html.escape(title)} - BVK Canon</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 1.5rem; }}
    th, td {{ border: 1px solid #ccc; padding: .5rem; text-align: left; vertical-align: top; }}
    pre {{ white-space: pre-wrap; background: #f6f6f6; padding: 1rem; border: 1px solid #ddd; }}
    .links a {{ margin-right: 1rem; }}
  </style>
</head>
<body>
  <p><a href=\"{index_url}\">Полный индекс</a> | <a href=\"{recovery_url}\">Recovery Scan</a></p>
  <h1>{html.escape(title)}</h1>
  <table>
    {meta_rows_html}
  </table>
  <p class=\"links\">
    <a href=\"{txt_url}\">Открыть текущий TXT</a>
    <a href=\"{html.escape(edit_url)}\">Редактировать на GitHub</a>
    <a href=\"{html.escape(history_url)}\">История на GitHub</a>
  </p>
  <pre>{html.escape(text)}</pre>
</body>
</html>
"""
    html_target.write_text(page, encoding="utf-8")
    return rel_under_current.as_posix(), html_target.relative_to(out_root).as_posix()


def is_key_doc(rel: str) -> bool:
    keys = {
        "00_INDEX/00_START_HERE.txt",
        "00_INDEX/MASTER_INDEX.txt",
        "00_INDEX/CHANGELOG.txt",
        "00_INDEX/LINK_MAP.txt",
        "00_INDEX/03_DATING_RULES_AND_PRIORITY.txt",
        "01_FOUNDATION/01_WORLD_CORE.txt",
        "01_FOUNDATION/02_STATE_IDENTITY.txt",
        "02_GOVERNANCE/01_CONSTITUTIONAL_FRAME.txt",
        "03_SOCIAL_ORDER/04_LABOR_CODE.txt",
        "03_SOCIAL_ORDER/05_HOUSING_CODE.txt",
        "04_ECONOMY/01_CURRENCY_AND_SOCIAL_STANDARD.txt",
        "05_TECH_AND_INFRA/01_TECH_MODEL.txt",
        "07_TIMELINE/01_TIMELINE_CORE_2026_2086.txt",
    }
    return rel in keys


def write_index(out_root: Path, docs: list[tuple[str, str]], title: str) -> None:
    grouped: dict[str, list[tuple[str, str]]] = {}
    for rel_txt, rel_html in docs:
        top = rel_txt.split("/", 1)[0]
        grouped.setdefault(top, []).append((rel_txt, rel_html))

    section_titles = {
        "00_INDEX": "Индекс",
        "01_FOUNDATION": "Foundation",
        "02_GOVERNANCE": "Governance",
        "03_SOCIAL_ORDER": "Social Order",
        "04_ECONOMY": "Economy",
        "05_TECH_AND_INFRA": "Tech and Infra",
        "06_ARCHIVE_AND_SITE": "Archive and Site",
        "07_TIMELINE": "Timeline",
        "08_NOVEL_LINK": "Novel Link",
    }

    sections_html = []
    for section in sorted(grouped):
        items = "\n".join(
            f'<li><a href="{html.escape(rel_html)}">{html.escape(rel_txt)}</a></li>'
            for rel_txt, rel_html in grouped[section]
        )
        sections_html.append(f"<h2>{html.escape(section_titles.get(section, section))}</h2><ul>{items}</ul>")

    page = f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <title>{html.escape(title)}</title>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p><a href=\"RECOVERY_SCAN.html\">Recovery Scan</a></p>
  {''.join(sections_html)}
</body>
</html>
"""
    (out_root / "index.html").write_text(page, encoding="utf-8")


def write_recovery(out_root: Path, docs: list[tuple[str, str]], title: str) -> None:
    items = "\n    ".join(
        f'<li><a href="{html.escape(rel_html)}">{html.escape(rel_txt)}</a></li>'
        for rel_txt, rel_html in docs if is_key_doc(rel_txt)
    )
    page = f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <title>{html.escape(title)}</title>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <ol>
    {items}
  </ol>
  <p><a href=\"index.html\">Полный индекс</a></p>
</body>
</html>
"""
    (out_root / "RECOVERY_SCAN.html").write_text(page, encoding="utf-8")


def build_site() -> None:
    clean_site_dir()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    public_docs: list[tuple[str, str]] = []
    assistant_docs: list[tuple[str, str]] = []

    for current_file in all_current_txt():
        text = current_file.read_text(encoding="utf-8")
        _title, meta, _body = parse_meta(text)
        if visible_in_public(meta):
            public_docs.append(render_document(current_file, PUBLIC_DIR, repo, "public"))
        if visible_in_assistant(meta):
            assistant_docs.append(render_document(current_file, ASSISTANT_DIR, repo, "assistant"))

    write_index(PUBLIC_DIR, public_docs, "BVK Canon Public Read")
    write_recovery(PUBLIC_DIR, public_docs, "BVK Recovery Scan")
    write_index(ASSISTANT_DIR, assistant_docs, "BVK Canon Assistant Read")
    write_recovery(ASSISTANT_DIR, assistant_docs, "BVK Assistant Recovery Scan")

    root_index = """<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <title>BVK Canon</title>
</head>
<body>
  <h1>BVK Canon</h1>
  <ul>
    <li><a href=\"PUBLIC_READ/index.html\">Публичный просмотр</a></li>
    <li><a href=\"ASSISTANT_READ/index.html\">Расширенный слой для ассистента</a></li>
  </ul>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(root_index, encoding="utf-8")


def main() -> None:
    backup_previous_versions(changed_current_files())
    build_site()


if __name__ == "__main__":
    main()
