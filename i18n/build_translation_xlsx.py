#!/usr/bin/env python3
"""Generate nisyros-wines-translation.xlsx — full translation worksheet (el).

Includes every translatable string on the site:
  • Static HTML strings (nav, intro slides, fixed UI labels, aria, SEO)
  • CMS — Config tab (hero, manifesto, contact, footer, wines page)
  • CMS — Wines tab (per-wine: name, subtitle, body, specs, detail fields)
  • CMS — Faces tab (per-photo: label, text)

The CMS rows are fetched live from the published Google Sheets CSV at build
time, so the workbook always reflects the current source of truth.

Re-run: `python3 i18n/build_translation_xlsx.py`
"""

import csv
import io
import sys
import urllib.request

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = "/home/user/nw/i18n/nisyros-wines-translation.xlsx"

CSV_BASE = ("https://docs.google.com/spreadsheets/d/e/"
            "2PACX-1vQGec_ewoWxtdcEXP05iJm4v2LHOoyW5sZc2bSBRVMzX7vlJIX8duf1JD"
            "--qMhpihBVgHMnHJxrgwkL/pub")
SHEET_GIDS = {
    "config": "1620319001",
    "wines":  "1993474932",
    "faces":  "1521558789",
}


# ══ Greek translations (first draft — needs review by native speaker) ════
# Each dict is keyed the way the corresponding workbook row is keyed.

TR_STATIC = {
    # Nav
    "nav.manifesto": "Μανιφέστο",
    "nav.wines":     "Κρασιά",
    "nav.faces":     "Πρόσωπα",
    "nav.contact":   "Επικοινωνία",
    "nav.lang_en":   "EN",
    "nav.lang_el":   "ΕΛ",
    "nav.aria_menu": "Μενού",
    # Wines intro slide
    "wines.intro.count":       "5 Κρασιά.",
    "wines.intro.vintages":    "2 Σοδειές.",
    "wines.intro.collections": "3 Συλλογές.",
    "wines.intro.cta":         "Ανακαλύψτε >",
    # Wine card body labels
    "wines.label.story":         "Ιστορία",
    "wines.label.winemaking":    "Οινοποίηση",
    "wines.label.tasting_notes": "Σημειώσεις Γεύσης",
    # Wine detail row labels
    "wines.detail.vintages":     "Σοδειές",
    "wines.detail.type":         "Τύπος",
    "wines.detail.variety":      "Ποικιλία",
    "wines.detail.appellation":  "Ονομασία",
    "wines.detail.origin":       "Προέλευση",
    "wines.detail.altitude":     "Υψόμετρο",
    "wines.detail.soil":         "Έδαφος",
    "wines.detail.vinification": "Μέθοδος",
    "wines.detail.production":   "Παραγωγή",
    "wines.collection_suffix":   "Συλλογή",
    "wines.alc_template":        "αλκ. {n}% vol.",
    # Wines collections slide
    "wines.collections.eyebrow": "Οι Συλλογές μας",
    "wines.collections.title":   "Τρεις Κατευθύνσεις",
    # Faces
    "faces.title.line1": "Πρόσωπα",
    "faces.title.line2": "& Τόποι",
    "faces.intro":       "Το νησί. Οι άνθρωποι. Τα μπουκάλια. Πώς μυρίζει το οινοποιείο στις πέντε το πρωί.",
    "faces.aria.close":    "Κλείσιμο",
    "faces.aria.previous": "Προηγούμενο",
    "faces.aria.next":     "Επόμενο",
    # Contact UI
    "contact.title.line1":    "Βρείτε",
    "contact.title.line2":    "μας",
    "contact.label.location": "Τοποθεσία",
    "contact.label.contact":  "Επικοινωνία",
    "contact.label.visits":   "Επισκέψεις & Γευσιγνωσίες",
    "contact.label.follow":   "Ακολουθήστε",
    "contact.label.trade":    "Εμπόριο & Διανομή",
    "contact.map_link":       "Δείτε στον χάρτη",
    "contact.email_link":     "e-mail",
    "contact.whatsapp_link":  "whatsapp",
    "contact.social_note":    "Ο αμπελώνας, το οινοποιείο, το νησί. Αφιλτράριστα.",
}

