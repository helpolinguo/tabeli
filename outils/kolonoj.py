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
#  {kodo: {"mot": [(motif, ce qu'il faut ecrire)], "exemptes": [...],
#          "narracio": [(motif, ...)]}}
#
#  « narracio » PORTE LES REGLES QUI NE VALENT QUE HORS DIALOGUE.
#  Une seule colonne en a besoin, le javanais, et une seule raison
#  la lui donne : ses niveaux de langue ne se choisissent pas par
#  texte mais par QUI PARLE A QUI. La narration du livret tient le
#  ngoko ; mais au tableau 5, qui est un dialogue d'un bout a
#  l'autre, l'enfant s'adresse a son oncle, et un enfant javanais
#  parle krama a son oncle. « kula », « mboten », « sampun » y sont
#  donc les formes JUSTES, et les relever serait crier sur la
#  politesse meme que l'alinea decrit.
#
#  LE DIALOGUE SE RECONNAIT AU FICHIER, ET LA MESURE EST NETTE.
#  Les attributions de parole s'ecrivent « \textsc{...}. --- » : le
#  tableau 5 en compte TRENTE-SIX, le tableau 12 en compte UNE (et
#  c'est « Noto. », pas un locuteur), les quatorze autres n'en ont
#  aucune. Le seuil est pose a cinq, ou il n'y a rien a departager.
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

    # LE TAMOUL CONTRE LUI-MEME. C'est la premiere colonne du releve
    # dont l'adversaire n'est ni une langue voisine ni une ecriture
    # ancienne, mais un REGISTRE. Le tamoul est diglossique pour de
    # bon : la langue parlee et la langue ecrite different jusque dans
    # la conjugaison, et personne n'imprime la premiere. Un livret de
    # 1926 rendu en tamoul parle serait aussi faux qu'un livret rendu
    # en argot — non pas trop moderne, mais d'un autre usage. On
    # releve donc les marques du parle les plus sures, celles qui ne
    # peuvent pas etre autre chose.
    #
    # Deux d'entre elles demandent une precaution. « இருக்கு » est la
    # forme parlee de « இருக்கிறது », mais elle est aussi la fin de
    # « கிடைக்கு » et de quelques autres : on l'exige donc precedee
    # d'un blanc. « இல்ல » est le parle de « இல்லை » et le debut de
    # « இல்லாத » : on exige la fin de mot. Un controle qui se declenche
    # sur un mot honnete finit desarme, et un controle desarme ne
    # controle plus rien.
    "ta": {"mot": [
        (r"(?<![\u0B80-\u0BFF])இருக்கு(?![\u0B80-\u0BFF])",
         "இருக்கிறது — la colonne s'imprime, elle ne se parle pas"),
        (r"(?<![\u0B80-\u0BFF])இல்ல(?![\u0B80-\u0BFF])", "இல்லை"),
        (r"(?<![\u0B80-\u0BFF])பண்ண(?:ு|ுது|லாம்)(?![\u0B80-\u0BFF])",
         "செய் / செய்கிறது"),
        (r"(?<![\u0B80-\u0BFF])ஏன்னா(?![\u0B80-\u0BFF])", "ஏனெனில்"),
        (r"(?<![\u0B80-\u0BFF])இப்ப(?![\u0B80-\u0BFF])", "இப்போது"),
        (r"(?<![\u0B80-\u0BFF])அப்ப(?![\u0B80-\u0BFF])", "அப்போது"),
        # LES CHIFFRES TAMOULS SONT DE L'EPIGRAPHIE. Le tamoul de 2026
        # compte en chiffres arabes, dans la prose comme dans
        # l'apparat — « அட்டவணை எண் 1 » et non « எண் ௧ ». Les
        # ௰ ௱ ௲ (dix, cent, mille) sont dans la meme plage et tombent
        # sous la meme regle.
        (r"[\u0BE6-\u0BF2]", "chiffres arabes — les chiffres tamouls "
                              "ne servent plus qu'en epigraphie"),
    ]},

    # L'OURDOU CONTRE DEUX VOISINES A LA FOIS, ET C'EST UN CAS NEUF.
    # Toutes les colonnes defendues jusqu'ici l'etaient sur UN front :
    # le cantonais contre le mandarin, le marathi contre le hindi, le
    # coreen contre le hanja, le tamoul contre son propre parle.
    # L'ourdou en a deux, et de natures differentes :
    #
    #   * il partage l'ECRITURE avec le pendjabi chahmoukhi (pnb),
    #     qui est une AUTRE LANGUE. Le risque est le meme que pour le
    #     cantonais : la voisine s'ecrit dans le meme alphabet et
    #     passerait inapercue.
    #   * il partage la LANGUE avec le hindi — meme grammaire, meme
    #     lexique de base — et n'en differe que par l'ecriture et par
    #     le REGISTRE SAVANT : sanskrit d'un cote, persan et arabe de
    #     l'autre. Le hindi ne peut pas s'infiltrer en devanagari,
    #     mais son vocabulaire savant TRANSLITTERE, si.
    #
    # LE PREMIER FRONT SE TIENT PAR LA GRAMMAIRE. Le genitif pendjabi
    # « دا » n'existe pas en ourdou, qui dit « کا » : c'est le
    # marqueur le plus frequent et le plus sur de la langue voisine.
    # On NE releve PAS « دی » ni « دے », qui sont pourtant les deux
    # autres formes du meme genitif : ce sont aussi des mots ourdous
    # ordinaires — « دی » est le passe de donner, « دے » son
    # imperatif. Un controle qui les prendrait crierait a chaque
    # page, et un controle qui crie finit desarme.
    #
    # LE SECOND SE TIENT PAR LE LEXIQUE, et les mots vises sont des
    # tatsama que l'ourdou imprime n'emploie jamais — non parce
    # qu'ils seraient trop savants, mais parce que sa colonne savante
    # est l'autre.
    "ur": {"mot": [
        (_mot("دا"), "کا — genitif pendjabi"),
        (_mot("دوجا", "تیجا"), "دوسرا / تیسرا"),
        # « اوہ » EST LE « اوہ » PENDJABI (« lui ») ET L'INTERJECTION
        # OURDOUE (« oh ! ») : deux mots pour une seule graphie. On
        # ne le releve pas, et l'on garde « ایہہ », qui n'est que
        # pendjabi.
        (_mot("ایہہ"), "یہ"),
        (_mot("نئیں"), "نہیں"),
        (_mot("کیتا"), "کیا"),
        (_mot("توں"), "سے"),
        (_mot("کول"), "پاس"),
        (_mot("جیہڑا", "جیہڑی"), "جو"),
        (_mot("ساڈا", "تہاڈا"), "ہمارا / تمہارا"),
        # LES TATSAMA DU HINDI, VISES SOUS LEUR FORME TRANSLITTEREE.
        (_mot("ودیالیہ"), "اسکول / مدرسہ"),
        (_mot("ودیارتھی"), "طالب علم"),
        (_mot("ادھیاپک"), "استاد"),
        (_mot("پستک"), "کتاب"),
        (_mot("پرارتھنا"), "دعا"),
        (_mot("سمے"), "وقت"),
        (_mot("ورش"), "سال"),
        (_mot("ناری"), "عورت"),
        (_mot("کاریہ"), "کام"),
    ]},
    # L'INDONESIEN SE DEFEND SUR DEUX FRONTS, ET AUCUN DES DEUX N'EST
    # UNE COLONNE VOISINE. Sa voisine reelle — le malais de Malaisie —
    # n'est dans aucun dossier de texto/, et rien ne la signalerait a
    # l'oeil : les deux standards s'ecrivent du meme alphabet et se
    # lisent l'un l'autre sans peine. On ne peut donc pas comparer, on
    # doit RELEVER.
    #
    # PREMIER FRONT, LE LEXIQUE. Les deux standards se separent sur une
    # liste courte et tres connue de mots quotidiens. On ne prend que
    # ceux dont la forme malaisienne n'existe pas du tout en
    # indonesien standard.
    #
    # SECOND FRONT, UNE DATE. L'orthographe d'avant la reforme de 1972
    # employait « dj », « tj », « oe », « sj » la ou l'on ecrit
    # aujourd'hui j, c, u, sy — et c'est exactement l'orthographe qu'un
    # imprimeur aurait employee en 1926, l'annee du fac-simile. C'est
    # le seul piege du releve ou la faute serait CONTEMPORAINE de la
    # source.
    #
    # LA MESURE AVANT LA REGLE, ET ELLE A DEJA CHANGE LA LISTE. Passe
    # sur le corps des trois premiers tableaux : zero mot malaisien,
    # zero « dj », zero « tj », zero « oe », zero « sj » — mais VINGT
    # ET TROIS « nj », tous dans « menjadi », « menjaga », « menjual »,
    # ou le n ferme un prefixe et le j ouvre la racine. « nj » est donc
    # exclu, comme le danda l'a ete du controle des ecritures melees.
    #
    # TOUS LES MOTIFS SONT INSENSIBLES A LA CASSE, et cela n'est pas
    # un detail : le premier essai n'a pas vu « Djalan » en tete de
    # phrase parce que « Dj » n'est pas « dj ». Les fautes de graphie
    # d'avant 1972 tombent justement sur des noms propres et des
    # debuts de phrase — c'est la ou l'ancienne orthographe survit le
    # plus longtemps.
    #
    # ET CINQ MOTS NE SONT PAS RELEVES, EXPRES, PARCE QU'ILS SONT DES
    # FAUX AMIS : « pejabat » est le bureau la-bas et le fonctionnaire
    # ici ; « budak » l'enfant la-bas et l'esclave ici ; « polis » la
    # police la-bas et la police d'assurance ici — et le tableau 7 met
    # justement en scene un agent d'assurances ; « kedai » et « lori »
    # vivent des deux cotes avec des emplois differents. Un controle
    # qui crie sur un mot juste finit desarme.
    "id": {"mot": [
        (r"(?i)(?<![A-Za-z])cikgu(?![A-Za-z])", "guru"),
        (r"(?i)(?<![A-Za-z])tandas(?![A-Za-z])", "toilet"),
        (r"(?i)(?<![A-Za-z])stesen(?![A-Za-z])", "stasiun"),
        (r"(?i)(?<![A-Za-z])ubat(?![A-Za-z])", "obat"),
        (r"(?i)(?<![A-Za-z])wang(?![A-Za-z])", "uang"),
        (r"(?i)(?<![A-Za-z])beg(?![A-Za-z])", "tas"),
        (r"(?i)(?<![A-Za-z])kerusi(?![A-Za-z])", "kursi"),
        (r"(?i)(?<![A-Za-z])almari(?![A-Za-z])", "lemari"),
        (r"(?i)(?<![A-Za-z])tingkap(?![A-Za-z])", "jendela"),
        (r"(?i)(?<![A-Za-z])bomba(?![A-Za-z])", "pemadam kebakaran"),
        (r"(?i)(?<![A-Za-z])tarikh(?![A-Za-z])", "tanggal"),
        (r"(?i)(?<![A-Za-z])tayar(?![A-Za-z])", "ban"),
        (r"(?i)(?<![A-Za-z])basikal(?![A-Za-z])", "sepeda"),
        (r"(?i)(?<![A-Za-z])hospital(?![A-Za-z])", "rumah sakit"),
        (r"(?i)[A-Za-z]*dj[A-Za-z]*", "graphie d'avant 1972 — « dj » se "
                                  "note « j » depuis la reforme"),
        (r"(?i)[A-Za-z]*tj[A-Za-z]*", "graphie d'avant 1972 — « tj » se "
                                  "note « c » depuis la reforme"),
        (r"(?i)[A-Za-z]*oe[A-Za-z]*", "graphie d'avant 1972 — « oe » se "
                                  "note « u » depuis la reforme"),
        (r"(?i)[A-Za-z]*sj[A-Za-z]*", "graphie d'avant 1972 — « sj » se "
                                  "note « sy » depuis la reforme"),
    ]},

    # LE JAVANAIS EST LE CAS INVERSE DE L'INDONESIEN, ET C'EST LA
    # MEME PAIRE DE LANGUES. Quand on defendait « id », la voisine
    # n'etait dans aucun dossier et il fallait relever sans pouvoir
    # comparer. Maintenant elle y est, ecrite par la meme main, la
    # ligne au-dessus — et c'est justement ce qui rend la derive
    # facile : l'indonesien est la langue d'ecole de tout locuteur du
    # javanais, celle dans laquelle il ecrit tout le reste de sa
    # journee. On releve donc les mots-outils indonesiens, qui sont
    # ceux qui glissent en premier, et jamais les mots de chose, que
    # les deux langues partagent par centaines.
    #
    # ET UN SECOND FRONT QU'AUCUNE AUTRE COLONNE N'A EU : LES NIVEAUX
    # DE LANGUE. Le javanais a deux lexiques paralleles — ngoko et
    # krama — et il faut en tenir un. La colonne tient le NGOKO ALUS :
    # narration en ngoko, et verbes krama inggil pour ce que fait le
    # grand-pere. C'est ce qu'un enfant javanais ecrit et ce qu'un
    # livre javanais de 2026 imprime.
    #
    # ON RELEVE DONC LE KRAMA ORDINAIRE — kula, mboten, menika,
    # ingkang, sampun, kaliyan, griya, toya —, qui signale une main
    # passee au niveau poli d'un bout a l'autre. ET ON NE RELEVE PAS
    # LES VERBES KRAMA INGGIL — dhahar, tindak, kondur, ngendika,
    # priksa, sare —, qui sont exactement ce que la regle de la
    # colonne EXIGE pour le grand-pere. Un controle qui crie sur la
    # forme que la consigne demande est pire qu'un controle absent :
    # c'est la lecon de « دی » et « دے », prise avant d'ecrire.
    #
    # FAUX AMIS ECARTES EXPRES : « bisa », « anak », « sekolah »,
    # « meja », « kursi », « jendela », « lawang » vivent dans les
    # deux langues avec le meme sens — les deux les tiennent souvent
    # du meme portugais ou du meme neerlandais. Les relever ferait
    # crier le controle sur chaque page.
    "jv": {"mot": [
        (r"(?i)(?<![A-Za-z])tidak(?![A-Za-z])", "ora"),
        (r"(?i)(?<![A-Za-z])dan(?![A-Za-z])", "lan"),
        (r"(?i)(?<![A-Za-z])dengan(?![A-Za-z])", "karo"),
        (r"(?i)(?<![A-Za-z])yang(?![A-Za-z])", "sing"),
        (r"(?i)(?<![A-Za-z])ini(?![A-Za-z])", "iki"),
        (r"(?i)(?<![A-Za-z])itu(?![A-Za-z])", "iku"),
        (r"(?i)(?<![A-Za-z])sudah(?![A-Za-z])", "wis"),
        (r"(?i)(?<![A-Za-z])juga(?![A-Za-z])", "uga"),
        (r"(?i)(?<![A-Za-z])tetapi(?![A-Za-z])", "nanging"),
        (r"(?i)(?<![A-Za-z])sangat(?![A-Za-z])", "banget"),
        (r"(?i)(?<![A-Za-z])besar(?![A-Za-z])", "gedhe"),
        (r"(?i)(?<![A-Za-z])kecil(?![A-Za-z])", "cilik"),
        (r"(?i)(?<![A-Za-z])orang(?![A-Za-z])", "wong"),
        # « rumah sakit » N'EST PAS RELEVE, ET C'EST UN NOM
        # D'INSTITUTION, PAS UN MOT. Le javanais dit omah pour la
        # maison, et « rumah » y est bien un indonesianisme — sauf
        # dans l'hopital, que Java appelle rumah sakit et pas
        # autrement. La seule autre forme possible est « griya
        # sakit », qui est du KRAMA : elle serait relevee par la
        # regle de niveau. Un mot emprunte peut donc etre la seule
        # forme juste, et le controle doit le savoir.
        (r"(?i)(?<![A-Za-z])rumah(?!\s+sakit)(?![A-Za-z])", "omah"),
        # « banyak » A ETE RELEVE ICI, PUIS OTE AU TABLEAU 3. Le mot
        # indonesien veut dire « beaucoup » et le javanais dit akeh —
        # la regle semblait bonne. Mais « banyak » est AUSSI un mot
        # javanais, et c'est l'OIE : elle parait au tableau 3, ou les
        # enfants du village font fuir les oies (25). Les deux mots
        # s'ecrivent pareil et ne sont pas le meme mot. Le controle
        # criait donc sur une forme juste, et il a fallu le desarmer
        # — comme pour « دی » et « دے » a la colonne ourdoue, et pour
        # les cinq faux amis ecartes d'avance a la colonne
        # indonesienne. Ici la lecon a servi CONTRE une regle qu'on
        # venait d'ecrire soi-meme.
        (r"(?i)(?<![A-Za-z])semua(?![A-Za-z])", "kabeh"),
        (r"(?i)(?<![A-Za-z])atau(?![A-Za-z])", "utawa"),
        (r"(?i)(?<![A-Za-z])hanya(?![A-Za-z])", "mung"),
        (r"(?i)(?<![A-Za-z])karena(?![A-Za-z])", "amarga"),
        (r"(?i)(?<![A-Za-z])kemudian(?![A-Za-z])", "banjur"),
        (r"(?i)(?<![A-Za-z])se(?:buah|orang|ekor)(?![A-Za-z])",
         "le javanais ne compte pas avec le classificateur indonesien"),
        # ET LE PIEGE DE LA DATE VAUT ICI AUSSI : la reforme de 1972
        # a refait l'orthographe latine de l'indonesien ET celle du
        # javanais d'un seul coup. « djaran », « tjilik », « boekoe »
        # sont donc exactement ce qu'un imprimeur aurait compose en
        # 1926, et c'est la seconde colonne ou la faute serait
        # CONTEMPORAINE de la source. On ne releve pas « sj », qui
        # n'a jamais servi au javanais ; on ne touche pas non plus a
        # « dh » et « th », qui sont des lettres retroflexes de la
        # langue et non des restes de graphie.
        (r"(?i)[A-Za-z]*dj[A-Za-z]*", "graphie d'avant 1972 — « dj » se "
                                  "note « j » depuis la reforme"),
        (r"(?i)[A-Za-z]*tj[A-Za-z]*", "graphie d'avant 1972 — « tj » se "
                                  "note « c » depuis la reforme"),
        (r"(?i)[A-Za-z]*oe[A-Za-z]*", "graphie d'avant 1972 — « oe » se "
                                  "note « u » depuis la reforme"),
    ],
     # LES REGLES DE NIVEAU NE VALENT QUE HORS DIALOGUE, et il a fallu
     # le tableau 5 pour le comprendre. Elles etaient d'abord dans
     # « mot », avec les autres, et c'etait juste tant que le livret
     # racontait. Le tableau 5 est un dialogue entier : Ioannes y parle
     # a son oncle, et un enfant javanais parle KRAMA a son oncle —
     # « kula » y est la forme juste, et l'alinea dit meme que l'enfant
     # est poli. La regle a donc ete deplacee, non otee : hors dialogue
     # elle vaut toujours, et le krama y signale bien que le niveau
     # entier a glisse.
     "narracio": [
        (r"(?i)(?<![A-Za-z])kula(?![A-Za-z])",
         "aku — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])mboten(?![A-Za-z])",
         "ora — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])menika(?![A-Za-z])",
         "iki — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])ingkang(?![A-Za-z])",
         "sing — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])sampun(?![A-Za-z])",
         "wis — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])kaliyan(?![A-Za-z])",
         "karo — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])griya(?![A-Za-z])",
         "omah — la narration tient le ngoko, non le krama"),
        (r"(?i)(?<![A-Za-z])toya(?![A-Za-z])",
         "banyu — la narration tient le ngoko, non le krama"),
    ]},

    # LE PERSAN A DEUX VOISINES DANS LE RELEVE ET ELLES SONT TOUTES LES
    # DEUX DANS SON ALPHABET. L'ourdou lui a pris sa graphie et la
    # moitie de son lexique savant ; l'arabe lui a donne l'alphabet et
    # l'autre moitie. C'est la premiere colonne dont la defense se joue
    # au CARACTERE plus qu'au mot — et c'est justement la que l'oeil ne
    # voit rien : ی et ي, ک et ك, ۱ et ١ se dessinent presque pareil, et
    # la ligne reste bien formee, le LaTeX compile, html.py publie.
    #
    # LES LETTRES QUE LE PERSAN N'A PAS. Six sont ourdoues — les
    # retroflexes ٹ ڈ ڑ, le noun ghunna ں, le bari yeh ے et le do-chashmi
    # heh ھ — et quatre sont arabes : le yeh ي, le kaf ك, la ta marbuta ة
    # et l'alef maqsura ى. Le persan ecrit ی, ک, ه et ی a leur place. Ce
    # ne sont pas des variantes de style : ce sont d'autres points de
    # code, et un texte persan n'en contient aucun.
    #
    # ET LES CHIFFRES SE SEPARENT DE MEME. Le persan compose ۰۱۲۳۴۵۶۷۸۹
    # (U+06F0..U+06F9), l'arabe ٠١٢٣٤٥٦٧٨٩ (U+0660..U+0669). Le releve
    # arabe ecrit « اللوحة رقم ١ », l'ourdou « جدول نمبر 1 » en chiffres
    # latins : trois colonnes du meme alphabet et trois series de
    # chiffres.
    #
    # ON NE RELEVE PAS أ NI إ, qui paraissent dans quelques emprunts
    # arabes que le persan imprime encore ainsi, ni ؤ ni ئ, qui sont
    # persans (مسئله, مؤسسه), ni ۀ (U+06C0), qui est la forme persane du
    # he suivi de hamza. Un controle qui crie sur une forme juste finit
    # desarme.
    #
    # ET UN SECOND FRONT, QUI EST UNE DATE COMME EN INDONESIEN : LE
    # DEMI-ESPACE. L'orthographe persane de 2026 exige un U+200C apres
    # le prefixe negatif-duratif « نمی » — نمی‌رود et non نمیرود. On ne
    # releve QUE « نمی », et non « می » seul, parce que می ouvre aussi
    # میز, میوه, میان, میدان, میلیون, ou il n'y a rien a couper :
    # « نمی » en tete de mot est toujours le prefixe, et jamais autre
    # chose.
    "fa": {"mot": [
        (r"[\u0679\u0688\u0691]", "lettre retroflexe ourdoue — le persan "
                                    "ne les a pas"),
        (r"\u06BA", "ں ourdou — le persan ecrit ن"),
        (r"\u06D2", "ے ourdou — le persan ecrit ی"),
        (r"\u06BE", "ھ ourdou — le persan ecrit ه"),
        (r"\u064A", "ي arabe (U+064A) — le persan ecrit ی (U+06CC)"),
        (r"\u0643", "ك arabe (U+0643) — le persan ecrit ک (U+06A9)"),
        (r"\u0629", "ة arabe — le persan ecrit ه"),
        (r"\u0649", "ى arabe — le persan ecrit ی"),
        (r"[\u0660-\u0669]", "chiffre arabe — le persan compose "
                              "۰۱۲۳۴۵۶۷۸۹ (U+06F0..U+06F9)"),
        (r"نمی(?!\u200c)", "demi-espace manquant — l'orthographe de 2026 "
                           "ecrit نمی\u200cرود"),
    ]},

    # LE HAOUSSA REPREND LE FRONT DU PERSAN — le CARACTERE et non le
    # mot — MAIS EN LETTRES LATINES, ET C'EST PIRE. Le persan se
    # defendait de deux langues voisines logees dans son alphabet ;
    # celle-ci se defend de sa PROPRE SAISIE. ɓ, ɗ, ƙ et ƴ sont quatre
    # lettres pleines de l'alphabet boko, non des b, d, k, y ornes :
    # « kofa » n'est pas « ƙofa », et la difference est celle d'un mot
    # a rien du tout. Or aucun clavier ordinaire ne les donne, tout
    # correcteur les rend a leur forme nue, et une ligne ainsi
    # depouillee reste bien formee : le LaTeX compile, html.py publie.
    #
    # ON NE RELEVE QUE LES MOTS DONT LA FORME NUE N'EXISTE PAS. kofa,
    # karfe, karshe, kauye, daya, daki, dauka, yan ne sont rien en
    # haoussa ; leur trouver un sens demande de supposer une faute. On
    # NE RELEVE PAS « kasa », qui est un mot — « en bas », « echouer »
    # — la ou « ƙasa » est le pays et le sol : la regle aurait raison
    # sur la lettre et tort sur le mot, et c'est exactement le cas du
    # « rumah sakit » javanais, paye une fois.
    #
    # ET UN SECOND FRONT, QUI EST UN ALPHABET FERME : le boko n'a ni
    # p, ni q, ni v, ni x. Ce qui vient d'ailleurs se refait a la
    # bouche haoussa — « bitamin », « fensir », « kwafi » — et un p
    # laisse dans un mot est toujours la trace d'une langue qui n'a
    # pas ete traduite. La regle ne vise que les mots a INITIALE
    # MINUSCULE : les noms propres gardent leur orthographe, Paris
    # reste Paris, et la capitale suffit a les mettre hors de portee.
    # Le lookbehind ecarte de meme les noms de macro — la lettre qui
    # suit un « \\ » ou une autre lettre n'ouvre aucun mot — et les
    # unites de \\VUcentre, ou le « pt » suit un chiffre.
    "ha": {"mot": [
        (r"[\u0600-\u06FF]", "lettre arabe — cette colonne s'ecrit en "
                              "boko, non en ajami"),
        (r"(?<![\\A-Za-z0-9])[a-zɓɗƙƴ’]*[pqvx][a-zɓɗƙƴ’]*",
         "lettre absente de l'alphabet boko (p, q, v, x)"),
        (r"(?<![A-Za-z])kofa(?![A-Za-z])", "ƙofa"),
        (r"(?<![A-Za-z])karfe(?![A-Za-z])", "ƙarfe"),
        (r"(?<![A-Za-z])karshe(?![A-Za-z])", "ƙarshe"),
        (r"(?<![A-Za-z])kauye(?![A-Za-z])", "ƙauye"),
        (r"(?<![A-Za-z])k(?:arami|anana)(?![A-Za-z])", "ƙarami / ƙanana"),
        (r"(?<![A-Za-z])daya(?![A-Za-z])", "ɗaya"),
        # « daki-daki » A FAIT CRIER CETTE REGLE AU TABLEAU 2, ET LA
        # REGLE AVAIT TORT. « ɗaki » est la chambre ; « daki-daki »,
        # sans crochet et redouble, est l'adverbe « en detail » — il
        # parait au N.-B. du tableau 2, ou le maitre est invite a
        # decrire chaque jeu daki-daki. Deux mots differents, et le
        # trait d'union les separe : on n'ouvre donc plus la regle sur
        # un mot qui touche un trait d'union, des deux cotes.
        (r"(?<![A-Za-z-])daki(?![A-Za-z-])", "ɗaki"),
        (r"(?<![A-Za-z])dauka(?![A-Za-z])", "ɗauka"),
        # LE HAOUSSA A DEUX ORTHOGRAPHES POUR UNE SEULE LETTRE, ET
        # C'EST UNE FRONTIERE : le Niger ecrit ƴan, le Nigeria ’yan.
        # Les deux sont justes chez eux. La colonne prend ƴ, pour que
        # son alphabet tienne en quatre crochets et non en trois
        # crochets plus une apostrophe — et la regle tient ce choix,
        # puisqu'elle s'ouvre aussi bien apres une apostrophe qu'apres
        # une espace. Ce n'est pas une faute qu'elle releve alors,
        # c'est un melange.
        (r"(?<![A-Za-z])yan(?![A-Za-z])", "ƴan (et non ’yan : la "
                                          "colonne ecrit le crochet)"),
        (r"'", "apostrophe droite — le haoussa de 2026 ecrit ’ (U+2019)"),
    ], "exemptes": [
        # LA NOTE « Balk-o » DU TABLEAU 5 EST LE SEUL ENDROIT DU
        # LIVRET QUI CITE D'AUTRES LANGUES MOT POUR MOT, et l'ido les
        # met lui-meme en italique pour dire qu'elles sont
        # etrangeres : « Balk-o = D. Balken, E. joist, F. solive, I.
        # travicello, R. balka, S. Port. viga ». La regle des lettres
        # absentes du boko a donc crie quatre fois, et elle avait
        # raison a la lettre : solive, poutre et viga ne sont pas du
        # haoussa, et ne doivent surtout pas le devenir. On ne
        # resserre donc rien — une citation n'est pas une faute
        # d'orthographe, c'est un autre texte —, on exempte les trois
        # lignes qui la portent, comme la colonne arabe egyptienne
        # exempte la plaisanterie du vieux cordonnier.
        "\\textit{solive}",
        "\\textit{poutre}",
        "\\textit{viga}",
        # ET LA NOTE « Lambrequino » DU TABLEAU 6 EST DE LA MEME
        # ESPECE, ce qui confirme la lecture faite au tableau 5 : ce
        # ne sont pas les italiques qui portent les citations, ce sont
        # les NOTES. Celle-ci gloses le mot par ses formes francaise,
        # espagnole, portugaise, allemande et anglaise —
        # « lambrequin, lambrequines, lambrequins » —, et l'ido ne les
        # met meme pas en italique. Le haoussa du texte, lui, ecrit
        # « lambarkin », sans q : la regle continue donc de mordre
        # partout ailleurs dans ce fichier.
        "lambrequin",
    ]},
}

