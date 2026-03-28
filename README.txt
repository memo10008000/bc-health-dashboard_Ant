Team Members:
	Shweta Nagdev
	Guillermo Granillo

Challenge Track:
	Public Health Equity & Healthcare Analytics Data-Driven Governance, Health Tech, and Crisis Intervention.

Problem Statement
	Population health analysts, healthcare executives, and government policymakers currently struggle with fragmented, static data sources when identifying regions that require immediate intervention. Critical metrics—such as primary care access gaps, systemic surgical wait times, and acute public health emergencies (like the opioid crisis) are often siloed across different reporting structures. To achieve true health equity, decision-makers require a unified environmental control center that seamlessly connects localized socioeconomic vulnerability with overarching provincial health system pressures to instantly guide resource allocation.

Solution Summary
	We developed the Provincial Health Control Center, a dynamic, multi-tab dashboard designed for real-time executive decision-making.

	The Synthesis Engine (Tab 1): Ingests Community Health Service Area (CHSA) data and calculates a live "Vulnerability Index" based on primary care gaps, ER pressure, opioid rates, and median household income—automatically flagging the highest-risk community (e.g., Sooke) for immediate intervention.

	Wait Times Efficacy (Tab 2): Provides a historic (2014-2025) and procedure-specific visualization tracking BC surgical wait times against the National Average and strict Federal Benchmarks, automatically categorizing procedures into Red/Amber/Green alerts.

	Narrative Crisis Tracking (Tab 3): Synthesizes complex opioid crisis data through dual-axis mapping (tracking hospital load vs. toxicity mortality). Crucially, the system dynamically injects the most vulnerable community identified in Tab 1 directly into the Tab 3 crisis briefing, structurally connecting overarching provincial trends to localized on-the-ground interventions.

Tech Stack
	Core Backend: Python 3
	Frontend Framework: Streamlit (utilized for complex rapid-prototyping, multi-tab layouts, and session states)
	Data Processing Algorithms: Pandas & NumPy (used for real-time mathematical indexing, YoY delta calculations, and data ingestion)
	High-Fidelity Visualizations: Plotly (Plotly Express & Graph Objects utilized for interactive mapping, dual-axis line charts, and sequential YlGnBu heatmaps)
	Styling: Custom CSS injection (to overwrite default components into a sophisticated Light Mode/high-contrast executive aesthetic)

How to Run/View the Demo
	Public URL
		https://bc-health-dashboardant-dscjbe2qtshtpkzi6mp775.streamlit.app/

	Run localy
		Open your terminal or command prompt.
		Navigate to your project folder
			cd "C:\Users\gsanc\Antigravity Tutorial\Healthcare"
		Ensure the required packages are installed:
			pip install streamlit pandas plotly numpy
		Run the Streamlit server
			python -m streamlit run app.py
		he dashboard will automatically launch in your default web browser at 
			http://localhost:8501.
			
Presentation
	https://docs.google.com/presentation/d/1lHbdNKi15VvewTtRMONL3cORu7GTB3-stalTpJlpfmQ/edit?slide=id.p1#slide=id.p1