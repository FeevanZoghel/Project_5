
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
max_battery = 300
min_battery_value = (300 / 85 * 100) * 0.1
charging_limit = 0.9 * max_battery
fast_charge_per_min = 450 / 60
slow_charge_per_min = 60 / 60
min_charging_time = 15
idle_energy_per_hour = 5  # Voorlopige aanname: 5 kWh per idle-activiteit

def get_travel_time(start, end):
    if start == end:
        return 0
    data = dm[(dm['start'] == start) & (dm['end'] == end)]
    if data.empty:
        return None
    value = data['max_travel_time'].iloc[0]
    return float(value) if pd.notna(value) else None

def get_energy(start, end, activity, line=None):
    if start == end and activity == 'material trip':
        return 0
    data = bp[(bp['start location'] == start) & (bp['end location'] == end) & (bp['activity'] == activity)]
    if line is not None:
        data = data[data['line'] == line]
    if data.empty:
        return None
    value = data['energy consumption'].mean()
    return float(value) if pd.notna(value) else None

def add_activity(bus, start_location, end_location, start_time, end_time, activity, energy, travel_time=0, line=None):
    previous = ibp[ibp['bus'] == bus]
    total_travel_time = 0 if previous.empty else previous.iloc[-1]['total travel time']
    total_travel_time = float(total_travel_time) + travel_time
    battery[bus] -= energy
    if battery[bus] < -1e-6 or battery[bus] > max_battery + 1e-6:
        raise ValueError(f'Ongeldige batterijstand voor {bus}: {battery[bus]}')
    ibp.loc[len(ibp)] = [start_location, end_location, start_time, end_time, activity, line, energy, battery[bus], total_travel_time, bus]

def calculate_charging(battery_start, minutes):
    if minutes < min_charging_time:
        return 0
    if battery_start < charging_limit:
        fast_minutes = min(minutes, (charging_limit - battery_start) / fast_charge_per_min)
        charged = fast_minutes * fast_charge_per_min
        remaining_minutes = minutes - fast_minutes
        charged += remaining_minutes * slow_charge_per_min
    else:
        charged = minutes * slow_charge_per_min
    return min(max_battery - battery_start, charged)

def garage_to_trip(bus, trip, start_time, benodigde_energy):
    material_time = get_travel_time('ehvgar', trip['start'])
    material_energy = get_energy('ehvgar', trip['start'], 'material trip')
    if material_time is None or material_energy is None:
        raise ValueError(f'Geen materieelrit vanuit garage naar {trip["start"]}')
    if battery[bus] < material_energy + benodigde_energy:
        raise ValueError(f'{bus} heeft onvoldoende energie')
    if material_time > 0:
        material_start_time = start_time - pd.Timedelta(minutes=material_time)
        add_activity(bus, 'ehvgar', trip['start'], material_start_time, start_time, 'material trip', material_energy, material_time)

for i in range(len(tt)):
    trip = tt.iloc[i]
    start_time = trip['sort_time']
    travel_time = get_travel_time(trip['start'], trip['end'])
    energy_consumption = get_energy(trip['start'], trip['end'], 'service trip', trip['line'])
    if travel_time is None or energy_consumption is None:
        raise ValueError(f'Ontbrekende ritgegevens bij timetable-rij {i}')
    end_time = start_time + pd.Timedelta(minutes=travel_time)
    return_energy = get_energy(trip['end'], 'ehvgar', 'material trip')
    if return_energy is None:
        raise ValueError(f'Ontbrekende terugritenergie bij timetable-rij {i}')
    benodigde_energy = energy_consumption + return_energy + min_battery_value
    beschikbare_bussen = []
    kandidaten = {}

    for bus in bussen:
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1]
        last_end_time = last_activity['end time']
        last_end_location = last_activity['end location']
        available_time = (start_time - last_end_time).total_seconds() / 60
        if available_time < 0:
            continue
        material_time = get_travel_time(last_end_location, trip['start'])
        material_energy = get_energy(last_end_location, trip['start'], 'material trip')
        if material_time is None or material_energy is None:
            continue
        idle_time = available_time - material_time
        if idle_time < 0:
            continue
        idle_consumption = (idle_time / 60) * idle_energy_per_hour
        total_energy_needed = material_energy + idle_consumption + benodigde_energy
        charging_minutes = 0
        charged_energy = 0

        # Laden bij de garage, ook als daarna een materieelrit nodig is
        if last_end_location == 'ehvgar':
            charging_minutes = idle_time
            charged_energy = calculate_charging(battery[bus], charging_minutes)

        if battery[bus] >= total_energy_needed:
            charged_energy = 0
            charging_minutes = 0
        elif battery[bus] + charged_energy < total_energy_needed:
            continue
        else:
            idle_time = 0
            idle_consumption = 0

        beschikbare_bussen.append(bus)
        kandidaten[bus] = {
            'last_end_time': last_end_time,
            'last_end_location': last_end_location,
            'material_time': material_time,
            'material_energy': material_energy,
            'idle_time': idle_time,
            'idle_energy': idle_consumption,
            'charging_minutes': charging_minutes,
            'charged_energy': charged_energy
        }

    if not beschikbare_bussen:
        gekozen_bus = f'bus{len(bussen) + 1}'
        battery[gekozen_bus] = max_battery
        garage_to_trip(gekozen_bus, trip, start_time, benodigde_energy)
        bussen.append(gekozen_bus)
    else:
        gekozen_bus = min(beschikbare_bussen, key=lambda bus: kandidaten[bus]['last_end_time'])
        kandidaat = kandidaten[gekozen_bus]
        current_time = kandidaat['last_end_time']
        current_location = kandidaat['last_end_location']

        if kandidaat['charged_energy'] > 0:
            charging_end = current_time + pd.Timedelta(minutes=kandidaat['charging_minutes'])
            add_activity(gekozen_bus, 'ehvgar', 'ehvgar', current_time, charging_end, 'charging', -kandidaat['charged_energy'])
            current_time = charging_end

        if kandidaat['idle_time'] > 0:
            idle_end = current_time + pd.Timedelta(minutes=kandidaat['idle_time'])
            add_activity(gekozen_bus, current_location, current_location, current_time, idle_end, 'idle', kandidaat['idle_energy'])
            current_time = idle_end

        if kandidaat['material_time'] > 0:
            material_end = current_time + pd.Timedelta(minutes=kandidaat['material_time'])
            add_activity(gekozen_bus, current_location, trip['start'], current_time, material_end, 'material trip', kandidaat['material_energy'], kandidaat['material_time'])

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
output_filename = 'Improved_plan_Feasibility_and_KPI_results.xlsx'
output = export_results_to_excel(feasibility_results, kpi_results, filename=output_filename)

t_end = time.perf_counter()
print(f'Computation time: {t_end - t_start:.2f} seconds.')
