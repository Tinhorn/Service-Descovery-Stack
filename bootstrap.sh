#!/bin/bash

#This will be run by root so no need to sudo

yum -y update

#install python and nginxparser
yum install -y python34 python34-pip curl nginx

#set python command to the latest
alternatives --set python /usr/bin/pytnon3.4

#upgrade cli and install boto
pip install -U awscli
pip install boto3



#Get the files needed from s3
mkdir /staging
aws s3 cp s3://microservicediscovery/ /staging --recursive
instanceid=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

chmod 700 -R /staging
cd /staging/



#move the file to their appropriate position
mv etcd/ /etc/

echo "Starting python bootstrap" >> bootstrap.log
python bootstrap.py $instanceid

if [ $? -eq 0 ]
then
  echo "bootstrap.py was successful" >> bootstrap.log
  echo "Setting permission on newly created file" >> bootstrap.log
  chmod 700 etcdcluster.sh
  ./etcdcluster.sh
  
  #Backing up the nginx conf
  cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
  
  #Repacing nginx conf
  rm /etc/nginx/nginx.conf
  cp nginx.conf /etc/nginx/
  
  #lowering the time needing to lower the timeout
  printf "\nnet.ipv4.tcp_fin_timeout 15\n" >> /etc/sysctl.conf
  
  #increasing the number of file describer for nginx proxying
  printf "\nsoft nofile 4096\nhard nofile 4096\n" >> /etc/security/limits.conf
  
  
  #starting nginx
  service nginx start
else
  echo "Something went wrong" >> bootstrap.log
fi