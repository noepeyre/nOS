import os
import json
import random
import shlex
import shutil
import sys
import time
from datetime import timedelta

from colorama import Style, init


init()

COLOR_NAMES = {
    "black": "#0C0C0C",
    "darkblue": "#000080",
    "darkgreen": "#008000",
    "darkcyan": "#008080",
    "darkred": "#800000",
    "darkmagenta": "#800080",
    "darkyellow": "#808000",
    "gray": "#808080",
    "darkgray": "#404040",
    "blue": "#0000FF",
    "lime": "#00FF00",
    "cyan": "#00FFFF",
    "red": "#FF0000",
    "magenta": "#FF00FF",
    "yellow": "#FFFF00",
    "white": "#FFFFFF",
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[index:index + 2], 16) for index in (0, 2, 4))


def normalize_color_value(color_value):
    if color_value is None:
        return None
    if color_value in COLOR_NAMES:
        return COLOR_NAMES[color_value]
    return color_value


def ansi_fg(hex_color):
    hex_color = normalize_color_value(hex_color)
    red, green, blue = hex_to_rgb(hex_color)
    return f"\033[38;2;{red};{green};{blue}m"


def ansi_bg(hex_color):
    hex_color = normalize_color_value(hex_color)
    red, green, blue = hex_to_rgb(hex_color)
    return f"\033[48;2;{red};{green};{blue}m"


COLOR_MAP = {name: ansi_fg(hex_color) for name, hex_color in COLOR_NAMES.items()}
COLOR_MAP["reset"] = Style.RESET_ALL

BG_COLOR_MAP = {name: ansi_bg(hex_color) for name, hex_color in COLOR_NAMES.items()}
BG_COLOR_MAP["reset"] = Style.RESET_ALL

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")
LOGO_FILE = os.path.join(BASE_DIR, "resources.txt")
FILES_ROOT = os.path.join(BASE_DIR, "files")
INSTALL_ROOT = os.path.dirname(BASE_DIR)
DEFAULT_SYSTEM_ID = os.path.basename(BASE_DIR) if os.path.basename(BASE_DIR).startswith("sys") else "sys0"
COMMS_ROOT = os.path.join(INSTALL_ROOT, "comms")
SYSTEM_IDS = tuple(f"sys{i}" for i in range(4))

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DEFAULT_CONFIG = {
    "username": "user",
    "password": "password",
    "primary": "white",
    "secondary": "white",
    "tertiary": "red",
    "background": "black",
    "totaluptime": "0",
}

MACHINE_SPECS = {
    "os": "Arch Linux x86_64",
    "kernel": "6.9.2-arch1-1",
    "packages": "1267 (pacman), 6 (flatpak)",
    "shell": "fish 3.7.1",
    "resolution": "2560x1440",
    "de": "GNOME 46.2",
    "wm": "Mutter",
    "wm_theme": "Adwaita",
    "theme": "Adwaita [GTK2/3]",
    "icons": "Adwaita [GTK2/3]",
    "terminal": "foot",
    "cpu": "Intel i7-4790K (8) @ 4.700GHz",
    "gpu": "NVIDIA GeForce GTX 1070",
    "memory": "2687MiB / 19938MiB",
}
SPEC_KEYS = tuple(f"spec_{key}" for key in MACHINE_SPECS)
CONFIG_COLOR_ORDER = (
    "black",
    "darkgray",
    "darkred",
    "red",
    "darkgreen",
    "lime",
    "darkyellow",
    "yellow",
    "darkblue",
    "blue",
    "darkmagenta",
    "magenta",
    "darkcyan",
    "cyan",
    "gray",
    "white",
)
NEOFETCH_PALETTE_ROWS = (
    ("black", "darkred", "darkgreen", "darkyellow", "darkblue", "darkmagenta", "darkcyan", "gray"),
    ("darkgray", "red", "lime", "yellow", "blue", "magenta", "cyan", "white"),
)

PRE_LOGIN_COMMANDS = {
    "help": "Show available commands",
    "su": "Log in as a configured user",
    "login": "Alias for su",
    "exit": "Shut down nOS",
    "shutdown": "Shut down nOS",
    "restart": "Restart nOS",
    "reboot": "Restart nOS",
}

AUTH_COMMANDS = {
    "help": "Show available commands",
    "clear": "Clear the screen",
    "echo": "Print text",
    "print": "Print text",
    "color": "Preview a text color",
    "cd": "Change current directory",
    "ls": "List files and directories",
    "mkdir": "Create a directory",
    "rm": "Remove a file",
    "rmdir": "Remove an empty directory",
    "copy": "Copy a file or directory",
    "cut": "Cut a file or directory",
    "paste": "Paste the clipboard",
    "nano": "Edit a text file",
    "neofetch": "Show system information",
    "whoami": "Show current user",
    "user": "Show current user or inspect a user",
    "login": "Log into an user",
    "connect": "Connect to another nOS system",
    "disconnect": "Disconnect from a system",
    "msg": "Send a message to the connected system",
    "adduser": "Create a new user",
    "exit": "Shut down nOS",
    "shutdown": "Shut down nOS",
    "restart": "Restart nOS",
    "reboot": "Restart nOS",
}

SUDO_COMMANDS = {"adduser", "mkdir", "rm", "rmdir", "copy", "cut", "paste", "nano"}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def color_text(text, color):
    return f"{COLOR_MAP.get(color, '')}{text}{COLOR_MAP['reset']}"


def color_text_on_background(text, color, background, reset=True):
    bg_hex = COLOR_NAMES.get(background, COLOR_NAMES[DEFAULT_CONFIG["background"]])
    suffix = Style.RESET_ALL if reset else ""
    return f"{ansi_bg(bg_hex)}{COLOR_MAP.get(color, '')}{text}{suffix}"


def print_colored(text, color="white", end="\n"):
    print(color_text(text, color), end=end)


def raw_color_text(text, fg=None, bg=None):
    prefix = ""
    if bg:
        prefix += ansi_bg(bg)
    if fg:
        prefix += ansi_fg(fg)
    return f"{prefix}{text}{Style.RESET_ALL}"


def compose_colored_line(segments, background, width=None):
    width = width or terminal_size().columns
    bg_hex = COLOR_NAMES.get(background, COLOR_NAMES[DEFAULT_CONFIG["background"]])
    visible_length = 0
    parts = [ansi_bg(bg_hex)]
    for text, fg in segments:
        if not text:
            continue
        parts.append(COLOR_MAP.get(fg, ""))
        parts.append(text)
        visible_length += len(text)
    if visible_length < width:
        parts.append(" " * (width - visible_length))
    parts.append(Style.RESET_ALL)
    return "".join(parts)


def typewriter(text, color="white", delay=0.01, end="\n"):
    for char in text:
        sys.stdout.write(color_text(char, color))
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


def terminal_size():
    return shutil.get_terminal_size((80, 24))


def print_centered(text, color="white"):
    width = terminal_size().columns
    print_colored(text.center(width), color)


def print_at_bottom_center(text, color="white"):
    width, height = terminal_size()
    sys.stdout.write(f"\033[{height};1H")
    print_colored(text.center(width), color, end="")
    sys.stdout.flush()


def print_at_bottom_right(text, color="white"):
    width, height = terminal_size()
    x = max(1, width - len(text) + 1)
    sys.stdout.write(f"\033[{height};{x}H")
    print_colored(text, color, end="")
    sys.stdout.flush()


def fill_screen(bg=None):
    bg = bg or COLOR_NAMES["black"]
    width, height = terminal_size()
    sys.stdout.write("\033[H")
    for row in range(height):
        end = "" if row == height - 1 else "\n"
        sys.stdout.write(raw_color_text(" " * width, bg=bg) + end)
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def clear_with_background(config):
    background = config.get("background", DEFAULT_CONFIG["background"])
    fill_screen(COLOR_NAMES.get(background, COLOR_NAMES[DEFAULT_CONFIG["background"]]))


def config_color_text(text, color, config, reset=True):
    return color_text_on_background(
        text,
        color,
        config.get("background", DEFAULT_CONFIG["background"]),
        reset=reset,
    )


def print_config_colored(text, color, config, end="\n"):
    bg = config.get("background", DEFAULT_CONFIG["background"])
    print(compose_colored_line([(text, color)], bg), end=end)


def load_history(limit=100):
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "a", encoding="utf-8"):
            pass
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        entries = [line.rstrip("\n") for line in file if line.strip()]
    return entries[-limit:]


def save_history(entries, limit=100):
    trimmed = [entry for entry in entries if entry.strip()][-limit:]
    with open(HISTORY_FILE, "a", encoding="utf-8"):
        pass
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        for entry in trimmed:
            file.write(f"{entry}\n")


def history_completion_matches(buffer_text, completions):
    prefix = buffer_text.strip()
    if not prefix:
        return []
    return [candidate for candidate in completions if candidate.startswith(prefix)]


def ensure_files_root():
    os.makedirs(FILES_ROOT, exist_ok=True)
    return FILES_ROOT


def ensure_comms_root():
    os.makedirs(COMMS_ROOT, exist_ok=True)
    os.makedirs(os.path.join(COMMS_ROOT, "sessions"), exist_ok=True)
    os.makedirs(os.path.join(COMMS_ROOT, "requests"), exist_ok=True)
    return COMMS_ROOT


def current_system_id(config):
    return str(config.get("system_id") or DEFAULT_SYSTEM_ID).strip() or DEFAULT_SYSTEM_ID


def system_folder(system_id):
    return os.path.join(INSTALL_ROOT, str(system_id).strip())


def comms_session_id(left, right):
    return "__".join(sorted([str(left).strip(), str(right).strip()]))


def comms_session_path(left, right):
    ensure_comms_root()
    return os.path.join(COMMS_ROOT, "sessions", f"{comms_session_id(left, right)}.json")


def comms_request_path(source, target):
    ensure_comms_root()
    return os.path.join(COMMS_ROOT, "requests", f"{source}__to__{target}.json")


