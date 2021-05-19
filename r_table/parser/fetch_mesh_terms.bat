set web_api_examples_path="C:\Users\manuh\Documents\sterner lab\mesh_input\SKR_Web_API_V2_3\SKR_Web_API_V2_3\examples"
set input_path="C:\Users\manuh\Documents\sterner lab\AuthorDisambiguation\r_table\parser\results\mesh\*.txt"
set output_folder_path="C:\Users\manuh\Documents\sterner lab\AuthorDisambiguation\r_table\parser\results\mesh\output"

echo %output_folder_path%
if not exist %output_folder_path% mkdir %output_folder_path%
cd %web_api_examples_path%


javac -cp ..\classes;..\lib\skrAPI.jar;..\lib\commons-logging-1.1.1.jar;..\lib\httpclient-cache-4.1.1.jar;..\lib\httpcore-nio-4.1.jar;..\lib\httpclient-4.1.1.jar;..\lib\httpcore-4.1.jar;..\lib\httpmime-4.1.1.jar -d ..\classes GenericBatch.java 

for %%i in (%input_path%) do (
    (echo %%i)
    (echo  %%~ni)
    (java -cp ..\classes;..\lib\skrAPI.jar;..\lib\commons-logging-1.1.1.jar;..\lib\httpclient-cache-4.1.1.jar;..\lib\httpcore-nio-4.1.jar;..\lib\httpclient-4.1.1.jar;..\lib\httpcore-4.1.jar;..\lib\httpmime-4.1.1.jar GenericBatch "%%i") > %output_folder_path%"\%%~ni.txt"  

)

