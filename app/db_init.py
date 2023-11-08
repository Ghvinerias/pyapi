import os
import pymongo

# MongoDB connection details
host = os.environ.get('MONGO_HOST')
port = int(os.environ.get('MONGO_PORT'))
username = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')

# Passwords for users
configs_password = 'somecomplexsalt'
infra_admin_password = 'somemorecomplexsalt'

# Establishing a connection
client = pymongo.MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
db = client['infra']

# Check if collections exist, create if not
collections_to_create = ['templates', 'nginx', 'appsettings']
existing_collections = db.list_collection_names()
for collection_name in collections_to_create:
    if collection_name not in existing_collections:
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created.")
    else:
        print(f"Collection '{collection_name}' already exists.")

# Check if users exist, create if not
users_to_create = [
    {"name": "configs", "pwd": configs_password, "roles": [{"role": "readWrite", "db": "infra"}]},
    {"name": "infra_admin", "pwd": infra_admin_password, "roles": [{"role": "dbOwner", "db": "infra"}]}
]

existing_users = db.command('usersInfo')
existing_usernames = [user['user'] for user in existing_users['users']]

for user_data in users_to_create:
    if user_data['name'] not in existing_usernames:
        db.command("createUser", user_data['name'], pwd=user_data['pwd'], roles=user_data['roles'])
        print(f"User '{user_data['name']}' created.")
    else:
        print(f"User '{user_data['name']}' already exists.")

# Closing the connection
client.close()
