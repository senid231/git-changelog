# git-changelog
Debian package changelog generator from git

## Usage
```
cd path/to/project
changelog-git
```

## Install
```
wget https://git.in.didww.com/denis.t/git-changelog/builds/artifacts/v1.0.0/download?job=build-job
unzip artifacts.zip -d git-changelog
pip install --user git-changelog/dist/git_changelog-1.0.tar.gz
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