# LE SEUIL AU-DELA DUQUEL UN FICHIER EST UN DIALOGUE. Mesure sur les
# seize tableaux ido : 36 attributions de parole au tableau 5, 1 au
# tableau 12 — et c'est « Noto. » —, 0 partout ailleurs. Cinq laisse
# donc les deux cas de part et d'autre sans rien serrer.
PAROLI = 5


# LES ECRITURES QUI NE SE MELENT PAS DANS UN MOT. Deux lettres de
# deux ecritures non latines ne se rencontrent jamais a l'interieur
# d'un meme mot : on n'ecrit pas un mot moitie arabe moitie tamoul.
# Quand cela arrive, c'est une faute de frappe qu'aucun autre controle
# ne peut voir — la ligne reste bien formee, le LaTeX compile, et
# l'oeil qui ne lit pas les deux ecritures passe dessus.
#
# LA MESURE AVANT LA REGLE : passe sur les 42 colonnes de texto/,
# le controle releve ZERO mot, une fois le danda « । » rendu neutre.
# Ce signe vit dans le bloc devanagari mais sert au bengali, au
# gujarati, au telougou et au marathe : sans cette exception le
# controle criait sur presque chaque phrase bengalie. Les liants
# U+200C et U+200D sont neutres pour la meme raison.
ECRITURES = [
    ("arabe", 0x0600, 0x06FF), ("devanagari", 0x0900, 0x097F),
    ("bengali", 0x0980, 0x09FF), ("gourmoukhi", 0x0A00, 0x0A7F),
    ("gujarati", 0x0A80, 0x0AFF), ("tamoul", 0x0B80, 0x0BFF),
    ("telougou", 0x0C00, 0x0C7F), ("kannada", 0x0C80, 0x0CFF),
    ("malayalam", 0x0D00, 0x0D7F), ("grec", 0x0370, 0x03FF),
    ("cyrillique", 0x0400, 0x04FF), ("hebreu", 0x0590, 0x05FF),
    ("han", 0x4E00, 0x9FFF), ("hangul", 0xAC00, 0xD7AF),
]
NEUTRES = {0x0964, 0x0965, 0x200C, 0x200D}


