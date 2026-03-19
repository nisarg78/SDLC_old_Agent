# MECH Avatar Phase 2 — AWS Console Setup Guide

**Region: ca-central-1 (Canada Central)**
**Naming prefix: mechavatar-lab-cac1**

Before you start, open AWS Console and make sure you're in **ca-central-1** (top-right corner).

---

## Step 1 — S3 Bucket

1. Go to **S3** → **Create bucket**
2. Bucket name: `mechavatar-lab-cac1-s3-inbound`
3. Region: Canada (Central) ca-central-1
4. Block all public access: **ON** (checked)
5. Click **Create bucket**
6. Open the bucket → **Create folder** → create these 6 folders one by one:
   - `documents/`
   - `questions/`
   - `outputs/`
   - `processed/`
   - `chunks/`
   - `embeddings/`

---

## Step 2 — DynamoDB Tables (9 tables)

Go to **DynamoDB** → **Tables** → **Create table** for each:

### Table 1: documents-metadata
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-documents-metadata` |
| Partition key | `document_id` (String) |
| Sort key | — (none) |
| Table settings | Customize settings |
| Read/write capacity | On-demand |

Click **Create table**.

### Table 2: processing-pipeline
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-processing-pipeline` |
| Partition key | `document_id` (String) |
| Sort key | `stage` (String) |
| Capacity | On-demand |

### Table 3: deduplication-index
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-deduplication-index` |
| Partition key | `content_hash` (String) |
| Sort key | — (none) |
| Capacity | On-demand |

### Table 4: user-queries (conversation memory)
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-user-queries` |
| Partition key | `session_id` (String) |
| Sort key | `timestamp` (String) |
| Capacity | On-demand |

After creation:
1. Click the table → **Additional settings** tab
2. **Time to Live (TTL)** → **Turn on**
3. TTL attribute name: `expires_at`
4. Click **Turn on TTL**

### Table 5: system-config (query cache)
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-system-config` |
| Partition key | `cache_key` (String) |
| Sort key | — (none) |
| Capacity | On-demand |

Enable TTL → attribute: `ttl`

### Table 6: chunks-metadata
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-mech-chunks-metadata` |
| Partition key | `identifier` (String) |
| Sort key | `document_id` (String) |
| Capacity | On-demand |

### Table 7: users (authentication)
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-users` |
| Partition key | `email` (String) |
| Sort key | — (none) |
| Capacity | On-demand |

### Table 8: user-sessions
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-user-sessions` |
| Partition key | `session_id` (String) |
| Sort key | — (none) |
| Capacity | On-demand |

Enable TTL → attribute: `expires_at`

### Table 9: rate-limits
| Field | Value |
|-------|-------|
| Table name | `mechavatar-lab-cac1-rate-limits` |
| Partition key | `user_id` (String) |
| Sort key | — (none) |
| Capacity | On-demand |

Enable TTL → attribute: `ttl`

**Verify:** DynamoDB → Tables → you should see 9 tables starting with `mechavatar-lab-cac1`.

---

## Step 3 — OpenSearch Serverless

### 3.1 Create Collection

1. Go to **Amazon OpenSearch Service** → Left sidebar → **Serverless** → **Collections**
2. Click **Create collection**
3. Collection name: `mechavatar-lab-cac1-docs`
4. Collection type: **Vector search**
5. Security:
   - Encryption: **Use AWS owned key**
   - Network access: **Public** (or VPC if your Lambdas are in VPC — for now use Public to test)
