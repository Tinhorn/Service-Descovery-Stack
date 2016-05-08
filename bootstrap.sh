#!/bin/bash

#This will be run by root so no need to sudo

yum -y update

#install python and nginxparser
yum install -y python34 python34-pip nginxparser curl

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
else
  echo "Something went wrong" >> bootstrap.log
fi