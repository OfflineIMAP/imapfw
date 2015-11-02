#!/bin/bash
#
# Run the travis tests locally.

errors=0
total=0
scripts=""

./get_tests.awk .travis.yml | while read script
do
  echo "\n=======  Running $script"
  total=$(($total + 1))
  $script
  if test $? -eq 0
  then
    scripts="$scripts\n- $script"
  else
    echo "======== FAILED"
    errors=$(($errors + 1))
    scripts="$scripts\n- $script (FAILED)"
  fi

  printf "\n\nTests done:"
  printf "$scripts\n"
  printf "\nTotal: $total\n"
done

# vim: expandtab ts=2 :
