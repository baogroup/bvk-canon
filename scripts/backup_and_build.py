#!/usr/bin/env python3
from pathlib import Path
import shutil
import html

REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_DIR = REPO_ROOT / "CURRENT"
PUBLIC_DIR = REPO_ROOT / "PUBLIC_READ"

GITHUB_REPO_BASE = "https://github.com/baogroup/bvk-canon"
GITHUB_BRANCH = "main"

PUBLIC_ACCESS = {"PUBLIC"}
ASSISTANT_ACCESS = {"PUBLIC", "SERVICE"}

SECTION_TITLES = {
    "00_INDEX": "Rodyklės ir darbo taisyklės",
    "01_ARCHIVE": "2026 metų archyvas",
    "01_FOUNDATION": "Pagrindai",
    "02_GOVERNANCE": "Valdymas",
    "03_SOCIAL_ORDER": "Socialinė tvarka",
    "04_ECONOMY": "Ekonomika",
    "05_TECH_AND_INFRA": "Technologijos ir infrastruktūra",
    "06_ARCHIVE_AND_SITE": "Archyvas ir svetainė",
    "07_TIMELINE": "Chronologija",
    "08_NOVEL_LINK": "Pasakojimo sluoksnis",
    "09_NEWS_AND_NARRATIVE": "Naujienų ir naratyvo sluoksnis",
    "02_SYMBOLS_AND_IDENTITY": "Simboliai ir tapatybė",
}

SECTION_DESCRIPTIONS = {
    "00_INDEX": "Pagrindiniai indeksai, ryšių žemėlapiai ir darbo taisyklės.",
    "01_ARCHIVE": "Pirmųjų metų įrašai, kronikos, klausimai ir pirminiai dokumentai.",
    "01_FOUNDATION": "Pamatiniai būsimos Respublikos ir BVK pasaulio dokumentai.",
    "02_GOVERNANCE": "Valdymo, konstitucinio karkaso ir viešosios tvarkos dokumentai.",
    "03_SOCIAL_ORDER": "Darbo, būsto, šeimos, švietimo ir socialinės tvarkos modeliai.",
    "04_ECONOMY": "Ekonomikos, vidinės vertės, socialinio standarto ir gamybos kryptys.",
    "05_TECH_AND_INFRA": "Technologijų, infrastruktūros ir techninės sistemos dokumentai.",
    "06_ARCHIVE_AND_SITE": "Archyvo, prieigos lygių, svetainės ir publikavimo taisyklės.",
    "07_TIMELINE": "Istorinė ir projekcinė chronologija nuo 2026 iki 2086 metų.",
    "08_NOVEL_LINK": "Pasakojimo, romano ir paslėpto naratyvinio sluoksnio jungtys.",
    "09_NEWS_AND_NARRATIVE": "Naujienų sistemos, redakcinės taisyklės ir publikacijų logika.",
    "02_SYMBOLS_AND_IDENTITY": "Ankstyvi simboliai, ženklai, vėliavos ir vizualinės tapatybės paieška.",
}

META_KEYS_ORDER = [
    "Statusas", "Статус",
    "Versija", "Версия",
    "Pirmojo priėmimo data", "Дата первого принятия",
    "Dabartinė redakcija", "Текущая редакция",
    "Pakeitimų istorija", "История поправок",
    "Prieigos lygis", "Уровень доступа",
    "Istorinė priklausomybė", "Историческая принадлежность",
    "Susiję uždari dokumentai", "Связанные закрытые документы",
    "Susijusių uždarų dokumentų kodai", "Коды связанных закрытых документов",
]

