# EXP-0001 — Baselines A/B/C sur la suite de scénarios de référence

Fiche d'expérience suivant le gabarit `docs/EVALUATION.md` §7. Elle **journalise un résultat** ; elle vit donc hors du protocole (qui, lui, reste sans résultat).


| Champ                               | Valeur                                                                                                                                                                                                                                                                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**                              | EXP-0001                                                                                                                                                                                                                                                                                                                 |
| **Date**                            | 2026-10-23                                                                                                                                                                                                                                                                                                               |
| **Nature**                          | Run**descriptif**du harness (smoke) sur la suite de référence.**PAS**une expérience confirmatoire préenregistrée : aucune sélection de métrique, aucun réglage de seuil, aucun ajustement a posteriori. À rapprocher de`EVALUATION.md`§5.1 (stats descriptives ≠ performance).                                |
| **Objectif**                        | Mesurer, de façon descriptive, si les baselines implémentées (A/B/C) atteignent la disposition de référence sur les 5 scénarios actuels, et si le RAG (C) change la disposition du stub par rapport à B.                                                                                                          |
| **Question**                        | Famille T (triage) uniquement : disposition prédite vs disposition de référence.                                                                                                                                                                                                                                      |
| **Dataset + version**               | `data/scenarios/*.json`(5 scénarios) : 3 synthétiques écrits à la main (`SC-AMBIGUOUS-001`,`SC-BRUTEFORCE-001`,`SC-INJECTION-001`) + 2 cas réels AIT-ADS (`fox-privesc-shadow`,`fox-dnsteal-dns-exfil`). AIT-ADS = CC BY 4.0, Zenodo 8263181. KB RAG =`data/knowledge/mitre_sample.json`version`sample-2026-10-22`. |
| **Vérité-terrain**                | Disposition d'un analyste de référence. Pour les synthétiques : fixée a priori à la conception. Pour les fox : disposition de référence informée par le`time_label`AIT-ADS (fenêtre temporelle),**non**un`event_label`certifié.                                                                                |
| **Modèle + version**               | Stub déterministe (`llm_provider=deterministic`,`llm_model=None`).`temperature=0.0`,`seed=7`—**sans effet**: le stub est déterministe par construction.                                                                                                                                                               |
| **Config d'ablation**               | A = triage déterministe (sans LLM) · B = stub sans RAG · C = stub + RAG. D/E non implémentés.                                                                                                                                                                                                                       |
| **Baseline**                        | A (triage) ; B et C comparés à A et entre eux.                                                                                                                                                                                                                                                                         |
| **Métrique primaire (déclarée)** | **Descriptive**: accord disposition-par-scénario avec la référence (comptage). Explicitement**pas**une métrique de performance de détection.                                                                                                                                                                        |
| **k exécutions**                   | 1 (déterministe → exact, pas de variance).                                                                                                                                                                                                                                                                             |
| **Commit Git**                      | Données`data/scenarios/`à`632b2b8`; consolidation du harness (`evals/run_eval.py`) dans le commit evals suivant. Manifeste :`evals/results/run_20261023T084832Z.json`.                                                                                                                                                 |

## Résultats observés


| Scénario             | Vérité               | A                         | B                         | C                         |
| --------------------- | ---------------------- | ------------------------- | ------------------------- | ------------------------- |
| SC-AMBIGUOUS-001      | insufficient\_evidence | ✅                        | ✅                        | ✅                        |
| SC-BRUTEFORCE-001     | escalate               | ✅                        | ✅                        | ✅                        |
| SC-INJECTION-001      | escalate               | ✅                        | ✅                        | ✅                        |
| fox-privesc-shadow    | escalate               | ❌ insufficient\_evidence | ❌ insufficient\_evidence | ❌ insufficient\_evidence |
| fox-dnsteal-dns-exfil | escalate               | ❌ insufficient\_evidence | ❌ insufficient\_evidence | ❌ insufficient\_evidence |
| **Accord**            |                        | **3/5**                   | **3/5**                   | **3/5**                   |

* Vérification de citations : `True` pour tous les cas B/C. Coût : `0.0` (stub hors-ligne).
* **C = B** sur la disposition de chaque scénario (invariance au RAG pour le stub).

## Interprétation

* Le stub n'atteint la référence que sur les 3 cas **synthétiques**, qui ont été écrits autour de sa propre règle (comptage de rafales d'échecs d'authentification). C'est une forme de **circularité** (`EVALUATION.md` §9 bis) : le synthétique encode nos hypothèses.
* Sur les **2 cas réels**, il échoue : `fox-privesc` est une chaîne `su`/`sudo` sans rafale d'échecs ; `fox-dnsteal` est un signal DNS faible sans échec d'auth. La règle de triage ne généralise donc pas au-delà du brute-force.
* **C = B** : le RAG n'influence pas la disposition du stub (elle dérive de signaux structurés, pas du savoir récupéré). Cohérent avec l'observation antérieure sur `fox-privesc` (C−B = 0).

## Limites

* **5 scénarios** : ce n'est **pas** un benchmark ; aucune moyenne agrégée n'est reportée comme performance.
* Les cas synthétiques, même corrects, **encodent nos hypothèses** → ne jamais conclure sur le seul synthétique (`EVALUATION.md` §12).
* Vérité-terrain des fox = `time_label` reconstruit (fenêtre), pas un `event_label` certifié.
* L'analyste par défaut est un **stub à base de règles** : aucun chiffre ici n'est une performance de vrai LLM.
* « Accord » est un **comptage descriptif**, pas une métrique de détection validée.

## Conclusion

Premier résultat d'évaluation honnête du projet : la triage à base de règles réussit les cas taillés pour elle et **échoue sur les deux cas réels**, le RAG ne changeant rien à la disposition. Résultat **négatif utile** qui motive (a) un analyste non trivial (vrai LLM, Baseline B-réel) et (b) l'élargissement du corpus de scénarios de référence.
