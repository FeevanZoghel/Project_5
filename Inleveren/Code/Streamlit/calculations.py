
import pandas as pd


def calculate_energy_consumption_kpis(bp):
    """
    Calculates the total energy consumption of all buses.

    The bus planning is sorted by bus number and start time.
    For each bus, all positive energy consumption values are
    added together. Negative values are excluded because
    these represent battery charging.

    Args:
        bp (pd.DataFrame): Bus planning containing the columns
            'bus', 'start time' and 'energy consumption'.

    Returns:
        float: Total energy consumption of all buses in kWh.
    """
    planning_sor = bp.sort_values(['bus', 'start time'])
    total_consumption = 0

    for bus, bus_data in planning_sor.groupby('bus'):
        total_consumption_bus = 0

        for energy in bus_data['energy consumption']:
            if energy > 0:
                total_consumption_bus += energy

        total_consumption += total_consumption_bus

    return total_consumption


def calculate_distances_and_kpis(bp, dm, tt):
    """
    Calculates distance, material trip and bus usage KPIs.

    The function uses the distance matrix to determine the
    distances of all required service trips in the timetable
    and all material trips in the bus planning.

    It calculates the total driving distance, the number of
    deployed buses and the number of material trips.

    Args:
        bp (pd.DataFrame): Bus planning containing bus numbers,
            activities, start locations and end locations.

        dm (pd.DataFrame): Distance matrix containing bus lines,
            start locations, end locations and distances in meters.

        tt (pd.DataFrame): Timetable containing the required
            service trips with their lines and locations.

    Returns:
        tuple:
            total_distance_m (float): Total driving distance
                in meters.
            total_distance_km (float): Total driving distance
                in kilometers.
            deployed_buses_count (int): Number of unique buses
                used in the planning.
            t_material_total (int): Total number of material trips.
            d_material_total (float): Total distance of material
                trips in meters.
            d_material_total_km (float): Total distance of material
                trips in kilometers.
    """
    lines = dm['line'].dropna().unique()
    material_dm = dm[dm['line'].isna()]
    material_trips = bp[bp['activity'] == 'material trip']
    deployed_buses_count = bp['bus'].nunique()

    distances = {}
    material_distances = {}

    d_service_total_m = 0
    d_material_total = 0
    t_material_total = 0

    for i in lines:
        line = dm[dm['line'] == i]

        for _, trip in line.iterrows():
            start = trip['start']
            end = trip['end']
            distance = trip['distance_m']
            distances[(i, start, end)] = distance

    for _, trip in tt.iterrows():
        line = trip['line']
        start = trip['start']
        end = trip['end']
        distance = distances[(line, start, end)]
        d_service_total_m += distance

    for _, trip in material_dm.iterrows():
        start = trip['start']
        end = trip['end']
        distance = trip['distance_m']
        material_distances[(start, end)] = distance

    for _, trip in material_trips.iterrows():
        start = trip['start location']
        end = trip['end location']
        distance = material_distances[(start, end)]
        d_material_total += distance
        t_material_total += 1

    total_distance_m = d_service_total_m + d_material_total
    total_distance_km = total_distance_m / 1000
    d_material_total_km = d_material_total / 1000

    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total, d_material_total, d_material_total_km


def convert_time_to_timedelta(time_values):
    """
    Converts a Series of time values into pandas Timedelta objects.

    The function applies a conversion to each value in the
    Series. It supports different time formats, including
    Timedelta, Timestamp, time strings and datetime strings.

    Args:
        time_values (pd.Series): Series containing time values
            that need to be converted.

    Returns:
        pd.Series: Series containing Timedelta objects.
            Invalid or missing values are returned as NaT.
    """

    def convert_single_time(value):
        """
        Converts an individual time value into a pandas Timedelta.

        The function checks the input type and attempts to
        convert it into a Timedelta. For Timestamp and datetime
        values, only the time component is used.

        Args:
            value: Individual time value to be converted.
                Can be a Timedelta, Timestamp or string.

        Returns:
            pd.Timedelta or pd.NaT: Converted time value,
                or NaT if the conversion fails.
        """

        if pd.isna(value):
            return pd.NaT

        if isinstance(value, pd.Timedelta):
            return value

        if isinstance(value, pd.Timestamp):
            return pd.Timedelta(
                hours=value.hour,
                minutes=value.minute,
                seconds=value.second,
                microseconds=value.microsecond
            )

        value = str(value).strip()

        # First try converting a time string or duration
        result = pd.to_timedelta(value, errors="coerce")

        if pd.notna(result):
            return result

        # Try converting a complete datetime string
        result = pd.to_datetime(value, errors="coerce")

        if pd.notna(result):
            return pd.Timedelta(
                hours=result.hour,
                minutes=result.minute,
                seconds=result.second,
                microseconds=result.microsecond
            )

        return pd.NaT

    return time_values.apply(convert_single_time)