TR_CONFIG = {
    "hero_location": "Νίσυρος · Αιγαίο Πέλαγος · Ελλάδα",
    "hero_tagline":  "Μια διακήρυξη.",
    # Manifesto I
    "m1_line1": "Κρασιά",
    "m1_line2": "από την",
    "m1_line3": "Άκρη",
    "m1_body":  "Η Νίσυρος είναι Ηφαίστειο. Ζωντανό. Αναπνέει, τρέμει, σου θυμίζει ποιος κουμαντάρει. Φτιάχνουμε εδώ το κρασί μας — στο χείλος του κρατήρα.",
    # Manifesto II
    "m2_line1": "Σχεδόν",
    "m2_line2": "Τίποτα",
    "m2_line3": "",
    "m2_body":  "Η ελάχιστη παρέμβαση στην οινοποίηση είναι μορφή αγάπης και σεβασμού. Δουλειά μας είναι να προστατεύουμε χωρίς να επεμβαίνουμε. Κάνουμε πίσω για να μιλήσει το αμπέλι.",
    # Manifesto III
    "m3_line1": "Με τη",
    "m3_line2": "Γη",
    "m3_body":  "Το ηφαιστειακό έδαφος της Νισύρου είναι ευλογημένη γη. Είμαστε φιλοξενούμενοι και, για μια στιγμή, φύλακες. Επί χιλιετίες η γεωργία συντηρούσε αυτό το νησί. Αναβιώνουμε αυτή την παράδοση, με σεβασμό και ατέλειωτη αφοσίωση. Το αμπέλι πρέπει να ζει εδώ πολύ μετά από εμάς.",
    # Manifesto IV
    "m4_line1": "Στους",
    "m4_line2": "Ώμους",
    "m4_line3": "Γιγάντων",
    "m4_body":  "Διαβάσαμε τα βιβλία, καθίσαμε με τους πρεσβύτερους, μάθαμε τις τοπικές παραδόσεις. Μελετάμε ζύμωση, μικροβιολογία, αμπελουργία. Και τους νόμους της φυσικής και της φύσης: θερμοκρασία, πίεση, χρόνος, κλίμα, εποχές. Η γνώση είναι η ελευθερία μας.",
    # Manifesto V
    "m5_line1": "Δοκιμάζουμε",
    "m5_line2": "πράγματα που",
    "m5_line3": "Αποτυγχάνουν",
    "m5_body":  "Ψάχνουμε σπάνιους αμπελώνες, ζυμώνουμε σε ασυνήθιστα δοχεία, αναμιγνύουμε το απρόσμενο. Η αποτυχία είναι μέρος της δημιουργίας. Απαραίτητη, για να συμβεί κάποιες φορές κάτι εξαιρετικό. Αλλά τίποτα δεν φεύγει από το οινοποιείο μας αν δεν είμαστε πραγματικά περήφανοι γι' αυτό.",
    # Manifesto VI
    "m6_line1": "Κάνουμε",
    "m6_line2": "Ό,τι Λέμε",
    "m6_body":  "Μοιραζόμαστε μαζί σας την ιστορία, τον αμπελώνα, τη σοδειά, κάθε βήμα της διαδικασίας.\\nΤις φωτεινές στιγμές, τις σκοτεινές ώρες. Κάνουμε ό,τι λέμε. Λέμε ό,τι κάνουμε. Η εμπιστοσύνη είναι μέρος του μπουκαλιού.",
    # Credo
    "credo_line1": "Μήνυμα",
    "credo_line2": "στο",
    "credo_line3": "μπουκάλι",
    "credo_body":  "Το ατελείωτο καλοκαίρι. Το φως του Αιγαίου στο ηλιοβασίλεμα. Ο άνεμος, τα κύματα, η ελευθερία. Αυτά τα νησιά είναι δώρο. Όπως και αυτά τα κρασιά. Μοναδικά, ανεπανάληπτα. Πιστά στη γη. Καθαρά στο ποτήρι.",
    # Contact
    "contact_subtitle":     "Είμαστε μια μικρή ομάδα σε ένα μικρό νησί. Απαντάμε οι ίδιοι σε κάθε μήνυμα.",
    "contact_loc_value":    "Νίσυρος",
    "contact_loc_sub":      "Μανδράκι\\nΝίσυρος, Δωδεκάνησα\\nΕλλάδα 853 03",
    "contact_email_value":  "daily@nisyroswines.com",
    "contact_email_sub":    "Απαντάμε όσο πιο γρήγορα μπορούμε, αλλά συχνά είμαστε στον αμπελώνα…",
    "contact_visits_value": "Με Ραντεβού",
    "contact_visits_sub":   "Καλωσορίζουμε τους περίεργους επισκέπτες. Προτιμάμε την αληθινή συζήτηση από τις ξεναγήσεις, γι' αυτό γράψτε μας εκ των προτέρων — ιδιαίτερα για γευσιγνωσίες. Αλλά αν περνάτε από εδώ, χτυπήστε την πόρτα. Αν είμαστε γύρω, θα ανοίξουμε.",
    "contact_trade_value":  "Περιορισμένη Διάθεση",
    "contact_trade_sub":    "Η παραγωγή είναι μικρή και συνεργαζόμαστε με λίγους εισαγωγείς που μοιράζονται τις αξίες μας.",
    "footer_text":          "Nisyros Wines · Δωδεκάνησα, Ελλάδα · Ηφαιστειακή Φύση",
    # Wines page
    "wines_subtitle": "Τρεις συλλογές. Έξι κρασιά. Δύο σοδειές.",
    "coll_1_name":    "Monopàtia",
    "coll_1_desc":    "Μια συλλογή ανορθόδοξων κρασιών εμπνευσμένη από τα παλιά πέτρινα μονοπάτια των Δωδεκανήσων, που γιορτάζει τη δημιουργική ελευθερία και την αυθεντική μοναδικότητα.",
    "coll_2_name":    "Nereides",
    "coll_2_desc":    "Μια συλλογή που παράγεται από επιλεγμένα σταφύλια σπάνιων αμπελώνων και ποικιλιών των Δωδεκανήσων.",
    "coll_3_name":    "Volcanica",
    "coll_3_desc":    "Κάθε σταφύλι καλλιεργείται και τρυγάται στη Νίσυρο. Καθαρό ηφαιστειακό terroir, αέρας του Αιγαίου, τίποτα άλλο.",
}

