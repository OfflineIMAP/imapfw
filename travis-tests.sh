#!/bin/bash
#
# Run the travis tests locally.

GET_TESTS_FILE='get_tests.awk'

cat <<EOF > "$GET_TESTS_FILE"
#!/usr/bin/awk -f

BEGIN {
  FS="\n"
}

{
  if (\$1 == "script:") {
    FS="- "
  }
  else if (\$1 == "  ") {
    print \$2
  }
}
EOF

chmod u+x "$GET_TESTS_FILE"


errors=0
total=0
scripts=""

./"$GET_TESTS_FILE" .travis.yml | while read script
do
  printf "\n=======  Running $script"
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
  printf "\nTotal: $total, errors: $errors\n"
done

rm -f "$GET_TESTS_FILE" > /dev/null 2>&1

# vim: expandtab ts=2 :
