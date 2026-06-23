"""
Chart Builder - Creates interactive Plotly charts for the dashboard.

Provides methods for creating various financial visualizations including
pie charts, line charts, bar charts, and treemaps for expense analysis.
All charts are dark-mode friendly with consistent styling.
"""

import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Dark theme colors for charts
CHART_COLORS = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#96CEB4",
    "#FFEAA7",
    "#DDA0DD",
    "#98D8C8",
    "#F7DC6F",
    "#BB8FCE",
    "#85C1E9",
    "#F0B27A",
    "#82E0AA",
]

DARK_BG = "#1E1E2E"
DARK_PAPER = "#282840"
TEXT_COLOR = "#E0E0E0"


class ChartBuilder:
    """
    Builder for creating interactive Plotly charts with consistent dark styling.

    Provides methods for:
        - Category spending pie chart
        - Monthly spending line chart
        - Income vs Expense bar chart
        - Top spending categories chart
    """

    @staticmethod
    def _apply_dark_theme(fig: go.Figure) -> go.Figure:
        """
        Apply dark theme styling to a plotly figure.

        Args:
            fig: Plotly figure to style

        Returns:
            Styled figure
        """
        fig.update_layout(
            paper_bgcolor=DARK_PAPER,
            plot_bgcolor=DARK_BG,
            font=dict(color=TEXT_COLOR, family="Arial, sans-serif"),
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(
                font=dict(color=TEXT_COLOR),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        return fig

    @staticmethod
    def create_category_pie_chart(
        category_data: dict, title: str = "Spending by Category"
    ) -> go.Figure:
        """
        Create a pie chart showing spending distribution across categories.

        Args:
            category_data: Dict mapping category names to amounts
            title: Chart title

        Returns:
            Plotly pie chart figure
        """
        if not category_data:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False)
            return ChartBuilder._apply_dark_theme(fig)

        labels = list(category_data.keys())
        values = list(category_data.values())

        fig = px.pie(
            values=values,
            names=labels,
            title=title,
            color_discrete_sequence=CHART_COLORS,
            hole=0.4,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percent: %{percent}",
        )

        fig = ChartBuilder._apply_dark_theme(fig)
        fig.update_layout(
            title=dict(font=dict(size=18, color=TEXT_COLOR)),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )

        return fig

    @staticmethod
    def create_monthly_spending_chart(
        monthly_data: pd.DataFrame, title: str = "Monthly Spending Trend"
    ) -> go.Figure:
        """
        Create a line chart showing monthly spending trends.

        Args:
            monthly_data: DataFrame with 'month' and 'total' columns
            title: Chart title

        Returns:
            Plotly line chart figure
        """
        if monthly_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False)
            return ChartBuilder._apply_dark_theme(fig)

        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        monthly_data["month_name"] = monthly_data["month"].map(month_names)

        fig = px.line(
            monthly_data,
            x="month_name",
            y="total",
            title=title,
            markers=True,
        )

        fig.update_traces(
            line=dict(color="#4ECDC4", width=3),
            marker=dict(size=8, color="#45B7D1"),
            hovertemplate="<b>%{x}</b><br>Spent: ₹%{y:,.2f}<br>",
        )

        fig = ChartBuilder._apply_dark_theme(fig)
        fig.update_layout(
            title=dict(font=dict(size=18, color=TEXT_COLOR)),
            xaxis=dict(title="Month", gridcolor="#333"),
            yaxis=dict(title="Amount (₹)", gridcolor="#333"),
        )

        # Add filled area under the line
        fig.update_traces(fill="tozeroy", fillcolor="rgba(78, 205, 196, 0.1)")

        return fig

    @staticmethod
    def create_income_vs_expense_chart(
        expense_data: pd.DataFrame,
        income_data: pd.DataFrame,
        title: str = "Income vs Expenses",
    ) -> go.Figure:
        """
        Create a grouped bar chart comparing income and expenses by month.

        Args:
            expense_data: DataFrame with monthly expense data
            income_data: DataFrame with monthly income data
            title: Chart title

        Returns:
            Plotly bar chart figure
        """
        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        # Merge expense and income data
        if expense_data.empty and income_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False)
            return ChartBuilder._apply_dark_theme(fig)

        fig = go.Figure()

        if not expense_data.empty:
            expense_data["month_name"] = expense_data["month"].map(month_names)
            fig.add_trace(
                go.Bar(
                    name="Expenses",
                    x=expense_data["month_name"],
                    y=expense_data["total"],
                    marker_color="#FF6B6B",
                    hovertemplate="<b>%{x}</b><br>Expenses: ₹%{y:,.2f}<br>",
                )
            )

        if not income_data.empty:
            income_data["month_name"] = income_data["month"].map(month_names)
            fig.add_trace(
                go.Bar(
                    name="Income",
                    x=income_data["month_name"],
                    y=income_data["total"],
                    marker_color="#4ECDC4",
                    hovertemplate="<b>%{x}</b><br>Income: ₹%{y:,.2f}<br>",
                )
            )

        fig.update_layout(
            title=title,
            barmode="group",
            xaxis=dict(title="Month", gridcolor="#333"),
            yaxis=dict(title="Amount (₹)", gridcolor="#333"),
        )

        fig = ChartBuilder._apply_dark_theme(fig)
        fig.update_layout(
            title=dict(font=dict(size=18, color=TEXT_COLOR)),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        return fig

    @staticmethod
    def create_top_categories_chart(
        category_totals: list[tuple[str, float]], title: str = "Top Spending Categories"
    ) -> go.Figure:
        """
        Create a horizontal bar chart of top spending categories.

        Args:
            category_totals: List of (category, amount) tuples sorted by amount
            title: Chart title

        Returns:
            Plotly horizontal bar chart figure
        """
        if not category_totals:
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False)
            return ChartBuilder._apply_dark_theme(fig)

        categories = [c[0] for c in category_totals]
        amounts = [c[1] for c in category_totals]

        # Reverse for horizontal bar (top at top)
        categories.reverse()
        amounts.reverse()

        colors = CHART_COLORS[: len(categories)]
        colors.reverse()

        fig = go.Figure(
            go.Bar(
                x=amounts,
                y=categories,
                orientation="h",
                marker_color=colors,
                hovertemplate="<b>%{y}</b><br>Total: ₹%{x:,.2f}<br>",
            )
        )

        fig.update_layout(
            title=title,
            xaxis=dict(title="Amount (₹)", gridcolor="#333"),
            yaxis=dict(title="", autorange="reversed"),
        )

        fig = ChartBuilder._apply_dark_theme(fig)
        fig.update_layout(
            title=dict(font=dict(size=18, color=TEXT_COLOR)),
            height=max(300, len(categories) * 60),
        )

        return fig

    @staticmethod
    def create_payment_method_chart(expense_df: pd.DataFrame) -> go.Figure:
        """
        Create a pie chart showing payment method distribution.

        Args:
            expense_df: DataFrame with expense data including payment_method

        Returns:
            Plotly pie chart figure
        """
        if expense_df.empty or "payment_method" not in expense_df.columns:
            fig = go.Figure()
            fig.add_annotation(text="No payment data", showarrow=False)
            return ChartBuilder._apply_dark_theme(fig)

        method_data = expense_df.groupby("payment_method")["amount"].sum().reset_index()

        fig = px.pie(
            values=method_data["amount"],
            names=method_data["payment_method"],
            title="Payment Methods",
            color_discrete_sequence=CHART_COLORS,
            hole=0.4,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>",
        )

        fig = ChartBuilder._apply_dark_theme(fig)
        fig.update_layout(
            title=dict(font=dict(size=16, color=TEXT_COLOR)),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )

        return fig
