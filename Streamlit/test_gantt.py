
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins
from html import escape
from pathlib import Path
import webbrowser

# Example bus planning
planning = [
    (1, 5.0, 7.0, "service trip", "Station", "Airport"),
    (1, 7.0, 8.0, "idle", "Airport", "Airport"),
    (1, 8.0, 10.0, "charging", "Airport", "Airport"),
    (2, 6.0, 9.0, "service trip", "Depot", "Station"),
    (2, 9.0, 11.0, "material trip", "Station", "Depot"),
    (3, 5.5, 8.0, "service trip", "Depot", "Airport"),
    (3, 8.0, 9.5, "idle", "Airport", "Airport"),
]

colors = {
    "service trip": "skyblue",
    "material trip": "orange",
    "idle": "lightgrey",
    "charging": "yellowgreen"
}


def format_time(hour):
    hours = int(hour)
    minutes = round((hour - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"


# Create figure
fig, ax = plt.subplots(figsize=(12, 5))

used_activities = set()

hover_x = []
hover_y = []
hover_labels = []

for bus, start, end, activity, location_start, location_end in planning:

    label = activity if activity not in used_activities else None
    used_activities.add(activity)

    ax.barh(
        bus,
        end - start,
        left=start,
        height=0.6,
        color=colors[activity],
        edgecolor="grey",
        label=label
    )

    # Hover point in the middle of each bar
    hover_x.append((start + end) / 2)
    hover_y.append(bus)

    hover_labels.append(
        f"<b>Start location:</b> {escape(location_start)}<br>"
        f"<b>End location:</b> {escape(location_end)}<br>"
        f"<b>Start time:</b> {format_time(start)}<br>"
        f"<b>End time:</b> {format_time(end)}"
    )


# Invisible hover points
points = ax.scatter(
    hover_x,
    hover_y,
    s=2500,              # Veel groter hover-oppervlak
    color="red",         # Tijdelijk zichtbaar
    alpha=0.6,           # Half transparant
    edgecolors="black",
    linewidths=1,
    zorder=10             # Punten boven de balken
)

# Built-in mpld3 tooltip
tooltip = plugins.PointHTMLTooltip(
    points,
    labels=hover_labels,
    hoffset=10,
    voffset=10
)

plugins.connect(fig, tooltip)

# Chart styling
ax.set_yticks([1, 2, 3])
ax.set_yticklabels(["Bus 1", "Bus 2", "Bus 3"])
ax.invert_yaxis()

ax.set_xlim(5, 12)
ax.set_xticks(range(5, 13))
ax.set_xticklabels([f"{h:02d}:00" for h in range(5, 13)])
ax.xaxis.tick_top()

ax.set_title("Interactive Bus Gantt Chart")
ax.set_xlabel("Time")
ax.grid(axis="x", alpha=0.3)
ax.set_axisbelow(True)

ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, -0.2),
    ncol=4
)

plt.tight_layout()

# Save and open HTML
html_path = Path(__file__).resolve().parent / "gantt_test.html"

mpld3.save_html(fig, str(html_path))
plt.close(fig)

webbrowser.open(html_path.as_uri() + "?v=2")

print(f"Chart saved to: {html_path}")