# Wines: keyed as "{wine_id}.{field}". Numbers, percentages and brand names
# kept in latin; grape varieties rendered in Greek script.
TR_WINES = {
    # w1 — 3 2 1...
    "w1.name":         "3 2 1...",
    "w1.subtitle":     "Μια ιστορία ξετυλίγεται",
    "w1.type":         "Λευκό",
    "w1.body": (
        "Η στιγμή που πραγματικά ξεκίνησε το ταξίδι μας στην οινοποίηση: η πρώτη φορά που σταθήκαμε πάνω από τους αμπελώνες του Αττάβυρου στον Έμπωνα της Ρόδου, όπου αρχαία αμπέλια γαντζώνονται σε βραχώδεις πλαγιές, σμιλεμένα από τον χρόνο, τον άνεμο και τα χέρια γενεών. Ξηρικό Αθήρι, καλλιεργημένο με το χέρι, με εξαιρετικά χαμηλές αποδόσεις. Αμπέλια εκατονταετίας, προ φυλλοξήρας, σε δροσερά αμμώδη-σχιστόλιθικα εδάφη στα 900 μέτρα. || "
        "Αργή ζύμωση σε χαμηλές θερμοκρασίες με αυτόχθονες ζύμες, παλαίωση οκτώ μηνών στις οινολάσπες. Αφιλτράριστο, διατηρώντας τη φυσική του δομή. || "
        "Λαμπερό. Αρωματικό. Μεταλλικό. Αρώματα φλούδας εσπεριδοειδών, γκρέιπφρουτ και άνθους πορτοκαλιάς ξεδιπλώνονται σε νότες αμυγδάλου και φρέσκου ψωμιού. Κομψό, ισορροπημένο, με ζωντανή οξύτητα και μακρά μεταλλική επίγευση. Η καθαρή έκφραση ενός διαχρονικού τοπίου. Πιείτε το με αγάπη. Αυτά τα αμπέλια περιμένουν εκατό χρόνια."
    ),
    "w1.specs":        "Αθήρι 100% | Αμπέλια εκατονταετίας χωρίς εμβολιασμό | Ελάχιστη παρέμβαση | ΠΓΕ Δωδεκανήσου",
    "w1.variety":      "100% Αθήρι",
    "w1.appellation":  "ΠΓΕ Δωδεκανήσου",
    "w1.origin":       "Έμπωνας, Ρόδος",
    "w1.altitude":     "400-900μ",
    "w1.soil":         "Σχιστόλιθος, Άμμος",
    "w1.vinification": "Ανοξείδωτος χάλυβας, αυτόχθονες ζύμες.",
    "w1.production":   "5000",
    "w1.vintages":     "2024 | 2025",

    # w2 — 40 Milia Konda
    "w2.name":         "40 Milia Konda",
    "w2.subtitle":     "Ένα κοινό τραπέζι",
    "w2.type":         "Ημιαφρώδες Ροζέ",
    "w2.body": (
        "Σαράντα μίλια ανοιχτής θάλασσας χωρίζουν το οινοποιείο μας από τον παλιό αμπελώνα όπου καλλιεργούνται αυτά τα σταφύλια. Οι αγρότες που κράτησαν αυτά τα αμπέλια ζωντανά μέσα από γενιές έγιναν οικογένεια. Ανάμεσά μας, σαράντα μίλια μοιάζουν με ένα κοινό τραπέζι. Konda: κοντά, όχι μακριά. || "
        "95% Αθήρι, 5% Μανδηλαριά από τους αμπελώνες της Σιάννας και του Έμπωνα στη Ρόδο. Συνδυασμός τεχνικών οινοποιείου: σύντομη εκχύλιση φλούδας, λευκή οινοποίηση ερυθρών σταφυλιών και ελαφριά ανθρακική εκχύλιση. Αυθόρμητη ζύμωση με αυτόχθονες ζύμες. Επαναζύμωση σε φιάλη. || "
        "Απαλό ροζ, λεπτό, ζωντανό. Λουλουδάτες νότες, φρούτα με λευκή σάρκα, ένας ψίθυρος κόκκινων μούρων. Φρέσκο, ζουμερό, με λεπτή φυσική φυσαλίδα και καθαρή αλατούχα επίγευση. Συνοδέψτε το με τον ήχο των κυμάτων και τον φρέσκο αέρα."
    ),
    "w2.specs":        "Μανδηλαριά · Αθήρι | Συνζύμωση | Ηφαιστειακό σιδηρούχο έδαφος | Ελάχιστο SO₂ | Συλλογή Monopàtia | Αφρώδες",
    "w2.variety":      "95% Αθήρι, 5% Μανδηλαριά",
    "w2.appellation":  "ΠΓΕ Δωδεκανήσου",
    "w2.origin":       "Σιάννα, Έμπωνας, Ρόδος",
    "w2.altitude":     "150μ",
    "w2.soil":         "Ηφαιστειακό και αμμώδες",
    "w2.vinification": "Σύντομη επαφή με τη φλούδα. Ελαφριά ανθρακική εκχύλιση. Αυθόρμητη ζύμωση.",
    "w2.production":   "1800",
    "w2.vintages":     "2025",

    # w3 — Roudià
    "w3.name":         "Roudià",
    "w3.subtitle":     "Το δέντρο της ζωής",
    "w3.type":         "Ελαφρύ Ερυθρό",
    "w3.body": (
        "Στα Δωδεκάνησα, το ρόδι λέγεται «ροδιά». Στον ελληνικό μύθο και τη μνήμη, ήταν πάντα ο καρπός της ζωής και της επιστροφής — που έφαγε η Περσεφόνη, που προσφέρεται στους γάμους, που σπάει στα κατώφλια για τύχη. Καθένα κρατά εκατό σπόρους, εκατό μικρές υποσχέσεις. Όπως ο καρπός του, αυτό το κρασί αποκαλύπτει ένα βαθύ, διαμαντένιο κόκκινο: πυκνό, ζωντανό, γενναιόδωρο. || "
        "Μανδηλαριά και Αθήρι από παλιά ξηρικά αμπέλια στα ηφαιστειακά αμμώδη εδάφη της Σιάννας, Ρόδος. Πρώιμος τρύγος για τη διατήρηση της φυσικής οξύτητας και της καθαρής φρουτώδους ενέργειας. Ημι-ανθρακική εκχύλιση για την ανάδειξη του πρωτογενούς αρωματικού προφίλ. Αυθόρμητη ζύμωση σε ανοξείδωτο χάλυβα με αυτόχθονες ζύμες. Χωρίς κολλάρισμα. 8 μήνες σε ανοξείδωτο χάλυβα. || "
        "Μια έκρηξη φρέσκων μικρών κόκκινων φρούτων — φραγκοστάφυλο, μουριά, μια λεπτή πινελιά κερασιού. Νευρώδες, ελαφρύ, δροσιστικό. Ζωντανή οξύτητα, λεπτές τανίνες. Πίνεται παγωμένο. Στη ζωή, στα ατελείωτα καλοκαιρινά ηλιοβασιλέματα."
    ),
    "w3.specs":        "Μαυροθήρικο · Ασύρτικο | Ξηρικά παλιά αμπέλια | Ηφαιστειακές αναβαθμίδες | ΠΓΕ Δωδεκανήσου",
    "w3.variety":      "70% Μανδηλαριά, 30% Αθήρι",
    "w3.appellation":  "ΠΓΕ Δωδεκανήσου",
    "w3.origin":       "Σιάννα, Έμπωνας, Ρόδος",
    "w3.altitude":     "150μ",
    "w3.soil":         "Ηφαιστειακό και αμμώδες",
    "w3.vinification": "Ημι-ανθρακική εκχύλιση. Αυθόρμητη ζύμωση σε ανοξείδωτες δεξαμενές. Χωρίς κολλάρισμα.",
    "w3.production":   "2000",
    "w3.vintages":     "2025",

    # w4 — Apiri
    "w4.name":         "Apiri",
    "w4.subtitle":     "Αμφορέας",
    "w4.type":         "Πορτοκαλί",
    "w4.body": (
        "Ο ζεστός αέρας που αναπνέει μέσα από τις σχισμές του ηφαιστείου — ακόμη και μέσα στα χωριά, στα σπίτια — λέγεται Apyri. Αυτό το κρασί παίρνει το όνομά του από αυτή την ανάσα. || "
        "Ελαφριά μερική εκχύλιση φλούδας για αρωματική πολυπλοκότητα· το υπόλοιπο πιέζεται απευθείας για φρεσκάδα και τραγανότητα. Ζύμωση σε ανοξείδωτο χάλυβα και αμφορείς με αυτόχθονες ζύμες. Χωρίς κολλάρισμα. Παλαίωση σε αμφορέα. || "
        "Εξελισσόμενα αρώματα λουλουδάτων και\nεξωτικών φρούτων, μέλι, αποξηραμένο βερίκοκο, καβουρδισμένο αμύγδαλο και απαλό καπνό. Στον ουρανίσκο, ευρύ, ελαφρώς αλατούχο, με ήπιες τανίνες και ζωντανή οξύτητα, καταλήγει μακρύ και με υφή. Ένα κρασί για περίεργους πότες και τολμηρούς συνδυασμούς φαγητού."
    ),
    "w4.specs":        "Μείγμα Αθήρι | Μερική επαφή με φλούδα | Αυθόρμητη ζύμωση | Αμφορέας | Χωρίς διαύγαση | Αφιλτράριστο",
    "w4.variety":      "100% Αθήρι",
    "w4.appellation":  "-",
    "w4.origin":       "Έμπωνας, Ρόδος",
    "w4.altitude":     "400-900μ",
    "w4.soil":         "Σχιστόλιθος, Άμμος",
    "w4.vinification": "Δεκαπενθήμερη εκχύλιση φλούδας. Ζύμωση σε ανοξείδωτο χάλυβα και αμφορείς. Αυτόχθονες ζύμες.",
    "w4.production":   "3000",
    "w4.vintages":     "2024 | 2025",

    # w5 — Atmida
    "w5.name":         "Atmida",
    "w5.subtitle":     "Ηφαιστειακή φύση",
    "w5.type":         "Ροζέ",
    "w5.body": (
        "Atmida: ο ατμός που υψώνεται από το έδαφος τα δροσερά πρωινά. Μια ήσυχη υπενθύμιση για το ποιος κουμαντάρει εδώ. Αυτό είναι το πρώτο μας κρασί φτιαγμένο εξ ολοκλήρου με σταφύλια από τη Νίσυρο. Δεν θα μπορούσαμε να είμαστε πιο περήφανοι. || "
        "Δύο ποικιλίες, που τρυγήθηκαν με αντίθετη λογική: Μαυροθήρικο πρώιμα για την οξύτητα, Ασύρτικο όψιμα για τη δομή και την πολυπλοκότητα. Αποβοστρύχωση με το χέρι, πατητήρι με τα πόδια κατά την παλαιά παράδοση. Ζύμωση με αυτόχθονες ζύμες. Χωρίς κολλάρισμα. 8 μήνες σε πήλινο αμφορέα. || "
        "Απαλό, λαμπερό, διάφανο κόκκινο. Άγρια φράουλα, μικρά κόκκινα φρούτα, βαθιά γήινα και μεταλλικά αρώματα — η άμεση κληρονομιά του ηφαιστειακού εδάφους. Η ζωντανή οξύτητα συναντά τη ζεστασιά και τη γευστικότητα. Η επίγευση είναι έντονη, φρέσκια και ξεκάθαρα μεταλλική. Πίνεται ελαφρώς παγωμένο. Αυτό είναι το διαλογιστικό μας κρασί: δώστε του χρόνο, και το ηφαίστειο θα μιλήσει."
    ),
    "w5.specs":        "Ασύρτικο · Μαυροθήρικο | Άγρια ζύμωση | Χωρίς διαύγαση | Πατημένο με τα πόδια",
    "w5.variety":      "60% Ασύρτικο, 40% Μαυροθήρικο",
    "w5.appellation":  "ΠΓΕ Δωδεκανήσου",
    "w5.origin":       "Νίσυρος",
    "w5.altitude":     "400μ",
    "w5.soil":         "Ηφαιστειακό, πλούσιο σε μέταλλα",
    "w5.vinification": "Πατημένο με τα πόδια. Αυτόχθονες ζύμες. Παλαιωμένο σε Αμφορέα. Χωρίς κολλάρισμα.",
    "w5.production":   "500",
    "w5.vintages":     "2025",
}

