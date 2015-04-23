/**
 * Created by salemm4 on 4/8/2015.
 */

import java.io.*;
import java.net.URL;
import java.util.Properties;
import java.util.Date;
import com.amazonaws.services.s3.model.S3ObjectInputStream;
import com.emc.vipr.s3.s3api;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.QueueingConsumer;
import com.rabbitmq.client.MessageProperties;

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.HttpMethod;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.model.GeneratePresignedUrlRequest;
import javafx.scene.control.Hyperlink;
import twitter4j.*;
import twitter4j.auth.AccessToken;


public class mosaicMeUploader  extends Thread{
    public String DONE_QUEUE_NAME = "";
    public String FINISHED_QUEUE_NAME = "";
    public String QUEUE_HOST_NAME = "";
    public String S3_ACCESS_KEY_ID = "";
    public String S3_SECRET_KEY = "";
    public String S3_ENDPOINT = "";
    public String S3_BUCKET = "";
    public String LOCAL_DIR = "";
    public String MOSAIC_OUT_LARGE_DIR = "";
    public String MOSAIC_OUT_SMALL_DIR = "";

    public String MOSAIC_OUT_LARGE_BUCKET = "";
    public String MOSAIC_OUT_SMALL_BUCKET = "";

    public String TWITTER_TEXT = "";
    public String TWITTER_TAG = "";
    public String CONSUMER_KEY = "";
    public String CONSUMER_SECRET = "";
    public String ACCESS_TOKEN = "";
    public String ACCESS_TOKEN_SECRET = "";

