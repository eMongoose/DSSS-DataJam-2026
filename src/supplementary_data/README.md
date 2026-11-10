=================================================================================================
Notes:

``cs`` stands for clean_supplementary: each file cleans the corresponding file
=================================================================================================
File explanations and ouptuts:

# Supplementary datasets, staged for all teams

__CMHC Rental Market Survey__

1. **Housing Market Information Portal**: vacancy, average and median rents, turnover, and universe counts by zone.

                     Neighbourhood vacancy_rate vr_conf avg_rent ar_conf med_rent mr_c    Units
0            West End/Stanley Park          1.7      c     1,914      b     1,950   b     3,915
1                      English Bay          2.7      b     2,020      a     2,000   a     6,773
2                         Downtown          4.3      b     2,198      a     2,140   a    12,303
3              South Granville/Oak          1.8      b     1,929      a     1,839   a     9,174
4             Kitsilano/Point Grey          1.7      b     2,051      a     1,931   a     7,632
5              Westside/Kerrisdale          2.4      b     2,385      b     2,300   b     3,559
6                          Marpole          2.6      c     1,540      b     1,532   b     3,799
7   Mount Pleasant/Renfrew Heights          2.5      c     1,903      a     1,800   a     8,249
8                    East Hastings          3.8      b     1,827      a     1,750   a     6,335
9              Southeast Vancouver          2.4      b     1,968      a     1,920   b     3,872
10      University Endowment Lands          1.3      a     2,805      a     2,760   b     2,082
11          Central Park/Metrotown           **     NaN    1,958      b     1,800   c     5,191
12               Southeast Burnaby          3.6      d     1,641      b     1,600   a     2,324
13                   North Burnaby          5.6      d     1,847      a     1,800   a     4,256
14                 New Westminster          5.8      d     1,794      a     1,738   a    10,622
15              North Vancouver CY          2.9      b     2,127      a     2,000   a     7,848
16              North Vancouver DM          3.3      b     2,683      b     2,551   a     2,049
17                  West Vancouver          1.6      c     2,577      b     2,300   c     2,747
18                        Richmond          3.1      b     1,887      a     1,868   a     3,311
19                           Delta          1.5      a     1,676      a     1,800   b     1,735
20                          Surrey          4.3      b     1,728      a     1,740   a     8,201
21                      White Rock          5.1      c     1,547      b     1,448   b     1,405
22     Langley City and Langley DM            3      a     2,007      a     2,000   a     4,065
23                      Tri-Cities           **     NaN    1,936      b     1,825   b     6,108
24        Maple Ridge/Pitt Meadows          2.3      b     1,514      a     1,600   b     1,796
25                       Vancouver          3.7      a     1,970      a     1,875   a   129,351

2. **Vacancy rates by rent quartile**: vacancy by price tier, more useful than a headline rate for anything about market segments.

__Duplicate Municipalities__: (TODO: INVESTIGATE WHY)

  census_subdivision  q1_vacancy  q2_vacancy  q3_vacancy  q4_vacancy
        Langley (CY)         2.2         0.5         1.0         1.1
        Langley (CY)         1.3         0.3         4.2         1.3
North Vancouver (CY)         NaN         NaN         3.1         4.5
North Vancouver (CY)         0.4         0.2         0.4         2.7

Metro Vancouver Q4 Vacancy Ranking:
 rank      census_subdivision  q1_vacancy  q2_vacancy  q3_vacancy  q4_vacancy
    1           Richmond (CY)         0.2         0.1         0.0         0.3
    2 Metro Vancouver A (RDA)         0.8         0.0         0.3         0.3
    3          Coquitlam (CY)         0.1         0.2         0.8         0.5
    4     Port Coquitlam (CY)         0.0         0.0         0.0         0.6
    5              Delta (CY)         0.3         0.5         0.0         1.3
    6         White Rock (CY)         0.0         0.8         2.5         1.4
    7          Vancouver (CY)         0.6         0.5         0.6         1.5 <-- e.g.
    8     West Vancouver (DM)         0.2         0.2         0.6         1.5
    9    New Westminster (CY)         0.3         0.9         0.7         1.7
   10            Burnaby (CY)         1.1         0.4         1.0         2.3
   11        Maple Ridge (CY)         1.8         0.0         1.1         2.9
   12             Surrey (CY)         0.3         0.3         0.8         3.3

---
Interpretation (Vancouver example):

Q1 = Cheapest rentals (0-25%), 
Q2 = Lower-Middle priced rentals (25-50%), 
Q3 = Upper-middle priced rentals (50-75%), 
Q4 = Most expensive rentals (>75%)

Rent quartile	Vacancy rate	Interpretation
Q1	            0.6%	        0.6% of the lowest-priced rental units were vacant
Q2	            0.5%	        0.5% of lower-middle-priced units were vacant
Q3	            0.6%	        0.6% of upper-middle-priced units were vacant
Q4	            1.5%	        1.5% of the highest-priced units were vacant


3. **Rent quartiles**: the rent distribution rather than just the average.