def calculate_waiting_time_kpis(bp, deployed_buses_count):
    """
    Calculates total and average waiting time for all buses.

    The function selects all idle activities from the bus
    planning and calculates their duration using the start
    and end times.

    If an idle period crosses midnight, one day is added
    to correct the negative time difference.

    The total waiting time is calculated in minutes and hours.
    The average waiting time is calculated per deployed bus.

    Args:
        bp (pd.DataFrame): Bus planning containing activities,
            start times and end times.

        deployed_buses_count (int): Number of unique buses
            used in the planning.

    Returns:
        tuple:
            tot_waiting_time_min (float): Total waiting time
                of all buses in minutes.
            tot_waiting_time_hours (float): Total waiting time
                of all buses in hours.
            avg_waiting_time_per_bus (float): Average waiting
                time per deployed bus in minutes.
    """
    idle = bp[bp['activity'] == 'idle'].copy()

    start_time = convert_time_to_timedelta(idle['start time'])
    end_time = convert_time_to_timedelta(idle['end time'])

    waiting_time = end_time - start_time
    waiting_time = waiting_time.where(
        waiting_time >= pd.Timedelta(0),
        waiting_time + pd.Timedelta(days=1)
    )

    tot_waiting_time_min = waiting_time.dt.total_seconds().sum() / 60
    tot_waiting_time_hours = tot_waiting_time_min / 60

    avg_waiting_time_per_bus = (
        tot_waiting_time_min / deployed_buses_count
        if deployed_buses_count > 0 else 0
    )

    return tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus


def calculate_charging_time_kpis(bp):
    """
    Calculates the total charging time of all buses.

    The function selects all charging activities from the
    bus planning and calculates the duration of each charging
    session using the start and end times.

    If a charging session crosses midnight, one day is added
    to correct the negative time difference.

    Args:
        bp (pd.DataFrame): Bus planning containing activities,
            start times and end times.

    Returns:
        tuple:
            total_charging_time_min (float): Total charging
                time of all buses in minutes.
            total_charging_time_hours (float): Total charging
                time of all buses in hours.
    """
    charging = bp[bp['activity'] == 'charging'].copy()

    start_time = convert_time_to_timedelta(charging['start time'])
    end_time = convert_time_to_timedelta(charging['end time'])

    charging_time = end_time - start_time

    charging_time = charging_time.where(
        charging_time >= pd.Timedelta(0),
        charging_time + pd.Timedelta(days=1)
    )

    total_charging_time_min = charging_time.dt.total_seconds().sum() / 60
    total_charging_time_hours = total_charging_time_min / 60

    return total_charging_time_min, total_charging_time_hours


def calculate_average_activity_times(bp):
    """
    Calculates the average duration of each activity type.

    The function converts start and end times into Timedelta
    objects and calculates the duration of each activity
    in minutes.

    Activities with missing time values or activity types
    are excluded from the calculations.

    If an activity crosses midnight, 1440 minutes are added
    to correct the negative duration.

    The average duration is calculated separately for each
    activity type, such as service trip, material trip,
    charging and idle.

    Args:
        bp (pd.DataFrame): Bus planning containing the columns
            'activity', 'start time' and 'end time'.

    Returns:
        dict: Dictionary containing the average duration
            in minutes for each activity type.
            The keys represent the activity types and
            the values represent their average durations.
    """
    df = bp.copy()

    df['start_td'] = convert_time_to_timedelta(df['start time'])
    df['end_td'] = convert_time_to_timedelta(df['end time'])

    df = df.dropna(subset=['start_td', 'end_td', 'activity'])

    df['duration'] = (
        df['end_td'] - df['start_td']
    ).dt.total_seconds() / 60

    df.loc[df['duration'] < 0, 'duration'] += 1440

    return df.groupby('activity')['duration'].mean().to_dict()
