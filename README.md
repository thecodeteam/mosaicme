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


The following section provides an overview of the Use Cases for MosaicMe. There are two main actors for this application  only one actor for this application, the end-user:
 
Use Case	                          | Description | Completed
------------------------------------- | -----------|-------------|
Retrieve images from Twitter feeds (Hashtags) | MosaicMe retrieves images from the defined list of Twitter hashtags and stores them in the Object store. The pictures are used to build the image library that will be used for building each mosaic. the EMC Code and EMCWorld twitter accounts. | Yes
Process a mosaic from a submitted picture | MosaicMe monitors a Twitter hashtag (#MosaicMe) for pictures. Once a picture is detected, it will build a mosaic from the submitted picture using the stored pictures in the object store.| Yes
Tweet Mosaic to Twitter Account		  | MosaicMe will Tweet the mosaic to the person that tweeted to the selected Twitter hashtag (#MosaicMe) | Yes
Display list Mosaics				  | Shows the list of mosaics currently stored in the system. The data will be available via the Web UI, API and ECS.| Yes
View and Zoom into Mosaic | Select a mosaic, display mosaic in a full screen and provide ability to zoom into the mosaic to view in detail, the raw pictures used for the composition. | Yes 
Configure Mosaicme 					  | Enables administrator to configure the system via a web interface. | No
Mosaicme statistics                   | Generates a list of statistics based on usage, storage, and images. meta data. Will use a Haddop cluster to process the stadistics. | No	
		



## Architecture 

Mosaicme is composed of multiple tiers. The following design shows the high level application architecture: 
The following diagram shows Mosaicme high level architecture: 

![Mosaicme high level architecture diagram](https://github.com/emccode/mosaicme/blob/master/documentation/images/mosaicme-high-level-architecture.PNG)

The following has an overview of each one of the components:


Component Name              |	Component Description | Completed
--------------------------- | ---------------------|---------------|
Web Interface               | Web Interface to for displaying pictures, mosaics, statistics and system configuration. | Yes
Mosaic processing service   | Mosaic processing service. Takes the mosaic generation request from the Orchestration API and generates the mosaic data and meta data. | Yes
Queuing Service				| Service to host the queues required by the system. | Yes
Twitter retrieval service   | Service that retrieves pictures and their meta data from the selected twitter accounts and adds them Object store. | Yes
Statistics Service			| Haddop Cluster that takes the data in the Object Store and processes the statistics. Stores the data back to the Object store using HDFS. | No
Caching Service             | Data caching service to speed the Web application. | Yes
Log Routing Service		    | Service to route all services logs to the Object Store. | No
Configuration & registry Service       | Service to maintain configuration, synchronization and naming registry. | No

For More information about the MosaicMe application Architecture [click Here](https://github.com/emccode/mosaicme/blob/master/documentation/MosaicMe-Architecture.md)



##Contributing to MosaicMe

The MosaicMe project has been licensed under the  [MIT](http://opensource.org/licenses/MIT "The MIT License (MIT)") License. In order to contribute to the MosaicMe project you will need to do two things:


1. License your contribution under the [DCO](http://elinux.org/Developer_Certificate_Of_Origin "Developer Certificate of Origin") + [MIT](http://opensource.org/licenses/MIT "The MIT License (MIT)")
2. Identify the type of contribution in the commit message


### 1. Licensing your Contribution: 

As part of the contribution, in the code comments (or license file) associated with the contribution must include the following:

“The MIT License (MIT)

Copyright (c) [Year], [Company Name (e.g., EMC Corporation)]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  The above copyright notice and this permission notice shall be included in  all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This code is provided under the Developer Certificate of Origin- [Insert Name], [Date (e.g., 1/1/15]”


**For example: **

A contribution from **Joe Developer**, an **independent developer**, submitted in** May 15th of 2015** should have an associated license (as file or/and code comments) like this:
 
“The MIT License (MIT)

Copyright (c) 2015, Joe Developer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  The above copyright notice and this permission notice shall be included in  all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This code is provided under the Developer Certificate of Origin- Joe Developer, May 15th 2015”

### 2. Identifying the Type of Contribution

In addition to identifying an open source license in the documentation, **all Git Commit messages** associated with a contribution must identify the type of contribution (i.e., Bug Fix, Patch, Script, Enhancement, Tool Creation, or Other).


## Licensing

MosaicME is licensed under the  [MIT](http://opensource.org/licenses/MIT "The MIT License (MIT)") license: 

“The MIT License (MIT)

Copyright (c) 2015, EMC Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Support

Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stackoverflow.com</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
