 Python script for list AWS EC2 instance. What is current AMI ID? When this instance has created.

Input

- AWS Region

Output

- Sumary like how many instances in total?
- List of EC2 instances with AMI ID
- List of AMI ID with created date information


at our company we have the rule for rotate AMI every 90 days

This script will run with command line. It may use in Gitlab CICD scheduler or AWS Lambda we not decide yet.

Usage this script.

export AWS_PROFILE=foobar
python check_ami.py --region us-east-1
