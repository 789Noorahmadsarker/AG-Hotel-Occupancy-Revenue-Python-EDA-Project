# Task 2: Clean the Individual Booking Records

Sample output from running `tasks/task_2_clean_booking_transactions.py` on the project data.

## Sample output

```text
Rows, columns: (134590, 12)
         booking_id  property_id booking_date check_in_date checkout_date  no_guests room_category booking_platform  ratings_given booking_status  revenue_generated  revenue_realized
0  May012216558RT11        16558     27-04-22      1/5/2022      2/5/2022       -3.0           RT1    direct online            1.0    Checked Out              10010             10010
1  May012216558RT12        16558     30-04-22      1/5/2022      2/5/2022        2.0           RT1           others            NaN      Cancelled               9100              3640
2  May012216558RT13        16558     28-04-22      1/5/2022      4/5/2022        2.0           RT1          logtrip            5.0    Checked Out            9100000              9100
3  May012216558RT14        16558     28-04-22      1/5/2022      2/5/2022       -2.0           RT1           others            NaN      Cancelled               9100              3640
4  May012216558RT15        16558     27-04-22      1/5/2022      2/5/2022        4.0           RT1    direct online            5.0    Checked Out              10920             10920
Bookings with invalid guest counts: 9
               booking_id  property_id  no_guests booking_status
0        May012216558RT11        16558       -3.0    Checked Out
3        May012216558RT14        16558       -2.0      Cancelled
17924    May122218559RT44        18559      -10.0        No Show
18020    May122218561RT22        18561      -12.0      Cancelled
18119   May122218562RT311        18562       -6.0    Checked Out
18121   May122218562RT313        18562       -4.0      Cancelled
56715    Jun082218562RT12        18562      -17.0    Checked Out
119765  Jul202219560RT220        19560       -1.0    Checked Out
134586   Jul312217564RT47        17564       -4.0    Checked Out
Rows after removing invalid guest counts: 134578
Average revenue per booking: 15,378
Acceptable range: -263,742 to 294,499
Outlier bookings: 5
               booking_id booking_status  revenue_generated  revenue_realized
2        May012216558RT13    Checked Out            9100000              9100
111      May012216559RT32    Checked Out           28560000             28560
315      May012216562RT22    Checked Out           12600000             12600
562     May012217559RT118      Cancelled            2000000              4420
129176   Jul282216562RT26    Checked Out           10000000             12600
Rows after removing revenue outliers: 134573
Largest remaining revenue value: 45,220
All three date columns converted to dates.
Check-in dates run from 2022-05-01 to 2022-07-31
                      count      mean      std      min      25%      50%      75%      max
property_id        134573.0  18061.19  1093.04  16558.0  17558.0  17564.0  18563.0  19563.0
no_guests          134573.0      2.04     1.03      1.0      1.0      2.0      2.0      6.0
ratings_given       56676.0      3.62     1.23      1.0      3.0      4.0      5.0      5.0
revenue_generated  134573.0  14915.96  6452.68   6500.0   9900.0  13500.0  18000.0  45220.0
revenue_realized   134573.0  12695.98  6927.79   2600.0   7600.0  11700.0  15300.0  45220.0
Saved: cleaned_data/clean_bookings.csv | rows: 134573
```

