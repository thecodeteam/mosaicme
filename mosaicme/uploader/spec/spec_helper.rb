require 'bunny'
require 'json'

connection = Bunny.new
connection.start

channel = connection.create_channel

queue = channel.queue 'uploader', durable: true

json = { img_url: 'http://abc.com' }.to_json
queue.publish json

connection.close
