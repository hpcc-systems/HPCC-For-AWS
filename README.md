# HPCC-For-AWS
This repo is about how to setup Elastic Kubernetes Service (EKS), Elastic FileSystem (EFS) Conatainer Storage Interface (CSI) driver and deploy HPCC Systems Cluster.
Assume everthing is on a Linux System. It should be similar to setup on Mac OS and Windows

## Prerequisities
- Python3
- AWS Client (AWS CLI): https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html. You will need run "aws configure" with AWS ACCESS KEY and AWS SCRETE ACCESS KEY as will as default region, for example us-east-1, and output such as "text".
- eksctl: https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html
- kubectl: https://kubernetes.io/docs/tasks/tools/
- helm: https://helm.sh/docs/intro/quickstart/


## [IAM Permissions](./IAM/README.md)
Current configuration will assume you have an IAM user. We will update for federated credential without IAM user later
The IAM user requires certain policies and roles for this exercise.  See above link for more details


## EFS Server
To setup a EFS server following this link https://aws.amazon.com/getting-started/tutorials/create-network-file-system/?pg=ln&sec=hs
The document of "EFS CSI Driver" also mentions who to create a EFS server with AWS CLI.

It is very important what the subnets of EFS server must be the super set of the subnets of Kubernete cluster (of couse will be in the saqme region). Otherwise the communication will be trementous slow.

## [EKS](./EKS/README.md)
EKS directory include instruction of how to deploy EKS cluster.


## [EFS CSI Driver](./EFS-CSI/README.md)
We will cover how to prepare and install EFS CSI Driver and EFS Storage Class



## HPCC Systems Cloud Deployment
Make sure you have done for
- Prerequisities
- IAM Permissions
- EFS Server
- EKS
- EFS CSI Driver

### Get HPCC-Platform repo or Add HPCC Helm repo
git clone https://github.com/hpcc-systems/HPCC-Platform.git
cd to HPCC-Platform and checkout the proper branch or tag.
For example,
```console
git checkout tags/community_8.8.4-1
```

### Deploy EFS Storage
Following storage deployment lifecycle is kubernetes cluster. As long as storage is keeping deployed and Kubernetes is up the PV/PVC are there.

make sure aws-efs storage class deployed:
```console
kubectl get sc
NAME            PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
aws-efs         efs.csi.aws.com         Delete          Immediate              false                  29h
gp2 (default)   kubernetes.io/aws-ebs   Delete          WaitForFirstConsumer   false                  37h
```
Currently helm/example/efs is broken due the expired old EFS CSI Provider
We do provide a fix in this repo: EFS-CSI
cd to EFS-CCI directory
#cd to helm/ and run
```console
helm install awsstorage ./hpcc-efs
#helm install awsstorage examples/efs/hpcc-efs
kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                        STORAGECLASS   REASON   AGE
pvc-08469c4d-bb33-4735-a172-befbc0f63211   1Gi        RWO            Delete           Bound    default/dali-awsstorage-hpcc-efs-pvc         aws-efs                 29h
pvc-43d81313-3d41-4184-9ce5-05432e6875c6   1Gi        RWX            Delete           Bound    default/mydropzone-awsstorage-hpcc-efs-pvc   aws-efs                 29h
pvc-77a230a0-08e2-4248-9b6b-a15aa1169da6   1Gi        RWX            Delete           Bound    default/dll-awsstorage-hpcc-efs-pvc          aws-efs                 29h
pvc-7b816b62-1e98-4776-b7b7-bf5cd0738e55   1Gi        RWX            Delete           Bound    default/sasha-awsstorage-hpcc-efs-pvc        aws-efs                 29h
pvc-7df36454-4ea6-4578-af35-5457d3f98205   3Gi        RWX            Delete           Bound    default/data-awsstorage-hpcc-efs-pvc         aws-efs                 29h

kubectl get pvc
NAME                                 STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
dali-awsstorage-hpcc-efs-pvc         Bound    pvc-08469c4d-bb33-4735-a172-befbc0f63211   1Gi        RWO            aws-efs        29h
data-awsstorage-hpcc-efs-pvc         Bound    pvc-7df36454-4ea6-4578-af35-5457d3f98205   3Gi        RWX            aws-efs        29h
dll-awsstorage-hpcc-efs-pvc          Bound    pvc-77a230a0-08e2-4248-9b6b-a15aa1169da6   1Gi        RWX            aws-efs        29h
mydropzone-awsstorage-hpcc-efs-pvc   Bound    pvc-43d81313-3d41-4184-9ce5-05432e6875c6   1Gi        RWX            aws-efs        29h
sasha-awsstorage-hpcc-efs-pvc        Bound    pvc-7b816b62-1e98-4776-b7b7-bf5cd0738e55   1Gi        RWX            aws-efs        29h
```

### Deploy HPCC Systems Cluster
Make sure awsstorage is deployed.
Deploy HPCC Systems cluster as usual
In helm directory run
```code
helm install <hpcc cluster name> ./hpcc --set global.image.version=<version> -f examples/efs/values-retained-efs.yaml
```
For example,
```console
helm install myhpcc ./hpcc --set global.image.version=8.8.4 -f examples/efs/values-retained-efs.yaml
```

There is also possible to deploy HPCC Systems with auto EFS storage, i.e. without deploying awsstorage storage. In this case the PV/PVC has life-cycle of HPCC Systems cluster instead of awsstorage storage or Kubernetes cluster.
```console
helm install myhpcc ./hpcc --set global.image.version=8.8.4 -f examples/efs/values-auto-efs.yaml
```



## [Terraform](./Terraform/README.md)
To do
