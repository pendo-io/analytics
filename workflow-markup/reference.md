# Tutorials

This is half tutorial and half desk reference for the various commandline tools necessary for the workflow. I spend a considerable amount of time copy and pasting from this file.

If you haven't gone through workflow.md and gettingstarted.md then reading this is a waste of time.

### Creating New Python virtual environments on Mac os

You should always use a virtual environment for your Python projects. It’s a best practice to keep all your virtualenvs in one place, for example .virtualenvs/ in your home directory. Let’s create that directory:

$ `mkdir ~/.virtualenvs`

Now create a new virtual environment called myvenv by running:
$ `python3 -m venv ~/.virtualenvs/myvenv`

To activate this virtual environment, so we can use it, we must also run the following command:
$ `source ~/.virtualenvs/myvenv/bin/activate`


Note that while the environment is active, you will see its name in parentheses. Software packages we install now will only be available within this virtual environment. You can use the command `pip freeze` to see all installed software within a virtual environment.

To stop using a virtual environment, either close the Terminal window or enter deactivate:
(myvenv) $ `deactivate`

### Use the virtual environment as the interpreter for a Pycharm project
When you open a project in pycharm, it will default the project interpreter to your global python installation. You'll want to switch this to the virtual environment. For Mac OS after opening a pycharm project, navigate to the ribbon pycharm >> preferences.

- In the search bar on top left type 'project interpreter'.
- Choose project interpreter on the left hand side.
- On the next page, find the gear in the top right corner, click it, and choose add.
- Choose the radio button for existing environment
- Choose the path to the python installation from the venv you created above.
- usually the path looks like: `venvdirectory/venvname/bin/python`
- Click apply/okay at the bottom.
- It should take ~2-5 minutes for the interpreter to update.

Now you can have 20 projects in pycharm all interpreted via different python installations.

### Creating a docker image.

I highly recommend going through the tutorial on the docker website or talking to someone on the team familiar with it. You can find the tutorial here: [Docker tutorial](https://docs.docker.com/get-started/). I only made it past the second lesson with containers. That's all you need to get started. Otherwise below is a cheatsheet.

#### Docker Cheatsheet:

these commands all run in terminal. Docker doesn't have a UI.

- Docker Commands - `docker container --help`
- List all local docker images - `docker image ls`
- Execute Image - `docker run imagename`
- List all active docker containers - `docker container ls`
- List all active and stopped containers - `docker container ls --all`

#### Building Images

cd to the root directory of the project where dockerfile and requirements.txt are located.
- building an image - `docker build --tag=$imagename:version .`
The period at the end is important.
to push to google cloud repository correctly images must be tagged as follows
- building an image for gcr - `docker build --tag=gcr.io/pendo-reporting/imagename:version .`
I usually just use 'latest' as the version. This is a big no no online, but idc.

#### Pushing to GCR
 `docker push gcr.io/pendo-reporting/imagename:version`


#### see stopped container and removing images:

- remove all stopped containers (memory wasters) - `docker rm ${docker ps -a -q}`
- remove all images with no tag (dangling)(memory wasters) - `docker system prune`

### Authorize gcloud and Docker

You should have logged into the google cloud sdk in a previous step, and downloaded docker. To make sure your docker installation works, starting with a fresh terminal, type `docker image ls`. you shouldn't get an error. Just a blank table. If this looks good then youll be able to run the command -

`gcloud auth configure-docker`

It will say its going to update a file. choose y and then press return. Now gcloud and docker will be linked this will allow you to push and pull docker images to and from google cloud registry.

### Creating a DAG for Airflow on google cloud composer
DAG's are created as a python script. Each dag file has a standard format. Imports, setting defaults args. Define the dag name, schedule etc. a list of operators (tasks) and finally dependancies and execution order. it is generally a single file per dag. These dags are tested in a test environment before being moved to production. Generally speaking, most python tasks will be run via a KubernetesPodOperator (airflow builtin module). These tasks simply execute a python script in a docker container where the image is stored on GCR.

Here is a link to a simple dag that we use at pendo:

There are further tutorials on the airflow website and the google cloud pages.
- [Airflow Docs](https://airflow.apache.org/)
- [Google Cloud composer Quickstart](https://cloud.google.com/composer/docs/quickstart)


### Testing Dags for airflow on google cloud Composer.
I can't do better than the google page for testing so I'll just copy and paste it below.

You can run a single task instance locally and view the log output. Viewing the output enables you to check for syntax and task errors. Testing locally does not check dependencies or communicate status to the database. We recommend that you put the DAGs in a data/test folder in your test environment.

Our test environment is called test-environment and can be found here: [Google Cloud Composer](https://console.cloud.google.com/composer/environments?project=pendo-reporting&folder=&organizationId=)

I have a cheatsheet here, but to find the actual docs: [Testing DAGS](https://cloud.google.com/composer/docs/how-to/using/testing-dags)

#### Check for syntax errors in terminal
gcloud composer environments run ENVIRONMENT_NAME \
 --location LOCATION \
 list_dags -- -sd /home/airflow/gcs/data/test

#### Check for task errors
gcloud composer environments run ENVIRONMENT_NAME \
  --location LOCATION \
  test -- -sd /home/airflow/gcs/data/test DAG_ID \
  TASK_ID DAG_EXECUTION_DATE
