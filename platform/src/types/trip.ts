export interface Activity {
  id: string;
  name: string;
  description: string;
  time?: string;
  duration?: string;
  cost?: number;
  category?: 'culture' | 'food' | 'nature' | 'nightlife' | 'shopping' | 'relaxation' | 'adventure';
  tags?: string[];
  story?: string;
}

export interface DaySchedule {
  morning: Activity[];
  afternoon: Activity[];
  evening: Activity[];
}

export interface Day {
  id: string;
  dayNumber: number;
  date: string;
  title: string;
  description?: string;
  schedule: DaySchedule;
  travelTip?: string;
}

export interface BudgetCategory {
  category: 'accommodation' | 'food' | 'transport' | 'activities' | 'miscellaneous';
  estimated: number;
  breakdown?: { item: string; cost: number }[];
}

export interface BudgetSummary {
  totalBudget: number;
  estimatedSpend: number;
  currency: string;
  categories: BudgetCategory[];
  dailyAverage: number;
}

export interface TravelEssentials {
  keyPhrases: { phrase: string; translation: string; pronunciation?: string }[];
  etiquetteTips: string[];
  generalAdvice: string[];
  visaRequirements?: string;
  healthRecommendations?: string[];
  packingList?: string[];
}

export interface Logistics {
  neighborhoods: { name: string; description: string; why: string }[];
  transportation: {
    airport: string;
    publicTransport: string[];
    tips: string[];
  };
  keyStations?: string[];
}

export interface FlightSegment {
  from: string;
  from_name: string;
  dep_time: string;
  to: string;
  to_name: string;
  arr_time: string;
  airline: string;
  flight_number: string;
  duration_min?: number;
}

export interface Flight {
  id: string;
  airline: string;
  flight_number: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  class: string;
  price: number;
  currency: string;
  stops: number;
  baggage_included: boolean;
  cancellation_policy: string;
  segments: FlightSegment[];
  link?: string;
  leg?: string;
  type?: string;
}

export interface SelectedActivity {
  id: string;
  name: string;
  description: string;
  type?: string;
  duration?: string;
  price?: number;
  rating?: number;
  reviews?: number;
  location?: string;
  best_time?: string;
  booking_required?: boolean;
  link?: string;
  category?: 'culture' | 'food' | 'nature' | 'nightlife' | 'shopping' | 'relaxation' | 'adventure';
  tags?: string[];
}

export interface Trip {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  adults: number;
  children: number;
  days: Day[];
  budget: BudgetSummary;
  essentials: TravelEssentials;
  logistics: Logistics;
  flights?: Flight[];
  activities?: SelectedActivity[];
  createdAt: string;
}

export interface TripPlanRequest {
  destination: string;
  destinationAirportCode?: string;
  origin?: string;
  originAirportCode?: string;
  startDate: string;
  endDate: string;
  adults: number;
  children: number;
  roundTrip: boolean;
  returnDate?: string;
  totalBudget: number;
  currency: string;
  comfortLevel: 'backpacker' | 'standard' | 'premium';
  preferredActivities: string[];
  travelPace: 'chill' | 'balanced' | 'packed';
  mustSee?: string;
}
