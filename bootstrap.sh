#!/bin/bash

ip=http://$(hostname -I)
ip=${ip::-1}
peerurl=$ip:2380
clienturl=$ip:2379
etcdname=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

EC2_Region=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
EC2_Region=${EC2_Region::-1}

#Get members of the Service Registy Tag
registry_instances=$(aws ec2 describe-instances \
--region $EC2_Region \
--filters "Name=tag:Purpose,Values=Service Registry" \
--query 'Reservations[*].Instances[*].[InstanceId,PrivateIpAddress]' \
--output text)

#The amount of Service Registry Instances
count_RI=$(wc -w <<< "$registry_instances")
count_RI=$count_RI/2
count_RI=$((count_RI/2))

#If 1 (This Instance), Create new cluster
if [ $count_RI == 2]
        then
            	nohup ./etcdnewcluster.sh &      		
fi