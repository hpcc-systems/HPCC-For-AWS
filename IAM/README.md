# IAM Permissions
Make sure you have an IAM user.
Login to AWS Console. Go to IAM service. Select the user.
Make you have following policies. If not click "Add permissions" to add them
```code
AmazonEC2FullAccess
AmazonEC2ContainerServiceRole
AmazonEC2ContainerServiceforEC2Role
AmazonEKS_CNI_Policy
AmazonEKSServicePolicy
AmazonS3FullAccess
AWSCloudFormationFullAccess
```
Not all above Policies needed by EKS/EFS/HPCC deployment but nice to have

In addition add following inline policies by clicking "Add inline policy".
Again some policies may overlap with above polices. We will clean them later.

```code
EFS
EKS
IAM_READ_TAG
KMS
OIDC
```
The contents of these online policies are in current directories with extension .json
Be aware in OIDC replace the account id 446598291512 to your AWS account id.
