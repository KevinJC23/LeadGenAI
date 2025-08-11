# B2B Lead Generation AI Platform

An enhanced Web Application to help users find potential customers and integrates Generative AI to create personalized messages through an AI Outreach Message Generator that can improving the efficiency to reaching potential companies.

## Overview

B2B Lead Generation AI Web Application leverages publicly available business data based on companies industry and location to identify high-quality leads. This platform also implements an AI Outreach Message Generator as the solution to help users create a message to potential clients or companies more faster, saving time, and effort. The AI generates a personalized message based on company details selected by user. 

<img width="1918" height="906" alt="LeadGenAI" src="https://github.com/user-attachments/assets/59c4ca9f-6fb6-41b9-ac29-c2e238a05096" />
<img width="1919" height="907" alt="AIOutreachMessageGenerator" src="https://github.com/user-attachments/assets/0b756541-d77e-41d8-9890-f6dab2124346" />

## Feature Analysis 
Strengths:
- Multi-source lead collection from both Apollo API and Yellow Pages, improving coverage and data accuracy.
- AI-powered outreach message generator that adapts tone, message type, and personalization level.
- Supports multiple outreach channels: cold email, LinkedIn message, and cold call scripts.
- Fallback message generation ensures no lead is left without an outreach attempt.

Limitations:
- Apollo API requires an API key or authenticated scraping session, limiting data access for some users.
- Web scraping depends on site structure stability; changes in Yellow Pages HTML may require code updates.
- AI message quality depends on the accuracy of input data; incomplete lead data may reduce personalization effectiveness.

## Strategic Development Focus
Using **Quality First Approach** to focus on improving the AI Outreach Message Generator by:
- Enhancing personalization through multi-level customization (low, medium, high).
- Expanding message type support (cold email, LinkedIn message, cold call scripts).
- Implementing a quality analysis feature that scores AI-generated messages.

Value Added:
- Increased likelihood of positive response due to targeted and personalized outreach.
- Reduced time for sales teams to craft effective initial messages.
- Flexibility for different outreach channels without rewriting core logic.

The improvements align with real-world business needs by:
- Helping sales teams scale outreach without sacrificing personalization.
- Reducing manual effort while maintaining quality.
- Offering adaptability for different industries, company sizes, and communication channels.

## Dataset

The data is collected through both API and Wesbite Scraping from two different main sources:
- **Apollo API:** Provides access to available public business and contact information. This requires either Apollo API key or authenticated scraping session to gather that information.
- **Scraping from Yellow Pages Website:** Provide an additional information that may not be available in the Apollo API. Data is gathered by using Python Playwright library, following by ethical scraping practices by implementing respectful delays to avoid sending to many request in a short time which can overload the target server and respecting site terms of service. 

## Data Preprocessing

After collecting data from two different sources, several processing steps are applied to ensure data quality through the step below:
- **Data Cleaning:** Removing or skipping some entries without essential fields.
- **Text Normalization:** Stripping extra spaces from company names, addresses, and contact numbers using ``.strip()``.
- **Missing Value Standarization:** Filling missing values with ``'N/A'`` when data is not available.
- **Field Combination:** Merging the street address and city into a single location field.
- **Field Derivation:** Extracting the ``domain`` from ``website_url`` to make it easier to match data between source.
- **Filtering:** Including only companies that match the industry & location specified by the user.

## Model Selection
AI Outreach Message Generator developed uses Google Gemini 1.5 Flash, a transformer-based generative model optimized for fast, high-quality text generation. 

Rationale for selection:
- Speed: Optimized for fast response times, suitable for interactive applications.
- Context Handling: Processes structured lead data to create relevant, personalized messages.
- Flexibility: Supports multiple message types and tone adjustments.
- Integration: Seamlessly integrates with Python backend via google.generativeai SDK.

## Performance Evaluation
The AI component is evaluated based on both technical output quality and business impact:
- Message Quality Analysis: AI scoring based on personalization, clarity, engagement, and call-to-action effectiveness.
- Fallback Reliability: Automatic generation of template-based fallback messages if AI fails.
- Lead Matching Accuracy: Validating that leads meet specified industry and location criteria.
- User Feedback Loop: Iteratively improving AI performance using real-world response data.

## Setup Instruction

### Prerequisites
- Node.js v18+ and npm – JavaScript runtime and package manager for the Frontend.
- pnpm (Package Manager) – Alternative package manager for faster and efficient installs.
- Python v3.9+ – Programming language for the Backend.
- Venv for Python Backend - For managing Python Backend dependencies.
- Apollo API Key - Required for accessing Apollo API data.
- Gemini API Key - Required for the AI Outreach Message Generator.

