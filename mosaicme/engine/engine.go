package main

import (
  "flag"
  "fmt"
  "log"
  "mosaicme"
  "os"
  "os/signal"
  "syscall"

  "github.com/caarlos0/env"
)

var (
  cfg = mosaicme.Config{
    QueueIn:   *flag.String("queue-in", "engine", "Input queue to receive jobs"),
    QueueOut:  *flag.String("queue-out", "publisher", "Output queue"),
    BucketIn:  *flag.String("bucket-in", "mosaicme-raw", "Bucket for raw images"), //optional
    BucketOut: *flag.String("bucket-out", "mosaicme-out", "Bucket for mosaics"),
  }
)

func init() {
  flag.Parse()
  err := env.Parse(&cfg)

  if err != nil {
    fmt.Printf("%+v\n", err)
    os.Exit(1)
  }
}

func main() {
  engine, err := mosaicme.NewEngine(&cfg)
  if err != nil {
    fmt.Printf("%+v\n", err)
    os.Exit(1)
  }

  engine.Start()

  c := make(chan os.Signal, 1)
  signal.Notify(c, os.Interrupt, syscall.SIGTERM)
  <-c
  log.Println("[Main] Received interruption...")
  log.Println("[Main] Waiting for goroutines to exit...")
  engine.Stop()
  log.Println("[Main] Exiting...")
  os.Exit(0)
}
