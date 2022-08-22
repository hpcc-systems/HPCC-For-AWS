#!/bin/bash
WORK_DIR=$(dirname $0)

EKS_DIR=$(cd ${WORK_DIR}/...;  pwd); cd $WORK_DIR
source ${EKS_DIR}/aws-saml-profile
#[[ -n $RISK_USERNAME ]] && ${AWS_DIR}/aws-get-saml

echo $AWS_PROFILE
source ${WORK_DIR}/configuration
[[ -n "$1" ]] && source $1
[[ -n "$2" ]] && source $2

# Create a Kubernetes Cluster
echo "eksctl create cluster  -p $AWS_PROFILE \
  --name ${EKS_NAME} \
  --region ${EKS_REGION} \
  --managed
  --nodegroup-name ${NODE_GROUP_NAME} \
  --node-type ${NODE_TYPE} \
  --nodes ${NODE_COUNT} \
  --nodes-min ${MIN_COUNT} \
  --nodes-max ${MAX_COUNT} \
  --node-volume-size ${NODE_VOLUME_SIZE} \
  ${NODE_SECURITY_GROUPS} \
  ${VPC_SUBNETS} \
  --tags \"${TAGS}\""
#  --version ${KUBERNETES_VERSION} \
#  --node-ami ${NODE_AMI} \

time eksctl create cluster -p $AWS_PROFILE \
  --name ${EKS_NAME} \
  --region ${EKS_REGION} \
  --managed \
  --nodegroup-name ${NODE_GROUP_NAME} \
  --node-type ${NODE_TYPE} \
  --nodes ${NODE_COUNT} \
  --nodes-min ${MIN_COUNT} \
  --nodes-max ${MAX_COUNT} \
  --node-volume-size ${NODE_VOLUME_SIZE} \
  ${VPC_SUBNETS} \
  --tags "${TAGS}"
#  --version ${KUBERNETES_VERSION} \
# "--managed" doesn't support "--node-ami"
#  --node-ami ${NODE_AMI} \