RECOVERY_PUBLIC = [
    "00_INDEX/00_START_HERE.txt",
    "00_INDEX/MASTER_INDEX.txt",
    "00_INDEX/LINK_MAP.txt",
    "00_INDEX/03_DATING_RULES_AND_PRIORITY.txt",
    "01_FOUNDATION/01_WORLD_CORE.txt",
    "01_FOUNDATION/02_STATE_IDENTITY.txt",
    "02_GOVERNANCE/01_CONSTITUTIONAL_FRAME.txt",
    "06_ARCHIVE_AND_SITE/09_SITE_ARCHIVE_PUBLICATION_MODEL.txt",
    "07_TIMELINE/01_TIMELINE_CORE_2026_2086.txt",
    "07_TIMELINE/10_EARLY_YEARS_LOGIC_2026_2046.txt",
]

RECOVERY_ASSISTANT_EXTRA = [
    "00_INDEX/04_SIMPLE_EDITING_WORKFLOW.txt",
    "00_INDEX/CLOSED_REFERENCE_REGISTRY.txt",
    "00_INDEX/05_CLOSED_LINKING_RULES.txt",
    "00_INDEX/07_ASSISTANT_WORK_PROTOCOL.txt",
    "00_INDEX/09_CHANGELOG_SCOPE_RULES.txt",
    "06_ARCHIVE_AND_SITE/06_ACCESS_LEVELS_AND_DOCUMENT_STATUS.txt",
    "06_ARCHIVE_AND_SITE/10_PUBLIC_READ_OFFICIAL_ARCHIVE_REDESIGN_PROTOCOL.txt",
]

CSS = """
:root {
  --bg: #f4f1ea;
  --paper: #fffdf8;
  --ink: #1e2b2f;
  --muted: #667477;
  --line: #ded5c5;
  --accent: #174d5f;
  --accent2: #8a2e2e;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.65;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  border-bottom: 1px solid var(--line);
  background: #ede7da;
}
.topbar-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 12px 22px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  font-size: 14px;
  color: var(--muted);
}
.hero {
  background: linear-gradient(180deg, #fffaf0 0%, #f4f1ea 100%);
  border-bottom: 1px solid var(--line);
}
.hero-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 44px 22px 34px;
}
.kicker {
  text-transform: uppercase;
  letter-spacing: .12em;
  color: var(--accent2);
  font-size: 13px;
  font-weight: 700;
}
h1 {
  font-size: clamp(32px, 4vw, 52px);
  line-height: 1.1;
  margin: 10px 0 14px;
}
.hero p {
  max-width: 820px;
  color: #425052;
  font-size: 18px;
}
.archive-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 22px 42px;
}
.quick-grid,
.section-grid,
.doc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.quick-card,
.section-card,
.doc-card,
.meta-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 24px rgba(40,31,18,.06);
}
.quick-card strong,
.section-card h3,
.doc-card h3 {
  display: block;
  margin-bottom: 8px;
}
.section-title {
  margin: 34px 0 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
}
.doc-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
}
.path,
.doc-path {
  color: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  word-break: break-word;
}
.badge {
  display: inline-block;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 3px 9px;
  margin: 3px 4px 3px 0;
  font-size: 12px;
  color: var(--muted);
  background: #f8f3e9;
}
.doc-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .doc-layout { grid-template-columns: 1fr; }
  .topbar-inner { display: block; }
}
.document {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: clamp(22px, 4vw, 42px);
  box-shadow: 0 10px 28px rgba(40,31,18,.07);
}
.document h1 {
  font-size: clamp(28px, 3.5vw, 44px);
}
.doc-body {
  white-space: pre-wrap;
  font-size: 17px;
}
.meta-card {
  position: sticky;
  top: 16px;
  margin-bottom: 16px;
}
.meta-row {
  border-bottom: 1px solid var(--line);
  padding: 9px 0;
}
.meta-row:last-child { border-bottom: 0; }
.meta-key {
  color: var(--muted);
  font-size: 13px;
}
.meta-val { margin-top: 2px; }
.tools a {
  display: block;
  margin: 8px 0;
}
.footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 14px;
}
"""

def reset_public_dir():
    PUBLIC_DIR.mkdir(exist_ok=True)
    for child in PUBLIC_DIR.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

