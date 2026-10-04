import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

ASSUMED_SOH = 85
INITIAL_BATTERY_CAPACITY = 300
MINIMUM_SOC = 0.10
QUICK_CHARGING_SPEED = 450 / 60
SLOW_CHARGING_SPEED = 60 / 60
MINIMUM_CHARGING_TIME = 15


def validate_columns(df):
    """
    Checks whether the DataFrame contains exactly the required columns
    in the correct order.

    Returns True if all columns are correct, otherwise False.
    """
    return df.columns.tolist() == REQUIRED_COLUMNS


def show_column_errors(df):
    """Displays detailed errors for incorrect or missing columns."""
    actual_columns = df.columns.tolist()

    if len(actual_columns) != len(REQUIRED_COLUMNS):
        st.error(f"The number of columns is incorrect. Expected {len(REQUIRED_COLUMNS)}, but found {len(actual_columns)}.")

    for index, expected_column in enumerate(REQUIRED_COLUMNS):
        if index >= len(actual_columns):
            st.error(f'Missing column: "{expected_column}".')
            continue

        actual_column = actual_columns[index]

        if actual_column != expected_column:
            st.error(f'Column {index + 1} is "{actual_column}". It should be "{expected_column}".')

    if len(actual_columns) > len(REQUIRED_COLUMNS):
        extra_columns = actual_columns[len(REQUIRED_COLUMNS):]

        for column in extra_columns:
            st.error(f'Unexpected column: "{column}".')


def validate_time_format(df):
    """
    Checks whether all start and end times use the HH:MM:SS format.

    Returns True if all times are valid, otherwise False.
    """
    time_columns = ['start time', 'end time']

    for column in time_columns:
        for value in df[column]:
            time_string = str(value)

            try:
                parts = time_string.split(':')

                if len(parts) != 3:
                    return False

                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])

                if not 0 <= hours <= 23:
                    return False
                if not 0 <= minutes <= 59:
                    return False
                if not 0 <= seconds <= 59:
                    return False

            except (ValueError, TypeError):
                return False

    return True


def show_time_format_errors(df):
    """Displays the row and column of every invalid time value."""
    time_columns = ['start time', 'end time']

    for column in time_columns:
        for row_index, value in enumerate(df[column]):
            time_string = str(value)

            try:
                parts = time_string.split(':')

                if len(parts) != 3:
                    st.error(f'Row {row_index + 2}, column "{column}": "{time_string}" is not in HH:MM:SS format.')
                    continue

                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])

                if not 0 <= hours <= 23:
                    st.error(f'Row {row_index + 2}, column "{column}": invalid hour "{hours}".')
                if not 0 <= minutes <= 59:
                    st.error(f'Row {row_index + 2}, column "{column}": invalid minute "{minutes}".')
                if not 0 <= seconds <= 59:
                    st.error(f'Row {row_index + 2}, column "{column}": invalid second "{seconds}".')

            except (ValueError, TypeError):
                st.error(f'Row {row_index + 2}, column "{column}": invalid time "{time_string}".')


def validate_energy_consumption(df):
    """
    Checks whether energy consumption has the correct sign.

    Charging activities must have negative energy consumption.
    All other activities must have positive energy consumption.

    Returns True if all energy values are valid, otherwise False.
    """
    for _, row in df.iterrows():
        if row['activity'] == 'charging':
            if row['energy consumption'] >= 0:
                return False
        else:
            if row['energy consumption'] <= 0:
                return False

    return True


def show_energy_consumption_errors(df):
    """Displays detailed errors for invalid energy consumption values."""
    for row_index, row in df.iterrows():
        activity = row['activity']
        energy = row['energy consumption']

        if activity == 'charging' and energy >= 0:
            st.error(f'Row {row_index + 2}: charging activity has an invalid energy consumption of {energy} kWh. Charging energy consumption must be negative.')

        elif activity != 'charging' and energy <= 0:
            st.error(f'Row {row_index + 2}: "{activity}" has an invalid energy consumption of {energy} kWh. Energy consumption must be positive.')


def validate_activity_times(df):
    """
    Checks whether the end time of each activity occurs after its start time.

    Returns True if all activity times are valid, otherwise False.
    """
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))
    durations = end_times - start_times

    return (durations > pd.Timedelta(0)).all()


def show_activity_time_errors(df):
    """Displays activities where the end time is not after the start time."""
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))

    for row_index in range(len(df)):
        duration = end_times.iloc[row_index] - start_times.iloc[row_index]

        if duration < pd.Timedelta(0):
            st.error(f'Row {row_index + 2}: end time ({df.iloc[row_index]["end time"]}) must be after start time ({df.iloc[row_index]["start time"]}).')
        elif end_time < start_time:
            end_time += pd.Timedelta(days=1)

def validate_minimum_soc(df):
    """
    Checks whether every bus remains above the minimum allowed SOC.

    Returns True if all buses remain above the minimum SOC,
    otherwise False.
    """
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
            st.error(f'Bus {bus}: battery drops to {minimum_battery:.2f} kWh. Minimum allowed is {minimum_battery_value:.2f} kWh.')


