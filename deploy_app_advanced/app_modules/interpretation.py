import html

import pandas as pd
import streamlit as st


def render_interpretation_insights(interpretation_df: pd.DataFrame) -> None:
    baseline_row = interpretation_df.iloc[0]
    scenario_rows = interpretation_df.iloc[1:]

    st.caption("Compare your baseline against targeted lifestyle changes.")

    metric_columns = st.columns(3)

    with metric_columns[0]:
        st.markdown(
            (
                '<div class="interp-card">'
                '<div class="interp-card-title">Current baseline</div>'
                f'<div class="interp-card-value">{baseline_row["Predicted Vitamin D (ng/mL)"]:.2f} ng/mL</div>'
                '<div class="interp-card-delta">0.00 ng/mL</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    for idx, (_, row) in enumerate(scenario_rows.iterrows(), start=1):
        delta_value = float(row["Change vs Baseline (ng/mL)"])
        delta_label = f"{delta_value:+.2f} ng/mL"
        scenario_title = html.escape(row["Scenario"].replace("If ", ""))
        with metric_columns[idx]:
            st.markdown(
                (
                    '<div class="interp-card">'
                    f'<div class="interp-card-title">{scenario_title}</div>'
                    f'<div class="interp-card-value">{row["Predicted Vitamin D (ng/mL)"]:.2f} ng/mL</div>'
                    f'<div class="interp-card-delta">{delta_label}</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

    best_row = scenario_rows.sort_values("Predicted Vitamin D (ng/mL)", ascending=False).iloc[0]
    best_delta = float(best_row["Change vs Baseline (ng/mL)"])
    st.success(
        f"Most impactful scenario: {best_row['Scenario']} -> {best_row['Predicted Vitamin D (ng/mL)']:.2f} ng/mL "
        f"({best_delta:+.2f} vs baseline)."
    )

    with st.popover("See detailed scenario inputs"):
        st.caption("Detailed scenario table")
        st.dataframe(interpretation_df, use_container_width=True, hide_index=True)
