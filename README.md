# Text Generation API with AWS Bedrock

This project demonstrates a minimal but production-aware **Text Generation API** built with AWS services. It leverages **Amazon Bedrock's foundation models** for generating text, while integrating **content filtering**, **usage monitoring**, and **deployment best practices** using AWS SAM.

---

## Project Summary

**Goal:** Explore advanced generative AI capabilities using AWS services, focusing on practical applications and best practices.

---

## Features

- **API Gateway + Lambda** backend
- **Text generation** using **Amazon Bedrock's `amazon.nova-micro`** model
- **Content filtering** using [Purgomalum profanity API](https://www.purgomalum.com/)
- **Usage metrics and logs** using **CloudWatch Logs + Metrics**
- **Deployed with AWS SAM** (Serverless Application Model)

---

## Project Structure 
CustomAwsLLMAPI
├── src/
│   ├── generate_text_lambda                  # structure used by AWS SAM
│   │   └── generate_text_lambda.py            # lambda handler 
│   │   └── requirements.txt  
├── requirements.txt                    # Requirements
├── README.md
├── samconfig.toml                      # File generating after building with AWS SAM
├── template.yaml                       # AWS SAM template
└── .gitignore

---

## Setup & Deployment

### Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Bedrock access enabled for your AWS account

### Deploy

```
sam build
sam deploy --guided
```

## API Usage 
To test the API endpoint run:
```
curl -X POST YOUR_API_ENDPOINT_YOU_FIND_ON_API_GATEWAY\
  -H "Content-Type: application/json" \
  -d '{"prompt": "YOUR PROMPT GOES HERE"}'  
```

### Successful Response
```
{
  "generated_text": "The ocean is a vast and mysterious place..."
}
```

### Error Responses
- 400 Bad Request (Missing prompt): 
    ```
    {
        "error": "Missing prompt"
    }
    ```
- 400 Bad Request (Filtered content):
    ```
    {
        "error": "Missing prompt"
    }
    ```
- 500 Internal Server Error:
    ```
    {
        "error": "Internal server error"
    }
    ```

---

## Security Measures 
#### Input Validation & Filtering:
- All user input is validated to check for profanity using the Purgomalum API.

- If any profane content is detected, the request is blocked before it reaches Bedrock.

#### IAM Permissions
- The Lambda function role is explicitly scoped to only invoke bedrock:InvokeModel on the amazon.nova-micro model.

- Follows the principle of least privilege.

---

## Monitoring & Metrics
### Logs
- All prompt inputs, filtered requests, and response times are logged to CloudWatch using print() statements.
- Logs include:
    - IP address (if available)

    - Prompt content

    - Whether it was blocked

    - Generation latency

#### Metrics
- Custom CloudWatch Metrics track:
    - BlockedPrompts — count of prompts filtered for profanity

    - ResponseLatency — average time taken to generate a response

#### Dashboard
- A CloudWatch Dashboard visualizes:
    - Number of Lambda invocations
    - Latency trends
    - Number of blocked prompts