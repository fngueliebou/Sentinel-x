# SENTINEL-X — Protocole d'évaluation

- **Statut** : protocole de référence (v0.2). À figer *avant* toute analyse de résultats.
- **Date** : 2026-10-16
- **Principe directeur** : *aucune capacité IA n'est « acquise » sans mesure vs au moins une baseline adaptée.* L'évaluation **renforce** le produit (Composante B), elle ne le remplace pas.
- **Documents liés** : conception → `docs/architecture/CONCEPTION_DE_REFERENCE.md` · état de l'art → `docs/research/state-of-the-art.md`.
- **Note d'honnêteté** : ce document définit *comment* mesurer. Il ne contient **aucun résultat** : toute valeur future est `NON ENCORE MESURÉ` tant qu'elle n'a pas été produite et journalisée.

> **Règles transversales anti-fuite / anti-circularité / anti-post-hoc**
> 1. **Préenregistrement** : hypothèses, métrique **primaire**, métriques secondaires et seuils de décision sont écrits et **commités avant** de produire les résultats (§7).
> 2. Séparation stricte **développement / test** ; aucun réglage sur le test (§6).
> 3. Le **corpus RAG** est séparé des **réponses de référence** d'évaluation.
> 4. Les données **synthétiques** ne prouvent jamais seules : toujours croiser avec des données publiques non générées par nous (AIT, GUIDE), et scénarios synthétiques **revus indépendamment** de leur génération.

---

## 1. Deux familles d'évaluation — strictement séparées

| | **Famille T — Triage simple** | **Famille I — Investigation multi-étapes** |
|---|---|---|
| Question | Escalader ? avec quelle priorité ? | Que s'est-il passé ? preuves, chronologie, techniques, conclusions tracées |
| Entrée | 1 alerte/incident + contexte | 1 alerte initiale + accès à des outils de récupération |
| Sortie | Classe (TP/BP/FP) et/ou rang | Rapport structuré + preuves citées |
| Nature | Classification / ranking | Récupération de preuves + raisonnement + rédaction |
| Modes d'échec | FP/FN, mauvais ordre | Preuves manquées, hallucination, citation erronée, clôture injustifiée |
| Données | GUIDE (+ réseau en complément) | AIT (logique Alert-Bench) + synthétiques à vérité-terrain |

**Pourquoi séparer** : tâches, données, vérité-terrain, métriques et modes d'échec différents. Un « score global » mêlant les deux masquerait p. ex. un FNR catastrophique. Chaque famille a ses baselines et sa grille.

---

## 2. Tâches évaluées (mappées aux niveaux)

| Niveau | Capacité | Famille | Tâche |
|---|---|---|---|
| N1 | Compréhension (NLP) | — | Extraction entités/IOC ; renvoi à la source |
| N2 | RAG contrôlé | support I | Qualité de récupération + groundedness/citations |
| N3 | Investigation par outils | I | Récupération correcte, chronologie, actions autorisées |
| N4 | Workflows + vérification | I | Rapport d'investigation ; ablations D/E (§3) |
| N0/N3 | Triage | T | Classification/priorisation vs baseline déterministe |
| Transversal | Robustesse | T+I | Injections, abus d'outils, respect des permissions |

---

## 3. Baselines et **ablations** (par famille)

Chaîne d'ablation incrémentale, pour **isoler l'apport de chaque composant** :

| Config | Composants | Sert à isoler |
|---|---|---|
| **A** | Règles / score déterministe (sans LLM) | Plancher non-LLM |
| **B** | LLM seul (alerte + contexte, sans récupération) | Apport du LLM nu |
| **C** | LLM + RAG | **Apport du RAG = C − B** |
| **D** | LLM + RAG + **outils** (lecture seule) | **Apport des outils = D − C** |
| **E** | LLM + RAG + outils + **vérification indépendante** (SENTINEL-X complet) | **Apport de la vérification = E − D** |

Règles :
- Chaque config tourne sur **les mêmes scénarios** (comparaison **appariée**, §7).
- Un composant n'est validé que si son incrément (p. ex. E−D) est **positif sur la métrique primaire** **et** ne dégrade ni la sécurité ni le coût au-delà du budget (§8-9).
- Les ablations D et E répondent explicitement à la demande : *mesurer séparément ce qu'apportent les outils et la vérification indépendante*, plutôt qu'un simple « avant/après » global.

---

## 4. Datasets retenus, rôle, vérité-terrain, licence