# Faces: keyed as "#{order}.{field}".
TR_FACES = {
    "#1.label":  "Τοπίο",            "#1.text":  "Ηφαιστειακή Φύση.",
    "#2.label":  "Οινοποιείο",       "#2.text":  "Πηλός και χρόνος.",
    "#3.label":  "Οινοποιείο",       "#3.text":  "Με τα πόδια. Όπως έκαναν.",
    "#4.label":  "Τρύγος",           "#4.text":  "Federico.",
    "#5.label":  "Τρύγος",           "#5.text":  "Φίλοι όταν μετράει.",
    "#6.label":  "Άνθρωποι",         "#6.text":  "Πόδια στο χώμα. Αυτό φτάνει.",
    "#8.label":  "Επικράτεια",       "#8.text":  "Ζωή παντού.",
    "#7.label":  "Οινοποιείο",       "#7.text":  "Παλαιώνει, αργά.",
    "#10.label": "Επικράτεια",       "#10.text": "Το νησί έχει δικό του μυαλό.",
    "#11.label": "Αμπελώνας",        "#11.text": "Έμπωνας, στη Ρόδο.",
    "#12.label": "Τρύγος",           "#12.text": "Καλεσμένοι.",
    "#13.label": "Άνθρωποι",         "#13.text": "Ποδήλατα, πάντα.",
    "#14.label": "Άνθρωποι",         "#14.text": "Federico Garzelli. Οινοποιός.",
    "#15.label": "Επικράτεια",       "#15.text": "Ζωή, ζωή.",
    "#16.label": "Φύτευση",          "#16.text": "Αργά.",
    "#17.label": "Άνθρωποι",         "#17.text": "Καμία ξεκούραση.",
    "#28.label": "Οινοποιείο",       "#28.text": "Ακόμη γίνεται.",
    "#18.label": "Τρύγος",           "#18.text": "Όλοι μαζί.",
    "#19.label": "Τρύγος",           "#19.text": "Πρώτη πίεση.",
    "#20.label": "Φύτευση",          "#20.text": "Φυτεύοντας σπόρους...",
    "#21.label": "Φύτευση",          "#21.text": "Γενιές.",
    "#22.label": "Τοπίο",            "#22.text": "Το Αιγαίο κρατά το φως.",
    "#23.label": "Άνθρωποι",         "#23.text": "Θεολόγος. Σώμα και ψυχή.",
    "#24.label": "Επικράτεια",       "#24.text": "Αλώνι — ο παραδοσιακός μύλος.",
    "#25.label": "Τοπίο",            "#25.text": "Βράζει.",
    "#26.label": "Άνθρωποι",         "#26.text": "Γιώργος και Nicola, 2020. «Κι αν…»",
    "#27.label": "Οινοποιείο",       "#27.text": "Σχεδόν έτοιμο.",
}

