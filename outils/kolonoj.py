#!/usr/bin/env python3
# ===================================================================
#  kolonoj.py — la forme et la langue des colonnes traduites
#
#  UN CONTROLE PAR COLONNE, ET IL NE CONTROLE PAS LA MEME CHOSE QUE
#  LES AUTRES. renvoji.py verifie que les renvois visent les memes
#  objets dans le meme ordre ; objekti.py, que chaque objet de chaque
#  planche est nomme ; controles.py, la pagination et l'appariement
#  des cles. Aucun ne regarde la MATIERE d'un fichier de traduction :
#  ses macros, ses coupures, et — pour les colonnes qui existent parce
#  qu'elles ne sont pas leur voisine — sa langue.
#
#  CE QUI L'A RENDU NECESSAIRE, une faute a la fois :
#
#   * « \textuperscript{(74)} », un s manquant, au tableau 11
#     cantonais. renvoji.py ne pouvait PAS la voir : il releve aussi
#     les renvois composes « (74) » a plein corps, parce que le releve
#     ido en compose ainsi au tableau 5. Le renvoi sortait donc juste
#     et le fichier composait faux.
#   * quatre « \nl » restes dans le tcheque, l'irlandais et le
#     galicien — une traduction ne suit aucune ligne du fac-simile.
#   * une accolade ouverte en fin de ligne, qui met une espace DEDANS
#     le groupe gras.
#   * un renvoi mis en gras au lieu d'en exposant, au tableau 10
#     egyptien : meme angle mort que le premier.
#   * trois blocs marathis ampute d'un fragment de phrase par une
#     reprise faite au numero de ligne. renvoji.py n'en a signale
#     qu'un — celui qui avait perdu un renvoi.
#
#  ET LA LANGUE, pour trois colonnes qui doivent se justifier d'exister
#  a cote d'une voisine : le cantonais contre le chinois, l'arabe
#  egyptien contre l'arabe standard, le marathi contre le hindi. Si
#  l'une d'elles ecrivait la langue de sa voisine, elle ferait double
#  emploi — et c'est le motif exact qui a fait ecarter le wu. On releve
#  donc les formes que la colonne NE DOIT PAS porter.
#
#  UN SIGNALEMENT DE LANGUE N'EST PAS TOUJOURS UNE FAUTE, et deux
#  l'ont prouve : le vieux cordonnier du tableau 7 egyptien oppose
#  lui-meme « صانع أحذية » a « جزمجي », et « طاولة » au tableau 13
#  n'est pas une table mais le trictrac. Les deux sont exemptes par
#  leur forme EXACTE, jamais par le mot : un controle qu'on desarme en
#  bloc ne controle plus rien.
#
#  USAGE
#      python3 outils/kolonoj.py            # toutes les colonnes
#      python3 outils/kolonoj.py yue mr     # celles-la
# ===================================================================

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
import renvoji                                              # noqa: E402

LARGO = 94          # caracteres, non octets : l'arabe et le devanagari
#                     en mettent beaucoup dans peu de largeur.

# LES MACROS QU'UNE TRADUCTION A LE DROIT D'ECRIRE. Tout le reste est
# une coquille — ou une macro de TRANSCRIPTION, qui n'a rien a faire
# ici : \nl, \cc et VUpage suivent les lignes et les feuillets du
# fac-simile, qu'une traduction ne suit pas.
CONNUES = {"VUgras", "VUnotes", "VUsaut", "VUcentre", "VUfilet", "VUtitre",
           "VUpk", "VUcontinue", "VUblancAlinea", "VUornamento",
           "textsuperscript", "textit", "textsc", "parplein",
           "centering", "par", "fontsize", "selectfont", "textls",
           "scshape"}

# LES DEUX COLONNES QUE CET OUTIL NE REGARDE PAS. io et fr ne sont pas
# des traductions mais des TRANSCRIPTIONS : elles suivent les lignes et
# les feuillets du fac-simile, donc elles ecrivent legitimement \nl,
# \cc et VUpage, et leurs lignes sont aussi longues que celles de 1926.
# Les leur reprocher reviendrait a leur reprocher d'etre fideles.
TRANSCRIPTIONS = {"io", "fr"}

