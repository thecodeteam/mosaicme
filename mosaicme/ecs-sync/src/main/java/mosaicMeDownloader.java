/**
 * Created by salemm4 on 4/8/2015.
 */

import java.io.*;
import java.util.Properties;
import java.util.Date;
import com.amazonaws.services.s3.model.S3ObjectInputStream;
import com.emc.vipr.s3.s3api;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.QueueingConsumer;
import com.rabbitmq.client.MessageProperties;
public class mosaicMeDownloader  extends Thread{
    public String ENGINE_QUEUE_NAME = "";
    public String DOWNLOAD_QUEUE_NAME = "";
    public String QUEUE_HOST_NAME = "";
    public String S3_ACCESS_KEY_ID = "";
    public String S3_SECRET_KEY = "";
    public String S3_ENDPOINT = "";
    public String S3_BUCKET = "";
    public String LOCAL_DIR = "";
    public String MOSAIC_IN_DIR = "";

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
            System.out.println(prop.getProperty("downloaderQueue"));
            System.out.println(prop.getProperty("engineQueue"));
            System.out.println(prop.getProperty("queueHost"));
            System.out.println(prop.getProperty("mosaicin"));

            S3_ACCESS_KEY_ID = prop.getProperty("username");
            S3_SECRET_KEY = prop.getProperty("password");
            S3_ENDPOINT = prop.getProperty("proxy");
            S3_BUCKET = prop.getProperty("inbucket");

            LOCAL_DIR = prop.getProperty("emclocal");
            DOWNLOAD_QUEUE_NAME = prop.getProperty("downloaderQueue");
            ENGINE_QUEUE_NAME = prop.getProperty("engineQueue");
            QUEUE_HOST_NAME = prop.getProperty("queueHost");
            MOSAIC_IN_DIR = prop.getProperty("mosaicin");

            ConnectionFactory factory = new ConnectionFactory();
            factory.setHost(QUEUE_HOST_NAME);
            Connection connection = factory.newConnection();
            Channel channel = connection.createChannel();

            channel.queueDeclare(DOWNLOAD_QUEUE_NAME, true, false, false, null);
            System.out.println(" [*] Waiting for messages. To exit press CTRL+C");

            channel.basicQos(1);

            QueueingConsumer consumer = new QueueingConsumer(channel);
            channel.basicConsume(DOWNLOAD_QUEUE_NAME, false, consumer);

            while (true) {
                QueueingConsumer.Delivery delivery = consumer.nextDelivery();
                String message = new String(delivery.getBody());

                System.out.println(" [x] Received '" + message + "'");
                downloadImage(message);
                System.out.println(" [x] Done -" + (new Date()).toString());

                channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void downloadImage(String image) {
        try {
            System.out.println(" Download Image '" + image + "'");
            S3ObjectInputStream in = s3api.ReadObject(S3_ACCESS_KEY_ID,
                    S3_SECRET_KEY, S3_ENDPOINT, null,
                    S3_BUCKET, image);


            File file = new File(MOSAIC_IN_DIR + image);

            int count = 0;
            byte[] buf = new byte[1024];
            OutputStream out = new FileOutputStream(file);
            while ((count = in.read(buf)) != -1) {
                if (Thread.interrupted()) {
                    throw new InterruptedException();
                }
                out.write(buf, 0, count);
            }
            out.close();
            in.close();
            putMessge(image);

        } catch (
                Exception e
                )

        {
            e.printStackTrace();
        }

    }

    public void  putMessge(String image) throws Exception
    {
        System.out.println(" Put Message on Q '" + ENGINE_QUEUE_NAME + "'");

        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(QUEUE_HOST_NAME);
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        channel.queueDeclare(ENGINE_QUEUE_NAME, true, false, false, null);



        channel.basicPublish( "", ENGINE_QUEUE_NAME,
                MessageProperties.PERSISTENT_TEXT_PLAIN,
                image.getBytes());
        System.out.println(" [x] Sent '" + image + "'");

        channel.close();
        connection.close();
    }
}