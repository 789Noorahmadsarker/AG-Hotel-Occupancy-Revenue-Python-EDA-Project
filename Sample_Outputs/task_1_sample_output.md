# Task 1: Prepare the Daily Room-Availability Table

Sample output from running `tasks/task_1_prepare_aggregated_bookings.py` on the project data.

## Sample output

```text
Rows, columns: (9200, 5)
   property_id check_in_date room_category  successful_bookings  capacity
0        16559      1-May-22           RT1                   25      30.0
1        19562      1-May-22           RT1                   28      30.0
2        19563      1-May-22           RT1                   23      30.0
3        17558      1-May-22           RT1                   30      19.0
4        16558      1-May-22           RT1                   18      19.0
Number of hotels: 25
[16558, 16559, 16560, 16561, 16562, 16563, 17558, 17559, 17560, 17561, 17562, 17563, 17564, 18558, 18559, 18560, 18561, 18562, 18563, 19558, 19559, 19560, 19561, 19562, 19563]
property_id
16559    7338
18562    7333
16563    7211
18560    6638
18561    6458
17563    6337
17559    6142
19560    6079
17560    6013
19562    5812
19561    5736
19563    5413
18559    5256
17561    5183
17558    5053
16562    4820
18563    4737
19559    4729
16560    4693
18558    4475
16561    4418
19558    4400
17564    3982
17562    3424
16558    3153
Name: successful_bookings, dtype: int64
Highest capacity: 50.0
 property_id room_category
       17558           RT2
property_id            0
check_in_date          0
room_category          0
successful_bookings    0
capacity               2
dtype: int64
    property_id check_in_date room_category  successful_bookings  capacity
8         17561      1-May-22           RT1                   22       NaN
14        17562      1-May-22           RT1                   12       NaN
Missing values left: 0
Rows with bookings greater than capacity: 6
      property_id check_in_date room_category  successful_bookings  capacity
3           17558      1-May-22           RT1                   30      19.0
12          16563      1-May-22           RT1                  100      41.0
4136        19558     11-Jun-22           RT2                   50      39.0
6209        19560      2-Jul-22           RT1                  123      26.0
8522        19559     25-Jul-22           RT1                   35      24.0
9194        18563     31-Jul-22           RT4                   20      18.0
Rows before: 9200 | Rows after: 9194
Occupancy range: 21.05 to 100.0
   property_id check_in_date room_category  successful_bookings  capacity  occ_pct
0        16559    2022-05-01           RT1                   25      30.0    83.33
1        19562    2022-05-01           RT1                   28      30.0    93.33
2        19563    2022-05-01           RT1                   23      30.0    76.67
4        16558    2022-05-01           RT1                   18      19.0    94.74
5        17560    2022-05-01           RT1                   28      40.0    70.00
Saved: cleaned_data/clean_aggregated_bookings.csv | rows: 9194
```

