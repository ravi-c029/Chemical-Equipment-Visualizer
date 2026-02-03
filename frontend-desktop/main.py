import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Configuration
API_URL = "http://127.0.0.1:8000/api/"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")
        self.setGeometry(100, 100, 1200, 800)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 1. Upload Section
        self.upload_btn = QPushButton("Upload CSV File")
        self.upload_btn.setStyleSheet("background-color: #007bff; color: white; padding: 10px; font-size: 16px;")
        self.upload_btn.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_btn)
        
        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; font-size: 16px;")
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.layout.addWidget(self.pdf_btn)

        # 2. Summary Stats Section
        self.stats_label = QLabel("Upload a file to see statistics.")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("font-size: 14px; margin: 10px;")
        self.layout.addWidget(self.stats_label)

        # 3. Tabs for Visualization and Data
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tab 1: Charts
        self.chart_tab = QWidget()
        self.chart_layout = QHBoxLayout(self.chart_tab)
        self.tabs.addTab(self.chart_tab, "Visualizations")

        # Matplotlib Figures
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)

        # Tab 2: Data Table
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.table = QTableWidget()
        self.table_layout.addWidget(self.table)
        self.tabs.addTab(self.table_tab, "Raw Data")

        # Tab 3: History
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout(self.history_tab)
        self.history_list = QTableWidget()
        self.history_layout.addWidget(self.history_list)
        self.refresh_hist_btn = QPushButton("Refresh History")
        self.refresh_hist_btn.clicked.connect(self.fetch_history)
        self.history_layout.addWidget(self.refresh_hist_btn)
        self.tabs.addTab(self.history_tab, "Upload History")

        # Initial History Load
        self.fetch_history()

    def upload_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if file_path:
            self.stats_label.setText("Uploading and Analyzing...")
            try:
                files = {'file': open(file_path, 'rb')}
                # Ensure using the correct password here
                response = requests.post(f"{API_URL}upload/", files=files, auth=('admin', 'ravi_admin@123'))
                
                if response.status_code == 201:
                    data = response.json()
                    self.current_dataset_id = data['id']  # Save the ID for PDF download
                    self.update_ui(data)
                    self.fetch_history() 
                else:
                    QMessageBox.critical(self, "Error", f"Upload failed: {response.text}")
                    self.stats_label.setText("Upload Failed.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")

    def update_ui(self, data):
        # 1. Update Summary
        summary = data['summary']
        self.stats_label.setText(
            f"Total Count: {summary['total_count']} | "
            f"Avg Flow: {summary['avg_flowrate']} | "
            f"Avg Pressure: {summary['avg_pressure']} | "
            f"Avg Temp: {summary['avg_temperature']}"
        )

        # 2. Update Charts (Matplotlib)
        self.ax1.clear()
        self.ax2.clear()

        # Data for charts
        types = list(data['type_distribution'].keys())
        counts = list(data['type_distribution'].values())

        # Bar Chart
        self.ax1.bar(types, counts, color=['blue', 'green', 'red', 'orange'])
        self.ax1.set_title("Equipment Type Distribution (Bar)")
        self.ax1.set_ylabel("Count")

        # Pie Chart
        self.ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        self.ax2.set_title("Equipment Type Distribution (Pie)")

        self.canvas.draw()

        # 3. Update Table
        rows = data['table_data']
        if rows:
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(rows[0]))
            self.table.setHorizontalHeaderLabels(rows[0].keys())

            for i, row in enumerate(rows):
                for j, (key, value) in enumerate(row.items()):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def fetch_history(self):
        try:
            # Fetch data from backend
            response = requests.get(f"{API_URL}history/", auth=('admin', 'ravi_admin@123'))
            
            if response.status_code == 200:
                history_data = response.json()
                
                # Update Table Columns: Now 7 columns instead of 3
                self.history_list.setColumnCount(7)
                self.history_list.setHorizontalHeaderLabels([
                    "ID", "Date Uploaded", "Filename", 
                    "Total Rows", "Avg Flow", "Avg Press", "Avg Temp"
                ])
                self.history_list.setRowCount(len(history_data))
                
                for i, item in enumerate(history_data):
                    # 1. Basic Info
                    self.history_list.setItem(i, 0, QTableWidgetItem(str(item['id'])))
                    
                    # Format date slightly for better readability
                    raw_date = item['uploaded_at'].split('T')[0] 
                    self.history_list.setItem(i, 1, QTableWidgetItem(raw_date))
                    
                    filename = item['file'].split('/')[-1]
                    self.history_list.setItem(i, 2, QTableWidgetItem(filename))
                    
                    # 2. Summary Stats (The missing part!)
                    # We use .get() or check for None to avoid errors if data is missing
                    count = str(item.get('total_count', 0))
                    flow = f"{item.get('avg_flowrate', 0):.2f}"
                    press = f"{item.get('avg_pressure', 0):.2f}"
                    temp = f"{item.get('avg_temperature', 0):.2f}"

                    self.history_list.setItem(i, 3, QTableWidgetItem(count))
                    self.history_list.setItem(i, 4, QTableWidgetItem(flow))
                    self.history_list.setItem(i, 5, QTableWidgetItem(press))
                    self.history_list.setItem(i, 6, QTableWidgetItem(temp))
                    
                # Adjust column widths to fit content
                self.history_list.resizeColumnsToContents()
                    
        except Exception as e:
            # Helpful to print error to console for debugging if needed
            print(f"Error fetching history: {e}")

    def download_pdf(self):
        # Use the ID from the currently loaded data
        if not hasattr(self, 'current_dataset_id'):
            QMessageBox.warning(self, "Warning", "Please upload a file first.")
            return

        try:
            # Send Auth here too! Ensure using the correct password
            response = requests.get(f"{API_URL}report/{self.current_dataset_id}/", auth=('admin', 'ravi_admin@123'))
            
            if response.status_code == 200:
                # Ask user where to save
                save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"report_{self.current_dataset_id}.pdf", "PDF Files (*.pdf)")
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", "PDF Saved Successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to download PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())