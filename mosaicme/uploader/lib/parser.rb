require 'optparse'

Options = Struct.new(:queue, :bucket)

class Parser
  def self.parse(options)
    args = Options.new

    opt_parser = OptionParser.new do |opts|
      opts.banner = "Usage: uploader.rb [options]"

      opts.on("-q", "--queue=NAME", "RabbitMQ queue name") do |q|
        args.queue = q
      end

      opts.on("-b", "--bucket=NAME", "Object store bucket where the image will be uploaded") do |b|
        args.bucket = b
      end

      opts.on("-h", "--help", "Prints this help") do
        puts opts
        exit
      end
    end

    opt_parser.parse!(options)
    if args.queue.nil? or args.bucket.nil?
      puts 'Missing required argument'
      exit
    end

    return args
  end
end
