import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

def validate_columns(df):
    """Checks whether the DataFrame contains exactly the required columns in the correct order."""
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
    """Checks whether all start and end times use the HH:MM:SS format."""
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
    """Checks whether energy consumption has the correct sign."""
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
    """Checks whether all activity durations are valid, including activities crossing midnight."""
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))
    for start_time, end_time in zip(start_times, end_times):
        if end_time < start_time:
            end_time += pd.Timedelta(days=1)
        duration = end_time - start_time
        if duration < pd.Timedelta(0):
            return False
    return True

def show_activity_time_errors(df):
    """Displays activities with invalid time durations."""
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))
    for row_index in range(len(df)):
        start_time = start_times.iloc[row_index]
        end_time = end_times.iloc[row_index]
        if end_time < start_time:
            end_time += pd.Timedelta(days=1)
        duration = end_time - start_time
        if duration < pd.Timedelta(0):
            st.error(f'Row {row_index + 2}: invalid activity duration.')

def validate_bus_planning(df):
    """Runs all data checks for the bus planning."""
    columns_valid = validate_columns(df)
    if not columns_valid:
        st.error("The bus planning contains errors.")
        with st.expander("Click here for details"):
            show_column_errors(df)
        return False
    time_format_valid = validate_time_format(df)
    energy_valid = validate_energy_consumption(df)
    if time_format_valid:
        activity_times_valid = validate_activity_times(df)
    else:
        activity_times_valid = False
    all_checks_passed = columns_valid and time_format_valid and energy_valid and activity_times_valid
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
    return all_checks_passed