6. Data access policy: Click **Create new policy**
   - Policy name: `mechavatar-lab-cac1-access`
   - Add a rule:
     - Rule name: `full-access`
     - Collections: select your collection `mechavatar-lab-cac1-docs`
     - Index permissions: select **All**
     - Principal: Your AWS account (select your IAM user/role that you're currently logged in as, AND the Lambda execution role once created)
7. Click **Create**

**Wait 2-5 minutes** for status to change from **Creating** to **Active**.

8. Once Active, copy the **Endpoint URL** (looks like: `https://xxxxxxxxxx.ca-central-1.aoss.amazonaws.com`)

**Save this URL — you need it for Lambda 04, 06, 07, and 10 environment variables.**

### 3.2 Create Indexes

You need to create 3 indexes. Use the **OpenSearch Dashboards** link from your collection.

1. From the collection page, click the **OpenSearch Dashboards URL**
2. Go to **Dev Tools** (left sidebar → wrench icon)
3. Run these three commands one at a time:

**Index 1: documents (vector + text)**
```json
PUT mechavatar-lab-cac1-documents
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 100
    }
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "engine": "nmslib",
          "parameters": { "ef_construction": 128, "m": 16 }
        }
      },
      "text": { "type": "text", "analyzer": "standard" },
      "document_id": { "type": "keyword" },
      "chunk_id": { "type": "keyword" },
      "file_name": { "type": "keyword" },
      "file_type": { "type": "keyword" },
      "content_type": { "type": "keyword" },
      "chunk_type": { "type": "keyword" },
      "page_number": { "type": "integer" },
      "section_title": { "type": "text" },
      "source_folder": { "type": "keyword" },
      "source_priority": { "type": "integer" },
      "chunk_number": { "type": "integer" },
      "word_count": { "type": "integer" },
      "has_table": { "type": "boolean" },
      "has_code": { "type": "boolean" },
      "indexed_at": { "type": "date" }
    }
  }
}
```

**Index 2: memory (vector)**
```json
PUT mechavatar-lab-cac1-memory
{
  "settings": { "index": { "knn": true } },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": { "name": "hnsw", "engine": "nmslib" }
      },
      "session_id": { "type": "keyword" },
      "content": { "type": "text" },
      "role": { "type": "keyword" },
      "timestamp": { "type": "date" }
    }
  }
}
```

**Index 3: pageindex (text only)**
```json
PUT mechavatar-lab-cac1-pageindex
{
  "mappings": {
    "properties": {
      "document_id": { "type": "keyword" },
      "page_number": { "type": "integer" },
      "heading_hierarchy": { "type": "text" },
      "section_title": { "type": "text" },
      "node_id": { "type": "keyword" }
    }
  }
}
```

---

## Step 4 — JWT Secret

1. Go to **AWS Systems Manager** → **Parameter Store** → **Create parameter**
2. Name: `/mechavatar/lab/jwt-secret`
3. Type: **SecureString**
4. Value: Generate a strong random string. You can use this: open a new browser tab, go to any random password generator, create a 64-character random string, paste it here.
5. Click **Create parameter**

**Copy this value** — you'll need it for Lambda 08's environment variable.

---

## Step 5 — IAM Role for Lambda

### 5.1 Create the Role

1. Go to **IAM** → **Roles** → **Create role**
2. Trusted entity type: **AWS service**
3. Use case: **Lambda**
4. Click **Next**
5. Search and attach these managed policies:
   - `AWSLambdaBasicExecutionRole`
   - `AWSLambdaVPCAccessExecutionRole`
6. Click **Next**
7. Role name: `mechavatar-lab-cac1-lambda-execution-role`
8. Click **Create role**

### 5.2 Add Custom Policy

1. Click on the role you just created
2. **Add permissions** → **Create inline policy**
3. Click **JSON** tab
4. Paste this (replace `ACCOUNT_ID` with your actual account ID):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDB",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:BatchGetItem"
      ],
      "Resource": "arn:aws:dynamodb:ca-central-1:ACCOUNT_ID:table/mechavatar-lab-cac1-*"
    },
    {
      "Sid": "S3",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:HeadObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::mechavatar-lab-cac1-s3-inbound",
        "arn:aws:s3:::mechavatar-lab-cac1-s3-inbound/*"
      ]
    },
    {
      "Sid": "Bedrock",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    },
    {
      "Sid": "OpenSearchServerless",
      "Effect": "Allow",
      "Action": [
        "aoss:APIAccessAll"
      ],
      "Resource": "arn:aws:aoss:ca-central-1:ACCOUNT_ID:collection/*"
    },
    {
      "Sid": "StepFunctions",
      "Effect": "Allow",
      "Action": [
        "states:StartExecution"
      ],
      "Resource": "arn:aws:states:ca-central-1:ACCOUNT_ID:stateMachine:mechavatar-lab-cac1-*"
    },
    {
      "Sid": "LambdaInvoke",
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-*"
    },
    {
      "Sid": "SSM",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter"
      ],
      "Resource": "arn:aws:ssm:ca-central-1:ACCOUNT_ID:parameter/mechavatar/*"
    },
    {
      "Sid": "CloudWatch",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

5. Policy name: `mechavatar-lab-cac1-lambda-services`
6. Click **Create policy**

**Copy the Role ARN** — looks like: `arn:aws:iam::ACCOUNT_ID:role/mechavatar-lab-cac1-lambda-execution-role`

---

## Step 6 — Lambda Layers

You need 3 layers. For each one, build the zip on your local machine first.

### Layer 1: Pydantic

On your local machine (Linux/Mac):
```bash
mkdir -p /tmp/layer1/python
pip install pydantic -t /tmp/layer1/python/
cd /tmp/layer1
zip -r layer1-pydantic.zip python/
```

Then in AWS Console:
1. **Lambda** → **Layers** → **Create layer**
2. Name: `mechavatar-lab-cac1-layer-pydantic`
3. Upload the `layer1-pydantic.zip`
4. Compatible runtimes: Python 3.11, Python 3.12
5. Click **Create**

### Layer 2: Extraction Libraries (L02 only)

```bash
mkdir -p /tmp/layer2/python
pip install pymupdf python-docx openpyxl python-pptx beautifulsoup4 lxml -t /tmp/layer2/python/
cd /tmp/layer2
zip -r layer2-extraction.zip python/
```

In Console:
1. **Lambda** → **Layers** → **Create layer**
2. Name: `mechavatar-lab-cac1-layer-extraction`
3. Upload `layer2-extraction.zip`
4. Compatible runtimes: Python 3.11, Python 3.12

### Layer 3: OpenSearch (L04, L06, L07, L10)

```bash
mkdir -p /tmp/layer3/python
pip install opensearch-py requests-aws4auth -t /tmp/layer3/python/
cd /tmp/layer3
zip -r layer3-opensearch.zip python/
```

In Console:
1. **Lambda** → **Layers** → **Create layer**
2. Name: `mechavatar-lab-cac1-layer-opensearch`
3. Upload `layer3-opensearch.zip`
4. Compatible runtimes: Python 3.11, Python 3.12

---

## Step 7 — Lambda Functions (9 functions)

For each Lambda:
1. Go to **Lambda** → **Create function**
2. Author from scratch
3. Fill in the table below
4. **Change default execution role** → Use an existing role → select `mechavatar-lab-cac1-lambda-execution-role`
5. Click **Create function**
6. Then: **Code** tab → **Upload from** → **.zip file** → upload the zipped Lambda file
7. Then: **Configuration** tab → **Environment variables** → **Edit** → add all variables from the table
8. Then: **Configuration** tab → **General configuration** → **Edit** → set Memory and Timeout
9. Then: **Code** tab → scroll down → **Layers** → **Add a layer** → **Custom layers** → select from list

### How to create each zip file

For each Lambda `.py` file, create a zip:
```bash
zip lambda_01_file_router.zip lambda_01_file_router.py
zip lambda_02_document_extractor.zip lambda_02_document_extractor.py
# ... repeat for each
```

---

### Lambda 01: File Router

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-file-router-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_01_file_router.lambda_handler` |
| Memory | 1024 MB |
| Timeout | 5 min (300 sec) |
| Layers | layer-pydantic |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `DOCUMENTS_TABLE` | `mechavatar-lab-cac1-mech-documents-metadata` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |
| `DEDUP_TABLE` | `mechavatar-lab-cac1-mech-deduplication-index` |
| `STATE_MACHINE_ARN` | `arn:aws:states:ca-central-1:ACCOUNT_ID:stateMachine:mechavatar-lab-cac1-document-processing-stepfn` |
| `BATCH_QA_LAMBDA_ARN` | `arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-batch-qa-processor-lambda` |

---

### Lambda 02: Document Extractor

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-document-extractor-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_02_document_extractor.lambda_handler` |
| Memory | 3008 MB |
| Timeout | 15 min (900 sec) |
| Layers | layer-pydantic, layer-extraction |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |
| `ENABLE_LLM_METADATA` | `true` |
| `TEXTRACT_ENABLED` | `false` |
| `ENABLE_CLAUDE_VISION_OCR` | `true` |

---

### Lambda 03: Embeddings Generator

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-embeddings-generator-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_03_embeddings_generator.lambda_handler` |
| Memory | 2048 MB |
| Timeout | 10 min (600 sec) |
| Layers | layer-pydantic |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |

---

### Lambda 04: Index Writer

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-index-writer-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_04_index_writer.lambda_handler` |
| Memory | 2048 MB |
| Timeout | 10 min (600 sec) |
| Layers | layer-pydantic, layer-opensearch |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |
| `OPENSEARCH_HOST` | `https://xxxxxxxxxx.ca-central-1.aoss.amazonaws.com` ← YOUR endpoint |
| `OPENSEARCH_INDEX` | `mechavatar-lab-cac1-documents` |
| `PAGEINDEX_INDEX` | `mechavatar-lab-cac1-pageindex` |
| `OPENSEARCH_MEMORY_INDEX` | `mechavatar-lab-cac1-memory` |

---

### Lambda 05: Metadata Updater

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-metadata-updater-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_05_metadata_updater.lambda_handler` |
| Memory | 512 MB |
| Timeout | 1 min (60 sec) |
| Layers | layer-pydantic |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `DOCUMENTS_TABLE` | `mechavatar-lab-cac1-mech-documents-metadata` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |
| `CHUNKS_METADATA_TABLE` | `mechavatar-lab-cac1-mech-chunks-metadata` |

---

### Lambda 06: Query Processor (RAG Engine)

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-query-processor-lambda` |
| Runtime | Python 3.12 |
| Handler | `lambda_06_query_processor.lambda_handler` |
| Memory | 3072 MB |
| Timeout | 5 min (300 sec) |
| Layers | layer-pydantic, layer-opensearch |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `OPENSEARCH_HOST` | `https://xxxxxxxxxx.ca-central-1.aoss.amazonaws.com` ← YOUR endpoint |
| `OPENSEARCH_INDEX` | `mechavatar-lab-cac1-documents` |
| `MEMORY_TABLE` | `mechavatar-lab-cac1-mech-user-queries` |
| `QUERY_CACHE_TABLE` | `mechavatar-lab-cac1-mech-system-config` |
| `MAX_TOKENS` | `3000` |
| `ENABLE_CROSS_ENCODER` | `true` |
| `ENABLE_ENTITY_RERANKING` | `true` |

---

### Lambda 07: Memory Processor

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-memory-processor-lambda` |
| Runtime | Python 3.12 |
| Handler | `lambda_07_memory_processor.lambda_handler` |
| Memory | 512 MB |
| Timeout | 30 sec |
| Layers | layer-opensearch |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `MEMORY_TABLE` | `mechavatar-lab-cac1-mech-user-queries` |
| `OPENSEARCH_HOST` | `https://xxxxxxxxxx.ca-central-1.aoss.amazonaws.com` ← YOUR endpoint |
| `OPENSEARCH_MEMORY_INDEX` | `mechavatar-lab-cac1-memory` |

---

### Lambda 08: Unified API Handler

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-unified-api-handler-lambda` |
| Runtime | Python 3.12 |
| Handler | `lambda_08_unified_api_handler.lambda_handler` |
| Memory | 512 MB |
| Timeout | 30 sec |
| Layers | (none needed) |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `LAMBDA_06_ARN` | `arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-query-processor-lambda` |
| `LAMBDA_07_ARN` | `arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-memory-processor-lambda` |
| `S3_BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `DOCUMENTS_TABLE` | `mechavatar-lab-cac1-mech-documents-metadata` |
| `MEMORY_TABLE` | `mechavatar-lab-cac1-mech-user-queries` |
| `SESSIONS_TABLE` | `mechavatar-lab-cac1-user-sessions` |
| `RATE_LIMIT_TABLE` | `mechavatar-lab-cac1-rate-limits` |
| `USERS_TABLE` | `mechavatar-lab-cac1-users` |
| `JWT_SECRET` | (paste the value from Step 4) |
| `JWT_EXPIRY_SECONDS` | `28800` |
| `ALLOWED_ORIGINS` | `*` |
| `ALLOW_ANONYMOUS` | `true` ← set to `false` in production |

---

### Lambda 10: Batch QA Processor

| Setting | Value |
|---------|-------|
| Function name | `mechavatar-lab-cac1-batch-qa-processor-lambda` |
| Runtime | Python 3.11 |
| Handler | `lambda_10_batch_qa_processor.lambda_handler` |
| Memory | 2048 MB |
| Timeout | 10 min (600 sec) |
| Layers | layer-pydantic, layer-opensearch |

Environment variables:

| Key | Value |
|-----|-------|
| `AWS_DEFAULT_REGION` | `ca-central-1` |
| `BUCKET_NAME` | `mechavatar-lab-cac1-s3-inbound` |
| `PIPELINE_TABLE` | `mechavatar-lab-cac1-mech-processing-pipeline` |
| `OPENSEARCH_HOST` | `https://xxxxxxxxxx.ca-central-1.aoss.amazonaws.com` ← YOUR endpoint |
| `OPENSEARCH_INDEX` | `mechavatar-lab-cac1-documents` |
| `LAMBDA_06_ARN` | `arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-query-processor-lambda` |
| `USE_LAMBDA_06` | `true` |

---

## Step 8 — Step Functions State Machine

1. Go to **Step Functions** → **Create state machine**
2. Choose **Write your workflow in code**
3. Type: **Standard**
4. Paste this definition (replace `ACCOUNT_ID` with your account ID):

```json
{
  "Comment": "MECH Avatar Document Processing Pipeline",
  "StartAt": "Extract",
  "States": {
    "Extract": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-document-extractor-lambda",
      "ResultPath": "$.extraction",
      "Next": "GenerateEmbeddings",
      "Retry": [{"ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 2, "IntervalSeconds": 5}],
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "PipelineFailed", "ResultPath": "$.error"}]
    },
    "GenerateEmbeddings": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-embeddings-generator-lambda",
      "InputPath": "$.extraction",
      "ResultPath": "$.embeddings",
      "Next": "IndexToOpenSearch",
      "Retry": [{"ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 2, "IntervalSeconds": 10}],
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "PipelineFailed", "ResultPath": "$.error"}]
    },
    "IndexToOpenSearch": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-index-writer-lambda",
      "InputPath": "$.embeddings",
      "ResultPath": "$.indexing",
      "Next": "UpdateMetadata",
      "Retry": [{"ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 2, "IntervalSeconds": 10}],
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "PipelineFailed", "ResultPath": "$.error"}]
    },
    "UpdateMetadata": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:mechavatar-lab-cac1-metadata-updater-lambda",
      "ResultPath": "$.metadata",
      "End": true,
      "Retry": [{"ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 1, "IntervalSeconds": 5}],
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "PipelineFailed", "ResultPath": "$.error"}]
    },
    "PipelineFailed": {
      "Type": "Fail",
      "Error": "PipelineError",
      "Cause": "Document processing pipeline failed"
    }
  }
}
```

5. State machine name: `mechavatar-lab-cac1-document-processing-stepfn`
6. Permissions: **Create new role** (it will auto-create a role with Lambda invoke permissions)
7. Click **Create state machine**

---

## Step 9 — VPC Endpoint for Private API Gateway

1. Go to **VPC** → **Endpoints** → **Create endpoint**
2. Name tag: `mechavatar-lab-cac1-apigw-endpoint`
3. Service category: **AWS services**
4. Search for: `com.amazonaws.ca-central-1.execute-api`
5. Select it
6. VPC: select your VPC
7. Subnets: select your private subnets (same ones where Fargate runs)
8. Security groups: select or create a security group that allows:
   - Inbound: HTTPS (443) from your Fargate security group
9. **Enable DNS name**: YES (checked)
10. Click **Create endpoint**

**Copy the VPC Endpoint ID** (starts with `vpce-`).

---

## Step 10 — Private REST API Gateway

### 10.1 Create the API

1. Go to **API Gateway** → **Create API**
2. Choose **REST API** (not HTTP API) → **Build**
3. API name: `mechavatar-lab-cac1-api`
4. Endpoint type: **Private**
5. VPC endpoint IDs: paste your `vpce-xxxxx` from Step 9
6. Click **Create API**

### 10.2 Set Resource Policy

1. In your API → left sidebar → **Resource Policy**
2. Paste this (replace `vpce-xxxxx` with your VPC endpoint ID, and `ACCOUNT_ID`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "execute-api:/*",
      "Condition": {
        "StringEquals": {
          "aws:sourceVpce": "vpce-xxxxx"
        }
      }
    }
  ]
}
```

3. Click **Save**

### 10.3 Create Proxy Resource

1. Click **Resources** in left sidebar
2. Click **/** (root)
3. **Actions** → **Create Resource**
4. Check **Configure as proxy resource**
5. Resource path: `{proxy+}`
6. Click **Create Resource**

### 10.4 Create ANY Method on {proxy+}

1. Click the `{proxy+}` resource
2. The ANY method should already be created. Click it.
3. Integration type: **Lambda Function**
4. Lambda Proxy integration: **checked**
5. Lambda Function: `mechavatar-lab-cac1-unified-api-handler-lambda`
6. Click **Save**
7. A popup asks "Add Permission" → Click **OK**

### 10.5 Also Add ANY to Root /

1. Click **/** (root resource)
2. **Actions** → **Create Method** → select **ANY** → click the checkmark
3. Integration type: **Lambda Function**
4. Lambda Proxy integration: **checked**
5. Lambda Function: `mechavatar-lab-cac1-unified-api-handler-lambda`
6. Click **Save** → **OK**

### 10.6 Deploy the API

1. **Actions** → **Deploy API**
2. Deployment stage: **[New Stage]**
3. Stage name: `dev`
4. Click **Deploy**

**Copy the Invoke URL** — it looks like: `https://xxxxxxxxxx.execute-api.ca-central-1.amazonaws.com/dev`

