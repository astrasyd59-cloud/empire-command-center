# TOOLS.md - Jyotishi

## Data Sources

### Swiss Ephemeris
- **Path:** `/usr/share/ephemeris/` or bundled
- **Coverage:** 3000 BCE - 3000 CE
- **Precision:** 0.001 arcsecond
- **Usage:** All planetary position calculations

### Birth Data Registry

**Primary Subject: Dibs**
| Field | Value |
|-------|-------|
| Date of Birth | February 1, 1998 |
| Time of Birth | 12:45 PM (12:45) |
| Time Zone | Mauritius (MUT, UTC+4) |
| Location | Mauritius (-20.3484° S, 57.5522° E) |

**Calculated Natal Positions:**
| Planet | Sign | House |
|--------|------|-------|
| Sun | Aquarius | 10th |
| Moon | Gemini | 2nd |
| Mercury | Capricorn | 9th |
| Venus | Capricorn | 9th |
| Mars | Aquarius | 10th |
| Jupiter | Aquarius | 10th |
| Saturn | Aries | 12th |
| Ascendant | Taurus | 1st |

## Tool Implementations

### Chart Calculation
```python
# Core function signature
calculate_chart(date, time, lat, lon, ayanamsa='Lahiri')
calculate_transits(natal_chart, date)
get_moon_phase(date)
get_nakshatra(moon_longitude)
```

### Daily Briefing Generator
- Aggregates transit data
- Filters for significant aspects (orb < 3°)
- Formats into readable insights
- Suggests timing windows

## Missing Tools / Wishlist

| Tool | Purpose | Status |
|------|---------|--------|
| Predictive engine | Pattern-based forecasting | Needed |
| Synastry calculator | Relationship chart comparison | Needed |
| Muhurta finder | Optimal timing search | Planned |
| Panchang generator | Full daily almanac | Planned |

## Dependencies

- Swiss Ephemeris C library
- pyswisseph Python bindings
- pytz for timezone handling
- geopy for location coordinates
