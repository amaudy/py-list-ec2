# AWS AMI Management Scripts

This repository contains Python scripts for managing and monitoring AWS AMI (Amazon Machine Image) information to support AMI rotation policies.

## Scripts

### 1. check_ami.py
Lists all EC2 instances and their AMI information, including compliance with 90-day rotation policy.

**Features:**
- Lists all EC2 instances with AMI IDs and launch times
- Shows AMI creation dates and age in days
- Displays summary statistics (total instances, unique AMIs)
- Identifies AMIs older than 90 days that need rotation

**Usage:**
```bash
export AWS_PROFILE=your-profile
python check_ami.py --region us-east-1
```

**Output:**
- Summary of total instances and unique AMIs
- Table of EC2 instances with AMI information
- Table of AMI details with creation dates and age
- Warning for AMIs exceeding 90-day policy

### 2. latest_ami.py
Finds the latest AMI based on name pattern and owner filters.

**Features:**
- Searches for latest AMI by creation date
- Filters by owner (default: private/self)
- Name pattern matching (default: `*company-abc*`)
- Detailed AMI information display
- 90-day rotation compliance check

**Usage:**
```bash
# Basic usage with default pattern
python latest_ami.py --region us-east-1

# Custom name pattern
python latest_ami.py --region us-east-1 --name-pattern "*my-company*"

# Different owner (account ID)
python latest_ami.py --region us-east-1 --owner 123456789012
```

**Output:**
- Latest AMI details (ID, name, creation date, age)
- AMI metadata (architecture, virtualization, encryption)
- Tags and block device mappings
- Rotation policy compliance status

## Prerequisites

### AWS Configuration
1. Configure AWS credentials using one of these methods:
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - IAM roles (for EC2/Lambda execution)
   - AWS profiles: `export AWS_PROFILE=your-profile`

2. Required IAM permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeImages"
            ],
            "Resource": "*"
        }
    ]
}
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Installation

1. Clone or download the scripts
2. Install dependencies:
   ```bash
   pip install boto3
   ```
3. Configure AWS credentials
4. Run the scripts with appropriate region parameter

## AMI Rotation Policy

These scripts support a **90-day AMI rotation policy** where:
- AMIs older than 90 days are flagged for rotation
- Warnings are displayed for non-compliant AMIs
- This helps maintain security and compliance standards

## Regional Considerations

**Important:** AMI IDs are region-specific. The same AMI will have different IDs in different regions. You must:
- Run scripts separately for each region
- Copy AMIs between regions if needed (each copy gets a new ID)
- Consider multi-region deployment strategies

## Use Cases

### GitLab CI/CD
```yaml
check_ami_rotation:
  image: python:3.9
  script:
    - pip install boto3
    - python check_ami.py --region $AWS_REGION
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

### AWS Lambda
These scripts can be packaged and deployed as Lambda functions for:
- Scheduled AMI compliance checks
- Automated AMI discovery
- Integration with monitoring systems

### Local Development
```bash
# Check all instances in a region
export AWS_PROFILE=dev
python check_ami.py --region us-east-1

# Find latest company AMI
python latest_ami.py --region us-east-1 --name-pattern "*company-abc*"
```

## Troubleshooting

### Common Issues

1. **No AMIs found**
   - Verify region parameter
   - Check AWS credentials and permissions
   - Confirm AMI name pattern is correct
   - Ensure AMIs are owned by the specified account

2. **Permission denied**
   - Verify IAM permissions for `ec2:DescribeInstances` and `ec2:DescribeImages`
   - Check AWS profile/credentials configuration

3. **Import errors**
   - Install boto3: `pip install boto3`
   - Verify Python version (3.6+ recommended)

### Debug Mode
Add error handling or boto3 debug logging if needed:
```python
import boto3
boto3.set_stream_logger('boto3', logging.DEBUG)
```

## Contributing

When adding new features:
1. Follow existing code patterns
2. Add appropriate error handling
3. Update this README
4. Test with multiple regions and scenarios