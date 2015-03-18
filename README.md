## Introduction

Mosaicme is a [Microservice](http://en.wikipedia.org/wiki/Microservices "Microservices") application that retrieves images from selected Twitter feeds, stores them on an [object store](http://en.wikipedia.org/wiki/Object_storage "Object Store"), and then it process them to build a mosaic based on a selected set of pictures. 

Mosaicme's goal is to provide developers with an example of how to build a distributed microservice application using Linux containers. It focuses on current best practices, showcases the use of Object stores,  the use of multiple [APIs](http://en.wikipedia.org/wiki/Application_programming_interface "APIs") ([REST](http://en.wikipedia.org/wiki/Representational_state_transfer "REST"), [S3](http://en.wikipedia.org/wiki/Amazon_S3 "AWS S3"), [SWIFT](http://en.wikipedia.org/wiki/OpenStack#Swift "OpenStack Swift"), [HDFS](http://en.wikipedia.org/wiki/Apache_Hadoop#HDFS "Haddop Distributed File System")), and automated deployment models.


[Architecture Diagram goes here]



## Use Cases


The following section provides an overview of the Use Cases for Mosaicme. There are two main actors for this application  only one actor for this application, the end-user:

 
Use Case	                          | Description
------------------------------------- | -----------|
Retrieve Images from Twitter Accounts | Mosaicme retrieves images from the selected list of Twitter accounts and stores them in the Object store.
Process Mosaic from selected Pictures | It will build a mosaic from a picture using the stored pictures. The resulting mosaic is then stored in the Object store.
Mosaic "My" Picture					  | Mosaic me will build a mosaic based on the picture provided by the user.
Display list Pictures				  | Shows the list of pictures currently stored in the system
Configure Mosaicme 					  | Enables administrator to configure the system






## Architecture 

Mosaicme is composed of multiple tiers. The following design shows the high level application architecture: 

[Architecture Model image]

The following has an overview of each one of the components

Component Name |	Component Description
-------------- | ---------------------|
Component 1    | Description. 
Component 2    | Description.
Component 3    | Description.
 


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

