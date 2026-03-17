from mftool import Mftool
import pandas as pd

mf = Mftool()

def get_category_map(target_category="Large Cap"):
    print(f"--- 🔍 Mapping {target_category} Funds ---")
    
    # 1. Get all schemes (this returns a dictionary of {code: name})
    all_schemes = mf.get_scheme_codes()
    
    mapped_funds = []
    
    # 2. Iterate and filter
    # We use a loop because we need to verify the 'category' via get_scheme_details
    # Note: This takes 1-2 mins because it pings AMFI for details
    for code, name in list(all_schemes.items())[:500]: # Limit to 500 for testing
        if "Direct" in name and "Growth" in name:
            try:
                details = mf.get_scheme_details(code)
                # Check if the scheme category matches our target (e.g., 'Equity Scheme - Large Cap Fund')
                if target_category.lower() in details.get('scheme_category', '').lower():
                    mapped_funds.append({
                        "scheme_code": code,
                        "scheme_name": name
                    })
                    print(f"✅ Found: {name}")
            except:
                continue
                
    return pd.DataFrame(mapped_funds)

# Example Usage
# df_large_cap = get_category_map("Large Cap")
# df_large_cap.to_csv("large_cap_codes.csv", index=False)