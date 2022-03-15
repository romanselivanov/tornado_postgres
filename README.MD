how to build:  
docker-compose up  

access api url:  

http://localhost/api/add/  
or
http://localhost/api/add  

example body:  

{  
    "body": "petdfgdad",  
    "key": "vasya"  
}  

methods:  

http://localhost/api/add/  
http://localhost/api/get?key=key  
http://localhost/api/update/{key}  
http://localhost/api/remove/{key}  
http://localhost/api/statistic/  
