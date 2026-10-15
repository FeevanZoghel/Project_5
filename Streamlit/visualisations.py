import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def gantt_chart_bus(bp, selected_buses=None):
    """Creates an interactive Gantt chart with hover information."""

    if selected_buses is not None:
        bp = bp[bp['bus'].isin(selected_buses)]

    if bp.empty:
        st.info("Select at least one bus to display the Gantt chart.")
        return

    planning = bp.copy()

    # Convert times to hours
    planning['start_hour'] = pd.to_timedelta(
        planning['start time'].astype(str)
    ).dt.total_seconds() / 3600

    planning['end_hour'] = pd.to_timedelta(
        planning['end time'].astype(str)
    ).dt.total_seconds() / 3600

    # Handle activities after midnight
    planning.loc[planning['start_hour'] < 5, 'start_hour'] += 24
    planning.loc[planning['end_hour'] < 5, 'end_hour'] += 24

    # Handle activities crossing midnight
    planning.loc[
        planning['end_hour'] < planning['start_hour'],
        'end_hour'
    ] += 24

    colors = {
        'service trip': 'skyblue',
        'material trip': 'orange',
        'idle': 'lightgrey',
        'charging': 'yellowgreen'
    }

    buses = sorted(planning['bus'].unique())

    # Maximum 20 buses per chart
    groups = [
        buses[i:i + 20]
        for i in range(0, len(buses), 20)
    ]

    for group in groups:
        fig = go.Figure()
        group_planning = planning[planning['bus'].isin(group)]

        for activity, color in colors.items():
            activity_data = group_planning[
                group_planning['activity'] == activity
            ]

            if activity_data.empty:
                continue

            hover_text = []
            labels = []

            for _, row in activity_data.iterrows():
                start = row['start_hour']
                end = row['end_hour']

                start_time = f"{int(start % 24):02d}:{int((start % 1) * 60):02d}"
                end_time = f"{int(end % 24):02d}:{int((end % 1) * 60):02d}"

                line = row['line']

                hover = (
                    f"<b>Bus {row['bus']}</b><br>"
                    f"Activity: {activity}<br>"
                    f"Start: {start_time}<br>"
                    f"End: {end_time}<br>"
                    f"From: {row['start location']}<br>"
                    f"To: {row['end location']}<br>"
                    f"Energy: {row['energy consumption']:.2f} kWh"
                )

                if activity == 'service trip' and pd.notna(line):
                    hover += f"<br>Line: {int(line)}"
                    labels.append(str(int(line)))
                else:
                    labels.append("")

                hover_text.append(hover)

            fig.add_trace(
                go.Bar(
                    x=(
                        activity_data['end_hour']
                        - activity_data['start_hour']
                    ),
                    y=activity_data['bus'].astype(str),
                    base=activity_data['start_hour'],
                    orientation='h',
                    name=activity,
                    marker=dict(
                        color=color,
                        line=dict(color='grey', width=0.5)
                    ),
                    text=labels,
                    textposition='inside',
                    textfont=dict(size=9, color='black'),
                    hovertext=hover_text,
                    hoverinfo='text',
                    width=0.8
                )
            )

        fig.update_layout(
            title=dict(
                text="Improved bus plan",
                x=0.5,
                font=dict(size=14)
            ),
            barmode='overlay',
            height=max(450, len(group) * 35 + 130),
            margin=dict(l=50, r=20, t=70, b=60),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='black'),
            legend=dict(
                orientation='h',
                y=-0.15,
                x=0.5,
                xanchor='center'
            ),
            hoverlabel=dict(
                bgcolor='white',
                font_size=13,
                font_color='black'
            )
        )

        fig.update_xaxes(
            range=[5, 29],
            tickmode='array',
            tickvals=list(range(5, 30)),
            ticktext=[
                f"{hour % 24:02d}:00"
                for hour in range(5, 30)
            ],
            side='top',
            showgrid=True,
            gridcolor='#E5E7EB',
            title='Time'
        )

        fig.update_yaxes(
            title='Bus',
            categoryorder='array',
            categoryarray=[
                str(bus) for bus in reversed(group)
            ],
            autorange='reversed'
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={'displayModeBar': False}
        )