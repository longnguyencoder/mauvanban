
import requests
import os
import sys

# Configuration
BASE_URL = 'http://localhost:5000/api'
LOGIN_Email = 'admin@mauvanban.vn'
LOGIN_PASSWORD = 'admin123'

# Helper to print colored output
def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️ {msg}")

def test_preview():
    # 1. Login
    print_info("Logging in...")
    login_resp = requests.post(f'{BASE_URL}/auth/login', json={
        'email': LOGIN_Email,
        'password': LOGIN_PASSWORD
    })
    
    if login_resp.status_code != 200:
        print_error(f"Login failed: {login_resp.text}")
        return
        
    token = login_resp.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print_success("Login successful")

    # 2. Prepare files
    # Use existing PDF
    pdf_path_1 = r'c:\Users\PT COMPUTER\Documents\GitHub\mauvanban\backend\uploads\documents\0c92b4eba078466dbe42ad094f92bfb5_20251217_143842.pdf'
    
    if not os.path.exists(pdf_path_1):
        print_error(f"Test file not found: {pdf_path_1}")
        return

    # Use same PDF for second file
    files = [
        ('files[]', ('test_file_1.pdf', open(pdf_path_1, 'rb'), 'application/pdf')),
        ('files[]', ('test_file_2.pdf', open(pdf_path_1, 'rb'), 'application/pdf'))
    ]
    
    # Fetch categories
    print_info("Fetching categories...")
    cat_resp = requests.get(f'{BASE_URL}/categories')
    if cat_resp.status_code != 200:
        print_error("Failed to fetch categories")
        return
    
    json_data = cat_resp.json()
    print_info(f"Category response structure keys: {json_data.keys()}")
    if 'data' in json_data:
        data_content = json_data['data']
        if isinstance(data_content, list):
             categories = data_content
        elif isinstance(data_content, dict) and 'data' in data_content:
             categories = data_content['data']
        else:
             print_error(f"Unexpected data format: {type(data_content)}")
             return
    else:
         print_error("No 'data' key in response")
         return
    
    if not categories:
        print_error("No categories found. Run seed_data.py first.")
        # Try to run seed if needed, but for now just fail
        return

    first_cat_id = categories[0]['id']
    print_info(f"Using category ID: {first_cat_id}")

    import uuid
    random_code = f"TEST-PREVIEW-{uuid.uuid4().hex[:6]}"
    
    data = {
        'code': random_code,
        'title': 'Test Document Preview Feature',
        'category_id': first_cat_id, 
        'price': 0,
        'description': 'Testing multi-file upload and preview generation',
        'is_featured': 'false'
    }

    # 3. Upload Document
    print_info("Uploading document with multiple files...")
    response = requests.post(
        f'{BASE_URL}/admin/documents',
        headers=headers,
        data=data,
        files=files
    )

    if response.status_code != 201:
        print_error(f"Upload failed: {response.text}")
        return

    doc_data = response.json()['data']
    doc_id = doc_data['id']
    print_success(f"Document created: {doc_data['title']} (ID: {doc_id})")

    # 4. Verify Files and Previews
    print_info("Verifying document details...")
    
    # files info is already in the create response
    files_info = doc_data.get('files', [])
    
    if len(files_info) != 2:
        print_error(f"Expected 2 files, got {len(files_info)}")
    else:
        print_success(f"Found {len(files_info)} files attached")

    # Check File 1
    file1 = files_info[0]
    print_info(f"Checking File 1: {file1['original_filename']}")
    if file1['file_type'] == 'pdf':
        if file1['preview_url']:
            print_success(f"Preview URL generated: {file1['preview_url']}")
            
            # Verify thumbnail_url is set
            if doc_data.get('thumbnail_url') == file1['preview_url']:
                print_success("Thumbnail URL matches Preview URL (Auto-set worked)")
            else:
                print_error(f"Thumbnail URL mismatch! Expected {file1['preview_url']}, got {doc_data.get('thumbnail_url')}")

            # Verify preview file exists
            preview_path = os.path.join(r'c:\Users\PT COMPUTER\Documents\GitHub\mauvanban\backend', file1['preview_url'].lstrip('/'))
            if os.path.exists(preview_path):
                    print_success("Preview file exists on disk")
            else:
                    print_error(f"Preview file NOT found on disk: {preview_path}")
        else:
            print_error("Preview URL is missing for PDF!")
    
    # Check File 2
    file2 = files_info[1]
    print_info(f"Checking File 2: {file2['original_filename']}")
    if file2['file_type'] == 'pdf':
         if file2['preview_url']:
             print_success(f"Preview URL generated for second file: {file2['preview_url']}")
         else:
             print_error("Preview URL missing for second PDF")

             print_error("Preview URL missing for second PDF")

