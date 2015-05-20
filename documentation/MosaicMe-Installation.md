# Installation Instructions 

**IN PROGRESS!!**

The MosaicMe application is a demo application to showcase how to build, and deploy a MicroService application. We have followed the best practices shared by the [12 Factor App](http://12factor.net/) manifest and best of breed DevOps tools to showcase how to automate the deployment of the application. 

## Installation components

MosaicMe is composed by multiple services running on Docker Container: 

|Group | Service | Description | Clustered | Container | Logging |
|------|---------|-------------|-----------|-----------|---------|
|MosaicMe|Mosaic Engine|Generates the Mosaics and Tweets the user | No | Yes | Yes|
|MosaicMe|Twitter Collector| Collect Tweets for building the Image library and images to be mosaic|No|Yes|Yes|
|MosaicMe|Website Collector| Website for displaying the mosaics|No|Yes|Yes|
|Queue|Distributed Queue|Queue Service to decouple dependencies and provide sociability (RabbitMQ)|Yes (x3)|Yes|Yes|
|Registry|Registry Service |Source Of truth for the Application (Consul)|Yes (x3)|Yes|Yes|
|Logging|Logging Router|Route logs from all components of the application (FuentD)|Yes (x3)|Yes|Yes|
|Object Store|Object Storage| Application state and data is stored as objects (EMC's ECS)|Yes (x4)|Yes|Yes|



## MosaicMe Containers location

|Group|Service|Container Location|
|-----|-------|--------|
|MosicMe|Twitter Collector|url|
|MosicMe|Mosaic Engine|url|
|MosicMe|Web Server|url|
|Queue|Queue Service|url|
|Registry|Registry Service|url|
|Logging|Logging Router|url|
|Object Store|Object Storage|url|



## Using Puppet / Ansible for Deployment



## MosaicMe Continuous Integration (CI) and Continuous Deployment (CD) Overview





 