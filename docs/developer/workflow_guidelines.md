# Workflow 

In pyDARN, all additive code whether it is a *bug fix* or *enhancement* must be merged into pyDARN via a **pull request**. 
Before creating a new branch or submitting a pull request, please make sure the following guidelines are met:
- [code style](developers/code_guide.md)
- [documentation guidelines](developer/)

## Pull Requests 

Pull requests are completed when a completed section of code/functionality/module or simple fix is done on separate branch that is not *develop* or *master*. 
Completed referring to: 
- Tested (see [testing guidelines](developers/testing_guide.md))
- Documented (see [documentation guidelines](developers/documentation_guide.md))

A pull request is [created](https://github.com/SuperDARN/pydarn/pulls) via clicking on **New pull request** and following the guidelines below. 
Once a pull request is created, [travis-CI](https://docs.travis-ci.com/user/tutorial/) will be invoked and will run the following tests:
- macosx, linux, and windows builds for python 3.5+ (Due to python 2.7 being deprecated in 2020, we will not support any python version lower than 3.5)
- testing scripts **yet to be implemented** 
- test coverage **yet to be implemented**
- profiling/benchmarking **future possibility** 
- python style checkers
  - [flake8](http://flake8.pycqa.org/en/latest/): PEP8 style checker for python
  - [MyPy](https://mypy.readthedocs.io/en/latest/introduction.html): python type checker

### Guidelines of Pull Request
The following guidelines are required for the pull request to be approved and the section of code to be accepted.
1. Any non-release branches must be merged into `develop` or another side-branch. Documentation based branches can be merged into `master` if referencing a typo, or further clarification in the current release. [HOT Fixes](developers/release_guidelines.md) still need to be merged to `develop` but will prompt a patch fix release of the current status of `develop`. 
2. Pull request titles: ensure the title of your pull request is **meaningful**. If your pull request is deemed **HOT Fix** worthy from *issue* conversation then put that in the title. 
3. Description: make sure the user understands where this pull request is coming from (i.e., referencing issues or common functionality requests). The current status and any limitations the code does not consider. And how to test your code, give some example code and expected results for the reviewers of your pull request. 
4. Reviewer requesting: at least two reviewers must be requested (of your choice) or a call out to anyone who wants to test your code. One reviewer you pick can be the code reviewer. The code reviewers responsibility is to do a code review on the code (please review [code review guidelines](develoepers/code_reviews.md)). The other reviewer will test your code. However, other reviewers can test/code review the pull request and one reviewer can do both jobs. 
5. No cowboy coding: This means you cannot merge your own pull request. One of the reviewers or members of the pyDARN community can merge your code in. However, it is preferred that one of the reviewers merges it. Pings on the pull request can be made to try and get the attention of the reviewers and others to help speed up a pull request. 
