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

  "github.com/dchest/uniuri"
)

func (e *Engine) builder() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  var err error
  rawDir := path.Join(e.config.BaseDir, "raw")               //raw images downloaded from S3
  tilesDir := path.Join(e.config.BaseDir, "tiles")           // tiles location to store generated tiles images by metapixel
  sourceDir := path.Join(e.config.BaseDir, "source")         // location to store the original pic to be processed to mosaic
  mosaicsDir := path.Join(e.config.BaseDir, "mosaics")       // location to store the new generated mosaic image
  thumbnailsDir := path.Join(e.config.BaseDir, "thumbnails") // location to store the thumnails for to display it on the website
  consumerTag := "engine"

  log.Printf("Creating tiles into\n")
  if err = e.createTiles(rawDir, tilesDir); err != nil {
    log.Printf("Error creating tiles: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Printf("Starting queue consumer (consumer tag %q)", consumerTag)
  deliveries, err := e.channel.Consume(
    e.config.QueueIn, // name
    consumerTag,      // consumerTag,
    false,            // noAck
    false,            // exclusive
    false,            // noLocal
    false,            // noWait
    nil,              // arguments
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

      log.Printf("Got message: %s\n", string(d.Body))

      var m Message

      err := json.Unmarshal(d.Body, &m)
      if err != nil {
        log.Printf("Error parsing JSON: %s\n", err)
        continue
      }

      mosaicName := uniuri.New() + "jpg"
      sourcePath := path.Join(sourceDir, mosaicName)

      err = e.downloadSource(m.ImgURL, sourcePath)
      if err != nil {
        log.Printf("Error downloading source image: %s\n", err)
        continue
      }

      mosaicPath := path.Join(mosaicsDir, mosaicName)

      if err := e.buildMosaic(sourcePath, mosaicPath, tilesDir); err != nil {
        log.Printf("Error building mosaic: %s\n", err)
        continue
      }

      thumbnailPath := path.Join(thumbnailsDir, mosaicName)

      if err := e.createThumbnail(mosaicPath, thumbnailPath); err != nil {
        log.Printf("Error creating thumbnail: %s\n", err)
        continue
      }

      m.MosaicName = mosaicName
      m.MosaicPath = mosaicPath
      m.ThumbnailPath = thumbnailPath

      // Send message to uploader goroutine
      e.uploaderChan <- &m

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

func (e *Engine) createTiles(rawPath, tilesPath string) error {
  cmd := "metapixel-prepare"
  args := []string{rawPath, tilesPath, "--width=32", "--height=32"}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}

func (e *Engine) downloadSource(sourceUrl, downloadPath string) error {
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

  return nil
}

func (e *Engine) buildMosaic(sourcePath, mosaicPath, tilesDir string) error {
  cmd := "metapixel"
  args := []string{"--metapixel", sourcePath, mosaicPath, "--library", tilesDir, "--scale=10", "--distance=5"}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}

func (e *Engine) createThumbnail(mosaicPath, thumbnailPath string) error {
  cmd := "convert"
  args := []string{"-thumbnail", "400", mosaicPath, thumbnailPath}
  if err := exec.Command(cmd, args...).Run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    return err
  }
  return nil
}
