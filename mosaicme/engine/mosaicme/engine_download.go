package mosaicme

import (
  "io"
  "log"
  "os"
  "path"
  "time"
)

func (e *Engine) downloader() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  log.Println("[Downloader] Starting goroutine")
  for {
    select {
    default:
      rawDir := path.Join(e.config.BaseDir, rawDir)
      log.Println(rawDir)

      time.Sleep(30000 * time.Millisecond)

      // Create a done channel to control 'ListObjects' go routine.
      doneCh := make(chan struct{})

      // Indicate to our routine to exit cleanly upon return.
      defer close(doneCh)
      objectCh := e.s3Client.ListObjects(e.config.BucketIn, "", false, doneCh)
      for object := range objectCh {
        if object.Err != nil {
          log.Println(object.Err)
          return
        }
        log.Println(" [Downloader] Found object " + object.Key)

        var localFilename = rawDir +"/" + object.Key

        if _, err := os.Stat(localFilename); os.IsNotExist(err) {

          //log.Println("[Downloader] saving file "+localFilename)

          obj, err := e.s3Client.GetObject(e.config.BucketIn, object.Key)
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

          log.Println("[Downloader] Skipping " + object.Key)
        }

      }

    case <-e.stopchan:
      log.Println("[Downloader] Stop signal received. Returning...")
      return
    }
  }

}