    public void run() {
        try {


            Properties prop = new Properties();
            ClassLoader classLoader = getClass().getClassLoader();
            prop.load(new FileInputStream(classLoader.getResource("ecsconfig.properties").getFile()));
            System.out.println(prop.getProperty("username"));
            System.out.println(prop.getProperty("password"));
            System.out.println(prop.getProperty("proxy"));
            System.out.println(prop.getProperty("emcbucket"));
            System.out.println(prop.getProperty("emclocal"));
            System.out.println(prop.getProperty("uploaderQueue"));
            System.out.println(prop.getProperty("queueHost"));
            System.out.println(prop.getProperty("twitterQueue"));
            System.out.println(prop.getProperty("mosaicoutlarge"));
            System.out.println(prop.getProperty("outlargebucket"));
            System.out.println(prop.getProperty("outsmallbucket"));

            S3_ACCESS_KEY_ID = prop.getProperty("username");
            S3_SECRET_KEY = prop.getProperty("password");
            S3_ENDPOINT = prop.getProperty("proxy");
            S3_BUCKET = prop.getProperty("emcbucket");
            LOCAL_DIR = prop.getProperty("emclocal");

            FINISHED_QUEUE_NAME = prop.getProperty("twitterQueue");
            DONE_QUEUE_NAME = prop.getProperty("uploaderQueue");
            QUEUE_HOST_NAME = prop.getProperty("queueHost");
            MOSAIC_OUT_LARGE_DIR = prop.getProperty("mosaicoutlarge");
            MOSAIC_OUT_SMALL_DIR = prop.getProperty("mosaicoutsmall");

            MOSAIC_OUT_LARGE_BUCKET = prop.getProperty("outlargebucket");
            MOSAIC_OUT_SMALL_BUCKET = prop.getProperty("outsmallbucket");
            TWITTER_TEXT = prop.getProperty("twitterText");
            TWITTER_TAG =  prop.getProperty("twitterhashtage");

            CONSUMER_KEY = prop.getProperty("consumerKey");;
            CONSUMER_SECRET = prop.getProperty("consumerSecret");;
            ACCESS_TOKEN = prop.getProperty("accessToken");;
            ACCESS_TOKEN_SECRET = prop.getProperty("accessTokenSecret");;



            ConnectionFactory factory = new ConnectionFactory();
            factory.setHost(QUEUE_HOST_NAME);
            Connection connection = factory.newConnection();
            Channel channel = connection.createChannel();

            channel.queueDeclare(DONE_QUEUE_NAME, true, false, false, null);
            System.out.println(" [*] Waiting for messages. To exit press CTRL+C");

            channel.basicQos(1);

            QueueingConsumer consumer = new QueueingConsumer(channel);
            channel.basicConsume(DONE_QUEUE_NAME, false, consumer);

            while (true) {
                QueueingConsumer.Delivery delivery = consumer.nextDelivery();
                String message = new String(delivery.getBody());

                System.out.println(" [x] Received '" + message + "'");
                uploadImage(message);
                System.out.println(" [x] Done -" + (new Date()).toString());

                channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);




            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void uploadImage(String image) {
        try {
            System.out.println(" Download Image '" + image + "'");

            String filelarge = MOSAIC_OUT_LARGE_DIR +"mosaic-"+image;
            String filesmall = MOSAIC_OUT_SMALL_DIR +"thm-"+image;
            String largeimage="mosaic-"+image;
            String smallimage="thm-"+image;


            FileInputStream fis2 = new FileInputStream(filesmall);
            s3api.CreateObject(S3_ACCESS_KEY_ID,S3_SECRET_KEY,S3_ENDPOINT,null,MOSAIC_OUT_SMALL_BUCKET,smallimage, fis2);



            java.util.Date expiration = new java.util.Date();
            long milliSeconds = expiration.getTime();
            milliSeconds += 1000 * 60 * 60*24*365; // Add 1 hour.
            expiration.setTime(milliSeconds);

            GeneratePresignedUrlRequest generatePresignedUrlRequest =
                    new GeneratePresignedUrlRequest(MOSAIC_OUT_SMALL_BUCKET, smallimage);
            generatePresignedUrlRequest.setMethod(HttpMethod.GET);
            generatePresignedUrlRequest.setExpiration(expiration);

            URL smallurl = s3api.generatePresignedUrl(S3_ACCESS_KEY_ID,S3_SECRET_KEY,S3_ENDPOINT,null,generatePresignedUrlRequest);




            FileInputStream fis = new FileInputStream(filelarge);
            File f = new File(filelarge);

            s3api.CreateLargeObject(S3_ACCESS_KEY_ID,S3_SECRET_KEY,S3_ENDPOINT,null,MOSAIC_OUT_LARGE_BUCKET,largeimage, f);

            generatePresignedUrlRequest =
                    new GeneratePresignedUrlRequest(MOSAIC_OUT_LARGE_BUCKET, largeimage);
            generatePresignedUrlRequest.setMethod(HttpMethod.GET);
            generatePresignedUrlRequest.setExpiration(expiration);

            URL largeurl = s3api.generatePresignedUrl(S3_ACCESS_KEY_ID,S3_SECRET_KEY,S3_ENDPOINT,null,generatePresignedUrlRequest);

            putMessge(smallurl.toString(),largeurl.toString());

            //Delete Files
        //    if(!(new File(filelarge).delete()))
                System.out.println("Can not delete file "+filelarge);

       //     if(!(new File(filesmall).delete()))
                System.out.println("Can not delete file "+filesmall);

        } catch (
                Exception e
                )

        {
            e.printStackTrace();
        }

    }

    public void  putMessge(String smallurl,String largeurl) throws Exception
    {
        try {
            System.out.println(" Put Message on twitter");
            System.out.println(" largeURL " +largeurl);
            //Instantiate a re-usable and thread-safe factory
            TwitterFactory twitterFactory = new TwitterFactory();

            //Instantiate a new Twitter instance
            Twitter twitter = twitterFactory.getInstance();

            //setup OAuth Consumer Credentials
            twitter.setOAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET);

            //setup OAuth Access Token
            twitter.setOAuthAccessToken(new AccessToken(ACCESS_TOKEN,ACCESS_TOKEN_SECRET));

            //Instantiate and initialize a new twitter status update
            //String msg="http://10.243.188.101:10101/mosaic-outlarge/mosaic-penguins.jpg?Signature=vNXXsGWjFRIxFqssKYB1hqXHqv4%3D&AWSAccessKeyId=wuser1%40sanity.local&Expires=1431224053";

            StatusUpdate statusUpdate = new StatusUpdate(TWITTER_TEXT);
            //attach any media, if you want to
            statusUpdate.setMedia("", new URL(smallurl).openStream());
            Status status = twitter.updateStatus(statusUpdate);

        }
        catch(Exception e)
        {
            e.printStackTrace();
        }

    }


}