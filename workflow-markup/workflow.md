## What is This?

1. An explanation of the tool sets and processes of pendo analytics.
2. This page specifically gives the why behind the current configuration.
3. It could take a couple hours to get set-up, therefore I felt like I owed an explanation.
4. This is specifically for folks who are scheduling workflows in Python.


### Background

I am a Python novice. A very large portion of my learning involved running code
on broken python installations. I didn't know at the time that the installation was broken, I
assumed there were syntax errors.

At the same time, we had(ve) been using Xplenty to replicate data from SaaS apps to BigQuery.
It works fine for light weight ETL, but has some flaws. I couldn't find a
good replacement for Xplenty in the SaaS world.

After a bit of research I realized that Python was the answer. The workflow documented here
solves the critical issues uncovered from a year of fumbling on ETL.

### issues

1. SaaS apps for ETL are black boxes. In any given workflow you cant just go into a text editor
and search for everywhere you referenced a certain column in Bigquery.
2. Xplenty, had limited support and no Stack overflow presence
3. No solution for automating analysis. If its not purely etl, it's not happening.
4. Horrible Dependency Graphing.
5. With Python Specifically, I broke my installation pretty much always.
6. Most recent issue is collaboration. We are concerned with our ability to scale.


### Solution

The solutions here are really simple.

1. let Xplenty do what it does well. Very simple replication. AKA, Salesforce rep.
2. For everything else use python on google cloud.
3. You don't have to do everything exactly the way I document below, but it should get you started.


### Python on Google cloud

Pendo is a google shop, so we didn't have any other choices. Luckily it does everything We need it to do.
Here is the process I use to create a project, and then deploy, schedule it on google cloud.

1. Version Control - Create a github repo.
2. Local Development - Create a python virtual environment for that specific project
3. Local Development - Write the code. If it works in python, it will work here.
4. Scale the Project - Create a docker image
5. Version Control for Docker - Upload the docker image to Google Cloud Registry
6. Workflow management - Write a DAG for Apache Airflow using solely KubernetesPodOperator.
7. Workflow management - Deploy the dag to Google Cloud Composer

So far this workflow fixes all the problems from above. It feels like as we scale, we should be able to
adjust this workflow, rather than tear it down and replace it. This workflow is very simple once you have done it once or twice.

#### Create a Github Repo

Because Stephen Perkins Said so.

#### Create a virtual environment per project

If you know why these are so important. Skip otherwise read. It was a problem for me right out of the gate
with python. Xplenty API python SDK, only supports python 2.7. Just about everything else at this point has been
migrated to python 3. I kept installing the Xplenty SDK into my python 3 installation and it kept breaking python 3.
Virtual environments give you the ability to install python into a specific project so that I can run an Xplenty project
in python 2.7 and a google cloud project in python 3, without breaking anything. Its like having 2 separate walled gardens,
where nothing I do in the Xplenty project can affect the google cloud project.

#### Create a Docker Image

We are develop everything locally with the intention of deploying it on the cloud. We can transfer all the code, but we can't transfer the venv. This is where docker comes in. It provides a way to turn a python application into a simple executable image. The image is the blueprint so that when we deploy to another computer. Docker Builds the environment easily with all dependancies needed to run the code. If the image can run locally, then it will run on any machine that can run docker images. Now we can develop on our local machines, and deploy anywhere.


#### Google Cloud Registry

The github of docker images for us. We do not use docker hub. Thats a No No.


#### Airflow

Airflow on Google cloud composer is our way to schedule the executables from the docker images, and manage dependancies between tasks in a simple way. Airflow out of the box is designed to orchestrate all tasks, and run all the tasks. This causes issues because running the tasks only requires airflow but any given project will require different dependancies. Some may need python 2.7 and some might run on python 3. To use Airflow out of the box, we would almost need a different environment per project. This is why we do not use Airflow Python operators. Instead we call a Kubernetes operator to create a pod (virtual machine with linux os.) download our docker image, from google cloud registry, run the commands, and wait for a success message from kubernetes. In this way, we can schedule 20 projects with different dependancies all in airflow, and never have to worry about them breaking each other. More importantly, none of these projects will break airflow itself. In this way, Airflow handles the orchestration, and docker/kubernetes, handles the task execution, in 2 separate non dependent environments.

It all sounds so complicated, but to do all this work, its only 3 lines of code.

#### Conclusion
This is a lot of writing, and I don't mean to bore you, I just want to make sure that anyone looking at the setup for the first time understands why it is the way it is. That way if you want to innovate, and add to the process, you can do so with some core tenants in mind. Also, learning it without a guidepost was daunting. I want to get you up an running in less than a day.

Check out the gettingstarted.md page to get started with all the tools that you will need to have installed.




-Chad
