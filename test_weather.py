import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the AI_app src to path
ai_app_src = Path(__file__).parent / "apps" / "AI_app" / "src"
sys.path.insert(0, str(ai_app_src))

from PlantCare_AI.utils.weather_info import WeatherForecastTool

print("=" * 60)
print("WEATHER TOOL TEST")
print("=" * 60)

# Check API Key
api_key = os.getenv("OPENWEATHERMAP_API_KEY")
print(f"\n1. Checking API Key...")
if api_key:
    print(f"   API Key found: {api_key[:10]}...***")
else:
    print(f"   ERROR: OPENWEATHERMAP_API_KEY not found in .env")
    exit(1)

# Initialize Weather Tool
print(f"\n2. Initializing WeatherForecastTool...")
try:
    weather_tool = WeatherForecastTool(api_key=api_key)
    print(f"   SUCCESS: WeatherForecastTool initialized")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test getting current weather for a city
test_cities = ["Mumbai", "New York", "London"]

for city in test_cities:
    print(f"\n3. Testing get_current_weather('{city}')...")
    try:
        result = weather_tool.get_current_weather(city)
        
        if result and "main" in result:
            print(f"   SUCCESS for {city}:")
            print(f"   - Temperature: {result['main']['temp']}°C")
            print(f"   - Humidity: {result['main']['humidity']}%")
            print(f"   - Description: {result['weather'][0]['description']}")
            print(f"   - Pressure: {result['main']['pressure']} hPa")
        else:
            print(f"   FAILED: No valid data returned")
            print(f"   Response: {result}")
    except Exception as e:
        print(f"   ERROR: {e}")

# Test forecast
print(f"\n4. Testing get_forecast_weather('Mumbai')...")
try:
    forecast = weather_tool.get_forecast_weather("Mumbai")
    
    if forecast and "list" in forecast:
        print(f"   SUCCESS: Forecast data retrieved")
        print(f"   - Number of forecasts: {len(forecast['list'])}")
        if forecast['list']:
            next_forecast = forecast['list'][0]
            print(f"   - Next forecast: {next_forecast['weather'][0]['description']}")
            print(f"   - Temperature: {next_forecast['main']['temp']}°C")
    else:
        print(f"   FAILED: No valid forecast data")
        print(f"   Response: {forecast}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
