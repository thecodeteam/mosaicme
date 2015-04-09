## Introduction

Mosaicme is a [Microservice](http://en.wikipedia.org/wiki/Microservices "Microservices") application that retrieves images from selected Twitter feeds, stores them on an [object store](http://en.wikipedia.org/wiki/Object_storage "Object Store"), and then it process them to build a mosaic based on a selected set of pictures. 

Mosaicme's goal is to provide developers with working example in how to build a distributed microservice application using best practices. The application includes the following 

- Use of Linux containers to host each service.
- Use of Object stores.
- Restful APIs as communication Channel ([REST](http://en.wikipedia.org/wiki/Representational_state_transfer "REST"), [S3](http://en.wikipedia.org/wiki/Amazon_S3 "AWS S3"), [SWIFT](http://en.wikipedia.org/wiki/OpenStack#Swift "OpenStack Swift"), [HDFS](http://en.wikipedia.org/wiki/Apache_Hadoop#HDFS "Haddop Distributed File System"))
- Use of External Services like Twitter and [Twilio](https://www.twilio.com/ "Twilio.com"))
- Automated deployment model
- Use of a Logging Router
- Use of Queuing, Caching and Configuration Services 
- Use of Haddop to calculate statistics
- Use of Puppet/Chef to deploy the application 


## Use Cases


The following section provides an overview of the Use Cases for Mosaicme. There are two main actors for this application  only one actor for this application, the end-user:

### Minimum viable Product (MVP)
 
Use Case	                          | Description
------------------------------------- | -----------|
Retrieve images from Twitter accounts | Mosaicme retrieves images from the selected list of Twitter accounts and stores them in the Object store. Use the EMC Code and EMCWorld twitter accounts. Use the #MosaicMe hashtag to trigger the picture retrieval.
Process a mosaic from the submitted picture | System will build a mosaic from the submitted picture  using the stored pictures in the system. The resulting mosaic is then stored in the Object store and made available to the Web application via a URI.
Post Mosaic to Twitter Account		  | Mosaicme will post a mosaic to a selected Twitter account(s) on a regular interval. This can be configured via the Configuration Section. The MosaicME Twitter Account  will Twitt to the EMCWorld and EMCCode Twitter Accounts.
Display list Pictures				  | Shows the list of pictures currently stored in the system. The Data will available via the Web UI, API and ECS.
Display list Mosaics				  | Shows the list of mosaics currently stored in the system. The data will be available via the Web UI, API and ECS.
Mosaic API open for Developers | Developers can use the Mosaic API endpoints to access the list of pictures and Mosaics.


### Stretch Goals


Use Case	                          | Description
------------------------------------- | -----------|
Booth Webcam						  | Webcam in the booth that allow people to take a picture and submit pictures to Twitter and then it follows the normal process for the mosaic creation and posting.
SMS "My" Mosaic						  | Using Twilio Services, the System will SMS you the selected Mosaic. This can be done via the Web Interface or by the user send it an SMS with the picture ID.
Configure Mosaicme 					  | Enables administrator to configure the system via a web interface.
Mosaicme statistics                   | Generates a list of statistics based on usage, storage, and images. meta data. Will use a Haddop cluster to process stats.			


## Architecture 

Mosaicme is composed of multiple tiers. The following design shows the high level application architecture: 
The following diagram shows Mosaicme high level architecture: 

![Mosaicme high level architecture diagram](https://github.com/emccode/mosaicme/blob/master/documentation/images/mosaicme-high-level-architecture.PNG)

The following has an overview of each one of the components:


### Minimum viable Product (MVP) Services

Component Name              |	Component Description
--------------------------- | ---------------------|
Web Interface               | Web Interface to for displaying pictures, mosaics, statistics and system configuration. 
Mosaic processing service   | Mosaic processing service. Takes the mosaic generation request from the Orchestration API and generates the mosaic data and meta data.
Queuing Service				| Service to host the queues required by the system.
Twitter retrieval service   | Service that retrieves pictures and their meta data from the selected twitter accounts and adds them Object store.


### Stretch Goals Services

Component Name              |	Component Description
--------------------------- | ---------------------|
Statistics Service			| Haddop Cluster that takes the data in the Object Store and processes the statistics. Stores the data back to the Object store using HDFS.
Caching Service             | Data caching service to speed the application.
Log Routing Service		    | Service to route all services logs to the Object Store.
Orchestration API service   | API service that orchestrates interactions with all services in the application. 
Configuration Service       | Service to maintain configuration, synchronization and naming registry.


### Component 1 

Introduction 

**[Image of Component 1]**

Description



### Component 2 

Introduction 

**[Image of Component 2]**

Description
   

### Component 3 

Introduction 

**[Image of Component 3]**

Description
   



## References

[1] Reference 1
 
[2] Reference 2 

[3] Reference 3

