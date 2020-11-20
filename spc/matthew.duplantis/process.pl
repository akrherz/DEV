#! /usr/local/perl/bin/perl

use constant epsilon => 1e-14;

chomp($ARGV[0]);

$directory = "/data/local/scripts/severe";

%shpline = ();

@uslon="";
@uslat="";
@uspoly="";
@segments="";

$US = "$directory/config/us_shapefile_points_with_marine.txt";
$PRODUCT = "$directory/products/$ARGV[0].txt";

$total=1;
$value=0;
open US, "< $US" or die "$US file cannot be read"; 
while(<US>)
{
	chomp $_;	
	@readline = split/,/, $_;
	$uslonval = $readline[0]; $uslonval =~ s/\s+//;
	$uslatval = $readline[1]; $uslatval =~ s/\s+//;
	push(@uslon,$uslonval);
	push(@uslat,$uslatval);
	$uspoly[$value] = $uslonval;
	$value++;
	$uspoly[$value] = $uslatval;
	$value++;
	$total++;
}
close US;

$countline1 = 0; $nothing = 0;
open PRODUCT, "< $PRODUCT" or die "$PRODUCT file cannot be read";
while(<PRODUCT>)
{
	@prodline = split/\s+/, $_;
	$name = $prodline[0];
	if($countline1 == 0)
	{
		$issued = $prodline[0];
		$valid_from = $prodline[1];
		$valid_until = $prodline[2];
		$prod_name = $prodline[3];
		$timeline = $prodline[4];
		$base_prod_name = $prod_name;
		$prod_name = "$prod_name" . "_$timeline";
	}
	if($countline1 != 0)
	{
		if($name ne "NONE")
		{
			push(@theorder,$name);
		}
		else
		{
			$nothing = 1;
			last;
		}
	}
	$countline1++;
}
close PRODUCT;

