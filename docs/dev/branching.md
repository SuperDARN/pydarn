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


## Developing New Features

In git, "branches" are used to make changes to the code without affecting the main codebase or the work of other developers. Once the changes on a new branch have been [tested](testing.md) and [reviewed](code_review.md) in a ["pull request"](PR.md), the new branch is merged into the main codebase. 

## Getting Started 

!!! Note
    Before you start writing new code, please create a new issue to describe what you are planning to do, and "assign" the issue to yourself. This lets other developers know what you are working on. See [issues](issues.md)

1. Clone the pydarn repo, the default branch will be 'develop': 

        `git clone git@github.com:SuperDARN/pydarn.git`

2. Change to the `pydarn` folder
        
        `cd pydarn`

3. Decide what branch to break off from:
    * HOTFIX: a fix that needs to be in main ASAP then branch from `main`
    * Documentation: existing main documentation with an update then branch from `main`
    * New Documentation: documentation that doesn't exist in the main documentation then branch from `develop`
    * New code/fix that can wait for a release then branch from `develop`
    * Removing legacy code then branch from `develop`
    * Code based on another branch then branch from that branch name
  
        `git checkout <branch name>`
        `git pull origin <branch name>`

4. Decide on the new branch name. It is recommended to use the following Prefixes:  
    * HOTFIX/ : a bug that needs to be fixed ASAP and pushed to `main`
    * FIX/ : a bug fix that can wait to be released 
    * ENH/ : an enhancement or new feature to the `develop` code
    * DOC/ : new or updating existing documentation 
    * DEP/ : deprecating code from the codebase
   
        `git checkout -b <prefix>/<new branch name>`

5. Now you have created your own branch locally. Make the modifications to the code on this branch, and then run the following commands to commit the changes:
    
        `git add <file changed>`
        `git commit -m <brief description of the change>`

6. Now "push" the changes to GitHub:

        `git push origin <new branch name>`

7. Repeat the above commands above as you work on the code changes 
8. Once you have completed, documented, tested and updated the [unit tests](pytest.md) then you can create a pull request, see [pull request](PR.md)

# Tips to Keep in Mind

 - If making a whole new module, read up on how to structure and have the module accessible to the rest of the code: [library structure](https://docs.python-guide.org/writing/structure/)
 - Make a short piece of code that tests your feature - this is helpful for you to test as you develop but also helpful to show testers how they can use your new feature.
 - Make sure that the code does not interfere with, change or break another part of the code base - this means you need to test anything peripheral to the code you have added too.
 - Write up some documentation! Documentation can be found in the docs directory and is written in markdown.
 - [Kwargs](https://realpython.com/python-kwargs-and-args/) - very useful to pass keyword arguments through various methods.
 - [Enum](https://realpython.com/python-kwargs-and-args/) is extremely helpful for when a keyword has multiple options to choose from (not just True, False).
 - pyDARN has implemented a standard return dictionary, so make sure that if you develop a new plot that you format your plot return the same as all others.