#!/usr/bin/env python3
"""
AWS EC2 Instance and AMI Information Script

This script lists EC2 instances, their AMI information, and checks AMI age
for compliance with 90-day rotation policy.

Usage: python check_ami.py --region <region>
"""

import argparse
import boto3
from datetime import datetime, timezone
from typing import List, Dict, Any


def parse_arguments():
    parser = argparse.ArgumentParser(description='Check EC2 instances and AMI information')
    parser.add_argument('--region', required=True, help='AWS region to check')
    return parser.parse_args()


def get_ec2_instances(region: str) -> List[Dict[str, Any]]:
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2.describe_instances()
        instances = []
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] != 'terminated':
                    instances.append(instance)
        
        return instances
    except Exception as e:
        print(f"Error fetching EC2 instances: {e}")
        return []


def get_ami_info(region: str, ami_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    ec2 = boto3.client('ec2', region_name=region)
    ami_info = {}
    
    if not ami_ids:
        return ami_info
    
    try:
        response = ec2.describe_images(ImageIds=ami_ids)
        
        for image in response['Images']:
            ami_id = image['ImageId']
            creation_date = datetime.fromisoformat(image['CreationDate'].replace('Z', '+00:00'))
            
            ami_info[ami_id] = {
                'name': image.get('Name', 'Unknown'),
                'creation_date': creation_date,
                'creation_date_str': creation_date.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'age_days': (datetime.now(timezone.utc) - creation_date).days
            }
    
    except Exception as e:
        print(f"Error fetching AMI information: {e}")
    
    return ami_info


def check_ami_rotation(ami_info: Dict[str, Dict[str, Any]], rotation_days: int = 90) -> List[str]:
    old_amis = []
    
    for ami_id, info in ami_info.items():
        if info['age_days'] > rotation_days:
            old_amis.append(ami_id)
    
    return old_amis


def main():
    args = parse_arguments()
    region = args.region
    
    print(f"Checking EC2 instances in region: {region}")
    print("=" * 50)
    
    instances = get_ec2_instances(region)
    
    if not instances:
        print("No EC2 instances found or error occurred.")
        return
    
    ami_ids = list(set([instance['ImageId'] for instance in instances]))
    ami_info = get_ami_info(region, ami_ids)
    
    print(f"\nSUMMARY:")
    print(f"Total EC2 instances: {len(instances)}")
    print(f"Unique AMIs in use: {len(ami_ids)}")
    
    print(f"\nEC2 INSTANCES:")
    print("-" * 80)
    print(f"{'Instance ID':<20} {'Instance Type':<15} {'AMI ID':<15} {'Launch Time':<20}")
    print("-" * 80)
    
    for instance in instances:
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        ami_id = instance['ImageId']
        launch_time = instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{instance_id:<20} {instance_type:<15} {ami_id:<15} {launch_time:<20}")
    
    print(f"\nAMI INFORMATION:")
    print("-" * 80)
    print(f"{'AMI ID':<15} {'AMI Name':<30} {'Created':<20} {'Age (days)':<10}")
    print("-" * 80)
    
    for ami_id in sorted(ami_ids):
        if ami_id in ami_info:
            info = ami_info[ami_id]
            name = info['name'][:29] if len(info['name']) > 29 else info['name']
            created = info['creation_date_str']
            age = info['age_days']
            print(f"{ami_id:<15} {name:<30} {created:<20} {age:<10}")
        else:
            print(f"{ami_id:<15} {'Unknown':<30} {'Unknown':<20} {'Unknown':<10}")
    
    old_amis = check_ami_rotation(ami_info)
    
    if old_amis:
        print(f"\n⚠️  AMI ROTATION WARNING:")
        print(f"The following AMIs are older than 90 days and should be rotated:")
        for ami_id in old_amis:
            age = ami_info[ami_id]['age_days']
            name = ami_info[ami_id]['name']
            print(f"  - {ami_id}: {name} ({age} days old)")
    else:
        print(f"\n✅ All AMIs are within the 90-day rotation policy.")


if __name__ == '__main__':
    main()