TR_SEO = {
    "seo.title":              "Nisyros Wines — Ηφαιστειακά Φυσικά Κρασιά από το Αιγαίο",
    "seo.description":        "Μικρός παραγωγός φυσικών κρασιών στη Νίσυρο, ηφαιστειογενές νησί στα Δωδεκάνησα. Αυτόχθονες ποικιλίες, ελάχιστη παρέμβαση, ηφαιστειακό terroir.",
    "seo.keywords":           "φυσικά κρασιά Ελλάδα, ηφαιστειακά κρασιά, κρασιά Αιγαίου, Νίσυρος, Δωδεκάνησα, Ελληνικά φυσικά κρασιά",
    "seo.og.title":           "Nisyros Wines — Ηφαιστειακά Φυσικά Κρασιά από το Αιγαίο",
    "seo.og.description":     "Μικρός παραγωγός φυσικών κρασιών στη Νίσυρο, ηφαιστειογενές νησί στα Δωδεκάνησα.",
    "seo.og.locale":          "el_GR",
    "seo.schema.description": "Μικρός παραγωγός φυσικών κρασιών στη Νίσυρο, ηφαιστειογενές νησί στα Δωδεκάνησα. Αυτόχθονες ποικιλίες, ελάχιστη παρέμβαση, ηφαιστειακό terroir.",
}

HEADER_FILL = PatternFill("solid", fgColor="2B2725")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="F5F2EE")
SECTION_FILL = PatternFill("solid", fgColor="C46E4B")
SECTION_FONT = Font(name="Calibri", size=11, bold=True, color="F5F2EE", italic=True)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(border_style="thin", color="DDD6CC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def fetch_csv(name):
    url = f"{CSV_BASE}?gid={SHEET_GIDS[name]}&single=true&output=csv"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read().decode("utf-8")
    return list(csv.reader(io.StringIO(data)))


def write_header(ws, row, cols):
    for c, h in enumerate(cols, 1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def write_section_divider(ws, row, label, span):
    cell = ws.cell(row=row, column=1, value=label)
    cell.font = SECTION_FONT
    cell.fill = SECTION_FILL
    cell.alignment = Alignment(vertical="center")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)


def add_sheet(wb, name, cols, col_widths, rows, intro=None):
    """rows: list of dict (regular row) or {"__section__": "label"} (divider)."""
    ws = wb.create_sheet(name)
    r = 1
    if intro:
        ws.cell(row=r, column=1, value=intro).font = Font(italic=True, color="6B6360")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(cols))
        ws.row_dimensions[r].height = 32
        ws.cell(row=r, column=1).alignment = WRAP
        r += 2
    write_header(ws, r, cols)
    header_row = r
    r += 1
    for row in rows:
        if "__section__" in row:
            write_section_divider(ws, r, row["__section__"], len(cols))
            r += 1
            continue
        for c, key in enumerate(cols, 1):
            cell = ws.cell(row=r, column=c, value=row.get(key, ""))
            cell.alignment = WRAP
            cell.border = BORDER
        r += 1
    for c, h in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(c)].width = col_widths[c - 1]
    ws.freeze_panes = f"A{header_row + 1}"  # freeze header row
    return ws


# ══ Build workbook ════════════════════════════════════════════════════════
wb = Workbook()
wb.remove(wb.active)

