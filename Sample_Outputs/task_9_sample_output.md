# Task 9: Booking Behaviour: How Far Ahead Do Guests Book and How Long Do They Stay?

Sample output from running `tasks/task_9_booking_behaviour_lead_time_and_stay.py` on the project data.

## Sample output

```text
Bookings: 134573
Lead time (days): average 3.71 | median 3.0 | longest 24
Average length of stay (ALOS): 2.37 nights
lead_days
0     23446
1     19589
2     22697
3     20782
4     16114
5     11903
6      8394
7      3672
20     2278
21     3522
24     2176

Bookings made 8 to 19 days ahead: 0
lead_group
Same day      17.4
1-3 days      46.9
4-7 days      29.8
20-24 days     5.9 

stay_group
1 night       47.6
2 nights      20.2
3-4 nights    13.0
5-6 nights    19.2 

party_group
Solo          32.9
Couple        44.7
3-4 guests    20.2
5-6 guests     2.1 
By hotel category
          bookings  avg_lead_days  avg_nights  avg_booking_value  share_pct
category                                                                   
Business     50928           2.17        1.77           15161.73      37.84
Luxury       83645           4.64        2.74           14766.32      62.16

By party size
             bookings  avg_lead_days  avg_nights  avg_booking_value  share_pct
party_group                                                                   
Solo            44311           2.84        2.03           14382.94      32.93
Couple          60215           4.22        2.58           14261.46      44.75
3-4 guests      27213           4.01        2.50           15949.51      20.22
5-6 guests       2834           3.46        2.28           27231.95       2.11

By city
           bookings  avg_lead_days  avg_nights  avg_booking_value  share_pct
city                                                                        
Bangalore     32015           3.76        2.38           15455.71      23.79
Delhi         24223           3.42        2.27           14298.42      18.00
Hyderabad     34883           3.84        2.44           10931.78      25.92
Mumbai        43452           3.73        2.38           18061.01      32.29
Length of stay mix (%) within each lead-time group
stay_group  1 night  2 nights  3-4 nights  5-6 nights
lead_group                                           
Same day       56.4      20.2        14.3         9.1
1-3 days       47.6      20.1        13.1        19.2
4-7 days       43.0      20.1        12.3        24.5
20-24 days     45.1      20.4        12.9        21.6
```

![task9 lead time and stay](../outputs/task9_lead_time_and_stay.png)

