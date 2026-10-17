# État de l'art — Investigation SOC assistée par IA (LLM / RAG / agents)

- **Statut** : revue de référence (v0.2). Base de la décision D1 (formulation de la contribution).
- **Date** : 2026-10-16
- **Portée** : triage et investigation d'alertes SOC par LLM, RAG cybersécurité, agents outillés, benchmarks et datasets associés, projets open source.

**Documents liés :** conception → `docs/architecture/CONCEPTION_DE_REFERENCE.md` · protocole → `docs/EVALUATION.md`.

- **Discipline de preuve** : **[VÉRIFIÉ]** (source citée) · **[AUTEURS]** (chiffre annoncé par les auteurs, non reproduit indépendamment ici) · **[NON VÉRIFIÉ]** (introuvable/non confirmé) · **[À CONFIRMER]**.

> **Conclusion portée en tête** : à la date de cette revue, « RAG + outils contrôlés + vérification indépendante + rapport tracé » **constitue l'état de l'art 2025-2026 et n'est pas une contribution originale**. Ce document cadre où une contribution défendable reste possible ([HYPOTHÈSE], non établie) : un **dispositif d'évaluation et de robustesse reproductible et ouvert**. Rien n'est revendiqué comme original ici.

---

## 1. Méthode de revue

Recherche web ciblée (octobre 2026) sur les systèmes nommés + travaux adjacents + datasets + dépôts. Pour chaque élément : nature de la contribution, ce qui est réellement implémenté/évalué, données, accessibilité publique, licence, limites, statut de vérification. **Aucun résultat n'a été reproduit indépendamment** dans le cadre de cette revue : tout chiffre est donc **[AUTEURS]** sauf mention contraire.

## 2. Tableau comparatif (synthèse)

| Système | Approche | Tâche | Données | Public ? | Vérif. indép. | Limite principale |
|---|---|---|---|---|---|---|
| CORTEX (2025) | Multi-agents, preuves réelles, décision auditable | Triage haute criticité | Traces SOC niveau processus, 10+ scénarios « réels » | Code/data **[NON VÉRIFIÉ]** | Non | Scénarios non redistribuables ; baseline unique |
| AIDA + Alert-Bench (arXiv:2610.10608) | Multi-agents : proposer → contester → adjuger ; registre append-only | Triage tier-1 + benchmark | Alert-Bench sur AIT-LDSv2/AIT-ADS | Données oui / harnais **[NON VÉRIFIÉ]** | Non | 1 scénario multi-étapes ; triage, pas investigation complète |
| Cognitive SOC (IEEE BigData 2025) | Multi-agents, récits adossés aux preuves, atténuation d'hallucinations | Rapport d'incident | **[NON VÉRIFIÉ]** | Code **[NON VÉRIFIÉ]** (péage) | Non | **Aucun chiffre vérifiable** |
| RAG for Security Incident Analysis (arXiv:2603.18196) | RAG + requêtes ciblées sur logs, mapping ATT&CK | Analyse d'incident de bout en bout | Scénarios malware + Active Directory | **[NON VÉRIFIÉ]** | Non | Démontre surtout l'utilité du RAG (déjà acquis) |
| Projets open source (§6) | Divers (agents, RAG MITRE, HITL) | Triage/investigation | Variables | Oui (dépôts) | Non | Évaluation rigoureuse quasi absente |

## 3. Travaux académiques — détail

### 3.1 CORTEX — *Collaborative LLM Agents for High-Stakes Alert Triage* (2025, préprint)
- **Nature** : architecture **multi-agents** collaborant sur **preuves réelles** (analyse comportementale, agents de collecte interrogeant des systèmes externes, agent de raisonnement) → **décision auditable**. **[VÉRIFIÉ]**
- **Données/éval** : traces de triage SOC **niveau processus**, **10+ scénarios réels** ; comparaison annoncée vs LLM **mono-agents** (réduction de faux positifs, meilleure qualité). **[AUTEURS]**
- **Accessibilité** : code/dataset **[NON VÉRIFIÉ]** ; licence inconnue. Auteurs exacts **[À CONFIRMER]**.
- **Limites** : baseline unique ; scénarios d'entreprise non redistribuables ; gains non reproduits.

