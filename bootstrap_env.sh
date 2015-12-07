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
sudo apt-get install -y gcc g++ gfortran build-essential git wget linux-image-generic libopenblas-dev python-dev liblapack-dev libblas-dev libxml2-dev libxslt1-dev
# python-pip python-nose python-numpy python-scipy

# Install pip2.6
# sudo easy_install-2.7 pip
# INstall python packages
sudo /usr/bin/pip install redis lxml

# Install keras
sudo /usr/bin/pip install git+git://github.com/Theano/Theano.git
sudo /usr/bin/pip install keras

# Attach EBS volume
sudo mkdir /mnt/nlp
sudo chown -R ubuntu /mnt/nlp
sudo mount /dev/xvdf /mnt/nlp


# Attach/format Instance store (that supportts TRIM)
sudo mkdir /mnt/ephemeral0
sudo chown -R ubuntu /mnt/ephemeral0
# sudo mkfs.ext4 -E nodiscard /dev/xvdb # DANGEROUS!
sudo mount /dev/xvdb /mnt/ephemeral0
sudo chown -R ubuntu /mnt/ephemeral0

# Move the XML files over to the ephemeral instance store for speed
cp -R /mnt/nlp/small_xml /mnt/ephemeral0/

# # Install nvidia drivers
# wget http://us.download.nvidia.com/XFree86/Linux-x86_64/358.16/NVIDIA-Linux-x86_64-358.16.run
# sudo /bin/bash ./NVIDIA-Linux-x86_64-358.16.run
# sudo reboot now
# # Check nvidia drivers
# nvidia-smi -q | head

# # install CUDA
# wget http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda_7.5.18_linux.run
# sudo sh cuda_7.5.18_linux.run
# sudo echo -e "\nexport PATH=/usr/local/cuda/bin:$PATH\n\nexport LD_LIBRARY_PATH=/usr/local/cuda/lib64" >> ~/.bashrc
# echo -e "\n[global]\nfloatX=float32\ndevice=gpu\n[mode]=FAST_RUN\n\n[nvcc]\nfastmath=True\n\n[cuda]\nroot=/usr/local/cuda" >> ~/.theanorc

# Rsync the working directory over to the server (into /mnt/nlp/code)
### RUN THIS ON THE LOCAL WORKSTATION
watch ./rsync.sh

# Install redis
cd /media/ephemeral0/ && wget http://download.redis.io/redis-stable.tar.gz && tar xvzf redis-stable.tar.gz && cd redis-stable && make distclean && make && sudo make install
# Startup redis and load the database
redis-server /mnt/nlp/code/redis.conf
