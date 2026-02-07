from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import base64
import httpx
import os
import uvicorn
import json
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()
app = FastAPI()
# Replace with your OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.post("/registration_card_check")
async def extract_text(file: UploadFile = File(...)):
    img_data = await file.read()
    img_b64 = base64.b64encode(img_data).decode()
    with open("example.txt",'r') as file:
        bad_data = file.read()
    json_data = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that evaluates if an image shows a valid vehicle registration document."
        },
        # # Few-shot example (Invalid Case)
        # {
        #     "role":"user",
        #     "content":[
        #         {
        #             "type":"image_url",
        #             "image_url":{
        #             "url":f"data:image/png;base64,{bad_data}"
        #             }
        #         }]
        # },
        # {
        #     "role":"user",
        #     "content":"""
        #     {
        #         "validate": false,
        #         "owner_name": "GARCIA LOPEZ XOCHITL",
        #         "vin": "1FTPW125X6KB43249",
        #         "Signature": "Barcodes present",
        #         "reason": "Part of the document is visibly overlapped by another section of paper, obstructing original content. This violates the requirement for no obstructions or overlapping."    
        #     }"""
        #     },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Your task is to determine if it is a valid Vehicle Registration document based on the following criteria:
                Validation Rules:
                1. validate = true only if:
                    - No Part of the document is covered or obstructed by object or paper.
                    - The image clearly shows a paper or card document that includes:
                    - The Registered Owner’s Name (an individual or company).
                    - Vehicle Information, especially the VIN (Vehicle Identification Number).
                    - Acceptable document types include:
                        DMV registration cards (e.g., half-page size forms like those issued in California).
                        Temporary registration documents (e.g., paper documents taped on a windshield).
                        Critical details must be clearly readable (minor blur is acceptable, but important text must still be recognizable).
                    - The document shows signs of being official, such as:
                        State seals
                        DMV logos
                        Watermarks
                        Barcodes or QR codes
                2. validate = false if:
                    - Analyze this image and determine whether one document or paper is overlapping or covering another beneath it.If there is visible paper on top of another—such as edges, creases, or content from a hidden layer—return.
                    - The image is blurry and important text cannot be clearly read.
                    - The image is cut off or missing key information (especially if the VIN or owner name is not fully visible).
                    - The image shows a license plate, insurance card, or any non-registration document.
                Output Format:
                    {
                        "validate": true/false,
                        "owner_name": "Owner’s full name if valid, otherwise null",
                        "vin": "Vehicle Identification Number if valid, otherwise null",
                        "Signature": "Signs of being official such as state seals, DMV logos, watermarks, barcodes or QR codes if valid, otherwise null.",
                        "reason": "Explain why the document is valid or not based on the criteria above."
                    }
                """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}"
                    }
                }
                
            ]
        }
    ],
    temperature=0.0
)

    ocr_result = json_data.choices[0].message.content.replace("```",
                                                              "").replace(
                                                                  "json", "")
    result = json.loads(ocr_result)
    print(result)
    return result


@app.post("/id_card_check")
async def extract_text(file: UploadFile = File(...)):
    id_img_data = await file.read()
    id_img_b64 = base64.b64encode(id_img_data).decode()
    id_data = client.chat.completions.create(
        model='gpt-4o',
        messages=[{
            "role":
            "user",
            "content": [{
                "type":
                "text",
                "text":
                """Your task is to analyze the image and determine if it is a valid Driver License or ID photo based on the following criteria:
                    Validation Rules:
                    1. If the image is NOT a Driver License or ID photo, immediately return validate: false and provide a clear reason.
                    2.For an image to be valid, it must meet ALL these conditions:
                        It should clearly show the front side of a Driver License or ID.
                        The entire license must be visible (i.e., not cropped, cut off, or obscured).
                        Text must be readable — slight blurring is acceptable, but the information must still be recognizable as a license.
                        The full name and the license or ID number must be visible.
                    3. In this case, also image is not valid:
                        A selfie of a person holding the license (we only want a picture of the license itself).
                        A blurred or unreadable license (extremely blurry to the point where it’s not recognizable).
                        Partial images where the license is cropped or missing parts.
                    Output Format: Always respond in pure JSON format with the following structure:
                        {
                            "validate": true/false,
                            "full_name": "Full name if valid, otherwise null",
                            "license_number": "License number if valid, otherwise null",
                            "reason": "provide the reason"
                        }
                """
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{id_img_b64}"
                }
            }]
        }],
        temperature=0.0)
    id_data_result = id_data.choices[0].message.content.replace("```",
                                                                "").replace(
                                                                    "json", "")
    result = json.loads(id_data_result)
    print(result)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
