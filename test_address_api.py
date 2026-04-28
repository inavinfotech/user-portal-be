import httpx
import asyncio
import uuid

async def test_address_api():
    base_url = "http://localhost:8001/api/v1"
    api_key = "app_a489ca0e0ac884c2b1e4319a" # From website .env
    api_secret = "ZgebMm87ZpZhXlWBLdHCNZLfLUlLbRT1htyMPzfy" # From website .env
    
    headers = {
        "X-API-KEY": api_key,
        "X-API-SECRET": api_secret
    }
    
    # We need a real user ID. Let's try to find one or just use a random UUID to see if we get a 404 (which proves the endpoint is reachable)
    test_user_id = str(uuid.uuid4())
    
    print(f"Testing address API at {base_url}")
    
    async with httpx.AsyncClient() as client:
        # 1. Try to get address for random user (should be 404)
        print(f"Fetching address for user {test_user_id}...")
        res = await client.get(f"{base_url}/addresses/user/{test_user_id}", headers=headers)
        print(f"GET status: {res.status_code}")
        
        # 2. Try to create address for random user
        print(f"Creating address for user {test_user_id}...")
        address_data = {
            "full_name": "Test User",
            "phone_number": "1234567890",
            "address_line": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "postal_code": "123456"
        }
        res = await client.post(f"{base_url}/addresses/user/{test_user_id}", headers=headers, json=address_data)
        print(f"POST status: {res.status_code}")
        if res.status_code == 200:
            print("Successfully created address!")
            data = res.json()
            print(f"Created Address ID: {data['id']}")
            
            # 3. Fetch it back
            res = await client.get(f"{base_url}/addresses/user/{test_user_id}", headers=headers)
            print(f"GET back status: {res.status_code}")
            if res.status_code == 200:
                print("Successfully fetched address back!")

if __name__ == "__main__":
    asyncio.run(test_address_api())
