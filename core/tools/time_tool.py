"""
Time tool for SmartDesk AI
Provides accurate current time information for different timezones.
"""

from datetime import datetime
import pytz
from typing import Dict, List, Optional

class TimeTool:
    """
    Tool for getting accurate current time information.
    """
    
    def __init__(self):
        self.common_timezones = {
            'toronto': 'America/Toronto',
            'new_york': 'America/New_York',
            'los_angeles': 'America/Los_Angeles',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney',
            'utc': 'UTC'
        }
    
    def get_current_time(self, timezone_name: str = 'toronto') -> Dict[str, str]:
        """
        Get current time for a specific timezone.
        
        Args:
            timezone_name: Name of the timezone (e.g., 'toronto', 'new_york', 'utc')
            
        Returns:
            Dictionary with formatted time information
        """
        try:
            # Get timezone
            tz_name = self.common_timezones.get(timezone_name.lower(), 'America/Toronto')
            tz = pytz.timezone(tz_name)
            
            # Get current time in that timezone
            now = datetime.now(tz)
            
            # Format the time
            formatted_time = now.strftime("%I:%M:%S %p")
            formatted_date = now.strftime("%A, %B %d, %Y")
            timezone_abbr = now.strftime("%Z")
            
            return {
                'time': formatted_time,
                'date': formatted_date,
                'timezone': tz_name,
                'timezone_abbr': timezone_abbr,
                'iso_format': now.isoformat(),
                'unix_timestamp': int(now.timestamp())
            }
        except Exception as e:
            return {
                'error': f"Error getting time for {timezone_name}: {str(e)}",
                'time': "Error",
                'date': "Error",
                'timezone': timezone_name
            }
    
    def get_time_in_toronto(self) -> Dict[str, str]:
        """Get current time in Toronto, Canada."""
        return self.get_current_time('toronto')
    
    def get_time_in_new_york(self) -> Dict[str, str]:
        """Get current time in New York, USA."""
        return self.get_current_time('new_york')
    
    def get_time_in_london(self) -> Dict[str, str]:
        """Get current time in London, UK."""
        return self.get_current_time('london')
    
    def get_time_in_tokyo(self) -> Dict[str, str]:
        """Get current time in Tokyo, Japan."""
        return self.get_current_time('tokyo')
    
    def get_utc_time(self) -> Dict[str, str]:
        """Get current UTC time."""
        return self.get_current_time('utc')
    
    def get_all_times(self) -> Dict[str, Dict[str, str]]:
        """
        Get current time for all common timezones.
        
        Returns:
            Dictionary with times for all timezones
        """
        times = {}
        for tz_name in self.common_timezones.keys():
            times[tz_name] = self.get_current_time(tz_name)
        return times
    
    def format_time_difference(self, time1: datetime, time2: datetime) -> str:
        """
        Format the difference between two times.
        
        Args:
            time1: First datetime object
            time2: Second datetime object
            
        Returns:
            Formatted time difference string
        """
        try:
            # Ensure both times are timezone-aware
            if time1.tzinfo is None:
                time1 = pytz.UTC.localize(time1)
            if time2.tzinfo is None:
                time2 = pytz.UTC.localize(time2)
            
            diff = abs(time2 - time1)
            total_seconds = int(diff.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds} seconds"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif total_seconds < 86400:
                hours = total_seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                days = total_seconds // 86400
                return f"{days} day{'s' if days != 1 else ''}"
        except Exception as e:
            return f"Error calculating time difference: {str(e)}"
    
    def get_timezone_info(self, timezone_name: str = 'toronto') -> Dict[str, str]:
        """
        Get detailed timezone information.
        
        Args:
            timezone_name: Name of the timezone
            
        Returns:
            Dictionary with timezone information
        """
        try:
            tz_name = self.common_timezones.get(timezone_name.lower(), 'America/Toronto')
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            
            return {
                'timezone_name': tz_name,
                'timezone_abbr': now.strftime("%Z"),
                'utc_offset': now.strftime("%z"),
                'is_dst': tz.dst(now) != tz.utcoffset(now),
                'current_time': now.strftime("%I:%M:%S %p"),
                'current_date': now.strftime("%A, %B %d, %Y")
            }
        except Exception as e:
            return {
                'error': f"Error getting timezone info for {timezone_name}: {str(e)}"
            }

# Global instance
time_tool = TimeTool()

def get_current_time(timezone: str = 'toronto') -> str:
    """
    Simple function to get current time as a formatted string.
    
    Args:
        timezone: Timezone name (default: 'toronto')
        
    Returns:
        Formatted time string
    """
    result = time_tool.get_current_time(timezone)
    if 'error' in result:
        return result['error']
    
    return f"{result['time']} {result['timezone_abbr']} on {result['date']}"

def get_time_in_toronto() -> str:
    """Get current time in Toronto as a formatted string."""
    return get_current_time('toronto') 