#!/bin/bash 

# Just a utility script to generate the build status table for README.md

specfile="linux-gpib.spec"
coprurl="https://copr.fedorainfracloud.org/coprs/vddvss/linux-gpib/package"

packages=$(rpmspec -q --qf "%{NAME}\n" $specfile | sed '/debug/d' | sort -u)

echo "| Package | Build Status |"
echo "| ------- | ------------ |"
for p in $packages ; do
    echo "| \`$p\` | [![build status]($coprurl/status_image/last_build.png)]($coprurl) |"
done