# ── README ────────────────────────────────────────────────────────────────
readme = wb.create_sheet("README")
readme_lines = [
    ("Nisyros Wines — Greek translation workbook", "title"),
    ("", None),
    ("Purpose", "h2"),
    ("Column `el` is pre-filled with a first-draft Greek translation. Please review, refine and overwrite where needed.", None),
    ("Leave column `key` and `en` untouched — they wire the translation back into the site.", None),
    ("The draft was produced as a starting point — a native Greek speaker familiar with wine terminology should validate every row, especially manifesto bodies, wine tasting notes, and faces captions where the poetic register matters.", None),
    ("", None),
    ("How it's organized", "h2"),
    ("Each sheet groups related strings. Order follows the user's path through the site:", None),
    ("  1. README              — this page", None),
    ("  2. Static HTML         — nav, intro slides, fixed UI labels (Story/Winemaking/…), aria labels", None),
    ("  3. CMS — Config        — hero, full manifesto, contact texts, footer, collection descriptions", None),
    ("  4. CMS — Wines         — per-wine content (name, subtitle, body, specs, detail fields) × 5 wines", None),
    ("  5. CMS — Faces         — gallery photo captions (label + text) × ~27 photos", None),
    ("  6. SEO                 — page title, meta description, social tags, structured data", None),
    ("", None),
    ("Guidelines", "h2"),
    ("• Tone: short declarative sentences, manifesto-like, no marketing fluff.", None),
    ("• Multi-line titles split with slashes (\"Wines / from the / Edge\") render one word per line — keep that rhythm in Greek.", None),
    ("• Brand names stay in latin script: Nisyros Wines, Monopàtia, Nereides, Volcanica, 3,2,1, 40 Milia Konda, Roudià, Apiri, Atmida.", None),
    ("• Grape varieties: keep latin (Athiri, Mandilaria, Assyrtiko, Mavrothiriko) unless the brand prefers Greek script — confirm with Nicola.", None),
    ("• Geographic names: use the natural Greek form — Νίσυρος, Δωδεκάνησα, Αιγαίο, Ρόδος, Έμπωνας, Σιάννα.", None),
    ("• Numbers, percentages, volumes, alcohol degrees, altitudes stay as-is.", None),
    ("• Body text with `||` separators: keep the `||` exactly where it is. Each part is rendered in its own block (Story / Winemaking / Tasting Notes).", None),
    ("• Specs separated by `|`: keep the `|` separators between items.", None),
    ("• If a string contains `\\n`, that is a literal newline marker — keep it.", None),
    ("• If meaning is ambiguous, write a question in the `notes` column.", None),
    ("", None),
    ("Deliverable", "h2"),
    ("Save this file as-is when done. The developer copies `el` values back into the codebase and into the Google Sheet's new `_el` columns.", None),
    ("", None),
    ("Generated from the live Google Sheet — re-run i18n/build_translation_xlsx.py to refresh.", "footer"),
]
for i, (text, kind) in enumerate(readme_lines, 1):
    cell = readme.cell(row=i, column=1, value=text)
    if kind == "title":
        cell.font = Font(size=18, bold=True, color="C46E4B")
    elif kind == "h2":
        cell.font = Font(size=13, bold=True, color="2B2725")
    elif kind == "footer":
        cell.font = Font(size=10, italic=True, color="6B6360")
    else:
        cell.font = Font(size=11, color="2B2725")
    cell.alignment = Alignment(wrap_text=True, vertical="top")
readme.column_dimensions["A"].width = 120

# ── 2. STATIC HTML ───────────────────────────────────────────────────────
STATIC_COLS = ["key", "en", "el", "notes"]
STATIC_W = [32, 60, 60, 50]

static_rows = [
    {"__section__": "NAV — top navigation"},
    {"key": "nav.manifesto", "en": "Manifesto",  "notes": "Top nav link"},
    {"key": "nav.wines",     "en": "Wines",      "notes": "Top nav link"},
    {"key": "nav.faces",     "en": "Faces",      "notes": "Top nav link"},
    {"key": "nav.contact",   "en": "Contact",    "notes": "Top nav link"},
    {"key": "nav.lang_en",   "en": "EN",         "notes": "Language switcher label (English)"},
    {"key": "nav.lang_el",   "en": "EL",         "notes": "Language switcher label (Greek) — likely 'ΕΛ'"},
    {"key": "nav.aria_menu", "en": "Menu",       "notes": "Hamburger button aria-label (screen reader)"},

    {"__section__": "WINES — intro slide (above the bottle cards)"},
    {"key": "wines.intro.count",       "en": "5 Wines.",     "notes": "Big line 1, red"},
    {"key": "wines.intro.vintages",    "en": "2 Vintages.",  "notes": "Big line 2"},
    {"key": "wines.intro.collections", "en": "3 Collections.", "notes": "Big line 3"},
    {"key": "wines.intro.cta",         "en": "Discover >",   "notes": "CTA button"},

    {"__section__": "WINES — card body labels (rendered above each text block)"},
    {"key": "wines.label.story",         "en": "Story",        "notes": "Wine card — label above part 1 of body"},
    {"key": "wines.label.winemaking",    "en": "Winemaking",   "notes": "Wine card — label above part 2 of body"},
    {"key": "wines.label.tasting_notes", "en": "Tasting Notes","notes": "Wine card — label above part 3 of body"},

    {"__section__": "WINES — detail row labels (right column of each card)"},
    {"key": "wines.detail.vintages",     "en": "Vintages",     "notes": "Wine detail row label"},
    {"key": "wines.detail.type",         "en": "Type",         "notes": "Wine detail row label"},
    {"key": "wines.detail.variety",      "en": "Variety",      "notes": "Wine detail row label"},
    {"key": "wines.detail.appellation",  "en": "Appellation",  "notes": "Wine detail row label"},
    {"key": "wines.detail.origin",       "en": "Origin",       "notes": "Wine detail row label"},
    {"key": "wines.detail.altitude",     "en": "Altitude",     "notes": "Wine detail row label"},
    {"key": "wines.detail.soil",         "en": "Soil",         "notes": "Wine detail row label"},
    {"key": "wines.detail.vinification", "en": "Vinification", "notes": "Wine detail row label"},
    {"key": "wines.detail.production",   "en": "Production",   "notes": "Wine detail row label"},
    {"key": "wines.collection_suffix",   "en": "Collection",
     "notes": 'Appended after name (e.g. "Volcanica Collection"). In Greek likely "Συλλογή" placed BEFORE the name — flag if word order matters.'},
    {"key": "wines.alc_template",        "en": "alc.{n}% by vol.",
     "notes": "Wine card footer template. Keep the {n} placeholder."},

    {"__section__": "WINES — collections slide (final card)"},
    {"key": "wines.collections.eyebrow", "en": "Our Collections", "notes": "Small eyebrow over title"},
    {"key": "wines.collections.title",   "en": "Three Directions","notes": "Big title — collection descriptions live in CMS Config"},

    {"__section__": "FACES — section header + lightbox"},
    {"key": "faces.title.line1", "en": "Faces",    "notes": "Section title line 1"},
    {"key": "faces.title.line2", "en": "& Places", "notes": "Section title line 2"},
    {"key": "faces.intro",
     "en": "The island. The people. The bottles. What the cellar smells like at five in the morning.",
     "notes": "Section intro caption"},
    {"key": "faces.aria.close",    "en": "Close",    "notes": "Lightbox close button — aria label"},
    {"key": "faces.aria.previous", "en": "Previous", "notes": "Lightbox previous button — aria label"},
    {"key": "faces.aria.next",     "en": "Next",     "notes": "Lightbox next button — aria label"},

    {"__section__": "CONTACT — section title + block labels (block contents are in CMS Config)"},
    {"key": "contact.title.line1", "en": "Find", "notes": "Big section title — line 1"},
    {"key": "contact.title.line2", "en": "Us",   "notes": "Big section title — line 2"},
    {"key": "contact.label.location", "en": "Location",          "notes": "Block label"},
    {"key": "contact.label.contact",  "en": "Contact",           "notes": "Block label"},
    {"key": "contact.label.visits",   "en": "Visits & Tastings", "notes": "Block label"},
    {"key": "contact.label.follow",   "en": "Follow",            "notes": "Block label"},
    {"key": "contact.label.trade",    "en": "Trade & Distribution", "notes": "Block label"},
    {"key": "contact.map_link",       "en": "See on map",        "notes": "Google Maps link"},
    {"key": "contact.email_link",     "en": "e-mail",            "notes": "Mailto link text"},
    {"key": "contact.whatsapp_link",  "en": "whatsapp",          "notes": "WhatsApp link text"},
    {"key": "contact.social_note",
     "en": "The vineyard, the cellar, the island. Unfiltered.",
     "notes": "Sub-note under @nisyroswines handle"},
]
for r in static_rows:
    if "key" in r:
        r["el"] = TR_STATIC.get(r["key"], "")
