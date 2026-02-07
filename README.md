# 🧭 ID Card & Vehicle Registration Document Verification [Project ID: P-411]

A FastAPI service that validates vehicle registration cards and driver licenses/ID documents using OpenAI GPT-4o vision—upload an image and get structured validation with owner name, VIN, and reason.

---

## 📚 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Screenshots](#screenshots)
- [API Documentation](#api-documentation)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

---

## 🧩 About

This project addresses the need to automatically verify identity and vehicle documents in workflows (e.g. onboarding, compliance, or KYC). Instead of manual checks, you can upload an image of a registration card or ID and get a clear valid/invalid result plus extracted fields and a reason.

**Goals:**

- **Vehicle registration:** Decide if an image is a valid, unobstructed DMV-style registration (half-page, temporary, etc.) and extract owner name, VIN, and signs of officiality (seals, logos, barcodes).
- **ID / Driver license:** Decide if an image is a valid front-side photo of a driver license or ID (full document visible, readable name and license number; reject selfies, blur, or cropped images).

Both flows use GPT-4o with strict validation rules and return consistent JSON for integration into your apps.

---

## ✨ Features

- **Vehicle registration validation** – Checks for unobstructed, readable registration documents (DMV-style or temporary), extracts owner name and VIN, and reports official markers (seals, logos, barcodes).
- **ID / Driver license validation** – Validates that the image is a clear, full front-side photo of a license or ID with readable full name and license number; rejects selfies, heavy blur, or partial crops.
- **Structured JSON responses** – Both endpoints return `validate`, extracted fields, and a `reason` for easy integration.
- **Image upload API** – Accept image files (e.g. JPEG/PNG) via `multipart/form-data` for both endpoints.

---

## 🧠 Tech Stack

| Category    | Technologies |
|------------|--------------|
| **Languages** | Python |
| **Frameworks** | FastAPI |
| **AI / APIs** | OpenAI API (GPT-4o) |
| **Server** | Uvicorn (ASGI) |
| **Tools** | python-dotenv, Pydantic |

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/Phoenix-dev11/idcard_analysis.git

# Navigate to the project directory
cd idcard_analysis

# Create a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
# Start the API server
uvicorn app:app --reload
# Or: python app.py
```

Then open your browser or API client and go to:

👉 [http://localhost:8000](http://localhost:8000)

- **Interactive API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Send `POST` requests with an image file to the endpoints below (e.g. via the Swagger UI “Try it out” or curl/Postman).

---

## 🧾 Configuration

Create a `.env` file in the project root with:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

No database or other services are required; the app uses only the OpenAI API for image analysis.

---

## 🖼 Screenshots

_Add demo images, GIFs, or UI preview screenshots here (e.g. Swagger UI, sample request/response, or your frontend)._

Example placeholder:

<!-- ![API Docs](predict/result.png) -->

---

## 📜 API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/registration_card_check` | Validate a vehicle registration document image and extract owner name, VIN, and official markers. |
| **POST** | `/id_card_check` | Validate a driver license or ID image and extract full name and license number. |

Both endpoints accept a single **image file** in the request body (e.g. form field `file`).

### Response: Vehicle Registration (`/registration_card_check`)

```json
{
  "validate": true,
  "owner_name": "JOHN DOE",
  "vin": "1FTPW125X6KB43249",
  "Signature": "State seal, barcode present",
  "reason": "Document is fully visible, readable, and shows official markers."
}
```

### Response: ID / Driver License (`/id_card_check`)

```json
{
  "validate": true,
  "full_name": "JANE SMITH",
  "license_number": "D1234567",
  "reason": "Front of license is fully visible with readable name and number."
}
```

When `validate` is `false`, extracted fields may be `null` and `reason` explains why the document was rejected.

---

## 📬 Contact

- **Author:** Hiroshi Nagaya 
- **Email:** phoenixryan1111@gmail.com  
- **GitHub:** @Phoenix-dev11  
- **Website/Portfolio:** hiroshi-nagaya.vercel.app 

---

## 🌟 Acknowledgements

- [OpenAI API](https://platform.openai.com/docs) – GPT-4o vision for document image analysis  
- [FastAPI](https://fastapi.tiangolo.com/) – Modern Python web framework and automatic API docs  
- Inspiration: Document verification and KYC workflows requiring automated ID and vehicle registration checks  
