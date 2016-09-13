require 'sneakers'
require 'sneakers/runner'
require 'json'
require 'aws-sdk'
require 'open-uri'

module Uploader

  class UploaderWorker
    include Sneakers::Worker
    from_queue Uploader.queue

    def work(message)
      logger.debug "[MESSAGE] #{message}"
      data = JSON.parse(message)
      if data.key?('img_url')
        upload(data['img_url'])
      end
      ack!
    end

    private

    def upload(img_url)
      logger.info "Uploading image '#{img_url}' to bucket '#{Uploader.bucket}'"

      begin
        Uploader.s3_client.head_bucket({bucket: Uploader.bucket})
      rescue Aws::S3::Errors::NotFound
        logger.debug 'Bucket does not exist. Creating it...'
        Uploader.s3_client.create_bucket({bucket: Uploader.bucket})
      end

      Uploader.s3_client.put_object({bucket: Uploader.bucket, key: File.basename(img_url), body: open(img_url)})
      logger.debug 'Image uploaded'
    end
  end
end
