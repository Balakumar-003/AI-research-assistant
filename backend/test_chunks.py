import httpx
import asyncio
import os
import pymupdf

BASE_URL = "http://127.0.0.1:8000"

async def test_chunks_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create a dummy PDF file using PyMuPDF for testing
        test_pdf_path = "test_chunk_paper.pdf"
        doc = pymupdf.open()
        
        # Add 3 pages of text
        for i in range(3):
            page = doc.new_page()
            text = f"This is page {i+1} of the document. " * 50 # Make it long enough to trigger chunking
            page.insert_text((50, 50), text)
            
        doc.save(test_pdf_path)
        doc.close()

        print("1. Register and Login User A")
        email_a = "userA_chunks@example.com"
        await client.post("/auth/register", json={"name": "User A", "email": email_a, "password": "password123"})
        r = await client.post("/auth/login", json={"email": email_a, "password": "password123"})
        token_a = r.json().get("access_token")
        headers_a = {"Authorization": f"Bearer {token_a}"}

        print("\n2. Create Project for User A")
        r = await client.post("/projects", json={"name": "Chunking Research"}, headers=headers_a)
        project_id = r.json().get("id")

        print("\n3. Upload PDF Paper")
        with open(test_pdf_path, "rb") as f:
            files = {"file": ("test_chunk_paper.pdf", f, "application/pdf")}
            r = await client.post(f"/projects/{project_id}/papers", files=files, headers=headers_a)
            paper_id = r.json().get("id")

        print("\n4. Process PDF Paper")
        r = await client.post(f"/papers/{paper_id}/process", headers=headers_a)
        
        print("\n5. Generate Chunks")
        r = await client.post(f"/papers/{paper_id}/chunks", headers=headers_a)
        print("Generate Chunks:", r.status_code, r.json())
        
        print("\n6. List Chunks")
        r = await client.get(f"/papers/{paper_id}/chunks", headers=headers_a)
        chunks_data = r.json()
        print("List Chunks:", r.status_code, f"Total: {chunks_data['total']}")
        
        if chunks_data['chunks']:
            first_chunk = chunks_data['chunks'][0]
            print("\n7. Get Single Chunk")
            r = await client.get(f"/chunks/{first_chunk['chunk_id']}", headers=headers_a)
            print("Get Chunk:", r.status_code, r.json())
            
        print("\n8. Delete Chunks")
        r = await client.delete(f"/papers/{paper_id}/chunks", headers=headers_a)
        print("Delete Chunks:", r.status_code, r.json())
        
        print("\n9. Verify Deletion")
        r = await client.get(f"/papers/{paper_id}/chunks", headers=headers_a)
        print("List Chunks after deletion:", r.status_code, r.json())

        # Cleanup test file
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    asyncio.run(test_chunks_api())
