#!/bin/bash

echo "Enter some text:"
read user_input
output_file="output.txt"
echo "$user_input" >> "$output_file"
echo "Your input has been saved to $output_file."
