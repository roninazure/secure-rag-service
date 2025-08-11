import os
import asyncio
from typing import Optional
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")

        self.test_mode = not all([self.aws_access_key_id, self.aws_secret_access_key])

        if not self.test_mode:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            self.bedrock_client = None

    async def _generate_test_response(self, message: str) -> str:
        """Generate test response when AWS credentials are not available"""
        message_lower = message.lower()
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm a mock response from the AI service. Please configure your AWS credentials to get live responses."
        else:
            return f"This is a test response for your message: '{message}'."

    async def generate_response(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Generate AI response using AWS Bedrock or test mode"""
        if self.test_mode:
            return await self._generate_test_response(message)

        prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "stopSequences": [],  # Titan doesn't support custom stop sequences in this format
                "temperature": 0.5,
                "topP": 0.9
            }
        })

        try:
            response = await asyncio.to_thread(
                self.bedrock_client.invoke_model,
                modelId=self.model_id,
                body=body,
                accept='application/json',
                contentType='application/json'
            )

            response_body = json.loads(response.get('body').read())
            
            # Try different response formats for different models
            text_response = ""
            if 'results' in response_body:
                text_response = response_body['results'][0]['outputText']
            elif 'outputText' in response_body:
                text_response = response_body['outputText']
            elif 'content' in response_body:
                text_response = response_body['content'][0]['text']
            else:
                text_response = str(response_body)
            
            # Clean up response - remove duplicate patterns
            text_response = text_response.strip()
            
            # Remove any trailing incomplete sentences after stop sequences
            stop_sequences = [
                "\n\nUser:", "\n\nAssistant:", "\n\nQuestion:", "\n\nAnswer:", 
                "\n\nBot:", "\n\nClient:", "\n\nCurrent question:", "\nUser:",
                "Based on the following information", "--- CONTEXT START ---",
                "IMPORTANT:", "Answer (based ONLY on the context provided):"
            ]
            for stop_seq in stop_sequences:
                if stop_seq in text_response:
                    text_response = text_response.split(stop_seq)[0]
            
            # Remove duplicate assistant responses and role prefixes
            if "Assistant:" in text_response:
                parts = text_response.split("Assistant:")
                text_response = parts[-1].strip()  # Take the last part after Assistant:
            
            # Remove any question echoing patterns
            if text_response.startswith("Based on"):
                # Find where the actual answer starts
                answer_markers = ["\n\n", ". ", ":\n"]
                for marker in answer_markers:
                    if marker in text_response:
                        parts = text_response.split(marker, 1)
                        if len(parts) > 1 and len(parts[1]) > 20:  # Ensure we have a substantial answer
                            text_response = parts[1]
                            break
            
            # Clean up any remaining formatting artifacts
            text_response = text_response.replace("Answer:", "").strip()
            text_response = text_response.replace("Response:", "").strip()
            
            return text_response.strip()

        except ClientError as e:
            print(f"Bedrock API Error: {e}")
            return f"Error communicating with AWS Bedrock: {e.response['Error']['Message']}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred. Please check the server logs."
    
    async def generate_legal_response(self, message: str) -> str:
        """
        Generate AI response with legal professional context
        """
        system_prompt = """You are an AI assistant designed to help legal professionals. 
        You provide helpful, accurate, and professional responses while being mindful of:
        - Legal terminology and concepts
        - Professional communication standards
        - Confidentiality and privacy considerations
        - The importance of human oversight in legal matters
        
        Always remind users that AI assistance should supplement, not replace, professional legal judgment."""
        
        return await self.generate_response(message, system_prompt)

# Global instance
ai_service = AIService()
