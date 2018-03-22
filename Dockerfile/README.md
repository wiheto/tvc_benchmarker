# Docker file instructions 

The docker file runs all the simulations and all the methods.
Requires docker is installed on your computer. 

To run, the Docker image first needs to be built.

'''
docker build -t tvc_benchmarker path/to/tvc_benchmarker/Dockerfile
'''

Then run the image. 

'''
docker run -i -t tvc_benchmarker 
''' 

This will run all tvc_benchmarker. To copy the files to your computer, you first need to identify the image. 

'''
docker ds -a 
'''

And there you should be able to find something like the following output: 

|CONTAINER ID|IMAGE|COMMAND|CREATED|STATUS|PORTS|NAMES
|---|---|---|---|---|---|---|
|ea0cef5dff59|tvc_benchmarker|"python3 -m tvc_benc…"|22 hours ago|Exited (0) 13 hours ago||brave_bardeen

You want to identify the NAMES (so here it would be brave_bardeen). 
Then to copy from the docker container, type: 

docker cp brave_bardeen:tvc_benchmarker/ ./ 

Flags to add a new method will be added to the dockerfile soon. 