def validate_soh(assumed_soh):
    """
    Checks whether the assumed State of Health is between 85% and 95%.

    Returns True if SOH is valid, otherwise False.
    """
    return 85 <= assumed_soh <= 95


def validate_location_continuity(df):
    """
    Checks whether the end location of each activity matches the
    start location of the next activity for the same bus.

    Returns True if all locations are continuous, otherwise False.
    """
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
                st.error(f'Bus {bus}: activity ending at {bus_data.loc[index, "end time"]} ends at "{current_end_location}", but the next activity starts at "{next_start_location}" at {bus_data.loc[index + 1, "start time"]}.')


def validate_required_trips(df, timetable):
    """
    Checks whether the number of service trips in the bus planning
    equals the number of required trips in the timetable.

    Returns True if the numbers match, otherwise False.
    """
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
        st.error(f'{difference} required service trip(s) are missing. Required: {required_trip_count}, planned: {planned_trip_count}.')

    elif difference < 0:
        st.error(f'There are {abs(difference)} too many service trips. Required: {required_trip_count}, planned: {planned_trip_count}.')


def validate_minimum_charging_time(df):
    """
    Checks whether every charging activity lasts at least 15 minutes.

    Returns True if all charging activities meet the minimum duration,
    otherwise False.
    """
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
                st.error(f'Bus {row["bus"]}: charging time is only {duration:.1f} minutes ({row["start time"]} - {row["end time"]}). Minimum required is {MINIMUM_CHARGING_TIME} minutes.')


def validate_charging_speed(df):
    """
    Checks whether each charging activity uses the correct charging speed.

    Returns True if all charging speeds are correct, otherwise False.
    """
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
                    st.error(f'Bus {bus}: incorrect charging speed. Calculated speed: {charging_speed:.2f} kWh/min. Required speed: {required_speed:.2f} kWh/min. Battery before charging: {battery:.2f} kWh.')

            battery -= row['energy consumption']


def validate_no_overlapping_trips(df):
    """
    Checks whether activities assigned to the same bus overlap.

    Returns True if no activities overlap, otherwise False.
    """
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
                st.error(f'Bus {bus}: overlapping activities. Activity {index + 1} ends at {bus_data.loc[index, "end time"]}, while activity {index + 2} starts at {bus_data.loc[index + 1, "start time"]}.')


def status_check(text, is_valid):
    """Displays a green check mark when a validation passes and a red cross when it fails."""
    if is_valid:
        color = "#4CAF50"
        symbol = "✓"
    else:
        color = "#EA3323"
        symbol = "✕"

    html = f"""
    <div style="
        background:#F3F4F6;
        border-radius:10px;
        padding:10px 14px;
        margin:10px 0;
        display:flex;
        align-items:center;
        gap:14px;
        width:100%;
        box-sizing:border-box;
    ">
        <div style="
            width:32px;
            height:32px;
            min-width:32px;
            border-radius:6px;
            background:{color};
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:22px;
            font-weight:bold;
            line-height:1;
        ">
            {symbol}
        </div>
        <span style="
            font-size:16px;
            color:#222222;
            font-weight:500;
        ">
            {text}
        </span>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def validate_bus_planning(df):
    """
    Runs all validations that only require the bus planning.

    Returns True if all checks pass, otherwise False.
    """
    columns_valid = validate_columns(df)

    if not columns_valid:
        st.error("The bus planning contains errors.")

        with st.expander("Click here for details"):
            show_column_errors(df)

        return False

    energy_valid = validate_energy_consumption(df)
    time_format_valid = validate_time_format(df)

    if time_format_valid:
        activity_times_valid = validate_activity_times(df)
        charging_time_valid = validate_minimum_charging_time(df)
        charging_speed_valid = validate_charging_speed(df)
        no_overlaps = validate_no_overlapping_trips(df)
    else:
        activity_times_valid = False
        charging_time_valid = False
        charging_speed_valid = False
        no_overlaps = False

    minimum_soc_valid = validate_minimum_soc(df)
    locations_valid = validate_location_continuity(df)

    all_checks_passed = (
        columns_valid
        and energy_valid
        and time_format_valid
        and activity_times_valid
        and minimum_soc_valid
        and locations_valid
        and charging_time_valid
        and charging_speed_valid
        and no_overlaps
    )

    if all_checks_passed:
        st.success("The bus planning is valid.")

    else:
        st.error("The bus planning contains errors.")

        with st.expander("Click here for details"):
            with st.container(height=400):
                show_column_errors(df)
                show_time_format_errors(df)
                show_energy_consumption_errors(df)

                if time_format_valid:
                    show_activity_time_errors(df)
                    show_minimum_charging_time_errors(df)
                    show_charging_speed_errors(df)
                    show_overlapping_trip_errors(df)

                show_minimum_soc_errors(df)
                show_location_continuity_errors(df)

    return all_checks_passed