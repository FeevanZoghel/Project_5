
import pandas as pd
import time

t_start = time.perf_counter()
bp = pd.read_excel('Bus_Plan_Cleaned.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')
columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'total battery bus', 'total travel time', 'bus']
ibp = pd.DataFrame(columns=columns)
tt['sort_time'] = pd.to_datetime(tt['departure_time'], format='%H:%M')
tt.loc[tt['sort_time'].dt.time < pd.Timestamp('05:07').time(), 'sort_time'] += pd.Timedelta(days=1)
tt = tt.sort_values('sort_time').reset_index(drop=True)

bussen = []
battery = {}
soh = 0.85
max_battery = 300 * soh
min_battery_value = max_battery * 0.10
charging_limit = max_battery * 0.90
fast_charge_per_min = 450 / 60
slow_charge_per_min = 60 / 60
min_charging_time = 15
idle_energy_per_hour = 5
first_departure = tt['sort_time'].iloc[0].normalize() + pd.Timedelta(hours=5)
eps = 1e-7

def get_travel_time(start, end, line=None):
    if start == end:
        return 0.0
    data = dm[(dm['start'] == start) & (dm['end'] == end)]
    if line is not None:
        data = data[data['line'] == line]
    if data.empty or pd.isna(data['max_travel_time'].iloc[0]):
        return None
    return float(data['max_travel_time'].iloc[0])

def get_energy(start, end, activity, line=None):
    if start == end and activity == 'material trip':
        return 0.0
    data = bp[(bp['start location'] == start) & (bp['end location'] == end) & (bp['activity'] == activity)]
    if line is not None:
        data = data[data['line'] == line]
    if data.empty:
        return None
    value = data['energy consumption'].mean()
    return float(value) if pd.notna(value) else None

def add_activity(bus, start_location, end_location, start_time, end_time, activity, energy, travel_time=0, line=None):
    previous = ibp[ibp['bus'] == bus]
    if not previous.empty:
        last = previous.iloc[-1]
        if start_time < last['end time'] - pd.Timedelta(microseconds=1):
            raise ValueError(f'Overlappende activiteiten voor {bus}')
        if last['end location'] != start_location:
            raise ValueError(f'Locatie sluit niet aan voor {bus}: {last["end location"]} -> {start_location}')
    if end_time < start_time:
        raise ValueError(f'Negatieve activiteitsduur voor {bus}')
    previous_travel = 0 if previous.empty else float(previous.iloc[-1]['total travel time'])
    new_battery = battery[bus] - energy
    if new_battery < min_battery_value - eps or new_battery > max_battery + eps:
        raise ValueError(f'Ongeldige batterijstand voor {bus}: {new_battery:.2f} kWh')
    battery[bus] = min(max_battery, new_battery)
    ibp.loc[len(ibp)] = [start_location, end_location, start_time, end_time, activity, line, energy, battery[bus], previous_travel + travel_time, bus]

def calculate_charging(battery_start, minutes):
    if minutes < min_charging_time or battery_start >= max_battery:
        return 0.0
    if battery_start < charging_limit:
        fast_minutes = min(minutes, (charging_limit - battery_start) / fast_charge_per_min)
        charged = fast_minutes * fast_charge_per_min
        charged += (minutes - fast_minutes) * slow_charge_per_min
    else:
        charged = minutes * slow_charge_per_min
    return min(max_battery - battery_start, charged)

def candidate(bus, trip, start_time, service_energy, return_energy, via_garage=False):
    last = ibp[ibp['bus'] == bus].iloc[-1]
    location = last['end location']
    ready_time = last['end time']
    available_minutes = (start_time - ready_time).total_seconds() / 60
    if available_minutes < 0:
        return None
    steps = []
    current_battery = battery[bus]
    current_time = ready_time
    if via_garage:
        to_garage_time = get_travel_time(location, 'ehvgar')
        to_garage_energy = get_energy(location, 'ehvgar', 'material trip')
        if to_garage_time is None or to_garage_energy is None:
            return None
        if current_battery - to_garage_energy < min_battery_value - eps:
            return None
        if to_garage_time > 0:
            steps.append((location, 'ehvgar', current_time, current_time + pd.Timedelta(minutes=to_garage_time), 'material trip', to_garage_energy, to_garage_time))
            current_time += pd.Timedelta(minutes=to_garage_time)
            current_battery -= to_garage_energy
        location = 'ehvgar'
    to_start_time = get_travel_time(location, trip['start'])
    to_start_energy = get_energy(location, trip['start'], 'material trip')
    if to_start_time is None or to_start_energy is None:
        return None
    wait_minutes = (start_time - current_time).total_seconds() / 60 - to_start_time
    if wait_minutes < -eps:
        return None
    wait_minutes = max(0.0, wait_minutes)
    required_after_wait = to_start_energy + service_energy + return_energy + min_battery_value
    if location == 'ehvgar' and current_battery < required_after_wait + (wait_minutes / 60) * idle_energy_per_hour - eps:
        charged = calculate_charging(current_battery, wait_minutes)
        if charged > 0 and wait_minutes >= min_charging_time and current_battery + charged >= required_after_wait - eps:
            charging_end = current_time + pd.Timedelta(minutes=wait_minutes)
            steps.append(('ehvgar', 'ehvgar', current_time, charging_end, 'charging', -charged, 0))
            current_time = charging_end
            current_battery += charged
            wait_minutes = 0
    if wait_minutes > eps:
        idle_energy = (wait_minutes / 60) * idle_energy_per_hour
        if current_battery - idle_energy < min_battery_value - eps:
            return None
        idle_end = current_time + pd.Timedelta(minutes=wait_minutes)
        steps.append((location, location, current_time, idle_end, 'idle', idle_energy, 0))
        current_time = idle_end
        current_battery -= idle_energy
    if current_battery < required_after_wait - eps:
        return None
    if to_start_time > 0:
        material_end = current_time + pd.Timedelta(minutes=to_start_time)
        steps.append((location, trip['start'], current_time, material_end, 'material trip', to_start_energy, to_start_time))
        current_time = material_end
        current_battery -= to_start_energy
    if abs((start_time - current_time).total_seconds()) > 0.01:
        return None
    return {'bus': bus, 'last_end_time': ready_time, 'steps': steps, 'via_garage': via_garage}

