#!/usr/bin/env python3
import csv
import os
import re
import sys


MOUNT_POINT = sys.argv[1] if len(sys.argv) > 1 else "/storage/roms"
RGBPI_DATA = sys.argv[2] if len(sys.argv) > 2 else "/storage/rgbpi/data"


def load_lines(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return {line.strip() for line in handle if line.strip()}
    except OSError:
        return set()


def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def get_subsystem(path, system, subsystems):
    subsystems = [s for s in subsystems if s]
    if not subsystems:
        return system
    for subsystem in subsystems:
        if subsystem in path:
            return subsystem
    return None


def clean_name(filename):
    name, _ = os.path.splitext(filename)
    return name


def normalize(name):
    return re.sub(r"[^A-Z0-9]+", "", name.upper().split("(")[0])


def preference_score(path):
    path = path.lower()
    score = 0
    for token, value in (
        ("(usa", 50),
        ("(world", 45),
        ("(europe", 40),
        ("(japan", 10),
    ):
        if token in path:
            score += value
    for token in ("(beta", "(proto", "(sample", "(demo", "(pirate", "(unl", "(hack", "(bad"):
        if token in path:
            score -= 25
    return score


def dedupe_games(games):
    selected = {}
    order = []
    for game in games:
        key = (game["System"], game["Subsystem"], normalize(game["Name"]))
        if key not in selected:
            selected[key] = game
            order.append(key)
            continue
        if preference_score(game["File"]) > preference_score(selected[key]["File"]):
            selected[key] = game
    return [selected[key] for key in order]


def main():
    systems_file = os.path.join(RGBPI_DATA, "systems.dat")
    dats_dir = os.path.join(MOUNT_POINT, "dats")
    games_file = os.path.join(dats_dir, "games.dat")
    fav_file = os.path.join(dats_dir, "favorites.dat")
    fav_tate_file = os.path.join(dats_dir, "favorites_tate.dat")
    bios_db = load_lines(os.path.join(RGBPI_DATA, "bios.dat"))
    scan_black_list = load_lines(os.path.join(RGBPI_DATA, "scan_black_list.dat"))
    fieldnames = ["Id", "Hash", "System", "Subsystem", "File", "Name", "Genre", "Developer", "Year", "Players"]
    games = []

    with open(systems_file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            system = row["System"]
            formats = tuple(part.lower() for part in row["Formats"].split("|") if part)
            subsystems = row["Subsystems"].split("|")
            search_paths = [
                os.path.join(MOUNT_POINT, "roms", system),
                os.path.join(MOUNT_POINT, system),
            ]
            seen = set()
            for search_path in search_paths:
                if not os.path.isdir(search_path):
                    continue
                for entry in scantree(search_path):
                    if entry.path in seen:
                        continue
                    seen.add(entry.path)
                    name = entry.name
                    lower_name = name.lower()
                    if not lower_name.endswith(formats):
                        continue
                    if name.startswith(".") or name.startswith("("):
                        continue
                    if name in bios_db or name in scan_black_list:
                        continue
                    if re.findall(r"\(disc.*[0-9].*\)", lower_name):
                        continue
                    subsystem = get_subsystem(entry.path, system, subsystems)
                    if not subsystem:
                        continue
                    games.append({
                        "Id": "",
                        "Hash": "",
                        "System": system,
                        "Subsystem": subsystem,
                        "File": entry.path.replace(MOUNT_POINT, "", 1),
                        "Name": clean_name(name),
                        "Genre": "?",
                        "Developer": "?",
                        "Year": "19XX",
                        "Players": "1",
                    })

    games = dedupe_games(games)
    os.makedirs(dats_dir, exist_ok=True)
    for path, rows in [(games_file, games), (fav_file, []), (fav_tate_file, [])]:
        with open(path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    print(f"scanned {len(games)} games into {games_file}")


if __name__ == "__main__":
    main()