Note the API ID (the `xxxxxxxxxx` part) — you need this for nginx.conf.

---

## Step 11 — S3 Event Notification (connect S3 → Lambda 01)

1. Go to **S3** → click `mechavatar-lab-cac1-s3-inbound` bucket
2. **Properties** tab → scroll down to **Event notifications**
3. **Create event notification**:

**Notification 1: Documents**
- Name: `document-upload-trigger`
- Prefix: `documents/`
- Event types: check **All object create events**
- Destination: **Lambda function**
- Lambda function: `mechavatar-lab-cac1-file-router-lambda`
- Click **Save changes**

**Notification 2: Questions**
- Click **Create event notification** again
- Name: `questions-upload-trigger`
- Prefix: `questions/`
- Event types: check **All object create events**
- Destination: **Lambda function**
- Lambda function: `mechavatar-lab-cac1-file-router-lambda`
- Click **Save changes**

If you get a "permission denied" error, go to Lambda 01 → **Configuration** → **Permissions** → **Resource-based policy statements** → **Add permissions**:
- Policy statement: `s3-invoke`
- Principal: `s3.amazonaws.com`
- Source ARN: `arn:aws:s3:::mechavatar-lab-cac1-s3-inbound`
- Action: `lambda:InvokeFunction`

---

## Step 12 — Frontend (Fargate)

