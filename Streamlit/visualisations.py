import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def gantt_chart_bus(bp):
    """Creates Gantt charts of the bus planning."""
    planning = bp.sort_values(['bus', 'start time'])
    start_times = pd.to_timedelta(planning['start time'].astype(str))
    end_times = pd.to_timedelta(planning['end time'].astype(str))
    planning = planning.copy()
    planning['start_hour'] = start_times.dt.total_seconds() / 3600
    planning['end_hour'] = end_times.dt.total_seconds() / 3600
    planning.loc[planning['start_hour'] < 5, 'start_hour'] += 24
    planning.loc[planning['end_hour'] <= 5, 'end_hour'] += 24
    colors = {
        'service trip': 'skyblue',
        'material trip': 'orange',
        'idle': 'lightgrey',
        'charging': 'yellowgreen'
    }
    buses = sorted(planning['bus'].unique())
    groups = []
    for i in range(0, len(buses), 20):
        groups.append(buses[i:i + 20])
    for group in groups:
        fig, ax = plt.subplots(figsize=(18, 8))
        group_planning = planning[planning['bus'].isin(group)]
        bus_positions = {}
        for i in range(len(group)):
            bus_positions[group[i]] = i
        activities_in_legend = []
        for i in range(len(group_planning)):
            trip = group_planning.iloc[i]
            bus = trip['bus']
            activity = trip['activity']
            start = trip['start_hour']
            end = trip['end_hour']
            duration = end - start
            y = bus_positions[bus]
            if activity not in activities_in_legend:
                label = activity
                activities_in_legend.append(activity)
            else:
                label = None
            ax.barh(
                y,
                duration,
                left=start,
                height=0.8,
                color=colors[activity],
                edgecolor='grey',
                linewidth=1,
                label=label
            )
            if activity == 'service trip':
                line = trip['line']
                ax.text(
                    start + duration / 2,
                    y,
                    f'{int(line)}',
                    ha='center',
                    va='center',
                    fontsize=8
                )
        hours = range(5, 30)
        ax.set_xlim(5, 29)
        ax.set_xticks(hours)
        ax.set_xticklabels([f'{hour % 24:02d}:00' for hour in hours])
        ax.set_yticks(range(len(group)))
        ax.set_yticklabels([f'Bus {bus}' for bus in group])
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.grid(axis='x', linestyle='-', alpha=0.4)
        ax.set_axisbelow(True)
        ax.set_xlabel('Time')
        ax.set_ylabel('Bus')
        ax.set_title('Improved bus plan')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=4)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)