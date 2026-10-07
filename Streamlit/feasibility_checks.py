import pandas as pd
import streamlit as st

ASSUMED_SOH = 85
INITIAL_BATTERY_CAPACITY = 300
MINIMUM_SOC = 0.10
QUICK_CHARGING_SPEED = 450 / 60
SLOW_CHARGING_SPEED = 60 / 60
MINIMUM_CHARGING_TIME = 15

def validate_minimum_soc(df):
    """Checks whether every bus remains above the minimum allowed SOC."""
    minimum_battery_value = (INITIAL_BATTERY_CAPACITY / ASSUMED_SOH * 100) * MINIMUM_SOC
    planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for energy_consumption in bus_data['energy consumption']:
            battery -= energy_consumption
            if battery < minimum_battery_value:
                return False
    return True

def show_minimum_soc_errors(df):
    """Displays buses that drop below the minimum allowed SOC."""
    minimum_battery_value = (INITIAL_BATTERY_CAPACITY / ASSUMED_SOH * 100) * MINIMUM_SOC
    planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        minimum_battery = INITIAL_BATTERY_CAPACITY
        for energy_consumption in bus_data['energy consumption']:
            battery -= energy_consumption
            if battery < minimum_battery:
                minimum_battery = battery
        if minimum_battery < minimum_battery_value:
            st.error(f'Bus {bus}: battery drops to {minimum_battery:.2f} kWh. Minimum allowed is {minimum_battery_value:.2f} kWh.')

def validate_soh(assumed_soh):
    """Checks whether the assumed State of Health is between 85% and 95%."""
    return 85 <= assumed_soh <= 95

def validate_location_continuity(df):
    """Checks whether consecutive activities for the same bus have matching locations."""
    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data) - 1):
            if bus_data['end location'][i] != bus_data['start location'][i + 1]:
                return False
    return True

def show_location_continuity_errors(df):
    """Displays every location mismatch between consecutive activities."""
    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data) - 1):
            end_location = bus_data['end location'][i]
            next_start_location = bus_data['start location'][i + 1]
            if end_location != next_start_location:
                st.error(f'Bus {bus}: location mismatch. Trip ends at "{end_location}", but the next trip starts at "{next_start_location}".')

def validate_required_trips(df, timetable):
    """Checks whether all required service trips are included in the schedule."""
    number_of_required_trips = len(timetable)
    service_trips_in_planning = df[df['activity'] == 'service trip']
    num_planned_trips = len(service_trips_in_planning)
    return number_of_required_trips == num_planned_trips

def show_required_trip_errors(df, timetable):
    """Displays whether required service trips are missing or overplanned."""
    number_of_required_trips = len(timetable)
    service_trips_in_planning = df[df['activity'] == 'service trip']
    num_planned_trips = len(service_trips_in_planning)
    if number_of_required_trips != num_planned_trips:
        difference = number_of_required_trips - num_planned_trips
        if difference > 0:
            st.error(f'{difference} required service trip(s) are missing. Required: {number_of_required_trips}, planned: {num_planned_trips}.')
        else:
            st.error(f'There are {abs(difference)} too many service trips. Required: {number_of_required_trips}, planned: {num_planned_trips}.')

def validate_minimum_charging_time(df):
    """Checks whether every charging activity lasts at least 15 minutes."""
    start_dt = pd.to_datetime('2026-01-01 ' + df['start time'].astype(str))
    end_dt = pd.to_datetime('2026-01-01 ' + df['end time'].astype(str))
    charging_duration_min = (end_dt - start_dt).dt.total_seconds() / 60
    for idx, row in df.iterrows():
        if row['activity'] == 'charging' and charging_duration_min.loc[idx] < MINIMUM_CHARGING_TIME:
            return False
    return True

def show_minimum_charging_time_errors(df):
    """Displays charging activities shorter than the minimum charging time."""
    start_dt = pd.to_datetime('2026-01-01 ' + df['start time'].astype(str))
    end_dt = pd.to_datetime('2026-01-01 ' + df['end time'].astype(str))
    charging_duration_min = (end_dt - start_dt).dt.total_seconds() / 60
    for idx, row in df.iterrows():
        if row['activity'] == 'charging':
            duration = charging_duration_min.loc[idx]
            if duration < MINIMUM_CHARGING_TIME:
                st.error(f'Bus {row["bus"]}: charging time is only {duration:.1f} minutes ({row["start time"]} - {row["end time"]}). Minimum required is {MINIMUM_CHARGING_TIME} minutes.')

def validate_charging_speed(df):
    """Checks whether each charging activity uses the correct charging speed."""
    planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for idx, row in bus_data.iterrows():
            if row['activity'] == 'charging':
                charging_duration = (pd.to_timedelta(str(row['end time'])) - pd.to_timedelta(str(row['start time']))).total_seconds() / 60
                charging_speed = abs(row['energy consumption']) / charging_duration
                if battery < 270:
                    if charging_speed != QUICK_CHARGING_SPEED:
                        return False
                else:
                    if charging_speed != SLOW_CHARGING_SPEED:
                        return False
            battery -= row['energy consumption']
    return True

def show_charging_speed_errors(df):
    """Displays every charging activity with an incorrect charging speed."""
    planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for idx, row in bus_data.iterrows():
            if row['activity'] == 'charging':
                charging_duration = (pd.to_timedelta(str(row['end time'])) - pd.to_timedelta(str(row['start time']))).total_seconds() / 60
                charging_speed = abs(row['energy consumption']) / charging_duration
                if battery < 270:
                    required_speed = QUICK_CHARGING_SPEED
                else:
                    required_speed = SLOW_CHARGING_SPEED
                if charging_speed != required_speed:
                    st.error(f'Bus {bus}: incorrect charging speed. Calculated speed: {charging_speed:.2f} kWh/min. Required speed: {required_speed:.2f} kWh/min. Battery before charging: {battery:.2f} kWh.')
            battery -= row['energy consumption']

def validate_no_overlapping_trips(df):
    """Checks whether activities assigned to the same bus overlap."""
    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data)):
            for j in range(i + 1, len(bus_data)):
                if bus_data['end time'][i] > bus_data['start time'][j]:
                    return False
    return True

def show_overlapping_trip_errors(df):
    """Displays overlapping activities."""
    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data)):
            for j in range(i + 1, len(bus_data)):
                if bus_data['end time'][i] > bus_data['start time'][j]:
                    st.error(f'Bus {bus}: overlapping trips. Trip {i + 1} ends at {bus_data["end time"][i]}, while trip {j + 1} starts at {bus_data["start time"][j]}.')

def status_check(text, is_valid):
    """Displays a green check mark when a validation passes and a red cross when it fails."""
    if is_valid:
        color = "#4CAF50"
        symbol = "✓"
    else:
        color = "#EA3323"
        symbol = "✕"
    html = f"""
    <div style="background:#F3F4F6;border-radius:10px;padding:10px 14px;margin:10px 0;display:flex;align-items:center;gap:14px;width:100%;box-sizing:border-box;">
        <div style="width:32px;height:32px;min-width:32px;border-radius:6px;background:{color};color:white;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:bold;line-height:1;">{symbol}</div>
        <span style="font-size:16px;color:#222222;font-weight:500;">{text}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)