### 12.1 Update nginx.conf

Open `frontend/nginx/nginx.conf` and change these two lines:

```nginx
set $api_host "YOUR_API_ID.execute-api.ca-central-1.amazonaws.com";
set $api_stage "dev";
```

Replace `YOUR_API_ID` with the API ID from Step 10.6.

Also check the resolver line matches your VPC DNS (usually `10.0.0.2` for a `10.0.0.0/16` VPC).

### 12.2 Create ECR Repository

1. Go to **ECR** → **Repositories** → **Create repository**
2. Repository name: `mechavatar-lab-cac1-frontend`
3. Click **Create repository**

### 12.3 Build and Push Docker Image

On your local machine:
```bash
cd frontend/

# Login to ECR
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com

# Build
docker build -t mechavatar-frontend:latest --target production .

# Tag
docker tag mechavatar-frontend:latest ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com/mechavatar-lab-cac1-frontend:latest

# Push
docker push ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com/mechavatar-lab-cac1-frontend:latest
```

### 12.4 Create ECS Task Definition

1. Go to **ECS** → **Task definitions** → **Create new task definition**
2. Task definition family: `mechavatar-lab-cac1-frontend`
3. Launch type: **Fargate**
4. Task size: CPU = 0.25 vCPU, Memory = 0.5 GB
5. Container:
   - Name: `frontend`
   - Image: `ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com/mechavatar-lab-cac1-frontend:latest`
   - Port mappings: 80 TCP
   - Health check command: `CMD-SHELL, curl -f http://localhost/health || exit 1`
