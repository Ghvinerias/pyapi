import os
from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB connection details

MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = int(os.environ.get('MONGO_PORT'))
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_USER = os.environ.get('MONGO_USER')
MONGO_PASS = os.environ.get('MONGO_PASS')


client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/")
db = client[MONGO_DB]

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
    data = request.json
    template_name = data.get('template_name')
    strings = data.get('strings')
    collection_name = data.get('collection_name')
    config_name = data.get('config_name')

    try:
        template = db.templates.find_one({'file_name': template_name})
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        template_content = template['data'].decode('utf-8')  # Decode the binary data

        # Replace strings in the template content
        for old_string, new_string in strings:
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
    template_name = request.json.get('template_name')

    try:
        template = db.templates.find_one({'file_name': template_name})
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        template_content = template['data'].decode('utf-8')  # Decode the binary data
        return jsonify({'template_content': template_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get config
@app.route('/get_config', methods=['POST'])
def get_config():
    data = request.json
    config_name = data.get('config_name')
    collection_name = data.get('collection_name')

    try:
        config = db[collection_name].find_one({'name': config_name})
        if not config:
            return jsonify({'error': 'Config not found'}), 404

        config_content = config['content']

        # Create and send the file as a download attachment
        response = make_response(config_content)
        response.headers['Content-Disposition'] = f'attachment; filename={config_name}.txt'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
