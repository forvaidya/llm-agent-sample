from weather_utils import fetch_weather_data
import asyncio
import random

async def simulate_request_with_random_error():
    """Simulate a request with a random chance of HTTP 500 error."""
    if random.random() < 0.2:  # 20% chance to simulate a 500 error
        error_source = "Simulated API"
        print(f"Simulated HTTP 500 Error from {error_source}: Falling back to alternative data.")
        return {"status": 500, "message": "Internal Server Error", "source": error_source}
    else:
        # Simulate a successful response
        return {"status": 200, "data": "Weather data"}

def main():
    async def bombard_requests():
        location = "Bangalore"
        tasks = [fetch_weather_data(location) for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Request {i + 1} failed with exception: {result}")
            else:
                print(f"Request {i + 1} succeeded with result: {result}")

    async def main():
        """Main function to test weather requests with random errors."""
        for _ in range(10):  # Simulate 10 requests
            response = await simulate_request_with_random_error()
            if response["status"] == 500:
                print(f"Simulated HTTP 500 Error from {response['source']}: {response['message']}")
            else:
                print("Successful Response:", response["data"])

    asyncio.run(bombard_requests())
    asyncio.run(main())

if __name__ == "__main__":
    main()
