-- TODO:
--   * Add primary keys
--   * Add indices
--   * Add non-null fields

CREATE TABLE agency (
    agency_id text,
    agency_name text,
    agency_url text,
    agency_timezone text,
    agency_lang text,
    agency_phone text
);

CREATE TABLE calendar_dates (
    service_id text,
    date date,
    exception_type integer,
);

CREATE TABLE calendar (
    service_id text,
    monday integer,
    tuesday integer,
    wednesday integer,
    thursday integer,
    friday integer,
    saturday integer,
    sunday integer,
    start_date date,
    end_date date
);

CREATE TABLE feed_info (
    feed_publisher_name text,
    feed_publisher_url text,
    feed_lang text,
    feed_start_date date,
    feed_end_date date,
    feed_version text
);

CREATE TABLE frequencies (
    trip_id text,
    start_time text,
    end_time text,
    headway_secs integer,
    exact_times integer
);

CREATE TABLE routes (
    route_id text,
    agency_id text,
    route_short_name text,
    route_long_name text,
    route_desc text,
    route_type integer
);

CREATE TABLE stop_times (
    trip_id text,
    arrival_time text,
    departure_time text,
    stop_id text,
    stop_sequence integer,
    pickup_type integer,
    drop_off_type integer
);

CREATE TABLE stops (
    stop_id text,
    stop_name text,
    stop_lat double precision,
    stop_lon double precision,
    location_type integer,
    parent_station text,
    platform_code text,
    original_stop_id text,
    didok text
);

CREATE TABLE transfers (
    from_start_id text,
    to_start_id text,
    from_route_id text,
    to_route_id text,
    from_trip_id text,
    to_trip_id text,
    transfer_type integer,
    min_transfer_time integer,
    service_id text
);

CREATE TABLE trips (
    route_id text,
    service_id text,
    trip_id text,
    trip_headsign text,
    trip_short_name text,
    direction_id integer,
    block_id text,
    original_trip_id text,
    hints text
);
