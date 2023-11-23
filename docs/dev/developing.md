<!--Copyright (C) 2023 SuperDARN Canada, University of Saskatchewan 
Author(s): Carley Martin 
Modifications:

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->

# Quick Guide to Developing

Once you have decided on an issue that you would like to develop, or have decided to develop your own feature, you can follow the rough guidelines below to develop your feature.
Each developer has different preferences on how they develop, text editors, OS and style. All are valid and you can use whatever method you wish to achieve the development of a new feature. Below is a quick run-through of how I (Carley) develop a new feature using a basic text editor and command line directly as a branch of the main repository.
It is not required, but probably useful if you have a relatively good knowledge and some experience of writing code in python - however, any style or efficiency issues can be picked up by the testers and fixed then!

Firstly, if you don't have the repository cloned, find a suitable location where you would like the repo and clone:
```
git clone https://github.com/SuperDARN/pydarn.git
```
The default branch is `develop` so your repository will already be showing the development branch. If you have the repository clones already, make sure to pull any new changes to the develop branch:
```
cd pydarn
git pull origin develop
```
Now, we want to make a new 'branch' of the repository where only the changes you are making will be present and it won't interfere with anyone else developing. 
```
git checkout -b ehn/new-feature-name
```
This command will create a new branch with the name 'ehn/new-feature-name' and move to that new branch.

You can now change any code in the new branch and it will not effect the development branch. You can add a whole new module - make sure you add anything you wish to call using pyDARN to the `__init__.py` file.

I suggest that you install and run the code frequently during development to check that everything is running as expected.
To do this make a virtual environment, install the branch of pyDARN and run some testing code you have developed. 
```
python3 -m virtualenv (or venv if 3.10+) venv-feature-name
source venv-feature-name/bin/activate
cd pydarn (make sure you are in the pydarn git repository)
pip3 install .
python3 your_testing_code.py
```

!!! Note
    If repeatedly testing, make sure to uninstall pydarn before reinstalling to pick up the changes.
    `pip3 uninstall pydarn`

If you wish to push finished or partially finished code to the repository on GitHub so others can see and test:
```
git status
git add .
git commit -m 'commint message here - what did you change, what's new ect.'
git push origin ehn/new-feature-branch
```

You can then continue developing, or if you have completed the feature, make a [pull request](dev/PR.md)!

# Tips to Keep in Mind

 - If making a whole new module, read up on how to structure and have the module accessible to the rest of the code: [library structure](https://docs.python-guide.org/writing/structure/)
 - Make a short piece of code that tests your feature - this is helpful for you to test as you develop but also helpful to show testers how they can use your new feature.
 - Make sure that the code does not interfere with, change or break another part of the code base - this means you need to test anything peripheral to the code you have added too.
 - Write up some documentation! Documentation can be found in the docs directory and is written in markdown.
 - [Kwargs](https://realpython.com/python-kwargs-and-args/) - very useful to pass keyword arguments through various methods.
 - [Enum](https://realpython.com/python-kwargs-and-args/) is extremely helpful for when a keyword has multiple options to choose from (not just True, False).
 - pyDARN has implemented a standard return dictionary, so make sure that if you develop a new plot that you format your plot return the same as all others.
