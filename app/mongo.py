from pymongo import MongoClient

class MongoAPI:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self, host, port, db, user, password):
        self.client = MongoClient(host, port, username=user, password=password)
        self.db = self.client[db]

    def test_connection(self):
        if self.client is not None:
            try:
                # Check if the connection is active by accessing a collection
                self.client.server_info()
                return {'message': 'Connection successful'}
            except Exception as e:
                return {'message': f'Connection failed: {e}'}
        return {'message': 'Not connected to MongoDB'}

    def upload_file(self, file_name, file_path):
        # Add implementation to upload file to MongoDB
        from bson.binary import Binary

        if self.db is None:
            return {'message': 'Not connected to MongoDB'}
        
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                self.db['templates'].insert_one({'file_name': file_name, 'data': Binary(file_content)})
            return {'message': 'File uploaded successfully'}
        except Exception as e:
            return {'message': f'Error uploading file: {e}'}

    def generate_config(self, data):
        # Add implementation to generate config
            if self.db[collection]:
                return list(self.db[collection].find({}))
            return []

    def list_configs(self):
        if self.db is None:
            return {'message': 'Not connected to MongoDB'}

        collection = self.db['configs']  # Replace 'configs' with your actual collection name
        configs = list(collection.find({}, {'_id': 0}))

        return {'configs': configs}

    def list_templates(self):
        if self.db is None:
            return {'message': 'Not connected to MongoDB'}

        collection = self.db['templates']  # Replace 'configs' with your actual collection name
        templates = list(collection.find({}, {'_id': 0}))

        return {'templates': templates}

    def show_template(self, template_name):
        # Add implementation to show template
        pass

    def get_config(self, config_name):
        # Add implementation to get config
        pass
