package mosaicme

import (
  "fmt"
  "log"
  "sync"

  "github.com/streadway/amqp"
)

const (
  baseDir = "/tmp/mosaicme"
)

type Config struct {
  QueueName      string
  BucketName     string
  BucketRawName  string
  EngineDir      string
  RabbitHost     string `env:"RABBITMQ_HOST,required"`
  RabbitPort     string `env:"RABBITMQ_PORT,required"`
  RabbitUser     string `env:"RABBITMQ_USER,required"`
  RabbitPassword string `env:"RABBITMQ_PASSWORD,required"`
  S3Host         string `env:"S3_HOST,required"`
  S3Port         string `env:"S3_PORT,required"`
  S3Https        bool   `env:"S3_HTTPS,required"`
  S3AccessKey    string `env:"S3_ACCESS_KEY,required"`
  S3SecrectKey   string `env:"S3_SECRET_KEY,required"`
}

type Engine struct {
  config   *Config
  wg       *sync.WaitGroup
  stopchan chan bool
  amqpConn *amqp.Connection
  channel  *amqp.Channel
}

func NewEngine(config *Config) (*Engine, error) {
  var err error

  e := &Engine{
    wg:       &sync.WaitGroup{},
    stopchan: make(chan bool),
    amqpConn: nil,
    channel:  nil,
    config:   config,
  }

  if err = e.initQueue(); err != nil {
    return nil, err
  }

  if err = e.initObjectStorage(); err != nil {
    return nil, err
  }

  return e, nil
}

func (e *Engine) initQueue() error {
  key := "test-key"
  exchange := "mosaicme"
  amqpURI := fmt.Sprintf("amqp://%s:%s@%s:%s",
    e.config.RabbitUser, e.config.RabbitPassword,
    e.config.RabbitHost, e.config.RabbitPort)

  e.amqpConn, err = amqp.Dial(amqpURI)
  if err != nil {
    return fmt.Errorf("Dial: %s", err)
  }

  go func() {
    fmt.Printf("closing: %s", <-e.amqpConn.NotifyClose(make(chan *amqp.Error)))
  }()

  log.Printf("got Connection, getting Channel")
  e.channel, err = e.amqpConn.Channel()
  if err != nil {
    return fmt.Errorf("Channel: %s", err)
  }

  log.Printf("got Channel, declaring Exchange (%q)", exchange)
  if err = e.channel.ExchangeDeclare(
    exchange, // name of the exchange
    "direct", // type
    true,     // durable
    false,    // delete when complete
    false,    // internal
    false,    // noWait
    nil,      // arguments
  ); err != nil {
    return fmt.Errorf("Exchange Declare: %s", err)
  }

  log.Printf("declared Exchange, declaring Queue %q", e.config.QueueName)
  queue, err := e.channel.QueueDeclare(
    e.config.QueueName, // name of the queue
    true,               // durable
    false,              // delete when usused
    false,              // exclusive
    false,              // noWait
    nil,                // arguments
  )
  if err != nil {
    return fmt.Errorf("Queue Declare: %s", err)
  }

  log.Printf("declared Queue (%q %d messages, %d consumers), binding to Exchange (key %q)",
    e.config.QueueName, queue.Messages, queue.Consumers, key)

  if err = e.channel.QueueBind(
    e.config.QueueName, // name of the queue
    key,                // bindingKey
    exchange,           // sourceExchange
    false,              // noWait
    nil,                // arguments
  ); err != nil {
    return fmt.Errorf("Queue Bind: %s", err)
  }
  return nil
}

func (e *Engine) initObjectStorage() error {
  //TODO: Initilize S3 client here
  return nil
}

func (e *Engine) Start() error {
  // go e.download()
  go e.builder()
  go e.uploader()
  return nil
}

func (e *Engine) Stop() error {
  close(e.stopchan)
  e.wg.Wait()
  return nil
}
