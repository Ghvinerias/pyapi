#NEW DB Configuration
curl -X POST http://localhost:5000/configure_new_db

# Upload Template
curl -X POST -F "file=@Nginx_template_SSL_Only.config" -F "file_name=Nginx_template_SSL_Only.config" http://localhost:5000/upload_file

# Get desired config content
curl -X POST -H "Content-Type: application/json" -d '{"config_name": "LCTasks.API", "collection_name": "nginx"}' http://localhost:5000/get_config --output LCTasks.API

#generate config based on specific template
curl -X POST -H "Content-Type: application/json" -d '{"template_name": "Nginx_template_SSL_Only.config", "strings": [["application_dns", "LCTasks.Test.API.lb.ge"], ["application_port", "7009"], ["application_name", "LCTasks.API"], ["application_ss_cer", "01-06.API.lb.ge2024.cer"], ["application_ss_crt", "01-06.API.lb.ge2024.key"]], "collection_name": "nginx", "config_name": "LCTasks.API"}' http://localhost:5000/generate_config

#Get desired template content
curl -X POST -H "Content-Type: application/json" -d '{"template_name": "Nginx_template_SSL_Only.config"}' http://localhost:5000/show_template

#List Templates
curl http://localhost:5000/list_templates

#Test Connection
curl http://localhost:5000/test