### 3.2 AIDA + Alert-Bench — *From Investigation Failures to Reliable SOC Agents* (arXiv:2610.10608)
- **Nature** : (1) étude de **5 approches de raisonnement LLM** ; (2) **Alert-Bench**, benchmark interactif rejouant de la télémétrie dans un SIEM vivant, exigeant la **récupération de preuves** ; (3) **AIDA** : **proposer → contester (challenge indépendant) → adjuger**, **registre append-only**. **[VÉRIFIÉ]**
- **Données** : Alert-Bench **bâti sur AIT-LDSv2 + AIT-ADS** (publics ; §5). **[VÉRIFIÉ]**
- **Chiffres** : **1 247 alertes** (unité : alertes du scénario multi-étapes retenu) ; **toutes** les approches manquent **≥ 40,4 %** des alertes d'attaque (unité : % d'alertes d'attaque non escaladées). **[AUTEURS — non reproduit ici]**
- **Accessibilité** : harnais Alert-Bench / code AIDA **[NON VÉRIFIÉ]** (préprint).
- **Pertinence** : réutiliser les datasets AIT pour l'investigation ; intégrer la leçon « charge d'investigation ↔ FNR » ; **vérification indépendante déjà présente → non originale**.

### 3.3 Cognitive SOC — *Evidence-Backed Narrative Generation for Security Operations with Multi-Agent LLM Architecture*
- **Réf. [VÉRIFIÉ]** : Sheikhi, Saeid ; Kostakos, Panos ; Lovén, Lauri — **IEEE Int. Conf. on Big Data (BigData) 2025**, p. **7027-7036**, DOI **10.1109/BigData66926.2025.11401968**. Version auto-archivée annoncée : urn.fi/URN:NBN:fi:oulu-202603122131 (dépôt oulurepo).
- **Ce que la fiche institutionnelle expose [VÉRIFIÉ]** : titre, auteurs, venue, pagination, DOI, et **mots-clés/thèmes déclarés** — *security operations ; large language models ; multi-agent systems ; narrative generation ; evidence attribution ; threat intelligence ; MITRE ATT&CK ; hallucination mitigation*.
- **Statut de vérification des contenus [NON VÉRIFIÉ]** : la tentative d'accès au résumé complet et à la version auto-archivée **a échoué dans cette session** (article IEEE derrière péage ; PDF du dépôt non récupérable via les outils disponibles). En conséquence :
  - « récits adossés aux preuves », « attribution de preuves », « atténuation des hallucinations », « multi-agents » sont des **thèmes/méthode déclarés par les auteurs** (mots-clés), **pas des résultats mesurés ni vérifiés**.
  - **Aucune métrique, aucun dataset, aucune disponibilité de code ne sont confirmés.** **Ne lui attribuer aucun résultat quantitatif** tant que le texte intégral n'a pas été lu.
- **Note terminologique** : « Cognitive SOC » est aussi un **terme générique** (cf. cadre Human-AI/Trusted Autonomy, arXiv:2505.23397) — ne pas confondre le concept générique et ce papier précis.
- **À faire pour clore** : obtenir le texte intégral (IEEE Xplore ou PDF oulurepo) et remplacer les thèmes par les résultats réellement rapportés, en distinguant [AUTEURS] vs reproduction indépendante.

### 3.4 RAG for Security Incident Analysis (arXiv:2603.18196)
- **Nature** : **RAG** exécutant des **requêtes ciblées** sur les logs, **mapping ATT&CK**, rapports interprétables ; **analyse d'incident de bout en bout**. **[VÉRIFIÉ]**
- **Éval** : **8 configurations de LLM**, scénarios **malware** et **Active Directory** ; sans RAG, les baselines **manquent toute l'infrastructure d'attaque** ; **quasi-équivalence** DeepSeek V3 (~89 %) vs Claude Sonnet 4. **[AUTEURS]**
- **Accessibilité** : code/données d'éval **[NON VÉRIFIÉ]**.
- **Implication** : « le RAG aide » est **déjà démontré** → ne peut pas être la contribution de SENTINEL-X.

### 3.5 Travaux de contexte (existence [VÉRIFIÉ])
- **REFINE** (arXiv:2609.32516) — triage en SOC industriel réel, 4 scénarios/4 phases ATT&CK ; le raisonnement LLM générique ne reproduit pas le triage propre à une organisation.
- **« LLMs in the SOC »** (Singh et al., arXiv:2508.18947) — 3 090 requêtes, 45 analystes, 10 mois ; les LLM **augmentent** sans remplacer l'expertise. **[AUTEURS pour les chiffres]**
- **Survey** « AI-Driven Security Alert Screening... » (arXiv:2605.08316) — inventaire de **22 datasets/benchmarks** ; identifie le **trou d'évaluation** : aucun benchmark ne mesure ensemble triage sur vraies alertes + vitesse + hallucination + robustesse aux injections. **[VÉRIFIÉ]**

