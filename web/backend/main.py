from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from pathlib import Path

app = FastAPI(title="AutoTrading Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

def get_log_files(log_type: str, days: int = 30) -> List[str]:
    """Get log files for the specified number of days"""
    log_dir = Path("../../logs").resolve()
    print(f"DEBUG: Looking for logs in: {log_dir}")
    print(f"DEBUG: Log dir exists: {log_dir.exists()}")
    if not log_dir.exists():
        return []
    
    files = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        file_pattern = f"{log_type}_{date}.json"
        file_path = log_dir / file_pattern
        if file_path.exists():
            files.append(str(file_path))
    
    return files

def load_json_logs(file_paths: List[str]) -> List[Dict]:
    """Load and combine JSON log files"""
    all_logs = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                if isinstance(logs, list):
                    all_logs.extend(logs)
                else:
                    all_logs.append(logs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return sorted(all_logs, key=lambda x: x.get('timestamp', ''))

@app.get("/api/trades")
async def get_trades(days: int = 7):
    """Get trading history"""
    trade_files = get_log_files("trades", days)
    trades = load_json_logs(trade_files)
    
    return {
        "trades": trades,
        "summary": {
            "total_trades": len(trades),
            "successful_trades": len([t for t in trades if t.get('success', False)]),
            "buy_trades": len([t for t in trades if t.get('trade_type') == 'buy']),
            "sell_trades": len([t for t in trades if t.get('trade_type') == 'sell']),
        }
    }

@app.get("/api/analysis")
async def get_analysis(days: int = 7):
    """Get analysis history"""
    analysis_files = get_log_files("analysis", days)
    print(f"DEBUG: Found analysis files: {analysis_files}")
    analysis = load_json_logs(analysis_files)
    print(f"DEBUG: Loaded {len(analysis)} analysis entries")
    
    return {
        "analysis": analysis,
        "chart_data": [
            {
                "timestamp": a.get('timestamp'),
                "price": a.get('current_price'),
                "total_asset": a.get('total_asset'),
                "fear_greed": a.get('fear_greed_index'),
                "recommendation": a.get('recommendation', {}).get('recommendation')
            }
            for a in analysis
        ]
    }

@app.get("/api/portfolio")
async def get_current_portfolio():
    """Get current portfolio status"""
    try:
        # This would integrate with your actual portfolio manager
        # For now, return latest analysis data
        analysis_files = get_log_files("analysis", 1)
        if analysis_files:
            latest_analysis = load_json_logs(analysis_files)
            if latest_analysis:
                latest = latest_analysis[-1]
                return {
                    "total_asset": latest.get('total_asset', 0),
                    "current_price": latest.get('current_price', 0),
                    "timestamp": latest.get('timestamp'),
                    "status": "active"
                }
        
        return {
            "total_asset": 0,
            "current_price": 0,
            "timestamp": datetime.now().isoformat(),
            "status": "no_data"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/performance")
async def get_performance_metrics(days: int = 30):
    """Get performance metrics"""
    trade_files = get_log_files("trades", days)
    trades = load_json_logs(trade_files)
    
    analysis_files = get_log_files("analysis", days)
    analysis = load_json_logs(analysis_files)
    
    if not analysis:
        return {"error": "No analysis data available"}
    
    # Calculate performance metrics
    initial_asset = analysis[0].get('total_asset', 0) if analysis else 0
    current_asset = analysis[-1].get('total_asset', 0) if analysis else 0
    
    total_return = ((current_asset - initial_asset) / initial_asset * 100) if initial_asset > 0 else 0
    
    successful_trades = [t for t in trades if t.get('success', False)]
    win_rate = (len(successful_trades) / len(trades) * 100) if trades else 0
    
    return {
        "total_return": round(total_return, 2),
        "win_rate": round(win_rate, 2),
        "total_trades": len(trades),
        "successful_trades": len(successful_trades),
        "initial_asset": initial_asset,
        "current_asset": current_asset,
        "period_days": days
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(30)  # Update every 30 seconds
            
            # Get latest data
            portfolio = await get_current_portfolio()
            await websocket.send_text(json.dumps({
                "type": "portfolio_update",
                "data": portfolio
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/debug")
async def debug_logs():
    """Debug log loading"""
    from pathlib import Path
    import os
    log_dir = Path("../../logs").resolve()
    
    result = {
        "cwd": str(Path.cwd()),
        "log_dir": str(log_dir),
        "exists": log_dir.exists(),
        "files": [str(f) for f in log_dir.glob("*.json")] if log_dir.exists() else []
    }
    
    if log_dir.exists():
        analysis_files = get_log_files("analysis", 7)
        result["analysis_files"] = analysis_files
        if analysis_files:
            analysis = load_json_logs(analysis_files)
            result["analysis_count"] = len(analysis)
            result["entries_with_asset"] = len([a for a in analysis if a.get('total_asset') is not None])
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)