Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/" ] }

exec { 'apt-get update':
  command => 'apt-get update',
  timeout => 60,
  tries   => 3
}

class { 'apt':
  always_apt_update => true,
}

package { ['python-software-properties']:
  ensure  => 'installed',
  require => Exec['apt-get update'],
}

$sysPackages = ['git', 'curl']
package { $sysPackages:
  ensure => "installed",
  require => Exec['apt-get update'],
}

class { 'python' :
    version    => 'system',
    pip        => true,
    dev        => true,
    gunicorn   => true,
  }

python::requirements { '/tmp/requirements.txt': }

include redis