def get_meta(meta, *keys, default=""):
    for key in keys:
        value = meta.get(key)
        if value:
            return value
    return default

def read_document(path: Path):
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    nonempty_idx = [i for i, line in enumerate(lines) if line.strip()]
    brand = lines[nonempty_idx[0]].strip() if nonempty_idx else "BVK CANON"
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

    access = get_meta(meta, "Prieigos lygis", "Уровень доступа", default="PUBLIC").strip().upper() or "PUBLIC"
    status = get_meta(meta, "Statusas", "Статус", default="")
    historical = get_meta(meta, "Istorinė priklausomybė", "Историческая принадлежность", default="")

    return {
        "brand": brand,
        "title": title,
        "meta": meta,
        "body": body,
        "raw": raw,
        "access": access,
        "status": status,
        "historical": historical,
    }

def build_github_links(rel_txt: str):
    repo_path = f"CURRENT/{rel_txt}"
    view_url = f"{GITHUB_REPO_BASE}/blob/{GITHUB_BRANCH}/{repo_path}"
    edit_url = f"{GITHUB_REPO_BASE}/edit/{GITHUB_BRANCH}/{repo_path}"
    history_url = f"{GITHUB_REPO_BASE}/commits/{GITHUB_BRANCH}/{repo_path}"
    return view_url, edit_url, history_url

def page_head(title: str):
    return f"""<!doctype html>
<html lang="lt">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
"""

def topbar():
    return """<div class="topbar"><div class="topbar-inner">
  <div>BVK Canon · viešasis archyvas</div>
  <div><a href="/bvk-canon/">Archyvo pradžia</a> · <a href="https://github.com/baogroup/bvk-canon" target="_blank" rel="noopener noreferrer">GitHub šaltinis</a></div>
</div></div>
"""

def hero(title, subtitle, kicker="Baltijos Kooperatinė Respublika"):
    return f"""<header class="hero"><div class="hero-inner">
  <div class="kicker">{html.escape(kicker)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div></header>
"""

def meta_html(doc):
    keys = []

    for k in META_KEYS_ORDER:
        if k in doc["meta"]:
            keys.append(k)

    for k in doc["meta"]:
        if k not in keys:
            keys.append(k)

    rows = []
    for key in keys:
        rows.append(
            f"""<div class="meta-row"><div class="meta-key">{html.escape(key)}</div><div class="meta-val">{html.escape(doc["meta"].get(key, ""))}</div></div>"""
        )

    return "\n".join(rows)

def rel_to_root_prefix(rel_txt):
    # PUBLIC_READ/html/<rel path>.html → PUBLIC_READ/index.html
    depth = rel_txt.count("/") + 1
    return "../" * depth

def build_doc_html(doc, rel_txt, root_mode="public"):
    page_title = f"{doc['title']} · BVK Canon"
    prefix = rel_to_root_prefix(rel_txt)

    # public: PUBLIC_READ/html/... → PUBLIC_READ/index.html
    # assistant: PUBLIC_READ/assistant/html/... → PUBLIC_READ/assistant/index.html
    index_url = f"{prefix}index.html"

    view_url, edit_url, history_url = build_github_links(rel_txt)

    if root_mode == "assistant":
        tools = f"""<div class="meta-card tools">
  <h3>GitHub</h3>
  <a href="{html.escape(view_url)}" target="_blank" rel="noopener noreferrer">Pirminis txt failas</a>
  <a href="{html.escape(edit_url)}" target="_blank" rel="noopener noreferrer">Redaguoti GitHub</a>
  <a href="{html.escape(history_url)}" target="_blank" rel="noopener noreferrer">Failo istorija</a>
</div>"""
    else:
        tools = f"""<div class="meta-card tools">
  <h3>Šaltinis</h3>
  <a href="{html.escape(view_url)}" target="_blank" rel="noopener noreferrer">Kanoninis txt GitHub</a>
  <a href="{html.escape(history_url)}" target="_blank" rel="noopener noreferrer">Failo istorija</a>
</div>"""

    early_note = ""
    hist = doc.get("historical", "").lower()
    if "ankstyv" in hist or "ранн" in hist or "2026" in hist:
        early_note = '<p class="badge">Ankstyvasis sluoksnis</p>'

    return page_head(page_title) + topbar() + hero(doc["title"], rel_txt, kicker=doc["brand"]) + f"""
<main class="archive-shell">
  <p><a href="{html.escape(index_url)}">← Grįžti į archyvo indeksą</a></p>
  <div class="doc-layout">
    <article class="document">
      <div class="doc-path">{html.escape(rel_txt)}</div>
      {early_note}
      <div class="doc-body">{html.escape(doc["body"])}</div>
    </article>
    <aside>
      <div class="meta-card">
        <h3>Dokumento kortelė</h3>
        {meta_html(doc)}
      </div>
      {tools}
    </aside>
  </div>
  <div class="footer">BVK Canon · dokumentas sugeneruotas iš CURRENT sluoksnio. GitHub išlieka kanoninis šaltinis.</div>
</main>
</body>
</html>
"""

