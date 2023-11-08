#NEW DB Configuration
curl -X POST http://localhost:5000/configure_new_db

# Upload Template
curl -X POST -F "file=@Nginx_template_SSL_Only.config" -F "file_name=Nginx_template_SSL_Only.config" http://localhost:5000/upload_file

# Get desired config content
curl -X POST -H "Content-Type: application/json" -d '{"config_name": "Example.API", "collection_name": "nginx"}' http://localhost:5000/get_config --output Example.API.conf

#generate config based on specific template
curl -X POST -H "Content-Type: application/json" -d '{"template_name": "Nginx_template_SSL_Only.config", "strings": [["application_dns", "Example.Test.API.slick.ge"], ["application_port", "7009"], ["application_name", "Example.API"], ["application_ssl_cer", "*.api.slick.ge.cer"], ["application_ssl_key", "01-06.API.lb.ge2024.key"]], "collection_name": "nginx", "config_name": "Example.API"}' http://localhost:5000/generate_config

#Get desired template content
curl -X POST -H "Content-Type: application/json" -d '{"template_name": "Nginx_template_SSL_Only.config"}' http://localhost:5000/show_template

#List Templates
curl http://localhost:5000/list_templates

#Test Connection
curl http://localhost:5000/test

