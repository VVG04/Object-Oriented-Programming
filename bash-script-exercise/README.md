# Exercise 1 (slide 18): Configure a development environment with Bash

**Statement:** [courses.dallard.tech/linux/bash_exo](https://courses.dallard.tech/linux/bash_exo/)
**Deliverable:** [`env_install.sh`](env_install.sh), a script that sets up Python, pip and Jupyter on macOS or Linux.

---

## 0. Key concepts (read this first)

| Concept | Plain explanation |
| --- | --- |
| **Terminal vs shell** | The *terminal* is the window you type in. The *shell* (bash, zsh) is the program inside it that reads your commands and asks the operating system to run them. One terminal, many possible shells. |
| **Environment variable** | A named value every program can read, like `$HOME` (your home folder), `$PATH` (where the shell looks for commands), `$SHELL` (your login shell), `$OSTYPE` (your OS). Read one with `echo "$HOME"`. |
| **Script** | A text file full of shell commands, run top to bottom. The first line (`#!/usr/bin/env bash`, the *shebang*) says which program should run it. |
| **Package manager** | A program that installs software for you: `brew` on macOS, `apt` on Ubuntu/Debian, `pip` for Python libraries. |

---

## Part 1: Improve your shell experience

### Step 1.1: Which shell am I using?

```bash
ps -p $$          # the shell running RIGHT NOW ($$ = the current process id)
echo "$SHELL"     # your LOGIN shell (the default one), may differ from the above
```

Typical answers: `/bin/zsh` on a modern Mac, `/bin/bash` on Linux.

### Step 1.2: Install Oh My Bash (or Oh My Zsh)

```bash
# Bash users
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# Zsh users (macOS default)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Pick a theme by editing the `OSH_THEME="..."` line in `~/.bashrc` (or `ZSH_THEME="..."` in `~/.zshrc`), then reload.

**Question: what is the purpose of the `source` command?**
`source file` runs the commands of `file` **inside your current shell**, instead of in a new child shell.
That is why we use `source ~/.bashrc` after editing it: the new settings (theme, plugins, aliases) apply immediately to the terminal you are in, without closing it.
If you ran `bash ~/.bashrc` instead, the changes would happen in a child shell that exits straight away, and your terminal would not change.

### Step 1.3: Enable the Git plugin

Open `~/.bashrc` (bash) or `~/.zshrc` (zsh), find the `plugins=(...)` line and add `git`:

```bash
plugins=(git)
```

Then reload: `source ~/.bashrc` (or `source ~/.zshrc`).

Check it works: `gst` should behave exactly like `git status`. Other aliases: `gl` = `git pull`, `gp` = `git push`, `glog` = pretty `git log`.

---

## Part 2: Check your Python installation

```bash
python3 --version     # e.g. "Python 3.12.4" means it is installed
```

If you get `command not found`, Python is missing; the script below installs it.
Always type `python3`, not `python`: on some machines `python` still means the old Python 2.

---

## Part 3: The script, explained feature by feature

Script structure (as asked in step 3.2):

1. **Shebang**: `#!/usr/bin/env bash`
2. **Functions** at the top: `pretty_print`, `detect_os`, `check_python`, ...
3. **Main logic** at the bottom: `main` calls the functions in order.
4. **Conditional branches**: `if`/`case` choose `brew` or `apt` depending on the OS.

| Feature | Function | How it works |
| --- | --- | --- |
| 1. Pretty printing | `pretty_print "msg" [level]` | Uses `printf '\n%b%s%b\n\n'`: a blank line, the coloured message, a blank line. `printf` is used instead of `echo` because `echo` behaves differently between macOS and Linux. |
| 2. OS detection | `detect_os` | `case "$OSTYPE" in darwin*) ... linux-gnu*) ...`. `$OSTYPE` is set by bash itself. |
| 3. Python check | `check_python` | `command -v python3` succeeds if the command exists. If it does, print the version; if not, install it with `brew` or `apt`. |
| 4. pip check | `check_pip` | `python3 -m pip --version`. Calling pip *through* python3 guarantees it's the pip of that same Python. |
| 5. Jupyter | `install_jupyter` | macOS: `brew install jupyterlab`. Linux: `python3 -m pip install --user notebook`, and if recent Ubuntu refuses it (the "externally-managed-environment" error) it falls back to `apt install jupyter-notebook`. |
| 6. brew doctor | `check_brew_health` | Only on macOS. `brew doctor` "fails" when it has warnings, so we catch that and print a yellow warning instead of crashing. |

### Best practices used (step 3.4)

- **Comments explain *why***, not just *what*.
- **Errors are handled**: the `run` helper checks every command, logs it and prints a red message when it fails.
- **Variables are always quoted**: `"$1"`, `"$@"`. Without quotes, a value with a space (like `My Documents`) is split into two words and breaks the command.

### All 5 bonus challenges are done

| Bonus | Where |
| --- | --- |
| Colour output | `GREEN`, `YELLOW`, `RED` ANSI codes in `pretty_print` |
| Logging | `log` writes a timestamp + action + `[ok]` / `[failed: exit N]` to `~/env_install.log` |
| Strict mode | `set -euo pipefail` at the top: `-e` stop on error, `-u` unset variable = error, `-o pipefail` a pipeline fails if any part fails |
| Command-line flags | `--dry-run`, `--verbose`, `--quiet` (plus `--help`), read by `parse_args` |
| Uninstall | `--uninstall` removes Jupyter |

---

## Part 4: Run and verify

```bash
chmod +x env_install.sh      # make it executable (do this once)
./env_install.sh --dry-run   # first see what it WOULD do
./env_install.sh             # then really run it
```

Verification checklist:

- [ ] Your prompt shows the Oh My Bash / Oh My Zsh theme
- [ ] `gst` works like `git status`
- [ ] `python3 --version` prints 3.x
- [ ] `python3 -m pip --version` prints a version
- [ ] `jupyter notebook` opens in the browser (on macOS, `jupyter lab` also works)
- [ ] On macOS: `brew doctor` says "Your system is ready to brew"

If `jupyter` is "not found" right after a Linux install, it went into `~/.local/bin`. Add it to your PATH:
`echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc`

Tested on Linux (Debian-based, Python 3.13): normal run, second run (detects Jupyter already there), `--dry-run`, `--quiet`, `--uninstall --dry-run`, `--help` and an unknown flag.

---

## Check yourself (exam style)

1. What is the difference between `$SHELL` and the shell you are currently running?
2. Why do we write `source ~/.bashrc` and not `bash ~/.bashrc`?
3. What does `chmod +x` do, and what error do you get without it?
4. What do the three options in `set -euo pipefail` each do?
5. Why should you write `"$file"` instead of `$file`?

<details>
<summary>Answers</summary>

1. `$SHELL` is your *default login* shell; the running shell is whatever you launched (you can type `bash` inside zsh). `ps -p $$` shows the real one.
2. `source` runs the file in the *current* shell so the changes stay; `bash file` runs it in a child shell that disappears.
3. It adds the "execute" permission. Without it, `./env_install.sh` gives `Permission denied`.
4. `-e`: exit on the first failing command. `-u`: using an unset variable is an error. `-o pipefail`: `a | b` fails if `a` fails, not only if `b` fails.
5. Quotes keep the value as one word, so names with spaces or `*` don't break the command.

</details>
