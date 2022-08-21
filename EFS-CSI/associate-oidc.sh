#!/bin/bash
WORK_DIR=$(dirname $0)

source ${WORK_DIR}/efs-env

oidc_id=$(aws eks describe-cluster --name ${EKS_NAME} --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)
echo "oidc_id: $oidc_id"
oidc_providers=$(aws iam list-open-id-connect-providers | grep $oidc_id)
if [ "${oidc_providers}" = "" ]
then
   echo "No OIDC Providers"
   echo "Try to create OIDC Provider"
   eksctl utils associate-iam-oidc-provider --cluster ${EKS_NAME} --approve
else
   echo "OIDC Providers exists:"
   echo $oidc_providers
fi
