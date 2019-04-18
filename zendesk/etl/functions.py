
def fetchLogin(bucket, yaml):
    from google.cloud import storage
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.get_blob(yaml)
    login = blob.download_as_string()
    login = eval(login)
    return (login)



def encrypt(message, key):
    from cryptography.fernet import Fernet
    key = key.encode()
    message = message.encode()
    return str(Fernet(key).encrypt(message),'utf-8')

def decrypt(token,key):
    from cryptography.fernet import Fernet
    key = key.encode()
    token = token.encode()
    return str(Fernet(key).decrypt(token),'utf-8')



def toRename(toRename,CustList):
    import re
    #lowercase the entire column for matching purposes
    toRename = toRename.lower()
    #create a list of words based on the . notation
    toRename = toRename.split('.')
    #remove 'fields' if it is the first word in the column
    toRename = [i.capitalize() for i in toRename]
    toRename = [re.sub('[^0-9a-zA-Z]+', '', i.title()) for i in toRename]
    toRename = ''.join(toRename)
    return(toRename)


def createBQTableIfNotExist(tableName,datasetName,SchemaDict):
    from google.cloud.exceptions import NotFound
    from google.cloud import bigquery
    try:
        client = bigquery.Client()
        dataset = client.dataset(datasetName)
        table_ref = dataset.table(tableName)
        client.get_table(table_ref)
        print('Table Already Exists')
    except NotFound:
        client = bigquery.Client()
        Schema = []
        for i in SchemaDict:
            Schema.append(bigquery.SchemaField(i['name'], i['type']))
        dataset_ref = client.dataset(datasetName)
        table_ref = dataset_ref.table(tableName)
        table = bigquery.Table(table_ref, schema=Schema)
        table = client.create_table(table)
        print('Table Created')