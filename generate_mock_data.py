import pandas as pd
import numpy as np

# BC Health Authorities
authorities = [
    'Island Health',
    'Fraser Health',
    'Vancouver Coastal Health',
    'Interior Health',
    'Northern Health'
]

# Create ~50 CHSAs
np.random.seed(42)

data = {
    'health_authority': np.random.choice(authorities, size=50),
    'chsa_name': [f"Community_{i}" for i in range(1, 51)],
    'pct_without_family_doctor': np.random.uniform(5.0, 45.0, size=50), # 5% to 45%
    'median_household_income': np.random.uniform(40000, 150000, size=50),
    'life_expectancy': np.random.uniform(75.0, 85.0, size=50),
    'opioid_overdose_rate': np.random.uniform(10.0, 120.0, size=50), # per 100k
    'er_visits_per_1000': np.random.uniform(300, 1200, size=50) # per 1000
}

df = pd.DataFrame(data)

# Round numbers for realism
df['pct_without_family_doctor'] = df['pct_without_family_doctor'].round(1)
df['median_household_income'] = df['median_household_income'].round(0)
df['life_expectancy'] = df['life_expectancy'].round(1)
df['opioid_overdose_rate'] = df['opioid_overdose_rate'].round(1)
df['er_visits_per_1000'] = df['er_visits_per_1000'].round(1)

df.to_csv('bc_health_indicators.csv', index=False)
print("Created bc_health_indicators.csv with 50 rows of mock data.")
