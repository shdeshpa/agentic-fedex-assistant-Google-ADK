# =============================================================================
#  Filename: weather_tool.py
#
#  Short Description: Weather lookup tool for ZIP codes to inform shipping decisions
#
#  Creation date: 2025-10-11
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Weather Lookup Tool for FedEx Shipping Assistant

Provides weather information for destination ZIP codes to help users make
informed shipping decisions, especially for weather-sensitive packages.

Features:
- ZIP code to weather lookup
- Current conditions and forecast
- Weather impact recommendations
- Free API using OpenWeatherMap
"""

import requests
import os
from typing import Dict, Any, Optional
from loguru import logger


class WeatherLookupTool:
    """
    Weather lookup tool that provides weather information for ZIP codes.
    
    Uses OpenWeatherMap API (free tier) to get current weather conditions
    and forecasts for destination locations.
    """
    
    def __init__(self):
        """Initialize the weather lookup tool."""
        # OpenWeatherMap API key (free tier available)
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("⚠️ No OpenWeatherMap API key found. Weather features disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("🌤️ Weather lookup tool initialized")
    
    def get_weather_for_zip(self, zip_code: str, country_code: str = "US") -> Dict[str, Any]:
        """
        Get weather information for a ZIP code.
        
        Args:
            zip_code: ZIP code to look up weather for
            country_code: Country code (default: US)
            
        Returns:
            Dictionary with weather information or error message
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Weather service not available. API key not configured.',
                'zip_code': zip_code,
                'weather_info': None
            }
        
        try:
            logger.info(f"🌤️ Looking up weather for ZIP {zip_code}")
            
            # Get current weather
            current_url = f"{self.base_url}/weather"
            params = {
                'zip': f"{zip_code},{country_code}",
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit and mph
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_info = {
                    'location': f"{data['name']}, {data['sys']['country']}",
                    'current_temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed']),
                    'description': data['weather'][0]['description'].title(),
                    'main_condition': data['weather'][0]['main'],
                    'visibility': round(data.get('visibility', 0) / 1609.34, 1) if data.get('visibility') else 'N/A',  # Convert to miles
                    'pressure': data['main']['pressure'],
                    'zip_code': zip_code
                }
                
                # Add shipping recommendations based on weather
                weather_info['shipping_recommendation'] = self._get_shipping_recommendation(weather_info)
                
                logger.success(f"✅ Weather retrieved for {weather_info['location']}")
                
                return {
                    'success': True,
                    'weather_info': weather_info,
                    'zip_code': zip_code
                }
                
            elif response.status_code == 404:
                logger.error(f"❌ ZIP code {zip_code} not found")
                return {
                    'success': False,
                    'error': f'ZIP code {zip_code} not found',
                    'zip_code': zip_code,
                    'weather_info': None
                }
            else:
                logger.error(f"❌ Weather API error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Weather service error: {response.status_code}',
                    'zip_code': zip_code,
                    'weather_info': None
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Weather API timeout")
            return {
                'success': False,
                'error': 'Weather service timeout',
                'zip_code': zip_code,
                'weather_info': None
            }
        except Exception as e:
            logger.error(f"❌ Weather lookup error: {e}")
            return {
                'success': False,
                'error': f'Weather lookup failed: {str(e)}',
                'zip_code': zip_code,
                'weather_info': None
            }
    
    def _get_shipping_recommendation(self, weather_info: Dict[str, Any]) -> str:
        """
        Generate shipping recommendations based on weather conditions.
        
        Args:
            weather_info: Weather data dictionary
            
        Returns:
            Recommendation string
        """
        temp = weather_info['current_temp']
        condition = weather_info['main_condition'].lower()
        wind_speed = weather_info['wind_speed']
        visibility = weather_info['visibility']
        
        recommendations = []
        
        # Temperature recommendations
        if temp < 32:  # Freezing
            recommendations.append("⚠️ **Freezing temperatures** - Consider protective packaging for electronics, liquids, or temperature-sensitive items")
        elif temp > 90:  # Hot
            recommendations.append("🌡️ **High temperatures** - Avoid shipping perishable items or electronics without temperature protection")
        
        # Weather condition recommendations
        if condition in ['rain', 'drizzle']:
            recommendations.append("🌧️ **Rainy conditions** - Ensure waterproof packaging for sensitive items")
        elif condition in ['snow', 'mist']:
            recommendations.append("❄️ **Snow/fog conditions** - Delays possible, consider expedited shipping")
        elif condition in ['thunderstorm']:
            recommendations.append("⛈️ **Storm conditions** - Significant delays likely, avoid urgent shipments")
        
        # Wind recommendations
        if wind_speed > 25:  # Strong winds
            recommendations.append("💨 **High winds** - Possible delivery delays, secure packaging recommended")
        
        # Visibility recommendations
        if isinstance(visibility, (int, float)) and visibility < 1:  # Poor visibility
            recommendations.append("🌫️ **Poor visibility** - Delivery delays expected")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("✅ **Good conditions** - Normal shipping should proceed without issues")
        
        return "\n".join(recommendations)
    
    def get_weather_summary(self, zip_code: str) -> str:
        """
        Get a formatted weather summary for display in the UI.
        
        Args:
            zip_code: ZIP code to get weather for
            
        Returns:
            Formatted weather summary string
        """
        result = self.get_weather_for_zip(zip_code)
        
        if not result['success']:
            return f"🌤️ **Weather**: {result['error']}"
        
        weather = result['weather_info']
        
        summary = f"""
🌤️ **Weather for {weather['location']} (ZIP: {zip_code})**

**Current Conditions:**
• Temperature: {weather['current_temp']}°F (feels like {weather['feels_like']}°F)
• Condition: {weather['description']}
• Humidity: {weather['humidity']}%
• Wind: {weather['wind_speed']} mph
• Visibility: {weather['visibility']} miles

**Shipping Recommendation:**
{weather['shipping_recommendation']}
        """.strip()
        
        return summary
    
    def is_weather_suitable_for_shipping(self, zip_code: str, package_type: str = "standard") -> Dict[str, Any]:
        """
        Determine if weather conditions are suitable for shipping.
        
        Args:
            zip_code: Destination ZIP code
            package_type: Type of package (standard, fragile, perishable, etc.)
            
        Returns:
            Dictionary with suitability assessment
        """
        result = self.get_weather_for_zip(zip_code)
        
        if not result['success']:
            return {
                'suitable': True,  # Default to suitable if weather unavailable
                'reason': 'Weather data unavailable',
                'recommendation': 'Proceed with normal shipping'
            }
        
        weather = result['weather_info']
        temp = weather['current_temp']
        condition = weather['main_condition'].lower()
        wind_speed = weather['wind_speed']
        
        issues = []
        
        # Package-specific checks
        if package_type.lower() in ['perishable', 'food', 'medicine']:
            if temp < 32 or temp > 90:
                issues.append(f"Temperature unsuitable for {package_type} ({temp}°F)")
        
        if package_type.lower() in ['fragile', 'electronics']:
            if condition in ['thunderstorm', 'rain'] and wind_speed > 20:
                issues.append("Storm conditions may affect fragile items")
        
        # General weather checks
        if condition == 'thunderstorm':
            issues.append("Severe weather - delivery delays expected")
        elif wind_speed > 30:
            issues.append("Extreme winds - delivery may be delayed")
        
        if issues:
            return {
                'suitable': False,
                'issues': issues,
                'recommendation': 'Consider delaying shipment or using protective packaging'
            }
        else:
            return {
                'suitable': True,
                'issues': [],
                'recommendation': 'Weather conditions are suitable for shipping'
            }


# Example usage and testing
if __name__ == "__main__":
    # Test the weather tool
    weather_tool = WeatherLookupTool()
    
    if weather_tool.enabled:
        # Test with a sample ZIP code
        result = weather_tool.get_weather_for_zip("10001")  # New York
        print("Weather lookup result:")
        print(result)
        
        if result['success']:
            print("\nWeather summary:")
            print(weather_tool.get_weather_summary("10001"))
    else:
        print("Weather tool disabled - no API key configured")
        print("To enable weather features:")
        print("1. Sign up at https://openweathermap.org/api")
        print("2. Get a free API key")
        print("3. Add OPENWEATHER_API_KEY to your .env file")
