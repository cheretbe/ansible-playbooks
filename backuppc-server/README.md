Testing
```shell
cd tools/vagrant/docker-tests/; vagrant up; finished
vagrant ssh -- 'cd /ansible-playbooks/backuppc-server; inv test'
```

Check if specific version upgrades to the latest version
```shell
# Check out version on an existing installation
grep "# Version" /usr/local/BackupPC/bin/BackupPC | cut -d"," -f1 | cut -d " " -f3
perl -e 'use lib "/usr/local/BackupPC/lib"; use BackupPC::XS; print $BackupPC::XS::VERSION . "\n"'
/usr/local/bin/rsync_bpc --version 2>&1 | head -n 1

# Run upgrade test in testing VM
inv test-upgrade-from-version 4.3.1 0.59 3.1.2.1
```
