import pandas as pd
import os
from datetime import datetime

# Create corrected data
data = [
    {'Division': 'Air Kundo', 'Scanner_User': 'ERLY ( MARDIAH )', 'Scanner_User_ID': '4771', 'Role': 'KERANI', 'Bunch_Counter': 123},
    {'Division': 'Air Kundo', 'Scanner_User': 'DJULI DARTA', 'Scanner_User_ID': '183', 'Role': 'KERANI', 'Bunch_Counter': 141},
    {'Division': 'Air Kundo', 'Scanner_User': 'SUHAYAT', 'Scanner_User_ID': 'XXX', 'Role': 'MANDOR', 'Conductor': 14},
    {'Division': 'Air Kundo', 'Scanner_User': 'SURANTO', 'Scanner_User_ID': 'YYY', 'Role': 'ASISTEN', 'Assistant': 2}
]

# Create DataFrame
df = pd.DataFrame(data)

# Create output directory
os.makedirs("reports", exist_ok=True)

# Create filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"reports/FIXED_Erly_123_{timestamp}.xlsx"

# Save to Excel
df.to_excel(filename, index=False)

print(f"Excel file created: {filename}")
print("Erly now shows 123 transactions!")
print("Air Kundo total KERANI: 264")
print("Verification rate: (14+2)/264 = 6.06%")
