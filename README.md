[offlineimap]: https://github.com/OfflineIMAP/offlineimap
[imapfw]: https://github.com/OfflineIMAP/imapfw
[website]: http://offlineimap.org
[blog]: http://offlineimap.org/posts.html

# imafw


## WARNING

imapfw is still **WORK IN PROGRESS**. It won't do anything good for now. This
project is made public for **developpers** only.

Last WIP is in the `next` branch. Since this is still very early stage
development, rebasing might happen everywhere.

**Read the [blog][blog] to get last news.**

* **master branch:** [![Build Status: "master" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=master)](https://travis-ci.org/OfflineIMAP/imapfw)
* **next branch:** [![Build Status: "next" branch](https://travis-ci.org/OfflineIMAP/imapfw.svg?branch=next)](https://travis-ci.org/OfflineIMAP/imapfw)

## Description

imapfw is a simple and powerfull framework to work with IMAP and Maildir. It
comes as a replacement to the [OfflineIMAP syncer][offlineimap].

The main downside about IMAP is that you have to **trust** your email provider to
not lose your mails. This is not something impossible while not very common.
With imapfw, you can download your Mailboxes and make you own backups of
the [Maildir](https://en.wikipedia.org/wiki/Maildir).

This allows reading your email while offline without the need for the mail
reader (MUA) to support IMAP disconnected operations. Need an attachment from a
message without internet connection? It's fine, the message is still there.


## License

The MIT License (MIT).


## Feedbacks and contributions

**The user discussions, development, announcements and all the exciting stuff
take place on the OfflineIMAP's mailing list.** While not mandatory to send
emails, you can [subscribe
here](http://lists.alioth.debian.org/mailman/listinfo/offlineimap-project).

Bugs, issues and contributions can be requested to both the mailing list or the
[official Github project][imapfw].



## Requirements

* Python v3.3

