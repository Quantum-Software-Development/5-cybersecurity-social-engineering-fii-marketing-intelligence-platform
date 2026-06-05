# MinIO Local Data Lake Setup Guide

## Objective

Create a local S3-compatible Data Lake using MinIO for storing datasets, analytical assets, and data engineering workloads.

## Prerequisites

- Docker installed
- Docker running

## Download the MinIO Image

```bash
docker pull minio/minio
```

## Create a Storage Directory

### Linux/macOS

```bash
mkdir -p ~/minio-data
```

### Windows PowerShell

```powershell
mkdir C:\minio-data
```

## Start MinIO

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v ~/minio-data:/data \
  minio/minio server /data --console-address ":9001"
```

## Verify the Container

```bash
docker ps
```

Expected container:

```text
minio
```

## Access the Web Console

```text
http://localhost:9001
```

Default credentials:

```text
Username: minioadmin
Password: minioadmin
```

## Create a Bucket

Example:

```text
bigdata-lake
```

## Upload Sample Data

Example files:

```text
funds.csv
market_data.csv
transactions.csv
```

## Test S3 API Connectivity

Install the AWS SDK:

```bash
pip install boto3
```

Example:

```python
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin"
)

print(s3.list_buckets())
```

## Validation Checklist

- MinIO container running
- Web console accessible
- Bucket created
- Files uploaded
- S3 API connectivity verified

## Summary

MinIO provides an S3-compatible object storage platform that can be used to implement a local Data Lake architecture for analytics, ETL pipelines, and machine learning workloads.
