<!--Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan 
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


# Testing Pull Requests 

One way to help pyDARN get developed faster and smoother is by testing [Pull Requests](https://github.com/SuperDARN/pydarn/pulls). 
This can take fifteen minutes or less to do, helps the developer merge their code,
and allows you to be on the author list!

Every contribution helps! 

## Setting up the testing environment

If you haven't cloned pyDARN before this will get you the correct branch installed to just test:
`pip install git+https://github.com/superdarn/pydarn@<branchname>`
Make sure to install any new instances of pyDARN, or branches that are not master in a virtual environment to avoid mixing pyDARN versions! 


If you wish to clone pyDARN for multi-branch comparison or testing in the future: 

1. Clone the [pyDARN repository](https://github.com/SuperDARN/pydarn.git) by typing 
  `git clone https://github.com/SuperDARN/pydarn.git`
  into the terminal or command line.
2. Then checkout the branch you need to test or test against. The author of the Pull Request should give you some information on how to test the code and if you need to checkout other branches to compare results. To checkout a branch you want to test use this git commands:
    ```bash
    git fetch 
    git checkout <branch name>
    git pull origin <branch name>
    ```
These lines *fetch* metadata on any new branches made, *checkout* the right branch you want to test and then *pull* changes to that branch so you're not behind any new changes made.
    !!! Note 
        if you are unaware what the branch name is at the top of the page below the Pull Request title and number shows the branch name and which branch it will be merged into. 

3. From here you just need to install the code run the normal installation steps in a python environment (this ensures it doesn't mix with your current pyDARN version)
    ```bash
    python3 -m virtual <environment name>
    source <environment name>/bin/activate
    ```
    for more information on [python virtual environment](https://docs.python.org/3.6/tutorial/venv.html) or to use conda with pyDARN see the [installation documentation](../user/install.md)

4. Next install the branch you are testing by moving to the pyDARN directory you just cloned and running `pip3 install . --user`
5. Once this is complete follow any test cases the documentation and Pull Request the author describes. 
Report anything in the Pull Request comments about how you tested the code, what your output is, and any feedback, or information.
Note: To suggest changes to and/or comment on certain sections of code, navigate to the Files Changed tab where it is possible to select multiple lines of code by clicking and dragging the '+' symbol next to line of code.
6. Once you are satisfied with the Pull Request, **approve** it by clicking on the top `Files changed` then clicking Review changes and select *Approve*. Make sure to comment what you did in testing for your approval. 

!!! Note
    If the Pull Request has more than two approvals (one for code review and another for testing) with no comments to respond to, then please merge the code. Merge button is at the bottom of the Pull Request page. 
