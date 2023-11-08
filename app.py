import os
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_swagger import swagger
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB connection details

MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = int(os.environ.get('MONGO_PORT'))
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_USER = os.environ.get('MONGO_USER')
MONGO_PASS = os.environ.get('MONGO_PASS')

configs_password = os.environ.get('MONGO_PASS')
infra_admin_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')


client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/")
db = client[MONGO_DB]

# Define Swagger UI blueprint
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # URL for your API specification
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Your Application Name"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Generate Swagger specification
@app.route('/api/swagger')
def get_api_spec():
    swag = swagger(app, from_file_keyword='swagger_from_file')
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Your Application API"
    return jsonify(swag)

# Test MongoDB connection
@app.route('/test', methods=['GET'])
def test_mongodb_connection():
    try:
        client.admin.command('ismaster')
        return jsonify({'message': 'Connected to MongoDB'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Upload file to MongoDB
@app.route('/upload_file', methods=['POST'])
def upload_file():
    file_name = request.form['file_name']
    file = request.files['file']
    
    existing_template = db.templates.find_one({'file_name': file_name})
    if existing_template:
        return jsonify({'error': 'A template with the same name already exists'}), 400

    if file:
        file_content = file.read().decode('utf-8')  # Read the file content as a string
        db.templates.insert_one({'file_name': file_name, 'content': file_content})
        return jsonify({'message': 'File uploaded successfully'})
    else:
        return jsonify({'error': 'No file uploaded'}), 400

# Generate config
@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        strings = data.get('strings')
        collection_name = data.get('collection_name')
        config_name = data.get('config_name')

        template = db.templates.find_one({'file_name': template_name})
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        template_content = template['content']

        # Replace strings in the template content
        for pair in strings:
            old_string, new_string = pair
            template_content = template_content.replace(old_string, new_string)

        # Save the modified template in the specified collection with the provided config name
        db[collection_name].insert_one({'name': config_name, 'content': template_content})

        return jsonify({'message': 'Config generated and saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List configs
@app.route('/list_configs', methods=['POST'])
def list_configs():
    data = request.json
    collection_name = data.get('collection_name')

    try:
        configs = [config['name'] for config in db[collection_name].find({}, {'name': 1})]
        return jsonify({'configs': configs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List templates
@app.route('/list_templates', methods=['GET'])
def list_templates():
    try:
        templates = [template['file_name'] for template in db.templates.find({}, {'_id': 0, 'file_name': 1})]
        return jsonify({'templates': templates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Show template
@app.route('/show_template', methods=['POST'])
def show_template():
    try:
        data = request.get_json()
        template_name = data.get('template_name')

        template = db.templates.find_one({'file_name': template_name})
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        template_content = template['content']
        return jsonify({'content': template_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get config
@app.route('/get_config', methods=['POST'])
def get_config():
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        collection_name = data.get('collection_name')

        config = db[collection_name].find_one({'name': config_name})
        if not config:
            return jsonify({'error': 'Config not found'}), 404

        config_content = config['content']

        response = make_response(config_content)
        response.headers['Content-Disposition'] = f'attachment; filename={config_name}.txt'
        response.headers['Content-Type'] = 'text/plain'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Configure New DB    
@app.route('/configure_new_db', methods=['POST'])
def run_configure_new_db():
    try:        # Check if collections exist, create if not
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

        return jsonify({'message': 'Database configuration completed successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
