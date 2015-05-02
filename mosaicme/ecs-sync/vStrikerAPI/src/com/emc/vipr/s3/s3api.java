/*
 * Copyright 2013 EMC Corporation. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 * http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
package com.emc.vipr.s3;
import java.net.URL;
import java.io.InputStream;
import java.util.List;

import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.S3ClientOptions;
import com.amazonaws.services.s3.model.*;
import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.HttpMethod;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;

import com.emc.vipr.services.s3.ViPRS3Client;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.ArrayList;

public class s3api {

	// Create Client Instance
	public static ViPRS3Client getS3Client(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE) {
		BasicAWSCredentials creds = new BasicAWSCredentials(S3_ACCESS_KEY_ID,
				S3_SECRET_KEY);
		S3ClientOptions opt = new S3ClientOptions();
		opt.setPathStyleAccess(true);
		ViPRS3Client client = new ViPRS3Client(S3_ENDPOINT, creds);


		client.setS3ClientOptions(opt);
		if (S3_ViPR_NAMESPACE != null) {
			client.setNamespace(S3_ViPR_NAMESPACE);
		}

		return client;
	}

	/********************************* Bucket Operations ******************************/

	public static void CreateBucket(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET) throws Exception {
		// create the ViPR S3 Client
		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);

		// create the bucket - used for subsequent demo operations
		s3.createBucket(S3_BUCKET);

	}

	public static ObjectListing ReadBucket(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET) throws Exception {
		// create the ViPR S3 Client
		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);

		// get bucket listing to retrieve the bucket name
		return s3.listObjects(S3_BUCKET);

	}

	public static List<Bucket> ListBuckets(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE)
			throws Exception {
		// create the ViPR S3 Client
		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);

		// get bucket listing to retrieve the bucket name
		return s3.listBuckets();

	}

	public static void DeleteBuckets(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET) throws Exception {
		// create the ViPR S3 Client
		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);

		// get bucket listing to retrieve the bucket name
		s3.deleteBucket(S3_BUCKET);

	}

	/********************************* Object Operations ******************************/
	public static void CreateObjectWithMeta(String S3_ACCESS_KEY_ID,
									String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
									String S3_BUCKET, String key, InputStream content,String metaKey,String metaValue) throws Exception {

		System.out.println("Access ID:"+S3_ACCESS_KEY_ID);
		System.out.println("Access secret:"+S3_SECRET_KEY);
		System.out.println("Access URL:"+S3_ENDPOINT);
		System.out.println("Access namespace:" + S3_ViPR_NAMESPACE);
		System.out.println("Access bucket:"+S3_BUCKET);
		System.out.println("Access key:"+key);

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		// create the object in the demo bucket
		if(metaKey.equals("") && metaValue.equals("")) {
			ObjectMetadata obj = new ObjectMetadata();
			obj.addUserMetadata(metaKey,metaValue);
			s3.putObject(S3_BUCKET, key, content, null);
		}
		else
			s3.putObject(S3_BUCKET, key, content, null);

	}

	public static void CreateObject(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET, String key, InputStream content) throws Exception {

		System.out.println("Access ID:"+S3_ACCESS_KEY_ID);
		System.out.println("Access secret:"+S3_SECRET_KEY);
		System.out.println("Access URL:"+S3_ENDPOINT);
		System.out.println("Access namespace:"+S3_ViPR_NAMESPACE);
		System.out.println("Access bucket:"+S3_BUCKET);
		System.out.println("Access key:"+key);

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		// create the object in the demo bucket

			s3.putObject(S3_BUCKET, key, content, null);

		}








	public static void CreateLargeObject(String S3_ACCESS_KEY_ID,
									String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
									String S3_BUCKET, String key, File file) throws Exception {

		System.out.println("Access ID:"+S3_ACCESS_KEY_ID);
		System.out.println("Access secret:"+S3_SECRET_KEY);
		System.out.println("Access URL:"+S3_ENDPOINT);
		System.out.println("Access namespace:"+S3_ViPR_NAMESPACE);
		System.out.println("Access bucket:"+S3_BUCKET);
		System.out.println("Access key:"+key);

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);

			InitiateMultipartUploadRequest initRequest = new InitiateMultipartUploadRequest(S3_BUCKET, key);
			InitiateMultipartUploadResult initResponse =s3.initiateMultipartUpload(initRequest);
			long partSize = 1 * 1024 * 1024; // Set part size to 1 MB.
			// list of UploadPartResponse objects for each part that is uploaded
			List<PartETag> partETags = new ArrayList<PartETag>();
			long filePosition = 0;
			for (int i = 1; filePosition < file.length(); i++) {
				// get the size of the chunk.  Note - the last part can be less than the chunk size
				partSize = Math.min(partSize, (file.length() - filePosition));

				System.out.println( String.format("Sending chunk [%d] starting at position [%d]", i, filePosition));

				// Create request to upload a part.
				UploadPartRequest uploadRequest = new UploadPartRequest()
						.withBucketName(S3_BUCKET).withKey(key)
						.withUploadId(initResponse.getUploadId()).withPartNumber(i)
						.withFileOffset(filePosition)
						.withFile(file)
						.withPartSize(partSize);

				// Upload part and add response to our list.
				PartETag eTagPart = s3.uploadPart(uploadRequest).getPartETag();
				partETags.add(eTagPart);

				// set file position to the next part in the file
				filePosition += partSize;
			}
			System.out.println("Waiting for completion of multi-part upload");
			CompleteMultipartUploadRequest compRequest = new
					CompleteMultipartUploadRequest(S3_BUCKET,
					key,
					initResponse.getUploadId(),
					partETags);

			s3.completeMultipartUpload(compRequest);




	}

	public static void UpdateObject(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET, String key, InputStream content) throws Exception {

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		// create the object in the demo bucket
		s3.putObject(S3_BUCKET, key, content, null);

	}

	public static void DeleteObject(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET, String key) throws Exception {

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		// create the object in the demo bucket
		s3.deleteObject(S3_BUCKET, key);

	}

	public static S3ObjectInputStream ReadObject(String S3_ACCESS_KEY_ID,
			String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,
			String S3_BUCKET, String key) throws Exception {

		ViPRS3Client s3 = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		// create the object in the demo bucket
		S3Object object = s3.getObject(S3_BUCKET, key);

		return object.getObjectContent();

	}

	public static URL generatePresignedUrl(String S3_ACCESS_KEY_ID,
										   String S3_SECRET_KEY, String S3_ENDPOINT, String S3_ViPR_NAMESPACE,GeneratePresignedUrlRequest  generatePresignedUrlRequest)
	{
		ViPRS3Client s3client = getS3Client(S3_ACCESS_KEY_ID, S3_SECRET_KEY,
				S3_ENDPOINT, S3_ViPR_NAMESPACE);
		return s3client.generatePresignedUrl(generatePresignedUrlRequest);
	}
}
