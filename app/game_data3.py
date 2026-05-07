"""Game schedule data - Part 3 (Groups I-L and Knockout matches)."""

GROUP_MATCHES_2 = [
    # Group I
    {"id": "GI1", "group": "I", "home": "France", "away": "Senegal", "date": "2026-06-16 15:00"},
    {"id": "GI2", "group": "I", "home": "Iraq", "away": "Norway", "date": "2026-06-16 18:00"},
    {"id": "GI3", "group": "I", "home": "France", "away": "Iraq", "date": "2026-06-22 17:00"},
    {"id": "GI4", "group": "I", "home": "Norway", "away": "Senegal", "date": "2026-06-22 20:00"},
    {"id": "GI5", "group": "I", "home": "Senegal", "away": "Iraq", "date": "2026-06-27 18:00"},
    {"id": "GI6", "group": "I", "home": "Norway", "away": "France", "date": "2026-06-27 18:00"},
    # Group J
    {"id": "GJ1", "group": "J", "home": "Argentina", "away": "Algeria", "date": "2026-06-16 21:00"},
    {"id": "GJ2", "group": "J", "home": "Austria", "away": "Jordan", "date": "2026-06-17 00:00"},
    {"id": "GJ3", "group": "J", "home": "Argentina", "away": "Austria", "date": "2026-06-22 23:00"},
    {"id": "GJ4", "group": "J", "home": "Jordan", "away": "Algeria", "date": "2026-06-23 02:00"},
    {"id": "GJ5", "group": "J", "home": "Algeria", "away": "Austria", "date": "2026-06-27 21:00"},
    {"id": "GJ6", "group": "J", "home": "Jordan", "away": "Argentina", "date": "2026-06-27 21:00"},
    # Group K
    {"id": "GK1", "group": "K", "home": "Portugal", "away": "DR Congo", "date": "2026-06-17 15:00"},
    {"id": "GK2", "group": "K", "home": "Uzbekistan", "away": "Colombia", "date": "2026-06-17 18:00"},
    {"id": "GK3", "group": "K", "home": "Portugal", "away": "Uzbekistan", "date": "2026-06-23 15:00"},
    {"id": "GK4", "group": "K", "home": "Colombia", "away": "DR Congo", "date": "2026-06-23 18:00"},
    {"id": "GK5", "group": "K", "home": "DR Congo", "away": "Uzbekistan", "date": "2026-06-28 00:00"},
    {"id": "GK6", "group": "K", "home": "Colombia", "away": "Portugal", "date": "2026-06-28 00:00"},
    # Group L
    {"id": "GL1", "group": "L", "home": "England", "away": "Croatia", "date": "2026-06-17 21:00"},
    {"id": "GL2", "group": "L", "home": "Ghana", "away": "Panama", "date": "2026-06-18 00:00"},
    {"id": "GL3", "group": "L", "home": "England", "away": "Ghana", "date": "2026-06-23 21:00"},
    {"id": "GL4", "group": "L", "home": "Panama", "away": "Croatia", "date": "2026-06-24 00:00"},
    {"id": "GL5", "group": "L", "home": "Croatia", "away": "Ghana", "date": "2026-06-28 18:00"},
    {"id": "GL6", "group": "L", "home": "Panama", "away": "England", "date": "2026-06-28 18:00"},
]

