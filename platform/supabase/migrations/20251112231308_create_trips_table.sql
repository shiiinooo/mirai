/*
  # Create trips table for Mirai AI Travel Planner

  1. New Tables
    - `trips`
      - `id` (uuid, primary key) - Unique identifier for each trip
      - `destination` (text) - Trip destination city/country
      - `start_date` (date) - Trip start date
      - `end_date` (date) - Trip end date
      - `trip_type` (text) - Type of trip (solo, couple, friends, family)
      - `trip_data` (jsonb) - Complete trip data including days, budget, essentials, logistics
      - `created_at` (timestamptz) - Timestamp when trip was created
      - `updated_at` (timestamptz) - Timestamp when trip was last updated

  2. Security
    - Enable RLS on `trips` table
    - Add policy for public read access (anyone can view generated trips)
    - For MVP, trips are publicly accessible via their ID

  3. Indexes
    - Add index on created_at for efficient sorting
    - Add index on destination for search functionality
*/

CREATE TABLE IF NOT EXISTS trips (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  destination text NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  trip_type text NOT NULL CHECK (trip_type IN ('solo', 'couple', 'friends', 'family')),
  trip_data jsonb NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view trips"
  ON trips
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anyone can create trips"
  ON trips
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS trips_created_at_idx ON trips(created_at DESC);
CREATE INDEX IF NOT EXISTS trips_destination_idx ON trips(destination);
