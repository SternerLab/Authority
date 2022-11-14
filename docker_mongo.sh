# docker volume create --name=mongovol --driver=local --opt type=ext4 --opt device=/dev/nvme1n1
# docker run -d -p 27017:27017 -v mongovol:/data mongo --cap-add CAP_SYS_ADMIN
# docker run -d -p 27017:27017 --device=/dev/nvme1n1:/wtf:rw --cap-add CAP_SYS_ADMIN mongo

# :/workspace/mongodb_data

# docker run -d -p 27017:27017 --device=/dev/nvme1n1:/wtf:rw mongo
#-v /mongodb_data:/data/db mongo
docker run -d -p 27017:27017 -v ~/mongodb_data:/data/db mongo
