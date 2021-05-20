#!/bin/bash
web_api_examples_path="SKR_Web_API_V2_4/examples"
input_path="../../../results/mesh/"
output_path="../../../results/mesh/output/"
cd $web_api_examples_path

export UTS_API_KEY=""
mkdir -p -- $output_path

javac -cp ../classes:../lib/skrAPI.jar:../lib/commons-logging-1.2.jar:../lib/httpclient-cache-4.5.13.jar:../lib/httpclient-4.5.13.jar:../lib/httpcore-4.4.13.jar:../lib/httpmime-4.5.13.jar -d ../classes GenericBatch.java
for filename in "$input_path"*; do
    if [[ "$filename" == *mesh\/[j-z]*\.* ]]
    then
        echo "$filename"
        fname=`basename $filename`
        output_file_name="${output_path}${fname}"
        echo $fname
        echo $output_file_name
        python "../../mesh_abstracts_preprocessor.py" --file $filename
        java -cp ../classes:../lib/skrAPI.jar:../lib/commons-logging-1.2.jar:../lib/httpclient-cache-4.5.13.jar:../lib/httpclient-4.5.13.jar:../lib/httpcore-4.4.13.jar:../lib/httpmime-4.5.13.jar GenericBatch $filename > $output_file_name
    fi
done
