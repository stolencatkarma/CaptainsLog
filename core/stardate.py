from datetime import datetime, timedelta
from dateutil import tz
import math
from typing import Optional


class StardateCalculator:
    """
    Star Citizen datetime calculator.
    Uses Star Citizen's Standard Earth Time (SET) system.
    """
    
    # Star Citizen universe starts in 2075 (when humans made first contact)
    # Current game year is around 2954, but we'll use current real date + 930 years
    SC_YEAR_OFFSET = 930
    
    @classmethod
    def earth_date_to_stardate(cls, earth_date: Optional[datetime] = None) -> str:
        """
        Convert Earth date to Star Citizen SET (Standard Earth Time).
        Returns format: YYYY.MM.DD.HH.MM
        """
        if earth_date is None:
            earth_date = datetime.now()
        
        # Convert to Star Citizen year
        sc_year = earth_date.year + cls.SC_YEAR_OFFSET
        
        # Format as Star Citizen SET
        set_time = f"{sc_year}.{earth_date.month:02d}.{earth_date.day:02d}.{earth_date.hour:02d}.{earth_date.minute:02d}"
        
        return set_time
    
    @classmethod
    def stardate_to_earth_date(cls, set_time: str) -> datetime:
        """
        Convert Star Citizen SET back to Earth date.
        """
        try:
            parts = set_time.split('.')
            sc_year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            hour = int(parts[3]) if len(parts) > 3 else 0
            minute = int(parts[4]) if len(parts) > 4 else 0
            
            # Convert back to Earth year
            earth_year = sc_year - cls.SC_YEAR_OFFSET
            
            return datetime(earth_year, month, day, hour, minute)
        except:
            return datetime.now()
    
    @classmethod
    def get_current_stardate(cls) -> str:
        """Get current Star Citizen SET"""
        return cls.earth_date_to_stardate()
    
    @classmethod
    def format_stardate(cls, set_time: str) -> str:
        """Format Star Citizen SET for display"""
        return f"SET {set_time}"
    
    @classmethod
    def get_stardate_info(cls) -> dict:
        """Get comprehensive Star Citizen SET information"""
        now = datetime.now()
        set_time = cls.earth_date_to_stardate(now)
        
        # Calculate Star Citizen year
        sc_year = now.year + cls.SC_YEAR_OFFSET
        
        return {
            'stardate': set_time,
            'formatted_stardate': cls.format_stardate(set_time),
            'earth_date': now.strftime("%Y-%m-%d %H:%M:%S"),
            'earth_date_long': now.strftime("%A, %B %d, %Y at %I:%M %p"),
            'sc_year': sc_year,
            'utc_time': now.utctimetuple(),
            'year': now.year,
            'day_of_year': now.timetuple().tm_yday,
            'set_display': f"Standard Earth Time {set_time}"
        }


# Utility functions for time zones and special dates
class TimeUtils:
    
    @staticmethod
    def get_time_zones():
        """Get common time zones for starship operations"""
        return {
            'UTC': tz.UTC,
            'Earth Standard': tz.gettz('UTC'),
            'Sol System': tz.gettz('UTC'),
            'Terra': tz.gettz('UTC'),
            'Crusader': tz.gettz('UTC+1'),
            'Hurston': tz.gettz('UTC+2'),
            'ArcCorp': tz.gettz('UTC+3'),
            'microTech': tz.gettz('UTC+4'),
            'Local': tz.tzlocal()
        }
    
    @staticmethod
    def get_ship_time(timezone_name: str = 'UTC') -> datetime:
        """Get current time in specified ship timezone"""
        zones = TimeUtils.get_time_zones()
        target_tz = zones.get(timezone_name, tz.UTC)
        return datetime.now(target_tz)
    
    @staticmethod
    def format_duration(start_time: datetime, end_time: Optional[datetime] = None) -> str:
        """Format duration between two times"""
        if end_time is None:
            end_time = datetime.now()
        
        duration = end_time - start_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
