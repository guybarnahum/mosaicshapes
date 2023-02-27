# Mosaic Shapes

<p align="center">
  <img src="./examples/mosaic1.jpg" width="30%"> 
  <img src="./examples/mosaic3.jpg" width="30%"> 
  <img src="./examples/mosaic4.jpg" width="30%"> 
</p>



```console
$ python run.py file://path/to/input.jpg -e 2000 -d -c 1; open /tmp/out.jpg

$ python run.py --help
usage: run.py [-h] [-d] [-c {0,1,2}] [-a] [-r WORKING_RES] [-e ENLARGE] [-m MULTI] [-p POOL] [-o OUT] [-b] [-D] N [N ...]

Mosaic photos

positional arguments:
  N                     Url photos

optional arguments:
  -h, --help            show this help message and exit
  -d, --diamond         Use diamond grid instead of squares
  -c {0,1,2}, --color {0,1,2}
                        Specify color values
  -a, --analogous       Use analogous color
  -r WORKING_RES, --working_res WORKING_RES
                        Resolution to sample from
  -e ENLARGE, --enlarge ENLARGE
                        Resolution to draw
  -m MULTI, --multi MULTI
  -p POOL, --pool POOL
  -o OUT, --out OUT     output file - default is /tmp/out.jpg
  -b, --base64url       urls are in base64url ecoding
  -D, --download-only   download image from url to local path
```

## FastApi

```console
cd app
uvicorn main:app --host 127.0.0.1 --port 9001
```

## Docker cheatsheet

You should know this already...

### Image Building

```console
docker build -t mosaicshapes . --no-cache 
docker build -t mosaicshapes . 
clear; docker build -t mosaicshapes . ; docker image prune -f ; docker images 
```

### Container Running

```console
docker run --rm -it --entrypoint bash mosaicshapes   
docker container run --rm -it -p 8080:80 mosaicshapes 

docker exec -it CONTAINER_ID /bin/bash
docker exec -it $(docker container ls -q --last 1) /bin/bash
```

### Cleanup 
Probably better to avoid the need for cleanup with ```--rm``` option for containers and ```prune``` for images

```console
docker ps -aq  
docker rm $(docker ps -aq)
docker image rm <image-id>
docker image prune
```

## Known Issues

### Temp file leaks when worker is terminated by system

