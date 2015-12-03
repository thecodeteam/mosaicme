Exec { path => [ '/bin/', '/sbin/' , '/usr/bin/', '/usr/sbin/' ] }

include apt

package { ['python-software-properties']:
  ensure  => 'installed',
  require => Class['apt'],
}

$sysPackages = ['git', 'curl', 'metapixel', 'supervisor']
package { $sysPackages:
  ensure  => 'installed',
  require => Class['apt'],
}

class { 'python' :
  version  => 'system',
  pip      => 'present',
  dev      => 'present',
  gunicorn => 'present',
}

python::requirements { '/tmp/requirements.txt': }

class { 'java':
  distribution => 'jre',
}

class { '::rabbitmq':
  port => '5672',
}

include redis
