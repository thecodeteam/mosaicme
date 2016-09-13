package mosaicme

import (
  "log"
  "time"
)

func (e *Engine) uploader() {
  e.wg.Add(1)
  defer func() {
    e.wg.Done()
  }()

  log.Println("Starting uploader goroutine")
  for {
    select {
    default:
      log.Println("2")
      time.Sleep(10000 * time.Millisecond)
    case <-e.stopchan:
      log.Println("Stop signal received. Returning...")
      return
    }
  }
}
