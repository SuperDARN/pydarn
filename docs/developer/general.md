# Developers Guide 

pyDARN is an open-source package that is currently not affiliated with any specific SuperDARN working group but supported by SuperDARN collaborators. The scope of this library is to provide a flexible standard methods for visualizing SuperDARN data. 

In the future IO operations will be removed from pyDARN and will become another library similar with any other functionalities that are not specific to data visualization. 

This section generally covers development in pydarn and guidelines that should be followed be any contributors to the library. 

## Communication and Teleconferences 

pyDARN is a collaborative, and constructive group that discourages any toxic or negative behaviour. If toxic or negative behaviour is observed then that person will be removed from the developers/contributors group. Please read [Communication Guidelines](developers/communication.guidelines) to ensure you are keeping pyDARN a collaborative and constructive group. 

Teleconferences, will be held at least once a year if not more when needed. An agenda will be drafted on the developers team chat and followed in the teleconference. The teleconference will focus on higher level topics that need further discussion either brought up by members or *Issues* and *Pull Requests*. If time allows a **RICE** (Reach, Impact, Confidence, Effort) to help score and refocus the group on important *Issues* and *Pull Requests* and future directions. Other topics that will be typically discussed in the teleconferences will include projects, milestones and new releases on pyDARN. 

Other forms of communication in pyDARN is our slack group, please contact Marina Schmidt to be added. 

## Code 

pyDARN is a collaborative library developed by engineers, scientists, and programmers, thus all significant code decisions will be discussed in the pyDARN developer team chat on GitHub and may be discussed in teleconference (if needed). 

Code changes are to be present in pull requests that are to be reviewed (see [Code Review](developers/code_review.md)) and tested by another developer before being merged. All additional features need to include unit and integration tests. **Non-tested code is broken code** and will not be merged. 

See [Code Style Guidelines](developers/code_style_guidelines.md) and [Testing Guidelines](developers/testing_guidelines.md) for requirements on code style and testing guidelines. 

## Naming branches 

All major branches should be based off of the `develop` branch unless a sub-branch from another major branch.  

When creating a new branch on pyDARN use the following nomenclature:
- `HOTFIX/<name of the fix>`: A quick fix in the code to solve a bug/error with the code - this type of fix may warrant a patch release when merged
- `feature/<package_nanem>`: A new feature to be added for the pertaining package/module 
  - `<package>/<new module name>`: Sub-branch(s) pertaining to the new feature if requires multiple modules to be implemented 
- `Fix/<name of the fix>`: Less higher-priority or difficult type of fix to a bug/error 
- `deprecation/<deleted package or module>`: Removing of a legacy feature(s) or out of scope feature

See [Workflow Guidelines](developers/workflow_guidelines.md) and [Release Guidelines](release_guidelines.md) for more details on branch workflow and release guidelines. 

## Labels and Milestones 

Each *Issue* and *Pull Request* should get at least one label to indicate the type of topic: `fix`, `new feature`, `enhancement`, `maintenance`, `documentation`, `deprecation`, etc. 

In addition to topic labels, please add any additional labels to help developers understand what your *Issue* or *Pull Requests* needs or is about. 
Other examples of labels: `high-priority`, `low-priority`, `discussion`, `need help`, `question`, etc. 

Milestones are another way of labeling your *Issue* and *Pull Request* importance towards a release or tasks that need to be completed if it is a larger implementation. Please ask if you wish to add your *Issue* or *Pull Request* to a release Milestone. Due to limited developer resources and time, not all *Issues* or *Pull Requests* will make it into the next pyDARN releases. However, minor releases can be made so there is hope! 

See [Issues and Pull Request Guidelines](developers/issue_PR_guidelines.md) for more details on *Issue* and *Pull Request* requirements. 
See [Workflow Guidelines](developers/workflow_guidelines.md) for more details on create milestones in pyDARN. 

## Pull Requests 

As mentioned before no *Pull Request* will be merged in by the author(s). Reviewers of the *Pull Request* are allowed to merge. If there is multiple involvement of developers on one *Pull Request* than any affiliated developer cannot review or merge the *Pull Request*.

**All major branches should be merged into the `develop` branch and NOT MASTER!**, any minor branch can be merged into their respected corresponding branch. 

The only exception is documentation updates based on `master` documentation. This is to fix any minor typos or clarity on installtion/usage guides. New feature documentation will be merged in with `develop`. 

See [Issues and Pull Request Guidelines](developers/issue_PR_guidelines.md) for more details on *Issue* and *Pull Request* requirements. 


