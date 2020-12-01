# Testing Pull Requests 

One way to help pyDARN get developed faster and smoothly is by testing [Pull Requests](https://github.com/SuperDARN/pydarn/pulls). 
Sometimes this can take fifteen minutes to do which helps the developer merge their code in 
and allowing you on the author list. 

Every contribution helps! 

## Setting up the testing environment

1. clone the [pyDARN repository](https://github.com/SuperDARN/pydarn.git)
  `git clone https://github.com/SuperDARN/pydarn.git`
2. Then checkout the branch you need to test or test against. The author of the Pull Request should give you some information on how to test the code and if you need to checkout other branches to compare results. To checkout a branch you want to test use this git commands:
    ```bash
    git fetch 
    git checkout <branch name>
    git pull origin <branch name>
    ```

    !!! Note 
        if you are unaware what the branch name is at the top of the page below the Pull Request title and number shows the branch name and which branch it will be merged into. 

3. From here you just need to install the code run the normal installation steps in a python environment (this ensures it doesn't mix with your current pyDARN version)
    ```bash
    python3 -m virtual <environment name>
    source <environment name>/bin/activate
    ```
    
    !!! Note
        To install python's virtual environment library `https://github.com/SuperDARN/pydarn.git`

4. Next install the branch you are testing: `cd cloned/pydarn/` and `pip3 install . --user`
5. Once this is complete follow any test cases the documentation and Pull Request the author describes. 
Report anything in the Pull Request comments about how you tested the code, what your output is, and any feedback, or information.
6. Once you are satisfied with the Pull Request, **approve** it by clicking on the top `Files changed` then clicking Review changes and select *Approve*

!!! Note
    If the Pull Request has more than two approvals with no comments to respond to, then please merge the code. Merge button is at the bottom of the Pull Request page. 
