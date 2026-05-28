# OmniRAG Project Structure

## Backend (FastAPI)
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   ├── endpoints.py
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── langgraph.py
│   ├── models/
│   │   └── file.py
│   ├── services/
│   │   └── file_service.py
│   ├── utils/
│   │   └── storage.py
│   └── main.py
├── requirements.txt
└── .env.example

## Frontend (Next.js)
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── upload/
│   │   └── page.tsx
│   ├── files/
│   │   └── page.tsx
│   └── chat/
│       └── page.tsx
├── components/
│   ├── FileUploader.tsx
│   ├── FileList.tsx
│   └── ChatInterface.tsx
├── lib/
│   └── api.ts
├── public/
├── styles/
│   └── globals.css
├── next.config.js
├── package.json
├── tailwind.config.ts
└── tsconfig.json

## Root
├── .env.example
└── README.md