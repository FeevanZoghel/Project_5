"""Improved bus planning algorithm adapted for Streamlit.

The scheduling logic is taken from AA_code_improved.py. Inputs are provided
as DataFrames and the result is returned, without file I/O or KPI exports.
"""

import pandas as pd


def solve_bus_planning(bp, dm, tt, assumed_battery_value=85, energy_method="mean", progress_callback=None):
    """
    Optimizes an electric bus schedule while considering travel times,
    energy consumption, battery capacity, and charging requirements.

    The optimization assigns trips to buses and determines the necessary
    material trips, idle periods, and charging activities to create a
    feasible bus planning.

    Argument:
        bp (pd.DataFrame): Original bus planning containing trip information,
            activities, assigned buses, and energy consumption.
        dm (pd.DataFrame): Distance matrix containing travel distances and
            minimum and maximum travel times between locations.
        tt (pd.DataFrame): Timetable containing the scheduled service trips.
        assumed_battery_value (float, optional): Assumed battery State of
            Health (SoH) as a percentage. Defaults to 85.
        energy_method (str, optional): Estimation method used for travel
            times and energy consumption. Must be "min", "mean", or "max".
            Defaults to "mean".
        progress_callback (callable, optional): Function used to report
            optimization progress. Defaults to None.

    Returns:
        pd.DataFrame: Improved bus planning containing the assigned buses,
            scheduled activities, start and end times, and energy consumption.

    Raises:
        ValueError: If energy_method is not "min", "mean", or "max".
    """
    bp = bp.copy()
    dm = dm.copy()
    tt = tt.copy()

    # Dataframe for improved bus plan

    ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','total battery bus' ,'total travel time','bus'])

    # Sort timetable, starting the day at 05:07 (dit stukje is met chat gemaakt)

    tt['sort_time'] = pd.to_datetime(tt['departure_time'], format='%H:%M')

    tt.loc[tt['sort_time'].dt.time < pd.Timestamp('05:07').time(), 'sort_time'] += pd.Timedelta(days=1)

    tt = tt.sort_values(by='sort_time').reset_index(drop=True)

    # lege set met bussen aanmaken

    bussen = []

    battery = {}

    charging_start = {}

    # Beginwaardes

    if energy_method not in ("min", "mean", "max"):
        raise ValueError("energy_method must be min, mean or max")
    def calculate_travel_time(dm_trip):
        """
        Calculates the estimated travel time based on the selected estimation method.

        Argument:
            dm_trip (pd.DataFrame): Distance matrix entries containing the minimum
                and maximum travel times for a specific trip.

        Returns:
            float: Estimated travel time in minutes, using the minimum, maximum,
                or average travel time based on energy_method.
        """
        min_time = dm_trip['min_travel_time'].iloc[0]
        max_time = dm_trip['max_travel_time'].iloc[0]

        if energy_method == "min":
            return min_time
        elif energy_method == "max":
            return max_time
        else:
            return (min_time + max_time) / 2
    if not 0 < assumed_battery_value <= 100:
        raise ValueError("assumed_battery_value must be between 0 and 100")

    max_battery = 300 * assumed_battery_value / 100

    charging_limit = 0.9 * max_battery

    fast_charge_per_min = 450 / 60

    slow_charge_per_min = 60 / 60

    min_battery_value = max_battery * 0.1

    def add_activity(ibp, bus, start_location, end_location, start_time, end_time,
                     activity, line, energy, battery_value, total_travel_time):
        """
        Adds a new activity to the improved bus planning DataFrame.

        Argument:
            ibp (pd.DataFrame): Improved bus planning to which the activity is added.
            bus (int): Identifier of the bus performing the activity.
            start_location (str): Starting location of the activity.
            end_location (str): Ending location of the activity.
            start_time (pd.Timestamp): Start time of the activity.
            end_time (pd.Timestamp): End time of the activity.
            activity (str): Type of activity, such as service trip, material trip,
                charging, or idle.
            line (str or None): Bus line associated with the activity, if applicable.
            energy (float): Energy consumption in kWh. Negative values indicate charging.
            battery_value (float): Remaining battery energy in kWh after the activity.
            total_travel_time (float): Cumulative travel time of the bus in minutes.

        Returns:
            None: The activity is added directly to the ibp DataFrame.
        """

        new_index = len(ibp)

        ibp.loc[new_index] = [start_location, end_location, start_time, end_time, activity, line, energy, battery_value, total_travel_time, bus]

    def check_charging_buses(bussen_opladen, ibp, battery, charging_start, start_time,
                             benodigde_energy, charging_limit, fast_charge_per_min,
                             slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip):
        
        """
        Checks charging buses and determines whether they can be assigned to a new trip.

        The function calculates the available charging time, updates battery levels,
        and accounts for energy consumption during idle periods. Buses located
        outside the garage are scheduled to return for charging.

        Argument:
            bussen_opladen (list): List of buses that need to be checked for charging.
            ibp (pd.DataFrame): Improved bus planning containing scheduled activities.
            battery (dict): Current battery energy in kWh for each bus.
            charging_start (dict): Starting time of the charging period for each bus.
            start_time (pd.Timestamp): Scheduled start time of the upcoming trip.
            benodigde_energy (float): Minimum energy required for the upcoming trip,
                including the required battery reserve.
            charging_limit (float): Battery energy threshold at which fast charging
                changes to slow charging.
            fast_charge_per_min (float): Fast charging rate in kWh per minute.
            slow_charge_per_min (float): Slow charging rate in kWh per minute.
            max_battery (float): Maximum available battery energy in kWh.
            beschikbare_bussen (list): List of buses available for the upcoming trip.
            dm (pd.DataFrame): Distance matrix containing travel times and distances.
            bp (pd.DataFrame): Original bus planning containing energy consumption data.
            trip (pd.Series): Upcoming service trip to be assigned.

        Returns:
            None: Updates the bus planning, battery levels, charging information,
                and available buses directly.
        """

        for bus in bussen_opladen:

            bus_planning = ibp[ibp['bus'] == bus]

            last_activity = bus_planning.iloc[-1, :]

            # bus staat al bij de garage

            if last_activity['end location'] == 'ehvgar':

                if bus not in charging_start:

                    charging_start[bus] = last_activity['end time']

                else:

                    available_minutes = max(0.0, (start_time - charging_start[bus]).total_seconds() / 60)
                    battery_start = battery[bus]

                    # Stop charging as soon as the battery reaches 100%.
                    if battery_start < charging_limit:
                        time_to_90 = (charging_limit - battery_start) / fast_charge_per_min
                        time_to_full = time_to_90 + (max_battery - charging_limit) / slow_charge_per_min
                    else:
                        time_to_full = (max_battery - battery_start) / slow_charge_per_min

                    charging_time = min(available_minutes, max(0.0, time_to_full))
                    if battery_start < charging_limit:
                        fast_minutes = min(charging_time, (charging_limit - battery_start) / fast_charge_per_min)
                        slow_minutes = charging_time - fast_minutes
                        charged_energy = fast_minutes * fast_charge_per_min + slow_minutes * slow_charge_per_min
                    else:
                        charged_energy = charging_time * slow_charge_per_min

                    charged_energy = min(max_battery - battery_start, charged_energy)
                    battery_after_charging = battery_start + charged_energy
                    charging_end = charging_start[bus] + pd.Timedelta(minutes=charging_time)
                    idle_minutes = max(0.0, (start_time - charging_end).total_seconds() / 60)
                    idle_energy = idle_minutes / 60 * 5

                    if charging_time >= 15 and battery_after_charging - idle_energy >= benodigde_energy:
                        battery[bus] = battery_after_charging
                        add_activity(ibp, bus, 'ehvgar', 'ehvgar', charging_start[bus], charging_end,
                                     'charging', None, -charged_energy, battery[bus], last_activity['total travel time'])

                        # Record the idle energy so the planning and battery ledger agree.
                        if idle_minutes > 1e-9:
                            battery[bus] -= idle_energy
                            add_activity(ibp, bus, 'ehvgar', 'ehvgar', charging_end, start_time,
                                         'idle', None, idle_energy, battery[bus], last_activity['total travel time'])

                        if last_activity['end location'] == trip['start']:
                            beschikbare_bussen.append(bus)
                        del charging_start[bus]

            else:

                material_start = last_activity['end location']

                dm_material = dm[(dm['start'] == material_start) & (dm['end'] == 'ehvgar')]

                material_travel_time = calculate_travel_time(dm_material)

                material_energy = bp[(bp['start location'] == material_start) & (bp['end location'] == 'ehvgar') &(bp['activity'] == 'material trip')]['energy consumption'].agg(energy_method)

                material_start_time = last_activity['end time']

                material_end_time = material_start_time + pd.Timedelta(minutes=material_travel_time)

                battery[bus] -= material_energy

                add_activity(ibp, bus, material_start, 'ehvgar', material_start_time, material_end_time, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)

                charging_start[bus] = material_end_time

    def garage_to_trip(bus, trip, start_time, ibp, battery, dm, bp):
        """
        Schedules a material trip from the garage to the starting location of a service trip.

        The function calculates the required travel time and energy consumption,
        updates the bus battery level, and adds the material trip to the improved
        bus planning. No activity is added if the service trip starts at the garage.

        Argument:
            bus (int): Identifier of the bus performing the material trip.
            trip (pd.Series): Upcoming service trip containing its starting location
                and bus line.
            start_time (pd.Timestamp): Scheduled departure time of the service trip.
            ibp (pd.DataFrame): Improved bus planning containing scheduled activities.
            battery (dict): Current battery energy in kWh for each bus.
            dm (pd.DataFrame): Distance matrix containing minimum and maximum travel times.
            bp (pd.DataFrame): Original bus planning containing energy consumption data.

        Returns:
            None: Updates the bus planning and battery level directly.
        """

        if trip['start'] == 'ehvgar':

                return

        dm_material = dm[(dm['start']=='ehvgar') & (dm['end'] == trip['start'])]

        material_travel_time = calculate_travel_time(dm_material)

        material_start_time = start_time - pd.Timedelta(minutes = material_travel_time)

        material_end_time = material_start_time+pd.Timedelta(minutes = material_travel_time)

        material_energy = bp[(bp['start location'] == 'ehvgar') & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].agg(energy_method)

        battery[bus] -= material_energy

        add_activity(ibp, bus, 'ehvgar', trip['start'], material_start_time, material_end_time, 'material trip', trip['line'], material_energy, battery[bus], material_travel_time)

    def check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=False):
        """
        Calculates the travel time and energy consumption of a material trip.

        The function determines whether a bus needs to travel from its current
        location to the starting location of the next service trip. If required,
        it calculates the travel time and energy consumption. When toevoegen
        is True, the material trip is added to the improved bus planning and
        the battery level is updated.

        Argument:
            bus (int): Identifier of the bus performing the material trip.
            last_activity (pd.Series): Last scheduled activity of the bus.
            trip (pd.Series or dict): Upcoming trip containing its starting location.
            ibp (pd.DataFrame): Improved bus planning containing scheduled activities.
            battery (dict): Current battery energy in kWh for each bus.
            dm (pd.DataFrame): Distance matrix containing minimum and maximum travel times.
            bp (pd.DataFrame): Original bus planning containing energy consumption data.
            toevoegen (bool, optional): Whether to add the material trip to the
                planning and update the battery level. Defaults to False.

        Returns:
            tuple: Contains the estimated material travel time in minutes (float)
                and the corresponding energy consumption in kWh (float).
        """

        if last_activity['end location'] == trip['start']:

            material_travel_time = 0

            material_energy = 0

        else: 

            dm_material = dm[(dm['start'] == last_activity['end location']) & (dm['end'] == trip['start'])]

            material_travel_time = calculate_travel_time(dm_material)

            material_energy = bp[(bp['start location'] == last_activity['end location']) & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].agg(energy_method)

        aankomsttijd = last_activity['end time'] + pd.Timedelta(minutes=material_travel_time)

        if toevoegen and material_travel_time >0:

            battery[bus] -= material_energy

            add_activity(ibp, bus, last_activity['end location'], trip['start'], last_activity['end time'], aankomsttijd, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)

        return material_travel_time, material_energy

    def calculate_idle_time(bus, start_time, ibp, battery, toevoegen = False):
        """
        Calculates the idle time and energy consumption of a bus between activities.

        The function determines the idle period between the bus's last scheduled
        activity and the start of the next activity. Energy consumption is
        calculated using a constant rate of 5 kWh per hour. When toevoegen
        is True, the idle activity is added to the improved bus planning
        and the battery level is updated.

        Argument:
            bus (int): Identifier of the bus.
            start_time (pd.Timestamp): Scheduled start time of the next activity.
            ibp (pd.DataFrame): Improved bus planning containing scheduled activities.
            battery (dict): Current battery energy in kWh for each bus.
            toevoegen (bool, optional): Whether to add the idle activity to the
                planning and update the battery level. Defaults to False.

        Returns:
            float: Energy consumption during the idle period in kWh.
        """

        last_activity = ibp[ibp['bus'] == bus].iloc[-1]

        idle_start = last_activity['end time']

        idle_end = start_time

        idle_hours = max(0, (idle_end - idle_start).total_seconds() / 3600) # nooit een negatieve wachttijd

        idle_energy = idle_hours * 5  # 5 kwh energie verbruik 

        if toevoegen and idle_hours>0:

            battery[bus] -= idle_energy

            add_activity(ibp, bus, last_activity['end location'], last_activity['end location'], idle_start, idle_end, 'idle', None, idle_energy, battery[bus], last_activity['total travel time'])

        return idle_energy

    for i in range(len(tt)):

        if progress_callback is not None:
            progress_callback(i, len(tt), "Optimizing")

        trip = tt.iloc[i,:]

        dm_trip = dm[(dm['start'] == trip['start']) &(dm['end'] == trip['end']) &(dm['line'] == trip['line'])]

        energy_consumption = bp[(bp['start location'] == trip['start']) & (bp['end location'] == trip['end']) & (bp['line'] == trip['line']) &(bp['activity'] == 'service trip')]['energy consumption'].agg(energy_method)

        start_time = trip['sort_time']

        travel_time = calculate_travel_time(dm_trip)

        end_time = start_time + pd.Timedelta(minutes=travel_time)

        # als er geen bussen maakt het een nieuwe bus aan

        if len(bussen) == 0:

            bussen.append(1)

            battery[1] = max_battery

            #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden

            garage_to_trip(1, trip, start_time, ibp, battery, dm, bp)

            new_index = len(ibp)

            ibp.loc[new_index, 'start location']        = trip['start']

            ibp.loc[new_index, 'end location']          = trip['end']

            ibp.loc[new_index, 'start time']            = start_time

            ibp.loc[new_index, 'end time']              = end_time

            ibp.loc[new_index, 'line']                  = trip['line']

            ibp.loc[new_index, 'bus']                   = bussen[0]

            ibp.loc[new_index, 'activity']              = 'service trip'

            ibp.loc[new_index, 'energy consumption']    = energy_consumption

            ibp.loc[new_index, 'total travel time']     = travel_time

            battery[1]                             -= energy_consumption

            ibp.loc[new_index, 'total battery bus']     = battery[1]

            continue

        material_energy         = bp[(bp['start location'] == trip['end']) & (bp['end location'] == 'ehvgar') & (bp['activity'] == 'material trip')]['energy consumption'].agg(energy_method)

        if trip['end'] =='ehvgar':

            benodigde_energy = energy_consumption +min_battery_value

        else: 

             benodigde_energy = energy_consumption +material_energy+min_battery_value

        beschikbare_bussen = []

        bussen_opladen = []

        # Bussen die al aan het laden zijn opnieuw controleren

        for bus in charging_start:

            bussen_opladen.append(bus)

        # kijkt of een bus beschikbaar is

        for bus in bussen:

            if bus in charging_start:
                continue

            bus_planning = ibp[ibp['bus'] == bus]

            last_activity = bus_planning.iloc[-1, :]

            material_travel_time, material_energy = check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp)

            idle_energy = calculate_idle_time(bus, start_time - pd.Timedelta(minutes=material_travel_time), ibp, battery)

            if (last_activity['end time'] + pd.Timedelta(minutes=material_travel_time) <= start_time):

                if battery[bus] >= benodigde_energy + material_energy + idle_energy:

                    beschikbare_bussen.append(bus)

                else:

                    if bus not in bussen_opladen:

                        bussen_opladen.append(bus)

        check_charging_buses(bussen_opladen, ibp, battery, charging_start, start_time, benodigde_energy, charging_limit, fast_charge_per_min, slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip)

    #########################hier niet aankomen#############################

        # als er geen bus beschikbaar is dan een nieuwe bus toevoegen

        nieuwe_bus_aangemaakt = False

        if len(beschikbare_bussen)==0:

            nieuwe_bus = len(bussen) + 1

            bussen.append(nieuwe_bus)

            battery[nieuwe_bus] = max_battery

            #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden

            garage_to_trip(nieuwe_bus, trip, start_time, ibp, battery, dm, bp)

            gekozen_bus = nieuwe_bus

            nieuwe_bus_aangemaakt = True

        # kiest de bus met de hoogste traveltijd 

        else:

                gekozen_bus = max(

                    beschikbare_bussen,

                    key=lambda b: ibp[ibp['bus'] == b].iloc[-1]['end time']

                )

                nieuwe_bus_aangemaakt = False

                last_activity = ibp[ibp['bus'] == gekozen_bus].iloc[-1, :]

                check_material_trip(gekozen_bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=True)

                calculate_idle_time(gekozen_bus, start_time, ibp, battery, toevoegen = True)

                # Haal de huidige totale reistijd van de gekozen bus op

                hoogste_travel_tijd = ibp[ibp['bus'] == gekozen_bus].iloc[-1]['total travel time']

        battery[gekozen_bus] -= energy_consumption

        if nieuwe_bus_aangemaakt:

            total_travel_time = travel_time

        else:

            total_travel_time = hoogste_travel_tijd + travel_time

        add_activity(ibp, gekozen_bus, trip['start'], trip['end'], start_time, end_time, 'service trip', trip['line'], energy_consumption, battery[gekozen_bus], total_travel_time)

    if progress_callback is not None:
        progress_callback(len(tt), len(tt), "Returning buses to the garage")

    # Return buses to the garage and fully charge them.

    for bus in bussen: 

        last_activity = ibp[ibp['bus'] == bus].iloc[-1]

        if last_activity['end location']!= 'ehvgar':

            trip_gar = {'start': 'ehvgar'} # normaal de volgende trip doorgeven, nu het alle trips gereden, dus de 'volgende' trip moet starten bij ehvgar wat de eindlocatie is

            material_travel_time, material_energy = check_material_trip(bus, last_activity, trip_gar, ibp, battery, dm, bp, toevoegen = True )

    for bus in bussen:
        if battery[bus] >= max_battery - 1e-9:
            continue
        last_activity = ibp[ibp['bus'] == bus].iloc[-1]
        battery_start = battery[bus]
        if battery_start < charging_limit:
            time_to_90 = (charging_limit - battery_start) / fast_charge_per_min
            charging_time = time_to_90 + (max_battery - charging_limit) / slow_charge_per_min
        else:
            charging_time = (max_battery - battery_start) / slow_charge_per_min
        # At the end of the operational day, reserve at least 15 minutes
        # for the charging activity. The actual energy is capped at 100%.
        charging_time = max(15.0, charging_time)
        charging_end = last_activity['end time'] + pd.Timedelta(minutes=charging_time)
        charged_energy = max_battery - battery_start
        battery[bus] = max_battery
        add_activity(ibp, bus, 'ehvgar', 'ehvgar', last_activity['end time'], charging_end,
                     'charging', None, -charged_energy, battery[bus], last_activity['total travel time'])

    ibp = ibp.sort_values(['bus', 'start time']).reset_index(drop=True)
    if progress_callback is not None:
        progress_callback(len(tt), len(tt), "Completed")
    return ibp
