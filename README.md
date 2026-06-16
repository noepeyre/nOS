# **nOS 🖥️**
*Un mini-OS simulé en terminal, écrit en Python, avec système de fichiers virtuel et communication multi-instances.*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/NoePeyre/nOS?style=flat)](https://github.com/NoePeyre/nOS/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/NoePeyre/nOS)](https://github.com/NoePeyre/nOS/issues)
[![Status: Actively Developed](https://img.shields.io/badge/Status-Actively%20Developed-green.svg)](https://github.com/NoePeyre/nOS)

---

---

## **📌 Table des Matières**
1. [📖 À propos](#-à-propos)
2. [✨ Fonctionnalités](#-fonctionnalités)
3. [📥 Installation](#-installation)
4. [🚀 Utilisation](#-utilisation)
5. [💻 Commandes Disponibles](#-commandes-disponibles)
6. [📁 Système de Fichiers Virtuel](#-système-de-fichiers-virtuel)
7. [🔗 Communication Multi-Systèmes](#-communication-multi-systèmes)
8. [🎨 Personnalisation](#-personnalisation)
9. [🐛 Bugs Connus & Roadmap](#-bugs-connus--roadmap)
10. [📸 Suggestions de Captures d'Écran](#-suggestions-de-captures-décran)
11. [🤝 Contribution](#-contribution)
12. [📜 License](#-license)

---

---

---

## **📖 À propos**
**nOS** est un **mini-OS simulé en terminal** écrit en Python, conçu pour imiter un système d'exploitation basique avec :
✅ **Démarrage BIOS** avec animations et logs simulés.
✅ **Configuration utilisateur** (nom, mot de passe, couleurs).
✅ **Écran de login** style *neofetch* avec ASCII art.
✅ **Shell interactif** avec historique des commandes.
✅ **Système de fichiers virtuel** (`cd`, `ls`, `mkdir`, `nano`, etc.).
✅ **Communication entre instances** (mode *swarm*).
✅ **Gestion des utilisateurs** avec permissions *sudo*.

---
**Pourquoi nOS ?**
- **Éducatif** : Comprendre le fonctionnement d'un shell et d'un OS.
- **Ludique** : Simuler un OS rétro dans ton terminal.
- **Modulaire** : Personnalisable (couleurs, logo, commandes).
- **Collaboratif** : Communication entre plusieurs instances nOS.

---

---

## **✨ Fonctionnalités**

### **✅ Implémentées**
   Catégorie | Fonctionnalités |
 |-----------|------------------|
 | **Boot** | Animation BIOS, spinner Braille, logs simulés, écran de démarrage. |
 | **Configuration** | Création de `config.txt`, choix des couleurs (16 thèmes), utilisateurs multiples. |
 | **Authentification** | Système de login (`su`, `login`), gestion des utilisateurs (`adduser`), permissions *sudo*. |
 | **Shell** | Prompt personnalisé, historique des commandes, autocomplétion. |
 | **Fichiers** | `cd`, `ls`, `mkdir`, `rm`, `rmdir`, `copy`, `cut`, `paste`, `nano`. |
 | **Exécution** | Lancement de scripts Python (`./fichier.py`). |
 | **Communication** | `connect`, `disconnect`, `msg` (mode *swarm*). |
 | **UI** | Couleurs personnalisables, ASCII art, *neofetch*. |

### **🚧 En Développement / À Corriger**
 | Problème | Statut | Priorité |
 |----------|--------|----------|
 | Background qui disparaît après 10 lignes | 🐛 Bug | ⭐⭐⭐⭐ |
 | `:` dans neofetch sans background | 🐛 Bug | ⭐⭐⭐⭐ |
 | `reboot` avec background noir au lieu de blanc | 🐛 Bug | ⭐⭐⭐ |
 | `cd ..` et `cd ../..` non implémentés | ⏳ À faire | ⭐⭐⭐⭐ |
 | `ls` crée des lignes noires | 🐛 Bug | ⭐⭐⭐ |
 | Connexion instantanée (pas de timeout) | ⏳ À faire | ⭐⭐ |
 | Héritage du thème lors de la connexion | ⏳ À faire | ⭐⭐ |
 | Transfert de fichiers entre systèmes | ⏳ À faire | ⭐⭐⭐ |
 | Prompt `user@sys0:/>` en mode *swarm* | ⏳ À faire | ⭐⭐⭐ |
 | Affichage des commandes *sudo-only* comme indisponibles | 🐛 Bug | ⭐⭐ |

---

---

## **📥 Installation**

### **📦 Prérequis**
- **Python 3.8+** ([Télécharger Python](https://www.python.org/downloads/))
- **`colorama`** (pour les couleurs dans le terminal)
  ```bash
  pip install colorama
