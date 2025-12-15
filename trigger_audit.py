import requests
import time

print("--- Triggering 10 Simulation Episodes ---")
for i in range(10):
    try:
        r = requests.get('http://localhost:5000/api/train')
        if r.status_code == 200:
            print(f"Episode {i+1}: Success")
        else:
            print(f"Episode {i+1}: Failed {r.status_code}")
    except Exception as e:
        print(f"Episode {i+1}: Error {e}")
    time.sleep(0.5)
print("--- Done ---")
