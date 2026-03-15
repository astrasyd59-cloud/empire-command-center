#!/usr/bin/env python3
"""
Complete Vedic Horoscope Generator for Dibashis
Born: Feb 1, 1998, 12:45 PM, Mauritius  
Target Date: Tuesday, March 3, 2026
"""

from skyfield.api import Loader, wgs84
from skyfield import almanac
from datetime import datetime, timedelta
import math

# Initialize skyfield
load = Loader('/tmp/skyfield_data')
eph = load('de440.bsp')
ts = load.timescale()

# Location
mauritius = wgs84.latlon(-20.3484, 57.5522)

# Vedic data
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_DEITIES = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

NAKSHATRA_SYMBOLS = [
    "🐎 Horse Head", "👑 Royal Throne", "🔥 Flame/Razor", "🐂 Chariot/Ox Cart", "🦌 Deer Head", "💎 Teardrop/Diamond",
    "🏹 Quiver of Arrows", "🌳 Circle/Arrow", "🐍 Serpent/Coiled", "👑 Royal Throne", "🛏️ Front Legs of Bed", "🛏️ Back Legs of Bed",
    "👊 Closed Hand/Fist", "💎 Shining Jewel", "🌿 Coral/Sapphire", "⚖️ Triumphant Arch", "🪷 Lotus Arch", "🌂 Umbrella/Earring",
    "🦁 Lion's Tail", "🐘 Elephant Tusk/Bed", "🐘 Elephant Tusk", "⬅️ Three Footprints", "🥁 Drum/Flute", "🔵 100 Physicians/Circle",
    "⚰️ Front of Funeral Cot", "⚰️ Back of Funeral Cot", "🐟 Fish/Shore"
]

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

RASHI_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

RASHI_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

PLANET_SYMBOLS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 
    'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
}

def tropical_to_sidereal(tropical_lon, ayanamsa=24.13):
    """Convert tropical to sidereal using Lahiri ayanamsa"""
    sidereal = tropical_lon - ayanamsa
    if sidereal < 0:
        sidereal += 360
    return sidereal

def get_rashi(sidereal_lon):
    return int(sidereal_lon / 30) % 12

def get_nakshatra(sidereal_lon):
    return int(sidereal_lon / (360/27)) % 27

def get_pada(sidereal_lon):
    nakshatra_deg = 360 / 27
    within_nak = sidereal_lon % nakshatra_deg
    return int(within_nak / (nakshatra_deg / 4)) + 1

def get_tithi(sun_lon, moon_lon):
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12)
    paksha = "Shukla" if tithi_num < 15 else "Krishna"
    tithi_index = tithi_num if tithi_num < 15 else tithi_num - 15
    return paksha, tithi_index + 1

def get_moon_phase(sun_lon, moon_lon):
    diff = (moon_lon - sun_lon) % 360
    illumination = (1 - math.cos(math.radians(diff))) / 2
    return illumination * 100

def get_planet_longitude(time, body_name):
    """Get tropical longitude for a planet"""
    body_map = {
        'Sun': 'sun', 'Moon': 'moon', 'Mercury': 'mercury', 
        'Venus': 'venus', 'Mars': 'mars barycenter',
        'Jupiter': 'jupiter barycenter', 'Saturn': 'saturn barycenter'
    }
    astrometric = eph['earth'].at(time).observe(eph[body_map[body_name]])
    app = astrometric.apparent()
    lon, lat, dist = app.ecliptic_latlon(epoch=None)
    return lon.degrees

