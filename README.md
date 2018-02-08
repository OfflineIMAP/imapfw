
[![imapfw](logo.png)](https://github.com/OfflineIMAP/imapfw)

**imapfw is a simple and powerful framework to work with mails.**

Also, it comes as a replacement to the [OfflineIMAP syncer][offlineimap].
**Check out the [official website][website] to get last news *([RSS][feed])* about imapfw.**
Also, we have room at
[![Gitter](https://badges.gitter.im/OfflineIMAP/imapfw.svg)](https://gitter.im/OfflineIMAP/imapfw?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
for more instant chatting.

<!--

I'm tired to update this. Will reborn once a script for releases will be written.

[![Latest release](https://img.shields.io/badge/latest release-v0.020-blue.svg)](https://github.com/OfflineIMAP/imapfw/releases)

-->


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
    <td> Website </td>
    <td> http://imapfw.offlineimap.org </td>
  </tr>
  <tr>
    <td> License </td>
    <td> The MIT License (MIT) </td>
  </tr>
  <tr>
    <td> Status </td>
    <td> <i> Work In Progress </i> </td>
  </tr>
</table>


* [![Build Status: "master" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=master)](https://travis-ci.org/OfflineIMAP/imapfw) (master)
* [![codecov.io](https://codecov.io/github/OfflineIMAP/imapfw/coverage.svg?branch=master)](https://codecov.io/github/OfflineIMAP/imapfw?branch=master) (master)
* [![Coverage Status](https://coveralls.io/repos/github/OfflineIMAP/imapfw/badge.svg?branch=master)](https://coveralls.io/github/OfflineIMAP/imapfw?branch=master) (master)
* [![Build Status: "next" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=next)](https://travis-ci.org/OfflineIMAP/imapfw) (next)
* [![codecov.io "next" branch](https://codecov.io/github/OfflineIMAP/imapfw/coverage.svg?branch=next)](https://codecov.io/github/OfflineIMAP/imapfw?branch=next) (next)
* [![Coverage Status "next" branch](https://coveralls.io/repos/github/OfflineIMAP/imapfw/badge.svg?branch=next)](https://coveralls.io/github/OfflineIMAP/imapfw?branch=next) (next)



![demo](https://raw.githubusercontent.com/OfflineIMAP/imapfw.github.io/gh-pages/images/imapfw.gif)


# Features

#### Scalable

As a framework, imapfw allows you to take control on what gets done:

* Embedded actions (softwares) requiring to write few to no Python code at all.
* For more control, a dedicated API allows to redefine the key parts of the
  frame in one file (called the *rascal*).
* Finally, most experienced users might rather directly import one or more
  modules and use them to write full softwares, using the framework as a
  "master-library": imapfw is written with **separation of concerns** in mind.

The choice of the level of control is left to the user.

#### All batteries included

The framework is intended to provide everything is needed. If any key library is
missing, it's welcome to make requests.

#### Simple

imapfw provides nice embedded actions. They can be used like any other software
sharing the same purpose.

#### Fast

Mainly relying on UIDs greatly helps to be fast.

Also, imapfw is designed to be fully concurrent. It even let the choice of the
concurrency backend (multiprocessing or threading, for now). To take real
advantage of this, implementation is made asynchronous almost everywhere.

#### Good documentation

Providing good documentation is a concern.

#### Quality

* Testing the framework is done with both static and dynamic testing. Each is
  used where it's the most relevant:
  - low-level code and modules have unit tests;
  - features like *actions* have black box tests.

* Continuous integration is done with [Travis CI][travis].

* The project is developed with a proven release cycle and release candidates.

#### Code

In order to offer the best, imapfw relies on the latest Python 3 technologies.
It uses the most usefull of what Python 3 provides.


# Requirements

* Python 3 (starting from v3.3)
* typing (for Python < 3.5)


# Status

imapfw is **WORK IN PROGRESS**. Running imapfw should not hurt but all the
features are not yet implemented. This is still early stage of development.

Last WIP is in the [`next`
branch](https://github.com/OfflineIMAP/imapfw/tree/next).  Also, you might like
to read our [CONTRIBUTING page][contributing] and check the [TODO list][wiki]
online.


# Supporting

Please, support the efforts! Staring the project at github is a good start.
Reviews, feedbacks and pull requests are welcome, too. ,-)

> Side note: I'm convinced that sooner is better when it's about reviews and
> feedbacks. Once features you need will be implemented, it might be harder
> to get things improved or take more time to get imapfw to fit your needs.


# Screencasts

[Channel of all the screencasts](http://www.dailymotion.com/offlineimap-project).

* [introduce imapfw syncAccounts](http://www.dailymotion.com/video/x3gpqqs_introduce-imapfw-syncaccounts_tech)

[![Introduce imapfw syncAccounts](https://raw.githubusercontent.com/OfflineIMAP/imapfw.github.io/gh-pages/images/dev-introduce-syncAccounts.png)](http://www.dailymotion.com/video/x3gpqqs_introduce-imapfw-syncaccounts_tech)

[subscribe]: http://lists.alioth.debian.org/mailman/listinfo/offlineimap-project
[offlineimap]: https://github.com/OfflineIMAP/offlineimap
[imapfw]: https://github.com/OfflineIMAP/imapfw
[website]: http://imapfw.offlineimap.org
[feed]: http://imapfw.offlineimap.org/feed.xml
[travis]: https://travis-ci.org/OfflineIMAP/imapfw
[wiki]: https://github.com/OfflineIMAP/imapfw/wiki
[contributing]: https://github.com/OfflineIMAP/imapfw/blob/next/CONTRIBUTING.md
