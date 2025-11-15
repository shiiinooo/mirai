import { useState, useEffect, useCallback } from 'react';
import { Check, ChevronsUpDown, Loader2, Plane } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { searchAirports, Airport } from '@/lib/api/airports';

interface AirportInputProps {
  value?: string;
  airportCode?: string;
  onChange: (city: string, airportCode: string) => void;
  placeholder?: string;
  label?: string;
  disabled?: boolean;
}

export function AirportInput({
  value = '',
  airportCode = '',
  onChange,
  placeholder = 'Select city...',
  label,
  disabled = false,
}: AirportInputProps) {
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [airports, setAirports] = useState<Airport[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedAirport, setSelectedAirport] = useState<Airport | null>(null);

  // Initialize selected airport if value is provided
  useEffect(() => {
    if (value && airportCode) {
      // Sanitize value - remove URLs and invalid characters
      const sanitizedCity = value
        .replace(/https?:\/\/[^\s]+/g, '') // Remove URLs
        .replace(/localhost:\d+/g, '') // Remove localhost URLs
        .trim();
      
      // Only set if we have a valid city name (not empty after sanitization)
      if (sanitizedCity && sanitizedCity.length > 0) {
        setSelectedAirport({
          code: airportCode,
          city: sanitizedCity,
          name: '',
          country: '',
          displayName: `${sanitizedCity} (${airportCode})`,
        });
      }
    } else if (!value && !airportCode) {
      // Clear selection if both are empty
      setSelectedAirport(null);
    }
  }, [value, airportCode]);

  // Debounced search
  useEffect(() => {
    if (!searchQuery || searchQuery.length < 2) {
      setAirports([]);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const results = await searchAirports(searchQuery);
        setAirports(results);
      } catch (error) {
        console.error('Failed to search airports:', error);
        setAirports([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSelect = useCallback(
    (airport: Airport) => {
      setSelectedAirport(airport);
      onChange(airport.city, airport.code);
      setOpen(false);
      setSearchQuery('');
    },
    [onChange]
  );

  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium text-slate-700">{label}</label>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            disabled={disabled}
            className={cn(
              'w-full justify-between bg-white border-slate-200 text-slate-900 hover:bg-slate-50',
              !selectedAirport && 'text-slate-500'
            )}
          >
            <div className="flex items-center gap-2 truncate">
              <Plane className="h-4 w-4 shrink-0" />
              {selectedAirport ? (
                <span className="truncate">{selectedAirport.displayName}</span>
              ) : (
                <span>{placeholder}</span>
              )}
            </div>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0" align="start">
          <Command shouldFilter={false}>
            <CommandInput
              placeholder="Search by city or airport code..."
              value={searchQuery}
              onValueChange={setSearchQuery}
            />
            <CommandList>
              {isSearching ? (
                <div className="flex items-center justify-center py-6">
                  <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
                  <span className="ml-2 text-sm text-slate-500">Searching...</span>
                </div>
              ) : airports.length === 0 ? (
                <CommandEmpty>
                  {searchQuery.length < 2
                    ? 'Type at least 2 characters to search'
                    : 'No airports found'}
                </CommandEmpty>
              ) : (
                <CommandGroup>
                  {airports.map((airport) => (
                    <CommandItem
                      key={airport.code}
                      value={airport.code}
                      onSelect={() => handleSelect(airport)}
                      className="cursor-pointer"
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          selectedAirport?.code === airport.code
                            ? 'opacity-100'
                            : 'opacity-0'
                        )}
                      />
                      <div className="flex flex-col">
                        <span className="font-medium">{airport.displayName}</span>
                        {airport.country && (
                          <span className="text-xs text-slate-500">
                            {airport.country}
                          </span>
                        )}
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {selectedAirport && (
        <p className="text-xs text-slate-500">
          Airport: {selectedAirport.code} • {selectedAirport.city}
        </p>
      )}
    </div>
  );
}

