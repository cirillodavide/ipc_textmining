use warnings;
use strict;
use Data::Dumper;

my %dict;
open FILE, "src/MRCONSO.RRF" or die $!;
while(<FILE>){
	chomp;
	next unless $_=~ m/\|ENG\|.*\|MSH\|/g;
	my @words = split /\|/, $_;
	push @{$dict{"MESH:".$words[13]}},"\"".$words[14]."\"";
}
close FILE;

open FILE, '>', 'src/MESH_MRCONSO.tsv' or die $!;
print FILE join("\t","MESH","term","synonyms"),"\n";
for my $mesh (keys %dict){
	print FILE join("\t",$mesh,${$dict{$mesh}}[0],join("|",@{$dict{$mesh}})),"\n";
}
close FILE;