| Dataset | Famille | Rôle | Vérité-terrain | Licence données |
|---|---|---|---|---|
| **Microsoft GUIDE** | T | Triage/priorisation, données réelles | Labels de triage **niveau incident** (TP/BP/FP), analystes clients | **CDLA-Permissive-2.0** |
| **AIT-LDSv2 + AIT-ADS** | I | Investigation avec logs + alertes | Vérité-terrain **événementielle** (AIT-ADS) ; attaque multi-étapes | **CC BY-NC-SA 4.0 (NC)** |
| **Scénarios synthétiques maison** | I + robustesse | Contrôle, cas ambigus, FP, injections | **Annotations de référence** : alertes/preuves/chronologie/conclusions/inconnues/actions attendues | À définir (interne) |
| **MITRE ATT&CK / Sigma / KEV / NVD** | support RAG | Corpus de connaissances (séparé des réponses de référence) | — | Variables (vérifier + **versionner**) |
| **CIC-IDS2017 / UNSW-NB15** | T (complément) | Baselines de classement réseau | Labels de flux | **À vérifier** |

**Licences — rappel (détail dans `state-of-the-art.md` §5.c)** : ne pas confondre licence du **code** (nôtre, p. ex. permissive), des **données** (AIT = NC/SA) et des **artefacts dérivés** (tout artefact *contenant* du contenu AIT reste CC BY-NC-SA 4.0 / non commercial ; des scripts ne contenant pas de données AIT peuvent être permissifs). À confirmer juridiquement avant publication.

---

## 5. Vérité-terrain par famille

**Famille T** : label de triage GUIDE (niveau incident). Limite : labels clients imparfaits ; fort déséquilibre.

