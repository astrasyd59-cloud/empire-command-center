#!/usr/bin/env python3
"""
Vedic Horoscope Generator for Dibashis
Born: Feb 1, 1998, 12:45 PM, Mauritius
Target Date: March 3, 2026
"""

from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, timedelta
import math

# Initialize skyfield
load = Loader('/tmp/skyfield_data')
eph = load('de440.bsp')
ts = load.timescale()

# Define locations
mauritius = wgs84.latlon(-20.3484, 57.5522)  # Port Louis, Mauritius

# Nakshatras (27 lunar mansions)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Rashis (Zodiac signs)
RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

# Tithis
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']

def get_longitude_at(time, body):
    """Get tropical longitude of a body at given time"""
    astrometric = eph['earth'].at(time).observe(eph[body])
    app = astrometric.apparent()
    lon, lat, dist = app.ecliptic_latlon(epoch=None)
    return lon.degrees

def tropical_to_sidereal(tropical_lon, ayanamsa=24.0):
    """Convert tropical longitude to sidereal (Lahiri ayanamsa approximation)"""
    sidereal = tropical_lon - ayanamsa
    if sidereal < 0:
        sidereal += 360
    return sidereal

def get_rashi(sidereal_lon):
    """Get rashi from sidereal longitude"""
    return int(sidereal_lon / 30) % 12

def get_nakshatra(sidereal_lon):
    """Get nakshatra from sidereal longitude"""
    return int(sidereal_lon / (360/27)) % 27

def get_pada(sidereal_lon):
    """Get pada (quarter) within nakshatra"""
    nakshatra_deg = 360 / 27  # ~13.33 degrees
    within_nak = sidereal_lon % nakshatra_deg
    return int(within_nak / (nakshatra_deg / 4)) + 1

def get_tithi(sun_lon, moon_lon):
    """Calculate tithi from sun and moon longitudes"""
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12)  # 30 tithis in 360 degrees
    paksha = "Shukla" if tithi_num < 15 else "Krishna"
    if tithi_num >= 15:
        tithi_num -= 15
    return paksha, tithi_num + 1

def calculate_planet_strength(sidereal_lon, house_cusps):
    """Calculate basic planetary strength"""
    # Simplified strength calculation
    return "Strong"

def get_muhurtas(date, lat=-20.3484, lon=57.5522):
    """Calculate muhurtas (auspicious times) for the day"""
    t0 = ts.utc(date.year, date.month, date.day, 0, 0, 0)
    t1 = ts.utc(date.year, date.month, date.day + 1, 0, 0, 0)
    
    # Get sunrise and sunset
    f = almanac.dark_twilight_day(eph, mauritius)
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise = None
    sunset = None
    
    for ti, event in zip(times, events):
        if event == 4:  # sunrise
            sunrise = ti.utc_datetime()
        elif event == 0:  # sunset
            sunset = ti.utc_datetime()
    
    if not sunrise or not sunset:
        # Fallback calculation
        sunrise = datetime(date.year, date.month, date.day, 5, 30)
        sunset = datetime(date.year, date.month, date.day, 18, 30)
    
    # Convert to Mauritius time (UTC+4)
    sunrise_local = sunrise + timedelta(hours=4)
    sunset_local = sunset + timedelta(hours=4)
    
    day_duration = sunset_local - sunrise_local
    day_muhurta = day_duration / 15  # 15 muhurtas in a day
    
    # Auspicious muhurtas (Abhijit is the 8th, Rahu Kalam varies by day)
    muhurtas = []
    for i in range(15):
        start = sunrise_local + i * day_muhurta
        end = start + day_muhurta
        
        names = [
            "Rudra", "Ahi", "Mitra", "Pitru", "Vasu", "Varaha", 
            "Vishvedeva", "Vidhi", "Abhijit", "Vijaya", "Nairrta", 
            "Jayanta", "Magha", "Prajapati", "Agni"
        ]
        
        quality = "Normal"
        if i == 7:  # Abhijit
            quality = "⭐ VERY AUSPICIOUS"
        elif i == 0 or i == 14:
            quality = "Inauspicious"
        
        muhurtas.append({
            'name': names[i],
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M'),
            'quality': quality
        })
    
    return muhurtas, sunrise_local.strftime('%H:%M'), sunset_local.strftime('%H:%M')

def get_rahu_kalam(day_of_week, sunrise_str, sunset_str):
    """Calculate Rahu Kalam (inauspicious time)"""
    # Rahu Kalam periods for each day (in 1/8th parts of day)
    rahu_periods = {
        0: (2, 3),   # Sunday: 2nd to 3rd 1/8
        1: (6, 7),   # Monday: 6th to 7th 1/8
        2: (5, 6),   # Tuesday: 5th to 6th 1/8
        3: (4, 5),   # Wednesday: 4th to 5th 1/8
        4: (3, 4),   # Thursday: 3rd to 4th 1/8
        5: (2, 3),   # Friday: 2nd to 3rd 1/8
        6: (1, 2),   # Saturday: 1st to 2nd 1/8
    }
    
    # For Tuesday, March 3, 2026
    period = rahu_periods.get(day_of_week, (0, 1))
    
    # Simplified - would need proper day duration calc
    return f"Rahu Kalam: Avoid starting new ventures during this period"

