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


## Branching 

In git, "branches" are used to make changes to the code without affecting the main codebase or the work of other developers. Once the changes on a new branch have been [tested](testing.md) and [reviewed](code_review.md) in a ["pull request"](PR.md), the new branch is merged into the main codebase. 

## Getting Started 

!!! Note
    Before you start writing new code, please create a new issue to describe what you are planning to do, and "assign" the issue to yourself. This lets other developers know what you are working on. See [issues](issues.md)

1. Clone the pydarn repo: 

        git clone git@github.com:SuperDARN/pydarn.git

    It is recommended by GitHub to create a [SSH key](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

2. Change to the `pydarn` folder
        
        cd pydarn

* Update the code
      
        git fetch
        git pull origin master

* Decide what branch to break off from:
    * HOTFIX: a fix that needs to be in master ASAP then branch from `master`
    * Documentation: existing  main documentation with an update then branch from `master`
    * New Documentation: documentation that doesn't exist in the main documentation then branch from `develop`
    * New code/fix that can wait for a release then branch from `develop`
    * Removing legacy code then branch from `develop`
    * Code based on another branch then branch from that branch name
  
        git checkout <branch name>

* Decide on the new branch name. It is recommended to use the following Prefixes:  
    * HOTFIX/ : a bug that needs to be fixed ASAP and pushed to `master`
    * FIX/ : a bug fix that can wait to be released 
    * EHN/ : an enhancement or new feature to the `develop` code
    * DOC/ : new or updating existing documentation 
    * DEP/ : deprecating code from the codebase
   
        git checkout -b <prefix/><branch name>

* Now you have created your own branch locally. Make the modifications to the code on this branch, and then run the following commands to commit the changes:
    
        git add <file changed>
        git commit -m <brief description of the change>

* Now "push" the changes to GitHub:

        git push origin <branch name>

* Repeat the above commands above as you work on the code changes 
* Once you have completed, documented, tested and update the [unit tests](pytest.md) then you can create a pull request, see [pull request](PR.md)
