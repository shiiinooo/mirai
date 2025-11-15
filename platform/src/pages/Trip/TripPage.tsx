import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { TripHeader } from '@/components/trip/TripHeader';
import { TripOverview } from '@/components/trip/TripOverview';
import { BudgetOverview } from '@/components/trip/BudgetOverview';
import { DayCard } from '@/components/trip/DayCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { AlertCircle, Home, ChevronLeft, ChevronRight } from 'lucide-react';
import { getTrip } from '@/lib/api/trips';
import { Trip } from '@/types/trip';
import { demoTrip } from '@/lib/demo-data';

export function TripPage() {
  const { id } = useParams<{ id: string }>();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDayIndex, setCurrentDayIndex] = useState(0);

  useEffect(() => {
    async function loadTrip() {
      if (!id) {
        setError('No trip ID provided');
        setIsLoading(false);
        return;
      }

      if (id === 'demo') {
        setTrip(demoTrip);
        setIsLoading(false);
        return;
      }

      try {
        const tripData = await getTrip(id);
        if (!tripData) {
          setError('Trip not found');
        } else {
          setTrip(tripData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trip');
      } finally {
        setIsLoading(false);
      }
    }

    loadTrip();
  }, [id]);

  if (isLoading) {
    return (
      <AppShell>
        <div className="space-y-6">
          <Skeleton className="h-32 w-full bg-slate-200" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              <Skeleton className="h-64 w-full bg-slate-200" />
              <Skeleton className="h-48 w-full bg-slate-200" />
            </div>
            <div className="lg:col-span-2">
              <Skeleton className="h-96 w-full bg-slate-200" />
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  if (error || !trip) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card className="max-w-md w-full bg-white border-slate-200 shadow-lg">
            <CardHeader>
              <div className="flex items-center gap-2 text-red-500">
                <AlertCircle className="h-5 w-5" />
                <CardTitle className="text-slate-900">Error Loading Trip</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-slate-600">{error || 'Trip not found'}</p>
              <Link to="/">
                <Button className="w-full bg-sky-400 hover:bg-sky-500 shadow-lg shadow-sky-200/50">
                  <Home className="mr-2 h-4 w-4" />
                  Back to Home
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <TripHeader trip={trip} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <TripOverview trip={trip} />
            <BudgetOverview budget={trip.budget} />

            {trip.essentials.keyPhrases.length > 0 && (
              <Card className="bg-white border-slate-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-900">Quick Essentials</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Currency</span>
                    <span className="font-medium text-slate-900">{trip.budget.currency}</span>
                  </div>
                  {trip.essentials.visaRequirements && (
                    <div className="pt-2 border-t border-slate-200">
                      <p className="text-xs text-slate-600">Visa</p>
                      <p className="text-sm text-slate-900 mt-1">
                        {trip.essentials.visaRequirements}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          <div className="lg:col-span-2">
            <Tabs defaultValue="itinerary" className="space-y-4">
              <TabsList className="bg-white border border-slate-200 shadow-sm">
                <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
                <TabsTrigger value="activities">Activities</TabsTrigger>
                <TabsTrigger value="flights">Flights</TabsTrigger>
                <TabsTrigger value="budget">Budget</TabsTrigger>
                <TabsTrigger value="essentials">Essentials</TabsTrigger>
                <TabsTrigger value="logistics">Logistics</TabsTrigger>
              </TabsList>

              <TabsContent value="itinerary" className="space-y-4">
                <div className="space-y-4">
                  <DayCard day={trip.days[currentDayIndex]} />

                  <div className="flex items-center justify-between">
                    <Button
                      variant="outline"
                      size="lg"
                      onClick={() => setCurrentDayIndex(prev => Math.max(0, prev - 1))}
                      disabled={currentDayIndex === 0}
                      className="border-2 border-slate-400 text-slate-900 bg-white hover:bg-slate-100 hover:border-sky-400 hover:text-sky-600 disabled:border-slate-300 disabled:text-slate-500 disabled:bg-slate-50 disabled:cursor-not-allowed disabled:hover:bg-slate-50 disabled:hover:border-slate-300 disabled:hover:text-slate-500"
                    >
                      <ChevronLeft className="mr-2 h-5 w-5" />
                      Previous Day
                    </Button>

                    <div className="text-center">
                      <p className="text-sm text-slate-600">
                        Day {currentDayIndex + 1} of {trip.days.length}
                      </p>
                      <div className="flex gap-1 mt-2">
                        {trip.days.map((_, index) => (
                          <button
                            key={index}
                            onClick={() => setCurrentDayIndex(index)}
                            className={`h-2 rounded-full transition-all ${
                              index === currentDayIndex
                                ? 'w-8 bg-sky-400'
                                : 'w-2 bg-slate-300 hover:bg-slate-400'
                            }`}
                            aria-label={`Go to day ${index + 1}`}
                          />
                        ))}
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      size="lg"
                      onClick={() => setCurrentDayIndex(prev => Math.min(trip.days.length - 1, prev + 1))}
                      disabled={currentDayIndex === trip.days.length - 1}
                      className="border-2 border-slate-400 text-slate-900 bg-white hover:bg-slate-100 hover:border-sky-400 hover:text-sky-600 disabled:border-slate-300 disabled:text-slate-500 disabled:bg-slate-50 disabled:cursor-not-allowed disabled:hover:bg-slate-50 disabled:hover:border-slate-300 disabled:hover:text-slate-500"
                    >
                      Next Day
                      <ChevronRight className="ml-2 h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="activities">
                <Card className="bg-white border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-slate-900">All Activities</CardTitle>
                    <p className="text-sm text-slate-600 mt-1">
                      {trip.activities?.length || 0} curated activities for your trip
                    </p>
                  </CardHeader>
                  <CardContent>
                    {trip.activities && trip.activities.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {trip.activities.map((activity) => (
                          <div
                            key={activity.id}
                            className="p-6 rounded-lg bg-slate-50 border border-slate-200 hover:border-sky-300 hover:shadow-md transition-all"
                          >
                            <div className="flex justify-between items-start mb-3">
                              <div className="flex-1">
                                <h3 className="text-lg font-semibold text-slate-900 mb-1">
                                  {activity.name}
                                </h3>
                                {activity.type && (
                                  <span className="inline-block px-2 py-1 text-xs rounded bg-sky-100 text-sky-600 border border-sky-200 mb-2">
                                    {activity.type}
                                  </span>
                                )}
                              </div>
                              {activity.rating && (
                                <div className="flex items-center gap-1 ml-2">
                                  <span className="text-sm font-semibold text-slate-900">
                                    {activity.rating.toFixed(1)}
                                  </span>
                                  <span className="text-yellow-400">★</span>
                                  {activity.reviews && (
                                    <span className="text-xs text-slate-500">
                                      ({activity.reviews})
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>

                            {activity.description && (
                              <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                                {activity.description}
                              </p>
                            )}

                            <div className="grid grid-cols-2 gap-3 mb-3">
                              {activity.duration && (
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Duration</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {activity.duration}
                                  </p>
                                </div>
                              )}
                              {activity.price !== undefined && activity.price > 0 && (
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Price</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {activity.price.toLocaleString()} {trip.budget.currency}
                                  </p>
                                </div>
                              )}
                              {activity.location && (
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Location</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {activity.location}
                                  </p>
                                </div>
                              )}
                              {activity.best_time && (
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Best Time</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {activity.best_time}
                                  </p>
                                </div>
                              )}
                            </div>

                            {activity.tags && activity.tags.length > 0 && (
                              <div className="flex flex-wrap gap-2 mb-3">
                                {activity.tags.map((tag, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-1 text-xs rounded bg-slate-200 text-slate-700"
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            )}

                            {activity.booking_required && (
                              <div className="mb-3">
                                <span className="px-2 py-1 text-xs rounded bg-amber-100 text-amber-700 border border-amber-200">
                                  Booking Required
                                </span>
                              </div>
                            )}

                            {activity.link && (
                              <Button
                                asChild
                                className="w-full bg-sky-400 hover:bg-sky-500 text-white shadow-lg shadow-sky-200/50"
                              >
                                <a
                                  href={activity.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  Learn More
                                </a>
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-slate-600">No activities available</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="flights">
                <Card className="bg-white border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-slate-900">Flight Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {trip.flights && trip.flights.length > 0 ? (
                      trip.flights.map((flight, idx) => (
                        <div
                          key={flight.id || idx}
                          className="p-6 rounded-lg bg-slate-50 border border-slate-200 space-y-4"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-lg font-semibold text-slate-900">
                                  {flight.airline} {flight.flight_number}
                                </h3>
                                {flight.leg && (
                                  <span className="px-2 py-1 text-xs rounded bg-sky-100 text-sky-600 border border-sky-200">
                                    {flight.leg}
                                  </span>
                                )}
                                {flight.type && (
                                  <span className="px-2 py-1 text-xs rounded bg-slate-200 text-slate-700">
                                    {flight.type}
                                  </span>
                                )}
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Route</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {flight.origin} → {flight.destination}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Departure</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {flight.departure_time}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Arrival</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {flight.arrival_time}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Duration</p>
                                  <p className="text-sm font-medium text-slate-900">
                                    {flight.duration}
                                  </p>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Class</p>
                                  <p className="text-sm text-slate-900">{flight.class}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Stops</p>
                                  <p className="text-sm text-slate-900">
                                    {flight.stops === 0 ? 'Direct' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Baggage</p>
                                  <p className="text-sm text-slate-900">
                                    {flight.baggage_included ? 'Included' : 'Not included'}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-600 mb-1">Price</p>
                                  <p className="text-lg font-semibold text-sky-600">
                                    {flight.price.toLocaleString()} {flight.currency}
                                  </p>
                                </div>
                              </div>

                              {flight.segments && flight.segments.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-slate-200">
                                  <p className="text-xs text-slate-600 mb-2">Flight Segments</p>
                                  <div className="space-y-2">
                                    {flight.segments.map((segment, segIdx) => (
                                      <div
                                        key={segIdx}
                                        className="p-3 rounded bg-white border border-slate-200"
                                      >
                                        <div className="flex items-center justify-between">
                                          <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                              <span className="text-sm font-medium text-slate-900">
                                                {segment.from_name} ({segment.from})
                                              </span>
                                              <span className="text-slate-400">→</span>
                                              <span className="text-sm font-medium text-slate-900">
                                                {segment.to_name} ({segment.to})
                                              </span>
                                            </div>
                                            <div className="flex items-center gap-4 text-xs text-slate-600">
                                              <span>{segment.airline} {segment.flight_number}</span>
                                              <span>Dep: {segment.dep_time}</span>
                                              <span>Arr: {segment.arr_time}</span>
                                              {segment.duration_min && (
                                                <span>Duration: {Math.floor(segment.duration_min / 60)}h {segment.duration_min % 60}m</span>
                                              )}
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {flight.link && (
                                <div className="mt-4 pt-4 border-t border-slate-200">
                                  <Button
                                    asChild
                                    className="w-full bg-sky-400 hover:bg-sky-500 text-white shadow-lg shadow-sky-200/50"
                                  >
                                    <a
                                      href={flight.link}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      Book This Flight
                                    </a>
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-slate-600">No flight information available</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="budget">
                <Card className="bg-white border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-slate-900">Budget Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {trip.budget.categories.map((category) => (
                        <div
                          key={category.category}
                          className="p-4 rounded-lg bg-slate-50 border border-slate-200"
                        >
                          <div className="flex justify-between items-center mb-2">
                            <h4 className="font-medium text-slate-900 capitalize">
                              {category.category}
                            </h4>
                            <span className="text-lg font-semibold text-sky-600">
                              {category.estimated.toLocaleString()} {trip.budget.currency}
                            </span>
                          </div>
                          <div className="text-sm text-slate-600">
                            {((category.estimated / trip.budget.totalBudget) * 100).toFixed(1)}% of
                            total
                          </div>
                          {category.breakdown && category.breakdown.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-slate-200 space-y-1">
                              {category.breakdown.map((item, idx) => (
                                <div key={idx} className="flex justify-between text-xs">
                                  <span className="text-slate-600">{item.item}</span>
                                  <span className="text-slate-900">
                                    {item.cost} {trip.budget.currency}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="essentials">
                <Card className="bg-white border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-slate-900">Travel Essentials</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                      {trip.essentials.keyPhrases.length > 0 && (
                        <AccordionItem value="phrases" className="border-slate-200">
                          <AccordionTrigger className="text-slate-900">
                            Key Phrases
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="space-y-3">
                              {trip.essentials.keyPhrases.map((phrase, idx) => (
                                <div
                                  key={idx}
                                  className="p-3 rounded-lg bg-slate-50 border border-slate-200"
                                >
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <p className="font-medium text-slate-900">{phrase.phrase}</p>
                                      <p className="text-sm text-slate-600 mt-1">
                                        {phrase.translation}
                                      </p>
                                      {phrase.pronunciation && (
                                        <p className="text-xs text-sky-600 mt-1">
                                          {phrase.pronunciation}
                                        </p>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      )}

                      {trip.essentials.etiquetteTips.length > 0 && (
                        <AccordionItem value="etiquette" className="border-slate-200">
                          <AccordionTrigger className="text-slate-900">
                            Etiquette Tips
                          </AccordionTrigger>
                          <AccordionContent>
                            <ul className="space-y-2">
                              {trip.essentials.etiquetteTips.map((tip, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-sky-400 mt-1">•</span>
                                  <span className="text-slate-900">{tip}</span>
                                </li>
                              ))}
                            </ul>
                          </AccordionContent>
                        </AccordionItem>
                      )}

                      {trip.essentials.generalAdvice.length > 0 && (
                        <AccordionItem value="advice" className="border-slate-200">
                          <AccordionTrigger className="text-slate-900">
                            General Travel Advice
                          </AccordionTrigger>
                          <AccordionContent>
                            <ul className="space-y-2">
                              {trip.essentials.generalAdvice.map((advice, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-sky-400 mt-1">•</span>
                                  <span className="text-slate-900">{advice}</span>
                                </li>
                              ))}
                            </ul>
                          </AccordionContent>
                        </AccordionItem>
                      )}

                      {trip.essentials.packingList && trip.essentials.packingList.length > 0 && (
                        <AccordionItem value="packing" className="border-slate-200">
                          <AccordionTrigger className="text-slate-900">
                            Packing List
                          </AccordionTrigger>
                          <AccordionContent>
                            <ul className="grid grid-cols-2 gap-2">
                              {trip.essentials.packingList.map((item, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-sky-400 mt-1">✓</span>
                                  <span className="text-slate-900">{item}</span>
                                </li>
                              ))}
                            </ul>
                          </AccordionContent>
                        </AccordionItem>
                      )}
                    </Accordion>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="logistics">
                <Card className="bg-white border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-slate-900">Logistics & Transportation</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {trip.logistics.neighborhoods.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-3">
                          Where to Stay
                        </h3>
                        <div className="space-y-3">
                          {trip.logistics.neighborhoods.map((neighborhood, idx) => (
                            <div
                              key={idx}
                              className="p-4 rounded-lg bg-slate-50 border border-slate-200"
                            >
                              <h4 className="font-medium text-slate-900 mb-1">
                                {neighborhood.name}
                              </h4>
                              <p className="text-sm text-slate-600 mb-2">
                                {neighborhood.description}
                              </p>
                              <p className="text-xs text-sky-600">Why: {neighborhood.why}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <h3 className="text-lg font-semibold text-slate-900 mb-3">
                        Transportation
                      </h3>
                      <div className="space-y-3">
                        <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                          <h4 className="font-medium text-slate-900 mb-2">Airport</h4>
                          <p className="text-sm text-slate-600">
                            {trip.logistics.transportation.airport}
                          </p>
                        </div>

                        {trip.logistics.transportation.publicTransport.length > 0 && (
                          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                            <h4 className="font-medium text-slate-900 mb-2">Public Transport</h4>
                            <ul className="space-y-1">
                              {trip.logistics.transportation.publicTransport.map((transport, idx) => (
                                <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                                  <span className="text-sky-400">•</span>
                                  {transport}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {trip.logistics.transportation.tips.length > 0 && (
                          <div className="p-4 rounded-lg bg-sky-50 border border-sky-200">
                            <h4 className="font-medium text-sky-600 mb-2">Transport Tips</h4>
                            <ul className="space-y-1">
                              {trip.logistics.transportation.tips.map((tip, idx) => (
                                <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                                  <span className="text-sky-400">→</span>
                                  {tip}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
