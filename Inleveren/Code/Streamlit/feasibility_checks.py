
import pandas as pd
import streamlit as st

ASSUMED_SOH = 85
INITIAL_BATTERY_CAPACITY = 300
MINIMUM_SOC = 0.10

QUICK_CHARGING_SPEED = 450 / 60  # kWh per minute
SLOW_CHARGING_SPEED = 60 / 60    # kWh per minute

MINIMUM_CHARGING_TIME = 15
OPERATIONAL_DAY_START = 5 * 60 + 7

ENERGY_TOLERANCE = 0.1
TIME_TOLERANCE = 1e-6

def get_max_battery(assumed_soh=ASSUMED_SOH):
    """Returns the maximum usable battery capacity in kWh."""
    return (
        INITIAL_BATTERY_CAPACITY
        * assumed_soh
        / 100
    )


def get_minimum_battery(assumed_soh=ASSUMED_SOH):
    """Returns the minimum allowed battery capacity in kWh."""
    return get_max_battery(assumed_soh) * MINIMUM_SOC


def get_operational_minutes(time_values):
    """Converts timestamps and clock times into operational minutes."""

    def convert_time(value):

        if isinstance(value, pd.Timedelta):
            minutes = value.total_seconds() / 60

        elif isinstance(value, pd.Timestamp):
            minutes = (
                value.hour * 60
                + value.minute
                + value.second / 60
                + value.microsecond / 60000000
            )

        else:
            time_str = str(value)

            if " " in time_str:
                time_str = time_str.split(" ")[-1]

            minutes = (
                pd.to_timedelta(time_str).total_seconds() / 60
            )

        if minutes < OPERATIONAL_DAY_START:
            minutes += 1440

        return minutes

    return time_values.apply(convert_time)


def sort_bus_planning(df):
    """Sorts activities by bus and operational start time."""

    planning = df.copy()

    planning["_start_minutes"] = get_operational_minutes(
        planning["start time"]
    )

    return planning.sort_values(
        ["bus", "_start_minutes"],
        kind="stable"
    ).reset_index(drop=True)


def get_activity_duration_minutes(start_time, end_time):
    """Calculates activity duration, including midnight."""

    def convert_time(value):

        if isinstance(value, pd.Timedelta):
            return value.total_seconds() / 60

        if isinstance(value, pd.Timestamp):
            return (
                value.hour * 60
                + value.minute
                + value.second / 60
                + value.microsecond / 60000000
            )

        time_str = str(value)

        if " " in time_str:
            time_str = time_str.split(" ")[-1]

        return pd.to_timedelta(time_str).total_seconds() / 60

    start = convert_time(start_time)
    end = convert_time(end_time)

    duration = end - start

    if duration < 0:
        duration += 1440

    return duration


def calculate_expected_charging_energy(
    battery_start,
    duration,
    assumed_soh=ASSUMED_SOH
):
    """
    Calculates expected charging energy.

    Fast charging: 450 kW up to 90% SOC.
    Slow charging: 60 kW from 90% to 100% SOC.
    """

    max_battery = get_max_battery(assumed_soh)
    charging_limit = 0.90 * max_battery

    battery_start = min(max_battery, battery_start)

    if duration <= 0:
        return 0.0

    # Fast charging phase
    fast_minutes = min(
        duration,
        max(0.0, charging_limit - battery_start)
        / QUICK_CHARGING_SPEED
    )

    fast_energy = fast_minutes * QUICK_CHARGING_SPEED

    # Slow charging phase
    slow_minutes = duration - fast_minutes
    slow_energy = slow_minutes * SLOW_CHARGING_SPEED

    # Never charge beyond maximum battery capacity
    expected_energy = min(
        max(0.0, max_battery - battery_start),
        fast_energy + slow_energy
    )

    return expected_energy

def validate_minimum_soc(df, assumed_soh=ASSUMED_SOH):
    """Checks whether every bus remains above the minimum SOC."""

    minimum_battery = get_minimum_battery(assumed_soh)
    max_battery = get_max_battery(assumed_soh)

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        battery = max_battery

        for energy in bus_data["energy consumption"]:

            battery -= float(energy)
            battery = min(battery, max_battery)

            if battery < minimum_battery - ENERGY_TOLERANCE:
                return False

    return True


def show_minimum_soc_errors(df, assumed_soh=ASSUMED_SOH):
    """Displays buses that drop below the minimum allowed SOC."""

    minimum_battery = get_minimum_battery(assumed_soh)
    max_battery = get_max_battery(assumed_soh)

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        battery = max_battery
        lowest_battery = max_battery

        for energy in bus_data["energy consumption"]:

            battery -= float(energy)
            battery = min(battery, max_battery)

            lowest_battery = min(lowest_battery, battery)

        if lowest_battery < minimum_battery - ENERGY_TOLERANCE:

            st.error(
                f"Bus {bus}: battery dropped to "
                f"{lowest_battery:.2f} kWh "
                f"(minimum: {minimum_battery:.2f} kWh, "
                f"SoH: {assumed_soh}%)."
            )


def validate_soh(assumed_soh):
    """Checks whether SoH is between 85% and 95%."""

    return 85 <= assumed_soh <= 95


def validate_location_continuity(df):
    """Checks whether consecutive activities have matching locations."""

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data) - 1):

            end_location = bus_data.loc[i, "end location"]
            next_start = bus_data.loc[i + 1, "start location"]

            if end_location != next_start:
                return False

    return True


def show_location_continuity_errors(df):
    """Displays every location mismatch."""

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data) - 1):

            end_location = bus_data.loc[i, "end location"]
            next_start = bus_data.loc[i + 1, "start location"]

            if end_location != next_start:

                st.error(
                    f"Bus {bus}: location mismatch "
                    f"({end_location} → {next_start})."
                )

