# Viam SDK with AWS Lambda
This repository provides examples for how to use the Viam Robotics Python SDK within an AWS Lamdba, enabling robot control from the cloud.

# Prerequisites
1. Install [Docker](https://www.docker.com/products/docker-desktop/)
1. Create an AWS account or use an existing account where you have permissions to modify AWS Lambda, API Gateway, and Identity and Access Management.
1. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
1. Authenticate your computer with the AWS CLI, usually using [aws configure, or some other authentication option](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods)

# Build and Deploy
The following command will create a zip file containing all dependencies as well as lambda code written in lambda_functions.py. The command then uploads the .zip file to the existing AWS Lambda function.
```
make full-workflow function=<functionname>
```
See the [Makefile](Makefile) for exact commands used to copy/customize for your own needs. These steps were generated based on [AWS's guidance to create .zip archives](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).

You must run full-workflow when first starting a project and anytime you change dependencies in the requirements.txt file. To speed up development of lambda code, you can append lambda_functions.py file into the existing zip file by running:
```
make append-workflow function=<functionname>
```
# Secrets
It is important to never expose your Viam secret or domain in code or other files. This example uses AWS Parameter Store, a feature within AWS Systems Manager, to store secrets in the cloud that are accessed in runtime by the lambda. The example requires two `SecureString` to be entered into Parameter Store: `/<robot_name>/location_secret` and `/<robot_name>/robot_fqdn`. On Viam's website you can copy these values on the Code Sample tab of your robot.

# Additional Permissions for IAM Role
When you create an AWS Lambda, by default an IAM role is generated for you. This role does not have permissions to retrieve secrets stored in AWS Parameter Store. Follow these steps to add permissions using a AWS managed role, or create your own policy from strach to suit your needs.

1. Go to the Configuration tab of your AWS Lambda
1. Click on the Permissions section
1. The section will provide a link to IAM for the role that the Lambda is using. It is listed as the `Role name` of the function. Click this link to go to IAM.
1. Click on Add Permission -> Attach Policy
1. Search for `AmazonSSMReadOnlyAccess`, which is an AWS managed role that provides read only access to AWS Systems Manager.
1. Check the box next to the role to select it and click Add Permissions.

# Additional Lambda Configuration
The default timeout (3 sec) for AWS Lambda is not long enough for many robotics projects. The network traversal that is done to connect to your robot from the cloud, can take several seconds. Then, synchronous robot control will take additional time. You should set a timeout that feels appropriate for your project.

1. Go to the Configuration tab of your AWS Lambda
1. Under General configuration, click edit
1. Change the timeout to the desired value
1. Save