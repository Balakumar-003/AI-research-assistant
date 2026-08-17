import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8000"

async def test_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("1. Health Check")
        r = await client.get("/health")
        print("Health:", r.status_code, r.json())
        
        print("\n2. Register User A")
        email_a = "userA@example.com"
        r = await client.post("/auth/register", json={"name": "User A", "email": email_a, "password": "password123"})
        if r.status_code not in (201, 400):
            print("Register error", r.text)
            
        print("\n3. Login User A")
        r = await client.post("/auth/login", json={"email": email_a, "password": "password123"})
        token_a = r.json().get("access_token")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        
        print("\n4. Create Project for User A")
        r = await client.post("/projects", json={"name": "NLP Research", "description": "Research on transformers"}, headers=headers_a)
        print("Create Project A:", r.status_code, r.json())
        project_a_id = r.json().get("id")
        
        print("\n5. List Projects for User A")
        r = await client.get("/projects", headers=headers_a)
        print("List Projects A:", r.status_code, r.json())
        
        print("\n6. Get Project A")
        r = await client.get(f"/projects/{project_a_id}", headers=headers_a)
        print("Get Project A:", r.status_code, r.json())
        
        print("\n7. Update Project A")
        r = await client.put(f"/projects/{project_a_id}", json={"name": "NLP Research (Updated)"}, headers=headers_a)
        print("Update Project A:", r.status_code, r.json())
        
        print("\n8. Register User B")
        email_b = "userB@example.com"
        r = await client.post("/auth/register", json={"name": "User B", "email": email_b, "password": "password123"})
        
        print("\n9. Login User B")
        r = await client.post("/auth/login", json={"email": email_b, "password": "password123"})
        token_b = r.json().get("access_token")
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        print("\n10. User B attempts to access User A's project")
        r = await client.get(f"/projects/{project_a_id}", headers=headers_b)
        print("User B Get Project A:", r.status_code, r.json())
        
        print("\n11. User A Deletes Project A")
        r = await client.delete(f"/projects/{project_a_id}", headers=headers_a)
        print("Delete Project A:", r.status_code, r.json())
        
        print("\n12. List Projects for User A after deletion")
        r = await client.get("/projects", headers=headers_a)
        print("List Projects A:", r.status_code, r.json())

if __name__ == "__main__":
    asyncio.run(test_api())
