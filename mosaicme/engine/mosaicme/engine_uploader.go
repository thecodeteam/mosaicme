package mosaicme

import (
  "encoding/json"
  "log"
  "os"
  "time"

  "github.com/streadway/amqp"
)

func (e *Engine) uploader() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  log.Println("Starting uploader goroutine")
  for {
    select {
    case m := <-e.uploaderChan:

      log.Println("2")
      time.Sleep(10000 * time.Millisecond)

      //Uploade Large file
      objectLarge, err := os.Open(m.MosaicPath)
      if err != nil {
        log.Fatalln(err)
      }
      defer objectLarge.Close()

      n, err := e.s3Client.PutObject(e.config.BucketOut, "large/"+m.MosaicName, objectLarge, "application/octet-stream")
      if err != nil {
        log.Fatalln(err)
      }
      log.Println("Uploaded large", m.MosaicName, " of size: ", n, "Successfully.")
      //presign the large URL
      presignedLargeURL, err := e.s3Client.PresignedPutObject(e.config.BucketOut, "large/"+m.MosaicName, time.Second*24*60*60*7)
      if err != nil {
        log.Fatalln(err)
      }
      log.Println(presignedLargeURL)

      //Uploade Small file
      objectSmall, err := os.Open(m.ThumbnailPath)
      if err != nil {
        log.Fatalln(err)
      }
      defer objectLarge.Close()

      n, err = e.s3Client.PutObject(e.config.BucketOut, "small/"+m.MosaicName, objectSmall, "application/octet-stream")
      if err != nil {
        log.Fatalln(err)
      }
      log.Println("Uploaded thumnail", m.MosaicName, " of size: ", n, "Successfully.")

      //presign the thunmail URL
      presignedURL, err := e.s3Client.PresignedPutObject(e.config.BucketOut, "small/"+m.MosaicName, time.Second*24*60*60*7)
      if err != nil {
        log.Fatalln(err)
      }

      log.Printf("Current presing URL: %s\n", presignedURL)

      log.Printf("Send message to Twitter Publisher component ")

      mJson, err := json.Marshal(*m)
      if err != nil {
        log.Fatalln(err)
      }

      err = e.channel.Publish(
        "mosaicme", // exchange
        "info",     // routing key,
        false,      // mandatory
        false,      // immediate
        amqp.Publishing{
          ContentType: "application/json",
          Body:        mJson,
        })
      if err != nil {
        log.Printf("Queue Consume Error: %s\n", err)
        close(e.stopchan)
        return
      }

    case <-e.stopchan:
      log.Println("Stop signal received. Returning...")
      return
    }
  }
}
