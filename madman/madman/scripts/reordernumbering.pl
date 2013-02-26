#!/usr/bin/perl
#TKR
use DBI;
use POSIX qw(strftime);
use Term::ANSIColor qw(:constants);

require "/etc/mediamanagement.conf"; #this file has to contain the following variables


$dbh = DBI->connect("DBI:mysql:$db:$host", $user, $pass);
my @do;
my @users;
$test = 0;
$help = 0;

foreach my $arg (@ARGV){
  if( $arg =~ /^--test$/i ){$test = 1;} #this runs as normal but does not actually move/copy anything or add to the db
  if( $arg =~ /^--help$/i ){$help = 1;} #displays all flags
  if( $arg =~ /^-h$/i ){$help = 1;} #displays all flags
}

$directory = @ARGV[-1];

if($help){
  print "--test -> this runs as normal but does not actually move/copy anything or add to the db.\n";
  print "--h, --help -> displays all flags.\n";
  exit(0);
}

if($directory eq ""){
  print "No directory specified. Quitting.\n";
  exit(0);
}

print "How many digits are being used in the current file (usually 1,2,3)?\n";
$digits  = <STDIN>;
chomp $digits;

print "What should the new filename start with?\n";
$startNum  = <STDIN>;
chomp $startNum;

if($test){
  print "You are in test mode\n";
}

my @files  = `ls -A "$directory"`;
my @do;
foreach(@files){
  if (!(-d "$_")) {
    $_ =~ s/\n//g;
    
    $num = sprintf("%2d", $startNum);

    $num =~ tr/ /0/;

    $stripped = substr $_, $digits;
    $reordered = "$num$stripped";
    
    
    push(@do, [$_, $reordered]);
    $startNum++;
  }
}


if(@do > 0){
  print "Path: $directory\n";
  foreach (@do){   
    printf "|%-40s -> %-40s|\n", $_->[0], $_->[1];
  }
  if(@do > 0){
    print "Proceed (y/n)?";
    $proceed  = <STDIN>;
    chomp $proceed;
    if($proceed eq "y"){
      foreach(@do){
        $command = "mv \"$directory$_->[0]\" \"$directory$_->[1]\"";
        if($test){
          print $command."\n";
        }else{
          system($command);
        }
      }
    }else{
      print "Quitting\n";
    }
  }
}


exit(0);
