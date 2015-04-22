/**
 * Created by salemm4 on 4/8/2015.
 */
import com.amazonaws.services.s3.model.S3ObjectInputStream;
import com.emc.vipr.s3.*;
import com.amazonaws.services.s3.model.ObjectListing;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.util.Properties;
public class emcWorldDownloader  extends Thread{

   public String S3_ACCESS_KEY_ID ="";
    public String S3_SECRET_KEY = "";
    public String S3_ENDPOINT = "";
    public String S3_BUCKET = "";
    public String LOCAL_DIR ="";
    public emcWorldDownloader() {
    }

    public  void run() {
        try {

            Properties prop = new Properties();
            ClassLoader classLoader = getClass().getClassLoader();
            prop.load(new FileInputStream(classLoader.getResource("ecsconfig.properties").getFile()));
            System.out.println(prop.getProperty("username"));
            System.out.println(prop.getProperty("password"));
            System.out.println(prop.getProperty("proxy"));
            System.out.println(prop.getProperty("emcbucket"));
            System.out.println(prop.getProperty("emclocal"));

            S3_ACCESS_KEY_ID = prop.getProperty("username");
            S3_SECRET_KEY = prop.getProperty("password");
            S3_ENDPOINT = prop.getProperty("proxy");
            S3_BUCKET = prop.getProperty("emcbucket");
            LOCAL_DIR = prop.getProperty("emclocal");

            while(true) {
                ObjectListing list = s3api.ReadBucket(S3_ACCESS_KEY_ID, S3_SECRET_KEY, S3_ENDPOINT, null, S3_BUCKET);

                System.out.println("bucket files count " + list.getObjectSummaries().size());

                int s3Count = list.getObjectSummaries().size();
                int localCount = new File(LOCAL_DIR).listFiles().length;
                if (s3Count != localCount) {

                    for (S3ObjectSummary obj :
                            list.getObjectSummaries()) {



                        if (!(new File(LOCAL_DIR, obj.getKey()).exists())) {
                            System.out.println("Downloading - " + obj.getKey());
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
                            System.out.println("skipping - " + obj.getKey());
                        }
                    }
                }
                else
                    System.out.println("No New Files Yet");

                System.out.println("Sleep for 1 minute");
                Thread.sleep(60000);
            }

        } catch (Exception e) {

            e.printStackTrace();
        }
    }

}
