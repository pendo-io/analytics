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
TargetTable = 'Users'
TempDataset = 'temp'
TempTable = TargetTable + '_' +  uuid4().hex
client = bigquery.Client()
schema = [
    {'name': 'Active', 'type': 'Boolean'},
    {'name': 'Alias', 'type': 'String'},
    {'name': 'ChatOnly', 'type': 'Boolean'},
    {'name': 'CreatedAt', 'type': 'Timestamp'},
    {'name': 'CustomRoleId', 'type': 'int64'},
    {'name': 'DefaultGroupId', 'type': 'Int64'},
    {'name': 'Details', 'type': 'String'},
    {'name': 'Email', 'type': 'String'},
    {'name': 'ExternalId', 'type': 'String'},
    {'name': 'IanaTimeZone', 'type': 'String'},
    {'name': 'Id', 'type': 'Int64'},
    {'name': 'LastLoginAt', 'type': 'Timestamp'},
    {'name': 'Locale', 'type': 'String'},
    {'name': 'LocaleId', 'type': 'Int64'},
    {'name': 'Moderator', 'type': 'Boolean'},
    {'name': 'Name', 'type': 'String'},
    {'name': 'Notes', 'type': 'String'},
    {'name': 'OnlyPrivateComments', 'type': 'Boolean'},
    {'name': 'OrganizationId', 'type': 'int64'},
    {'name': 'ReportCsv', 'type': 'Boolean'},
    {'name': 'RestrictedAgent', 'type': 'Boolean'},
    {'name': 'Role', 'type': 'String'},
    {'name': 'RoleType', 'type': 'Int64'},
    {'name': 'Shared', 'type': 'Boolean'},
    {'name': 'SharedAgent', 'type': 'Boolean'},
    {'name': 'Suspended', 'type': 'String'},
    {'name': 'Tags', 'type': 'String'},
    {'name': 'TicketRestriction', 'type': 'String'},
    {'name': 'TimeZone', 'type': 'String'},
    {'name': 'TwoFactorAuthEnabled', 'type': 'String'},
    {'name': 'UpdatedAt', 'type': 'Timestamp'},
    {'name': 'Verified', 'type': 'Boolean'},
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
select max(UNIX_SECONDS(updatedat)) as StartTime
from zendesk.Users
"""
             )
startTime = client.query(startTime, location="US")
startTime = startTime.result()
startTime = list(startTime)

startTime = startTime[0][0]
count = 1000
dataList = []
x = 0
while count == 1000:
    users = zenpy.users.incremental(start_time=startTime)
    dataList = dataList + users._response_json['users']
    start_time = users.end_time
    count = users.count
    x = x+1
    print('Data Has been retrieved {} times'.format(x))

df = json_normalize(dataList)


# Obscure end user Name and Email
df.loc[(df['role'] == 'end-user') & (df['email'].notnull()), 'email'] = df.loc[
    (df['role'] == 'end-user') & (df['email'].notnull()), 'email'].map(lambda x: encrypt(x, login['ckey']))
df.loc[(df['role'] == 'end-user') & (df['name'].notnull()), 'name'] = df.loc[
    (df['role'] == 'end-user') & (df['name'].notnull()), 'name'].map(lambda x: encrypt(x, login['ckey']))

# Get the list of columns
columns = list(df.columns)

# Rename the Columns
df = df.rename(columns=lambda x: toRename(x, columns))


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
                          select *, row_number() over(partition by id,updatedat) as RowNum
                          from zendesk.Users 
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