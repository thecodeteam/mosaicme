require 'uploader/version'
require 'sneakers'
require 'sneakers/runner'
require 'aws-sdk'
require 'logger'


module Uploader

  def self.queue
    @@queue
  end

  def self.bucket
    @@bucket
  end

  def self.s3_client
    @@s3
  end

  def self.start(queue:, bucket:)
    mandatory = ['RABBITMQ_HOST', 'RABBITMQ_PORT', 'RABBITMQ_USER', 'RABBITMQ_PASSWORD', 'S3_ACCESS_KEY', 'S3_SECRET_KEY', 'S3_REGION', 'S3_HOST', 'S3_PORT', 'S3_HTTPS']
    missing = mandatory.select{ |param| ENV[param].nil? }
    unless missing.empty?
      raise ArgumentError.new("Missing the following environment variables: #{missing.join(', ')}")
    end

    @@queue = queue
    @@bucket = bucket

    Sneakers.configure(
      amqp: "amqp://#{ENV['RABBITMQ_USER']}:#{ENV['RABBITMQ_PASSWORD']}@#{ENV['RABBITMQ_HOST']}:#{ENV['RABBITMQ_PORT']}",
      daemonize: false,
      log: STDOUT,
      workers: 1,
      timeout_job_after: 60,
      threads: 10,
    )

    Sneakers.logger.level = Logger::INFO

    protocol = (ENV['S3_HTTPS'] == '1' || ENV['S3_HTTPS'].downcase == 'true')? 'https' : 'http'

    @@s3 = Aws::S3::Client.new(
        :access_key_id => ENV['S3_ACCESS_KEY'],
        :secret_access_key => ENV['S3_SECRET_KEY'],
        :region => ENV['S3_REGION'],
        :endpoint => "#{protocol}://#{ENV['S3_HOST']}:#{ENV['S3_PORT']}/",
        :force_path_style => true)

    require 'uploader/worker'

    puts "Uploader starting. Listen queue: #{@@queue}. Upload bucket: #{@@bucket}"

    r = Sneakers::Runner.new([ Uploader::UploaderWorker ])
    r.run
  end
end