DEVA = r"[\u0900-\u097F]"


def _deva(*formes):
    """Frontiere de mot en devanagari, faute de pouvoir compter sur \\b.

    LE \\b DE PYTHON EST INUTILISABLE EN DEVANAGARI : le virama « ् »
    et les matras sont des marques combinantes, que str.isalnum()
    rejette. Python voit donc une frontiere AU MILIEU de « प्रत्येक »,
    et « \\bये\\b » y trouve un pronom hindi qui n'existe pas — douze
    signalements, tous faux, au premier jet du tableau 1 marathi.
    """
    return "|".join(f"(?<!{DEVA}){re.escape(f)}(?!{DEVA})" for f in formes)


def _mot(*formes):
    return "|".join(rf"\b{re.escape(f)}\b" for f in formes)


# -------------------------------------------------------------------
#  LES COLONNES QUI ONT UNE LANGUE A DEFENDRE
# -------------------------------------------------------------------
#  {kodo: {"mot": [(motif, ce qu'il faut ecrire)], "exemptes": [...]}}
#
#  Les colonnes absentes de cette table ne subissent que le controle de
#  forme, qui vaut pour toutes.
LINGUI = {

    # LE CANTONAIS CONTRE LE CHINOIS STANDARD. Les quatorze marqueurs
    # sont poses en tete de texto/yue/10-toubiu-01.tex ; on releve ici
    # les formes du nord qui les remplaceraient.
    "yue": {"mot": [
        (_mot("是"), "係"), (_mot("在"), "喺"), (_mot("的"), "嘅"),
        (_mot("不"), "唔"), (_mot("了"), "咗"), (_mot("他"), "佢"),
        (_mot("沒有"), "冇"), (_mot("看"), "睇"), (_mot("拿"), "攞"),
        (_mot("給"), "畀"), (_mot("很"), "好"), (_mot("們"), "哋"),
    ]},

    # L'ARABE EGYPTIEN CONTRE L'ARABE STANDARD.
    "arz": {"mot": [
        (_mot("هذه"), "دي"), (_mot("هذا"), "ده"), (_mot("هؤلاء"), "دول"),
        (_mot("ذلك"), "ده"), (_mot("تلك"), "دي"),
        (_mot("ليس", "ليست", "ليسوا"), "مش"),
        (_mot("الذي", "التي", "الذين"), "اللي"),
        (_mot("سوف"), "حـ / هـ"),
        (_mot("ماذا"), "إيه"), (_mot("كيف"), "إزاي"), (_mot("أين"), "فين"),
        (_mot("لماذا"), "ليه"), (_mot("متى"), "إمتى"),
        (_mot("الآن"), "دلوقتي"), (_mot("عندما", "حينما"), "لما"),
        (_mot("جدًا", "جداً"), "أوي"),
        (_mot("كثيرًا", "كثيرة", "كثيرون"), "كتير"),
        (_mot("أيضًا", "أيضاً"), "كمان"), (_mot("فقط"), "بس"),
        (_mot("ثلاثة", "ثلاث"), "تلاتة / تلات"),
        (_mot("ثمانية", "ثماني"), "تمانية / تمن"),
        (_mot("سيارة", "سيارات"), "عربية"),
        (_mot("غرفة", "غرف"), "أوضة"),
        (_mot("نافذة", "نوافذ"), "شباك"),
        (_mot("حقيبة", "حقائب"), "شنطة"),
        (_mot("حذاء", "أحذية"), "جزمة"),
        (_mot("طاولة", "طاولات"), "ترابيزة"),
        (_mot("جدار", "جدران"), "حيطة"),
        (_mot("شيء", "أشياء"), "حاجة"),
        (_mot("أسماء"), "أسامي"), (_mot("ملابس"), "هدوم"),
        (_mot("معطف", "معاطف"), "بالطو"),
        (_mot("ممحاة"), "أستيكة"), (_mot("مصباح"), "لمبة"),
    ], "exemptes": [
        # LA CHUTE DU VIEUX CORDONNIER, tableau 7 : « en ville je
        # m'appelais صانع أحذية et je n'avais pas de clients ; ici je
        # m'appelle جزمجي et le travail ne manque pas ». Le mot savant
        # EST la plaisanterie, et l'ido l'a deja sous la forme
        # « shuifisto » / « shureparisto ».
        "(صانع أحذية)",
        # AU TABLEAU 13, « طاولة » N'EST PAS UNE TABLE : c'est le
        # trictrac, qui porte ce nom-la en egyptien et pas un autre. Le
        # signalement ordinaire est juste PRECISEMENT parce que le mot
        # est pris ailleurs.
        "طاولة} \\textsuperscript{(81)",
    ], "virgule": True},

    # LE MARATHI CONTRE LE HINDI. Deux langues, un meme alphabet.
    # « हो », « का » et « की » ne sont PAS releves : le marathi dit हो
    # pour « oui », का pour « pourquoi » et की pour « que ».
    "mr": {"mot": [
        (_deva("है", "हैं", "हूँ"), "आहे / आहेत"),
        (_deva("था", "थे", "थी"), "होता / होते / होती"),
        (_deva("नहीं"), "नाही"), (_deva("को"), "ला"),
        (_deva("और"), "आणि"), (_deva("लेकिन"), "पण"),
        (_deva("क्योंकि"), "कारण"), (_deva("बहुत"), "खूप"),
        (_deva("यह", "वह", "ये", "वे"), "हा / ही / हे / तो / ती / ते"),
        (_deva("कुछ"), "काही"), (_deva("सब"), "सर्व"),
        (_deva("लोग"), "लोक"), (_deva("भी"), "सुद्धा / पण"),
        (_deva("यहाँ", "वहाँ"), "इथे / तिथे"), (_deva("अब"), "आता"),
        (_deva("क्या"), "काय"), (_deva("कैसे"), "कसे"),
        (_deva("कहाँ"), "कुठे"),
        (_deva("लड़का", "लड़के", "लड़की"), "मुलगा / मुलगी"),
        (_deva("आदमी"), "माणूस"), (_deva("पानी"), "पाणी"),
        (_deva("छोटा", "छोटी", "छोटे"), "लहान"),
        (_deva("बड़ा", "बड़ी", "बड़े"), "मोठा / मोठी / मोठे"),
        (_deva("दरवाज़ा", "दरवाजा"), "दार"),
        (_deva("किताब"), "पुस्तक"),
        (_deva("आँख", "आंख", "आँखें"), "डोळा / डोळे"),
        (_deva("सड़क"), "रस्ता"),
        # LES TROIS MOTS D'APPARAT NE SE RELEVENT QUE SOUS LEUR
        # FORME D'APPARAT. « दृश्य » est du marathi parfaitement
        # ordinaire — une vue, un spectacle — et le tableau 10
        # l'emploie deux fois a bon droit ; ce qui serait fautif
        # est « पहिले दृश्य » a la place de « पहिला प्रवेश ». On vise
        # donc le mot PRECEDE DE SON ORDINAL, jamais le mot seul :
        # un controle trop large se fait desarmer, et un controle
        # desarme ne controle plus rien.
        (_deva("तालिका क्रमांक"), "तक्ता क्रमांक"),
        (_deva("पहिले दृश्य", "दुसरे दृश्य", "तिसरे दृश्य",
               "चौथे दृश्य"), "पहिला प्रवेश ..."),
        (_deva("पहिली शृंखला", "दुसरी शृंखला", "तिसरी शृंखला",
               "चौथी शृंखला"), "पहिली मालिका ..."),
    ], "exemptes": [
        # « ये » EST AUSSI L'IMPERATIF MARATHI DE « VENIR ». Le hindi
        # ecrit ये pour « ceux-ci » ; le marathi, lui, conjugue येणे et
        # dit « ये रे » — viens donc. Deux langues, un meme alphabet, et
        # cette fois les deux mots s'ecrivent avec exactement les memes
        # signes : aucune frontiere, aucune matra ne les separe. On
        # exempte la forme suivie de sa particule, jamais le mot seul.
        "ये रे",
        # « ये-जा », LE VA-ET-VIENT : meme verbe येणे, meme deux
        # signes que le pronom hindi. Le tableau 9 l'ecrit de la
        # chaussee qui facilite les communications.
        "ये-जा",
        # « दरवाजा » N'EST PAS TOUJOURS DU HINDI. Le marathi dit दार
        # pour la porte d'une maison — c'est la regle, et la colonne
        # l'applique partout — mais दरवाजा pour la GRANDE porte
        # d'un fort, celle qu'on appelle महादरवाजा au Maharashtra.
        # Le tableau 11 parle de la porte du vieux chateau fortifie
        # flanquee de ses deux tours : c'est ce mot-la et pas
        # l'autre. Exemptee par sa forme exacte, avec son renvoi ;
        # la graphie hindi दरवाज़ा, avec son nukta, reste relevee
        # partout, et दरवाजा aussi ailleurs qu'ici.
        r"\VUgras{दरवाजा} \textsuperscript{(8)}",
    ]},

    # LE TELOUGOU CONTRE LE HINDI, ET LE CAS EST DIFFERENT DES TROIS
    # AUTRES. Le cantonais, l'egyptien et le marathi devaient se
    # defendre contre une voisine PROCHE ; le telougou est dravidien
    # et n'a aucune parente avec les colonnes indiennes du releve. Le
    # risque n'est donc pas de derailler vers le hindi mais d'y
    # puiser un mot savant la ou le telougou en a un a lui — ce que
    # font les traductions pressees. On releve les formes hindi et
    # sanskrites que le telougou courant ne dit pas.
    "te": {"mot": [
        (_mot("है", "हैं", "था", "थे"), "ఉంది / ఉన్నాయి"),
        (_mot("नहीं"), "లేదు / కాదు"),
        (_mot("और"), "మరియు"), (_mot("लेकिन"), "కానీ"),
        (_mot("क्योंकि"), "ఎందుకంటే"), (_mot("बहुत"), "చాలా"),
        (_mot("यह", "वह"), "ఇది / అది"),
        (_mot("क्या", "कैसे", "कहाँ"), "ఏమిటి / ఎలా / ఎక్కడ"),
        # LES MOTS D'APPARAT, VISES SOUS LEUR SEULE FORME D'APPARAT,
        # comme pour le marathi : « దృశ్యం » est du telougou
        # parfaitement ordinaire pour une vue.
        (_mot("తాలికా", "తాలిక"), "పట్టిక"),
        (_mot("మొదటి దృశ్యం", "రెండవ దృశ్యం", "మూడవ దృశ్యం",
              "నాలుగవ దృశ్యం"), "మొదటి రంగం ..."),
    ]},

    # LE COREEN CONTRE LE HANJA. Les autres colonnes se defendent
    # contre une langue VOISINE qui partage leur alphabet — le
    # cantonais contre le mandarin, le marathi contre le hindi. Le
    # coreen n'a pas de voisin de ce genre : le hangul n'est partage
    # par personne. Ce qui le guette est autre chose, et plus simple :
    # le mot sino-coreen ecrit en ideogrammes, comme on l'imprimait
    # encore en 1926. Le coreen de 2026 s'ecrit tout en hangul ; un
    # seul ideogramme dans texto/ko est donc une faute, quel qu'il
    # soit, et la regle tient en une classe de caracteres.
    "ko": {"mot": [
        (r"[\u4E00-\u9FFF]", "hangul seul — le coreen de 2026 "
                              "n'imprime plus le hanja"),
    ]},
}


