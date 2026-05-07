"""Game schedule data - Part 2 (GROUP_MATCHES and KNOCKOUT_MATCHES)."""

GROUP_MATCHES = [
    # Group A
    {"id": "GA1", "group": "A", "home": "Mexico", "away": "South Africa", "date": "2026-06-11 15:00"},
    {"id": "GA2", "group": "A", "home": "South Korea", "away": "Czech Republic", "date": "2026-06-11 22:00"},
    {"id": "GA3", "group": "A", "home": "Czech Republic", "away": "South Africa", "date": "2026-06-18 12:00"},
    {"id": "GA4", "group": "A", "home": "Mexico", "away": "South Korea", "date": "2026-06-18 21:00"},
    {"id": "GA5", "group": "A", "home": "Czech Republic", "away": "Mexico", "date": "2026-06-24 21:00"},
    {"id": "GA6", "group": "A", "home": "South Africa", "away": "South Korea", "date": "2026-06-24 21:00"},
    # Group B
    {"id": "GB1", "group": "B", "home": "Canada", "away": "Bosnia and Herzegovina", "date": "2026-06-12 15:00"},
    {"id": "GB2", "group": "B", "home": "Qatar", "away": "Switzerland", "date": "2026-06-13 15:00"},
    {"id": "GB3", "group": "B", "home": "Switzerland", "away": "Bosnia and Herzegovina", "date": "2026-06-18 15:00"},
    {"id": "GB4", "group": "B", "home": "Canada", "away": "Qatar", "date": "2026-06-19 18:00"},
    {"id": "GB5", "group": "B", "home": "Bosnia and Herzegovina", "away": "Canada", "date": "2026-06-25 15:00"},
    {"id": "GB6", "group": "B", "home": "Switzerland", "away": "Qatar", "date": "2026-06-25 15:00"},
    # Group C
    {"id": "GC1", "group": "C", "home": "Brazil", "away": "Morocco", "date": "2026-06-12 18:00"},
    {"id": "GC2", "group": "C", "home": "Haiti", "away": "Scotland", "date": "2026-06-12 21:00"},
    {"id": "GC3", "group": "C", "home": "Scotland", "away": "Morocco", "date": "2026-06-19 12:00"},
    {"id": "GC4", "group": "C", "home": "Brazil", "away": "Haiti", "date": "2026-06-19 21:00"},
    {"id": "GC5", "group": "C", "home": "Morocco", "away": "Haiti", "date": "2026-06-25 21:00"},
    {"id": "GC6", "group": "C", "home": "Scotland", "away": "Brazil", "date": "2026-06-25 21:00"},
    # Group D
    {"id": "GD1", "group": "D", "home": "United States", "away": "Paraguay", "date": "2026-06-13 18:00"},
    {"id": "GD2", "group": "D", "home": "Australia", "away": "Turkey", "date": "2026-06-13 21:00"},
    {"id": "GD3", "group": "D", "home": "Turkey", "away": "Paraguay", "date": "2026-06-19 15:00"},
    {"id": "GD4", "group": "D", "home": "United States", "away": "Australia", "date": "2026-06-20 00:00"},
    {"id": "GD5", "group": "D", "home": "Paraguay", "away": "Australia", "date": "2026-06-26 00:00"},
    {"id": "GD6", "group": "D", "home": "Turkey", "away": "United States", "date": "2026-06-26 00:00"},
    # Group E
    {"id": "GE1", "group": "E", "home": "Germany", "away": "Curaçao", "date": "2026-06-14 12:00"},
    {"id": "GE2", "group": "E", "home": "Ivory Coast", "away": "Ecuador", "date": "2026-06-14 18:00"},
    {"id": "GE3", "group": "E", "home": "Ecuador", "away": "Curaçao", "date": "2026-06-20 15:00"},
    {"id": "GE4", "group": "E", "home": "Germany", "away": "Ivory Coast", "date": "2026-06-20 21:00"},
    {"id": "GE5", "group": "E", "home": "Curaçao", "away": "Ivory Coast", "date": "2026-06-26 15:00"},
    {"id": "GE6", "group": "E", "home": "Ecuador", "away": "Germany", "date": "2026-06-26 15:00"},
    # Group F
    {"id": "GF1", "group": "F", "home": "Netherlands", "away": "Japan", "date": "2026-06-14 16:00"},
    {"id": "GF2", "group": "F", "home": "Sweden", "away": "Tunisia", "date": "2026-06-14 22:00"},
    {"id": "GF3", "group": "F", "home": "Netherlands", "away": "Sweden", "date": "2026-06-20 13:00"},
    {"id": "GF4", "group": "F", "home": "Tunisia", "away": "Japan", "date": "2026-06-21 00:00"},
    {"id": "GF5", "group": "F", "home": "Japan", "away": "Sweden", "date": "2026-06-25 19:00"},
    {"id": "GF6", "group": "F", "home": "Tunisia", "away": "Netherlands", "date": "2026-06-25 19:00"},
    # Group G
    {"id": "GG1", "group": "G", "home": "Belgium", "away": "Egypt", "date": "2026-06-15 15:00"},
    {"id": "GG2", "group": "G", "home": "Iran", "away": "New Zealand", "date": "2026-06-15 21:00"},
    {"id": "GG3", "group": "G", "home": "Belgium", "away": "Iran", "date": "2026-06-21 15:00"},
    {"id": "GG4", "group": "G", "home": "New Zealand", "away": "Egypt", "date": "2026-06-21 21:00"},
    {"id": "GG5", "group": "G", "home": "Egypt", "away": "Iran", "date": "2026-06-26 23:00"},
    {"id": "GG6", "group": "G", "home": "New Zealand", "away": "Belgium", "date": "2026-06-26 23:00"},
    # Group H
    {"id": "GH1", "group": "H", "home": "Spain", "away": "Cape Verde", "date": "2026-06-15 12:00"},
    {"id": "GH2", "group": "H", "home": "Saudi Arabia", "away": "Uruguay", "date": "2026-06-15 18:00"},
    {"id": "GH3", "group": "H", "home": "Spain", "away": "Saudi Arabia", "date": "2026-06-21 12:00"},
    {"id": "GH4", "group": "H", "home": "Uruguay", "away": "Cape Verde", "date": "2026-06-21 18:00"},
    {"id": "GH5", "group": "H", "home": "Cape Verde", "away": "Saudi Arabia", "date": "2026-06-26 20:00"},
    {"id": "GH6", "group": "H", "home": "Uruguay", "away": "Spain", "date": "2026-06-26 20:00"},
]