def generate_horoscope():
    # Target date: March 3, 2026
    target_date = datetime(2026, 3, 3)
    target_time = ts.utc(2026, 3, 3, 12, 0, 0)  # noon
    
    # Birth data
    birth_time = ts.utc(1998, 2, 1, 8, 45, 0)  # 12:45 PM Mauritius = 8:45 UTC
    
    print("=== VEDIC HOROSCOPE CALCULATION ===")
    print(f"Target Date: {target_date.strftime('%A, %B %d, %Y')}")
    print()
    
    # Calculate planetary positions
    planet_positions = {}
    
    bodies = {
        'Sun': 'sun',
        'Moon': 'moon', 
        'Mercury': 'mercury',
        'Venus': 'venus',
        'Mars': 'mars',
        'Jupiter': 'jupiter barycenter',
        'Saturn': 'saturn barycenter'
    }
    
    print("=== PLANETARY POSITIONS (March 3, 2026) ===")
    
    sun_tropical = get_longitude_at(target_time, 'sun')
    moon_tropical = get_longitude_at(target_time, 'moon')
    
    sun_sidereal = tropical_to_sidereal(sun_tropical)
    moon_sidereal = tropical_to_sidereal(moon_tropical)
    
    print(f"Sun Tropical: {sun_tropical:.2f}°")
    print(f"Sun Sidereal: {sun_sidereal:.2f}° → {RASHIS[get_rashi(sun_sidereal)]}")
    print(f"Moon Tropical: {moon_tropical:.2f}°")
    print(f"Moon Sidereal: {moon_sidereal:.2f}° → {NAKSHATRAS[get_nakshatra(moon_sidereal)]}")
    
    # Calculate tithi
    paksha, tithi_num = get_tithi(sun_sidereal, moon_sidereal)
    print(f"\nTithi: {paksha} {TITHIS[tithi_num-1]}")
    
    # Moon phase
    moon_phase = (moon_tropical - sun_tropical) % 360
    illumination = (1 - math.cos(math.radians(moon_phase))) / 2 * 100
    print(f"Moon Illumination: {illumination:.1f}%")
    
    # All planets
    for name, body_key in bodies.items():
        try:
            tropical = get_longitude_at(target_time, body_key)
            sidereal = tropical_to_sidereal(tropical)
            rashi = get_rashi(sidereal)
            nakshatra = get_nakshatra(sidereal)
            
            planet_positions[name] = {
                'tropical': tropical,
                'sidereal': sidereal,
                'rashi': rashi,
                'rashi_name': RASHIS[rashi],
                'nakshatra': NAKSHATRAS[nakshatra],
                'degree_in_rashi': sidereal % 30
            }
            
            print(f"{name}: {RASHIS[rashi]} ({sidereal % 30:.2f}°), {NAKSHATRAS[nakshatra]}")
        except Exception as e:
            print(f"{name}: Error - {e}")
    
    # Rahu and Ketu (approximate - mean nodes)
    rahu_sidereal = (moon_sidereal - sun_sidereal) % 360  # Simplified
    rahu_sidereal = 180  # Approximate for March 2026
    ketu_sidereal = (rahu_sidereal + 180) % 360
    
    planet_positions['Rahu'] = {
        'sidereal': rahu_sidereal,
        'rashi': get_rashi(rahu_sidereal),
        'rashi_name': RASHIS[get_rashi(rahu_sidereal)],
        'nakshatra': NAKSHATRAS[get_nakshatra(rahu_sidereal)],
        'degree_in_rashi': rahu_sidereal % 30
    }
    planet_positions['Ketu'] = {
        'sidereal': ketu_sidereal,
        'rashi': get_rashi(ketu_sidereal),
        'rashi_name': RASHIS[get_rashi(ketu_sidereal)],
        'nakshatra': NAKSHATRAS[get_nakshatra(ketu_sidereal)],
        'degree_in_rashi': ketu_sidereal % 30
    }
    
    print(f"Rahu: {RASHIS[get_rashi(rahu_sidereal)]}")
    print(f"Ketu: {RASHIS[get_rashi(ketu_sidereal)]}")
    
    # Muhurtas
    muhurtas, sunrise, sunset = get_muhurtas(target_date)
    
    print(f"\n=== MUHURTAS ===")
    print(f"Sunrise: {sunrise}")
    print(f"Sunset: {sunset}")
    
    return {
        'date': target_date,
        'sun': {'sidereal': sun_sidereal, 'rashi': get_rashi(sun_sidereal), 'rashi_name': RASHIS[get_rashi(sun_sidereal)]},
        'moon': {'sidereal': moon_sidereal, 'nakshatra': NAKSHATRAS[get_nakshatra(moon_sidereal)], 'pada': get_pada(moon_sidereal)},
        'tithi': f"{paksha} {TITHIS[tithi_num-1]}",
        'moon_illumination': illumination,
        'planets': planet_positions,
        'muhurtas': muhurtas,
        'sunrise': sunrise,
        'sunset': sunset,
        'day_of_week': target_date.weekday()
    }

if __name__ == "__main__":
    data = generate_horoscope()
    print("\n=== DATA READY FOR HTML ===")
    print(f"Date: {data['date']}")
    print(f"Sun: {data['sun']}")
    print(f"Moon: {data['moon']}")
    print(f"Tithi: {data['tithi']}")
