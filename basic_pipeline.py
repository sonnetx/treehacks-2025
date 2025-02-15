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
from report.report import ReportData
from pydantic import BaseModel

class EmissionsResponse(BaseModel):
    emissions_per_kg: float

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

    def analyze_image(self, image_path: str) -> List[Dict]:
        """Analyze image using OpenAI Vision API to identify trash items and their disposal category."""
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
                                "text": "Please identify all waste items in this image and categorize them as trash, recycle, or compost. Return as a JSON list. If there are duplicate items, list each multiple times. Format: {\"items\": [{\"name\": \"item1\", \"mass_kg\": 0.5, \"category\": \"recycle\"}, {\"name\": \"item2\", \"mass_kg\": 0.3, \"category\": \"compost\"}, ...]}"
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

    async def get_emissions_for_item(self, session: aiohttp.ClientSession, item: Dict) -> Dict:
        """Get carbon emissions data for a single item using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        disposal_method = "landfill" if item['category'] == "trash" else item['category']
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "Return a JSON object with a single field 'emissions_per_kg' containing the numeric value."
                },
                {
                    "role": "user",
                    "content": f"What is the carbon footprint (in CO2 equivalent) per kilogram of disposing {item['name']} in a {disposal_method}? Return only the numeric value in kg CO2e/kg."
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": EmissionsResponse.model_json_schema()}
            },
            "max_tokens": 100,
            "temperature": 0.2,
            "top_p": 0.9
        }

        try:
            async with session.post(self.perplexity_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"API Error for {item['name']}: Status {response.status}, Response: {error_text}")
                    return {"item": item['name'], "mass_kg": item['mass_kg'], "category": item['category'], "emissions_per_kg": None, "total_emissions": None}
                
                result = await response.json()
                if 'choices' not in result:
                    print(f"Unexpected API response for {item['name']}: {result}")
                    return {"item": item['name'], "mass_kg": item['mass_kg'], "category": item['category'], "emissions_per_kg": None, "total_emissions": None}
                
                try:
                    perplexity_response = result['choices'][0]['message']['content']
                    
                    # Use OpenAI to parse and structure the response
                    openai_response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Parse the input and return a JSON object with a single field 'emissions_per_kg' containing just the numeric value. Remove any units or extra text. If there's no value in the input, use a reasonable estimate."
                            },
                            {
                                "role": "user",
                                "content": perplexity_response
                            }
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=100
                    )
                    
                    content = json.loads(openai_response.choices[0].message.content)
                    emissions_per_kg = content['emissions_per_kg']
                    total_emissions = emissions_per_kg * item['mass_kg']
                    return {
                        "item": item['name'], 
                        "mass_kg": item['mass_kg'],
                        "category": item['category'],
                        "emissions_per_kg": emissions_per_kg,
                        "total_emissions": total_emissions
                    }
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error parsing response for {item['name']}: {result['choices'][0]['message']['content']}")
                    return {"item": item['name'], "mass_kg": item['mass_kg'], "category": item['category'], "emissions_per_kg": None, "total_emissions": None}
                    
        except Exception as e:
            print(f"Error getting emissions for {item['name']}: {str(e)}")
            return {"item": item['name'], "mass_kg": item['mass_kg'], "category": item['category'], "emissions_per_kg": None, "total_emissions": None}

    async def get_all_emissions(self, items: List[Dict]) -> List[Dict]:
        """Get carbon emissions data for all items concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                task = self.get_emissions_for_item(session, item)
                tasks.append(task)
                await asyncio.sleep(0.5)
            results = await asyncio.gather(*tasks)
            return results

    def analyze_trash(self, image_path: str) -> ReportData:
        """Complete analysis of trash image and return ReportData object."""
        # Get items from image with categories
        items = self.analyze_image(image_path)
        
        if not items:
            return ReportData(0, 0, 0, [], [], 0.0, 0.0)

        # Get emissions data for all items
        emissions_data = asyncio.run(self.get_all_emissions(items))
        
        # Count items by category
        num_trash = sum(1 for item in emissions_data if item["category"] == "trash")
        num_compost = sum(1 for item in emissions_data if item["category"] == "compost")
        num_recycle = sum(1 for item in emissions_data if item["category"] == "recycle")
        
        # Get names of recyclable and compostable items
        recycle_names = [item["item"] for item in emissions_data if item["category"] == "recycle"]
        compost_names = [item["item"] for item in emissions_data if item["category"] == "compost"]
        
        # Calculate potential savings and ensure they're positive
        recycle_savings = abs(sum(item["total_emissions"] for item in emissions_data 
                            if item["category"] == "recycle" and item["total_emissions"] is not None))
        compost_savings = abs(sum(item["total_emissions"] for item in emissions_data 
                            if item["category"] == "compost" and item["total_emissions"] is not None))
        
        return ReportData(
            numTrash=num_trash,
            numCompost=num_compost,
            numRecycle=num_recycle,
            recycleNames=recycle_names,
            compostNames=compost_names,
            recycleSavings=recycle_savings,
            compostSavings=compost_savings
        )

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize with your API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)
    
    # Example usage
    # image_path = "trashbin.jpg"
    image_path = "sample-images/stanfordtrash.jpg"
    report_data = analyzer.analyze_trash(image_path)
    
    print(f"Number of trash items: {report_data.numTrash}")
    print(f"Number of compost items: {report_data.numCompost}")
    print(f"Number of recycle items: {report_data.numRecycle}")
    print(f"Recyclable items: {', '.join(report_data.recycleNames)}")
    print(f"Compostable items: {', '.join(report_data.compostNames)}")
    print(f"Potential CO2 savings from recycling: {report_data.recycleSavings:.3f} kg CO2e")
    print(f"Potential CO2 savings from composting: {report_data.compostSavings:.3f} kg CO2e")

if __name__ == "__main__":
    main()