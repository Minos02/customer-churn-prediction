import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { Users, TrendingUp, AlertCircle, DollarSign, Activity, Upload, Download, Brain } from 'lucide-react'

const API_URL = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [kpis, setKpis] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [batchFile, setBatchFile] = useState(null)
  const [batchResults, setBatchResults] = useState(null)
  const [batchLoading, setBatchLoading] = useState(false)

  useEffect(() => {
    axios.get(`${API_URL}/kpis`)
      .then(res => setKpis(res.data))
      .catch(err => console.error(err))
  }, [])

  const [formData, setFormData] = useState({
    gender: 'Male',
    SeniorCitizen: 'No',
    Partner: 'Yes',
    Dependents: 'No',
    tenure: 12,
    PhoneService: 'Yes',
    MultipleLines: 'No',
    InternetService: 'Fiber optic',
    OnlineSecurity: 'No',
    OnlineBackup: 'No',
    DeviceProtection: 'No',
    TechSupport: 'No',
    StreamingTV: 'Yes',
    StreamingMovies: 'Yes',
    Contract: 'Month-to-month',
    PaperlessBilling: 'Yes',
    PaymentMethod: 'Electronic check',
    MonthlyCharges: 70.0,
    TotalCharges: 1000.0
  })

  const handlePredict = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/predict`, formData)
      setPrediction(res.data)
    } catch (err) {
      alert('Prediction failed: ' + err.message)
    }
    setLoading(false)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'tenure' || name === 'MonthlyCharges' || name === 'TotalCharges' 
        ? parseFloat(value) 
        : value
    }))
  }

  const handleBatchUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    setBatchFile(file)
    setBatchLoading(true)
    
    const reader = new FileReader()
    reader.onload = async (event) => {
      const text = event.target.result
      const rows = text.split('\n').filter(row => row.trim())
      const headers = rows[0].split(',').map(h => h.trim())
      
      const customers = rows.slice(1).map(row => {
        const values = row.split(',').map(v => v.trim())
        const customer = {}
        headers.forEach((header, i) => {
          customer[header] = values[i]
        })
        return customer
      })
      
      try {
        const predictions = []
        for (const customer of customers) {
          const res = await axios.post(`${API_URL}/predict`, customer)
          predictions.push({ ...customer, ...res.data })
        }
        setBatchResults(predictions)
      } catch (err) {
        alert('Batch prediction failed: ' + err.message)
      }
      setBatchLoading(false)
    }
    reader.readAsText(file)
  }

  const downloadSampleCSV = () => {
    const csv = `gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges
Male,No,Yes,No,12,Yes,No,Fiber optic,No,No,No,No,Yes,Yes,Month-to-month,Yes,Electronic check,85.0,1020.0
Female,Yes,No,No,24,Yes,Yes,DSL,Yes,Yes,No,Yes,No,No,One year,No,Mailed check,65.0,1560.0`
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'customer_template.csv'
    a.click()
  }

  const contractData = [
    { name: 'Month-to-month', churn: 42 },
    { name: 'One year', churn: 11 },
    { name: 'Two year', churn: 3 }
  ]

  const tenureData = [
    { tenure: '0-12', churn: 45 },
    { tenure: '13-24', churn: 32 },
    { tenure: '25-48', churn: 18 },
    { tenure: '48+', churn: 8 }
  ]

  const COLORS = ['#ef4444', '#f59e0b', '#10b981']

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-zinc-900/50 backdrop-blur-xl border-b border-zinc-800/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-white">ChurnGuard AI</h1>
              <span className="text-xs text-zinc-500 px-2 py-1 bg-zinc-800/50 rounded">v1.0</span>
            </div>
            <nav className="flex space-x-2">
              {['dashboard', 'predict', 'batch', 'analytics'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === tab
                      ? 'bg-white/10 backdrop-blur-md text-white border border-white/20'
                      : 'text-zinc-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && kpis && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Business Overview</h2>
            
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50 hover:border-zinc-700/50 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Total Customers</p>
                    <h3 className="text-3xl font-bold text-white mt-2">
                      {kpis.total_customers.toLocaleString()}
                    </h3>
                  </div>
                  <Users className="w-12 h-12 text-blue-400" />
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50 hover:border-zinc-700/50 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Churned</p>
                    <h3 className="text-3xl font-bold text-red-400 mt-2">
                      {kpis.churned_customers.toLocaleString()}
                    </h3>
                  </div>
                  <AlertCircle className="w-12 h-12 text-red-400" />
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50 hover:border-zinc-700/50 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Churn Rate</p>
                    <h3 className="text-3xl font-bold text-yellow-400 mt-2">
                      {kpis.churn_rate.toFixed(1)}%
                    </h3>
                  </div>
                  <TrendingUp className="w-12 h-12 text-yellow-400" />
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50 hover:border-zinc-700/50 transition-all">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Avg Revenue</p>
                    <h3 className="text-3xl font-bold text-green-400 mt-2">
                      ${kpis.avg_monthly_charges.toFixed(2)}
                    </h3>
                  </div>
                  <DollarSign className="w-12 h-12 text-green-400" />
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50">
                <h3 className="text-lg font-semibold text-white mb-4">Churn by Contract</h3>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={contractData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="name" stroke="#71717a" />
                    <YAxis stroke="#71717a" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#18181b', 
                        border: '1px solid #27272a', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Bar dataKey="churn" fill="#10b981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50">
                <h3 className="text-lg font-semibold text-white mb-4">Churn by Tenure</h3>
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={tenureData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="tenure" stroke="#71717a" />
                    <YAxis stroke="#71717a" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#18181b', 
                        border: '1px solid #27272a', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Line type="monotone" dataKey="churn" stroke="#ef4444" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Single Prediction Tab */}
        {activeTab === 'predict' && (
          <div className="max-w-5xl mx-auto">
            <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-8 border border-zinc-800/50">
              <h2 className="text-2xl font-bold text-white mb-6">🔮 Predict Customer Churn</h2>
              
              <form onSubmit={handlePredict} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.keys(formData).slice(0, 6).map(key => (
                    <div key={key}>
                      <label className="block text-zinc-400 text-sm mb-2 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </label>
                      {typeof formData[key] === 'number' ? (
                        <input 
                          type="number" 
                          name={key} 
                          value={formData[key]} 
                          onChange={handleChange}
                          className="w-full px-4 py-2.5 rounded-xl bg-black/30 backdrop-blur-md border border-zinc-800 text-white focus:border-emerald-500 focus:outline-none transition-all"
                        />
                      ) : (
                        <select 
                          name={key} 
                          value={formData[key]} 
                          onChange={handleChange}
                          className="w-full px-4 py-2.5 rounded-xl bg-black/30 backdrop-blur-md border border-zinc-800 text-white focus:border-emerald-500 focus:outline-none transition-all"
                        >
                          {key === 'gender' ? ['Male', 'Female'].map(v => <option key={v}>{v}</option>) : 
                           ['Yes', 'No'].map(v => <option key={v}>{v}</option>)}
                        </select>
                      )}
                    </div>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-emerald-500/20 backdrop-blur-md border border-emerald-500/50 text-emerald-400 font-semibold py-3.5 px-6 rounded-xl hover:bg-emerald-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Analyzing...' : '🚀 Predict Churn'}
                </button>
              </form>

              {prediction && (
                <div className="mt-8 p-6 bg-black/30 backdrop-blur-md rounded-xl border border-zinc-800">
                  <h3 className="text-xl font-bold text-white mb-4">Prediction Result</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                      <p className="text-zinc-400 text-sm">Probability</p>
                      <p className="text-3xl font-bold text-yellow-400 mt-2">
                        {(prediction.churn_probability * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="text-center p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                      <p className="text-zinc-400 text-sm">Prediction</p>
                      <p className={`text-3xl font-bold mt-2 ${prediction.churn_prediction === 1 ? 'text-red-400' : 'text-green-400'}`}>
                        {prediction.churn_prediction === 1 ? 'CHURN' : 'STAY'}
                      </p>
                    </div>
                    <div className="text-center p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
                      <p className="text-zinc-400 text-sm">Risk Level</p>
                      <p className="text-3xl font-bold text-orange-400 mt-2">
                        {prediction.risk_level}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Batch Prediction Tab */}
        {activeTab === 'batch' && (
          <div className="max-w-5xl mx-auto space-y-6">
            <div className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-8 border border-zinc-800/50">
              <h2 className="text-2xl font-bold text-white mb-6">📂 Batch Prediction</h2>
              
              <div className="space-y-4">
                <button
                  onClick={downloadSampleCSV}
                  className="w-full bg-blue-500/20 backdrop-blur-md border border-blue-500/50 text-blue-400 font-semibold py-3 px-6 rounded-xl hover:bg-blue-500/30 transition-all flex items-center justify-center space-x-2"
                >
                  <Download className="w-5 h-5" />
                  <span>Download Sample CSV Template</span>
                </button>

                <div className="relative">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleBatchUpload}
                    className="hidden"
                    id="batch-upload"
                  />
                  <label
                    htmlFor="batch-upload"
                    className="w-full bg-emerald-500/20 backdrop-blur-md border border-emerald-500/50 text-emerald-400 font-semibold py-3 px-6 rounded-xl hover:bg-emerald-500/30 transition-all flex items-center justify-center space-x-2 cursor-pointer"
                  >
                    <Upload className="w-5 h-5" />
                    <span>{batchFile ? batchFile.name : 'Upload CSV File'}</span>
                  </label>
                </div>

                {batchLoading && (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400 mx-auto"></div>
                    <p className="text-zinc-400 mt-4">Processing predictions...</p>
                  </div>
                )}

                {batchResults && (
                  <div className="mt-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">
                        Results ({batchResults.length} customers)
                      </h3>
                      <button className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all">
                        Download Results
                      </button>
                    </div>
                    <div className="bg-black/30 backdrop-blur-md rounded-xl border border-zinc-800 overflow-hidden">
                      <div className="overflow-x-auto max-h-96">
                        <table className="w-full text-sm">
                          <thead className="bg-zinc-800/50">
                            <tr>
                              <th className="px-4 py-3 text-left text-zinc-400">Tenure</th>
                              <th className="px-4 py-3 text-left text-zinc-400">Contract</th>
                              <th className="px-4 py-3 text-left text-zinc-400">Probability</th>
                              <th className="px-4 py-3 text-left text-zinc-400">Prediction</th>
                              <th className="px-4 py-3 text-left text-zinc-400">Risk</th>
                            </tr>
                          </thead>
                          <tbody>
                            {batchResults.map((row, i) => (
                              <tr key={i} className="border-t border-zinc-800 hover:bg-white/5">
                                <td className="px-4 py-3 text-white">{row.tenure}</td>
                                <td className="px-4 py-3 text-white">{row.Contract}</td>
                                <td className="px-4 py-3 text-yellow-400">
                                  {(row.churn_probability * 100).toFixed(1)}%
                                </td>
                                <td className="px-4 py-3">
                                  <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${
                                    row.churn_prediction === 1 
                                      ? 'bg-red-500/20 text-red-400' 
                                      : 'bg-green-500/20 text-green-400'
                                  }`}>
                                    {row.churn_prediction === 1 ? 'CHURN' : 'STAY'}
                                  </span>
                                </td>
                                <td className="px-4 py-3 text-orange-400">{row.risk_level}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Model Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { label: 'ROC-AUC', value: '83.48%', color: 'text-green-400' },
                { label: 'Accuracy', value: '80.0%', color: 'text-blue-400' },
                { label: 'F1-Score', value: '79.0%', color: 'text-purple-400' }
              ].map(metric => (
                <div key={metric.label} className="bg-zinc-900/50 backdrop-blur-xl rounded-2xl p-6 border border-zinc-800/50">
                  <p className="text-zinc-400 text-sm">{metric.label}</p>
                  <p className={`text-4xl font-bold ${metric.color} mt-2`}>{metric.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800/50 mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-zinc-500">
            <p>Built with Python • FastAPI • React • ML</p>
            <p>ChurnGuard AI © 2026</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
