package mosaicme

import (
        "io"
        "log"
        "os"
        "github.com/minio/minio-go"
		"time"
)

func (e *Engine) download() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  log.Println("Starting download raw images goroutine")
    for {
     select {
      default:
        engineRawDir := e.config.EngineDir+"/raw/"
		s3Host := e.config.S3Host+":"+e.config.S3Port
		
        time.Sleep(30000 * time.Millisecond)
        client,err := minio.NewV2(s3Host, e.config.S3AccessKey, e.config.S3SecrectKey, false)
        if err != nil {
                log.Println(err)
                return
        }
       // Create a done channel to control 'ListObjects' go routine.       
	    doneCh := make(chan struct{})

		// Indicate to our routine to exit cleanly upon return.
        defer close(doneCh)
        objectCh := client.ListObjects(e.config.BucketRawName, "", false, doneCh)
                for object := range objectCh {
                        if object.Err != nil {
                                log.Println(object.Err)
                                return
                        }
                        log.Println("Found object " + object.Key)

                        var localFilename = engineRawDir+object.Key

                        if _, err := os.Stat(localFilename); os.IsNotExist(err) {

                                log.Println(localFilename)

                                obj, err := client.GetObject(e.config.BucketRawName, object.Key)
                                if err != nil {
                                        log.Fatalln(err)
                                }
                                localFile, err := os.Create(localFilename)
                                if err != nil {
                                        log.Fatalln(err)
                                }
                                if _, err := io.Copy(localFile, obj); err != nil {
                                        log.Fatalln(err)
                                }
                                //localFile.close()

                        } else {

                             log.Println("Skipping " + object.Key)
                        }

                }
  
	  
	  
	  
	  
	  case <-e.stopchan:
      log.Println("Stop signal received. Returning...")
      return
    }
  }
  

       
  


}





