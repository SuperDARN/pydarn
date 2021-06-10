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

# Issues 

GitHub Issues are a convenient way to communicate with pydarn developers about future changes to the pydarn codebase. Issues are not just for bug reporting. They can also be used to:

- Notify others that a new feature is being planned
- Ask for help or advice on using/installing pyDARN
- Initiate open discussions about a pydarn-related topic

When opening a new issue on the pyDARN Github page, you will be prompted to use a template to describe your issue. These templates are designed to help you provide enough detail for other developers to respond.

!!! IMPORTANT
    pyDARN no longer maintains reading and writing SuperDARN data formats. Please address all issues on reading and writing to [pyDARNio](https://github.com/SuperDARN/pyDARNio)

## Other Working Group Issues

Please only open issues related to pyDARN. Questions on the following topics should be directed elsewhere:

- Reading/Writing SuperDARN files into pyDARN: [pyDARNio](https://github.com/SuperDARN/pyDARNio)
- Processing methods and algorithms of SuperDARN data: [Radar Software Toolkit](https://github.com/SuperDARN/rst)
- Corrupt or missing RAWACF files: [Data Distribution Working Group (DDWG)](https://github.com/SuperDARN/DDWG)
- Radar data formats, hardware files and other metadata: [Data Standards Working Group (DSWG)](https://github.com/superdarn/dswg-published-docs)
- Radar control programs and operating schedules: [Scheduling Working Group (SWG)](http://superdarn.thayer.dartmouth.edu/wg-scd.html)
- General questions for the Data Analysis Working Group (DAWG) that are not specifically about pyDARN: open an issue on the [internal DAWG Github repo](https://github.com/SuperDARN/dawg) (requires access rights) or email the [DAWG mailing list](mailto:darn-dawg@isee.nagoya-u.ac.jp)

## Submit an Issue

To open a new issue, follow these steps from the [pyDARN repository](https://github.com/SuperDARN/pydarn)

1. Click the [issues tab](https://github.com/SuperDARN/pydarn/issues) on the top left side of the page 
2. Check whether there is already an open issue on your topic. You can use the search bar to find similar issues. 
3. If there are no similar issues, click the [New issue](https://github.com/SuperDARN/pydarn/issues/new/choose) button (top right)
4. Choose an issue template, or select *open a blank issue* at the bottom of the page if none of the templates seem appropriate
5. Fill out the template information, and add a descriptive title
6. Fill out the side bar information:  
    - Assignees: Assign yourself to the issue if you are planning to work on it yourself. Leave blank if you are not planning to work on it.
    - Labels: these are used to categorize and filter issues (examples below). You can have multiple labels. 
    - Projects: Indicate if this issue is part of a [project](projects.md)
    - Milestone: Please leave this blank. The DAWG chairs will fill in this information later when a timeline emerges (e.g. working towards a new release)
    - Linked Pull Request: Leave this blank for now. This can be filled out when a pull request that solves this issue is created (see [pull requests](PR.md))
* Click *Submit new issue*. At this point, everyone who is subscribed to the pyDARN repository will receive an email. Depending on your notification settings, you may receive emails when others comment on the issue. Check your user settings to subscribe or unsubscribe to email notifications.


## Following The Issue

Please follow the ongoing conversation about your issue, especially if other developers request more information. 
If you do not respond for a while, the issue will go **stale** and may be closed. DAWG tries to keep issues open and contact users if their issues have gone stale. 

Please keep in mind that DAWG members have priorities other than pyDARN, and they live in many different time zones, so be patient while waiting for a response. If nobody has responded in 1-2 weeks, it's fine to ask again.

## Closing Issues

Issues should be closed when:

- A [pull request](PR.md) that addresses the issue is merged
- The original question raised in an issue has been answered

If new issues emerge during a discussion, open a new issue and discuss it there. This is to avoid scope creep.

## Stale Issues

If an issue goes stale (no progress for over 3 months), the pyDARN lead developer may follow this procedure:

1. Ask about the issue's status in the conversation
2. Email the user who opened the issue
3. Request that we discuss the issue in the next DAWG meeting (add label *telecon*), or place it in a project to be re-opened later
* Label the issue **stale** until progress can be made on it again
* Request to close the issue if none of the above steps elicit any information to keep it open
* DAWG chairs can close **stale** issues

## Assignees

The Assignees section is used to indicate who (if anyone) is actively working on each issue. This helps to avoid duplicated work, and to identify issues that nobody is currently working on (if you are looking for something to do!).
If you would like to offer assistance on an issue that someone else is assigned to, please ask them first. If you agree to take over the issue from them, assign yourself to it.

## Labels 

pyDARN supports the following [labels](https://github.com/SuperDARN/pydarn/labels):

| Label             | Definition                                                  |
| ----------------- | ----------------------------------------------------------- |
| bug               | Issue is about a potential bug                              |
| DAWG              | Issue for Data Analysis Working Group                       |
| DDWG              | Issue for Data Distribution Working Group                   |
| default change    | Default change in one of the methods                        |
| Deprecation       | Removing legacy code/feature from the codebase              |
| discussion        | Issue requires a discussion                                 |
| documentation     | Issue pertains to documentation                             |
| DSWG              | This is DSWG issue                                          |
| duplicate         | There is already another issue about the same problem       |
| enhancement       | Issue pertains about enhancing pydarn                       |
| good first issue  | Good for newcomers                                          |
| Error/Warning     | Issue is purposing an new error or warning check for pydarn |
| help wanted       | Issue is looking for some help on the problem               |
| high priority     | Issue needs to be looked at over others                     |
| invalid           | Issue about something being invalid                         |
| low priority      | Issue is not very important at the time                     |
| PyDARNio issue    | Issue for pyDARNio                                          |
| Programmer needed | Issue needs programmers help                                |
| question          | Issue regards to a question                                 |
| RST               | Issue for RST                                               |
| Scientist input   | Issue needs Scientist help                                  |
| telecon           | Issue needs to be discussed in a telecon                    |
| wontfix           | Issue could not be fixed                                    |
| workaround        | Issue was fixed with a workaround                           |


### Creating A New Label

To create a new label go to [pydarn labels](https://github.com/SuperDARN/pydarn/labels) and click on [New label](https://github.com/SuperDARN/pydarn/labels)

Give a concise name for the label and provide a description. A color can be randomly generated or chosen based on the hex value. Please avoid similar colors to other labels if possible. 

Then click on *Create Label*.

!!! WARNING
    Avoid creating new labels when creating a new issue: this can delete the issue being created!

## Open-ended Issues 

Sometimes Issues can be open-ended, especially discussion issues. Here are some steps to make progress on the issue and prevent it going **stale**:
- Label it with *telecon* if needs to be further discussed in a telecon with DAWG members 
- Once a general idea is established, close the issue and create a project to break it into a defined tasks. Open the first task as an issue, see [projects](projects.md).