6. Click **Create**

### 12.5 Create ECS Service

1. Go to **ECS** → **Clusters** → select/create your cluster
2. **Create service**
3. Launch type: **Fargate**
4. Task definition: select `mechavatar-lab-cac1-frontend`
5. Service name: `mechavatar-lab-cac1-frontend-svc`
6. Desired tasks: 1
7. Networking:
   - VPC: your VPC
   - Subnets: private subnets (same as VPC Endpoint)
   - Security group: allow inbound 80 from ALB, outbound 443 to VPC Endpoint
8. Load balancer: select your ALB
   - Target group: create new, port 80, health check path `/health`
9. Click **Create service**

---

## Step 13 — Verification

### Test 1: Lambda 08 (direct invoke)

1. Go to **Lambda** → `mechavatar-lab-cac1-unified-api-handler-lambda`
2. **Test** tab → create test event:
```json
{
  "httpMethod": "GET",
  "path": "/personas",
  "headers": {},
  "queryStringParameters": {},
  "pathParameters": {}
}
```
3. Click **Test**
4. You should see a 200 response with 6 personas listed

### Test 2: Document Pipeline

1. Go to **S3** → `mechavatar-lab-cac1-s3-inbound`
2. Upload a small PDF to the `documents/` folder
3. Go to **Step Functions** → check your state machine for a new execution
4. Watch it go through: Extract → Embeddings → Index → Metadata
5. Each step should show green (Success)

