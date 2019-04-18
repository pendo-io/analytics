# Getting Started.

If you are here I hope you read workflow.md. If you haven't, go there first. This doc is really in the
weeds and if you don't have the context for why you are doing this, it's not going to make any real sense.


### Step one Bookmarks:

Just go ahead and bookmark these pages. You'll be there everyday. At this point, just bookmark them,
don't worry about looking around too much just yet. You can do that after the tutorial. The google specific
bookmarks below are all part of the pendo-reporting project on GCE.

1. [BigQuery](https://bigquery.cloud.google.com/queries/pendo-reporting?pli=1)
2. [Cloud Storage](https://console.cloud.google.com/storage/browser?project=pendo-reporting)
3. [Google Cloud Registry](https://console.cloud.google.com/gcr/images/pendo-reporting?project=pendo-reporting&folder&organizationId=916152866672)
4. [Google Cloud Composer](https://console.cloud.google.com/composer/environments?project=pendo-reporting&folder=&organizationId=)

### Step two Google Cloud SDK

To work effectively with Google Cloud in python you're going to need their command-line tools. Go to the link
below and follow the instructions for setup. make sure you are able to login etc.

- [Google Cloud SDK](https://cloud.google.com/sdk/)

### Step three Github

Download it. If you need a quick tutorial, Grab one of us.
- [Github Download](https://desktop.github.com/)

### Step four python Setup

If you are on Mac OS you have python 2 installed. If you are on windows, likely you don't have anything. You need to
set up python in a way that works with virtual environments, and is simple to update etc. On Mac I recommend, homebrew
on PC I recommend Anaconda. I don't have the links for PC but below is the link to the best tutorial I have seen on installing
homebrew, python3 and creating virtual environments. You know you are good here if you end up logged into a venv on your computer.

- [python3 installation instructions mac](https://wsvincent.com/install-python3-mac/)

### Step five IDE and Text Editor

This is really personal preference. I really like Atom for text editor, and PyCharm for IDE. Some folks prefer
jupyter notebooks. Jupyter is really good if you want to present an analysis, Pycharm is really good if you want to
create a program. Atom is a life saver, For Instance, If you have many dependent sql queries in a project
and need to know where a certain table and column is referenced, you can ctrl+f through all files at once rather than searching
file by file. Here are the links to download.

- [Atom](https://atom.io/)
- [Pycharm Community](https://www.jetbrains.com/pycharm/download/#section=mac)

### Step six Docker

Like I said, dont worry about going through the tutorial just yet. Just download it for now.

- [Docker Get-Started](https://www.docker.com/get-started)


### Conclusion

Now you should have read about the workflow and installed the necessary tools. If you didn't have any crazy errors then you should be good to proceed to the next tutorial called reference.md. It is the last document to get through, and is really just a desk reference for using the various tools etc. It is highly encouraged to do the quick start exercises for google cloud composer and docker. reference.md will not teach you how to use them, but rather provide high level information and useful terminal commands. If you have downloaded docker, I encourage you to schedule a meeting with another analyst to get a tutorial. 
