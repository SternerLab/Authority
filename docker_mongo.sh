# docker run -d -p 27017:27017 --device=/dev/nvme1n1:/wtf:rw --cap-add CAP_SYS_ADMIN mongo
docker run -d -p 27017:27017  -v /workspace:/workspace -v ~/mongodb_data:/data/db mongo
