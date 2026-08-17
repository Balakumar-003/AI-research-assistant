import httpx
import asyncio
import os

BASE_URL = "http://127.0.0.1:8000"

async def test_papers_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create a dummy PDF file for testing
        test_pdf_path = "test_paper.pdf"
        with open(test_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy pdf content")

        print("1. Register and Login User A")
        email_a = "userA_papers@example.com"
        await client.post("/auth/register", json={"name": "User A", "email": email_a, "password": "password123"})
        r = await client.post("/auth/login", json={"email": email_a, "password": "password123"})
        token_a = r.json().get("access_token")
        headers_a = {"Authorization": f"Bearer {token_a}"}

        print("\n2. Create Project for User A")
        r = await client.post("/projects", json={"name": "Paper Research"}, headers=headers_a)
        project_id = r.json().get("id")
        print("Project created:", project_id)

        print("\n3. Upload PDF Paper")
        with open(test_pdf_path, "rb") as f:
            files = {"file": ("test_paper.pdf", f, "application/pdf")}
            r = await client.post(f"/projects/{project_id}/papers", files=files, headers=headers_a)
            print("Upload Paper:", r.status_code, r.json())
            paper_id = r.json().get("id")

        print("\n4. List Papers in Project")
        r = await client.get(f"/projects/{project_id}/papers", headers=headers_a)
        print("List Papers:", r.status_code, r.json())

        print("\n5. Get Paper Metadata")
        r = await client.get(f"/papers/{paper_id}", headers=headers_a)
        print("Get Paper:", r.status_code, r.json())

        print("\n6. Register and Login User B")
        email_b = "userB_papers@example.com"
        await client.post("/auth/register", json={"name": "User B", "email": email_b, "password": "password123"})
        r = await client.post("/auth/login", json={"email": email_b, "password": "password123"})
        token_b = r.json().get("access_token")
        headers_b = {"Authorization": f"Bearer {token_b}"}

        print("\n7. User B Attempts to Access User A's Paper")
        r = await client.get(f"/papers/{paper_id}", headers=headers_b)
        print("User B Get Paper:", r.status_code, r.json())
        r = await client.delete(f"/papers/{paper_id}", headers=headers_b)
        print("User B Delete Paper:", r.status_code, r.json())

        print("\n8. User A Deletes Paper")
        r = await client.delete(f"/papers/{paper_id}", headers=headers_a)
        print("User A Delete Paper:", r.status_code, r.json())

        print("\n9. Verify Deletion")
        r = await client.get(f"/projects/{project_id}/papers", headers=headers_a)
        print("List Papers after deletion:", r.status_code, r.json())

        # Cleanup test file
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    asyncio.run(test_papers_api())
