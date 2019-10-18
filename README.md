# ChangeBot
A changelog bot written in Python. Creates a changelog of events in an SVN server for one day and posts it to Discord (via webhooks), PasteBin, and Twitter. I used TortoiseSVN, so I can't verify if this will work for other SVN repositories.

Requires the following Python3 extensions:

* python-discord-webhook: https://pypi.org/project/discord-webhook/

* PySVN: https://pypi.org/project/svn/

* Tweepy: https://www.tweepy.org/

* pbwrap: https://pypi.org/project/pbwrap/
