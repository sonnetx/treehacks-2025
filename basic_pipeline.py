import os
import json
import base64
from typing import List, Dict
import requests
from openai import OpenAI
import asyncio
import aiohttp
from dotenv import load_dotenv

class TrashAnalyzer:
    def __init__(self, openai_api_key: str, perplexity_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.perplexity_api_key = perplexity_api_key
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"

    def analyze_image(self, image_path: str) -> List[str]:
        """Analyze image using OpenAI Vision API to identify trash items."""
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare the message for GPT-4 Vision
            response = self.openai_client.chat.completions.create(
                #model="gpt-4-vision-preview",
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please identify all trash/waste items in this image and return them as a JSON list. Format: {\"items\": [\"item1\", \"item2\", ...]}",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            # Parse the response to get trash items
            content = response.choices[0].message.content
            trash_items = json.loads(content)["items"]
            return trash_items

        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return []

    async def get_emissions_for_item(self, session: aiohttp.ClientSession, item: str) -> Dict:
        """Get carbon emissions data for a single trash item using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"What is the carbon footprint (in CO2 equivalent) per kilogram of disposing {item} in a landfill? Return only the numeric value in kg CO2e/kg."
        
        data = {
            "model": "mixtral-8x7b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with session.post(self.perplexity_url, headers=headers, json=data) as response:
                result = await response.json()
                emissions = float(result['choices'][0]['message']['content'].strip())
                return {"item": item, "emissions": emissions}
        except Exception as e:
            print(f"Error getting emissions for {item}: {str(e)}")
            return {"item": item, "emissions": None}

    async def get_all_emissions(self, trash_items: List[str]) -> List[Dict]:
        """Get carbon emissions data for all trash items concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_emissions_for_item(session, item) for item in trash_items]
            results = await asyncio.gather(*tasks)
            return results

    def analyze_trash(self, image_path: str) -> Dict:
        """Complete analysis of trash image including emissions data."""
        # Get trash items from image
        trash_items = self.analyze_image(image_path)
        
        if not trash_items:
            return {"error": "No trash items detected in image"}

        # Get emissions data for all items
        emissions_data = asyncio.run(self.get_all_emissions(trash_items))
        
        # Calculate total emissions
        total_emissions = sum(item["emissions"] for item in emissions_data if item["emissions"] is not None)
        
        return {
            "items": emissions_data,
            "total_emissions": total_emissions,
            "unit": "kg CO2e/kg"
        }

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize with your API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)
    
    # Example usage
    image_path = "trashbin.jpg"
    results = analyzer.analyze_trash(image_path)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()