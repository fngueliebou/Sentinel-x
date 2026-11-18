> # DOCUMENT ARCHIVÉ
>
> Ce fichier est la **version combinée v0.1** de la conception de référence (état de l'art + conception + protocole dans un seul document). Il est remplacé et conservé uniquement pour l'historique.
>
> **Sources de vérité actuelles :**
>
> - Conception/architecture → `docs/architecture/CONCEPTION_DE_REFERENCE.md`
> - État de l'art → `docs/research/state-of-the-art.md`
> - Protocole d'évaluation → `docs/EVALUATION.md`
>
> Date d'archivage : 2026-10-16.
>
> ---

# SENTINEL-X — Conception de référence

- **Statut** : proposition de source de vérité du dépôt.
- **Version** : 0.1 (révision post-réorientation)
- **Date** : 2026-10-15
- **Portée** : revue de l'état de l'art vérifiée + conception de référence + décisions ouvertes.
- **Principe de lecture** : ce document distingue rigoureusement **[VÉRIFIÉ]** (confirmé par une source citée), **[NON VÉRIFIÉ]** (introuvable ou non confirmé), **[HYPOTHÈSE]** (proposition à tester), **[DÉCISION]** (choix de conception acté) et **[OUVERT]** (à trancher). Aucune idée n'est présentée comme originale sans élément à l'appui.

---

## PARTIE I — REVUE DE L'ÉTAT DE L'ART (vérifiée)

### I.1 Méthode

Revue menée par recherche (octobre 2026) sur les travaux nommés dans la mission (CORTEX, AIDA/Alert-Bench, SecAlertBench, Cognitive SOC) + travaux adjacents + projets open source. Pour chaque élément : ce qui est réellement implémenté/évalué, les données, l'accessibilité publique, les limites, et le statut de vérification. Les affirmations non confirmées sont signalées comme telles plutôt que comblées.

### I.2 Travaux académiques

#### CORTEX — *Collaborative LLM Agents for High-Stakes Alert Triage* (2025)

- **[VÉRIFIÉ]** Architecture **multi-agents** de triage d'alertes où des agents spécialisés collaborent sur des **preuves réelles** : un agent d'analyse comportementale inspecte des séquences d'activité, des agents de collecte interrogent des systèmes externes, un agent de raisonnement synthétise une décision **auditable**.
- **[VÉRIFIÉ]** Jeu de données de workflow SOC **fin** : traces de triage au niveau processus sur **10+ scénarios réels** ; comparaison annoncée contre des LLM **mono-agents**, avec réduction des faux positifs et meilleure qualité d'investigation revendiquées *par les auteurs*.
- **[NON VÉRIFIÉ]** Disponibilité publique du code et du jeu de données ; licence.
- **Limites** : évaluation contre un seul type de baseline (mono-agent) ; scénarios « réels » d'entreprise difficilement redistribuables ; gains auto-rapportés.
- **Pertinence SENTINEL-X** : la « vérification indépendante » et la séparation de rôles que tu envisages **existent déjà ici** → ne pas les revendiquer comme nouvelles.

#### AIDA + Alert-Bench — *From Investigation Failures to Reliable SOC Agents* (arXiv:2610.10608, ~oct. 2026)

- **[VÉRIFIÉ]** Étude systématique de **5 approches de raisonnement LLM** pour le triage interactif.
- **[VÉRIFIÉ]** **Alert-Bench** : benchmark interactif qui **rejoue de la télémétrie d'entreprise dans un SIEM vivant** et impose à chaque système de **récupérer des preuves**. Construit à partir de la télémétrie **AIT-LDSv2** (Landauer et al., Zenodo) avec la vérité-terrain par événement d'**AIT-ADS**. *Les datasets AIT sont publics mais sous CC BY-NC-SA 4.0 — non commercial (voir I.3).*
- **[VÉRIFIÉ — chiffres annoncés par les auteurs, non reproduits indépendamment]** Échelle : **1 247 alertes** (unité : alertes du scénario multi-étapes retenu pour Alert-Bench) ; **toutes** les approches évaluées ont manqué **≥ 40,4 %** des alertes liées à l'attaque (unité : % d'alertes d'attaque non escaladées). Constats : les alertes d'attaque sont davantage rejetées quand les recherches ne renvoient rien ; un rejet ne reçoit pas une investigation plus poussée qu'une escalade.
- **[VÉRIFIÉ]** **AIDA** : architecture multi-agents imposant une **décision proposée explicite** puis une **contestation indépendante** et une **adjudication séparée**, avec un **registre d'investigation en ajout-seul** (append-only).
- **Limites** : un seul scénario multi-étapes rapporté ; benchmark centré triage tier-1, pas investigation complète multi-sources ; **[NON VÉRIFIÉ]** disponibilité publique du harnais Alert-Bench / du code AIDA (préprint — à confirmer).
- **Pertinence SENTINEL-X** : **très forte**. (1) Alert-Bench repose sur les datasets **AIT** (publics) → réutilisables par toi. (2) Le piège « charge d'investigation vs faux négatifs » est documenté → à intégrer dans ton protocole. (3) Le mécanisme « proposer → contester → adjuger » recouvre ton idée de vérification indépendante → non original.

#### Cognitive SOC — *Evidence-Backed Narrative Generation ... Multi-Agent LLM Architecture* (Sheikhi, Kostakos, Lovén — IEEE BigData 2025, DOI 10.1109/BigData66926.2025.11401968)

- **[VÉRIFIÉ]** Existence, auteurs, venue (IEEE Int. Conf. on Big Data 2025, p. 7027-7036). Thème : **génération de récits adossés aux preuves** par **système multi-agents**, avec **attribution de preuves**, **MITRE ATT&CK** et **atténuation des hallucinations**.
- **[NON VÉRIFIÉ]** Aucune métrique chiffrée, aucun jeu de données, aucune disponibilité de code confirmés (article IEEE sous péage ; une version auto-archivée existe — urn.fi/URN:NBN:fi:oulu-202603122131 — à consulter pour confirmation). **Ne lui attribuer aucun résultat quantitatif.**
- **Note terminologique** : « Cognitive SOC » est aussi un **terme générique** employé par d'autres travaux (p. ex. un cadre « Human-AI Collaboration / Trusted Autonomy », arXiv:2505.23397 ; un ancien « NGC2SOC »). Ne pas confondre le concept générique et le papier précis ci-dessus.

#### SecAlertBench

- **[NON VÉRIFIÉ]** Aucun benchmark nommé exactement « SecAlertBench » n'a pu être trouvé. Candidats probables de confusion : **Alert-Bench** (ci-dessus), **SALAD-SOC**, **SecBench** (QA cyber), **SIABench** (alerte + artefact PCAP). **À confirmer** : si tu as une référence précise (lien/DOI), transmets-la ; sinon ne pas la citer.

#### RAG for Security Incident Analysis (arXiv:2603.18196)

- **[VÉRIFIÉ]** Système **RAG** qui exécute des **requêtes ciblées** sur les logs, **mappe vers MITRE ATT&CK**, et génère des rapports interprétables ; se positionne sur l'**analyse d'incident de bout en bout** (pas seulement le triage/résumé).
- **[VÉRIFIÉ]** Évalué sur **8 configurations de LLM**, scénarios **malware** et **Active Directory** ; constats : sans RAG, les baselines **manquent toute l'infrastructure d'attaque** ; une **quasi-équivalence** est rapportée entre DeepSeek V3 (~89 %) et Claude Sonnet 4.
- **Pertinence** : **pré-répond en partie** à ta comparaison « LLM seul vs LLM+RAG ». Ton apport ne peut donc pas être « montrer que le RAG aide » (déjà montré) mais la **rigueur/reproductibilité/robustesse** de la mesure.

#### Autres travaux utiles (brièvement, [VÉRIFIÉ] pour l'existence)

- **REFINE** (arXiv:2609.32516) : cadre d'« évolution résiliente » pour le triage en **SOC industriel réel**, 4 scénarios sur 4 phases ATT&CK ; souligne que le raisonnement LLM générique ne reproduit pas le comportement de triage propre à une organisation.
- **« LLMs in the SOC »** (Singh et al., arXiv:2508.18947) : étude longitudinale de **3 090 requêtes, 45 analystes, 10 mois** ; conclusion : les LLM sont des **aides cognitives qui augmentent et ne remplacent pas** l'expertise.
- **Survey** « AI-Driven Security Alert Screening... » (arXiv:2605.08316) : inventaire de **22 datasets/benchmarks** ; identifie explicitement le **trou d'évaluation** : aucun benchmark ne mesure directement, ensemble, l'exactitude de triage sur de **vraies** alertes, la vitesse d'investigation, le **taux d'hallucination** et la **robustesse aux injections**.

### I.3 Jeux de données et benchmarks — séparation stricte

**I.3.a — Jeux de données publiquement disponibles (disponibilité confirmée)**


| Dataset                               | Source primaire                                                                                                   | Contenu (unité mesurée)                                                                                                                        | Licence (vérifiée)                                          | Provenance du chiffre                                                                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Microsoft GUIDE                       | Freitas et al., arXiv:2407.09017 (DOI 10.1145/3701716.3715209) ; Kaggle                                           | ~1 M**incidents** avec label de triage client (TP/BP/FP) ; 1,6 M alertes ; >13 M preuves ; 6,1 k orgs ; 441 techniques ATT&CK ; fenêtre ~2 sem. | **CDLA-Permissive-2.0** (permissive)                          | Annoncé par les auteurs ; non reproduit ici                                                                                                      |
| AIT-LDSv2                             | Landauer et al., Zenodo DOI 10.5281/zenodo.5789064 (v2.1 : 10.5281/zenodo.19483937)                               | Logs synthétiques, 8 bancs d'essai, logs système + trafic réseau, attaque multi-étapes                                                       | **CC BY-NC-SA 4.0** (non commercial, partage à l'identique)  | Descriptif auteurs                                                                                                                                |
| AIT-ADS                               | Landauer et al., CSET 2024 (DOI 10.1145/3675741.3675748) ; Zenodo record/8263181 ; code`ait-aecid/alert-data-set` | **> 2,6 M alertes** (unité : alertes générées) ; 93 signatures, via Suricata/Wazuh/AMiner sur AIT-LDSv2                                      | **CC BY-NC-SA 4.0**                                           | Annoncé par les auteurs.*Autre mesure, autre équipe* : PACT (arXiv:2605.22324) utilise un flux AIT-ADS de 587 943 alertes, 0,99 % malveillantes |
| CIC-IDS2017 / UNSW-NB15               | UNB / UNSW                                                                                                        | Flux réseau étiquetés                                                                                                                         | **À vérifier par dataset** (conditions d'usage académique) | Usage courant                                                                                                                                     |
| MITRE ATT&CK / Sigma / CISA KEV / NVD | Sources officielles                                                                                               | Techniques, règles, vulnérabilités                                                                                                            | Variables par source (à vérifier et**versionner**)          | —                                                                                                                                                |

**I.3.b — Code, infrastructures de benchmark et licences restant à vérifier (NON confirmés)**

- **Alert-Bench** (harnais interactif d'AIDA) : disponibilité du harnais/code **[NON VÉRIFIÉ]**. Les *données sous-jacentes* (AIT) sont publiques ; le *harnais* ne l'est pas (confirmé).
- **CORTEX** : code + dataset de traces SOC **[NON VÉRIFIÉ]**.
- **Cognitive SOC** : code **[NON VÉRIFIÉ]** (IEEE sous péage).
- **RAG for Security Incident Analysis** (arXiv:2603.18196) : disponibilité code/données d'éval **[NON VÉRIFIÉ]**.
- **SALAD-SOC** : dérivé d'UNSW/CICIDS ; **pas de DOI archivé** signalé par la survey → disponibilité/licence **à vérifier**.
- **Benchmark « AI SOC » (Simbian)** : non public (billet vendeur ; ~100 scénarios, meilleurs modèles 61-67 % en mai 2025 — auto-rapporté, non reproductible).
- **Contrainte licence dataset → licence dépôt** : AIT étant **NC/ShareAlike**, tout artefact d'évaluation dérivé d'AIT hérite de contraintes **non commerciales** → **un pipeline d'évaluation reposant sur AIT ne peut pas être présenté comme librement redistribuable sans restriction**. Impact direct sur D5 (licence du dépôt).

### I.4 Projets open source (existence [VÉRIFIÉ] ; capacités auto-déclarées)


| Projet                               | Description auto-déclarée                                                                                                                             | Licence        | Remarque                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ----------------------------------- |
| `nuk3s/soc-ai`                       | Triage LLM auto-hébergé pour alertes Security Onion ; tire les événements liés, intel local, runbook                                               | Apache 2.0     | Release 1.0 (juin 2026) ; LLM local |
| `ronitspatil/aegis-soc-triage`       | Agent de triage LangGraph ; enrichissement parallèle ; clôture ou brouillon de ticket pour**approbation humaine** ; agent outil pour logs historiques | MIT            | Proche de ta cible fonctionnelle    |
| `avigupta2194/agentic-soc-assistant` | LangGraph + Gemini ;**RAG MITRE ATT&CK** (ChromaDB, 690+ techniques, seuil de pertinence) ; extraction IOC ; rapport structuré                         | (à vérifier) | Démonstrateur mono-alerte          |
| `waitesgithub`/`zhadyz/AI_SOC`       | Multi-agents ; Foundation-Sec-8B ; Wazuh ; TheHive ; RAG MITRE/CVE/runbooks ; corrélation ; orchestrateur de réponse                                  | (à vérifier) | « Research implementation »       |
| `Vigil-SOC/vigil`                    | « Open source AI SOC » ; tourne sur ton propre LLM, local ou distant ; MCP                                                                            | Apache 2.0     | Actif (oct. 2026)                   |
| `FunnyWolf/agentic-soc-platform`     | Plateforme SOC agentique open source ; Splunk/ELK ; playbooks ; convergence de cas                                                                      | (à vérifier) | Actif                               |
| `bluesaphire76/sovereign-ai-soc`     | Local-first ; Wazuh, Suricata ; incidents « correlation-first » ; HITL                                                                                | (à vérifier) | Actif                               |

### I.5 Ce que l'état de l'art fait déjà vs ce qui manque

**Déjà largement couvert (donc non différenciant) :**

- Triage/résumé d'alerte par LLM + RAG MITRE/CTI, sortie structurée, mapping ATT&CK.
- Architecture **multi-agents** avec séparation de rôles et **vérification/contestation indépendante** (CORTEX, AIDA).
- Génération de récits **adossés aux preuves** avec atténuation d'hallucinations (Cognitive SOC).
- Investigation RAG de bout en bout, approbation humaine, auto-hébergement, LLM local (nombreux dépôts).

**Faible ou absent (fenêtre de différenciation) — [HYPOTHÈSE] :**

1. **Évaluation reproductible, standardisée et ouverte** combinant *dans un même harnais* : qualité de triage, qualité de retrieval, **groundedness/exactitude des citations**, qualité d'investigation, **robustesse sécurité** et **coût**. Les surveys constatent ce trou.
2. **Évaluation sérieuse de la robustesse** (injection indirecte via logs/documents, abus d'outils, RAG poisoning) **mesurée**, pas seulement affirmée.
3. **Honnêteté expérimentale** : publier limites et résultats négatifs ; la plupart des dépôts open source sont des démonstrateurs sans protocole d'évaluation.

### I.6 Implication directe pour le positionnement

La contribution défendable de SENTINEL-X **n'est pas** l'architecture d'agents ni « RAG + outils + vérification » (état de l'art 2025-2026). Elle peut être, **[HYPOTHÈSE] à valider après une revue formelle** : *une plateforme SOC d'investigation open source dont l'élément distinctif est un dispositif d'évaluation et de robustesse reproductible et réutilisable*, appliqué sur des données publiques avec provenance et limites documentées. La plateforme reste le produit ; l'évaluation/robustesse est l'angle.

---

## PARTIE II — CONCEPTION DE RÉFÉRENCE

### 1. Positionnement et valeur propre

- **[DÉCISION]** SENTINEL-X est une **plateforme SOC d'investigation open source**, auto-hébergeable, qui transforme des alertes et leurs événements en **investigations structurées, tracées et vérifiables** assistant la décision humaine.
- **[DÉCISION]** La GenAI/NLP/RAG/agents contrôlés font partie de son **identité technique** et montent en capacité par niveaux validés.
- **[HYPOTHÈSE]** Valeur propre = **investigation adossée aux preuves + dispositif d'évaluation/robustesse de première classe**, reproductible sur données publiques. À confirmer par revue formelle de l'existant (Partie III, D1).
- **Ce que SENTINEL-X n'est pas** : ni SIEM complet, ni wrapper LLM, ni simple détecteur ML, ni simple benchmark (le benchmark est *un composant*, pas le produit).

### 2. Problématique centrale et utilisateurs

- **Problématique [DÉCISION]** : *Comment concevoir une plateforme d'investigation SOC assistée par IA (NLP, RAG, agents à permissions limitées) qui contextualise des alertes, mène des vérifications fondées sur des outils en lecture seule, et produit des conclusions vérifiables et traçables — tout en maîtrisant les hallucinations, les données adversariales et les actions non autorisées — et dont chaque apport IA est **mesuré** contre des baselines ?*
- **Utilisateurs visés** :
  - *Primaire* : analyste SOC tier-1/tier-2 (triage, investigation assistée).
  - *Secondaire* : ingénieur détection / threat-intel (enrichissement, règles).
  - *Tertiaire* : chercheur/étudiant (harnais d'évaluation reproductible).
  - *Non visé pour l'instant* : réponse automatique en production, intégration SIEM d'entreprise large.

### 3. Les deux composantes

**Composante A — Plateforme SOC intelligente (le produit)**
Ingestion/normalisation d'alertes → score de priorité **explicable** → enrichissement (ATT&CK, Sigma, KEV, NVD) → investigation assistée (NLP, RAG, agents outillés en lecture seule) → **rapport structuré** séparant faits / inférences / hypothèses / inconnues / recommandations → provenance + journal d'audit. Approbation humaine pour toute action sensible (proposition ≠ exécution).

**Composante B — Dispositif d'évaluation & de sécurité (la différenciation)**
Harnais reproductible mesurant chaque capacité IA (triage, retrieval, groundedness, investigation, robustesse, coût) sur jeux publics + scénarios synthétiques contrôlés indépendamment ; batterie d'attaques (injection indirecte, abus d'outils, RAG poisoning) avec taux mesurés ; traçabilité complète (prompts versionnés, modèle figé, seeds).

> **[DÉCISION]** B est **de première classe**, pas un ajout final : chaque capacité de A ne « passe » qu'avec sa mesure dans B.

### 4. Capacités IA successives (niveaux de maturité)

Progression par niveaux, **sans durée**. Chaque niveau ne s'ouvre qu'une fois le précédent *accepté* (critères en §10).

- **N0 — Socle reproductible** : schéma d'alerte/événement, import de données documentées, validation, recherche documentaire basique, **baseline de triage déterministe**, tests. *(Pas d'IA générative encore.)*
- **N1 — Compréhension des alertes (NLP)** : extraction d'entités/IOC, normalisation, résumé d'alerte, explication des champs, détection d'informations manquantes. Sorties **structurées**, erreurs mesurées, renvoi aux données sources.
- **N2 — RAG contrôlé** : index de connaissances versionné, récupération de passages, **citations**, filtres de pertinence, réponses limitées aux éléments retrouvés + « preuve insuffisante » autorisé.
- **N3 — Investigation par outils** : orchestrateur choisissant parmi des **outils autorisés en lecture seule**, interrogeant événements/connaissances, construisant une chronologie ; chaque action **autorisée, journalisée, fondée sur un résultat réel**.
- **N4 — Workflows multi-étapes + vérification indépendante** : planification, réévaluation après résultats, gestion des inconnues, reprise sur erreur, **challenge indépendant** avant clôture (inspiré d'AIDA — **non original**, assumé). Démontrer un gain sur scénarios de référence vs *LLM seul* et *LLM+RAG*.
- **N5 — Intelligence enrichie** : corrélation multi-alertes, graphe de relations, mémoire d'investigation contrôlée, rôles multiples — **chaque extension doit améliorer une métrique sans dégrader sécurité/repro/coût**.

### 5. Datasets par capacité, licences, limites

**Distinction clé : triage simple ≠ investigation multi-étapes.**


| Capacité                            | Datasets candidats                                                                 | Ce qu'ils permettent                                      | Limite                                                       | Licence (à vérifier)                                                |
| ------------------------------------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------- |
| Triage (classification/priorisation) | Microsoft GUIDE ; SALAD-SOC ; CIC-IDS2017 ; UNSW-NB15                              | Baselines de triage/classement, métriques déséquilibre | Pas d'investigation ; biais/déséquilibre ; dérivés       | GUIDE : CDLA-2.0 ; autres : à vérifier                              |
| RAG / connaissances                  | MITRE ATT&CK ; Sigma ; CISA KEV ; NVD                                              | Enrichissement, mapping, citations                        | Versionnement obligatoire ; qualité variable                | Variables par source                                                  |
| Investigation multi-étapes          | **AIT-LDSv2 + AIT-ADS** (base d'Alert-Bench) ; scénarios **synthétiques** maison | Chronologie, preuves, vérité-terrain événementielle   | Environnement de labo ≠ SOC réel ;**AIT = non commercial** | AIT :**CC BY-NC-SA 4.0** ; synthétiques maison : licence à définir |
| Robustesse / sécurité              | Scénarios synthétiques adversariaux maison (injections dans logs/docs)           | Mesure injection/abus d'outils/poisoning                  | Risque de**circularité** (cf. ci-dessous)                   | Produit interne                                                       |

**Garde-fous données [DÉCISION]** :

- Séparer **corpus RAG** et **réponses de référence** d'évaluation (anti-fuite).
- Séparation stricte dev / test ; grille d'évaluation figée **avant** l'analyse.
- Les scénarios synthétiques sont **révisés indépendamment** (règles ou relecture) pour éviter d'évaluer un modèle sur ses propres conventions — **la circularité reste le risque n°1** et impose de **toujours** croiser avec des données publiques non générées par toi (p. ex. AIT via Alert-Bench).
- Ne publier que le redistribuable ; sinon fournir scripts d'acquisition + manifestes + licences.

### 6. Expériences et baselines

Baselines **minimales** (reprises de l'état de l'art pour comparabilité) :

- **Baseline A** : règles / score déterministe, sans LLM.
- **Baseline B** : LLM seul (alerte + contexte disponible).
- **Baseline C** : LLM + RAG.
- **SENTINEL-X** : RAG + outils autorisés + vérification + rapport structuré.


| Dimension         | Métriques                                                                                                        | Note méthodo                                                                |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Triage            | Precision, Recall, F1, PR-AUC ; qualité du classement                                                            | PR-AUC prioritaire (déséquilibre)                                          |
| RAG               | Recall@k, MRR, nDCG                                                                                               | Jeu de questions à documents pertinents de référence                      |
| Preuves/citations | % d'affirmations liées à une preuve pertinente ; exactitude des citations ; taux d'affirmations non supportées | « Groundedness »                                                           |
| Investigation     | Exactitude vs scénario de référence ; preuves trouvées ; hypothèses erronées ; reconnaissance des inconnues | **Charge d'investigation à lire conjointement au FNR** (leçon Alert-Bench) |
| Sécurité        | Résistance aux injections (logs/docs) ; % d'actions interdites bloquées ; respect des permissions               | Batterie d'attaques variée, taux mesuré                                    |
| Efficacité       | Latence, nб d'appels modèle/outils,**coût/€ estimé par investigation**, reproductibilité                    | Budget coût fixé a priori → hypothèse falsifiable                        |

**[DÉCISION]** Aucune capacité IA n'est « acquise » sans mesure vs au moins une baseline adaptée.

### 7. Architecture logicielle et choix technologiques

**[DÉCISION] Monolithe modulaire** à interfaces explicites (pas de microservices au départ).


| Domaine             | Choix initial                                                                                                                                  | Justification                                                                                       | Évolution conditionnelle                                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Langage / API       | Python, FastAPI, Pydantic                                                                                                                      | Standard, typage, contrats de données                                                              | Contrats plus stricts si intégrations ↑                                                                                                         |
| Stockage            | **PostgreSQL + pgvector** (alertes, scénarios, audit **et** vecteurs dans le même moteur)                                                    | **Un seul composant** couvre relationnel + vectoriel → pas de service supplémentaire à déployer | **Qdrant** séparé seulement si hybride avancé / filtres / échelle le justifient (mesuré)                                                     |
| Recherche/RAG       | Récupération vectorielle via pgvector + BM25/texte intégral Postgres                                                                        | Reste dans le composant existant ; hybride simple possible sans brique externe                      | Reranking / filtres de métadonnées avancés / Qdrant sur besoin mesuré                                                                         |
| Modèles IA         | Abstraction`LLMProvider` + baseline déterministe ; **v1 = un fournisseur API hébergé** (ex. Claude), **déploiement local NON obligatoire** | Remplaçabilité, repro, time-to-first-result ; le local n'est pas un prérequis de la v1           | **Option locale (Ollama/vLLM) supportée, pas imposée** ; à activer pour souveraineté / reproductibilité hors-ligne / comparaison de modèles |
| Orchestration agent | **Machine à états explicite** maison, minimale                                                                                               | Lisibilité, traçabilité, pas de lock-in framework                                                | Adopter LangGraph*seulement si* la complexité le justifie (décision ouverte)                                                                    |
| Triage/ML           | Règles + scikit-learn (baselines)                                                                                                             | Baselines avant modèles avancés                                                                   | Classifieurs ajoutés si labels/gains le permettent                                                                                               |
| Interface           | Démo légère (API + UI minimale)                                                                                                             | Démontrabilité sans surcoût                                                                      | Dashboard d'investigation plus tard                                                                                                               |
| Reproductibilité   | pytest, données d'exemple, Docker Compose, docs                                                                                               | Socle repro dès N0                                                                                 | CI, suivi d'expériences, pipelines d'éval                                                                                                       |

### 8. Sécurité, traçabilité, reproductibilité, anti-injection

- **Données non fiables [DÉCISION]** : tout événement/log/document/sortie d'outil est traité comme potentiellement hostile ; ne peut jamais remplacer les instructions système. Séparation stricte *instructions* / *données* dans les prompts.
- **Permissions outils** : liste explicite, **lecture seule au départ**, pas d'accès shell, pas de scan réel, pas de remédiation auto ; validation des arguments, limitation des données exposées, journalisation appels+résultats, arrêt sûr en cas d'incertitude.
- **Proposition ≠ exécution** : toute action sensible passe par proposition → politique → validation → autorisation → (humain). Le prototype doit démontrer qu'il **sait refuser/s'abstenir**.
- **Traçabilité IA** : pour chaque investigation, stocker modèle + version, version de prompt/template, documents récupérés, appels d'outils + résultats, sortie structurée finale, horodatage, ID incident.
- **Reproductibilité LLM [DÉCISION]** : modèle **figé** par expérience, température/seed consignés, **prompts versionnés** hors code, journalisation complète ; sans cela, aucun résultat n'est rejouable.
- **Secrets** : `.env` jamais commité, `.env.example`, scanners (Gitleaks, etc.) ; ne pas envoyer de secrets/données sensibles à un fournisseur externe.
- **Anti-injection mesuré** : batterie d'attaques (injection indirecte dans logs/docs, abus d'outils, RAG poisoning) → **taux de blocage mesuré**, pas affirmé. Un éventuel classifieur d'injection doit être **évalué**, pas supposé fiable.

### 9. Conserver / reformuler / reporter / abandonner (vs spec initiale)


| Élément (spec/PDF initiaux)                               | Décision                       | Justification                                                                                             |
| ----------------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Schéma d'alerte/événement normalisé                     | **Conserver**                   | Socle N0                                                                                                  |
| Baseline de triage déterministe                            | **Conserver**                   | Baseline A obligatoire                                                                                    |
| RAG cyber + provenance + « preuve insuffisante »          | **Conserver (cœur)**           | Identité ; déjà bien conçu                                                                            |
| Investigation LLM à outils lecture seule                   | **Conserver (cœur)**           | Produit                                                                                                   |
| Policy engine + approbation humaine + audit                 | **Conserver**                   | Différenciation sécurité                                                                               |
| Sorties structurées, prompts versionnés, traçabilité IA | **Conserver**                   | Repro/sécurité                                                                                          |
| Vérification/challenge indépendant                        | **Conserver mais reformuler**   | Utile, mais**non original** (AIDA/CORTEX) → ne pas revendiquer                                           |
| Datasets réseau (CIC-IDS/UNSW)                             | **Reformuler**                  | Baseline triage uniquement ; pas investigation                                                            |
| UEBA / anomalie comportementale ML                          | **Reporter**                    | Source de signaux optionnelle, plus le cœur                                                              |
| Corrélation multi-alertes / graphe d'attaque               | **Reporter (N5)**               | Après investigation de base validée                                                                     |
| Elastic/Kibana, Airflow, n8n, MLflow, DVC, Prometheus       | **Reporter (conditionnel)**     | Réintroduction sur besoin mesuré (ADR)                                                                  |
| Axe HPC / Slurm / Jean Zay                                  | **Abandonner du cœur**         | Décision actée ; éventuelle expérience de scalabilité*découplée* plus tard, sans dépendance stage |
| Neo4j                                                       | **Abandonner (pour l'instant)** | NetworkX si besoin ; pas avant cas d'usage                                                                |
| Évaluation humaine avec participants                       | **Reporter**                    | Coût éthique/RGPD disproportionné au stade actuel                                                      |
| Réponse automatique (niveaux ≥3)                          | **Reporter**                    | Hors périmètre initial ; lecture seule d'abord                                                          |

### 10. Critères d'acceptation par niveau (portes de passage)


| Niveau                     | Le niveau est « accepté » si…                                                                                                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **N0**                     | Import reproductible ; schéma validé ; baseline de triage déterministe mesurée ; jeux de test + labels documentés ; tests verts ; Docker Compose up fonctionne proprement.                               |
| **N1**                     | Sorties NLP**structurées** ; erreurs d'extraction **mesurées** (précision/rappel entités/IOC) ; chaque élément extrait **renvoie à sa source** ; régression testée.                                  |
| **N2**                     | Qualité de retrieval mesurée (Recall@k/MRR/nDCG) ;**% d'affirmations réellement supportées** mesuré ; « preuve insuffisante » émis quand il le faut ; citations vérifiables.                         |
| **N3**                     | Chaque action d'outil**autorisée + journalisée + fondée sur un résultat réel** ; permissions **testées** (tentatives interdites bloquées) ; chronologie reconstruite sur ≥1 scénario de référence. |
| **N4**                     | **Amélioration démontrée** vs *LLM seul* et *LLM+RAG* sur scénarios figés (investigation + groundedness) **sans** dégrader sécurité/coût ; charge d'investigation lue avec le FNR.                   |
| **N5**                     | Chaque extension (corrélation/graphe/mémoire) répond à un**besoin constaté** et **améliore une métrique** sans régression de sécurité/repro/coût.                                                  |
| **Transversal (toujours)** | Robustesse : taux d'actions interdites bloquées et résistance aux injections**mesurés** et non en régression ; repro : modèle figé + prompts versionnés + seeds consignés.                            |

---

## PARTIE III — DÉCISIONS OUVERTES


| #      | Décision ouverte                               | Options                                                                        | Recommandation (justifiée)                                                                                                                                                                                                                                      |
| ------ | ----------------------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **D1** | Formulation exacte de la contribution originale | (a) harnais d'éval ouvert ; (b) robustesse sécurité mesurée ; (c) les deux | **Faire une revue formelle (docs/research/state-of-the-art.md) AVANT de trancher.** Candidat fort : (c), car c'est le trou identifié par les surveys. Ne rien revendiquer avant.                                                                                |
| **D2** | Framework d'orchestration d'agents              | Machine à états maison vs LangGraph                                          | Commencer**maison** (lisibilité, traçabilité, pas de lock-in) ; réévaluer à N4 si la complexité l'exige.                                                                                                                                                  |
| **D3** | Moteur vectoriel initial                        | pgvector (dans Postgres) vs Qdrant d'emblée                                   | **pgvector d'abord** (zéro composant en plus) ; Qdrant seulement si hybride/filtres/échelle *mesurés* nécessaires.                                                                                                                                           |
| **D4** | Fournisseur LLM (v1)                            | API hébergée vs local obligatoire                                            | **API hébergée derrière `LLMProvider` en v1 ; local (Ollama/vLLM) supporté mais NON obligatoire.** Versions figées pour la reproductibilité. Le local devient utile pour souveraineté / repro hors-ligne / comparaison de modèles, pas comme prérequis. |
| **D5** | Licence du dépôt                              | MIT/Apache-2.0 vs AGPL                                                         | **[OUVERT]** dépend (a) des dépendances liées et (b) des **licences dataset** : l'usage d'AIT (CC BY-NC-SA 4.0, **non commercial**) contraint la redistribution des artefacts d'évaluation dérivés. À trancher dans un ADR licences.                      |
| **D6** | Source « SecAlertBench »                      | —                                                                             |                                                                                                                                                                                                                                                                  |
| **D7** | Rôle exact des datasets réseau (CIC-IDS/UNSW) | Triage seul vs plus                                                            | Les cantonner au**triage/baseline** ; l'investigation s'appuie sur AIT + synthétique.                                                                                                                                                                           |

---

## PARTIE IV — Sources (avec statut)

- CORTEX — *Collaborative LLM Agents for High-Stakes Alert Triage* (2025). researchgate.net/publication/396094185 — [VÉRIFIÉ existence/contenu ; dispo code NON VÉRIFIÉE]
- AIDA + Alert-Bench — *From Investigation Failures to Reliable SOC Agents*, arXiv:2610.10608 — [VÉRIFIÉ]
- Cognitive SOC — Sheikhi, Kostakos, Lovén, IEEE BigData 2025, DOI 10.1109/BigData66926.2025.11401968 — [VÉRIFIÉ existence/venue/thème ; détails NON VÉRIFIÉS]
- RAG for Security Incident Analysis — arXiv:2603.18196 — [VÉRIFIÉ]
- REFINE — arXiv:2609.32516 — [VÉRIFIÉ existence]
- LLMs in the SOC (Singh et al.) — arXiv:2508.18947 — [VÉRIFIÉ]
- Survey alert screening / fatigue — arXiv:2605.08316 — [VÉRIFIÉ]
- Unified Framework Human-AI / Trusted Autonomy — arXiv:2505.23397 — [VÉRIFIÉ existence]
- Elastic licensing (AGPLv3 + ELv2 + SSPL depuis 08/2024) — elastic.co/pricing/faq/licensing — [VÉRIFIÉ]
- n8n Sustainable Use License (fair-code, non-OSI) — docs.n8n.io/sustainable-use-license — [VÉRIFIÉ]
- Projets open source : github.com/nuk3s/soc-ai ; ronitspatil/aegis-soc-triage ; avigupta2194/agentic-soc-assistant ; waitesgithub(zhadyz)/AI_SOC ; Vigil-SOC/vigil ; FunnyWolf/agentic-soc-platform — [VÉRIFIÉ existence ; capacités auto-déclarées]
- **SecAlertBench** — **[introuvable]**

---

## PARTIE V — Correspondance avec le dépôt

- Ce fichier → `docs/architecture/CONCEPTION_DE_REFERENCE.md` (source de vérité de conception).
- Partie I → extraire vers `docs/research/state-of-the-art.md` (à enrichir en revue formelle, D1).
- §6 + §10 → `docs/EVALUATION.md` (protocole + portes).
- §8 → `docs/THREAT_MODEL.md` + `SECURITY.md`.
- Décisions D1-D7 → `docs/decisions/ADR-0xx-*.md`.
- §9 → `CHANGELOG.md` / `PROJECT_STATE.md`.
