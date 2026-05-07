"""World Cup 2026 game data - Teams, groups, and flags."""

# Flag emoji mapping
FLAGS = {
    "Mexico": "mx", "South Africa": "za", "South Korea": "kr", "Czech Republic": "cz",
    "Canada": "ca", "Bosnia and Herzegovina": "ba", "Qatar": "qa", "Switzerland": "ch",
    "Brazil": "br", "Morocco": "ma", "Haiti": "ht", "Scotland": "gb-sct",
    "United States": "us", "Paraguay": "py", "Australia": "au", "Turkey": "tr",
    "Germany": "de", "Curaçao": "cw", "Ivory Coast": "ci", "Ecuador": "ec",
    "Netherlands": "nl", "Japan": "jp", "Sweden": "se", "Tunisia": "tn",
    "Belgium": "be", "Egypt": "eg", "Iran": "ir", "New Zealand": "nz",
    "Spain": "es", "Cape Verde": "cv", "Saudi Arabia": "sa", "Uruguay": "uy",
    "France": "fr", "Senegal": "sn", "Iraq": "iq", "Norway": "no",
    "Argentina": "ar", "Algeria": "dz", "Austria": "at", "Jordan": "jo",
    "Portugal": "pt", "DR Congo": "cd", "Uzbekistan": "uz", "Colombia": "co",
    "England": "gb-eng", "Croatia": "hr", "Ghana": "gh", "Panama": "pa",
}

TEAMS = [
    {"name": "Mexico", "group": "A"}, {"name": "South Africa", "group": "A"},
    {"name": "South Korea", "group": "A"}, {"name": "Czech Republic", "group": "A"},
    {"name": "Canada", "group": "B"}, {"name": "Bosnia and Herzegovina", "group": "B"},
    {"name": "Qatar", "group": "B"}, {"name": "Switzerland", "group": "B"},
    {"name": "Brazil", "group": "C"}, {"name": "Morocco", "group": "C"},
    {"name": "Haiti", "group": "C"}, {"name": "Scotland", "group": "C"},
    {"name": "United States", "group": "D"}, {"name": "Paraguay", "group": "D"},
    {"name": "Australia", "group": "D"}, {"name": "Turkey", "group": "D"},
    {"name": "Germany", "group": "E"}, {"name": "Curaçao", "group": "E"},
    {"name": "Ivory Coast", "group": "E"}, {"name": "Ecuador", "group": "E"},
    {"name": "Netherlands", "group": "F"}, {"name": "Japan", "group": "F"},
    {"name": "Sweden", "group": "F"}, {"name": "Tunisia", "group": "F"},
    {"name": "Belgium", "group": "G"}, {"name": "Egypt", "group": "G"},
    {"name": "Iran", "group": "G"}, {"name": "New Zealand", "group": "G"},
    {"name": "Spain", "group": "H"}, {"name": "Cape Verde", "group": "H"},
    {"name": "Saudi Arabia", "group": "H"}, {"name": "Uruguay", "group": "H"},
    {"name": "France", "group": "I"}, {"name": "Senegal", "group": "I"},
    {"name": "Iraq", "group": "I"}, {"name": "Norway", "group": "I"},
    {"name": "Argentina", "group": "J"}, {"name": "Algeria", "group": "J"},
    {"name": "Austria", "group": "J"}, {"name": "Jordan", "group": "J"},
    {"name": "Portugal", "group": "K"}, {"name": "DR Congo", "group": "K"},
    {"name": "Uzbekistan", "group": "K"}, {"name": "Colombia", "group": "K"},
    {"name": "England", "group": "L"}, {"name": "Croatia", "group": "L"},
    {"name": "Ghana", "group": "L"}, {"name": "Panama", "group": "L"},
]

GROUPS = {}
for t in TEAMS:
    GROUPS.setdefault(t["group"], []).append(t["name"])
