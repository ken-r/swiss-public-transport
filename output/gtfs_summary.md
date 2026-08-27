# GTFS Dataset Summary

## agency

- Load time: 0.06s
- Number of rows: 473
- Number of columns: 6

### Column names

- `agency_id`
- `agency_name`
- `agency_url`
- `agency_timezone`
- `agency_lang`
- `agency_phone`

### First five rows

```text
agency_id                     agency_name      agency_url agency_timezone agency_lang  agency_phone
      823         Basler Verkehrsbetriebe https://sweg.de   Europe/Berlin          DE           NaN
       11 Schweizerische Bundesbahnen SBB  https://sbb.ch   Europe/Berlin          DE 0848 44 66 88
       65                          THURBO  https://sbb.ch   Europe/Berlin          DE           NaN
       33                    BLS AG (bls)  https://bls.ch   Europe/Berlin          DE           NaN
       72                  Rhätische Bahn  https://rhb.ch   Europe/Berlin          DE           NaN
```

## calendar_dates

- Load time: 6.37s
- Number of rows: 10501182
- Number of columns: 3

### Column names

- `service_id`
- `date`
- `exception_type`

### First five rows

```text
service_id     date  exception_type
  TA+00000 20251219               2
  TA+00000 20251226               2
  TA+00000 20260102               2
  TA+00000 20260109               2
  TA+00000 20260116               2
```

## calendar

- Load time: 0.20s
- Number of rows: 78999
- Number of columns: 10

### Column names

- `service_id`
- `monday`
- `tuesday`
- `wednesday`
- `thursday`
- `friday`
- `saturday`
- `sunday`
- `start_date`
- `end_date`

### First five rows

```text
service_id  monday  tuesday  wednesday  thursday  friday  saturday  sunday  start_date  end_date
        TA       1        1          1         1       1         1       1    20251214  20261212
  TA+00000       0        0          0         0       1         0       0    20251214  20261212
  TA+00030       0        0          0         0       0         1       1    20251214  20261212
  TA+00100       0        0          0         0       1         0       1    20251214  20261212
  TA+00110       1        1          1         1       1         0       0    20251214  20261212
```

## feed_info

- Load time: 0.06s
- Number of rows: 1
- Number of columns: 6

### Column names

- `feed_publisher_name`
- `feed_publisher_url`
- `feed_lang`
- `feed_start_date`
- `feed_end_date`
- `feed_version`

### First five rows

```text
feed_publisher_name feed_publisher_url feed_lang  feed_start_date  feed_end_date  feed_version
                SBB     https://sbb.ch        DE         20251214       20261212      20260815
```

## frequencies

- Load time: 0.04s
- Number of rows: 1885
- Number of columns: 5

### Column names

- `trip_id`
- `start_time`
- `end_time`
- `headway_secs`
- `exact_times`

### First five rows

```text
                   trip_id start_time end_time  headway_secs  exact_times
 .ojp-92-EV1-F.1.TA.89.j26   06:59:00 23:59:00          3600            0
 .ojp-92-EV1-F.1.TA.95.j26   07:15:00 23:15:00          3600            0
 .ojp-92-EV1-F.1.TA.98.j26   06:30:00 22:30:00          3600            0
 .ojp-92-EV1-F.1.TA.99.j26   06:45:00 22:45:00          3600            0
.ojp-92-EV1-F.1.TA.237.j26   06:49:00 22:49:00          3600            0
```

## routes

- Load time: 0.07s
- Number of rows: 5125
- Number of columns: 6

### Column names

- `route_id`
- `agency_id`
- `route_short_name`
- `route_long_name`
- `route_desc`
- `route_type`

### First five rows

```text
     route_id agency_id route_short_name  route_long_name route_desc  route_type
91-10-A-j26-1        78              S10              NaN          S         109
91-10-B-j26-1        11              S10              NaN          S         109
91-10-C-j26-1        65              S10              NaN          S         109
91-10-D-j26-1        11               10              NaN        EXT         117
91-10-E-j26-1      3849               10              NaN          T         900
```

## stop_times

- Load time: 82.86s
- Number of rows: 29921301
- Number of columns: 7

### Column names

