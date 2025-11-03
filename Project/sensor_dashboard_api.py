from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import os
from datetime import datetime
from core.sensor_api import get_sensor_api
from core.database_enhanced import (
    view_all_FuelTank_data,
    get_all_pumps,
    get_pump_directory
)

app = Flask(__name__)
CORS(app)

sensor_api = get_sensor_api()

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم خزانات الوقود الذكية</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@200..1000&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Cairo', sans-serif; background-color: #ffffff; color: #1a1a1a; }
        .tank-container { width: 280px; height: 150px; border: 3px solid #b0b0b0; border-radius: 75px; overflow: hidden;
            background: linear-gradient(to bottom, #cccccc, #e0e0e0, #cccccc);
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.2), inset 0 0 10px rgba(0, 0, 0, 0.1); }
        .fuel-fill { position: absolute; top: 0; left: 0; height: 100%;
            transition: width 0.6s ease-out, background 0.3s; }
        .pump-on { box-shadow: 0 0 10px #0f0, 0 0 3px #0f0; border-color: #0c0 !important; background-color: #f0fff0; }
        .pump-off { box-shadow: 0 0 10px #f00, 0 0 3px #f00; border-color: #c00 !important; background-color: #fff0f0; }
        .meter-display { font-family: 'Inter', monospace; font-size: 2.5rem; color: #0f0;
            text-shadow: 0 0 8px rgba(0, 255, 0, 0.7); background-color: #111; padding: 8px 16px;
            border-radius: 8px; border: 1px solid #0f0; }
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="text-center mb-12">
            <h1 class="text-4xl sm:text-5xl font-extrabold text-blue-800 tracking-wider">
                لوحة تحكم خزانات الوقود الذكية
            </h1>
            <p class="text-xl text-gray-700 mt-2">نظام مراقبة متقدم للتشغيل والتحكم</p>
        </header>

        <section class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center text-gray-800 border-b-2 border-blue-500 pb-2">
                بيانات الخزانات
            </h2>
            <div id="tanks-display" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center"></div>
        </section>

        <section class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center text-gray-800 border-b-2 border-blue-500 pb-2">
                وحدات التحكم بالمضخات
            </h2>
            <div id="pumps-display" class="grid grid-cols-1 lg:grid-cols-2 gap-10"></div>
        </section>

        <div id="error-message" class="fixed top-4 left-1/2 transform -translate-x-1/2 p-4 bg-red-600 text-white rounded-lg shadow-2xl z-50 hidden"></div>
    </div>

    <script>
        let tanksData = [];
        let pumpsData = [];

        function showMessage(message, type = 'error') {
            const errorDiv = document.getElementById('error-message');
            errorDiv.textContent = message;
            errorDiv.className = `fixed top-4 left-1/2 transform -translate-x-1/2 p-4 rounded-lg shadow-2xl z-50 ${type === 'error' ? 'bg-red-600' : 'bg-green-600'} text-white`;
            errorDiv.style.opacity = '1';
            errorDiv.classList.remove('hidden');
            setTimeout(() => { errorDiv.classList.add('hidden'); }, 3000);
        }

        async function fetchTanksData() {
            try {
                const response = await fetch('/api/tanks');
                const data = await response.json();
                tanksData = data.tanks || [];
                return tanksData;
            } catch (error) {
                showMessage('فشل في جلب بيانات الخزانات: ' + error.message);
                return [];
            }
        }

        async function fetchPumpsData() {
            try {
                const response = await fetch('/api/pumps');
                const data = await response.json();
                pumpsData = data.pumps || [];
                return pumpsData;
            } catch (error) {
                showMessage('فشل في جلب بيانات المضخات: ' + error.message);
                return [];
            }
        }

        async function fetchAllData() {
            await Promise.all([fetchTanksData(), fetchPumpsData()]);
            renderDashboard();
        }

        function createTankCard(tank) {
            return `
                <div class="bg-white p-4 rounded-xl shadow-lg w-80 relative border border-gray-200">
                    <h3 class="text-lg font-bold mb-1 text-blue-600">${tank.name}</h3>
                    <p class="text-xs text-gray-500 mb-4">السعة: ${tank.capacity.toLocaleString()} لتر</p>
                    <div class="tank-container">
                        <div class="fuel-fill" style="width: ${tank.currentLevel}%; background: linear-gradient(to right, #4ECDC4 0%, #4ECDC4AA 100%);"></div>
                    </div>
                    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 p-2 bg-gray-50 border border-blue-300 rounded-lg">
                        <p class="text-xl font-mono font-bold text-blue-700">${tank.currentLevel.toFixed(1)}%</p>
                    </div>
                </div>
            `;
        }

        function createPumpCard(pump) {
            const isOn = pump.status === 'ON';
            const statusColor = isOn ? 'text-green-700' : 'text-red-700';
            const tankNames = pump.associatedTanks.map(id => `<span class="bg-blue-100 text-xs py-1 px-3 rounded-full">${id}</span>`).join(' ');

            return `
                <div class="bg-white p-6 rounded-2xl shadow-xl border-2 border-gray-200 flex flex-col md:flex-row gap-6">
                    <div class="flex flex-col items-center justify-center w-full md:w-1/3 p-4">
                        <div class="p-4 rounded-full border-4 border-gray-400 mb-4 ${isOn ? 'pump-on' : 'pump-off'}">
                            <svg class="text-blue-600" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <rect x="3" y="14" width="18" height="8" rx="2"/><path d="M7 14V3h10v11"/><path d="M12 7l-2 2h4l-2-2"/>
                            </svg>
                        </div>
                        <p class="text-xl font-bold ${statusColor}">${isOn ? 'شغالة' : 'متوقفة'}</p>
                    </div>
                    <div class="flex flex-col w-full md:w-2/3 justify-center">
                        <h4 class="text-2xl font-extrabold mb-4 text-gray-800">${pump.name}</h4>
                        <div class="mb-6">
                            <p class="text-sm text-gray-500 mb-1">عداد الترقيم (لتر):</p>
                            <div class="meter-display">
                                <span>${pump.meterReading.toFixed(2)}</span>
                            </div>
                        </div>
                        <div class="mb-4">
                            <p class="text-sm text-gray-500 mb-2">الخزانات المرتبطة:</p>
                            <div class="flex flex-wrap gap-2">${tankNames}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        function renderDashboard() {
            document.getElementById('tanks-display').innerHTML = tanksData.map(createTankCard).join('');
            document.getElementById('pumps-display').innerHTML = pumpsData.map(createPumpCard).join('');
        }

        window.onload = async function() {
            await fetchAllData();
            setInterval(fetchAllData, 30000);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/tanks')
def get_tanks():
    try:
        tank_data = view_all_FuelTank_data()
        sensor_readings = sensor_api.get_all_sensor_readings()

        tanks = []
        for tank in tank_data:
            tank_id = tank[0]
            fuel_type = tank[1] or 'غير محدد'
            capacity = float(tank[2]) if tank[2] else 10000
            current_level_liters = sensor_readings.get(tank_id, float(tank[3]) if tank[3] else capacity * 0.7)
            current_level_percent = (current_level_liters / capacity) * 100 if capacity > 0 else 0

            tanks.append({
                'id': tank_id,
                'name': f'خزان {fuel_type} {tank_id}',
                'fuelType': fuel_type,
                'capacity': capacity,
                'currentLevel': min(current_level_percent, 100),
                'currentLiters': current_level_liters,
                'lastUpdated': datetime.now().isoformat()
            })

        return jsonify({'success': True, 'tanks': tanks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pumps')
def get_pumps():
    try:
        pump_data = get_all_pumps()
        pump_directory = get_pump_directory()
        tank_connections = {}
        for entry in pump_directory:
            pump_id = entry[1]
            tank_id = entry[2]
            if pump_id not in tank_connections:
                tank_connections[pump_id] = []
            tank_connections[pump_id].append(tank_id)

        pumps = []
        for pump in pump_data:
            pump_id = pump[0]
            pump_name = pump[1] or f'المضخة رقم {pump_id}'
            import random
            status = 'ON' if random.random() > 0.3 else 'OFF'
            meter_reading = random.uniform(1000, 50000)

            pumps.append({
                'id': pump_id,
                'name': pump_name,
                'status': status,
                'meterReading': meter_reading,
                'associatedTanks': tank_connections.get(pump_id, []),
                'lastUpdated': datetime.now().isoformat()
            })

        return jsonify({'success': True, 'pumps': pumps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
