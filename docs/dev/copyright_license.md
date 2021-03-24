<!---
(C) copyright 2019 SuperDARN Canada, University of Saskatchewan 
(C) copyright 2021 The University Centre in Svalbard (UNIS)

authors: Marina Schmidt, SuperDARN Canada
         Emma Bland, UNIS

pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU Lesser General Public License, supplemented by
the additional permissions listed below.

       
Modifications:
          Emma Bland, UNIS, 2021-02-12 : added background information about LGPL, why copyright information is required, FAQ, and pyDARN license history 
          Marina Schmidt, University of Saskatchewan: added LGPL license for pyDARN
-->


Licensing of pyDARN

The SuperDARN pyDARN library is licensed under the [GNU Lesser General Public License (LGPL) v3.0](https://www.gnu.org/licenses/lgpl-3.0.html). This license guarantees that end users have the freedom to use, modify and share the software. The *Free Software Foundation*, which published the LGPL, explains that:

> *"The licenses for most software and other practical works are designed to take away your freedom to share and change the works. By contrast, the GNU Lesser General Public License is intended to guarantee your freedom to share and change all versions of a program--to make sure it remains free software for all its users."*


> *"Developers that use the GNU LGPL protect your rights with two steps: (1) __assert copyright__ on the software, and (2) __offer you this License__ giving you legal permission to copy, distribute and/or modify it."*

This license ensures that the scientific community (and everyone else) is legally permitted to use, copy, modify and redistribute the pyDARN library. In this way, the library can be maintained and improved over time to support the advancement of science. 


## License requirements

The LGPL v3.0 License states that:

- The pyDARN source code must be distributed with the library
- License and copyright information must be included at the top of each source code file (more info on copyright below)
- If the code has been modified, there must be a notice stating that it has been modified, by who, and when
- Modifications must be released under the same license as pyDARN (LGPL v3.0 or later)


### License notices

The software must include the following notices: 

``` C
/*
<one line to give the program's name and a brief idea of what it does.>
Copyright (C) <year>  <name of author>

This file is part of the pyDARN Library.

pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU Lesser General Public License, supplemented by
the additional permissions listed below.

Modifications:
          <fist and last name>, <institution> <year-month-day of the modification> : <comment on the change (optional)> 
*/
```

According to the [LGPL license documentation](https://www.gnu.org/licenses/lgpl-3.0.en.html): 

> *"It is safest to attach them to the start of each source file to most effectively state the exclusion of warranty; and each file should have at least the “copyright” line and a pointer to where the full notice is found.*"

## License permissions

When developing in pyDARN you are granting permission for your code to be licensed under the LGPL. This will be ok in almost all situations. Exceptions may arise if your employer wants to make your program into its own proprietary software/library, or if your funding agency has restrictions on the publication of research outputs (e.g. defense contracts). If you suspect that you won't be allowed to contribute code to pyDARN under the LGPL, [it is recommended](https://www.gnu.org/licenses/gpl-faq.html#WhatIfSchool) that you negotiate this with your employer/funding agency at an early stage in developing the software. 

!!! IMPORTANT
    Please make sure to review the [license](https://www.gnu.org/licenses/lgpl-3.0.html), and check with your employer/funding agency that you have permission to distribute your code under the LGPLv3. 

## Copyright

The LGPL license requires that all code includes a copyright notice. The purpose of the copyright notice is to __protect the rights of the developers__ by:

  1. Giving them (and their employer) credit for their work
  2. Preventing their code from being distributed under a different license without their knowledge/permission
  3. Giving them the power to enforce the terms of the license<br>
     *e.g. take someone to court if they violate the license*

### How to copyright your code

You should add copyright information if you have written new code from scratch or substantially modified someone else's code. Examples of substantial modifications to existing code include significant changes to the code's structure or functionality. This is a gray area, so use your best judgment and ask other developers at the pull request stage if you are unsure. 

!!! IMPORTANT
    Ask your employer about what to write in your copyright line. If you contribute to the pyDARN library in your free time, then just put your own name in the copyright line.


An example copyright line structure is:

``` C
/*
(C) copyright <year> of <institution/entity>

author: <first and last name>, <institution>
/
```

Since pyDARN is developed collaboratively by the SuperDARN community, it may be appropriate to have multiple copyright lines in a single source file, for example: 
``` C
/*
(C) copyright <year> of <institution/entity>
(C) copyright <year> of <another institution/entry>

authors: <first and last name>, <institution>
         <first and last name>, <institution>

Modifications: 
           <fist and last name>, <institution> <year-month-day of the modification> : <comment on the change (optional)> 
*/
```

!!! IMPORTANT
    Never remove the existing copyright information from a source file.

#### Minor modifications

Adding copyright notices is appropriate only for __substantial__ modifications. If you make minor modifications to someone else's code (e.g. bug fixes), then you should document this in the modification history (example above), but do not add a new copyright line. 

## Frequently asked questions

__Can pyDARN be released with a different license?__<br/>
To release pyDARN with a different license, we would need permission from all of the copyright holders. This means that, in practice, it would be very difficult to re-license the software. This is by design of the LGPL license--it ensures that the library can always be used freely. 

__What happens if I don't include copyright information in my code?__<br/>
In most countries, authors automatically hold the copyright to their own work even if they don't add a copyright notice. This is to protect the rights of people who are not aware of the law. However, omitting copyright information means that:

- You may be breaching your employment contract
- You are not complying with the LGPL requirement to include copyright information
- You may not get credit for your work
- It is more difficult for you to prove that you are the copyright holder


__Do I have to include my institution in the copyright line?__<br/>
That depends on the terms of your employment. Check your employment contract or ask the research office. If you contribute to the pyDARN library in your free time, then just put your own name in the copyright line.

__Can I copyright code to a generic "SuperDARN" organization?__<br/>
No, the copyright holder has to be a legal entity or a person. Your employer may also object to this. If you contribute to the pyDARN library in your free time, then just put your own name in the copyright line.

__Why does every pyDARN source file have license notices at the top? Isn't it sufficient to include the license file in the top-level directory of pyDARN?__<br/>
Since the LGPL allows users to modify and redistribute portions of the pyDARN library, it is possible that individual source files might become separated from the license file. If this happens, it will be unclear to users what their legal rights are to use/modify/distribute that version of the code (which is a violation of the LGPL). Therefore, all source files should clearly indicate that they are licensed under the LGPL (writing "see license.txt" is not sufficient).

__If I add a new library to pyDARN, can that library have a different license?__<br/>
If the new library was originally developed outside of pyDARN, the author of that library can choose to license it under another license as long as it complies with LGPL license when adding it to pyDARN. Code that has been developed within pyDARN must be licensed under LGPL.


__I've added code to pyDARN. Can I also release my code under a different license?__<br/>
Yes, provided that you are the copyright holder of the code, and that it is a standalone library (developed outside of pyDARN), you are free to license it under different non-exclusive licenses ([more info](https://www.gnu.org/licenses/gpl-faq.html#ReleaseUnderLGPLAndNF)). Remember that:

__Am I allowed to copy code from pyDARN into my own software project? What do I have to do to comply with pyDARN's license?__<br/>

- You are free to copy or modify any portion of the pyDARN code
- You are free to share the software outputs (data files, plots)

__Who owns the outputs of pyDARN (processed data files, plots)?__<br/>
pyDARN outputs belong to the end user who created them. The user is free to share them under any terms, and is not bound by the LGPL.

__I have more questions about the LGPL__<br/>
There's lots of helpful information [here](https://www.gnu.org/licenses/gpl-faq.html).
