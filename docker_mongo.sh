# docker volume create --name=mongovol --driver local --opt type=extfs --opt device=:/workspace/mongodb_data
# docker run -d -p 27017:27017 -v mongovol:/data/db mongo
docker run -d -p 27017:27017 -v ~/mongodb_data:/data/db mongo
