import httpx
import asyncio
import os
# pyrefly: ignore [missing-import]
import pymupdf

BASE_URL = "http://127.0.0.1:8000"

async def test_papers_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create a dummy PDF file using PyMuPDF for testing
        test_pdf_path = "test_paper.pdf"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Attention Is All You Need")
        page2 = doc.new_page()
        page2.insert_text((50, 50), "The Transformer...")
        doc.save(test_pdf_path)
        doc.close()

        print("1. Register and Login User A")
        email_a = "userA_process@example.com"
        await client.post("/auth/register", json={"name": "User A", "email": email_a, "password": "password123"})
        r = await client.post("/auth/login", json={"email": email_a, "password": "password123"})
        token_a = r.json().get("access_token")
        headers_a = {"Authorization": f"Bearer {token_a}"}

        print("\n2. Create Project for User A")
        r = await client.post("/projects", json={"name": "Paper Processing Research"}, headers=headers_a)
        project_id = r.json().get("id")

        print("\n3. Upload PDF Paper")
        with open(test_pdf_path, "rb") as f:
            files = {"file": ("test_paper.pdf", f, "application/pdf")}
            r = await client.post(f"/projects/{project_id}/papers", files=files, headers=headers_a)
            print("Upload Paper:", r.status_code, r.json())
            paper_id = r.json().get("id")

        print("\n4. Check Status (Expected: uploaded)")
        r = await client.get(f"/papers/{paper_id}/processing-status", headers=headers_a)
        print("Status:", r.status_code, r.json())

        print("\n5. Process PDF Paper")
        r = await client.post(f"/papers/{paper_id}/process", headers=headers_a)
        print("Process:", r.status_code, r.json())

        print("\n6. Check Status (Expected: processed)")
        r = await client.get(f"/papers/{paper_id}/processing-status", headers=headers_a)
        print("Status:", r.status_code, r.json())

        print("\n7. Get Extracted Content")
        r = await client.get(f"/papers/{paper_id}/content", headers=headers_a)
        print("Content:", r.status_code, r.json())

        # Cleanup test file
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    asyncio.run(test_papers_api())