## Releases 

pyDARN does not follow any **strict** release time line as it is a collaborative  open-source library that is based on volunteer efforts. When there is enough contributions or significant changes to the code one of the following types of release will be made: 
- `MAJOR`: Rarely changes, requires large significant change(s) to the code, like multiple additional modules/packages or architecture changes
- `MINOR`: Common changes, requires new feature(s), deprecation(s) and major bug fixes
- `PATCH`: frequently changes, requires a hot-fix, updates to code, and better maintenance improvements

The pyDARN version number `MAJOR`.`MINOR`.`PATCH` will indicate which release type is made and final version will appear on PyPI. 

To keep progress moving and not halt any further development on other *Issues* *Pull Requests* that arise during a release, development branches for the release be made. This will keep the `develop` branch from being frozen during a release period (as this could take months). Release branches will follow the release candidate nomenclature: 
- `DEV`: denoted with a `dev0+<git-commit-hash>` indicating a Development version that is soon ready to be a release version. May require review or waiting on a *Pull Request* to be merged
- `ALPHA`: denoted with a `a` and a number indicating the beginning of testing phase of the release version 
- `BETA`: denoted with a `b` and a number indicating that it passed the alpha phase of testing and now in second phase of ensure minimal impact on the user. Focuses on performance, and user interactions. 
- `RELEASE_CANDIDATE`: denote with a `rc` and a number indication it is in the final phase and is ready to be released right away, just needs to be approved on

The version number indicate in the testing phase of potential final release would be: `MAJOR`.`MINOR`.`PATCH`[`DEV`, `ALPHA`, `BETA`, `RELEASE_CANDIDATE`]. Movements between the following testing phases of a release branch can be made by any main developer in pyDARN. However, **final releases are to be approved and preformed by senior developers or pyDARN**

Currently senior developers are: 
- Marina Schmidt 
- Ashton Remier 
- Angeline Burell 
- Kevin Sterne 

See [Release Guidelines](developer/release_guidelines.md) for more information on the release process of pyDARN. 

## Copyrights and Licensing

pyDARN is licensed under GPL v3.0 this license it not compatible with other licenses so when adding code in pyDARN your code will be licensed under GPL v3.0. 
As a requirement of the GPL v3.0 license, all authors of their code hold the copyrights to it but are allowing it to be open-sourced in pyDARN. 

When contributing code to pyDARN please add the copyright and author line at the top of the file, for example: 
```python
# (C) copyright 2019 SuperDARN Canada, University of Saskatchewan
# author: Marina Schmidt
```
Because pyDARN is collaborative library, shared-copyright is allowed encouraged. If another developer from another institution helped develop the new feature of code then include their copyright line below, for example: 
```python 
# (C) copyright 2019 SuperDARN Canada, University of Saskatchewan 
# author: Marina Schmidt 
# (C) copyright 2019 SRI International, San Francisco 
# author: Ashton Remier
```

In addition to the copyright line, a disclaimer of the license GPL v3.0 needs to be included in every file, for example: 

```python 
# DISCLAIMER: This code is licensed under GPL v3.0 which can be located in LICENSE.md in the root directory
```

If you make modifications to the code that constitute you as an author (like bug-fixes, typos, code refactoring, ...) then you will need to make note when the modification was made, by who and a small description, for example: 
```python
# Modifications: 
# 2019-08-20 Marin Schmidt - fixed a bug with range gates presentation in range-time parameter plots 
```

## Citing and DOI 

In your code please make sure to cite any proprietary software used and articles that your code may be based off of. 

See [Citing pyDARN](user/citing.md) for details on how to cite pyDARN in your own work. 

Data Object Identification (DOI) is a way for pyDARN to be cited in articles. The DOI is created by [zenodo](https://zenodo.org/) for every final release of pyDARN. 

## Deprecations 

 To ensure scope is kept in pyDARN and it stays flexible and maintainable deprecations of features and legacy code will occur. This includes changing to newer versions of python and not supporting old version, like python 2.7. We understand this can be annoying to users that may need to change their code in the future, however, with a minimal developer resource pyDARN has this is the best option to ensure maintenance stays and supporting old backwards compatibility is not over burdening the teams valuable time. 

 Reasons code may be deprecated: 
 - buggy 
 - API isn't clean/understandable 
 - not within scope 
 - no long supported functionality or legacy 

See [Workflow Guidelines](developers/workflow_guidelines.md) for more information on how deprecations are processed in pyDARN. 
