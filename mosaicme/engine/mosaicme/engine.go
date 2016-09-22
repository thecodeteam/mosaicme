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

// Config contains the configuration information for the Engine struct
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

// Message contains the information to be sent to the next service in the pipeline
type Message struct {
  TwitterHandler string `json:"twitter_handler"`
  UserName       string `json:"user_name"`
  ImgURL         string `json:"img_url"`
  MosaicName     string
  MosaicPath     string
  ThumbnailPath  string
}

// Engine contains the information needed to work
type Engine struct {
  config       *Config
  wg           *sync.WaitGroup
  stopchan     chan bool
  amqpConn     *amqp.Connection
  channel      *amqp.Channel
  uploaderChan chan *Message
  s3Client     *minio.Client
}

// NewEngine initializes an instance of an Engine struct
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

  log.Println("[Init] Creating temporary directories")
  if err = e.createDirs(); err != nil {
    log.Printf("[Init] Error creating temporary directories: %s\n", err)
    return nil, err
  }
  log.Println("[Init] Temporary directories created")

  log.Println("[Init] Initializing message broker")
  if err = e.initQueues(); err != nil {
    log.Printf("[Init] Error initializing message broker: %s\n", err)
    return nil, err
  }
  log.Println("[Init] Message broker initialized")

  log.Println("[Init] Initializing object storage backend")
  if err = e.initObjectStorage(); err != nil {
    log.Printf("[Init] Error initializing object storage backend: %s\n", err)
    return nil, err
  }
  log.Println("[Init] Object storage backend initialized")

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

  amqpURI := fmt.Sprintf("amqp://%s:%s@%s:%s",
    e.config.RabbitUser, e.config.RabbitPassword,
    e.config.RabbitHost, e.config.RabbitPort)

  log.Println("[Init] Connecting to AMQP broker")
  e.amqpConn, err = amqp.Dial(amqpURI)
  if err != nil {
    return fmt.Errorf("Dial: %s", err)
  }

  go func() {
    fmt.Printf("closing: %s", <-e.amqpConn.NotifyClose(make(chan *amqp.Error)))
  }()

  log.Println("[Init] Got AMQP connection, getting channel")
  e.channel, err = e.amqpConn.Channel()
  if err != nil {
    return fmt.Errorf("Error getting channel: %s", err)
  }

  log.Printf("[Init] Declaring queue-in %q", e.config.QueueIn)
  queueIn, err := e.channel.QueueDeclare(
    e.config.QueueIn, // name of the queue
    true,             // durable
    false,            // delete when usused
    false,            // exclusive
    false,            // noWait
    nil,              // arguments
  )
  if err != nil {
    return fmt.Errorf("Error declaring queue-in %q: %s", e.config.QueueIn, err)
  }

  log.Printf("[Init] Declared queue-in (%q %d messages, %d consumers)\n",
    e.config.QueueIn, queueIn.Messages, queueIn.Consumers)

  log.Printf("[Init] Declaring queue-out %q", e.config.QueueOut)
  queueOut, err := e.channel.QueueDeclare(
    e.config.QueueOut, // name of the queue
    true,              // durable
    false,             // delete when usused
    false,             // exclusive
    false,             // noWait
    nil,               // arguments
  )
  if err != nil {
    return fmt.Errorf("Error declaring queue-out %q: %s", e.config.QueueOut, err)
  }

  log.Printf("[Init] Declared queue-out (%q %d messages, %d consumers)\n",
    e.config.QueueOut, queueOut.Messages, queueOut.Consumers)

  return nil
}

func (e *Engine) initObjectStorage() error {

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

// Start starts the engine
func (e *Engine) Start() error {
  // go e.download()
  go e.builder()
  go e.uploader()

  return nil
}

// Stop stops the engine
func (e *Engine) Stop() error {
  close(e.stopchan)
  e.wg.Wait()
  return nil
}
