#! /usr/local/perl/bin/perl

chomp($ARGV[0]);
if($ARGV[0] eq "NEWPTSDY1")
{
	$shorttype = "DY1";
	$prod_name = "Day1_Conv_Outlook";
}

@hazards = ("TORNADO","HAIL","WIND","CATEGORICAL");

%torhash = ("0.02" => "02\%", 
	    "0.05" => "05\%",
            "0.10" => "10\%",
            "0.15" => "15\%",
            "0.30" => "30\%",
            "0.45" => "45\%",
            "0.60" => "60\%",
            "SIGN" => "SIGNIFICANT",
);

%windhailhash = ("0.05" => "05\%",
                 "0.15" => "15\%",
                 "0.30" => "30\%",
                 "0.45" => "45\%",
                 "0.60" => "60\%",
                 "SIGN" => "SIGNIFICANT",
);

%cathash = ("HIGH" => "HIGH", 
	    "MDT"  => "MODERATE",
            "SLGT" => "SLIGHT",
            "TSTM" => "GENERAL",
);

%shpline = ();

@found = ();

system("textdb -r $ARGV[0] > /data/local/scripts/severe/products/$ARGV[0]");

$PRODUCT = "/data/local/scripts/severe/products/$ARGV[0]";

open OUT2, ">/data/local/scripts/severe/products/$ARGV[0].txt";

$end_of_year = 0;
open PRODUCT, "< $PRODUCT" or die "PRODUCT file cannot be read"; 
while(<PRODUCT>)
{
	if((/T SUN /) || (/T MON /) || (/T TUE /) || (/T WED /) || (/T THU /) || (/T FRI /) || (/T SAT /))
	{
		@dateline = split/\s+/, $_;
		$dateline[4] =~ s/JAN/01/;
		$dateline[4] =~ s/FEB/02/;
		$dateline[4] =~ s/MAR/03/;
		$dateline[4] =~ s/APR/04/;
		$dateline[4] =~ s/MAY/05/;
		$dateline[4] =~ s/JUN/06/;
		$dateline[4] =~ s/JUL/07/;
		$dateline[4] =~ s/AUG/08/;
		$dateline[4] =~ s/SEP/09/;
		$dateline[4] =~ s/OCT/10/;
		$dateline[4] =~ s/NOV/11/;
		$dateline[4] =~ s/DEC/12/;
		#$day = "$dateline[6]"."$dateline[4]"."$dateline[5]";
		$year = $dateline[6];
		if(($dateline[4] == 12)&&($dateline[5] == 31))
		{
			$end_of_year = 1;
		}
	}
	if(/VALID TIME/)
	{
		@readline = split/\s+/, $_;
		$valid_until = $readline[4];
		$issued = $readline[2];
		$valid_from = $issued;
		@issueline = split//, $issued;
		$hour = "$issueline[2]"."$issueline[3]"."$issueline[4]"."$issueline[5]";
		if($hour <= 5){$year = ($year + 1);}
		$issue_day = "$issueline[0]"."$issueline[1]";
		if(($issue_day eq "01")&&($dateline[4] eq "01")){$dateline[4] = "02";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "02")){$dateline[4] = "03";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "03")){$dateline[4] = "04";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "04")){$dateline[4] = "05";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "05")){$dateline[4] = "06";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "06")){$dateline[4] = "07";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "07")){$dateline[4] = "08";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "08")){$dateline[4] = "09";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "09")){$dateline[4] = "10";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "10")){$dateline[4] = "11";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "11")){$dateline[4] = "12";}
		elsif(($issue_day eq "01")&&($dateline[4] eq "12")){$dateline[4] = "01";}
		$day = "$year"."$dateline[4]"."$issue_day";
		print OUT2 "$issued $valid_from $valid_until $prod_name $day"."_"."$hour"."Z\n";
	}
}
close PRODUCT;

