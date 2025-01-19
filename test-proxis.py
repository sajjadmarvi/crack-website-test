import requests

def check_proxies_from_file(file_path):
    """
    Check which proxies from a file are working.
    
    Args:
        file_path (str): Path to the file containing proxy list (one proxy per line in the format 'IP:PORT').
    
    Returns:
        list: A list of working proxies.
    """
    working_proxies = []
    test_url = "https://www.google.com"  # URL to test proxies
    
    try:
        # Read the proxy list from the file
        with open(file_path, "r") as file:
            proxy_list = [line.strip() for line in file if line.strip()]
        
        for proxy in proxy_list:
            proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
            try:
                # Send a request using the proxy
                response = requests.get(test_url, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    print(f"Proxy {proxy} is working.")
                    working_proxies.append(proxy)
                else:
                    print(f"Proxy {proxy} returned status code {response.status_code}.")
            except Exception as e:
                print(f"Proxy {proxy} failed. Error: {e}")
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return working_proxies

# Example usage
file_path = input("Enter the path to the proxy list file: ")
working_proxies = check_proxies_from_file(file_path)

# Save the working proxies to a new file
if working_proxies:
    output_file = "working_proxies.txt"
    with open(output_file, "w") as file:
        file.write("\n".join(working_proxies))
    print(f"\nWorking proxies have been saved to {output_file}")
else:
    print("\nNo working proxies found.")

