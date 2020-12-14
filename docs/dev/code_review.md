# Code Reviews 

Reviewing code is like proof reading a paper, it is essential to ensure the following: 

- code is user readable
- enforces consistency
- helps encourage collaboration
- code has a proper structure
- The algorithms and software are tested and verified 

Anyone can code review even if you don't program in the native language, which for pyDARN is python. 
Code reviewing is also an excellent learning experience which helps you better understand the software and how to program in general. 

If you are more advanced in the native programming language or science being implemented in the code, a short code review on finding any mistakes, or bugs in the code is more than welcome. 
This is not a requirement as it can be tedious and time consuming, and testing code should show these mistakes/bugs. If you wish to do this you can focus on one portion of the code to comb through. 

Code reviews should not take more than an hour and Pull Requests should be less than 400 lines.
However, these restrictions can be challenging for new features and major changes. 
If this is the case, then you can code review parts of a file or specific files to reduce your time spent. 

## How to start a Code Review 

1. Pick a Pull Request to code review, which can be found [here](https://github.com/SuperDARN/pydarn/pulls)
2. Click on `files changed` at the top of the PR conversation below the title on the right side 
    
    !!! Note 
        Before starting a code review always check for others comments, if something you have stated is already stated 
        then you can leave it alone or give a "thumbs up :+1" to the comment to show support. 

3. Now review the changes that occurred in this PR - avoid commenting on other lines not included in the changes as this is `scope creep`.
4. If you want to make a comment hover the cursor over the line numbers on the left side and a **+** button will appear. Click it!
5. Now write any feedback or questions in the box and hit `Start a review` on the bottom right in the pop up window. 
    
    !!! Warning
        Do not make several single comments as this can cause a lot of email notifications

6. If you want to change a line in the code use a [suggestion](https://haacked.com/archive/2019/06/03/suggested-changes/)
7. If you wish to comment on several consecutive lines hold **+** down and drag the cursor down to select multiple lines
8. Once you are done, click on `Finish your changes` or `Review changes` (if no comments made) then comment on any general feedback in the text box. This should include what type of review you did and if you will be continuing your review at a later time/date.  Some examples include:
  - Testing and code review to find a bug 
  - Code review on style/formatting 
  - Partial code review 
9. Select:  
  - Comment: general comments to be fixed up but nothing major
    
    !!! Note
        If you did a partial review please select comment. Approve is only done for complete reviews or complete testing 

  - Approve: everything looks good no changes needed
    
    !!! Note
        This should only be done on complete code reviews. You can also revert your approval after it is made if you find something else later. 
        Do this by going down to the merge button and find your name under approvals and click the three dots and select `re-review` 
  
  - Request Changes: major changes to make
      
    !!! Warning
        Request changes, prevents anyone from merging the code. Generally you will need to approve the changes that were addressed. 
        Generally if you cannot do this then do not use Request changes.

10. Submit! 

!!! Note
    If you want to make minor changes directly in the code like typos and grammar changes you can pull the code down described in [testing](testing.md)
    and change the code as you want and then re-push the code back to the code. The Developer can review the changes in your commit. 

### What to look for?

Here is a list of what to look for 

- Does it follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style?
- Is the copyright and license disclaimer in the file?
- Did they add the modification line if they made updates?
- Are there doc strings for the class and for functions?
- Are there confusing variables, functions, and/or class names? 
- Are there defaults and do they make sense for the function? 
- Is the code too complex? Could it be simpler? 
- Do the error messages/exceptions make sense and are helpful?
- Could there be more comments on certain sections?
- Are hard coded values documented? 
- Are algorithms or mathematical equations cited to publication, webpage, or book? 
- Does the nomenclature make sense? 
- Are there any cases they may need to reconsider? 
- Would comments or documentation make sense to the general user?

## How to speed up code reviews

Here are some tips and tricks:

- Dedicated a certain amount of time and just review what you can in that time period 
- Scan for missing doc strings and obvious mistakes 
- Focus on what has been changed 
- If an issue repeats then make a comment for them to fix the rest and add in the general feedback when submitting the comments 
- Do not get too pedantic!
- Break up the reviews if you can only review a few files or functions then do it and mention it. 

## Reviewing a review 
  
As a developer you will need to address any comments that come up from code reviews like you would with reviewers comments in a paper submission. 
Comments should addressed and resolved before merging the code. 

If you do step 2 and look at the comments in `files changed` view you can address multiple comments in one batch. 

### Batch Committing of Suggestions 

First look for all the suggestion comments and if you agree then add to `batch suggestions`, once you have gone through all them 
then at the top in the middle there is `commit suggestions` and this commit all the suggestions for you. 

### Responding to Comments 

If you don't agree with a suggestion try to find a compromise or acknowledge their effort and explain why you prefer your style.
Remember to hit `Start a review` to prevent multiple email notifications. 

If you made the change requested, then select `resolve conflict` so they know you addressed their comment.

If you are answering a question or responding to some feedback, remember to acknowledge their time and effort, then address it in collaborative manner. 
Remember to hit `Start a review` to prevent multiple email notifications. 

Once all comments are addressed then follow steps 9-10 in the `How to start a Code Review` section. 

## General Guidelines

Here are some general guidelines to follow when code reviewing or responding to one: 

- Dedicate time to review in a given period, avoid being distracted 
- Ask questions instead of stating 
- Remember to comment on the code 
- Acknowledge time spent and say "Thank you" 
- Suggest solutions or help
- Avoid aggressive terminology 
- Avoid reviewing in a bad mood or feeling pressured/rush 
- Review all comments to make sure it sounds helpful and not demeaning 
- Avoid pedantic points, focus on what is needed and not personal preferences 
- Any amount of reviewing small or large is welcome! 
- Approve! Make sure to comment what type of approval you are giving, complete testing or a complete reviewing of the code. This will help others know what needs to be done to get the PR closer to `merge` 

!!! Note
    If you approve the PR and you are the second to approve, or there are already 2 approvals and all concerns are addressed 
    with one approval on testing and one approval on code review, please merge the PR! An exception to this is if  it is a release PR or if more than two approvals are requested in the PR instructions. 

!!! Note
    Do not be scared to `approve` or `merge` code as it can be reverted quite easily if it needs to be. Also, reach out and ask if you are unsure! 