def test_manual_thumbnail():
    print_info("\n--- Testing Manual Thumbnail Upload (Word File) ---")
    
    # 1. Login (Reuse check, but need simpler flow or just assume logged in if running full script. 
    # Better to keep it self contained or shared state. Let's just re-login or clean up.)
    
    login_resp = requests.post(f'{BASE_URL}/auth/login', json={
        'email': LOGIN_Email,
        'password': LOGIN_PASSWORD
    })
    token = login_resp.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Fetch Category (Corrected Logic)
    cat_resp = requests.get(f'{BASE_URL}/categories')
    json_data = cat_resp.json()
    
    # Check if data is list or dict
    if isinstance(json_data.get('data'), list):
         categories_list = json_data['data']
    else:
         categories_list = json_data.get('data', {}).get('data', [])

    if not categories_list:
        print_error("No categories found")
        return
    cat_id = categories_list[0]['id']

    # 2. Create Dummy Word & Image
    word_path = 'test_doc.docx'
    thumb_path = 'test_thumb.jpg'
    
    with open(word_path, 'w') as f: f.write("Dummy Word content")
    # Create simple blank image for thumb
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'blue')
    img.save(thumb_path)

    try:
        # 3. Upload Thumbnail
        print_info("Uploading thumbnail image...")
        with open(thumb_path, 'rb') as f:
            thumb_files = {'file': f}
            thumb_resp = requests.post(f'{BASE_URL}/upload/image', headers=headers, files=thumb_files)
        
        if thumb_resp.status_code not in [200, 201]:
             print_error(f"Thumbnail upload failed: {thumb_resp.text}")
             return

        uploaded_thumb_url = thumb_resp.json()['data']['file_url']
        print_success(f"Thumbnail uploaded: {uploaded_thumb_url}")

        # 4. Create Document
        import uuid
        code = f"TEST-WORD-{uuid.uuid4().hex[:6]}"
        
        data = {
            'code': code,
            'title': 'Test Word Doc with Manual Thumbnail',
            'category_id': cat_id,
            'price': 0,
            'thumbnail_url': uploaded_thumb_url,
            'description': 'Testing word file with manual cover image'
        }

        print_info("Creating document...")
        # Open file in a context manager to ensure it closes
        with open(word_path, 'rb') as f_word:
            files_payload = [
                ('files[]', ('test_doc.docx', f_word, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
            ]
            
            response = requests.post(f'{BASE_URL}/admin/documents', headers=headers, data=data, files=files_payload)

        if response.status_code != 201:
            print_error(f"Document creation failed: {response.text}")
            return

        doc_data = response.json()['data']
        print_success(f"Document created: {doc_data['title']} (ID: {doc_data['id']})")
        
        # 5. Verify
        if doc_data.get('thumbnail_url') == uploaded_thumb_url:
            print_success("Document thumbnail matches manually uploaded image.")
        else:
            print_error(f"Thumbnail mismatch! Expected {uploaded_thumb_url}, Got {doc_data.get('thumbnail_url')}")

    finally:
        # Clean up files
        try:
            if os.path.exists(word_path): os.remove(word_path)
            if os.path.exists(thumb_path): os.remove(thumb_path)
        except Exception as e:
            print_error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    test_preview()
    test_manual_thumbnail()
