# EFS CSI Driver

## Reference
https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html


## Prepare environment
Fill following information in efs-env
```code
ACCOUNT_ID       # AWS Account ID
EKS_NAME         # EKS cluster name: kubectl configure get-cluster  (The first part of the name before ".")
EFS_ID           # EFS ID can be found from AWS Console or command-line:
                   aws efs describe-file-systems --query "FileSystems[*].FileSystemId" --output text
EFS_REGION       # EFS region
EFS_SECURITY_GROUPS  # EFS seucurity group which is the subnet security group which should be same as EKS
```

## Add NFS Inbound Rule
Either from the AWS Console or run the following script to add the NFS inbound rule if no such rule is present.
Allow subnets of the VPC to access port 2049 (NFS).

```code
./add-inbound-nfs-rule.sh
```


## Install EFS CSI Driver
Run following command:
```code
./install-csi-driver.sh
```
To verify
```console
helm list -n kube-system
NAME                    NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                           APP VERSION
aws-efs-csi-driver      kube-system     1               2022-08-19 17:25:53.6078326 -0400 EDT   deployed        aws-efs-csi-driver-2.2.7        1.4.0

kubectl get pod -n kube-system | grep efs-csi
efs-csi-controller-594c7f67c7-8zk72   3/3     Running   0          32h
efs-csi-controller-594c7f67c7-mncgd   3/3     Running   0          32h
efs-csi-node-8g8fk                    3/3     Running   0          32h
efs-csi-node-fp8vt                    3/3     Running   0          32h
```

## Install "aws-efs" Stroage Class
```console
kubectl apply -f storageclass.yaml
```
To verify
```code
kubectl get sc
NAME            PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
aws-efs         efs.csi.aws.com         Delete          Immediate              false                  32h
```
