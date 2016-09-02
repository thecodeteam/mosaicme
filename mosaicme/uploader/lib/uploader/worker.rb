require 'sneakers'
require 'sneakers/runner'
require 'json'
require 'aws-sdk'
require 'open-uri'

class UploaderWorker
  include Sneakers::Worker
  from_queue ENV['LISTEN_QUEUE']

  def work(message)
    logger.info "[MESSAGE] #{message}"
    data = JSON.parse(message)
    if data.key?('img_url')
      upload(data['img_url'])
    end
    ack!
  end

  private

  def upload(img_url)
    logger.info "Uploading img url: #{img_url}"

    s3 = Aws::S3::Client.new(
        :access_key_id => ENV['S3_ACCESS_KEY'],
        :secret_access_key => ENV['S3_SECRET_KEY'],
        :region => 'local',
        :endpoint => "http://#{ENV['S3_HOST']}:#{ENV['S3_PORT']}/",
        :force_path_style => true)

    begin
      s3.head_bucket({bucket: ENV['UPLOAD_BUCKET']})
    rescue Aws::S3::Errors::NotFound
      puts 'Bucket does not exist. Creating it...'
      s3.create_bucket({bucket: ENV['UPLOAD_BUCKET']})
    end

    s3.put_object({bucket: ENV['UPLOAD_BUCKET'], key: File.basename(img_url), body: open(img_url)})
  end
end
