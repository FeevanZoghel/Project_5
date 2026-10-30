import pandas as pd

def calculate_energy_consumption_kpis(bp):
    """Calculates the total energy consumption of all buses."""
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
    """Calculates distance and material trip KPIs."""
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

    def convert_single_time(value):

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

        # Probeer eerst een gewone tijd of tijdsduur
        result = pd.to_timedelta(value, errors="coerce")

        if pd.notna(result):
            return result

        # Probeer een volledige datum met tijd
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
    """Calculates total and average waiting time, including overnight idle periods."""
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
    """Calculates total charging time, including charging across midnight."""

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
    df = bp.copy()
    df['start_td'] = convert_time_to_timedelta(df['start time'])
    df['end_td'] = convert_time_to_timedelta(df['end time'])

    df = df.dropna(subset=['start_td', 'end_td', 'activity'])
    df['duration'] = (df['end_td'] - df['start_td']).dt.total_seconds() / 60
    df.loc[df['duration'] < 0, 'duration'] += 1440

    return df.groupby('activity')['duration'].mean().to_dict()
