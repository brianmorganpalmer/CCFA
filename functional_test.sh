#!/bin/bash

function trackfail () {
	exit_code=$1
	command="$2"
	if [ $exit_code -ne 0 ]; then
		failures=$(printf "%s\n%s\n" "$failures" "$command")
	else 
		successes=$(printf "%s\n%s\n" "$successes" "$command")
	fi
}

function printtrack() {
	echo "failures:"
	echo "$failures"
	echo "successes:"
	echo "$successes"
	if [ $(echo "$failures" | wc -l) -gt 0 ]; then
		exitcode=1
	fi
}

echo "----------------------------------------"
echo "Running functional test for 16s pipeline"
echo "----------------------------------------"
wget -O- 'http://huttenhower.sph.harvard.edu/biobakery-shop/anadama/16s_functional_test.tgz' | tar -xzf -
cd 16s_functional_test
mibc_build initialize-project \
	'study_description: test' \
	'sample_type: mouse' \
	'filename:' \
	'16s_data: true' \
	'study_title: test' \
	'platform: 454' \
	'visualize: yes'
trackfail $? "mibc_build initialize-project"
cd - > /dev/null 2>&1
mibc_build runproject --project 16s_functional_test/ --reporter=verbose > 16s_functional_test.run.log 2>&1
trackfail $? "mibc_build runproject" 
echo "16s pipeline functional test complete"
echo "----------------------------------------"

echo "----------------------------------------"
echo "Running functional test for wgs pipeline"
echo "----------------------------------------"
wget -O- 'http://huttenhower.sph.harvard.edu/biobakery-shop/anadama/wgs_functional_test.tgz' | tar -xzf -
cd wgs_functional_test
mibc_build initialize-project \
        'study_description: test' \
        'sample_type: human, skin' \
        'filename:' \
        '16s_data: no' \
        'study_title: test' \
        'platform: 454' \
        'visualize: yes'
trackfail $? "mibc_build initialize-project"
cd - > /dev/null 2>&1
mibc_build runproject --project wgs_functional_test/ --reporter=verbose > wgs_functional_test.run.log 2>&1
trackfail $? "mibc_build runproject" 
echo "wgs pipeline functional test complete"
echo "----------------------------------------"

echo "----------------------------------------"
printtrack
echo "----------------------------------------"

exit $exitcode
