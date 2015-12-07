# Environment setup script
sudo yum install -y numpy scipy matplotlib install gcc gcc-c++ make python-devel libxml2-devel libxslt-devel

# Install pip2.6
sudo easy_install-2.6 pip
# INstall python packages
sudo /usr/local/bin/pip2.6 install redis lxml

# Attach EBS volume
sudo mkdir /mnt/nlp
sudo chown -R ec2-user /mnt/nlp
sudo mount /dev/xvdf /mnt/nlp


# Attach/format Instance store (that supportts TRIM)
sudo mkdir /mnt/ephemeral0
sudo chown -R ec2-user /mnt/ephemeral0
sudo mkfs.ext4 -E nodiscard /dev/xvdb
sudo mount /dev/xvdb /mnt/ephemeral0
sudo chown -R ec2-user /mnt/ephemeral0

# Move the XML files over to the ephemeral instance store for speed
screen -dmS migrating_xml
screen -S migrating_xml -X stuff "cp -R /mnt/nlp/xml /mnt/ephemeral0/"

# Rsync the working directory over to the server (into /mnt/nlp/code)
### RUN THIS ON THE LOCAL WORKSTATION
watch ./rsync.sh

# Install redis
screen -dmS installing_redis
screen -S installing_redis -X stuff "cd /mnt/ephemeral0/ && wget http://download.redis.io/redis-stable.tar.gz && tar xvzf redis-stable.tar.gz && cd redis-stable && make distclean && make && sudo make install \n"
# Startup redis
screen -S installing_redis -X stuff "redis-server /mnt/nlp/code/redis.conf ^M"
