import json
import re
from pathlib import Path

FILE = Path("data/all_profiles.txt")
SECTIONS = ["About", "Experience", "Education", "Skills",
            "Languages", "Interests", "Recent Activity"]
DATES = r"((?:[A-Za-z]+ )?\d{4}) - ((?:[A-Za-z]+ )?\d{4}|present)\s*(.*)"


def split_commas(text):
    # split on commas, but not inside brackets: "Python (programming language)"
    return [p.strip() for p in re.split(r",\s*(?![^()]*\))", text) if p.strip()]


def bullets(lines):
    # join each "- item" with the lines that continue it
    items = []
    for line in lines:
        if line.startswith("- "):
            items.append(line[2:].strip())
        else:
            items[-1] += " " + line.strip()
    return items


def read_profile(profile_id, text, names):
    lines = text.splitlines()
    name = lines[0].strip()
    profile = {"id": profile_id, "name": name}

    # cut the text into sections
    parts = {"header": []}
    current = "header"
    for line in lines[1:]:
        if line in SECTIONS:
            current = line
            parts[current] = []
        elif line.strip():
            parts[current].append(line)

    # header: "Headline: ...", "Location: ...", "Network: ..."
    for line in parts["header"]:
        key, value = line.split(":", 1)
        profile[key.lower()] = value.strip()

    profile["about"] = " ".join(parts["About"])
    profile["skills"] = split_commas(" ".join(parts["Skills"]))
    profile["interests"] = split_commas(" ".join(parts["Interests"]))
    profile["languages"] = bullets(parts["Languages"])

    profile["experiences"] = []
    for item in bullets(parts["Experience"]):
        title, company, rest = [x.strip() for x in item.split(",", 2)]
        d = re.search(DATES, rest)
        profile["experiences"].append({
            "title": title, "company": company, "start": d.group(1),
            "end": None if d.group(2) == "present" else d.group(2),
            "description": d.group(3)})

    profile["education"] = []
    for item in bullets(parts["Education"]):
        item = re.sub(r"\s*Skills:.*", "", item)  # drop "Skills: NumPy and 16 more"
        d = re.search(DATES, item)
        info = split_commas(item[:d.start()])
        profile["education"].append({
            "institution": info[0], "degree": info[1], "field": info[2] if len(info) > 2 else None,
            "start": d.group(1), "end": None if d.group(2) == "present" else d.group(2)})

    profile["activity"] = []
    for item in bullets(parts["Recent Activity"]):
        mentioned = [n for n in names if n != name and n in item]
        profile["activity"].append({"text": item, "mentioned": mentioned})
    return profile


# the file looks like: ===== PROFILE 1 =====, text, ===== PROFILE 2 =====, text, ...
parts = re.split(r"^===== PROFILE (\d+) =====\s*$", FILE.read_text(encoding="utf-8"), flags=re.MULTILINE)
# parts = [text before, "1", text of 1, "2", text of 2, ...]
chunks = [(f"profile_{int(n):02d}", body.strip()) for n, body in zip(parts[1::2], parts[2::2])]

# if the same person is in the file twice, keep only the first one
unique, seen = [], set()
for pid, text in chunks:
    name = text.splitlines()[0].strip()
    if name in seen:
        print("WARNING: duplicate profile skipped:", name)
        continue
    seen.add(name)
    unique.append((pid, text))
chunks = unique

names = [text.splitlines()[0].strip() for _, text in chunks]  # first line = name
profiles = [read_profile(pid, text, names) for pid, text in chunks]

with open("data/profiles.json", "w", encoding="utf-8") as f:
    json.dump(profiles, f, ensure_ascii=False, indent=2)

# quick check: how many items did we find in each section?
print(f"{len(profiles)} profiles saved to data/profiles.json")
for p in profiles:
    counts = {k: len(p[k]) for k in ["experiences", "education", "skills", "languages", "interests", "activity"]}
    print(p["name"], counts)
    if 0 in counts.values():
        print("  WARNING: an empty section!")