def calculate_all_positions(target_time):
    """Calculate all planetary positions"""
    positions = {}
    
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    
    for planet in planets:
        try:
            tropical = get_planet_longitude(target_time, planet)
            sidereal = tropical_to_sidereal(tropical)
            rashi = get_rashi(sidereal)
            nakshatra = get_nakshatra(sidereal)
            pada = get_pada(sidereal)
            
            positions[planet] = {
                'tropical': tropical,
                'sidereal': sidereal,
                'rashi': rashi,
                'rashi_name': RASHIS[rashi],
                'rashi_lord': RASHI_LORDS[rashi],
                'nakshatra': nakshatra,
                'nakshatra_name': NAKSHATRAS[nakshatra],
                'nakshatra_deity': NAKSHATRA_DEITIES[nakshatra],
                'nakshatra_symbol': NAKSHATRA_SYMBOLS[nakshatra],
                'pada': pada,
                'deg_in_rashi': sidereal % 30
            }
        except Exception as e:
            print(f"Error calculating {planet}: {e}")
    
    # Rahu and Ketu (mean nodes approximation)
    # True node calculation is complex, using approximate positions for March 2026
    # Rahu around 5° Pisces, Ketu around 5° Virgo (axis)
    rahu_sidereal = 335.0  # Approximate for March 2026
    ketu_sidereal = (rahu_sidereal + 180) % 360
    
    for name, lon in [('Rahu', rahu_sidereal), ('Ketu', ketu_sidereal)]:
        rashi = get_rashi(lon)
        nakshatra = get_nakshatra(lon)
        pada = get_pada(lon)
        positions[name] = {
            'sidereal': lon,
            'rashi': rashi,
            'rashi_name': RASHIS[rashi],
            'rashi_lord': RASHI_LORDS[rashi],
            'nakshatra': nakshatra,
            'nakshatra_name': NAKSHATRAS[nakshatra],
            'nakshatra_deity': NAKSHATRA_DEITIES[nakshatra],
            'nakshatra_symbol': NAKSHATRA_SYMBOLS[nakshatra],
            'pada': pada,
            'deg_in_rashi': lon % 30
        }
    
    return positions

def get_sunrise_sunset(date):
    """Get sunrise and sunset times for Mauritius"""
    t0 = ts.utc(date.year, date.month, date.day, 0, 0, 0)
    t1 = ts.utc(date.year, date.month, date.day + 1, 0, 0, 0)
    
    f = almanac.dark_twilight_day(eph, mauritius)
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise = None
    sunset = None
    
    for ti, event in zip(times, events):
        dt = ti.utc_datetime() + timedelta(hours=4)  # UTC+4 for Mauritius
        if event == 4:  # sunrise
            sunrise = dt
        elif event == 0:  # sunset
            sunset = dt
    
    if not sunrise:
        sunrise = datetime(date.year, date.month, date.day, 6, 0) + timedelta(hours=4)
    if not sunset:
        sunset = datetime(date.year, date.month, date.day, 18, 30) + timedelta(hours=4)
        
    return sunrise, sunset

def calculate_muhurtas(sunrise, sunset):
    """Calculate 15 muhurtas of the day"""
    day_duration = sunset - sunrise
    muhurta_duration = day_duration / 15
    
    names = [
        "Rudra", "Ahi", "Mitra", "Pitru", "Vasu", "Varaha",
        "Vishvedeva", "Vidhi", "Abhijit", "Vijaya", "Nairrita",
        "Jayanta", "Magha", "Prajapati", "Agni"
    ]
    
    qualities = [
        "⚠️ Inauspicious", "Neutral", "⭐ Good", "Neutral", "Good", "Neutral",
        "Good", "⭐ Auspicious", "⭐⭐ VERY AUSPICIOUS", "⭐ Auspicious", "⚠️ Inauspicious",
        "⭐ Good", "⭐ Good", "Neutral", "⚠️ Inauspicious"
    ]
    
    muhurtas = []
    for i in range(15):
        start = sunrise + i * muhurta_duration
        end = start + muhurta_duration
        muhurtas.append({
            'num': i + 1,
            'name': names[i],
            'start': start.strftime('%H:%M'),
            'end': end.strftime('%H:%M'),
            'quality': qualities[i]
        })
    
    return muhurtas

def get_rahu_kalam(day_of_week, sunrise, sunset):
    """Calculate Rahu Kalam"""
    # Rahu Kalam in 1/8th parts of day
    periods = {0: (2,3), 1: (6,7), 2: (5,6), 3: (4,5), 4: (3,4), 5: (2,3), 6: (1,2)}
    start_8th, end_8th = periods.get(day_of_week, (2,3))
    
    day_duration = sunset - sunrise
    eighth = day_duration / 8
    
    start = sunrise + start_8th * eighth
    end = sunrise + end_8th * eighth
    
    return start.strftime('%H:%M'), end.strftime('%H:%M')

