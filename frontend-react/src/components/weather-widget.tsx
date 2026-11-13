"use client";

import { useEffect, useState } from "react";
import {
  Sun,
  CloudSun,
  Cloud,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudFog,
} from "lucide-react";

interface CurrentWeather {
  temperature: number;
  windspeed: number;
  weathercode: number;
  time: string;
}

interface LocationInfo {
  lat: number;
  lon: number;
  isDefault: boolean;
}

interface WeatherCache {
  location: LocationInfo;
  weather: CurrentWeather;
  label: string;
  fetchedAt: number;
}

const WEATHER_ICONS: Record<number, React.ElementType> = {
  0: Sun,
  1: CloudSun,
  2: CloudSun,
  3: CloudSun,
  45: CloudFog,
  48: CloudFog,
  51: CloudRain,
  53: CloudRain,
  55: CloudRain,
  56: CloudRain,
  57: CloudRain,
  61: CloudRain,
  63: CloudRain,
  65: CloudRain,
  66: CloudRain,
  67: CloudRain,
  71: CloudSnow,
  73: CloudSnow,
  75: CloudSnow,
  77: CloudSnow,
  80: CloudRain,
  81: CloudRain,
  82: CloudRain,
  85: CloudSnow,
  86: CloudSnow,
  95: CloudLightning,
  96: CloudLightning,
  99: CloudLightning,
};

const CACHE_KEY = "aso_weather_cache";
const CACHE_TTL_MS = 30 * 60 * 1000; // 30 minutes
const GEO_MAX_AGE_MS = 30 * 60 * 1000;
const DEFAULT_LOCATION: LocationInfo = { lat: 6.5244, lon: 3.3792, isDefault: true };

function fallbackLabel(location: LocationInfo): string {
  if (location.isDefault) return "Lagos, Nigeria";
  return "Your location";
}

function sameLocation(a: LocationInfo, b: LocationInfo): boolean {
  return a.lat === b.lat && a.lon === b.lon;
}

function readCache(): WeatherCache | null {
  try {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as WeatherCache;
    if (!parsed || typeof parsed.fetchedAt !== "number" || !parsed.weather) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeCache(entry: WeatherCache): void {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(entry));
  } catch {
    // Ignore storage failures (private mode, quota).
  }
}

function cacheIsFresh(cache: WeatherCache | null, location: LocationInfo): boolean {
  if (!cache) return false;
  if (Date.now() - cache.fetchedAt > CACHE_TTL_MS) return false;
  return sameLocation(cache.location, location);
}

function resolveLocation(): Promise<LocationInfo> {
  return new Promise((resolve) => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      resolve(DEFAULT_LOCATION);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          isDefault: false,
        }),
      () => resolve(DEFAULT_LOCATION),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: GEO_MAX_AGE_MS }
    );
  });
}

async function fetchWeather(location: LocationInfo): Promise<CurrentWeather> {
  const res = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&current_weather=true`
  );
  if (!res.ok) throw new Error("weather request failed");
  const data = await res.json();
  if (!data.current_weather) throw new Error("no current weather in response");
  return data.current_weather as CurrentWeather;
}

async function reverseGeocode(location: LocationInfo): Promise<string> {
  try {
    const res = await fetch(
      `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${location.lat}&longitude=${location.lon}`
    );
    if (!res.ok) throw new Error("reverse geocode failed");
    const data = await res.json();
    const city = data.city || data.locality || data.principalSubdivision || "";
    const country = data.countryName || data.countryCode || "";
    const label = [city, country].filter(Boolean).join(", ");
    return label || fallbackLabel(location);
  } catch {
    return fallbackLabel(location);
  }
}

export function WeatherWidget() {
  const [weather, setWeather] = useState<CurrentWeather | null>(null);
  const [locationLabel, setLocationLabel] = useState("");
  const [isDefaultLocation, setIsDefaultLocation] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      const location = await resolveLocation();
      if (cancelled) return;

      const cache = readCache();

      if (cacheIsFresh(cache, location)) {
        const fresh = cache as WeatherCache;
        if (cancelled) return;
        setWeather(fresh.weather);
        setLocationLabel(fresh.label || fallbackLabel(location));
        setIsDefaultLocation(location.isDefault);
        setLoading(false);
        return;
      }

      let weatherData: CurrentWeather | null = null;
      let label = "";
      try {
        weatherData = await fetchWeather(location);
        label = await reverseGeocode(location);
        writeCache({ location, weather: weatherData, label, fetchedAt: Date.now() });
      } catch {
        if (cache && sameLocation(cache.location, location)) {
          weatherData = cache.weather;
          label = cache.label;
        }
      }

      if (cancelled) return;

      if (weatherData) {
        setWeather(weatherData);
        setLocationLabel(label || fallbackLabel(location));
        setIsDefaultLocation(location.isDefault);
        setLoading(false);
      } else {
        setError(true);
        setLoading(false);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="glass-card glass-card-transition flex items-center gap-3 text-xs text-[var(--muted-foreground)] p-4"
      >
        Weather unavailable
      </div>
    );
  }

  if (loading || !weather) {
    return (
      <div className="glass-card glass-card-transition flex items-center gap-3 animate-pulse text-xs text-[var(--muted-foreground)] p-4"
      >
        <Cloud size={20} /> Loading weather…
      </div>
    );
  }

  const Icon = WEATHER_ICONS[weather.weathercode] || Cloud;

  return (
    <div className="glass-card glass-card-transition flex items-center gap-3 p-4"
    >
      <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style={{ background: "rgba(255,255,255,0.05)" }}>
        <Icon size={22} className="text-[var(--primary)]" />
      </div>
      <div>
        <div className="text-sm font-bold text-[var(--foreground)]">
          {Math.round(weather.temperature)}°C
        </div>
        <div className="text-xs text-[var(--muted-foreground)] flex items-center gap-1 flex-wrap">
          <span className="truncate">{locationLabel}</span>
          {isDefaultLocation && (
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 shrink-0">
              📍 Default
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
