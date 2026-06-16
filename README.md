# nOS
A minimalist terminal OS simulator written in Python, featuring a virtual file system and multi-instance communication.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/NoePeyre/nOS?style=flat)](https://github.com/NoePeyre/nOS/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/NoePeyre/nOS)](https://github.com/NoePeyre/nOS/issues)
[![Status: Actively Developed](https://img.shields.io/badge/Status-Actively%20Developed-green.svg)](https://github.com/NoePeyre/nOS)

---

► Table of Contents
1. [About](#about)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Available Commands](#available-commands)
6. [Virtual File System](#virtual-file-system)
7. [Multi-System Communication](#multi-system-communication)
8. [Customization](#customization)
9. [Screenshots](#screenshots)
10. [Known Issues & Roadmap](#known-issues--roadmap)
11. [Contributing](#contributing)
12. [License](#license)

---

## About
nOS is a Python-based terminal OS simulator designed to mimic a lightweight operating system with:
☑ BIOS boot animation with simulated logs
☑ User configuration (username, password, colors)
☑ Neofetch-style login screen with ASCII art
☑ Interactive shell with command history and autocompletion
☑ Virtual file system (cd, ls, mkdir, nano, etc.)
☑ Multi-instance communication (swarm mode)
☑ User management with sudo permissions

nOS is educational, modular, and designed for terminal enthusiasts who want to simulate a retro OS experience.

---

## Features

### Implemented
   Category | Features |
 |----------|----------|
 | Boot | BIOS animation, Braille spinner, simulated logs, boot screen |
 | Configuration | Auto-generated config.txt, 16-color themes, multiple users |
 | Authentication | Login system (su, login), user management (adduser), sudo permissions |
 | Shell | Custom prompt, command history, path autocompletion |
 | File System | cd, ls, mkdir, rm, rmdir, copy, cut, paste, nano |
 | Execution | Run Python scripts (./file.py) |
 | Communication | connect, disconnect, msg (swarm mode) |
 | UI | Customizable colors, ASCII art, neofetch display |

### In Development / To Fix
 | Issue | Description | Status | Priority |
 |-------|-------------|--------|----------|
 | Incomplete background | Background disappears after 10 lines and behind ":" in neofetch | ⚠ Unfixed | ★★★★ |
 | Reboot with black background | Reboot shows black background instead of white | ⚠ Unfixed | ★★★ |
 | Missing cd .. | cd .. and cd ../.. not implemented | ⏳ Planned | ★★★★ |
 | ls black lines | ls command leaves black line artifacts | ⚠ Unfixed | ★★★ |
 | Connection timeout | Connection only works after 20s timeout | ⏳ Planned | ★★ |
 | Sudo commands not marked | Sudo-only commands not shown as unavailable | ⚠ Unfixed | ★★ |
 | File transfer | File transfer between systems not implemented | ⏳ Planned | ★★★ |
 | Swarm prompt | Show user@sysX:/> instead of user@nOS:/> in swarm mode | ⏳ Planned | ★★★ |
 | Theme inheritance | Inherit colors from connected system | ⏳ Planned | ★★ |

---

## Installation

### Prerequisites
► Python 3.8+
► colorama (for cross-platform colored output)
```bash
pip install colorama

### Download and run
git clone https://github.com/NoePeyre/nOS.git
cd nOS

# Standard version (sys0)
python sys0/sys.py

# Swarm mode (4 instances)
# Open 4 terminals and run in each:
python sys0/sys.py  # Terminal 1
python sys1/sys.py  # Terminal 2
python sys2/sys.py  # Terminal 3
python sys3/sys.py  # Terminal 4

## Usage

### Available modes

| Mode | Folder | Description | Launch command |
|------|--------|-------------|----------------|
| Basic | nOS-x86-64 | Complete sys/ folder | python sys/sys.py |
| Lightweight | nOS-x86-64-lw | sys.py only | python sys/sys.py |
| Swarm | nOS-x86-64-swarm | sys0/, sys1/, sys2/, sys3/ (interconnectable), and server tools | launch.bat |
| Developement | nOS-x86-64-dev | Development version with all resources and 4 instances | python sys/sys.py (x4) |
