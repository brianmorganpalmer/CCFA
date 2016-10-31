#!/bin/sh

## deposition checker python wrapper script
## calls python repository checker scripts for given username 
## and email address

username=$1
useremail=$2

##echo "<br> testing:"
##echo "<br>start<br>"
##echo "User: $username<br>"
##echo "Email: $useremail<br>"

# setup python environment
. /var/www/ccfa/python/venv/bin/activate
# run python script and capture output
output=`/var/www/ccfa/python/deposition/deposition_tests.py -u $username 2>&1`
# spit all output to stdout
echo $output
