import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Iterator;
import java.util.List;
import java.io.File;


import org.javaswift.joss.client.factory.AccountConfig;
import org.javaswift.joss.client.factory.AccountFactory;
import org.javaswift.joss.model.Account;
import org.javaswift.joss.model.Container;
import org.javaswift.joss.model.StoredObject;
;
import java.text.SimpleDateFormat;
import com.amazonaws.services.s3.model.Bucket;
import com.amazonaws.services.s3.model.ObjectListing;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import java.util.Date;

import com.emc.vipr.s3.*;
import com.emc.vipr.swift.*;


import com.emc.vipr.services.s3.ViPRS3Client;

public class VStrikerAPIUnitTest {

	public static String username="wuser1@sanity.local";
	public static String atmosusername="7b359e4d039540008ea4fbf4d20cd591/wuser1@sanity.local";
	public static String password="+0K1VUuvMPr6udyFgX54UqiVx5vH8Zn+CrV3mb6t";
	public static String s3proxy="http://10.247.188.225:10101";
	public static String swiftproxy="http://10.243.188.101:10501";
	public static String atmosproxy="http://10.247.188.225:10301";

	public static String s3bucket="test-s3";
	public static String swiftbucket="test-swift";
	public static String atmosbucket="test-atmos";
	public static String filelocation="C:\\mosaic-generator\\MontyPython\\in\\jellyfish.jpg";
	public static String fileName ="jellyfish.jpg";


	public  void test() throws Exception {
		/*System.out.println("Hello Test");
		TestS3API();
		TestS3CreateObject();*/

		TestSwiftGetClient();
		TestSwiftReadBucket();
		TestSwiftCreateObject();
		TestSwiftDeleteObject();

	}


	public static void TestS3API() throws Exception
	{
		ViPRS3Client conn =s3api.getS3Client(username,password,s3proxy,null);
		System.out.println("Unit Test S3 API " +conn.S3_SERVICE_NAME);
	}

	public static void TestS3ReadBucket() throws Exception
	{
		ObjectListing list =s3api.ReadBucket(username,password,s3proxy,null,s3bucket);
		   for (S3ObjectSummary objectSummary : 
			   list.getObjectSummaries()) {
			   System.out.println("Unit Test S3 API Bucket Read - " + objectSummary.getKey() + "  " +
                       "(size = " + objectSummary.getSize() + 
                       ")");
		   }
	}

	public static void TestS3CreateObject() throws Exception
	{
		try
		{
				FileInputStream fis = new FileInputStream(filelocation);
				s3api.CreateObject(username,password,s3proxy,null,s3bucket,fileName, fis);
			System.out.println("Finished loading S3 Test file");
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public static void TestSwiftGetClient() throws Exception
	{

		Account conn =swiftapi.ViPRSwiftClient(username,password,swiftproxy);
		System.out.println("Unit Test SWIFT API " +conn.toString());
	}

	public static void TestSwiftReadBucket() throws Exception
	{
		Account account =swiftapi.ViPRSwiftClient(username,password,swiftproxy);
		for (Container container : account.list()) {
			boolean isPublic = container.isPublic();
			System.out.printf("%nContainer: %s (%s, %d objects using %d bytes)%n", container.getName(), isPublic ? "public" : "private",
					container.getCount(), container.getBytesUsed());


			if (container.getCount() > 0) {
				System.out.println("Contents:");
				for (StoredObject object : container.list()) {
					System.out.printf("  %s%n", object.getName());
					if (isPublic) {
						System.out.printf("    Public URL: %s%n", object.getPublicURL());
					}
					System.out.printf("    Type: %s%n    Size: %s%n    Last modified: %s%n    E-tag: %s%n", object.getContentType(), object.getContentLength(),
							object.getLastModified(), object.getEtag());

				}
			}
		}
	}
	public static void TestSwiftCreateObject() throws Exception
	{
		try
		{   FileInputStream fis = new FileInputStream(filelocation);
			swiftapi.CreateObject(username, password, swiftproxy,swiftbucket,fileName, fis);
			System.out.println("Finished Create Swift Test file");
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public static void TestSwiftDeleteObject() throws Exception
	{
		try
		{
			swiftapi.DeleteObject(username,password,swiftproxy,swiftbucket,fileName);
			System.out.println("Finished Deleting Swift Test file");

		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}



}