def formo(f, lg, mauvais):
    """Les controles de forme, qui valent pour toutes les colonnes."""
    regle = LINGUI.get(lg, {})
    mots = regle.get("mot", [])
    exemptes = regle.get("exemptes", [])
    for i, l in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        if l.startswith("%"):
            continue
        for m in re.finditer(r"\\([A-Za-z]+)", l):
            if m.group(1) not in CONNUES:
                mauvais.append(f"{f}:{i} macro inconnue : \\{m.group(1)}")
        if "\\VUgras{}" in l:
            mauvais.append(f"{f}:{i} \\VUgras vide")
        # UNE ACCOLADE OUVERTE EN FIN DE LIGNE : le retour a la ligne se
        # rend par une espace, et l'espace tombe alors DEDANS le groupe.
        if re.search(r"\{\s*$", l):
            mauvais.append(f"{f}:{i} accolade ouverte en fin de ligne")
        # UN RENVOI MIS EN GRAS AU LIEU D'EN EXPOSANT. On ne vise que la
        # parenthese de RENVOI : le tableau 1 met legitimement en gras
        # « (ألماني وإنجليزي...) », parenthese comprise.
        if re.search(r"\\VUgras\{\((?:\d{1,3}|[a-z])\)", l):
            mauvais.append(f"{f}:{i} renvoi en gras au lieu d'exposant")
        for pat, bon in mots:
            m = re.search(pat, l)
            if m and not any(e in l for e in exemptes):
                mauvais.append(f"{f}:{i} forme etrangere « {m.group(0)} »"
                               f" -> {bon}")
        # LA VIRGULE LATINE DANS DE LA PROSE ARABE : elle ne se voit pas
        # a l'oeil dans un texte retourne de droite a gauche.
        if regle.get("virgule") and re.search(r"\}\s*,\s*$", l):
            mauvais.append(f"{f}:{i} virgule latine en arabe -> ،")
        if l.lstrip().startswith(("\\", "{")):
            continue
        if re.search(r"[^-]-$", l):
            mauvais.append(f"{f}:{i} trait d'union en fin de ligne")
        if len(l) > LARGO:
            mauvais.append(f"{f}:{i} ligne de {len(l)} caracteres")


