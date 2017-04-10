# git-changelog
Debian package changelog generator from git

## Usage
```
cd path/to/project
changelog-git
```

## Install
```
pip install https://github.com/senid231/git-changelog/releases/download/v1.0-pre1/git_changelog-1.0.tar.gz
```

## Example

Will append version details to the top of `debian/changelog` and print it to output

```
$ mkdir -p debian
$ echo "git-changelog-app (1.0.0) wheezy; urgency=low" > debian/changelog
$ echo "  * initial" >> debian/changelog
$ echo " -- Denis <senid231@gmail.com>  Sun, 9 Apr 2017 20:32:00 +0300" >> debian/changelog
$ changelog-git 
Project path: /home/senid/projects/my/git_changelog
Related path to changelog: debian/changelog
Package name: git-changelog-app
Version (default 1.0.1): 
From commit (default HEAD 2b6c033a15e10065f6ae02169f7852642f788a67): HEAD~2
To commit: HEAD 2b6c033a15e10065f6ae02169f7852642f788a67
git-changelog-app (1.0.1) wheezy; urgency=low
  * add script distribution
  * small upgrades
 -- Denis <senid231@gmail.com>  Sun, 9 Apr 2017 20:35:15 +0300
```
