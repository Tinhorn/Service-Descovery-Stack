#!/usr/bin/python


import boto3
import logging
import sys
from sys import argv

def main(argv):

	try:
		instance_id = argv[1]
		logger.info("The instance this script is running on  is " + instance_id)

		ec2 = boto3.resource('ec2',region_name='us-east-1')
		ec2Client = boto3.client('ec2',region_name='us-east-1')


		instance = ec2.Instance(id=instance_id)
		logger.info('Getting instances with the tag: "Service Registry"')
		response = ec2Client.describe_instances(Filters=[{'Name': 'tag:Purpose', 'Values': ['Service Registry',]},{"Name" : "instance-state-name", 'Values': ['running',]}])
		serviceRegistryReservations = response['Reservations']

		logging.info("Creating cluuster script...")
		if len(serviceRegistryReservations) == 1:
			logging.info("There was only one instance; which means there is no existing cluster")
			create_new_cluster(instance)
		else:
			sync_to_cluster(instance,serviceRegistryReservations)
	
	except:
		logging.info("Something went wrong ")
		logging.info(sys.exc_info())
		sys.exit(1)
		
def create_new_cluster(instance):
	logger.info("Creating new cluster script")

	peerurl = "http://{}:2380".format(instance.private_ip_address)
	clienturl = "http://{}:2379".format(instance.private_ip_address)
	target = open("etcdcluster.sh", 'w')
	target.truncate()

	#setting peerurl
	write_line_to_file(target,"export ETCD_NAME={}".format(instance.id))

	#setting clienturl
	write_line_to_file(target,"export ETCD_INITIAL_CLUSTER={}={}".format(instance.id,peerurl))

	#Setting the new cluster flag
	write_line_to_file(target,"export ETCD_INITIAL_CLUSTER_STATE=new")

	write_line_to_file(target,"cd /etc/etcd/")
	write_line_to_file(target,"\n")

	#starting etcd
	write_line_to_file(target,"nohup ./etcd --initial-advertise-peer-urls {0} --listen-peer-urls {0} --listen-client-urls {1} --advertise-client-urls {1} --initial-cluster-token service-discovery-client &".format(peerurl,clienturl))

	write_line_to_file(target,"\n")
	logger.info("Done writing file")

def sync_to_cluster(instance,serviceRegistryReservations):
	logger.info("Creating sync cluster script with peers")
	peerurl = "http://{}:2380".format(instance.private_ip_address)
	clienturl = "http://{}:2379".format(instance.private_ip_address)
	clientpeerurl = ""

	for reservation in serviceRegistryReservations :
		for srInstance in reservation["Instances"]:
			clientpeerurl += "{}=http://{}:2380,".format(srInstance["InstanceId"],srInstance["PrivateIpAddress"])
			
	clientpeerurl = clientpeerurl[:-1]
	
	logger.info("Clientpeer url: {}".format(clientpeerurl))
	logger.info("Instance id: {}".format(instance.id))

	target = open("etcdcluster.sh", 'w')
	target.truncate()
	
	
	#Adding the host machine to the cluster
	
	write_line_to_file(target,'curl -s http://internal-Service-Registry-Internal-ELB-1537977493.us-east-1.elb.amazonaws.com:2379/v2/members -XPOST -H "Content-Type: application/json" -d \'{{"peerURLs":["{0}"]}}\''.format(peerurl))

	#setting peerurl
	write_line_to_file(target,"export ETCD_NAME={}".format(instance.id))

      #setting clienturl
	write_line_to_file(target,"export ETCD_INITIAL_CLUSTER={}".format(clientpeerurl))

      #Setting the new cluster flag
	write_line_to_file(target,"export ETCD_INITIAL_CLUSTER_STATE=existing")

	write_line_to_file(target,"cd /etc/etcd/")
	write_line_to_file(target,"\n")
	

	#starting etcd
	write_line_to_file(target,"nohup ./etcd --initial-advertise-peer-urls {0} --listen-peer-urls {0} --listen-client-urls {1} --advertise-client-urls {1} --initial-cluster-token service-discovery-client &".format(peerurl,clienturl))
	write_line_to_file(target,"\n")
	logger.info("Done writing file")


def write_line_to_file(target,line):
	target.write(line)
	target.write("\n")

def validate_args(argv):
	if len(argv) < 2:
		logging.info("No argument, Have to specify the instance id")
		sys.exit(1)

if __name__ == "__main__":
	logging.basicConfig(filename='bootstrap.log')
	logger = logging.getLogger("BootStrap")
	logger.setLevel(logging.INFO)
	logger.info("\n\n"+"-"*5 + "Starting python script" + "-"*5)
	validate_args(argv)
	main(argv)
	logger.info("-"*5 + "Ending python script" + "-"*5 + '\n')