# Task 3: Where Are Our Rooms Filling Up? Occupancy by Room Class and City

Sample output from running `tasks/task_3_occupancy_by_room_class_and_city.py` on the project data.

## Sample output

```text
   property_id check_in_date room_category  successful_bookings  capacity  occ_pct room_class  property_name  category       city
0        16559    2022-05-01           RT1                   25      30.0    83.33   Standard  Atliq Exotica    Luxury     Mumbai
1        19562    2022-05-01           RT1                   28      30.0    93.33   Standard      Atliq Bay    Luxury  Bangalore
2        19563    2022-05-01           RT1                   23      30.0    76.67   Standard   Atliq Palace  Business  Bangalore
3        16558    2022-05-01           RT1                   18      19.0    94.74   Standard   Atliq Grands    Luxury      Delhi
4        17560    2022-05-01           RT1                   28      40.0    70.00   Standard     Atliq City  Business     Mumbai
Average occupancy % by room class
room_class
Presidential    59.28
Premium         58.03
Elite           58.01
Standard        57.89
Name: occ_pct, dtype: float64
Average occupancy % by city
city
Delhi        61.51
Hyderabad    58.12
Mumbai       57.91
Bangalore    56.33
Name: occ_pct, dtype: float64
```

![task3 occupancy room class city](../outputs/task3_occupancy_room_class_city.png)

