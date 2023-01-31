# Elastic Kubernetes Service (EKS)

We currently provide one EKS cluster configuration one-node-pool which as name suggested has only one node pool.
Later we will provide more configurations such as multiple node pools, horizontal scalable node pools and spot pools, etc
First define region (AWS_REGION) in aws-saml-profile. You can leave AWS_PROFILE as "default" if you configure AWS CLI with 'aws configure' which save ACCESS KEY and SECURITY KEY in 'default' section of ~/.aws/credentials.

For most of the configurations you just need modify configuration file
```code
EKS_REGION
EKS_NAME
NODE_SECURITY_GROUPS
EKS_SUBNET_IDS
VPC_SUBNETS
TAGS
```
You also can modify NODE_COUNT, NODE_TYPE, etc
To start the cluster:
```code
./start.sh
```
To stop it
```code
./delete-eks.sh
```

## one-node-pool
The EKS cluster has one node pool.
The directory include configuration file as well create/start/delete scripts
