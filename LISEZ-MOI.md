# Delmas-Tabeli — transcription LaTeX et page de lecture bilingue

Transcription diplomatique de deux livrets jumeaux :

* **`Expliko-Libreto di la Delmas-Tabeli helpanta`**, J. Guignon,
  Ido-akademiano, Ido-Kontoro, Thaon-les-Vosges (Vosges, France) ;
  imprimerie des Tableaux Auxiliaires Delmas, 6 place Saint-Christoly,
  Bordeaux, **1926**. 116 feuillets numérisés, 112 folios imprimés.
* **`Livret explicatif des Tableaux Auxiliaires Delmas`**, E. Rochelle,
  professeur au lycée de Bordeaux ; G. Delmas, imprimeur-éditeur,
  10 rue Saint-Christoly, Bordeaux. 96 feuillets numérisés, 88 folios
  imprimés plus la table des matières.

Les deux ouvrages sont dans le domaine public. Le livret ido est la
version idiste du livret français : même découpage en **16 tableaux**,
même numérotation d'alinéas, mêmes renvois chiffrés aux objets des
tableaux muraux.

Objectif, comme pour le *Kompleta Gramatiko* : **une ligne du
fac-similé = une ligne du PDF**, même pagination, mêmes folios, mêmes
coupures de mot. Et, en plus ici : **une page de lecture à deux
colonnes**, l'ido à gauche, une autre langue à droite, appariées alinéa
par alinéa.

---

## 1. État d'avancement

