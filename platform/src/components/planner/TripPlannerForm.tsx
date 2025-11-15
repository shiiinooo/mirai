import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { planTrip } from '@/lib/api/trips';
import { TripPlanRequest } from '@/types/trip';
import { AirportInput } from './AirportInput';

const formSchema = z.object({
  destination: z.string().min(2, 'Destination is required'),
  destinationAirportCode: z.string().optional(),
  origin: z.string().optional(),
  originAirportCode: z.string().optional(),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  adults: z.number().min(1).max(10),
  children: z.number().min(0).max(10),
  roundTrip: z.boolean(),
  returnDate: z.string().optional(),
  totalBudget: z.string().min(1, 'Budget is required'),
  currency: z.string(),
  comfortLevel: z.enum(['backpacker', 'standard', 'premium']),
  preferredActivities: z.string(),
  travelPace: z.enum(['chill', 'balanced', 'packed']),
  mustSee: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface TripPlannerFormProps {
  onLoadingChange?: (isLoading: boolean) => void;
}

export function TripPlannerForm({ onLoadingChange }: TripPlannerFormProps) {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      adults: 1,
      children: 0,
      roundTrip: false,
      currency: 'EUR',
      comfortLevel: 'standard',
      travelPace: 'balanced',
      preferredActivities: '',
      origin: '',
    },
  });

  // Origin is handled via form state, no need to watch separately

  // Detect user's current location on component mount
  useEffect(() => {
    const detectLocation = async () => {
      if (!navigator.geolocation) {
        toast.info('Geolocation is not supported by your browser');
        return;
      }

      setIsDetectingLocation(true);

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;
            
            // Reverse geocoding to get city name
            const response = await fetch(
              `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
            );
            
            if (response.ok) {
              const data = await response.json();
              const city = data.city || data.locality || '';
              const country = data.countryName || '';
              const locationString = city && country ? `${city}, ${country}` : city || country || '';
              
              if (locationString) {
                setValue('origin', locationString);
                toast.success(`Detected your location: ${locationString}`);
              } else {
                toast.warning('Could not determine your city name');
              }
            } else {
              // Fallback: use coordinates
              setValue('origin', `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
              toast.info('Using coordinates as location');
            }
          } catch (error) {
            console.error('Error getting location:', error);
            toast.error('Failed to detect your location');
          } finally {
            setIsDetectingLocation(false);
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
          toast.warning('Location access denied. You can enter your origin manually.');
          setIsDetectingLocation(false);
        }
      );
    };

    detectLocation();
  }, [setValue]);

  const roundTrip = watch('roundTrip');
  const currency = watch('currency');
  const comfortLevel = watch('comfortLevel');
  const travelPace = watch('travelPace');

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    onLoadingChange?.(true);

    try {
      const request: TripPlanRequest = {
        destination: data.destination,
        destinationAirportCode: data.destinationAirportCode || undefined,
        origin: data.origin || undefined,
        originAirportCode: data.originAirportCode || undefined,
        startDate: data.startDate,
        endDate: data.endDate,
        adults: data.adults,
        children: data.children,
        roundTrip: data.roundTrip,
        returnDate: data.roundTrip ? data.returnDate : undefined,
        totalBudget: parseFloat(data.totalBudget),
        currency: data.currency,
        comfortLevel: data.comfortLevel,
        preferredActivities: data.preferredActivities
          .split(',')
          .map((a) => a.trim())
          .filter(Boolean),
        travelPace: data.travelPace,
        mustSee: data.mustSee,
      };

      const trip = await planTrip(request);
      toast.success('Trip plan generated successfully!');
      navigate(`/trip/${trip.id}`);
    } catch (error) {
      console.error('Error planning trip:', error);
      toast.error('Failed to generate trip plan. Please try again.');
      setIsLoading(false);
      onLoadingChange?.(false);
    }
  };

  return (
    <Card className="bg-white border-slate-200 shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl text-slate-900">Plan Your Journey</CardTitle>
        <CardDescription className="text-slate-600">
          Tell us about your dream trip and we'll create a personalized travel handbook
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Trip Basics</h3>

            <AirportInput
              label="Origin (Where you're flying from)"
              placeholder="e.g., New York, London, Paris..."
              value={watch('origin')}
              airportCode={watch('originAirportCode')}
              onChange={(city, code) => {
                setValue('origin', city);
                setValue('originAirportCode', code);
              }}
              disabled={isDetectingLocation}
            />

            <AirportInput
              label="Destination (Where you're going)"
              placeholder="e.g., Tokyo, Paris, New York..."
              value={watch('destination')}
              airportCode={watch('destinationAirportCode')}
              onChange={(city, code) => {
                setValue('destination', city);
                setValue('destinationAirportCode', code);
              }}
            />
            {errors.destination && (
              <p className="text-sm text-red-500">{errors.destination.message}</p>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate" className="text-slate-700">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  {...register('startDate')}
                  className="bg-white border-slate-200"
                />
                {errors.startDate && (
                  <p className="text-sm text-red-500">{errors.startDate.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="endDate" className="text-slate-700">End Date</Label>
                <Input
                  id="endDate"
                  type="date"
                  {...register('endDate')}
                  className="bg-white border-slate-200"
                />
                {errors.endDate && (
                  <p className="text-sm text-red-500">{errors.endDate.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <Label>Travelers</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="adults" className="text-slate-700">Adults</Label>
                  <Input
                    id="adults"
                    type="number"
                    min="1"
                    max="10"
                    {...register('adults', { valueAsNumber: true })}
                    className="bg-white border-slate-200"
                  />
                  {errors.adults && (
                    <p className="text-sm text-red-500">{errors.adults.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="children" className="text-slate-700">Children</Label>
                  <Input
                    id="children"
                    type="number"
                    min="0"
                    max="10"
                    {...register('children', { valueAsNumber: true })}
                    className="bg-white border-slate-200"
                  />
                  {errors.children && (
                    <p className="text-sm text-red-500">{errors.children.message}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="roundTrip"
                  checked={roundTrip}
                  onChange={(e) => setValue('roundTrip', e.target.checked)}
                  className="h-4 w-4 text-sky-600 border-slate-300 rounded focus:ring-sky-500"
                />
                <Label htmlFor="roundTrip" className="text-slate-700 cursor-pointer">
                  Round Trip
                </Label>
              </div>

              {roundTrip && (
                <div className="space-y-2">
                  <Label htmlFor="returnDate" className="text-slate-700">Return Date</Label>
                  <Input
                    id="returnDate"
                    type="date"
                    {...register('returnDate')}
                    className="bg-white border-slate-200"
                    min={watch('startDate')}
                  />
                  {errors.returnDate && (
                    <p className="text-sm text-red-500">{errors.returnDate.message}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          <Separator className="bg-slate-200" />

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Budget</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="totalBudget" className="text-slate-700">Total Budget</Label>
                <Input
                  id="totalBudget"
                  type="number"
                  placeholder="3000"
                  {...register('totalBudget')}
                  className="bg-white border-slate-200"
                />
                {errors.totalBudget && (
                  <p className="text-sm text-red-500">{errors.totalBudget.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="currency" className="text-slate-700">Currency</Label>
                <Select value={currency} onValueChange={(value) => setValue('currency', value)}>
                  <SelectTrigger className="bg-white border-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EUR">EUR (€)</SelectItem>
                    <SelectItem value="USD">USD ($)</SelectItem>
                    <SelectItem value="GBP">GBP (£)</SelectItem>
                    <SelectItem value="JPY">JPY (¥)</SelectItem>
                    <SelectItem value="AUD">AUD (A$)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-700">Comfort Level</Label>
              <RadioGroup value={comfortLevel} onValueChange={(value) => setValue('comfortLevel', value as any)}>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { value: 'backpacker', label: 'Backpacker', desc: 'Budget-friendly' },
                    { value: 'standard', label: 'Standard', desc: 'Balanced comfort' },
                    { value: 'premium', label: 'Premium', desc: 'Luxury experience' },
                  ].map((level) => (
                    <div key={level.value} className="flex items-start space-x-2">
                      <RadioGroupItem value={level.value} id={level.value} className="mt-1" />
                      <div className="cursor-pointer" onClick={() => setValue('comfortLevel', level.value as any)}>
                        <Label htmlFor={level.value} className="capitalize cursor-pointer font-medium text-slate-900">
                          {level.label}
                        </Label>
                        <p className="text-xs text-slate-500">{level.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>
          </div>

          <Separator className="bg-slate-200" />

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Preferences</h3>

            <div className="space-y-2">
              <Label htmlFor="preferredActivities" className="text-slate-700">Preferred Activities</Label>
              <Input
                id="preferredActivities"
                placeholder="e.g., culture, food, nature, nightlife (comma-separated)"
                {...register('preferredActivities')}
                className="bg-white border-slate-200"
              />
              <p className="text-xs text-slate-500">Separate multiple activities with commas</p>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-700">Travel Pace</Label>
              <RadioGroup value={travelPace} onValueChange={(value) => setValue('travelPace', value as any)}>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { value: 'chill', label: 'Chill', desc: 'Relaxed, fewer activities' },
                    { value: 'balanced', label: 'Balanced', desc: 'Mix of rest and exploration' },
                    { value: 'packed', label: 'Packed', desc: 'Maximum experiences' },
                  ].map((pace) => (
                    <div key={pace.value} className="flex items-start space-x-2">
                      <RadioGroupItem value={pace.value} id={`pace-${pace.value}`} className="mt-1" />
                      <div className="cursor-pointer" onClick={() => setValue('travelPace', pace.value as any)}>
                        <Label htmlFor={`pace-${pace.value}`} className="capitalize cursor-pointer font-medium text-slate-900">
                          {pace.label}
                        </Label>
                        <p className="text-xs text-slate-500">{pace.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-2">
              <Label htmlFor="mustSee" className="text-slate-700">Must-See / Must-Do (Optional)</Label>
              <Textarea
                id="mustSee"
                placeholder="Any specific places or experiences you don't want to miss?"
                {...register('mustSee')}
                className="bg-white border-slate-200 min-h-[100px]"
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-sky-400 hover:bg-sky-500 text-white shadow-lg shadow-sky-200/50"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating your perfect trip...
              </>
            ) : (
              'Create My Travel Plan'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
