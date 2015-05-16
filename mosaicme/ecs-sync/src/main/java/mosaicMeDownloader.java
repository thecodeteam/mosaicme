/**
 * Created by salemm4 on 4/8/2015.
 */

import java.io.*;
import java.util.Properties;
import java.util.Date;
import com.amazonaws.services.s3.model.S3ObjectInputStream;
import com.emc.vipr.s3.s3api;
import com.emc.vipr.swift.*;

import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.QueueingConsumer;
import com.rabbitmq.client.MessageProperties;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import org.json.simple.parser.JSONParser;


public class mosaicMeDownloader  extends Thread{
    public String ENGINE_QUEUE_NAME = "";
    public String DOWNLOAD_QUEUE_NAME = "";
    public String QUEUE_HOST_NAME = "";
    public String S3_ACCESS_KEY_ID = "";
    public String S3_SECRET_KEY = "";
    public String S3_ENDPOINT = "";
    public String MOSAIC_IN_BUCKET = "";
    public String LOCAL_DIR = "";
    public String MOSAIC_IN_DIR = "";

    public String SWIFT_ACCESS_KEY_ID ="";
    public String SWIFT_SECRET_KEY = "";
    public String SWIFT_ENDPOINT = "";
    public String PROTOCOL ="";

    public void run() {
        try {


            vLogger.LogInfo("mosaicMeDownloader: Start up");
            Properties prop = new Properties();
            ClassLoader classLoader = getClass().getClassLoader();
            prop.load(new FileInputStream(classLoader.getResource("ecsconfig.properties").getFile()));
            System.out.println(prop.getProperty("username"));
            System.out.println(prop.getProperty("password"));
            System.out.println(prop.getProperty("proxy"));
            System.out.println(prop.getProperty("emcbucket"));
            System.out.println(prop.getProperty("emclocal"));
            System.out.println(prop.getProperty("downloaderQueue"));
            System.out.println(prop.getProperty("engineQueue"));
            System.out.println(prop.getProperty("queueHost"));
            System.out.println(prop.getProperty("mosaicin"));

            S3_ACCESS_KEY_ID = prop.getProperty("username");
            S3_SECRET_KEY = prop.getProperty("password");
            S3_ENDPOINT = prop.getProperty("proxy");
            MOSAIC_IN_BUCKET = prop.getProperty("inbucket");

            SWIFT_ACCESS_KEY_ID = prop.getProperty("swiftusername");
            SWIFT_SECRET_KEY = prop.getProperty("swiftpassword");
            SWIFT_ENDPOINT = prop.getProperty("swiftproxy");

            LOCAL_DIR = prop.getProperty("emclocal");
            DOWNLOAD_QUEUE_NAME = prop.getProperty("downloaderQueue");
            ENGINE_QUEUE_NAME = prop.getProperty("engineQueue");
            QUEUE_HOST_NAME = prop.getProperty("queueHost");
            MOSAIC_IN_DIR = prop.getProperty("mosaicin");
            PROTOCOL=prop.getProperty("objectType");

            ConnectionFactory factory = new ConnectionFactory();
            factory.setHost(QUEUE_HOST_NAME);
            Connection connection = factory.newConnection();
            Channel channel = connection.createChannel();

            channel.queueDeclare(DOWNLOAD_QUEUE_NAME, true, false, false, null);
            System.out.println(" [*] Waiting for messages. To exit press CTRL+C");
            vLogger.LogInfo("mosaicMeDownloader: [*] Waiting for messages. To exit press CTRL+C");
            channel.basicQos(1);

            QueueingConsumer consumer = new QueueingConsumer(channel);
            channel.basicConsume(DOWNLOAD_QUEUE_NAME, false, consumer);

            while (true) {
                QueueingConsumer.Delivery delivery = consumer.nextDelivery();
                String message = new String(delivery.getBody());

                vLogger.LogInfo("mosaicMeDownloader:  [x] Received '" + message + "'");
                System.out.println(" [x] Received '" + message + "'");
                downloadImage(message);
                System.out.println(" [x] Done -" + (new Date()).toString());
                vLogger.LogInfo("mosaicMeDownloader:[x]Done - " + (new Date()).toString());

                        channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
            }
        } catch (Exception e) {
            e.printStackTrace();
            vLogger.LogError("mosaicMeDownloader:" + e.getMessage());
        }
    }

    public void downloadImage(String msg) {
        try {

            System.out.println(" Download Image '" + msg + "'");
            vLogger.LogInfo("mosaicMeDownloader: Download Image '" + msg + "'");
            JSONParser jsonParser = new JSONParser();
            JSONObject jsonObject = (JSONObject) jsonParser.parse(msg);
            String image = (String) jsonObject.get("media_id") +".jpg";
            vLogger.LogInfo("mosaicMeDownloader: Download image '" + image + "'");

            File file = new File(MOSAIC_IN_DIR + image);
            int count = 0;
            byte[] buf = new byte[1024];
            OutputStream out = new FileOutputStream(file);

            if(PROTOCOL.equals("S3")) {

                S3ObjectInputStream inS3 = s3api.ReadObject(S3_ACCESS_KEY_ID,
                        S3_SECRET_KEY, S3_ENDPOINT, null,
                        MOSAIC_IN_BUCKET, image);

                while ((count = inS3.read(buf)) != -1) {
                    if (Thread.interrupted()) {
                        throw new InterruptedException();
                    }
                    out.write(buf, 0, count);
                }
                out.close();
                inS3.close();
            }
            else {


                InputStream inSwift = swiftapi.ReadObject(SWIFT_ACCESS_KEY_ID,
                        SWIFT_SECRET_KEY, SWIFT_ENDPOINT,MOSAIC_IN_BUCKET, image);

                while ((count = inSwift.read(buf)) != -1) {
                    if (Thread.interrupted()) {
                        throw new InterruptedException();
                    }
                    out.write(buf, 0, count);
                }
                out.close();
                inSwift.close();
            }






            putMessge(msg);

        } catch (Exception e) {
            e.printStackTrace();
            vLogger.LogError("mosaicMeDownloader:" + e.getMessage());

        }

    }

    public void  putMessge(String image) throws Exception
    {
        System.out.println(" Put Message on Q '" + ENGINE_QUEUE_NAME + "'");
        vLogger.LogInfo("mosaicMeDownloader: Put Message on Q '" + ENGINE_QUEUE_NAME + "'");

        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(QUEUE_HOST_NAME);
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        channel.queueDeclare(ENGINE_QUEUE_NAME, true, false, false, null);



        channel.basicPublish( "", ENGINE_QUEUE_NAME,
                MessageProperties.PERSISTENT_TEXT_PLAIN,
                image.getBytes());
        System.out.println(" [x] Sent '" + image + "'");
        vLogger.LogInfo("mosaicMeDownloader:  [x] Sent '" + image + "'");

        channel.close();
        connection.close();
    }
}