OUTPUT TRUNCATED:

province    centre      census_subdivision dwelling_type bedroom_type  p25_rent  p50_rent  p75_rent
    B.C. Vancouver            Langley (DM)   Apt & Other    1 Bedroom      1700      1961      2000
    B.C. Vancouver            Langley (DM)   Apt & Other    2 Bedroom      1914      2238      2675
    B.C. Vancouver            Langley (DM)   Apt & Other        Total      1810      2000      2270
    B.C. Vancouver            Langley (DM)         Total    1 Bedroom      1700      1961      2000
    B.C. Vancouver            Langley (DM)         Total    2 Bedroom      1914      2238      2675
    B.C. Vancouver            Langley (DM)         Total        Total      1810      2000      2270
    B.C. Vancouver            Langley (CY)   Apt & Other    1 Bedroom      1100      1450      1700
    B.C. Vancouver            Langley (CY)   Apt & Other    2 Bedroom      1567      2000      2275
    B.C. Vancouver            Langley (CY)   Apt & Other  3 Bedroom +      2500      2958      3200
    B.C. Vancouver            Langley (CY)   Apt & Other        Total      1342      1700      2050
    B.C. Vancouver            Langley (CY)         Total    1 Bedroom      1100      1450      1700


4. **Number of units by building size**: the rental universe, useful for sizing displacement effects.
bu = bedroom unit

OUTPUT TRUNCATED:

province    centre                           zone                  neighbourhood dwelling_type structure_size  bachelor_units  one_bu  two_bu  three_plus_bu  total_units
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North   Apt & Other           6-19             1.0     2.0    20.0            2.0         25.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North   Apt & Other          20-49           109.0   306.0   162.0            1.0        578.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North   Apt & Other          50-99            93.0   596.0   106.0           23.0        818.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North   Apt & Other        100-199             0.0   119.0     6.0            0.0        125.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North   Apt & Other          Total           203.0  1023.0   294.0           26.0       1546.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North         Total           6-19             1.0     2.0    20.0            2.0         25.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North         Total          20-49           109.0   306.0   162.0            1.0        578.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North         Total          50-99            93.0   596.0   106.0           23.0        818.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North         Total        100-199             0.0   119.0     6.0            0.0        125.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park North         Total          Total           203.0  1023.0   294.0           26.0       1546.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South   Apt & Other           6-19            15.0    74.0    10.0            1.0        100.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South   Apt & Other          20-49           327.0   678.0   124.0            7.0       1136.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South   Apt & Other          50-99           110.0   516.0    43.0            1.0        670.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South   Apt & Other        100-199            27.0   402.0    29.0            0.0        458.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South   Apt & Other          Total           479.0  1670.0   206.0            9.0       2364.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South         Total           6-19            15.0    74.0    10.0            1.0        100.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South         Total          20-49           327.0   678.0   124.0            7.0       1136.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South         Total          50-99           110.0   516.0    43.0            1.0        670.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South         Total        100-199            27.0   402.0    29.0            0.0        458.0
    B.C. Vancouver          West End/Stanley Park    West End/Stanley Park South         Total          Total           479.0  1670.0   206.0            9.0       2364.0

5. **Percentile rents for small centres**: relevant if you look at smaller BC communities, which the legality constraint pushes toward.

METRO VANCOUVER 2025 RENT PERCENTILES:
        province met_centre                       rms_zone  studio_p30  studio_p50  studio_p65  studio_p80  one_bedroom_p30  one_bedroom_p50  one_bedroom_p65  one_bedroom_p80  two_bedroom_p30  two_bedroom_p50  two_bedroom_p65  two_bedroom_p80  three_plus_bedroom_p30  three_plus_bedroom_p50  three_plus_bedroom_p65  three_plus_bedroom_p80
