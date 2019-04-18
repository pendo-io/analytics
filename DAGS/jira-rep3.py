import datetime

from airflow import models
from airflow.operators import dummy_operator
from airflow.contrib.operators import kubernetes_pod_operator

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

default_dag_args = {
    # Setting start date as yesterday starts the DAG immediately
    'start_date': YESTERDAY,
    # To email on failure or retry set 'email' arg to your email and enable
    'email_on_failure': False,
    'email_on_retry': False,
    # If a task fails, retry it once after waiting at least 5 minutes
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'project_id': models.Variable.get('gcp_project')
}


# If a Pod fails to launch, or has an error occur in the container, Airflow
# will show the task as failed.
with models.DAG(
        dag_id='jira-rep',
        schedule_interval='0 11 * * *',
		default_args=default_dag_args) as dag:
    # Only name, namespace, image, and task_id are required to create a
    # KubernetesPodOperator.
	jira_pull_issues = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='jira-pull-issues',
        # Name of task you want to run, used to generate Pod ID.
        name='jira-pull-issues',
		image_pull_policy='Always',
		cmds = ["python","JiraIssues.py"],
        # The namespace to run within Kubernetes
        namespace='default',
        # Docker image specified.
        image='gcr.io/pendo-reporting/jira-pull-issues:latest')


	jira_pull_changelog = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='jira-pull-changelog',
        # Name of task you want to run, used to generate Pod ID.
        name='jira-pull-changelog',
		image_pull_policy='Always',
		cmds = ["python","JiraChangelog.py"],
        # The namespace to run within Kubernetes
        namespace='default',
        # Docker image specified.
        image='gcr.io/pendo-reporting/jira-pull-issues:latest')


	Dummy = dummy_operator.DummyOperator(task_id='Dummy')

	pr_jira_employeefirstresolution = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='jira-employee-first-resolution',
        # Name of task you want to run, used to generate Pod ID.
        name='jira-employee-first-resolution',
		image_pull_policy='Always',
		cmds = ["python","pr_jira_EmployeeFirstResolution.py"],
        # The namespace to run within Kubernetes
        namespace='default',
        # Docker image specified.
        image='gcr.io/pendo-reporting/jira-pull-issues:latest')


	pr_jira_timeperstatus = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='jira-time-per-status',
        # Name of task you want to run, used to generate Pod ID.
        name='jira-time-per-status',
		image_pull_policy='Always',
		cmds = ["python","pr_jira_TimePerStatus.py"],
        # The namespace to run within Kubernetes
        namespace='default',
        # Docker image specified.
        image='gcr.io/pendo-reporting/jira-pull-issues:latest')




jira_pull_issues >> Dummy
jira_pull_changelog >> Dummy
Dummy >> pr_jira_employeefirstresolution
Dummy >> pr_jira_timeperstatus
