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

## Unit Testing

Unit testing in pyDARN is a way to check that pydarn is running correctly with any new changes to the code. These tests are meant to be simple and short to only test input (parameter) changes to ensure the code does not fail. 
Exceptions can also be tested to make sure it fails correctly. Please note testing in pyDARN is for validity (code runs as it should) but not validation (outputting accurate plots). Validation testing is done by users who understanding the scientific accuracy the plots represent. 

pyDARN uses [`pytest`](https://docs.pytest.org/en/6.2.x/) for unit testing. 

## Using `pytest`

Running `pytest` in pyDARN is for developers and testers that work with GitHub. To run `pytest` in pyDARN:

!!! Warning
    Make sure you install pytest in your virtual environment or on your computer

1. [clone the pydarn repository](https://github.com/superdarn/pydarn)
2. change directory to pyDARN `cd pydarn`
3. install pydarn `pip install . --user` 
    - you can install a [virtual environment](../users/install.md) first to protect your current pyDARN install 
4. now run pytest `pytest` it should report no fails 
5. If it reports a fail please look into it if you are the developer of the change, or report it on the pull request if you are testing

## Writing pytest tests 

### Adding to Pre-existing Tests 

Changing, adding, and/or removing parameters from pyDARN methods, means the test code will need to change in the `parameterize` decorator. Please refer to the `test_<module>.py` file that corresponds with the methods module you changed.

- If you **changed a parameters input type, limitation, or name**, then look for the parameter in the `parameterize` decorators list (typically above the class) and changed the `key` name if you changed the parameter name or `value` if the type or limits are changed. Then update the method calls that take the parameter.  
- If you **add a new parameter** to a pyDARN method, then add a `parameterize` decorator before the class (with the other ones) and add the parameter name as the `key` name and add potential `value` test cases. (Not too many as this will make it slow to test). Make sure to add it to the corresponding method tests as well. 
- If you **remove a parameter** then remove the `parameterize` decorator corresponding to the parameter. 

### Adding a New Test Module

If you are creating a new class or module (new python file) then you will need to add a new test module (file) to the `pydarn/test` directory. 
Name the file test_<module/class name>.py such that `pytest` can find it and run it. 

You can use `test/test_rtp.py` as a template on how to write test code and read [`pytest`](https://docs.pytest.org/en/6.2.x/) on other plugins to for testing if its needed. 

Make sure to add what is needed to test and not too many parameterization options as it will make the tests go slow. Keep it to bare minimum needed to the test the parameter input. 
Remember this is not to test the accuracy as pytest cannot look at the plot but rather to test edge cases of parameters that make it fail.

!!! Note
    There are files provided for testing in the `test/data/` directory. If you need to add please keep the file size as small as possible and check in with other before adding. If its too big, it may not be able to be added to GitHub and cause pydarn to be slow to download. 

To avoid writing several tests with the same body of code, consider using the `paranetrize` to provide various types of inputs for one function. 

If you want to reuse `parameterize` parameters for other tests place them in a class, all methods of that class have to take the `parameterize` parameters. One can add more parameters to a method by placing the `parameterize` decorator and parameter name above it and then include in the methods input. 
