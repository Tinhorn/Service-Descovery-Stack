#!/bin/bash

ip=http://$(hostname -I)
ip=${ip::-1}
peerurl=$ip:2380
clienturl=$ip:2379
etcdname=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
clusterpeerurl=""

EC2_Region=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
EC2_Region=${EC2_Region::-1}

registry_instances=$(aws ec2 describe-instances \
--region $EC2_Region \
--filters "Name=tag:Purpose,Values=Service Registry" \
--query 'Reservations[*].Instances[*].[InstanceId,PrivateIpAddress]' \
--output text) 


index=0

for record in $registry_instances ;
	do 
		index=$((index+1))
		out=$(( $index % 2 ))
   		if [ $out -eq 1 ]
   			then
				clusterpeerurl="$clusterpeerurl$record="
   		else
			 clusterpeerurl="${clusterpeerurl}http://${record}:2380,"
   		fi
done

clusterpeerurl=${clusterpeerurl::-1}

echo $clusterpeerurl

curl -s http://204.204.1.139:2379/v2/members -XPOST \
-H "Content-Type: application/json" -d "{\"peerURLs\":[\""${peerurl}"\"]}"


export ETCD_NAME="$etcdname"
export ETCD_INITIAL_CLUSTER="$clusterpeerurl"
export ETCD_INITIAL_CLUSTER_STATE=existing

#curl http://ServiceRegistryELB-977958502.us-east-1.elb.amazonaws.com:2379/v2/members -XPOST \
#-H "Content-Type: application/json" -d '{"peerURLs":["$peerurl"]}'


./etcd --name $etcdname --initial-advertise-peer-urls $peerurl \
--listen-peer-urls $peerurl \
--listen-client-urls $clienturl \
--advertise-client-urls $clienturl \
--initial-cluster-token service-discovery-client
