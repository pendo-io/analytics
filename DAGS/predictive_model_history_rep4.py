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
dag = models.DAG(dag_id='predictive-model-history-rep', schedule_interval='0 12 * * *', default_args=default_dag_args)
    # Only name, namespace, image, and task_id are required to create a
    # KubernetesPodOperator. 
refresh_models = kubernetes_pod_operator.KubernetesPodOperator(
	# The ID specified for the task.
	task_id='refresh-all-models',
	# Name of task you want to run, used to generate Pod ID.
	name='refresh-all-models',
	image_pull_policy='Always',
	cmds = ["python","RefreshAllModels.py"],
	# The namespace to run within Kubernetes
	namespace='default',
	# Docker image specified.
	image='gcr.io/pendo-reporting/modelhistory:latest',
	dag=dag)
	
	
refresh_history_healthscore = kubernetes_pod_operator.KubernetesPodOperator(
	# The ID specified for the task.
	task_id='history-healthscore',
	# Name of task you want to run, used to generate Pod ID.
	name='history-healthscore',
	image_pull_policy='Always',
	cmds = ["python","historyhealthscore.py"],
	# The namespace to run within Kubernetes
	namespace='default',
	# Docker image specified.
	image='gcr.io/pendo-reporting/modelhistory:latest',
	dag=dag)	
		
	

		

refresh_models >> refresh_history_healthscore
	
	
	
	