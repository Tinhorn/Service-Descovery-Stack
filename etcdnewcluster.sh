ip=http://$(hostname -I)
ip=${ip::-1}
peerurl=$ip:2380
clienturl=$ip:2379
etcdname=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

export ETCD_NAME="$etcdname"
export ETCD_INITIAL_CLUSTER="$etcdname=$peerurl"
export ETCD_INITIAL_CLUSTER_STATE=new

./etcd --name $etcdname --initial-advertise-peer-urls $peerurl \
--listen-peer-urls $peerurl \
--listen-client-urls $clienturl \
--advertise-client-urls $clienturl \
--initial-cluster-token service-discovery-client \
