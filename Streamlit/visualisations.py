from calculations import convert_time_to_timedelta
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import mpld3
from mpld3 import plugins
import streamlit.components.v1 as components
from html import escape

def gantt_chart_bus(bp, title = 'improved bus plan', selected_buses=None):
    """Creates interactive Gantt charts of the bus planning."""
    if selected_buses is not None:
        bp = bp[bp['bus'].isin(selected_buses)]
    if bp.empty:
        st.info("Select at least one bus to display the Gantt chart.")
        return
    # Prepare planning
    planning = bp.sort_values(['bus', 'start time']).copy()
    planning['bus'] = planning['bus'].astype(int)
    start_times = convert_time_to_timedelta(planning['start time'])
    end_times = convert_time_to_timedelta(planning['end time'])
    if start_times.isna().any() or end_times.isna().any():
        st.error('Invalid start or end time in bus planning.')
        return
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
    for group_index, group in enumerate(groups):
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
                color=colors.get(activity, 'lightgrey'),
                edgecolor='#000000',
                linewidth=1,
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
        # Invisible hover points
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
        hours = list(range(5, 30))
        ax.set_xlim(4.2, 29)
        ax.set_xticks(hours)
        # Hide automatically generated time labels
        ax.set_xticklabels([])
        ax.tick_params(
            axis='x',
            which='both',
            labeltop=False,
            labelbottom=False,
            length=0
        )
        # Custom time labels
        for hour in hours:
            ax.text(
                hour,
                -1.15,
                f'{hour % 24:02d}:00',
                ha='center',
                va='center',
                fontsize=15,
                fontweight='bold',
                color='#333333',
                clip_on=False
            )
        # Y-axis
        ax.set_yticks(range(len(group)))
        ax.set_yticklabels([])
        # Bus 1 at the top
        ax.set_ylim(len(group) - 0.5, -1.5)
        # Draw bus labels manually
        for i, bus in enumerate(group):
            ax.text(
                4.22,
                i,
                f"Bus {bus}",
                ha='left',
                va='center',
                fontsize=15,
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
            axis='y',
            color='#E5E7EB',
            linewidth=0.6,
            alpha=0.05
        )
        # Titles
        ax.set_xlabel('Time',
                      fontsize = 25,
                      fontweight = 'bold',
                      color = '#333333')
        # Titles
        ax.set_title(
            title,
            fontsize=26,           # Lettergrootte
            fontweight='bold',     # Vetgedrukt
            color='#333333'        # Tekstkleur
        )
        # Legend
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )
        # Figure margins
        fig.subplots_adjust(
            left=0.01,
            right=0.99,
            top=0.96,
            bottom=0.15
        )
        # Convert Matplotlib to interactive HTML
        html = mpld3.fig_to_html(fig)
        # Unique IDs for each chart
        container_id = f"gantt-container-{group_index}"
        chart_id = f"gantt-chart-{group_index}"
        button_id = f"fullscreen-button-{group_index}"
        # Fullscreen functionality and responsive scaling
        fullscreen_html = f"""
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }}
            #{container_id} {{
                background: white;
                padding: 10px;
                width: 100%;
                box-sizing: border-box;
                position: relative;
                overflow: hidden;
            }}
            #{chart_id} {{
                width: 100%;
                position: relative;
                overflow: hidden;
            }}
            #{chart_id} svg {{
                display: block;
                transform-origin: top left;
            }}
            /* Fullscreen styling */
            #{container_id}:fullscreen {{
                background: white;
                width: 100vw;
                height: 100vh;
                overflow: auto;
            }}
            #{container_id}:fullscreen #{chart_id} {{
                overflow: visible;
            }}
            /* Hide automatic x-axis labels */
            #{chart_id} .mpld3-xaxis .tick text,
            #{chart_id} .mpld3-xaxis text {{
                display: none !important;
            }}
            /* Tooltip styling */
            #{container_id} .mpld3-tooltip {{
                background-color: #F3F4F6 !important;
                color: #222222 !important;
                border: 2px solid #555555 !important;
                border-radius: 8px !important;
                padding: 10px 14px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                z-index: 999999 !important;
                pointer-events: none;
            }}
            /* Fullscreen button */
            #{button_id} {{
                padding: 7px 12px;
                margin-bottom: 10px;
                background: #EA3323;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }}
        </style>
        <div id="{container_id}">
            <button
                id="{button_id}"
                onclick="toggleFullscreen_{group_index}()"
            >
                ⛶ Fullscreen
            </button>
            <div id="{chart_id}">
                {html}
            </div>
        </div>
        <script>
        (function() {{
            const container = document.getElementById(
                "{container_id}"
            );
            const chart = document.getElementById(
                "{chart_id}"
            );
            const button = document.getElementById(
                "{button_id}"
            );
            let originalWidth = null;
            let originalHeight = null;
            function resizeGantt() {{
                const svg = chart.querySelector("svg");
                if (!svg) return;
                // Store original SVG dimensions
                if (originalWidth === null) {{
                    originalWidth = parseFloat(
                        svg.getAttribute("width")
                    );
                    originalHeight = parseFloat(
                        svg.getAttribute("height")
                    );
                }}
                if (!originalWidth || !originalHeight) return;
                const isFullscreen =
                    document.fullscreenElement === container;
                const availableWidth =
                    container.clientWidth - 20;
                const scale = isFullscreen
                    ? 1
                    : Math.min(
                        1,
                        availableWidth / originalWidth
                    );
                // Scale SVG
                svg.style.transform =
                    `scale(${{scale}})`;
                // Adjust wrapper dimensions
                chart.style.height =
                    `${{originalHeight * scale}}px`;
                chart.style.width = isFullscreen
                    ? `${{originalWidth}}px`
                    : "100%";
                // Update container height
                if (!isFullscreen) {{
                    container.style.height =
                        `${{originalHeight * scale + button.offsetHeight + 30}}px`;
                }} else {{
                    container.style.height = "100vh";
                }}
            }}
            // Fullscreen functionality
            button.addEventListener("click", function() {{
                if (!document.fullscreenElement) {{
                    container.requestFullscreen();
                }} else {{
                    document.exitFullscreen();
                }}
            }});
            // Resize when fullscreen changes
            document.addEventListener(
                "fullscreenchange",
                resizeGantt
            );
            // Resize when browser size changes
            window.addEventListener(
                "resize",
                resizeGantt
            );
            // Wait until mpld3 has created the SVG
            const resizeObserver = new MutationObserver(
                function() {{
                    if (chart.querySelector("svg")) {{
                        resizeGantt();
                        resizeObserver.disconnect();
                    }}
                }}
            );
            resizeObserver.observe(chart, {{
                childList: true,
                subtree: true
            }});
            // Move tooltips into fullscreen container
            function moveTooltips() {{
                document.querySelectorAll(
                    "body > .mpld3-tooltip"
                ).forEach(function(tooltip) {{
                    container.appendChild(tooltip);
                }});
            }}
            const tooltipObserver = new MutationObserver(
                moveTooltips
            );
            tooltipObserver.observe(document.body, {{
                childList: true
            }});
            // Initial sizing
            resizeGantt();
            moveTooltips();
        }})();
        </script>
        """
        # Display in Streamlit
        components.html(
            fullscreen_html,
            height=850,
            scrolling=False
        )
        plt.close(fig)