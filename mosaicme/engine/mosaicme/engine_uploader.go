package mosaicme

import (
  "encoding/json"
  "log"
  "os"
  "time"

  "github.com/streadway/amqp"
)

// uploader listens to a channel for messages from the builder goroutine with
// mosaics, uploads them to the object storage backend, and notifies the
// Publisher service once it's done
func (e *Engine) uploader() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  log.Println("Starting uploader goroutine")
  for {
    select {
    case m := <-e.uploaderChan:

      log.Printf("[Uploader] %s - Uploading high-res mosaic\n", m.MosaicName)

      objectLarge, err := os.Open(m.MosaicPath)
      if err != nil {
        log.Printf("[Uploader] %s - Error opening high-res mosaic in local filesystem: %s\n", m.MosaicName, err)
        continue
      }

      n, err := e.s3Client.PutObject(e.config.BucketOut, "large/"+m.MosaicName, objectLarge, "application/octet-stream")
      objectLarge.Close()
      if err != nil {
        log.Printf("[Uploader] %s - Error uploading high-res mosaic to object store: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Uploader] %s - Uploaded high-res mosaic successfully. Size: %d\n", m.MosaicName, n)
      log.Printf("[Uploader] %s - Generating presigned URL for high-res mosaic\n", m.MosaicName)

      presignedLargeURL, err := e.s3Client.PresignedPutObject(e.config.BucketOut, "large/"+m.MosaicName, time.Second*24*60*60*7)
      if err != nil {
        log.Printf("[Uploader] %s - Error signing URL for high-res mosaic: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Uploader] %s - Generated presigned URL for high-res mosaic: %s\n", m.MosaicName, presignedLargeURL)
      log.Printf("[Uploader] %s - Uploading mosaic thumbnail\n", m.MosaicName)

      objectSmall, err := os.Open(m.ThumbnailPath)
      if err != nil {
        log.Printf("[Uploader] %s - Error opening thumbnail in local filesystem: %s\n", m.MosaicName, err)
        continue
      }

      n, err = e.s3Client.PutObject(e.config.BucketOut, "small/"+m.MosaicName, objectSmall, "application/octet-stream")
      objectSmall.Close()
      if err != nil {
        log.Printf("[Uploader] %s - Error uploading thumbnail to object store: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Uploader] %s - Uploaded mosaic thumbnail successfully. Size: %d\n", m.MosaicName, n)
      log.Printf("[Uploader] %s - Generating presigned URL for mosaic thumbnail\n", m.MosaicName)

      presignedURL, err := e.s3Client.PresignedPutObject(e.config.BucketOut, "small/"+m.MosaicName, time.Second*24*60*60*7)
      if err != nil {
        log.Printf("[Uploader] %s - Error signing URL: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Uploader] %s - Generated presigned URL for mosaic thumbnail: %s\n", m.MosaicName, presignedURL)
      log.Printf("[Uploader] %s - Sending message to Publisher\n", m.MosaicName)

      mJSON, err := json.Marshal(*m)
      if err != nil {
        log.Printf("[Uploader] %s - Error parsing message: %s\n", m.MosaicName, err)
        continue
      }

      err = e.channel.Publish(
        "mosaicme", // exchange
        "info",     // routing key,
        false,      // mandatory
        false,      // immediate
        amqp.Publishing{
          ContentType: "application/json",
          Body:        mJSON,
        })

      if err != nil {
        log.Printf("[Uploader] %s - Error sending message to Publisher: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Uploader] %s - Sent message to Twitter Publisher\n", m.MosaicName)

    case <-e.stopchan:
      log.Println("[Uploader] Stop signal received. Returning...")
      return
    }
  }
}
