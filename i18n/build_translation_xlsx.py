#!/usr/bin/env python3
"""Generate nisyros-wines-translation.xlsx — translation worksheet for el (Greek).

One row per string, grouped in sheets by site section. Translator fills the
`el` column. The XLSX is the source of truth for the translator; final values
are then committed back into i18n/el.json and the Google Sheet (wines/faces).
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = "/home/user/nw/i18n/nisyros-wines-translation.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="2B2725")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="F5F2EE")
WRAP = Alignment(wrap_text=True, vertical="top")

COLS = ["key", "en", "el", "notes"]
COL_WIDTHS = {"key": 32, "en": 70, "el": 70, "notes": 50}


def add_sheet(wb, name, rows, intro=None):
    ws = wb.create_sheet(name)
    r = 1
    if intro:
        ws.cell(row=r, column=1, value=intro).font = Font(italic=True, color="6B6360")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        r += 2
    for c, h in enumerate(COLS, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
    r += 1
    for row in rows:
        for c, key in enumerate(COLS, 1):
            cell = ws.cell(row=r, column=c, value=row.get(key, ""))
            cell.alignment = WRAP
        r += 1
    for c, h in enumerate(COLS, 1):
        ws.column_dimensions[get_column_letter(c)].width = COL_WIDTHS[h]
    ws.freeze_panes = "A{}".format((3 if intro else 1) + 1)
    return ws


wb = Workbook()
# Remove default sheet
wb.remove(wb.active)

# ── README ────────────────────────────────────────────────────────────────
readme = wb.create_sheet("README")
readme_lines = [
    ("Nisyros Wines — Greek translation workbook", "title"),
    ("", None),
    ("Purpose", "h2"),
    ("Translate every English string in column `en` into Greek in column `el`.", None),
    ("Leave column `en` and `key` untouched — they are used to wire the text back into the site.", None),
    ("", None),
    ("How it's organized", "h2"),
    ("Each sheet = one section of the site. Order matches the user's scroll path:", None),
    ("  1. Nav            — top navigation labels", None),
    ("  2. Hero           — landing screen", None),
    ("  3. Manifesto      — 7 horizontal slides (titles + body)", None),
    ("  4. Wines (UI)     — fixed labels around the wine cards", None),
    ("  5. Wines (CMS)    — per-wine content (lives in Google Sheets — see notes)", None),
    ("  6. Faces          — gallery section + per-photo captions", None),
    ("  7. Contact        — contact blocks + footer", None),
    ("  8. SEO            — page title, meta description, social tags", None),
    ("", None),
    ("Guidelines for the translator", "h2"),
    ("• Tone: short declarative sentences, manifesto-like, no marketing fluff.", None),
    ("• Keep line breaks inside multi-line titles (e.g. \"Wines / from the / Edge\") — each slash = new line.", None),
    ("• Brand names stay in latin script: Nisyros Wines, Monopàtia, Nereides, Volcanica, 3,2,1, 40 Milia Konda, Roudià, Apiri, Atmida.", None),
    ("• Geographic names: use the natural Greek form — Νίσυρος, Δωδεκάνησα, Αιγαίο.", None),
    ("• Where a string already exists in Greek (e.g. SEO meta `description`/`keywords`), reuse or refine it.", None),
    ("• If a string has HTML inside it (e.g. <br>), keep the tag intact and translate around it.", None),
    ("• If the meaning is ambiguous, leave a comment in the `notes` column or in red text.", None),
    ("", None),
    ("Wines & Faces CMS", "h2"),
    ("The 5 wines and the gallery photo captions live in a Google Sheet, not in the codebase.", None),
    ("The `Wines (CMS)` and `Faces (CMS)` sheets in this file list the current English content for reference.", None),
    ("Translations for those will be added as new columns in the Google Sheet (name_el, body_el, …).", None),
    ("", None),
    ("Deliverable", "h2"),
    ("Save this file as-is when done. The developer will copy the `el` column back into the codebase.", None),
]
for i, (text, kind) in enumerate(readme_lines, 1):
    cell = readme.cell(row=i, column=1, value=text)
    if kind == "title":
        cell.font = Font(size=16, bold=True, color="C46E4B")
    elif kind == "h2":
        cell.font = Font(size=12, bold=True, color="2B2725")
    else:
        cell.font = Font(size=11, color="2B2725")
    cell.alignment = Alignment(wrap_text=True, vertical="top")
readme.column_dimensions["A"].width = 110

# ── 1. NAV ────────────────────────────────────────────────────────────────
nav_rows = [
    {"key": "nav.manifesto", "en": "Manifesto",  "notes": "Top nav link"},
    {"key": "nav.wines",     "en": "Wines",      "notes": "Top nav link"},
    {"key": "nav.faces",     "en": "Faces",      "notes": "Top nav link"},
    {"key": "nav.contact",   "en": "Contact",    "notes": "Top nav link"},
    {"key": "nav.lang_en",   "en": "EN",         "notes": "Language switcher label (English). Will likely stay 'EN'."},
    {"key": "nav.lang_el",   "en": "EL",         "notes": "Language switcher label (Greek). Likely 'ΕΛ' in Greek."},
]
add_sheet(wb, "1. Nav", nav_rows)

# ── 2. HERO ───────────────────────────────────────────────────────────────
hero_rows = [
    {"key": "hero.location", "en": "Nisyros · Aegean Sea · Greece",
     "notes": "Small caption above the wordmark. Keep the · separators."},
]
add_sheet(wb, "2. Hero", hero_rows)

# ── 3. MANIFESTO ──────────────────────────────────────────────────────────
manifesto_rows = [
    # I — Edge
    {"key": "m1.line1", "en": "Wines",   "notes": "I — Big title, line 1"},
    {"key": "m1.line2", "en": "from the","notes": "I — Big title, line 2"},
    {"key": "m1.line3", "en": "Edge",    "notes": "I — Big title, line 3 (red accent)"},
    {"key": "m1.body",  "en": "Nisyros is a Volcano. Alive. It breathes, it trembles, it reminds you who is in charge. We make our wine here — on the edge of the crater.",
     "notes": "I — Body paragraph"},
    # II — Nothing
    {"key": "m2.line1", "en": "Almost",  "notes": "II — Big title, line 1"},
    {"key": "m2.line2", "en": "Nothing", "notes": "II — Big title, line 2 (red accent)"},
    {"key": "m2.body",  "en": "Minimal intervention in winemaking is a form of love and respect. Our job is to protect without interfering. We step back so the vine can speak.",
     "notes": "II — Body paragraph"},
    # III — Land
    {"key": "m3.line1", "en": "With the","notes": "III — Big title, line 1"},
    {"key": "m3.line2", "en": "Land",    "notes": "III — Big title, line 2 (red accent)"},
    {"key": "m3.body",  "en": "The volcanic soil of Nisyros is a blessed land. We are guests and, for a moment, caretakers. For millennia agriculture sustained this island. We revive that tradition, with respect and endless dedication. The vine must live here long after we are gone.",
     "notes": "III — Body paragraph"},
    # IV — Shoulders of Giants
    {"key": "m4.line1", "en": "On the",       "notes": "IV — Big title, line 1"},
    {"key": "m4.line2", "en": "Shoulders",    "notes": "IV — Big title, line 2"},
    {"key": "m4.line3", "en": "of Giants",    "notes": "IV — Big title, line 3 (red accent)"},
    {"key": "m4.body",  "en": "We read the books, sat with our elders, learned the local traditions. We study fermentation, microbiology, viticulture. And the rules of physics and nature: temperature, pressure, time, climate, seasons. Knowledge is our freedom.",
     "notes": "IV — Body paragraph"},
    # V — Fail
    {"key": "m5.line1", "en": "We try",       "notes": "V — Big title, line 1"},
    {"key": "m5.line2", "en": "things that",  "notes": "V — Big title, line 2"},
    {"key": "m5.line3", "en": "Fail",         "notes": "V — Big title, line 3 (red accent)"},
    {"key": "m5.body",  "en": "We look for rare vineyards, ferment in unusual vessels, blend the unexpected. Failure is part of making. Essential, so that sometimes, something extraordinary happens. But nothing leaves our cellar unless we are really proud of it.",
     "notes": "V — Body paragraph"},
    # VI — We Do What We Say
    {"key": "m6.line1", "en": "We Do",        "notes": "VI — Big title, line 1"},
    {"key": "m6.line2", "en": "What we Say",  "notes": "VI — Big title, line 2 (red accent)"},
    {"key": "m6.body",  "en": "We share with you the story, the vineyard, the vintage, every step of the process. The bright moments, the dark hours. We do what we say. We say what we do. Trust is part of the bottle.",
     "notes": "VI — Body paragraph"},
    # Credo
    {"key": "credo.line1", "en": "Message", "notes": "VII / Credo — Big title, line 1"},
    {"key": "credo.line2", "en": "in the",  "notes": "VII / Credo — Big title, line 2"},
    {"key": "credo.line3", "en": "bottle",  "notes": "VII / Credo — Big title, line 3 (red accent)"},
    {"key": "credo.body",  "en": "The endless summer. The Aegean light at sunset. The wind, the waves, the freedom. These islands are a gift. So are these wines. Unique, unrepeatable. True to the land. Clean in the glass.",
     "notes": "VII / Credo — Body paragraph"},
]
add_sheet(wb, "3. Manifesto", manifesto_rows,
          intro="Manifesto = 7 horizontal slides. Titles are multi-line; keep each `line_n` as its own short line. Bodies are one paragraph each.")

# ── 4. WINES UI (static labels) ───────────────────────────────────────────
wines_ui_rows = [
    # Intro slide
    {"key": "wines.intro.count",       "en": "5 Wines.",             "notes": "Intro slide — line 1 (red)"},
    {"key": "wines.intro.vintages",    "en": "2 Vintages.",          "notes": "Intro slide — line 2"},
    {"key": "wines.intro.collections", "en": "3 Collections.",       "notes": "Intro slide — line 3"},
    {"key": "wines.intro.cta",         "en": "Discover >",           "notes": "Intro slide — CTA button"},
    # Wine card body labels (from js/main.js)
    {"key": "wines.label.story",         "en": "Story",          "notes": "Wine card body label"},
    {"key": "wines.label.winemaking",    "en": "Winemaking",     "notes": "Wine card body label"},
    {"key": "wines.label.tasting_notes", "en": "Tasting Notes",  "notes": "Wine card body label"},
    # Wine detail rows
    {"key": "wines.detail.vintages",     "en": "Vintages",       "notes": "Wine detail row label"},
    {"key": "wines.detail.type",         "en": "Type",           "notes": "Wine detail row label"},
    {"key": "wines.detail.variety",      "en": "Variety",        "notes": "Wine detail row label"},
    {"key": "wines.detail.appellation",  "en": "Appellation",    "notes": "Wine detail row label"},
    {"key": "wines.detail.origin",       "en": "Origin",         "notes": "Wine detail row label"},
    {"key": "wines.detail.altitude",     "en": "Altitude",       "notes": "Wine detail row label"},
    {"key": "wines.detail.soil",         "en": "Soil",           "notes": "Wine detail row label"},
    {"key": "wines.detail.vinification", "en": "Vinification",   "notes": "Wine detail row label"},
    {"key": "wines.detail.production",   "en": "Production",     "notes": "Wine detail row label"},
    # Collection word + footer
    {"key": "wines.collection_suffix", "en": "Collection",
     "notes": 'Appended after the collection name (e.g. "Volcanica Collection"). In Greek likely "Συλλογή" placed BEFORE the name — flag if grammar requires re-ordering.'},
    {"key": "wines.alc_template",      "en": "alc.{n}% by vol.",
     "notes": "Footer of the wine card. Keep the {n} placeholder; only translate around it."},
    # Three Directions slide
    {"key": "wines.collections.eyebrow", "en": "Our Collections", "notes": "Collections slide — eyebrow"},
    {"key": "wines.collections.title",   "en": "Three Directions","notes": "Collections slide — big title"},
    {"key": "wines.collections.monopatia.desc",
     "en": "A collection of unconventional wines inspired by Dodecanese's old stone paths celebrating creative freedom and authentic uniqueness.",
     "notes": "Monopàtia collection description"},
    {"key": "wines.collections.nereides.desc",
     "en": "A collection produced with selected grapes from rare Dodecanese vineyards and varieties.",
     "notes": "Nereides collection description"},
    {"key": "wines.collections.volcanica.desc",
     "en": "Single-island wines. Every grape grown and harvested on Nisyros. Pure volcanic terroir, Aegean wind, nothing else.",
     "notes": "Volcanica collection description"},
]
add_sheet(wb, "4. Wines (UI)", wines_ui_rows,
          intro="Fixed labels around the wine cards (intro slide, body labels, detail rows, collections slide). Per-wine content is in the next sheet.")

# ── 5. WINES CMS ─────────────────────────────────────────────────────────
# Reference list — actual translation happens in the Google Sheet, with new
# columns suffixed _el. Listed here so the translator has the full picture.
wines_cms_rows = [
    {"key": "(reference)", "en": "The 5 wines live in a Google Sheet (tab `wines`). For each wine the translator will fill Greek versions in new columns suffixed `_el`:",
     "notes": "Read-only intro row"},
    {"key": "wine.name",         "en": "name",
     "notes": "Usually stays in the original (proper noun)."},
    {"key": "wine.subtitle",     "en": "subtitle",
     "notes": "One-liner under the wine name."},
    {"key": "wine.body",         "en": "body (3 parts separated by `||`)",
     "notes": "Part 1 = Story, Part 2 = Winemaking, Part 3 = Tasting Notes. Keep the `||` separators when translating."},
    {"key": "wine.vintages",     "en": "vintages",     "notes": "Years usually stay numeric."},
    {"key": "wine.type",         "en": "type",         "notes": "e.g. White / Red / Skin contact"},
    {"key": "wine.variety",      "en": "variety",      "notes": "Grape varieties — translate where a Greek name exists, otherwise keep latin."},
    {"key": "wine.appellation",  "en": "appellation",  "notes": "PGI / PDO descriptor"},
    {"key": "wine.origin",       "en": "origin",       "notes": "Location / vineyard"},
    {"key": "wine.altitude",     "en": "altitude",     "notes": "e.g. 250m. Number stays."},
    {"key": "wine.soil",         "en": "soil",         "notes": "e.g. Volcanic ash"},
    {"key": "wine.vinification", "en": "vinification", "notes": "Brief winemaking note"},
    {"key": "wine.production",   "en": "production",   "notes": "e.g. 1,500 bottles"},
    {"key": "(current wines)", "en":
        "Wines currently on the site: (1) 3,2,1 — Nereides · (2) 40 Milia Konda — Nereides · (3) Roudià — Volcanica · (4) Apiri — Monopàtia · (5) Atmida — Monopàtia",
     "notes": "For reference."},
]
add_sheet(wb, "5. Wines (CMS)", wines_cms_rows,
          intro="REFERENCE ONLY — per-wine content lives in Google Sheets, not in this file. New `_el` columns will be added to the `wines` tab.")

# ── 6. FACES ──────────────────────────────────────────────────────────────
faces_rows = [
    {"key": "faces.title.line1", "en": "Faces",     "notes": "Section title, line 1"},
    {"key": "faces.title.line2", "en": "& Places",  "notes": "Section title, line 2"},
    {"key": "faces.intro",
     "en": "The island. The people. The bottles. What the cellar smells like at five in the morning.",
     "notes": "Section intro caption"},
    {"key": "faces.aria.close",    "en": "Close",     "notes": "Lightbox close button — screen reader label"},
    {"key": "faces.aria.previous", "en": "Previous",  "notes": "Lightbox previous button — screen reader label"},
    {"key": "faces.aria.next",     "en": "Next",      "notes": "Lightbox next button — screen reader label"},
    {"key": "faces.aria.menu",     "en": "Menu",      "notes": "Hamburger button — screen reader label"},
    {"key": "(reference)",
     "en": "Per-photo `label` and `text` captions live in Google Sheets (tab `faces`). The translator will fill `label_el` and `text_el` columns there.",
     "notes": "Read-only — CMS-driven"},
]
add_sheet(wb, "6. Faces", faces_rows)

# ── 7. CONTACT ────────────────────────────────────────────────────────────
contact_rows = [
    {"key": "contact.title.line1", "en": "Find",     "notes": "Section title, line 1"},
    {"key": "contact.title.line2", "en": "Us",       "notes": "Section title, line 2"},
    {"key": "contact.subtitle",
     "en": "We are a small operation on a small island. We answer every message ourselves.",
     "notes": "Section subtitle"},

    {"key": "contact.location.label",   "en": "Location",   "notes": "Block label"},
    {"key": "contact.location.value",   "en": "Nisyros",    "notes": "Big value — Νίσυρος"},
    {"key": "contact.location.line1",   "en": "Mandraki village", "notes": "Address line 1"},
    {"key": "contact.location.line2",   "en": "Nisyros, Dodecanese", "notes": "Address line 2"},
    {"key": "contact.location.line3",   "en": "Greece 853 03", "notes": "Address line 3 (postcode)"},
    {"key": "contact.location.map_link","en": "See on map", "notes": "Google Maps link text"},

    {"key": "contact.reach.label",    "en": "Contact",    "notes": "Block label"},
    {"key": "contact.reach.email",    "en": "e-mail",     "notes": "Link text"},
    {"key": "contact.reach.whatsapp", "en": "whatsapp",   "notes": "Link text"},
    {"key": "contact.reach.note",
     "en": "We reply as soon as we can, but we're often out in the vineyard…",
     "notes": "Sub-note under contact links"},

    {"key": "contact.visits.label", "en": "Visits & Tastings", "notes": "Block label"},
    {"key": "contact.visits.value", "en": "By Appointment",    "notes": "Big value"},
    {"key": "contact.visits.note",
     "en": "We welcome curious visitors. We prefer real conversation over guided tours, so please write to us in advance — especially for tastings. But if you're passing by, knock on the door. If we're around, we'll open it.",
     "notes": "Sub-note"},

    {"key": "contact.social.label", "en": "Follow", "notes": "Block label"},
    {"key": "contact.social.note",  "en": "The vineyard, the cellar, the island. Unfiltered.",
     "notes": "Sub-note under @nisyroswines handle"},

    {"key": "contact.trade.label", "en": "Trade & Distribution", "notes": "Block label"},
    {"key": "contact.trade.value", "en": "Limited Allocation",   "notes": "Big value"},
    {"key": "contact.trade.note",
     "en": "Production is small and we work with a handful of importers who share our values.",
     "notes": "Sub-note"},

    {"key": "footer.text",
     "en": "Nisyros Wines · Dodecanese, Greece · Volcanic Nature",
     "notes": "Site footer line. Keep the · separators."},
]
add_sheet(wb, "7. Contact", contact_rows)

# ── 8. SEO / HEAD ─────────────────────────────────────────────────────────
seo_rows = [
    {"key": "seo.title",
     "en": "Nisyros Wines — Volcanic Natural Wines from the Aegean Sea",
     "notes": "<title> tag — keep it under ~65 chars in Greek if possible"},
    {"key": "seo.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece. Indigenous grape varieties, minimal intervention, volcanic terroir.",
     "notes": "<meta description>. A Greek version already exists in head.html — review and refine: Μικρός παραγωγός φυσικών κρασιών στη Νίσυρο, ηφαιστειογενές νησί στα Δωδεκάνησα. Αυτόχθονες ποικιλίες, ελάχιστη παρέμβαση, ηφαιστειακό terroir."},
    {"key": "seo.keywords",
     "en": "natural wines Greece, volcanic wines, Aegean wines, Nisyros, Dodecanese wines, Greek natural wine producer",
     "notes": "<meta keywords>. Greek version already in head.html: φυσικά κρασιά Ελλάδα, ηφαιστειακά κρασιά, κρασιά Αιγαίου, Νίσυρος, Δωδεκάνησα, Ελληνικά φυσικά κρασιά"},
    {"key": "seo.og.title",
     "en": "Nisyros Wines — Volcanic Natural Wines from the Aegean Sea",
     "notes": "Open Graph title (social share preview). Usually = seo.title."},
    {"key": "seo.og.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece.",
     "notes": "Open Graph description (shorter than seo.description)."},
    {"key": "seo.og.locale", "en": "en_GB", "notes": "For Greek version use `el_GR` — fixed value, no translation needed."},
    {"key": "seo.schema.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece. Indigenous grape varieties, minimal intervention, volcanic terroir.",
     "notes": "Schema.org Winery `description`. Usually = seo.description."},
]
add_sheet(wb, "8. SEO", seo_rows,
          intro="Meta tags and structured data. Some Greek copy already exists in head.html — translator should review and refine, not re-write from scratch.")

wb.save(OUT)
print("✓ Wrote", OUT)
