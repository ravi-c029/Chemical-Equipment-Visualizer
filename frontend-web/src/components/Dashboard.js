import React, { useState, useEffect } from "react";
import api from "../api/axios";
import { Bar, Pie } from "react-chartjs-2";
import "chart.js/auto"; // Required for Chart.js 3+
import "bootstrap/dist/css/bootstrap.min.css";

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch history on load
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get("history/");
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch history");
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    setError("");

    try {
      const res = await api.post("upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setData(res.data);
      fetchHistory(); // Refresh history list
    } catch (err) {
      setError("Upload failed. Check console for details.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!data || !data.id) return;

    try {
      // We request the PDF as a 'blob' (binary large object)
      const res = await api.get(`report/${data.id}/`, { responseType: "blob" });

      // Create a fake link to trigger the download
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${data.id}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error("PDF Download failed", err);
    }
  };

  // Chart Data Helpers
  const getChartData = () => {
    if (!data) return null;
    const labels = Object.keys(data.type_distribution);
    const values = Object.values(data.type_distribution);

    return {
      labels: labels,
      datasets: [
        {
          label: "Equipment Type Distribution",
          data: values,
          backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
        },
      ],
    };
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Chemical Equipment Visualizer</h2>

      {/* 1. Upload Section */}
      <div className="card p-4 mb-4">
        <h4>Upload CSV</h4>
        <div className="d-flex gap-2">
          <input
            type="file"
            className="form-control"
            onChange={handleFileChange}
            accept=".csv"
          />
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={loading}
          >
            {loading ? "Uploading..." : "Analyze"}
          </button>
          <button
            className="btn btn-danger ms-2"
            onClick={handleDownloadPDF}
            disabled={!data}
          >
            Download PDF Report
          </button>
        </div>
        {error && <p className="text-danger mt-2">{error}</p>}
      </div>

      {/* 2. Visualization Section */}
      {data && (
        <div className="row mb-5">
          {/* Summary Cards */}
          <div className="col-12 mb-4">
            <div className="d-flex justify-content-between text-center">
              <div className="card p-3 flex-fill mx-1">
                <h5>Total Count</h5>
                <h3>{data.summary.total_count}</h3>
              </div>
              <div className="card p-3 flex-fill mx-1">
                <h5>Avg Flowrate</h5>
                <h3>{data.summary.avg_flowrate}</h3>
              </div>
              <div className="card p-3 flex-fill mx-1">
                <h5>Avg Pressure</h5>
                <h3>{data.summary.avg_pressure}</h3>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="col-md-6">
            <div className="card p-3">
              <h5>Type Distribution (Pie)</h5>
              <Pie data={getChartData()} />
            </div>
          </div>
          <div className="col-md-6">
            <div className="card p-3">
              <h5>Type Distribution (Bar)</h5>
              <Bar data={getChartData()} />
            </div>
          </div>

          {/* Data Table */}
          <div className="col-12 mt-4">
            <div className="card p-3">
              <h5>Raw Data (First 50 Rows)</h5>
              <div style={{ maxHeight: "300px", overflowY: "scroll" }}>
                <table className="table table-striped table-sm">
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.table_data.map((row, idx) => (
                      <tr key={idx}>
                        <td>{row["Equipment Name"]}</td>
                        <td>{row["Type"]}</td>
                        <td>{row["Flowrate"]}</td>
                        <td>{row["Pressure"]}</td>
                        <td>{row["Temperature"]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* 3. History Management Section (Required by Task) */}
            <div className="card p-4 mt-4 mb-5 shadow-sm">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4>Upload History (Last 5)</h4>
                    <button className="btn btn-sm btn-outline-secondary" onClick={fetchHistory}>Refresh History</button>
                </div>
                
                {history.length === 0 ? (
                    <p className="text-muted">No files uploaded yet.</p>
                ) : (
                    <div className="table-responsive">
                        <table className="table table-hover table-bordered">
                            <thead className="table-light">
                                <tr>
                                    <th>Date</th>
                                    <th>File Name</th>
                                    <th>Total Rows</th>
                                    <th>Avg Flowrate</th>
                                    <th>Avg Pressure</th>
                                    <th>Avg Temp</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((item) => (
                                    <tr key={item.id}>
                                        <td>{new Date(item.uploaded_at).toLocaleString()}</td>
                                        <td>
                                            {/* Extract just the filename from the full path */}
                                            {item.file.split('/').pop()}
                                        </td>
                                        {/* This is the "Summary" data required by the task */}
                                        <td>{item.total_count}</td>
                                        <td>{item.avg_flowrate ? item.avg_flowrate.toFixed(2) : '-'}</td>
                                        <td>{item.avg_pressure ? item.avg_pressure.toFixed(2) : '-'}</td>
                                        <td>{item.avg_temperature ? item.avg_temperature.toFixed(2) : '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
    </div>
  );
};

export default Dashboard;
