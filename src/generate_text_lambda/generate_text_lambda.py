import json
import os
import boto3
import requests
import time

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def is_prompt_clean(prompt):
    """Call external content filtering API"""
    try:
        response = requests.get("https://www.purgomalum.com/service/containsprofanity", params={"text": prompt})
        return response.text.lower() == "false"  # API returns 'true' if profanity is found
    except Exception as e:
        print(f"[FILTER ERROR] Could not check prompt: {e}")
        return False  # Default to blocking if API fails

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        prompt = body.get("prompt", "")
        source_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")

        print(f"[RECEIVED] Prompt from {source_ip}: {prompt}")

        if not prompt:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing prompt"})
            }

        if not is_prompt_clean(prompt):
            print(f"[FILTERED] Profanity detected in prompt: {prompt}")
            print(f"[METRIC] Blocked prompt: '{prompt}' from IP: {source_ip}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Inappropriate content detected."})
            }

        # Generate with Bedrock
        bedrock_model_id = os.environ["BEDROCK_MODEL_ID"]
        bedrock_input = {
            "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]  
                    }
                ],
            "inferenceConfig": {
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        start = time.time()
        response = bedrock.invoke_model(
            modelId=bedrock_model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(bedrock_input)
        )

        response_body = response['body'].read().decode('utf-8')
        response_data = json.loads(response_body)

        # Extract the response text
        content_list = response_data.get('output', {}).get('message', {}).get('content', [])
        formatted_response = "\n".join([item.get('text', '') for item in content_list])

        print(f"[GENERATED] From {source_ip}: {formatted_response}")
        duration = time.time() - start
        print(f"[METRIC] Generation took {duration:.2f}s")

        return {
            "statusCode": 200,
            "body": json.dumps({"generated_text": formatted_response})
        }

    except Exception as e:
        print(f"[ERROR] {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }