#!/usr/bin/env python3
"""
AWS Latest AMI Finder Script

This script finds the latest AMI based on filters:
- Owner: private (your account's AMIs)
- Name pattern: configurable (default: *company-abc*)

Usage: python latest_ami.py --region <region> [--name-pattern <pattern>]
"""

import argparse
import boto3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


def parse_arguments():
    parser = argparse.ArgumentParser(description='Find latest AMI with filters')
    parser.add_argument('--region', required=True, help='AWS region to search')
    parser.add_argument('--name-pattern', default='*company-abc*', 
                       help='AMI name pattern to filter (default: *company-abc*)')
    parser.add_argument('--owner', default='self', 
                       help='AMI owner filter (default: self for private AMIs)')
    return parser.parse_args()


def get_latest_ami(region: str, name_pattern: str, owner: str = 'self') -> Optional[Dict[str, Any]]:
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        filters = [
            {
                'Name': 'name',
                'Values': [name_pattern]
            },
            {
                'Name': 'state',
                'Values': ['available']
            }
        ]
        
        response = ec2.describe_images(
            Owners=[owner],
            Filters=filters
        )
        
        if not response['Images']:
            return None
        
        latest_ami = max(response['Images'], 
                        key=lambda x: datetime.fromisoformat(x['CreationDate'].replace('Z', '+00:00')))
        
        return latest_ami
        
    except Exception as e:
        print(f"Error fetching AMI information: {e}")
        return None


def format_ami_info(ami: Dict[str, Any]) -> None:
    creation_date = datetime.fromisoformat(ami['CreationDate'].replace('Z', '+00:00'))
    age_days = (datetime.now(timezone.utc) - creation_date).days
    
    print(f"Latest AMI Found:")
    print(f"==================")
    print(f"AMI ID:          {ami['ImageId']}")
    print(f"Name:            {ami['Name']}")
    print(f"Description:     {ami.get('Description', 'N/A')}")
    print(f"Owner ID:        {ami['OwnerId']}")
    print(f"Architecture:    {ami['Architecture']}")
    print(f"Root Device:     {ami['RootDeviceType']}")
    print(f"Virtualization:  {ami['VirtualizationType']}")
    print(f"State:           {ami['State']}")
    print(f"Created:         {creation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Age:             {age_days} days")
    
    if 'Tags' in ami and ami['Tags']:
        print(f"Tags:")
        for tag in ami['Tags']:
            print(f"  {tag['Key']}: {tag['Value']}")
    
    print(f"\nBlock Device Mappings:")
    for mapping in ami.get('BlockDeviceMappings', []):
        device_name = mapping['DeviceName']
        if 'Ebs' in mapping:
            ebs = mapping['Ebs']
            print(f"  {device_name}: {ebs.get('VolumeSize', 'N/A')}GB "
                  f"({ebs.get('VolumeType', 'N/A')}) "
                  f"{'Encrypted' if ebs.get('Encrypted', False) else 'Not Encrypted'}")


def main():
    args = parse_arguments()
    
    print(f"Searching for latest AMI in region: {args.region}")
    print(f"Name pattern: {args.name_pattern}")
    print(f"Owner: {args.owner}")
    print("=" * 50)
    
    latest_ami = get_latest_ami(args.region, args.name_pattern, args.owner)
    
    if latest_ami:
        format_ami_info(latest_ami)
        
        creation_date = datetime.fromisoformat(latest_ami['CreationDate'].replace('Z', '+00:00'))
        age_days = (datetime.now(timezone.utc) - creation_date).days
        
        if age_days > 90:
            print(f"\n⚠️  WARNING: This AMI is {age_days} days old (>90 days)")
            print("Consider updating to a newer AMI for security compliance.")
        else:
            print(f"\n✅ AMI is within 90-day rotation policy ({age_days} days old)")
            
    else:
        print("No AMI found matching the specified criteria.")
        print("\nPossible reasons:")
        print("- No AMIs with the specified name pattern exist")
        print("- AMIs might be owned by a different account")
        print("- AMIs might be in a different region")
        print("- AMIs might be in 'pending' or 'failed' state")


if __name__ == '__main__':
    main()