def validate_required_trips(df, timetable):
    """Checks whether all required service trips are included."""

    required_trips = len(timetable)

    planned_trips = len(
        df[df["activity"] == "service trip"]
    )

    return required_trips == planned_trips


def show_required_trip_errors(df, timetable):
    """Displays missing or extra service trips."""

    required_trips = len(timetable)

    planned_trips = len(
        df[df["activity"] == "service trip"]
    )

    difference = required_trips - planned_trips

    if difference > 0:

        st.error(
            f"{difference} required service trip(s) missing "
            f"({planned_trips}/{required_trips} planned)."
        )

    elif difference < 0:

        st.error(
            f"{abs(difference)} extra service trip(s) planned "
            f"({planned_trips}/{required_trips} required)."
        )


def validate_minimum_charging_time(df):
    """Checks whether every charging activity lasts at least 15 minutes."""

    charging = df[df["activity"] == "charging"]

    for _, row in charging.iterrows():

        duration = get_activity_duration_minutes(
            row["start time"],
            row["end time"]
        )

        if duration < MINIMUM_CHARGING_TIME - TIME_TOLERANCE:
            return False

    return True


def show_minimum_charging_time_errors(df):
    """Displays charging activities shorter than 15 minutes."""

    charging = df[df["activity"] == "charging"]

    for _, row in charging.iterrows():

        duration = get_activity_duration_minutes(
            row["start time"],
            row["end time"]
        )

        if duration < MINIMUM_CHARGING_TIME - TIME_TOLERANCE:

            st.error(
                f"Bus {row['bus']}: charging lasted "
                f"{duration:.2f} min "
                f"(minimum: {MINIMUM_CHARGING_TIME} min)."
            )



def get_charging_speed_errors(df, assumed_soh=ASSUMED_SOH):
    """
    Simulates battery charging using the original charging logic.

    Fast charging: 450 kW up to 90% SOC.
    Slow charging: 60 kW from 90% to 100% SOC.

    Uses the selected SoH and correct operational-day sorting.
    """

    errors = []

    max_battery = get_max_battery(assumed_soh)
    charging_limit = 0.90 * max_battery
    minimum_battery = get_minimum_battery(assumed_soh)

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        battery = max_battery

        for _, row in bus_data.iterrows():

            if row["activity"] == "charging":

                duration = get_activity_duration_minutes(
                    row["start time"],
                    row["end time"]
                )

                if duration < MINIMUM_CHARGING_TIME - TIME_TOLERANCE:

                    errors.append(
                        f"Bus {bus}: charging duration is "
                        f"{duration:.2f} minutes "
                        f"(minimum: {MINIMUM_CHARGING_TIME} minutes)."
                    )

                    continue

                time_available = duration

                # Fast charging up to 90% SOC
                if battery < charging_limit:

                    needed_energy = charging_limit - battery
                    time_needed = needed_energy / QUICK_CHARGING_SPEED

                    if time_available <= time_needed:

                        battery += time_available * QUICK_CHARGING_SPEED
                        time_available = 0

                    else:

                        battery = charging_limit
                        time_available -= time_needed

                # Slow charging from 90% to 100% SOC
                if time_available > 0 and battery < max_battery:

                    battery += min(
                        time_available * SLOW_CHARGING_SPEED,
                        max_battery - battery
                    )

            else:

                battery -= float(row["energy consumption"])

            if battery < minimum_battery - ENERGY_TOLERANCE:

                errors.append(
                    f"Bus {bus}: battery dropped to "
                    f"{battery:.2f} kWh "
                    f"(minimum: {minimum_battery:.2f} kWh)."
                )

            if battery > max_battery + ENERGY_TOLERANCE:

                errors.append(
                    f"Bus {bus}: battery exceeded maximum capacity "
                    f"({battery:.2f}/{max_battery:.2f} kWh)."
                )

    return errors


def validate_charging_speed(df, assumed_soh=ASSUMED_SOH):
    """Returns True when the charging simulation is feasible."""

    return len(
        get_charging_speed_errors(df, assumed_soh)
    ) == 0


def show_charging_speed_errors(df, assumed_soh=ASSUMED_SOH):
    """Displays charging simulation errors."""

    errors = get_charging_speed_errors(df, assumed_soh)

    for error in errors:
        st.error(error)


def get_overlapping_trip_errors(df):
    """Finds overlapping activities for each bus."""

    errors = []

    planning = sort_bus_planning(df)

    for bus, bus_data in planning.groupby("bus"):

        previous_end = None

        for _, row in bus_data.iterrows():

            start = float(row["_start_minutes"])

            duration = get_activity_duration_minutes(
                row["start time"],
                row["end time"]
            )

            end = start + duration

            if (
                previous_end is not None
                and start < previous_end - TIME_TOLERANCE
            ):

                errors.append(
                    f"Bus {bus}: overlapping activity "
                    f"starting at {row['start time']}."
                )

            previous_end = (
                end if previous_end is None
                else max(previous_end, end)
            )

    return errors


def validate_no_overlapping_trips(df):
    """Checks whether activities assigned to a bus overlap."""

    return len(get_overlapping_trip_errors(df)) == 0


def show_overlapping_trip_errors(df):
    """Displays all overlapping activity errors."""

    for error in get_overlapping_trip_errors(df):
        st.error(error)

def status_check(text, is_valid):
    """Displays a green check mark or a red cross."""

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
    ">{symbol}</div>
    <span style="
        font-size:16px;
        color:#222222;
        font-weight:500;
    ">{text}</span>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)
