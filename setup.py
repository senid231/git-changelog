from setuptools import setup
import git_changelog

setup(
    name='git_changelog',
    version=git_changelog.__version__,
    packages=['git_changelog'],
    # scripts=['bin/changelog-git'],
    url='https://github.com/senid231/git-changelog',
    license='MIT',
    author='Denis Talakevich',
    author_email='senid231@gmail.com',
    description='appends changelog using git commits',
    install_requires=['tzlocal', 'GitPython'],
    entry_points={
        'console_scripts':
            ['changelog-git = git_changelog.GitChangelog:append_to_changelog']
    }

)
