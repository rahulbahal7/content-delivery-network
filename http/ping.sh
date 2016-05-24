#!/bin/bash
echo $*
((count = 5))                            # Maximum number to try.
while [[ $count -ne 0 ]] ; do
    ping -c 1 $*                      # Try once.
    rc=$?
    if [[ $rc -eq 0 ]] ; then
        ((count = 1))                      # If okay, flag to exit loop.
    fi
    ((count = count - 1))                  # So we don't go forever.
done

if [[ $rc -eq 0 ]]
then                  # Make final determination.
    echo "here"
else
    echo "Timeout."
fi
