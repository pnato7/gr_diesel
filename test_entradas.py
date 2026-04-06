#!/usr/bin/env python
from backend.app import create_app
from backend.connection import db

app = create_app()

# Create a test client
with app.test_client() as client:
    # First login with correct credentials
    rv = client.post('/login', data={
        'username': 'patrao',
        'password': 'patrao'
    }, follow_redirects=False)
    
    print(f'Login response status: {rv.status_code}')
    print(f'Login response location: {rv.headers.get("Location")}')
    
    # Check session
    with client.session_transaction() as sess:
        print(f'Session after login: is_owner={sess.get("is_owner")}, user_id={sess.get("user_id")}')
    
    # Then access entradas WITHOUT follow_redirects to see the actual response
    rv = client.get('/entradas', follow_redirects=False)
    
    print(f'Entradas response status: {rv.status_code}')
    
    if rv.status_code == 302:
        print(f'Redirect to: {rv.headers.get("Location")}')
        print('✗ Still redirecting - session not maintained')
    else:
        response_text = rv.data.decode()
        if 'const notas' in response_text:
            print('✓ const notas found')
            for line in response_text.split('\n'):
                if 'const notas' in line:
                    print(f'Line: {line.strip()[:100]}')
