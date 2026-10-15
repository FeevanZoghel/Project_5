
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mpld3
from mpld3 import plugins
import streamlit.components.v1 as components
from html import escape


def gantt_chart_bus(bp, selected_buses=None):
    """Creates interactive Gantt charts of the bus planning."""

    if selected_buses is not None:
        bp = bp[bp['bus'].isin(selected_buses)]

    if bp.empty:
        st.info("Select at least one bus to display the Gantt chart.")
        return

    planning = bp.sort_values(['bus', 'start time']).copy()

    start_times = pd.to_timedelta(planning['start time'].astype(str))
    end_times = pd.to_timedelta(planning['end time'].astype(str))

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

        fig, ax = plt.subplots(figsize=(14, 7))

        group_planning = planning[planning['bus'].isin(group)]

        bus_positions = {}
        for i in range(len(group)):
            bus_positions[group[i]] = i

        activities_in_legend = []

        # Store hover information
        hover_x = []
        hover_y = []
        hover_labels = []

        for i in range(len(group_planning)):

            trip = group_planning.iloc[i]

            bus = trip['bus']
            activity = trip['activity']
            start = trip['start_hour']
            end = trip['end_hour']

            duration = end - start

            if duration < 0:
                duration += 24

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

            # Hover point at the centre of each activity
            hover_x.append(start + duration / 2)
            hover_y.append(y)

            hover_labels.append(
                f"<b>Start location:</b> "
                f"{escape(str(trip['start location']))}<br>"
                f"<b>End location:</b> "
                f"{escape(str(trip['end location']))}<br>"
                f"<b>Start time:</b> "
                f"{escape(str(trip['start time']))}<br>"
                f"<b>End time:</b> "
                f"{escape(str(trip['end time']))}"
            )

            if activity == 'service trip' and pd.notna(trip['line']):
                line = trip['line']

                ax.text(
                    start + duration / 2,
                    y,
                    f'{int(line)}',
                    ha='center',
                    va='center',
                    fontsize=8
                )

        # Add invisible hover points
        points = ax.scatter(
            hover_x,
            hover_y,
            s=25,
            color='red',
            alpha=0.6,
            zorder=10
        )

        tooltip = plugins.PointHTMLTooltip(
            points,
            labels=hover_labels,
            hoffset=15,
            voffset=15
        )

        plugins.connect(fig, tooltip)

        # Chart styling
        hours = range(5, 30)

        ax.set_xlim(5, 29)
        ax.set_xticks(hours)
        ax.set_xticklabels([
            f'{hour % 24:02d}:00' for hour in hours
        ])

        ax.set_yticks(range(len(group)))
        ax.set_yticklabels([
            f'Bus {bus}' for bus in group
        ])

        ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')

        ax.set_axisbelow(True)
        ax.grid(
            axis='x',
            color='#E5E7EB',
            linewidth=0.6,
            alpha=0.35
        )

        ax.set_axisbelow(True)

        ax.set_xlabel('Time')

        ax.set_yticks(range(len(group)))
        ax.set_yticklabels([f'Bus {bus}' for bus in group])
        ax.set_ylim(len(group) - 0.5, -0.5)

        ax.set_title('Improved bus plan')

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )

        plt.tight_layout()

        # Convert to interactive HTML
        html = mpld3.fig_to_html(fig)

        components.html(
            html,
            height=850,
            scrolling=False
        )

        plt.close(fig)
