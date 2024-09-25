# Seestar_Varstar
Drawing upon the work of Kai (seestar_run) and Arseneceefe (S50).

Designed to support observations of variable stars where a set of targets are observed repeatedly over a night. I found that constructing a schedule for seestar_run to do this, while possible, is rather tedious. I also have pruned away some of the functions from seestar_run regarding mosics as these are not required.

# Setup:

Modify the seestar_varstar_params.py to set the IP address of your Seestar on you local network

Add the targets you require for the night in a schedule file (e.g. schedule_yyyymmdd.dat) which is formatted thus:

Name,ExpTime,TotalExp
RU Lup,10,120
Eta Boo,1,60

At the command line enter:

python seestar_varstar.py schedule_yyyymmdd.dat <repetition mode> <debug boolean>

Where the repetition mode can be:

* repeat - The set of targets is looped repeatedly until dawn
* single - The set is excuted only once
# END SETUP

# To note
For this application the LP filter in not required hence is_lp_filter=False

# to do
Need to add code to modify the exposure settings