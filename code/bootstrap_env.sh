# Environment setup script
sudo yum update -y
sudo reboot # Updating kernel

# install packages
# FOR AMAZON LINUX
# sudo yum install -y python27-numpy python27-scipy python27-matplotlib gcc gcc-c++ make python-devel libxml2-devel libxslt-devel git zsh
sudo yum groupinstall -y "Development tools"
sudo yum install kernel-devel-`uname -r` -y

# FOR ubuntu
sudo apt-get update
sudo apt-get install -y gcc g++ gfortran build-essential git wget linux-image-generic libopenblas-dev python-dev liblapack-dev libblas-dev libxml2-dev libxslt1-dev libhdf5-dev unzip
# python-pip python-nose python-numpy python-scipy

# Install pip2.6
# sudo easy_install-2.7 pip
# INstall python packages
sudo /usr/bin/pip install redis lxml gensim sklearn cython h5py


# Install keras
sudo /usr/bin/pip install git+git://github.com/Theano/Theano.git
sudo /usr/bin/pip install keras

# Attach EBS volume
sudo mkdir /mnt/nlp
sudo chown -R ubuntu /mnt/nlp
sudo mount /dev/xvdf /mnt/nlp

# Let's move our EBS volume to S^3 bucket for external viewing by the world
sudo apt-get install awscli
aws s3 cp /mnt/nlp s3://nlp-dataset-6806-2015 --recursive --acl public-read --storage-class STANDARD_IA

# Attach/format Instance store (that supportts TRIM)
sudo mkdir /mnt/ephemeral0
sudo chown -R ubuntu /mnt/ephemeral0
# sudo mkfs.ext4 -E nodiscard /dev/xvdb # DANGEROUS!
sudo mount /dev/xvdb /mnt/ephemeral0
sudo chown -R ubuntu /mnt/ephemeral0

# Move the XML files over to the ephemeral instance store for speed
cp -R /mnt/nlp/small_xml /mnt/ephemeral0/
cp -R /mnt/nlp/word2vec_models /mnt/ephemeral0/

# Rsync the working directory over to the server (into /mnt/nlp/code)
### RUN THIS ON THE LOCAL WORKSTATION
watch ./rsync.sh

# Install redis
cd /mnt/ephemeral0/ && wget http://download.redis.io/redis-stable.tar.gz && tar xvzf redis-stable.tar.gz && cd redis-stable && make distclean && make && sudo make install
# Startup redis and load the database
redis-server /mnt/nlp/code/redis.conf

# FIX PERMISSIONS
sudo chown -R ubuntu /home/ubuntu/
