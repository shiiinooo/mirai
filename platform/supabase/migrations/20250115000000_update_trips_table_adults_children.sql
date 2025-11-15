/*
  # Update trips table to use adults/children instead of trip_type

  1. Changes
    - Add `adults` column (integer, NOT NULL, default 1)
    - Add `children` column (integer, NOT NULL, default 0)
    - Make `trip_type` nullable (for backward compatibility with existing data)
    - Remove CHECK constraint on `trip_type` since it's no longer required

  2. Migration Strategy
    - Add new columns with defaults
    - Update existing rows to have default values
    - Make trip_type nullable
    - Drop the CHECK constraint
*/

-- Add new columns with defaults
ALTER TABLE trips 
  ADD COLUMN IF NOT EXISTS adults integer NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS children integer NOT NULL DEFAULT 0;

-- Make trip_type nullable (for backward compatibility)
ALTER TABLE trips 
  ALTER COLUMN trip_type DROP NOT NULL;

-- Drop the CHECK constraint on trip_type since it's no longer required
ALTER TABLE trips 
  DROP CONSTRAINT IF EXISTS trips_trip_type_check;

-- Update existing rows to have default values if they don't already
UPDATE trips 
SET 
  adults = 1,
  children = 0
WHERE adults IS NULL OR children IS NULL;