system("cp /data/local/scripts/severe/products/$ARGV[0] /data/local/scripts/severe/products/$ARGV[0].$day.$issued");

$label = "";
$current_name = "";

for($j=0;$j<($#hazards+1);$j++)
{
	open PRODUCT, "< $PRODUCT" or die "PRODUCT file cannot be read"; 
	while(<PRODUCT>)
	{
		if(/\.\.\. $hazards[$j]/)
		{
			$basename = "$hazards[$j]_";
			$linecount = 1;
			while(<PRODUCT>)
			{
				@readline = split/\s+/, $_;				
				if($readline[1] ne "")
                                {
					if($readline[0] ne "")
                                        {
						$oldlabel = $label;
						$label = $readline[0];$linecount=1;
						$old_name = $current_name;
					}
					else
					{
						$linecount++;
					}
					$current_name = "$hazards[$j]_$label";										
				        if($hazards[$j] eq "TORNADO")
					{
						$name = "$basename"."$torhash{$label}"; 
					}
					elsif($hazards[$j] eq "CATEGORICAL")
					{
						$name = "$basename"."$cathash{$label}"; 
					}
					else
					{
						$name = "$basename"."$windhailhash{$label}";
					}
					if(($old_name eq $current_name)&&($linecount==1))
					{
						$shpline{$name} .= "99999999";						
					}
					if($linecount==1)
					{
						$initial{$name} = $readline[1];
						if($hazards[$j] ne "CATEGORICAL")
						{
							push (@found, $name);
						}
					}
					$i = 1;
					for (@readline)
					{
						if($readline[$i] ne "")
						{					
							if($readline[$i] ne "99999999")
							{							
								($lat[$i],$lon[$i]) = readlatlon($readline[$i]);
								if($linecount==1)
								{
									$initial1{$name} = "$lon[1] $lat[1]";									
								}
								$shpline{$name} .= "$lon[$i] $lat[$i] ";
								$final{$name} = $readline[$i];
								$i++;
							}
							else
							{
								$shpline{$name} .= "99999999";
								$i++;
							}
						}
					}	
				}			
				if(/\&\&/)
				{
					last;
				}
			}
			last;
		}
	}
	close PRODUCT;							
}

foreach $m (@found)
{
	push(@temp_array, $m) unless ($seen{$m}++);	
}
@found = @temp_array;

if($found[0] eq "")
{
	print OUT2 "NONE\n";
}
else
{
	for $n (@found)
	{	
		$name = $n;
		print OUT2 "$name 1 $shpline{$name}\n";	
	}
	if($shpline{CATEGORICAL_GENERAL} ne "")
	{
		print OUT2 "CATEGORICAL_GENERAL 1 $shpline{CATEGORICAL_GENERAL}\n";	
	}
	if($shpline{CATEGORICAL_SLIGHT} ne "")
	{
		print OUT2 "CATEGORICAL_SLIGHT 1 $shpline{CATEGORICAL_SLIGHT}\n";	
	}
	if($shpline{CATEGORICAL_MODERATE} ne "")
	{
		print OUT2 "CATEGORICAL_MODERATE 1 $shpline{CATEGORICAL_MODERATE}\n";	
	}
	if($shpline{CATEGORICAL_HIGH} ne "")
	{
		print OUT2 "CATEGORICAL_HIGH 1 $shpline{CATEGORICAL_HIGH}\n";	
	}
}

close OUT2;

sub readlatlon
{
	my ($number) = @_;
	@varline = split//, $number;
	$lt = "$varline[0]$varline[1]"."."."$varline[2]$varline[3]";
        if($varline[4] <= 2)
	{
		$ln = "-1"."$varline[4]$varline[5]"."."."$varline[6]$varline[7]";
	}	
	else
	{
		$ln = "-"."$varline[4]$varline[5]"."."."$varline[6]$varline[7]";
	}
	return ($lt,$ln);
}

exit;
