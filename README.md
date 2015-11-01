
# imapfw

<!-- Markdown sucks for tables without headers. -->

<table>
  <tr>
    <td> Author </td>
    <td> Nicolas Sebrecht </td>
  </tr>
  <tr>
    <td> Source </td>
    <td> http://github.com/OfflineIMAP/imapfw </td>
  </tr>
  <tr>
    <td> License </td>
    <td> The MIT License (MIT) </td>
  </tr>
  <tr>
    <td> Status </td>
    <td> Work In Progress </td>
  </tr>
</table>



**imapfw is a simple and powerfull framework to work with IMAP and Maildir. It
comes as a replacement to the [OfflineIMAP syncer][offlineimap].**

* [![Build Status: "master" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=master)](https://travis-ci.org/OfflineIMAP/imapfw) for branch "master"
* [![Build Status: "next" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=next)](https://travis-ci.org/OfflineIMAP/imapfw) for branch "next"


**Read the [blog][blog] to get last news about imapfw.**


## Features

#### Scalable

As a framework, imapfw allows you to take control on what gets done.

It comes with pre-configured actions requiring to write few to no Python code at
all. For more control, a dedicated API allows to redefine the key parts of the
frame in one file (called the rascal). Also, the more experienced users might
rather directly import one or more modules and use them to write a full
software: imapfw was written with *separation of concerns* in mind.

The choice of the level of control is left to the user.

#### All batteries included

The framework is intended to provide everything is needed. If any key library is
missing, it's welcome to make requests.

#### Simple

imapfw provides nice embedded pre-configured actions for real beginners. It can
be used as any other software sharing the same goals.

#### Fast

imapfw is designed to be fully concurrent. It even let the choice of the
concurrency backend to use (multiprocessing or threading, for now). To take
real advantage of this, implemetation is made asynchronous everywhere.

Mainly relying on UIDs greatly helps to the purpose.

#### Good documentation

Providing good documentation is a concern.

#### Quality

Testing the framework is done with both static and dynamic testing. Each is used
where it's the most relevant:
- low-level code and modules have unit tests;
- features like *actions* have black box tests.

Continous intergration is done with [Travis CI](https://travis-ci.org/OfflineIMAP/imapfw).

The framework is developed with proven release cycle.

#### Code

In order to offer the best, imapfw relies on the last Python 3 technologies. It
uses the more usefull of what Python 3 provides such as annotations.


## Feedbacks and contributions

**The user discussions, development, announcements and all the exciting stuff
take place on the OfflineIMAP's mailing list and github.**

While not mandatory to send emails, you can [subscribe
here](http://lists.alioth.debian.org/mailman/listinfo/offlineimap-project).

Bugs, issues and contributions can be requested to both the mailing list or the
[official Github project][imapfw].


## Requirements

* Python v3.3

## Warning

imapfw is still **WORK IN PROGRESS**. Running imapfw should not hurt but all the
features are not yet implemented since this is still early stage of development.

Last WIP is in the `next` branch.

## Supporting

Please, support the efforts! Staring the project is a good start.
Reviews and feedbacks are welcome, too. ,-)

[offlineimap]: https://github.com/OfflineIMAP/offlineimap
[imapfw]: https://github.com/OfflineIMAP/imapfw
[website]: http://offlineimap.org
[blog]: http://offlineimap.org/posts.html