### Clone the Repository
```
# Clone LeadGenAI Repository
git clone https://github.com/KevinJC23/LeadGenAI.git
```

### Backend Setup (BE)
```
# Go to the Backend Directory
cd BE

# Create a Python Virtual Environment
python -m venv venv

# Activate the Virtual Environment
source venv/bin/activate    # For Mac/Linux
venv\Scripts\activate       # For Windows

# Install Backend Dependencies
pip install -r requirements.txt
```

Create a `.env` file in the BE/ directory with the following contents:
```
# Apollo API Key for Accessing Business Data
APOLLO_API_KEY=your_apollo_api_key

# Gemini API Key for AI Outreach Message Generator
GEMINI_API_KEY=your_gemini_api_key

# Delay (in Seconds) Between Scraping Requests to Avoid Overloading the Server
SCRAPING_DELAY=2
```

Run the Backend server with Uvicorn:
```
# Start the Backend with auto-reload Enabled for Development
uvicorn main:app --reload
```

### Frontend Setup (FE)
```
# Go to the Frontend Directory
cd FE

# Install pnpm Globally (Package Manager)
npm install -g pnpm

# Install All Project Dependencies Listed in package.json
pnpm install
```

Install Additional Depedencies
```
# Utility for Merging Tailwind CSS Classes
npm install tailwind-merge

# Icon Library
npm install lucide-react

# Radix UI Components
npm install @radix-ui/react-checkbox
npm install @radix-ui/react-select
npm install @radix-ui/react-slot class-variance-authority
npm install @radix-ui/react-label
npm install @radix-ui/react-tabs
```

Create a `.env` file in the FE/ directory with the following content:
```
# Backend API base URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the Frontend development server:
```
# Start the Frontend with pnpm in Development Mode
pnpm dev

or

# Start the Frontend with npm in Development Mode
npm run dev
```

### Docker Setup 
This project includes a Dockerfile for both the Backend and Frontend, along with a docker-compose.yaml file to run them together. If you want to run this project using Docker, make sure to install both Docker and Docker Compose on your system.

Create .env Files
```
# Backend (BE/.env)
APOLLO_API_KEY=your_apollo_api_key
GEMINI_API_KEY=your_gemini_api_key
SCRAPING_DELAY=2

# Frontend (FE/.env)
NEXT_PUBLIC_API_URL=http://backend:8000
```

Build and Run with Docker
```
# From the root folder (where docker-compose.yaml is located):
docker compose up --build

# Access the Application
Frontend → http://localhost:3000
Backend → http://localhost:8000
```

Stop the Containers
```
docker compose down
```

## Folder Structure
Frontend (Next.js) & Backend (Python)
```
LEADGEN-AI/
│
├── BE/                               # Backend - API & Business Logic
│   ├── api/                          # API Route Definitions & Initialization
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── core/                         # Core Configuration & Constants
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── constants.py
│   │
│   ├── models/                       # Data Models & Schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── services/                     # Business Logic & Service Layer
│   │   ├── __init__.py
│   │   ├── ai_outreach_service.py
│   │   ├── apollo_client.py
│   │   ├── data_transformer.py
│   │   ├── export_service.py
│   │   └── scraper_service.py
│   │
│   ├── venv/                         # Python Virtual Environment
│   ├── Dockerfile                    # Backend Docker Configuration
│   ├── main.py                       # Main Application Entry Point
│   └── requirements.txt              # Python Dependencies
│
├── FE/                               # Frontend - User Interface
│   ├── public/                       # Public Assets
│   │   └── favicon.ico
│   │
│   ├── src/                          # Source Code
│   │   ├── app/                      # Main Application Structure
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   │
│   │   ├── components/               # Reusable UI Components
│   │   │   ├── ui/                   # Shared UI Elements
│   │   │   │   ├── alert.tsx
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── checkbox.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── label.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   └── textarea.tsx
│   │   │   ├── aioutreachgenerator.tsx
│   │   │   └── leadgenerator.tsx
│   │   │
│   │   ├── contents/                 # Static Data & Options
│   │   │   ├── index.ts
│   │   │   ├── industries.ts
│   │   │   └── locations.ts
│   │   │
│   │   └── lib/                      # API Calls & Utilities
│   │       ├── api.ts
│   │       └── utils.ts
│   │
│   ├── .env                          # Environment Variables
│   ├── Dockerfile                    # Frontend Docker Configuration
│   ├── package.json                  # Node.js Dependencies
│   ├── next.config.js                # Next.js Configuration
│   └── tsconfig.json                 # TypeScript Configuration
│
├── docker-compose.yaml               # Docker Compose File
└── README.md                         # Markdown
```
