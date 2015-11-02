#!/usr/bin/awk -f

BEGIN {
  FS="\n"
}

{
  if ($1 == "script:") {
    FS="- "
  }
  else if ($1 == "  ") {
    print $2
  }
}

# vim: expandtab ts=2 :
