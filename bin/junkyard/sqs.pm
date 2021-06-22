sub get_configuration_file {
my $noofqueues = 2;
my @queue = ('regular','debug');
my @maxqu = (1,1);
my @maxperuser = (1,1);
my @quhost = ('arrows','arrows');
my @pool = (0,0);
my @web = (0,0);
my $sqsdir = "/srv/arrows/.sqs";
my $bindir = "/srv/arrows/bin";
my $mandir = "/srv/arrows/man";
my $noremote = 0;
my @remotealias;
my @remotehosts;
my %hostpath;
my $wait = 2;
my @psexe = ('ps','ps');
my @psflag = ('-U','-U');
my $webhost = '';
my $webuser = '';
my $webserver = '';
# do not alter this line
#
# You can easily alter this file and just reinstall it with
# './install.pl sqs.pm'. 
#
# Obviously you must take care in making changes and you will have to
# stop and then restart qseek for the changes to take effect. 
#
# You can not alter the directory names, but you can add queues, remove
# queues (with great care), alter #maxqu and $maxperuser, add remote
# hosts and probably everything else.

return ($noofqueues, $noremote, $wait, $sqsdir, $bindir, $mandir, 
  \@queue, \@maxqu, \@maxperuser, \@quhost, \@pool, \@web,
  \@remotealias, \@remotehosts, \@psexe, \@psflag,
  \%hostpath,$webhost,$webuser,$webserver);
}
1;

