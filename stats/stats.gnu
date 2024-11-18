#!/usr/bin/gnuplot 
set xdata time
set timefmt "%Y-%m-%d"
set xrange ["2021-07-01":"2024-11-01"]
set format x "%m/%y"
set key left
plot "stats.txt" us 1:2 w linesp t "SCS github members"
set term png
set output "stats.png"
replot
