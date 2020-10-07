cd "C:\Users\manuh\Documents\sterner lab\mesh_input\SKR_Web_API_V2_3\SKR_Web_API_V2_3\examples"

javac -cp ..\classes;..\lib\skrAPI.jar;..\lib\commons-logging-1.1.1.jar;..\lib\httpclient-cache-4.1.1.jar;..\lib\httpcore-nio-4.1.jar;..\lib\httpclient-4.1.1.jar;..\lib\httpcore-4.1.jar;..\lib\httpmime-4.1.1.jar -d ..\classes GenericBatch.java 

set list2=quarbullnuttorni quarjfloracadsci quarrevibiol rangecolmana recaucinsmus recoauckmuse repoprogcondroya restmananote revijardbotanaci rhodora riviortoital rivipatovege rivisocitoscorti rodriguesia seedtechnology selbyana semiannuagas sidacontbota sirwjhookrepokew soutnatu soutnatu2 systbiol systbotamono systematicbotany systgeogplan systzool taxon torreya tranamerentosoc2 tranamerentosoc3 tranamerentosoci tranamermicrsoci trimrepoohioherp 
set list=ursus vegehistarch vegetatio wateintejwatebio weeds weedscience weedtechnology westnortamernatu wildmono wildsocibull wildsocibull2011 willbeih willdenowia wilsbull wilsjornit wilsq worldviews yorkcactj zeitmorpokoltier zeitpfla zeitpflagall zeitpflapfla zeitpflapfla2 zeitpflapflapfla zewibiabeplanta
(for %%a in (%list%) do (
    REM echo "C:\Users\manuh\Documents\sterner lab\AuthorDisambiguation\r_table\results\mesh\%%a\input.txt"
    (java -cp ..\classes;..\lib\skrAPI.jar;..\lib\commons-logging-1.1.1.jar;..\lib\httpclient-cache-4.1.1.jar;..\lib\httpcore-nio-4.1.jar;..\lib\httpclient-4.1.1.jar;..\lib\httpcore-4.1.jar;..\lib\httpmime-4.1.1.jar GenericBatch "C:\Users\manuh\Documents\sterner lab\AuthorDisambiguation\r_table\results\mesh\%%a\input.txt") > "C:\Users\manuh\Documents\sterner lab\AuthorDisambiguation\r_table\results\mesh\output\%%a.txt"  

))

