use warnings;
use strict;
use LWP::Simple;
$ENV{'PERL_LWP_SSL_VERIFY_HOSTNAME'} = 0;
use Time::Progress;

# Download PubMed records that are indexed in MeSH for query entry.

my $mesh = $ARGV[0];
my $outfile = $ARGV[1];
my $db = 'pubmed';
my $query = $mesh;

#assemble the esearch URL
my $base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/';
my $url = $base . "esearch.fcgi?db=$db&term=$query&usehistory=y";

#post the esearch URL
my $output = get($url);

#parse WebEnv, QueryKey and Count
my $web = $1 if ($output =~ /<WebEnv>(\S+)<\/WebEnv>/);
my $key = $1 if ($output =~ /<QueryKey>(\d+)<\/QueryKey>/);
my $count = $1 if ($output =~ /(\d+)<\/Count>/);

#open output file for writing
open OUT, '>', $outfile || die "Can't open file!\n";
binmode(OUT, ":utf8"); # this is to process wide characters

#initiate the progress bar
$| = 1;
my $p = new Time::Progress;
$p->attr( min => 0, max => $count );

#retrieve data in batches of 500
my $retmax = 500;
for (my $retstart = 0; $retstart < $count; $retstart += $retmax) {
	
	my $efetch_url = $base . "efetch.fcgi?db=$db&WebEnv=$web";
	$efetch_url .= "&query_key=$key&retstart=$retstart";
	$efetch_url .= "&retmax=$retmax&rettype=abstract&retmode=xml";
	my $efetch_out = get($efetch_url);
	
	print $p->report("%45b %p\r", $retstart);

print OUT "$efetch_out";
}
close OUT;
