
import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = [
    'start location', 'end location', 'start time',
    'end time', 'activity', 'line', 'energy consumption', 'bus'
]


def validate_columns(df):
    """
    Checks whether the DataFrame contains the required columns.

    The function compares the column names and their order
    with the predefined list of required columns.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns to be validated.

    Returns:
        bool: True if all required columns are present in
            the correct order, otherwise False.
    """
    return df.columns.tolist() == REQUIRED_COLUMNS


def show_column_errors(df):
    """
    Displays detailed error messages for incorrect columns.

    The function checks the number, names and order of the
    columns in the DataFrame. Missing, incorrect and
    unexpected columns are reported using Streamlit.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns to be checked.

    Returns:
        None: Displays error messages in the Streamlit interface.
    """
    actual_columns = df.columns.tolist()

    if len(actual_columns) != len(REQUIRED_COLUMNS):
        st.error(
            f"The number of columns is incorrect. "
            f"Expected {len(REQUIRED_COLUMNS)}, "
            f"but found {len(actual_columns)}."
        )

    for index, expected_column in enumerate(REQUIRED_COLUMNS):
        if index >= len(actual_columns):
            st.error(f'Missing column: "{expected_column}".')
            continue

        actual_column = actual_columns[index]

        if actual_column != expected_column:
            st.error(
                f'Column {index + 1} is "{actual_column}". '
                f'It should be "{expected_column}".'
            )

    if len(actual_columns) > len(REQUIRED_COLUMNS):
        extra_columns = actual_columns[len(REQUIRED_COLUMNS):]

        for column in extra_columns:
            st.error(f'Unexpected column: "{column}".')


def validate_time_format(df):
    """
    Checks whether all time values use a valid HH:MM:SS format.

    The function checks the start and end time columns.
    Each time value must contain hours, minutes and seconds,
    separated by colons.

    Hours must be between 0 and 23, while minutes and
    seconds must be between 0 and 59.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'start time' and 'end time'.

    Returns:
        bool: True if all time values are valid,
            otherwise False.
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
    """
    Displays detailed error messages for invalid time values.

    The function checks the start and end time columns and
    identifies values that do not follow the HH:MM:SS format.

    Invalid hours, minutes and seconds are reported separately.
    Each error message includes the corresponding row number
    and column name.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'start time' and 'end time'.

    Returns:
        None: Displays detailed error messages in Streamlit.
    """
    time_columns = ['start time', 'end time']

    for column in time_columns:
        for row_index, value in enumerate(df[column]):
            time_string = str(value)

            try:
                parts = time_string.split(':')

                if len(parts) != 3:
                    st.error(
                        f'Row {row_index + 2}, column "{column}": '
                        f'"{time_string}" is not in HH:MM:SS format.'
                    )
                    continue

                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])

                if not 0 <= hours <= 23:
                    st.error(
                        f'Row {row_index + 2}, column "{column}": '
                        f'invalid hour "{hours}".'
                    )

                if not 0 <= minutes <= 59:
                    st.error(
                        f'Row {row_index + 2}, column "{column}": '
                        f'invalid minute "{minutes}".'
                    )

                if not 0 <= seconds <= 59:
                    st.error(
                        f'Row {row_index + 2}, column "{column}": '
                        f'invalid second "{seconds}".'
                    )

            except (ValueError, TypeError):
                st.error(
                    f'Row {row_index + 2}, column "{column}": '
                    f'invalid time "{time_string}".'
                )


def validate_energy_consumption(df):
    """
    Checks whether energy consumption values have the correct sign.

    Charging activities must have negative energy consumption
    because energy is added to the battery.

    All other activities must have positive energy consumption
    because energy is used by the bus.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'activity' and 'energy consumption'.

    Returns:
        bool: True if all energy consumption values have
            the correct sign, otherwise False.
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
    """
    Displays error messages for invalid energy consumption.

    The function checks whether charging activities have
    negative energy consumption and all other activities
    have positive energy consumption.

    Each invalid value is reported with its row number,
    activity type and energy consumption in kWh.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'activity' and 'energy consumption'.

    Returns:
        None: Displays detailed error messages in Streamlit.
    """
    for row_index, row in df.iterrows():
        activity = row['activity']
        energy = row['energy consumption']

        if activity == 'charging' and energy >= 0:
            st.error(
                f'Row {row_index + 2}: charging activity has '
                f'an invalid energy consumption of {energy} kWh. '
                f'Charging energy consumption must be negative.'
            )

        elif activity != 'charging' and energy <= 0:
            st.error(
                f'Row {row_index + 2}: "{activity}" has '
                f'an invalid energy consumption of {energy} kWh. '
                f'Energy consumption must be positive.'
            )


def validate_activity_times(df):
    """
    Checks whether all activity durations are non-negative.

    The function calculates the duration of each activity
    using its start and end times.

    If an activity crosses midnight, one day is added to
    the end time to correct the negative time difference.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'start time' and 'end time'.

    Returns:
        bool: True if all calculated activity durations
            are non-negative, otherwise False.
    """
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
    """
    Displays error messages for invalid activity durations.

    The function calculates the duration of each activity
    using the start and end times.

    Activities crossing midnight are corrected by adding
    one day to the end time.

    If an activity has a negative duration after this
    correction, its row number is displayed in Streamlit.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the columns 'start time' and 'end time'.

    Returns:
        None: Displays error messages for invalid
            activity durations in Streamlit.
    """
    start_times = pd.to_timedelta(df['start time'].astype(str))
    end_times = pd.to_timedelta(df['end time'].astype(str))

    for row_index in range(len(df)):
        start_time = start_times.iloc[row_index]
        end_time = end_times.iloc[row_index]

        if end_time < start_time:
            end_time += pd.Timedelta(days=1)

        duration = end_time - start_time

        if duration < pd.Timedelta(0):
            st.error(
                f'Row {row_index + 2}: invalid activity duration.'
            )


def validate_bus_planning(df):
    """
    Performs all data validation checks on the bus planning.

    The function checks whether the DataFrame contains the
    required columns, valid time formats, correct energy
    consumption signs and valid activity durations.

    Column validation is performed first. If the columns
    are incorrect, the remaining checks are skipped.

    Activity duration validation is only performed when
    all time values have a valid format.

    The overall validation result and any detected errors
    are displayed in the Streamlit interface.

    Args:
        df (pd.DataFrame): Bus planning DataFrame containing
            the planning data to be validated.

    Returns:
        bool: True if all validation checks pass,
            otherwise False.
    """
    columns_valid = validate_columns(df)

    if not columns_valid:
        st.error("The bus planning data contains errors.")

        with st.expander("Click here for details"):
            show_column_errors(df)

        return False

    time_format_valid = validate_time_format(df)
    energy_valid = validate_energy_consumption(df)

    if time_format_valid:
        activity_times_valid = validate_activity_times(df)
    else:
        activity_times_valid = False

    all_checks_passed = (
        columns_valid
        and time_format_valid
        and energy_valid
        and activity_times_valid
    )

    if all_checks_passed:
        st.success("The bus planning data is valid.")

    else:
        st.error("The bus planning contains errors.")

        with st.expander("Click here for details"):
            with st.container():
                show_column_errors(df)
                show_time_format_errors(df)
                show_energy_consumption_errors(df)

                if time_format_valid:
                    show_activity_time_errors(df)

    return all_checks_passed
