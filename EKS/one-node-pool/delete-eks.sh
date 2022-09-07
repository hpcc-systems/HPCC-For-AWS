#!/bin/bash
WORK_DIR=$(dirname $0)
EKS_DIR=$(cd ${WORK_DIR}/..;  pwd); cd $WORK_DIR
source ${EKS_DIR}/aws-saml-profile
${EKS_DIR}/aws-get-saml

source ${WORK_DIR}/configuration
[[ -n "$1" ]] && source $1
[[ -n "$2" ]] && source $2

# Delete Kubernetes Cluster
echo "eksctl delete cluster ${EKS_NAME} ... "
time eksctl delete cluster ${EKS_NAME} -p $AWS_PROFILE -w
