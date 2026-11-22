# git mini exo (slide 26)

All the commands below were run for real in a test folder; the outputs shown come from that run.
Parts 9 to 11 need a GitHub account (creating a repo on github.com), so for those I give the commands only.

## Part 1: setup and config

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global --list      # to check
```

Output: `git version 2.43.0`. The name and email are stored once and written in every commit you make.

## Part 2: create the first repository

```bash
mkdir my-first-repo      # create the folder
cd my-first-repo         # go inside
git init                 # turn it into a git repository (creates the hidden .git folder)
touch readme.txt         # create an empty file
```

## Part 3: first commit

1. State of the repo: `git status`
2. Stage the file: `git add readme.txt`
3. Commit: `git commit -m "Add readme file"`
4. History: `git log`

Before `git add`, `git status` says `Untracked files: readme.txt`. After it, the file is `A` (added to the staging area).

## Part 4: make changes

1. Add a line: `echo "second line" >> readme.txt`
2. `git status` shows `modified: readme.txt` in red, "Changes not staged for commit": git sees the file differs from the last commit but I haven't staged it yet.
3. `git add readme.txt` then `git commit -m "Update readme with a second line"`
4. I now have **2 commits** (`git log --oneline` shows two lines).

## Part 5: exploration

- `git diff` shows what changed since the last commit in files that are not staged yet. Lines starting with `+` were added, `-` removed:

```
diff --git a/readme.txt b/readme.txt
 hello
+second line
```

- `git log --oneline` shows the history with one line per commit (short id + message):

```
0d97714 Update readme with a second line
6274baf Add readme file
```

## Part 6: branches

1. List branches: `git branch` (the current one has a `*`)
2. Create `feature-script`: `git branch feature-script`
3. Switch to it: `git switch feature-script` (older way: `git checkout feature-script`)
4. Create and switch in one command: `git switch -c dev` (older way: `git checkout -b dev`)
5. Back to `feature-script`: `git switch feature-script`
6. Check: `git branch` shows `* feature-script`

```
  dev
* feature-script
  main
```

## Part 7: bash script on a branch

On `feature-script`, I created [`install.sh`](install.sh):

```bash
#!/bin/bash
echo "Starting installation..."
sudo apt update
sudo apt install -y tree
echo "Installation complete!"
```

```bash
chmod +x install.sh        # make it executable
git add install.sh
git commit -m "Add install script"
git log --oneline
```

```
1de81ef Add install script
0d97714 Update readme with a second line
6274baf Add readme file
```

## Part 8: merge branches

1. `git switch main`
2. `ls` shows only `readme.txt`. **`install.sh` is not there**, because that commit exists only on the `feature-script` branch; each branch has its own files.
3. `git merge feature-script`
4. `ls` again: now `install.sh` is there too.
5. `git log --oneline` on main shows the install commit on top. Git said `Fast-forward`: main had no new commits of its own, so git just moved the `main` label forward and did not create a merge commit.
6. Delete the merged branch: `git branch -d feature-script`

## Part 9: push to GitHub

1. On github.com: New repository, name `my-first-repo`.
2. Do **not** tick "Add a README" (the repo must be empty, otherwise the histories differ and the first push is refused).
3. Link the local repo to GitHub: `git remote add origin https://github.com/<my-username>/my-first-repo.git`
4. Push: `git push -u origin main` (`-u` remembers that `main` goes to `origin`, so later `git push` is enough)
5. After refreshing the page, GitHub shows my files (`readme.txt`, `install.sh`) and the commits.

## Part 10: delete and clone

1. Leave the folder: `cd ..`
2. Delete it: `rm -rf my-first-repo`
3. Clone from GitHub: `git clone https://github.com/<my-username>/my-first-repo.git`
4. `cd my-first-repo` then `ls` shows the files again, and `git log` shows the whole history.

## Part 11: full workflow from scratch (`bash-installer`)

```bash
cd ..
rm -rf my-first-repo                # delete the local folder
# delete the repo on GitHub: Settings > Danger zone > Delete this repository
mkdir bash-installer && cd bash-installer
git init
echo "# bash-installer" > README.md   # explain what the project is
git add README.md
git commit -m "Add README"
git switch -c feature-install
cp ../install.sh .                    # the install script from part 7
git add install.sh
git commit -m "Add install script"
git switch main
git merge feature-install
git branch -d feature-install
# create a new empty repo on GitHub, then:
git remote add origin https://github.com/<my-username>/bash-installer.git
git push -u origin main
```

The finished project is in [`bash-installer/`](bash-installer/).

## Reflection questions

1. **Why is version control useful?** It keeps the whole history, so I can see who changed what and go back to an older version, several people can work together, and the code is backed up on a server.
2. **Staging vs committing?** Staging (`git add`) chooses which changes will go in the next commit; committing (`git commit`) actually saves that selection as a snapshot in the history.
3. **When should I commit?** Often and in small steps, each time one logical thing works (a function, a fix), with a clear message.
4. **`git init` vs `git clone`?** `git init` creates a new empty repository from the current folder; `git clone` copies an existing repository (all files and history) from a remote like GitHub.
5. **Why good commit messages?** So that I (and others) can understand later what changed and why, and find the commit that introduced a bug.
6. **Purpose of branches?** To work on something separately without touching the stable `main` code, and merge it once it works.
7. **When to create a branch instead of working on `main`?** For a new feature, a bug fix or an experiment, and whenever several people work at the same time.