def ecriture(c):
    o = ord(c)
    if o in NEUTRES:
        return None
    for nom, debut, fin in ECRITURES:
        if debut <= o <= fin:
            return nom
    return None


def octet(f, i, l, mauvais):
    """Ce qui ne peut pas etre du texte, en-tetes compris."""
    # LE CARACTERE DE REMPLACEMENT. Un U+FFFD s'est glisse dans le
    # bloc c4-08-1 de texto/ur/15-jadval-06.tex, a la place d'un
    # point ourdou. Aucun des cinq outils ne l'a vu : renvoji.py ne
    # lit que l'ordre des renvois, kolonoj.py ne lisait que les
    # macros et les mots, html.py l'aurait publie tel quel. Un
    # caractere de remplacement n'est jamais voulu : c'est la trace
    # d'un octet perdu au passage d'un encodage a un autre. On releve
    # avec lui les caracteres de controle C0, sauf la tabulation.
    for m in re.finditer(r"[\ufffd\x00-\x08\x0b-\x1f\x7f]", l):
        mauvais.append(f"{f}:{i} caractere impossible "
                       f"U+{ord(m.group(0)):04X} — octet perdu"
                       f" a la conversion")
    for mot in l.split():
        vues = {ecriture(c) for c in mot}
        vues.discard(None)
        if len(vues) > 1:
            mauvais.append(f"{f}:{i} « {mot} » mele "
                           f"{' et '.join(sorted(vues))} dans un seul "
                           f"mot — faute de frappe")


