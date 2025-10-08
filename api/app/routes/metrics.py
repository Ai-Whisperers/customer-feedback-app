"""
Metrics and dashboard routes for monitoring OpenAI usage.
Provides real-time visibility into token consumption and costs.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import structlog

from app.services.metrics_service import MetricsService

logger = structlog.get_logger()

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_ui():
    """
    Serve the metrics dashboard HTML UI.

    Returns:
        HTML page with real-time metrics visualization
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAI Usage Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            color: white;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .subtitle {
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .refresh-info {
            color: rgba(255,255,255,0.8);
            margin-bottom: 20px;
            font-size: 0.9em;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }

        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 4px;
        }

        .metric-value.cost {
            color: #f59e0b;
        }

        .metric-unit {
            font-size: 0.9em;
            color: #999;
        }

        .section {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .section-title {
            font-size: 1.3em;
            margin-bottom: 16px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }

        .info-row:last-child {
            border-bottom: none;
        }

        .info-label {
            color: #666;
            font-weight: 500;
        }

        .info-value {
            color: #333;
            font-weight: 600;
        }

        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .progress-bar {
            width: 100%;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            color: white;
            font-size: 0.85em;
            font-weight: 600;
        }

        .alert {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 16px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .alert-warning {
            background: #fee2e2;
            border-left-color: #ef4444;
        }

        .timestamp {
            text-align: right;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
            margin-bottom: 10px;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.2s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 1.2em;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .updating {
            animation: pulse 1.5s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenAI Usage Dashboard</h1>
        <p class="subtitle">Real-time token consumption and cost tracking</p>
        <p class="refresh-info">Auto-refreshes every 5 seconds</p>
        <div class="timestamp" id="timestamp">Loading...</div>

        <div id="loading" class="loading">
            Loading metrics...
        </div>

        <div id="dashboard" style="display: none;">
            <!-- Main Metrics -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Tokens</div>
                    <div class="metric-value" id="total-tokens">0</div>
                    <div class="metric-unit">tokens</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Total Cost</div>
                    <div class="metric-value cost" id="total-cost">$0.00</div>
                    <div class="metric-unit">USD</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Comments Analyzed</div>
                    <div class="metric-value" id="total-comments">0</div>
                    <div class="metric-unit">comments</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Avg Tokens/Comment</div>
                    <div class="metric-value" id="avg-tokens">0</div>
                    <div class="metric-unit">tokens/comment</div>
                </div>
            </div>

            <!-- Token Breakdown -->
            <div class="section">
                <h3 class="section-title">Token Breakdown</h3>
                <div class="info-row">
                    <span class="info-label">Input Tokens (Prompts)</span>
                    <span class="info-value" id="prompt-tokens">0</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Output Tokens (Completions)</span>
                    <span class="info-value" id="completion-tokens">0</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total Requests</span>
                    <span class="info-value" id="total-requests">0</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total Batches</span>
                    <span class="info-value" id="total-batches">0</span>
                </div>
            </div>

            <!-- Last Hour Stats -->
            <div class="section">
                <h3 class="section-title">Last Hour</h3>
                <div class="info-row">
                    <span class="info-label">Tokens Used</span>
                    <span class="info-value" id="hour-tokens">0</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Cost</span>
                    <span class="info-value" id="hour-cost">$0.00</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Comments Processed</span>
                    <span class="info-value" id="hour-comments">0</span>
                </div>
            </div>

            <!-- Pricing Info -->
            <div class="section">
                <h3 class="section-title">Pricing (GPT-4o-mini)</h3>
                <div class="info-row">
                    <span class="info-label">Input Tokens</span>
                    <span class="info-value" id="price-input">$0.15 / 1M tokens</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Output Tokens</span>
                    <span class="info-value" id="price-output">$0.60 / 1M tokens</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Model</span>
                    <span class="info-value" id="model-name">gpt-4o-mini</span>
                </div>
            </div>

            <!-- Cost per 1000 Comments Estimate -->
            <div class="section">
                <h3 class="section-title">Cost Estimates</h3>
                <div class="info-row">
                    <span class="info-label">Per 1,000 Comments</span>
                    <span class="info-value cost" id="cost-per-1k">~$0.00</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Per 10,000 Comments</span>
                    <span class="info-value cost" id="cost-per-10k">~$0.00</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let lastUpdate = null;

        async function fetchMetrics() {
            try {
                const response = await fetch('/api/metrics/summary');
                const data = await response.json();

                updateDashboard(data);

                // Show dashboard, hide loading
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';

            } catch (error) {
                console.error('Failed to fetch metrics:', error);
                document.getElementById('loading').textContent = 'Error loading metrics. Retrying...';
            }
        }

        function updateDashboard(data) {
            const global = data.global || {};
            const lastHour = data.last_hour || {};
            const pricing = data.pricing || {};

            // Update timestamp
            const now = new Date();
            document.getElementById('timestamp').textContent =
                `Last updated: ${now.toLocaleString()}`;

            // Main metrics
            document.getElementById('total-tokens').textContent =
                (global.total_tokens || 0).toLocaleString();
            document.getElementById('total-cost').textContent =
                `$${(global.total_cost_usd || 0).toFixed(4)}`;
            document.getElementById('total-comments').textContent =
                (global.total_comments || 0).toLocaleString();
            document.getElementById('avg-tokens').textContent =
                (global.avg_tokens_per_comment || 0).toFixed(1);

            // Token breakdown
            document.getElementById('prompt-tokens').textContent =
                (global.total_prompt_tokens || 0).toLocaleString();
            document.getElementById('completion-tokens').textContent =
                (global.total_completion_tokens || 0).toLocaleString();
            document.getElementById('total-requests').textContent =
                (global.total_requests || 0).toLocaleString();
            document.getElementById('total-batches').textContent =
                (global.total_batches || 0).toLocaleString();

            // Last hour
            document.getElementById('hour-tokens').textContent =
                (lastHour.total_tokens || 0).toLocaleString();
            document.getElementById('hour-cost').textContent =
                `$${(lastHour.total_cost_usd || 0).toFixed(4)}`;
            document.getElementById('hour-comments').textContent =
                (lastHour.total_comments || 0).toLocaleString();

            // Pricing
            document.getElementById('price-input').textContent =
                `$${pricing.input_per_1m_tokens || 0.15} / 1M tokens`;
            document.getElementById('price-output').textContent =
                `$${pricing.output_per_1m_tokens || 0.60} / 1M tokens`;
            document.getElementById('model-name').textContent =
                pricing.model || 'gpt-4o-mini';

            // Cost estimates
            const avgTokens = global.avg_tokens_per_comment || 60;
            const inputRatio = 0.6; // Assume 60% input, 40% output
            const outputRatio = 0.4;

            const costPer1k = (
                (avgTokens * 1000 * inputRatio / 1_000_000 * pricing.input_per_1m_tokens) +
                (avgTokens * 1000 * outputRatio / 1_000_000 * pricing.output_per_1m_tokens)
            );

            document.getElementById('cost-per-1k').textContent =
                `~$${costPer1k.toFixed(3)}`;
            document.getElementById('cost-per-10k').textContent =
                `~$${(costPer1k * 10).toFixed(2)}`;
        }

        // Initial fetch
        fetchMetrics();

        // Auto-refresh every 5 seconds
        setInterval(fetchMetrics, 5000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router.get("/summary")
async def get_metrics_summary():
    """
    Get comprehensive metrics summary.

    Returns:
        JSON with global metrics, recent metrics, and pricing info
    """
    try:
        dashboard_data = MetricsService.get_dashboard_data()
        return JSONResponse(content=dashboard_data)
    except Exception as e:
        logger.error("Failed to get metrics summary", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/task/{task_id}")
async def get_task_metrics(task_id: str):
    """
    Get metrics for a specific task.

    Args:
        task_id: Task ID to get metrics for

    Returns:
        JSON with task-specific metrics
    """
    try:
        metrics = MetricsService.get_task_metrics(task_id)

        if metrics:
            return JSONResponse(content=metrics)
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Metrics not found for task"}
            )
    except Exception as e:
        logger.error("Failed to get task metrics", task_id=task_id, error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/recent")
async def get_recent_metrics(hours: int = 1):
    """
    Get metrics for recent time period.

    Args:
        hours: Number of hours to look back (default: 1)

    Returns:
        JSON with metrics for the specified period
    """
    try:
        metrics = MetricsService.get_recent_metrics(hours=hours)
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error("Failed to get recent metrics", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/reset")
async def reset_metrics():
    """
    Reset all metrics (admin only - use with caution).

    Returns:
        Confirmation message
    """
    try:
        MetricsService.reset_metrics()
        return JSONResponse(content={
            "message": "Metrics reset successfully",
            "warning": "This action cannot be undone"
        })
    except Exception as e:
        logger.error("Failed to reset metrics", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
