/**
 * Created by salemm4 on 4/8/2015.
 */
import java.io.BufferedReader;
import java.io.InputStreamReader;
public class syncengine {
    public static void main(String[] args) {
     try {
         String start="";
         String key="";
         vLogger.LogInfo("ecs-sync: Start up");
         System.out.println(" Welcome to Mosaic-ECS Sync Engine");
         System.out.println("");

         if(args.length>0) {
             start = args[0];
             vLogger.LogInfo("ecs-sync: Start up Option =" + start);
             System.out.println("ecs-sync: Start up Option =" + start);
         }
         else {

             System.out.println("1- Start EMC World Downloader Only.");
             System.out.println("2- Start MosaicMe Downloader Only.");
             System.out.println("3- Start MosaicMe Uploader Only.");
             System.out.println("4- Start All");
             System.out.println("5- Exit");
         }
         while (true) {
          if(start.equals("")) {
              System.out.print("Enter Option Number: ");
              key = new BufferedReader(new InputStreamReader(System.in)).readLine();
              vLogger.LogInfo("ecs-sync: User select " + key);
          }else
              key=start;
             if (key.equals("1") || key.equals("2") || key.equals("3") || key.equals("4") || key.equals("5")) {
                 int n = Integer.parseInt(key);

                 switch (n) {
                     case 1: {

                         emcWorldDownloader downloader = new emcWorldDownloader();
                         downloader.run();
                         break;
                     }

                     case 2: {
                         mosaicMeDownloader getter = new mosaicMeDownloader();
                         getter.run();
                         break;
                     }

                     case 3: {
                         mosaicMeUploader uploader = new mosaicMeUploader();
                         uploader.run();
                         break;
                     }

                     case 4: {
                         (new Thread(new emcWorldDownloader())).start();
                         (new Thread(new mosaicMeDownloader())).start();
                         (new Thread(new mosaicMeUploader())).start();
                         break;
                     }

                     case 5: {
                         System.exit(0);
                     }

                     default: {

                         System.out.println("Please Choice number 1-4 Only.");

                         break;
                     }


                 }
             } else {
                 System.out.println("Please Choice number 1-4 Only.");

             }
         }

     }
     catch(Exception e)
     {
             vLogger.LogError("ecs-sync:Error" + e.getMessage());

         e.printStackTrace();
     }
    }


}
