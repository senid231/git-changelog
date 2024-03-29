[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine)

# git-changelog
Debian package changelog generator from git

## Usage
```
$ changelog-git -h
Usage:
  changelog-git [options]

Options:
  -h, --help                Show help.
  -v, --version             Show version.
  -d, --debug               Debug mode (print debug logs).
  -q, --quiet               Suppress all output (except errors).
  -A, --auto-commit         Create new branch and commit changelog.
  -D, --detailed            Do not skip guessed prompts.
  -Y, --yes                 Skip all prompts with defaults.
  --project-path=<path>     Path to project root (default current directory).
  --next-version=<version>  Set next changelog version (default ask in prompt).
  --package-name=<name>     Set package name (default ask in prompt).
  --changelog-path=<path>   Set relative changelog path (default 'debian/changelog').
  --to-commit=<ref>         Set to commit (default 'HEAD').
  --from-commit=<ref>       Set from commit (default last tag).
  --urgency=<name>          Set urgency (default from changelog).
  --debian-branch=<ref>     Set debian branch (default from changelog).
  --user-name=<name>        Set user name (default from git config).
  --user-email=<email>      Set user email (default from git config).
```

## Install
Download [latest build](https://www.dropbox.com/s/50tm3yg5p415yxd/git_changelog-1.1.4.tar.gz?dl=0) from dropbox

in the directory where you download it run:
```
sudo pip install git_changelog-1.1.4.tar.gz
```

## Upgrade
```
sudo pip install -U git_changelog-1.1.4.tar.gz
```

## Uninstall
```
sudo pip uninstall git_changelog
```

## Usage

Will append version details to the top of `debian/changelog`

`-A` flag allows to create bump commit in separate branch for MR

```
$ changelog-git -A
Project path: /home/senid/projects/my/git_changelog
Related path to changelog: debian/changelog
Package name: git-changelog-app
Version (default 1.0.1): 
From commit (default HEAD): HEAD~2
To commit: HEAD
```
will create new branch `bump-1.0.1` from `HEAD`, 
append changelog with:
```
git-changelog-app (1.0.1) wheezy; urgency=low
  * add script distribution
  * small upgrades
 -- Denis <senid231@gmail.com>  Sun, 9 Apr 2017 20:35:15 +0300
 ```
and commit it with message:
```
bump 1.0.1

[ci skip] [changelog skip]
```

# Building
```shell
cd /path/to/project
python setup.py sdist
# file with your build will be in ./dist/git_changelog-X.Y.Z.tar.gz
```
