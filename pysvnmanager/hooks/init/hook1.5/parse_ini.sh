#!/bin/bash


CONFIG=../conf/hooks.ini

function readconf() {
 
    match=0
 
    while read line; do
        # skip comments
        [[ $line =~ ^\ {0,}# ]] && continue

 
        # skip empty lines
        [[ -z "$line" ]] && continue
 
        # still no match? lets check again
        if [ $match == 0 ]; then

            # do we have a section tag ?
            if [[ $line =~ ^\[.*?\] ]]; then

                #strip []
                line=${line:1:$((${#line}-2))}
                # strip whitespace
                section=${line// /}

                # do we have a match ?
                if [[ "$section" == "$1" ]]; then
                    match=1
                    continue
                fi
 
                continue
            fi
 
        # found next section after config was read - exit loop
        elif [[ $line =~ ^\[.*?\] && $match == 1 ]]; then
            break
 
        # got a config line eval it
        else
            var=${line%%=*}
            var=${var// /}
            value=${line##*=}
            value=${value## }
            eval "$var='$value'"
        fi
 
    done < "$CONFIG"
}


