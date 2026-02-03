# Chemical Equipment Parameter Visualizer 🧪📊

**A Hybrid Web & Desktop Application**

Welcome to the **Chemical Equipment Parameter Visualizer**! This project is a hybrid application designed to analyze and visualize chemical equipment data (Flowrate, Pressure, Temperature, etc.) from CSV files. 

Whether you prefer a web interface or a native desktop application, this system has you covered. Both frontends communicate with a single, robust **Django** backend to ensure consistency in data analysis and storage.

---

## 🚀 Key Features

* **Hybrid Architecture:** One backend (Django) powering two frontends (React Web + PyQt5 Desktop).
* **Data Analytics:** Automatically calculates Total Count, Average Flowrate, Pressure, and Temperature.
* **Visualizations:** * **Web:** Interactive charts using Chart.js.
    * **Desktop:** Native plotting using Matplotlib.
* **History Management:** Keeps track of the last 5 uploaded datasets.
* **CSV Support:** Robust parsing using Pandas.

---

## 🛠️ Tech Stack

| Layer | Technology | Usage |
| :--- | :--- | :--- |
| **Backend** | Django + DRF | API & Business Logic |
| **Data Processing** | Pandas | CSV Parsing & Analytics |
| **Database** | SQLite | Data Storage |
| **Web Frontend** | React.js + Chart.js | Browser-based UI |
| **Desktop Frontend** | PyQt5 + Matplotlib | Native Desktop UI |

---

## ⚙️ Setup & Installation

Follow these steps to get the entire system running on your local machine.

### 1. Prerequisites
Ensure you have the following installed:
* **Python** (v3.8 or higher)
* **Node.js** & **npm** (for the Web App)

---

### 2. Backend Setup (Django)
The backend is the heart of the application. We need to start this first.

1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment (optional but recommended):
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install django djangorestframework pandas django-cors-headers
    ```

4.  Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  Start the server:
    ```bash
    python manage.py runserver
    ```
    > 🟢 **Success:** The backend is now running at `http://127.0.0.1:8000/`

---

### 3. Web Application Setup (React)
Now, let's fire up the web dashboard. Open a **new terminal**.

1.  Navigate to the web folder:
    ```bash
    cd frontend-web
    ```

2.  Install dependencies:
    ```bash
    npm install  axios chart.js react-chartjs-2 bootstrap
    ```

3.  Start the React app:
    ```bash
    npm start
    ```
    > 🟢 **Success:** The browser should open automatically at `http://localhost:3000`

---

### 4. Desktop Application Setup (PyQt5)
Prefer a desktop app? Let's run the native client. Open a **new terminal**.

1.  Navigate to the desktop folder:
    ```bash
    cd frontend-desktop
    ```

2.  Install desktop-specific libraries:
    ```bash
    pip install PyQt5 matplotlib requests
    ```

3.  Run the application:
    ```bash
    python main.py
    ```
    > 🟢 **Success:** The desktop GUI window should appear.

---

## 🧪 How to Use

1.  **Get the Sample Data:** Use the provided `sample_equipment_data.csv` file located in the root directory.
    
2.  **Upload:**
    * **Web:** Click "Choose File" -> Select CSV -> Click "Analyze".
    * **Desktop:** Click the blue "Upload CSV File" button -> Select CSV.

3.  **Analyze:**
    * View the summary cards (Averages & Counts).
    * Explore the Bar and Pie charts for Equipment Type distribution.
    * Scroll through the raw data table.

4.  **Check History:**
    Both apps allow you to view the history of the last 5 uploads.

---

## 📝 Notes for Evaluators
* **CORS:** The Django backend is configured to accept requests from `localhost:3000` (React).
* **Database:** A local `db.sqlite3` file is created in the backend folder.
* **Upload Limit:** The system automatically cleans up old datasets, keeping only the recent 5.

Happy Coding! 🚀