## 4. Lecture critique : acquis vs trou

**Acquis (non différenciant)** : triage/résumé LLM + RAG ATT&CK, sortie structurée, mapping ; multi-agents avec vérification/contestation indépendante (CORTEX, AIDA) ; récits adossés aux preuves (Cognitive SOC, *thème déclaré*) ; investigation RAG, HITL, auto-hébergement (dépôts open source).

**Trou (fenêtre, [HYPOTHÈSE] non établie)** :
1. **Évaluation ouverte, reproductible, standardisée** combinant *dans un même harnais* triage + retrieval + groundedness/citations + investigation + **robustesse sécurité** + **coût**.
2. **Robustesse mesurée** (injection indirecte via logs/docs, abus d'outils, RAG poisoning).
3. **Honnêteté expérimentale** (limites, résultats négatifs).

## 5. Datasets — disponibilité et licences

### 5.a Jeux publics confirmés
- **Microsoft GUIDE** — Freitas et al., arXiv:2407.09017 (DOI 10.1145/3701716.3715209) ; Kaggle. ~1 M **incidents** labellisés (triage TP/BP/FP), 1,6 M alertes, >13 M preuves, 6,1 k orgs, 441 techniques ATT&CK. **Licence données : CDLA-Permissive-2.0 (permissive).** [VÉRIFIÉ]
- **AIT-LDSv2** — Landauer et al., Zenodo DOI 10.5281/zenodo.5789064 (v2.1 : 10.5281/zenodo.19483937). **Licence données : CC BY-NC-SA 4.0** (attribution, non commercial, partage à l'identique). [VÉRIFIÉ]
- **AIT-ADS** — Landauer et al., CSET 2024 (DOI 10.1145/3675741.3675748) ; Zenodo record/8263181 ; code `ait-aecid/alert-data-set`. **> 2,6 M alertes [AUTEURS]** (PACT, arXiv:2605.22324, en utilise un flux de 587 943 alertes, 0,99 % malveillantes — autre mesure, autre équipe). **Licence données : CC BY-NC-SA 4.0.** [VÉRIFIÉ]

### 5.b À vérifier / non confirmés
Harnais **Alert-Bench** ; **SALAD-SOC** (dérivé UNSW/CICIDS, pas de DOI archivé signalé) ; licences exactes de **CIC-IDS2017 / UNSW-NB15** ; benchmark **Simbian** (non public, billet vendeur : ~100 scénarios, meilleurs modèles 61-67 % en mai 2025 — auto-rapporté).

### 5.c Licences : trois plans à ne pas confondre
La licence d'un jeu de **données** ne contamine pas automatiquement le **code**. Distinguer :

1. **Licence du code SENTINEL-X** — choisie par nous (p. ex. permissive), **indépendante** des licences de données. Du code qui *lit* AIT à l'exécution, sans **contenir ni redistribuer** de données AIT, n'est en principe pas une œuvre dérivée des données. **À confirmer juridiquement, non un avis juridique.**
2. **Licence des données** — AIT = **CC BY-NC-SA 4.0** : usage **non commercial**, **attribution**, et **partage à l'identique** de toute **adaptation des données**. GUIDE = **CDLA-Permissive-2.0** (pas de clause NC/SA).
3. **Licence des artefacts dérivés** — si nous **redistribuons** des données AIT transformées (alertes prétraitées, splits, extraits de logs, index RAG **contenant** du contenu AIT), cet artefact est une **adaptation** → il doit rester **CC BY-NC-SA 4.0** et **non commercial**. En revanche, des **scripts** de téléchargement/transformation qui **ne contiennent pas** de données AIT peuvent être sous licence permissive.

**Conditions de redistribution à vérifier avant publication (checklist, non exhaustive) :**
- Ne **pas** bundler AIT (ni dérivés contenant du contenu AIT) sous licence permissive.
- Marquer tout artefact d'évaluation **contenant** du contenu AIT comme CC BY-NC-SA 4.0 + mention NC.
- Fournir des **scripts d'acquisition** plutôt que redistribuer les données quand c'est possible.
- Vérifier séparément CIC-IDS2017 / UNSW-NB15 (conditions propres).
- Attribution requise pour AIT **et** GUIDE.
- Impact sur **D5** (licence du dépôt) : un dépôt permissif reste possible pour le **code** ; les **données/artefacts dérivés d'AIT** suivent CC BY-NC-SA et ne peuvent pas être présentés comme librement redistribuables sans restriction.

## 6. Projets open source (existence [VÉRIFIÉ] ; capacités **auto-déclarées**)

| Projet | Capacités auto-déclarées | Licence | Note |
|---|---|---|---|
| `nuk3s/soc-ai` | Triage LLM auto-hébergé (Security Onion) ; événements liés ; intel local ; runbook | Apache 2.0 | LLM local ; R1.0 (juin 2026) |
| `ronitspatil/aegis-soc-triage` | LangGraph ; enrichissement parallèle ; clôture ou ticket pour **approbation humaine** ; agent outil (logs historiques) | MIT | Proche de la cible fonctionnelle |
| `avigupta2194/agentic-soc-assistant` | LangGraph + Gemini ; RAG ATT&CK (ChromaDB, 690+ techniques) ; IOC ; rapport structuré | [À vérifier] | Démonstrateur mono-alerte |
| `zhadyz/AI_SOC` | Multi-agents ; Foundation-Sec-8B ; Wazuh ; TheHive ; RAG MITRE/CVE ; corrélation ; orchestrateur | [À vérifier] | « Research implementation » |
| `Vigil-SOC/vigil` | « Open source AI SOC » ; LLM local/distant ; MCP | Apache 2.0 | Actif |
| `FunnyWolf/agentic-soc-platform` | SOC agentique ; Splunk/ELK ; playbooks ; convergence de cas | [À vérifier] | Actif |
| `bluesaphire76/sovereign-ai-soc` | Local-first ; Wazuh/Suricata ; corrélation-first ; HITL | [À vérifier] | Actif |

**Constat** : terrain open source **encombré** côté fonctionnalités ; **évaluation reproductible sérieuse quasi absente** → cohérent avec le trou (§4). Maturité réelle à réexaminer au moment de construire.

## 7. Positionnement de SENTINEL-X (à valider, non établi)

Visée : *plateforme SOC d'investigation open source dont l'élément distinctif est un **dispositif d'évaluation + robustesse reproductible et réutilisable**, sur données publiques avec provenance/licences/limites documentées.* **[HYPOTHÈSE]** — à confirmer en complétant §9 **avant toute revendication** (D1).

## 8. Références (vérifiables)

- Freitas, Kalajdjieski, Gharib, McCann — *AI-Driven Guided Response for SOCs with Microsoft Copilot for Security*. arXiv:2407.09017 ; DOI 10.1145/3701716.3715209. (GUIDE)
- Tsegai, Kantchelian, Yao, Gao — *From Investigation Failures to Reliable SOC Agents...*. arXiv:2610.10608. (AIDA / Alert-Bench)
- Sheikhi, Kostakos, Lovén — *Cognitive SOC: Evidence-Backed Narrative Generation...*. IEEE BigData 2025, p. 7027-7036 ; DOI 10.1109/BigData66926.2025.11401968 ; auto-archive urn.fi/URN:NBN:fi:oulu-202603122131.
- *CORTEX: Collaborative LLM Agents for High-Stakes Alert Triage* (2025, préprint ; auteurs à confirmer).
- *Retrieval-Augmented LLMs for Security Incident Analysis*. arXiv:2603.18196.
- Singh et al. — *LLMs in the SOC...*. arXiv:2508.18947.
- *AI-Driven Security Alert Screening and Alert Fatigue Mitigation... Survey*. arXiv:2605.08316.
- *REFINE...*. arXiv:2609.32516.
- Landauer et al. — *AIT Log Data Set V2.x*. Zenodo DOI 10.5281/zenodo.5789064 ; v2.1 : 10.5281/zenodo.19483937 (CC BY-NC-SA 4.0).
- Landauer et al. — *Introducing a New Alert Data Set for Multi-Step Attack Analysis* (AIT-ADS). CSET 2024, DOI 10.1145/3675741.3675748 ; Zenodo record/8263181.
- *PACT: Reducing Alert Fatigue...*. arXiv:2605.22324 (mesures AIT-ADS tierces).

## 9. À compléter avant de clore D1

- **Cognitive SOC** : lire le texte intégral (IEEE Xplore / PDF oulurepo) et remplacer les thèmes par les résultats réellement rapportés.
- Confirmer auteurs/venue exacts de **CORTEX**.
- Vérifier la disponibilité publique des **harnais** (Alert-Bench) et **codes** (AIDA, Cognitive SOC, RAG-incident).
- Clarifier **« SecAlertBench »** (référence vérifiable ou retrait — D6).
- Vérifier licences exactes de **CIC-IDS2017 / UNSW-NB15** et statut de **SALAD-SOC**.
