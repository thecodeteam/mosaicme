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

  log.Printf("[Builder] Creating tiles into\n")
  if err = e.createTiles(rawDir, tilesDir); err != nil {
    log.Printf("[Builder] Error creating tiles: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Printf("[Builder] Initializing input queue '%s'\n", e.config.QueueIn)
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
    log.Printf("[Builder] Queue Consume Error: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Println("[Builder] Starting goroutine")

  for {
    select {
    case d := <-deliveries:

      mosaicName := uniuri.New() + ".jpg"

      log.Printf("[Builder] %s - Got message: %s\n", mosaicName, string(d.Body))

      var m Message

      log.Printf("[Builder] %s - Parsing message\n", mosaicName)

      err := json.Unmarshal(d.Body, &m)
      if err != nil {
        log.Printf("[Builder] %s - Error parsing JSON: %s\n", m.MosaicName, err)
        continue
      }

      m.MosaicName = mosaicName
      m.MosaicPath = path.Join(mosaicsDir, mosaicName)
      m.ThumbnailPath = path.Join(thumbnailsDir, mosaicName)
      sourcePath := path.Join(sourceDir, m.MosaicName)

      log.Printf("[Builder] %s - Downloading source image from URL: %s\n", m.MosaicName, m.ImgURL)

      err = e.downloadSource(m.ImgURL, sourcePath)
      if err != nil {
        log.Printf("[Builder] %s - Error downloading source image: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Builder] %s - Downloaded source image\n", m.MosaicName)
      log.Printf("[Builder] %s - Building mosaic\n", m.MosaicName)

      if err := e.buildMosaic(sourcePath, m.MosaicPath, tilesDir); err != nil {
        log.Printf("[Builder] %s - Error building mosaic: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Builder] %s - Mosaic built\n", m.MosaicName)
      log.Printf("[Builder] %s - Creating thumbnail\n", m.MosaicName)

      if err := e.createThumbnail(m.MosaicPath, m.ThumbnailPath); err != nil {
        log.Printf("[Builder] %s - Error creating thumbnail: %s\n", m.MosaicName, err)
        continue
      }

      log.Printf("[Builder] %s - Created thumbnail\n", m.MosaicName)
      log.Printf("[Builder] %s - Sending message to Uploader goroutine\n", m.MosaicName)

      e.uploaderChan <- &m

      log.Printf("[Builder] %s - Message sent to Uploader goroutine\n", m.MosaicName)

      d.Ack(true)

    case <-e.stopchan:
      log.Println("[Builder] Stop signal received. Returning...")
      // will close() the deliveries channel
      if err := e.channel.Cancel(consumerTag, true); err != nil {
        log.Printf("[Builder] Consumer cancel failed: %s\n", err)
        return
      }

      if err := e.amqpConn.Close(); err != nil {
        log.Printf("[Builder] AMQP connection close error: %s\n", err)
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