| Étape | État |
|---|---|
| Découpage des scans en feuillets | fait (116 + 96 ; les deux PDF sont déjà en pages simples) |
| Relevé de géométrie (`outils/inventaire.py`) | fait sur les 212 feuillets |
| Calibration (`outils/kalibro.py`) | faite ; corps mesuré par la chasse (§ 4) |
| Transcription ido | **les 16 tableaux** (feuillets 7 à 108) ; reste : liminaires et table |
| Transcription française | **les 16 tableaux** (feuillets 9 à 92) ; reste : l'*Avertissement* et la table |
| Page de lecture (`index.html`) | faite, complète pour ce qui est transcrit |
| Traduction anglaise (`texto/en/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction espagnole (`texto/es/`) | **les 16 tableaux**, faite en 2026 d'après l'ido, contrôlée sur le français et l'anglais |
| Traduction russe (`texto/ru/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction chinoise (`texto/zh/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction arabe (`texto/ar/`) | **les 16 tableaux**, faite en 2026 d'après l'ido ; colonne de droite à gauche |
| Traduction québécoise (`texto/fr-CA/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — non calquée sur le fac-similé français (§ 8) |
| Traduction vietnamienne (`texto/vi/`) | **les 16 tableaux**, faite en 2026 d'après l'ido |
| Traduction cantonaise (`texto/yue/`) | **les 16 tableaux**, faite en 2026 d'après l'ido, en caractères traditionnels — écrite en cantonais et non en chinois standard (§ 8) |
| Traduction en arabe égyptien (`texto/arz/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — écrite en égyptien et non en arabe standard ; colonne de droite à gauche (§ 8) |
| Traduction marathe (`texto/mr/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — en devanagari comme le hindi, mais ni la même langue ni la même ponctuation (§ 8) |
| Traduction telougoue (`texto/te/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne dravidienne du relevé, et celle qui a fait la règle modificateur–tête (§ 8, § 9) |
| Traduction coréenne (`texto/ko/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — seule colonne du relevé sans langue voisine, d'où un contrôle qui tient en une classe de caractères (§ 8) |
| Traduction tamoule (`texto/ta/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne dont l'adversaire est un **registre** et non une langue, et celle qui a fait naître `ordo.py` (§ 8, § 9) |
| Traduction ourdoue (`texto/ur/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne à **deux voisines de natures différentes** (l'écriture avec le pendjabi chahmoukhi, la langue avec le hindi), et celle qui a rendu au tableau 11 ses gros plans (§ 8) |
| Traduction indonésienne (`texto/id/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — seule colonne dont la voisine n'est **dans aucun dossier**, d'où un contrôle qui relève au lieu de comparer, et sur une **date** autant que sur un lexique (§ 8) |
| Traduction javanaise (`texto/jv/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne dont la voisine a été écrite par la même main, et **seule du relevé à avoir des niveaux de langue grammaticalisés** (ngoko, krama), d'où un contrôle qui distingue le récit du dialogue (§ 8) |
| Traduction persane (`texto/fa/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne dont la défense se joue au **caractère** et non au mot : deux voisines (ourdou, arabe) logent dans son propre alphabet, où ی/ي et ک/ك ne se distinguent pas à l'œil (§ 8) |
| Traduction haoussa (`texto/ha/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — seule colonne qui s'écrive en **lettres latines** et dont le contrôle vise pourtant le caractère : ɓ, ɗ, ƙ, ƴ sont quatre lettres pleines qu'aucun clavier ne donne, et l'alphabet boko n'a ni p, ni q, ni v, ni x (§ 8) |
| Traduction gujaratie (`texto/gu/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — colonne **à tête finale**, où l'outil qui compte est `parigi.py`, lu *avant* d'écrire : le génitif gujarati pose le possesseur devant le possédé et retourne à lui seul la moitié des couples de renvois (§ 8) |
| Traduction levantine (`texto/apc/`) | **les 16 tableaux**, faite en 2026 d'après l'ido — première colonne dont les **deux voisines sont la même langue qu'elle** (l'arabe standard, l'égyptien) : le danger n'y est pas le mot étranger mais la main qui remonte toute seule vers le registre de l'école (§ 8) |
| Les 16 tableaux muraux | **absents** — voir § 7 |
| Contrôles automatiques | huit contrôles (`outils/controles.py`), plus la forme et la langue des colonnes traduites (`outils/kolonoj.py`) et les paires de renvois à retourner (`outils/parigi.py`) |

Le projet compile en permanence :

    make -f tab.mk           # tabeli.pdf, tableaux.pdf, index.html

Le fichier de compilation s'appelle `tab.mk` et non `Makefile` : le pont
vers le disque refuse d'écrire un fichier portant ce dernier nom.

---

## 2. Les deux fac-similés

**Ils ne sont pas de même nature, et cela commande tout le reste.**

`Expliko-Libreto.pdf` — 116 pages, images JPEG en niveaux de gris,
passage au scanner : le cadrage est constant d'une page à l'autre, la
justification mesure 1456 px sur toutes les pages pleines (écart-type
faible une fois les pages d'apparat écartées). C'est un fac-similé
qu'on peut mesurer.

`Livret explicatif.pdf` — 96 pages, **prise de vue** : chaque feuillet
a été photographié séparément, le livre était gondolé, l'éclairage
inégal. La justification du même bloc imprimé y mesure de **990 à
1550 px** selon la page. Une mesure prise sur une page ne vaut donc
que pour elle. Toute mesure globale sur ce fac-similé doit d'abord
**normaliser chaque page sur sa propre largeur de bloc** ; c'est ce que
devra faire le contrôle 11.

Correspondance, vérifiée par lecture directe des folios :

    folio imprimé = numéro de feuillet − 2      (dans les DEUX livrets)

Feuillets : `skan/io/f-001.jpg` … `f-116.jpg`, `skan/fr/f-001.jpg` …
`f-096.jpg`. Ils ne sont pas versionnés (170 Mo) ; ils se régénèrent
depuis les deux PDF d'origine :

    pdftoppm -jpeg -r 300 Expliko-Libreto.pdf   skan/io/f
    pdfimages -j "Livret explicatif.pdf"        skan/fr/f   # puis renumérotation en base 1

---

## 3. Structure des deux livrets

Chaque tableau se compose ainsi :

    TABELO N° n            /  TABLEAU N° n
      titre du tableau
      Deskripto generala.  /  I. Description générale.
        alinéas 1 … 8
      Detaloza deskripto.  /  II. Description détaillée.
        alinéas 9 … 19

**L'édition ido ajoute des intertitres que le français ne connaît
pas** : au tableau 1, `La ludo-korto`, `La bona lernanti`, `La mala
lernanti`, `Desegno e muziko`, `La doceyo pri la cienci`. Guignon
découpe en sections un texte que Rochelle laisse courir. Elle ajoute
aussi une note de bas de page sur la latinisation des prénoms, absente
du français.

Ces écarts sont **réels** et la page de lecture les montre : la case
d'en face reste vide plutôt que de recevoir un texte déplacé pour faire
joli. C'est le seul rendu honnête d'une édition qui n'est pas une
traduction ligne à ligne.

Table des 16 tableaux (d'après la table des matières française) :

| n° | français | folio fr |
|---|---|---|
| 1 | L'École. — Le Lycée. — La Classe | 7 |
| 2 | Le Corps humain. — La Récréation. — Les Jeux | 12 |
| 3 | L'Enfance (Un Baptême au village) ; La Jeunesse (Une Fête publique) | 17 ; 20 |
| 4 | L'Âge mûr (Le Repas de noce) ; La Vieillesse (L'Anniversaire) | 23 ; 26 |
| 5 | La Maison et sa construction | 29 |
| 6 | La Maison intérieure. — Les Meubles | 35 |
| 7 | Le Village (en hiver) ; La Maison rustique (au printemps) | 43 ; 46 |
| 8 | La Moisson (en été) ; La Vendange (en automne) | 49 ; 51 |
| 9 | La Montagne. — La Ville d'eaux ; La Forêt. — La Chasse | 54 ; 57 |
| 10 | La Mer. — Le Port | 60 |
| 11 | La Ville et ses monuments. — Un incendie | 65 |
| 12 | La Gare. — Les Chemins de fer | 69 |
| 13 | L'Hôtel. — Le Restaurant. — Le Café | 73 |
| 14 | La Rue. — Les Commerçants | 76 |
| 15 | Le Marché. — Les Comestibles | 82 |
| 16 | Un Grand Magasin. — Les Jouets | 86 |

---

## 4. Calibration — trois instruments, dont un seul tient

`outils/inventaire.py` relève, feuillet par feuillet : boîte d'encre,
lignes de base, pas des lignes. `outils/kalibro.py` en tire les
constantes du préambule.

### L'échelle : une notice de bibliothèque

Les deux fac-similés sont des prises de vue ; rien dans l'image ne dit
combien de pixels font un millimètre. La notice HathiTrust du *Livret
explicatif* (20ᵉ éd., G. Delmas, 1916) porte **« 90 p., 2 l. 18 cm. »** :
la hauteur du papier est donc **180 mm**, mesure de bibliothèque et non
hypothèse. `kalibro.py` prend l'échelle sur la hauteur, ce que donnent
toutes les notices, et non sur la largeur, qu'aucune ne donne.

Le livret ido n'a pas de notice trouvée. On lui applique la même
hauteur : même presse — « Imprimerie des Tableaux Auxiliaires Delmas,
6 place Saint-Christoly » — et les deux éditions se vendaient ensemble.
C'est une inférence, pas une mesure. Elle donne un papier de
**104,6 × 180 mm** pour l'ido, **109,1 × 180 mm** pour le français : le
second tombe pile sur un in-16 courant, ce qui est rassurant.

### Le corps : le rapport 1,20 était faux

Le corps était d'abord déduit du pas des lignes par le rapport d'usage
`corps = pas / 1,20`. Résultat à la compilation : **294 lignes trop
courtes sur 100 pages** pour l'ido, **1179 sur 84** pour le français —
une ligne sur trois n'atteignait pas la marge, et TeX écartait les mots
pour combler. Un rapport n'est pas une mesure.

Deuxième instrument, `outils/altox.py` : la **hauteur d'x**, mesurée du
plateau de densité de chaque ligne. Elle réclamait 12,8 pt pour l'ido —
sous un interlignage de 11,68 pt, c'est-à-dire un interlignage négatif.
Impossible. Mesurer ma propre composition avec le même code n'annule
pas le biais : le fac-similé est de l'encre sur du papier, elle s'étale,
le grain et le JPEG épaississent, et le plateau est lu deux à trois
pixels trop haut de chaque côté — les 18 % d'écart constatés.
**L'outil est conservé, et son verdict aussi : il dit ce qu'il mesure et
pourquoi on ne le suit pas.**

Troisième instrument, celui qu'on retient : `outils/chaso.py`. Il
n'existe que parce que le relevé est diplomatique. **On possède le texte
exact de chaque ligne du fac-similé.** Le bon corps est donc celui pour
lequel ces lignes-là, dans la justification mesurée, remplissent leur
mesure comme elles la remplissent sur le papier. On balaie, on compile,
on compte :

| corps | ido : courtes / longues | | corps | français : courtes / longues |
|---|---|---|---|---|
| 9,73 | 294 / 0 | | 8,90 | 1179 / 0 |
| 10,33 | 48 / 0 | | 9,80 | 261 / 0 |
| **10,93** | **21 / 0** | | **10,70** | **41 / 1** |
| 11,23 | 20 / 1 | | 10,85 | 23 / 11 |
| 11,53 | 18 / 24 | | 11,30 | 13 / 113 |

Le minimum est net des deux côtés : 21 lignes lâches sur ~3 700 pour
l'ido (0,6 %), 42 sur ~3 400 pour le français (1,2 %), et aucune ligne
qui déborde côté ido. Ce n'est pas un réglage à l'œil : c'est une mesure
prise sur plusieurs milliers de lignes dont le fac-similé est l'étalon.

Les corps retenus, **10,93 pt sur 11,68 pt** (ido) et **10,70 pt sur
10,68 pt** (français), donnent un interlignage presque nul — composition
« au fer », normale pour un livret bon marché de cette époque, et très
loin du 1,20 qu'on avait supposé.

### Ce qui reste faux, et pourquoi on le sait

Le **contrôle 6** signale que la boîte d'encre du fac-similé français
couvre **96,5 % de la hauteur de l'image**, contre 83,7 % pour l'ido.
Un livre imprimé a des marges : ce chiffre ne dit pas que le français
n'en a pas, il dit que **le cadre de la prise de vue tombe à l'intérieur
du papier**. La hauteur d'image ne vaut donc pas la hauteur du papier,
et l'échelle qu'on en tire est fausse de quelques pour cent.

Ce que cela abîme, et ce que cela n'abîme pas :

* les **rapports internes** — pas sur justification, hauteur d'x sur
  justification, corps trouvé par la chasse — sont pris dans l'image et
  ne dépendent d'aucune échelle : ils sont justes ;
* seule **l'échelle d'ensemble** du volume français est incertaine. La
  page composée est juste de forme et approximative de taille.

> **À FAIRE, et cela prend trente secondes :** poser une règle sur les
> deux exemplaires, mesurer la hauteur du papier, puis
>
>     python3 outils/kalibro.py io <mm>
>     python3 outils/kalibro.py fr <mm>
>     python3 outils/chaso.py io && python3 outils/chaso.py fr

## 5. Le relevé LaTeX

Fichiers dans `texto/io/` et `texto/fr/`. Deux marques portent tout :

    \nl     fin de ligne SANS trait d'union
    \cc     fin de ligne AVEC trait d'union (le trait est composé)

On n'utilise jamais `\\` : il annule la justification de la ligne.
Aucune césure n'est décidée par TeX ; toutes sont relevées sur le scan.

**Une traduction n'est pas un relevé.** `texto/en/` contient les mêmes
clés `%%K`, le même apparat macro pour macro et les mêmes renvois
`\textsuperscript{(n)}` — ce sont eux qui ouvrent les gros plans, et un
numéro déplacé ouvrirait sur autre chose. Mais elle ne porte ni `\nl`
ni `\cc`, qui n'ont de sens que pour un fac-similé, ni
`\begin{VUpage}`, puisqu'elle n'a ni feuillet ni folio. Elle traduit
l'**ido**, que porte la colonne de gauche, en contrôlant sur le
français ; là où l'ido subdivise et pas le français, elle subdivise
aussi.

**La source est de 1926 ; la traduction est de 2026.** Ce sont deux
dates, et la seconde n'est pas négociable : une colonne doit se lire
comme si un être humain l'avait écrite cette année-ci. Le monde décrit,
lui, reste celui du livret — on ne modernise pas le lycée, le pion ni la
diligence ; on modernise la **langue**, jamais les choses. Trois fautes
en découlent, et il faut les traquer une par une :

1. **La tournure vieillie.** Le « for » explicatif anglais — *his
   satchel is torn, for he is very careless* — que plus personne
   n'écrit ; le « shall » de futur ; le « one » impersonnel ; « Nor do
   I care for… » ; « so kind a daughter-in-law » pour « such a kind
   daughter-in-law ». Elles ne sont pas fausses : elles sont datées, et
   c'est pire, parce qu'elles font croire que la traduction est
   d'époque.

2. **Le calque de la source.** « here is the milkwoman » pour *voici la
   laitière*, « to take advantage of his mother being busy » pour *il
   profite de ce que sa mère est occupée*, « they serve us to digest »
   pour *ils nous servent à digérer*. La phrase est grammaticale et
   n'est d'aucune langue.

3. **La contraction absente.** Dans un dialogue — le tableau 5 en est
   plein — un enfant de 2026 dit *I can't see him*, non *I cannot see
   him*. L'absence totale de contractions dans une colonne entière est
   la marque la plus sûre d'une traduction faite il y a cent ans, ou
   par une machine.

Le contrôle se fait au balayage, langue par langue, sur une liste de
marques établie pour cette langue-là : `grep` de la tournure suspecte,
puis lecture de chaque occurrence — aucune de ces marques n'est fautive
à tous les coups, et « for instance » n'est pas le « for » explicatif.

**Et une variante régionale est une colonne à part.** Là où deux états
d'une même langue diffèrent et sont l'un et l'autre bien connus —
l'anglais britannique et l'américain, le portugais européen et le
brésilien —, on ne choisit pas : on écrit les deux. Le pendjabi l'a
déjà fait, mais pour l'alphabet et non pour le lexique ; c'est la même
décision, prise pour une autre raison.

**Et un calque n'est pas toujours un mot.** Le fac-similé français met une
espace devant les deux-points, le point-virgule, le point d'exclamation et
le point d'interrogation. C'est le français ; ce n'est presque aucune autre
langue. Cette espace était passée, avec le texte, dans dix colonnes —
néerlandais 51, suédois 51, espéranto 51, finnois 51, interlingua 48,
hindi 56, pendjabi 56 et 56, turc 57, irlandais 2 — et dans aucune des
autres. Un balayage de registre se fait donc sur les **signes** autant que
sur les mots : on ne relit pas un blanc, et c'est pour cela qu'il traverse.
Les deux PDF, eux, gardent la leur : **la source ne bouge pas.**

**Et une coquille se corrige à la lecture, jamais au relevé.** Onze
coquilles des deux livrets composent maintenant proprement dans la page,
sans qu'aucun `.tex` bouge. Six étaient déjà décrites en tête des fichiers
de `texto/fr` — `cuisuine`, `LA SALLE A MANGER,`, `7 ---` sans son point,
`classe. .`, `une dinde. une oie. un canard`, `'est très consciencieuse` —
mais décrites seulement : rien ne les corrigeait. Cinq n'avaient jamais
été vues, et chacune se dénonce par une **comparaison interne**, jamais
par un dictionnaire :

| trouvaille | ce qui la dénonce |
| --- | --- |
| `le detail d'un repas` (t7) | les quatre autres `détail` du livret portent l'accent |
| `Meze dil magasino` (t16) | le même tableau écrit `magazino` deux fois avec un z |
| `hiké` (note du t6) | l'ido écrit `hike` trois fois ailleurs, et ne connaît pas l'accent aigu |
| `la tempo , konsultis` (t12) | la seule espace avant une virgule des 40 000 mots des deux livrets |
| deux `«` pour un `»` (t7, alinéa 15) | l'ido du même bloc n'en ouvre qu'un |

**On ne sait pas si ces cinq sont de l'imprimeur ou du releveur** : ce
dépôt ne contient pas les pages du livret, seulement les seize planches.
La correction se pose donc dans `gravuri/korekti.json`, où elle ne touche
pas les deux PDF et se défait d'une ligne le jour où un fac-similé
tranchera. Une sixième ne se corrige pas faute d'endroit où la poser : au
colophon ido, « les Tabl aux Auxi'iaires Delmas » porte deux lettres
cassées, mais le bloc `t99-apar-5` n'est pas rendu dans la page.

**Deux pièges pour qui ajoutera une entrée.** Les intertitres s'apparient
par leur **place**, non par leur clé — le français fait cinq sections là
où l'ido en fait neuf, et la ligne porte la clé de l'ido : « La Salle à
Manger » est le `t06-tit-3` du français et se compose dans `t06-tit-5`.
Et le **nom du gros plan** ne vient pas de l'alinéa mais de
`gravuri/numeri.json` : une règle posée avant la composition des boutons
corrige la ligne et laisse la coquille dans le `title`. Dans les deux cas
rien ne signale une règle qui ne mord pas.

**Un seizième du volume n'avait aucun gros plan, et rien ne le disait.**
Six planches portent plusieurs vignettes qui recommencent chacune à 1, si
bien que `gravuri/numeri.json` y range les numéros par scène — `c1:1`,
`c2:1`. Le tableau 11, lui, n'a qu'une numérotation : la première partie
va de 1 à 43, « L'Incendie » continue de 44 à 96, et seule la
**numérotation des alinéas** repart de 1 — d'où des clés `t11-c1` et
`t11-c2` sur une planche à numéros nus. `html.py` cherchait donc
« c2:46 », ne trouvait rien, et ne posait aucun bouton : quatre-vingt-neuf
gros plans manquants, dans les 42 colonnes à la fois, sans un mot dans
aucun contrôle — la fonction qui ouvre un bouton rend `None` en silence,
par construction, puisqu'**on ne promet pas un gros plan qu'on ne saurait
pas montrer**. Le défaut n'est apparu qu'en comptant les boutons table par
table pendant l'écriture de la colonne ourdoue : `t11` était le seul zéro
d'une colonne de seize nombres. La réparation est un repli sur le numéro
nu, et elle est sûre parce que le relevé le montre : aucune planche ne
mêle les deux formes, ses numéros sont **tous** préfixés ou **tous** nus.
Une colonne complète passe ainsi de 1 644 boutons à 1 733. (Le premier report annonçait 1 642 → 1 731 : le total avait été additionné à la main sur la liste des seize tableaux au lieu d'être relu dans le fichier. Deux de plus, et c'est le fichier qui a raison.)

**Une mesure seule ne dit rien ; il faut les trente.** Le balayage de
registre de 2026 a été mené colonne par colonne, mais chaque chiffre a été
lu contre les vingt-neuf autres — c'est la comparaison qui désigne la
faute, pas la valeur. Le turc disait « pek » 117 fois et « çok » 52 : rien
d'anormal en soi, jusqu'à ce que les vingt-neuf autres colonnes montrent
partout le mot neutre en tête. Le néerlandais disait « zeer » 109 fois
contre 4 « heel » ; le japonais portait 116 mots d'avant-guerre ; le
russe, cherché de la même manière, en rendait quatre. **Un balayage qui ne
trouve rien est un résultat**, et il se note comme les autres.

Ce que les trente colonnes ont donné :

| corrigé | ce qui a été trouvé |
| --- | --- |
| en | 26 « for » explicatifs, 6 « here is », zéro contraction, une classe de dessin prise pour un salon |
| sv | 34 « ty », 61 « skall », 51 espaces françaises |
| es, pt, ca, gl | le présentatif calqué : 22 « he aquí », 22 « eis », 21 « heus aquí », 33 « velaquí » — aux mêmes blocs |
| ca, cs | la conjonction livresque : 10 « car », 31 « neboť » |
| nl | 32 « ziehier », 51 espaces, 109 « zeer », un hiver qui régnait |
| ja | 116 mots d'avant-guerre (硝子, 珈琲, 停車場…), 12 tournures |
| tr | 460 copules -dir, 106 « pek » pour « çok », 67 termes gras qui portaient la copule |
| ru | 2 « ибо », 2 « весьма » |
| zh | 3 « 这里是 » redondants |
| lb | un hiver qui régnait |
| eo, fi, hi, ia, pa, pnb, ga | l'espace française devant les signes doubles, et rien d'autre |

| gardé | pourquoi |
| --- | --- |
| ro « iată », oc « vaicí », lt « štai », eo « jen », ia « ecce », lb « do ass », rm « qua è » | le présentatif de ces langues **se dit encore** |
| fi « sillä », lt « nes », et « sest », lb « well », uk « бо », ro 5 « căci » | la conjonction causale y est courante, pas livresque |
| ja である (276 fois), ja 汽船, ja 蓄音機 | registre expositif normal ; objets qui portent encore ce nom |
| es « reina el invierno », pt, ca, gl | la tournure se dit dans ces langues, et pas en néerlandais |
| ga, ar, bn, hi, pa, pnb, eu, de, it | rien à corriger : ces colonnes étaient déjà écrites au registre d'aujourd'hui |

**Et l'on ne corrige pas une colonne parce qu'une autre l'a été.** Le même
bloc de l'ido — « nam regnas la vintro » — se garde en espagnol et s'ôte
en néerlandais, parce que ce n'est pas le bloc qu'on juge, c'est la langue
d'arrivée.

Les espaces-mots sont rendus insécables : le seul point de coupure légal
d'une ligne est celui que le relevé a placé, et une ligne trop large
devient un « Overfull \hbox » que les contrôles inventorient — la faute
passe du silence au bruit.

Chaque page est composée dans une `minipage` de hauteur fixe : une
retouche dans un alinéa ne peut pas faire migrer du texte vers la page
suivante.

**Les clés `%%K`.** Chaque bloc du relevé porte une ligne

    %%K t01-09-3 p

soit `t<tableau>-<numéro d'alinéa>-<rang dans l'alinéa>` puis le type
(`p` alinéa, `sub` intertitre, `apar` page d'apparat, `noto` note). Un
alinéa coupé par un changement de page porte deux fois la même clé, la
seconde suivie de `suite`.

C'est par ces clés que la page de lecture apparie les deux colonnes.
Elles reprennent **la numérotation d'alinéas de l'auteur**, la seule
chose que les deux éditions partagent : elles n'ont ni la même
pagination, ni le même nombre de lignes, ni le même découpage en
sections.

---

## 6. La page de lecture

`outils/html.py` construit `index.html` à partir des mêmes sources
LaTeX. **Le texte n'est saisi qu'une fois** : le PDF et la page en
sortent tous deux, et il est donc impossible que les deux états du
texte divergent.

### Ce qu'elle porte, et ce qu'elle ne porte pas

**Les seize tableaux, et rien d'autre.** Couverture, dédicace,
PREFACO, AVERTISSEMENT, tables des matières, annonces de l'éditeur :
tout cela est dans les deux PDF, qui reproduisent les volumes entiers,
et reste hors de la page de lecture. Ces pièces ne se répondent pas
d'une édition à l'autre — la préface de Guignon n'est pas
l'avertissement de Rochelle, elle en est même le contraire par le ton —
et les afficher côte à côte donnait deux colonnes qui se regardaient
sans rien avoir à se dire. Le partage se lit sur le nom du fichier :
`00-` les liminaires, `90-` la fin, entre les deux les tableaux.

### Du relevé diplomatique à l'écran

* `\nl` devient une espace ; `\cc` **ne laisse rien** — le mot se
  recolle. C'est la seule manière de rendre le texte cherchable :
  `docochambro` coupé en `doco-chambro` ne se trouverait pas.
* Un mot coupé au milieu d'un passage gras porte deux `\VUgras` ; les
  balises **jointives** se recollent, celles que sépare une espace non.
* **Sauf quand la ligne se casse sur le trait d'union d'un composé.**
  « choux- » puis « fleurs » redonnait `chouxfleurs`, et le gros plan
  s'intitulait ainsi : 49 composés étaient dans ce cas, 15 en français et
  34 en ido. Aucune règle ne sépare les deux cas — le fac-similé compose
  le même trait des deux côtés, et le relevé n'a pas de quoi les
  distinguer. **C'est la colonne qui tranche** : soit elle écrit ailleurs
  le composé non coupé (`cerf-volant`, `dorso-salto`), soit elle écrit
  d'autres composés sur la même moitié, tous avec le trait
  (`aquo-krucho`, `aquo-tubaro` commandent `aquo-falo`). Quand elle ne dit
  ni l'un ni l'autre, **on ne tranche pas** : `vitberi` et `teretajo`
  s'écrivent des deux façons dans le fac-similé et restent collés. La
  table est dans `gravuri/korekti.json`, section `trati`.
* Deux appels de renvoi séparés par la coupure — `(9, 11,` et `12)` —
  sont un seul renvoi et se réunissent.
* Le `%` de fin de ligne LaTeX est retiré. Sans cela le texte des notes
  commençait par un pourcent, et leur marqueur d'appel n'était plus
  reconnu.

### Les notes se replient

Au bas d'une page imprimée la note a sa place ; dans une colonne qui
défile, posée entre deux alinéas, elle coupe la lecture. L'appel
devient donc un bouton et la note s'ouvre sous l'alinéa qui la porte,
comme dans la page du *Kompleta Gramatiko*.

L'appariement se fait **par la page et par le marqueur**, les deux : un
`(1)` de note et un `(1)` de renvoi au tableau mural s'écrivent pareil,
seule la page les distingue. Trois cas ont demandé un traitement
propre : deux notes sur une même page portant toutes deux `(*)` se
départagent par l'ordre ; un appel peut se trouver sur la page
précédente, quand l'alinéa est à cheval ; et la note du tableau 8 est
appelée depuis le titre d'une scène, pas depuis un alinéa.

### La synchronisation des deux colonnes

Les clés `%%K` apparient les rangs. Là où une édition coupe en deux ce
que l'autre laisse d'un tenant, le PDF garde chaque édition telle
quelle — il est diplomatique — et la page de lecture recolle les deux
moitiés dans leur colonne, en marquant d'un filet l'endroit où l'autre
édition allait à la ligne. Les rangs restent ainsi parallèles.

Cela ne suffisait pas. Le **tableau 5** est un dialogue sans numéros
d'alinéa imprimés : les deux relevés ont dû compter eux-mêmes, ils
n'ont pas compté pareil, et la page mettait en regard une réplique et
la réponse à la précédente. Vingt-quatre rangs sur les trente et un
mal appariés du volume venaient de là. Les clés françaises du tableau 5
ont été renumérotées sur la numérotation ido, prise comme référence ;
six autres cas isolés (tableaux 1, 2, 6, 7, 9, 11) ont été repris au
fac-similé. Il reste **un** rang mal apparié sur 524 — une *Nota*
pédagogique propre au français.

### Disposition

**Deux panneaux, pas trois.** Le *Kompleta Gramatiko* a un volet droit
pour les mots-clés ; ce livre n'en a pas, et la place qui reste sert
aux deux colonnes de texte. À gauche la table des matières, au centre
les deux colonnes, rien à droite, **et pas de pied de page**.

La table des matières a **trois rangs**, parce que le livre en a trois :
le tableau, la scène, l'intertitre. Les tableaux à plusieurs parties
portent « Unesma ceno » et « Duesma ceno », composés en italique et non
en petites capitales — c'est ce qui les distingue, et c'est au
fac-similé qu'on le lit.

Sous 900 px de largeur, les colonnes s'empilent — l'ido d'abord, la
traduction dessous avec un filet à gauche — et la table devient un
tiroir.

**Le titre se centre sur la colonne, non sur ce qui reste de la
colonne.** La case ido porte 17 px de marge et 1 px de filet **à
droite**, pour poser la ligne de partage ; sa boîte de contenu est donc
de 18 px plus étroite que la case française, et `text-align:center`
centrait dans cette boîte-là. Les deux titres d'un même rang tombaient
à 9 px l'un de l'autre — toujours 9, à toute largeur, **et que le folio
paraisse ou non** : le folio est en `position:absolute` hors de la
colonne et n'y était pour rien. On rend à la case ido, pour les seuls
rangs centrés, un blanc égal à gauche. Sous 900 px la case perd sa
marge et son filet, et le blanc de compensation se retire avec eux.
Mesuré au navigateur sur les 40 rangs centrés, à 1400, 1100, 950 et
800 px : −9 px avant, 0 après.

Le sélecteur de langue ne recharge rien **une fois la langue venue** :
elle reste dans la page, et la bascule est instantanée. Le français y
est d'emblée — c'est un fac-similé transcrit, il fait partie de
l'objet ; les traductions, marquées `differita` dans `LANGUES`, vivent
dans `lingui/<kodo>.json` et ne se téléchargent qu'au moment où le
menu les nomme. La page ne porte que leurs cases vides. Mesuré : zéro
requête vers `lingui/` tant qu'on n'a pas choisi English, une seule
ensuite, jamais reprise.

La recherche traverse toutes les langues présentes, et elle porte sur
**les colonnes à la fois** : un mot ido trouve l'alinéa, et sa
traduction reste en face même si elle ne contient pas le mot. Ce qui
arrive en cours de route entre dans la copie non surlignée dont la
recherche repart, puis la relance — sans quoi un mot déjà tapé ne
serait pas surligné dans la langue qui vient d'arriver.

L'infobulle d'un renvoi porte le nom de l'objet **dans la langue de sa
colonne** : « fumeyo » à gauche, « fumoir » au milieu, « smoking
room » à droite. `outils/objekti.py` les relève des trois sources du
même geste — le substantif en gras devant le renvoi — et 1610 objets
sur 1693 sont nommés dans les trois.

Le folio de chaque bloc se pose dans le blanc extérieur de sa colonne
et renvoie à la page correspondante du PDF. Ce n'est pas une
soustraction fixe : le volume ido saute deux feuillets vierges, et les
pages composées sont donc numérotées dans l'ordre, une fois pour
toutes.

## 7. Les 16 tableaux muraux — ce qui manque

Tout le texte des deux livrets renvoie par des chiffres — `(18)`,
`(32)`, `(a)`, `(ab)` — aux objets **numérotés sur les tableaux muraux
Delmas**, seize planches en couleurs de 90 × 120 cm. Sans elles, les
renvois du texte ne mènent nulle part.

Ce qu'on a : **une seule réduction**, en trait, au feuillet 111 du
livret ido — le tableau mural n° 12, « Les Voyages ». Les quinze autres
sont à retrouver.

Une fois les planches en main, le travail est balisé :

1. relever, sur chaque planche, la position de chaque numéro ;
2. en faire une carte cliquable (`<area>` ou SVG en surimpression) ;
3. relier chaque `<sup>(18)</sup>` du texte à sa zone, dans les deux
   sens : cliquer le renvoi éclaire l'objet, survoler l'objet donne le
   mot en ido, en français et dans la langue affichée.

C'est là que « des versions améliorées des tableaux originaux » prend
son sens : un tableau mural dont chaque objet porte son nom dans six
langues, ce que l'imprimé de 1926 ne pouvait pas faire.

---

## 8. Arborescence

    LISEZ-MOI.md
    tab.mk                    compilation
    main-io.tex               -> tabeli.pdf
    main-fr.tex               -> tableaux.pdf
    preambule.tex             macros, communes aux deux volumes
    kalibro-io.tex            mesures du fac-similé ido      (PRODUIT)
    kalibro-fr.tex            mesures du fac-similé français (PRODUIT)
    index.html                page de lecture                (PRODUIT)
    texto/io/10-tabelo-01.tex … 25-tabelo-16.tex
    texto/fr/10-tableau-01.tex … 25-tableau-16.tex
    texto/fr-CA/10-tableau-01.tex … 25-tableau-16.tex   (traduction)
    texto/vi/10-bang-01.tex … 25-bang-16.tex           (traduction)
    texto/yue/10-toubiu-01.tex … 25-toubiu-16.tex     (traduction)
    texto/arz/10-lawha-01.tex … 25-lawha-16.tex       (traduction)
    texto/mr/10-takta-01.tex … 25-takta-16.tex        (traduction)
    texto/te/10-pattika-01.tex … 25-pattika-16.tex  (traduction)
    texto/ko/10-dopyo-01.tex … 25-dopyo-16.tex      (traduction)
    texto/ta/10-attavanai-01.tex … 25-attavanai-16.tex (traduction)
    texto/ur/10-jadval-01.tex … 25-jadval-16.tex      (traduction)
    texto/id/10-bagan-01.tex … 25-bagan-16.tex       (traduction)
    texto/jv/10-gambar-01.tex … 25-gambar-16.tex     (traduction)
    texto/fa/10-tablo-01.tex … 25-tablo-16.tex       (traduction)
    texto/ha/10-hoto-01.tex … 25-hoto-16.tex        (traduction)
    texto/gu/10-kostak-01.tex … 25-kostak-16.tex     (traduction)
    texto/apc/10-lawha-01.tex … 25-lawha-16.tex      (traduction)
    outils/inventaire.py      relevé de géométrie, feuillet par feuillet
    outils/mesures.py         médianes et échelles possibles
    outils/kalibro.py         écrit kalibro-*.tex
    outils/altox.py           hauteur d'x (mesure écartée, § 4)
    outils/chaso.py           corps par la chasse (mesure retenue, § 4)
    outils/ceni.py            indice de scène dans les clés %%K
    outils/controles.py       les six contrôles
    outils/kolonoj.py         la forme et la langue des colonnes traduites
    outils/parigi.py          les paires de renvois à retourner (§ 9)
    outils/ordo.py            l'ordre des renvois, bloc par bloc (§ 9)
    outils/CONSIGNE-RELEVE.md consigne de transcription
    outils/lekto.py           prépare un feuillet pour la lecture à l'œil
    outils/html.py            écrit index.html
    outils/gabarito.html      gabarit de la page de lecture
    outils/inv-io.json        relevé brut (PRODUIT)
    outils/inv-fr.json        relevé brut (PRODUIT)
    skan/io/, skan/fr/        feuillets (non versionnés)

---

### La note se pose au pied, et le texte lui cède la place

`\VUnotes` posait sa note **absolument**, dans une boîte de hauteur nulle
calée sur le pied du bloc : elle tombait juste, et elle ne poussait rien.
Sur une page dont le texte descend jusqu'au pied, les deux s'imprimaient
l'un **sur** l'autre — sept pages du livret ido, une du français. La note
se **diffère** maintenant jusqu'à la fermeture de la page et entre dans le
flux après le dernier alinéa : le chevauchement est impossible par
construction. Les quatorze blocs `noto` du relevé ne bougent pas.

Trois pièges, dans l'ordre où ils se sont payés : le ressort du bas de la
minipage, qu'il faut battre d'un ordre (`fill` et non `fil`), sans quoi la
note se pose au milieu du blanc ; **`\vtop` et non `\vbox`**, dont le point
de référence est la *dernière* ligne de base, si bien qu'ajouté après le
texte il remonte de toute sa hauteur et se repose par-dessus ; et
`\VUnotoBas`, qui partait de `\VUfolioY` — la ligne de base du folio, non
le sommet du bloc — et posait donc la note 4 mm trop haut.

**Et la correction a mis au jour ce qu'elle cachait.** Six feuillets
portent, au relevé, plus de matière que la feuille n'en tient : le texte y
remplit déjà le bloc, et la note n'a plus que la marge du bas, qui ne
suffit pas de 1,7 à 2,7 mm — `tabeli` f9 et f35, `tableaux` f45, f75, f76
et f91. Tant que la note s'imprimait *dans* le texte, elle ne sortait
jamais du papier. Trancher ces six pages demande le fac-similé du livret,
que ce dépôt ne contient pas : `outils/notoj.py` les **nomme** à chaque
construction, et `make -f tab.mk controles` l'appelle.

### Les variantes régionales

**Deux éditions d'une même langue ne diffèrent, dans ce livret, que par
quelques dizaines de mots.** En faire deux colonnes de seize fichiers
reviendrait à recopier trente mille mots pour en changer soixante — et à
devoir corriger deux fois chaque coquille trouvée plus tard. La colonne
de base ne bouge donc pas, et `texto/varianti.json` dit ce que l'autre
édition écrit à la place. **Aucune des deux n'est privilégiée au menu** :
« English (UK) » est `texto/en` telle quelle, « English (US) » est la
même passée par la table.

| paire | règles | ce que le chiffre dit |
| --- | --- | --- |
| en-GB / en-US | 63 | la colonne portait 26 marques britanniques et zéro américaine |
| es-ES / es-419 | 29 | dont 12 pour le seul verbe `coger` |
| de-DE / de-AT | 29 | les en-têtes des tableaux 5, 12 et 15 l'annonçaient depuis la traduction |
| pt-PT / pt-BR | 46 | et l'en-tête portugais annonçait le Brésil : il se trompait sur sa propre colonne |
| nl-NL / nl-BE | 8 | sur 34 oppositions courantes, 8 se présentent : les deux normes disent presque la même chose dans ce registre concret |
| zh-Hans / zh-Hant | 1154 | ce n'est pas un lexique, c'est une écriture |

**Trois choses que ces tables ont apprises.** D'abord qu'une règle doit
parfois être **liée à un bloc** : `biscuits` se dit *crackers* à côté du
fromage et *cookies* à côté du pain d'épice, `carriage` est une voiture à
chevaux au tableau 3 et un wagon au tableau 12. Ensuite que **l'ordre
compte** — `luggage van` avant `luggage` — et qu'un **échange** doit
tourner dans le bon sens : `Sessel` devient *Fauteuil* **puis** `Stuhl`
devient *Sessel*, sinon les deux chaises finissent en fauteuils. Enfin
qu'une conversion d'**écriture** ne se fait pas par remplacements
successifs : quarante-cinq suites chinoises ne changent pas et ne sont là
que pour **protéger** — 里 vaut 裏 dans 屋里 et reste 里 dans 莫里斯 — ce
qu'un remplacement successif ne sait pas exprimer. D'où le mode
`unpase`, qui compile les règles en une expression unique, la plus longue
d'abord.

**Ce que les variantes ont coûté à l'ordre du menu, et comment on l'a
repris.** Le menu se trie sur `texto/lingui.json` : le français d'abord
parce qu'il n'est pas une traduction, puis les deux langues construites,
puis toutes les autres **par nombre de locuteurs premiers**. Or
`poser_varianti()` remplace le code de la colonne par celui de
l'affichage — `en` devient `en-GB` et `en-US` — et le registre, lui, ne
connaît que `en`. La recherche du chiffre échouait donc, les deux
éditions passaient pour des langues sans locuteurs, et la règle « une
langue sans chiffre passe en queue » les y envoyait. **Six langues y
sont tombées d'un coup**, dont les quatre plus parlées du livret :

| langue | locuteurs | rang attendu | rang obtenu |
| --- | --- | --- | --- |
| chinois | 988 M | 1<sup>er</sup> | après le romanche |
| espagnol | 487 M | 2<sup>e</sup> | après le romanche |
| anglais | 372 M | 3<sup>e</sup> | après le romanche |
| portugais | 252 M | 5<sup>e</sup> | après le romanche |
| allemand | 76 M | 16<sup>e</sup> | après le romanche |
| néerlandais | 25 M | 20<sup>e</sup> | après le romanche |

Le chiffre se cherche maintenant sous le code de la **colonne** — celui
des fichiers et du registre — puis, à défaut, sous la sous-étiquette de
langue avant le tiret. Cette dernière règle donne aussi sa place au
québécois, qui est une colonne régionale sans être une variante et qui
n'a rien à faire au registre d'Ethnologue : `fr-CA` compte avec le
français.

**Et un garde, parce que le tri ne peut pas se contrôler lui-même.** Le
rejouer donnerait le même résultat faux ; on contrôle donc **sa
matière** : toute colonne doit se retrouver dans le registre. Quatre
n'ont pas de chiffre et c'est voulu — le français, l'espéranto,
l'interlingua, et l'arabe standard qui n'a presque pas de locuteurs
premiers. Toute autre est signalée à la construction. Vérifié en retirant
l'arabe de la liste des dispenses : le signalement sort.

**Et la septième paire ne s'est pas faite ici.** Les six colonnes de base
sont des *traductions* de 2026 ; la colonne française est la
**transcription d'un fac-similé de 1926**, et la source ne bouge pas. Un
calque « fr-CA » posé sur elle donnerait un livret de 1926 écrit avec les
mots du Québec d'aujourd'hui : un objet qui n'a jamais existé, et qui
mentirait sur les deux. C'est donc une colonne à part entière, traduite
de l'ido comme les trente autres — voir ci-dessous.

### La trente et unième colonne : le français du Canada

**Deux colonnes françaises, et ce qui les sépare se compte.** `texto/fr`
transcrit le fac-similé de 1926 ; `texto/fr-CA` traduit **l'ido**, en
français standard du Québec de 2026, dans ses seize fichiers
`*-tableau-*.tex`. Elles se ressemblent forcément — c'est la même langue
qui traduit le même titre, et l'apparat du volume y est mot pour mot le
même. La différence tient en **117 choix lexicaux** et une convention
typographique.

| tableau | choix | tableau | choix | tableau | choix | tableau | choix |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9 | 5 | 8 | 9 | 4 | 13 | 9 |
| 2 | 7 | 6 | **14** | 10 | **3** | 14 | 9 |
| 3 | 6 | 7 | 6 | 11 | 8 | 15 | 9 |
| 4 | 8 | 8 | 6 | 12 | 6 | 16 | 5 |

**Les deux extrêmes disent la même chose.** Le tableau 6 — l'intérieur de
la maison — en compte quatorze : c'est dans la maison que le vocabulaire
des deux rives a le plus divergé. Le tableau 10 — la mer et le port — n'en
compte que trois, et il faut le dire plutôt que de meubler la liste : le
vocabulaire de la marine est un vocabulaire de **métier**, fixé par la
même école et les mêmes manuels des deux côtés de l'Atlantique. Entre les
deux, le tableau 11, celui des métiers de la ville, en compte huit —
parce que les noms de fonction sont ce qui vieillit le plus vite.

**Neuf faux amis, et c'est le vrai travail.** Ce ne sont pas des mots que
le Québec ignore : ce sont des mots qu'il connaît et qui y désignent
**autre chose**. Aucun ne se voit à la lecture, et chacun aurait fait dire
au texte le contraire de ce que la gravure montre.

| le fac-similé écrit | au Québec, ce mot nomme | on écrit donc |
| --- | --- | --- |
| cartable (57) | un classeur à anneaux | sac d'école |
| veste (10) | le vêtement sans manches | veston |
| pupitre (18) | le bureau de l'élève | tables |
| liqueur (48, 7, 36) | une boisson gazeuse | alcool, spiritueux |
| jaquette (11) | une chemise de nuit | veston |
| **bluet (1)** | **un petit fruit** | **centaurée** |
| balayeuse (12) | un aspirateur | voiture de balayage |
| borne-fontaine (78) | une bouche d'incendie | fontaine de pierre |
| torchon | le chiffon à plancher | linge à vaisselle |

Le plus sérieux est le sixième, parce qu'il est le plus discret : « Bluets,
coquelicots et digitales » sont les fleurs des champs du tableau 8, et le
lecteur d'ici aurait lu des petits fruits mêlés à des coquelicots au
milieu d'un champ de blé.

**Vingt-trois mots du fac-similé restent, et c'est un résultat.**
Souliers, plumier, poêle, corset, redingote, chevaux de bois, chandelle,
réveille-matin, évier, chaudron, essuie-mains, billot, corridor, perron,
remise, buanderie, barbier, glissoire, traîneau, bonhomme de neige,
marrons, bas, table d'hôte. La France leur préférerait volontiers
chaussures, gomme, couloir, réveil, torchon ; **le Québec dit les
premiers, en 2026 comme en 1926**. On ne remplace pas un mot pour la
seule raison qu'il est ancien.

**Trois mots que le fac-similé coupe en deux, et qu'on recolle.** L'ido
écrit un seul mot là où le livret français en emploie deux, et c'est
chaque fois le même enseignement : la source est plus cohérente que sa
traduction de 1926.

| ido | le fac-similé | on écrit |
| --- | --- | --- |
| `robineto` (48, 52) | robinet / cannelle | robinet, deux fois |
| `trotuaro` (53, 65) | quai / trottoirs | quai, deux fois |
| `grumo` (19, 54) | chasseur / groom | groom, deux fois |

**Les trois repas changent de nom, et c'est le décalage le plus
régulier.** Le Québec dit *déjeuner* le matin, *dîner* le midi, *souper*
le soir ; la France de 1926 disait *déjeuner* le midi et *dîner* le soir.
Le repas de noces du tableau 4, qui se prend « le soir » sous la véranda,
est donc un souper. Le tableau 13 en donne la meilleure preuve, parce que
**l'ido y distingue lui-même les deux** là où le français les appelle tous
deux « déjeuner » : `dejuneto` est le petit repas monté à la chambre —
c'est le déjeuner ; `dejuno` est le repas de la table d'hôte, celui du
menu, des tripes et du gigot — c'est le dîner.

**La convention typographique** : pas d'espace devant « ; », « ! » et
« ? », espace devant « : ». C'est l'usage courant du Québec, où l'espace
fine insécable recommandée devant les trois premiers est, faute d'être
disponible, ordinairement omise plutôt que remplacée par une espace
pleine. Le fac-similé, lui, la pose pleine (« langues vivantes ? ») :
c'est, en une marque, la différence qui se voit le plus vite entre les
deux colonnes françaises.

**Et la règle qui gouverne tout le reste : on modernise la langue, jamais
les choses.** Le lycée reste un lycée, l'encrier un encrier, la soutane
une soutane, le mât de cocagne un mât de cocagne. La préfecture, le
préfet, les gendarmes et l'école communale sont des institutions
*françaises* que le Québec n'a jamais eues : les traduire en institutions
d'ici aurait déplacé la ville entière.

### La colonne cantonaise : une langue, pas une prononciation

Le cantonais est la seule colonne dont il fallait justifier l'existence
avant de l'écrire. Le chinois est déjà là (`texto/zh/`), et si la colonne
`yue` s'était contentée de transcrire les mêmes phrases en caractères
traditionnels, elle aurait fait double emploi — exactement le motif pour
lequel **le wu a été écarté** (`texto/lingui.json`, champ `ecartita`).

Elle existe parce que le cantonais écrit n'est pas du chinois standard lu
à voix haute. Il a sa grammaire, et Hong Kong l'imprime tous les jours.
Les quatorze marqueurs qui la portent sont posés en tête du tableau 1 :

| cantonais | mandarin | sens |
| --- | --- | --- |
| 係 | 是 | être |
| 喺 | 在 | à, dans |
| 嘅 | 的 | de, attributif |
| 唔 | 不 | ne pas |
| 咗 | 了 | accompli |
| 佢 | 他 | il, elle |
| 哋 | 们 | pluriel (我哋, 佢哋) |
| 冇 | 沒有 | ne pas avoir |
| 睇 | 看 | regarder |
| 攞 | 拿 | prendre |
| 畀 | 給 | donner |
| 好 | 很 | très |
| 呢 / 嗰 | 這 / 那 | ce-ci / ce-là |
| 啲 | 些 | les, du |

**Quatre choses que le cantonais fait et que le nord ne fait pas.**

*Il postpose le genre et l'âge des bêtes, comme l'ido.* L'ido dit
`mutonulo`, `mutonino`, `mutonyuno` ; le mandarin doit antéposer 公鸡,
母鸡, 小鸡 ; le cantonais écrit 雞公, 雞乸, 雞仔 — même ordre que la
source. Le tableau 7 en aligne vingt, et le caractère 乸, qui fait toutes
les femelles, ne s'écrit pas au nord.

*Il transcrit là où le nord traduit.* 芝士 le fromage (7), 車厘子 la
cerise (8), 士多啤梨 la fraise (9), 忌廉 la crème, 批 la tourte, 撻 la
tarte, 貼士 le pourboire, 啤牌 les cartes (13), 車卡 la voiture de train
(12). Le cas extrême est 飛 (12), le billet : une syllabe pour *fare*,
un caractère qui veut dire « voler » et ne sert plus qu'à porter le son.
Et 𨋢 (13), l'ascenseur, n'est même pas un mot habillé : c'est un
caractère **forgé** pour *lift*, absent du répertoire de base d'Unicode.

*Il a des mots que le nord n'a pas du tout.* 走鬼 (15) — « courir au
fantôme » — est ce que crie le colporteur sans patente quand la police
arrive, et par extension le colporteur lui-même : c'est mot pour mot la
scène du bloc 16 du tableau 15. 師奶 est la ménagère qui fait son marché.
夾萬 (16), « qui serre dix mille », est le coffre-fort. 公仔 (16) est
tout ce qui est figuré, et fait souche : 公仔麵, 公仔書, 公仔箱.

*Et il réordonne.* Le meilleur argument de la colonne ne doit rien à
l'anglais : le trottoir (11) est 行人路 au sud et 人行道 au nord. Les
**mêmes trois caractères** — homme, marcher, voie — dans un autre ordre.

**Le suffixe de métier 佬**, relevé pour la première fois au bâtiment du
tableau 6 (泥水佬, 油漆佬, 玻璃佬), court ensuite d'un bout à l'autre du
livret : 打鐵佬, 補鞋佬, 飛髮佬 (7), 收割佬, 箍桶佬 (8), 伐木佬,
燒炭佬 (9), 白鐵佬, 影相佬, 掃街佬 (14). Le vietnamien faisait la même
chose avec `thợ`.

**L'obstacle unique, et la manière de le lever.** Le chinois place le
déterminant devant le déterminé ; l'ido l'inverse ; et le renvoi suit son
mot. Chaque « X de Y » sort donc les renvois à l'envers. Trente-cinq
divergences ont été relevées d'un coup aux tableaux 3 à 6, aucune à
l'œil, toutes par `outils/renvoji.py`. Le remède, repris de la colonne
chinoise, n'a plus changé : **nommer d'abord ce que l'ido nomme
d'abord**, puis qualifier par une seconde proposition — un tiret, 即係,
連, ou 嗰個係…嘅. Écrite ainsi dès le premier jet, la fin de la colonne
sort juste. Le tableau 15 n'a demandé aucune reprise : il énumère, et une
énumération n'a pas de possesseur à placer.

**Un contrôle nouveau, né d'une faute que rien ne voyait.** Le tableau 11
portait `\textuperscript{(74)}` — un s manquant. `renvoji.py` relève
*aussi* les renvois composés « (74) » à plein corps, parce que le relevé
ido en compose ainsi au tableau 5 : la parenthèse nue rattrapait donc la
macro cassée, et le contrôle des renvois sortait à zéro divergence sur un
fichier qui n'aurait pas composé. Le relevé des **macros** la prend, et a
pris du même coup quatre `\nl` restés dans trois autres colonnes (tchèque,
irlandais, galicien) — une traduction n'a pas de fins de ligne du
fac-similé à reproduire.

### La colonne égyptienne : une grammaire, pas un accent

La colonne `arz` a dû se justifier avant d'être écrite, exactement comme
la cantonaise : l'arabe standard est déjà là (`texto/ar/`), et une
colonne qui se serait contentée de le transcrire au Caire aurait fait
double emploi à la prononciation près — le motif exact pour lequel **le
wu a été écarté**.

Elle existe parce que l'égyptien écrit a une grammaire que l'arabe
standard n'a pas. Les quatorze marqueurs qui la portent sont posés en
tête du tableau 1 :

| égyptien | standard | sens |
| --- | --- | --- |
| ده / دي / دول | هذا / هذه / هؤلاء | ce, cette, ces |
| مش | ليس | ne… pas (nom, adjectif) |
| ما…ش | لا / لم | ne… pas (verbe) : مايعرفش |
| بـ + inaccompli | يكتب | le présent : بيكتب |
| حـ / هـ | سوف / سـ | le futur : هيكتب |
| بتاع / بتاعة / بتوع | l'annexion seule | la possession |
| اللي | الذي / التي / الذين | invariable |
| أوي | جدًا | très |
| كمان | أيضًا | aussi |
| بس | لكن / فقط | mais, seulement |
| لسه | ما زال | encore |
| زي | مثل | comme |
| علشان | لأن / لكي | parce que, pour que |
| كام | كم / بضعة | combien, quelques |

**Et une phonologie qui s'écrit.** Le ث passe à ت, le ذ à د, le ظ à ض.
Ce ne sont pas des fautes d'orthographe : c'est ainsi que l'égyptien
s'imprime, en romans, au théâtre et en sous-titres.

| égyptien | standard | |
| --- | --- | --- |
| تلاتة, تمن, تالت, كتير | ثلاثة, ثمانية, ثالث, كثير | ث → ت |
| تلج, توم, تعبان, تعلب | ثلج, ثوم, ثعبان, ثعلب | |
| دقن, دراع, ده, ديل, ديب | ذقن, ذراع, ذاك, ذيل, ذئب | ذ → د |
| ضهر, عضم, ضلمة | ظهر, عظم, ظلمة | ظ → ض |

**La règle atteint jusqu'à l'apparat**, et c'est la première fois qu'une
prononciation oblige à toucher au marquage des rôles : « المشهد التاني »
n'était pas reconnu par le motif `CENO` de `outils/html.py`, qui
n'attendait que « الثاني ». Deux membres ajoutés à `CENO` et à `SERIO`.

**Le corps humain fait la démonstration en un seul tableau.** Vingt-deux
mots du tableau 2, et pas un emprunt : وش le visage, مناخير le nez, ودان
les oreilles, راس, دقن, شنب, سوالف, شفايف, سنان, رقبة, زور, قفا, ضهر,
كتاف, مصارين, دراع, إيد, صوابع, ضوافر, كوع, بطة الرجل, عضم. Ce sont ceux
que tout le monde emploie ; l'arabe standard en emploie d'autres.

**Trois procédés de formation des noms de métier**, relevés au fil des
tableaux — onze en tout :

| suffixe | origine | exemples |
| --- | --- | --- |
| **-جي** | turc | صفرجي (t4), عربجي et كهربجي (t5), جزمجي (t7), بوسطجي (t11), تحويلجي (t12), تلغرافجي (t13), صندوقجي et كوميسيونجي (t14), مكوجيّة (t15) |
| **-اتي** | | مصوّراتي, ساعاتي, نضّاراتي (t14), مسنّاتي (t15) |
| **-ّان / -ّاي** | arabe | البنّا, النقّاش, القزّاز, السمكري, الجنايني, الحطّاب, الفحّام, الفرّان, البقّال |

Le premier se pose sur l'objet qu'on manie, le deuxième sur ce qu'on
fabrique ou répare. C'est l'exact pendant du suffixe **佬** de la colonne
cantonaise, et le tableau 5 — les métiers du bâtiment — est le même des
deux côtés.

**Deux couches d'emprunt se lisent tableau par tableau.** Le turc a
laissé l'armée, l'atelier et l'administration ; l'italien et le français
la maison, le vêtement et la table.

| turc | | italien / français | |
| --- | --- | --- | --- |
| أوضة | la chambre | كوميدينو | la table de nuit |
| قشلاق | la caserne | سكرتير | le secrétaire |
| كوريك | la pelle | كنبة, برواز, نجفة | canapé, cadre, lustre |
| بوية | la peinture | فاترينة, تنده | devanture, marquise |
| أجزخانة | la pharmacie | كاسّة, بوستة | caisse, poste |
| أورطة, يوزباشي, بكباشي, صاغ, شاويش, باشجاويش | les grades | بانيو, دُش, أسانسير | baignoire, douche, ascenseur |
| أبلة | la maîtresse d'école | روشتّة, بلكونة, أباجورة | ordonnance, balcon, abat-jour |

**Les institutions tombent juste, une à une.** Ce n'est pas une
correspondance approchée : la مديرية *est* la circonscription d'un
chef-lieu, le مدير son préfet, le مأمور le chef de police d'un district,
وكيل النيابة celui qui ouvre l'enquête, le ناظر le proviseur puis le chef
de gare, le فرّاش le concierge qui porte le registre, la فسحة la
récréation, l'إشبين et l'إشبينة le parrain et la marraine, le ملبّس les
dragées du baptême, le مولد la fête foraine entière, la عمدة le maire du
village. Le tableau 11 les aligne, et le dernier bloc se lit sans une
glose.

**Cinq noms formés par ressemblance**, qui ont cessé d'être des images :
عين الجمل le noyer (« l'œil du chameau »), أبو فروة le marron, عيش
الغراب le champignon (« le pain du corbeau »), سمك موسى la sole, بلح
البحر les moules. Et le pain lui-même est **عيش**, qui veut dire « la
vie » ; le ciel de lit est **ناموسية**, de ناموس le moustique — la
planche française y voit un ornement, l'égyptien ce à quoi ça sert.

**Le seul trou de la colonne, et il est instructif.** Le fléau du tableau
8 n'a pas de nom égyptien, parce que l'Égypte bat au **نورج**, le
traîneau à rouleaux. Le nommer نورج aurait changé la *chose*, ce que la
règle interdit — « on modernise la langue, jamais les choses » — et il a
donc fallu le **décrire**, `عصي الدراس`, plutôt que le nommer. Sept
tableaux où l'égyptien avait le mot d'avance ; celui-là ne l'a pas, et il
fallait le dire aussi.

**L'annexion arabe suit l'ido pas à pas**, et c'est le résultat le plus
net de la colonne : **aucune inversion de renvoi n'est due à la langue**
sur 683 blocs. L'arabe place le possédé avant le possesseur —
`منشار الحطّاب`, la scie du bûcheron — exactement comme l'ido. Les
quinze reprises qu'il a fallu étaient des maladresses de rédaction, pas
des contraintes de syntaxe. Le chinois, qui range dans l'autre sens,
avait coûté **trente-cinq** inversions aux seuls tableaux 3 à 6.

**Le contrôle de cette colonne relève aussi la langue.** Celui du
cantonais vérifiait la forme ; celui-ci y ajoute la liste des mots que
l'égyptien *ne dit pas* — هذا, ليس, الذي, سوف, ماذا, جدًا, ثلاثة, سيارة,
غرفة, نافذة, حقيبة, جدار, ملابس — parce que la raison d'être de la
colonne est justement de ne pas les écrire. Il a signalé deux fois un mot
savant qu'il fallait **garder** : `صانع أحذية` au tableau 7, où le vieux
cordonnier oppose lui-même les deux registres, et `طاولة` au tableau 13,
qui en égyptien n'est pas une table mais le trictrac. Les deux sont
exemptés par leur forme exacte, jamais par le mot : un contrôle qu'on
désarme en bloc ne contrôle plus rien.

---

### La colonne marathe : le même alphabet, l'autre langue

Le marathi s'écrit en devanagari, comme le hindi de la colonne voisine.
C'est tout ce que les deux ont en commun. Le marathi conjugue *आहे* là
où le hindi dit *है*, il marque l'objet par *ला* et non par *को*, il dit
*आणि* et non *और*, *खूप* et non *बहुत*, *मुलगा* et non *लड़का*, *पाणी*
et non *पानी*, *दार* et non *दरवाज़ा* — et il **termine ses phrases par
un point**, quand le hindi pose un danda. Deux colonnes en devanagari
sur la même page, deux ponctuations.

**Ce qui distingue cette colonne, c'est ce qu'elle n'a pas eu à
emprunter.** Le livret porte trois notes d'auteur où l'ido cherche un
mot qu'il n'a pas ; le marathi l'avait dans les trois cas.

| La note | Ce que l'ido cherche | Ce que le marathi dit |
|---|---|---|
| tableau 5 | « *Balk-o*, racine technique pas encore adoptée », après six langues alignées | **वासा** — la pièce équarrie qui porte le plancher |
| tableau 6 | « *babo* = infanteto, l'anglais *baby*, le français *bébé* » | **बाळ** |
| tableau 6 | « *lambrequino* », donné en cinq langues | **झालर** |

Et la lieue du tableau 9, que l'ido rend par « *quaropa kilometri* »,
des kilomètres quadruples, s'appelle **कोस**.

**Les métiers portent leur nom de caste** : गवंडी le maçon, पाथरवट le
tailleur de pierre, सुतार le charpentier, लोहार le forgeron, धनगर le
berger, चांभार le cordonnier, न्हावी le barbier, सोनार l'orfèvre, सराफ
le changeur, कोळीण la poissonnière, परटीण la blanchisseuse. Et l'amiral
du tableau 10 est **सरखेल** — le titre de Kanhoji Angre, qui tint la
côte de Konkan contre les compagnies européennes au XVIII<sup>e</sup>
siècle. Le livret écrit « admiralo » ; le mot marathe est plus ancien.

**Trois mots servent deux fois, et ce ne sont pas des métaphores** :
नांगर est l'ancre et la charrue, घाट le col de montagne et le quai,
बंब le chaudron et la pompe à incendie.

**Trois trous, et on ne les a pas bouchés.** Le marron chaud du
tableau 7 (le châtaignier ne pousse pas au Maharashtra), le fléau du
tableau 8 (on y bat en faisant piétiner les bœufs — **exactement le
même trou que la colonne égyptienne**, qui bat au نورج, et exactement
la même solution : *les bâtons de battage*), et le charpentier du
tableau 5, que le marathi ne distingue pas du menuisier. On écrit
l'emprunt ou la périphrase, et on le note en tête du fichier : *on
modernise la langue, jamais les choses*.

**La postposition est le seul obstacle, et il est mesurable.** Le
marathi place le possesseur avant le possédé : « X de Y » sort donc à
l'envers, et `renvoji.py` l'a relevé **soixante-neuf fois des tableaux
3 à 16** — le compte est celui des messages de commit, tableau par
tableau ; les deux premiers sont antérieurs au relevé. Le remède est toujours le même — nommer d'abord ce que
l'ido nomme d'abord, puis qualifier par une seconde proposition. Mais
le compte par tableau dit quelque chose de plus :

| Tableau | Inversions | Ce que fait le tableau |
|---|---|---|
| 13 (l'hôtel) | **9** | il accroche des choses les unes aux autres |
| 14 (la rue) | **3** | il énumère des métiers côte à côte |
| 15 (le marché) | **4** | il énumère un étal |

Le 14 est trois fois plus long que le 13 et coûte trois fois moins.
**Ce n'est pas la longueur d'un tableau qui coûte, c'est sa syntaxe** —
et la colonne cantonaise avait fait le même constat au même tableau 15,
dans une langue sans aucun rapport.

**Le contrôle de cette colonne a été corrigé deux fois plutôt que
désarmé.** `kolonoj.py` relevait `दृश्य` comme du hindi : c'est du
marathi ordinaire — une vue — et la règle visait en réalité l'apparat,
elle vise donc maintenant le mot **précédé de son ordinal**. Il relevait
`दरवाजा` : c'est le mot de la **grande** porte d'un fort, celle qu'on
appelle महादरवाजा, et l'exemption a été vérifiée en posant un दरवाजा
ordinaire ailleurs, que le contrôle relève aussitôt. Deux autres formes
sont exemptées par leur forme exacte : `ये रे` et `ये-जा`, bâtis sur le
verbe येणे et écrits avec exactement les mêmes signes que le pronom
hindi ये — le `\b` de Python ne pouvait pas les séparer, et un humain
non plus.

### La colonne telougoue : la première dravidienne, et la règle qu'elle a donnée

Le telougou n'est pas de la famille du hindi ni du marathi. Il ne
partage avec eux ni l'alphabet, ni le lexique de base, ni la
grammaire : *అది* et non *यह*, *వచ్చాడు* et non *आया*, et une
morphologie qui agglutine là où l'indo-aryen décline.

**Et c'est cette colonne qui a donné la règle générale du relevé.** Les
quatre premiers tableaux ont coûté 2, 0, 9 puis 7 inversions relevées
*après coup* par `renvoji.py`. Le tableau 4 en a livré la cause exacte,
et ce n'était pas l'agglutination : c'est l'**ordre modificateur–tête**.
En telougou — comme en tamoul, en coréen, en ourdou, en persan, en
goudjarati, en bhojpouri —, tout ce qui qualifie précède ce qui est
qualifié. Dès qu'un renvoi tombe sur un modificateur et un autre sur sa
tête, les deux sortent à l'envers, mécaniquement. De là `parigi.py`
(§ 9), qui lit l'ido *avant* qu'on écrive et donne la liste des paires
à retourner. Le tableau 5, le plus long du livret, a été écrit avec sa
liste en main : **zéro inversion au premier jet**, et les onze tableaux
suivants aussi.

**Le compte par tableau redit ce que le marathi avait trouvé, dans une
famille de langues sans rapport avec la sienne :**

| Tableau | Retournements | Paires listées | Ce que fait le tableau |
|---|---|---|---|
| 13 (l'hôtel) | **19** | 33 | il accroche des choses les unes aux autres |
| 14 (la rue) | **9** | 16 | il énumère des métiers |
| 15 (le marché) | **7** | 18 | il énumère un étal — 105 renvois, le maximum du livret |
| 16 (le bazar) | **7** | 20 | il énumère une ménagerie en carton |

Le 15 a douze renvois de **plus** que le 13 et coûte douze
retournements de **moins**. Le marathi avait mesuré 9 contre 3 aux
mêmes tableaux. Deux langues, deux familles, deux rédactions
indépendantes : la cause n'est pas dans la langue d'arrivée, elle est
dans la syntaxe du texte de 1926.

*(La colonne « paires listées » n'est pas comparable d'un bout à
l'autre : `parigi.py` a gagné le participe passif au tableau 14, ce qui
a fait passer le livret de 386 à 408 paires — § 9.)*

**Ce que le telougou avait, et ce qu'il n'avait pas.** Deux tableaux
n'ont rien coûté en vocabulaire — le port (10) et la gare (12) : la
côte d'Andhra fait neuf cents kilomètres, le chemin de fer y est entré
en 1893, et la langue a ses mots, *జలాంతర్గామి* le sous-marin comme
*పట్టాలు* les rails. Le marché (15) est l'endroit où elle est le plus
chez elle : riz, lentilles, ail, oignon, banane, ananas, crabe,
crevette, caille, perdrix s'écrivent sans un emprunt. Ce qui manque
manque parce que la **chose** manque, et se lit d'un coup d'œil : le
fléau du tableau 8 — le Maharashtra et l'Égypte l'écrivaient déjà par
périphrase, pour la même raison —, le marron chaud, le hêtre, le
chêne, l'orme, la bruyère, la fougère, l'artichaut, le camembert ; le
renne, la belette et le phoque de la ménagerie du tableau 16, seuls
absents sur vingt animaux nommés.

**Quatre oiseaux et un jeu sont notés comme non résolus** plutôt que
masqués : l'hirondelle, la bergeronnette et l'alouette du tableau 8, la
grive du 15, le jeu de dames du 13. Le telougou a des jeux de plateau
et beaucoup de noms d'oiseaux ; aucun n'est *ceux-là*, et coller un nom
approchant aurait fait croire à un mot.

**Trois fois le même arbitrage sur les noms de métier, et le résultat
n'est pas toujours le même.** Le marathi pouvait garder चांभार pour le
cordonnier : c'est un patronyme ordinaire aujourd'hui. Les équivalents
telougous nomment des castes opprimées et ne servent plus d'étiquettes
de métier ; la colonne écrit donc la fonction — *చెప్పులు కుట్టేవాడు*,
*గొర్రెల కాపరి*, *బట్టలకు రంగు వేసేవాడు* pour le teinturier — et
*క్షురకుడు*, le mot neutre des enseignes, pour le coiffeur. Même
raison, plus simple, pour le boucher du tableau 15 : *కసాయి* traduit
exactement « boucher » et sert aujourd'hui d'injure ; on écrit *మాంసం
అమ్మేవాడు*. La même règle de fidélité donne deux résultats dans deux
langues, et c'est la langue vivante qui tranche, pas la symétrie.

**Les institutions se décrivent, elles ne se transposent pas.** Une
préfecture, une Bourse, une école normale de 1926 n'ont pas
d'équivalent administratif en Andhra ; leur donner le nom de
l'institution indienne la plus proche aurait déplacé la chose. La
colonne écrit *పరిపాలన భవనం*, *వర్తక భవనం*, *ఉపాధ్యాయ శిక్షణ కళాశాల* —
exactement ce qu'avaient écrit le hindi et le marathe avant elle. Trois
langues, trois rédactions séparées, une seule solution.

### La colonne coréenne : la seule sans langue voisine

Toutes les colonnes du relevé qui doivent se défendre contre une autre
langue se défendent contre une **voisine qui partage leur alphabet** : le
cantonais contre le mandarin, l'égyptien contre l'arabe standard, le
marathe contre le hindi, le flamand contre le néerlandais des Pays-Bas.
Le coréen n'a pas de voisin de ce genre. Le hangul n'est partagé par
personne, et rien d'autre ne s'écrit avec.

**Son contrôle tient donc en une classe de caractères, et c'est le
premier du relevé qui ne soit pas une liste de mots.** Le coréen de 2026
n'imprime plus le hanja : un seul idéogramme dans `texto/ko` est une
faute, quel qu'il soit. `outils/kolonoj.py` refuse la plage
`[\u4E00-\u9FFF]` en bloc. Vérifié en plantant 時計 à la place de 시계
au tableau 1 (le contrôle sort la ligne et le caractère), puis en le
retirant : 0 signalement sur les seize fichiers.

**Troisième famille pour la règle modificateur–tête, et `parigi.py` n'a
rien eu à changer.** Après l'indo-aryen (marathe) et le dravidien
(telougou), le coréen est de la troisième famille sans rapport avec les
deux autres — et la règle vaut à l'identique, parce qu'elle ne parle pas
de la langue d'arrivée mais de l'ido de 1926.

*(Une mise au point d'unités, faite dans `texto/ko/23-dopyo-14.tex` :
les 9 contre 3 du marathe et les 19 contre 9 du telougou sont des
inversions **réellement faites** ; les 33 contre 16 du coréen sont des
paires **listées** par `parigi.py`. Ce dernier compte ne mesure pas la
colonne coréenne — il mesure l'ido, puisque `parigi.py` ne lit que l'ido
et sort la même liste pour toutes les colonnes. Le rapport de deux pour
un vaut dans les deux unités ; la colonne coréenne confirme la cause
dans une troisième famille, elle n'ajoute pas un troisième relevé
indépendant.)*

**Le fléau, et ce qu'il fallait quatre langues pour prouver.** Le
marathe, l'égyptien et le telougou ont tous les trois dû périphraser le
fléau du tableau 8 ; trois absences ne prouvaient rien sur la chose,
seulement que trois cultures ne la battaient pas ainsi. Le coréen a le
mot **et** l'outil — 도리깨, deux bâtons reliés par une lanière. C'est
la langue qui **possède** la chose qui règle la question, pas celles qui
en manquent. Même forme pour le marron chaud du tableau 7, le trou le
mieux documenté du relevé : 군밤 est une nourriture de rue de l'hiver
coréen, et cette colonne-là n'y perd rien.

**Le tableau 9 est le miroir exact de son homologue telougou.** Le
telougou empruntait neuf noms d'un coup — hêtre, chêne, orme, peuplier,
sapin, bruyère, fougère, primevère, pie —, parce qu'aucun de ces vivants
ne passe en Andhra. La Corée est à la latitude de la France : la liste
se retourne d'un bloc, quatorze noms propres (너도밤나무, 참나무,
느릅나무, 자작나무, 미루나무, 전나무, 고사리, 앵초, 까치, 노루,
딱따구리, 다람쥐, 민달팽이…), et il n'en manque que quatre — le chamois,
la bruyère, la marmotte, la pervenche. Pyrénées, Alpes, sous-bois
d'Europe occidentale. **La coupure ne suit pas la langue, elle suit la
carte** ; il aura fallu deux colonnes sur la même planche pour le
montrer sans discuter.

**Et la lieue tombe juste, comme l'ఆమడ telougou.** Le coréen mesure les
longues marches en 리, et 십 리 fait quatre kilomètres — la lieue du
livret. Le mot vit encore dans le proverbe *십 리도 못 가서 발병 난다*.

*(J'en avais tiré qu'une journée de marche d'homme ne dépend d'aucune
langue. La colonne tamoule, écrite ensuite, a cassé la règle : son
unité de longue distance est le காதம், qui vaut selon les textes dix à
seize kilomètres et non quatre. Deux coïncidences ne faisaient pas une
loi ; la troisième langue était celle qui pouvait la défaire, et elle
l'a défaite — § 8, la colonne tamoule.)*

**Les institutions se décrivent, quatrième langue et quatrième fois** :
행정 청사, 상업 회관, 사범 학교. À quatre rédactions séparées, la
convergence cesse d'être une coïncidence de famille.

**Les mots devenus des injures, quatre fois dans cette seule colonne** :
난쟁이 (tableau 3), 갖바치 le cordonnier (tableaux 7 et 14), 백정 le
boucher (tableau 15) — deux des métiers 천민 —, et le « cigano » du
tableau 9 écrit 떠돌이 사람. Même arbitrage que pour le కసాయి telougou
et la coupure de caste marathe : on écrit la fonction.

**Ce qu'on n'a pas transposé, alors que c'était tentant** — et c'est
noté dans l'en-tête de chaque fichier concerné :

* 진놀이 pour le jeu de barres (tableau 2) : un jeu coréen de deux camps
  qui se poursuivent, exactement la même forme. L'écrire remplacerait le
  jeu du livret par un autre.
* 툇마루 pour le vérando (tableau 4) : la galerie de la maison coréenne
  est un autre objet ; la colonne écrit l'emprunt 베란다.
* 온돌 et 아궁이 pour le lit et la cheminée (tableau 6) : deux mots
  coréens vivants et faux. La colonne écrit 침대, 벽난로, 욕조. Un seul
  아궁이 est gardé, au bloc c4-01-1, parce que là la chose **est** un
  foyer ouvert où tourne une broche.
* Le menu du tableau 13 reste français — les tripes à la mode de Caen,
  le gigot, le Saint-Émilion sont les choses qu'on mange dans cette
  salle-là.

On modernise la langue, jamais les choses, et cela vaut aussi pour les
choses qu'on aurait plaisir à retrouver.

### La colonne tamoule : quand l'adversaire est un registre

Toutes les colonnes du relevé qui doivent se défendre se défendaient
jusqu'ici contre une **langue voisine** — le cantonais contre le
mandarin, l'égyptien contre l'arabe standard, le marathe contre le
hindi — ou contre une **écriture ancienne**, le coréen contre le hanja.
Le tamoul est le premier cas différent : sa voisine dravidienne, le
télougou, ne partage pas une lettre avec lui, et son écriture n'est
partagée par personne. Ce qui le guette est un **registre**.

**Le tamoul est diglossique pour de bon** : la langue parlée et la
langue écrite diffèrent jusque dans la conjugaison — *இருக்கு* contre
*இருக்கிறது*, *இல்ல* contre *இல்லை*, *பண்ணு* contre *செய்* — et
personne n'imprime la première. `kolonoj.py` relève six marques du
parlé, chacune bornée par une classe tamoule en avant et en arrière,
parce que « இல்ல » est aussi le début de « இல்லை » et de « இல்லாத ».
S'y ajoutent les chiffres tamouls, qui ne servent plus qu'en
épigraphie. Vérifié en plantant « குளிரா இல்ல » et « அட்டவணை எண் ௧ » :
deux signalements, avec la ligne et la forme.

**Et on ne vise pas les lettres grantha**, ஜ ஷ ஸ ஹ, qui servent aux
noms étrangers — la note (*) du tableau 1 impose justement d'écrire
ஸ்டெஃபானுஸ். Le contrôle symétrique de la pureté serait aussi faux que
le contrôle du parlé est juste : les manuels de 2026 impriment
நோட்டுப் புத்தகம், சிலேட்டு, பென்சில். **On modernise la langue,
jamais les choses — et on ne la purifie pas non plus.**

**Cette colonne a fait naître `ordo.py` (§ 9).** Le tableau 9 a coûté
neuf écarts au premier passage, dont sept sur des couples que
`parigi.py` ne contient pas ; le tableau 10, écrit avec la suite des
renvois sous les yeux, en a coûté trois, et le tableau 15 — cent deux
renvois, le maximum du livret — un seul.

**Trois colonnes sur la même planche, et le compte suit la latitude.**
Le tableau 9 est le meilleur relevé de tout le livret sur ce point :

| Colonne | Latitude | Noms empruntés sur la planche 9 |
|---|---|---|
| coréenne | 33–43° N | **4** |
| télougoue | 13–19° N | **9** |
| tamoule | 8–13° N | **17** |

Ce n'est plus une illustration de « le mot est là où la chose est » :
c'est une **mesure**, et elle ne pouvait pas se faire avec moins de
trois colonnes sur la même planche. Le tableau 16 la refait dans
l'autre sens — sur dix-huit bêtes de la ménagerie, le tamoul en nomme
seize et garde même la hyène, que le coréen empruntait.

**Et la même langue ne paie rien trois tableaux plus loin.** Le port
(10), la ville (11) et le chemin de fer (12) coûtent quatre emprunts à
eux trois : la côte de Coromandel fait mille kilomètres, le commerce
maritime tamoul est plus vieux que l'ère chrétienne, et la première
ligne indienne part de Madras en 1856. **Ce n'est pas la langue qui
est riche ou pauvre, c'est la planche qui est chez elle ou non** — la
colonne télougoue avait fait exactement le même parcours.

**Deux mots vieux de deux mille ans tombent sur des planches de 1926.**
சதுரங்கம் (tableau 13) est le nom du jeu des quatre corps d'armée,
d'où viennent le *shatranj* persan et le *chess* anglais : sur un salon
de café où tout le reste vient d'Europe, un seul objet fait le chemin
inverse. யாழ் (tableaux 14 et 16) est la harpe du Sangam, celle qui a
donné son nom à Yazhpanam, et பேரிகை le grand tambour des mêmes
textes — au milieu d'un étalage de guitares et de clarinettes.

**Le vasistas (78) casse enfin sa série.** Trente-huit colonnes
l'avaient nommé sans périphrase et la tâche 25 avait été close
là-dessus. Le tamoul a la chose dans toutes ses maisons, mais l'écrit
la nomme en deux mots — மேல் சாளரம் — et le parlé emprunte
« ventilator » à l'anglais, que la colonne n'écrit pas. Il faut donc
dire **trente-huit fois sur trente-neuf**, et non plus « toutes » :
une série qui ne casse jamais ne prouve rien tant qu'on ne l'a pas
cassée.

**Huit refus de transposition, un par occasion, et jamais le même
mot.** கபடி pour le jeu de barres (2) — le coréen avait refusé 진놀이
au même renvoi, deux langues sans rapport et le même piège ; பாதுகை
pour les sabots (3) ; திண்ணை pour le vérando (4) et pour le balcon
(5, 10, 13) ; கோட்டை pour le manoir (4) — mais **écrit** au tableau 9,
où le renvoi est une vraie forteresse : ce n'est pas le mot qu'on
juge, c'est la chose ; மாவட்ட ஆட்சியர் அலுவலகம் pour la préfecture
(11), qui était la tentation la plus forte de tout le relevé.

**Quatre noms de métier arbitrés, et jamais par prudence.** Le
cordonnier (7), le coiffeur et le tailleur (14), le boucher (15) ont
tous un nom de caste en tamoul, et tous servent d'injure. La colonne
écrit la fonction — mais celle qui est **peinte sur les enseignes de
Chennai en 2026**, முடி திருத்துபவர், தையல்காரர் : écrire la fonction
ne veut pas dire l'affadir.

**Deux choses corrigées en cours de route, et dites ici plutôt que
tues.** La lieue ne tombe pas juste en tamoul : le காதம் vaut dix à
seize kilomètres et non quatre, ce qui défait la règle que les
coïncidences télougoue et coréenne avaient suggérée (§ 8, colonne
coréenne). Et la parenté tamoule, l'une des plus fines qui soient —
நாத்தனார் la sœur du mari, சகலை le mari de la sœur aînée de l'épouse —
est **moins** précise que la coréenne sur un point : மாமனார் est le
beau-père des deux côtés. Deux langues très précises, précises sur des
axes différents.


### La colonne ourdoue : deux voisines, et de natures différentes

Toutes les colonnes défendues jusqu'ici l'étaient sur **un** front : le
cantonais contre le mandarin, le marathe contre le hindi, le coréen
contre le hanja, le tamoul contre son propre parlé. L'ourdou en a deux,
et elles ne se ressemblent pas.

* Il partage l'**écriture** avec le pendjabi chahmoukhi (`texto/pnb`),
  qui est une autre langue : même alphabet, même nastaliq, la voisine
  passerait inaperçue.
* Il partage la **langue** avec le hindi (`texto/hi`) — même grammaire,
  même lexique de base, au point que les deux se parlent sans
  traduction. Ils diffèrent par l'écriture, qui empêche toute
  contamination visible, et par le **registre savant** : sanskrit d'un
  côté, persan et arabe de l'autre.

`kolonoj.py` tient donc les deux fronts par deux moyens différents : le
premier par la **grammaire** — le génitif pendjabi *دا* n'existe pas en
ourdou, qui dit *کا* —, le second par le **lexique** — les tatsama du
hindi, ودیالیہ, پستک, ادھیاپک, que l'ourdou imprimé n'emploie jamais,
non parce qu'ils seraient trop savants mais parce que sa colonne
savante est l'autre. **Et deux mots n'ont pas été relevés, exprès** :
*دی* et *دے* sont les autres formes du génitif pendjabi et aussi des
mots ourdous ordinaires, le passé et l'impératif de « donner » ; de
même *اوہ*, pronom pendjabi et interjection ourdoue. Un contrôle qui
crie à chaque page finit désarmé.

**Le mot suit la date, pas la carte ni le prestige.** Le tableau 9 le
montre par un contre-exemple qu'aucune autre colonne n'offrait :
گلیشیئر, le glacier, est un **emprunt** dans la langue d'un pays qui
porte le Baltoro et le Siachen. Avoir la chose sous les yeux ne suffit
donc pas. Le tableau 10 donne l'autre bout : آبدوز, le sous-marin, est
un composé persan transparent — *آب* l'eau, *دوز* qui plonge — forgé au
XX⁠e siècle pour une chose que le persan n'avait jamais vue, et
« submarine » n'a jamais eu sa chance. **گلیشیئر est arrivé avant que
l'ourdou ait forgé ; آبدوز est arrivé avant l'anglais.**

**Deux tableaux voisins se renversent, et c'est l'usage qui décide.**
Sur mer (10), tout ce qui précédait la vapeur porte un nom persan —
عرشہ le pont, مستول le mât, لنگر l'ancre, بندرگاہ le port, آبنائے le
détroit, برزخ l'isthme — et tout ce que la vapeur a inventé est
anglais : کروزر, فریگیٹ, تارپیڈو, بوائلر, پسٹن. Au chemin de fer (12),
la vapeur **est** l'objet et pourtant l'ourdou nomme presque tout :
ڈبّا le wagon, پٹری le rail, پھاٹک la barrière, اوقات نامہ
l'indicateur, مال گاڑی le train de marchandises. Sept emprunts
seulement — et les sept se tiennent par la main : انجن, پلیٹ فارم,
ٹکٹ, گارڈ, سگنل sont les cinq mots qu'un voyageur lit **écrits** sur
place, en anglais, depuis 1861 ; بوائلر et پسٹن sont les deux pièces
qu'un voyageur ne voit jamais. Le chemin de fer indien a été construit
tôt et a servi tout le monde ; la marine à vapeur est restée le métier
d'un corps d'officiers qui parlait anglais.

**Trois mots ont voyagé dans l'autre sens, et il faut les compter dans
le bon.** برآمدہ la véranda (tableau 5), قلی le porteur (12), بازار le
bazar (16) : l'anglais et le français les ont pris à l'ourdou et au
persan, pas l'inverse. Les trois se ressemblent — un lieu couvert, un
homme qui porte, un marché : trois choses que l'Europe a rencontrées en
Asie et pour lesquelles elle n'avait pas de mot à elle.

**L'administration est le domaine où la colonne n'invente rien**, et la
raison est historique et non linguistique : l'Inde britannique a bâti
les mêmes offices que la France sur le même modèle, et ils ont gardé
leurs noms. ڈپٹی کمشنر rend exactement le préfet (11) ; تحصیل دار
exactement le percepteur (14) ; s'y ajoutent محصول خانہ, بلدیہ کا گھر,
عدالت, بچت خانہ, ڈاک خانہ, کتب خانہ, عجائب گھر, دار المعلمین. Et
گھنٹہ گھر, le beffroi (11), est le plus exact des neuf : une tour
communale qui porte l'horloge et la cloche et domine la vieille ville —
celle de Faisalabad, de Multan, de Lahore, bâtie au même siècle et pour
la même raison, et le mot dit « la maison de la cloche ».

**Dix refus de transposition, et le plus dur portait sur le plus beau
mot.** سارنگی est l'instrument à archet du nord de l'Inde et il était
tentant pour le violon (11), puisqu'il est vivant là où وائلن est un
emprunt ; mais il n'a ni le même jeu ni la même place, et il n'est pas
dans un orchestre de fosse. La colonne garde en revanche بانسری pour la
flûte et ڈھول pour le tambour, parce que ceux-là **sont** les choses.
Au tableau 9, on pouvait écrire مارخور pour le chamois (54) — le grand
caprin du Pakistan, son animal national — et on ne l'a pas fait. Au 8,
le vin, la bière et le cidre sont nommés sans détour dans une langue
dont la plupart des lecteurs n'en boivent pas. Au 15, le porc ouvre le
tableau et la colonne écrit son jambon, son boudin et son lard : c'est
l'usage qui a changé, pas le mot. **Et le ھارمونیم (14) renverse la
règle sans la casser** : mot emprunté, chose venue d'Europe en 1875, et
devenu l'instrument le plus ordinaire de la musique du nord de l'Inde.
Ce qui compte n'est pas d'où vient le mot, c'est ce qu'il montre.

**La relative postposée est l'outil qui manquait aux colonnes à tête
finale.** L'ourdou possède *جو … ہے*, héritée du persan, qui se pose
**après** son antécédent comme celle de l'ido. Le coréen et le tamoul
n'ont que le participe antéposé et devaient couper la phrase en deux ;
au bloc `t07-c2-12-1`, où les trois colonnes ont trébuché sur le même
passage, l'ourdou seul s'en tire sans couper. La prédiction écrite dans
l'en-tête du tableau 9 — « plus de deux divergences par tableau une
fois l'outil pris comme construction ordinaire » — a été vérifiée aux
tableaux 10 à 16 : **zéro faute d'ordre sur sept tableaux de suite**.
Le tiret reste nécessaire pour la circonstance et pour le génitif à
trois étages, que la relative ne prend pas sans lourdeur.

**Et c'est en comptant les gros plans tableau par tableau, pendant
l'écriture de cette colonne, qu'on a vu que le tableau 11 n'en avait
aucun** — dans les 42 colonnes à la fois, depuis toujours (§ 8, plus
haut).

### La colonne indonésienne : une voisine qui n'est dans aucun dossier

Toutes les colonnes défendues jusqu'ici l'étaient **contre une langue
présente ailleurs dans `texto/`** : le cantonais contre le mandarin, le
marathe contre le hindi, l'ourdou contre le chahmoukhi et le hindi à la
fois. L'indonésien a une voisine, et de très près — le malais de
Malaisie est la **même langue à un standard près** —, mais elle n'est
dans aucun dossier. Rien ne la signalerait à l'œil, et il n'y a donc
rien à comparer. `kolonoj.py` doit **relever**, non comparer, et il le
fait sur deux fronts.

**Le premier est géographique.** Les deux standards se séparent sur une
liste courte et très connue de mots quotidiens : *cikgu* contre *guru*,
*tandas* contre *toilet*, *stesen* contre *stasiun*, *ubat* contre
*obat*, *wang* contre *uang*, *beg* contre *tas*, *kerusi* contre
*kursi*, *almari* contre *lemari*, *tingkap* contre *jendela*, *bomba*
contre *pemadam kebakaran*, *tarikh* contre *tanggal*, *tayar* contre
*ban*, *basikal* contre *sepeda*, *hospital* contre *rumah sakit*.

**Le second est une date, et il est propre à ce livret.** L'orthographe
d'avant la réforme de 1972 — *boekoe* pour `buku`, *djalan* pour
`jalan`, *tjelana* pour `celana` — est exactement celle qu'un imprimeur
aurait employée en 1926, l'année du fac-similé. **C'est le seul piège du
relevé où la faute serait contemporaine de la source :** une colonne
écrite « comme à l'époque » serait plus fidèle à la date et moins fidèle
à la consigne, qui est d'écrire l'indonésien de 2026. Le contrôle relève
donc `dj`, `tj`, `oe` et `sj` partout ; `nj` est exclu exprès, il compte
23 occurrences justes dans *menjadi*, *menjaga*, *menjual*.

**Et cinq mots n'ont pas été relevés, exprès, parce qu'ils sont des faux
amis** : *pejabat* est le bureau là-bas et le fonctionnaire ici,
*budak* l'enfant là-bas et l'esclave ici, *polis* la police là-bas et la
police d'assurance ici — et le tableau 7 met justement en scène un agent
d'assurances —, *kedai* et *lori* existent des deux côtés avec des
emplois différents. Un contrôle qui crie sur un mot juste finit désarmé :
c'est la leçon de *دی* et *دے* à la colonne ourdoue, appliquée avant
d'avoir servi.

**Cinq couches, et chacune découverte par un tableau précis.** L'en-tête
du tableau 1 annonçait trois couches ; le tableau 5 en a révélé une
quatrième (le hokkien de la cuisine et du commerce de détail), le
tableau 11 une cinquième (le portugais) — et la correction a été écrite
là où la fausse annonce avait été faite, en notant que la preuve était
déjà dans l'en-tête du tableau 4, `beranda` < *varanda*. Le fond est
malais ; le sanskrit et l'arabe donnent l'école, la religion et l'État ;
le portugais donne les objets des navires du XVI<sup>e</sup> siècle
(*sepatu*, *jendela*, *meja*, *gereja*, *bendera*, *biola*, *serdadu*) ;
le néerlandais donne l'administration, l'armée et le potager (*zeni*,
*sersan mayor*, *brankas*, *wesel*, *kasir*, *wortel*, *buncis*,
*kol*) ; le hokkien donne la cuisine et la boutique.

**Le violon accepté, le théâtre refusé — et c'est la même règle.** Le
tableau 16 nomme le violon `biola`, du portugais *viola*, là où l'ourdou
avait refusé l'emprunt et gardé *سارنگی* (plus haut). Le même tableau
refuse pourtant `wayang` pour le théâtre de marionnettes (41) et écrit
`panggung boneka` : la chose gravée est un petit théâtre européen à
rideau rouge et à fauteuils d'orchestre, et lui donner le nom du wayang
aurait modernisé **la chose**. Le mot suit l'objet quand l'objet est
venu, et le refuse quand la langue en avait déjà un — dans un sens comme
dans l'autre.

**L'exotisme d'une planche belge est ici le voisinage.** La ménagerie en
carton du tableau 16 range côte à côte ce que le fabricant tenait pour
des bêtes lointaines : le rhinocéros (7), le singe (10), le crocodile
(12), la panthère (15), le léopard (18), la chauve-souris (35), le
palmier (70), et le « pays planté de cocotiers » qu'attaquent des
pirates dans un jeu de patience (48). Pour cette colonne, ce ne sont pas
des bêtes lointaines : `badak` et `macan tutul` vivent à Java et à
Sumatra, `buaya` est un des mots les plus anciennement malais du
tableau, et la côte du jeu est celle du lecteur. **La colonne ne le dit
pas : elle nomme, et c'est le nom qui le dit.** Le tableau 15 avait
donné l'envers du même fait — le potager y est néerlandais d'un bout à
l'autre parce que ce sont les Hollandais qui ont planté ces légumes-là,
et les fleurs artificielles du tableau 16 s'empruntent cinq fois sur six
pour la raison inverse : ces plantes n'ont jamais poussé ici.

**Une seule espèce de faute, quatre fois.** `\VUgras{}` vide aux
tableaux 5, 9, 10 et 15, toujours à la même place : un renvoi qui suit
un terme dont le groupe gras est déjà fermé, la main ouvrant un second
groupe pour « porter » l'exposant alors que l'exposant se porte tout
seul. `kolonoj.py` l'a relevée les quatre fois **sans qu'on ait eu à
inventer un contrôle pour elle** : il existait déjà. Le tableau 16, qui
porte cent trois renvois — plus que tout autre du livret —, n'en a
aucun, parce que la faute a été cherchée avant d'écrire.

### La colonne javanaise : le contrôle apprend où sa règle s'applique

La colonne javanaise est **l'exact contraire de la précédente, et c'est
la même paire de langues.** Quand on défendait l'indonésien, la voisine
n'était dans aucun dossier et il fallait relever sans pouvoir comparer.
Ici la voisine est `texto/id`, écrite par la même main, la colonne
d'avant : le danger s'est retourné, ce n'est plus l'absence de la
voisine, c'est sa **présence**. L'indonésien est la langue d'école de
tout locuteur du javanais, et une phrase javanaise glisse à
l'indonésien par les mots-outils avant de glisser par autre chose.
`kolonoj.py` relève donc vingt mots-outils — *tidak/ora*, *dan/lan*,
*dengan/karo*, *yang/sing*, *ini/iki*, *itu/iku* — et **jamais les mots
de chose**, que les deux langues partagent par centaines.

**Et un second front qu'aucune autre colonne n'a eu : les niveaux de
langue.** Le javanais a deux lexiques parallèles dans une seule langue,
le *ngoko* et le *krama*. La colonne tient le **ngoko alus** :
narration en ngoko, verbes krama inggil pour ce que fait le grand-père.
On relève donc le krama ordinaire — *kula*, *mboten*, *menika*,
*ingkang*, *sampun*, *kaliyan*, *griya*, *toya* —, et **on ne relève
pas** les verbes krama inggil — *dhahar*, *tindak*, *kondur*,
*ngendika*, *priksa*, *sare* —, qui sont exactement ce que la règle
exige. Un contrôle qui crie sur la forme que la consigne demande est
pire qu'un contrôle absent.

**Trois réglages, de trois natures différentes, et c'est le vrai
apport de cette colonne au relevé.**

1. **Une règle ôtée, parce que le mot n'était pas le même mot.** Les
   oies du tableau 3 se disent *banyak* en javanais ; *banyak* était
   relevé comme indonésianisme — il y signifie « beaucoup », et le
   javanais dit *akeh*. Les deux mots s'écrivent pareil et n'ont rien
   à voir : le javanais est un **oiseau**. La règle est ôtée, sa
   raison écrite à la place où elle était, et le mot reparaît au
   tableau 7 — une règle ôtée pour une bonne raison se paie une fois
   et sert toujours.
2. **Huit règles déplacées, parce que la situation change.** Le
   tableau 5 est un dialogue d'un bout à l'autre : Ioannes y parle à
   son oncle, et **un enfant javanais parle krama à un adulte**.
   *kula* y est la forme juste. Les niveaux ne se choisissent pas par
   texte mais par **qui parle à qui**. Les huit règles de krama sont
   donc passées de `"mot"` à une clé nouvelle, `"narracio"`, qui ne
   s'applique qu'aux fichiers **narrés**. Le dialogue se reconnaît au
   fichier et la mesure est nette : les attributions de parole
   s'écrivent `\textsc{...}. ---`, le tableau 5 en compte **36**, le
   tableau 12 en compte **une** — et c'est « Noto. », pas un locuteur
   —, les quatorze autres **aucune**. Le seuil est posé à cinq.
   Vérifié dans les deux sens : quatre mots de krama glissés exprès
   dans le tableau 4 sont relevés, les mêmes dans le tableau 5 ne le
   sont pas.
3. **Une règle resserrée, parce qu'un mot n'est pas un nom.**
   L'hôpital du tableau 11 se dit *rumah sakit* à Java comme partout ;
   or *rumah* était relevé, le javanais disant *omah*. La règle avait
   raison sur le **mot** et tort sur le **nom** — et la seule autre
   forme possible, *griya sakit*, est du krama, que la règle de niveau
   relèverait à son tour. `rumah` est donc relevé **sauf devant
   `sakit`**.

**Sept refus, et le dernier était préparé par les six autres.** Le
javanais offrait un mot tout prêt pour sept objets gravés, et la
colonne l'a refusé chaque fois : *gobak sodor* pour le jeu de barres
(tableau 2), *joged* pour le bal public (3), *gendhongan* pour le
berceau (6), *gamelan* pour l'orchestre (11), *dhakon* et *macanan*
pour les jeux du café (13), et enfin **`wayang` pour le théâtre de
marionnettes du tableau 16**. C'est le seul des sept dont la chose
ressemble à s'y méprendre à la chose gravée — un théâtre de
marionnettes contre un théâtre de marionnettes —, et c'est justement
pourquoi il fallait le refuser : la planche montre un petit théâtre
européen à rideau rouge et fauteuils d'orchestre. **On modernise la
langue, jamais les choses.**

**Mais le violon (76) est accepté, et sous le même nom portugais qu'en
indonésien :** *biola*, de *viola*. La colonne ourdoue avait refusé
l'emprunt et gardé *سارنگی* ; les deux colonnes de Java le prennent. Le
mot suit l'objet quand l'objet est venu, et le refuse quand la langue
en avait déjà un — le javanais avait le rebab et le gamelan, pas le
violon d'orchestre.

**Quatre couples néerlandais contre portugais, anglais ou malais,** et
ils disent toute la différence des deux colonnes de Java : *potlot* /
*pensil* le crayon, *pit* / *sepeda* le vélo, *porok* / *garpu* la
fourchette, *sepur* / *kereta api* le train. Quand les deux langues ont
emprunté le même objet, ce n'est presque jamais au même prêteur ni au
même siècle — et le dernier couple est le seul où la forme javanaise
soit un emprunt **contre** une forme indonésienne native. L'emprunt
n'est pas un signe de faiblesse : il est un signe de date.

**Et cinq mots sont sortis de Java**, ce qui n'arrive presque jamais
dans ce relevé : *wajan* la poêle (tableau 6), devenue *wadjan* en
néerlandais et *wok* en anglais ; *lahar* la coulée (9), qui se dit
*lahar* à Paris comme à Yogyakarta ; *jong* le grand voilier (10), pris
par les Portugais sous la forme *junco* et devenu *junk* en anglais —
le seul des cinq qui ait changé de chose en route ; plus *قلی* et
*بازار* déjà relevés à la colonne ourdoue. Presque tout ce livret
décrit des choses qui sont venues ; il faut un tableau de cuisine, un
volcan et un bateau pour qu'une chose parte.

**Trois lexiques que le javanais ne doit à personne** — le corps
(tableau 2), la parenté (4) et la ferme (7) —, et pas un mot commun
avec l'indonésien sur trente parties du corps : *sirah* contre
*kepala*, *rai* contre *wajah*, *mripat* contre *mata*, *untu* contre
*gigi*, *getih* contre *darah*, *balung* contre *tulang*. **Le lexique
le plus ancien est celui qui se ressemble le moins.** Et l'inverse est
vrai : le potager du tableau 15 est néerlandais **dans les deux
colonnes, mot pour mot**, parce que ce sont les mêmes Hollandais qui
ont planté les mêmes légumes dans les mêmes jardins.

### La colonne persane : la défense se joue au caractère

Les quarante-deux colonnes précédentes se défendaient d'une **langue**
voisine ; celle-ci se défend de deux voisines qui **logent dans son
propre alphabet**. L'ourdou lui a pris sa graphie et la moitié de son
lexique savant ; l'arabe lui a donné l'alphabet et l'autre moitié. Or
**ی et ي, ک et ك, ۱ et ١ se dessinent presque pareil** : une ligne
fautive reste bien formée, le LaTeX compile, `html.py` publie, et l'œil
ne voit rien. Les dix règles de `kolonoj.py` visent donc le
**caractère** — trois lettres rétroflexes ourdoues, ں, ے, ھ, puis ي,
ك, ة, ى arabes, les chiffres ٠١٢٣ contre ۰۱۲۳, et le demi-espace
manquant de نمی‌رود. **Elles ont toutes été prouvées sur un fichier
fabriqué avant qu'une ligne de persan soit écrite** : un contrôle qui
lit l'octet doit être vérifié sur des octets, pas sur du texte qu'on
espère juste.

**Le corps est persan, les organes sont arabes, et la frontière suit
exactement la peau.** Tout ce qu'on montre du doigt porte un nom
iranien — سر, چشم, دست, زانو, استخوان, خون —, et ce qu'il faut ouvrir
pour le voir porte un nom arabe — جمجمه le crâne, قلب le cœur, معده
l'estomac. La raison est une bibliothèque : **la médecine du monde
iranien s'est écrite en arabe** — Avicenne a composé le *Qanun* en
arabe —, et l'anatomie est revenue au persan dans la langue où elle
avait été rédigée. Ce que l'enfant nomme est persan ; ce que le médecin
nomme est arabe. Le même partage tient au tableau 4 : *سرماخوردگی*, « le
fait d'avoir pris froid », est persan et se dit de soi-même ; la fièvre
et l'ordonnance sont arabes.

**Une troisième couche, française, et elle date tout ce qui est arrivé
au XIX<sup>e</sup> siècle** : مرسی, آباژور, دوش, آسانسور, بلیت, واگن,
کراوات, کنکور — et les **mois grégoriens**, مارس, آوریل, مه, ژوئن,
ژوئیه, اوت. L'Iran a pourtant ses propres mois, ceux du calendrier
solaire hégirien, qui sont les noms des *izad* zoroastriens ; mais la
planche grave un printemps d'Europe, et **on modernise la langue,
jamais les choses**. Le français tient ici la place exacte que le
néerlandais tient en javanais, et pour la même raison : c'est la langue
par laquelle l'État moderne est arrivé.

**Les cinq sens sont cinq noms formés sur cinq verbes par un seul
suffixe** — بینایی, شنوایی, بویایی, چشایی, بساوایی —, ce que le
javanais fait au même alinéa du même tableau avec son préfixe *pa-*.
Deux langues sans parenté, la même élégance, et le français comme l'ido
y opposent cinq noms sans famille.

**Trois refus, et ils portent le compte du relevé à huit.** Le samovar
du tableau 6, le takyeh du 11 et le *خیمه‌شب‌بازی* du 16 : chaque fois
le persan offrait le mot tout prêt, chaque fois la planche gravait une
chose européenne — une cafetière belge, un opéra à l'italienne, un petit
théâtre à rideau rouge. La colonne écrit قهوه‌جوش, « le fait-bouillir-le-café » ;
تئاتر et اپرا pour la salle ; تئاتر عروسکی pour les marionnettes. **Mais le
violon (76) est accepté sous le nom ویولن, tandis que کمانچه reste à
l'instrument persan** — la solution la plus économique des trois du
relevé, et elle n'était possible que parce que la langue avait déjà les
deux choses.

**Sept fautes d'ordre en seize tableaux, toutes de placement, aucune de
grammaire.** Le quai du tableau 3, la table et la bibliothèque du 6, le
fumier du 7, la meule du 8, le cerf du 9, la valise du 12, le pourboire
du 13 : le persan est à tête initiale et pose ses compléments après,
rien ne l'obligeait à intervertir. **Une colonne qui se trompe sans que
la grammaire l'y pousse ne se corrige que par la machine** — c'est
exactement ce que le javanais avait montré au même tableau 3, au bloc
voisin.

**Et le chemin de fer du tableau 12 mesure une date dans la forme des
mots.** Le javanais n'avait pas un terme à lui — *sepur*, *karcis*,
*rel*, *peron*, tout néerlandais, parce que la première ligne de Java
date de 1867. Le persan a construit son transiranien en 1938, un siècle
après l'invention, et il a eu le temps de composer : راه‌آهن le chemin
de fer, ایستگاه le lieu où l'on s'arrête, قطار la file. **Ce qui arrive
tôt arrive avec son nom étranger ; ce qui arrive tard trouve une langue
prête à composer.** Java a reçu la machine avant d'avoir un mot ;
l'Iran l'a reçue après en avoir fait un.

**Enfin le vasistas (78) clôt une série de quarante-trois colonnes.**
Le français nomme cette fenêtre par une question allemande, l'indonésien
et le javanais par le néerlandais *boven*, le jour d'en haut ; le persan
dit *دریچه*, diminutif de *در*, la porte. **Une petite porte.** C'est le
seul des quarante-trois qui nomme la chose par ce qu'elle est et non par
où elle est — et c'est un mot que la langue avait déjà.

### La colonne haoussa : le contrôle vise la lettre, en alphabet latin

La colonne persane défendait son alphabet contre deux voisines qui y
logeaient. Celle-ci s'écrit en **lettres latines** et n'a aucune
voisine dans le relevé — et son contrôle vise le caractère malgré
tout, parce que **son alphabet compte quatre lettres qu'aucun clavier
ordinaire ne donne** : ɓ, ɗ, ƙ, ƴ. Ce ne sont pas des b, d, k, y
ornés, ce sont des lettres pleines, et « kofa » n'est pas « ƙofa » :
c'est la différence d'un mot à rien du tout. Une ligne dépouillée de
ses crochets reste bien formée, le LaTeX compile, `html.py` publie, et
l'œil qui lit le français ne voit rien. **Cette colonne se défend de
sa propre saisie**, ce qu'aucune autre n'avait eu à faire.

Douze règles dans `kolonoj.py`, **prouvées sur un fichier fabriqué
avant qu'une ligne de haoussa soit écrite**, comme les dix règles
persanes. Huit visent des formes nues qui ne sont *rien* en haoussa
(kofa, karfe, karshe, kauye, daya, daki, dauka, yan) ; une vise la
lettre arabe, cette colonne étant en boko et non en ajami ; une
l'apostrophe droite, là où le coup de glotte s'écrit ’ ; et **une
vise p, q, v, x, que l'alphabet boko n'a pas**.

**Trois réglages, et les trois sont venus du texte.**

1. **Une règle resserrée.** Le N.-B. du tableau 2 invite le maître à
   décrire chaque jeu « daki-daki », en détail. Or *daki* était relevé,
   puisque la chambre s'écrit *ɗaki* et que la forme nue ne valait
   rien : elle valait quelque chose, liée à elle-même par un trait
   d'union. C'est le « rumah sakit » javanais dans une autre langue.
2. **Une règle qui tient un choix et non une faute.** Le Niger écrit
   *ƴan*, le Nigeria *’yan* ; les deux sont justes chez eux. La
   colonne s'est donnée **quatre crochets**, et trois crochets plus
   une apostrophe n'est pas le même alphabet. Ce que la règle relève
   n'est donc pas une faute mais un **mélange** — première du relevé
   dans ce cas.
3. **Deux exemptions, et elles disent où sont les citations.** La note
   « Balk-o » du tableau 5 et la note « Lambrequino » du tableau 6
   citent d'autres langues mot pour mot ; la règle des lettres
   absentes a crié quatre fois puis deux, et elle avait raison à la
   lettre. **Une citation n'est pas une faute d'orthographe, c'est un
   autre texte** — et ce ne sont pas les italiques qui les portent,
   ce sont les NOTES.

**Et la règle des lettres absentes a fait la meilleure prise du
relevé**, au tableau 15 : l'ido y nomme une confiture « riba o
quinga », groseille ou coing, et l'alinéa avait été écrit en laissant
les mots **anglais** dans le texte — *currant* et *quince*. Ce n'est
pas une faute d'orthographe, c'est un mot qu'on a oublié de traduire,
et aucun autre contrôle ne l'aurait vu : `renvoji.py` compte des
renvois, `plenajo` compare des longueurs, `html.py` publie. **Le q de
« quince » a suffi.**

**Cinq mots portent presque toute la colonne, et ils nomment par la
forme ou par l'usage, jamais par l'espèce.** *keke* est tout ce qui
tourne sur un axe — la bicyclette (2), la voiture attelée (5), le
rouet et la roue de moulin (7), le funiculaire (9), la roue à aubes
(10), le tramway à chevaux (11), les roues de la locomotive (12), le
fiacre et la machine à coudre (14) : **dix objets, un seul mot.**
*jirgi* est tout grand porteur, et c'est le milieu qui le distingue —
jirgin ruwa le bateau, jirgin ƙasa le train, jirgin sama l'avion.
*dutse* est la pierre et la montagne, et bâtit tout le tableau 9.
*fitila* est la lampe quel que soit son combustible, de l'huile au
phare. *ma-* fait le lieu, l'agent et l'outil, et **la voyelle finale
sépare le lieu de l'homme** — ma’aikata l'atelier contre ma’aikaci
l'ouvrier, maƙera la forge contre maƙeri le forgeron.

**Un métier à nom en « ma- » est plus vieux que le siècle ; un métier
à nom en « mai » a été fabriqué hier.** Le préfixe est fermé, et la
liste des ma- est exactement celle des métiers que la ville haoussa
avait avant les Britanniques ; le mot libre *mai* est ouvert et a
nommé tout ce qui est arrivé depuis. Le coiffeur le prouve à lui
seul : « wanzami » au village (tableau 7), métier héréditaire ; « mai
gyaran gashi » en ville (tableau 14), boutique au premier étage. Les
mêmes ciseaux, et trois siècles entre les deux mots.

**Douze refus, et deux d'entre eux valent pour tout le relevé.** Les
marrons du tableau 7 : « gyaɗa », l'arachide grillée, donne mot pour
mot la scène gravée — la vieille femme qui grelotte, le brasero, le
cornet de papier, les mains qu'on réchauffe — et **la ressemblance
parfaite d'un usage ne fait pas l'identité d'une chose**. Le chanteur
de rue du tableau 14 : « maroƙi » avait été **écrit** au tableau 3
pour le mendiant, parce que là l'homme demandait ; ici il tourne une
manivelle. **Le même mot accepté à un tableau et refusé à un autre,
pour la même raison les deux fois.**

**Ce que le haoussa ne doit à personne tient en trois lexiques** — le
corps (2), la cuisine (6) et la basse-cour (7) — et **ce qu'il doit,
il le doit à qui a apporté la chose** : les sept jours à l'arabe, les
douze mois à l'anglais, la marine et le chemin de fer à l'anglais
encore. Mais **pas une de ses quatre directions**, arewa, kudu,
gabas, yamma, que la rose des vents du tableau 16 confirme. On
emprunte le temps, qui s'écrit ; on garde l'espace, qui se marche.

**Et l'exception de la douane tombe ici, après avoir tenu deux fois.**
Le javanais gardait « pabean » et le persan « گمرک » comme seul
bâtiment moderne à nom d'ici, parce qu'on perçoit au port depuis
toujours. Le haoussa n'a jamais eu de douane de port : le commerce
transsaharien se taxait à la porte de la ville, « kuɗin ƙofa ». **Une
exception qui tient deux fois et tombe la troisième en dit plus
qu'une qui tiendrait toujours** — elle ne tenait pas à la douane,
elle tenait au port.

### La colonne gujaratie : l'outil qui compte se lit *avant* d'écrire

Les deux colonnes précédentes ont appris que le contrôle peut viser la
lettre. Celle-ci apprend autre chose : **quel outil de la famille il
faut lire, et à quel moment.** Le gujarati est une langue à **tête
finale** — le possesseur avant le possédé, le complément avant le
verbe, la relative avant son antécédent. Or le livret est écrit dans
une langue à tête initiale, et il enchaîne les génitifs : *le jet DE
la fontaine*, *le bureau DE mon cousin*, *l'impériale DE l'omnibus*,
*la scie DU bûcheron*. Chaque fois que deux renvois tombent de part et
d'autre d'un « de », **le gujarati les retourne tout seul**.

**Les trois outils se lisent à trois moments, et c'est cette colonne
qui l'a démontré.** `parigi.py` **AVANT** : il dit quels *couples*
vont s'inverser, et il faut l'avoir lu avant d'écrire une ligne.
`ordo.py` **PENDANT** : il donne la suite complète des renvois du
bloc, à recopier. `renvoji.py` **APRÈS** : il dit si l'ordre est bon.
Les tableaux où `parigi.py` n'a pas été consulté d'abord sont ceux qui
ont saigné : deux fautes au tableau 1, quatre au tableau 3, quatre au
tableau 6, et **cinq au tableau 14** — le record du relevé, sur un
tableau qui n'est qu'une enfilade de vitrines appartenant chacune à
quelqu'un. **Un tableau de possessifs est, pour une langue à tête
finale, ce que le bloc aveugle est pour le contrôle : l'endroit où il
faut compter à la main.**

**Le remède est un seul et il est toujours le même** : la relative
gujaratie en « જે », héritée du sanskrit, qui **pose la tête d'abord**
et rejette le reste derrière. *La scie (34), laquelle est aux mains du
bûcheron (33).* Ce n'est pas une acrobatie de traducteur : c'est la
tournure ordinaire de la langue, et c'est justement pour cela qu'elle
marche.

**Le contrôle de langue, lui, vise le mot et non la lettre** — treize
règles, contre les douze du haoussa et les dix du persan. La difficulté
n'est pas la même : le gujarati a **trois voisines de trois natures** —
le hindi, qui partage son fonds et la moitié de ses mots-outils ; le
marathi, qui partage sa grammaire ; l'ourdou et le persan, qui ont
fourni le vocabulaire du commerce et de l'administration. Une règle de
caractère écarte le dévanagari (`U+0900..U+097F`) : le gujarati est le
dévanagari **moins la barre du haut**, et douze règles de mot écartent
les formes hindies qui se glisseraient sans qu'on les voie — *હૈ* pour
*છે*, *ઔર* pour *અને*, *કા/કી* pour *નો/ના/ની*. Trois formes sont
**délibérément non relevées** — નહીં, કે, મેં — parce qu'elles sont
hindies **et** gujaraties : une règle qui crierait au tableau 1 serait
désarmée au tableau 16.

**Ce que cette colonne a trouvé tient en une phrase : une langue garde
le nom de ce qu'elle a manié.** Le bouleau (t. 9) est « ભૂર્જ » parce
que le Cachemire a écrit dessus pendant quinze siècles ; le sapin, qui
n'a jamais servi à rien ici, n'a pas de nom. Le port de commerce
(t. 10) est entièrement gujarati — વહાણ, સઢ, ડોલકાઠી, હલેસું, સુકાન,
તૂતક, લંગર, ધક્કો, ગોદી, વખાર, જકાત, ખલાસી, દીવાદાંડી — et le port de
guerre entièrement anglais, parce que cette côte a commercé deux mille
ans et n'a plus eu de marine à elle après les Portugais. Le chemin de
fer (t. 12) partage exactement : **ce qu'on voit** reçoit un mot d'ici
(ગાડી le train, ડબો le wagon, પાટા les rails), **ce qu'on ne fait
qu'apprendre** reste anglais (સિગ્નલ, પ્લૅટફૉર્મ, ટિકિટ, ગાર્ડ).

**Sept refus, et quatre d'affilée du même genre.** La châtaigne (t. 7)
contre l'arachide grillée, le coquelicot (t. 8) contre le pavot à
opium, la pervenche (t. 9) contre celle de Madagascar, le fromage
(t. 13) contre le paneer. Chaque fois **le mot tombait sous la main et
la chose n'était pas la même** — c'est exactement pour cela qu'il
fallait refuser. À l'inverse, l'harmonium (t. 14) est écrit sans
hésiter : la chose est venue, elle est restée, et le mot est d'ici.

**Trois interdits, trois religions, une seule règle.** Le cochon
(t. 7) dans l'État le plus végétarien de l'Inde, le menu de crevettes
et de Saint-Émilion (t. 13) dans le seul grand État sous prohibition
totale, et la viande de bœuf (t. 15), dont l'abattage est puni de la
réclusion à perpétuité depuis 2017. Les trois sont écrits, sans note
et sans détour, avec les mots que la langue possède : ભૂંડ, ઝીંગા,
દારૂ, ગૌમાંસ. **La langue a les mots ; c'est le faire qui est
interdit, pas le nommer** — la colonne haoussa l'avait démontré une
fois, celle-ci le démontre trois fois de plus, et la troisième dans un
code pénal et non dans des têtes.

**Onze mots portugais en seize tableaux**, et aucun n'a l'air
étranger à qui le parle : મેજ la table, પાદરી le prêtre, અનનાસ
l'ananas, મિસ્ત્રી le maçon, બંબો la pompe — qui revient au tableau 11
comme pompe à incendie, le pompier étant « બંબાવાળો » —, ઇસ્પિતાલ
l'hôpital, આયા la bonne d'enfants, બટાટા la pomme de terre, કોબી le
chou, પાંઉ le pain, નાતાલ Noël. **Les Portugais n'ont pas seulement
apporté des mots : ils ont apporté les légumes, et le mot est venu
accroché à la chose.** Diu et Daman ont été portugais jusqu'en 1961 :
ce n'est pas un vieux fonds, c'est un voisinage.

**Et deux mots ont remonté le courant, à deux tableaux de suite** :
કુલી le porteur (t. 12), parti d'ici vers l'anglais, et શતરંજ les
échecs (t. 13), chaturanga en sanskrit, passés par la Perse avant
d'arriver dans un café de Royan. Un troisième aurait suivi — વાણિયો le
marchand, qui a donné *banyan* — mais c'est un nom de caste avant
d'être un nom de métier, et le commerçant du tableau 14 est un drapier
français : on a écrit « વેપારી ». **Le tableau 7 avait noté que les
métiers sont des castes ; c'est au tableau 14 que cela coûte quelque
chose.**

**Enfin le mot qui ferme le relevé était dans un titre.** « La
Bazaro », au tableau 16, est « બજાર » : le seul des seize titres du
livret dont les deux langues possédaient déjà le mot. Il est persan et
il est arrivé dans chacune par une route différente — dans le gujarati
directement, avec les marchands ; dans l'ido par le turc, l'italien et
le français, après un tour de la Méditerranée. **Le livret dit bazar à
un lecteur qui dit bazar.**

### La colonne levantine : quand les deux voisines sont la même langue

Les quinze colonnes précédentes se défendaient contre une langue
**étrangère** : le marathe contre le hindi, le persan contre l'ourdou,
le gujarati contre le hindi. L'arabe levantin (`texto/apc/`) est le
premier cas où **les deux voisines sont la même langue que lui** —
l'arabe standard (`ar`), qui est la forme *écrite* de sa propre langue,
et l'égyptien (`arz`), qui en est une autre forme parlée. Le danger
n'est donc pas qu'un mot étranger se glisse : **c'est que la main, en
écrivant, remonte toute seule vers le registre qu'on lui a appris à
l'école.** Les vingt règles de `kolonoj.py` visent les deux côtés à la
fois — douze contre le standard (ليس, هذا, الذي, سوف, ماذا, أين, متى,
الآن, هل, يوجد, أيضًا…), sept contre l'égyptien (ده, دي, إزاي, فين,
دلوقتي, كده, عايز, بتاع), une contre les quatre lettres persanes.

**Trois formes ne sont délibérément pas relevées**, et il fallait
l'écrire sous peine de les reprendre plus tard : `كيف` est levantin
*et* standard, `بس` est levantin *et* égyptien, `في` est l'existentiel
levantin *et* la préposition standard. Une règle sur l'une des trois
crierait à chaque tableau, et **un contrôle qu'on désarme ne contrôle
plus rien** — la leçon du marathe au tableau 10.

#### Le défaut de `\b`, trouvé en trois fois

C'est cette colonne qui a mis au jour la faute la plus ancienne du
contrôle. En arabe, `\b` de Python **ne se referme pas là où finit le
mot** : les signes diacritiques (tanwin `U+064B`, chadda `U+0651`…)
sont de catégorie `Mn`, donc « non-mot », et la frontière tombe *avant*
eux. Le défaut a été trouvé en trois temps, et chaque temps a démenti
le précédent :

1. **Au câblage** — la règle `أيضاً` ne criait jamais. Mesuré : `أيضًا`
   (alef puis tanwin) déclenche, `أيضاً` (tanwin puis alef) non. **Et
   la colonne égyptienne portait la même règle morte depuis le
   début**, pour `أيضاً`, `جداً` et la famille `كثيرًا`.
2. **Au tableau 1** — la règle `هل` s'est déclenchée *à l'intérieur*
   de `هلّق`, qui est le mot levantin le plus ordinaire du relevé : la
   chadda est une marque, le `\b` se referme donc juste avant elle. Le
   premier correctif, à une seule négation, **inventait un mot par le
   milieu tout en en manquant un par la fin**.
3. **Au tableau 3** — `فين` s'est déclenchée dans `مجدّفين` : le `\b`
   *ouvrant* s'ouvre après une marque, exactement de même.

La forme finale n'emploie plus `\b` du tout et encadre le mot de deux
négations, **comme `_deva` et `_guj` le faisaient depuis le premier
jour** : la réponse était dans le fichier, deux helpers plus haut. Les
vingt règles ont été prouvées une à une sur un fichier fabriqué (20/20
déclenchent) ; `ar` et `arz`, réparées au passage, restent à zéro
signalement.

#### Ce que la colonne a trouvé

- **La forme du mot date le métier** (tableau 14). Le suffixe turc
  `-جي` s'accroche à **l'objet qu'on vend** — البرنيطجي le chapelier,
  الكفوفجي le gantier, العربجي le charretier, المكوجيّة la repasseuse
  (t. 15) — et la forme arabe `فعّال` au **geste qu'on fait** —
  الحدّاد, النجّار, الخيّاط, الصبّاغ. On forge, on scie, on coud : ce
  sont des verbes, et les métiers sont vieux. On vend des chapeaux et
  des parapluies : ce sont des objets, et ils sont arrivés avec
  l'Empire. **C'est exactement la loi que la colonne haoussa avait
  trouvée sur ses préfixes ma-/mai-** : deux langues sans rapport, deux
  morphologies, une seule manière de dater un mot.
- **Trois fois sous l'arabe.** `تموز` Tammuz (t. 5) et `صمّون` le petit
  pain (t. 15) descendent à l'akkadien — le second par le grec
  σεμίδαλις et l'araméen, et l'ido écrivait au même renvoi `semli`,
  qui est le *Semmel* allemand, **du même mot akkadien arrivé par
  l'autre bout de l'Europe**. `التمساح` le crocodile (t. 16) descend au
  copte, donc à l'égyptien ancien. Le temps, la nourriture, une bête du
  Nil.
- **Des mots sortis et revenus** : `المقهى` (t. 13) est le café de
  l'Europe entière ; `الترسانة` et `الأميرال` (t. 14) sont partis puis
  rentrés ; `القيسريّة` (t. 15), la halle, est le nom de César resté
  sur les plaques d'Alep. Et `الشطرنج` (t. 13) est **l'étape du milieu
  de la route dont la colonne gujaratie avait trouvé le départ** :
  chaturanga → شطرنج → scacchi, échecs, chess.
- **Le mot que la voisine lit autrement.** Le seul alinéa du livret qui
  aligne la poire, la prune et la pêche (t. 15, alinéa 9) écrit en
  levantin إجّاص، خوخ، درّاق ; l'égyptien du même relevé écrirait
  كمثرى، برقوق، خوخ. **Les deux colonnes emploient خوخ, et il vaut
  prune à Beyrouth, pêche au Caire.** Un mot faux ne se verrait pas
  ici : il se lirait.
- **Le menu du tableau 13 passe sans une égratignure**, et c'est
  précieux, parce que c'est lui qui avait cassé la colonne gujaratie.
  La difficulté du gujarati n'était donc **pas** la francité du repas :
  c'étaient les interdits. **Il aura fallu deux colonnes pour savoir ce
  qui était difficile dans la première.**

#### Une règle suspendue en le disant

L'alinéa 5 du tableau 16 — la bataille de soldats de plomb — est **le
seul endroit de la colonne écrit en arabe standard, exprès**. Le siège,
le bombardement, l'assaut, la sortie, l'armistice, le traité de paix
n'ont aucune forme dialectale : on ne raconte pas une guerre en
levantin, on la raconte en fusha, parce que c'est la langue des
communiqués. La colonne le fait et l'inscrit dans son en-tête : **une
règle qu'on suspend en le disant vaut mieux qu'une règle qu'on trahit
en silence.**

Et la dernière tentation a été refusée. Le théâtre de marionnettes du
tableau 16 (41) et ses trois personnages appellent de toutes leurs
forces `كراكوز`, le Karagöz du théâtre d'ombres ottoman, que tout le
monde connaît à Damas et à Alep. **Ce n'est pas ce que la planche
montre.** On écrit donc مسرح العرايس et les trois noms transcrits : *on
modernise la langue, jamais les choses* — et la règle se vérifie mieux
au dernier tableau qu'au premier, parce qu'au dernier on sait
exactement ce qu'on perd.

Enfin le titre du seizième tableau n'a pas eu besoin d'être traduit :
`البازار`. La colonne gujaratie avait fait la même trouvaille au même
tableau avec `બજાર`, et le français de Rochelle écrit *bazar* sans
s'apercevoir qu'il écrit du persan. **Trois colonnes et l'original sur
un seul mot, et c'est le dernier titre du livret.**

## 9. Les huit contrôles

    python3 outils/controles.py

1. **Pagination** — folio imprimé = feuillet − 2, sur toutes les pages.
2. **Feuillets** — aucun oublié, aucun relevé deux fois. Les deux
   versos vierges du livret ido (48, 76) sont reconnus comme tels.
3. **Appariement** — quelles clés n'existent que d'un côté.
4. **Unicité** — aucune clé posée deux fois dans une même langue.
5. **Coupures** — chaque fin d'alinéa à cheval a sa reprise.
6. **Géométrie** — la boîte d'encre occupe-t-elle une part
   vraisemblable de la page ?
7. **Gras** — les deux colonnes mettent-elles en gras le même nombre de
   passages ? L'une témoigne pour l'autre.
8. **Synchronie** — les deux colonnes d'un rang portent-elles le même
   alinéa ? Une différence de longueur énorme dit que le compteur de
   clés a dérivé.

État actuel : contrôle 8 à 1 rang sur 524 ; contrôle 3 à 10 clés
orphelines sur 572 ; contrôle 6 signale l'échelle du fac-similé
français (§ 4) ; **contrôle 7 à 187 alinéas sur 562**, soit un tiers —
c'est le chantier ouvert.

### Le neuvième contrôle : la matière des colonnes traduites

    python3 outils/kolonoj.py            # les 46 colonnes traduites
    python3 outils/kolonoj.py yue mr     # celles-là

Les huit contrôles ci-dessus regardent la pagination, l'appariement des
clés et la géométrie ; `renvoji.py` regarde les renvois ; `objekti.py`,
les objets nommés. **Aucun ne regardait la matière d'un fichier de
traduction** — ses macros, ses coupures, sa langue. Cet outil-là, écrit
d'abord au coup par coup dans un répertoire temporaire, est maintenant
dans `outils/`, en un seul contrôle paramétré. Il ne prend jamais `io`
ni `fr` : ce sont des *transcriptions*, elles suivent les lignes du
fac-similé et écrivent donc légitimement `\nl`, `\cc` et `VUpage`.

Chaque contrôle est né d'une faute, et deux d'entre elles étaient
**invisibles à `renvoji.py`** :

| Le contrôle | Ce qui l'a rendu nécessaire |
|---|---|
| macro inconnue | `\textuperscript{(74)}` au tableau 11 cantonais, `\textsuperscht{}` deux fois en irlandais — un s manquant, un i et un p en moins. `renvoji.py` **ne pouvait pas les voir** : il relève aussi les renvois composés `(74)` à plein corps, parce que le relevé ido en compose ainsi au tableau 5. Le renvoi sortait juste et le fichier composait faux. Même contrôle : quatre `\nl` restés en tchèque, en irlandais et en galicien |
| renvoi en gras | `\VUgras{(94)}` au tableau 10 égyptien — même angle mort |
| accolade en fin de ligne | le retour à la ligne se rend par une espace, et l'espace tombe alors *dedans* le groupe gras |
| ligne trop longue | 41 lignes de 95 à 139 caractères dans neuf colonnes écrites avant que la règle existe |
| bloc amputé | trois blocs marathis avaient perdu un fragment de phrase, repris au numéro de ligne dans un fichier déjà replié. `renvoji.py` n'en a signalé **qu'un** — celui qui avait perdu un renvoi |
| forme étrangère | trois colonnes n'existent que parce qu'elles ne sont pas leur voisine (§ 8) |
| forme étrangère **hors dialogue** | le javanais choisit son niveau de langue par *qui parle à qui*, non par texte : ses huit règles de krama vivent dans une clé à part, `"narracio"`, qui ne s'applique qu'aux fichiers narrés. Le dialogue se reconnaît au nombre d'attributions de parole — 36 au tableau 5, une au 12, aucune ailleurs, seuil à cinq (§ 8) |

Le contrôle du bloc amputé ne compte pas les mots : il compare la
**longueur** de chaque bloc à celle de son homologue ido et se cale sur
la médiane de la colonne. Le rapport varie beaucoup d'une écriture à
l'autre — le chinois dit en cent signes ce que le marathi dit en trois
cents — mais il varie peu d'un bloc à l'autre *dans* une même colonne.
Un bloc tombé sous la moitié de la médiane a perdu quelque chose.

Les 46 coupures posées dans les neuf colonnes trop larges ont été
vérifiées comme il se doit : les **42 colonnes rendues sont identiques
octet pour octet** avant et après. Un retour à la ligne se rend par une
espace, et l'espace entre deux idéogrammes s'ôte partout (§ 8) — replier
une ligne ne change donc rien à ce qui se lit.

**Un caractère de remplacement n'est jamais du texte, et le contrôle
a été ajouté après coup.** Un `U+FFFD` s'était glissé en fin de phrase
dans `texto/ur/15-jadval-06.tex`, à la place d'un point ourdou. Aucun
des cinq outils ne l'a vu : `renvoji.py` ne lit que l'ordre des
renvois, `kolonoj.py` ne lisait que les macros et les mots, `html.py`
l'aurait publié tel quel. Il n'a été trouvé qu'en relisant. Le contrôle
relève désormais le caractère de remplacement et les caractères de
commande C0 — c'est le seul de ce fichier qui ne regarde ni la langue
ni la mise en page : **il regarde l'octet**.

**Un signalement de langue n'est pas toujours une faute**, et deux
l'ont prouvé au tableau 7 et au tableau 13 égyptiens (§ 8). Les deux
sont exemptés par leur forme **exacte**, jamais par le mot : un contrôle
qu'on désarme en bloc ne contrôle plus rien.

---

### La liste de courses : `parigi.py`

    python3 outils/parigi.py 5     # les paires du tableau 5
    python3 outils/parigi.py       # les 408 paires du livret

Ce n'est pas un contrôle, c'est une **liste de courses**. `renvoji.py`
dit *après coup* que deux renvois sont sortis dans le mauvais ordre ;
celui-ci le dit *avant*, en lisant l'ido seul.

**La cause est l'ordre modificateur-tête, et rien d'autre.** La colonne
télougoue a coûté 2, 0, 9 puis 7 inversions aux tableaux 1 à 4, et le
tableau 4 en a donné la raison exacte : en télougou — comme en tamoul,
en coréen, en ourdou, en persan, en goudjarati —, **tout ce qui
qualifie précède ce qui est qualifié**, sans exception. Dès qu'un
renvoi tombe sur un modificateur et un autre sur sa tête, les deux
sortent à l'envers, mécaniquement, quelle que soit la phrase.

L'outil relève donc, dans chaque bloc de l'ido, les couples de renvois
séparés par un mot de rattachement — *di, dil, de, kun, qua, por, sur,
proxim*… — **ou par un participe**, qui rattache sans mot-outil :
« bubi (35) *preiranta* la muzikisti (36) ». Il ne relève **pas** les
énumérations : deux renvois séparés par « e » ne sont pas en rapport de
dépendance, et une langue à tête finale les rend dans l'ordre. C'est
pourquoi les tableaux qui énumèrent — le marché, la rue — coûtent moins
que ceux qui rattachent, **dans toutes les langues du relevé**.

**Il est calibré, et ses ratés sont nommés.** Sur les dix-huit
inversions réellement commises aux tableaux 3 et 4 télougous — relevées
par `renvoji.py`, puis corrigées, donc de vérité connue :

| Fenêtre | Trouvées | Lignes à lire (t1–t4) |
|---|---|---|
| 30 caractères | 13 sur 18 | 29 |
| **45 caractères** | **16 sur 18** | **55** |
| 80 caractères | 16 sur 18 | 88 |

Le motif s'est élargi **une fois depuis**, et il vaut la peine de dire
pourquoi. Au tableau 8 deux inversions ont passé, toutes deux absentes
de la liste :

* « la planajo (39) **ube** flugeskas la alaudi (41) » — `ube` est
  l'adverbe relatif de lieu, de la même famille que `qua`, et le motif
  l'avait oublié. **Vrai trou, comblé** : le relevé passe à 17 sur 19.
* « la fisho (47) snapas l'angelo quik **kande** ili plunjas sua filo
  (46) » — `kande` introduit une circonstancielle, pas un modificateur
  de nom. **Ce n'est pas un rapport modificateur-tête**, et l'outil a
  raison de ne pas le signaler : l'inversion venait du rédacteur. On
  n'ajoute donc ni `kande` ni `dum`.

Le premier cas élargit l'outil, le second lui donne raison. Les
distinguer valait mieux que d'ajouter les deux.

**Il s'est élargi une seconde fois au tableau 14, et cette fois il
manquait une moitié de paradigme.** « tamburestro (42) *sequata* da la
tamburisti (43) » et « porto-triciklo (80) *duktata* da grumo (79) »
sont des rapports modificateur-tête aussi francs que « bubi (35)
*preiranta* la muzikisti (36) » — mais le participe y est **passif**, et
le motif ne prenait que l'actif : *-ant, -int, -ont*, sans *-at, -it,
-ot*. Le livret passe de 386 à **408 paires**, six pour cent de lignes
en plus pour vingt-deux rattachements dont dix-huit sont attributifs.
Un minimum de deux lettres devant la désinence vient avec, sans quoi le
motif prend *tota*, *tote*, *poti*, *pinti* — un adjectif, un adverbe
et deux noms qui finissent comme des participes.

**On a refusé, en revanche, d'allonger la fenêtre.** Deux inversions
seulement ont échappé à la liste sur seize tableaux, toutes deux par
distance : 54 caractères au tableau 10, 47 au tableau 11, contre une
fenêtre de 45. Porter la fenêtre à 55 les rattraperait toutes les deux
— et ferait passer le livret de 408 à 490 paires, vingt pour cent de
lignes en plus. Ce n'est pas le principe qui diffère du cas précédent,
c'est le **rapport** : six pour cent pour vingt-deux, contre vingt pour
cent pour deux. On mesure avant de trancher, et `renvoji.py` a de toute
façon attrapé les deux au premier jet.

**Et « \cc » n'est pas une coupure, c'est une soudure.** Le fac-similé
coupe ses mots en fin de ligne ; la transcription le note ainsi. Le
premier jet dépouillait ce jeton comme n'importe quelle macro, en le
remplaçant par une espace : « ku\cc\nranta » se lisait « ku ranta », et
six paires du livret se trouvaient tenues par des **fragments** qui
ressemblaient à des participes — *ranta, sante, mante, vinta, dante,
danta*. Elles étaient justes par accident. La coupure tombe en outre
souvent au milieu d'un gras — « \VUgras{voya}\cc\n\VUgras{jonti} » —,
et il a fallu franchir aussi la frontière de groupe pour que
« voyajonti » redevienne un mot.

Celui-là reste signalé, et c'est irréductible : en ido le nom d'agent
pluriel et l'adjectif participe ont la même finale, *-anti*, *-onti*.
Aucune expression régulière ne les sépare. On le laisse donc, et on
l'écrit dans l'en-tête plutôt que d'élargir le motif pour le faire
taire : **du bruit connu n'est pas du bruit ignoré.**

Les deux qui échappent sont nommées dans l'en-tête du fichier, et l'une
d'elles n'est **pas** un rapport modificateur-tête : c'est une
coordination, que le télougou rend dans l'ordre — l'outil a raison de ne
pas la signaler. Sur les dix-sept vraies paires, il en trouve seize.

**Ce n'est donc pas un contrôle exhaustif, et il ne prétend pas
l'être** : `renvoji.py` reste l'autorité. Celui-ci fait gagner du temps,
pas de la certitude.

**Ce qu'il vaut, mesuré :** le tableau 5 télougou, **le plus long du
livret** — 68 blocs, plus de cent vingt renvois —, a été écrit avec sa
liste en main et n'a coûté **aucune** inversion au premier jet, là où
les quatre précédents en avaient coûté dix-huit. **Les onze tableaux
suivants non plus** : la colonne télougoue est complète, 683 blocs,
`renvoji.py` à zéro divergence.

---

### L'ordre reçu : `ordo.py`

    python3 outils/ordo.py t10     # les blocs du tableau 10
    python3 outils/ordo.py 3       # les deux scènes, c1 et c2

**Le troisième outil de la même famille, et il comble un trou qu'on a
payé cher.** `parigi.py` dit *avant* d'écrire quelles **paires** une
langue à tête finale sortira à l'envers ; `renvoji.py` dit *après coup*
si l'ordre est bon. Entre les deux manquait la chose la plus simple :
la **suite complète** des renvois d'un bloc, à suivre en écrivant.

**Elle manquait vraiment, et c'est mesuré.** Le tableau 9 tamoul a
coûté **neuf** écarts au premier passage, et **sept** portaient sur des
couples que `parigi.py` ne contient pas — la scie et le bûcheron, le
cor et les veneurs, la corneille et sa branche, l'araignée et sa
mouche. Ce ne sont pas des rapports modificateur-tête : `parigi.py` n'a
pas à les voir. Le tableau 10, écrit avec la suite sous les yeux, en a
coûté **trois**. Neuf contre trois, même colonne, deux tableaux de
suite.

Il imprime pour chaque clé `%%K` les renvois dans l'ordre où ils
tombent — chiffres, lettres, « 94 bis », et les parenthèses nues que le
fac-similé compose sans leur `\textsuperscript`. Les blocs « suite »
sont recollés au bloc qu'ils continuent, comme `html.py` les recolle.
Il ne porte **aucun** jugement : c'est une copie de l'ordre reçu, et
c'est tout ce qu'on lui demande.

---

## 10. Prochaines étapes, dans l'ordre

1. **Le gras.** Le contrôle 7 signale 187 alinéas où les deux colonnes
   ne mettent pas en gras le même nombre de passages. Les tableaux 16 et
   5, les deux pires, ont été repris au fac-similé ; quatorze restent.
   Une part des écarts est réelle — « jenio-soldato » contre « soldat du
   génie » ne fait pas le même compte — mais pas toute.
   Outil : `python3 outils/grasdiff.py t08`.
2. **Mesurer à la règle la hauteur du papier** des deux exemplaires
   (§ 4), puis `kalibro.py`, puis `korpo.py`.
3. Traduire le français vers les cinq autres langues de l'ONU :
   ajouter les entrées dans `LANGUES` et `DOSSIER`, en tête de
   `outils/html.py`, et un fichier par langue et par tableau dans
   `texto/<code>/`. Prévoir `dir="rtl"` pour l'arabe.
4. Retrouver les seize tableaux muraux et les rendre cliquables (§ 7).