def section_for(rel_txt):
    return rel_txt.split("/", 1)[0]

def title_for_section(sec):
    return SECTION_TITLES.get(sec, sec.replace("_", " "))

def build_doc_card(rel_txt, rel_html, doc):
    status = html.escape(doc.get("status") or "—")
    access = html.escape(doc.get("access") or "PUBLIC")
    historical = html.escape(doc.get("historical") or "")

    return f"""<article class="doc-card">
  <div>
    <h3><a href="{html.escape(rel_html)}">{html.escape(doc["title"])}</a></h3>
    <div class="path">{html.escape(rel_txt)}</div>
    <div><span class="badge">{status}</span><span class="badge">{access}</span></div>
    <p>{historical}</p>
  </div>
  <div><a href="{html.escape(rel_html)}">Skaityti →</a></div>
</article>"""

def build_index_html(items, title, intro, root_mode="public"):
    groups = {}

    for rel_txt, rel_html, doc in items:
        groups.setdefault(section_for(rel_txt), []).append((rel_txt, rel_html, doc))

    quick_links = [
        ("Pradėti čia", "html/00_INDEX/00_START_HERE.html"),
        ("Chronologija", "html/07_TIMELINE/01_TIMELINE_CORE_2026_2086.html"),
        ("2026 metų archyvas", "html/01_ARCHIVE/2026/00_ARCHIVE_INDEX_2026.html"),
        ("Pirmųjų metų kronikos", "html/01_ARCHIVE/2026/01_FOUNDING_CHRONICLES/00_FOUNDING_CHRONICLES_INDEX_2026.html"),
        ("Atviri klausimai", "html/01_ARCHIVE/2026/02_OPEN_QUESTIONS/00_OPEN_QUESTIONS_INDEX_2026.html"),
        ("Archyvo modelis", "html/06_ARCHIVE_AND_SITE/09_SITE_ARCHIVE_PUBLICATION_MODEL.html"),
    ]

    parts = [
        page_head(title),
        topbar(),
        hero(title, intro, kicker="BVK Canon"),
        '<main class="archive-shell">',
    ]

    if root_mode == "assistant":
        parts.append('<div class="quick-card"><strong>Assistant sluoksnis</strong><p>Šiame indekse matomi PUBLIC ir SERVICE dokumentai, skirti konteksto atkūrimui ir kanono darbui.</p></div>')
    else:
        parts.append('<div class="quick-card"><strong>Viešasis sluoksnis</strong><p>Čia rodomi PUBLIC dokumentai. Darbo, riboto ir uždaro sluoksnio dokumentai viešai nerodomi.</p></div>')

    parts.append('<h2 class="section-title">Greitas įėjimas</h2><div class="quick-grid">')

    existing = {rel_html for _, rel_html, _ in items}
    for label, link in quick_links:
        if link in existing:
            parts.append(f'<a class="quick-card" href="{html.escape(link)}"><strong>{html.escape(label)}</strong><span>Atidaryti</span></a>')

    parts.append("</div>")

    parts.append('<h2 class="section-title">Pagrindiniai skyriai</h2><div class="section-grid">')

    for sec in sorted(groups.keys()):
        count = len(groups[sec])
        parts.append(f"""<a class="section-card" href="#sec-{html.escape(sec)}">
  <h3>{html.escape(title_for_section(sec))}</h3>
  <p>{html.escape(SECTION_DESCRIPTIONS.get(sec, "Dokumentų skyrius."))}</p>
  <span class="badge">{count} dokumentai</span>
</a>""")

    parts.append("</div>")

    for sec in sorted(groups.keys()):
        parts.append(f'<h2 class="section-title" id="sec-{html.escape(sec)}">{html.escape(title_for_section(sec))}</h2>')
        parts.append('<div class="doc-grid">')

        for rel_txt, rel_html, doc in sorted(groups[sec], key=lambda x: x[0]):
            parts.append(build_doc_card(rel_txt, rel_html, doc))

        parts.append("</div>")

    parts.append('<div class="footer">GitHub saugo kanoninį šaltinį ir istoriją. Šis puslapis yra skaitomas viešasis archyvas, sugeneruotas iš repozitorijos.</div>')
    parts.append("</main></body></html>")

    return "\n".join(parts)

