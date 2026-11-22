#!/usr/bin/env bash
#
# env_install.sh — set up a Python development environment from scratch.
#
# What it does (one "feature" per step of the exercise):
#   1. pretty_print   : readable, coloured output
#   2. detect_os      : find out if we are on macOS or Linux (uses $OSTYPE)
#   3. python3 check  : install Python 3 if missing, otherwise show its version
#   4. pip check      : make sure pip works and show its version
#   5. Jupyter        : install Jupyter Notebook
#   6. brew doctor    : on macOS only, check that Homebrew is healthy
#
# Usage:
#   ./env_install.sh              normal run
#   ./env_install.sh --dry-run    print what WOULD run, change nothing
#   ./env_install.sh --verbose    also print every command before running it
#   ./env_install.sh --quiet      only print warnings and errors
#   ./env_install.sh --uninstall  remove Jupyter (undo step 5)
#   ./env_install.sh --help       show this help

# ---------------------------------------------------------------------------
# Strict mode (bonus): stop on the first failing command (-e), treat unset
# variables as errors (-u), and make a pipeline fail if ANY part fails
# (-o pipefail). Without this, a failed install would be silently ignored.
# ---------------------------------------------------------------------------
set -euo pipefail

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
LOG_FILE="${HOME}/env_install.log"   # bonus: every action is logged here
DRY_RUN=false
VERBOSE=false
QUIET=false
UNINSTALL=false

# ANSI colour codes (bonus). "\033[" starts a code, "0m" resets to normal.
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# ---------------------------------------------------------------------------
# Functions (defined first, used later in main)
# ---------------------------------------------------------------------------

# Write one line to the log file with a timestamp.
log() {
    printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

# Feature 1: pretty printing.
# $1 = the message, $2 = optional level: info (default), success, warn, error.
# A blank line before and after makes each step easy to spot in the output.
pretty_print() {
    local message="$1"
    local level="${2:-info}"
    local color="$RESET"

    case "$level" in
        success) color="$GREEN" ;;
        warn)    color="$YELLOW" ;;
        error)   color="$RED" ;;
    esac

    log "[$level] $message"

    # In quiet mode we only show warnings and errors.
    if [[ "$QUIET" == true && "$level" != "warn" && "$level" != "error" ]]; then
        return 0
    fi

    printf '\n%b%s%b\n\n' "$color" "$message" "$RESET"
}

# Run a command, or only show it in dry-run mode. Logs success or failure.
# "$@" means "all arguments, each kept as one word" (safe with spaces).
run() {
    if [[ "$DRY_RUN" == true ]]; then
        printf '[dry-run] %s\n' "$*"
        log "[dry-run] $*"
        return 0
    fi
    if [[ "$VERBOSE" == true ]]; then
        printf '+ %s\n' "$*"
    fi
    log "[run] $*"
    if "$@"; then
        log "[ok] $*"
    else
        local code=$?
        log "[failed: exit $code] $*"
        pretty_print "Command failed: $*" error
        return "$code"
    fi
}

# Return 0 (true) if a command exists on this machine.
command_exists() {
    command -v "$1" > /dev/null 2>&1
}

# Feature 2: detect the operating system from the OSTYPE variable.
# OSTYPE is set by bash itself: "darwin..." on macOS, "linux-gnu" on Linux.
detect_os() {
    case "$OSTYPE" in
        darwin*)    OS="macos" ;;
        linux-gnu*) OS="linux" ;;
        *)          OS="unknown" ;;
    esac
}

# Install a package with the right package manager for this OS.
install_package() {
    local package="$1"
    if [[ "$OS" == "macos" ]]; then
        if ! command_exists brew; then
            pretty_print "Homebrew is missing. Install it from https://brew.sh first." error
            exit 1
        fi
        run brew install "$package"
    elif [[ "$OS" == "linux" ]]; then
        run sudo apt-get update
        run sudo apt-get install -y "$package"
    else
        pretty_print "Unsupported OS ($OSTYPE). Install $package by hand." error
        exit 1
    fi
}

# Feature 3: make sure python3 exists.
check_python() {
    if command_exists python3; then
        pretty_print "Python is installed: $(python3 --version 2>&1)" success
    else
        pretty_print "python3 not found, installing it..." warn
        if [[ "$OS" == "macos" ]]; then
            install_package python
        else
            install_package python3
        fi
    fi
}

# Feature 4: make sure pip works. We call it through python3 ("python3 -m pip")
# so we are sure pip belongs to the same Python we just checked.
check_pip() {
    if python3 -m pip --version > /dev/null 2>&1; then
        pretty_print "pip is installed: $(python3 -m pip --version)" success
    else
        pretty_print "pip not found, installing it..." warn
        if [[ "$OS" == "linux" ]]; then
            install_package python3-pip
        else
            run python3 -m ensurepip --upgrade
        fi
    fi
}

# Feature 5: install Jupyter Notebook. The command differs by OS:
# on macOS we use Homebrew's "jupyterlab" formula;
# on Linux we first try pip in the user's home (--user, so no sudo). Recent
# Ubuntu/Debian refuse that ("externally-managed-environment", PEP 668), so if
# pip fails we fall back to the system package from apt.
install_jupyter() {
    if command_exists jupyter; then
        pretty_print "Jupyter is already installed: $(command -v jupyter)" success
        return 0
    fi
    pretty_print "Installing Jupyter Notebook..."
    if [[ "$OS" == "macos" ]]; then
        run brew install jupyterlab
    elif ! run python3 -m pip install --user notebook; then
        pretty_print "pip refused, trying the apt package instead..." warn
        install_package jupyter-notebook
    fi
    pretty_print "Jupyter installed. Start it with: jupyter notebook" success
}

# Bonus: undo feature 5.
uninstall_jupyter() {
    pretty_print "Removing Jupyter Notebook..." warn
    if [[ "$OS" == "macos" ]]; then
        run brew uninstall jupyterlab || true
    else
        run python3 -m pip uninstall -y notebook || true
    fi
    pretty_print "Jupyter removed." success
}

# Feature 6: on macOS only, ask Homebrew to check itself.
# "brew doctor" exits with an error when it has warnings, so we catch that
# and show a warning instead of stopping the whole script (strict mode).
check_brew_health() {
    if [[ "$OS" != "macos" ]]; then
        return 0
    fi
    pretty_print "Running brew doctor..."
    if run brew doctor; then
        pretty_print "Homebrew is healthy." success
    else
        pretty_print "brew doctor found issues, read its advice above." warn
    fi
}

show_help() {
    # Print the comment block at the top of this file (lines starting "# ").
    sed -n '3,19p' "$0" | sed 's/^# \{0,1\}//'
}

# Bonus: read the command-line flags.
parse_args() {
    for arg in "$@"; do
        case "$arg" in
            --dry-run)   DRY_RUN=true ;;
            --verbose)   VERBOSE=true ;;
            --quiet)     QUIET=true ;;
            --uninstall) UNINSTALL=true ;;
            -h|--help)   show_help; exit 0 ;;
            *) pretty_print "Unknown option: $arg (try --help)" error; exit 1 ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# Main logic: the steps run in order, using the functions above.
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"
    log "===== env_install.sh started ($*) ====="

    detect_os
    pretty_print "Detected OS: $OS ($OSTYPE)"

    if [[ "$UNINSTALL" == true ]]; then
        uninstall_jupyter
        exit 0
    fi

    check_python
    check_pip
    install_jupyter
    check_brew_health

    pretty_print "All done! Log file: $LOG_FILE" success
}

main "$@"
