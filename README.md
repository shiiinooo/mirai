# mirai - AI-Powered Travel Planner

An intelligent travel planning application that creates fully personalized trip itineraries in minutes. Simply enter your destination, budget, dates, and preferences, and let AI handle the rest.

## ✨ Features

- **AI-Powered Itinerary Generation**: Create personalized trip plans using LangGraph multi-agent system
- **Real-Time Flight & Hotel Data**: Integration with SerpAPI for actual flight and hotel options
- **Smart Budget Management**: Automatic budget allocation and tracking across all categories
- **Comprehensive Travel Handbook**:
  - Day-by-day detailed itineraries
  - Flight information with booking links
  - Hotel recommendations
  - Activities and attractions
  - Restaurant suggestions
  - Key phrases for destination language
  - Travel tips and etiquette
  - Packing lists
- **Beautiful Modern UI**: Clean, minimalistic design with soft sky-blue accents
- **Geolocation Support**: Automatic origin detection for seamless trip planning

## 🏗️ Project Structure

```
mirai/
├── ai-service/          # Python FastAPI backend
│   ├── trip_planner/    # LangGraph multi-agent system
│   │   ├── agent.py     # Workflow orchestration
│   │   └── utils/
│   │       ├── nodes/   # Individual agent nodes
│   │       ├── state.py # State schema
│   │       └── tools.py # API integrations (SerpAPI)
│   ├── api.py          # FastAPI REST API
│   ├── transformers.py # Data transformation
│   ├── main.py         # Standalone script runner
│   └── requirements.txt
│
├── platform/           # React TypeScript frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── pages/      # Landing, Planner, Trip pages
│   │   ├── lib/        # API client, utilities
│   │   └── types/      # TypeScript definitions
│   └── package.json
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **API Keys**:
  - OpenAI API key (required)
  - SerpAPI key (required for real flight/hotel data)

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd mirai
```

2. **Set up the backend:**
```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "SERPAPI_API_KEY=your_serpapi_key_here" >> .env
```

3. **Set up the frontend:**
```bash
cd ../platform
npm install

# Create .env file (optional, defaults to localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### Running the Application

**Terminal 1 - Start Backend:**
```bash
cd ai-service
source venv/bin/activate
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd platform
npm run dev
```

Visit `http://localhost:5173` to use the application.

## 🐳 Docker Deployment

For easy deployment with Docker Compose:

1. **Create `.env` file in root:**
```bash
OPENAI_API_KEY=your_openai_key_here
SERPAPI_API_KEY=your_serpapi_key_here
VITE_API_URL=http://backend:8000
```

2. **Start services:**
```bash
docker-compose up -d --build
```

3. **Access:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

See [DOCKER.md](DOCKER.md) for detailed Docker deployment guide.

## 🔧 Configuration

### Backend Environment Variables (`ai-service/.env`)

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
SERPAPI_API_KEY=your_serpapi_key_here
```

### Frontend Environment Variables (`platform/.env`)

```bash
VITE_API_URL=http://localhost:8000
```

## 🎯 How It Works

The system uses a **LangGraph multi-agent architecture**:

1. **Parallel Data Collection** (No LLM):
   - Transport Agent: Fetches real flight data via SerpAPI
   - Accommodation Agent: Fetches hotel options via SerpAPI
   - Activities Agent: Searches for attractions and activities
   - Dining Agent: Finds restaurant recommendations
   - Key Phrases Agent: Generates essential phrases for destination language

2. **Intelligent Selection** (LLM-Powered):
   - Budget Coordinator: Selects optimal combination within budget
   - Itinerary Generator: Creates day-by-day structured itinerary

3. **Output**: Complete travel handbook with all details

## 📚 Documentation

- **Backend**: See [ai-service/README.md](ai-service/README.md) for detailed backend documentation
- **Frontend**: See [platform/README.md](platform/README.md) for frontend setup and customization

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - REST API framework
- **LangGraph** - Multi-agent workflow orchestration
- **OpenAI GPT-4** - LLM for intelligent planning
- **SerpAPI** - Real flight and hotel data
- **Pydantic** - Data validation

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **TailwindCSS** - Styling
- **Shadcn/ui** - UI component library
- **React Hook Form + Zod** - Form management and validation

## 🌐 API Endpoints

- `POST /v1/trips/plan` - Generate trip itinerary
- `GET /health` - Health check

See `http://localhost:8000/docs` for interactive API documentation.

## 🎨 Design

The application features a clean, minimalistic design with:
- Soft sky-blue color scheme (#60A5FA, #38BDF8)
- White and light gray backgrounds
- Generous whitespace
- Modern typography
- Responsive layout

## 📝 Example Request

```json
{
  "destination": "Tokyo, Japan",
  "origin": "Paris, France",
  "startDate": "2025-11-15",
  "endDate": "2025-11-20",
  "tripType": "solo",
  "totalBudget": 3000,
  "currency": "EUR",
  "comfortLevel": "standard",
  "preferredActivities": ["culture", "food", "nature"],
  "travelPace": "balanced",
  "mustSee": "Shibuya Crossing, teamLab Borderless"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[Add your license here]

## 🐛 Issues & Support

For bugs, feature requests, or questions, please open an issue in the repository.

## 🙏 Acknowledgments

- OpenAI for GPT models
- SerpAPI for travel data
- LangGraph for workflow orchestration
- Shadcn/ui for beautiful components
