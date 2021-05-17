#!/bin/bash
web_api_examples_path="SKR_Web_API_V2_4/examples"
input_path="../../../results/mesh/*.txt"
output_path="../../../results/mesh/output"
cd $web_api_examples_path

mkdir -p -- $output_path

javac -cp ../classes:../lib/skrAPI.jar:../lib/commons-logging-1.1.1.jar:../lib/httpclient-cache-4.1.1.jar:../lib/httpcore-nio-4.1.jar:../lib/httpclient-4.1.1.jar:../lib/httpcore-4.1.jar:../lib/httpmime-4.1.1.jar -d ../classes GenericBatch.java

for filename in $input_path; do
    echo $filename
    # (java -cp ../classes:../lib/skrAPI.jar:../lib/commons-logging-1.1.1.jar:../lib/httpclient-cache-4.1.1.jar:../lib/httpcore-nio-4.1.jar:../lib/httpclient-4.1.1.jar:../lib/httpcore-4.1.jar:../lib/httpmime-4.1.1.jar GenericBatch) > %output_folder_path%"\%%~ni.txt"  
done