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
 | Configuration | Auto-generated config.txt, 16-color themes, multiple users, nOS installer |
 | Authentication | Login system (su, login), user management (adduser), sudo permissions |
 | Shell | Custom prompt, command history, path autocompletion |
 | File System | cd, ls, mkdir, rm, rmdir, copy, cut, paste |
 | Software | Full nano recreation |
 | Execution | Run Python scripts (./file.py) |
 | Communication | connect, disconnect, msg, file transfer (swarm mode) |
 | UI | Customizable colors, ASCII art, neofetch display |

### In Development / To Fix
 | Issue | Description | Status | Priority |
 |-------|-------------|--------|----------|
 | Connection timeout | Connection only works after 20s timeout | ⏳ Planned | ★★★★ |
 | Visual artifacts | Screen flicker and cursor flickering | ⏳ Planned | ★★★ |
 | Sudo commands not marked | Sudo-only commands not shown as unavailable | X Unplanned | ★ |
 | File transfer | File hosting between systems not implemented | ⏳ Planned | ★ |

---

## Installation

### Prerequisites
► Python 3.8+
► colorama (for cross-platform colored output)
```bash
pip install colorama
```
### Download and run
```bash
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
```
## Usage

### Available modes

| Mode | Folder | Description | Launch command |
|------|--------|-------------|----------------|
| Basic | nOS-x86-64 | Complete sys/ folder | python sys/sys.py |
| Lightweight | nOS-x86-64-lw | sys.py only | python sys/sys.py |
| Swarm | nOS-x86-64-swarm | sys0/, sys1/, sys2/, sys3/ (interconnectable), and server tools | launch.bat |
| Developement | nOS-x86-64-dev | Development version with all resources and 4 instances | python sys/sys.py (x4) |

### First Run

Run ```bash python sys0/sys.py ```
If config.txt does not exist:

Follow setup prompts (username, password, colors)
System will automatically reboot

Log in with:

```bash su <username>
-> Password (masked with ⍟)
````

### Swarm mode

Open 4 terminals
In each terminal, launch an instance:

```bash
python sys0/sys.py  # Terminal 1
python sys1/sys.py  # Terminal 2
````
or run launch.cmd

From sys0, connect to sys1:

```bash connect sys1 
````

In sys1, accept the connection with Y

## Available Commands

### Basic Commands (All Users)

Command | Description | Example
------- | ----------- | -------
help | Show available commands | help
su <user> | Login as user | su noe
login <user> | Alias for su | login noe
whoami | Show current user | whoami
user [user] | Show user info | user noe
clear | Clear screen | clear
echo <text> | Print text | echo Hello
color <color> | Preview color | color red
neofetch | Show system info | neofetch
cd <path> | Change directory | cd /textes
ls [path] | List files/directories | ls /
reboot | Restart nOS | reboot
shutdown | Shut down nOS | shutdown

### Sudo Commands (Sudo Users Only)

⚠ These commands require sudo privileges.
If not sudo, nOS will display: "permission denied: sudo required"

Command | Description | Example
------- | ----------- | -------
adduser | Create new user | adduser
mkdir <path> | Create directory | mkdir Documents
rm <file> | Remove file | rm texte.txt
rmdir <dir> | Remove empty directory | rmdir Documents
copy <path> | Copy file/directory to clipboard | copy texte.txt
cut <path> | Cut file/directory to clipboard | cut texte.txt
paste [path] | Paste from clipboard | paste /textes
nano [file] | Text editor | nano texte.txt

### Communication Commands (Swarm Mode)

Command | Description | Example
------- | ----------- | -------
connect <system> | Connect to another nOS instance | connect sys1
disconnect | Disconnect from current instance | disconnect
msg <text> | Send message to connected instance | msg Hello sys1!

## Virtual File System
nOS includes a virtual file system based in sys/files/:
► Root: / (maps to sys/files/)
► Security: Cannot escape / (no access to Windows files)
► Persistence: Files are saved in sys/files/

### Usage Examples

```bash
# Create directory
mkdir Documents

# List files in root
ls /

# Edit file with nano
nano note.txt

# Execute Python script
./my_script.py

# Copy and paste files
copy note.txt
paste /Documents
````
### Known Limitations
✖ only one communication is allowed at the time

## Multi-System Communication
nOS allows multiple instances to communicate with each other (swarm mode).
Each instance is an independent system with its own config.txt and resources.txt.

### Connection Workflow

From sys0:

```bash connect sys1 ```

→ Displays: "waiting for answer from sys1"

In sys1:

```bash incoming connection request from sys0. would you like to accept (Y/n)? Y ````

If Y: Displays "request accepted" in sys1 and "exit code 0: connection successful" in sys0
If N: Displays "denied" in sys1 and "exit code 1: denied" in sys0

Messaging:

```bash # In sys0:
msg Hello sys1!
````

```bash # In sys1:
[sys0] Hello sys1!
````

Disconnect:

```bash disconnect ````

## Features to Implement:

⏳ More than 1 connection at a time
⏳ File hosting on one server with URLs

## Customization
config.txt
Edit config.txt to customize nOS:
```bash
# Main user
username=noe
password=peyre

# Colors (16 available)
primary=blue
secondary=darkblue
tertiary=yellow
background=white

# Total uptime
totaluptime=891
uptime_seconds=891

# Users list (JSON)
users=[
  {
    "username": "admin",
    "password": "pwd",
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "29/06/09",
    "sudo": true,
    "totaluptime": "4675"
  }
]
````
16 Color Palette

img

### Logo and Banner
Edit resources.txt to change ASCII art:
````bash
logo
[your ASCII art here]
end

banner
[your banner here]
end
````

## Known Issues & Roadmap
### Critical Bugs

Issue | Description | Status | Priority
------ | ----------- | ------ | --------
Connection timeout | Connection only works after 20s timeout | ⏳ Planned | ★★
Sudo commands not marked | Sudo-only commands not shown as unavailable | X Not planned | ★★

## Roadmap

Version | Features | Status
------- | -------- | ------
v1.0.0 | Initial stable release | ✔ Complete
v1.1.0 | Instant connection (no timeout) | ⏳ In progress
v1.2.0 | File hosting | ⏳ Planned


## Contributing
Want to contribute to nOS? Follow these steps:

### Steps to Contribute

Fork the repository:
````bash
git clone https://github.com/NoePeyre/nOS.git
cd nOS
git checkout -b fix/your-fix  # or feature/your-feature
````

Make your changes and test them
Commit your changes:
````bash
git add .
git commit -m "fix: description of your fix"
````
Push your branch:
````bash
git push origin fix/your-fix
````

Open a Pull Request on GitHub:

Clearly describe your changes
Add screenshots if needed
Link to existing Issues (e.g., Fixes #123)

### Contribution Ideas

Type | Example | Difficulty
---- | ------- | -----------
UI Improvement / Features | Feature rich bios | ★★
New Feature | File hosting | ★★★★
Documentation | Improve this README | ★
New Feature | Create color themes feature | ★



License
This project is licensed under the MIT License - see LICENSE for details.