add_sheet(wb, "2. Static HTML", STATIC_COLS, STATIC_W, static_rows,
          intro="Strings hard-coded in sections/*.html and js/main.js. These are NOT in the CMS — they live in the code and must be translated here.")

# ── 3. CMS — Config ──────────────────────────────────────────────────────
config_rows_raw = fetch_csv("config")
CFG_NOTES = {
    "hero_location":      "Caption above the wordmark on the hero",
    "hero_tagline":       "Currently unused on site — translate anyway in case it's wired up later",
    "m1_line1":  "Manifesto I — Big title line 1",
    "m1_line2":  "Manifesto I — Big title line 2",
    "m1_line3":  "Manifesto I — Big title line 3 (red accent)",
    "m1_body":   "Manifesto I — Body paragraph",
    "m2_line1":  "Manifesto II — Big title line 1",
    "m2_line2":  "Manifesto II — Big title line 2 (red accent)",
    "m2_line3":  "Manifesto II — Empty in current data; leave empty",
    "m2_body":   "Manifesto II — Body paragraph",
    "m3_line1":  "Manifesto III — Big title line 1",
    "m3_line2":  "Manifesto III — Big title line 2 (red accent)",
    "m3_body":   "Manifesto III — Body paragraph",
    "m4_line1":  "Manifesto IV — Big title line 1",
    "m4_line2":  "Manifesto IV — Big title line 2",
    "m4_line3":  "Manifesto IV — Big title line 3 (red accent)",
    "m4_body":   "Manifesto IV — Body paragraph",
    "m5_line1":  "Manifesto V — Big title line 1",
    "m5_line2":  "Manifesto V — Big title line 2",
    "m5_line3":  "Manifesto V — Big title line 3 (red accent)",
    "m5_body":   "Manifesto V — Body paragraph",
    "m6_line1":  "Manifesto VI — Big title line 1",
    "m6_line2":  "Manifesto VI — Big title line 2 (red accent)",
    "m6_body":   "Manifesto VI — Body paragraph. Contains a literal newline.",
    "credo_line1": "Credo / Manifesto VII — Big title line 1",
    "credo_line2": "Credo / Manifesto VII — Big title line 2",
    "credo_line3": "Credo / Manifesto VII — Big title line 3 (red accent)",
    "credo_body":  "Credo / Manifesto VII — Body paragraph",
    "contact_subtitle":     "Sub-title under \"Find Us\"",
    "contact_loc_value":    "Big value in Location block — \"Nisyros\" → \"Νίσυρος\"",
    "contact_loc_sub":      "Address. `\\n` = line break, keep them.",
    "contact_email_value":  "Email address — DO NOT TRANSLATE (it's the literal mailto target)",
    "contact_email_sub":    "Sub-note under contact links",
    "contact_visits_value": "Big value in Visits block",
    "contact_visits_sub":   "Sub-note in Visits block",
    "contact_trade_value":  "Big value in Trade block",
    "contact_trade_sub":    "Sub-note in Trade block",
    "footer_text":          "Page footer. Keep the · separators.",
    "wines_subtitle":       "Wines page subtitle (not yet wired into HTML — translate anyway)",
    "coll_1_name":          "Collection name — likely stays \"Monopàtia\"",
    "coll_1_desc":          "Monopàtia description (also appears on Three Directions slide)",
    "coll_2_name":          "Collection name — likely stays \"Nereides\"",
    "coll_2_desc":          "Nereides description (also appears on Three Directions slide)",
    "coll_3_name":          "Collection name — likely stays \"Volcanica\"",
    "coll_3_desc":          "Volcanica description (also appears on Three Directions slide)",
}
config_rows = []
for row in config_rows_raw:
    if not row or len(row) < 2:
        continue
    key, val = row[0], row[1]
    if not key.strip():
        continue
    if key.startswith("▸"):
        config_rows.append({"__section__": key.strip().lstrip("▸").strip()})
        continue
    config_rows.append({
        "key":   key,
        "en":    val,
        "el":    TR_CONFIG.get(key, ""),
        "notes": CFG_NOTES.get(key, ""),
    })
add_sheet(wb, "3. CMS — Config", STATIC_COLS, STATIC_W, config_rows,
          intro="Lives in Google Sheets (tab `config`). These values overwrite the HTML at runtime — translate them all. Section dividers are for orientation only.")

# ── 4. CMS — Wines ───────────────────────────────────────────────────────
wines_rows_raw = fetch_csv("wines")

# Header row in the CSV is row index 2 (after the two banner rows)
header = [c.split("\n")[0].strip().lower() for c in wines_rows_raw[2]]


def w_get(row, col):
    try:
        idx = header.index(col.lower())
    except ValueError:
        return ""
    return row[idx] if idx < len(row) else ""