for i, trip in tt.iterrows():
    start_time = trip['sort_time']
    travel_time = get_travel_time(trip['start'], trip['end'], trip['line'])
    energy_consumption = get_energy(trip['start'], trip['end'], 'service trip', trip['line'])
    return_energy = get_energy(trip['end'], 'ehvgar', 'material trip')
    if travel_time is None or energy_consumption is None or return_energy is None:
        raise ValueError(f'Ontbrekende ritgegevens bij timetable-rij {i}')
    end_time = start_time + pd.Timedelta(minutes=travel_time)
    opties = []
    for bus in bussen:
        direct = candidate(bus, trip, start_time, energy_consumption, return_energy)
        via_garage = candidate(bus, trip, start_time, energy_consumption, return_energy, via_garage=True)
        if direct is not None:
            opties.append(direct)
        if via_garage is not None:
            opties.append(via_garage)
    if opties:
        # Greedy Rule: bus met vroegste eindtijd; bij gelijkstand liever geen omweg via garage
        keuze = min(opties, key=lambda c: (c['last_end_time'], c['via_garage'], len(c['steps'])))
        gekozen_bus = keuze['bus']
        for start_loc, end_loc, t0, t1, activity, energy, duration in keuze['steps']:
            add_activity(gekozen_bus, start_loc, end_loc, t0, t1, activity, energy, duration)
    else:
        gekozen_bus = f'bus{len(bussen) + 1}'
        material_time = get_travel_time('ehvgar', trip['start'])
        material_energy = get_energy('ehvgar', trip['start'], 'material trip')
        if material_time is None or material_energy is None:
            raise ValueError(f'Geen materieelrit van garage naar {trip["start"]}')
        material_start = start_time - pd.Timedelta(minutes=material_time)
        if material_start < first_departure:
            raise ValueError(f'Nieuwe bus voor rit {i} moet vóór 05:00 vertrekken: {material_start}')
        if max_battery < material_energy + energy_consumption + return_energy + min_battery_value - eps:
            raise ValueError(f'Nieuwe bus heeft onvoldoende energie voor rit {i}')
        battery[gekozen_bus] = max_battery
        if material_time > 0:
            add_activity(gekozen_bus, 'ehvgar', trip['start'], material_start, start_time, 'material trip', material_energy, material_time)
        bussen.append(gekozen_bus)
    add_activity(gekozen_bus, trip['start'], trip['end'], start_time, end_time, 'service trip', energy_consumption, travel_time, trip['line'])

print(f'Aantal benodigde bussen: {len(bussen)}')
print(ibp)
excel_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']
df_improved_plan = ibp[excel_columns].copy()
df_improved_plan['start time'] = pd.to_datetime(df_improved_plan['start time']).dt.strftime('%H:%M:%S')
df_improved_plan['end time'] = pd.to_datetime(df_improved_plan['end time']).dt.strftime('%H:%M:%S')
df_improved_plan.to_excel('Improved_Bus_Planning_version_B.xlsx', index=False)

from Code_for_bus_cleaned import run_all_feasibility_checks, run_all_kpi_calculations, export_results_to_excel

feasibility_results = run_all_feasibility_checks(ibp, tt)
kpi_results = run_all_kpi_calculations(ibp, dm, tt)
output = export_results_to_excel(feasibility_results, kpi_results, filename='Improved_plan_Feasibility_and_KPI_results.xlsx')
t_end = time.perf_counter()
print(f'Computation time: {t_end - t_start:.2f} seconds.')
