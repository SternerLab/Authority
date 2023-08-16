# docker run -d -p 27017:27017 --device=/dev/nvme1n1:/wtf:rw --cap-add CAP_SYS_ADMIN mongo
docker run -d -p 27017:27017  -v /workspace:/workspace -v ~/mongodb_data:/data/db mongo
# docker run -d -p 27018:27018  -v /workspace:/workspace -v /workspace/jstor_resolution_mongodb_archive_dec_20_2022_lsaldyt:/data/db mongo
