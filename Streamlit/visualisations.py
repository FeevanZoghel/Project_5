
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

    # Prepare planning
    planning = bp.sort_values(['bus', 'start time']).copy()

    start_times = pd.to_timedelta(
        planning['start time'].astype(str)
    )

    end_times = pd.to_timedelta(
        planning['end time'].astype(str)
    )

    planning['start_hour'] = start_times.dt.total_seconds() / 3600
    planning['end_hour'] = end_times.dt.total_seconds() / 3600

    # Handle times after midnight
    planning.loc[
        planning['start_hour'] < 5, 'start_hour'
    ] += 24

    planning.loc[
        planning['end_hour'] <= 5, 'end_hour'
    ] += 24

    # Activity colors
    colors = {
        'service trip': 'skyblue',
        'material trip': 'orange',
        'idle': 'lightgrey',
        'charging': 'yellowgreen'
    }

    # Split buses into groups of maximum 20
    buses = sorted(planning['bus'].unique())

    groups = [
        buses[i:i + 20]
        for i in range(0, len(buses), 20)
    ]

    for group in groups:

        fig, ax = plt.subplots(figsize=(14, 7))

        group_planning = planning[
            planning['bus'].isin(group)
        ]

        bus_positions = {
            bus: i for i, bus in enumerate(group)
        }

        activities_in_legend = []

        # Store hover information
        hover_x = []
        hover_y = []
        hover_labels = []

        # Draw activities
        for _, trip in group_planning.iterrows():

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

            # Draw activity bar
            ax.barh(
                y,
                duration,
                left=start,
                height=0.8,
                color=colors[activity],
                edgecolor='grey',
                linewidth=2,
                label=label
            )

            # Hover point in the middle of the bar
            hover_x.append(start + duration / 2)
            hover_y.append(y)

            # Tooltip information
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

            # Line numbers inside service trips
            if (
                activity == 'service trip'
                and pd.notna(trip['line'])
            ):
                ax.text(
                    start + duration / 2,
                    y,
                    f"{int(trip['line'])}",
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='black'
                )

        # Hover points
        points = ax.scatter(
            hover_x,
            hover_y,
            s=25,
            color='red',
            alpha=0,
            zorder=10
        )

        # Add tooltip
        tooltip = plugins.PointHTMLTooltip(
            points,
            labels=hover_labels,
            hoffset=15,
            voffset=15
        )

        plugins.connect(fig, tooltip)

        # X-axis
        hours = range(5, 30)

        ax.set_xlim(4.2, 29)
        ax.set_xticks(hours)

        ax.set_xticklabels([
            f'{hour % 24:02d}:00'
            for hour in hours
        ])

        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')

        # Y-axis
        ax.set_yticks(range(len(group)))
        ax.set_yticklabels([])

        # Bus 1 at the top
        ax.set_ylim(len(group) - 0.5, -0.5)

        # Draw bus labels manually using data coordinates
        for i, bus in enumerate(group):
            ax.text(
                4.22,
                i,
                f"Bus {bus}",
                ha='left',
                va='center',
                fontsize=10,
                color='black',
                zorder=20,
                bbox=dict(
                    facecolor='white',
                    edgecolor='none',
                    alpha=0.85,
                    pad=1
                )
            )

        # Grid styling
        ax.set_axisbelow(True)

        ax.grid(
            axis='x',
            color='#E5E7EB',
            linewidth=0.6,
            alpha=0.25
        )

        ax.grid(
            axis = 'y',
            color = '#E5E7EB',
            linewidth = 0.6,
            alpha = 0.05
        )

        # Titles
        ax.set_xlabel('Time')
        ax.set_title('Improved bus plan')

        # Legend
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )

        # Figure margins
        fig.subplots_adjust(
            left=0.12,
            right=0.98,
            top=0.88,
            bottom=0.15
        )

        # Convert Matplotlib to interactive HTML
        html = mpld3.fig_to_html(fig)

        # Fullscreen functionality
        
        # Fullscreen functionality
        fullscreen_html = f"""
        <style>
            #gantt-container {{
                background: white;
                padding: 10px;
                width: 100%;
                height: 100%;
                box-sizing: border-box;
                position: relative;
                overflow: visible;
            }}

            #gantt-container:fullscreen {{
                background: white;
                width: 100vw;
                height: 100vh;
                overflow: auto;
            }}

            #gantt-container .mpld3-tooltip {{
                z-index: 999999 !important;
                pointer-events: none;
            }}

            #fullscreen-button {{
                padding: 7px 12px;
                margin-bottom: 10px;
                background: #EA3323;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}
        </style>

        <div id="gantt-container">

            <button id="fullscreen-button" onclick="toggleFullscreen()">
                ⛶ Fullscreen
            </button>

            <div id="gantt-chart">
                {html}
            </div>

        </div>

        <script>
        function toggleFullscreen() {{
            const container = document.getElementById("gantt-container");

            if (!document.fullscreenElement) {{
                container.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}

        // Move mpld3 tooltips into the fullscreen container
        function moveTooltips() {{
            const container = document.getElementById("gantt-container");

            document.querySelectorAll("body > .mpld3-tooltip").forEach(function(tooltip) {{
                container.appendChild(tooltip);
            }});
        }}

        // mpld3 creates its tooltip elements asynchronously
        const tooltipObserver = new MutationObserver(function() {{
            moveTooltips();
        }});

        tooltipObserver.observe(document.body, {{
            childList: true
        }});

        moveTooltips();
        </script>
        """


        # Display in Streamlit
        components.html(
            fullscreen_html,
            height=850,
            scrolling=False
        )

        plt.close(fig)
