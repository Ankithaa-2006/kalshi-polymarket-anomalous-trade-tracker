import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Test gamma API markets
        r1 = await client.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1")
        print("Gamma Markets status:", r1.status_code)
        
        # Test CLOB API or Gamma API for trades?
        # Let's try Gamma events?
        r2 = await client.get("https://gamma-api.polymarket.com/events?limit=1")
        print("Gamma Events status:", r2.status_code)

if __name__ == "__main__":
    asyncio.run(main())
