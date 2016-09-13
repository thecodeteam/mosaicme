package mosaicme

import (
  "encoding/json"
  "log"
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

  consumerTag := "engine"

  log.Printf("Queue bound to Exchange, starting Consume (consumer tag %q)", consumerTag)
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
      log.Printf(
        "got %dB delivery: [%v] %q",
        len(d.Body),
        d.DeliveryTag,
        d.Body,
      )

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

func (e *Engine) buildMosaic(data []byte) error {
  var m Message
  err := json.Unmarshal(data, &m)
  if err != nil {
    return err
  }
  log.Printf("Message: %+v\n", m)

  //TODO: build mosaic with metapixel
  return nil
}
