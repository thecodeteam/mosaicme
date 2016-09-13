package main

import (
  "app/mosaicme"
  "flag"
  "fmt"
  "log"
  "os"
  "os/signal"
  "syscall"

  "github.com/caarlos0/env"
)

var (
  cfg = mosaicme.Config{
    QueueName:  *flag.String("queue", "engine", "Queue name"),
    BucketName: *flag.String("bucket", "mosaics", "Bucket name"),
  }
)

func init() {
  flag.Parse()
  err := env.Parse(&cfg)

  if err != nil {
    fmt.Printf("%+v\n", err)
    os.Exit(1)
  }
  fmt.Printf("Config: %+v\n", cfg)
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
  log.Println("Received interruption...")
  log.Println("Waiting for goroutines to exit...")
  engine.Stop()
  log.Println("Exiting...")
  os.Exit(0)
}