### Test 3: Query (after documents are indexed)

1. Go to **Lambda** → `mechavatar-lab-cac1-unified-api-handler-lambda`
2. Test with:
```json
{
  "httpMethod": "POST",
  "path": "/chat/query",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"query\": \"What is this document about?\", \"session_id\": \"test-session-001\"}",
  "queryStringParameters": {},
  "pathParameters": {}
}
```

Note: For this test set `ALLOW_ANONYMOUS=true` in Lambda 08 env vars (so you don't need a JWT). Change to `false` after testing.

### Test 4: Frontend

Open your ALB URL in a browser. You should see the MECH Avatar login page.

---

## Quick Reference — All Resource Names

| Resource | Name |
|----------|------|
| S3 Bucket | `mechavatar-lab-cac1-s3-inbound` |
| DynamoDB: documents | `mechavatar-lab-cac1-mech-documents-metadata` |
| DynamoDB: pipeline | `mechavatar-lab-cac1-mech-processing-pipeline` |
| DynamoDB: dedup | `mechavatar-lab-cac1-mech-deduplication-index` |
| DynamoDB: memory | `mechavatar-lab-cac1-mech-user-queries` |
| DynamoDB: cache | `mechavatar-lab-cac1-mech-system-config` |
| DynamoDB: chunks | `mechavatar-lab-cac1-mech-chunks-metadata` |
| DynamoDB: users | `mechavatar-lab-cac1-users` |
| DynamoDB: sessions | `mechavatar-lab-cac1-user-sessions` |
| DynamoDB: rate limits | `mechavatar-lab-cac1-rate-limits` |
| OpenSearch Collection | `mechavatar-lab-cac1-docs` |
| OpenSearch: documents | `mechavatar-lab-cac1-documents` |
| OpenSearch: memory | `mechavatar-lab-cac1-memory` |
| OpenSearch: pageindex | `mechavatar-lab-cac1-pageindex` |
| Step Functions | `mechavatar-lab-cac1-document-processing-stepfn` |
| Lambda 01 | `mechavatar-lab-cac1-file-router-lambda` |
| Lambda 02 | `mechavatar-lab-cac1-document-extractor-lambda` |
| Lambda 03 | `mechavatar-lab-cac1-embeddings-generator-lambda` |
| Lambda 04 | `mechavatar-lab-cac1-index-writer-lambda` |
| Lambda 05 | `mechavatar-lab-cac1-metadata-updater-lambda` |
| Lambda 06 | `mechavatar-lab-cac1-query-processor-lambda` |
| Lambda 07 | `mechavatar-lab-cac1-memory-processor-lambda` |
| Lambda 08 | `mechavatar-lab-cac1-unified-api-handler-lambda` |
| Lambda 10 | `mechavatar-lab-cac1-batch-qa-processor-lambda` |
| API Gateway | `mechavatar-lab-cac1-api` |
| VPC Endpoint | `mechavatar-lab-cac1-apigw-endpoint` |
| IAM Role | `mechavatar-lab-cac1-lambda-execution-role` |
| SSM Parameter | `/mechavatar/lab/jwt-secret` |
| ECR Repository | `mechavatar-lab-cac1-frontend` |
| ECS Service | `mechavatar-lab-cac1-frontend-svc` |
