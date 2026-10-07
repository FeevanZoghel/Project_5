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
    sorted_planning = df.sort_values(['bus', 'start time'])
    for _, bus_data in sorted_planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for energy_consumption in bus_data['energy consumption']:
            battery -= energy_consumption
            if battery < minimum_battery_value:
                return False
    return True

def show_minimum_soc_errors(df):
    """Displays buses that drop below the minimum allowed SOC."""
    minimum_battery_value = (INITIAL_BATTERY_CAPACITY / ASSUMED_SOH * 100) * MINIMUM_SOC
    sorted_planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in sorted_planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        minimum_battery = INITIAL_BATTERY_CAPACITY
        for energy_consumption in bus_data['energy consumption']:
            battery -= energy_consumption
            minimum_battery = min(minimum_battery, battery)
        if minimum_battery < minimum_battery_value:
            st.error(f'Bus {bus}: SOC drops to {minimum_battery:.2f} kWh')

def validate_soh(assumed_soh):
    """Checks whether the assumed State of Health is between 85% and 95%."""
    return 85 <= assumed_soh <= 95

def validate_location_continuity(df):
    """Checks whether consecutive activities for the same bus have matching locations."""
    sorted_planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for _, bus_data in sorted_planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for index in range(len(bus_data) - 1):
            current_end_location = bus_data.loc[index, 'end location']
            next_start_location = bus_data.loc[index + 1, 'start location']
            if current_end_location != next_start_location:
                return False
    return True

def show_location_continuity_errors(df):
    """Displays every location mismatch between consecutive activities."""
    sorted_planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in sorted_planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for index in range(len(bus_data) - 1):
            current_end_location = bus_data.loc[index, 'end location']
            next_start_location = bus_data.loc[index + 1, 'start location']
            if current_end_location != next_start_location:
                st.error(f'Bus {bus}: location mismatch "{current_end_location}" → "{next_start_location}".')

def validate_required_trips(df, timetable):
    """Checks whether the number of service trips equals the number of required trips."""
    required_trip_count = len(timetable)
    planned_service_trips = df[df['activity'] == 'service trip']
    planned_trip_count = len(planned_service_trips)
    return required_trip_count == planned_trip_count

def show_required_trip_errors(df, timetable):
    """Displays whether required service trips are missing or overplanned."""
    required_trip_count = len(timetable)
    planned_trip_count = len(df[df['activity'] == 'service trip'])
    difference = required_trip_count - planned_trip_count
    if difference > 0:
        st.error(f'{difference} required trip(s) missing ({planned_trip_count}/{required_trip_count} planned).')
    elif difference < 0:
        st.error(f'{abs(difference)} extra trip(s) planned ({planned_trip_count}/{required_trip_count} required).')

def validate_minimum_charging_time(df):
    """Checks whether every charging activity lasts at least 15 minutes."""
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))
    charging_duration_minutes = (end_times - start_times).dt.total_seconds() / 60
    for index, row in df.iterrows():
        if row['activity'] == 'charging' and charging_duration_minutes.loc[index] < MINIMUM_CHARGING_TIME:
            return False
    return True

def show_minimum_charging_time_errors(df):
    """Displays charging activities shorter than the minimum charging time."""
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))
    charging_duration_minutes = (end_times - start_times).dt.total_seconds() / 60
    for index, row in df.iterrows():
        if row['activity'] == 'charging':
            duration = charging_duration_minutes.loc[index]
            if duration < MINIMUM_CHARGING_TIME:
                st.error(f'Bus {row["bus"]}: charging time {duration:.1f} min ({MINIMUM_CHARGING_TIME} min required).')

def validate_charging_speed(df):
    """Checks whether each charging activity uses the correct charging speed."""
    sorted_planning = df.sort_values(['bus', 'start time'])
    for _, bus_data in sorted_planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for _, row in bus_data.iterrows():
            if row['activity'] == 'charging':
                charging_duration = (pd.to_timedelta(str(row['end time'])) - pd.to_timedelta(str(row['start time']))).total_seconds() / 60
                charging_speed = abs(row['energy consumption']) / charging_duration
                if battery < 270:
                    required_speed = QUICK_CHARGING_SPEED
                else:
                    required_speed = SLOW_CHARGING_SPEED
                if abs(charging_speed - required_speed) > 1e-9:
                    return False
            battery -= row['energy consumption']
    return True

def show_charging_speed_errors(df):
    """Displays every charging activity with an incorrect charging speed."""
    sorted_planning = df.sort_values(['bus', 'start time'])
    for bus, bus_data in sorted_planning.groupby('bus'):
        battery = INITIAL_BATTERY_CAPACITY
        for _, row in bus_data.iterrows():
            if row['activity'] == 'charging':
                charging_duration = (pd.to_timedelta(str(row['end time'])) - pd.to_timedelta(str(row['start time']))).total_seconds() / 60
                charging_speed = abs(row['energy consumption']) / charging_duration
                if battery < 270:
                    required_speed = QUICK_CHARGING_SPEED
                else:
                    required_speed = SLOW_CHARGING_SPEED
                if abs(charging_speed - required_speed) > 1e-9:
                    st.error(f'Bus {bus}: charging speed {charging_speed:.2f} kWh/min ({required_speed:.2f} required).')
            battery -= row['energy consumption']

def validate_no_overlapping_trips(df):
    """Checks whether activities assigned to the same bus overlap."""
    sorted_planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for _, bus_data in sorted_planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for index in range(len(bus_data) - 1):
            current_end_time = pd.to_timedelta(str(bus_data.loc[index, 'end time']))
            next_start_time = pd.to_timedelta(str(bus_data.loc[index + 1, 'start time']))
            if current_end_time > next_start_time:
                return False
    return True

def show_overlapping_trip_errors(df):
    """Displays every pair of consecutive activities that overlap."""
    sorted_planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in sorted_planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for index in range(len(bus_data) - 1):
            current_end_time = pd.to_timedelta(str(bus_data.loc[index, 'end time']))
            next_start_time = pd.to_timedelta(str(bus_data.loc[index + 1, 'start time']))
            if current_end_time > next_start_time:
                st.error(f'Bus {bus}: activities overlap ({bus_data.loc[index, "end time"]} → {bus_data.loc[index + 1, "start time"]}).')

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