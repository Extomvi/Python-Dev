# Python-Dev
Building a Python Application

## Software Used
* Python: 3.8.3
* OS: ubuntu/bionic64
* Daemon: Supervisord
* Local Environment: Vagrant + VirtualBox
* Production Environment: Google Cloud - Compute Engine
* Code Editor: Visual Studio Code
* Data Persistence: Cloud Firestore
* Blob storage: Cloud Storage

# Running the Web Server
data_storage="firestore" blob_storage="cloudstorage" blob_storage_bucket="advanced_python_cloud_academy" GOOGLE_APPLICATION_CREDENTIALS="/vagrant/service_account.json" gunicorn -b "0.0.0.0:8080" -w 1 "web.main:create_app()" --timeout=60

curl -XPOST http://127.0.0.1:8080/images -H "Authorization:8h45ty"
