# Task 5: Month-by-Month Occupancy by City, Including the New August Data

Sample output from running `tasks/task_5_monthly_occupancy_with_august.py` on the project data.

## Sample output

```text
May-July rows: 9194
August rows: 7
August file agrees with the hotel list.
Combined rows: 9201
Average occupancy % by city and month
month      2022-05  2022-06  2022-07  2022-08
city                                         
Bangalore    57.09    55.85    56.04    74.65
Delhi        61.81    61.46    61.25      NaN
Hyderabad    59.01    57.69    57.64      NaN
Mumbai       58.44    57.79    57.50    77.24
Data coverage per month
         days  hotels  rows
month                      
2022-05    31      25  3098
2022-06    30      25  2999
2022-07    31      25  3097
2022-08     1       7     7
June average occupancy % by city
city
Delhi        61.46
Mumbai       57.79
Hyderabad    57.69
Bangalore    55.85
Name: occ_pct, dtype: float64
```

![task5 city occupancy by month](../outputs/task5_city_occupancy_by_month.png)

