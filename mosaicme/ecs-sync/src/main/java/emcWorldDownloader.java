/**
 * Created by salemm4 on 4/8/2015.
 */
import com.amazonaws.services.s3.model.S3ObjectInputStream;
import com.emc.vipr.s3.*;
import com.emc.vipr.swift.swiftapi;
import com.amazonaws.services.s3.model.ObjectListing;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import org.javaswift.joss.model.StoredObject;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.util.Collection;
import java.util.Properties;
public class emcWorldDownloader  extends Thread{

    public String S3_ACCESS_KEY_ID ="";
    public String S3_SECRET_KEY = "";
    public String S3_ENDPOINT = "";

    public String SWIFT_ACCESS_KEY_ID ="";
    public String SWIFT_SECRET_KEY = "";
    public String SWIFT_ENDPOINT = "";

    public String S3_BUCKET = "";
    public String SWIFT_BUCKET = "";

    public String LOCAL_DIR ="";

    public String PROTOCOL ="";
    public String PB_S3_ACCESS_KEY_ID ="";
    public String PB_S3_SECRET_KEY = "";
    public String PB_S3_ENDPOINT = "";
    public String PB_S3_BUCKET = "";
    public String PB_ACTIVE = "";
    public emcWorldDownloader() {
    }

    public  void run() {
        try {
            vLogger.LogInfo("emcWorldDownloader: Start up");
            Properties prop = new Properties();
            File fecsconfig = new File("/mosaic/setting/ecsconfig.properties");
            if(fecsconfig.exists()) {
                vLogger.LogInfo("emcWorldDownloader: Read Conf file from mosaic folder");
                prop.load(new FileInputStream(fecsconfig));
            }
            else {
                vLogger.LogInfo("emcWorldDownloader: Read Conf file from local folder");
                ClassLoader classLoader = getClass().getClassLoader();
                prop.load(new FileInputStream(classLoader.getResource("ecsconfig.properties").getFile()));
            }

            S3_ACCESS_KEY_ID = prop.getProperty("username");
            S3_SECRET_KEY = prop.getProperty("password");
            S3_ENDPOINT = prop.getProperty("proxy");

            SWIFT_ACCESS_KEY_ID = prop.getProperty("swiftusername");
            SWIFT_SECRET_KEY = prop.getProperty("swiftpassword");
            SWIFT_ENDPOINT = prop.getProperty("swiftproxy");
            SWIFT_BUCKET = prop.getProperty("swiftcollectbucket");

            S3_BUCKET = prop.getProperty("s3collectbucket");
            LOCAL_DIR = prop.getProperty("emclocal");

            PROTOCOL=prop.getProperty("objectType");
            if(PROTOCOL.equals("S3")) DownloadUsingS3();
            else
                DownloadUsingSWIFT();


        } catch (Exception e) {
            vLogger.LogError("emcWorldDownloader:" + e.getMessage());
            e.printStackTrace();
        }
    }

    public void DownloadUsingS3() throws Exception
    {

        while(true) {
            ObjectListing list = s3api.ReadBucket(S3_ACCESS_KEY_ID, S3_SECRET_KEY, S3_ENDPOINT, null, S3_BUCKET);

            System.out.println("bucket files count " + list.getObjectSummaries().size());
            vLogger.LogInfo("emcWorldDownloader: bucket files count " + list.getObjectSummaries().size());

            int s3Count = list.getObjectSummaries().size();
            int localCount = new File(LOCAL_DIR).listFiles().length;
            if (s3Count != localCount) {

                for (S3ObjectSummary obj :
                        list.getObjectSummaries()) {



                    if (!(new File(LOCAL_DIR, obj.getKey()).exists())) {
                        System.out.println("Downloading - " + obj.getKey());
                        vLogger.LogInfo("emcWorldDownloader: Downloading - " + obj.getKey());
                        S3ObjectInputStream in = s3api.ReadObject(S3_ACCESS_KEY_ID,
                                S3_SECRET_KEY, S3_ENDPOINT, null,
                                S3_BUCKET, obj.getKey());


                        File file = new File(LOCAL_DIR + obj.getKey());

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
                    }
                    else
                    {
                        System.out.println("Skipping - " + obj.getKey());
                        vLogger.LogInfo("emcWorldDownloader: Skipping - " + obj.getKey());
                    }
                }
            }
            else
                System.out.println("No New Files Yet");

            vLogger.LogInfo("emcWorldDownloader: Skipping - Sleep 60 seconds");
            System.out.println("Sleep for 1 minute");
            Thread.sleep(60000);
        }


    }

    public void DownloadUsingSWIFT() throws Exception
    {

        while(true) {
            Collection<StoredObject> list = swiftapi.ReadBucket(SWIFT_ACCESS_KEY_ID, SWIFT_SECRET_KEY, SWIFT_ENDPOINT, SWIFT_BUCKET);

            int scount = list.size();
            int localCount = new File(LOCAL_DIR).listFiles().length;
            if (scount != localCount) {

                for (StoredObject obj :list) {

                    if (!(new File(LOCAL_DIR, obj.getName()).exists())) {
                        System.out.println("Downloading - " + obj.getName());
                        vLogger.LogInfo("emcWorldDownloader: Downloading - " + obj.getName());
                        InputStream in = swiftapi.ReadObject(SWIFT_ACCESS_KEY_ID,SWIFT_SECRET_KEY, SWIFT_ENDPOINT,SWIFT_BUCKET, obj.getName());

                        File file = new File(LOCAL_DIR + obj.getName());

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
                    }
                    else
                    {
                        System.out.println("Skipping - " + obj.getName());
                        vLogger.LogInfo("emcWorldDownloader: Skipping - " + obj.getName());
                    }
                }
            }
            else
                System.out.println("No New Files Yet");

            vLogger.LogInfo("emcWorldDownloader: Skipping - Sleep 60 seconds");
            System.out.println("Sleep for 1 minute");
            Thread.sleep(60000);
        }


    }



}
