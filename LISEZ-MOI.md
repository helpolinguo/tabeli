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
| Les 16 tableaux muraux | **absents** — voir § 7 |
| Contrôles automatiques | huit contrôles (`outils/controles.py`) |

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
    outils/inventaire.py      relevé de géométrie, feuillet par feuillet
    outils/mesures.py         médianes et échelles possibles
    outils/kalibro.py         écrit kalibro-*.tex
    outils/altox.py           hauteur d'x (mesure écartée, § 4)
    outils/chaso.py           corps par la chasse (mesure retenue, § 4)
    outils/ceni.py            indice de scène dans les clés %%K
    outils/controles.py       les six contrôles
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
