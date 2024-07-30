<!--Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:
2024-07-30 CJM Rewritten

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->


# Testing Pull Requests 

Testing pull requests for pyDARN can help development move at a quicker pace. We use the online tools for GitHub to test and review new code.
Some pull request testing can take fifteen minutes or less to do, and allows you to be on the author list for the next release!

You can browse our open pull requests here: [Pull Requests](https://github.com/SuperDARN/pydarn/pulls).
When a developer wants to amend or add new code to the code base, they must first make a 'branch' off from the main code base to allow for their changes to be tracked properly, and make sure those changes do not interfere with the main code base. 
A pull request is when that developer has finished and wants the code to be included back in the main codebase, but we want to make sure that the code is working and does not break any existing code - therefore, we test it.

!!! Note
    It is always recommended to install different branches of pyDARN in Python virtual environments to make sure that 
    a) Your main installation of pyDARN is not affected, 
    b) You are definitely testing the correct branch and,
    c) Existing installations of pyDARN are not interacting with your testing.
    Read more about Python virtual environments here:[python virtual environment](https://docs.python.org/3.6/tutorial/venv.html)

1. Make and activate your virtual environment:  
`python3 -m venv venv-name-here`  
`source venv-name-here/bin/activate`  

2. Decide if you want to quick install or clone install the branch that requires testing.  

    a) Quick install by typing:  
    `pip install git+https://github.com/superdarn/pydarn@<branchname>`  

    b) Clone install by:  
    `git clone https://github.com/SuperDARN/pydarn.git`  
    Checkout the branch:  
    `git checkout <branchname>`  
    Move into repository and install this branch:  
    `cd pydarn`  
    `pip install .`  

    !!! Note
        You can check the installation of pyDARN if it appears in the list produced by `pip list`. This can also be used to check the version number of pyDARN and the required dependencies too.
  
    !!! Note 
        The branchname can be found at the top of the page below the Pull Request title and number shows the branch name and which branch it will be merged into. 

3. Now you are ready tu test the code. The developer who made the Pull Request should have written up a piece of test code and described the desired output (if they haven't, comment and ask for it!).
You will need to make a new Python file `test_code.py`, that includes the code, and will need to source any [data](https://pydarn.readthedocs.io/en/main/user/superdarn_data/) that you might need to use. 

4. Then run the file and interpret the outcome `python3 test_code.py`. It is always useful for the tester to make changes to the test code, use different key words, and different data to test for edge cases and all around usability of the new changes. 

6. What to write up in a comment once tested.  
    a) The code in your `test_code.py` file.  
    b) Any plots that the code has made - interpret them scientifically if you are testing science data and accuracy, or comment on their appearance if it a new type of plot. Is it clear, is it useful, should it be laid out differently?  
    c) If there are any errors, copy the whole traceback into a comment for the developer to read.  
    d) Include any attempts to circumvent or fix errors and how that worked out.  
    e) Include versions of dependencies required by developer - we always want to know what version of Matplotlib is being used!  
    f) Include suggestions if you are able and are doing a [code review](https://pydarn.readthedocs.io/en/main/dev/code_review/).  
    g) If you are unsure, include as much information as possible for the developer to follow and recreate what you have done.  

7. If everything worked as expected and you are happy with the code, you can **approve** the code officially if you are already part of the pyDARN development team by clicking `Files Changed` then clicking `Review Changes` and select *Approve*.
If you are not a member, please make a clear statement at the end of the comment saying if you require further changes, or you approve and think the pull request should be merged. 

!!! Note
    If the Pull Request has the required number of approvals stated by the developer (including your own) with no comments to respond to, then feel free to merge the code. The merge button is at the bottom of the Pull Request page, you can then also delete the branch (an option for this will show up once merged).
