# SENTINEL-X — Conception de référence

- **Statut** : source de vérité **architecture / périmètre / capacités / choix techniques / décisions**.
- **Version** : 0.2 (consolidation : revue et protocole externalisés dans leurs propres documents)
- **Date** : 2026-10-16
- **Portée** : ce document ne contient **ni la revue de l'état de l'art, ni le protocole d'évaluation** (documents dédiés ci-dessous).

**Documents liés (une seule source de vérité par sujet) :**

- État de l'art → `docs/research/state-of-the-art.md`
- Protocole d'évaluation → `docs/EVALUATION.md`
- Version combinée v0.1 (remplacée) → `docs/archive/CONCEPTION_DE_REFERENCE_v0.1_COMBINED_SUPERSEDED.md`

**Conventions de statut** : **[DÉCISION]** (choix acté) · **[HYPOTHÈSE]** (à tester, non établi) · **[OUVERT]** (à trancher). Aucune revendication d'originalité n'est faite ici ; voir l'état de l'art.

---

## 1. Positionnement et valeur propre

- **[DÉCISION]** SENTINEL-X est une **plateforme SOC d'investigation open source**, auto-hébergeable, qui transforme des alertes et leurs événements en **investigations structurées, tracées et vérifiables** assistant la décision humaine.
- **[DÉCISION]** La GenAI / NLP / RAG / agents contrôlés font partie de son **identité technique** et montent en capacité par niveaux validés.
- **[DÉCISION]** La plateforme SOC reste le **produit**. Le dispositif d'évaluation et de robustesse **renforce** le produit ; il ne le remplace pas.
- **[HYPOTHÈSE]** Élément distinctif candidat = **investigation adossée aux preuves + évaluation/robustesse reproductible**. **Non établi** : à confirmer par la revue formelle avant toute revendication (voir état de l'art ; décision D1).
- **Ce que SENTINEL-X n'est pas** : ni SIEM complet, ni simple wrapper LLM, ni simple détecteur ML, ni simple benchmark.

## 2. Problématique et utilisateurs

- **Problématique [DÉCISION]** : *concevoir une plateforme d'investigation SOC assistée par IA (NLP, RAG, agents à permissions limitées) qui contextualise des alertes, mène des vérifications fondées sur des outils en lecture seule, et produit des conclusions vérifiables et traçables — en maîtrisant hallucinations, données adversariales et actions non autorisées — chaque apport IA étant **mesuré** contre des baselines (voir `EVALUATION.md`).*
- **Utilisateurs** : *primaire* analyste SOC tier-1/tier-2 ; *secondaire* ingénieur détection / threat-intel ; *tertiaire* chercheur/étudiant (reproductibilité). *Hors cible initiale* : réponse automatique en production, intégration SIEM d'entreprise large.

## 3. Les deux composantes

**A — Plateforme SOC intelligente (produit).** Ingestion/normalisation d'alertes → score de priorité **explicable** → enrichissement (ATT&CK, Sigma, KEV, NVD) → investigation assistée (NLP, RAG, agents outillés en lecture seule) → **rapport structuré** (faits / inférences / hypothèses / inconnues / recommandations) → provenance + journal d'audit. Approbation humaine pour toute action sensible.

**B — Dispositif d'évaluation & de sécurité (renfort du produit, de première classe).** Mesure chaque capacité IA (triage, retrieval, groundedness, investigation, robustesse, coût) ; batterie d'attaques (injection indirecte, abus d'outils, RAG poisoning) ; traçabilité (prompts versionnés, modèle figé, seeds). **Protocole détaillé dans `EVALUATION.md`.**

> **[DÉCISION]** Une capacité de A n'est « acquise » qu'une fois mesurée dans B.

## 4. Capacités IA successives (niveaux de maturité)

Progression par niveaux, **sans durée**. Un niveau ne s'ouvre qu'une fois le précédent accepté.

- **N0 — Socle reproductible** : schéma d'alerte/événement, import de données documentées, validation, recherche documentaire basique, **baseline de triage déterministe**, tests. *(Pas d'IA générative.)*
- **N1 — Compréhension des alertes (NLP)** : extraction d'entités/IOC, normalisation, résumé, explication des champs, détection d'informations manquantes. Sorties **structurées**, renvoi aux sources.
- **N2 — RAG contrôlé** : index de connaissances versionné, récupération, **citations**, filtres de pertinence, réponses limitées aux éléments retrouvés + « preuve insuffisante » autorisé.
- **N3 — Investigation par outils** : orchestrateur choisissant parmi des **outils autorisés en lecture seule**, interrogeant événements/connaissances, construisant une chronologie ; chaque action **autorisée, journalisée, fondée sur un résultat réel**.
- **N4 — Workflows multi-étapes + vérification indépendante** : planification, réévaluation, gestion des inconnues, reprise sur erreur, **challenge indépendant** avant clôture (inspiré d'AIDA — **non original**, assumé).
- **N5 — Intelligence enrichie** : corrélation multi-alertes, graphe de relations, mémoire d'investigation contrôlée, rôles multiples — chaque extension doit **améliorer une métrique sans dégrader** sécurité/repro/coût.

## 5. Datasets par capacité (rôle ; licences détaillées ailleurs)

Rôle fonctionnel uniquement. **Détail licences + conditions de redistribution → `state-of-the-art.md` ; usage expérimental → `EVALUATION.md`.**


| Capacité                            | Datasets                                                           | Rôle                                           |
| ------------------------------------ | ------------------------------------------------------------------ | ----------------------------------------------- |
| Triage (classification/priorisation) | Microsoft GUIDE ; (CIC-IDS2017 / UNSW-NB15 en complément réseau) | Baselines de triage/classement                  |
| RAG / connaissances                  | MITRE ATT&CK ; Sigma ; CISA KEV ; NVD                              | Enrichissement, mapping, citations (versionné) |
| Investigation multi-étapes          | AIT-LDSv2 + AIT-ADS ; scénarios synthétiques maison              | Chronologie, preuves, vérité-terrain          |
| Robustesse / sécurité              | Scénarios adversariaux maison                                     | Injection / abus d'outils / poisoning           |

**Garde-fou transversal [DÉCISION]** : ne jamais conclure sur le seul synthétique ; croiser avec des données publiques non générées par nous. Détail anti-fuite/anti-circularité dans `EVALUATION.md`.

## 6. Baselines (résumé ; protocole dans `EVALUATION.md`)

Chaîne d'ablation : **A** règles (sans LLM) → **B** LLM seul → **C** LLM+RAG → **D** LLM+RAG+outils → **E** LLM+RAG+outils+vérification indépendante (SENTINEL-X complet). L'apport des outils = D−C ; l'apport de la vérification = E−D. Métriques, rubrique de notation et gestion de la variance : `EVALUATION.md`.

## 7. Architecture logicielle et choix techniques

**[DÉCISION] Monolithe modulaire** à interfaces explicites (pas de microservices au départ).


| Domaine               | Choix initial                                                                                                                  | Justification                                                      | Évolution conditionnelle                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Langage / API         | Python, FastAPI, Pydantic                                                                                                      | Standard, typage, contrats de données                             | Contrats plus stricts si intégrations ↑                                                                                               |
| Stockage relationnel  | **PostgreSQL** (alertes, scénarios, audit)                                                                                    | Un seul moteur fiable couvre tôt les besoins                      | —                                                                                                                                      |
| Recherche vectorielle | **pgvector** (extension Postgres)                                                                                              | Vecteurs dans le moteur existant, aucun service en plus            | **Qdrant** séparé si ANN à l'échelle / filtres avancés mesurés nécessaires                                                       |
| Recherche plein texte | **FTS natif PostgreSQL** (`tsvector`/`tsquery`, ranking `ts_rank`)                                                             | Lexical sans composant externe.*NB : le FTS natif n'est pas BM25.* | Extension**BM25** (p. ex. `pg_search`/VectorChord-BM25) ou moteur dédié **seulement si** un vrai scoring BM25 est mesuré nécessaire |
| RAG hybride           | Fusion score vectoriel (pgvector) + lexical (FTS)                                                                              | Hybride simple sans brique externe                                 | Reranking / filtres métadonnées avancés sur besoin mesuré                                                                           |
| Modèles IA           | Abstraction`LLMProvider` + baseline déterministe ; **v1 = un fournisseur API hébergé** (Claude) ; **local NON obligatoire** | Remplaçabilité, repro, time-to-first-result                      | **Local (Ollama/vLLM) supporté, pas imposé** : souveraineté / repro hors-ligne / comparaison de modèles                             |
| Orchestration agent   | **Machine à états explicite** maison, minimale                                                                               | Lisibilité, traçabilité, pas de lock-in                         | LangGraph*seulement si* la complexité le justifie (D2)                                                                                 |
| Triage/ML             | Règles + scikit-learn (baselines)                                                                                             | Baselines avant modèles avancés                                  | Classifieurs ajoutés si labels/gains le permettent                                                                                     |
| Interface             | Démo légère (API + UI minimale)                                                                                             | Démontrabilité sans surcoût                                     | Dashboard d'investigation plus tard                                                                                                     |
| Reproductibilité     | pytest, données d'exemple, Docker Compose, docs                                                                               | Socle repro dès N0                                                | CI, suivi d'expériences, pipelines d'éval                                                                                             |

## 8. Sécurité, traçabilité, reproductibilité, anti-injection

- **Données non fiables [DÉCISION]** : tout événement/log/document/sortie d'outil est potentiellement hostile ; ne remplace jamais les instructions système. Séparation stricte *instructions* / *données*.
- **Permissions outils** : liste explicite, **lecture seule au départ**, pas de shell, pas de scan réel, pas de remédiation auto ; validation des arguments, données exposées limitées, journalisation appels+résultats, arrêt sûr en cas d'incertitude.
- **Proposition ≠ exécution** : proposition → politique → validation → autorisation → (humain) pour toute action sensible. Le prototype doit **savoir s'abstenir**.
- **Traçabilité IA** : par investigation — modèle+version, version de prompt/template, documents récupérés, appels d'outils+résultats, sortie structurée, horodatage, ID incident.
- **Reproductibilité LLM [DÉCISION]** : modèle figé, température/seed consignés, prompts versionnés hors code, journalisation complète.
- **Secrets** : `.env` jamais commité, `.env.example`, scanners (Gitleaks, etc.).
- **Anti-injection mesuré** : batterie d'attaques → **taux de blocage mesuré** (voir `EVALUATION.md`), jamais affirmé.

## 9. Conserver / reformuler / reporter / abandonner (vs spec initiale)


| Élément                                                   | Décision                       | Justification                                              |
| ----------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------- |
| Schéma d'alerte/événement normalisé                     | **Conserver**                   | Socle N0                                                   |
| Baseline de triage déterministe                            | **Conserver**                   | Baseline A                                                 |
| RAG cyber + provenance + « preuve insuffisante »          | **Conserver (cœur)**           | Identité                                                  |
| Investigation LLM à outils lecture seule                   | **Conserver (cœur)**           | Produit                                                    |
| Policy engine + approbation humaine + audit                 | **Conserver**                   | Différenciation sécurité                                |
| Sorties structurées, prompts versionnés, traçabilité IA | **Conserver**                   | Repro/sécurité                                           |
| Vérification/challenge indépendant                        | **Conserver mais reformuler**   | Utile,**non original** (AIDA/CORTEX) → ne pas revendiquer |
| Datasets réseau (CIC-IDS/UNSW)                             | **Reformuler**                  | Baseline triage uniquement                                 |
| UEBA / anomalie comportementale ML                          | **Reporter**                    | Source de signaux optionnelle, plus le cœur               |
| Corrélation multi-alertes / graphe d'attaque               | **Reporter (N5)**               | Après investigation de base validée                      |
| Elastic/Kibana, Airflow, n8n, MLflow, DVC, Prometheus       | **Reporter (conditionnel)**     | Réintroduction sur besoin mesuré (ADR)                   |
| Axe HPC / Slurm / Jean Zay                                  | **Abandonner du cœur**         | Décision actée ; sans dépendance stage                  |
| Neo4j                                                       | **Abandonner (pour l'instant)** | NetworkX si besoin                                         |
| Évaluation humaine avec participants                       | **Reporter**                    | Coût éthique/RGPD disproportionné au stade actuel       |
| Réponse automatique                                        | **Reporter**                    | Lecture seule d'abord                                      |

## 10. Critères d'acceptation par niveau (portes de passage)

Mesure effectuée selon `EVALUATION.md`.


| Niveau          | Accepté si…                                                                                                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **N0**          | Import reproductible ; schéma validé ; baseline de triage déterministe mesurée ; jeux de test + labels documentés ; tests verts ;`docker compose up` propre.                                      |
| **N1**          | Sorties NLP structurées ; erreurs d'extraction mesurées (précision/rappel entités/IOC) ; chaque élément renvoie à sa source ; régression testée.                                              |
| **N2**          | Retrieval mesuré (Recall@k/MRR/nDCG) ; % d'affirmations supportées mesuré ; « preuve insuffisante » émis à bon escient ; citations vérifiables.                                                |
| **N3**          | Chaque action d'outil autorisée + journalisée + fondée sur un résultat réel ; permissions testées (tentatives interdites bloquées) ; chronologie reconstruite sur ≥1 scénario de référence. |
| **N4**          | Apport des outils (D−C) et de la vérification (E−D)**mesurés** sur scénarios figés (investigation + groundedness) **sans** dégrader sécurité/coût ; charge d'investigation lue avec le FNR.  |
| **N5**          | Chaque extension répond à un besoin constaté et**améliore une métrique** sans régression de sécurité/repro/coût.                                                                              |
| **Transversal** | Robustesse mesurée et non en régression ; repro : modèle figé + prompts versionnés + seeds.                                                                                                       |

## 11. Décisions ouvertes (synthèse ; détail et justif. dans les docs liés)


| #      | Décision                       | Recommandation actuelle                                                                                                    |
| ------ | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **D1** | Formulation de la contribution  | Revue formelle (`state-of-the-art.md`) **avant** toute revendication. Candidat : évaluation + robustesse reproductibles.  |
| **D2** | Orchestration agent             | Machine à états maison ; réévaluer LangGraph à N4.                                                                    |
| **D3** | Moteur vectoriel                | pgvector d'abord ; Qdrant sur besoin mesuré.                                                                              |
| **D4** | Fournisseur LLM v1              | API hébergée derrière`LLMProvider` ; local supporté non obligatoire ; versions figées.                                |
| **D5** | Licence du dépôt              | **[OUVERT]** séparer licence du code / des données / des artefacts dérivés (voir `state-of-the-art.md`). ADR licences. |
| **D6** | « SecAlertBench »             | Référence vérifiable à fournir, sinon retiré.                                                                         |
| **D7** | Datasets réseau (CIC-IDS/UNSW) | Cantonnés au triage/baseline.                                                                                             |
| **D8** | Scoring lexical BM25            | FTS natif Postgres d'abord ; extension BM25 ou moteur dédié seulement si un vrai BM25 est mesuré nécessaire.           |

## 12. Correspondance avec le dépôt

- Ce fichier → `docs/architecture/CONCEPTION_DE_REFERENCE.md` (conception).
- État de l'art → `docs/research/state-of-the-art.md`.
- Protocole → `docs/EVALUATION.md`.
- Menaces IA (à venir) → `docs/THREAT_MODEL.md` + `SECURITY.md`.
- Décisions D1-D8 → `docs/decisions/ADR-0xx-*.md`.
- Statut projet → `PROJECT_STATE.md`.
