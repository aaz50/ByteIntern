# AWS Lambda Deployment Guide

This guide covers migrating from GitHub Actions to AWS Lambda for faster, more frequent job checks.

## Why AWS Lambda?

**Benefits:**
- Run every 5-15 minutes (vs 6 hours on GitHub Actions)
- Generous free tier: 1M requests/month
- True serverless - only pay for what you use
- Learn AWS (valuable for career/interviews)

**When to migrate:**
- You want to check for jobs every 5-15 minutes
- Early application is critical (first to apply advantage)
- You want to learn AWS

## Architecture Overview

```
EventBridge Rule (schedule) → Lambda Function → DynamoDB
                                      ↓
                                Email/Notification
```

**Components:**
1. **Lambda Function**: Runs your job tracker code
2. **EventBridge**: Triggers Lambda on schedule (like cron)
3. **DynamoDB**: Stores job data (replaces SQLite)
4. **IAM Role**: Permissions for Lambda

## Prerequisites

1. AWS Account (free tier eligible)
2. AWS CLI installed and configured
3. Working job tracker from Phase 1

## Step-by-Step Setup

### Step 1: Set Up AWS Account

1. Go to https://aws.amazon.com/
2. Create free tier account
3. Note: Requires credit card (won't be charged if you stay in free tier)

### Step 2: Install AWS CLI

**Mac:**
```bash
brew install awscli
```

**Windows:**
Download from: https://aws.amazon.com/cli/

**Configure:**
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

### Step 3: Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name job-tracker \
    --attribute-definitions \
        AttributeName=job_id,AttributeType=S \
    --key-schema \
        AttributeName=job_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

**Explanation:**
- `job_id` is the primary key (partition key)
- `PAY_PER_REQUEST` = pay per operation (better for low volume)
- Free tier: 25GB storage, 25 WCU/RCU

### Step 4: Implement DynamoDB Storage

Update `src/core/storage.py` to implement the `DynamoDBStorage` class:

```python
import boto3
from boto3.dynamodb.conditions import Key

class DynamoDBStorage:
    def __init__(self, table_name: str, region: str):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def init_database(self) -> None:
        # Table created via CLI/IaC
        pass
    
    def is_new_job(self, job_id: str) -> bool:
        response = self.table.get_item(Key={'job_id': job_id})
        return 'Item' not in response
    
    def add_job(self, job: Dict) -> None:
        self.table.put_item(
            Item={
                'job_id': job['id'],
                'title': job['title'],
                'company': job['company'],
                'location': job.get('location', ''),
                'url': job['url'],
                'description': job.get('description', ''),
                'posted_date': job.get('posted_date', ''),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'first_seen': datetime.now().isoformat(),
                'notified': False
            }
        )
    
    # Implement other methods...
```

### Step 5: Create Lambda Deployment Package

```bash
# Install dependencies including boto3
pip install -r requirements.txt boto3 -t package/

# Copy your source code
cp -r src package/

# Create zip
cd package
zip -r ../lambda-deployment.zip .
cd ..
```

### Step 6: Create IAM Role for Lambda

Create `trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create role:
```bash
aws iam create-role \
    --role-name job-tracker-lambda-role \
    --assume-role-policy-document file://trust-policy.json
```

Attach policies:
```bash
# Basic Lambda execution
aws iam attach-role-policy \
    --role-name job-tracker-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# DynamoDB access
aws iam attach-role-policy \
    --role-name job-tracker-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

### Step 7: Create Lambda Function

```bash
aws lambda create-function \
    --function-name job-tracker \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/job-tracker-lambda-role \
    --handler src.runners.lambda.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        EMAIL_SENDER=your-email@gmail.com,
        EMAIL_PASSWORD=your-app-password,
        EMAIL_RECIPIENT=your-email@gmail.com,
        ADZUNA_APP_ID=your-app-id,
        ADZUNA_API_KEY=your-api-key,
        DB_TYPE=dynamodb,
        DYNAMODB_TABLE=job-tracker,
        AWS_REGION=us-east-1
    }"
```

**Get your account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

### Step 8: Create EventBridge Rule

```bash
# Create rule to run every 15 minutes
aws events put-rule \
    --name job-tracker-schedule \
    --schedule-expression "rate(15 minutes)"

# Give EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name job-tracker \
    --statement-id job-tracker-event \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/job-tracker-schedule

# Add Lambda as target
aws events put-targets \
    --rule job-tracker-schedule \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:job-tracker"
```

**Schedule options:**
- `rate(5 minutes)` - Every 5 minutes (very frequent!)
- `rate(15 minutes)` - Every 15 minutes
- `rate(1 hour)` - Every hour
- `cron(0 9 * * ? *)` - 9am daily

### Step 9: Test Lambda

```bash
# Invoke manually
aws lambda invoke \
    --function-name job-tracker \
    --invocation-type RequestResponse \
    response.json

# Check output
cat response.json
```

### Step 10: Monitor

**View logs:**
```bash
# Get log streams
aws logs describe-log-streams \
    --log-group-name /aws/lambda/job-tracker \
    --order-by LastEventTime \
    --descending \
    --max-items 1

# View latest logs
aws logs tail /aws/lambda/job-tracker --follow
```

**Or use AWS Console:**
1. Go to CloudWatch → Log Groups
2. Find `/aws/lambda/job-tracker`
3. View log streams

## Cost Estimation

**Free Tier (12 months):**
- Lambda: 1M requests + 400K GB-seconds/month
- DynamoDB: 25GB storage + 25 WCU/RCU
- This is MORE than enough for job tracking

**After free tier:**
- Lambda: ~$0.20/month (if running every 15 min)
- DynamoDB: ~$1-2/month
- **Total: <$5/month**

## Updating Lambda

When you make code changes:

```bash
# Rebuild package
pip install -r requirements.txt boto3 -t package/
cp -r src package/
cd package && zip -r ../lambda-deployment.zip . && cd ..

# Update Lambda
aws lambda update-function-code \
    --function-name job-tracker \
    --zip-file fileb://lambda-deployment.zip
```

## Cleanup (if you want to delete everything)

```bash
# Remove EventBridge rule
aws events remove-targets --rule job-tracker-schedule --ids "1"
aws events delete-rule --name job-tracker-schedule

# Delete Lambda
aws lambda delete-function --function-name job-tracker

# Delete DynamoDB table
aws dynamodb delete-table --table-name job-tracker

# Delete IAM role
aws iam detach-role-policy --role-name job-tracker-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name job-tracker-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam delete-role --role-name job-tracker-lambda-role
```

## Troubleshooting

**Lambda timeout:**
- Increase timeout: `aws lambda update-function-configuration --function-name job-tracker --timeout 120`

**DynamoDB permission errors:**
- Check IAM role has DynamoDB permissions
- Verify table name matches configuration

**Environment variables not loading:**
- Check they're set in Lambda configuration
- Use AWS Console to verify

## Advanced: Infrastructure as Code

Instead of CLI commands, use Terraform or AWS SAM:

**SAM template.yaml:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  JobTrackerFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: job-tracker
      Runtime: python3.11
      Handler: src.runners.lambda.lambda_handler
      Timeout: 60
      Events:
        Schedule:
          Type: Schedule
          Properties:
            Schedule: rate(15 minutes)
      Environment:
        Variables:
          DB_TYPE: dynamodb
          DYNAMODB_TABLE: job-tracker
```

Deploy with:
```bash
sam build
sam deploy --guided
```

## Next Steps

After Lambda is working:
1. Build FastAPI backend
2. Create React frontend
3. Add more features (filtering, tracking, etc.)

---

**Questions?** Come back when you're ready for this phase!
