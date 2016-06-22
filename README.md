ALKY
==

AWS Login Keys.... YEAH!

Rationale
--

When video editors create assets, currently, they save files to a SAN and tell an asset management tool to associate the new file to some context via custom extensions/plugins in Adobe Prelude and Adobe Premiere Pro. This approach requires the asset manager to have access into the same network as the SAN and to have control over it.

As part of the new video tooling we push assets into S3 for the asset manager to work with. This removes the need for poking holes on firewalls, allows other geographical locations better access to files and moves the transport of files to Amazon’s backbone.

In order to do this, video editors need to be able to push assets from workstations and in the field to the pertinent buckets. Because there are many video editors, because the number of editors change often, and because we don’t want to either bake in credentials to the Adobe plugins nor use long-life keys stored on local machines/ laptops which can be open to misuse, we want to generate short-life keys as/when needed which give access.

Installing Locally
--

```bash
$ virtualenv venv/
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Running Locally
--

The following env vars beed to be set, as per:

```bash
$ export ALKY_USERNAME='me@example.com'
$ export ALKY_PASSWORD='secret'
```

From there the tool can be run as per:

```bash
$ ALKY_MFA_CODE=123456 python src/alky.py
```
