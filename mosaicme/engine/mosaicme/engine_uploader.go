package mosaicme

import (
  "log"
  "time"
  "github.com/minio/minio-go"
)

func (e *Engine) uploader(tweetOut Message) {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()


  log.Println("Starting uploader goroutine")
  for {
    select {
    default:

      // we need to get the filename for mosaic


      log.Println("2")
      time.Sleep(10000 * time.Millisecond)
      mosaicsDir := path.Join(baseDir, "mosaics") // location to store the new generated mosaic image
      thumbnailsDir := path.Join(baseDir, "thumbnails") // location to store the thumnails for to display it on the website
      s3Host := e.config.S3Host + ":" + e.config.S3Port
      mosaicsOut := e.config.BucketOutName

      client, err := minio.NewV2(s3Host, e.config.S3AccessKey, e.config.S3SecrectKey, false)
      if err != nil {
        log.Println(err)
        return
      }
      //Uploade Large file
      objectLarge, err := os.Open(mosaicsDir+"/"+ e.config.mosaicFileName)
	    if err != nil {
		log.Fatalln(err)
	}
	defer objectLarge.Close()

	n, err := client.PutObject(mosaicsOut,"large/"+ e.config.mosaicFileName, objectLarge, "application/octet-stream")
	    if err != nil {
		log.Fatalln(err)
	}
	log.Println("Uploaded large", e.config.mosaicFileName, " of size: ", n, "Successfully.")
       //presign the large URL
        presignedLargeURL, err := client.PresignedPutObject(mosaicsOut,"large/"+ e.config.mosaicFileName, time.Second*24*60*60*7)
	    if err != nil {
                log.Fatalln(err)
        }
        log.Println(presignedLargeURL)

        //Uploade Small file
        objectSmall, err := os.Open(thumbnailsDir+"/"+ e.config.mosaicFileName)
	    if err != nil {
		log.Fatalln(err)
	}
	defer objectLarge.Close()

	n, err := client.PutObject(mosaicsOut,"small/"+ e.config.mosaicFileName, objectSmall, "application/octet-stream")
	    if err != nil {
		log.Fatalln(err)
	}
	log.Println("Uploaded thumnail", e.config.mosaicFileName, " of size: ", n, "Successfully.")

    //presign the thunmail URL
        presignedURL, err := client.PresignedPutObject(mosaicsOut,"large/"+ e.config.mosaicFileName, time.Second*24*60*60*7)
	    if err != nil {
                log.Fatalln(err)
        }

        log.Println("current presing url :" + presignedURL)

	tweetOut.ImgURL = presignedURL

//TODO update the the incoming tweet Message with presignURL in the image url element

// Put Message out on Queued
	log.Printf("Creating tiles into\n")
	if err = e.createTiles(); err != nil {
	    log.Printf("Error creating tiles: %s\n", err)
	    close(e.stopchan)
	    return
	  }
	    log.Printf("Starting queue publishing ")

	err := e.channel.Publish(
	    "mosaicme",        // exchange
	    "info",      // routing key,
	    false,              // mandatory
	    false,              // immediate
            amqp.Publishing{
		    ContentType: "application/json",
		    Body:        []byte(tweetOut),
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