KNOCKOUT_MATCHES = [
    # Round of 32 (1/16)
    {"id": "KO73", "phase": "R32", "match_num": 73, "home": "2A", "away": "2B", "date": "2026-06-28 15:00"},
    {"id": "KO74", "phase": "R32", "match_num": 74, "home": "1E", "away": "3ABCDF", "date": "2026-06-29 16:30"},
    {"id": "KO75", "phase": "R32", "match_num": 75, "home": "1F", "away": "2C", "date": "2026-06-29 21:00"},
    {"id": "KO76", "phase": "R32", "match_num": 76, "home": "1C", "away": "2F", "date": "2026-06-29 13:00"},
    {"id": "KO77", "phase": "R32", "match_num": 77, "home": "1I", "away": "3CDFGH", "date": "2026-06-30 17:00"},
    {"id": "KO78", "phase": "R32", "match_num": 78, "home": "2E", "away": "2I", "date": "2026-06-30 13:00"},
    {"id": "KO79", "phase": "R32", "match_num": 79, "home": "1A", "away": "3CEFHI", "date": "2026-06-30 21:00"},
    {"id": "KO80", "phase": "R32", "match_num": 80, "home": "1L", "away": "3EHIJK", "date": "2026-07-01 12:00"},
    {"id": "KO81", "phase": "R32", "match_num": 81, "home": "1D", "away": "3BEFIJ", "date": "2026-07-01 20:00"},
    {"id": "KO82", "phase": "R32", "match_num": 82, "home": "1G", "away": "3AEHIJ", "date": "2026-07-01 16:00"},
    {"id": "KO83", "phase": "R32", "match_num": 83, "home": "2K", "away": "2L", "date": "2026-07-02 19:00"},
    {"id": "KO84", "phase": "R32", "match_num": 84, "home": "1H", "away": "2J", "date": "2026-07-02 15:00"},
    {"id": "KO85", "phase": "R32", "match_num": 85, "home": "1B", "away": "3EFGIJ", "date": "2026-07-02 23:00"},
    {"id": "KO86", "phase": "R32", "match_num": 86, "home": "1J", "away": "2H", "date": "2026-07-03 18:00"},
    {"id": "KO87", "phase": "R32", "match_num": 87, "home": "1K", "away": "3DEIJL", "date": "2026-07-03 21:30"},
    {"id": "KO88", "phase": "R32", "match_num": 88, "home": "2D", "away": "2G", "date": "2026-07-03 14:00"},
    # Round of 16 (1/8)
    {"id": "KO89", "phase": "R16", "match_num": 89, "home": "W74", "away": "W77", "date": "2026-07-04 17:00"},
    {"id": "KO90", "phase": "R16", "match_num": 90, "home": "W73", "away": "W75", "date": "2026-07-04 13:00"},
    {"id": "KO91", "phase": "R16", "match_num": 91, "home": "W76", "away": "W78", "date": "2026-07-05 16:00"},
    {"id": "KO92", "phase": "R16", "match_num": 92, "home": "W79", "away": "W80", "date": "2026-07-05 20:00"},
    {"id": "KO93", "phase": "R16", "match_num": 93, "home": "W83", "away": "W84", "date": "2026-07-06 15:00"},
    {"id": "KO94", "phase": "R16", "match_num": 94, "home": "W81", "away": "W82", "date": "2026-07-06 20:00"},
    {"id": "KO95", "phase": "R16", "match_num": 95, "home": "W86", "away": "W88", "date": "2026-07-07 12:00"},
    {"id": "KO96", "phase": "R16", "match_num": 96, "home": "W85", "away": "W87", "date": "2026-07-07 16:00"},
    # Quarter-finals (1/4)
    {"id": "KO97", "phase": "QF", "match_num": 97, "home": "W89", "away": "W90", "date": "2026-07-09 16:00"},
    {"id": "KO98", "phase": "QF", "match_num": 98, "home": "W93", "away": "W94", "date": "2026-07-10 15:00"},
    {"id": "KO99", "phase": "QF", "match_num": 99, "home": "W91", "away": "W92", "date": "2026-07-11 17:00"},
    {"id": "KO100", "phase": "QF", "match_num": 100, "home": "W95", "away": "W96", "date": "2026-07-11 21:00"},
    # Semi-finals (1/2)
    {"id": "KO101", "phase": "SF", "match_num": 101, "home": "W97", "away": "W98", "date": "2026-07-14 15:00"},
    {"id": "KO102", "phase": "SF", "match_num": 102, "home": "W99", "away": "W100", "date": "2026-07-15 15:00"},
    # Third place
    {"id": "KO103", "phase": "3rd", "match_num": 103, "home": "L101", "away": "L102", "date": "2026-07-18 17:00"},
    # Final
    {"id": "KO104", "phase": "Final", "match_num": 104, "home": "W101", "away": "W102", "date": "2026-07-19 15:00"},
]
