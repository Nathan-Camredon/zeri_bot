# Instructions & Mémoire du Projet (Zeri Bot)

Ce fichier sert de référence pour le comportement de l'agent et la documentation des décisions techniques du projet.

## 1. Règles de Comportement 🤖

*   **NO CODE AUTO**: Ne jamais modifier ou générer du code directement sans une demande explicite et validée.
*   **Concepts > Code**: Privilégier l'explication des concepts, de l'architecture et du "pourquoi" avant de proposer du "comment".
*   **Guidage**: Agir comme un mentor ou un lead dev qui guide l'utilisateur, plutôt que comme un exécutant.

## 2. Décisions Techniques Validées ✅

*   **Base de Données**: SQLite est utilisé pour le moment. Une migration vers PostgreSQL est envisagée pour plus tard, mais la priorité est la stabilité actuelle.
*   **Format des Dates**: 
    *   L'input utilisateur pour les disponibilités doit être flexible (ex: "Lundi", "Mardi").
    *   **REFUSÉ**: Le format "JJ/MM" (date précise) a été écarté pour l'ajout de disponibilité. On reste sur un système récurrent (Tous les Lundis).
    *   Le parsing se fait via `modules.utils.parse_day_input`.
*   **Constantes**: Les listes de jours (`DAYS`) sont centralisées dans `modules/constants.py` et ne doivent pas être dans le `.env` (logique vs config).
*   **Architecture**:
    *   Architecture modulaire (`modules/`) validée.
    *   La sécurité SQL (requêtes paramétrées) est une priorité absolue.

## 3. Observations & Dette Technique 📝

*   **Concurrence**: SQLite peut bloquer (`database is locked`) si plusieurs requêtes d'écriture arrivent simultanément. Ce n'est pas critique pour l'instant mais à surveiller.
*   **Logging**: Il manque parfois de logs d'erreurs explicites (trop de `try... except: pass`). À améliorer progressivement.
*   **Typage**: Le typage strict (Type Hinting) n'est pas une priorité pour l'utilisateur ("ça ne sert pas à grand chose en python"), ne pas insister dessus sauf si critique.

## 4. Glossaire

*   **Disponibilité (Availability)** : Créneaux horaires récurrents (ex: Tous les lundis 18h-20h).
*   **Session** : Un événement ponctuel planifié (Match, Entraînement) à une date précise.
