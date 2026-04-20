
#!/usr/bin/env python3
from pathlib import Path
import shutil
import html
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_DIR = REPO_ROOT / "CURRENT"
PUBLIC_DIR = REPO_ROOT / "PUBLIC_READ"

SECTION_TITLES = {
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

PUBLIC_ACCESS = {"PUBLIC"}
ASSISTANT_ACCESS = {"PUBLIC", "SERVICE"}

META_KEYS_ORDER = [
    "Статус",
    "Версия",
    "Дата первого принятия",
    "Текущая редакция",
    "История поправок",
    "Уровень доступа",
    "Историческая принадлежность",
    "Связанные закрытые документы",
    "Коды связанных закрытых документов",
]

RECOVERY_PUBLIC = [
    "00_INDEX/00_START_HERE.txt",
    "00_INDEX/MASTER_INDEX.txt",
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
]

RECOVERY_ASSISTANT_EXTRA = [
    "00_INDEX/04_SIMPLE_EDITING_WORKFLOW.txt",
    "00_INDEX/CLOSED_REFERENCE_REGISTRY.txt",
    "00_INDEX/05_CLOSED_LINKING_RULES.txt",
]

def reset_public_dir():
    PUBLIC_DIR.mkdir(exist_ok=True)
    for child in PUBLIC_DIR.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

def read_document(path: Path):
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # pick first two meaningful lines as brand + title
    nonempty_idx = [i for i, line in enumerate(lines) if line.strip()]
    brand = nonempty_idx and lines[nonempty_idx[0]].strip() or path.stem
    title = path.stem.replace("_", " ")
    title_idx = None
    if len(nonempty_idx) >= 2:
        title_idx = nonempty_idx[1]
        title = lines[title_idx].strip()
    elif nonempty_idx:
        title_idx = nonempty_idx[0]
        title = lines[title_idx].strip()

    meta = {}
    body_start = 0
    if title_idx is not None:
        i = title_idx + 1
        # skip blank lines
        while i < len(lines) and not lines[i].strip():
            i += 1
        started = False
        while i < len(lines):
            line = lines[i].rstrip()
            if not line.strip():
                if started:
                    i += 1
                    break
                i += 1
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
                started = True
                i += 1
                continue
            if started:
                break
            i += 1
        body_start = i
    body = "\n".join(lines[body_start:]).strip()

    access = meta.get("Уровень доступа", "PUBLIC").strip().upper() or "PUBLIC"
    return {
        "brand": brand,
        "title": title,
        "meta": meta,
        "body": body,
        "raw": raw,
        "access": access,
    }

def safe_title_from_rel(rel_path: str):
    return rel_path.replace(".txt", "").replace("/", " / ")

def build_doc_html(doc, rel_txt, root_mode="public"):
    # root_mode: public or assistant
    page_title = html.escape(doc["title"])
    brand = html.escape(doc["brand"])
    meta_rows = []
    # show metadata in predictable order, then any extras
    keys = []
    for k in META_KEYS_ORDER:
        if k in doc["meta"]:
            keys.append(k)
    for k in doc["meta"]:
        if k not in keys:
            keys.append(k)
    for key in keys:
        val = html.escape(doc["meta"].get(key, ""))
        meta_rows.append(f"<tr><th>{html.escape(key)}</th><td>{val}</td></tr>")
    meta_table = "\n".join(meta_rows)
    body_html = html.escape(doc["body"])
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{page_title} - BVK Canon</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 1.5rem; }}
    th, td {{ border: 1px solid #ddd; padding: .5rem; text-align: left; vertical-align: top; }}
    pre {{ white-space: pre-wrap; background: #f6f6f6; padding: 1rem; border: 1px solid #ddd; }}
    .links a {{ margin-right: 1rem; }}
    .note {{ color: #666; font-size: .95rem; }}
  </style>
</head>
<body>
  <p class="links"><a href="../../index.html">Полный индекс</a> <a href="../../RECOVERY_SCAN.html">Recovery Scan</a></p>
  <h1>{page_title}</h1>
  <p class="note">{brand} · {html.escape(rel_txt)}</p>
  <table>
    {meta_table}
  </table>
  <pre>{body_html}</pre>
</body>
</html>
"""

def build_index_html(items, title, intro, root_mode="public"):
    groups = {}
    for rel_txt, rel_html, doc in items:
        sec = rel_txt.split("/", 1)[0]
        groups.setdefault(sec, []).append((rel_txt, rel_html, doc))
    parts = [f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(intro)}</p>"""]
    if root_mode == "assistant":
        parts.append('<p><strong>Рабочий слой для ассистента.</strong> Здесь опубликованы документы уровней PUBLIC и SERVICE.</p>')
    else:
        parts.append('<p><a href="RECOVERY_SCAN.html">Recovery Scan</a></p>')
    for sec in sorted(groups.keys()):
        label = SECTION_TITLES.get(sec, sec)
        parts.append(f"<h2>{html.escape(label)}</h2><ul>")
        for rel_txt, rel_html, doc in sorted(groups[sec], key=lambda x: x[0]):
            parts.append(f'<li><a href="{html.escape(rel_html)}">{html.escape(rel_txt)}</a></li>')
        parts.append("</ul>")
    parts.append("</body></html>")
    return "\n".join(parts)

def build_recovery_html(items, title, assistant=False):
    wanted = list(RECOVERY_PUBLIC)
    if assistant:
        wanted.extend(RECOVERY_ASSISTANT_EXTRA)
    by_rel = {rel_txt: (rel_html, doc) for rel_txt, rel_html, doc in items}
    lines = [f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>Эта страница служит короткой точкой входа для быстрого восстановления контекста проекта.</p>
  <ol>"""]
    for rel in wanted:
        if rel in by_rel:
            rel_html, doc = by_rel[rel]
            label = doc["title"]
            lines.append(f'<li><a href="{html.escape(rel_html)}">{html.escape(label)}</a></li>')
    lines.extend(["</ol>", '<p><a href="index.html">Полный индекс</a></p>', "</body></html>"])
    return "\n".join(lines)

def gather_documents():
    docs = []
    for path in sorted(CURRENT_DIR.rglob("*.txt")):
        rel = path.relative_to(CURRENT_DIR).as_posix()
        doc = read_document(path)
        docs.append((rel, doc))
    return docs

def make_output():
    reset_public_dir()
    (PUBLIC_DIR / ".nojekyll").write_text("", encoding="utf-8")

    docs = gather_documents()

    public_items = []
    assistant_items = []

    for rel_txt, doc in docs:
        html_rel = f"html/{rel_txt[:-4]}.html"
        if doc["access"] in PUBLIC_ACCESS:
            target = PUBLIC_DIR / html_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(build_doc_html(doc, rel_txt, root_mode="public"), encoding="utf-8")
            public_items.append((rel_txt, html_rel, doc))

            atarget = PUBLIC_DIR / "assistant" / html_rel
            atarget.parent.mkdir(parents=True, exist_ok=True)
            atarget.write_text(build_doc_html(doc, rel_txt, root_mode="assistant"), encoding="utf-8")
            assistant_items.append((rel_txt, html_rel, doc))

        elif doc["access"] in ASSISTANT_ACCESS:
            atarget = PUBLIC_DIR / "assistant" / html_rel
            atarget.parent.mkdir(parents=True, exist_ok=True)
            atarget.write_text(build_doc_html(doc, rel_txt, root_mode="assistant"), encoding="utf-8")
            assistant_items.append((rel_txt, html_rel, doc))

    # Public root
    (PUBLIC_DIR / "index.html").write_text(
        build_index_html(
            public_items,
            "BVK Canon Public Read",
            "Открытый слой чтения канона Балтийской Кооперативной Республики.",
            root_mode="public",
        ),
        encoding="utf-8",
    )
    (PUBLIC_DIR / "RECOVERY_SCAN.html").write_text(
        build_recovery_html(public_items, "BVK Recovery Scan", assistant=False),
        encoding="utf-8",
    )

    # Assistant layer
    (PUBLIC_DIR / "assistant").mkdir(exist_ok=True)
    (PUBLIC_DIR / "assistant" / "index.html").write_text(
        build_index_html(
            assistant_items,
            "BVK Canon Assistant Read",
            "Расширенный слой чтения для восстановления контекста проекта.",
            root_mode="assistant",
        ),
        encoding="utf-8",
    )
    (PUBLIC_DIR / "assistant" / "RECOVERY_SCAN.html").write_text(
        build_recovery_html(assistant_items, "BVK Assistant Recovery Scan", assistant=True),
        encoding="utf-8",
    )

if __name__ == "__main__":
    make_output()
