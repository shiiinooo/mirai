# Trip Planner Platform (Frontend)

A modern React + TypeScript web application for creating personalized travel itineraries powered by AI.

## 🎨 Features

- **Interactive Trip Planning Form** - Easy-to-use form with geolocation support
- **AI-Powered Itineraries** - Generate comprehensive travel plans in minutes
- **Beautiful UI** - Clean, minimalistic design with soft sky-blue accents
- **Day-by-Day View** - Detailed schedules with activities, costs, and timing
- **Flight Information** - Real flight data with booking links
- **Budget Tracking** - Complete budget breakdown by category
- **Travel Essentials** - Key phrases, etiquette tips, and packing lists

## 🏗️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for navigation
- **TailwindCSS** for styling
- **Shadcn/ui** for UI components
- **React Hook Form** for form management
- **Zod** for validation
- **Supabase** (optional) for trip persistence

## 📁 Project Structure

```
platform/
├── src/
│   ├── components/
│   │   ├── layout/         # App shell and layouts
│   │   ├── planner/        # Trip planning form
│   │   ├── trip/           # Trip display components
│   │   └── ui/             # Reusable UI components (shadcn)
│   ├── pages/
│   │   ├── Landing/        # Landing page
│   │   ├── Planner/        # Trip planning form
│   │   └── Trip/           # Trip display page
│   ├── lib/
│   │   ├── api/            # API client and endpoints
│   │   ├── demo-data.ts    # Sample trip data
│   │   └── utils.ts        # Utility functions
│   ├── types/
│   │   └── trip.ts         # TypeScript interfaces
│   └── hooks/              # Custom React hooks
├── supabase/
│   └── migrations/         # Database migrations
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- AI Service backend running (see `ai-service/README.md`)

### Installation

1. **Install dependencies:**

```bash
cd platform
npm install
```

2. **Set up environment variables:**

Create a `.env` file in the platform directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Supabase Configuration (Optional - only if using database)
# VITE_SUPABASE_URL=https://your-project.supabase.co
# VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Running the Application

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## 📖 Usage

### Creating a Trip

1. Navigate to the home page
2. Fill out the trip planning form:
   - **Destination**: Where you want to go
   - **Dates**: Start and end dates
   - **Trip Type**: Solo, couple, friends, or family
   - **Budget**: Total budget and currency
   - **Comfort Level**: Backpacker, standard, or premium
   - **Activities**: Your interests (comma-separated)
   - **Travel Pace**: Chill, balanced, or packed
   - **Must-See**: (Optional) Specific places or experiences
3. Click "Create My Travel Plan"
4. Wait for the AI to generate your itinerary (15-30 seconds)
5. View your personalized trip handbook

### Viewing a Trip

The trip page includes five tabs:

- **Itinerary**: Day-by-day schedule with activities and meals
- **Flights**: Detailed flight information with booking links
- **Budget**: Detailed cost breakdown by category
- **Essentials**: Key phrases, etiquette tips, packing list
- **Logistics**: Transportation info and neighborhood guides

## 🔌 API Integration

The platform communicates with the AI service backend through REST API:

### Endpoints Used

- `POST /v1/trips/plan` - Generate trip itinerary
- `GET /health` - Check backend status

### API Client

The API client is located at `src/lib/api/client.ts` and handles:
- Request/response formatting
- Error handling
- Base URL configuration from environment variables

## 🗄️ Database (Optional)

The app can persist trips to Supabase for later retrieval:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the migration in `supabase/migrations/`
3. Add Supabase credentials to `.env`
4. Trips will be automatically saved after generation

## 🎨 Customization

### Styling

- TailwindCSS configuration: `tailwind.config.js`
- Global styles: `src/index.css`
- Component styles: Inline with Tailwind classes

### Components

UI components are from [shadcn/ui](https://ui.shadcn.com/). To add new components:

```bash
npx shadcn-ui@latest add [component-name]
```

### Color Scheme

The app uses a clean, minimalistic light theme with soft sky-blue accents. Modify colors in:
- `tailwind.config.js` - Theme colors
- `src/index.css` - CSS variables

Current color palette:
- Background: White to light gray (#F8F9FA to #FFFFFF)
- Accents: Soft sky blue (#60A5FA, #38BDF8)
- Text: Dark slate (#1E293B to #334155)

## 🧪 Development

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

### Format Code

```bash
npm run format
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | URL of the AI service backend | Yes |
| `VITE_SUPABASE_URL` | Supabase project URL | No |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | No |

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Other Platforms

The app is a standard Vite/React app and can be deployed to:
- Netlify
- AWS Amplify
- GitHub Pages
- Any static hosting service

**Important**: Make sure to set the `VITE_API_URL` environment variable to your deployed backend URL.

## 🤝 Integration with AI Service

The platform expects the AI service to be running and accessible. See `ai-service/README.md` for setup instructions.

**Quick Start Both Services:**

Terminal 1 (Backend):
```bash
cd ai-service
source venv/bin/activate
uvicorn api:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd platform
npm run dev
```

## 📄 License

See project root for license information.