def get_yama_kalam(day_of_week, sunrise, sunset):
    """Calculate Yama Gandam (similar to Rahu Kalam but different periods)"""
    periods = {0: (5,6), 1: (4,5), 2: (3,4), 3: (2,3), 4: (1,2), 5: (0,1), 6: (6,7)}
    start_8th, end_8th = periods.get(day_of_week, (4,5))
    
    day_duration = sunset - sunrise
    eighth = day_duration / 8
    
    start = sunrise + start_8th * eighth
    end = sunrise + end_8th * eighth
    
    return start.strftime('%H:%M'), end.strftime('%H:%M')

def get_gulika_kalam(day_of_week, sunrise, sunset):
    """Calculate Gulika Kalam"""
    periods = {0: (7,8), 1: (1,2), 2: (6,7), 3: (5,6), 4: (4,5), 5: (3,4), 6: (2,3)}
    start_8th, end_8th = periods.get(day_of_week, (3,4))
    
    day_duration = sunset - sunrise
    eighth = day_duration / 8
    
    start = sunrise + start_8th * eighth
    end = sunrise + end_8th * eighth
    
    return start.strftime('%H:%M'), end.strftime('%H:%M')

def get_vara(day_of_week):
    """Get day lord"""
    lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    return lords[day_of_week]

def generate_horoscope_data():
    """Generate complete horoscope data"""
    target_date = datetime(2026, 3, 3)
    target_time = ts.utc(2026, 3, 3, 8, 0, 0)  # Morning time
    
    # Calculate positions
    positions = calculate_all_positions(target_time)
    
    # Sun and Moon data
    sun = positions['Sun']
    moon = positions['Moon']
    
    # Tithi calculation
    paksha, tithi_num = get_tithi(sun['sidereal'], moon['sidereal'])
    tithi_name = TITHIS[tithi_num - 1]
    
    # Moon phase
    moon_phase = get_moon_phase(sun['sidereal'], moon['sidereal'])
    
    # Sunrise/sunset
    sunrise, sunset = get_sunrise_sunset(target_date)
    
    # Muhurtas
    muhurtas = calculate_muhurtas(sunrise, sunset)
    
    # Inauspicious times
    day_of_week = target_date.weekday()
    rahu_start, rahu_end = get_rahu_kalam(day_of_week, sunrise, sunset)
    yama_start, yama_end = get_yama_kalam(day_of_week, sunrise, sunset)
    gulika_start, gulika_end = get_gulika_kalam(day_of_week, sunrise, sunset)
    
    # Day lord
    vara_lord = get_vara(day_of_week)
    
    # Yoga (Sun + Moon longitude / 13°20')
    yoga_lon = (sun['sidereal'] + moon['sidereal']) % 360
    yoga_num = int(yoga_lon / (360/27))
    yogas = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
        "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Indra", "Vaidhriti"
    ]
    yoga = yogas[yoga_num]
    
    # Karana (half tithi)
    karana_num = int(((moon['sidereal'] - sun['sidereal']) % 360) / 6) % 11
    karanas = [
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", 
        "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
    ]
    karana = karanas[karana_num]
    
    return {
        'date': target_date,
        'positions': positions,
        'sun': sun,
        'moon': moon,
        'paksha': paksha,
        'tithi_num': tithi_num,
        'tithi_name': tithi_name,
        'moon_phase': moon_phase,
        'sunrise': sunrise.strftime('%H:%M'),
        'sunset': sunset.strftime('%H:%M'),
        'muhurtas': muhurtas,
        'rahu_kalam': (rahu_start, rahu_end),
        'yama_kalam': (yama_start, yama_end),
        'gulika_kalam': (gulika_start, gulika_end),
        'vara_lord': vara_lord,
        'yoga': yoga,
        'karana': karana,
        'day_of_week': target_date.strftime('%A')
    }

if __name__ == "__main__":
    data = generate_horoscope_data()
    print("Horoscope data generated successfully!")
    print(f"Date: {data['date'].strftime('%A, %B %d, %Y')}")
    print(f"Tithi: {data['paksha']} {data['tithi_name']}")
    print(f"Nakshatra: {data['moon']['nakshatra_name']}")
    print(f"Sun: {data['sun']['rashi_name']}")