if($nothing != 1)
{
	$countline = 0;
	open PRODUCT, "< $PRODUCT" or die "$PRODUCT file cannot be read";
	while(<PRODUCT>)
	{
		chomp($_);
	
		if($countline == 0)
		{
 			@prodline = split/\s+/, $_;
			$issued = $prodline[0];
			$valid_from = $prodline[1];
			$valid_until = $prodline[2];
			$prod_name = $prodline[3];
			$timeline = $prodline[4];
			$base_prod_name = $prod_name;
			$prod_name = "$prod_name" . "_$timeline";
			$_ = <PRODUCT>;
		}

		$points = $_;	
		@prodline = split/\s+/, $_;
		$name = $prodline[0];
	        @nameline = split/_/,$name;
		$subname = $nameline[0];
		$index = $prodline[1];	
		$size = $#prodline;

		push(@names,$name);
		push(@subnames,$subname);

		$points =~ s/^$name $index //;

		@subline = split/99999999/, $points;
		$sublinesize = ($#subline+1);
	
		$sizeof{$name} = $sublinesize;
        	$polygon_count = 0; $start_num = 0; $finish_num = 0; $initial_range_1 = 0; $initial_range_2 = 0; $segment_count = 0; $diff = 0;
		
		for($j=1;$j<=$sublinesize;$j++)
		{
			for($k=($j+1);$k<=$sublinesize;$k++)
			{
				if($subline[$j-1] == $subline[$k-1])
				{
					splice(@subline, ($k-1), 1);
				}
			}
		}

		for($j=1;$j<=$sublinesize;$j++)
		{
	          @subpoint = split/\s+/,$subline[$j-1];
		  $subpointsize = $#subpoint;
		  ($init_x0, $init_y0) = ($subpoint[0],$subpoint[1]);
		  ($init_x1, $init_y1) = ($subpoint[2],$subpoint[3]);
        	  $poly_check_x0 = $init_x0;
		  $poly_check_y0 = $init_y0;

		  ($init_x4, $init_y4) = ($subpoint[$subpointsize-3],$subpoint[$subpointsize-2]);
		  ($init_x5, $init_y5) = ($subpoint[$subpointsize-1],$subpoint[$subpointsize]);
        	  $poly_check_x1 = $init_x5;
        	  $poly_check_y1 = $init_y5;
        	  $poly_check{$name}[$j] = 1;

		  $start_error = 0; $finish_error = 0; $add_plus[$j] = 0;

		  if(($poly_check_x0 != $poly_check_x1)&&($poly_check_y0 != $poly_check_y1))
		  {
		    $segment_count++;
        	    $poly_check{$name}[$j] = 0;
        	    $test_x0y0 = point_in_polygon($init_x0,$init_y0,@uspoly);
        	    $test_x1y1 = point_in_polygon($init_x1,$init_y1,@uspoly);
        	    $test_x4y4 = point_in_polygon($init_x4,$init_y4,@uspoly);
        	    $test_x5y5 = point_in_polygon($init_x5,$init_y5,@uspoly);
	    
	    
		    if(($test_x0y0==0)&&($test_x1y1==0)&&($subpointsize>3))
        	    {
			$start_str_to_replace = "$subpoint[0] $subpoint[1] $subpoint[2] $subpoint[3]";
			for($a=1;$test_x1y1==0;$a++)
			{
				($init_x0, $init_y0) = ($subpoint[$a*2],$subpoint[($a*2)+1]);		
				($init_x1, $init_y1) = ($subpoint[($a*2)+2],$subpoint[($a*2)+3]);          
        	    		$test_x1y1 = point_in_polygon($init_x1,$init_y1,@uspoly);
				if($test_x1y1==0)
				{
					$start_str_to_replace .= " $subpoint[($a*2)+2] $subpoint[($a*2)+3]";
				}
				if($a==100){last;}
			}
			($start_x,$start_y,$start_num) = test_segment($init_x0,$init_y0,$init_x1,$init_y1);
			$start_error = 1;		
	            }
		    elsif(($test_x0y0==0)&&($test_x1y1==1))
		    {
		    	($start_x,$start_y,$start_num) = test_segment($init_x0,$init_y0,$init_x1,$init_y1);
		    }
        	    elsif(($test_x0y0==1)&&($test_x1y1==1))
		    {
			($new_start_x,$new_start_y) = slope_out($init_x0,$init_y0,$init_x1,$init_y1);
			($start_x,$start_y,$start_num) = test_segment($new_start_x,$new_start_y,$init_x0,$init_y0);
        	    }
		    else
		    {
			($start_x,$start_y,$start_num) = reverse_test_segment($init_x0,$init_y0,$init_x1,$init_y1);
			$dist1 = distance($start_x,$start_y,$init_x0,$init_y0);
			$dist2 = distance($start_x,$start_y,$init_x1,$init_y1);
			if($dist2 < $dist1)
			{
				($start_x,$start_y,$start_num) = test_segment($init_x0,$init_y0,$init_x1,$init_y1);
			}
		    }
            
		    $start_x = sprintf "%.3f",$start_x; $start_y = sprintf "%.3f",$start_y;
		    $start_x{$name}[$j] = $start_x; $start_y{$name}[$j] = $start_y;
		    $start_num{$name}[$j] = $start_num;
		    $start_x{$name}[$start_num] = $start_x; $start_y{$name}[$start_num] = $start_y;
	    	 
	            if(($test_x4y4==0)&&($test_x5y5==0)&&($subpointsize>3))
        	    {
			$finish_str_to_replace = "$subpoint[$subpointsize-3] $subpoint[$subpointsize-2] $subpoint[$subpointsize-1] $subpoint[$subpointsize]";
			for($b=1;$test_x4y4==0;$b++)
			{
				($init_x5, $init_y5) = ($subpoint[$subpointsize-(($b*2)+1)],$subpoint[$subpointsize-($b*2)]);		
				($init_x4, $init_y4) = ($subpoint[$subpointsize-(($b*2)+3)],$subpoint[$subpointsize-(($b*2)+2)]);          
        	    		$test_x4y4 = point_in_polygon($init_x4,$init_y4,@uspoly);
				if($test_x4y4==0)
				{
					$finish_str_to_replace = "$subpoint[$subpointsize-(($b*2)+3)] $subpoint[$subpointsize-(($b*2)+2)] " . "$finish_str_to_replace";
				}
				if($b==100){last;}
			}
			($finish_x,$finish_y,$finish_num) = test_segment($init_x4,$init_y4,$init_x5,$init_y5);
			$finish_error = 1;		
        	    }
		    elsif(($test_x5y5==0)&&($test_x4y4==1))
		    {
		    	($finish_x,$finish_y,$finish_num) = test_segment($init_x4,$init_y4,$init_x5,$init_y5);
		    }
        	    elsif(($test_x5y5==1)&&($test_x4y4==1))
		    {
			($finish_x,$finish_y,$finish_num) = test_segment($init_x4,$init_y4,$init_x5,$init_y5);
			if(($finish_x == "")&&($finish_y == ""))
        	        {
				($new_finish_x,$new_finish_y) = slope_out($init_x5,$init_y5,$init_x4,$init_y4);
				($finish_x,$finish_y,$finish_num) = test_segment($new_finish_x,$new_finish_y,$init_x5,$init_y5);
			}		
            	    }
	    	    else
	    	    {
			($finish_x,$finish_y,$finish_num) = test_segment($init_x4,$init_y4,$init_x5,$init_y5);
			$dist3 = distance($finish_x,$finish_y,$init_x4,$init_y4);
			$dist4 = distance($finish_x,$finish_y,$init_x5,$init_y5);
			if($dist3 < $dist4)
			{
				($finish_x,$finish_y,$finish_num) = reverse_test_segment($init_x4,$init_y4,$init_x5,$init_y5);
			}
                    }
   
		    $finish_x = sprintf "%.3f",$finish_x; $finish_y = sprintf "%.3f",$finish_y;		 
		    $finish_x{$name}[$j] = $finish_x; $finish_y{$name}[$j] = $finish_y;
		    $finish_num{$name}[$j] = $finish_num;

		    $finish_x{$name}[$finish_num] = $finish_x; $finish_y{$name}[$finish_num] = $finish_y;
		    $finishing{$name}[$start_num] = $finish_num;            
            
	            if($start_error==1)
            	    {
	    		$subline[$j-1] =~ s/$start_str_to_replace/$start_x $start_y/;
	            }
	    	    else
            	    {
			$subline[$j-1] =~ s/$subpoint[0] $subpoint[1]/$start_x $start_y/;
            	    }
            	    if($finish_error==1)
            	    {
			$subline[$j-1] =~ s/$finish_str_to_replace/$finish_x $finish_y/;
            	    }
            	    else
            	    {
 	        	$subline[$j-1] =~ s/$subpoint[$subpointsize-1] $subpoint[$subpointsize]/$finish_x $finish_y/;
            	    }
	    	    $subline[$j-1] =~ s/\n//;
	    	    $subline{$name}[$start_num] = $subline[$j-1];	    
	          }          
          	  if($poly_check{$name}[$j]==1)
          	  {
            		$subpointsize = ($#subpoint+1);
		        $limit = ($subpointsize/2);
	    		$poly_total = 0; $poly_counter{$name}[$j]=0; $poly_counter_x{$name}[$j]=""; $poly_counter_y{$name}[$j]="";

	   		for($h=0;$h<$limit;$h++)
	    		{
				$p1=($h*2);$p2=(($h*2)+1);$p3=(($h*2)+2);$p4=(($h*2)+3);$p5=(($h*2)+4);$p6=(($h*2)+5);
				if($p1>=$subpointsize){$p1=($p1-$subpointsize);}
				if($p2>=$subpointsize){$p2=($p2-$subpointsize);}
				if($p3>=$subpointsize){$p3=($p3-$subpointsize);}
				if($p4>=$subpointsize){$p4=($p4-$subpointsize);}
				if($p5>=$subpointsize){$p5=($p5-$subpointsize);}
				if($p6>=$subpointsize){$p6=($p6-$subpointsize);}
				($poly_x0, $poly_y0) = ($subpoint[$p1],$subpoint[$p2]);
	        		($poly_x1, $poly_y1) = ($subpoint[$p3],$subpoint[$p4]);
	    			($poly_x2, $poly_y2) = ($subpoint[$p5],$subpoint[$p6]);
				$poly_clockwise = clockwise($poly_x0,$poly_y0,$poly_x1,$poly_y1,$poly_x2,$poly_y2);		
				$poly_total = ($poly_total + $poly_clockwise);		
	    		}
	    		if($poly_total<0){$poly_counter{$name}[$j]=1;$poly_counter_x{$name}[$j]=$poly_x0;$poly_counter_y{$name}[$j]=$poly_y0;}# print "$name BECOMES j=$j poly_counter=$poly_counter{$name}[$j]\n";}
	    		$subline[$j-1] =~ s/\n//;
            		$segment_count=0;            
          	  }
                } 
	        $v = 0; $w = 0; @new_subline=""; @unsorted=""; $new_seg_count = 0;
        	for($j=1;$j<=$sublinesize;$j++)
        	{
			if($poly_check{$name}[$j]==1)
			{
				$v++;
				$new_subline[$v] = $subline[$j-1];
				if($poly_counter{$name}[$j]==1)
				{
					$poly_counter{$name}[$v]=1;
					$poly_counter_x{$name}[$v]=$poly_counter_x{$name}[$j];
					$poly_counter_y{$name}[$v]=$poly_counter_y{$name}[$j];	
					if($j>$v)
					{
						$poly_counter{$name}[$j]=0; $poly_counter_x{$name}[$j]=""; $poly_counter_y{$name}[$j]="";
					}			
				}	
			}
			else
			{
				$new_seg_count++;
				$w++;
				$unsorted[$w] = $start_num{$name}[$j];
				$new_start_num{$name}[$new_seg_count] = $start_num{$name}[$j];
				$w++;
				$unsorted[$w] = $finish_num{$name}[$j];
				$new_finish_num{$name}[$new_seg_count] = $finish_num{$name}[$j];
				if(($start_num{$name}[$j]=="") && ($finish_num{$name}[$j]==""))
				{
					$w=($w-2);
					$new_seg_count=($new_seg_count-1);
				}
			}
		}	
		@sorted="";@beginning_sorted="";
		if($w!=0)
		{
			@sorted = sort {$a <=> $b} @unsorted;
			for($j=1;$j<=$new_seg_count;$j++)
        		{
				for($k=1;$k<=$#sorted;$k++)
		        	{
					if($sorted[$k] == $new_start_num{$name}[$j])
						{
						$beginning_sorted[$j] = $k;
					}
					if($sorted[$k] == $new_finish_num{$name}[$j])
					{
						$ending_sorted[$j] = $k;
						$val_of_end[$sorted[$k]]=$k;
						}
				}
				$start_and_end[$beginning_sorted[$j]] = $val_of_end[$finishing{$name}[$sorted[$beginning_sorted[$j]]]];
			}
			for($h=1;$h<($#uslat+1);$h++)
			{		
				$start_done[$sorted[$h]] = 0;
			}
			for($j=1;($j<=($w/2));$j++)
        		{
				if($start_done[$sorted[$beginning_sorted[$j]]]!=1)
				{
					$beginning = $beginning_sorted[$j];
					$ending = $ending_sorted[$j];
					$v++;
					$new_subline[$v] = $subline{$name}[$sorted[$beginning]];
					$start_done[$sorted[$beginning]] = 1;
					$new_beginning=0;
					while($ending!=$new_beginning)
					{
						$new_beginning = ($ending+1);
						if($new_beginning>=($#sorted+1))
						{
							$new_beginning = ($new_beginning-$#sorted);
						}
						if($new_beginning!=$beginning)
						{
							$returned_line = get_array_of_us_points($finish_x{$name}[$sorted[$ending]], $finish_y{$name}[$sorted[$ending]], $start_x{$name}[$sorted[$new_beginning]], $start_y{$name}[$sorted[$new_beginning]]);
							$new_subline[$v] .= $returned_line;
							$new_subline[$v] .= $subline{$name}[$sorted[$new_beginning]];
							$start_done[$sorted[$new_beginning]] = 1;
							$ending = $start_and_end[$new_beginning];
						}
							else
						{
							$returned_line = get_array_of_us_points($finish_x{$name}[$sorted[$ending]], $finish_y{$name}[$sorted[$ending]], $start_x{$name}[$sorted[$beginning]], $start_y{$name}[$sorted[$beginning]]);
							$new_subline[$v] .= $returned_line;
							$start_done[$sorted[$beginning]] = 1;
							last;
						}
					}
				}
			}
		}
		$kml_count=1;
		for($t=1;$t<=($#new_subline+1);$t++)
        	{
			if($poly_counter{$name}[$t]==1)
			{
				for($u=1;$u<=($#new_subline+1);$u++)
        			{
					if($t!=$u)
					{
						@poly_to_test = split/\s+/,$new_subline[$u];
						$return_val=point_in_polygon($poly_counter_x{$name}[$t],$poly_counter_y{$name}[$t],@poly_to_test);
						if($return_val==1)
						{
							$kml_outer{$name}[$u]=$new_subline[$u];
							$kml_inner{$name}[$u]=$new_subline[$t];
						}
					}
				}
			}
			else
			{
				$kml_outer{$name}[$t]=$new_subline[$t];
			}
			$kmlcount{$name}=$kml_count;
			$kml_count++;
		}
		for($v=1;$v<=$#new_subline;$v++)
        	{
			if($v!=1)
			{
				if($new_subline[$v] != "")
				{			
					$shpline{$name}[1] .= "+ $new_subline[$v]";
				}
			}
			else
			{
				$shpline{$name}[1] .= $new_subline[$v];
			}
		}	
		$countline++;
	}
	close PRODUCT;

	foreach $m (@names)
	{
		push(@temp_array, $m) unless ($seen{$m}++);	
	}
	@names = @temp_array;

	foreach $n (@subnames)
	{
		push(@temp_array1, $n) unless ($seen{$n}++);	
	}
	@subnames = @temp_array1;

	create_shp_new();
	create_kml();

}
else
{
	create_nothing_shp();
	create_nothing_kml();
}

time_on_images();
send_to_web();
scour_dir();

exit;

sub send_to_web
{
	system("ssh ldad\@ls1 /data/ldad/web/bin/ldad_html_update.sh");
}

sub time_on_images
{
	if($ARGV[0] eq "NEWPTSDY1")
	{
		system("convert images/Day1_Template.png -font Courier -pointsize 12 -draw \"fill white stroke white stroke-width 1 text 10,40 'ISSUED AT $timeline'\" images/Day1_Conv_Outlook.png");
		system("scp images/Day1_Conv_Outlook.png ldad\@ls1:/data/ldad/web/images");
	}
	if($ARGV[0] eq "NEWPTSDY2")
	{
		system("convert images/Day2_Template.png -font Courier -pointsize 12 -draw \"fill white stroke white stroke-width 1 text 9,147 'ISSUED AT $timeline'\" images/Day2_Conv_Outlook.png");
		system("scp images/Day2_Conv_Outlook.png ldad\@ls1:/data/ldad/web/images");
	}
	if($ARGV[0] eq "NEWPTSDY3")
	{
		system("convert images/Day3_Template.png -font Courier -pointsize 12 -draw \"fill white stroke white stroke-width 1 text 9,147 'ISSUED AT $timeline'\" images/Day3_Conv_Outlook.png");
		system("scp images/Day3_Conv_Outlook.png ldad\@ls1:/data/ldad/web/images");
	}
	if($ARGV[0] eq "NEWPTSD48")
	{
		system("convert images/Day4-8_Template.png -font Courier -pointsize 12 -draw \"fill white stroke white stroke-width 1 text 9,247 'ISSUED AT $timeline'\" images/Day4-8_Conv_Outlook.png");
		system("scp images/Day4-8_Conv_Outlook.png ldad\@ls1:/data/ldad/web/images");
	}
}

sub scour_dir
{
	system("rm $directory/shp/$base_prod_name/$base_prod_name*");
}

sub create_kml
{
	if($ARGV[0] eq "NEWPTSDY1")
	{
		%kmlhash = ("TORNADO_02%" => "0", 
			    "TORNADO_05%" => "1000",
		            "TORNADO_10%" => "2000",
		            "TORNADO_15%" => "3000",
        		    "TORNADO_30%" => "4000",
		            "TORNADO_45%" => "5000",
        		    "TORNADO_60%" => "6000",
        		    "TORNADO_SIGNIFICANT" => "7000",
			    "HAIL_05%" => "0", 
			    "HAIL_15%" => "1000",
        		    "HAIL_30%" => "2000",
		            "HAIL_45%" => "3000",
        		    "HAIL_60%" => "4000",
        		    "HAIL_SIGNIFICANT" => "5000",
			    "WIND_05%" => "0", 
			    "WIND_15%" => "1000",
        		    "WIND_30%" => "2000",
		            "WIND_45%" => "3000",
        		    "WIND_60%" => "4000",
        		    "WIND_SIGNIFICANT" => "5000",
			    "CATEGORICAL_GENERAL" => "0", 
			    "CATEGORICAL_SLIGHT" => "1000",
        		    "CATEGORICAL_MODERATE" => "2000",
		            "CATEGORICAL_HIGH" => "3000",
		);
		%kmlcolorhash = ("TORNADO_02%" => "7feded00", 
			         "TORNADO_05%" => "7fff0000",
      	        	         "TORNADO_10%" => "7f00cc00",
	                	 "TORNADO_15%" => "7f007f00",
	        	         "TORNADO_30%" => "7f00eded",
        	 	         "TORNADO_45%" => "7f0178ff",
        		         "TORNADO_60%" => "7f0000eb",
        	        	 "TORNADO_SIGNIFICANT" => "7fed20d8",
			         "HAIL_05%" => "7fff0000", 
			         "HAIL_15%" => "7f007f00",
        		         "HAIL_30%" => "7f00eded",
	                	 "HAIL_45%" => "7f0178ff",
	        	         "HAIL_60%" => "7f0000eb",
        		         "HAIL_SIGNIFICANT" => "7fed20d8",
			         "WIND_05%" => "7fff0000", 
		        	 "WIND_15%" => "7f007f00",
	        	         "WIND_30%" => "7f00eded",
		                 "WIND_45%" => "7f0178ff",
        		         "WIND_60%" => "7f0000eb",
        	        	 "WIND_SIGNIFICANT" => "7fed20d8",
			         "CATEGORICAL_GENERAL" => "7f007f00", 
			         "CATEGORICAL_SLIGHT" => "7f00eded",
        		         "CATEGORICAL_MODERATE" => "7f0000eb",
	                	 "CATEGORICAL_HIGH" => "7fed20d8",
		);
	}
	if(($ARGV[0] eq "NEWPTSDY2")||($ARGV[0] eq "NEWPTSDY3"))
	{
		%kmlhash = ("ANY-SEVERE_05%" => "0", 
			    "ANY-SEVERE_15%" => "1000",
		            "ANY-SEVERE_30%" => "2000",
		            "ANY-SEVERE_45%" => "3000",
        		    "ANY-SEVERE_60%" => "4000",
		            "ANY-SEVERE_SIGNIFICANT" => "5000",		            
			    "CATEGORICAL_GENERAL" => "0", 
			    "CATEGORICAL_SLIGHT" => "1000",
        		    "CATEGORICAL_MODERATE" => "2000",
		            "CATEGORICAL_HIGH" => "3000",
		);
		%kmlcolorhash = ("ANY-SEVERE_05%" => "7fff0000", 
			         "ANY-SEVERE_15%" => "7f007f00",
      	        	         "ANY-SEVERE_30%" => "7f00eded",
	                	 "ANY-SEVERE_45%" => "7f0178ff",
	        	         "ANY-SEVERE_60%" => "7f0000eb",
        	 	         "ANY-SEVERE_SIGNIFICANT" => "7fed20d8",
        		         "CATEGORICAL_GENERAL" => "7f007f00", 
			         "CATEGORICAL_SLIGHT" => "7f00eded",
        		         "CATEGORICAL_MODERATE" => "7f0000eb",
	                	 "CATEGORICAL_HIGH" => "7fed20d8",
		);
	}
	if($ARGV[0] eq "NEWPTSD48")
	{
		%kmlhash = ("ANY-SEVERE_DAY4" => "0", 
			    "ANY-SEVERE_DAY5" => "1000",
		            "ANY-SEVERE_DAY6" => "2000",
		            "ANY-SEVERE_DAY7" => "3000",
        		    "ANY-SEVERE_DAY8" => "4000",
		);
		%kmlcolorhash = ("ANY-SEVERE_DAY4" => "7f0000eb", 
			         "ANY-SEVERE_DAY5" => "7f8f0f98",
      	        	         "ANY-SEVERE_DAY6" => "7f007f00",
	                	 "ANY-SEVERE_DAY7" => "7fff0000",
	        	         "ANY-SEVERE_DAY8" => "7f08355a",
		);
	}
	
	$KMLFILE = "$directory/shp/$base_prod_name/$prod_name.kml\n";
	open KMLFILE, "> $KMLFILE" or die "$KMLFILE file cannot be overwritten\n";
	print KMLFILE "<\?xml version=\"1.0\" encoding=\"UTF-8\"\?>\n";
	print KMLFILE "<kml xmlns=\"http://earth.google.com/kml/2.2\">\n";
	print KMLFILE "<Document>\n";
	print KMLFILE "<name>$prod_name</name>\n";
	print KMLFILE "  <description>\n";
	print KMLFILE "	   <![CDATA[$prod_name KML file written by:<br>\n";
        print KMLFILE "      Matthew Duplantis - Information Technology Officer<br>\n";
	print KMLFILE "	     National Weather Service - Shreveport, LA<br>]]>\n";
        print KMLFILE "  </description>\n";
 	print KMLFILE "  <open>1</open>\n";	
	print KMLFILE "  <ScreenOverlay>\n";
	print KMLFILE "    <name>Product Legend</name>\n";
	print KMLFILE "    <description>\n";
	print KMLFILE "      <![CDATA[<table border=0 width=\"250\"><tr><td>\n";
        print KMLFILE "      SPC's $base_prod_name.</td></tr></table>]]>\n";
	print KMLFILE "    </description>\n";
	print KMLFILE "    <visibility>1</visibility>\n";
	print KMLFILE "    <Icon>\n";
	print KMLFILE "      <href>http://www.srh.noaa.gov/images/shv/$base_prod_name.png</href>\n";
	print KMLFILE "    </Icon>\n";
	print KMLFILE "    <overlayXY x=\".02\" y=\".01\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <screenXY x=\".02\" y=\".01\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <rotationXY x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <size x=\"-1\" y=\"-1\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "  </ScreenOverlay>\n";
	for($l=0;$l<($#subnames+1);$l++)
	{
		for($k=0;$k<($#names+1);$k++)
		{
			if($names[$k] =~ /$subnames[$l]/)
			{
				$name = $names[$k];
				$color = $kmlcolorhash{$name};	
				print KMLFILE "	<Style id=\"$name\">\n";
				print KMLFILE "			<LineStyle>\n";
				print KMLFILE "			<width>6</width>\n";
				print KMLFILE "                 </LineStyle>\n";
				print KMLFILE "		<PolyStyle>\n";
				print KMLFILE "			<color>$kmlcolorhash{$name}</color>\n";
				print KMLFILE "		</PolyStyle>\n";
				print KMLFILE " </Style>\n";
			}
		}
	}	
	for($l=0;$l<($#subnames+1);$l++)
	{
		for($k=0;$k<($#names+1);$k++)
		{
			if($k==0)
			{
				print KMLFILE "<Folder>\n";
				print KMLFILE "<name>$subnames[$l]</name>\n";
				print KMLFILE "<open>1</open>\n";								
			}
			if($names[$k] =~ /$subnames[$l]/)
			{
				$name = $names[$k];
				$height = $kmlhash{$name};	
				print KMLFILE "	<Placemark>\n";
				print KMLFILE "         <visibility>1</visibility>\n";
				print KMLFILE "		<name>$name</name>\n";
				print KMLFILE "		<styleUrl>\#"."$name"."</styleUrl>\n";
				print KMLFILE "         <MultiGeometry>\n";
				for($i=1;$i<($kmlcount{$name}+1);$i++)
				{
					if($kml_outer{$name}[$i]!="")
					{
						print KMLFILE "		<Polygon>\n";	
						print KMLFILE "			<outerBoundaryIs>\n";
						print KMLFILE "				<LinearRing>\n";
						print KMLFILE "					<coordinates>\n";				
						@coords = split/\s+/,$kml_outer{$name}[$i];
						for($j=0;$j<($#coords+1);$j++)
						{
							$altkey = $j+1;
							if($coords[$j]<0)
							{
								print KMLFILE "$coords[$j], ";
							}
							else
							{
								print KMLFILE "$coords[$j], $height ";
							}
							if((($altkey % 7) == 0)&&($altkey != 0))
							{
								print KMLFILE "\n";
							}
						}
						print KMLFILE "					</coordinates>\n";
						print KMLFILE "				</LinearRing>\n";
						print KMLFILE "			</outerBoundaryIs>\n";
					}
					if($kml_inner{$name}[$i]!="")
					{
						print KMLFILE "			<innerBoundaryIs>\n";
						print KMLFILE "				<LinearRing>\n";
						print KMLFILE "					<coordinates>\n";				
						@coords1 = split/\s+/,$kml_inner{$name}[$i];
						for($j1=0;$j1<($#coords1+1);$j1++)
						{
							$altkey1 = $j1+1;
							if($coords1[$j1]<0)
							{
								print KMLFILE "$coords1[$j1], ";
							}
							else
							{
								print KMLFILE "$coords1[$j1], $height ";
							}
							if((($altkey1 % 7) == 0)&&($altkey1 != 0))
					 		{
								print KMLFILE "\n";
							}
						}
						print KMLFILE "					</coordinates>\n";
						print KMLFILE "				</LinearRing>\n";
						print KMLFILE "			</innerBoundaryIs>\n";
					}
					if($kml_outer{$name}[$i]!="")
					{
						print KMLFILE "		</Polygon>\n";
					}					
				}				
				print KMLFILE " </MultiGeometry>\n";
				print KMLFILE "	</Placemark>\n";							
			}
			if($k==$#names)
			{
				print KMLFILE "</Folder>\n";
			}
		}
	}	
	print KMLFILE "</Document>\n";
	print KMLFILE "</kml>\n";
	close KMLFILE;
	##system("scp $directory/shp/$base_prod_name/$prod_name.kml ldad\@ls1:/data/ldad/shp/$base_prod_name/$timeline");
	##system("scp $directory/shp/$base_prod_name/$prod_name.kml ldad\@ls1:/data/ldad/web/images/shp/$base_prod_name/$base_prod_name".".latest.kml");	
}

sub create_nothing_kml
{
	$KMLFILE = "$directory/shp/$base_prod_name/$prod_name.kml\n";
	open KMLFILE, "> $KMLFILE" or die "$KMLFILE file cannot be overwritten\n";
	print KMLFILE "<\?xml version=\"1.0\" encoding=\"UTF-8\"\?>\n";
	print KMLFILE "<kml xmlns=\"http://earth.google.com/kml/2.2\">\n";
	print KMLFILE "<Document>\n";
	print KMLFILE "<name>$prod_name</name>\n";
	print KMLFILE "  <description>\n";
	print KMLFILE "	   <![CDATA[$prod_name KML file written by:<br>\n";
        print KMLFILE "      Matthew Duplantis - Information Technology Officer<br>\n";
	print KMLFILE "	     National Weather Service - Shreveport, LA<br>]]>\n";
        print KMLFILE "  </description>\n";
 	print KMLFILE "  <open>1</open>\n";	
	print KMLFILE "  <ScreenOverlay>\n";
	print KMLFILE "    <name>Product Legend</name>\n";
	print KMLFILE "    <description>\n";
	print KMLFILE "      <![CDATA[<table border=0 width=\"250\"><tr><td>\n";
        print KMLFILE "      SPC's $base_prod_name.</td></tr></table>]]>\n";
	print KMLFILE "    </description>\n";
	print KMLFILE "    <visibility>1</visibility>\n";
	print KMLFILE "    <Icon>\n";
	print KMLFILE "      <href>http://www.srh.noaa.gov/images/shv/$base_prod_name.png</href>\n";
	print KMLFILE "    </Icon>\n";
	print KMLFILE "    <overlayXY x=\".02\" y=\".01\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <screenXY x=\".02\" y=\".01\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <rotationXY x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "    <size x=\"-1\" y=\"-1\" xunits=\"fraction\" yunits=\"fraction\" />\n";
	print KMLFILE "  </ScreenOverlay>\n";	
	print KMLFILE "    <LookAt>\n";
	print KMLFILE "    <longitude>-101.00</longitude>\n";
	print KMLFILE "    <latitude>38.50</latitude>\n";
	print KMLFILE "    <altitude>4000000</altitude>\n";
	print KMLFILE "    <range>4000000</range>\n";
	print KMLFILE "    <tilt>0</tilt>\n";
	print KMLFILE "    </LookAt>\n";
	print KMLFILE "	<Style id=\"Nothing\">\n";
	print KMLFILE "			<IconStyle>\n";
	print KMLFILE "                 <color>00000000</color>\n";
	print KMLFILE "			<scale>1</scale>\n";
	print KMLFILE "                 </IconStyle>\n";
	print KMLFILE "		<LabelStyle>\n";
	print KMLFILE "			<color>ff000000</color>\n"; # ffed20d8
	print KMLFILE "                 <scale>1.2</scale>\n";
	print KMLFILE "		</LabelStyle>\n";
	print KMLFILE " </Style>\n";
	print KMLFILE "  <Placemark>\n";
	print KMLFILE "    <visibility>1</visibility>\n";
	print KMLFILE "    <name>PREDICTABILITY TOO LOW</name>\n";
	print KMLFILE "    <LookAt>\n";
	print KMLFILE "    <longitude>-101.00</longitude>\n";
	print KMLFILE "    <latitude>38.50</latitude>\n";
	print KMLFILE "    <altitude>4000000</altitude>\n";
	print KMLFILE "    <range>4000000</range>\n";
	print KMLFILE "    <tilt>0</tilt>\n";
	print KMLFILE "    </LookAt>\n";
	print KMLFILE "    <styleUrl>#Nothing</styleUrl>\n";
	print KMLFILE "    <Point>\n";
	print KMLFILE "     <coordinates>-101.00, 38.50, 0 </coordinates>\n";
	print KMLFILE "    </Point>\n";
	print KMLFILE "  </Placemark>\n";
	print KMLFILE "</Document>\n";
	print KMLFILE "</kml>\n";
	close KMLFILE;
	#system("scp $directory/shp/$base_prod_name/$prod_name.kml ldad\@ls1:/data/ldad/shp/$base_prod_name/$timeline");
	#system("scp $directory/shp/$base_prod_name/$prod_name.kml ldad\@ls1:/data/ldad/web/images/shp/$base_prod_name/$base_prod_name".".latest.kml");
}

sub create_shp_new
{
	$cat_find = 0;
	$hail_find = 0;
	$tornado_find = 0;
	$wind_find = 0;

	for($l=0;$l<($#subnames+1);$l++)
	{
		if($subnames[$l] eq "CATEGORICAL"){$cat_find = 1;}
		if($subnames[$l] eq "HAIL"){$hail_find = 1;}
		if($subnames[$l] eq "TORNADO"){$tornado_find = 1;}
		if($subnames[$l] eq "WIND"){$wind_find = 1;}
						
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."$subnames[$l] polygon");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."$subnames[$l] -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		for($k=0;$k<($#theorder+1);$k++)
		{
			if($theorder[$k] =~ /$subnames[$l]/)
			{
				$name = $theorder[$k];
				system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."$subnames[$l] $shpline{$name}[1]");
				system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."$subnames[$l].dbf $name $issued $valid_from $valid_until");	
				system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."$subnames[$l].prj");					

			}
		}
	#system("rsync -ave ssh $directory/shp/$base_prod_name/$subnames[$l]* ldad\@ls1:/data/ldad/shp/$base_prod_name/$timeline");
	}

	if($cat_find == 0)
	{
		$predictability = "'SEE TEXT'";
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."CATEGORICAL point");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."CATEGORICAL -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."CATEGORICAL -97.00 38.00");
		system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."CATEGORICAL.dbf $predictability $issued $valid_from $valid_until");						
		system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."CATEGORICAL.prj");			
	}
	if($hail_find == 0)
	{
		$predictability = "'LESS THAN 5% ALL AREAS'";
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."HAIL point");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."HAIL -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."HAIL -97.00 38.00");
		system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."HAIL.dbf $predictability $issued $valid_from $valid_until");						
		system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."HAIL.prj");			
	}
	if($tornado_find == 0)
	{
		$predictability = "'LESS THAN 2% ALL AREAS'";
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."TORNADO point");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."TORNADO -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."TORNADO -97.00 38.00");
		system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."TORNADO.dbf $predictability $issued $valid_from $valid_until");						
		system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."TORNADO.prj");			
	}
	if($wind_find == 0)
	{
		$predictability = "'LESS THAN 5% ALL AREAS'";
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."WIND point");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."WIND -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."WIND -97.00 38.00");
		system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."WIND.dbf $predictability $issued $valid_from $valid_until");						
		system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."WIND.prj");			
	}

	#system("rsync -ave ssh $directory/config/$base_prod_name.lyr ldad\@ls1:/data/ldad/shp/$base_prod_name/$timeline/$base_prod_name"."_$timeline.lyr");
	#system("cp $directory/config/$base_prod_name.lyr shp/$base_prod_name/$base_prod_name"."_$timeline.lyr");										
	#system("zip -j $directory/shp/$base_prod_name/$base_prod_name $directory/shp/$base_prod_name/*");
	#system("scp $directory/shp/$base_prod_name/$base_prod_name.zip ldad\@ls1:/data/ldad/web/images/shp/$base_prod_name/$base_prod_name".".latest.zip");
}

sub create_nothing_shp
{
	if($ARGV[0] eq "NEWPTSDY1")
	{
		@hazards = ("TORNADO","HAIL","WIND","CATEGORICAL"); $layerfile = "Predictability_Too_Low.lyr";
	}
	if(($ARGV[0] eq "NEWPTSDY2")||($ARGV[0] eq "NEWPTSDY3"))
	{
		@hazards = ("ANY-SEVERE","CATEGORICAL"); $predictability="'NO ORGANIZED SEVERE TSTMS FCST'";
		if($ARGV[0] eq "NEWPTSDY2"){$layerfile = "Day2_PredTooLow.lyr";}
		if($ARGV[0] eq "NEWPTSDY3"){$layerfile = "Day3_PredTooLow.lyr";}
	}
	if($ARGV[0] eq "NEWPTSD48")
	{
		@hazards = ("ANY-SEVERE"); $predictability="'PREDICTABILITY TOO LOW'"; $layerfile = "Days4to8_PredTooLow.lyr";
	}
	for($e=0;$e<=$#hazards;$e++)
	{
		system("./shapelib-1.2.10/shpcreate shp/$base_prod_name/"."$hazards[$e] point");
		system("./shapelib-1.2.10/dbfcreate shp/$base_prod_name/"."$hazards[$e] -s NAME 50, -s ISSUED 15, -s VALID_FROM 15, -s VALID_UNTIL 15");
		system("./shapelib-1.2.10/shpadd shp/$base_prod_name/"."$hazards[$e] -97.00 38.00");
		system("./shapelib-1.2.10/dbfadd shp/$base_prod_name/"."$hazards[$e].dbf $predictability $issued $valid_from $valid_until");						
		system("cp $directory/config/MAIN.prj shp/$base_prod_name/"."$hazards[$e].prj");
	}
	#system("cp $directory/config/$layerfile shp/$base_prod_name/$base_prod_name"."_$timeline.lyr");
	#system("rsync -ave ssh $directory/shp/$base_prod_name/* ldad\@ls1:/data/ldad/shp/$base_prod_name/$timeline");	
	#system("scp $directory/shp/$base_prod_name/$prod_name-* ldad\@ls1:/data/ldad/shp/$base_prod_name");
	#system("zip -j $directory/shp/$base_prod_name/$base_prod_name $directory/shp/$base_prod_name/*");
	#system("scp $directory/shp/$base_prod_name/$base_prod_name.zip ldad\@ls1:/data/ldad/web/images/shp/$base_prod_name/$base_prod_name".".latest.zip");
}

sub clockwise
{
	my($x0,$y0,$x1,$y1,$x2,$y2) = @_;
	return($x2-$x0) * ($y1-$y0) - ($x1-$x0) * ($y2-$y0);
}

sub distance
{
	my @p = @_;
	return sqrt(($_[0] - $_[2])**2 + ($_[1] - $_[3])**2);
}

sub find
{
	my $find; my $finding_index;	
	my($x0, $y0) = @_;
        for(my $c=1;$c<($#uslat+1);$c++)
	{
		$y1 = $uslat[$c];
		$x1 = $uslon[$c];
		if($c == $#uslat)
		{	
			$y2 = $uslat[1];
			$x2 = $uslon[1];			
		}
		else
		{
			$y2 = $uslat[$c+1];
			$x2 = $uslon[$c+1];
		}
		if(($x0<=$x1)&&($x0>=$x2)&&((($y0>=$y1)&&($y0<=$y2))||(($y0<=$y1)&&($y0>=$y2)))&&($find==0))
		{
			$finding_index = $c; $find = 1;
		}
		if(($x0>=$x1)&&($x0<=$x2)&&((($y0>=$y1)&&($y0<=$y2))||(($y0<=$y1)&&($y0>=$y2)))&&($find==0))
		{
			$finding_index = $c; $find = 1;
		}
		if($find==1){return $finding_index;}
	}
}

sub get_array_of_us_points
{
	my $start_find=0; my $end_find=0; my $return_line = ""; my $capture = 0;
	my ($x0, $y0, $x1, $y1) = @_;
	chomp $x0; chomp $y0; chomp $x1; chomp $y1;
	my $internal_count = 0;
	for(my $c=1;$c<($#uslat+1);$c++)
	{
		$y2 = $uslat[$c]; chomp $y2;
		$x2 = $uslon[$c]; chomp $x2;
		if($c == $#uslat)
		{	
			$y3 = $uslat[1];
			$x3 = $uslon[1];
			$c = 0;
			$internal_count++;		
		}
		else
		{
			$y3 = $uslat[$c+1];
			$x3 = $uslon[$c+1];
		}
		if($capture == 1)
		{
			$return_line .= "$x2 $y2 ";
		}
		if(($x0<=$x2)&&($x0>=$x3)&&((($y0>=$y2)&&($y0<=$y3))||(($y0<=$y2)&&($y0>=$y3)))&&($start_find==0))
		{
			$starting_index = $c; $start_find = 1; $capture = 1;
		}
		if(($x0>=$x2)&&($x0<=$x3)&&((($y0>=$y2)&&($y0<=$y3))||(($y0<=$y2)&&($y0>=$y3)))&&($start_find==0))
		{
			$starting_index = $c; $start_find = 1; $capture = 1;	
		}
		if(($x1<=$x2)&&($x1>=$x3)&&((($y1>=$y2)&&($y1<=$y3))||(($y1<=$y2)&&($y1>=$y3)))&&($end_find==0)&&($start_find==1))
		{
			$ending_index = $c; $end_find = 1; $return_line .= "$x1 $y1 "; return $return_line;
		}
		if(($x1>=$x2)&&($x1<=$x3)&&((($y1>=$y2)&&($y1<=$y3))||(($y1<=$y2)&&($y1>=$y3)))&&($end_find==0)&&($start_find==1))
		{
			$ending_index = $c; $end_find = 1; $return_line .= "$x1 $y1 "; return $return_line;
		}
		if($internal_count>3)
		{
			# An error has occurred!
			print "An error has occurred in get_array_of_us_points\n";
			return "0 0 ";
		}	
	}	
}

sub test_segment
{
	my $val;	
	my ($x0, $y0, $x1, $y1) = @_;
	for(my $c=1;$c<($#uslat+1);$c++)
	{
		$y2 = $uslat[$c];
		$x2 = $uslon[$c];
		if($c == $#uslat)
		{	
			$y3 = $uslat[1];
			$x3 = $uslon[1];			
		}
		else
		{
			$y3 = $uslat[$c+1];
			$x3 = $uslon[$c+1];
		}
                ($ret_x, $ret_y, $true) = line_intersection($x0,$y0,$x1,$y1,$x2,$y2,$x3,$y3);
		if($true)
                {
                      	if($c == $#uslat)
			{	
				$y3 = $uslat[1];
				$x3 = $uslon[1];			
			}
			else
			{
				$y3 = $uslat[$c+1];
				$x3 = $uslon[$c+1];
			}
                        $val = find($ret_x, $ret_y);			
			return ($ret_x, $ret_y, $val);
                }
	}	
}

sub reverse_test_segment
{
	my $val;	
	my ($x0, $y0, $x1, $y1) = @_;
	for(my $c=$#uslat;$c>0;$c--)
	{
		$y2 = $uslat[$c];
		$x2 = $uslon[$c];
		if($c == 1)
		{	
			$y3 = $uslat[$#uslat];
			$x3 = $uslon[$#uslat];			
		}
		else
		{
			$y3 = $uslat[$c-1];
			$x3 = $uslon[$c-1];
		}
                ($ret_x, $ret_y, $true) = line_intersection($x0,$y0,$x1,$y1,$x2,$y2,$x3,$y3);
		if($true)
                {
                      	if($c == 1)
			{	
				$y3 = $uslat[$#uslat];
				$x3 = $uslon[$#uslat];			
			}
			else
			{
				$y3 = $uslat[$c-1];
				$x3 = $uslon[$c-1];
			}
                        $val = find($ret_x, $ret_y);			
			return ($ret_x, $ret_y, $val);
                }
	}	
}

sub bounding_box
{
	my ($d, @bb) = @_;
	my @p = splice(@bb, 0, 4);	

	@bb = (@p, @p) unless @bb;

	for(my $i=0; $i<$d; $i++)
	{
		for (my $j=0; $j<@p; $j+=$d)
		{
			my $ij = $i + $j;
			$bb[$i] = $p[$ij] if $p[$ij] < $bb[$i];
			$bb[$i+$d] = $p[$ij] if $p[$ij] > $bb[$i+$d];
		}
	}
	return @bb;
}

sub bounding_box_intersect
{
	my ($d, @bb) = @_;
	my @aa = splice(@bb, 0, 2 * $d);
	
	for(my $i_min=0; $i_min<$d; $i_min++)
	{
		my $i_max = $i_min + $d;

		return 0 if ($aa[$i_max] + epsilon) < $bb[$i_min];
		return 0 if ($bb[$i_max] + epsilon) < $aa[$i_min];
	}

	return 1;
}

sub line_intersection
{
	my($x0, $y0, $x1, $y1, $x2, $y2, $x3, $y3);
	($x0, $y0, $x1, $y1, $x2, $y2, $x3, $y3) = @_;

	my @box_a = bounding_box(2, $x0, $y0, $x1, $y1);	
	my @box_b = bounding_box(2, $x2, $y2, $x3, $y3);

	return (0,0,0) unless bounding_box_intersect(2, @box_a, @box_b);

	my ($x,$y);
	
	my $dy10 = $y1 - $y0;
	my $dx10 = $x1 - $x0;
	my $dy32 = $y3 - $y2;
	my $dx32 = $x3 - $x2;

	my $dy10z = abs($dy10) < epsilon;
	my $dx10z = abs($dx10) < epsilon;
	my $dy32z = abs($dy32) < epsilon;
	my $dx32z = abs($dx32) < epsilon;

	my $dyx10;
	my $dyx32;

	$dyx10 = $dy10 / $dx10 unless $dx10z;
	$dyx32 = $dy32 / $dx32 unless $dx32z;

	unless (defined $dyx10 or defined $dyx32)
	{
		return (0,0,0);  # parallel vertical
	}
	elsif($dy10z and not $dy32z)
	{
		$y = $y0;
		$x = $x2 + ($y - $y2) * $dx32/ $dy32;
	}
	elsif(not $dy10z and $dy32z)
	{
		$y = $y2;
		$x = $x0 + ($y - $y0) * $dx10/ $dy10;
	}
	elsif($dx10z and not $dx32z)
	{
		$x = $x0;
		$y = $y2 + $dyx32 * ($x - $x2);
	}
	elsif(not $dx10z and $dx32z)
	{
		$x = $x2;
		$y = $y0 + $dyx10 * ($x - $x0);
	}
	elsif(abs($dyx10 - $dyx32) < epsilon)
	{
		return (0,0,0);
	}
	else
	{
		$x = ($y2 - $y0 + $dyx10*$x0 - $dyx32*$x2)/($dyx10 - $dyx32);
		$y = $y0 + $dyx10 * ($x - $x0);
	}
	
	my $h10 = $dx10 ? ($x - $x0) / $dx10 : ($dy10 ? ($y - $y0) / $dy10 : 1);
	my $h32 = $dx32 ? ($x - $x2) / $dx32 : ($dy32 ? ($y - $y2) / $dy32 : 1);

	return ($x, $y, $h10 >= 0 && $h10 <= 1 && $h32 >=0 && $h32 <= 1);
}

sub slope_in
{
	my ($x0, $y0, $x1, $y1) = @_;
	my $dy10 = $y1 - $y0;
	my $dx10 = $x1 - $x0;
	my $x2; my $y2;
	
	if($dy10<0){$y2=($y1-((abs($dy10)*2)));}
	elsif($dy10>0){$y2=($y1+($dy10*2));}
	else{$y2=$y1;}

	if($dx10<0){$x2=($x1+((abs($dx10)*2)));}
	elsif($dx10>0){$x2=($x1-($dx10*2));}
	else{$x2=$x1;}
	
	return ($x2,$y2);
}

sub slope_out
{
	my ($x0, $y0, $x1, $y1) = @_;
	my $dy10 = $y1 - $y0;
	my $dx10 = $x1 - $x0;
	my $x2; my $y2;
	
	if($dy10<0){$y2=($y0+(abs($dy10)*2));}
	elsif($dy10>0){$y2=($y0-($dy10*2));}
	else{$y2=$y0;}

	if($dx10<0){$x2=($x0+((abs($dx10)*2)));}
	elsif($dx10>0){$x2=($x0-($dx10*2));}
	else{$x2=$x0;}
	
	return ($x2,$y2);
}


sub point_in_polygon
{
	my($x,$y,@xy)=@_;

	my $n=@xy/2;
	my @i = map{2*$_} 0 .. (@xy/2);
	my @x = map{$xy[$_]  } @i;
	my @y = map{$xy[$_+1]} @i;
	
	my($i,$j);

	my $side = 0;

	for($i=0,$j=$n-1;$i<$n;$j=$i++)
	{
		if(
		    (
		      (($y[$i]<=$y)&&($y<$y[$j]))||
		      (($y[$j]<=$y)&&($y<$y[$i]))
                    )
                    and
                    ($x<($x[$j]-$x[$i])*($y-$y[$i])/($y[$j]-$y[$i])+$x[$i])){$side=not $side;}
	}
	return $side ? 1 : 0;
}
