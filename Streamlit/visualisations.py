import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import mpld3

from mpld3 import plugins
from html import escape


class BarHoverTooltip(plugins.PluginBase):
    """Tooltip for Matplotlib bar patches in mpld3."""

    JAVASCRIPT = """
    mpld3.register_plugin("barhovertooltip", BarHoverTooltip);

    BarHoverTooltip.prototype = Object.create(mpld3.Plugin.prototype);
    BarHoverTooltip.prototype.constructor = BarHoverTooltip;
    BarHoverTooltip.prototype.requiredProps = ["ids", "labels"];

    function BarHoverTooltip(fig, props) {
        mpld3.Plugin.call(this, fig, props);
    }

    BarHoverTooltip.prototype.draw = function() {
        var fig = this.fig;
        var props = this.props;

        var tooltip = d3.select(fig.canvas)
            .append("div")
            .attr("class", "bar-hover-tooltip")
            .style("position", "absolute")
            .style("visibility", "hidden")
            .style("pointer-events", "none")
            .style("background", "white")
            .style("color", "#222")
            .style("border", "1px solid #999")
            .style("border-radius", "6px")
            .style("padding", "10px")
            .style("font-size", "12px")
            .style("box-shadow", "0 2px 8px rgba(0,0,0,0.15)")
            .style("z-index", "1000");

        props.ids.forEach(function(id, index) {
            var element = mpld3.get_element(id, fig);

            if (!element) {
                return;
            }

            var label = props.labels[index];

            element.elements()
                .on("mouseover.barhover", function() {
                    tooltip
                        .html(label)
                        .style("visibility", "visible");
                })
                .on("mousemove.barhover", function() {
                    var mouse = d3.mouse(fig.canvas);

                    tooltip
                        .style("left", (mouse[0] + 15) + "px")
                        .style("top", (mouse[1] + 15) + "px");
                })
                .on("mouseout.barhover", function() {
                    tooltip.style("visibility", "hidden");
                });
        });
    };
    """

    def __init__(self, bars, labels):
        self.dict_ = {
            "type": "barhovertooltip",
            "ids": [mpld3.utils.get_id(bar) for bar in bars],
            "labels": labels
        }


def gantt_chart_bus(bp, selected_buses=None):
    """Creates interactive Matplotlib Gantt charts."""

    if selected_buses is not None:
        bp = bp[bp['bus'].isin(selected_buses)]

    if bp.empty:
        st.info("Select at least one bus to display the Gantt chart.")
        return

    planning = bp.sort_values(['bus', 'start time']).copy()

    start_times = pd.to_timedelta(
        planning['start time'].astype(str)
    )

    end_times = pd.to_timedelta(
        planning['end time'].astype(str)
    )

    planning['start_hour'] = start_times.dt.total_seconds() / 3600
    planning['end_hour'] = end_times.dt.total_seconds() / 3600

    planning.loc[
        planning['start_hour'] < 5, 'start_hour'
    ] += 24

    planning.loc[
        planning['end_hour'] <= 5, 'end_hour'
    ] += 24

    colors = {
        'service trip': 'skyblue',
        'material trip': 'orange',
        'idle': 'lightgrey',
        'charging': 'yellowgreen'
    }

    buses = sorted(planning['bus'].unique())

    groups = [
        buses[i:i + 20]
        for i in range(0, len(buses), 20)
    ]

    for group in groups:

        fig, ax = plt.subplots(figsize=(18, 8))

        group_planning = planning[
            planning['bus'].isin(group)
        ]

        bus_positions = {
            bus: i for i, bus in enumerate(group)
        }

        activities_in_legend = []

        tooltip_bars = []
        tooltip_labels = []

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

            bars = ax.barh(
                y,
                duration,
                left=start,
                height=0.8,
                color=colors[activity],
                edgecolor='grey',
                linewidth=1,
                label=label
            )

            bar = bars[0]

            # Tooltip: only locations and times
            tooltip_text = (
                f"<b>Start location:</b> "
                f"{escape(str(trip['start location']))}<br>"
                f"<b>End location:</b> "
                f"{escape(str(trip['end location']))}<br>"
                f"<b>Start time:</b> "
                f"{escape(str(trip['start time']))}<br>"
                f"<b>End time:</b> "
                f"{escape(str(trip['end time']))}"
            )

            tooltip_bars.append(bar)
            tooltip_labels.append(tooltip_text)

            # Line numbers inside service trips
            if (
                activity == 'service trip'
                and pd.notna(trip['line'])
            ):
                line = trip['line']

                ax.text(
                    start + duration / 2,
                    y,
                    f'{int(line)}',
                    ha='center',
                    va='center',
                    fontsize=8
                )

        # Time axis
        hours = range(5, 30)

        ax.set_xlim(5, 29)
        ax.set_xticks(hours)

        ax.set_xticklabels([
            f'{hour % 24:02d}:00'
            for hour in hours
        ])

        # Bus axis
        ax.set_yticks(range(len(group)))

        ax.set_yticklabels([
            f'Bus {bus}'
            for bus in group
        ])

        ax.invert_yaxis()

        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')

        ax.grid(
            axis='x',
            linestyle='-',
            alpha=0.4
        )

        ax.set_axisbelow(True)

        ax.set_xlabel('Time')
        ax.set_ylabel('Bus')
        ax.set_title('Improved bus plan')

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )

        # Add hover tooltips
        plugins.connect(
            fig,
            BarHoverTooltip(
                tooltip_bars,
                tooltip_labels
            )
        )

        plt.tight_layout()

        # Convert Matplotlib chart to interactive HTML
        html = mpld3.fig_to_html(fig)

        # Display in Streamlit
        components.html(
            html,
            height=650,
            scrolling=True
        )

        plt.close(fig)