def plenajo(lg, mot, mauvais):
    """Un bloc a-t-il perdu du texte ?

    LA CHIRURGIE PAR NUMERO DE LIGNE EST CE QUI A RENDU CE CONTROLE
    NECESSAIRE : trois blocs marathis y ont perdu un fragment de
    phrase, et renvoji.py n'en a vu qu'un — celui qui avait perdu un
    renvoi. On compare donc la LONGUEUR de chaque bloc a celle de son
    homologue ido, en caracteres, et l'on se cale sur la mediane de la
    colonne : le rapport varie beaucoup d'une ecriture a l'autre — le
    chinois dit en cent signes ce que le marathi dit en trois cents —
    mais il varie peu d'un bloc a l'autre DANS une meme colonne. Un
    bloc tombe sous la moitie de la mediane a perdu quelque chose.
    """
    io = renvoji.blocs("io", "tabelo")
    tr = renvoji.blocs(lg, mot)
    if not tr:
        return
    def net(t):
        return len(re.sub(r"\\[A-Za-z]+|[{}\s]|---", "", t))
    rap = {k: net(v) / net(io[k]) for k, v in tr.items()
           if k in io and net(io[k]) > 60}
    if len(rap) < 20:
        return
    med = sorted(rap.values())[len(rap) // 2]
    for k, r in sorted(rap.items()):
        if r < med / 2:
            mauvais.append(f"  {k} : bloc a {r / med:.0%} de la longueur "
                           f"mediane de la colonne — texte perdu ?")


def main(args):
    lgs = args or sorted(set(renvoji.DOSSIER) - TRANSCRIPTIONS)
    total = 0
    for lg in lgs:
        if lg not in renvoji.DOSSIER:
            raise SystemExit(f"  langue inconnue : {lg}")
        if lg in TRANSCRIPTIONS:
            raise SystemExit(f"  {lg} est une transcription, pas une "
                             f"traduction : elle suit le fac-simile.")
        d = RACINE / "texto" / lg
        fichiers = sorted(d.glob(f"*-{renvoji.DOSSIER[lg]}-*.tex"))
        if not fichiers:
            continue
        mauvais = []
        for f in fichiers:
            formo(f, lg, mauvais)
        plenajo(lg, renvoji.DOSSIER[lg], mauvais)
        for m in mauvais:
            print(m)
        total += len(mauvais)
        print(f"  {lg} : {len(fichiers):2d} fichiers, "
              f"{len(mauvais)} signalement{'s' if len(mauvais) > 1 else ''}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
