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
    required_dm = ['line', 'start', 'end', 'distance_m']
    required_tt = ['line', 'start', 'end']
    for column in required_dm:
        if column not in dm.columns:
            raise ValueError(f'Distance Matrix is missing column "{column}". Available columns: {dm.columns.tolist()}')
    for column in required_tt:
        if column not in tt.columns:
            raise ValueError(f'Timetable is missing column "{column}". Available columns: {tt.columns.tolist()}')
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
        line_data = dm[dm['line'] == i]
        for _, trip in line_data.iterrows():
            start = trip['start']
            end = trip['end']
            distance = trip['distance_m']
            distances[(i, start, end)] = distance
    for _, trip in tt.iterrows():
        key = (trip['line'], trip['start'], trip['end'])
        if key not in distances:
            raise ValueError(f'No service trip distance found for {key}.')
        d_service_total_m += distances[key]
    for _, trip in material_dm.iterrows():
        material_distances[(trip['start'], trip['end'])] = trip['distance_m']
    for _, trip in material_trips.iterrows():
        key = (trip['start location'], trip['end location'])
        if key not in material_distances:
            raise ValueError(f'No material trip distance found for {key}.')
        d_material_total += material_distances[key]
        t_material_total += 1
    total_distance_m = d_service_total_m + d_material_total
    total_distance_km = total_distance_m / 1000
    d_material_total_km = d_material_total / 1000
    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total, d_material_total, d_material_total_km

def calculate_waiting_time_kpis(bp, deployed_buses_count):
    """Calculates total and average waiting time."""
    start_time = pd.to_timedelta(bp['start time'].astype(str))
    end_time = pd.to_timedelta(bp['end time'].astype(str))
    idle = bp[bp['activity'] == 'idle']
    waiting_time = end_time[idle.index] - start_time[idle.index]
    tot_waiting_time_min = waiting_time.dt.total_seconds().sum() / 60
    tot_waiting_time_hours = tot_waiting_time_min / 60
    avg_waiting_time_per_bus = tot_waiting_time_min / deployed_buses_count
    return tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus

def calculate_charging_time_kpis(bp):
    """Calculates total charging time."""
    start_time = pd.to_timedelta(bp['start time'].astype(str))
    end_time = pd.to_timedelta(bp['end time'].astype(str))
    charging = bp[bp['activity'] == 'charging']
    charging_time = end_time[charging.index] - start_time[charging.index]
    total_charging_time_min = charging_time.dt.total_seconds().sum() / 60
    total_charging_time_hours = total_charging_time_min / 60
    return total_charging_time_min, total_charging_time_hours