require 'bunny'
require 'json'

connection = Bunny.new
connection.start

channel = connection.create_channel

queue = channel.queue 'uploader', durable: true

json = { img_url: 'http://kingofwallpapers.com/coche/coche-002.jpg' }.to_json
queue.publish json

connection.close
