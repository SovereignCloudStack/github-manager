#!/bin/bash
# stats.sh
rm stats.txt
for year in 2021 2022 2023 2024; do
	if test $year == 2021; then stmonth=7; else stmonth=1; fi
	if test $year == 2024; then enmonth=11; else enmonth=12; fi
	for month in `seq $stmonth $enmonth`; do
		MO=`printf %02i $month`
		git checkout "`git rev-list main -n 1 --first-parent --before=$year-$MO-01`"
		if test -e orgs/SovereignCloudStack/data.yaml; then
			MEM=`grep 'login:' orgs/SovereignCloudStack/data.yaml | wc -l`
		elif test -e orgs/SovereignCloudStack/people/members.yml; then
			MEM=`grep 'login:' orgs/SovereignCloudStack/people/members.yml | wc -l`
			MEM2=`grep '^      - ' orgs/SovereignCloudStack/teams/members.yml  | sort -u | wc -l`
			if test $MEM2 -gt $MEM; then MEM=$MEM2; fi
		else
			MEM=`grep '^      - ' orgs/scs/teams/members.yml  | sort -u | wc -l`
		fi
		echo -e "$year-$MO-01\t$MEM" | tee -a stats.txt
	done
done
git checkout main
