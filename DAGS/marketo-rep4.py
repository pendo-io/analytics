import datetime

from airflow import models
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators import kubernetes_pod_operator

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=2)

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
dag = models.DAG(dag_id='marketo-replication', schedule_interval='0 11 * * *', default_args=default_dag_args)
# Only name, namespace, image, and task_id are required to create a
# KubernetesPodOperator.
reload_activity_types = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='activity-types-reload',
    # Name of task you want to run, used to generate Pod ID.
    name='activity-types-reload',
    image_pull_policy='Always',
    cmds=["python", "ActivityTypes.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

reload_form_fields = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='form-fields-reload',
    # Name of task you want to run, used to generate Pod ID.
    name='form-fields-reload',
    image_pull_policy='Always',
    cmds=["python", "formfields.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

forms_reload = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='forms-reload',
    # Name of task you want to run, used to generate Pod ID.
    name='forms-reload',
    image_pull_policy='Always',
    cmds=["python", "forms.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

lead_schema_reload = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='lead-schema-reload',
    # Name of task you want to run, used to generate Pod ID.
    name='lead-schema-reload',
    image_pull_policy='Always',
    cmds=["python", "LeadSchema.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

leads_refresh = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='leads-refresh',
    # Name of task you want to run, used to generate Pod ID.
    name='leads-refresh',
    image_pull_policy='Always',
    cmds=["python", "marketoLeads.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

form_fill_outs_refresh = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='form-fill-outs-refresh',
    # Name of task you want to run, used to generate Pod ID.
    name='form-fill-outs-refresh',
    image_pull_policy='Always',
    cmds=["python", "formfillouts.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

dummy = DummyOperator(task_id='Dummy', dag=dag)

flat_form_fills = kubernetes_pod_operator.KubernetesPodOperator(
    # The ID specified for the task.
    task_id='flat-form-fills',
    # Name of task you want to run, used to generate Pod ID.
    name='flat-form-fills',
    image_pull_policy='Always',
    env_vars= {'QueryPath': 'Queries/FlatFormFillouts.sql'},
    cmds=["python", "RunQuery.py"],
    # The namespace to run within Kubernetes
    namespace='default',
    # Docker image specified.
    image='gcr.io/pendo-reporting/marketo-replication:latest',
    dag=dag)

reload_activity_types >> dummy
reload_form_fields >> dummy
forms_reload >> dummy
lead_schema_reload >> dummy
leads_refresh >> dummy
form_fill_outs_refresh >> flat_form_fills
flat_form_fills >> dummy