- `trip_id`
- `arrival_time`
- `departure_time`
- `stop_id`
- `stop_sequence`
- `pickup_type`
- `drop_off_type`

### First five rows

```text
              trip_id arrival_time departure_time               stop_id  stop_sequence  pickup_type  drop_off_type
 .ojp-91-1.1.TA.1.j26     06:42:00       06:42:00  ch:1:sloid:88776:1:3              1            0              0
 .ojp-91-1.1.TA.1.j26     06:43:00       06:43:00  ch:1:sloid:88778:1:1              2            0              0
 .ojp-91-1.1.TA.1.j26     06:45:00       06:45:00  ch:1:sloid:88071:1:1              3            0              0
 .ojp-91-1.1.TA.1.j26     06:46:00       06:46:00 ch:1:sloid:78143:2:36              4            0              0
.ojp-91-1.1.TA.10.j26     25:30:00       25:30:00 ch:1:sloid:78143:2:36              1            0              0
```

## stops

- Load time: 0.73s
- Number of rows: 103815
- Number of columns: 9

### Column names

- `stop_id`
- `stop_name`
- `stop_lat`
- `stop_lon`
- `location_type`
- `parent_station`
- `platform_code`
- `original_stop_id`
- `didok`

### First five rows

```text
stop_id         stop_name  stop_lat  stop_lon  location_type parent_station platform_code original_stop_id   didok
7104307 Figueras Vilafant 42.264779  2.943025            NaN  Parent7104307           NaN          7104307 7104307
7171801   Barcelona Sants 41.378914  2.140371            NaN  Parent7171801           NaN          7171801 7171801
7179300            Gerona 41.979519  2.816488            NaN  Parent7179300           NaN          7179300 7179300
8002140      Augsburg Hbf 48.365441 10.885569            NaN  Parent8002140           NaN          8002140 8002140
8002301     Lindau-Reutin 47.552384  9.703296            NaN  Parent8002301           NaN          8002301 8002301
```

## transfers

- Load time: 3.25s
- Number of rows: 738132
- Number of columns: 9

### Column names

- `from_stop_id`
- `to_stop_id`
- `from_route_id`
- `to_route_id`
- `from_trip_id`
- `to_trip_id`
- `transfer_type`
- `min_transfer_time`
- `service_id`

### First five rows

```text
from_stop_id to_stop_id from_route_id to_route_id from_trip_id to_trip_id  transfer_type  min_transfer_time service_id
     7104307    7104307           NaN         NaN          NaN        NaN              2              300.0        NaN
     7171801    7171801           NaN         NaN          NaN        NaN              2              600.0        NaN
     7179300    7179300           NaN         NaN          NaN        NaN              2              300.0        NaN
     8002140    8002140           NaN         NaN          NaN        NaN              2              300.0        NaN
     8002301    8002301           NaN         NaN          NaN        NaN              2              240.0        NaN
```

## trips

- Load time: 7.38s
- Number of rows: 1884326
- Number of columns: 9

### Column names

- `route_id`
- `service_id`
- `trip_id`
- `trip_headsign`
- `trip_short_name`
- `direction_id`
- `block_id`
- `original_trip_id`
- `hints`

### First five rows

```text
     route_id service_id                   trip_id trip_headsign  trip_short_name  direction_id  block_id            original_trip_id hints
91-10-A-j26-1      TA+rJ   .ojp-91-10-A.1.TA.1.j26     Zürich HB            12976             0       NaN ch:1:sjyid:100058:12976-005  2 NF
91-10-A-j26-1   TA+oos00  .ojp-91-10-A.1.TA.10.j26     Zürich HB            12816             0       NaN ch:1:sjyid:100058:12816-002  2 NF
91-10-A-j26-1   TA+oos00 .ojp-91-10-A.1.TA.100.j26     Zürich HB            12926             0       NaN ch:1:sjyid:100058:12926-002  2 NF
91-10-A-j26-1   TA+oos00 .ojp-91-10-A.1.TA.101.j26     Zürich HB            12928             0       NaN ch:1:sjyid:100058:12928-001  2 NF
91-10-A-j26-1   TA+oos00 .ojp-91-10-A.1.TA.102.j26     Zürich HB            12930             0       NaN ch:1:sjyid:100058:12930-001  2 NF
```
