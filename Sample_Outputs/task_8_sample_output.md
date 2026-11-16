# Task 8: Hotel KPI Scorecard (Occupancy, ADR and RevPAR)

Sample output from running `tasks/task_8_hotel_kpi_scorecard.py` on the project data.

## Sample output

```text
Bookings: 134573 | Availability rows: 9194
Hotel-days where 'successful_bookings' equals ALL bookings made: 99.9%
Hotel-days where it equals only guests who stayed:              5.7%
Bookings left out because their day/hotel row was removed in Task 1: 115
Table rows: 9194
Whole chain
             booked_occ_pct  net_occ_pct       adr  revpar
all_hotels                                                
Whole chain           57.85        40.59  14927.71  7346.6
KPIs by city
           hotels  rooms_available  booked_occ_pct  net_occ_pct       adr   revpar
city                                                                              
Mumbai          8          75053.0           57.88        40.65  18083.97  8906.52
Delhi           5          39979.0           60.50        42.37  14316.55  7356.51
Bangalore       6          57319.0           55.76        38.99  15453.02  7325.19
Hyderabad       6          60058.0           58.06        40.84  10944.73  5411.06
KPIs by hotel category
          booked_occ_pct  net_occ_pct       adr   revpar
category                                                
Business           58.19        40.79  15157.52  7496.84
Luxury             57.65        40.46  14788.05  7256.04

KPIs by room class
              booked_occ_pct  net_occ_pct       adr    revpar
room_class                                                   
Presidential           59.21        41.79  27469.22  13881.40
Premium                57.57        40.39  17766.17   8704.69
Elite                  57.61        40.33  13315.66   6519.95
Standard               57.84        40.58   9457.98   4657.44
KPIs by hotel (ranked by RevPAR)
                                              booked_occ_pct  net_occ_pct       adr    revpar
property_id property_name city      category                                                 
16559       Atliq Exotica Mumbai    Luxury             65.91        46.38  18962.66  10637.79
17563       Atliq Palace  Mumbai    Business           66.23        46.80  18836.90  10609.44
17559       Atliq Exotica Mumbai    Luxury             66.09        46.80  17865.62  10115.38
17561       Atliq Blu     Mumbai    Luxury             66.28        46.38  16717.67   9452.47
19562       Atliq Bay     Bangalore Luxury             65.81        46.37  16612.55   9334.64
19560       Atliq City    Bangalore Business           65.57        45.33  16262.36   8992.81
16561       Atliq Blu     Delhi     Luxury             65.78        45.96  15462.81   8626.18
16563       Atliq Palace  Delhi     Business           66.32        46.39  14686.48   8284.76
17558       Atliq Grands  Mumbai    Luxury             53.64        37.54  17544.84   7968.23
17560       Atliq City    Mumbai    Business           53.14        36.96  17217.13   7776.27
16558       Atliq Grands  Delhi     Luxury             65.78        46.05  13543.52   7523.11
17564       Atliq Seasons Mumbai    Business           44.61        31.49  19512.01   7405.51
19559       Atliq Exotica Bangalore Luxury             53.85        38.16  15004.13   6875.49
17562       Atliq Bay     Mumbai    Luxury             44.84        31.22  17876.28   6798.61
19561       Atliq Blu     Bangalore Luxury             53.29        37.19  14920.35   6778.46
19563       Atliq Palace  Bangalore Business           53.49        37.15  14957.09   6778.26
16560       Atliq City    Delhi     Business           53.70        38.19  13687.06   6285.15
16562       Atliq Bay     Delhi     Luxury             53.44        37.02  13844.94   6256.92
18562       Atliq Bay     Hyderabad Luxury             65.85        46.21  11150.98   6218.73
18560       Atliq City    Hyderabad Business           66.19        46.99  10743.92   6083.69
18561       Atliq Blu     Hyderabad Luxury             65.59        46.22  10156.73   5692.49
19558       Atliq Grands  Bangalore Luxury             44.37        31.11  14603.70   5534.93
18558       Atliq Grands  Hyderabad Luxury             53.45        37.31  12156.80   5523.95
18563       Atliq Palace  Hyderabad Business           52.96        36.87  11176.86   5012.01
18559       Atliq Exotica Hyderabad Luxury             44.62        31.51  10654.23   4061.07
           hotels  booked_occ_pct       adr   revpar    revenue  revenue_per_hotel  revenue_rank  revpar_rank
city                                                                                                         
Mumbai          8           57.88  18083.97  8906.52  668460961        83557620.12             1            1
Delhi           5           60.50  14316.55  7356.51  294106008        58821201.60             4            2
Bangalore       6           55.76  15453.02  7325.19  419872335        69978722.50             2            3
Hyderabad       6           58.06  10944.73  5411.06  324977530        54162921.67             3            4
```

![task8 kpis by city](../outputs/task8_kpis_by_city.png)

![task8 occupancy gap and revpar heatmap](../outputs/task8_occupancy_gap_and_revpar_heatmap.png)

```text
Saved: cleaned_data/hotel_kpis.csv | hotels: 25
```

