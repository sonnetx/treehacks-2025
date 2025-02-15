import os
import json
import base64
from typing import List, Dict
import requests
from openai import OpenAI
import asyncio
import aiohttp
from dotenv import load_dotenv
from PIL import Image
import io

class TrashAnalyzer:
    def __init__(self, openai_api_key: str, perplexity_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.perplexity_api_key = perplexity_api_key
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"

    def encode_image(self, image_path: str) -> str:
        """Encode image as base64 string with resizing."""
        img = Image.open(image_path)
        image = img.resize((1000, 1000))  # Resize to suitable resolution
        
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            image_bytes = output.getvalue()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        return encoded_image

    def analyze_image(self, image_path: str) -> List[str]:
        """Analyze image using OpenAI Vision API to identify trash items."""
        try:
            encoded_image = self.encode_image(image_path)

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please identify all trash/waste items in this image and return them as a JSON list. If there are duplicate items, list each multiple times. Format: {\"items\": [\"item1\", \"item2\", ...]}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300
            )

            return json.loads(response.choices[0].message.content)["items"]

        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return []

    async def get_emissions_for_item(self, session: aiohttp.ClientSession, item: str) -> Dict:
        """Get carbon emissions data for a single trash item using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise. Output ONLY a single numberic value. No other explanation or comments or nuance."
                },
                {
                    "role": "user",
                    "content": f"What is the carbon footprint (in CO2 equivalent) per kilogram of disposing {item} in a landfill? Return only the numeric value in kg CO2e/kg. Do not include any other text or comments or nuance. If you cannot find the information, return a reasonable estimate (only return a single number, not any explanation)"
                }
            ],
            "max_tokens": 100,
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": None,
            "return_images": False,
            "return_related_questions": False,
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }

        try:
            async with session.post(self.perplexity_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"API Error for {item}: Status {response.status}, Response: {error_text}")
                    return {"item": item, "emissions": None}
                
                result = await response.json()
                if 'choices' not in result:
                    print(f"Unexpected API response for {item}: {result}")
                    return {"item": item, "emissions": None}
                
                try:
                    content = result['choices'][0]['message']['content'].strip()
                    # Extract just the number from the response
                    emissions = float(''.join(filter(lambda x: x.isdigit() or x == '.', content)))
                    return {"item": item, "emissions": emissions}
                except (ValueError, KeyError) as e:
                    print(f"Error parsing response for {item}: {content}")
                    return {"item": item, "emissions": None}
                    
        except Exception as e:
            print(f"Error getting emissions for {item}: {str(e)}")
            return {"item": item, "emissions": None}

    async def get_all_emissions(self, trash_items: List[str]) -> List[Dict]:
        """Get carbon emissions data for all trash items concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in trash_items:
                task = self.get_emissions_for_item(session, item)
                tasks.append(task)
                # Add a small delay between requests
                await asyncio.sleep(0.5)
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