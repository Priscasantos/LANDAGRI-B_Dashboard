# Temporal density chart
st.subheader("🌊 Temporal Density of LULC Initiatives")

if meta:  # Create density data using metadata
    density_data = []
    all_years = set()

    for nome, meta_item in meta.items():
        # Ensure the initiative is in the filtered_df before processing
        if nome in filtered_df["Name"].values:
            if "available_years" in meta_item and meta_item["available_years"]:
                for ano in meta_item["available_years"]:
                    density_data.append({"nome": nome, "ano": ano})
                    all_years.add(ano)

    if density_data:
        density_df = pd.DataFrame(density_data)
        year_counts = density_df["ano"].value_counts().sort_index()

        # Density chart by year (discrete bars)
        fig_density_line = go.Figure()
        fig_density_line.add_trace(
            go.Bar(
                x=year_counts.index,
                y=year_counts.values,
                name="Active Initiatives",
                marker=dict(
                    color="rgba(0,150,136,0.8)",
                    line=dict(color="rgba(0,150,136,1)", width=1),
                ),
                hovertemplate="<b>Year: %{x}</b><br>"
                + "Active Initiatives: %{y}<extra></extra>",
            )
        )

        fig_density_line.update_layout(
            title="📊 Temporal Density: Number of Initiatives per Year",
            xaxis_title="Year",
            yaxis_title="Number of Active Initiatives",
            height=450,
            hovermode="x unified",
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.2)",
                tickmode="linear",
                dtick=2,
            ),
            yaxis=dict(
                showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)"
            ),
        )
        st.plotly_chart(fig_density_line, use_container_width=True)

        # Enhanced temporal metrics - Modern cards
        st.markdown("#### 📈 Temporal Metrics")

        # CSS for temporal metrics
        st.markdown(
            """
        <style>
        .temporal-metric {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .temporal-metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.3rem 0;
        }
        .temporal-metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .temporal-metric-delta {
            font-size: 0.8rem;
            opacity: 0.8;
            margin-top: 0.2rem;
        }
        .timeline-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Calculate and display temporal metrics
        if all_years:  # Ensure all_years is not empty
            first_year = min(all_years) if all_years else "N/A"
            last_year = max(all_years) if all_years else "N/A"
            peak_activity_year = (
                year_counts.idxmax() if not year_counts.empty else "N/A"
            )
            avg_initiatives_per_year = (
                year_counts.mean() if not year_counts.empty else 0
            )

            tm_col1, tm_col2, tm_col3, tm_col4 = st.columns(4)
            with tm_col1:
                st.markdown(
                    f"""<div class="temporal-metric">
                                    <div class="temporal-metric-value">🗓️ {first_year}</div>
                                    <div class="temporal-metric-label">First Year Covered</div>
                                </div>""",
                    unsafe_allow_html=True,
                )
            with tm_col2:
                st.markdown(
                    f"""<div class="temporal-metric">
                                    <div class="temporal-metric-value">🗓️ {last_year}</div>
                                    <div class="temporal-metric-label">Last Year Covered</div>
                                </div>""",
                    unsafe_allow_html=True,
                )
            with tm_col3:
                st.markdown(
                    f"""<div class="temporal-metric">
                                    <div class="temporal-metric-value">🚀 {peak_activity_year}</div>
                                    <div class="temporal-metric-label">Peak Activity Year</div>
                                </div>""",
                    unsafe_allow_html=True,
                )
            with tm_col4:
                st.markdown(
                    f"""<div class="temporal-metric">
                                    <div class="temporal-metric-value">📊 {avg_initiatives_per_year:.1f}</div>
                                    <div class="temporal-metric-label">Avg. Initiatives/Year</div>
                                </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                "ℹ️ Temporal metrics cannot be calculated as no year data is available from the filtered initiatives' metadata."
            )
    else:
        st.info(
            "ℹ️ No temporal density data to display based on current filters and available metadata."
        )


if __name__ == "__main__":
    run()