def read_json_file(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return default


def write_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def normalize_virtual_path(path):
    if path is None:
        return ""
    path = str(path).replace("\\", "/").strip()
    if path in ("", ".", "/"):
        return ""
    parts = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def virtual_path_label(path):
    rel = normalize_virtual_path(path)
    return "/" if not rel else f"/{rel}"


def resolve_virtual_path(path, cwd=""):
    ensure_files_root()
    cwd = normalize_virtual_path(cwd)
    raw_path = "" if path is None else str(path).replace("\\", "/").strip()
    if raw_path in ("", "."):
        candidate = cwd
    else:
        if raw_path.startswith("/"):
            segments = []
            raw_path = raw_path[1:]
        else:
            segments = [segment for segment in cwd.split("/") if segment]
        for part in raw_path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if segments:
                    segments.pop()
                continue
            segments.append(part)
        candidate = "/".join(segments)
    absolute = os.path.abspath(os.path.join(FILES_ROOT, candidate))
    root = os.path.abspath(FILES_ROOT)
    if os.path.commonpath([absolute, root]) != root:
        raise ValueError("path escapes nOS root")
    return absolute


def path_from_files_root(absolute_path):
    ensure_files_root()
    absolute_path = os.path.abspath(absolute_path)
    root = os.path.abspath(FILES_ROOT)
    if os.path.commonpath([absolute_path, root]) != root:
        return absolute_path
    rel = os.path.relpath(absolute_path, root).replace("\\", "/")
    return "/" if rel == "." else f"/{rel}"


def list_directory_entries(absolute_path):
    entries = []
    for name in os.listdir(absolute_path):
        full = os.path.join(absolute_path, name)
        entries.append((name, os.path.isdir(full)))
    return sorted(entries, key=lambda item: (not item[1], item[0].lower()))


def path_completion_matches(token, cwd=""):
    cwd = normalize_virtual_path(cwd)
    token = token or ""
    if token.endswith("/"):
        base_dir, partial = token.rstrip("/"), ""
    elif "/" in token:
        base_dir, partial = token.rsplit("/", 1)
    else:
        base_dir, partial = "", token
    try:
        search_dir = resolve_virtual_path(base_dir or ".", cwd)
    except ValueError:
        return []
    if not os.path.isdir(search_dir):
        return []
    matches = []
    for name, is_dir in list_directory_entries(search_dir):
        if name.startswith(partial):
            candidate = name + ("/" if is_dir else "")
            prefix = f"{base_dir}/" if base_dir else ""
            matches.append(prefix + candidate)
    return matches


def split_command_context(buffer_text, cursor_pos):
    left = buffer_text[:cursor_pos]
    start = left.rfind(" ") + 1
    token = buffer_text[start:cursor_pos]
    return left, start, token


def shell_completion_matches(buffer_text, cursor_pos, config, logged_in):
    command_names = sorted((AUTH_COMMANDS if logged_in else PRE_LOGIN_COMMANDS).keys())
    cwd = config.get("_cwd", "")
    left, token_start, token = split_command_context(buffer_text, cursor_pos)
    first_word = left.split()[0] if left.split() else ""
    if token_start == 0:
        return [name for name in command_names if name.startswith(token)]

    file_commands = {"cd", "ls", "mkdir", "rm", "rmdir", "copy", "cut", "paste", "nano"}
    if first_word in file_commands:
        return path_completion_matches(token, cwd)
    return [name for name in command_names if name.startswith(token)]


def read_line_with_background(prompt_segments, config, mask=None):
    background = config.get("background", DEFAULT_CONFIG["background"])
    width = terminal_size().columns
    buffer = []
    cursor_pos = 0
    history = config.get("_history", [])
    history_index = None
    completion_state = {"key": None, "index": 0, "matches": []}
    cursor_visible = True
    last_blink = time.time()

    def visible_text(show_cursor=True):
        typed = mask * len(buffer) if mask else "".join(buffer)
        cursor_char = "_" if show_cursor else " "
        cursor_slice = min(cursor_pos, len(typed))
        return typed[:cursor_slice] + cursor_char + typed[cursor_slice:]

    def redraw(show_cursor=True):
        line_text = visible_text(show_cursor)
        line = compose_colored_line(prompt_segments + [(line_text, config["secondary"])], background, width)
        sys.stdout.write("\r\033[?25l" + line + "\r")
        sys.stdout.flush()

    def commit():
        typed = mask * len(buffer) if mask else "".join(buffer)
        print(compose_colored_line(prompt_segments + [(typed, config["secondary"])], background, width))

    def set_buffer(text, position=None):
        nonlocal cursor_pos
        buffer[:] = list(text)
        cursor_pos = len(buffer) if position is None else max(0, min(len(buffer), position))

    def reset_completion():
        completion_state["key"] = None
        completion_state["index"] = 0
        completion_state["matches"] = []

    def update_history_index(direction):
        nonlocal history_index
        if not history:
            return
        if history_index is None:
            history_index = len(history)
        history_index = max(0, min(len(history) - 1, history_index + direction))
        set_buffer(history[history_index], len(history[history_index]))
        reset_completion()
        redraw()

    def current_context():
        line = "".join(buffer)
        left = line[:cursor_pos]
        start = left.rfind(" ") + 1
        right = line[cursor_pos:]
        next_space = right.find(" ")
        end = cursor_pos + next_space if next_space != -1 else len(buffer)
        token_prefix = line[start:cursor_pos]
        token = line[start:end]
        command = left.split()[0] if left.split() else ""
        return start, end, token_prefix, token, command

    def apply_completion(matches):
        nonlocal history_index, cursor_pos
        if not matches:
            return
        start, end, _, _, _ = current_context()
        state_key = (start, end, "".join(buffer[:cursor_pos]), tuple(matches))
        if completion_state["key"] != state_key:
            completion_state["key"] = state_key
            completion_state["index"] = 0
            completion_state["matches"] = matches
        else:
            completion_state["index"] = (completion_state["index"] + 1) % len(matches)

        chosen = matches[completion_state["index"]]
        replacement = chosen
        if end > start:
            buffer[start:end] = list(replacement)
        else:
            buffer[start:start] = list(replacement)
        cursor_pos = start + len(replacement)
        history_index = None
        reset_completion()
        redraw()

    def handle_command_key(key):
        nonlocal history_index, cursor_pos
        if key == "enter":
            commit()
            return "".join(buffer), True
        if key == "backspace":
            if cursor_pos > 0:
                del buffer[cursor_pos - 1]
                cursor_pos -= 1
                history_index = None
                reset_completion()
                redraw()
            return None, False
        if key == "delete":
            if cursor_pos < len(buffer):
                del buffer[cursor_pos]
                history_index = None
                reset_completion()
                redraw()
            return None, False
        if key == "up":
            update_history_index(-1)
            return None, False
        if key == "down":
            if history_index is None:
                return None, False
            if history_index < len(history) - 1:
                history_index += 1
                set_buffer(history[history_index], len(history[history_index]))
            else:
                history_index = None
                set_buffer("", 0)
            reset_completion()
            redraw()
            return None, False
        if key == "tab":
            start, end, token_prefix, token, command = current_context()
            if start == 0 and token_prefix.startswith("./"):
                matches = [f"./{match}" for match in path_completion_matches(token_prefix[2:], config.get("_cwd", ""))]
            elif start == 0:
                completions = config.get("_commands", [])
                matches = [candidate for candidate in completions if candidate.startswith(token_prefix)]
            else:
                file_commands = {"cd", "ls", "mkdir", "rm", "rmdir", "copy", "cut", "paste", "nano"}
                if command in file_commands:
                    matches = path_completion_matches(token_prefix, config.get("_cwd", ""))
                else:
                    completions = config.get("_commands", [])
                    matches = [candidate for candidate in completions if candidate.startswith(token_prefix)]
            if matches:
                apply_completion(matches)
            return None, False
        if key == "left":
            if cursor_pos > 0:
                cursor_pos -= 1
                redraw()
            return None, False
        if key == "right":
            if cursor_pos < len(buffer):
                cursor_pos += 1
                redraw()
            return None, False
        if key == "home":
            cursor_pos = 0
            redraw()
            return None, False
        if key == "end":
            cursor_pos = len(buffer)
            redraw()
            return None, False
        if len(key) == 1 and key.isprintable():
            buffer[cursor_pos:cursor_pos] = list(key)
            cursor_pos += 1
            history_index = None
            reset_completion()
            redraw()
        return None, False

    redraw()

    if os.name == "nt":
        import msvcrt

        try:
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
            while True:
                if msvcrt.kbhit():
                    char = msvcrt.getwch()
                    if char in ("\r", "\n"):
                        commit()
                        return "".join(buffer)
                    if char == "\003":
                        raise KeyboardInterrupt
                    if char == "\b":
                        handle_command_key("backspace")
                        continue
                    if char in ("\x00", "\xe0"):
                        key_code = msvcrt.getwch()
                        special = {
                            "H": "up",
                            "P": "down",
                            "K": "left",
                            "M": "right",
                            "S": "delete",
                            "G": "home",
                            "O": "end",
                        }
                        if key_code == "I":
                            handle_command_key("tab")
                        else:
                            handle_command_key(special.get(key_code, ""))
                        continue
                    if char == "\t":
                        handle_command_key("tab")
                        continue
                    handle_command_key(char)
                    continue
                if time.time() - last_blink >= 0.45:
                    cursor_visible = not cursor_visible
                    redraw(cursor_visible)
                    last_blink = time.time()
                time.sleep(0.03)
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    import termios
    import tty
    import select

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        while True:
            readable, _, _ = select.select([sys.stdin], [], [], 0.05)
            if readable:
                char = sys.stdin.read(1)
                if char in ("\r", "\n"):
                    commit()
                    return "".join(buffer)
                if char == "\x03":
                    raise KeyboardInterrupt
                if char in ("\x7f", "\b"):
                    handle_command_key("backspace")
                    continue
                if char == "\t":
                    handle_command_key("tab")
                    continue
                if char == "\x1b":
                    seq = sys.stdin.read(1)
                    if seq == "[":
                        code = sys.stdin.read(1)
                        if code == "3":
                            tail = sys.stdin.read(1)
                            if tail == "~":
                                handle_command_key("delete")
                            continue
                        arrows = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end"}
                        handle_command_key(arrows.get(code, ""))
                    continue
                handle_command_key(char)
                continue
            if time.time() - last_blink >= 0.45:
                cursor_visible = not cursor_visible
                redraw(cursor_visible)
                last_blink = time.time()
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def render_centered_block(lines, block_width, bg="#0000A8"):
    fill_screen(bg)
    width, height = terminal_size()
    start_row = max(1, (height - len(lines)) // 2 + 1)
    start_col = max(1, (width - block_width) // 2 + 1)
    for index, line in enumerate(lines):
        sys.stdout.write(f"\033[{start_row + index};{start_col}H{line}")
    sys.stdout.flush()


def loading_message(message, seconds, color="white", note=None, type_message=True, background=None):
    start = time.time()
    bg = background or COLOR_NAMES["black"]
    fill_screen(bg)
    if type_message:
        typewriter(message, color, delay=0.015, end="")
    else:
        sys.stdout.write(raw_color_text(message, color, bg))
        sys.stdout.flush()

    while time.time() - start < seconds:
        for dots in (".", "..", "...", "   "):
            if time.time() - start >= seconds:
                break
            sys.stdout.write("\r" + raw_color_text(f"{message}{dots}", color, bg))
            sys.stdout.flush()
            if note:
                sys.stdout.write(f"\n{raw_color_text(note, color, bg)}\033[F")
                sys.stdout.flush()
            time.sleep(0.25)
    print()
    if note:
        print()


def fake_startup_log():
    lines = [
        "nOS kernel command line: quiet splash root=/dev/nvme0n1p2",
        "ACPI: Early table checksum verification enabled",
        "ACPI: SSDT 0x00000000BEE76000 0008B2 loaded",
        "CPU: Intel(R) Core(TM) i7-4790K CPU @ 4.00GHz",
        "CPU: Spectre V2 mitigation enabled",
        "Memory: 19938M available, 1024M reserved",
        "PCI: probing bus 0000:00",
        "PCI: bridge configuration complete",
        "DMAR: IOMMU enabled",
        "clocksource: Switched to clocksource tsc",
        "nvme nvme0: pci function 0000:01:00.0",
        "nvme nvme0: 4/0/0 default/read/poll queues",
        "EXT4-fs (nvme0n1p2): mounted filesystem with ordered data mode",
        "systemd[1]: Mounted Kernel Configuration File System.",
        "systemd[1]: Mounted Temporary Directory /tmp.",
        "systemd[1]: Started Journal Service.",
        "systemd[1]: Reached target Local File Systems.",
        "systemd[1]: Reached target Basic System.",
        "udevd[322]: starting version 255.6-2-arch",
        "usbcore: registered new interface driver usbfs",
        "usbcore: registered new interface driver hub",
        "usbcore: registered new interface driver usbhid",
        "input: AT Translated Set 2 keyboard as /devices/platform/i8042/serio0/input/input0",
        "snd_hda_intel 0000:00:1b.0: bound 0000:00:02.0",
        "nvidia: loading out-of-tree module taints kernel.",
        "nvidia-modeset: Loading NVIDIA Kernel Mode Setting Driver",
        "NetworkManager: link enp3s0 is up",
        "NetworkManager: DHCPv4 address 192.168.1.42/24",
        "audit: type=1130 audit(1718441102.233:8): unit=NetworkManager comm=\"systemd\"",
        "dbus-daemon[412]: successfully activated service 'org.freedesktop.systemd1'",
        "polkitd[525]: started daemon version 124",
        "gdm.service: reached graphical login target",
        "nOS-login[611]: pre-auth shell initialized",
        "nOS-display[622]: terminal framebuffer ready",
        "nOS-config[640]: probing local configuration",
        "nOS-config[641]: config path resolved to sys/config.txt",
    ]
    start = time.time()
    stamp = random.uniform(0.001, 0.08)
    while time.time() - start < 3:
        stamp += random.uniform(0.002, 0.19)
        print_colored(f"[{stamp:12.6f}] {random.choice(lines)}", "white")
        time.sleep(random.choice((0.008, 0.014, 0.022, 0.035, 0.075, 0.14)))


def spinner_line(message, seconds, color="white"):
    start = time.time()
    index = 0
    while time.time() - start < seconds:
        frame = SPINNER_FRAMES[index % len(SPINNER_FRAMES)]
        sys.stdout.write(f"\r{COLOR_MAP.get(color, '')}{message} {frame}{COLOR_MAP['reset']}")
        sys.stdout.flush()
        index += 1
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
    sys.stdout.flush()


def read_boot_key():
    if os.name == "nt":
        import msvcrt

        if not msvcrt.kbhit():
            return None
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()
            return {
                "S": "delete",
                "H": "up",
                "P": "down",
                "K": "left",
                "M": "right",
                "D": "f10",
                "\x86": "f12",
            }.get(key)
        if key == "\x1b":
            return "escape"
        if key in ("\r", "\n"):
            return "enter"
        return key.lower()

    import select

    readable, _, _ = select.select([sys.stdin], [], [], 0)
    if not readable:
        return None
    key = sys.stdin.read(1)
    if key == "\x1b":
        return "escape"
    if key == "\x7f":
        return "delete"
    if key in ("\r", "\n"):
        return "enter"
    return key.lower()


def bios_line(text="", fg="#FFFFFF", bg="#000080", width=None):
    width = width or terminal_size().columns
    print(raw_color_text(text[:width].ljust(width), fg, bg))


def award_cell(label, selected=False, width=31):
    prefix = "► "
    text = f"{prefix}{label}"
    fg = "#FFFFFF" if selected else "#FFFF00"
    bg = "#C00000" if selected else "#0000A8"
    return raw_color_text(text[:width].ljust(width), fg, bg)


def award_plain(text, fg="#FFFFFF", bg="#0000A8", width=None):
    width = width or terminal_size().columns
    return raw_color_text(text[:width].ljust(width), fg, bg)


def bios_split_line(left_text, right_text, left_width, right_width, left_fg="#FFFFFF", right_fg="#FFFFFF", bg="#0000A8"):
    left = left_text[:left_width].ljust(left_width)
    right = right_text[:right_width].ljust(right_width)
    return (
        raw_color_text("║", "#FFFFFF", bg)
        + raw_color_text(left, left_fg, bg)
        + raw_color_text("║", "#FFFFFF", bg)
        + raw_color_text(right, right_fg, bg)
        + raw_color_text("║", "#FFFFFF", bg)
    )


def award_message_screen(message, seconds=2):
    box_width = min(terminal_size().columns, 78)
    lines = [
        raw_color_text("CMOS Setup Utility - Copyright (C) 1984-1999 Award Software".center(box_width), "#FFFFFF", "#0000A8"),
        raw_color_text(" " * box_width, "#FFFFFF", "#0000A8"),
        raw_color_text(f"  {message}".ljust(box_width), "#FFFF00", "#0000A8"),
    ]
    render_centered_block(lines, box_width, "#0000A8")
    time.sleep(seconds)


def reset_config_from_bios():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


def bios_menu():
    selected = 0
    items = [
        "Standard CMOS Features",
        "Advanced BIOS Features",
        "Advanced Chipset Features",
        "Integrated Peripherals",
        "Power Management Setup",
        "PnP/PCI Configurations",
        "PC Health Status",
        "Delete nOS Configuration",
        "Frequency/Voltage Control",
        "Load Fail-Safe Defaults",
        "Load Optimized Defaults",
        "Set Supervisor Password",
        "Set User Password",
        "Save & Exit Setup",
        "Exit Without Saving",
    ]
    reset_index = 7
    save_index = 13
    exit_index = 14

    while True:
        width = terminal_size().columns
        left_items = items[:8]
        right_items = items[8:]
        box_width = min(width, 78)
        inner_width = box_width - 2
        left_width = (inner_width - 1) // 2
        right_width = inner_width - left_width - 1
        border = "═" * (box_width - 2)

        lines = [
            raw_color_text("CMOS Setup Utility - Copyright (C) 1984-1999 Award Software".center(box_width), "#FFFFFF", "#0000A8"),
            raw_color_text(f"╔{border}╗", "#FFFFFF", "#0000A8"),
        ]
        for row in range(8):
            left = award_cell(left_items[row], selected == row, left_width)
            right_label = right_items[row] if row < len(right_items) else ""
            right_index = row + 8
            right = award_cell(right_label, selected == right_index, right_width) if right_label else award_plain("", width=right_width)
            lines.append(raw_color_text("║", "#FFFFFF", "#0000A8") + left + raw_color_text("║", "#FFFFFF", "#0000A8") + right + raw_color_text("║", "#FFFFFF", "#0000A8"))
        lines.extend([
            raw_color_text(f"╠{'═' * left_width}╦{'═' * right_width}╣", "#FFFFFF", "#0000A8"),
            bios_split_line("Esc : Quit", "↑ ↓ ← →   : Select Item", left_width, right_width),
            bios_split_line("F10 : Save & Exit Setup", "Enter    : Select", left_width, right_width),
            raw_color_text(f"╠{border}╣", "#FFFFFF", "#0000A8"),
        ])
        help_text = "Delete config.txt and reboot..." if selected == reset_index else "Time, Date, Hard Disk Type..."
        if selected in (save_index, exit_index):
            help_text = "Reboot using the only available boot target..."
        lines.append(raw_color_text(f"║{help_text.center(box_width - 2)}║", "#FFFF00", "#0000A8"))
        lines.append(raw_color_text(f"╚{border}╝", "#FFFFFF", "#0000A8"))
        render_centered_block(lines, box_width, "#0000A8")

        key = read_boot_key()
        if key == "up":
            if selected > 0:
                selected -= 1
        elif key == "down":
            if selected < len(items) - 1:
                selected += 1
        elif key == "left" and selected >= 8:
            selected -= 8
        elif key == "right" and selected < 8 and selected + 8 < len(items):
            selected += 8
        elif key in ("r", "enter") and selected == reset_index:
            reset_config_from_bios()
            award_message_screen("config.txt deleted. Rebooting...", 2)
            clear_screen()
            return "reboot"
        elif key == "escape":
            clear_screen()
            return "reboot"
        elif key == "f10":
            clear_screen()
            return "reboot"
        elif key == "enter" and selected in (save_index, exit_index):
            clear_screen()
            return "reboot"

        time.sleep(0.08)


def boot_manager():
    selected = 0
    items = ["nOS Boot Volume"]
    while True:
        width = min(terminal_size().columns, 78)
        inner_width = width - 2
        border = "═" * inner_width
        lines = [
            raw_color_text("Award Boot Manager".center(width), "#FFFFFF", "#0000A8"),
            raw_color_text(f"╔{border}╗", "#FFFFFF", "#0000A8"),
            raw_color_text(("║ Select boot device:".ljust(width - 1) + "║")[:width], "#FFFF00", "#0000A8"),
            raw_color_text(("║".ljust(width - 1) + "║")[:width], "#FFFFFF", "#0000A8"),
        ]
        for index, item in enumerate(items):
            bg = "#C00000" if index == selected else "#0000A8"
            fg = "#FFFFFF" if index == selected else "#FFFF00"
            line = raw_color_text("║", "#FFFFFF", "#0000A8")
            line += raw_color_text(f" ► {item}".ljust(inner_width), fg, bg)
            line += raw_color_text("║", "#FFFFFF", "#0000A8")
            lines.append(line)
        lines.extend([
            raw_color_text(("║".ljust(width - 1) + "║")[:width], "#FFFFFF", "#0000A8"),
            raw_color_text(("║ Enter : Boot    Esc : Continue normal boot".ljust(width - 1) + "║")[:width], "#FFFFFF", "#0000A8"),
            raw_color_text(f"╚{border}╝", "#FFFFFF", "#0000A8"),
        ])
        render_centered_block(lines, width, "#0000A8")

        key = read_boot_key()
        if key in ("enter", "escape"):
            clear_screen()
            return None
        time.sleep(0.08)


def fake_boot_screen():
    clear_screen()
    fake_startup_log()
    clear_screen()
    spinner_line("Starting nOS", 1.4, "white")
    clear_screen()
    banner_lines = read_banner()
    if banner_lines:
        banner_width = max((len(line) for line in banner_lines), default=4)
        render_centered_block(
            [raw_color_text(line.center(banner_width), COLOR_NAMES["white"], COLOR_NAMES["black"]) for line in banner_lines],
            banner_width,
            COLOR_NAMES["black"],
        )
    else:
        render_centered_block([raw_color_text("nOS.".center(4), COLOR_NAMES["white"], COLOR_NAMES["black"])], 4, COLOR_NAMES["black"])
    print_at_bottom_center("[DEL] ENTER BIOS | [F12] BOOT MENU", "white")

    start = time.time()
    index = 0
    while time.time() - start < 10:
        key = read_boot_key()
        if key == "delete":
            return bios_menu()
        if key == "f12":
            return boot_manager()
        print_at_bottom_right(SPINNER_FRAMES[index % len(SPINNER_FRAMES)], "white")
        index += 1
        time.sleep(0.1)
    clear_screen()
    return None


def black_screen_pause(min_seconds=2.5, max_seconds=3.5):
    clear_screen()
    time.sleep(random.uniform(min_seconds, max_seconds))


def repair_config_screen():
    width, height = terminal_size()
    fill_screen("#0000A8")
    lines = [
        "A critical error occured".center(width),
        "".center(width),
        "Repair nOS".center(width),
        "".center(width),
        "The system configuration is damaged or empty.".center(width),
        "Press any key to repair nOS and reboot.".center(width),
    ]
    rendered = [raw_color_text(line, "#FFFFFF", "#0000A8") for line in lines]
    render_centered_block(rendered, width, "#0000A8")

    start = time.time()
    while time.time() - start < 3:
        if read_boot_key() is not None:
            break
        time.sleep(0.08)

    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return "missing", None

    config = {}
    has_kv = False
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            config[key] = value
            has_kv = True

    if not has_kv:
        return "corrupt", None

    config = {**DEFAULT_CONFIG, **config}
    if "system_id" not in config or not config.get("system_id"):
        config["system_id"] = DEFAULT_SYSTEM_ID
    if "totaluptime" not in config:
        config["totaluptime"] = config.get("uptime_seconds", "0")
    records = user_records_from_config(config)
    if not records and config.get("username"):
        records = [normalize_user_record({
            "username": config.get("username", ""),
            "password": config.get("password", ""),
            "sudo": True,
        })]
    if records and not config.get("username"):
        config["username"] = records[0]["username"]
        config["password"] = records[0]["password"]
    if records:
        save_user_records(config, records)

    if not validate_loaded_config(config):
        return "corrupt", None

    return "ok", config


def validate_loaded_config(config):
    required_keys = ("username", "password", "primary", "secondary", "tertiary", "background", "system_id")
    for key in required_keys:
        if not config.get(key):
            return False
    for key in ("primary", "secondary", "tertiary", "background"):
        if config.get(key) not in COLOR_MAP:
            return False
    try:
        int(str(config.get("totaluptime", "0")))
    except ValueError:
        return False
    if not user_records_from_config(config):
        return False
    return True


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")


def validate_color(color, fallback, config=None):
    if color in COLOR_MAP and color != "reset":
        return color
    if config:
        print_config_colored(f"Unknown color '{color}'. Using {fallback}.", "red", config)
    else:
        print_colored(f"Unknown color '{color}'. Using {fallback}.", "red")
    return fallback


def read_color_choice(prompt, fallback):
    choice = read_line_with_background([(prompt, "white")], {
        "background": DEFAULT_CONFIG["background"],
        "secondary": "white",
    }).strip().lower()
    if not choice:
        return fallback
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(CONFIG_COLOR_ORDER):
            return CONFIG_COLOR_ORDER[index]
    return validate_color(choice, fallback)


def masked_input(prompt, mask="⍟", config=None):
    if config:
        return read_line_with_background([(prompt, config["secondary"])], config, mask=mask).strip()
    else:
        print_colored(prompt, "white", end="")
    if os.name == "nt":
        import msvcrt

        chars = []
        while True:
            char = msvcrt.getwch()
            if char in ("\r", "\n"):
                print()
                return "".join(chars)
            if char == "\003":
                raise KeyboardInterrupt
            if char == "\b":
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            chars.append(char)
            sys.stdout.write(mask)
            sys.stdout.flush()

    import termios
    import tty

    chars = []
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)
            if char in ("\r", "\n"):
                print()
                return "".join(chars)
            if char == "\x03":
                raise KeyboardInterrupt
            if char in ("\x7f", "\b"):
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            chars.append(char)
            sys.stdout.write(mask)
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def display_color_palette():
    print()
    half = len(CONFIG_COLOR_ORDER) // 2
    for row in range(half):
        left_index = row + 1
        right_index = row + half + 1
        left_name = CONFIG_COLOR_ORDER[row]
        right_name = CONFIG_COLOR_ORDER[row + half]
        padding = " " * max(1, 18 - len(left_name))
        left = f"{left_index:2}. {color_text('████', left_name)} {color_text(left_name, left_name)}{padding}"
        right = f"{right_index:2}. {color_text('████', right_name)} {color_text(right_name, right_name)}"
        print(f"{left}  {right}")
    print()


def line_with_background(text, color, config):
    bg = config.get("background", DEFAULT_CONFIG["background"])
    return compose_colored_line([(text, color)], bg)


def neofetch_palette_segments():
    return [[("███", color) for color in row] for row in NEOFETCH_PALETTE_ROWS]


def setup_config():
    print_colored("First Boot: System Configuration", "white")
    loading_message("No configuration file found. Creating one", 2, "white")

    setup_prompt_config = {
        "background": DEFAULT_CONFIG["background"],
        "secondary": "white",
        "primary": "white",
        "tertiary": "red",
    }
    username = prompt_config_value("username: ", setup_prompt_config, DEFAULT_CONFIG["username"])
    password = masked_input("password: ", config=setup_prompt_config).strip() or DEFAULT_CONFIG["password"]
    first_name = prompt_config_value("first name: ", setup_prompt_config, "")
    last_name = prompt_config_value("last name: ", setup_prompt_config, "")
    birth_date = prompt_config_value("birth date: ", setup_prompt_config, "")

    display_color_palette()
    primary = read_color_choice("primary color, used for accent: ", "white")
    secondary = read_color_choice("secondary color, used for text: ", "white")
    tertiary = read_color_choice("tertiary color, used for critical informations: ", "red")
    background = read_color_choice("background color: ", "black")

    initial_user = normalize_user_record({
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "sudo": True,
        "totaluptime": "0",
    })

    config = {
        "username": username,
        "password": password,
        "system_id": DEFAULT_SYSTEM_ID,
        "primary": primary,
        "secondary": secondary,
        "tertiary": tertiary,
        "background": background,
        "totaluptime": "0",
        "uptime_seconds": "0",
        "users": json.dumps([initial_user], ensure_ascii=False),
    }
    loading_message("Writing out config file", 1, "white")
    save_config(config)
    black_screen_pause()
    return config


def config_has_machine_specs(config):
    return all(key in config and config[key] for key in SPEC_KEYS)


def ensure_machine_specs(config):
    if config_has_machine_specs(config):
        loading_message("Reading machine specs in config file", 0.35, "white", background=COLOR_NAMES["black"])
        return config

    loading_message(
        "Scanning machine specifications",
        random.uniform(0.35, 0.85),
        "white",
        background=COLOR_NAMES["black"],
    )
    for key, value in MACHINE_SPECS.items():
        config[f"spec_{key}"] = value
    save_runtime_config(config)
    return config


def get_uptime(config):
    seconds = int(float(config.get("totaluptime", config.get("uptime_seconds", "0"))))
    if "_session_start" in config:
        seconds += int(time.time() - float(config["_session_start"]))
    return str(timedelta(seconds=seconds))


def save_runtime_config(config):
    now = time.time()
    elapsed = int(now - float(config.get("_session_start", now)))
    previous = int(float(config.get("totaluptime", config.get("uptime_seconds", "0"))))
    total = previous + elapsed
    config["totaluptime"] = str(total)
    config["uptime_seconds"] = str(total)
    config["_session_start"] = str(now)

    current_user = config.get("_current_user")
    user_session_start = config.get("_user_session_start")
    if current_user and user_session_start is not None:
        records = user_records_from_config(config)
        user_elapsed = int(now - float(user_session_start))
        for record in records:
            if record["username"] == current_user:
                record["totaluptime"] = str(int(float(record.get("totaluptime", "0"))) + user_elapsed)
                break
        save_user_records(config, records)
        config["_user_session_start"] = str(now)

    persisted = {key: value for key, value in config.items() if not key.startswith("_")}
    save_config(persisted)


def normalize_user_record(record):
    normalized = {
        "username": "",
        "password": "",
        "first_name": "",
        "last_name": "",
        "birth_date": "",
        "sudo": False,
        "totaluptime": "0",
    }
    if isinstance(record, dict):
        normalized.update(record)
    normalized["username"] = str(normalized.get("username", "")).strip()
    normalized["password"] = str(normalized.get("password", ""))
    normalized["first_name"] = str(normalized.get("first_name", "")).strip()
    normalized["last_name"] = str(normalized.get("last_name", "")).strip()
    normalized["birth_date"] = str(normalized.get("birth_date", "")).strip()
    sudo_value = normalized.get("sudo", False)
    if isinstance(sudo_value, str):
        sudo_value = sudo_value.strip().lower() in ("1", "true", "yes", "y", "on")
    normalized["sudo"] = bool(sudo_value)
    try:
        normalized["totaluptime"] = str(int(float(normalized.get("totaluptime", "0"))))
    except ValueError:
        normalized["totaluptime"] = "0"
    return normalized


def user_records_from_config(config):
    raw = config.get("users", "")
    if not raw:
        if config.get("username"):
            return [normalize_user_record({
                "username": config.get("username", ""),
                "password": config.get("password", ""),
                "sudo": True,
            })]
        return []

    try:
        records = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(records, list):
        return []
    return [normalize_user_record(record) for record in records if isinstance(record, dict)]


def save_user_records(config, records):
    config["users"] = json.dumps([normalize_user_record(record) for record in records], ensure_ascii=False)


def find_user_record(config, username):
    username = str(username).strip()
    for record in user_records_from_config(config):
        if record["username"] == username:
            return record
    return None


def update_user_record(config, updated_record):
    records = user_records_from_config(config)
    for index, record in enumerate(records):
        if record["username"] == updated_record["username"]:
            records[index] = normalize_user_record(updated_record)
            save_user_records(config, records)
            return True
    records.append(normalize_user_record(updated_record))
    save_user_records(config, records)
    return True


def prompt_config_value(prompt, config, default=""):
    prompt_segments = [(prompt, config.get("secondary", DEFAULT_CONFIG["secondary"]))]
    value = read_line_with_background(prompt_segments, config).strip()
    return value or default


def user_full_name(record):
    parts = [record.get("first_name", "").strip(), record.get("last_name", "").strip()]
    return " ".join(part for part in parts if part).strip()


def user_summary_lines(record, active=False):
    name = user_full_name(record) or "(no name)"
    lines = [
        f"username: {record['username']}",
        f"name: {name}",
        f"birth date: {record.get('birth_date', '') or '(unknown)'}",
        f"sudo: {'yes' if record.get('sudo') else 'no'}",
        f"total uptime: {timedelta(seconds=int(record.get('totaluptime', '0')))}",
    ]
    if active:
        lines.append("session: active")
    return lines


def prompt_new_user_record(config, default_sudo=False):
    username = prompt_config_value("username: ", config)
    password = masked_input("password: ", config=config).strip()
    first_name = prompt_config_value("first name: ", config, "")
    last_name = prompt_config_value("last name: ", config, "")
    birth_date = prompt_config_value("birth date: ", config, "")
    return normalize_user_record({
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "sudo": bool(default_sudo),
        "totaluptime": "0",
    })


def update_active_user_uptime(config):
    current = config.get("_current_user")
    if not current:
        return
    started = float(config.get("_user_session_start", time.time()))
    elapsed = int(time.time() - started)
    record = find_user_record(config, current)
    if not record:
        return
    total = int(float(record.get("totaluptime", "0"))) + elapsed
    record["totaluptime"] = str(total)
    update_user_record(config, record)
    config["_user_session_start"] = str(time.time())


def begin_user_session(config, username):
    config["_current_user"] = username
    config["_user_session_start"] = str(time.time())


def end_user_session(config):
    update_active_user_uptime(config)
    config.pop("_current_user", None)
    config.pop("_user_session_start", None)


def normalize_comms_pair(left, right):
    left = str(left).strip()
    right = str(right).strip()
    if not left or not right or left == right:
        return None
    return left, right


def load_session_state(left, right):
    return read_json_file(comms_session_path(left, right), default={
        "status": "idle",
        "participants": [left, right],
        "messages": [],
    })


def save_session_state(left, right, state):
    write_json_file(comms_session_path(left, right), state)


def poll_connected_messages(config):
    peer = config.get("_connected_peer")
    if not peer:
        return
    system_id = current_system_id(config)
    state = load_session_state(system_id, peer)
    if state.get("status") != "active":
        config.pop("_connected_peer", None)
        config.pop("_comms_cursor", None)
        return
    messages = state.get("messages", [])
    cursor = int(config.get("_comms_cursor", 0))
    if cursor > len(messages):
        cursor = 0
    for message in messages[cursor:]:
        if message.get("from") != system_id:
            sender = message.get("from", peer)
            text = message.get("text", "")
            print(compose_colored_line([(f"[{sender}] ", config["primary"]), (text, config["secondary"])], config.get("background", DEFAULT_CONFIG["background"])))
    config["_comms_cursor"] = str(len(messages))


def pending_connection_requests(system_id):
    ensure_comms_root()
    request_dir = os.path.join(COMMS_ROOT, "requests")
    requests = []
    for name in sorted(os.listdir(request_dir)):
        path = os.path.join(request_dir, name)
        if not os.path.isfile(path):
            continue
        payload = read_json_file(path)
        if payload and payload.get("target") == system_id and payload.get("status", "pending") == "pending":
            requests.append((path, payload))
    return requests


def request_connection(config, target_system):
    source = current_system_id(config)
    target_system = str(target_system).strip()
    if not target_system:
        return False, "usage: connect <system>"
    if target_system == source:
        return False, "cannot connect to the same system"
    if target_system not in SYSTEM_IDS and not os.path.isdir(system_folder(target_system)):
        return False, f"system not found: {target_system}"
    if config.get("_connected_peer"):
        return False, f"already connected to {config['_connected_peer']}"

    request = {
        "source": source,
        "target": target_system,
        "status": "pending",
        "created_at": time.time(),
    }
    request_path = comms_request_path(source, target_system)
    write_json_file(request_path, request)
    print_config_colored(f"waiting for answer from {target_system}", config["secondary"], config)

    start = time.time()
    while time.time() - start < 20:
        payload = read_json_file(request_path, default=None)
        if payload and payload.get("status") == "denied":
            try:
                os.remove(request_path)
            except OSError:
                pass
            return False, "exit code 1: denied"
        session = read_json_file(comms_session_path(source, target_system), default=None)
        if session and session.get("status") == "active":
            config["_connected_peer"] = target_system
            config["_comms_cursor"] = str(len(session.get("messages", [])))
            return True, "exit code 0: connection succesful"
        time.sleep(0.25)

    return False, "connection timeout"


def answer_connection_request(config, request, accepted):
    source = request["source"]
    target = request["target"]
    request_path = comms_request_path(source, target)
    if accepted:
        session = {
            "status": "active",
            "participants": [source, target],
            "messages": [],
            "created_at": time.time(),
        }
        save_session_state(source, target, session)
        try:
            os.remove(request_path)
        except OSError:
            pass
        config["_connected_peer"] = source
        config["_comms_cursor"] = "0"
        return True, "request accepted"

    request["status"] = "denied"
    write_json_file(request_path, request)
    return False, "denied"


def disconnect_peer(config):
    peer = config.get("_connected_peer")
    if not peer:
        return False, "not connected"
    system_id = current_system_id(config)
    session_path = comms_session_path(system_id, peer)
    state = read_json_file(session_path, default=None)
    if state:
        state["status"] = "closed"
        save_session_state(system_id, peer, state)
    config.pop("_connected_peer", None)
    config.pop("_comms_cursor", None)
    return True, f"disconnected from {peer}"


def send_peer_message(config, text):
    peer = config.get("_connected_peer")
    if not peer:
        return False, "not connected"
    system_id = current_system_id(config)
    state = load_session_state(system_id, peer)
    if state.get("status") != "active":
        return False, "session not active"
    state.setdefault("messages", []).append({
        "from": system_id,
        "text": text,
        "timestamp": time.time(),
    })
    save_session_state(system_id, peer, state)
    config["_comms_cursor"] = str(len(state["messages"]))
    return True, None


def load_resource_sections():
    if not os.path.exists(LOGO_FILE):
        return {}

    valid_names = {"logo", "banner"}
    sections = {}
    current_name = None
    current_lines = []

    with open(LOGO_FILE, "r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.rstrip("\r\n")
            stripped = line.strip().lower()

            if current_name is None:
                if stripped in valid_names:
                    current_name = stripped
                    current_lines = []
                continue

            if stripped == "end":
                if current_name not in sections and current_lines:
                    sections[current_name] = current_lines[:]
                current_name = None
                current_lines = []
                continue

            if stripped in valid_names:
                current_name = stripped
                current_lines = []
                continue

            current_lines.append(line)

    return sections


def read_resource(name):
    sections = load_resource_sections()
    lines = sections.get(name, [])
    cleaned = [line.rstrip() for line in lines if line.strip()]
    return cleaned


def read_logo():
    return read_resource("logo")


def read_banner():
    return read_resource("banner")


def neofetch_palette_lines(config):
    background = config.get("background", DEFAULT_CONFIG["background"])
    return ["".join(color_text_on_background("███", color, background) for color in row) for row in NEOFETCH_PALETTE_ROWS]


def shell_cwd(config):
    return normalize_virtual_path(config.get("_cwd", ""))


def set_shell_cwd(config, cwd):
    config["_cwd"] = normalize_virtual_path(cwd)


def format_fs_entry(name, is_dir, config):
    suffix = "/" if is_dir else ""
    color = config["primary"] if is_dir else config["secondary"]
    return name + suffix, color


def fs_copy_item(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def fs_set_clipboard(config, path, mode):
    config["_clipboard"] = {"path": path, "mode": mode}


def fs_paste_clipboard(config, destination=None):
    clipboard = config.get("_clipboard")
    if not clipboard:
        return False, "clipboard is empty"

    destination = destination or config.get("_cwd", "")
    dest_dir = resolve_virtual_path(destination or ".", config.get("_cwd", ""))
    if not os.path.isdir(dest_dir):
        return False, "destination is not a directory"

    source = clipboard["path"]
    if not os.path.exists(source):
        return False, "clipboard item no longer exists"

    name = os.path.basename(source.rstrip("\\/"))
    target = os.path.join(dest_dir, name)
    if os.path.exists(target):
        return False, f"target already exists: {name}"

    if clipboard["mode"] == "cut":
        shutil.move(source, target)
        config["_clipboard"] = None
    else:
        fs_copy_item(source, target)
    return True, f"pasted {name}"


def fs_list_command(config, args):
    target = args[0] if args else "."
    abs_path = resolve_virtual_path(target, config.get("_cwd", ""))
    if not os.path.exists(abs_path):
        return False, f"not found: {target}"
    if os.path.isfile(abs_path):
        entry_text, entry_color = format_fs_entry(os.path.basename(abs_path), False, config)
        print(compose_colored_line([(entry_text, entry_color)], config.get("background", DEFAULT_CONFIG["background"])))
        return True, None

    entries = list_directory_entries(abs_path)
    if not entries:
        print_config_colored("(empty)", config["secondary"], config)
        return True, None
    for name, is_dir in entries:
        entry_text, entry_color = format_fs_entry(name, is_dir, config)
        print(compose_colored_line([(entry_text, entry_color)], config.get("background", DEFAULT_CONFIG["background"])))
    return True, None


def fs_change_directory(config, args):
    target = "".join(args) if args else ""
    abs_path = resolve_virtual_path(target or ".", config.get("_cwd", ""))
    if not os.path.exists(abs_path):
        return False, f"not found: {target}"
    if not os.path.isdir(abs_path):
        return False, f"not a directory: {target}"
    set_shell_cwd(config, path_from_files_root(abs_path))
    return True, virtual_path_label(config.get("_cwd", ""))


def fs_make_directory(config, args):
    if not args:
        return False, "usage: mkdir <path>"
    target = resolve_virtual_path(args[0], config.get("_cwd", ""))
    if os.path.exists(target):
        return False, "path already exists"
    os.makedirs(target, exist_ok=False)
    return True, f"created {args[0]}"


def fs_remove_file(config, args):
    if not args:
        return False, "usage: rm <file>"
    target = resolve_virtual_path(args[0], config.get("_cwd", ""))
    if not os.path.exists(target):
        return False, "file not found"
    if os.path.isdir(target):
        return False, "use rmdir for directories"
    os.remove(target)
    return True, f"removed {args[0]}"


def fs_remove_directory(config, args):
    if not args:
        return False, "usage: rmdir <dir>"
    target = resolve_virtual_path(args[0], config.get("_cwd", ""))
    if not os.path.exists(target):
        return False, "directory not found"
    if not os.path.isdir(target):
        return False, "not a directory"
    os.rmdir(target)
    return True, f"removed {args[0]}"


def fs_copy_command(config, args, cut=False):
    if not args:
        return False, "usage: copy <path>" if not cut else "usage: cut <path>"
    source = resolve_virtual_path(args[0], config.get("_cwd", ""))
    if not os.path.exists(source):
        return False, "source not found"
    fs_set_clipboard(config, source, "cut" if cut else "copy")
    return True, f"{'cut' if cut else 'copied'} {args[0]}"


def fs_paste_command(config, args):
    destination = args[0] if args else None
    return fs_paste_clipboard(config, destination)


def nano_read_file(abs_path):
    if not os.path.exists(abs_path):
        return [""]
    with open(abs_path, "r", encoding="utf-8", errors="replace") as file:
        lines = file.read().splitlines()
    return lines if lines else [""]


def nano_write_file(abs_path, lines):
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def run_virtual_python_file(config, path_arg, args=None):
    args = args or []
    target = resolve_virtual_path(path_arg, config.get("_cwd", ""))
    if not os.path.exists(target):
        return False, f"file not found: {path_arg}"
    if os.path.isdir(target):
        return False, "cannot execute a directory"
    if not target.lower().endswith(".py"):
        return False, "can only execute .py files"

    with open(target, "r", encoding="utf-8", errors="replace") as file:
        source = file.read()

    old_argv = sys.argv[:]
    old_cwd = os.getcwd()
    namespace = {
        "__name__": "__main__",
        "__file__": target,
        "__package__": None,
    }
    try:
        os.chdir(os.path.dirname(target))
        sys.argv = [path_arg] + args
        exec(compile(source, target, "exec"), namespace, namespace)
    except SystemExit as exc:
        code = getattr(exc, "code", 0)
        if code not in (0, None):
            return False, f"script exited with code {code}"
    except Exception as exc:
        return False, f"script error: {exc}"
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv
    return True, None


def nano_editor(config, path_arg=None):
    ensure_files_root()
    target = resolve_virtual_path(path_arg or "untitled.txt", config.get("_cwd", ""))
    if os.path.isdir(target):
        print_config_colored("nano expects a file path, not a directory", config["tertiary"], config)
        return None

    lines = nano_read_file(target)
    cursor_x = 0
    cursor_y = 0
    offset_x = 0
    offset_y = 0
    dirty = False
    status = "EDIT"
    nano_clipboard = ""

    def clamp_cursor():
        nonlocal cursor_x, cursor_y
        cursor_y = max(0, min(cursor_y, len(lines) - 1))
        cursor_x = max(0, min(cursor_x, len(lines[cursor_y])))

    def read_key():
        if os.name == "nt":
            import msvcrt

            char = msvcrt.getwch()
            if char in ("\r", "\n"):
                return "enter"
            if char == "\x03":
                raise KeyboardInterrupt
            if char == "\t":
                return "tab"
            if char in ("\b", "\x7f"):
                return "backspace"
            if char in ("\x00", "\xe0"):
                code = msvcrt.getwch()
                return {
                    "H": "up",
                    "P": "down",
                    "K": "left",
                    "M": "right",
                    "S": "delete",
                    "G": "home",
                    "O": "end",
                    "D": "f10",
                }.get(code)
            return {
                "\x0f": "ctrl_o",
                "\x12": "ctrl_r",
                "\x0b": "ctrl_k",
                "\x15": "ctrl_u",
                "\x18": "ctrl_x",
                "\x1b": "escape",
            }.get(char, char)

        import termios
        import tty
        import select

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            readable, _, _ = select.select([sys.stdin], [], [], 0.02)
            if not readable:
                return None
            char = sys.stdin.read(1)
            if char in ("\r", "\n"):
                return "enter"
            if char == "\x03":
                raise KeyboardInterrupt
            if char == "\t":
                return "tab"
            if char in ("\x7f", "\b"):
                return "backspace"
            if char == "\x1b":
                readable, _, _ = select.select([sys.stdin], [], [], 0.02)
                if not readable:
                    return "escape"
                seq = sys.stdin.read(1)
                if seq == "[":
                    code = sys.stdin.read(1)
                    if code == "3":
                        if sys.stdin.read(1) == "~":
                            return "delete"
                    return {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end"}.get(code)
                return "escape"
            return {
                "\x0f": "ctrl_o",
                "\x12": "ctrl_r",
                "\x0b": "ctrl_k",
                "\x15": "ctrl_u",
                "\x18": "ctrl_x",
            }.get(char, char)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def prompt_line(message, default=""):
        prompt_buffer = list(default)
        prompt_cursor = len(prompt_buffer)

        def render_prompt():
            render(f"{message}{''.join(prompt_buffer)}", prompt_cursor, len(message))

        while True:
            render_prompt()
            key = read_key()
            if key is None:
                continue
            if key in ("enter", "f10"):
                return "".join(prompt_buffer)
            if key in ("escape", "ctrl_x"):
                return None
            if key == "backspace":
                if prompt_cursor > 0:
                    del prompt_buffer[prompt_cursor - 1]
                    prompt_cursor -= 1
            elif key == "delete":
                if prompt_cursor < len(prompt_buffer):
                    del prompt_buffer[prompt_cursor]
            elif key == "left":
                if prompt_cursor > 0:
                    prompt_cursor -= 1
            elif key == "right":
                if prompt_cursor < len(prompt_buffer):
                    prompt_cursor += 1
            elif key == "home":
                prompt_cursor = 0
            elif key == "end":
                prompt_cursor = len(prompt_buffer)
            elif len(key) == 1 and key.isprintable():
                prompt_buffer.insert(prompt_cursor, key)
                prompt_cursor += 1

    def save_file_as():
        nonlocal target, dirty, status
        chosen = prompt_line("File Name to Write: ", path_from_files_root(target))
        if not chosen:
            return
        target = resolve_virtual_path(chosen, config.get("_cwd", ""))
        if os.path.isdir(target):
            print_config_colored("cannot write to a directory", config["tertiary"], config)
            return
        nano_write_file(target, lines)
        dirty = False
        status = "SAVED"

    def save_file():
        nonlocal dirty, status
        nano_write_file(target, lines)
        dirty = False
        status = "SAVED"

    def open_file_into_buffer():
        nonlocal lines, cursor_x, cursor_y, offset_x, offset_y, dirty, status
        chosen = prompt_line("Read File: ", "")
        if not chosen:
            return
        other = resolve_virtual_path(chosen, config.get("_cwd", ""))
        if os.path.isdir(other):
            print_config_colored("cannot read a directory", config["tertiary"], config)
            return
        new_lines = nano_read_file(other)
        lines[:] = new_lines if new_lines else [""]
        cursor_x = cursor_y = offset_x = offset_y = 0
        dirty = True
        status = "EDIT"

    def render(prompt_text=None, prompt_cursor=0, prompt_prefix_len=0):
        nonlocal offset_x, offset_y
        width, height = terminal_size()
        body_height = max(5, height - 5)
        clamp_cursor()
        if cursor_y < offset_y:
            offset_y = cursor_y
        if cursor_y >= offset_y + body_height:
            offset_y = cursor_y - body_height + 1
        if cursor_x < offset_x:
            offset_x = cursor_x
        if cursor_x >= offset_x + width - 2:
            offset_x = cursor_x - width + 3

        bg = COLOR_NAMES["black"]
        bar_bg = "#000080"
        fill_screen(bg)
        header = f" GNU nano 7.2   {path_from_files_root(target)}"
        status_line = prompt_text if prompt_text is not None else f"Modified: {'yes' if dirty else 'no'}   {status}"
        help_line_1 = "^G Help  ^O Write Out  ^R Read File  ^K Cut  ^U Paste  ^T Execute"
        help_line_2 = "^X Exit  ^C Location  ^_ Go To Line  ^J Justify"
        sys.stdout.write(f"\033[1;1H{raw_color_text(header[:width].ljust(width), '#FFFFFF', bar_bg)}")
        for row in range(body_height):
            sys.stdout.write(f"\033[{row + 2};1H")
            line_index = offset_y + row
            if line_index < len(lines):
                visible = lines[line_index][offset_x:offset_x + width]
                sys.stdout.write(raw_color_text(visible.ljust(width), config["secondary"], bg))
            else:
                sys.stdout.write(raw_color_text(" ".ljust(width), config["secondary"], bg))
        sys.stdout.write(f"\033[{body_height + 2};1H{raw_color_text(status_line[:width].ljust(width), '#FFFFFF', bar_bg)}")
        sys.stdout.write(f"\033[{body_height + 3};1H{raw_color_text(help_line_1[:width].ljust(width), '#FFFFFF', bar_bg)}")
        sys.stdout.write(f"\033[{body_height + 4};1H{raw_color_text(help_line_2[:width].ljust(width), '#FFFFFF', bar_bg)}")

        if prompt_text is not None:
            prompt_pos = prompt_prefix_len + prompt_cursor
            if prompt_pos < width:
                sys.stdout.write(f"\033[{body_height + 2};{prompt_pos + 1}H{raw_color_text('_', '#FFFFFF', bar_bg)}")
        else:
            cursor_screen_y = cursor_y - offset_y + 2
            cursor_screen_x = cursor_x - offset_x + 1
            if 2 <= cursor_screen_y <= body_height + 1:
                line = lines[cursor_y]
                cursor_char = line[cursor_x] if cursor_x < len(line) else "_"
                sys.stdout.write(f"\033[{cursor_screen_y};{cursor_screen_x}H{raw_color_text(cursor_char, config['primary'], bg)}")
        sys.stdout.flush()

    def insert_file_at_cursor(path_arg_inner):
        nonlocal lines, cursor_x, cursor_y, dirty
        source = resolve_virtual_path(path_arg_inner, config.get("_cwd", ""))
        if os.path.isdir(source):
            print_config_colored("cannot insert a directory", config["tertiary"], config)
            return
        insert_lines = nano_read_file(source)
        current = lines[cursor_y]
        before = current[:cursor_x]
        after = current[cursor_x:]
        lines[cursor_y] = before + insert_lines[0]
        for extra in insert_lines[1:]:
            lines.insert(cursor_y + 1, extra)
            cursor_y += 1
        lines.insert(cursor_y + 1, after)
        cursor_y += 1
        cursor_x = 0
        dirty = True

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        render()
        while True:
            key = read_key()
            if key is None:
                continue
            if key in ("ctrl_x", "escape"):
                if dirty:
                    answer = prompt_line("Save modified buffer? (y/n) ", "y")
                    if answer and answer.lower().startswith("y"):
                        save_file()
                    elif answer and answer.lower().startswith("n"):
                        pass
                    else:
                        continue
                clear_with_background(config)
                return None
            elif key in ("ctrl_o", "f10"):
                save_file_as()
            elif key == "ctrl_r":
                chosen = prompt_line("Read File: ", "")
                if chosen:
                    insert_file_at_cursor(chosen)
            elif key == "ctrl_k":
                nano_clipboard = lines[cursor_y]
                del lines[cursor_y]
                if not lines:
                    lines.append("")
                cursor_y = min(cursor_y, len(lines) - 1)
                cursor_x = 0
                dirty = True
            elif key == "ctrl_u":
                if nano_clipboard:
                    line = lines[cursor_y]
                    lines[cursor_y] = line[:cursor_x] + nano_clipboard + line[cursor_x:]
                    cursor_x += len(nano_clipboard)
                    dirty = True
            elif key == "left":
                if cursor_x > 0:
                    cursor_x -= 1
                elif cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = len(lines[cursor_y])
            elif key == "right":
                if cursor_x < len(lines[cursor_y]):
                    cursor_x += 1
                elif cursor_y < len(lines) - 1:
                    cursor_y += 1
                    cursor_x = 0
            elif key == "up":
                if cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = min(cursor_x, len(lines[cursor_y]))
            elif key == "down":
                if cursor_y < len(lines) - 1:
                    cursor_y += 1
                    cursor_x = min(cursor_x, len(lines[cursor_y]))
            elif key == "home":
                cursor_x = 0
            elif key == "end":
                cursor_x = len(lines[cursor_y])
            elif key == "backspace":
                if cursor_x > 0:
                    line = lines[cursor_y]
                    lines[cursor_y] = line[:cursor_x - 1] + line[cursor_x:]
                    cursor_x -= 1
                    dirty = True
                elif cursor_y > 0:
                    prev_len = len(lines[cursor_y - 1])
                    lines[cursor_y - 1] += lines[cursor_y]
                    del lines[cursor_y]
                    cursor_y -= 1
                    cursor_x = prev_len
                    dirty = True
            elif key == "delete":
                line = lines[cursor_y]
                if cursor_x < len(line):
                    lines[cursor_y] = line[:cursor_x] + line[cursor_x + 1:]
                    dirty = True
                elif cursor_y < len(lines) - 1:
                    lines[cursor_y] += lines[cursor_y + 1]
                    del lines[cursor_y + 1]
                    dirty = True
            elif key == "enter":
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x]
                lines.insert(cursor_y + 1, line[cursor_x:])
                cursor_y += 1
                cursor_x = 0
                dirty = True
            elif key == "tab":
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x] + "    " + line[cursor_x:]
                cursor_x += 4
                dirty = True
            elif len(key) == 1 and key.isprintable():
                line = lines[cursor_y]
                lines[cursor_y] = line[:cursor_x] + key + line[cursor_x:]
                cursor_x += 1
                dirty = True
            render()
    except KeyboardInterrupt:
        clear_with_background(config)
        return None
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def display_neofetch(config, current_user=None):
    clear_with_background(config)
    logo_lines = read_logo()
    background = config.get("background", DEFAULT_CONFIG["background"])
    labels = [
        ("OS", config.get("spec_os", MACHINE_SPECS["os"])),
        ("Kernel", config.get("spec_kernel", MACHINE_SPECS["kernel"])),
        ("Uptime", get_uptime(config)),
        ("Packages", config.get("spec_packages", MACHINE_SPECS["packages"])),
        ("Shell", config.get("spec_shell", MACHINE_SPECS["shell"])),
        ("Resolution", config.get("spec_resolution", MACHINE_SPECS["resolution"])),
        ("DE", config.get("spec_de", MACHINE_SPECS["de"])),
        ("WM", config.get("spec_wm", MACHINE_SPECS["wm"])),
        ("WM Theme", config.get("spec_wm_theme", MACHINE_SPECS["wm_theme"])),
        ("Theme", config.get("spec_theme", MACHINE_SPECS["theme"])),
        ("Icons", config.get("spec_icons", MACHINE_SPECS["icons"])),
        ("Terminal", config.get("spec_terminal", MACHINE_SPECS["terminal"])),
        ("CPU", config.get("spec_cpu", MACHINE_SPECS["cpu"])),
        ("GPU", config.get("spec_gpu", MACHINE_SPECS["gpu"])),
        ("Memory", config.get("spec_memory", MACHINE_SPECS["memory"])),
        ("User", current_user or "not logged in"),
    ]

    palette_rows = neofetch_palette_segments()
    total_lines = max(len(logo_lines), len(labels) + 1 + len(palette_rows))
    logo_width = max((len(line) for line in logo_lines), default=0)

    for index in range(total_lines):
        logo = logo_lines[index] if index < len(logo_lines) else ""
        if index < len(labels):
            label, value = labels[index]
            right_segments = [(f"{label}:", config["primary"]), (" ", None), (value, config["secondary"])]
        elif index == len(labels):
            right_segments = []
        else:
            palette_index = index - len(labels) - 1
            right_segments = palette_rows[palette_index] if palette_index < len(palette_rows) else []
        print(
            compose_colored_line(
                [(logo.ljust(logo_width), config["primary"]), ("    ", None)] + right_segments,
                background,
            )
        )


def user_exists(config, username):
    return find_user_record(config, username) is not None


def check_password(config, username, password):
    user = find_user_record(config, username)
    return bool(user and password == user.get("password"))


def show_help(logged_in, config, commands=None):
    commands = commands or (AUTH_COMMANDS if logged_in else PRE_LOGIN_COMMANDS)
    visible_order = ["help"]
    if logged_in:
        visible_order.extend(["clear", "echo", "color", "cd", "ls", "neofetch", "whoami", "user", "login", "connect", "disconnect", "msg", "shutdown", "reboot"])
    else:
        visible_order.extend(["su", "login", "shutdown", "reboot"])
    sudo_order = ["adduser", "mkdir", "rm", "rmdir", "copy", "cut", "paste", "nano"]
    hidden_commands = {"print", "exit", "restart", "cp", "remove", "rs", "rb", "sd", "log", "nf", "list"}

    print_config_colored("", config["secondary"], config)
    for command in visible_order:
        if command in hidden_commands or command not in commands:
            continue
        description = commands[command]
        print(compose_colored_line([("  ", None), (command, config["primary"]), (": " + description, config["secondary"])], config.get("background", DEFAULT_CONFIG["background"])))
    if logged_in:
        current_user = config.get("_current_user")
        current_record = find_user_record(config, current_user) if current_user else None
        if current_record and current_record.get("sudo"):
            for command in sudo_order:
                description = AUTH_COMMANDS.get(command)
                if description:
                    print(compose_colored_line([("  ", None), (command, config["primary"]), (": " + description, config["secondary"])], config.get("background", DEFAULT_CONFIG["background"])))
        else:
            print_config_colored("sudo only:", config["tertiary"], config)
            for command in sudo_order:
                description = AUTH_COMMANDS.get(command)
                if description:
                    print(compose_colored_line([("  ", None), (command, config["primary"]), (": " + description + " [sudo only]", config["tertiary"])], config.get("background", DEFAULT_CONFIG["background"])))
    print_config_colored("", config["secondary"], config)


def shutdown(config):
    save_runtime_config(config)
    loading_message("Shutting down", random.uniform(2, 10), config.get("secondary", DEFAULT_CONFIG["secondary"]), background=config.get("background", DEFAULT_CONFIG["background"]))
    clear_screen()
    time.sleep(2)
    raise SystemExit


def restart(config):
    save_runtime_config(config)
    loading_message(
        "Restarting",
        random.uniform(5, 15),
        config.get("secondary", DEFAULT_CONFIG["secondary"]),
        type_message=False,
        background=config.get("background", DEFAULT_CONFIG["background"]),
    )
    time.sleep(9)
    return "reboot"


def prompt_incoming_connection(config):
    if config.get("_connected_peer"):
        return
    system_id = current_system_id(config)
    requests = pending_connection_requests(system_id)
    if not requests:
        return

    request_path, request = requests[0]
    source = request.get("source", "unknown")
    print_config_colored("incoming connection request", config["secondary"], config)
    print_config_colored(f"from {source}", config["secondary"], config)
    answer = prompt_config_value("would you like to accept (Y/n)? ", config, "y").strip().lower()
    accepted = answer in ("", "y", "yes", "true")
    ok, message = answer_connection_request(config, request, accepted)
    print_config_colored(message, config["secondary"] if ok else config["tertiary"], config)
    if accepted:
        loading_message("Connecting", 2, "white", background=COLOR_NAMES["black"])


def shell(config):
    logged_in_user = None
    history = load_history()
    ensure_files_root()
    set_shell_cwd(config, config.get("_cwd", ""))
    config["_clipboard"] = None
    display_neofetch(config)

    while True:
        try:
            prompt_incoming_connection(config)
            poll_connected_messages(config)
            prompt_user = logged_in_user or "guest"
            logged_in = logged_in_user is not None
            current_user_record = find_user_record(config, logged_in_user) if logged_in_user else None
            commands = AUTH_COMMANDS if logged_in else PRE_LOGIN_COMMANDS
            if current_user_record and not current_user_record.get("sudo"):
                commands = {name: desc for name, desc in commands.items() if name not in SUDO_COMMANDS}
            config["_history"] = history
            config["_commands"] = sorted(commands.keys())
            prompt_path = virtual_path_label(config.get("_cwd", ""))
            raw_input = read_line_with_background(
                [(f"{prompt_user}@nOS:{prompt_path}", config["primary"]), ("> ", config["secondary"])],
                config,
            ).strip()
            if not raw_input:
                continue

            history.append(raw_input)
            save_history(history)

            try:
                parts = shlex.split(raw_input)
            except ValueError:
                print_config_colored("syntax error in command line", config["tertiary"], config)
                continue
            if not parts:
                continue

            alias_map = {
                "login": "su",
                "print": "echo",
            }
            command = alias_map.get(parts[0].lower(), parts[0].lower())
            args = parts[1:]
            if command.startswith("./"):
                ok, message = run_virtual_python_file(config, command[2:], args)
                if not ok and message:
                    print_config_colored(message, config["tertiary"], config)
                continue
            if command == "cd.." and not args:
                command = "cd"
                args = [".."]
            if command == "cd" and len(args) == 1 and args[0] == "..":
                args = [".."]

            if command == "help":
                show_help(logged_in, config, commands)
            elif command in ("exit", "shutdown"):
                shutdown(config)
            elif command in ("restart", "reboot"):
                return restart(config)
            elif command == "connect":
                if not args:
                    print_config_colored("usage: connect <system>", config["tertiary"], config)
                    continue
                ok, message = request_connection(config, args[0])
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
                else:
                    loading_message("Connecting", 2, "white", background=COLOR_NAMES["black"])
                    print_config_colored(message, config["secondary"], config)
            elif command == "disconnect":
                ok, message = disconnect_peer(config)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
                else:
                    print_config_colored(message, config["secondary"], config)
            elif command == "msg":
                if not args:
                    print_config_colored("usage: msg <text>", config["tertiary"], config)
                    continue
                ok, message = send_peer_message(config, " ".join(args))
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "su":
                if not args:
                    print_config_colored("usage: su <user>", config["tertiary"], config)
                    continue

                username = args[0]
                if not user_exists(config, username):
                    print_config_colored("user not found in config file", config["tertiary"], config)
                    continue

                password = masked_input("password: ", config=config).strip()
                if not password:
                    print_config_colored("missing credentials", config["tertiary"], config)
                    continue
                if not check_password(config, username, password):
                    print_config_colored("password incorrect", config["tertiary"], config)
                    continue

                update_active_user_uptime(config)
                logged_in_user = username
                begin_user_session(config, username)
                print(compose_colored_line([("logged in as ", config["secondary"]), (username, config["primary"])], config.get("background", DEFAULT_CONFIG["background"])))
            elif not logged_in:
                if command in AUTH_COMMANDS:
                    print_config_colored("not logged in. use: su <user>", config["tertiary"], config)
                else:
                    print_config_colored(f"unknown command: {command}", config["tertiary"], config)
            elif command in SUDO_COMMANDS and not (current_user_record and current_user_record.get("sudo")):
                print_config_colored("permission denied: sudo required", config["tertiary"], config)
            elif command == "clear":
                clear_with_background(config)
            elif command == "echo":
                print_config_colored(" ".join(args), config["secondary"], config)
            elif command == "color":
                if not args:
                    print_config_colored("usage: color <color>", config["tertiary"], config)
                    continue
                color = validate_color(args[0].lower(), config["secondary"], config)
                print_config_colored("This text is colored.", color, config)
            elif command == "neofetch":
                display_neofetch(config, logged_in_user)
            elif command == "whoami":
                print_config_colored(logged_in_user or "guest", config["secondary"], config)
            elif command == "user":
                if args:
                    target_user = find_user_record(config, args[0])
                    if not target_user:
                        print_config_colored("user not found", config["tertiary"], config)
                    else:
                        for line in user_summary_lines(target_user, active=target_user["username"] == logged_in_user):
                            print_config_colored(line, config["secondary"], config)
                else:
                    print_config_colored(logged_in_user or "guest", config["secondary"], config)
            elif command == "cd":
                ok, message = fs_change_directory(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "ls":
                ok, message = fs_list_command(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "mkdir":
                ok, message = fs_make_directory(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "rm":
                ok, message = fs_remove_file(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "rmdir":
                ok, message = fs_remove_directory(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "copy":
                ok, message = fs_copy_command(config, args, cut=False)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "cut":
                ok, message = fs_copy_command(config, args, cut=True)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
            elif command == "paste":
                ok, message = fs_paste_command(config, args)
                if not ok:
                    print_config_colored(message, config["tertiary"], config)
                else:
                    print_config_colored(message, config["secondary"], config)
            elif command == "adduser":
                new_user = prompt_new_user_record(config, default_sudo=False)
                if not new_user["username"] or find_user_record(config, new_user["username"]):
                    print_config_colored("invalid or existing username", config["tertiary"], config)
                elif not new_user["password"]:
                    print_config_colored("missing password", config["tertiary"], config)
                else:
                    records = user_records_from_config(config)
                    records.append(new_user)
                    save_user_records(config, records)
                    save_runtime_config(config)
                    print_config_colored(f"user created: {new_user['username']}", config["secondary"], config)
            elif command == "nano":
                nano_editor(config, args[0] if args else None)
            else:
                print_config_colored(f"unknown command: {command}", config["tertiary"], config)
        except KeyboardInterrupt:
            print_config_colored("", config["secondary"], config)
            print_config_colored("Use 'exit' to shut down.", config["tertiary"], config)


def boot_once():
    boot_action = fake_boot_screen()
    if boot_action == "reboot":
        return "reboot"

    status, config = load_config()
    if status == "missing":
        setup_config()
        return "reboot"
    if status == "corrupt":
        repair_config_screen()
        return "reboot"

    config["_session_start"] = str(time.time())
    config = ensure_machine_specs(config)
    return shell(config)


def main():
    while True:
        action = boot_once()
        if action != "reboot":
            break


if __name__ == "__main__":
    main()
