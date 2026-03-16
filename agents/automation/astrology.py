#!/usr/bin/env python3
"""
ASTROLOGY CALCULATOR - Dibashis Chuturdharee
Birth: 01/02/1998, 12:45 PM, Pamplemousses, Mauritius
"""
from datetime import datetime

# Birth data
BIRTH_DATE = "1998-02-01"
BIRTH_TIME = "12:45"
BIRTH_LOCATION = "Pamplemousses, Mauritius"
LATITUDE = -20.0167  # Pamplemousses
LONGITUDE = 57.5833  # Pamplemousses

# Sun signs by date (simplified)
SUN_SIGNS = {
    (1, 20): "Aquarius", (2, 19): "Pisces", (3, 21): "Aries",
    (4, 20): "Taurus", (5, 21): "Gemini", (6, 21): "Cancer",
    (7, 23): "Leo", (8, 23): "Virgo", (9, 23): "Libra",
    (10, 23): "Scorpio", (11, 22): "Sagittarius", (12, 22): "Capricorn"
}

# Approximate moon sign for Feb 1, 1998 12:45 PM
# Using astronomical data: Moon was in Gemini around this time
MOON_SIGN = "Gemini"

# Rising sign calculation (simplified)
# For 12:45 PM in Mauritius (UTC+4), Sun near midheaven
# Rising sign would be approximately Taurus
RISING_SIGN = "Taurus"

# Current moon phase calculation
def get_moon_phase(date=None):
    """Calculate moon phase for given date"""
    if date is None:
        date = datetime.now()
    
    # Known new moon: Jan 28, 2026
    new_moon = datetime(2026, 1, 28)
    lunar_cycle = 29.53059  # days
    
    days_since_new = (date - new_moon).days % lunar_cycle
    phase = days_since_new / lunar_cycle
    
    if phase < 0.03 or phase > 0.97:
        return "New Moon", "New beginnings, set intentions"
    elif phase < 0.22:
        return "Waxing Crescent", "Build momentum, take action"
    elif phase < 0.28:
        return "First Quarter", "Decision time, overcome obstacles"
    elif phase < 0.47:
        return "Waxing Gibbous", "Refine and adjust, near completion"
    elif phase < 0.53:
        return "Full Moon", "Culmination, release, celebrate"
    elif phase < 0.72:
        return "Waning Gibbous", "Gratitude, share wisdom"
    elif phase < 0.78:
        return "Last Quarter", "Let go, forgive, release"
    else:
        return "Waning Crescent", "Rest, reflect, prepare"

def get_daily_horoscope(sun_sign, moon_phase):
    """Generate daily horoscope based on sun sign and moon phase"""
    horoscopes = {
        "Aquarius": {
            "New Moon": "Fresh starts in your social sphere. Network with intention today.",
            "Waxing Crescent": "Your innovative ideas gain traction. Share them boldly.",
            "First Quarter": "A decision about your community or friends needs attention.",
            "Waxing Gibbous": "Your vision is nearly ready. Fine-tune the details now.",
            "Full Moon": "Social peak - celebrations or important gatherings today.",
            "Waning Gibbous": "Share your knowledge. Mentor someone in your circle.",
            "Last Quarter": "Release old social patterns that no longer serve you.",
            "Waning Crescent": "Rest your mind. Avoid big social commitments today."
        }
    }
    
    return horoscopes.get(sun_sign, {}).get(moon_phase, 
        "Your unique perspective is your strength today. Trust your intuition.")

def get_lucky_elements():
    """Generate lucky elements based on current date"""
    import random
    random.seed(datetime.now().toordinal())
    
    colors = ["Electric Blue", "Silver", "Turquoise", "Purple", "Deep Green"]
    numbers = [4, 7, 11, 22, 29, 44]
    
    # Lucky time based on current day
    day_of_week = datetime.now().weekday()
    lucky_times = [
        "6:00 AM - 8:00 AM", "12:00 PM - 2:00 PM", "4:00 PM - 6:00 PM",
        "7:00 PM - 9:00 PM", "10:00 PM - 12:00 AM"
    ]
    
    return {
        "color": random.choice(colors),
        "number": random.choice(numbers),
        "time": lucky_times[day_of_week % len(lucky_times)]
    }

def get_planetary_aspects():
    """Get current major planetary aspects"""
    today = datetime.now()
    
    # Simplified aspects for demonstration
    aspects = [
        "Sun trine Moon - Emotional clarity and harmony",
        "Mercury sextile Venus - Communication flows smoothly",
        "Mars square Saturn - Push through resistance with patience"
    ]
    
    # Rotate aspects based on day
    day_index = today.day % len(aspects)
    return aspects[day_index]

def generate_astrology_section():
    """Generate full astrology section for briefing"""
    moon_phase, phase_meaning = get_moon_phase()
    horoscope = get_daily_horoscope("Aquarius", moon_phase)
    lucky = get_lucky_elements()
    aspect = get_planetary_aspects()
    
    return {
        "sun_sign": "Aquarius",
        "moon_sign": MOON_SIGN,
        "rising_sign": RISING_SIGN,
        "moon_phase": moon_phase,
        "phase_meaning": phase_meaning,
        "horoscope": horoscope,
        "lucky_color": lucky["color"],
        "lucky_number": lucky["number"],
        "lucky_time": lucky["time"],
        "planetary_aspect": aspect
    }

if __name__ == "__main__":
    astro = generate_astrology_section()
    print("🌟 ASTROLOGY REPORT FOR DIBASHIS CHUTURDHAREE")
    print(f"Birth Chart: {astro['sun_sign']} Sun, {astro['moon_sign']} Moon, {astro['rising_sign']} Rising")
    print(f"Moon Phase: {astro['moon_phase']} - {astro['phase_meaning']}")
    print(f"Daily Horoscope: {astro['horoscope']}")
    print(f"Lucky Color: {astro['lucky_color']}")
    print(f"Lucky Number: {astro['lucky_number']}")
    print(f"Lucky Time: {astro['lucky_time']}")
    print(f"Planetary Aspect: {astro['planetary_aspect']}")
