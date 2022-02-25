<!--Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->

# Releasing 

pyDARN is an open source library and thus has various versions with updates. By releasing the code in versions it helps with reproducibility in publications, and allows changes to be implemented as a batch update of a version.  This reduces the frequency of updates required by users to stay up to date.

## Scheduling 

pyDARN does not follow a strict release schedule because development of pyDARN is mainly driven by volunteers in the SuperDARN community.  
However, if bug fixes, documentation updates, enhancements, new features, or deprecations are on the `develop` branch for over a few months it is 
best to make a release to get it out to the community. 

One way to plan for a release associated with your work is by using [milestones](https://docs.github.com/en/github/managing-your-work-on-github/about-milestones). In pyDARN, we use milestones for planning releases, and for organizing [issues](issues.md) and [pull requests](PR.md) to respective releases.  This helps create a timeline for version releases. 
Anyone can [create a milestone](https://github.com/SuperDARN/pydarn/milestones) on GitHub for pyDARN. 
Go to pull requests on GitHub, select `milestone` top right above the list of pull requests. Then select [New milestone](https://github.com/SuperDARN/pydarn/milestones/new) and fill in the following information:

- **Title:** pyDARN *(See version numbers below)*
- **Date:** due date pick something a couple months away (takes roughly 3-4 weeks of testing and getting the release branch out)
- **Description:** describe any specific changes focusing on for this release 

Then click on **Create milestone**

## Version numbers

Before creating a release issue/pull request, determine what the [version type](https://semver.org/) will be:

**Major.minor.patch**

- Major: change to the user interface or large structural change to the library. Deprecations typically lead to a major release.  
- Minor: new feature, enhancement or default change has been made 
- Patch: bug fixes and documentation updates

!!! NOTE
    Documentation doesn't need to be associated with a release unless it accompanies a new change to the code. 

Then take the previous pyDARN version number and add one to the associated type location. 
For example, if we are on pyDARN 2.0 and:

- it's a ***major*** release then the number will be: 3.0
- it's a ***minor*** release then the number will be: 2.1
- it's a ***patch*** release then the number will be: 2.0.1 


## Workflow

1. Once a version number is determined, create an [issue](issues.md) using the discussion template. This issue will give some heads up to testers and developers that a release will be made soon 
and to confirm the version number is correct. State why a release is needed and what pull requests should be included that have not been **merged** yet using [GitHubs checklist feature](https://docs.github.com/en/github/managing-your-work-on-github/about-task-lists)
2. Once the pull requests needed for the releases are merged into `develop` then create a release branch:
        
        git checkout develop
        git checkout -b release/<version number>

3. Complete the Pre-Release Checklist below to make some minor changes before opening the pull request
4. Now create a pull request for the release branch.  This should merge into `main`.
5. Add the following to the PR info: 
    - **Title**: Release pyDARN <version>
    - **Scope**: add information on the main focus of this release
    - **Include link to readthedocs** on this release (DVWG Chair to do this)
    - **Changes:** history of what has changed, look at the [milestones closed tasks](https://github.com/SuperDARN/pydarn/milestones?state=open)
    - **Approvals:** 3 (reviews+testing)
    - **Testing:** Using Github Checklists to include what needs to be tested, tested on what kind of data, and operating systems
        - For example: 
            - test summary plotting 
            - test fan plots 
            - test grid plotting 
            - test grabbing hardware information 
            - test on North and South hemisphere data
            - test on Borealis data 
            - test using RPM linux machine (OpenSuse, Fedora, RedHat)
            - test using Debian linux machine (Ubuntu)
            - test using MacOsX
            - test using Windows 



### Pre-Release Checklist 

!!! IMPORTANT
    Do this before the pull request to make it part of the review process 

- Make sure the `.zenodo.json` file is updated to reflect the [DVWG authorship guidelines]() and everyone is okay with the order. Please confirm with additional new members if their name and ORCID iD is correct. 
- Update `version.py` file to have the new version number on the line `__version__=""`
- Update `README.md` file to reflect the new changes of the release and version number 

### Release Checklist

Once the test is complete and at least three approvals are obtained make sure the following steps are performed.  
The pyDARN lead developer or DVWG chair should do this step; however, if you request to do it and get approval then go ahead! 

1. **merge** the release branch in `main` and confirm the above updates are there
2. [Tag and release the code](https://github.com/SuperDARN/pydarn/releases/new)
- tag: v<version number>
- target: `main`
- Release Title: pyDARN v<version number>
- Description: Header "Version *number* - Release!" then add "pyDARN release v*number* includes the following features:" listing all the new changes to the code. Please see other [releases](https://github.com/SuperDARN/pydarn/releases) to keep with consistency
- Hit Publish Release!
- Once a release has been made check on the [pyDARN Zenodo](https://zenodo.org/record/3727269) and look for the version you just released on the right hand side under **Versions**. Please note this may take some time. If this does not work Contact Lead Developer and DVWG Chair on the matter.
- Once the Zenodo DOI is made for the new release, select the DOI markdown tag on the right hand side below **publication date**. Copy the markdown syntax. 
- `git checkout main` and `git pull origin main`
- Paste this syntax in `docs/user/citing.md` under DOI's.       
    
        git add docs/user/citing.md
        git commit -m "updated DOI links"
        git push origin main

- Once this is done, double check everything looks correct

#### Uploading to PyPi 
This step requires the lead developers help as they have access to the pyDARN PyPi account. 

1. Update to make sure everything looks good:
      
        git checkout main
        git fetch
        git pull origin main 

2. Remove old builds
        
        cd dist 
        rm -rf <old versions>
        cd ..

- [Build pyDARN package](https://packaging.python.org/tutorials/packaging-projects/)
        
        python3 -m pip install --upgrade build
        python3 -m build

- check it built the correct version
        
        cd dist
        ls
  Should see 
        
        pyDARN-pydarn-version.number-py3-none-any.whl  pydarn-version.number.tar.gz

- Install twine `python3 -m pip install --user --upgrade twine`
- Upload to testpypi `python3 -m twine upload --repository testpypi dist/*` 
    
    !!! NOTE
        you will need an account with testpypi for this to work

- View the pyDARN package on the link provided in the `twine upload` output, should have the README.md as the front description page. If not contact pyDARN lead developer. 
- Check that the test page looks good and that you can download `pydarn` from the test pypi: 
        
        python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-YOUR-USERNAME-HERE

- **Upload to PyPi**, this should be done by the pyDARN lead developer as it needs the pyDARN PyPi account: 
  
        python3 -m twine upload dist/*

- Test that it worked by looking at the [pyDARN PyPi page](https://pypi.org/project/pydarn/)
- Install from PyPi: `pip3 install pydarn` and try running pydarn 

### Post Release Checklist

After the above is done do the following to make sure everything is up to date: 

- Let the DVWG chair know a pyDARN release has been made to update the DVWG website 
- Email [DARN-users](darn-users@isee.nagoya-u.ac.jp) about the new release of pyDARN 
- Merge `main` back into `develop`:
        
        git checkout develop
        git pull origin develop
        git merge main
