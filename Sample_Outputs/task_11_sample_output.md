# Task 11: Booking Channel Mix and Dependency

Sample output from running `tasks/task_11_booking_channel_mix_and_dependency.py` on the project data.

## Sample output

```text
Bookings: 134573 | Channels: 7
By channel
                  bookings  booking_share_pct  money_share_pct  money_per_booking  cancel_rate_pct  avg_rating  avg_lead_days
booking_platform                                                                                                             
others               55061              40.92            40.93           12700.58            24.87        3.62           3.70
makeyourtrip         26896              19.99            19.95           12671.55            24.99        3.62           3.72
logtrip              14753              10.96            10.97           12708.87            24.31        3.62           3.64
direct online        13374               9.94             9.89           12632.62            25.00        3.61           3.73
tripster              9630               7.16             7.20           12779.52            24.99        3.62           3.74
journey               8106               6.02             6.00           12648.82            24.78        3.63           3.75
direct offline        6753               5.02             5.06           12790.60            24.49        3.62           3.75

By channel group
                     bookings  booking_share_pct  money_share_pct  money_per_booking  cancel_rate_pct  avg_rating  avg_lead_days
channel_group                                                                                                                   
Travel agency (OTA)     59385              44.13            44.13           12695.23            24.79        3.62           3.71
Unclassified            55061              40.92            40.93           12700.58            24.87        3.62           3.70
Direct                  20127              14.96            14.94           12685.62            24.83        3.62           3.73
                hhi  effective_channels
Whole chain  2090.9                 4.8
Bangalore    2058.1                 4.9
Delhi        2096.2                 4.8
Hyderabad    2111.0                 4.7
Mumbai       2100.5                 4.8
Business     2096.9                 4.8
Luxury       2087.3                 4.8
Weeks analysed: 13  (02 May to 25 Jul)

Change in share per week (percentage points):
Direct                 0.030
Travel agency (OTA)   -0.010
Unclassified          -0.021
                   measure  best_minus_worst  p_value real_difference
Cancellation rate (points)             0.689    0.864     No (chance)
    Money kept per booking           157.983    0.550     No (chance)
     Guest rating (1 to 5)             0.014    0.997     No (chance)
          Lead time (days)             0.115    0.500     No (chance)
```

![task11 channel mix](../outputs/task11_channel_mix.png)

![task11 channel mix trend](../outputs/task11_channel_mix_trend.png)

