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
url = "https://api2.idanalyzer.com/quickscan"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-KEY": os.environ.get("X_API_KEY"),
}

class VehicleData(BaseModel):
    vin: str
    make: str
    model: str
    year: str
    license_plate: str = None
    total_fees: str = None
    reg_start: str = None
    reg_end: str = None


@app.post("/registration_card_check")
async def extract_text(file: UploadFile = File(...)):
    img_data = await file.read()
    img_b64 = base64.b64encode(img_data).decode()

    json_data = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
            "user",
            "content": [{
                "type":
                "text",
                "text":
                """Extract key vehicle registration fields from this image: VIN, make, model, year, license plate, registration dates, fees.
                   result is json."""
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            }]
        }],
        temperature=0.0)
    ocr_result = json_data.choices[0].message.content.replace("```", "").replace("json", "")
    try:
        print("ocr_result:", ocr_result)
        # Try to parse the GPT response as JSON
        vehicle_data_dict = json.loads(ocr_result)
        print("vehicle_data:", vehicle_data_dict)
        # Create a VehicleData object and fill in missing fields with defaults
        vehicle_data = VehicleData(
            vin=vehicle_data_dict.get("VIN", ""),
            make=vehicle_data_dict.get("make", ""),
            model=vehicle_data_dict.get("model", ""),
            year=vehicle_data_dict.get("year", ""),
            license_plate=vehicle_data_dict.get("license_plate", ""),
            total_fees=vehicle_data_dict.get("fees", ""),
            reg_start=vehicle_data_dict.get("registration_start", ""),
            reg_end=vehicle_data_dict.get("registration_end", ""))

        # Verify the extracted data
        verification_result = verify(vehicle_data)
        print(f"OCR_Result: {ocr_result}\nVerification: {verification_result}")
        # Return both the extracted data and verification result
        return {
            "ocr_data": vehicle_data_dict,
            "verification": verification_result
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse OCR result as JSON",
            "raw_result": ocr_result
        }
    except Exception as e:
        return {
            "error": f"Error processing data: {str(e)}",
            "raw_result": ocr_result
        }


def verify(data: VehicleData) -> Dict:
    reasons = []
    valid = True

    # VIN must be 17 characters
    if len(data.vin) != 17:
        valid = False
        reasons.append("VIN is not 17 characters long")
        return {"valid": False, "confidence": 50, "reasons": reasons}

    # Decode VIN using NHTSA API
    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{data.vin}?format=json"
    response = httpx.get(nhtsa_url)
    decoded = response.json()
    print("decoded",decoded)
    vin_info = {
        item['Variable']: item['Value']
        for item in decoded['Results'] if item['Value']
    }

    # Compare with user-provided fields
    vin_make = vin_info.get('Make', '').lower()
    vin_model = vin_info.get('Model', '').lower()
    vin_year = vin_info.get('Model Year', '')

    if vin_make and vin_make not in data.make.lower():
        valid = False
        reasons.append(f"VIN make mismatch: {vin_make} != {data.make}")

    if vin_model and vin_model not in data.model.lower():
        valid = False
        reasons.append(f"VIN model mismatch: {vin_model} != {data.model}")

    if vin_year and vin_year != data.year:
        valid = False
        reasons.append(f"VIN year mismatch: {vin_year} != {data.year}")

    # Example check: Year range
    if not (2000 <= int(data.year) <= 2025):
        valid = False
        reasons.append("Unusual vehicle year")

    # Check total fees
    try:
        fee = float(data.total_fees.replace("$", ""))
        if fee < 50 or fee > 1000:
            valid = False
            reasons.append("Total fees seem suspicious")
    except:
        reasons.append("Invalid total fees format")

    # Basic date check
    if data.reg_start == "00/00/2015":
        valid = False
        reasons.append("Invalid registration start date")
    print("Validation result:", valid)
    return {
        "valid": valid,
        "confidence": 95 if valid else 60,
        "reasons": reasons,
        "vin_decoded": vin_info
    }

@app.post("/id_card_check")
async def extract_text(file: UploadFile = File(...)):
    img_data = await file.read()
    img_b64 = base64.b64encode(img_data).decode()
    response = requests.post(url,headers=headers, json={"document": img_b64})
    print("response",response.json())
    return response.json()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