def formo(f, lg, mauvais):
    """Les controles de forme, qui valent pour toutes les colonnes."""
    regle = LINGUI.get(lg, {})
    mots = regle.get("mot", [])
    exemptes = regle.get("exemptes", [])
    lignes = f.read_text(encoding="utf-8").split("\n")
    # UN FICHIER QUI PARLE N'EST PAS UN FICHIER QUI RACONTE. Les
    # regles de « narracio » ne s'appliquent qu'aux tableaux narres :
    # voir PAROLI, plus haut, et l'en-tete de LINGUI.
    dialogo = sum(x.count("\\textsc{") for x in lignes
                  if not x.startswith("%")) >= PAROLI
    if not dialogo:
        mots = mots + regle.get("narracio", [])
    # LE MOT DE BROUILLON LAISSE DANS LE TEXTE. Trois fois dans la
    # seule colonne ourdoue, deux fois dans la tamoule, on a tape un
    # mot francais seul sur sa ligne — « Wait », « Ordre » — en
    # cherchant sa phrase, et on ne l'a pas efface. renvoji.py ne le
    # voit que si le brouillon portait un renvoi ; kolonoj.py ne le
    # voyait pas du tout ; html.py l'aurait publie au milieu d'un
    # alinea ourdou.
    #
    # Une ligne entierement latine, seule, sans macro ni ponctuation,
    # ne peut pas etre du texte dans une colonne qui ne s'ecrit pas
    # en lettres latines. On ne le dit pas d'apres une liste de
    # langues mais d'apres le FICHIER : s'il compte moins d'un
    # dixieme de lettres latines, il n'est pas latin. Passe sur les
    # 42 colonnes, le controle rend ZERO signalement — les noms
    # propres et les citations du fac-simile sont toujours dans une
    # phrase, jamais seuls sur leur ligne.
    #  Les noms de macro sont latins et il y en a partout : on les
    #  ote avant de compter, sans quoi aucun fichier ne serait juge
    #  non latin. Le premier essai de ce controle est tombe dans ce
    #  piege et n'a rien releve du tout.
    corps = "\n".join(x for x in lignes if not x.startswith("%"))
    corps = re.sub(r"\\[A-Za-z]+", "", corps)
    lettres = [c for c in corps if c.isalpha()]
    latines = sum(1 for c in lettres if ord(c) < 0x250)
    nolatina = bool(lettres) and latines < len(lettres) // 10
    for i, l in enumerate(lignes, 1):
        # LES DEUX CONTROLES QUI SUIVENT REGARDENT L'OCTET, PAS LA
        # LANGUE, ET ILS PASSENT DONC AUSSI SUR LES COMMENTAIRES.
        # C'est la seule difference avec tout le reste du fichier, et
        # elle a ete payee deux fois : un U+FFFD dans le corps de
        # texto/ur/15-jadval-06.tex, puis un ک arabe glisse au milieu
        # d'un mot tamoul cite dans l'EN-TETE de
        # texto/ur/17-jadval-08.tex. Un en-tete se lit ; il doit donc
        # se controler.
        octet(f, i, l, mauvais)
        if l.startswith("%"):
            continue
        for m in re.finditer(r"\\([A-Za-z]+)", l):
            if m.group(1) not in CONNUES:
                mauvais.append(f"{f}:{i} macro inconnue : \\{m.group(1)}")
        if "\\VUgras{}" in l:
            mauvais.append(f"{f}:{i} \\VUgras vide")
        if nolatina and re.fullmatch(r"[A-Za-z\u00c0-\u024f'\u2019-]+",
                                     l.rstrip()):
            mauvais.append(f"{f}:{i} « {l.strip()} » seul sur sa "
                           f"ligne dans une colonne non latine — "
                           f"mot de brouillon oublie ?")
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
