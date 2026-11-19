# Task 10: Cancellations, No-Shows and Revenue Leakage

Sample output from running `tasks/task_10_cancellations_and_revenue_leakage.py` on the project data.

## Sample output

```text
Bookings: 134573
booking_status
Checked Out    70.1
Cancelled      24.8
No Show         5.0
Value of all bookings when made : 2,007,285,455
Money actually kept             : 1,708,536,599
Revenue leakage                 : 298,748,856  (14.9% of booked value)
Cancellation fees recovered     : 199,165,904
Average money lost per cancelled booking: 8,940
Chain-wide cancellation rate: 24.83%
Segments tested: 56 | flagged as unusual: 0

Five segments furthest from the chain average:
          dimension  segment  bookings  cancel_rate_pct  z_score
Hotel (property ID)    19560      5978            26.38     2.77
     Length of stay  1 night     64059            25.19     2.08
     Length of stay 2 nights     27140            24.31    -2.00
        Arrival day  Weekend     50215            24.48    -1.80
Hotel (property ID)    18563      4728            25.95     1.78
                       min    max  gap_points
dimension                                    
Hotel (property ID)  24.00  26.38        2.38
Party size           24.47  25.83        1.36
Length of stay       24.31  25.19        0.88
Booking channel      24.31  25.00        0.69
Arrival day          24.48  25.04        0.55
Room class           24.44  24.96        0.52
City                 24.63  25.06        0.44
Hotel category       24.71  25.03        0.32
Lead time            24.70  24.96        0.26
 cancellation_rate_cut_points  bookings_saved  extra_revenue  uplift_pct_of_realized
                            1            1346       12031222                    0.70
                            2            2691       24062443                    1.41
                            3            4037       36093665                    2.11
                            5            6729       60156108                    3.52
```

![task10 cancellation overview](../outputs/task10_cancellation_overview.png)

![task10 cancellation by segment](../outputs/task10_cancellation_by_segment.png)

