This is the repository for the CyberIrishman 5 Day AI and Cyber Course
Here would will find logs to be parsed/inspected and for training and testing as well as some of the code to present the learning concepts

Logs presented in the rba_005.csv file are in this format

In terminal we can inspect >head  rba_005.csv  
   

index,Login Timestamp,User ID,Round-Trip Time [ms],IP Address,Country,Region,City,ASN,User Agent String,Browser Name and Version,OS Name and Version,Device Type,Login Successful,Is Attack IP,Is Account Takeover   
1751,2020-02-03 13:06:41.282,5445253994546962491,,77.106.183.7,NO,Innlandet,Ingeberg,29492,"Mozilla/5.0  (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko Chrome/90.0.4411.0 Safari/537.36",Chrome 90.0.4411,Mac OS X 10.14.6,desktop,True,False,False  
3744,2020-02-03 13:30:07.676,8200300057825330033,,10.0.160.153,NO,-,-,500030,"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 OPR/65.0.3467.72",Opera 65.0.3467,Mac OS X 10.14.6,desktop,True,False,False    
5949,2020-02-03 13:55:37.938,6052294313599860885,,199.26.84.177,US,-,-,393398,"Mozilla/5.0  (Linux; Android 10.0.99) AppleWebKit/537.36 (KHTML, like Gecko Version/4.0 Chrome/85.0.4183.101 Mobile Safari/537.36 Cordova/9.0.0 SpvAppBrowser/4.3.13 SpvID/ad62b3ae7e3a",Chrome Mobile WebView 85.0.4183,Android 10.0.99,mobile,True,False,False   
8013,2020-02-03 14:19:27.383,-4324475583306591935,,109.254.26.154,CZ,-,-,20590,"Mozilla/5.0  (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) Build/NDQS26.69-64-11-7; wv AppleWebKit/537.36 (KHTML, like Gecko Version/4.0 Chrome/85.0.4183.81 Mobile Safari/537.36",Chrome Mobile WebView 85.0.4183,iOS 14.2.1,mobile,False,False,False   
   
In the day2_auth.log file the logs are derived from the RBA dataset with 30 extra augmented logs to find with our projects.  
These are in the format : 
2025-06-02T00:09:12.904Z host=auth-gw-01 svc=login event=AUTH_SUCCESS user=user_35924a uid=-602929497224448488 src_ip=10.0.64.186 country=NO asn=AS29695 device=mobile result=success reason=ok ua="Mozilla/5.0  (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko Chrome/81.0.4044.1925.138 Mobile Safari/537.36 OPT/2.4"  
2025-06-02T00:15:31.601Z host=auth-gw-01 svc=login event=AUTH_FAILURE user=user_3c1fac uid=1595739281232346896 src_ip=77.222.214.25 country=NO asn=AS29695 device=mobile result=fail reason=invalid_credentials ua="Mozilla/5.0  (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko Chrome/81.0.4044.1928.111 Mobile Safari/537.36,gzip(gfe,gzip(gfe variation/222762"   
2025-06-02T00:19:54.843Z host=auth-gw-01 svc=login event=AUTH_SUCCESS user=user_ec3cdd uid=6257035908712866724 src_ip=91.186.5.48 country=GB asn=AS29550 device=desktop result=success reason=ok ua="Mozilla/5.0  (X11; CrOS armv7l 5978.98.0) AppleWebKit/537.36 (KHTML, like Gecko Chrome/79.0.3945.192.194.130 Safari/537.36 RuxitSynthetic/1.0 v5043457830 t8347097904287973985"  
2025-06-02T00:21:34.329Z host=auth-gw-01 svc=login event=AUTH_FAILURE user=user_8421a6 uid=-2153373345281138399 src_ip=170.39.77.137 country=US asn=AS393398 device=mobile result=fail reason=invalid_credentials ua="Mozilla/5.0  (Linux; Android 4.1; Galaxy Nexus Build/JRN84D) AppleWebKit/537.36 (KHTML, like Gecko Chrome/81.0.4044.1925.117 Mobile Safari/537.36"  
