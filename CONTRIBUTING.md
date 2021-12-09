# Contributing to Niviz

Thank you for thinking about contributing to Niviz!

This document outlines a set of guidelines for contributing to Niviz. These are meant to serve as guidelines to make your contributing process as easy as possible. None of these are written in stone, so if you disagree/would like to amend any of these guidelines please feel free to raise an issue!

## Have questions?

If you have questions please use the GitHub [Discussions](https://github.com/jerdra/niviz/discussions) board. Just set the discussion type to Q&A and we (the community) will try to get back to you as soon as possible!

## How Can I Contribute?

### Reporting Bugs

As Niviz is in it's awkward growth phase, numerous bugs may occur. If you run into one it's an opportunity to contribute! Before creating a bug report, please check whether the issue has already been reported in our [Github Issues](https://github.com/jerdra/niviz/issues). If not feel free to create a Bug Report with the following:
1. A clear and descriptive title of the bug
2. A brief description of the bug
3. Under what conditions did the bug appear + steps to reproduce is preferable
4. What was the expected result, and why?
5. Whether you are open to resolving the issue

If you'd like to tackle the issue, please add the appropriate GitHub label `will-implement`, and we'll get in touch to walk you through the process! Note that not every bug has an immediate and obvious solution, in which case some digging will be required of you; of course we'll do our part in investigating solutions as well!

### Suggesting New Features and Enhancements

Contributing new ideas and features into a project is one of the most fulfilling aspects of open-source project development. Since Niviz is relatively small and new, there is a LOT of room for growth and for you to shape the development of the project. Before you request a feature please take into consideration the following:

1. How much effort will the feature take to implement. Note that while features are often great additions to a project, they also allot additional burden on the maintainers if poorly implemented
2. Is the feature request appropriate for the project scope encapsulated by Niviz?
3. What is your motivation for the feature you wish to implement?
4. Are you willing to work on the feature that you are requesting

If you believe that your feature does indeed belong in Niviz then feel free to create a feature request in the [GitHub Issues](https://github.com/jerdra/niviz/issues) board! When submitting a feature request try to have the following:

1. Use a clear descriptive title of the feature
2. Provide context for why your feature is sorely needed by Niviz
3. Give some examples of where your feature could be useful to end-users and developers of Niviz
4. Indicate whether you would like to work on said feature. If so, please add a GitHub Issues label called `will-implement`.

### Finding Issues to Contribute to

Unsure where to begin when contributing to Niviz? Start by looking at the [GitHub Issues](https://github.com/jerdra/niviz/issues). The two relevant labels that are indicative of a contributing opportunity are as follows:

1. `good-first-issue` - issues labelled with these require minimal burden on the contributor and provide a foot-in-the-door opportunity to contribute
2. `help-wanted` - these issues require a bit more work as even the maintainers themselves may not immediately have a solution. If you feel like you can take one of these on, please do! We're looking to learn from our contributors as much as you are from us :)

### Code Contributions

You've found a bug, devised a much-needed feature, or found an issue that speaks to you... you are ready to contribute to the Niviz project! Before you start typing out any code please make sure:

1. An issue exists for your contribution
2. You got the go-ahead from the maintainers to start working on a contribution

Please don't submit PRs unless a contribution opportunity has been green-lighted. It's easier to keep track of who's contributing what when communication is plenty!

Okay, so you've gotten approval for your contribution and you're ready to write... but wait, there's a few more things to keep in mind!

### Style-Guide

Niviz enforces some style guides in order to maintain consistency in how code is written and documented. This makes it easier for future developers reading through code to either squash bugs or to contribute new features.


#### Git Commit Messages

(Gratefully taken from [Atom's Style Guide](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#styleguides)
- Use present tense in commits (i.e  "Add feature" not "Added feature")
- Keep commit messages concise
- Use [git rebase](https://www.git-tower.com/learn/git/faq/git-squash) to squash a bunch of messy commits into a few logical ones
- Keep your contributing short and within scope. Don't go modifying extraneous files that are unrelated to your contribution.

#### Python Code

In order to ensure consistent code formatting we use a number of tools to help us out. It is expected that you too use these tools:

- [flake8](https://github.com/PyCQA/flake8) - enforce adherence to the [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [yapf](https://github.com/google/yapf) - python code formatter, can be run within your editor or through command-line
- Use [google-style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) in *all your code*! 


### Pull Requests

Pull Requests are the standard way to contribute code changes to open source projects. When submitting a pull request please ensure the following:

1. You have a clear descriptive title of what your PR entails. Please use the following title prefixes when submitting a PR
	1. `MAINT`: <TITLE> - when contribution is related to maintenance (i.e CI, packaging)
	2. `ENH`: <TITLE> - when contribution is adding a feature enhancement
	3. `FIX`: <TITLE> - when contribution is fixing broken behaviour (i.e bug squashing)
	4. `DOCS`: <TITLE> - when contribution is solely modifying documentation (i.e writing tutorials, configuration for docs)
	5. `TST`: <TITLE> - when contribution is solely related to updating testing code
	6. `STY`: <TITLE> - when contribution consists of only updating code style. No behaviour changes in code should occur!
	7. `REF`: <TITLE> - when contribution is solely refactoring. No new features should be added
2. You reference an issue that is being resolved by the PR
3. Reference the issue being resolved in your PR, this can be done by writing in your PR a line that says "Resolves #<ISSUE NUBER". GitHub will auto-associate the PR with the provided issue
4. You have a clean, concise, and readable commit history. If your commit history is a bit messy, no problem! Use [git rebase](https://www.git-tower.com/learn/git/faq/git-squash) to re-format your commits into something cleaner
5. Ping the maintainers if you haven't heard back, but try to be polite about it. Maintainers, like you, are also busy people with jobs and lives; please be considerate :)


### Documentation

Documentation is auto-generated from code using [Sphinx](https://www.sphinx-doc.org/en/master/) for the most part. However some components, such as tutorials, are manually written by contributors/maintainers. This is always an area that could use some work, refinement, and feedback!
