package mosaicme

import (
  "encoding/json"
  "fmt"
  "io"
  "log"
  "net/http"
  "os"
  "os/exec"
  "path"
  "time"

)

type Message struct {
  TwitterHandler string `json:"twitter_handler"`
  UserName       string `json:"user_name"`
  ImgURL         string `json:"img_url"`  // this could be tweet imge as income or presign url as outcome msg
}

func (e *Engine) builder() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  var err error
  rawDir := path.Join(baseDir, "raw")  //raw images downloaded from S3
  tilesDir := path.Join(baseDir, "tiles") // tiles location to store generated tiles images by metapixel
  sourceDir := path.Join(baseDir, "source") // location to store the original pic to be processed to mosaic
  mosaicsDir := path.Join(baseDir, "mosaics") // location to store the new generated mosaic image
  thumbnailsDir := path.Join(baseDir, "thumbnails") // location to store the thumnails for to display it on the website

  consumerTag := "engine"

  log.Printf("Creating tiles into\n")
  if err = e.createTiles(); err != nil {
    log.Printf("Error creating tiles: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Printf("Starting queue consumer (consumer tag %q)", consumerTag)
  deliveries, err := e.channel.Consume(
    e.config.QueueInName, // name
    consumerTag,        // consumerTag,
    false,              // noAck
    false,              // exclusive
    false,              // noLocal
    false,              // noWait
    nil,                // arguments
  )
  if err != nil {
    log.Printf("Queue Consume Error: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Println("Starting builder goroutine")
  for {
    select {
    case d := <-deliveries:

      var m Message
      err := json.Unmarshal(d, &m)
      if err != nil {
        return err
      }

      e.config.mosaicFileName,err = e.downloadSource(m.ImgURL,sourceDir)
      if err != nil {
        return err
      }
      log.Printf("Building mosaic...\n")
      if err := e.buildMosaic(d.Body); err != nil {
        log.Printf("Error parsing message to JSON: %s\n", err)
        continue
      }

      if err := e.buildMosaic(d.Body); err != nil {
        log.Printf("Error parsing message to JSON: %s\n", err)
        continue
      }

      //TODO: Send message to uploader
      go e.uploader(m)

      d.Ack(true)

    case <-e.stopchan:
      log.Println("Stop signal received. Returning...")
      // will close() the deliveries channel
      if err := e.channel.Cancel(consumerTag, true); err != nil {
        log.Printf("Consumer cancel failed: %s\n", err)
        return
      }

      if err := e.amqpConn.Close(); err != nil {
        log.Printf("AMQP connection close error: %s\n", err)
        return
      }

      return
    }
  }
}

func (e *Engine) createTiles() error {
  cmd := "metapixel-prepare"
  args := []string{rawDir, tilesDir, "--width=32", "--height=32"}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}

func (e *Engine) downloadSource(sourceUrl string, downloadPath string)  ( string, error) {
  // Create the file
  out, err := os.Create(downloadPath)
  if err != nil {
    return err
  }
  defer out.Close()

  // Get the data
  resp, err := http.Get(sourceUrl)
  if err != nil {
    return err
  }
  defer resp.Body.Close()

  // Writer the body to file
  _, err = io.Copy(out, resp.Body)
  if err != nil {
    return err
  }
  //return file name
  return out.Name()
}

func (e *Engine) buildMosaic(sourcePath, mosaicPath, tilesDir string) error {
  cmd = "metapixel"
  args = []string{"--metapixel", sourcePath, mosaicPath, "--library", tilesDir, "--scale=10", "--distance=5"}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}

func (e *Engine) createThumbnail(mosaicPath, thumbnailPath string) error {
  cmd = "convert"
  args = []string{"-thumbnail", "400", mosaicPath, thumbnailPath}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}
