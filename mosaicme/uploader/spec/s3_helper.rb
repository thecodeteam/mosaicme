require 'aws-sdk'
require 'open-uri'

path = File.expand_path(__FILE__)
puts "Path: #{path}"

s3 = Aws::S3::Client.new(
    :access_key_id => 'YOUR_ACCESS_KEY_ID',
    :secret_access_key => 'YOUR_SECRET_ACCESS_KEY',
    :region => 'local',
    :endpoint => 'http://localhost:4569/',
    :force_path_style => true)


begin
  s3.head_bucket({bucket: "mosaicme-raw"})
rescue Aws::S3::Errors::NotFound
  puts 'Bucket does not exist. Creating it...'
  s3.create_bucket({bucket: "mosaicme-raw"})
end

s3.put_object({bucket: "mosaicme-raw", key: __FILE__, body: open(path)})

objects = s3.list_objects({bucket: "mosaicme-raw"})

puts objects.contents.map(&:key)
