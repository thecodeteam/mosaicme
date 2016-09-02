require 'sneakers'
require 'sneakers/runner'

class UploaderWorker
  include Sneakers::Worker
  from_queue ENV['LISTEN_QUEUE']

  def work(message)
    logger.info "[MESSAGE] #{message}"
    ack!
  end
end
