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
  ImgURL         string `json:"img_url"`
}

func (e *Engine) builder() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  var err error
  rawDir := path.Join(baseDir, "raw")
  tilesDir := path.Join(baseDir, "tiles")
  sourceDir := path.Join(baseDir, "source")
  mosaicsDir := path.Join(baseDir, "mosaics")
  thumbnailsDir := path.Join(baseDir, "thumbnails")
  consumerTag := "engine"

  log.Printf("Creating tiles into\n")
  if err = e.createTiles(); err != nil {
    log.Printf("Error creating tiles: %s\n", err)
    close(e.stopchan)
    return
  }

  log.Printf("Starting queue consumer (consumer tag %q)", consumerTag)
  deliveries, err := e.channel.Consume(
    e.config.QueueName, // name
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

      e.downloadSource(m.ImgURL)

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
      time.Sleep(2000 * time.Millisecond)

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
