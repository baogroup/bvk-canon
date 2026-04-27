from pathlib import Path
import re

root = Path("CURRENT/01_ARCHIVE/2027")

for path in root.glob("A-2027-*.txt"):
    text = path.read_text(encoding="utf-8")

    match = re.search(r"A-(\d{4})-(\d{2})-(\d{2})-", path.name)
    if not match:
        continue

    date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    text_new = re.sub(
        r"Pirmojo priėmimo data:\s*\d{4}-\d{2}-\d{2}",
        f"Pirmojo priėmimo data: {date}",
        text,
        count=1,
    )

    text_new = re.sub(
        r"Dabartinė redakcija:\s*\d{4}-\d{2}-\d{2}",
        f"Dabartinė redakcija: {date}",
        text_new,
        count=1,
    )

    if text_new != text:
        path.write_text(text_new, encoding="utf-8")
        print(f"Updated {path} -> {date}")
