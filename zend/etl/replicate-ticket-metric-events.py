from zenpy import Zenpy
from pandas import DataFrame
from functions import fetchLogin, encrypt, createBQTableIfNotExist, toRename
from pandas.io.json import json_normalize
import cryptography
from uuid import uuid4
from google.cloud import bigquery

# Need to Define all the bigquery Places
TargetProject = 'pendo-reporting'
TargetDataset = 'zendesk'
TargetTable = 'TicketMetricEvents'
TempDataset = 'temp'
TempTable = TargetTable + '_' +  uuid4().hex
client = bigquery.Client()
schema = [
    {'name': 'Deleted', 'type': 'String'},
    {'name': 'Id', 'type': 'Int64'},
    {'name': 'InstanceId', 'type': 'Int64'},
    {'name': 'Metric', 'type': 'String'},
    {'name': 'SlaBusinessHours', 'type': 'String'},
    {'name': 'SlaPolicyDescription', 'type': 'String'},
    {'name': 'SlaPolicyId', 'type': 'Int64'},
    {'name': 'SlaPolicyTitle', 'type': 'String'},
    {'name': 'SlaTarget', 'type': 'Int64'},
    {'name': 'StatusBusiness', 'type': 'int64'},
    {'name': 'StatusCalendar', 'type': 'Int64'},
    {'name': 'TicketId', 'type': 'Int64'},
    {'name': 'Time', 'type': 'TimeStamp'},
    {'name': 'Type', 'type': 'String'}
]

SchemaColumns = []
for i in schema:
    SchemaColumns.append(i['name'])

selectList = ",".join(SchemaColumns)


createBQTableIfNotExist(TargetTable,TargetDataset,schema)


# Get api creds from secret place
login = fetchLogin('non-descript-information', 'zendesk.yml')

# Create the Creds for login
creds = {
    'email': 'rick@pendo.io',
    'token': login['token'],
    'subdomain': login['companyid']
}

# Create a Client
zenpy = Zenpy(**creds)

# Get the StartTime

startTime = ("""
select coalesce(max(UNIX_SECONDS(Time)),0) as StartTime
from zendesk.TicketMetricEvents
"""
             )
startTime = client.query(startTime, location="US")
startTime = startTime.result()
startTime = list(startTime)

startTime = startTime[0][0]
count = 10000
dataList = []
x = 0
while count == 10000:
    metrics = zenpy.tickets.metrics_incremental(start_time=startTime)
    dataList = dataList + metrics._response_json['ticket_metric_events']
    startTime = metrics.end_time
    count = metrics.count
    x = x+1
    print('Data Has been retrieved {} times and the next startdate is {}'.format(x,startTime))

df = json_normalize(dataList)


# Get the list of columns
columns = list(df.columns)
# Rename the Columns
df = df.rename(columns=lambda x: toRename(x, columns))

# New Column Names
columns = list(df.columns)

for i in SchemaColumns:
    if i not in columns:
        df[i] = ''




#Create a new dataframe of only the selected columns. This will ensure order etc.
dfForUpload = DataFrame()
for i in schema:
    dfForUpload[i['name']] = df[i['name']]




# Upload Data to a temp table
dfForUpload.to_gbq('{}.{}'.format(TempDataset, TempTable), 'pendo-reporting', if_exists='replace', table_schema=schema)
print('Loaded To Temp')


# delete from the target table where the id is in the temp table
DeleteFromStateTable = (
    """
    delete from `{}.{}.{}`
    where id in (select id from `{}.{}.{}`)
    """.format(TargetProject, TargetDataset, TargetTable, TargetProject, TempDataset, TempTable)
    # add Where table dataset and project etc.
)
DeleteState = client.query(DeleteFromStateTable, location="US")
DeleteState.result()

# Insert everything from the temp table into the target table
InsertQuery = (
    """
    Insert into `{}.{}.{}` ({})
    select {}
    from `{}.{}.{}`
    """.format(TargetProject, TargetDataset, TargetTable, selectList, selectList, TargetProject, TempDataset, TempTable)
    # add Where table dataset and project etc.
)
InsertLog = client.query(InsertQuery, location="US")
InsertLog.result()
print('Loaded Records to Targt Table')

# Delete Duplicates. Zendesk Sends Duplicates on Purpose for Whatever Reason. ZendeskSpecific
DeleteDups = ("""
                Create or Replace Table zendesk.Users as (
                    select * except(RowNum)
                    from 
                        (
                          select *, row_number() over(partition by id,Time) as RowNum
                          from zendesk.TicketMetricEvents
                        )x
                    where RowNum = 1
                )
                """)
DeleteDups = client.query(DeleteDups, location="US")
DeleteDups.result()
print('Duplicates Deleted')

# Drop the temp table
dataset_id = TempDataset
table_id = TempTable
table_ref = client.dataset(dataset_id).table(table_id)
client.delete_table(table_ref)  # API request
print('Table {}:{} deleted.'.format(dataset_id, table_id))