WINE_COLS = ["wine", "field", "en", "el", "notes"]
WINE_W = [16, 18, 60, 60, 38]

WINE_FIELDS = [
    ("name",         "Wine name (likely stays in original)"),
    ("subtitle",     "One-liner under the wine name"),
    ("type",         "Wine type — e.g. White / Rosé / Light Red / Orange"),
    ("body",         "3 parts separated by ||  →  Story || Winemaking || Tasting Notes. KEEP the || separators."),
    ("specs",        "Pipe-separated specs shown as small tags. KEEP the | separators between items."),
    ("variety",      "Grape varieties — keep latin names (Athiri, Mandilaria…) unless the brand prefers Greek script"),
    ("appellation",  "Designation — e.g. PGI Dodecanese"),
    ("origin",       "Vineyard / location"),
    ("altitude",     "Numbers usually stay (e.g. 400-900m)"),
    ("soil",         "Soil description"),
    ("vinification", "Brief winemaking note"),
    ("production",   "Production count — number stays"),
    ("vintages",     "Years separated by `|` — keep numbers and separator"),
]
wines_rows = []
# CSV format: row 0 = banner, row 1 = instructions, row 2 = header,
# rows 3+ = either section dividers (▸…) or wines.
for row in wines_rows_raw[3:]:
    if not row or not any(c.strip() for c in row):
        continue
    first = row[0].strip()
    if first.startswith("▸"):
        wines_rows.append({"__section__": first.lstrip("▸").strip()})
        continue
    if first.startswith("📷") or first.startswith("HOW"):
        continue
    wine_id = w_get(row, "id")
    name = w_get(row, "name")
    if not wine_id or not name:
        continue
    label = f"{wine_id} — {name}"
    for field, note in WINE_FIELDS:
        val = w_get(row, field).strip()
        if not val:
            continue
        wines_rows.append({
            "wine":  label,
            "field": field,
            "en":    val,
            "el":    TR_WINES.get(f"{wine_id}.{field}", ""),
            "notes": note,
        })
add_sheet(wb, "4. CMS — Wines", WINE_COLS, WINE_W, wines_rows,
          intro="Lives in Google Sheets (tab `wines`). One row per (wine × translatable field). Final values will be written back into new `_el` columns in the sheet.")

# ── 5. CMS — Faces ───────────────────────────────────────────────────────
faces_rows_raw = fetch_csv("faces")
# CSV: row 0 = banner, row 1 = instructions, row 2 = header, rows 3+ = photos
FACES_COLS = ["photo", "field", "en", "el", "notes"]
FACES_W = [10, 12, 50, 50, 40]
faces_rows = []
for row in faces_rows_raw[3:]:
    if not row or len(row) < 4:
        continue
    order, _img, label, text = (row + [""] * 4)[:4]
    order = order.strip()
    if not order:
        continue
    if order.startswith("📷") or order.startswith("HOW"):
        continue
    if label.strip():
        faces_rows.append({
            "photo": f"#{order}",
            "field": "label",
            "en":    label,
            "el":    TR_FACES.get(f"#{order}.label", ""),
            "notes": "Short caption shown over the photo in the lightbox (e.g. Landscape, Winery, Harvest, People). Some labels repeat across photos.",
        })
    if text.strip():
        faces_rows.append({
            "photo": f"#{order}",
            "field": "text",
            "en":    text,
            "el":    TR_FACES.get(f"#{order}.text", ""),
            "notes": "One-line caption under the label.",
        })
add_sheet(wb, "5. CMS — Faces", FACES_COLS, FACES_W, faces_rows,
          intro="Lives in Google Sheets (tab `faces`). One row per (photo × translatable field). `#N` matches the `oredr` column in the sheet. Final values will be written back into new `_el` columns.")

# ── 6. SEO ───────────────────────────────────────────────────────────────
seo_rows = [
    {"key": "seo.title",
     "en": "Nisyros Wines — Volcanic Natural Wines from the Aegean Sea",
     "notes": "<title> tag — try to stay under ~65 chars in Greek"},
    {"key": "seo.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece. Indigenous grape varieties, minimal intervention, volcanic terroir.",
     "notes": "<meta description>. A draft Greek version already exists in head.html — review and refine: \"Μικρός παραγωγός φυσικών κρασιών στη Νίσυρο, ηφαιστειογενές νησί στα Δωδεκάνησα. Αυτόχθονες ποικιλίες, ελάχιστη παρέμβαση, ηφαιστειακό terroir.\""},
    {"key": "seo.keywords",
     "en": "natural wines Greece, volcanic wines, Aegean wines, Nisyros, Dodecanese wines, Greek natural wine producer",
     "notes": "<meta keywords>. Greek draft already in head.html: \"φυσικά κρασιά Ελλάδα, ηφαιστειακά κρασιά, κρασιά Αιγαίου, Νίσυρος, Δωδεκάνησα, Ελληνικά φυσικά κρασιά\""},
    {"key": "seo.og.title",
     "en": "Nisyros Wines — Volcanic Natural Wines from the Aegean Sea",
     "notes": "Open Graph title (social share preview). Usually = seo.title."},
    {"key": "seo.og.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece.",
     "notes": "Open Graph description (shorter than seo.description)."},
    {"key": "seo.og.locale", "en": "en_GB",
     "notes": "For Greek version use `el_GR` — fixed value, no translation."},
    {"key": "seo.schema.description",
     "en": "Small producer of natural wines on Nisyros, a volcanic island in the Dodecanese, Greece. Indigenous grape varieties, minimal intervention, volcanic terroir.",
     "notes": "Schema.org Winery `description`. Usually = seo.description."},
]
for r in seo_rows:
    if "key" in r:
        r["el"] = TR_SEO.get(r["key"], "")
add_sheet(wb, "6. SEO", STATIC_COLS, STATIC_W, seo_rows,
          intro="Meta tags and structured data. A draft Greek version of description/keywords already exists in head.html — review and refine, don't rewrite from scratch.")

wb.save(OUT)
print("✓ Wrote", OUT)
print("  Sheets:", ", ".join(s for s in wb.sheetnames))
