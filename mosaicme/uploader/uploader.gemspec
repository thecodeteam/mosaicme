# coding: utf-8
lib = File.expand_path('../lib', __FILE__)
$LOAD_PATH.unshift(lib) unless $LOAD_PATH.include?(lib)
require "uploader/version"

Gem::Specification.new do |s|
  s.name           = 'uploader'
  s.version        = Uploader::VERSION
  s.date           = '2016-09-06'
  s.summary        = %q{MosaicMe Uploader service}
  s.description    = %q{Receives images from a RabbitMQ queue and uploades them to a S3-compatible bucket}
  s.authors        = ["Adrian Moreno"]
  s.email          = 'adrian.moreno@emc.com'
  s.files          = `git ls-files`.split($/)
  s.executables    = s.files.grep(/^bin/).map { |f| File.basename(f) }
  s.require_paths  = ["lib"]
  s.homepage       = 'https://github.com/codedellemc/mosaicme'
  s.license        = 'MIT'
  s.add_dependency 'sneakers', '~>2.3'
  s.add_dependency 'bunny', '~>2.2'
  s.add_dependency 'aws-sdk', '~>2.5'
end