**Famille I** : deux sources complémentaires —
1. **Vérité-terrain événementielle AIT-ADS** (quelles alertes/événements appartiennent à l'attaque).
2. **Annotations de référence des scénarios synthétiques** : pour chaque scénario, fixées *a priori* — alertes attendues, preuves à trouver, chronologie correcte, techniques ATT&CK attendues, conclusions acceptables, **inconnues légitimes**, actions **autorisées/interdites**. **Revues indépendamment** de la génération.

> La qualité d'investigation est mesurée **contre ces annotations**, jamais contre l'avis du modèle lui-même.

---

## 6. Séparation développement / test

- **Splits figés et versionnés** (hash du jeu de test consigné) ; le test ne sert jamais à régler prompts, seuils ou modèles.
- **Généralisation, pas mémorisation** : pour les scénarios synthétiques, séparer **par template/paramètres générateurs**, pas seulement par instance — les scénarios de test utilisent des **familles d'attaque / variantes tenues à l'écart** du développement.
- **Anti-fuite** : le corpus RAG ne contient pas les réponses de référence ; les scénarios de dev ne recouvrent pas ceux de test.
- **Journalisation** : chaque exécution enregistre version de dataset, version de modèle, version de prompt, seed, commit.

---

## 7. Métriques, comparaisons et préenregistrement

### 7.a Métriques par famille
**Famille T** : Precision/Recall/F1 par classe ; **PR-AUC prioritaire** (déséquilibre, pas l'accuracy) ; **FPR/FNR** ; ranking P@K/nDCG si priorisation.
**Famille I** : exactitude vs référence ; rappel de preuves pertinentes ; **charge d'investigation** (nb étapes/outils) **lue conjointement au FNR** (leçon Alert-Bench) ; hypothèses erronées ; reconnaissance des inconnues.
**Support RAG (N2)** : Recall@k / Precision@k, MRR, nDCG ; **groundedness** (% d'affirmations liées à une preuve pertinente) ; exactitude des citations ; taux d'affirmations non supportées.

### 7.b Rubrique de notation des rapports d'investigation (Famille I)
Chaque rapport est noté par une grille **figée** ; notation au **niveau affirmation** (claim-level), pas au jugé global :
1. **Exactitude de la conclusion** vs conclusion de référence (correcte / partielle / incorrecte).
2. **Ancrage (grounding)** : part des affirmations reliées à une preuve récupérée réelle.
3. **Exactitude des citations** : la preuve citée soutient-elle l'affirmation ?
4. **Couverture des preuves** : part des preuves de référence effectivement trouvées.
5. **Mapping ATT&CK** : techniques correctes / manquées / inventées.
6. **Gestion de l'incertitude** : les inconnues légitimes sont-elles signalées (« preuve insuffisante ») plutôt que comblées ?
7. **Affirmations non supportées** (hallucinations) : compte, pénalisant.

**Qui note** : adjudication selon la grille ; un **juge LLM** indépendant (modèle distinct de celui évalué, prompt de notation versionné) **peut** pré-noter, mais avec **contrôle humain par échantillon** et **accord inter-annotateurs** reporté. L'évaluation humaine complète avec participants reste **reportée** (coût éthique/RGPD) — cf. conception.

### 7.c Gestion de la variabilité des LLM
- **k exécutions** par config (k fixé à l'avance, p. ex. ≥ 5) ; reporter **moyenne + dispersion** (écart-type ou IC), pas une valeur unique.
- Décodage **figé** (température, seed si le fournisseur le permet) ; **noter** que certains fournisseurs restent non déterministes même à température 0.
- **Comparaisons appariées** : A→E sur **les mêmes scénarios** ; reporter les **deltas par scénario**, pas seulement des moyennes agrégées.

### 7.d Éviter les conclusions post-hoc
- **Métrique primaire unique** déclarée avant les runs ; le reste est secondaire/exploratoire et étiqueté comme tel.
- **Pas de sélection de métrique** après avoir vu les résultats ; pas de changement de seuil a posteriori.
- Quand de **nombreuses configurations** sont comparées, prévoir une **correction pour comparaisons multiples** et distinguer résultats **confirmatoires** vs **exploratoires**.
- **Plan d'analyse commité** (fichier horodaté) avant de produire les chiffres finaux.

---

## 8. Tests adversariaux (robustesse — transversal)

**Menaces mesurées** : injection de prompt **indirecte** (instructions malveillantes dans logs/documents/sorties d'outils), **abus d'outils** (tenter une action interdite), **RAG poisoning** (fausse connaissance insérée).

**Protocole** : batterie d'attaques **variée et versionnée** ; chaque attaque a un **résultat attendu** (bloquée / neutralisée / signalée). On mesure, on n'affirme pas.

| Métrique | Unité |
|---|---|
| Actions interdites **bloquées** | % |
| Succès d'injection (instruction suivie) | % (↓ mieux) |
| Respect des permissions (lecture seule) | % de conformité |
| Détection de conflit de sources (poisoning) | taux |
| Signalement d'incertitude sous attaque | taux |

**Garde-fou** : un éventuel classifieur anti-injection est lui-même **évalué**, jamais supposé fiable. Les données hostiles ne remplacent jamais les instructions système.

---

## 9. Coûts et efficacité

| Métrique | Unité | Note |
|---|---|---|
| Latence | ms/s par alerte ou investigation | p50/p95 |
| Appels modèle / outils | compte | par investigation |
| Tokens | compte | entrée/sortie |
| **Coût estimé** | € par investigation | **budget fixé a priori** → hypothèse « sans coûts disproportionnés » **falsifiable** |
| Reproductibilité | oui/non | rejouable à config figée |

---

## 10. Enregistrement d'expérience (reproductibilité)

Par expérience significative : `ID`, date, objectif, hypothèse, dataset+version, modèle+version, config/paramètres, **seed**, config d'ablation (A–E), baseline, **métrique primaire déclarée**, k exécutions, résultats observés (`NON ENCORE MESURÉ` sinon), interprétation, limites, commit Git. Prompts **versionnés hors code** ; modèle **figé** (fournisseur, version, température).

---

## 11. Limites connues du protocole

- **Circularité résiduelle** : les scénarios synthétiques, même revus, encodent nos hypothèses → ne jamais conclure sur le seul synthétique.
- **AIT = laboratoire** : ne reproduit pas un SOC réel ; généralisation limitée.
- **GUIDE = triage seulement** : pas d'investigation multi-étapes.
- **Labels imparfaits** : GUIDE (clients) et AIT (labo) ≠ vérité absolue.
- **Juge LLM** : peut biaiser la notation des rapports → contrôle humain par échantillon obligatoire.
- **Non-déterminisme LLM** : variance inter-runs ; d'où k exécutions + versions figées.
- **Chiffres de l'état de l'art non reproduits** : comparaisons à CORTEX/AIDA/etc. fondées sur des chiffres **annoncés par leurs auteurs**.
- **Pas de validation terrain** : aucune mesure en SOC de production (hors périmètre).

## 12. Portes de passage

Critères d'acceptation N0→N5 dans la conception (`CONCEPTION_DE_REFERENCE.md` §10). Règle unique : **mesurer dans ce protocole avant de déclarer un niveau acquis.**
