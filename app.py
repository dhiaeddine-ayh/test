import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import numpy as np

class ECGComparerWebApp:
    def __init__(self):
        st.set_page_config(
            page_title="INNOVATION ACADEMY", 
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.setup_session_state()
        self.create_layout()

    def setup_session_state(self):
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'selected_signals' not in st.session_state:
            st.session_state.selected_signals = []
        if 'all_signals' not in st.session_state:
            st.session_state.all_signals = []
        if 'plot_colors' not in st.session_state:
            st.session_state.plot_colors = {
                'background': '#000000',
                'grid': '#E5E5E5',
                'default_colors': [
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
                ]
            }

    def create_layout(self):
        st.title("INNOVATION ACADEMY")
        
        # Create sidebar controls
        with st.sidebar:
            st.header("Controls")
            
            # Create tabs in sidebar
            tab_data, tab_appearance = st.tabs(["📊 Data", "🎨 Appearance"])
            
            with tab_data:
                uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
                
                if uploaded_file is not None:
                    self.load_csv(uploaded_file)
                    
                    if st.session_state.data is not None:
                        self.signal_selector()
                        
                    if st.button("Clear Plot"):
                        st.session_state.selected_signals = []
            
            with tab_appearance:
                st.subheader("Color Settings")
                st.session_state.plot_colors['background'] = st.color_picker(
                    "Background Color", 
                    st.session_state.plot_colors['background']
                )

        # Create tabs for Plot and Statistics
        tab1, tab2 = st.tabs(["📈 Plot View", "📊 Statistics View"])
        
        # Plot tab
        with tab1:
            if st.session_state.data is not None:
                self.display_plot()
        
        # Statistics tab
        with tab2:
            if st.session_state.data is not None and st.session_state.selected_signals:
                self.display_statistics()

    def load_csv(self, uploaded_file):
        try:
            st.session_state.data = pd.read_csv(uploaded_file)
            st.session_state.all_signals = list(range(len(st.session_state.data)))
            st.success("CSV file loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

    def signal_selector(self):
        # Show available classes
        unique_labels = st.session_state.data.iloc[:, -1].unique()
        if st.button("Show Available Classes"):
            st.write("Available Classes:", unique_labels)
        
        # Add class selector
        selected_class = st.selectbox(
            "Select class to plot",
            options=['All'] + list(unique_labels),
            index=0
        )
        
        # Add button to plot all signals from selected class
        if st.button("Plot Signals by Class"):
            if selected_class == 'All':
                st.session_state.selected_signals = st.session_state.all_signals
            else:
                # Get indices of signals from selected class
                class_indices = st.session_state.data[st.session_state.data.iloc[:, -1] == selected_class].index.tolist()
                st.session_state.selected_signals = class_indices
        
        # Add number input for random signal selection
        num_signals_to_plot = st.number_input(
            "Number of random signals to plot",
            min_value=1,
            max_value=len(st.session_state.all_signals),
            value=1
        )
        
        # Add button to plot random signals
        if st.button("Plot Random Signals"):
            # Randomly select the specified number of signals
            st.session_state.selected_signals = np.random.choice(
                st.session_state.all_signals,
                size=num_signals_to_plot,
                replace=False  # Ensures no signal is selected twice
            ).tolist()
        
        # Add button to plot all signals
        if st.button("Plot All Signals"):
            st.session_state.selected_signals = st.session_state.all_signals
        
        selected_signals = st.multiselect(
            "Select signals to compare",
            options=[f"Signal {i+1}" for i in st.session_state.all_signals],
            default=[f"Signal {i+1}" for i in st.session_state.selected_signals]
        )

        if selected_signals != [f"Signal {i+1}" for i in st.session_state.selected_signals]:
            st.session_state.selected_signals = [int(s.split()[1]) - 1 for s in selected_signals]

        if st.button("Switch Diagram"):
            st.session_state.selected_signals = []

    def display_plot(self):
        if not st.session_state.selected_signals:
            st.info("Please select a signal to plot.")
            return

        fig = go.Figure()
        
        default_colors = st.session_state.plot_colors['default_colors']
        colors = []
        for i in range(len(st.session_state.selected_signals)):
            colors.append(default_colors[i % len(default_colors)])
        
        line_styles = [
            dict(width=1.5),                     # solid
            dict(width=1.5, dash='dash'),        # dashed
            dict(width=1.5, dash='dot'),         # dotted
            dict(width=1.5, dash='dashdot'),     # dash-dot
            dict(width=1.5, dash='longdash'),    # long dash
        ]
        
        for idx, signal_idx in enumerate(st.session_state.selected_signals):
            signal_data = st.session_state.data.iloc[signal_idx, :-1].values
            label = st.session_state.data.iloc[signal_idx, -1]
            
            style_idx = idx % len(line_styles)
            
            fig.add_trace(go.Scatter(
                y=signal_data,
                name=f'Signal {signal_idx + 1} (Label: {label})',
                line=dict(color=colors[idx], **line_styles[style_idx])
            ))
        
        if len(st.session_state.selected_signals) > 1:
            title = 'Comparison: ' + ' vs '.join([f'Signal {s + 1}' for s in st.session_state.selected_signals])
        else:
            title = f'Signal {st.session_state.selected_signals[0] + 1}'
        
        fig.update_layout(
            title=title,
            xaxis_title=' ',
            yaxis_title='Signal Amplitude',
            showlegend=True,
            height=600,
            plot_bgcolor=st.session_state.plot_colors['background'],
            paper_bgcolor=st.session_state.plot_colors['background'],
            xaxis=dict(gridcolor=st.session_state.plot_colors['grid']),
            yaxis=dict(gridcolor=st.session_state.plot_colors['grid'])
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def display_statistics(self):
        st.header("Signal Statistics")
        
        # Create columns dynamically based on number of selected signals
        num_signals = len(st.session_state.selected_signals)
        
        # Store all statistics for download
        all_stats_data = {}
        
        # Display statistics for each signal
        for idx, signal_idx in enumerate(st.session_state.selected_signals):
            # Get signal data excluding the last column (label)
            signal_data = st.session_state.data.iloc[signal_idx, :-1].values
            
            st.subheader(f"Statistics for Signal {signal_idx + 1}")
            
            # Basic statistics
            stats = {
                "Mean": signal_data.mean(),
                "Median": np.median(signal_data),
                "Std Dev": signal_data.std(),
                "Min": signal_data.min(),
                "Max": signal_data.max(),
                "Range": signal_data.max() - signal_data.min(),
                "Skewness": pd.Series(signal_data).skew(),
                "Kurtosis": pd.Series(signal_data).kurtosis(),
            }
            
            # Store statistics for this signal
            signal_key = f"Signal {signal_idx + 1}"
            all_stats_data[signal_key] = stats
            
            # Create a DataFrame for better formatting
            stats_df = pd.DataFrame(
                stats.items(),
                columns=['Metric', 'Value']
            )
            stats_df['Value'] = stats_df['Value'].round(4)
            st.dataframe(stats_df, hide_index=True)
            
            # Add download button for individual signal statistics
            csv = stats_df.to_csv(index=False)
            st.download_button(
                label=f"Download Signal {signal_idx + 1} Statistics",
                data=csv,
                file_name=f'signal_{signal_idx + 1}_statistics.csv',
                mime='text/csv',
            )
            
            # Additional statistical visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribution Plot")
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=signal_data,
                    nbinsx=50,
                    name=f"Signal {signal_idx + 1}"
                ))
                fig.update_layout(
                    title=f"Distribution of Signal {signal_idx + 1}",
                    xaxis_title="Value",
                    yaxis_title="Frequency",
                    showlegend=True,
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Box Plot")
                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=signal_data,
                    name=f"Signal {signal_idx + 1}"
                ))
                fig.update_layout(
                    title=f"Box Plot of Signal {signal_idx + 1}",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()  # Add a visual separator between signals
        
        # Add correlation analysis for pairs of signals
        if num_signals > 1:
            st.header("Correlation Analysis")
            
            # Create correlation matrix
            correlation_matrix = np.zeros((num_signals, num_signals))
            for i in range(num_signals):
                for j in range(num_signals):
                    signal1 = st.session_state.data.iloc[st.session_state.selected_signals[i], :-1].values
                    signal2 = st.session_state.data.iloc[st.session_state.selected_signals[j], :-1].values
                    correlation_matrix[i, j] = np.corrcoef(signal1, signal2)[0, 1]
            
            # Display correlation matrix
            correlation_df = pd.DataFrame(
                correlation_matrix,
                columns=[f"Signal {s + 1}" for s in st.session_state.selected_signals],
                index=[f"Signal {s + 1}" for s in st.session_state.selected_signals]
            )
            st.write("Correlation Matrix:")
            st.dataframe(correlation_df)
            
            # Add correlation to statistics
            all_stats_data['Correlation Matrix'] = correlation_df.to_dict()
        
        # Add download button for all statistics
        st.header("Download All Statistics")
        
        # Convert all statistics to DataFrame
        all_stats_df = pd.DataFrame()
        for signal_name, stats in all_stats_data.items():
            if signal_name != 'Correlation Matrix':
                temp_df = pd.DataFrame(stats.items(), columns=['Metric', signal_name])
                if all_stats_df.empty:
                    all_stats_df = temp_df
                else:
                    all_stats_df = all_stats_df.merge(
                        temp_df, 
                        on='Metric', 
                        how='outer'
                    )
        
        # Create download buttons
        csv_all = all_stats_df.to_csv(index=False)
        st.download_button(
            label="Download All Statistics (CSV)",
            data=csv_all,
            file_name='all_statistics.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    app = ECGComparerWebApp()