def build_recovery_html(items, title, assistant=False):
    wanted = list(RECOVERY_PUBLIC)

    if assistant:
        wanted.extend(RECOVERY_ASSISTANT_EXTRA)

    by_rel = {rel_txt: (rel_html, doc) for rel_txt, rel_html, doc in items}

    parts = [
        page_head(title),
        topbar(),
        hero(title, "Trumpas įėjimas konteksto atkūrimui ir svarbiausiems kanono dokumentams.", kicker="Recovery Scan"),
        '<main class="archive-shell"><div class="doc-grid">',
    ]

    for rel in wanted:
        if rel in by_rel:
            rel_html, doc = by_rel[rel]
            parts.append(build_doc_card(rel, rel_html, doc))

    parts.append('</div><div class="footer"><a href="index.html">Visas indeksas</a></div></main></body></html>')

    return "\n".join(parts)

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

            assistant_target = PUBLIC_DIR / "assistant" / html_rel
            assistant_target.parent.mkdir(parents=True, exist_ok=True)
            assistant_target.write_text(build_doc_html(doc, rel_txt, root_mode="assistant"), encoding="utf-8")
            assistant_items.append((rel_txt, html_rel, doc))

        elif doc["access"] in ASSISTANT_ACCESS:
            assistant_target = PUBLIC_DIR / "assistant" / html_rel
            assistant_target.parent.mkdir(parents=True, exist_ok=True)
            assistant_target.write_text(build_doc_html(doc, rel_txt, root_mode="assistant"), encoding="utf-8")
            assistant_items.append((rel_txt, html_rel, doc))

    (PUBLIC_DIR / "index.html").write_text(
        build_index_html(
            public_items,
            "BVK Canon viešasis archyvas",
            "Atviras Baltijos Kooperatinės Respublikos ir BVK kanono dokumentų skaitymo sluoksnis.",
            root_mode="public",
        ),
        encoding="utf-8",
    )

    (PUBLIC_DIR / "RECOVERY_SCAN.html").write_text(
        build_recovery_html(public_items, "BVK Recovery Scan", assistant=False),
        encoding="utf-8",
    )

    (PUBLIC_DIR / "assistant").mkdir(exist_ok=True)

    (PUBLIC_DIR / "assistant" / "index.html").write_text(
        build_index_html(
            assistant_items,
            "BVK Canon assistant archyvas",
            "Išplėstas PUBLIC ir SERVICE dokumentų sluoksnis konteksto atkūrimui.",
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
