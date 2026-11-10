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

export function WeatherWidget() {
  const [weather, setWeather] = useState<CurrentWeather | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(
      "https://api.open-meteo.com/v1/forecast?latitude=6.5244&longitude=3.3792&current_weather=true"
    )
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled && data.current_weather) {
          setWeather(data.current_weather);
        }
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
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

  if (!weather) {
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
        <div className="text-xs text-[var(--muted-foreground)]">Lagos, Nigeria</div>
      </div>
    </div>
  );
}
