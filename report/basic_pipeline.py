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
from report import ReportData
from pydantic import BaseModel
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

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

    def analyze_images(self, before_image_path: str, after_image_path: str) -> List[Dict]:
        """Analyze before and after images using OpenAI Vision API to identify new trash items."""
        try:
            encoded_before = self.encode_image(before_image_path)
            encoded_after = self.encode_image(after_image_path)

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "I will show you two images of a trash area - one before and one after. Please identify only the NEW waste items that appear in the second image and categorize them as trash, recycle, or compost. Return as a JSON list. If there are duplicate new items, list each multiple times. Format: {\"items\": [{\"name\": \"item1\", \"mass_kg\": 0.5, \"proper_category\": \"recycle\"}, {\"name\": \"item2\", \"mass_kg\": 0.3, \"proper_category\": \"compost\"}, ...]}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_before}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_after}"
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
            print(f"Error analyzing images: {str(e)}")
            return []

    def get_recommendations(self, trash_items: List[Dict], compost_items: List[Dict], recycle_items: List[Dict]) -> List[str]:
        """Get recommendations based on trash items, compost items, and recycle items."""
        prompt = "Based on the items identified in the trash, compost, and recycling bins, provide recommendations to reduce waste and improve recycling rates. Include suggestions for reducing waste, composting, and recycling more effectively."
        print(trash_items)
        print(compost_items)
        print(recycle_items)
        trash_prompt = "Trash items: " + ", ".join(item["item"] for item in trash_items)
        compost_prompt = "Compost items: " + ", ".join(item["item"] for item in compost_items)
        recycle_prompt = "Recyclable items: " + ", ".join(item["item"] for item in recycle_items)
        items = [trash_prompt, compost_prompt, recycle_prompt]

        recommendations = []

        for item in items:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": item}
                ],
                # response_format={"type": "json_object"},
                max_tokens=300
            )

            recommendation = response.choices[0].message.content
            recommendations.append(recommendation)
        print(recommendations)
        return recommendations
        

    # async def get_emissions_for_item(self, session: aiohttp.ClientSession, item: Dict) -> Dict:
    #     """Get landfill emissions data for a single item using Perplexity API."""
    #     headers = {
    #         "Authorization": f"Bearer {self.perplexity_api_key}",
    #         "Content-Type": "application/json"
    #     }
        
    #     payload = {
    #         "model": "sonar",
    #         "messages": [
    #             {
    #                 "role": "system",
    #                 "content": "Return a JSON object with a single field 'emissions_per_kg' containing the numeric value."
    #             },
    #             {
    #                 "role": "user",
    #                 "content": f"What is the carbon footprint (in CO2 equivalent) per kilogram of disposing {item['name']} in a landfill? Return only the numeric value in kg CO2e/kg."
    #             }
    #         ],
    #         "response_format": {
    #             "type": "json_schema",
    #             "json_schema": {"schema": EmissionsResponse.model_json_schema()}
    #         },
    #         "max_tokens": 100,
    #         "temperature": 0.2,
    #         "top_p": 0.9
    #     }

    #     try:
    #         async with session.post(self.perplexity_url, headers=headers, json=payload) as response:
    #             if response.status != 200:
    #                 error_text = await response.text()
    #                 print(f"API Error for {item['name']}: Status {response.status}, Response: {error_text}")
    #                 return {"item": item['name'], "mass_kg": item['mass_kg'], "proper_category": item['proper_category'], "landfill_emissions": None}
                
    #             result = await response.json()
    #             if 'choices' not in result:
    #                 print(f"Unexpected API response for {item['name']}: {result}")
    #                 return {"item": item['name'], "mass_kg": item['mass_kg'], "proper_category": item['proper_category'], "landfill_emissions": None}
                
    #             try:
    #                 perplexity_response = result['choices'][0]['message']['content']
                    
    #                 # Use OpenAI to parse and structure the response
    #                 openai_response = self.openai_client.chat.completions.create(
    #                     model="gpt-4o-mini",
    #                     messages=[
    #                         {
    #                             "role": "system",
    #                             "content": "Parse the input and return a JSON object with a single field 'emissions_per_kg' containing just the numeric value. Remove any units or extra text. If there's no value in the input, use a reasonable estimate."
    #                         },
    #                         {
    #                             "role": "user",
    #                             "content": perplexity_response
    #                         }
    #                     ],
    #                     response_format={"type": "json_object"},
    #                     max_tokens=100
    #                 )
                    
    #                 content = json.loads(openai_response.choices[0].message.content)
    #                 emissions_per_kg = content['emissions_per_kg']
    #                 total_emissions = emissions_per_kg * item['mass_kg']
                    
    #                 return {
    #                     "item": item['name'],
    #                     "mass_kg": item['mass_kg'],
    #                     "proper_category": item['proper_category'],
    #                     "landfill_emissions": total_emissions
    #                 }
    #             except (ValueError, KeyError, json.JSONDecodeError) as e:
    #                 print(f"Error parsing response for {item['name']}: {result['choices'][0]['message']['content']}")
    #                 return {"item": item['name'], "mass_kg": item['mass_kg'], "proper_category": item['proper_category'], "landfill_emissions": None}
                    
    #     except Exception as e:
    #         print(f"Error getting emissions for {item['name']}: {str(e)}")
    #         return {"item": item['name'], "mass_kg": item['mass_kg'], "proper_category": item['proper_category'], "landfill_emissions": None}

    async def get_emissions_for_item(self, session: aiohttp.ClientSession, item: Dict) -> Dict:
        """Get landfill emissions data for a single item using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "Return a JSON object with a single field 'emissions_per_kg' containing the numeric value."
                },
                {
                    "role": "user",
                    "content": f"What is the carbon footprint (in CO2 equivalent) per kilogram of disposing {item['name']} in a landfill? Return only the numeric value in kg CO2e/kg."
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
            async with session.post(
                self.perplexity_url, headers=headers, json=payload, ssl=ssl_context
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"API Error for {item['name']}: Status {response.status}, Response: {error_text}")
                    return {
                        "item": item['name'],
                        "mass_kg": item['mass_kg'],
                        "proper_category": item['proper_category'],
                        "landfill_emissions": None
                    }

                result = await response.json()
                if 'choices' not in result:
                    print(f"Unexpected API response for {item['name']}: {result}")
                    return {
                        "item": item['name'],
                        "mass_kg": item['mass_kg'],
                        "proper_category": item['proper_category'],
                        "landfill_emissions": None
                    }

                try:
                    perplexity_response = result['choices'][0]['message']['content']
                    
                    print(f"Perplexity response: {perplexity_response}")

                    openai_response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Parse the input and return a JSON object with a single field 'emissions_per_kg' containing just the numeric value."
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
                        "proper_category": item['proper_category'],
                        "landfill_emissions": total_emissions
                    }
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error parsing response for {item['name']}: {result['choices'][0]['message']['content']}")
                    return {
                        "item": item['name'],
                        "mass_kg": item['mass_kg'],
                        "proper_category": item['proper_category'],
                        "landfill_emissions": None
                    }

        except Exception as e:
            print(f"Error getting emissions for {item['name']}: {str(e)}")
            return {
                "item": item['name'],
                "mass_kg": item['mass_kg'],
                "proper_category": item['proper_category'],
                "landfill_emissions": None
            }
        
    async def get_all_emissions(self, items: List[Dict]) -> List[Dict]:
        """Get landfill emissions data for all items concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                task = self.get_emissions_for_item(session, item)
                tasks.append(task)
                await asyncio.sleep(0.5)
            results = await asyncio.gather(*tasks)
            return results

    def analyze_trash(self, before_image_path: str, after_image_path: str) -> ReportData:
        """Analyze new items in trash and calculate emissions impact."""
        items = self.analyze_images(before_image_path, after_image_path)
        
        if not items:
            return ReportData(0, 0, 0, [], [], [], 0.0, 0.0, 0.0)

        emissions_data = asyncio.run(self.get_all_emissions(items))
        
        # Group items by their proper category
        trash_items = [item for item in emissions_data if item["proper_category"] == "trash"]
        compost_items = [item for item in emissions_data if item["proper_category"] == "compost"]
        recycle_items = [item for item in emissions_data if item["proper_category"] == "recycle"]
        
        # Calculate scope 2 emissions for each category going to landfill
        trash_emissions = sum(item["landfill_emissions"] for item in trash_items 
                            if item["landfill_emissions"] is not None)
        compost_emissions = sum(item["landfill_emissions"] for item in compost_items 
                              if item["landfill_emissions"] is not None)
        recycle_emissions = sum(item["landfill_emissions"] for item in recycle_items 
                              if item["landfill_emissions"] is not None)
        
        recommendations = self.get_recommendations(trash_items, compost_items, recycle_items)

        return ReportData(
            numTrash=len(trash_items),
            numCompost=len(compost_items),
            numRecycle=len(recycle_items),
            trashNames=[item["item"] for item in trash_items],
            recycleNames=[item["item"] for item in recycle_items],
            compostNames=[item["item"] for item in compost_items],
            trashEmissions=trash_emissions,
            compostInTrashEmissions=compost_emissions,
            recycleInTrashEmissions=recycle_emissions,
            recommendations=recommendations
        )

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize with your API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)
    
    # Example usage with before and after images
    #before_image_path = "sample-images/IMG_6702.jpg"
    before_image_path = "../sample-images/notrash.jpg"
    after_image_path = "../sample-images/IMG_6703.jpg"
    report_data = analyzer.analyze_trash(before_image_path, after_image_path)
    
    print("\nAnalysis Results:")
    print(f"Number of trash items: {report_data.numTrash}")
    print(f"Number of compost items: {report_data.numCompost}")
    print(f"Number of recycle items: {report_data.numRecycle}")
    print(f"Trash items: {', '.join(report_data.trashNames)}")
    print(f"Recyclable items: {', '.join(report_data.recycleNames)}")
    print(f"Compostable items: {', '.join(report_data.compostNames)}")
    print(f"CO2 impact from trash: {report_data.trashEmissions:.3f} kg CO2e")
    print(f"CO2 impact from compost in trash: {report_data.compostInTrashEmissions:.3f} kg CO2e")
    print(f"CO2 impact from recyclables in trash: {report_data.recycleInTrashEmissions:.3f} kg CO2e")

if __name__ == "__main__":
    main()