British Columbia  VANCOUVER          West End/Stanley Park      1444.0      1800.0      1950.0      2000.0           1603.0           1880.0           2000.0           2200.0           2511.0           2800.0           2917.0           3300.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER                    English Bay      1455.0      1643.0      1850.0      2345.0           1700.0           1994.0           2050.0           2200.0           2451.0           3000.0           3200.0           3350.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER                       Downtown      1625.0      1798.0      1921.0      2130.0           1882.0           2150.0           2300.0           2500.0           2800.0           3200.0           3525.0           3940.0                  4740.0                  4995.0                  5650.0                  5888.0
British Columbia  VANCOUVER            South Granville/Oak      1350.0      1500.0      1650.0      1875.0           1650.0           1841.0           1955.0           2214.0           2087.0           2500.0           2711.0           3070.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER           Kitsilano/Point Grey      1400.0      1699.0      1795.0      1950.0           1725.0           1890.0           2000.0           2200.0           2395.0           2608.0           2845.0           3250.0                  3533.0                  4000.0                  4050.0                  4100.0
British Columbia  VANCOUVER            Westside/Kerrisdale         NaN      1950.0      2500.0      2500.0           1500.0           1854.0           2150.0           2325.0           2600.0           2950.0           3100.0           3550.0                     NaN                  5100.0                  5100.0                  5100.0
British Columbia  VANCOUVER                        Marpole      1200.0      1495.0      1500.0      1700.0           1250.0           1500.0           1595.0           1790.0           1600.0           1863.0           2000.0           2410.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER Mount Pleasant/Renfrew Heights      1651.0      1900.0      2037.0      2150.0           1475.0           1700.0           1800.0           2034.0           2000.0           2400.0           2781.0           3300.0                  3090.0                  3600.0                  3700.0                  3950.0
British Columbia  VANCOUVER                  East Hastings      1550.0      1725.0      1850.0      1960.0           1500.0           1650.0           1850.0           2050.0           1946.0           2400.0           2600.0           2987.0                     NaN                  3350.0                  3545.0                  4331.0
British Columbia  VANCOUVER            Southeast Vancouver         NaN      1300.0      1626.0      1801.0           1400.0           1750.0           1930.0           2100.0           2260.0           2500.0           2630.0           2900.0                  2594.0                  3075.0                  3100.0                  3707.0
British Columbia  VANCOUVER     University Endowment Lands      1775.0      1800.0      1800.0      2053.0           2295.0           2400.0           2440.0           2900.0           3316.0           3350.0           3500.0           3550.0                  3271.0                  3271.0                  4050.0                  4200.0
British Columbia  VANCOUVER         Central Park/Metrotown      1311.0         NaN      2081.0      2088.0           1424.0           1650.0           2000.0           2393.0           1774.0           2125.0              NaN              NaN                  2400.0                     NaN                     NaN                     NaN
British Columbia  VANCOUVER              Southeast Burnaby         NaN         NaN         NaN      2000.0           1495.0           1550.0           1650.0           1800.0           1675.0           1850.0           1853.0           2100.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER                  North Burnaby      1038.0      1038.0      1275.0      1673.0           1525.0           1700.0           1850.0           2050.0           1763.0           1941.0           2275.0           2610.0                  1800.0                     NaN                     NaN                  2951.0
British Columbia  VANCOUVER                New Westminster      1375.0      1600.0      1800.0      1809.0           1468.0           1628.0           1795.0           2050.0           1850.0           2120.0           2400.0           2640.0                  2450.0                  2795.0                  3150.0                  3370.0
British Columbia  VANCOUVER             North Vancouver CY      1500.0      1818.0      1873.0      1945.0           1690.0           1933.0           2111.0           2300.0           1961.0           2200.0           2673.0           3191.0                  3650.0                  3900.0                  4150.0                  4600.0
British Columbia  VANCOUVER             North Vancouver DM         NaN         NaN         NaN         NaN           2350.0           2500.0           2575.0           2575.0           2300.0           2800.0           3100.0           3369.0                  1713.0                  2380.0                  3125.0                  3800.0
British Columbia  VANCOUVER                 West Vancouver      1683.0      1864.0      2199.0      2300.0           2004.0           2095.0           2125.0           2613.0           2718.0           3530.0           3731.0           3817.0                  4106.0                     NaN                     NaN                     NaN
British Columbia  VANCOUVER                       Richmond      1270.0      1570.0      1740.0      1940.0           1406.0           1540.0           1815.0           2050.0           1745.0           1931.0           2050.0           2267.0                  2240.0                  2344.0                  2501.0                     NaN
British Columbia  VANCOUVER                          Delta         NaN      1409.0      1500.0      1560.0              NaN           1775.0           1925.0           1925.0           1500.0           1800.0           2150.0           2150.0                     NaN                     NaN                     NaN                     NaN
British Columbia  VANCOUVER                         Surrey      1626.0      1663.0      1700.0      1759.0           1380.0           1700.0           1843.0           1950.0           1425.0           1825.0           2250.0           2400.0                  1441.0                  1700.0                  1957.0                  2700.0
British Columbia  VANCOUVER                     White Rock      1167.0      1350.0      1350.0      1400.0           1300.0           1390.0           1500.0           1725.0           1630.0           1850.0           1900.0           2000.0                  2204.0                  2975.0                  3095.0                  3200.0
British Columbia  VANCOUVER    Langley City and Langley DM      1250.0      1250.0      1250.0      1518.0           1611.0           1800.0           1925.0           2049.0           2039.0           2300.0           2420.0           2522.0                  2800.0                  2900.0                  3055.0                  3200.0
British Columbia  VANCOUVER                     Tri-Cities         NaN      1740.0      2000.0      2070.0           1400.0           1750.0           2045.0           2187.0           1720.0           2100.0           2500.0           2900.0                     NaN                  3320.0                  3550.0                  3600.0
British Columbia  VANCOUVER       Maple Ridge/Pitt Meadows       807.0       979.0      1000.0      1335.0           1275.0           1500.0           1650.0           1775.0           1345.0           1800.0           1950.0           2200.0                  2300.0                  2300.0                  2300.0                  2400.0

6. **Vancouver Open Data**: non-market housing data, subdivision category areas, and local area and zone boundaries.

NOT INCLUDED



