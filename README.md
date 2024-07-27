# Variables

`MY_USER` is jumbo username
`MY_PASS` is jumbo password
`BEARER_SPLITWISE` splitwise bearer token
More .env variables can be found in the .env-example that need to be filled in

# Run project

`uvicorn app.main:app --port 80`

# Docker
To build to docker
```docker build -t typingpenguin/bill_management .``` 

to run the docker
```docker run -e MY_USER=[REPLACE_USERNAME] -e MY_PASS=[REPLACE_PASSWORD] -d --name bill_container -p 80:80 bill_management```