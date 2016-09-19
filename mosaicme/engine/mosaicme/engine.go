package mosaicme

import (
  "fmt"
  "log"
  "os"
  "path"
  "sync"

  minio "github.com/minio/minio-go"
  "github.com/streadway/amqp"
)

const (
  // directory to store the new generated mosaic image
  mosaicsDir = "mosaics"
  // directory to store raw images downloaded from object store
  rawDir = "raw"
  // directory to store tiles generated from raw images by metapixel to build mosaics
  tilesDir = "tiles"
  // directory to store the original images to be processed
  sourceDir = "source"
  // direcoty to store the thumbnails to display it on the website
  thumbnailsDir = "thumbnails"
)

type Config struct {
  QueueIn        string
  QueueOut       string
  BucketIn       string
  BucketOut      string
  BaseDir        string `env:"MOSAICME_BASEDIR" envDefault:"/tmp/mosaicme"`
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

type Message struct {
  TwitterHandler string `json:"twitter_handler"`
  UserName       string `json:"user_name"`
  ImgURL         string `json:"img_url"`
  MosaicName     string
  MosaicPath     string
  ThumbnailPath  string
}

type Engine struct {
  config       *Config
  wg           *sync.WaitGroup
  stopchan     chan bool
  amqpConn     *amqp.Connection
  channel      *amqp.Channel
  uploaderChan chan *Message
  s3Client     *minio.Client
}

func NewEngine(config *Config) (*Engine, error) {
  var err error

  e := &Engine{
    wg:           &sync.WaitGroup{},
    stopchan:     make(chan bool),
    amqpConn:     nil,
    channel:      nil,
    config:       config,
    uploaderChan: make(chan *Message),
    s3Client:     nil,
  }

  if err = e.createDirs(); err != nil {
    return nil, err
  }

  if err = e.initQueues(); err != nil {
    return nil, err
  }

  if err = e.initObjectStorage(); err != nil {
    return nil, err
  }

  return e, nil
}

func (e *Engine) createDirs() error {
  var err error
  dirs := [5]string{mosaicsDir, rawDir, tilesDir, sourceDir, thumbnailsDir}
  for _, dir := range dirs {
    newPath := path.Join(e.config.BaseDir, dir)
    err = os.MkdirAll(newPath, os.ModePerm)
    if err != nil {
      return err
    }
  }
  return nil
}

func (e *Engine) initQueues() error {
  var err error

  keyIn := "engine-in-key"
  keyOut := "engine-out-key"
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

  log.Printf("declared Exchange, declaring Queue-In %q", e.config.QueueIn)
  queue, err := e.channel.QueueDeclare(
    e.config.QueueIn, // name of the queue
    true,             // durable
    false,            // delete when usused
    false,            // exclusive
    false,            // noWait
    nil,              // arguments
  )
  if err != nil {
    return fmt.Errorf("Queue-in Declare: %s", err)
  }

  log.Printf("declared Queue-In (%q %d messages, %d consumers), binding to Exchange (key %q)",
    e.config.QueueIn, queue.Messages, queue.Consumers, keyIn)

  //Bind Queue-in with Exchange
  if err = e.channel.QueueBind(
    e.config.QueueIn, // name of the queue
    keyIn,            // bindingKey
    exchange,         // sourceExchange
    false,            // noWait
    nil,              // arguments
  ); err != nil {
    return fmt.Errorf("Queue Bind: %s", err)
  }
  log.Printf("declared Exchange, declaring Queue-Out %q", e.config.QueueOut)
  queue2, err := e.channel.QueueDeclare(
    e.config.QueueOut, // name of the queue
    true,              // durable
    false,             // delete when usused
    false,             // exclusive
    false,             // noWait
    nil,               // arguments
  )
  if err != nil {
    return fmt.Errorf("Queue-Out Declare: %s", err)
  }

  log.Printf("declared Queue-Out (%q %d messages, %d consumers), binding to Exchange (key %q)",
    e.config.QueueOut, queue2.Messages, queue2.Consumers, keyOut)

  //Bind Queue-out with Exchange
  if err = e.channel.QueueBind(
    e.config.QueueOut, // name of the queue
    keyOut,            // bindingKey
    exchange,          // sourceExchange
    false,             // noWait
    nil,               // arguments
  ); err != nil {
    return fmt.Errorf("Queue Bind: %s", err)
  }
  return nil
}

func (e *Engine) initObjectStorage() error {

  log.Println("Initializing object storage client...")

  endpoint := e.config.S3Host + ":" + e.config.S3Port
  client, err := minio.New(endpoint, e.config.S3AccessKey, e.config.S3SecrectKey, e.config.S3Https)
  if err != nil {
    return err
  }
  e.s3Client = client

  err = e.createBucket(e.config.BucketIn)
  if err != nil {
    return err
  }

  err = e.createBucket(e.config.BucketOut)
  if err != nil {
    return err
  }

  log.Println("Object storage initialized successfully")
  return nil
}

func (e *Engine) createBucket(bucketName string) error {
  exists, err := e.s3Client.BucketExists(bucketName)
  if err != nil {
    return err
  }
  if exists {
    return nil
  }

  err = e.s3Client.MakeBucket(bucketName, "us-east-1")
  if err != nil {
    return err
  }
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
