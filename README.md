# NordBord Injury Risk Monitor

This dashboard provides a robust and intuitive interface for monitoring and assessing the risk of hamstring strength imbalance in athletes. It is built using Python and Streamlit, offering a user-friendly web application for sports scientists, physiotherapists, and coaches.

## Main Features

- **Dynamic Filtering**: Users can filter the data based on age groups, teams, status, metrics, and player imbalance.
- **Real-Time Analytics**: The dashboard displays real-time updates on the total players selected, imbalance, and strength gain/loss.
- **Test Result Overview**: It offers a detailed result of the ISO Prone and other tests for selected players, including pass/fail status on NordBord tests and imbalance metrics.
- **Graphical Insights**: Presents graphical data of Max Force, Max Torque, and Max Impulse, divided into left and right foot metrics over time, allowing for an immediate visual understanding of the data.
- **Automated Alerts**: Critical information and alerts are highlighted in red text, generated dynamically based on the data provided.

## Installation

Ensure you have Python installed on your system. This application requires Python 3.6 or later.

1. **Clone the Repository**
```sh
git clone https://github.com/your-username/nordbord-injury-risk-monitor.git
cd nordbord-injury-risk-monitor
```

2. **Set Up a Virtual Environment (Optional but recommended)**
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install Dependencies**
```sh
pip install -r requirements.txt
```

## Running the Application
To run the application, navigate to the application directory and execute:
```sh
streamlit run dashboard.py
```

The dashboard will be served on your local machine, typically at http://localhost:8501, and you can open it in your web browser.
